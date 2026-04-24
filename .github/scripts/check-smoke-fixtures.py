#!/usr/bin/env python3
"""Reference implementation of skill parsing/rendering logic.

Runs over ci/fixtures/* and diffs produced output against ci/golden/*.

When the verifier and skill markdown disagree, fix whichever artifact
is wrong: ambiguous skill markdown is a bug, stale verifier logic is
also a bug. The verifier is NOT a canonical authority over the skill;
both are expressions of the same intent, cross-checked by CI.

Design (per 메타-9, Codex Q5 2026-04-14):
- Functional dispatch + dataclasses + FIXTURE_SCENARIOS manifest
- Actual simulation for every fixture (input -> produced -> diff vs golden)
- Semantic assertions BEFORE byte diff (cause, not just drift)
- Real happy-path lock (acquire/release); contention branches out of Phase 1
- Shared registry library via .github/scripts/lib/recommendation_registry
- Deterministic I/O: newline="\\n", SMOKE_PINNED_UTC env var, sorted globs

Exit codes:
    0 - all 4 fixtures PASS
    1 - any fixture fails semantic assertions or byte diff
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# Make lib.recommendation_registry importable when invoked from repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.recommendation_registry import check_recommendations, load_registry  # noqa: E402

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover
    print(f"[FATAL] jsonschema not installed: {exc}", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = ROOT / "ci" / "fixtures"
GOLDEN_DIR = ROOT / "ci" / "golden"
SCHEMAS_DIR = ROOT / "plugin" / "references" / "schemas"
REGISTRY_PATH = ROOT / "plugin" / "references" / "recommendation-registry.json"

# Make the ci/scripts/ sibling directory importable for the shared
# normalization implementation (model-drift-rules.md table parser + matcher).
_CI_SCRIPTS = ROOT / "ci" / "scripts"
if str(_CI_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_CI_SCRIPTS))
from t3_model_drift_check import (  # noqa: E402
    normalize_model_id,
    parse_normalization_table,
)

# Section heading (legacy MD) -> snake_case JSON field name.
SECTION_TO_FIELD = {
    "Runtime & Language": "runtime_and_language",
    "Framework & Libraries": "framework_and_libraries",
    "Package Management": "package_management",
    "Testing": "testing",
    "Build & Dev": "build_and_dev",
    "Project Structure": "project_structure",
    "Claude Code Configuration State": "claude_code_configuration_state",
}

# Per-section: bullet-key (as written) -> JSON sub-field name.
BULLET_KEY_MAP = {
    "runtime_and_language": {
        "Runtime": "runtime",
        "Language": "language",
        "Module system": "module_system",
    },
    "framework_and_libraries": {
        "Framework": "framework",
        "UI": "ui",
        "Styling": "styling",
    },
    "package_management": {
        "Manager": "manager",
        "Lock file": "lock_file",
    },
    "testing": {
        "Unit": "unit",
        "E2E": "e2e",
    },
    "build_and_dev": {
        "Bundler": "bundler",
        "Linter": "linter",
        "Formatter": "formatter",
    },
    "project_structure": {
        "Type": "type",
        "Source convention": "source_convention",
        "Key directories": "key_directories",
    },
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class RunContext:
    pinned_utc: str
    work_dir: Path
    fixture_name: str


@dataclass
class WorkspaceState:
    """In-memory mirror of canonical files. Used for semantic assertions.
    Filled as handlers run; re-read from disk would risk TOCTOU races."""
    profile: dict | None = None
    recommendations: dict | None = None
    changelog: str | None = None
    state_summary: str | None = None
    examined_legacy_md: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Primitive 2: Atomic write (state_io.md §atomic-write)
# ---------------------------------------------------------------------------


def atomic_write_text(path: Path, content: str) -> None:
    """Temp file in same directory then os.replace. Explicit LF + UTF-8."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = tempfile.NamedTemporaryFile(
        "w",
        dir=path.parent,
        encoding="utf-8",
        newline="\n",
        delete=False,
    )
    try:
        tmp.write(content)
        tmp.close()
        os.replace(tmp.name, path)
    except Exception:
        # Clean up the temp if replace did not consume it.
        try:
            Path(tmp.name).unlink()
        except FileNotFoundError:
            pass
        raise


def atomic_write_json(path: Path, obj: dict) -> None:
    """Indented JSON + trailing newline (matches golden layout)."""
    content = format_json_golden(obj) + "\n"
    atomic_write_text(path, content)


def format_json_golden(obj) -> str:
    """JSON serializer matching the golden fixtures' hand-authored style:

    - Arrays of primitives (str/num/bool/null) are rendered on ONE line:
      `["a", "b", "c"]` and `[]`.
    - Objects whose values are all primitives AND have <= 3 fields are rendered
      INLINE: `{ "k": v, "k2": v2 }`.
    - Objects containing arrays, nested objects, or more than 3 fields are
      EXPANDED across multiple lines with 2-space indentation.
    - Arrays of objects are always expanded.

    This matches what a human JSON author writes: scan-friendly when small,
    readable when nested. Our goldens are authored by hand; the verifier must
    reproduce the same style byte-for-byte."""
    return _dump(obj, 0)


def _is_primitive(v) -> bool:
    return isinstance(v, (str, int, float, bool)) or v is None


def _array_all_primitive(arr) -> bool:
    return all(_is_primitive(x) for x in arr)


def _object_is_inline(obj) -> bool:
    """Inline rule derived from hand-authored goldens:

    - Empty object: inline `{}`.
    - Exactly 1 primitive field: inline (e.g. `metadata: { "last_updated": ... }`).
    - 2+ primitive fields where ALL values are bool or int (no str, no null):
      inline (e.g. `claude_md: { "exists": true, "section_count": 5 }`).
    - Everything else: expanded.

    Goldens expand multi-field records that contain string or null values
    (project profile sections), and inline the small bool/int "flag records"
    plus single-field wrappers."""
    if not isinstance(obj, dict):
        return False
    if len(obj) == 0:
        return True
    if not all(_is_primitive(v) for v in obj.values()):
        return False
    if len(obj) == 1:
        return True
    return all(isinstance(v, bool) or (isinstance(v, int) and not isinstance(v, bool)) for v in obj.values())


_LINE_WIDTH_THRESHOLD = 110


def _dump(v, indent: int, parent_prefix_len: int = 0) -> str:
    """Render value `v` at nesting depth `indent`. parent_prefix_len is the
    length of the line prefix before this value (used to decide whether a
    wide inline array should wrap to multi-line). Goldens expand arrays
    whose inline representation pushes the line past ~110 chars."""
    pad = "  " * indent
    if _is_primitive(v):
        return _scalar(v)
    if isinstance(v, list):
        if not v:
            return "[]"
        if _array_all_primitive(v):
            inline = "[" + ", ".join(_scalar(x) for x in v) + "]"
            if parent_prefix_len + len(inline) <= _LINE_WIDTH_THRESHOLD:
                return inline
            # wrap: expand array of primitives across lines
            lines = ["["]
            for i, item in enumerate(v):
                comma = "," if i < len(v) - 1 else ""
                lines.append("  " * (indent + 1) + _scalar(item) + comma)
            lines.append(pad + "]")
            return "\n".join(lines)
        # array of objects — always expand
        lines = ["["]
        for i, item in enumerate(v):
            comma = "," if i < len(v) - 1 else ""
            lines.append("  " * (indent + 1) + _dump(item, indent + 1, len("  ") * (indent + 1)) + comma)
        lines.append(pad + "]")
        return "\n".join(lines)
    if isinstance(v, dict):
        if len(v) == 0:
            return "{}"
        if _object_is_inline(v):
            parts = [f'{json.dumps(k, ensure_ascii=False)}: {_scalar(val)}' for k, val in v.items()]
            return "{ " + ", ".join(parts) + " }"
        items = list(v.items())
        lines = ["{"]
        for i, (k, val) in enumerate(items):
            comma = "," if i < len(items) - 1 else ""
            key_str = f'{json.dumps(k, ensure_ascii=False)}: '
            child_prefix = len("  ") * (indent + 1) + len(key_str)
            child = _dump(val, indent + 1, child_prefix)
            lines.append("  " * (indent + 1) + key_str + child + comma)
        lines.append(pad + "}")
        return "\n".join(lines)
    raise TypeError(f"cannot serialize {type(v).__name__}: {v!r}")


def _scalar(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return json.dumps(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    raise TypeError(f"not a scalar: {v!r}")


# ---------------------------------------------------------------------------
# Primitive 1: State-mutation lock (state_io.md §state-mutation-lock)
# ---------------------------------------------------------------------------


def acquire_lock(lock_path: Path, behavior: str, pinned_utc: str) -> None:
    """Acquire state-mutation lock at lock_path.

    Writes {"pid": <int>, "started_at": <iso>} content via atomic_write_text.

    **Phase 1 scope**: CI is single-threaded; contention and stale-lock
    branches are out of scope per ci/README.md. The `behavior` parameter
    documents the intended semantics per Primitive 1 (Step 0.5 aborts on
    contention; Final Phase waits up to 30s), but both branches currently
    take the happy path. Phase 2+ will implement real contention handling
    when multi-shell fixtures land.
    """
    if behavior not in {"abort_immediately", "wait_30s"}:
        raise ValueError(f"unknown lock behavior: {behavior}")
    content = json.dumps({"pid": os.getpid(), "started_at": pinned_utc})
    atomic_write_text(lock_path, content)


def release_lock(lock_path: Path) -> None:
    if lock_path.exists():
        os.unlink(lock_path)


# ---------------------------------------------------------------------------
# Parsing helpers (legacy MD -> canonical JSON)
# ---------------------------------------------------------------------------


def _strip_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body) where frontmatter is minimal yaml we
    actually need (title/last_updated/source_files_checked). The full yaml
    parser is overkill; we only need a couple fields for migration."""
    fm: dict = {}
    if not text.startswith("---"):
        return fm, text
    end = text.find("\n---", 3)
    if end == -1:
        return fm, text
    head = text[3:end].strip("\n")
    body = text[end + 4 :].lstrip("\n")
    current_list_key: str | None = None
    for raw in head.splitlines():
        if raw.startswith("  - ") and current_list_key:
            fm.setdefault(current_list_key, []).append(raw[4:].strip())
            continue
        current_list_key = None
        if ":" not in raw:
            continue
        key, _, val = raw.partition(":")
        key = key.strip()
        val = val.strip()
        if not val:
            # List to follow.
            current_list_key = key
            fm[key] = []
        else:
            fm[key] = val
    return fm, body


def _extract_frontmatter_version(frontmatter: dict) -> str:
    """Return the version literal from a parsed frontmatter dict.

    Accepts the dict returned by _strip_frontmatter. Raises ValueError if the
    'version' key is absent. Strips surrounding quotes for robustness.
    """
    raw = frontmatter.get("version")
    if raw is None:
        raise ValueError("config-changelog.md frontmatter missing 'version' field")
    # Strip surrounding quotes in case _strip_frontmatter preserved them.
    return raw.strip("'\"")


def _parse_compacted_history_anchors(body: str) -> list[dict]:
    """Parse per-skill anchor blocks from the ## Compacted History section.

    Forward-compat READ only (T4c handles emission). If the section is absent
    or contains no anchors, returns []. Tolerant parser: any line matching
    '- skill: /X' inside ## Compacted History is treated as an anchor header;
    sibling 'last_entry_date:', 'last_model:', 'last_capability_fingerprint:'
    lines are consumed as anchor fields.

    Per plan D3 (coordination note): learning-system.md does not yet specify
    the rendered anchor syntax, so minimal pattern-match is used.

    Returns list of dicts with keys: skill, last_entry_date, last_model,
    last_capability_fingerprint.
    """
    lines = body.splitlines()
    # Find ## Compacted History section
    in_section = False
    anchors: list[dict] = []
    current_anchor: dict | None = None
    for line in lines:
        stripped = line.strip()
        if stripped == "## Compacted History":
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            # Next heading — end of Compacted History section
            break
        if not in_section:
            continue
        # Match anchor header: '- skill: /audit'
        skill_match = re.match(r"^-\s+skill:\s+(/\S+)", line)
        if skill_match:
            if current_anchor is not None:
                anchors.append(current_anchor)
            current_anchor = {
                "skill": skill_match.group(1),
                "last_entry_date": None,
                "last_model": None,
                "last_capability_fingerprint": None,
            }
            continue
        if current_anchor is not None:
            # Consume sibling fields (indented or same-level)
            date_match = re.match(r"^\s+last_entry_date:\s*(.+)$", line)
            if date_match:
                current_anchor["last_entry_date"] = date_match.group(1).strip().strip("'\"") or None
                continue
            model_match = re.match(r"^\s+last_model:\s*(.*)$", line)
            if model_match:
                val = model_match.group(1).strip().strip("'\"")
                current_anchor["last_model"] = val if val and val.lower() != "null" else None
                continue
            fp_match = re.match(r"^\s+last_capability_fingerprint:\s*(.*)$", line)
            if fp_match:
                val = fp_match.group(1).strip()
                current_anchor["last_capability_fingerprint"] = None if val.lower() == "null" else (val or None)
                continue
    if current_anchor is not None:
        anchors.append(current_anchor)
    return anchors


def _value_or_null(value: str) -> str | None:
    """'Not detected' -> None; otherwise stripped string."""
    v = value.strip()
    if v == "Not detected":
        return None
    return v


# Known bullet keys per special section (not in BULLET_KEY_MAP).
SPECIAL_SECTION_KEYS = {
    "project_structure": {"Type", "Source convention", "Key directories"},
    "claude_code_configuration_state": {
        "CLAUDE.md", "settings.json", "Rules", "Agents", "Hooks", "MCP",
    },
}


def parse_profile_md(text: str, source_file: str, pinned_utc: str) -> dict:
    """Parse legacy project-profile.md into profile.json dict.

    Mapping:
      - `## Section Name` -> snake_case JSON key (via SECTION_TO_FIELD)
      - `- Key: Value` bullets -> sub-fields (via BULLET_KEY_MAP)
      - "Not detected" values -> null
    The Claude Code Configuration State section and project_structure have
    special bullet handling (object shapes, lists).

    Strictness (per Task 7 parser robustness cases 06/07/10/11):
      - Body with no recognized `## <Section>` heading -> raise (covers empty
        file + pre-v2.10 top-level bullets that never match v2.10 layout).
      - Inside a recognized section, a `- ` line with no `:` -> raise
        (corrupt key).
      - Inside a recognized section, a `- Key: Value` whose key is not a
        canonical field name for that section -> raise (bilingual / unknown
        keys). Nested sub-bullets (`  - ...`) are not affected — they start
        with whitespace and are not picked up by the `- ` guard.
    A raise on any of these is caught by Step 0.5 phase 4 and routes the
    migration into the fallback/empty-canonical branch.
    """
    fm, body = _strip_frontmatter(text)
    source_files = fm.get("source_files_checked") or [source_file]

    # Strict pre-check: at least one recognized v2.10 section heading must
    # appear in the body. Rejects empty files and pre-v2.10 top-level-bullet
    # layouts without forcing the body-walker to guess.
    recognized_headings = [
        line[3:].strip()
        for line in body.splitlines()
        if line.startswith("## ") and line[3:].strip() in SECTION_TO_FIELD
    ]
    if not recognized_headings:
        raise ValueError(
            "legacy profile MD has no recognized v2.10 section headings "
            "(empty body or pre-v2.10 format)"
        )

    profile: dict = {
        "schema_version": "1.0.0",
        "metadata": {
            "generated_by": "guardians-of-the-claude",
            "last_updated": pinned_utc,
            "source_files_checked": source_files,
        },
        "runtime_and_language": {"runtime": None, "language": None, "module_system": None},
        "framework_and_libraries": {"framework": None, "ui": None, "styling": None},
        "package_management": {"manager": None, "lock_file": None},
        "testing": {"unit": None, "e2e": None},
        "build_and_dev": {"bundler": None, "linter": None, "formatter": None},
        "project_structure": {
            "type": None,
            "source_convention": None,
            "key_directories": [],
        },
        "claude_code_configuration_state": {
            "claude_md": {"exists": False, "section_count": 0},
            "settings_json": {"exists": False, "has_permissions": False},
            "rules_count": 0,
            "agents_count": 0,
            "hooks_count": 0,
            "mcp_servers_count": 0,
        },
    }

    current_field: str | None = None
    for raw in body.splitlines():
        line = raw.rstrip()
        if line.startswith("## "):
            heading = line[3:].strip()
            current_field = SECTION_TO_FIELD.get(heading)
            continue
        if not line.startswith("- ") or current_field is None:
            continue
        # Strict: in a recognized section, every top-level `- ` bullet must
        # have a colon separating key from value.
        if ":" not in line[2:]:
            raise ValueError(
                f"malformed bullet in section {current_field!r}: "
                f"expected `- Key: Value`, got {line!r}"
            )
        key, _, value = line[2:].partition(":")
        key = key.strip()
        value = value.strip()
        # Strict: key must be a canonical field name for the section.
        if current_field in SPECIAL_SECTION_KEYS:
            allowed = SPECIAL_SECTION_KEYS[current_field]
        else:
            allowed = set(BULLET_KEY_MAP.get(current_field, {}).keys())
        if key not in allowed:
            raise ValueError(
                f"unknown field key {key!r} in section {current_field!r}; "
                f"expected one of {sorted(allowed)}"
            )
        if current_field == "project_structure":
            if key == "Type":
                # e.g., "Single project (not monorepo)" -> "single_project"
                #       "Monorepo" -> "monorepo"
                low = value.lower()
                if "monorepo" in low and "not monorepo" not in low:
                    profile["project_structure"]["type"] = "monorepo"
                elif "single" in low:
                    profile["project_structure"]["type"] = "single_project"
                else:
                    profile["project_structure"]["type"] = _value_or_null(value)
            elif key == "Source convention":
                profile["project_structure"]["source_convention"] = _value_or_null(value)
            elif key == "Key directories":
                if value and value != "Not detected":
                    profile["project_structure"]["key_directories"] = [
                        item.strip() for item in value.split(",") if item.strip()
                    ]
        elif current_field == "claude_code_configuration_state":
            ccs = profile["claude_code_configuration_state"]
            if key == "CLAUDE.md":
                exists = value.startswith("exists")
                section_count = 0
                if "(" in value and "sections)" in value:
                    inner = value[value.find("(") + 1 : value.find(" sections)")]
                    try:
                        section_count = int(inner)
                    except ValueError:
                        section_count = 0
                ccs["claude_md"] = {"exists": exists, "section_count": section_count}
            elif key == "settings.json":
                exists = value.startswith("exists")
                has_perm = "permissions" in value
                ccs["settings_json"] = {"exists": exists, "has_permissions": has_perm}
            elif key in ("Rules", "Agents", "Hooks", "MCP"):
                num = 0
                parts = value.split()
                if parts:
                    try:
                        num = int(parts[0])
                    except ValueError:
                        num = 0
                if key == "Rules":
                    ccs["rules_count"] = num
                elif key == "Agents":
                    ccs["agents_count"] = num
                elif key == "Hooks":
                    ccs["hooks_count"] = num
                elif key == "MCP":
                    ccs["mcp_servers_count"] = num
        else:
            bullet_map = BULLET_KEY_MAP[current_field]
            sub = bullet_map[key]
            profile[current_field][sub] = _value_or_null(value)

    return profile


def parse_latest_md(text: str, skill: str, pinned_utc: str, registry_by_key: dict) -> list[dict]:
    """Parse legacy latest-{skill}.md Recommendations section.

    Per Codex Q5 Pitfall 3 + Step 4: deterministic, no keyword matching.
    Each bullet must match `- id: <legacy-id>` / `- <legacy-id>: <desc> — STATUS`.
    Registry aliases resolve legacy-id -> canonical key. Unregistered ids are
    a fixture bug and raise ValueError.
    """
    _, body = _strip_frontmatter(text)
    lines = body.splitlines()
    # Locate `## Recommendations` block.
    start = None
    for idx, line in enumerate(lines):
        if line.strip() == "## Recommendations":
            start = idx + 1
            break
    if start is None:
        return []

    # Slice until next `## ` heading (or EOF).
    end = len(lines)
    for idx in range(start, len(lines)):
        if lines[idx].startswith("## ") and lines[idx].strip() != "## Recommendations":
            end = idx
            break
    block = lines[start:end]

    # Two supported shapes in our fixtures:
    #   Shape A: multi-line with `- id: <legacy-id>` and sibling `description:` / `status:` lines.
    #   Shape B: one-line `- <legacy-id>: <description> — STATUS`.
    entries: list[dict] = []
    current: dict | None = None

    def finalize(cur: dict | None) -> None:
        if cur is None:
            return
        legacy = cur.get("_legacy_id")
        if not legacy:
            return
        row = registry_by_key.get(legacy)
        if row is None:
            raise ValueError(f"fixture uses unregistered legacy id: {legacy}")
        first = cur.get("first_seen") or pinned_utc
        last = cur.get("last_seen") or pinned_utc
        status = cur.get("status", "PENDING")
        pending_count = cur.get("pending_count")
        if pending_count is None:
            pending_count = 1 if status == "PENDING" else 0
        entry = {
            "id": row["key"],  # canonical key (Lint 3: aliases never persist)
            "description": cur.get("description", "").strip(),
            "issued_by": skill,
            "status": status,
            "pending_count": int(pending_count),
            "first_seen": first,
            "last_seen": last,
            "resolved_by": None,
            "declined_reason": None,
        }
        if status == "RESOLVED":
            entry["resolved_by"] = cur.get("resolved_by")
        entries.append(entry)

    for raw in block:
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if stripped == "(none)":
            return []
        if line.startswith("- "):
            finalize(current)
            current = {}
            body_part = line[2:]
            # Shape A marker: starts with "id: "
            if body_part.startswith("id:"):
                current["_legacy_id"] = body_part[3:].strip()
                continue
            # Shape B: "- <legacy-id>: <desc> — STATUS"
            if ":" in body_part:
                legacy, _, rest = body_part.partition(":")
                current["_legacy_id"] = legacy.strip()
                # rest may be "description — STATUS" or just description
                desc, sep, status = rest.rpartition("—")
                if sep:
                    current["description"] = desc.strip()
                    current["status"] = status.strip()
                else:
                    current["description"] = rest.strip()
                continue
            continue
        if current is None:
            continue
        # Sub-fields (Shape A continuations)
        sub_stripped = stripped
        if sub_stripped.startswith("description:"):
            current["description"] = sub_stripped[len("description:") :].strip()
        elif sub_stripped.startswith("status:"):
            current["status"] = sub_stripped[len("status:") :].strip()
        elif sub_stripped.startswith("pending_count:"):
            try:
                current["pending_count"] = int(
                    sub_stripped[len("pending_count:") :].strip()
                )
            except ValueError:
                current["pending_count"] = 1
        elif sub_stripped.startswith("first_seen:"):
            current["first_seen"] = sub_stripped[len("first_seen:") :].strip()
        elif sub_stripped.startswith("last_seen:"):
            current["last_seen"] = sub_stripped[len("last_seen:") :].strip()
        elif sub_stripped.startswith("resolved_by:"):
            current["resolved_by"] = sub_stripped[len("resolved_by:") :].strip()

    finalize(current)
    return entries


# ---------------------------------------------------------------------------
# Drift State Derivation (see learning-system.md, section "Drift Advisory Derivation")
# ---------------------------------------------------------------------------


_NORMALIZATION_RULES_CACHE: list[dict] | None = None


def _get_normalization_rules() -> list[dict]:
    """Parse and cache the authoritative normalization table (observed rows only).
    Parsing is deferred to first call to keep import side-effects minimal.
    """
    global _NORMALIZATION_RULES_CACHE
    if _NORMALIZATION_RULES_CACHE is None:
        rules_file = ROOT / "plugin" / "references" / "model-drift-rules.md"
        _NORMALIZATION_RULES_CACHE = parse_normalization_table(
            rules_file.read_text(encoding="utf-8")
        )
    return _NORMALIZATION_RULES_CACHE


def _scan_baseline_anchor(changelog_text: str | None) -> tuple[bool, str | None]:
    """Reverse-chronological scan for /audit baseline anchor.

    Returns (baseline_present, baseline_last_model). baseline_last_model is
    None when the first reached /audit anchor has a delta-omitted bullet
    (first-anchor-wins: do not skip past null).
    """
    if not changelog_text:
        return (False, None)

    # Split on H2 sections; pick each by name since document order varies
    # (Compacted History may appear before or after Recent Activity).
    sections = re.split(r"^## ", changelog_text, flags=re.MULTILINE)
    recent_activity = next(
        (s for s in sections if s.lstrip().startswith("Recent Activity")),
        None,
    )

    # Recent Activity: most-recent entry wins; sort H3 entries by date descending.
    if recent_activity:
        entries = re.findall(
            r"^### (\d{4}-\d{2}-\d{2})\s+[—-]\s+/(audit|create|secure|optimize)\b[^\n]*\n(.*?)(?=^### |\Z)",
            recent_activity,
            flags=re.MULTILINE | re.DOTALL,
        )
        entries.sort(key=lambda t: t[0], reverse=True)
        for _date, skill, body in entries:
            if skill != "audit":
                continue
            m = re.search(r"^- Model:\s*(.+?)\s*$", body, flags=re.MULTILINE)
            if m:
                model = m.group(1).strip()
                return (True, None if model.lower() == "null" else model)

    # Compacted History: delegate to the authoritative multi-line anchor parser
    # (shares null-normalization and document-order semantics).
    anchors = _parse_compacted_history_anchors(changelog_text)
    for anchor in anchors:
        if anchor.get("skill") == "/audit":
            # First-anchor-wins: return even on null last_model (do not skip).
            return (True, anchor.get("last_model"))

    return (False, None)


def _drift_state(
    current_fp: dict | None,
    baseline_present: bool,
    baseline_fp: dict | None,
) -> str:
    """Silence evaluation order. Returns one of:
    normalization_null, missing_baseline, match, drift.
    """
    # Silence evaluation order (short-circuit).
    if current_fp is None or (baseline_present and baseline_fp is None):
        return "normalization_null"
    if not baseline_present:
        return "missing_baseline"
    if current_fp == baseline_fp:
        return "match"
    return "drift"


def _test_scan_order() -> list[str]:
    """L2 unit test: pure function assertions for _scan_baseline_anchor
    + _drift_state. Returns list of failure messages (empty = PASS).
    """
    failures: list[str] = []

    # Fixture 1: Recent Activity has /audit entry with bullet (em-dash header).
    ra_hit = """
## Recent Activity

### 2026-04-22 — /audit
- Model: claude-opus-4-7
- Applied: ...
"""
    present, model = _scan_baseline_anchor(ra_hit)
    if not (present and model == "claude-opus-4-7"):
        failures.append(f"scan RA hit: got ({present}, {model})")

    # Fixture 2: Recent Activity exhausted, Compacted History has /audit anchor
    # (multi-line YAML-ish form per _parse_compacted_history_anchors).
    ch_hit = """
## Recent Activity

### 2026-04-22 — /create
- Applied: ...

## Compacted History

### 2026-Q1

- skill: /audit
  last_entry_date: 2026-03-15
  last_model: claude-sonnet-4-6
  last_capability_fingerprint: null
"""
    present, model = _scan_baseline_anchor(ch_hit)
    if not (present and model == "claude-sonnet-4-6"):
        failures.append(f"scan CH hit: got ({present}, {model})")

    # Fixture 3: First /audit anchor reached has null model (first-anchor-wins).
    # Second bucket has non-null; test must confirm we do NOT skip past the null.
    ch_null = """
## Recent Activity

## Compacted History

### 2026-Q1

- skill: /audit
  last_entry_date: 2026-03-10
  last_model: null
  last_capability_fingerprint: null

### 2025-Q4

- skill: /audit
  last_entry_date: 2025-12-01
  last_model: claude-opus-4-5
  last_capability_fingerprint: null
"""
    present, model = _scan_baseline_anchor(ch_null)
    if not (present and model is None):
        failures.append(f"scan first-anchor-wins null: got ({present}, {model})")

    # Fixture 4: All buckets exhausted, no /audit anchor anywhere.
    no_audit = """
## Recent Activity

### 2026-04-22 — /create
- Applied: ...

## Compacted History
"""
    present, model = _scan_baseline_anchor(no_audit)
    if not (present is False and model is None):
        failures.append(f"scan empty: got ({present}, {model})")

    # Fixture 4b: None changelog.
    present, model = _scan_baseline_anchor(None)
    if not (present is False and model is None):
        failures.append(f"scan None: got ({present}, {model})")

    # Fixture 4c: empty-string changelog.
    present, model = _scan_baseline_anchor("")
    if not (present is False and model is None):
        failures.append(f"scan empty-string: got ({present}, {model})")

    # Fixture 4d: Recent Activity /audit without - Model: bullet (delta-omit).
    # Scan must skip past the bulletless entry and fall through to Compacted History.
    ra_delta_omit = """
## Recent Activity

### 2026-04-22 — /audit
- Applied: ...

## Compacted History

### 2025-Q4

- skill: /audit
  last_entry_date: 2025-12-01
  last_model: claude-haiku-4-5
  last_capability_fingerprint: null
"""
    present, model = _scan_baseline_anchor(ra_delta_omit)
    if not (present and model == "claude-haiku-4-5"):
        failures.append(f"scan delta-omit RA fallback to CH: got ({present}, {model})")

    # Fixture 5-8: _drift_state silence order.
    fp_opus = {"family_tier": "opus", "context_window_class": "200k",
               "reasoning_class": "extended_any", "context_management_class": "compaction_capable"}
    fp_sonnet = {"family_tier": "sonnet", "context_window_class": "200k",
                 "reasoning_class": "extended_any", "context_management_class": "compaction_capable"}

    if _drift_state(fp_opus, True, fp_opus) != "match":
        failures.append("drift_state match")
    if _drift_state(fp_opus, True, fp_sonnet) != "drift":
        failures.append("drift_state drift")
    if _drift_state(None, True, fp_opus) != "normalization_null":
        failures.append("drift_state current-null")
    if _drift_state(fp_opus, False, None) != "missing_baseline":
        failures.append("drift_state missing")

    return failures


def _test_render_drift_header() -> list[str]:
    """L3 unit test: render_state_summary injects drift header when
    state == 'drift' and stays silent for match. Returns list of failure
    messages (empty = PASS).
    """
    failures: list[str] = []

    profile_stub: dict = {
        "schema_version": "1.0.0",
        "claude_code_configuration_state": {
            "model": "claude-sonnet-4-6",
            "claude_md": {"exists": True},
            "settings_json": {"exists": True},
            "rules_count": 0,
            "agents_count": 0,
            "hooks_count": 0,
            "mcp_servers_count": 0,
        },
    }
    recs_stub: dict = {"schema_version": "1.0.0", "recommendations": []}
    # NOTE: frontmatter is required here but NOT in _test_scan_order stubs —
    # render_state_summary pipeline calls _render_recent_skill_results →
    # _parse_changelog_entries → _extract_frontmatter_version, which raises
    # ValueError on absent version. Bare _scan_baseline_anchor has no such
    # dependency.
    changelog_stub = """---
version: 1.1.0
---

## Recent Activity

### 2026-04-20 — /audit
- Model: claude-opus-4-7
- Applied: score snapshot
"""
    ctx_stub = RunContext(
        pinned_utc="2026-04-14T00:00:00Z",
        work_dir=Path("."),
        fixture_name="t6-render-drift-header-unit",
    )

    out = render_state_summary(profile_stub, recs_stub, changelog_stub, ctx_stub)

    if "Model drift: claude-opus-4-7 -> claude-sonnet-4-6" not in out:
        failures.append("drift header missing from render")

    # Placement: header must fall between H1 and ## Project Profile.
    idx_h1 = out.find("# Claude Code Configuration State")
    idx_header = out.find("Model drift:")
    idx_profile = out.find("## Project Profile")
    if not (idx_h1 != -1 and idx_header != -1 and idx_profile != -1
            and idx_h1 < idx_header < idx_profile):
        failures.append(
            f"drift header placement wrong: h1={idx_h1} "
            f"header={idx_header} profile={idx_profile}"
        )

    # Silence test: when current model == baseline model, no header.
    profile_match = {
        **profile_stub,
        "claude_code_configuration_state": {
            **profile_stub["claude_code_configuration_state"],
            "model": "claude-opus-4-7",
        },
    }
    out_match = render_state_summary(
        profile_match, recs_stub, changelog_stub, ctx_stub
    )
    if "Model drift:" in out_match:
        failures.append("drift header leaked into match state")

    # Silence test: missing_baseline (no /audit in changelog) stays silent.
    out_missing = render_state_summary(
        profile_stub, recs_stub, None, ctx_stub
    )
    if "Model drift:" in out_missing:
        failures.append("drift header leaked into missing_baseline state")

    # Silence test: normalization_null (unknown current model) stays silent.
    profile_unknown = {
        **profile_stub,
        "claude_code_configuration_state": {
            **profile_stub["claude_code_configuration_state"],
            "model": "claude-future-unknown-model-2099",
        },
    }
    out_null = render_state_summary(
        profile_unknown, recs_stub, changelog_stub, ctx_stub
    )
    if "Model drift:" in out_null:
        failures.append("drift header leaked into normalization_null state")

    return failures


def _test_t6_fixtures() -> list[str]:
    """L3 integration test: byte-match smoke fixtures against goldens.

    4 rendering fixtures (drift-recent-activity, drift-compacted-history,
    normalization-null-silence, crossskill-create-drift) render through
    render_state_summary and byte-match against ci/fixtures/t6-*/golden/
    state-summary.md.

    1 stateless fixture (stateless-silence) asserts marker-file presence +
    state-summary.md golden absence (structural evidence that terminal
    state rendering is skipped in stateless mode — no runtime emulation).
    """
    failures: list[str] = []
    fixture_root = ROOT / "ci" / "fixtures"

    rendering_fixtures = [
        "t6-drift-recent-activity",
        "t6-drift-compacted-history",
        "t6-normalization-null-silence",
        "t6-crossskill-create-drift",
    ]
    for name in rendering_fixtures:
        fdir = fixture_root / name
        profile_path = fdir / "profile.json"
        changelog_path = fdir / "changelog.md"
        golden_path = fdir / "golden" / "state-summary.md"
        if not profile_path.exists():
            failures.append(f"{name}: missing profile.json")
            continue
        if not golden_path.exists():
            failures.append(f"{name}: missing golden/state-summary.md")
            continue
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        changelog = (
            changelog_path.read_text(encoding="utf-8")
            if changelog_path.exists()
            else None
        )
        golden = golden_path.read_text(encoding="utf-8")
        ctx = RunContext(
            pinned_utc=os.environ.get("SMOKE_PINNED_UTC", "2026-04-14T00:00:00Z"),
            work_dir=Path("."),
            fixture_name=name,
        )
        actual = render_state_summary(
            profile,
            {"schema_version": "1.0.0", "recommendations": []},
            changelog,
            ctx,
        )
        if actual != golden:
            failures.append(
                f"{name}: byte mismatch (len actual={len(actual)}, "
                f"golden={len(golden)})"
            )

    stateless_fixtures = ["t6-stateless-silence"]
    for name in stateless_fixtures:
        fdir = fixture_root / name
        marker = fdir / "golden" / "terminal-no-state-summary.marker"
        if not marker.exists():
            failures.append(f"{name}: missing stateless marker")
        if (fdir / "golden" / "state-summary.md").exists():
            failures.append(
                f"{name}: state-summary golden should not exist "
                f"(stateless mode)"
            )

    return failures


# ---------------------------------------------------------------------------
# Rendering (learning-system.md §State Rendering)
# ---------------------------------------------------------------------------


def render_state_summary(profile: dict, recs: dict, changelog_text: str | None, ctx: RunContext) -> str:
    """Produce state-summary.md content per learning-system.md layout."""
    header = (
        "<!-- ─────────────────────────────────────────────\n"
        " Generated from JSON state — DO NOT EDIT.\n"
        " Read-only view. Manual edits will be overwritten\n"
        " on next skill invocation.\n"
        f" Generated at: {ctx.pinned_utc}\n"
        f" Source: profile.json v{profile.get('schema_version', '1.0.0')}, "
        f"recommendations.json v{recs.get('schema_version', '1.0.0')}\n"
        "───────────────────────────────────────────────── -->\n\n"
    )

    rl = profile.get("runtime_and_language") or {}
    fw = profile.get("framework_and_libraries") or {}
    pm = profile.get("package_management") or {}
    ts = profile.get("testing") or {}
    bd = profile.get("build_and_dev") or {}
    ps = profile.get("project_structure") or {}
    ccs = profile.get("claude_code_configuration_state") or {}

    # Drift advisory derivation (shared per learning-system.md, section
    # "Drift Advisory Derivation"). Silent when state is match,
    # missing_baseline, or normalization_null.
    rules = _get_normalization_rules()
    current_model_id = ccs.get("model")
    current_fp = (
        normalize_model_id(current_model_id, rules)
        if current_model_id
        else None
    )
    baseline_present, baseline_model_id = _scan_baseline_anchor(changelog_text)
    baseline_fp = (
        normalize_model_id(baseline_model_id, rules)
        if baseline_model_id
        else None
    )
    state = _drift_state(current_fp, baseline_present, baseline_fp)

    drift_block = ""
    if state == "drift":
        drift_block = (
            f"Model drift: {baseline_model_id} -> {current_model_id}\n\n"
        )

    def _or_not_detected(v):  # noqa: E306
        return v if v else "Not detected"

    claude_md = ccs.get("claude_md") or {}
    settings_json = ccs.get("settings_json") or {}
    check = "✓" if claude_md.get("exists") else "✗"
    check_sj = "✓" if settings_json.get("exists") else "✗"
    config_line = (
        f"CLAUDE.md {check}, settings.json {check_sj}, "
        f"Rules {int(ccs.get('rules_count', 0))}, "
        f"Agents {int(ccs.get('agents_count', 0))}, "
        f"Hooks {int(ccs.get('hooks_count', 0))}, "
        f"MCP {int(ccs.get('mcp_servers_count', 0))}"
    )

    profile_block = (
        "# Claude Code Configuration State\n\n"
        f"{drift_block}"
        "## Project Profile\n"
        f"- Runtime: {_or_not_detected(rl.get('runtime'))}\n"
        f"- Language: {_or_not_detected(rl.get('language'))}\n"
        f"- Framework: {_or_not_detected(fw.get('framework'))}\n"
        f"- Package Manager: {_or_not_detected(pm.get('manager'))}\n"
        f"- Testing: {_or_not_detected(ts.get('unit'))} / {_or_not_detected(ts.get('e2e'))}\n"
        f"- Build: {_or_not_detected(bd.get('bundler'))}\n"
        f"- Structure: {_or_not_detected(ps.get('type'))}\n"
        f"- Config: {config_line}\n\n"
    )

    open_recs = [
        r for r in recs.get("recommendations", [])
        if r.get("status") in ("PENDING", "DECLINED")
    ]
    if not open_recs:
        open_block = "## Open Recommendations\n*No open recommendations.*\n\n"
    else:
        lines = ["## Open Recommendations"]
        for r in open_recs:
            status = r["status"]
            pending_count = int(r.get("pending_count", 0))
            if status == "PENDING" and pending_count > 1:
                badge = f"**[{status}× {pending_count}]**"
            else:
                badge = f"**[{status}]**"
            tail = f" — from /{r['issued_by']}"
            if status == "PENDING" and r.get("first_seen"):
                first_date = r["first_seen"].split("T")[0]
                tail += f" (first: {first_date})"
            if status == "DECLINED" and r.get("declined_reason"):
                tail += f" — {r['declined_reason']}"
            lines.append(f"- {badge} {r['description']}{tail}")
        open_block = "\n".join(lines) + "\n\n"

    recent_block = _render_recent_skill_results(changelog_text)
    return header + profile_block + open_block + recent_block


def _render_recent_skill_results(changelog_text: str | None) -> str:
    """Render Recent Skill Results from changelog Recent Activity tail.

    For each skill with at least one entry in Recent Activity, emit the
    most-recent entry (by the entry's own ordering in the file). Rendered
    in first-appearance-of-skill order — matching hand-authored golden
    ordering (chronological, since changelog entries are appended in time
    order)."""
    out = ["## Recent Skill Results", ""]
    if not changelog_text:
        return "\n".join(out) + "\n"
    parsed = _parse_changelog_entries(changelog_text)
    entries = parsed["entries"]
    # anchors unused by _render_skill_results; ignored here
    # Preserve first-occurrence order of each skill, but use its LAST entry.
    order: list[str] = []
    latest_per_skill: dict[str, dict] = {}
    for entry in entries:
        skill = entry["skill"]
        if skill not in latest_per_skill:
            order.append(skill)
        latest_per_skill[skill] = entry
    for skill in order:
        entry = latest_per_skill[skill]
        summary = _entry_summary_line(entry)
        out.append(f"### /{skill} — {entry['date']}")
        out.append(summary)
        out.append("")
    text = "\n".join(out).rstrip() + "\n"
    return text


def _parse_changelog_entries(text: str) -> dict:
    """Parse config-changelog.md and return {entries, anchors}.

    Return shape (v1.1.0+):
        {
            "entries": list[dict],   # Recent Activity entries
            "anchors": list[dict],   # Compacted History per-skill anchors (may be [])
        }

    Each entry dict: {date, skill, detected, applied, recommendations,
                      bullet_model: str | None}

    Frontmatter dispatch (per §2.5 Addition A + DEC-10):
      - version "1.0.0" → bullet_model = None for all entries (omit→null)
      - version "1.1.0" → recognize "- Model:" per entry; None on absent
      - unknown version → raises ValueError (no silent fallback)

    Caller must destructure: entries = result["entries"]
    """
    fm, body = _strip_frontmatter(text)
    version = _extract_frontmatter_version(fm)
    if version not in ("1.0.0", "1.1.0"):
        raise ValueError(
            f"Unknown config-changelog.md frontmatter version: {version!r}. "
            f"Parser supports '1.0.0' or '1.1.0' only. See §2.5 schema-evolution policy."
        )
    # Find ## Recent Activity
    lines = body.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if line.strip() == "## Recent Activity":
            start = idx + 1
            break
    if start is None:
        anchors = _parse_compacted_history_anchors(body)
        return {"entries": [], "anchors": anchors}
    entries: list[dict] = []
    current: dict | None = None
    for raw in lines[start:]:
        line = raw.rstrip()
        if line.startswith("### "):
            if current is not None:
                entries.append(current)
            # `### 2026-04-05 — /create` or `### 2026-04-05 — /create (2 runs)`
            header_text = line[4:].strip()
            date_part, _, rest = header_text.partition(" — ")
            skill_token = rest.split()[0] if rest else ""
            skill_name = skill_token.lstrip("/")
            current = {
                "date": date_part.strip(),
                "skill": skill_name,
                "detected": None,
                "applied": None,
                "recommendations": [],
                "bullet_model": None,  # §2.5 Addition A + §3.2 line 432
            }
            continue
        if current is None:
            continue
        if line.startswith("- Detected:"):
            current["detected"] = line[len("- Detected:") :].strip()
        elif line.startswith("- Applied:"):
            current["applied"] = line[len("- Applied:") :].strip()
        elif line.startswith("- Recommendations:"):
            current["recommendations_inline"] = line[len("- Recommendations:") :].strip()
        elif version == "1.1.0" and line.startswith("- Model:"):
            value = line[len("- Model:"):].strip()
            # Per DEC-8 line 244: "- Model: (none)" literal is forbidden for
            # writers; defense-in-depth coerces it + empty value → None so the
            # placeholder never leaks as a string into downstream consumers.
            current["bullet_model"] = value if (value and value != "(none)") else None
        elif line.startswith("  - "):
            current["recommendations"].append(line[4:].strip())
    if current is not None:
        entries.append(current)
    anchors = _parse_compacted_history_anchors(body)
    return {"entries": entries, "anchors": anchors}


def _entry_summary_line(entry: dict) -> str:
    """Produce the one-liner under `### /skill — date`.

    Per learning-system.md §State Rendering: "One-line summary from the
    entry's Applied or Detected field" — goldens consistently use Applied
    verbatim (including `(none)` when nothing was applied), so we return
    Applied whenever it is populated. Detected is a secondary fallback for
    the edge case where an entry has no Applied line at all."""
    applied = entry.get("applied")
    if applied is not None:
        return applied.strip() or "(none)"
    detected = entry.get("detected")
    if detected is not None:
        return detected.strip() or "(none)"
    return "(none)"


# ---------------------------------------------------------------------------
# Phase 0 — Step 0.5 (8-phase clean)
# ---------------------------------------------------------------------------


def _state_root(ctx: RunContext) -> Path:
    """Canonical state directory: work_dir/local/ OR work_dir/ for the
    `migration` fixture (flat layout matching Task 5 golden).
    Determined by golden layout, since the fixture contract's golden is
    the source of truth.

    Local lane (Task 7 parser robustness cases): names of the form
    `case-XX` also use the flat work_dir layout — they test the migration
    parser in isolation and do not simulate a full project workspace."""
    if ctx.fixture_name == "migration":
        return ctx.work_dir
    if ctx.fixture_name.startswith("case-"):
        return ctx.work_dir
    return ctx.work_dir / "local"


def _detect_legacy_md(state_root: Path) -> list[Path]:
    """Scan for legacy project-profile.md + latest-*.md files."""
    if not state_root.exists():
        return []
    legacy = []
    pp = state_root / "project-profile.md"
    if pp.exists():
        legacy.append(pp)
    for p in sorted(state_root.glob("latest-*.md")):
        legacy.append(p)
    return legacy


def _unique_backup_dir(state_root: Path, ts_label: str) -> Path:
    base = state_root / "legacy-backup" / ts_label
    if not base.exists():
        return base
    n = 2
    while True:
        candidate = state_root / "legacy-backup" / f"{ts_label}-{n}"
        if not candidate.exists():
            return candidate
        n += 1


def step_0_5(ctx: RunContext, state: WorkspaceState) -> WorkspaceState:
    """8-phase clean Step 0.5 (Task 3 mechanism; Task 6 verifier mirror).

    Phases:
    1. Acquire state-mutation lock (abort_immediately behavior).
    2. Classify canonical files (absent | present-valid | present-corrupt).
    3. Routing: all valid -> jump to 6; any missing/corrupt -> 4.
    4. Recover per-file from legacy MD (resolve legacy ids via registry aliases);
       fallback to empty canonicals on parse failure.
    5. Quarantine ALL examined legacy MD (success or failure) to legacy-backup.
    6. Regenerate/validate state-summary (mtime-based).
    7. (Optional) Migration notice. CI smoke does not print.
    8. Release lock.
    """
    state_root = _state_root(ctx)
    state_root.mkdir(parents=True, exist_ok=True)

    # Lock lives at work_dir/local/.state.lock (or work_dir/.state.lock for migration).
    lock_path = state_root / ".state.lock"

    # Phase 1
    acquire_lock(lock_path, "abort_immediately", ctx.pinned_utc)

    try:
        registry_by_key = load_registry(REGISTRY_PATH)

        # Phase 2 — classify canonicals
        profile_path = state_root / "profile.json"
        recs_path = state_root / "recommendations.json"
        changelog_path = state_root / "config-changelog.md"

        def _try_load_json(path: Path) -> tuple[str, dict | None]:
            if not path.exists():
                return ("absent", None)
            try:
                obj = json.loads(path.read_text(encoding="utf-8"))
                return ("present-valid", obj)
            except (OSError, json.JSONDecodeError):
                return ("present-corrupt", None)

        profile_status, profile_obj = _try_load_json(profile_path)
        recs_status, recs_obj = _try_load_json(recs_path)

        # Phase 2 (legacy)
        legacy_files = _detect_legacy_md(state_root)
        state.examined_legacy_md = [str(p) for p in legacy_files]

        # Phase 3/4/5
        need_recovery = (
            profile_status != "present-valid"
            or recs_status != "present-valid"
            or bool(legacy_files)
        )

        backup_dir: Path | None = None
        if need_recovery:
            # Build quarantine directory using pinned UTC with filesystem-safe
            # format: "2026-04-14T13-42-09Z" (colons -> dashes).
            ts_label = ctx.pinned_utc.replace(":", "-")
            backup_dir = _unique_backup_dir(state_root, ts_label)

            # Phase 4: per-file recovery
            legacy_profile_md = state_root / "project-profile.md"
            legacy_audit_md = state_root / "latest-audit.md"
            legacy_secure_md = state_root / "latest-secure.md"

            if profile_status != "present-valid":
                # Move corrupt canonical aside BEFORE overwriting.
                if profile_status == "present-corrupt":
                    backup_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(profile_path), str(backup_dir / "profile.json"))
                if legacy_profile_md.exists():
                    try:
                        profile_obj = parse_profile_md(
                            legacy_profile_md.read_text(encoding="utf-8"),
                            "package.json",
                            ctx.pinned_utc,
                        )
                    except Exception:
                        profile_obj = _empty_profile(ctx.pinned_utc)
                else:
                    profile_obj = _empty_profile(ctx.pinned_utc)
                atomic_write_json(profile_path, profile_obj)

            if recs_status != "present-valid":
                if recs_status == "present-corrupt":
                    backup_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(recs_path), str(backup_dir / "recommendations.json"))
                # Aggregate from every latest-*.md present.
                merged: list[dict] = []
                for legacy_md in [legacy_audit_md, legacy_secure_md]:
                    if legacy_md.exists():
                        skill_name = legacy_md.stem.split("latest-", 1)[1]
                        try:
                            recs_list = parse_latest_md(
                                legacy_md.read_text(encoding="utf-8"),
                                skill_name,
                                ctx.pinned_utc,
                                registry_by_key,
                            )
                            merged.extend(recs_list)
                        except Exception:
                            pass
                recs_obj = {
                    "schema_version": "1.0.0",
                    "metadata": {"last_updated": ctx.pinned_utc},
                    "recommendations": merged,
                }
                atomic_write_json(recs_path, recs_obj)

            # Phase 5: quarantine EVERY examined legacy MD file.
            if legacy_files:
                backup_dir.mkdir(parents=True, exist_ok=True)
                for src in legacy_files:
                    dst = backup_dir / src.name
                    shutil.move(str(src), str(dst))

        # Populate state.
        state.profile = profile_obj
        state.recommendations = recs_obj
        if changelog_path.exists():
            state.changelog = changelog_path.read_text(encoding="utf-8")

        # Phase 6: render/regen state-summary.md.
        if state.profile is not None and state.recommendations is not None:
            summary = render_state_summary(
                state.profile, state.recommendations, state.changelog, ctx
            )
            atomic_write_text(state_root / "state-summary.md", summary)
            state.state_summary = summary

        # Phase 7: migration notice intentionally not printed in CI smoke.

    finally:
        # Phase 8
        release_lock(lock_path)

    return state


def _empty_profile(pinned_utc: str) -> dict:
    return {
        "schema_version": "1.0.0",
        "metadata": {
            "generated_by": "guardians-of-the-claude",
            "last_updated": pinned_utc,
            "source_files_checked": [],
        },
    }


def _empty_recommendations(pinned_utc: str) -> dict:
    return {
        "schema_version": "1.0.0",
        "metadata": {"last_updated": pinned_utc},
        "recommendations": [],
    }


# ---------------------------------------------------------------------------
# Merge rules (merge_rules.md)
# ---------------------------------------------------------------------------


PROFILE_KEY_ORDER = [
    "schema_version",
    "metadata",
    "runtime_and_language",
    "framework_and_libraries",
    "package_management",
    "testing",
    "build_and_dev",
    "project_structure",
    "claude_code_configuration_state",
]

CCS_KEY_ORDER = [
    "model",
    "scoring_model_ack",
    "claude_md",
    "settings_json",
    "rules_count",
    "agents_count",
    "hooks_count",
    "mcp_servers_count",
]


def _ordered_profile(obj: dict) -> dict:
    """Return a new dict with keys in canonical schema order."""
    ordered = {}
    for k in PROFILE_KEY_ORDER:
        if k in obj:
            ordered[k] = obj[k]
    for k, v in obj.items():
        if k not in ordered:
            ordered[k] = v
    # Nested ccs key order
    ccs = ordered.get("claude_code_configuration_state")
    if isinstance(ccs, dict):
        ccs_ordered = {}
        for k in CCS_KEY_ORDER:
            if k in ccs:
                ccs_ordered[k] = ccs[k]
        for k, v in ccs.items():
            if k not in ccs_ordered:
                ccs_ordered[k] = v
        ordered["claude_code_configuration_state"] = ccs_ordered
    return ordered


def merge_profile(current: dict | None, delta: dict, skill: str) -> dict:
    """Section ownership per merge_rules.md.
    Always re-order result keys to canonical schema order (so merged profiles
    don't drift between skills which may supply sections in different orders)."""
    owned_by_create_audit = [
        "runtime_and_language",
        "framework_and_libraries",
        "package_management",
        "testing",
        "build_and_dev",
        "project_structure",
    ]
    if current is None:
        current = _empty_profile(delta.get("metadata", {}).get("last_updated", ""))
    merged = json.loads(json.dumps(current))  # deep copy via JSON
    merged["schema_version"] = "1.1.0"
    delta_meta = delta.get("metadata", {})
    existing_meta = merged.setdefault("metadata", {})
    existing_meta["generated_by"] = "guardians-of-the-claude"
    existing_meta["last_updated"] = delta_meta.get("last_updated", existing_meta.get("last_updated"))
    existing_sources = existing_meta.get("source_files_checked") or []
    for s in delta_meta.get("source_files_checked", []):
        if s not in existing_sources:
            existing_sources.append(s)
    existing_meta["source_files_checked"] = existing_sources

    if skill in ("create", "audit"):
        for k in owned_by_create_audit:
            if k in delta:
                merged[k] = delta[k]
        if "claude_code_configuration_state" in delta:
            ccs_d = delta["claude_code_configuration_state"]
            ccs_m = merged.setdefault("claude_code_configuration_state", {})
            if "claude_md" in ccs_d:
                ccs_m["claude_md"] = ccs_d["claude_md"]
            for kk in ("rules_count", "agents_count", "hooks_count", "mcp_servers_count"):
                if kk in ccs_d:
                    ccs_m[kk] = ccs_d[kk]
            if skill == "create" and "settings_json" in ccs_d:
                ccs_m["settings_json"] = ccs_d["settings_json"]
            # First-run initialization: /audit populates settings_json when
            # there is no prior value to preserve. /secure owns edits; /audit
            # owns initial detection when current state is missing the field.
            if skill == "audit" and "settings_json" in ccs_d and "settings_json" not in ccs_m:
                ccs_m["settings_json"] = ccs_d["settings_json"]
            # /audit is the authoritative writer for model and scoring_model_ack.
            if skill == "audit":
                if "model" in ccs_d:
                    ccs_m["model"] = ccs_d["model"]
                if "scoring_model_ack" in ccs_d:
                    ccs_m["scoring_model_ack"] = ccs_d["scoring_model_ack"]
    if skill == "secure":
        if "claude_code_configuration_state" in delta:
            ccs_d = delta["claude_code_configuration_state"]
            ccs_m = merged.setdefault("claude_code_configuration_state", {})
            if "settings_json" in ccs_d:
                ccs_m["settings_json"] = ccs_d["settings_json"]
            # C2 (T7): /secure co-owns counts per merge_rules.md §profile.json
            for count_key in ("rules_count", "agents_count", "hooks_count", "mcp_servers_count"):
                if count_key in ccs_d:
                    ccs_m[count_key] = ccs_d[count_key]

    if skill == "optimize":
        if "claude_code_configuration_state" in delta:
            ccs_d = delta["claude_code_configuration_state"]
            ccs_m = merged.setdefault("claude_code_configuration_state", {})
            # C2 (T7): /optimize co-owns counts per merge_rules.md §profile.json;
            # must NOT touch settings_json (owned by /secure) or claude_md (owned by /create+/audit).
            for count_key in ("rules_count", "agents_count", "hooks_count", "mcp_servers_count"):
                if count_key in ccs_d:
                    ccs_m[count_key] = ccs_d[count_key]

    return _ordered_profile(merged)


def merge_recommendations(current: dict | None, delta_recs: list[dict], pinned_utc: str) -> dict:
    """Merge by canonical id; preserve untouched; refresh metadata.last_updated."""
    if current is None:
        current = _empty_recommendations(pinned_utc)
    by_id: dict[str, dict] = {
        r["id"]: dict(r) for r in current.get("recommendations", [])
    }
    for delta in delta_recs:
        rid = delta["id"]
        if rid in by_id:
            existing = by_id[rid]
            existing["status"] = delta.get("status", existing["status"])
            existing["pending_count"] = delta.get("pending_count", existing["pending_count"])
            existing["last_seen"] = delta.get("last_seen", existing["last_seen"])
            if "description" in delta:
                existing["description"] = delta["description"]
            if delta.get("status") == "RESOLVED":
                existing["resolved_by"] = delta.get("resolved_by")
            if delta.get("status") == "DECLINED":
                existing["declined_reason"] = delta.get("declined_reason")
        else:
            by_id[rid] = dict(delta)

    merged = {
        "schema_version": "1.0.0",
        "metadata": {"last_updated": pinned_utc},
        "recommendations": list(by_id.values()),
    }
    return merged


def _changelog_with_entry(current_text: str | None, entry_md: str, entry_count_delta: int = 1) -> str:
    """Append entry_md to Recent Activity; bump entry_count by entry_count_delta.

    Phase 1 scope: merge_rules.md §config-changelog.md (same-day semantics)
    requires in-place update if an entry for this skill already exists on
    today's date. No Phase 1 fixture triggers this branch (warm-start's
    prior entry is on a different date). Implement when a Phase 2 fixture
    runs the same skill twice in one pinned-UTC session.
    """
    if current_text is None:
        current_text = (
            "---\n"
            "title: Configuration Changelog\n"
            "description: Decision journal for Claude Code configuration changes\n"
            "version: 1.1.0\n"
            "compacted_at: never\n"
            "entry_count: 0\n"
            "---\n\n"
            "## Compacted History\n\n(none)\n\n"
            "## Recent Activity\n\n"
        )
    # Update entry_count.
    new_text = current_text
    lines = new_text.splitlines()
    for idx, line in enumerate(lines):
        if line.startswith("entry_count:"):
            try:
                n = int(line.split(":")[1].strip())
            except ValueError:
                n = 0
            lines[idx] = f"entry_count: {n + entry_count_delta}"
            break
    new_text = "\n".join(lines)
    if not new_text.endswith("\n"):
        new_text += "\n"
    # Append the new entry to tail.
    if not new_text.endswith("\n\n"):
        new_text += "\n"
    # Ensure trailing newline after append.
    new_text = new_text.rstrip("\n") + "\n\n" + entry_md.rstrip("\n") + "\n"
    return new_text


def parse_last_changelog_entry_model(changelog_text: str | None) -> str | None:
    """Return model string from the most recent Recent Activity entry's
    `- Model:` bullet, or None when no bullet exists (pre-v1.1.0 entry OR
    delta-omitted v1.1.0 entry OR empty changelog)."""
    if not changelog_text:
        return None
    lines = changelog_text.splitlines()
    last_heading_idx = -1
    for idx in range(len(lines) - 1, -1, -1):
        if lines[idx].startswith("### ") and " — /" in lines[idx]:
            last_heading_idx = idx
            break
    if last_heading_idx == -1:
        return None
    for idx in range(last_heading_idx + 1, len(lines)):
        line = lines[idx]
        if line.startswith("### "):
            break
        if line.startswith("- Model: "):
            return line[len("- Model: "):].strip()
    return None


# ---------------------------------------------------------------------------
# Skill handlers (reference implementations — mimic Final Phase output)
# ---------------------------------------------------------------------------


def _final_phase_write(ctx: RunContext, state: WorkspaceState) -> None:
    """Write four canonical files + state-summary under real lock (wait_30s)."""
    state_root = _state_root(ctx)
    lock_path = state_root / ".state.lock"
    acquire_lock(lock_path, "wait_30s", ctx.pinned_utc)
    try:
        if state.profile is not None:
            atomic_write_json(state_root / "profile.json", state.profile)
        if state.recommendations is not None:
            atomic_write_json(state_root / "recommendations.json", state.recommendations)
        if state.changelog is not None:
            atomic_write_text(state_root / "config-changelog.md", state.changelog)
        if state.profile is not None and state.recommendations is not None:
            summary = render_state_summary(
                state.profile, state.recommendations, state.changelog, ctx
            )
            atomic_write_text(state_root / "state-summary.md", summary)
            state.state_summary = summary
    finally:
        release_lock(lock_path)


def handle_create(ctx: RunContext, state: WorkspaceState) -> WorkspaceState:
    """First-time scaffold for beginner-path fixture.

    Detects Next.js + React from package.json; writes CLAUDE.md + .claude/settings.json;
    initializes profile.json + recommendations.json + config-changelog.md."""
    pkg_path = ctx.work_dir / "package.json"
    package = json.loads(pkg_path.read_text(encoding="utf-8")) if pkg_path.exists() else {}
    deps = package.get("dependencies", {})

    framework = None
    ui = None
    if "next" in deps:
        framework = "Next.js 15"
    if "react" in deps:
        ui = "React 19"

    profile_delta = {
        "schema_version": "1.0.0",
        "metadata": {
            "last_updated": ctx.pinned_utc,
            "source_files_checked": ["package.json"],
        },
        "runtime_and_language": {
            "runtime": "Node.js",
            "language": None,
            "module_system": None,
        },
        "framework_and_libraries": {
            "framework": framework,
            "ui": ui,
            "styling": None,
        },
        "package_management": {"manager": "npm", "lock_file": None},
        "testing": {"unit": None, "e2e": None},
        "build_and_dev": {"bundler": None, "linter": None, "formatter": None},
        "project_structure": {
            "type": "single_project",
            "source_convention": None,
            "key_directories": [],
        },
        "claude_code_configuration_state": {
            "claude_md": {"exists": True, "section_count": 5},
            "settings_json": {"exists": True, "has_permissions": True},
            "rules_count": 0,
            "agents_count": 0,
            "hooks_count": 0,
            "mcp_servers_count": 0,
        },
    }
    state.profile = merge_profile(state.profile, profile_delta, "create")
    state.recommendations = merge_recommendations(
        state.recommendations, [], ctx.pinned_utc
    )

    # Changelog entry for /create
    date = ctx.pinned_utc.split("T")[0]
    create_entry = (
        f"### {date} — /create\n"
        f"- Detected: Next.js 15 (first scan)\n"
        f"- Profile updated: generated\n"
        f"- Applied: CLAUDE.md + settings.json scaffold\n"
        f"- Resolved: (none)\n"
        f"- Recommendations: (none)"
    )
    state.changelog = _changelog_with_entry(state.changelog, create_entry)

    # Scaffold CLAUDE.md + .claude/settings.json (write separately — not under state lock
    # since they're not canonical state files).
    claude_md = (
        "# Project Overview\n\n"
        "TaskFlow is a Next.js web application (App Router). React 19 frontend.\n"
        "Starter scaffold generated by /guardians-of-the-claude:create — flesh\n"
        "out sections as the project grows.\n\n"
        "## Build & Run\n\n"
        "npm run dev          # starts dev server on :3000\n"
        "npm run build        # production build\n"
        "npm start            # serves the production build\n\n"
        "## Testing\n\n"
        "Not yet configured. Add a test runner (Vitest / Jest / Playwright) and\n"
        "update this section when tests exist.\n\n"
        "## Code Style & Conventions\n\n"
        "- Follow Next.js App Router conventions (app/ directory, server\n"
        "  components by default, \"use client\" only when needed)\n"
        "- Use TypeScript strict mode when .ts/.tsx files are added\n"
        "- Keep shared logic in src/lib/; keep route handlers thin\n\n"
        "## Important Context\n\n"
        "- Starter configuration — no custom rules, hooks, or agents yet\n"
        "- Run /guardians-of-the-claude:audit periodically to detect drift\n"
        "- Run /guardians-of-the-claude:secure when adding secrets/env handling\n"
    )
    atomic_write_text(ctx.work_dir / "CLAUDE.md", claude_md)

    settings = {
        "$schema": "https://json.schemastore.org/claude-code-settings.json",
        "permissions": {
            "allow": [
                "Bash(npm run dev)",
                "Bash(npm run build)",
                "Bash(npm start)",
                "Bash(git diff *)",
                "Bash(git log *)",
            ],
            "deny": [
                "Read(./.env)",
                "Read(./.env.*)",
                "Edit(./.env)",
                "Edit(./.env.*)",
                "Write(./.env)",
                "Write(./.env.*)",
                "Read(./secrets/)",
                "Edit(./secrets/)",
                "Write(./secrets/)",
            ],
        },
    }
    atomic_write_json(ctx.work_dir / ".claude" / "settings.json", settings)

    _final_phase_write(ctx, state)
    return state


def handle_audit(ctx: RunContext, state: WorkspaceState) -> WorkspaceState:
    """Full profile regenerate + recommendation merge.

    Behavior differs per fixture because the /audit skill's detection logic
    is context-dependent. This handler mimics Final Phase output for the
    three /audit-exercising fixtures (migration, beginner-path second run,
    warm-start, monorepo)."""
    date = ctx.pinned_utc.split("T")[0]
    # Build a profile_delta from what /audit would detect in the workspace.
    profile_delta = _audit_detect_profile(ctx)
    state.profile = merge_profile(state.profile, profile_delta, "audit")
    state.recommendations = merge_recommendations(
        state.recommendations, [], ctx.pinned_utc
    )

    # Per-fixture changelog entry (mimics `/audit` output).
    if ctx.fixture_name == "beginner-path":
        entry = (
            f"### {date} — /audit\n"
            f"- Model: {state.profile['claude_code_configuration_state']['model']}\n"
            f"- Detected: (none)\n"
            f"- Profile updated: (none)\n"
            f"- Applied: (none)\n"
            f"- Resolved: (none)\n"
            f"- Recommendations: (none)"
        )
        state.changelog = _changelog_with_entry(state.changelog, entry)
    elif ctx.fixture_name == "warm-start":
        # warm-start appends a new entry for 2026-04-14 /audit with 2x pending.
        entry = (
            f"### {date} — /audit\n"
            f"- Model: {state.profile['claude_code_configuration_state']['model']}\n"
            f"- Detected: (none)\n"
            f"- Profile updated: (none)\n"
            f"- Applied: (none)\n"
            f"- Resolved: (none)\n"
            f"- Recommendations:\n"
            f"  - Split CLAUDE.md into rule files — PENDING (2x)"
        )
        state.changelog = _changelog_with_entry(state.changelog, entry)
    elif ctx.fixture_name == "monorepo":
        entry = (
            f"### {date} — /audit\n"
            f"- Model: {state.profile['claude_code_configuration_state']['model']}\n"
            f"- Detected: monorepo layout (2 workspaces)\n"
            f"- Profile updated: generated\n"
            f"- Applied: (none)\n"
            f"- Resolved: (none)\n"
            f"- Recommendations: (none)"
        )
        state.changelog = _changelog_with_entry(state.changelog, entry)
        # Also emit monorepo audit-output.md (disclosure-only).
        audit_output = (
            "# /audit — Monorepo Run\n\n"
            "Root `CLAUDE.md` detected; 2 workspace packages contain their own `CLAUDE.md`.\n\n"
            "## Additional CLAUDE.md Files\n\n"
            "Disclosure only — per-package scoring is scheduled for a future audit\n"
            "release (see `docs/ROADMAP.md` \"Audit v4 Phase 2\").\n\n"
            "- packages/api/CLAUDE.md (9 lines)\n"
            "- packages/web/CLAUDE.md (8 lines)\n"
        )
        atomic_write_text(ctx.work_dir / "audit-output.md", audit_output)
    # migration fixture: the /audit run doesn't add a changelog entry —
    # Step 0.5 already built profile/recs from legacy; no /audit-level change.

    _final_phase_write(ctx, state)
    return state


def _audit_detect_profile(ctx: RunContext) -> dict:
    """Per-fixture deterministic profile detection (reference implementation).

    This mimics what /audit would emit when scanning the workspace.
    Phase 1 scope: 4 fixtures hardcoded; broader heuristics are out of scope
    per Phase 1 Task 6 (verifier is a REFERENCE implementation of current
    output, not a fully general /audit simulator)."""
    name = ctx.fixture_name
    if name == "migration":
        return {
            "metadata": {
                "last_updated": ctx.pinned_utc,
                "source_files_checked": ["package.json", "tsconfig.json"],
            },
            "runtime_and_language": {
                "runtime": "Node.js 22.x",
                "language": "TypeScript 5.7",
                "module_system": "ESM",
            },
            "framework_and_libraries": {
                "framework": "Next.js 15 (App Router)",
                "ui": "React 19",
                "styling": "Tailwind CSS v4",
            },
            "package_management": {"manager": "pnpm", "lock_file": "pnpm-lock.yaml"},
            "testing": {"unit": "Vitest", "e2e": None},
            "build_and_dev": {
                "bundler": "Turbopack",
                "linter": "ESLint 9 (flat config)",
                "formatter": "Prettier",
            },
            "project_structure": {
                "type": "single_project",
                "source_convention": "src/",
                "key_directories": ["src/app/", "src/components/", "src/lib/"],
            },
            "claude_code_configuration_state": {
                "claude_md": {"exists": True, "section_count": 5},
                "settings_json": {"exists": True, "has_permissions": True},
                "rules_count": 0,
                "agents_count": 0,
                "hooks_count": 0,
                "mcp_servers_count": 0,
                "model": "claude-opus-4-7",
                "scoring_model_ack": {
                    "version": "audit-score-v4.0.0",
                    "seen_count": 0,
                },
            },
        }
    if name == "warm-start":
        return {
            "metadata": {
                "last_updated": ctx.pinned_utc,
                "source_files_checked": ["package.json", "tsconfig.json"],
            },
            "runtime_and_language": {
                "runtime": "Node.js 22.x",
                "language": "TypeScript 5.7",
                "module_system": "ESM",
            },
            "framework_and_libraries": {
                "framework": "Next.js 15 (App Router)",
                "ui": "React 19",
                "styling": "Tailwind CSS v4",
            },
            "package_management": {"manager": "pnpm", "lock_file": "pnpm-lock.yaml"},
            "testing": {"unit": "Vitest", "e2e": "Playwright"},
            "build_and_dev": {
                "bundler": "Turbopack",
                "linter": "ESLint 9",
                "formatter": "Prettier",
            },
            "project_structure": {
                "type": "single_project",
                "source_convention": "src/",
                "key_directories": ["src/app/", "src/components/", "src/lib/"],
            },
            "claude_code_configuration_state": {
                "claude_md": {"exists": True, "section_count": 5},
                "settings_json": {"exists": True, "has_permissions": True},
                "rules_count": 2,
                "agents_count": 1,
                "hooks_count": 2,
                "mcp_servers_count": 0,
                "model": "claude-opus-4-7",
                "scoring_model_ack": {
                    "version": "audit-score-v4.0.0",
                    "seen_count": 0,
                },
            },
        }
    if name == "monorepo":
        return {
            "metadata": {
                "last_updated": ctx.pinned_utc,
                "source_files_checked": [
                    "package.json",
                    "packages/api/package.json",
                    "packages/web/package.json",
                ],
            },
            "runtime_and_language": {
                "runtime": "Node.js",
                "language": None,
                "module_system": None,
            },
            "framework_and_libraries": {
                "framework": "Next.js 15 (web) / Express 4 (api)",
                "ui": "React 19",
                "styling": None,
            },
            "package_management": {"manager": "pnpm", "lock_file": None},
            "testing": {"unit": None, "e2e": None},
            "build_and_dev": {"bundler": None, "linter": None, "formatter": None},
            "project_structure": {
                "type": "monorepo",
                "source_convention": "packages/",
                "key_directories": ["packages/api/", "packages/web/"],
            },
            "claude_code_configuration_state": {
                "claude_md": {"exists": True, "section_count": 5},
                "settings_json": {"exists": False, "has_permissions": False},
                "rules_count": 0,
                "agents_count": 0,
                "hooks_count": 0,
                "mcp_servers_count": 0,
                "model": "claude-opus-4-7",
                "scoring_model_ack": {
                    "version": "audit-score-v4.0.0",
                    "seen_count": 0,
                },
            },
        }
    # beginner-path: /audit after /create leaves profile unchanged (same detection).
    if name == "beginner-path":
        return {
            "metadata": {
                "last_updated": ctx.pinned_utc,
                "source_files_checked": ["package.json"],
            },
            "runtime_and_language": {
                "runtime": "Node.js",
                "language": None,
                "module_system": None,
            },
            "framework_and_libraries": {
                "framework": "Next.js 15",
                "ui": "React 19",
                "styling": None,
            },
            "package_management": {"manager": "npm", "lock_file": None},
            "testing": {"unit": None, "e2e": None},
            "build_and_dev": {"bundler": None, "linter": None, "formatter": None},
            "project_structure": {
                "type": "single_project",
                "source_convention": None,
                "key_directories": [],
            },
            "claude_code_configuration_state": {
                "claude_md": {"exists": True, "section_count": 5},
                "settings_json": {"exists": True, "has_permissions": True},
                "rules_count": 0,
                "agents_count": 0,
                "hooks_count": 0,
                "mcp_servers_count": 0,
                "model": "claude-opus-4-7",
                "scoring_model_ack": {
                    "version": "audit-score-v4.0.0",
                    "seen_count": 0,
                },
            },
        }
    raise KeyError(f"no audit detection preset for fixture {name!r}")


def handle_secure(ctx: RunContext, state: WorkspaceState) -> WorkspaceState:
    """Process /secure fixture run: profile merge + changelog + recommendations.

    Per-fixture detection presets live in _secure_detect_profile. Phase 1
    FIXTURE_SCENARIOS does not include /secure; Phase 2a T7 atomic runners
    (ci/scripts/t7_secure_*_check.py) exercise /secure via SKILL_HANDLERS
    monkey-patch for fixture-specific behavior. Adding a /secure entry to
    FIXTURE_SCENARIOS requires adding a per-fixture branch in
    _secure_detect_profile."""
    date = ctx.pinned_utc.split("T")[0]
    profile_delta = _secure_detect_profile(ctx)
    state.profile = merge_profile(state.profile, profile_delta, "secure")
    state.recommendations = merge_recommendations(
        state.recommendations, [], ctx.pinned_utc
    )
    current_model = state.profile.get("claude_code_configuration_state", {}).get("model")
    previous_model = parse_last_changelog_entry_model(state.changelog)
    model_bullet = (
        f"- Model: {current_model}\n"
        if current_model is not None and current_model != previous_model
        else ""
    )
    entry = (
        f"### {date} — /secure\n"
        f"{model_bullet}"
        f"- Detected: fixture-driven\n"
        f"- Profile updated: claude_code_configuration_state\n"
        f"- Applied: (fixture-specific)\n"
        f"- Resolved: (none)\n"
        f"- Recommendations: (none)"
    )
    state.changelog = _changelog_with_entry(state.changelog, entry)
    _final_phase_write(ctx, state)
    return state


def _secure_detect_profile(ctx: RunContext) -> dict:
    """Per-fixture /secure deltas. Add branches as Phase 2+ fixtures land."""
    raise KeyError(f"no /secure detection preset for fixture {ctx.fixture_name!r}")


def handle_optimize(ctx: RunContext, state: WorkspaceState) -> WorkspaceState:
    """Process /optimize fixture run: counts merge + changelog + recommendations.

    Per-fixture detection presets live in _optimize_detect_profile. Phase 1
    FIXTURE_SCENARIOS does not include /optimize; Phase 2a T7 atomic runners
    (ci/scripts/t7_optimize_e2e_check.py) exercise /optimize via SKILL_HANDLERS
    monkey-patch. Adding an /optimize entry to FIXTURE_SCENARIOS requires
    adding a per-fixture branch in _optimize_detect_profile."""
    date = ctx.pinned_utc.split("T")[0]
    profile_delta = _optimize_detect_profile(ctx)
    state.profile = merge_profile(state.profile, profile_delta, "optimize")
    state.recommendations = merge_recommendations(
        state.recommendations, [], ctx.pinned_utc
    )
    current_model = state.profile.get("claude_code_configuration_state", {}).get("model")
    previous_model = parse_last_changelog_entry_model(state.changelog)
    model_bullet = (
        f"- Model: {current_model}\n"
        if current_model is not None and current_model != previous_model
        else ""
    )
    entry = (
        f"### {date} — /optimize\n"
        f"{model_bullet}"
        f"- Detected: fixture-driven\n"
        f"- Profile updated: counts\n"
        f"- Applied: (fixture-specific)\n"
        f"- Resolved: (none)\n"
        f"- Recommendations: (none)"
    )
    state.changelog = _changelog_with_entry(state.changelog, entry)
    _final_phase_write(ctx, state)
    return state


def _optimize_detect_profile(ctx: RunContext) -> dict:
    """Per-fixture /optimize deltas. Add branches as Phase 2+ fixtures land."""
    raise KeyError(f"no /optimize detection preset for fixture {ctx.fixture_name!r}")


SKILL_HANDLERS = {
    "create": handle_create,
    "audit": handle_audit,
    "secure": handle_secure,
    "optimize": handle_optimize,
}

FIXTURE_SCENARIOS = {
    "migration": {"skill_sequence": ["audit"], "pre_run": []},
    "beginner-path": {"skill_sequence": ["create", "audit"], "pre_run": []},
    "warm-start": {"skill_sequence": ["audit"], "pre_run": [("touch_older", "local/state-summary.md", "1 day")]},
    "monorepo": {"skill_sequence": ["audit"], "pre_run": []},
}


def apply_pre_run(pre_run, ctx: RunContext) -> None:
    for action in pre_run:
        op = action[0]
        if op == "touch_older":
            rel_path = action[1]
            delta = action[2]
            target = ctx.work_dir / rel_path
            if not target.exists():
                continue
            days = 1
            if delta.endswith("day") or delta.endswith("days"):
                try:
                    days = int(delta.split()[0])
                except ValueError:
                    days = 1
            dt = datetime.fromisoformat(ctx.pinned_utc.replace("Z", "+00:00"))
            past = dt.timestamp() - days * 86400
            os.utime(target, (past, past))


# ---------------------------------------------------------------------------
# Semantic assertions (run BEFORE byte diff per Codex Q5 Pitfall 2)
# ---------------------------------------------------------------------------


def _load_schema(name: str) -> dict:
    return json.loads((SCHEMAS_DIR / name).read_text(encoding="utf-8"))


def assert_schema_valid(ctx: RunContext, state: WorkspaceState) -> list[str]:
    failures = []
    # Dispatch profile schema wrapper by declared `schema_version`.
    # profile.schema.json was factored into base + versioned wrappers in v2.12.0.
    # v2.12.1 adds v1.1.0 dispatch alongside the legacy v1.0.0 path.
    from referencing import Registry, Resource  # noqa: PLC0415
    base_schema = _load_schema("profile.schema.base.json")
    registry = Registry().with_resources(
        [("profile.schema.base.json", Resource.from_contents(base_schema))]
    )

    version_to_wrapper = {
        "1.0.0": "profile.schema.v1.0.0.json",
        "1.1.0": "profile.schema.v1.1.0.json",
    }

    recs_schema = _load_schema("recommendations.schema.json")
    if state.profile is None:
        failures.append("profile.json was not written")
    else:
        declared_version = state.profile.get("schema_version")
        if declared_version not in version_to_wrapper:
            failures.append(
                f"profile.json schema_version '{declared_version}' not dispatchable; "
                f"expected one of {sorted(version_to_wrapper)}"
            )
        else:
            profile_schema = _load_schema(version_to_wrapper[declared_version])
            try:
                jsonschema.Draft202012Validator(profile_schema, registry=registry).validate(state.profile)
            except jsonschema.ValidationError as e:
                failures.append(f"profile.json schema invalid ({declared_version}): {e.message}")
    if state.recommendations is None:
        failures.append("recommendations.json was not written")
    else:
        try:
            jsonschema.validate(state.recommendations, recs_schema)
        except jsonschema.ValidationError as e:
            failures.append(f"recommendations.json schema invalid: {e.message}")
    return failures


def assert_registry_lint(ctx: RunContext, state: WorkspaceState) -> list[str]:
    if state.recommendations is None:
        return []
    registry = load_registry(REGISTRY_PATH)
    return check_recommendations(
        state.recommendations.get("recommendations", []), registry
    )


def assert_aliases_never_persist(ctx: RunContext, state: WorkspaceState) -> list[str]:
    """Invariant 2: persisted ids must be canonical keys, not aliases."""
    if state.recommendations is None:
        return []
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    alias_set: set[str] = set()
    for row in data["registry"]:
        alias_set.update(row.get("aliases", []))
    failures = []
    for r in state.recommendations.get("recommendations", []):
        if r["id"] in alias_set:
            failures.append(
                f"recommendation id '{r['id']}' is a registry alias; "
                "aliases must never be persisted forward"
            )
    return failures


def assert_legacy_quarantined(ctx: RunContext, state: WorkspaceState, scenario: dict) -> list[str]:
    """Invariant 1: legacy MD must not coexist with canonical state.

    If Step 0.5 saw any legacy MD files, they must now live under
    legacy-backup/<timestamp>/ and NOT at top-level of state_root."""
    if not state.examined_legacy_md:
        return []
    state_root = _state_root(ctx)
    failures = []
    for p_str in state.examined_legacy_md:
        name = Path(p_str).name
        still = state_root / name
        if still.exists():
            failures.append(f"legacy MD '{name}' still at top-level after Step 0.5")
    backup_dirs = sorted((state_root / "legacy-backup").glob("*")) if (state_root / "legacy-backup").exists() else []
    if not backup_dirs:
        failures.append("legacy MD examined but no legacy-backup directory created")
    else:
        # At least one backup dir must contain each examined file.
        for p_str in state.examined_legacy_md:
            name = Path(p_str).name
            if not any((bd / name).exists() for bd in backup_dirs):
                failures.append(f"legacy MD '{name}' not present under legacy-backup/")
    return failures


def assert_summary_derived_from_sources(ctx: RunContext, state: WorkspaceState) -> list[str]:
    """Invariant 4: state-summary.md must equal the renderer's output over
    current profile + recommendations + changelog."""
    if state.profile is None or state.recommendations is None:
        return []
    state_root = _state_root(ctx)
    summary_path = state_root / "state-summary.md"
    if not summary_path.exists():
        return ["state-summary.md not present"]
    on_disk = summary_path.read_text(encoding="utf-8")
    expected = render_state_summary(
        state.profile, state.recommendations, state.changelog, ctx
    )
    if on_disk != expected:
        return ["state-summary.md not derived from current sources (in-memory re-render mismatch)"]
    return []


# ---------------------------------------------------------------------------
# Byte diff (last gate)
# ---------------------------------------------------------------------------


def byte_diff_tree(actual: Path, golden: Path, input_dir: Path | None = None) -> str:
    """Recursive byte-for-byte comparison of directory trees.

    Compares every file present in golden against the same path in actual.
    Extra files in actual are ONLY flagged if they did NOT already exist
    unchanged in the fixture's input/ (the verifier mutates a work-copy of
    input/, so input source files like package.json are allowed to linger
    unchanged — goldens only capture the skill-produced artifacts).

    Returns "" if equal, else a concise multi-line diff summary."""
    actual_files = _collect_files(actual)
    golden_files = _collect_files(golden)
    input_files_unchanged: dict[str, bytes] = {}
    if input_dir is not None:
        for rel in _collect_files(input_dir):
            input_files_unchanged[rel] = (input_dir / rel).read_bytes()

    diffs = []
    missing = sorted(golden_files - actual_files)
    for rel in missing:
        diffs.append(f"missing file (in golden, not in actual): {rel}")

    extra = sorted(actual_files - golden_files)
    for rel in extra:
        actual_bytes = (actual / rel).read_bytes()
        # Allowed: byte-identical carryover from input/ (not touched by verifier).
        if rel in input_files_unchanged and input_files_unchanged[rel] == actual_bytes:
            continue
        diffs.append(f"extra file (in actual, not in golden): {rel}")

    for rel in sorted(actual_files & golden_files):
        a = (actual / rel).read_bytes()
        g = (golden / rel).read_bytes()
        if a != g:
            diffs.append(f"byte mismatch: {rel}")
    return "\n  ".join(diffs) if diffs else ""


def _collect_files(root: Path) -> set[str]:
    """Return set of POSIX-style relative paths for every file under root.
    Excludes .state.lock (lock file is transient and should not be present
    after a successful run, but in case cleanup failed we ignore it)."""
    if not root.exists():
        return set()
    out = set()
    for p in sorted(root.rglob("*")):
        if p.is_file():
            # Skip transient lock file if it leaked.
            if p.name == ".state.lock":
                continue
            rel = p.relative_to(root)
            out.add(rel.as_posix())
    return out


# ---------------------------------------------------------------------------
# Fixture runner
# ---------------------------------------------------------------------------


def load_initial_state(ctx: RunContext) -> WorkspaceState:
    """Load any pre-existing canonical state from a warm-start or similar fixture."""
    state = WorkspaceState()
    state_root = _state_root(ctx)
    profile_path = state_root / "profile.json"
    recs_path = state_root / "recommendations.json"
    changelog_path = state_root / "config-changelog.md"
    summary_path = state_root / "state-summary.md"
    if profile_path.exists():
        try:
            state.profile = json.loads(profile_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            state.profile = None
    if recs_path.exists():
        try:
            state.recommendations = json.loads(recs_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            state.recommendations = None
    if changelog_path.exists():
        state.changelog = changelog_path.read_text(encoding="utf-8")
    if summary_path.exists():
        state.state_summary = summary_path.read_text(encoding="utf-8")
    return state


def run_fixture(
    name: str,
    src_dir: Path | None = None,
    golden_dir: Path | None = None,
    scenario: dict | None = None,
) -> tuple[bool, str]:
    """Run one fixture through Step 0.5 + (optional) skill handlers, then
    assert semantics, then byte-diff work_dir against the frozen target.

    Optional parameters let the local lane (LOCAL_FIXTURES_DIR) reuse
    the CI code path unchanged — each local case provides its own src_dir
    (case/input) and golden_dir (case/expected), and optionally a per-case
    scenario.json (fallback to a migration-only default when absent). All
    5 semantic assertions are shared with the CI lane."""
    if scenario is None:
        scenario = FIXTURE_SCENARIOS[name]
    if src_dir is None:
        src_dir = FIXTURES_DIR / name / "input"
    if golden_dir is None:
        golden_dir = GOLDEN_DIR / name
    with tempfile.TemporaryDirectory() as tmpdir:
        work_dir = Path(tmpdir) / name
        shutil.copytree(src_dir, work_dir)
        ctx = RunContext(
            pinned_utc=os.environ["SMOKE_PINNED_UTC"],
            work_dir=work_dir,
            fixture_name=name,
        )
        apply_pre_run(scenario["pre_run"], ctx)
        state = load_initial_state(ctx)
        state = step_0_5(ctx, state)
        for skill in scenario["skill_sequence"]:
            handler = SKILL_HANDLERS[skill]
            state = handler(ctx, state)

        # SEMANTIC ASSERTIONS BEFORE BYTE DIFF
        failures = []
        failures += assert_schema_valid(ctx, state)
        failures += assert_registry_lint(ctx, state)
        failures += assert_aliases_never_persist(ctx, state)
        failures += assert_legacy_quarantined(ctx, state, scenario)
        failures += assert_summary_derived_from_sources(ctx, state)
        if failures:
            return (False, "semantic: " + "; ".join(failures))

        # BYTE DIFF as last gate
        diff = byte_diff_tree(work_dir, golden_dir, input_dir=src_dir)
        if diff:
            return (False, "byte diff:\n  " + diff)
        return (True, "ok")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


# Default scenario applied to each local (LOCAL_FIXTURES_DIR) case that does
# NOT ship its own scenario.json. Migration-only by design: Task 7 cases
# exercise Step 0.5 (parser robustness) in isolation. Skill handlers rely on
# hardcoded per-fixture presets (FIXTURE_SCENARIOS + _audit_detect_profile)
# and would raise for unknown local case names. A case that needs skill
# execution can override with its own scenario.json.
LOCAL_DEFAULT_SCENARIO = {"skill_sequence": [], "pre_run": []}


def run_local_lane(base: Path) -> int:
    """Iterate case directories under `base` (sorted for deterministic order
    per Primitive 5) and run each through run_fixture. Each case provides
    input/ and expected/; scenario.json is optional. Returns 0 on all-pass."""
    if not base.is_dir():
        print(
            f"[FATAL] LOCAL_FIXTURES_DIR={base} is not a directory",
            file=sys.stderr,
        )
        return 2
    case_dirs = sorted(p for p in base.iterdir() if p.is_dir())
    if not case_dirs:
        print(
            f"[FATAL] LOCAL_FIXTURES_DIR={base} has no case subdirectories",
            file=sys.stderr,
        )
        return 2
    fail_count = 0
    for case in case_dirs:
        scenario_file = case / "scenario.json"
        if scenario_file.exists():
            scenario = json.loads(scenario_file.read_text(encoding="utf-8"))
        else:
            scenario = dict(LOCAL_DEFAULT_SCENARIO)
        try:
            passed, msg = run_fixture(
                name=case.name,
                src_dir=case / "input",
                golden_dir=case / "expected",
                scenario=scenario,
            )
        except Exception as exc:  # noqa: BLE001
            passed = False
            msg = f"exception: {exc.__class__.__name__}: {exc}"
        tag = "PASS" if passed else "FAIL"
        print(f"[{tag}] {case.name}: {msg}")
        if not passed:
            fail_count += 1
    return 1 if fail_count else 0


def main() -> int:
    if "SMOKE_PINNED_UTC" not in os.environ:
        print("[FATAL] SMOKE_PINNED_UTC env var is required", file=sys.stderr)
        return 2

    # Pure-function unit tests gate the fixture loop: if helpers are wrong,
    # integration fixtures can't possibly pass, and isolated failures are
    # easier to diagnose than fixture-level byte diffs.
    unit_failures: list[str] = []
    unit_failures.extend(_test_scan_order())
    unit_failures.extend(_test_render_drift_header())
    unit_failures.extend(_test_t6_fixtures())
    if unit_failures:
        for f in unit_failures:
            print(f"[FAIL] unit test: {f}", file=sys.stderr)
        return 1

    # Local lane: iterate LOCAL_FIXTURES_DIR case subdirs.
    # Shared verifier, shared semantic assertions — no duplicated logic.
    local_dir = os.environ.get("LOCAL_FIXTURES_DIR")
    if local_dir:
        return run_local_lane(Path(local_dir))

    # CI lane: frozen 4-fixture manifest.
    fixtures = ["migration", "beginner-path", "warm-start", "monorepo"]
    fail_count = 0
    for name in fixtures:
        try:
            passed, msg = run_fixture(name)
        except Exception as exc:  # noqa: BLE001
            passed = False
            msg = f"exception: {exc.__class__.__name__}: {exc}"
        tag = "PASS" if passed else "FAIL"
        print(f"[{tag}] {name}: {msg}")
        if not passed:
            fail_count += 1
    return 1 if fail_count else 0


if __name__ == "__main__":
    sys.exit(main())
