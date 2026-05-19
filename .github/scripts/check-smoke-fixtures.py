#!/usr/bin/env python3
"""Reference implementation of skill parsing/rendering logic.

Runs over ci/fixtures/* and diffs produced output against ci/golden/*.

When the verifier and skill markdown disagree, fix whichever artifact
is wrong: ambiguous skill markdown is a bug, stale verifier logic is
also a bug. The verifier is NOT a canonical authority over the skill;
both are expressions of the same intent, cross-checked by CI.

Design:
- Functional dispatch + dataclasses + FIXTURE_SCENARIOS manifest
- Actual simulation for every fixture (input -> produced -> diff vs golden)
- Semantic assertions BEFORE byte diff (cause, not just drift)
- Real state-mutation short lock (atomic os.mkdir acquire / rename-aside
  stale-reclaim / release); contention branches out of Phase 1
- Final-Phase optimistic concurrency (OCC) A->B->C: Step A snapshot under
  the short lock, Step B lock-free merge/render (canonical reads forbidden
  and instrumented), Step C short-lock compare-and-commit keyed on a
  per-write deterministic commit_id nonce with bounded N=3 retry
- commit_id marker preflight: all-4-absent => genesis (Step 0.5 mints
  the first commit_id; a Final Phase that observes `absent` without
  genesis aborts), partial/mixed => torn-set preserve-first-then-stop
- audit_run_id minted in canonical microsecond form (+00:00 offset) with
  a parse-to-datetime monotonic bump (never string-sort), independent of
  commit_id
- Shared registry library via .github/scripts/lib/recommendation_registry
- Deterministic I/O: newline="\\n", SMOKE_PINNED_UTC env var (FATAL if
  unset), sorted globs, scripted single-threaded "concurrency" (no real
  threads / sleep / wallclock / randomness) — same input => byte-identical

Exit codes:
    0 - every fixture in FIXTURE_SCENARIOS PASSes (semantic + byte diff)
    1 - any fixture fails semantic assertions or byte diff
    2 - environment/precondition FATAL (e.g. jsonschema missing,
        SMOKE_PINNED_UTC unset)
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Windows cp949 defense: ensure stdout/stderr are UTF-8 so non-ASCII strings
# don't raise UnicodeEncodeError on Korean-locale Windows hosts.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

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


def _metadata_inline(key: str | None, v: dict) -> bool:
    """Hand-authored-golden rule: a ``metadata`` object renders INLINE when
    every value is a scalar (no nested array/object), regardless of field
    count. Derived 1:1 from the goldens:

    - ``recommendations.json`` / ``drift-state.json`` metadata
      ``{ "last_updated": …, "commit_id": … }`` (2 scalars) → INLINE.
    - ``profile.json`` metadata
      ``{ generated_by, last_updated, source_files_checked: [...],
      commit_id }`` contains an array → NOT all-scalar → stays EXPANDED
      (exactly as the profile goldens render it).

    Scoped to the ``metadata`` key so the generic ``_object_is_inline``
    rule (which keeps multi-field profile *sections* like
    ``package_management`` / ``testing`` expanded) is unaffected."""
    return (
        key == "metadata"
        and isinstance(v, dict)
        and len(v) > 0
        and all(_is_primitive(val) for val in v.values())
    )


def _dump(v, indent: int, parent_prefix_len: int = 0, key: str | None = None) -> str:
    """Render value `v` at nesting depth `indent`. parent_prefix_len is the
    length of the line prefix before this value (used to decide whether a
    wide inline array should wrap to multi-line). Goldens expand arrays
    whose inline representation pushes the line past ~110 chars. `key` is
    the parent object's key for this value (only `metadata` is special-
    cased — see _metadata_inline)."""
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
        if _object_is_inline(v) or _metadata_inline(key, v):
            parts = [f'{json.dumps(k, ensure_ascii=False)}: {_scalar(val)}' for k, val in v.items()]
            return "{ " + ", ".join(parts) + " }"
        items = list(v.items())
        lines = ["{"]
        for i, (k, val) in enumerate(items):
            comma = "," if i < len(items) - 1 else ""
            key_str = f'{json.dumps(k, ensure_ascii=False)}: '
            child_prefix = len("  ") * (indent + 1) + len(key_str)
            child = _dump(val, indent + 1, child_prefix, key=k)
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
# Primitive 1: State-mutation short-lock (atomic mkdir-acquire directory +
# owner.json, rename-aside stale reclaim, token-checked idempotent release)
# ---------------------------------------------------------------------------

# Short-lock reclaim threshold: deliberately ≫ the bounded sub-second write
# burst, and deliberately identical to the Final-Phase contention-wait bound
# (the single coherent "give up or reclaim" boundary).
_LOCK_RECLAIM_THRESHOLD_S = 30

# Deterministic per-acquire nonce source. The verifier is single-threaded and
# SMOKE_PINNED_UTC-pinned, so a monotonically-increasing counter yields a
# unique-per-acquire token while keeping fixture output byte-reproducible
# (NO os.urandom / real randomness — short-lock primitive + CLAUDE.md
# verifier mandate).
_LOCK_TOKEN_COUNTER = 0


class LockContention(Exception):
    """Raised when the state-mutation short-lock cannot be acquired.

    Step 0.5 (`abort_immediately`) raises this on the first live contention.
    The Final Phase (`wait_30s`) raises it only after the bounded re-attempt
    window elapses with the holder still live (the staleness-reclaim case:
    bound elapsed but the holder is still alive, so reclaim is refused)."""


def _next_lock_token() -> str:
    """Return a fresh deterministic acquisition nonce (the short-lock
    owner.json `token`)."""
    global _LOCK_TOKEN_COUNTER
    _LOCK_TOKEN_COUNTER += 1
    return f"tok-{_LOCK_TOKEN_COUNTER:08d}"


def _parse_iso_utc(value: str) -> float:
    """ISO-8601 UTC string -> epoch seconds.

    Mirrors the ``datetime.fromisoformat(value.replace("Z", "+00:00"))``
    idiom used by ``apply_pre_run``'s ``touch_older`` branch (line number
    intentionally omitted — it drifts as the file grows; grep the idiom)."""
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def _parse_audit_run_id(value: str) -> datetime:
    """Parse an ``audit_run_id``-family ISO-8601 UTC string to a tz-aware
    ``datetime``. Reuses the ``.replace("Z", "+00:00")`` idiom so
    BOTH the bare-``Z`` legacy form AND the canonical ``.ffffff+00:00`` form
    parse identically — this is precisely why the canonical-microsecond
    ``audit_run_id`` rule mandates parse-to-datetime and FORBIDS string-sort:
    ``2026-…00Z`` vs ``2026-…00.000001Z`` order correctly as datetimes but
    MISorder lexicographically."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _canonical_audit_run_id(dt: datetime) -> str:
    """Render a ``datetime`` to the CANONICAL ``audit_run_id`` form:
    ISO-8601 UTC, ALWAYS 6 fractional (microsecond) digits, explicit
    ``+00:00`` offset — e.g. ``2026-05-18T09:00:00.000000+00:00``. The
    bare-``Z`` suffix is NORMALIZED AWAY so all values are uniform.
    Deterministic: pure function of the input datetime (no wall clock)."""
    return dt.astimezone(timezone.utc).isoformat(timespec="microseconds")


def _monotonic_audit_run_id(candidate_raw: str, existing_raw: list[str]) -> str:
    """Canonical-microsecond form + parse-to-datetime monotonic bump.

    ``candidate_raw`` is the new run's id base (the pinned clock —
    ``ctx.pinned_utc`` — NEVER the wall clock, so the verifier stays
    deterministic). ``existing_raw`` is EVERY pre-existing id across
    ``baseline.audit_run_ids[]`` AND ``last_seen.audit_run_id``.

    Rule (computed under the Final-Phase Step C short lock where exclusivity
    holds): parse ALL ids to ``datetime`` (NEVER string-sort). If the
    candidate ``<= max(existing parsed)``, the result is
    ``max(existing) + 1 microsecond``; otherwise the candidate as-is. The
    returned value is ALWAYS the canonical ``.ffffff+00:00`` form.

    Determinism: the +1µs is derived from the on-disk ``max`` (not the wall
    clock); same fixture input ⇒ byte-identical output every run. This is a
    TARGETED carve-out from the ``state_io.md`` second-precision rule,
    scoped ONLY to ``audit_run_id`` — and independent of ``commit_id``
    (which carries NO ordering; ``audit_run_id`` is the ordering carrier)."""
    cand_dt = _parse_audit_run_id(candidate_raw)
    if existing_raw:
        max_dt = max(_parse_audit_run_id(v) for v in existing_raw)
        if cand_dt <= max_dt:
            cand_dt = max_dt + timedelta(microseconds=1)
    return _canonical_audit_run_id(cand_dt)


def _write_owner_json(lock_dir: Path, token: str, started_at: str) -> None:
    """Write owner.json via a UNIQUE sibling tempfile under local/ then
    os.replace into the lock dir (NEVER a tempfile inside the lock
    dir — a stray temp would break os.rmdir)."""
    local_dir = lock_dir.parent
    content = json.dumps({"token": token, "started_at": started_at})
    tmp = tempfile.NamedTemporaryFile(
        "w",
        dir=local_dir,
        prefix=".state.lock.owner.",
        encoding="utf-8",
        newline="\n",
        delete=False,
    )
    try:
        tmp.write(content)
        tmp.close()
        os.replace(tmp.name, lock_dir / "owner.json")
    except Exception:
        try:
            Path(tmp.name).unlink()
        except FileNotFoundError:
            pass
        raise


def _read_owner_json(lock_dir: Path) -> tuple[str, dict | None]:
    """Classify owner.json: ('absent'|'valid'|'corrupt', obj-or-None).

    A CORRUPT owner.json is NOT reclaimable — the caller must
    treat 'corrupt' as a live/hard-error, never stale."""
    owner_path = lock_dir / "owner.json"
    try:
        raw = owner_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ("absent", None)
    except OSError:
        return ("corrupt", None)
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        return ("corrupt", None)
    if not isinstance(obj, dict) or "token" not in obj or "started_at" not in obj:
        return ("corrupt", None)
    return ("valid", obj)


def _gc_tombstones(local_dir: Path, now_epoch: float) -> None:
    """Best-effort GC of .state.lock.dead.* tombstones older than the
    reclaim threshold. Tombstones are NEVER read / never used for
    synchronization — purely housekeeping."""
    try:
        entries = list(local_dir.glob(".state.lock.dead.*"))
    except OSError:
        return
    for dead in entries:
        try:
            age = now_epoch - dead.stat().st_mtime
        except OSError:
            continue
        if age >= _LOCK_RECLAIM_THRESHOLD_S:
            try:
                shutil.rmtree(dead, ignore_errors=True)
            except OSError:
                pass


def _is_stale(lock_dir: Path, now_epoch: float) -> bool:
    """Short-lock dual-condition staleness:

    - owner.json present & `started_at` age ≥ threshold  → stale
    - owner.json absent & lock-dir st_mtime age ≥ threshold → stale
    - owner.json CORRUPT → NOT stale (live/hard-error, never reclaimable)
    """
    status, obj = _read_owner_json(lock_dir)
    if status == "corrupt":
        return False
    if status == "valid":
        try:
            started = _parse_iso_utc(obj["started_at"])
        except (ValueError, TypeError, KeyError):
            # Unparseable started_at is a corruption variant → not reclaimable.
            return False
        return (now_epoch - started) >= _LOCK_RECLAIM_THRESHOLD_S
    # status == "absent": fall back to lock-dir mtime.
    try:
        dir_mtime = lock_dir.stat().st_mtime
    except OSError:
        # Lock dir vanished between mkdir-fail and here — treat as not stale;
        # the caller's next acquire attempt will re-evaluate.
        return False
    return (now_epoch - dir_mtime) >= _LOCK_RECLAIM_THRESHOLD_S


def _try_reclaim(lock_dir: Path, token: str) -> None:
    """Single atomic rename-aside (the short-lock stale-reclaim primitive).
    Concurrent reclaimers serialize: exactly one os.replace succeeds; losers
    get FileNotFoundError/OSError and simply re-evaluate on the next acquire
    attempt."""
    dead = lock_dir.parent / f".state.lock.dead.{token}"
    try:
        os.replace(lock_dir, dead)
    except (FileNotFoundError, OSError):
        # Lost the reclaim race (another reclaimer renamed first) — re-evaluate.
        pass


def acquire_lock(
    lock_dir: Path, behavior: str, pinned_utc: str
) -> str:
    """Acquire the state-mutation short-lock and return the
    acquisition token (thread it to `release_lock` so release can verify it
    still owns the lock).

    Lock object: directory `local/.state.lock/` with owner metadata
    `owner.json = {"token", "started_at"}`. Acquire gate is
    `os.mkdir(lock_dir)` (atomic create-or-fail); `FileExistsError` ⇒
    contention. Stale holders are reclaimed via a single atomic rename-aside.

    Caller asymmetry:
      - `abort_immediately` (Step 0.5): raise LockContention on the first
        live contention.
      - `wait_30s` (Final Phase): bounded deterministic re-attempts up to the
        30s window (a scripted attempt counter, NOT real time.sleep /
        wallclock), then LockContention if the holder is still live.

    Happy path (every existing single-shell fixture): the lock dir does not
    exist, so the very first os.mkdir succeeds and neither the contention nor
    the reclaim path is ever entered — byte-identical to the prior stub's
    end-state (lock fully removed by release_lock)."""
    if behavior not in {"abort_immediately", "wait_30s"}:
        raise ValueError(f"unknown lock behavior: {behavior}")

    now_epoch = _parse_iso_utc(pinned_utc)
    local_dir = lock_dir.parent
    local_dir.mkdir(parents=True, exist_ok=True)
    _gc_tombstones(local_dir, now_epoch)

    token = _next_lock_token()
    # Bounded deterministic attempt budget for wait_30s. Contention in the
    # verifier is SCRIPTED (Task 8 driver), never real concurrency — so this
    # is a fixed attempt counter, not a wallclock loop. abort_immediately
    # gets a single attempt (no waiting).
    max_attempts = (
        _LOCK_RECLAIM_THRESHOLD_S if behavior == "wait_30s" else 1
    )
    attempt = 0
    while True:
        try:
            os.mkdir(lock_dir)
        except FileExistsError:
            # Contention: either a live holder or a reclaimable stale one.
            if _is_stale(lock_dir, now_epoch):
                # Reclaim (atomic rename-aside) then retry the mkdir gate
                # immediately — the winner of the reclaim race re-creates a
                # fresh lock; losers harmlessly re-evaluate.
                _try_reclaim(lock_dir, token)
                continue
            # Live (or corrupt/hard-error) holder.
            attempt += 1
            if attempt >= max_attempts:
                raise LockContention(
                    f"state-mutation lock held at {lock_dir} "
                    f"(behavior={behavior}, attempts={attempt})"
                )
            # wait_30s: deterministic bounded re-attempt (no time.sleep).
            continue
        # mkdir succeeded — we own the lock. Publish owner.json.
        _write_owner_json(lock_dir, token, pinned_utc)
        return token


def release_lock(lock_dir: Path, token: str) -> None:
    """Idempotent, finally-style release (the token-checked short-lock
    release primitive).

    Re-read owner.json; ONLY if its `token` matches the token this caller
    acquired with do we unlink owner.json then os.rmdir the lock dir (ENOENT
    ignored). A token mismatch means we were stale-reclaimed — do NOTHING
    (deleting would clobber the new owner)."""
    status, obj = _read_owner_json(lock_dir)
    if status != "valid" or obj.get("token") != token:
        # Either the lock is gone, corrupt, or owned by a new holder that
        # reclaimed us. Removing anything here would clobber the new owner.
        return
    try:
        os.unlink(lock_dir / "owner.json")
    except FileNotFoundError:
        pass
    try:
        os.rmdir(lock_dir)
    except FileNotFoundError:
        pass


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

    Forward-compat READ only. If the section is absent
    or contains no anchors, returns []. Tolerant parser: any line matching
    '- skill: /X' inside ## Compacted History is treated as an anchor header;
    sibling 'last_entry_date:', 'last_model:', 'last_capability_fingerprint:'
    lines are consumed as anchor fields.

    Per the coordination note: compaction.md does not yet specify
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

    Deterministic, no keyword matching.
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
# Drift State Derivation (see drift-state.md, section "Drift Advisory Derivation")
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

    # drift_state with baseline=opus, last_seen=sonnet -> drift.
    drift_state_drift = {
        "schema_version": "1.0.0",
        "metadata": {"last_updated": "2026-04-14T00:00:00Z"},
        "baseline": {
            "model_id": "claude-opus-4-7",
            "first_observed_at": "2026-03-15T00:00:00Z",
            "audit_run_ids": ["2026-03-15T00:00:00Z"],
        },
        "last_seen": {
            "model_id": "claude-sonnet-4-6",
            "audit_run_id": "2026-04-14T00:00:00Z",
            "observed_at": "2026-04-14T00:00:00Z",
        },
        "legacy_migration": None,
    }

    out = render_state_summary(
        profile_stub, recs_stub, changelog_stub, ctx_stub,
        drift_state=drift_state_drift,
    )

    if "Model drift detected: claude-opus-4-7 -> claude-sonnet-4-6" not in out:
        failures.append("drift header missing from render")

    # Placement: header must fall between H1 and ## Project Profile.
    idx_h1 = out.find("# Claude Code Configuration State")
    idx_header = out.find("Model drift detected:")
    idx_profile = out.find("## Project Profile")
    if not (idx_h1 != -1 and idx_header != -1 and idx_profile != -1
            and idx_h1 < idx_header < idx_profile):
        failures.append(
            f"drift header placement wrong: h1={idx_h1} "
            f"header={idx_header} profile={idx_profile}"
        )

    # Silence test: match state (baseline == last_seen) -> no header.
    drift_state_match = {
        "schema_version": "1.0.0",
        "metadata": {"last_updated": "2026-04-14T00:00:00Z"},
        "baseline": {
            "model_id": "claude-opus-4-7",
            "first_observed_at": "2026-03-15T00:00:00Z",
            "audit_run_ids": ["2026-03-15T00:00:00Z"],
        },
        "last_seen": {
            "model_id": "claude-opus-4-7",
            "audit_run_id": "2026-04-14T00:00:00Z",
            "observed_at": "2026-04-14T00:00:00Z",
        },
        "legacy_migration": None,
    }
    out_match = render_state_summary(
        profile_stub, recs_stub, changelog_stub, ctx_stub,
        drift_state=drift_state_match,
    )
    if "Model drift detected:" in out_match:
        failures.append("drift header leaked into match state")

    # Silence test: missing_baseline (drift_state=None) stays silent.
    out_missing = render_state_summary(
        profile_stub, recs_stub, None, ctx_stub, drift_state=None
    )
    if "Model drift detected:" in out_missing:
        failures.append("drift header leaked into missing_baseline state")

    # Silence test: normalization_null (unknown last_seen model) stays silent.
    drift_state_null = {
        "schema_version": "1.0.0",
        "metadata": {"last_updated": "2026-04-14T00:00:00Z"},
        "baseline": {
            "model_id": "claude-opus-4-7",
            "first_observed_at": "2026-03-15T00:00:00Z",
            "audit_run_ids": ["2026-03-15T00:00:00Z"],
        },
        "last_seen": {
            "model_id": "claude-future-unknown-model-2099",
            "audit_run_id": "2026-04-14T00:00:00Z",
            "observed_at": "2026-04-14T00:00:00Z",
        },
        "legacy_migration": None,
    }
    out_null = render_state_summary(
        profile_stub, recs_stub, changelog_stub, ctx_stub,
        drift_state=drift_state_null,
    )
    if "Model drift detected:" in out_null:
        failures.append("drift header leaked into normalization_null state")

    return failures


def _test_t6_fixtures() -> list[str]:
    """L3 integration test: byte-match smoke fixtures against goldens.

    5 rendering fixtures (drift-recent-activity, drift-compacted-history,
    normalization-null-silence, crossskill-create-drift,
    state-summary-drift-header-wording) render through render_state_summary
    and byte-match against ci/fixtures/t6-*/golden/state-summary.md.

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
        "t6-state-summary-drift-header-wording",
    ]
    for name in rendering_fixtures:
        fdir = fixture_root / name
        profile_path = fdir / "profile.json"
        changelog_path = fdir / "changelog.md"
        drift_state_path = fdir / "drift-state.json"
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
        drift_state = (
            json.loads(drift_state_path.read_text(encoding="utf-8"))
            if drift_state_path.exists()
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
            drift_state=drift_state,
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
# Rendering (state-rendering.md §State Rendering)
# ---------------------------------------------------------------------------


def render_state_summary(
    profile: dict,
    recs: dict,
    changelog_text: str | None,
    ctx: RunContext,
    drift_state: dict | None = None,
    commit_id: str | None = None,
) -> str:
    """Produce state-summary.md content per state-rendering.md layout.

    `commit_id`, when supplied (OCC path only — the derived
    summary *echoes* the per-write source nonce but is never an authority),
    adds a
    ` commit_id: <id>` header line directly after the ` Source:` line. It
    is omitted entirely for the pre-OCC fixtures whose goldens carry no
    such line, so their byte output is unchanged."""
    commit_line = f" commit_id: {commit_id}\n" if commit_id else ""
    header = (
        "<!-- ─────────────────────────────────────────────\n"
        " Generated from JSON state — DO NOT EDIT.\n"
        " Read-only view. Manual edits will be overwritten\n"
        " on next skill invocation.\n"
        f" Generated at: {ctx.pinned_utc}\n"
        f" Source: profile.json v{profile.get('schema_version', '1.0.0')}, "
        f"recommendations.json v{recs.get('schema_version', '1.0.0')}\n"
        f"{commit_line}"
        "───────────────────────────────────────────────── -->\n\n"
    )

    rl = profile.get("runtime_and_language") or {}
    fw = profile.get("framework_and_libraries") or {}
    pm = profile.get("package_management") or {}
    ts = profile.get("testing") or {}
    bd = profile.get("build_and_dev") or {}
    ps = profile.get("project_structure") or {}
    ccs = profile.get("claude_code_configuration_state") or {}

    # Drift advisory derivation per drift-state.md "Drift Advisory Derivation".
    # Reads from drift-state.json (passed as drift_state param).
    # Absent/None drift_state → missing_baseline (silent). Silent on match,
    # missing_baseline, normalization_null; injects header only on drift.
    rules = _get_normalization_rules()
    last_seen = (drift_state.get("last_seen") or None) if drift_state else None
    baseline_obj = (drift_state.get("baseline") or None) if drift_state else None
    current_fp = (
        normalize_model_id(last_seen["model_id"], rules)
        if last_seen and last_seen.get("model_id")
        else None
    )
    baseline_present = baseline_obj is not None
    baseline_fp = (
        normalize_model_id(baseline_obj["model_id"], rules)
        if baseline_obj and baseline_obj.get("model_id")
        else None
    )
    state = _drift_state(current_fp, baseline_present, baseline_fp)

    drift_block = ""
    if state == "drift":
        drift_block = (
            f"Model drift detected: {baseline_obj['model_id']} -> {last_seen['model_id']}\n\n"
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

    Frontmatter dispatch (per the schema-evolution policy):
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
            f"Parser supports '1.0.0' or '1.1.0' only. See the changelog schema-evolution policy."
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
                "bullet_model": None,
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
            # Per the omit→null rule: "- Model: (none)" literal is forbidden for
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

    Per state-rendering.md §State Rendering: "One-line summary from the
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
       fallback to empty canonicals on parse failure; plus one-shot drift-state.json
       migration (derive from config-changelog.md or cold-start — no legacy MD source).
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
    lock_token = acquire_lock(lock_path, "abort_immediately", ctx.pinned_utc)

    try:
        registry_by_key = load_registry(REGISTRY_PATH)

        # Phase 2 — classify canonicals
        profile_path = state_root / "profile.json"
        recs_path = state_root / "recommendations.json"
        changelog_path = state_root / "config-changelog.md"
        drift_state_path = state_root / "drift-state.json"

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

        # drift-state.json: classify including schema validity (present-valid only
        # if parse succeeds AND schema validates — corrupt includes schema invalid).
        drift_state_status_raw, drift_state_obj_raw = _try_load_json(drift_state_path)
        if drift_state_status_raw == "present-valid":
            if not _validate_drift_state_schema(drift_state_obj_raw):
                drift_state_status_raw = "present-corrupt"
                drift_state_obj_raw = None
        drift_state_status = drift_state_status_raw

        # Phase 2 (legacy)
        legacy_files = _detect_legacy_md(state_root)
        state.examined_legacy_md = [str(p) for p in legacy_files]

        # Phase 3/4/5
        need_recovery = (
            profile_status != "present-valid"
            or recs_status != "present-valid"
            or drift_state_status != "present-valid"
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

            # Phase 4 (drift-state.json): one-shot migration.
            # Idempotence guard: re-read under lock; skip if already present-valid.
            if drift_state_status != "present-valid":
                # Re-read from disk (idempotence guard under lock).
                _reread_status, _reread_obj = _try_load_json(drift_state_path)
                if _reread_status == "present-valid" and _validate_drift_state_schema(_reread_obj):
                    # Another writer already migrated; use on-disk state.
                    drift_state_obj_raw = _reread_obj
                    drift_state_status = "present-valid"
                else:
                    # Move corrupt canonical aside BEFORE overwriting.
                    if drift_state_status == "present-corrupt":
                        backup_dir.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(drift_state_path), str(backup_dir / "drift-state.json"))
                    # Read changelog for derivation (may have been loaded already).
                    _cl_text = (
                        changelog_path.read_text(encoding="utf-8")
                        if changelog_path.exists()
                        else None
                    )
                    derived = _derive_drift_state_from_changelog(_cl_text, ctx.pinned_utc)
                    atomic_write_json(drift_state_path, derived)
                    # Readback + schema-validate (single-attempt; no retry).
                    _rb_status, _rb_obj = _try_load_json(drift_state_path)
                    if _rb_status == "present-valid" and _validate_drift_state_schema(_rb_obj):
                        drift_state_obj_raw = _rb_obj
                    else:
                        # Readback failed or schema invalid; keep whatever is on-disk.
                        print("WARNING: drift-state.json readback validation failed after write; using in-memory derived state", file=sys.stderr)
                        drift_state_obj_raw = derived  # use in-memory fallback

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
                state.profile, state.recommendations, state.changelog, ctx,
                drift_state=drift_state_obj_raw,
            )
            atomic_write_text(state_root / "state-summary.md", summary)
            state.state_summary = summary

        # Phase 7: migration notice intentionally not printed in CI smoke.

    finally:
        # Phase 8
        release_lock(lock_path, lock_token)

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


def _empty_drift_state(pinned_utc: str) -> dict:
    """Cold-start drift-state.json: all optional fields null."""
    return {
        "schema_version": "1.0.0",
        "metadata": {"last_updated": pinned_utc},
        "baseline": None,
        "last_seen": None,
        "legacy_migration": None,
    }


def _validate_drift_state_schema(obj: dict) -> bool:
    """Return True if obj passes drift-state.schema.v1.0.0.json validation."""
    try:
        from referencing import Registry, Resource  # noqa: PLC0415
        base_schema = json.loads((SCHEMAS_DIR / "drift-state.schema.base.json").read_text(encoding="utf-8"))
        wrapper_schema = json.loads((SCHEMAS_DIR / "drift-state.schema.v1.0.0.json").read_text(encoding="utf-8"))
        registry = Registry().with_resources(
            [("drift-state.schema.base.json", Resource.from_contents(base_schema))]
        )
        jsonschema.Draft202012Validator(wrapper_schema, registry=registry).validate(obj)
        return True
    except Exception:  # noqa: BLE001
        # Fail-closed: if the drift-state schema file is unreadable, classify the
        # instance as corrupt (forces re-derivation) rather than passing unvalidated.
        return False


def _derive_drift_state_from_changelog(changelog_text: str | None, pinned_utc: str) -> dict:
    """Derive drift-state.json from config-changelog.md for the migration.

    Collects all /audit observation events with non-null Model bullets from
    both Recent Activity (v1.1.0) and Compacted History anchors.
    Sorted ascending by date (oldest first).

    If audit_observations is non-empty → derive_from_changelog:
      - baseline: oldest observation (model_id, first_observed_at, audit_run_ids)
      - last_seen: most-recent observation (model_id, audit_run_id, observed_at)
      - legacy_migration.source_changelog_anchor_run_id = baseline.first_observed_at

    If audit_observations is empty → cold_start (all null fields).
    """
    if not changelog_text:
        return _empty_drift_state(pinned_utc)

    # Collect (date_str, model_id) pairs for /audit entries with non-null Model.
    audit_observations: list[tuple[str, str]] = []

    # Try to parse changelog version; default to treating as v1.0.0 (no Model bullets)
    try:
        fm, body = _strip_frontmatter(changelog_text)
        version = _extract_frontmatter_version(fm)
    except Exception:  # noqa: BLE001
        version = "1.0.0"

    # Recent Activity: scan for /audit entries with - Model: <non-null>
    # Only v1.1.0+ changelogs have Model bullets; v1.0.0 entries are omit-paths.
    # Conservative-omit policy: a changelog version other than "1.1.0" (e.g., a
    # future "1.2.0") intentionally skips Recent Activity collection here and
    # degrades toward cold_start, rather than raising like _parse_changelog_entries.
    # A one-shot migration must not hard-fail on a future changelog format; a
    # missed Recent-Activity observation only delays drift-baseline establishment
    # to the next /audit, whereas a raise would abort migration entirely.
    if version == "1.1.0":
        try:
            parsed = _parse_changelog_entries(changelog_text)
            for entry in parsed.get("entries", []):
                if entry.get("skill") == "audit":
                    bullet_model = entry.get("bullet_model")
                    if bullet_model is not None:
                        audit_observations.append((entry["date"], bullet_model))
        except Exception:  # noqa: BLE001
            pass

    # Compacted History: scan anchors for /audit with non-null last_model.
    # This applies to all versions since compacted anchors are always structured.
    try:
        anchors = _parse_compacted_history_anchors(changelog_text)
        for anchor in anchors:
            if anchor.get("skill") == "/audit":
                last_model = anchor.get("last_model")
                if last_model is not None:
                    last_entry_date = anchor.get("last_entry_date")
                    if last_entry_date:
                        audit_observations.append((last_entry_date, last_model))
    except Exception:  # noqa: BLE001
        pass

    if not audit_observations:
        return _empty_drift_state(pinned_utc)

    # Sort ascending by date (oldest first). Same-date tie: stable (list order).
    audit_observations.sort(key=lambda t: t[0])

    oldest_date, oldest_model = audit_observations[0]
    newest_date, newest_model = audit_observations[-1]

    first_observed_at = oldest_date + "T00:00:00Z"
    rules = _get_normalization_rules()
    oldest_fp = normalize_model_id(oldest_model, rules)

    # audit_run_ids: all observations where model normalizes to baseline model,
    # ascending, FIFO trim to 50.
    audit_run_ids: list[str] = []
    for obs_date, obs_model in audit_observations:
        obs_fp = normalize_model_id(obs_model, rules)
        if oldest_fp is not None and obs_fp is not None and obs_fp == oldest_fp:
            audit_run_ids.append(obs_date + "T00:00:00Z")
    audit_run_ids = audit_run_ids[:50]

    # Guarantee at least the baseline itself is in audit_run_ids.
    if not audit_run_ids:
        audit_run_ids = [first_observed_at]

    return {
        "schema_version": "1.0.0",
        "metadata": {"last_updated": pinned_utc},
        "baseline": {
            "model_id": oldest_model,
            "first_observed_at": first_observed_at,
            "audit_run_ids": audit_run_ids,
        },
        "last_seen": {
            "model_id": newest_model,
            "audit_run_id": newest_date + "T00:00:00Z",
            "observed_at": newest_date + "T00:00:00Z",
        },
        "legacy_migration": {
            "source_changelog_anchor_run_id": first_observed_at,
        },
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
    "monorepo_detection",
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
    owned_by_audit_only = [
        "monorepo_detection",
    ]
    if current is None:
        current = _empty_profile(delta.get("metadata", {}).get("last_updated", ""))
    merged = json.loads(json.dumps(current))  # deep copy via JSON
    # Lock-free Step-B merge output is the pre-stamp wrapper (no commit_id);
    # _stamp_commit_id is the SOLE path that bumps this to the
    # commit_id-required wrapper. Single-sourced via the module constant.
    merged["schema_version"] = _MERGE_PROFILE_SCHEMA_VERSION
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
    if skill == "audit":
        for k in owned_by_audit_only:
            if k in delta:
                merged[k] = delta[k]
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
    lock_token = acquire_lock(lock_path, "wait_30s", ctx.pinned_utc)
    try:
        if state.profile is not None:
            atomic_write_json(state_root / "profile.json", state.profile)
        if state.recommendations is not None:
            atomic_write_json(state_root / "recommendations.json", state.recommendations)
        if state.changelog is not None:
            atomic_write_text(state_root / "config-changelog.md", state.changelog)
        if state.profile is not None and state.recommendations is not None:
            drift_state_path = state_root / "drift-state.json"
            try:
                drift_state = json.loads(
                    drift_state_path.read_text(encoding="utf-8")
                ) if drift_state_path.exists() else None
            except (OSError, json.JSONDecodeError):
                drift_state = None
            summary = render_state_summary(
                state.profile, state.recommendations, state.changelog, ctx,
                drift_state=drift_state,
            )
            atomic_write_text(state_root / "state-summary.md", summary)
            state.state_summary = summary
    finally:
        release_lock(lock_path, lock_token)


# ---------------------------------------------------------------------------
# OCC layer (short-lock A / lock-free B / compare-and-commit C)
# ---------------------------------------------------------------------------
#
# The OCC layer is DORMANT for every fixture whose input source files carry
# NO commit_id marker (all 39 pre-existing fixtures): _final_phase_write /
# step_0_5 behave byte-identically to before. It activates only when the
# commit_id marker preflight classifies the 4 sources as present-and-uniform
# — i.e.
# the state-lock-* fixtures whose input is stamped with commit_id. The
# "concurrency" is SCRIPTED and single-threaded (the verifier is
# SMOKE_PINNED_UTC-pinned): a fixture counter advances a deterministic
# commit_id sequence and a one-shot hook injects shell B's full A→B→C commit
# between shell A's Step A release and Step C acquire. NO real threads /
# sleep / wallclock / randomness — same input ⇒ byte-identical output.

# Reset per run_fixture (see _reset_run_state). Module globals because the
# instrumentation must straddle acquire/merge/commit call sites.
_COMMIT_ID_COUNTER = 0
# "B" while shell A is in its lock-free Step B window (between A's Step A
# release and A's Step C acquire); None otherwise. ASSERT_NO_READ_DURING_B
# samples this at every canonical read.
_OCC_PHASE: str | None = None
# Canonical reads observed while _OCC_PHASE == "B" (must stay empty).
_OCC_READS_DURING_B: list[str] = []
# Every commit_id ever minted this run (must be all-distinct).
_OCC_COMMIT_IDS: list[str] = []
# One-shot guard for the scripted shell-B injection during A's Step B.
_OCC_B_INJECTED = False
# Set True ONLY by the genesis sub-step (step_0_5_genesis) immediately
# before it performs the genesis stamp/commit. The Final-Phase commit
# chokepoint (_occ_commit) reads this: a commit attempted while the 4
# sources are still `absent` is permitted ONLY when genesis set this flag
# (the genesis mint itself). Any OTHER write path that reaches _occ_commit
# on an `absent` set with this flag still False is a Final Phase that
# observed `absent` without genesis having minted — it MUST NOT invent a
# commit_id; the guard raises GenesisRequiredAbort instead ("absent" is
# non-comparable; only Step 0.5 mints the genesis id).
_GENESIS_MINTED = False

_OCC_CANONICAL_NAMES = frozenset({
    "profile.json", "recommendations.json", "config-changelog.md",
    "drift-state.json", "state-summary.md",
})

# The scoring-model contract id the current /audit Final Phase writes into
# profile.claude_code_configuration_state.scoring_model_ack (spec: the A1
# Row-2 ack-write stamps the *current* contract). Bumped here from the
# legacy v4.1.0 the per-fixture detect presets still carry.
_CURRENT_SCORING_CONTRACT = "audit-score-v4.2.0"
# Profile schema version produced by the lock-free Step-B merge BEFORE the
# OCC commit stamps commit_id (this wrapper does NOT require metadata.commit_id).
# `merge_profile` writes exactly this; `_stamp_commit_id` then bumps it to
# `_OCC_PROFILE_SCHEMA_VERSION`. Single-sourced so the pre-/post-stamp pair
# cannot silently desync (guarded by an assert in `_stamp_commit_id`).
_MERGE_PROFILE_SCHEMA_VERSION = "1.2.0"
# Profile schema version whose versioned wrapper REQUIRES metadata.commit_id
# (only the new wrapper adds commit_id to required; the legacy wrapper keeps
# it optional). An OCC commit stamps commit_id, so it writes profile at this
# version. MUST be a
# strict bump from `_MERGE_PROFILE_SCHEMA_VERSION` (asserted at the stamp site).
_OCC_PROFILE_SCHEMA_VERSION = "1.3.0"


def _reset_run_state() -> None:
    """Reset all per-run OCC/lock instrumentation back to genesis state.

    Called at the top of every run_fixture so module globals (which must
    straddle the acquire/merge/commit call sites) do NOT leak across the
    FIXTURE_SCENARIOS loop. Resets exactly six per-run carriers:
      - `_COMMIT_ID_COUNTER` -> 0  (deterministic commit_id sequence
        restarts; re-seeded from the input nonce on the first Step A)
      - `_OCC_PHASE` -> None  (the "B" lock-free-window flag sampled by
        the no-read-during-B probe)
      - `_OCC_B_INJECTED` -> False  (one-shot scripted shell-B injection
        guard)
      - `_GENESIS_MINTED` -> False  (the genesis-minted flag the
        Final-Phase commit chokepoint checks before permitting a commit
        on an `absent` source set)
      - `_OCC_READS_DURING_B` -> cleared  (canonical reads observed while
        in Step B; must end empty)
      - `_OCC_COMMIT_IDS` -> cleared  (every commit_id minted this run;
        asserted all-distinct)"""
    global _COMMIT_ID_COUNTER, _OCC_PHASE, _OCC_B_INJECTED, _GENESIS_MINTED
    _COMMIT_ID_COUNTER = 0
    _OCC_PHASE = None
    _OCC_B_INJECTED = False
    _GENESIS_MINTED = False
    _OCC_READS_DURING_B.clear()
    _OCC_COMMIT_IDS.clear()


def _seed_commit_counter_from(commit_obs: str | None) -> None:
    """Seed the deterministic commit_id counter from the OBSERVED input
    nonce so the first NEW mint continues the distinct sequence rather than
    re-minting the value the input already consumed.

    The input fixture is pre-stamped (e.g. ``commit-0001`` — a prior write's
    burst). Minting must yield the NEXT id (``commit-0002`` for shell B's
    commit, ``commit-0003`` for shell A's retried commit). Parsing the
    numeric suffix keeps this fully deterministic (no wall-clock / random)
    and contract-faithful (each successful burst gets a distinct, never
    reused, per-write commit_id nonce). Idempotent: only seeds once per run
    (the first Step A); later Step-A re-snapshots must NOT rewind the
    counter."""
    global _COMMIT_ID_COUNTER
    if _COMMIT_ID_COUNTER != 0:
        return
    if commit_obs and commit_obs.startswith("commit-"):
        try:
            _COMMIT_ID_COUNTER = int(commit_obs.split("-", 1)[1])
        except ValueError:
            _COMMIT_ID_COUNTER = 0


def _mint_commit_id() -> str:
    """Mint the next DETERMINISTIC distinct commit_id (the per-write nonce
    verifier value: a distinct sequence advanced by a fixture counter —
    never a reused constant). The counter is seeded from the input nonce
    (_seed_commit_counter_from) so mints continue the sequence
    (input commit-0001 → first mint commit-0002 → next commit-0003 …).
    Records every id for ASSERT_COMMITID_UNIQUE."""
    global _COMMIT_ID_COUNTER
    _COMMIT_ID_COUNTER += 1
    cid = f"commit-{_COMMIT_ID_COUNTER:04d}"
    _OCC_COMMIT_IDS.append(cid)
    return cid


def _occ_read_probe(path: Path) -> None:
    """Instrument a canonical-source read. If shell A is in its lock-free
    Step B window, record the read — ASSERT_NO_READ_DURING_B then fails the
    fixture (the OCC protocol's lock-free Step B and its CI assertion: Step
    B must read NOTHING canonical)."""
    if _OCC_PHASE == "B" and path.name in _OCC_CANONICAL_NAMES:
        _OCC_READS_DURING_B.append(path.name)


def _read_commit_id_json(path: Path) -> str | None:
    """metadata.commit_id from a JSON source (probe-instrumented). None when
    absent/unreadable."""
    _occ_read_probe(path)
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    cid = obj.get("metadata", {}).get("commit_id")
    return cid if isinstance(cid, str) else None


def _read_commit_id_changelog(path: Path) -> str | None:
    """commit_id from config-changelog.md frontmatter (probe-instrumented)."""
    _occ_read_probe(path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    fm, _ = _strip_frontmatter(text)
    cid = fm.get("commit_id")
    return cid.strip("'\"") if isinstance(cid, str) else None


# Single source of truth for the 4 canonical SOURCE files the commit_id
# marker preflight reads, in marker-preflight order, paired with the
# per-file commit_id reader. state-summary.md is intentionally absent — it
# is the derived cache and NEVER a marker-classification authority (it
# participates in neither the preflight nor torn classification).
# The three consumers (`_occ_marker_state`, `_TORN_SOURCE_FILES`,
# `_observed_source_commit_ids`) all derive from THIS tuple so the
# file-list + reader pairing is encoded exactly once (was triplicated).
_SOURCE_READERS: tuple[tuple[str, Callable[[Path], str | None]], ...] = (
    ("profile.json", _read_commit_id_json),
    ("recommendations.json", _read_commit_id_json),
    ("drift-state.json", _read_commit_id_json),
    ("config-changelog.md", _read_commit_id_changelog),
)


def _occ_marker_state(state_root: Path) -> tuple[str, str | None]:
    """commit_id marker preflight over the 4 SOURCE files (state-summary.md
    is the derived cache, never an authority — excluded). Returns:
      ("absent", None)  — all 4 lack commit_id (legacy → genesis elsewhere)
      ("uniform", id)   — all 4 present and identical (OCC-comparable)
      ("torn", None)    — partial / mixed (→ torn-set preserve-first stop;
                          out of scope here)
    """
    ids = [reader(state_root / name) for name, reader in _SOURCE_READERS]
    present = [i for i in ids if i is not None]
    if not present:
        return ("absent", None)
    if len(present) == len(_SOURCE_READERS) and len(set(present)) == 1:
        return ("uniform", present[0])
    return ("torn", None)


def _occ_snapshot(ctx: RunContext, state_root: Path) -> dict:
    """OCC Step A read: under the short lock the 4 sources are read into
    an in-memory snapshot (probe-instrumented; A's lock is held here so
    these reads are legitimately NOT in the Step B window)."""
    snap: dict = {}
    p = state_root / "profile.json"
    _occ_read_probe(p)
    snap["profile"] = json.loads(p.read_text(encoding="utf-8"))
    r = state_root / "recommendations.json"
    _occ_read_probe(r)
    snap["recommendations"] = json.loads(r.read_text(encoding="utf-8"))
    d = state_root / "drift-state.json"
    _occ_read_probe(d)
    snap["drift_state"] = json.loads(d.read_text(encoding="utf-8"))
    c = state_root / "config-changelog.md"
    _occ_read_probe(c)
    snap["changelog"] = c.read_text(encoding="utf-8")
    return snap


def _occ_audit_deltas(ctx: RunContext, snapshot: dict) -> dict:
    """Step B (lock-free): compute THIS skill's /audit Final-Phase result
    purely from `snapshot` (NO canonical reads — operates on the in-memory
    Step A capture only). Returns the merged-but-unstamped {profile,
    recommendations, changelog}; commit_id + schema bump are applied at
    Step C commit time.

    The /audit detection itself (Phase 1–4) is fixture-pinned to the
    state-lock-* project shape (Next.js/React/Tailwind, pnpm, Vitest +
    Playwright, Turbopack, single_project — identical to the input profile
    sections). On an OCC retry this function is re-invoked against the NEW
    snapshot but the *detection* is unchanged — modelling the OCC retry rule
    "re-merge the already-computed deltas; primary analysis is NOT
    re-run"."""
    date = ctx.pinned_utc.split("T")[0]

    profile_delta = {
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
            # scoring_model_ack is computed below from the snapshot's prior
            # ack (A1 Row 2 ack-write, Final Phase only — re-applied each
            # OCC attempt against the then-current snapshot).
        },
    }

    # A1 Row 2: scoring-model ack-write. Trigger = ack absent OR its
    # seen_count < 2 (cap). seen_count = min(prev_seen + 1, 2). prev is read
    # from the SNAPSHOT (the Step A / re-snapshot capture), never from disk.
    prev_ack = (
        snapshot.get("profile", {})
        .get("claude_code_configuration_state", {})
        .get("scoring_model_ack")
    )
    prev_seen = 0
    if isinstance(prev_ack, dict) and isinstance(prev_ack.get("seen_count"), int):
        # Only carry the prior count when it acked the CURRENT contract;
        # a different contract id resets the counter (seen this contract 0×).
        if prev_ack.get("version") == _CURRENT_SCORING_CONTRACT:
            prev_seen = prev_ack["seen_count"]
    new_seen = min(prev_seen + 1, 2)
    profile_delta["claude_code_configuration_state"]["scoring_model_ack"] = {
        "version": _CURRENT_SCORING_CONTRACT,
        "seen_count": new_seen,
    }

    merged_profile = merge_profile(snapshot["profile"], profile_delta, "audit")
    merged_recs = merge_recommendations(
        snapshot["recommendations"], [], ctx.pinned_utc
    )
    # warm-start-style /audit changelog entry (2x pending carried forward).
    entry = (
        f"### {date} — /audit\n"
        f"- Model: {merged_profile['claude_code_configuration_state']['model']}\n"
        f"- Detected: (none)\n"
        f"- Profile updated: (none)\n"
        f"- Applied: (none)\n"
        f"- Resolved: (none)\n"
        f"- Recommendations:\n"
        f"  - Split CLAUDE.md into rule files — PENDING (2x)"
    )
    merged_changelog = _changelog_with_entry(snapshot["changelog"], entry)
    return {
        "profile": merged_profile,
        "recommendations": merged_recs,
        "changelog": merged_changelog,
    }


def _occ_drift_state_audit_update(
    ctx: RunContext, snap_drift_state: dict, current_model_id: str
) -> dict:
    """drift-state.md "Update step" (`/audit` only) applied lock-free in
    Step B from the Step A snapshot, with the canonical-microsecond
    ``audit_run_id`` form + parse-to-datetime monotonic bump.

    Returns a NEW drift_state dict (the snapshot is never mutated).

    Scope (T11 interpretation — see report): this models drift-state.md's
    branch 1 (baseline non-null, fingerprint-match append) + branch 3
    (always update ``last_seen``) for an ALREADY-ESTABLISHED ledger only.
    The cold-start baseline-creation branch 2 is intentionally NOT modelled
    in the verifier OCC path — it has never been (T6–T10 passed ``drift_state``
    through unchanged), and adding it would perturb the byte-frozen
    cold-start goldens (``state-lock-concurrent`` / ``state-lock-occ-conflict``
    have ``baseline:null,last_seen:null``). So a cold-start (``baseline`` AND
    ``last_seen`` both null) is returned UNCHANGED — preserving every prior
    state-lock golden byte-for-byte while the established-ledger path
    exercises the canonical-microsecond form + monotonic bump.

    The candidate id base is the PINNED clock (``ctx.pinned_utc``) — never
    ``datetime.now()`` — and the +1µs (when the candidate collides) is
    derived from the on-disk ``max`` of the snapshot's existing ids, so the
    same fixture input yields byte-identical output every run."""
    ds = json.loads(json.dumps(snap_drift_state))
    baseline = ds.get("baseline")
    last_seen = ds.get("last_seen")

    # Cold-start: nothing established yet → leave UNCHANGED (out of T11
    # scope; preserves the byte-frozen cold-start state-lock goldens).
    if baseline is None and last_seen is None:
        return ds

    # Gather EVERY pre-existing id (across baseline.audit_run_ids[]
    # AND last_seen.audit_run_id) so the monotonic bump parses them all.
    existing: list[str] = []
    if isinstance(baseline, dict):
        existing.extend(baseline.get("audit_run_ids") or [])
    if isinstance(last_seen, dict) and last_seen.get("audit_run_id"):
        existing.append(last_seen["audit_run_id"])

    # Candidate base = pinned clock; canonical-microsecond form + monotonic
    # bump.
    new_run_id = _monotonic_audit_run_id(ctx.pinned_utc, existing)

    rules = _get_normalization_rules()
    cur_fp = normalize_model_id(current_model_id, rules)

    # Branch 1: baseline non-null → append the new id to FIFO audit_run_ids
    # only when the running model fingerprint matches the baseline (null
    # normalization ⇒ uncertain ⇒ NOT baseline-confirming; drift ⇒ skip).
    if isinstance(baseline, dict):
        base_fp = (
            normalize_model_id(baseline.get("model_id"), rules)
            if baseline.get("model_id")
            else None
        )
        if cur_fp is not None and base_fp is not None and cur_fp == base_fp:
            ids = list(baseline.get("audit_run_ids") or [])
            ids.append(new_run_id)
            if len(ids) > 50:
                ids = ids[-50:]
            baseline["audit_run_ids"] = ids

    # Branch 3: ALWAYS update last_seen (canonical-form id; observed_at is a
    # plain pinned-clock timestamp, NOT an audit_run_id-family value, so it
    # is NOT canonical-normalized — the canonical-microsecond carve-out is
    # scoped to audit_run_id only).
    ds["last_seen"] = {
        "model_id": current_model_id,
        "audit_run_id": new_run_id,
        "observed_at": ctx.pinned_utc,
    }
    return ds


def _occ_merge_drift_state(
    ctx: RunContext, snapshot: dict, merged_profile: dict
) -> dict:
    """Resolve the Step-B drift_state for an OCC ``/audit`` commit: apply the
    drift-state.md Update step (canonical-microsecond ``audit_run_id`` +
    parse-to-datetime monotonic bump) to the snapshot's drift_state.
    ``/audit`` is
    the only skill modelled by the OCC scenario, so this is unconditional
    here (the established-ledger gating lives in
    ``_occ_drift_state_audit_update``).

    ``current_model_id`` is read from the MERGED profile's
    ``claude_code_configuration_state.model`` — i.e. the model the ``/audit``
    Final-Phase resolved (drift-state.md: the genesis Model-field write
    path) — NOT the raw input snapshot profile (which need not carry a
    ``model`` yet)."""
    current_model_id = (
        merged_profile.get("claude_code_configuration_state", {}).get("model")
        or "claude-opus-4-7"
    )
    return _occ_drift_state_audit_update(
        ctx, snapshot["drift_state"], current_model_id
    )


def _stamp_commit_id(merged: dict, commit_id: str) -> tuple[dict, dict, str, dict]:
    """Stamp the per-write `commit_id` nonce onto the 4 source surfaces and
    bump profile to the commit_id-required wrapper version. Returns
    (profile, recommendations, changelog_text, drift_state)."""
    profile = json.loads(json.dumps(merged["profile"]))
    # Coupling guard (per-write commit_id nonce + schema requiredness): the
    # incoming profile MUST be the pre-stamp merge wrapper, and the stamp
    # MUST be a real bump. If a
    # future edit changes one constant but not the merge/stamp path, this
    # fires loudly instead of silently writing a commit_id-less wrapper
    # tagged as commit_id-required (or vice versa).
    assert profile.get("schema_version") == _MERGE_PROFILE_SCHEMA_VERSION, (
        f"_stamp_commit_id expected pre-stamp profile schema_version "
        f"{_MERGE_PROFILE_SCHEMA_VERSION!r} (the merge_profile output), got "
        f"{profile.get('schema_version')!r} — merge/stamp version coupling desynced"
    )
    assert _OCC_PROFILE_SCHEMA_VERSION != _MERGE_PROFILE_SCHEMA_VERSION, (
        f"_OCC_PROFILE_SCHEMA_VERSION must be a strict bump from "
        f"_MERGE_PROFILE_SCHEMA_VERSION (both {_MERGE_PROFILE_SCHEMA_VERSION!r}) "
        f"— commit_id-required wrapper transition would be a no-op"
    )
    profile["schema_version"] = _OCC_PROFILE_SCHEMA_VERSION
    profile.setdefault("metadata", {})["commit_id"] = commit_id

    recs = json.loads(json.dumps(merged["recommendations"]))
    recs.setdefault("metadata", {})["commit_id"] = commit_id

    drift_state = json.loads(json.dumps(merged["drift_state"]))
    drift_state.setdefault("metadata", {})["last_updated"] = merged.get(
        "pinned_utc", drift_state.get("metadata", {}).get("last_updated")
    )
    drift_state["metadata"]["commit_id"] = commit_id

    changelog = _changelog_set_commit_id(merged["changelog"], commit_id)
    return profile, recs, changelog, drift_state


def _changelog_set_commit_id(text: str, commit_id: str) -> str:
    """Set/replace the `commit_id:` line in config-changelog.md frontmatter.

    If the frontmatter already carries a `commit_id:` line (every OCC
    fixture's input does), replace it IN PLACE (preserving field order). If
    it does NOT, insert one directly after `entry_count:` to match the
    golden frontmatter order. The two cases are mutually exclusive — a
    pre-scan picks exactly one so a duplicate `commit_id:` line can never be
    emitted (the prior single-pass version inserted after `entry_count:`
    AND then replaced the later existing line, yielding two)."""
    lines = text.split("\n")
    # Pre-scan: does the FIRST frontmatter block already have a commit_id?
    has_commit = False
    fm_seen = 0
    for line in lines:
        if line == "---":
            fm_seen += 1
            if fm_seen == 2:
                break
            continue
        if fm_seen == 1 and line.startswith("commit_id:"):
            has_commit = True
            break

    out: list[str] = []
    in_fm = False
    fm_bounds = 0
    for line in lines:
        if line == "---":
            fm_bounds += 1
            in_fm = fm_bounds == 1
            out.append(line)
            continue
        if has_commit:
            if in_fm and line.startswith("commit_id:"):
                out.append(f"commit_id: {commit_id}")
                continue
            out.append(line)
            continue
        # No existing commit_id → insert once, right after entry_count.
        out.append(line)
        if in_fm and line.startswith("entry_count:"):
            out.append(f"commit_id: {commit_id}")
    return "\n".join(out)


def _occ_commit(
    ctx: RunContext, state_root: Path, merged: dict, commit_id: str,
    state: WorkspaceState | None = None,
) -> None:
    """OCC Step C write (compare-and-commit): atomic-write all 5 files
    stamped with `commit_id` — the 4 sources first (any order), then
    state-summary.md LAST (sources-first/summary-last so a
    post-sources/pre-summary crash is a normal regen, not a torn set).

    Defensive guard ("absent" is non-comparable; ONLY Step 0.5 mints the
    genesis commit_id): this is the single Final-Phase commit
    chokepoint. If it is reached while the 4 SOURCE files are still
    `absent` (no commit_id anywhere) AND the genesis sub-step has NOT
    flagged a mint this run, then a Final Phase observed `absent` without
    genesis having occurred — it MUST NOT invent a commit_id and commit.
    Raise GenesisRequiredAbort (route back to Step 0.5 / defer) rather
    than coercing absent→a real value. The genesis sub-step itself sets
    _GENESIS_MINTED True immediately before calling this, so its own
    legitimate absent→first-mint write passes; the OCC `uniform` callers
    operate on an already-marked set so this guard is a no-op for them."""
    if not _GENESIS_MINTED:
        try:
            _pre_marker = _occ_marker_state(state_root)[0]
        except Exception:  # noqa: BLE001
            _pre_marker = "absent"
        if _pre_marker == "absent":
            raise GenesisRequiredAbort(
                "Final-Phase commit attempted on an `absent` (markerless) "
                "source set without genesis having minted the first "
                "commit_id; deferring to Step 0.5 genesis (absent is "
                "non-comparable; inventing a commit_id here is "
                "forbidden)."
            )
    merged = dict(merged)
    merged["pinned_utc"] = ctx.pinned_utc
    profile, recs, changelog, drift_state = _stamp_commit_id(merged, commit_id)

    atomic_write_json(state_root / "profile.json", profile)
    atomic_write_json(state_root / "recommendations.json", recs)
    atomic_write_json(state_root / "drift-state.json", drift_state)
    atomic_write_text(state_root / "config-changelog.md", changelog)

    summary = render_state_summary(
        profile, recs, changelog, ctx,
        drift_state=drift_state, commit_id=commit_id,
    )
    atomic_write_text(state_root / "state-summary.md", summary)

    if state is not None:
        state.profile = profile
        state.recommendations = recs
        state.changelog = changelog
        state.state_summary = summary


def _occ_one_commit_burst(
    ctx: RunContext, state_root: Path, lock_path: Path,
    state: WorkspaceState | None = None,
) -> str:
    """One full A→B→C OCC commit cycle WITHOUT the scripted B-injection
    (used for shell B, and for shell A's bounded retries). Returns the
    commit_id written.

    A: short-lock, snapshot, commit_obs, release.
    B: lock-free merge from the snapshot (NO canonical reads — enforced by
       the _OCC_PHASE=="B" probe).
    C: short-lock, re-read commit_now; == ⇒ commit fresh id; != ⇒ bounded
       A→B→C retry (N=3) then abort with the exact spec string.
    """
    global _OCC_PHASE
    attempts = 0
    while True:
        attempts += 1
        # --- Step A (short lock) ---
        tok_a = acquire_lock(lock_path, "wait_30s", ctx.pinned_utc)
        try:
            snapshot = _occ_snapshot(ctx, state_root)
            _pre = _occ_marker_state(state_root)
            commit_obs = _pre[1]
            _seed_commit_counter_from(commit_obs)
        finally:
            release_lock(lock_path, tok_a)

        # --- Step B (NO lock, NO canonical reads) ---
        _OCC_PHASE = "B"
        try:
            merged = _occ_audit_deltas(ctx, snapshot)
            # drift-state.md Update step (`/audit`): canonical-microsecond
            # audit_run_id + parse-to-datetime monotonic bump,
            # computed lock-free from the Step A snapshot.
            merged["drift_state"] = _occ_merge_drift_state(
                ctx, snapshot, merged["profile"]
            )
        finally:
            _OCC_PHASE = None

        # --- Step C (short lock) ---
        tok_c = acquire_lock(lock_path, "wait_30s", ctx.pinned_utc)
        try:
            now_state = _occ_marker_state(state_root)
            commit_now = now_state[1]
            if commit_now != commit_obs:
                # Concurrent commit landed during B → bounded A→B→C retry.
                if attempts >= 3:
                    raise OccConflictAbort(
                        "state not persisted due to concurrent activity; re-run."
                    )
                continue  # release happens in finally, then re-loop A→B→C
            commit_id = _mint_commit_id()
            _occ_commit(ctx, state_root, merged, commit_id, state)
            return commit_id
        finally:
            release_lock(lock_path, tok_c)


class OccConflictAbort(Exception):
    """Raised when OCC exhausts its N=3 bounded compare-and-commit
    retries."""


class GenesisRequiredAbort(Exception):
    """Raised when a Final-Phase commit is attempted on an `absent`
    (markerless) source set without the genesis sub-step having minted
    the first commit_id ("absent" is non-comparable; only Step
    0.5 mints the genesis id — a Final Phase that observes absent defers,
    it never invents a value)."""


# Source files that vote on torn classification (the same 4
# sources the commit_id marker preflight reads; state-summary.md is the
# derived cache and NEVER participates in torn classification). Derived
# from the
# single _SOURCE_READERS source of truth so the file list cannot drift
# out of sync with the preflight / per-file observer.
_TORN_SOURCE_FILES = tuple(name for name, _reader in _SOURCE_READERS)


def _observed_source_commit_ids(state_root: Path) -> list[tuple[str, str | None]]:
    """Return [(filename, observed commit_id or None)] for the 4 SOURCE
    files in marker-preflight order. None ⇒ the file is absent or carries
    no commit_id marker. The summary is intentionally excluded — it is the
    derived cache, never a torn-classification authority. Derived
    from the single _SOURCE_READERS source of truth (same list+reader
    pairing the commit_id marker preflight uses)."""
    return [
        (name, reader(state_root / name)) for name, reader in _SOURCE_READERS
    ]


def recover_torn_set(ctx: RunContext, state_root: Path) -> str:
    """Torn-set recovery: PRESERVE-FIRST, then STOP.

    Invoked ONLY when the commit_id marker preflight (``_occ_marker_state``
    — the SAME classifier the ``uniform``/``absent`` branches use; this is
    its partial/mixed outcome, not a parallel detector) returns ``torn``.

    Order is contractually fixed (the torn-set recovery contract):
      1. PRESERVE FIRST — before anything else, copy all 4 SOURCE files
         BYTE-FOR-BYTE into ``local/legacy-backup/{ISO-8601-UTC}/`` (the
         ISO dir name comes from the pinned clock via the existing
         legacy-backup quarantine helper — deterministic, never
         ``datetime.now()``). The originals are LEFT IN PLACE (copy, not
         move): a torn set is preserved, not consumed.
      2. Emit a precise diagnostic naming each of the 4 source files and
         its observed ``commit_id`` (or ``absent``).
      3. STOP — NO auto-merge, NO auto-reinit, NO commit, NO new
         ``commit_id`` minted (the path never routes through
         ``_stamp_commit_id``). The derived summary is NEVER a recovery
         authority. Reinitialization is an explicit user action only and
         is NOT modelled here.

    Returns the diagnostic string (also printed to stderr)."""
    # 1. PRESERVE FIRST — deterministic ISO dir from the pinned clock,
    #    reusing the exact legacy-backup quarantine path Step 0.5 uses
    #    (ctx.pinned_utc with ':' -> '-', collision-suffixed).
    ts_label = ctx.pinned_utc.replace(":", "-")
    backup_dir = _unique_backup_dir(state_root, ts_label)
    backup_dir.mkdir(parents=True, exist_ok=True)
    for name in _TORN_SOURCE_FILES:
        src = state_root / name
        if src.exists():
            # Byte-for-byte copy (NOT move): the torn originals stay in
            # local/ untouched; the quarantine is an additive snapshot.
            shutil.copyfile(str(src), str(backup_dir / name))

    # 2. Precise per-file diagnostic (observed commit_id or "absent").
    observed = _observed_source_commit_ids(state_root)
    detail = ", ".join(
        f"{fname}={cid if cid is not None else 'absent'}"
        for fname, cid in observed
    )
    diagnostic = (
        "TORN STATE DETECTED: the 4 canonical source files carry "
        f"non-uniform commit_id ({detail}). Preserved byte-for-byte to "
        f"{backup_dir.name}/ under legacy-backup/. STOP: no merge, no "
        "reinit, no commit performed — reinitialization is an explicit "
        "user action."
    )
    print(f"WARNING: {diagnostic}", file=sys.stderr)
    # 3. STOP — caller returns immediately; no merge/commit/new commit_id.
    return diagnostic


def run_occ_scenario(ctx: RunContext, state: WorkspaceState) -> WorkspaceState:
    """Scripted shell-A OCC /audit with shell B's full A→B→C commit injected
    between A's Step A release and A's Step C acquire (the OCC Step C
    changed-commit_id retry branch + the concurrent-shell mutual-exclusion
    CI assertions).

    Deterministic, single-threaded, NO real concurrency: the "injection"
    is a one-shot scripted hook fired the first time A enters its Step B
    window. Drives the fixture to its frozen golden:
      input commit-0001 → A snapshots commit-0001 → B commits commit-0002
      → A's Step C sees commit-0002 != commit-0001 → A retries → A re-snaps
      commit-0002, re-merges, commits commit-0003 (final, uniform)."""
    global _OCC_PHASE, _OCC_B_INJECTED
    state_root = _state_root(ctx)
    lock_path = state_root / ".state.lock"

    attempts = 0
    while True:
        attempts += 1
        # --- Shell A Step A (short lock) ---
        tok_a = acquire_lock(lock_path, "wait_30s", ctx.pinned_utc)
        try:
            snapshot = _occ_snapshot(ctx, state_root)
            commit_obs = _occ_marker_state(state_root)[1]
            _seed_commit_counter_from(commit_obs)
        finally:
            release_lock(lock_path, tok_a)

        # --- Shell A Step B (NO lock, NO canonical reads) ---
        _OCC_PHASE = "B"
        try:
            merged = _occ_audit_deltas(ctx, snapshot)
            # drift-state.md Update step (`/audit`): canonical-microsecond
            # audit_run_id + parse-to-datetime monotonic bump,
            # computed lock-free from the Step A snapshot.
            merged["drift_state"] = _occ_merge_drift_state(
                ctx, snapshot, merged["profile"]
            )
            # Scripted injection: shell B's FULL A→B→C commit, exactly once,
            # while shell A is mid-Step-B. _OCC_PHASE is briefly cleared so
            # B's own legitimate (lock-held) reads are not misattributed to
            # A's Step-B no-read window, then restored.
            if not _OCC_B_INJECTED:
                _OCC_B_INJECTED = True
                _OCC_PHASE = None
                try:
                    _occ_one_commit_burst(ctx, state_root, lock_path, None)
                finally:
                    _OCC_PHASE = "B"
        finally:
            _OCC_PHASE = None

        # --- Shell A Step C (short lock) ---
        tok_c = acquire_lock(lock_path, "wait_30s", ctx.pinned_utc)
        try:
            commit_now = _occ_marker_state(state_root)[1]
            if commit_now != commit_obs:
                if attempts >= 3:
                    raise OccConflictAbort(
                        "state not persisted due to concurrent activity; re-run."
                    )
                # Bounded A→B→C retry: re-snapshot, re-merge A's already-
                # computed /audit deltas onto the new snapshot, re-commit.
                # The scripted B-injection does NOT re-fire (one-shot guard),
                # so the retry runs A→B→C only — modelling the OCC
                # compare-and-commit retry.
                continue
            commit_id = _mint_commit_id()
            _occ_commit(ctx, state_root, merged, commit_id, state)
            return state
        finally:
            release_lock(lock_path, tok_c)


def step_0_5_genesis(ctx: RunContext, state: WorkspaceState) -> WorkspaceState:
    """commit_id marker preflight `absent` branch — Step 0.5 GENESIS
    (legacy upgrade).

    Invoked ONLY when the commit_id marker preflight (``_occ_marker_state``
    — the SAME classifier the ``uniform``/``torn`` branches use; this is its
    all-markerless ``absent`` outcome, not a parallel detector) reports
    ``absent`` AFTER step_0_5 has run. step_0_5 has already locked,
    classified the markerless-but-valid legacy JSON sources as
    present-valid against their own commit_id-OPTIONAL legacy wrappers,
    found no legacy MD to quarantine, and regenerated the summary cache.

    Genesis MINTS the FIRST ``commit_id`` and stamps the existing legacy
    canonical set with it — it does NOT re-run /audit detection (the
    legacy profile CONTENT is preserved; genesis only ADDS the marker and
    bumps the profile to the commit_id-required wrapper). It reuses the
    EXACT T8 mint/stamp/commit chain (``_seed_commit_counter_from`` →
    ``_mint_commit_id`` → ``_occ_commit`` → ``_stamp_commit_id``) so the
    genesis-written profile is ``schema_version 1.3.0`` WITH the minted
    ``commit_id`` (never a 1.2.0 profile carrying a commit_id). No
    parallel mint/stamp; deterministic (counter seeded from the absent
    state ⇒ no observed nonce ⇒ first mint ``commit-0001``; pinned clock;
    no ``datetime.now()``/sleep/randomness).

    Lock-disciplined like the other Final-Phase writers (short lock,
    re-read marker under lock for idempotence: if another writer already
    minted — set is now ``uniform`` — adopt on-disk and skip; genesis is
    one-shot per legacy state)."""
    global _GENESIS_MINTED
    state_root = _state_root(ctx)
    lock_path = state_root / ".state.lock"
    lock_token = acquire_lock(lock_path, "wait_30s", ctx.pinned_utc)
    try:
        # Idempotence guard under lock: re-read the marker. If it is no
        # longer `absent`, genesis already happened (another writer) —
        # adopt the on-disk canonical set and do NOT re-mint.
        marker_now = _occ_marker_state(state_root)[0]
        if marker_now != "absent":
            for fname, attr in (
                ("profile.json", "profile"),
                ("recommendations.json", "recommendations"),
            ):
                p = state_root / fname
                if p.exists():
                    setattr(state, attr, json.loads(p.read_text(encoding="utf-8")))
            cl = state_root / "config-changelog.md"
            if cl.exists():
                state.changelog = cl.read_text(encoding="utf-8")
            ss = state_root / "state-summary.md"
            if ss.exists():
                state.state_summary = ss.read_text(encoding="utf-8")
            return state

        # Build the merge bundle from the post-step_0_5 in-memory state
        # (profile/recommendations/changelog) + drift-state from disk.
        # No /audit delta merge — genesis preserves legacy CONTENT and
        # only stamps the marker (skill_sequence is empty for the genesis
        # fixture, mirroring the state-lock-* Step-0.5-isolation pattern).
        drift_state_path = state_root / "drift-state.json"
        try:
            drift_state = (
                json.loads(drift_state_path.read_text(encoding="utf-8"))
                if drift_state_path.exists()
                else _empty_drift_state(ctx.pinned_utc)
            )
        except (OSError, json.JSONDecodeError):
            drift_state = _empty_drift_state(ctx.pinned_utc)

        merged = {
            "profile": state.profile,
            "recommendations": state.recommendations,
            "changelog": state.changelog,
            "drift_state": drift_state,
        }

        # Seed from the OBSERVED nonce — which is None for an `absent`
        # set, so the counter stays 0 and the FIRST mint is commit-0001
        # (the genesis id). _seed_commit_counter_from is the same helper
        # the OCC Step A uses; passing the absent-state nonce (None) is a
        # no-op on the counter, which is exactly the genesis semantics.
        _seed_commit_counter_from(_occ_marker_state(state_root)[1])
        # Flag the mint BEFORE _occ_commit so its defensive
        # "absent without genesis ⇒ abort" guard permits THIS legitimate
        # genesis first-mint write (the only sanctioned absent→commit).
        _GENESIS_MINTED = True
        commit_id = _mint_commit_id()
        _occ_commit(ctx, state_root, merged, commit_id, state)
        return state
    finally:
        release_lock(lock_path, lock_token)


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
        # Emit monorepo audit-output.md per per-package-rollup.md format.
        # Subpackage Score Rollup section renders when monorepo_detection.detected==true
        # AND subpackage_coverage.package_roots_total>0 (output-format.md conditional rule).
        audit_output = (
            "# /audit — Monorepo Run\n\n"
            "Root `CLAUDE.md` detected; 2 workspace packages contain their own `CLAUDE.md`.\n\n"
            "## Subpackage Score Rollup\n\n"
            "  min=60.0, median=60.0, worst=packages/api, packages/web "
            "(2 scored, 0 without CLAUDE.md, 0 unscored)\n\n"
            "| Path | Score | Cap |\n"
            "|---|---|---|\n"
            "| packages/api | 60.0 | 100 |\n"
            "| packages/web | 60.0 | 100 |\n"
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
                    "version": "audit-score-v4.1.0",
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
                    "version": "audit-score-v4.1.0",
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
            "monorepo_detection": {
                "detected": True,
                "evidence": [
                    {
                        "type": "workspace_declaration",
                        "ecosystem": "node",
                        "manifest": "package.json",
                        "field": "workspaces",
                        "raw_value": ["packages/*"],
                        "resolved_roots": ["packages/api", "packages/web"],
                        "resolved_roots_total": 2,
                        "resolved_roots_truncated": False,
                    },
                ],
                "package_roots": ["packages/api", "packages/web"],
                "package_roots_for_scoring": ["packages/api", "packages/web"],
                "package_root_caps": {
                    "display": 20,
                    "scored": 50,
                    "unscored_count_in_view": 0,
                    "total_filtered": 2,
                },
                "notes": [],
            },
            "claude_code_configuration_state": {
                "claude_md": {
                    "exists": True,
                    "section_count": 5,
                    "subpackage_coverage": {
                        "package_roots_total": 2,
                        "with_claude_md": 2,
                        "without_claude_md": 0,
                        "scored_count": 2,
                    },
                    "subpackages": [
                        {
                            "path": "packages/api",
                            "claude_md_path": "packages/api/CLAUDE.md",
                            "final_score": 60.0,
                            "cap_tier": 100,
                            "lav_breakdown": {
                                "L1": 0, "L2": 0, "L3": 0, "L4": 0, "L5": 1, "L6": 0,
                            },
                        },
                        {
                            "path": "packages/web",
                            "claude_md_path": "packages/web/CLAUDE.md",
                            "final_score": 60.0,
                            "cap_tier": 100,
                            "lav_breakdown": {
                                "L1": 0, "L2": 0, "L3": 0, "L4": 0, "L5": 1, "L6": 0,
                            },
                        },
                    ],
                },
                "settings_json": {"exists": False, "has_permissions": False},
                "rules_count": 0,
                "agents_count": 0,
                "hooks_count": 0,
                "mcp_servers_count": 0,
                "model": "claude-opus-4-7",
                "scoring_model_ack": {
                    "version": "audit-score-v4.1.0",
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
                    "version": "audit-score-v4.1.0",
                    "seen_count": 0,
                },
            },
        }
    raise KeyError(f"no audit detection preset for fixture {name!r}")


def handle_secure(ctx: RunContext, state: WorkspaceState) -> WorkspaceState:
    """Process /secure fixture run: profile merge + changelog + recommendations.

    Per-fixture detection presets live in _secure_detect_profile. Phase 1
    FIXTURE_SCENARIOS does not include /secure; the atomic runners
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
    FIXTURE_SCENARIOS does not include /optimize; the atomic runners
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
    # drift-state.json migration fixtures: test step_0_5 migration path.
    # skill_sequence=[] — these fixtures verify Step 0.5 in isolation; no skill run needed.
    "drift-state-cold-start": {"skill_sequence": [], "pre_run": []},
    "drift-state-migrate-valid-anchor": {"skill_sequence": [], "pre_run": []},
    "drift-state-migrate-all-null-anchors": {"skill_sequence": [], "pre_run": []},
    "drift-state-corrupt-quarantine": {"skill_sequence": [], "pre_run": []},
    "drift-state-skip-if-valid": {"skill_sequence": [], "pre_run": []},
    # Concurrent-shell mutual-exclusion fixture (the OCC protocol + its CI
    # assertions). DELIBERATE
    # TDD red: the stub acquire_lock has no contention detection, so the
    # scripted two-shell A↔B interleaving cannot serialize and the produced
    # state diverges from the golden. Task 7 (real mkdir/token/rename-aside
    # short-lock) + Task 8 (OCC snapshot/commit + scripted concurrent commit
    # during B + commit_id minting) make it pass. skill_sequence=[] mirrors the
    # drift-state-* Step-0.5-isolation pattern; the OCC driver is wired
    # verifier-side (run_occ_scenario) keyed off the input commit_id markers.
    "state-lock-concurrent": {"skill_sequence": [], "pre_run": []},
    # OCC compare-and-commit conflict (the OCC Step C changed-commit_id
    # retry branch + the ASSERT_NO_READ_DURING_B / ASSERT_COMMITID_UNIQUE
    # CI assertions). Same scripted
    # interleaving as state-lock-concurrent, observed through the OCC lens;
    # pins the same deterministic golden so a regression in either the lock
    # primitive or the OCC layer trips both fixtures independently.
    "state-lock-occ-conflict": {"skill_sequence": [], "pre_run": []},
    # Torn-set detection + preserve-first recovery. The 4 SOURCE
    # files carry a NON-UNIFORM commit_id (a crash interrupted a prior
    # writer between source writes). The commit_id marker preflight's torn
    # branch
    # quarantines all 4 sources byte-for-byte to legacy-backup/{ISO}/,
    # surfaces a per-file diagnostic, and STOPS (no merge/reinit/commit/new
    # commit_id). skill_sequence=[] mirrors the state-lock-* Step-0.5
    # isolation pattern; the torn preflight is wired verifier-side
    # (run_fixture) keyed off the input commit_id markers.
    "state-lock-torn": {"skill_sequence": [], "pre_run": []},
    # Legacy-upgrade genesis (the commit_id marker preflight `absent`
    # branch). ALL 4 SOURCE files lack commit_id (a pre-marker legacy
    # state). The commit_id marker preflight
    # classifies `absent`; after step_0_5 leaves the markerless-valid
    # sources in place, the genesis sub-step mints the FIRST commit_id
    # (commit-0001) and stamps the legacy set (profile→schema 1.3.0 +
    # commit_id) via the same T8 mint/stamp/commit chain — legacy CONTENT
    # preserved, marker added. skill_sequence=[] mirrors the state-lock-*
    # Step-0.5 isolation pattern; the genesis path is wired verifier-side
    # (run_fixture) gated to this fixture so the 39 pre-existing
    # markerless `absent` fixtures stay byte-identical.
    "state-lock-genesis": {"skill_sequence": [], "pre_run": []},
    # audit_run_id canonical microsecond + monotonic bump. Reuses
    # the state-lock-occ-conflict scripted interleaving (run_occ_scenario)
    # because that driver already produces TWO /audit write bursts at the
    # SAME pinned clock — the natural same-microsecond collision the
    # canonical-microsecond + monotonic-bump rule fixes.
    # The ONLY pre-state diff vs. state-lock-occ-conflict is drift-state.json
    # (an ALREADY-ESTABLISHED ledger so the drift-state.md Update step's
    # append branch fires; occ-conflict is a cold-start the OCC path leaves
    # unchanged). Shell B's emission does NOT collide (pinned 04-14 > the
    # 04-13 pre-existing max); shell A's retried emission DOES (same
    # microsecond as B's) ⇒ bumps to max+1µs. skill_sequence=[] mirrors the
    # state-lock-* Step-0.5-isolation pattern; the OCC driver is wired
    # verifier-side keyed off the uniform input commit_id markers.
    "audit-run-id-collision": {"skill_sequence": [], "pre_run": []},
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
# Semantic assertions (run BEFORE byte diff)
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
        "1.2.0": "profile.schema.v1.2.0.json",
        # v1.3.0 is the commit_id-required wrapper (the per-write commit_id
        # nonce + schema requiredness): the OCC commit stamps
        # metadata.commit_id and writes profile at this
        # version, so assert_schema_valid must be able to dispatch it.
        "1.3.0": "profile.schema.v1.3.0.json",
    }

    # Recommendations dispatcher (mirrors profile pattern).
    # combined recommendations.schema.json was retired in favor of the
    # base + versioned-wrapper architecture.
    recs_version_to_wrapper = {
        "1.0.0": "recommendations.schema.v1.0.0.json",
        "1.1.0": "recommendations.schema.v1.1.0.json",
    }
    recs_base_schema = _load_schema("recommendations.schema.base.json")
    registry = registry.with_resources(
        [("recommendations.schema.base.json", Resource.from_contents(recs_base_schema))]
    )

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
        declared_recs_version = state.recommendations.get("schema_version")
        if declared_recs_version not in recs_version_to_wrapper:
            failures.append(
                f"recommendations.json schema_version '{declared_recs_version}' not dispatchable; "
                f"expected one of {sorted(recs_version_to_wrapper)}"
            )
        else:
            recs_schema = _load_schema(recs_version_to_wrapper[declared_recs_version])
            try:
                jsonschema.Draft202012Validator(recs_schema, registry=registry).validate(state.recommendations)
            except jsonschema.ValidationError as e:
                failures.append(f"recommendations.json schema invalid ({declared_recs_version}): {e.message}")
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
    current profile + recommendations + changelog + drift-state."""
    if state.profile is None or state.recommendations is None:
        return []
    state_root = _state_root(ctx)
    summary_path = state_root / "state-summary.md"
    if not summary_path.exists():
        return ["state-summary.md not present"]
    on_disk = summary_path.read_text(encoding="utf-8")
    drift_state_path = state_root / "drift-state.json"
    try:
        drift_state = json.loads(
            drift_state_path.read_text(encoding="utf-8")
        ) if drift_state_path.exists() else None
    except (OSError, json.JSONDecodeError):
        drift_state = None
    # OCC path: the summary echoes the per-write source commit_id nonce.
    # Re-render with the SAME nonce the sources carry so this invariant
    # compares like for like. Non-OCC fixtures have no commit_id ⇒ None ⇒
    # unchanged.
    src_commit_id = (
        state.profile.get("metadata", {}).get("commit_id")
        if isinstance(state.profile, dict) else None
    )
    expected = render_state_summary(
        state.profile, state.recommendations, state.changelog, ctx,
        drift_state=drift_state, commit_id=src_commit_id,
    )
    if on_disk != expected:
        return ["state-summary.md not derived from current sources (in-memory re-render mismatch)"]
    return []


def assert_no_read_during_b(ctx: RunContext, state: WorkspaceState) -> list[str]:
    """ASSERT_NO_READ_DURING_B (the OCC lock-free Step B and its CI
    assertion): zero canonical-file reads occur
    between shell A's Step A lock-release and its Step C lock-acquire — the
    lock-free merge MUST operate solely on the in-memory Step A snapshot.
    The OCC layer sets _OCC_PHASE=="B" across exactly that window and every
    canonical read is probe-instrumented; any recorded read is a violation.
    Surfaces as a [FAIL] semantic message (same channel as the other
    invariants / LockContention), never an unhandled crash."""
    if _OCC_READS_DURING_B:
        return [
            "ASSERT_NO_READ_DURING_B: canonical read(s) during Step B "
            f"(lock-free window): {sorted(set(_OCC_READS_DURING_B))}"
        ]
    return []


def assert_commitid_unique(ctx: RunContext, state: WorkspaceState) -> list[str]:
    """ASSERT_COMMITID_UNIQUE (the per-write commit_id nonce and its CI
    assertion): every successful write burst AND
    every recovery/reinit mints a DISTINCT commit_id — no reuse across the
    run (a reused id would void OCC / torn-set / ABA detection). Inspects
    every id minted via _mint_commit_id this run."""
    if len(_OCC_COMMIT_IDS) != len(set(_OCC_COMMIT_IDS)):
        return [
            "ASSERT_COMMITID_UNIQUE: commit_id reused across write bursts: "
            f"{_OCC_COMMIT_IDS}"
        ]
    return []


# ---------------------------------------------------------------------------
# Byte diff (last gate)
# ---------------------------------------------------------------------------


# Golden-only artifacts: present as frozen reference snapshots in golden/
# but the reference Python skill handlers in this script do not (yet) emit
# them. byte-diff comparison is skipped when the file is missing from the
# actual run; once present, byte equality is enforced. This existence guard
# lets goldens land ahead of generator wiring while still catching golden
# regression once a future task connects the handler to the artifact path.
# Migration fixture has no entry here (and no qa-report.md golden) — its
# legacy-state preservation contract is unchanged.
GOLDEN_ONLY_ARTIFACTS = frozenset({"local/qa-report.md"})


def byte_diff_tree(actual: Path, golden: Path, input_dir: Path | None = None) -> str:
    """Recursive byte-for-byte comparison of directory trees.

    Compares every file present in golden against the same path in actual.
    Extra files in actual are ONLY flagged if they did NOT already exist
    unchanged in the fixture's input/ (the verifier mutates a work-copy of
    input/, so input source files like package.json are allowed to linger
    unchanged — goldens only capture the skill-produced artifacts).

    Files listed in GOLDEN_ONLY_ARTIFACTS are skipped from the
    "missing file" check when absent in actual — they are frozen
    reference snapshots whose generators are not yet wired. When such a
    file IS present in actual, byte equality is still enforced.

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
        # Allowed: golden-only reference snapshot whose generator is
        # not yet wired into the Python reference handler.
        if rel in GOLDEN_ONLY_ARTIFACTS:
            continue
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

    Excludes the entire state-mutation short-lock surface, which
    is transient and must NEVER be byte-diffed against a golden:
      - the lock DIRECTORY ``local/.state.lock/`` and everything inside it
        (``owner.json``),
      - stale-reclaim tombstones ``local/.state.lock.dead.<token>/`` and
        their contents,
      - the sibling owner-tempfiles ``local/.state.lock.owner.*`` that
        ``_write_owner_json`` os.replace()s into the lock dir.
    All four share the ``.state.lock`` name-prefix, so excluding any path
    component that starts with ``.state.lock`` covers the directory, its
    contents, the dead-tombstones, and the tempfiles in one rule. (The old
    ``p.name == ".state.lock"`` test only matched the LEGACY single-FILE
    lock — it never matched ``owner.json`` inside the T7 directory lock, so
    a leaked/transient lock artifact would otherwise spuriously
    ``extra file``-diff and mask the real concurrency assertion.)"""
    if not root.exists():
        return set()
    out = set()
    for p in sorted(root.rglob("*")):
        if p.is_file():
            rel = p.relative_to(root)
            # Skip anything under / named within the short-lock surface.
            if any(part.startswith(".state.lock") for part in rel.parts):
                continue
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
    # Reset the per-run OCC instrumentation/counters so the deterministic
    # commit_id sequence restarts at commit-0001 for THIS fixture regardless
    # of how many fixtures ran before it in the loop.
    _reset_run_state()
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

        # Torn-set preflight — runs BEFORE step_0_5 so a torn set is
        # PRESERVED FIRST then STOPPED, with the originals left exactly as
        # found (step_0_5 would otherwise regen state-summary.md / recover,
        # mutating the very state the torn-set contract says to preserve).
        # Uses the SAME commit_id marker classifier the OCC `uniform`
        # branch uses
        # (`_occ_marker_state`) — the `torn` return is its partial/mixed
        # outcome, NOT a parallel detector. Fixtures whose 4 sources carry
        # NO commit_id (all pre-existing) classify `absent` and are
        # unaffected; only a genuinely non-uniform 4-source set trips this.
        try:
            torn_pre = _occ_marker_state(_state_root(ctx))
        except Exception:  # noqa: BLE001
            torn_pre = ("absent", None)
        if torn_pre[0] == "torn":
            # PRESERVE FIRST → diagnostic → STOP. No step_0_5, no skill
            # handlers, no OCC, no merge/reinit/commit, no new commit_id.
            # The originals stay byte-identical; the byte-diff gate against
            # the golden is the only post-condition (summary-derived
            # assertion is intentionally bypassed: torn recovery does NOT
            # regenerate the summary, so the preserved torn summary need not
            # re-render from the torn sources).
            recover_torn_set(ctx, _state_root(ctx))
            diff = byte_diff_tree(work_dir, golden_dir, input_dir=src_dir)
            if diff:
                return (False, "byte diff:\n  " + diff)
            return (True, "ok")

        # M2 (mutual-exclusion invariant): the torn branch ABOVE `return`s
        # before reaching step_0_5, and step_0_5 is the OTHER
        # `_unique_backup_dir` caller (its legacy-MD quarantine). That early
        # return is precisely what guarantees the two legacy-backup
        # quarantine writers (recover_torn_set here, step_0_5's Phase 5) can
        # never collide on the same pinned-clock ts_label in one run. Do NOT
        # insert any code between the torn block and step_0_5 that voids
        # this early return (e.g. a fall-through that lets a torn set also
        # reach step_0_5).
        state = step_0_5(ctx, state)
        for skill in scenario["skill_sequence"]:
            handler = SKILL_HANDLERS[skill]
            state = handler(ctx, state)

        # commit_id marker preflight (post-step_0_5). The SAME
        # `_occ_marker_state` classifier, three mutually-exclusive outcomes:
        #   uniform → OCC layer: scripted shell-A /audit with shell B's
        #             A→B→C commit injected during A's lock-free Step B
        #             (the OCC protocol + its CI assertions).
        #   absent  → GENESIS: this is a pre-marker legacy state;
        #             step_0_5 left the markerless-valid sources in place
        #             (commit_id-optional legacy wrappers) and regenerated
        #             the summary. The genesis sub-step mints the FIRST
        #             commit_id and stamps the legacy set (profile→1.3.0 +
        #             commit_id) via the same T8 mint/stamp/commit chain.
        #             "absent" is non-comparable — NOT a value, NOT 0,
        #             never OCC-comparable; ONLY this Step-0.5 genesis
        #             sub-step mints the genesis id.
        #   torn    → already handled by the pre-step_0_5 torn preflight
        #             above (returns before reaching here).
        # Fixtures whose input carries NO commit_id (all 39 pre-existing
        # skill-flow fixtures + the drift-state-* / migration set) classify
        # `absent` here. They keep their exact prior output because they do
        # NOT mirror the state-lock-genesis Step-0.5-isolation registration
        # — genesis only runs for state-lock-genesis (the sole fixture
        # whose 4 markerless sources are all present-valid post-step_0_5
        # with an empty skill_sequence); see the gate below.
        try:
            occ_pre = _occ_marker_state(_state_root(ctx))
        except Exception:  # noqa: BLE001
            occ_pre = ("absent", None)
        if occ_pre[0] == "uniform":
            state = run_occ_scenario(ctx, state)
        elif occ_pre[0] == "absent" and name == "state-lock-genesis":
            # Legacy-upgrade genesis. Gated to the dedicated fixture so
            # the 39 pre-existing `absent` fixtures (whose goldens have no
            # commit_id) are byte-unchanged: genesis is opt-in exactly like
            # the OCC `uniform` branch is keyed off input markers.
            state = step_0_5_genesis(ctx, state)

        # SEMANTIC ASSERTIONS BEFORE BYTE DIFF
        failures = []
        failures += assert_schema_valid(ctx, state)
        failures += assert_registry_lint(ctx, state)
        failures += assert_aliases_never_persist(ctx, state)
        failures += assert_legacy_quarantined(ctx, state, scenario)
        failures += assert_summary_derived_from_sources(ctx, state)
        failures += assert_no_read_during_b(ctx, state)
        failures += assert_commitid_unique(ctx, state)
        if failures:
            return (False, "semantic: " + "; ".join(failures))

        # BYTE DIFF as last gate
        diff = byte_diff_tree(work_dir, golden_dir, input_dir=src_dir)
        if diff:
            return (False, "byte diff:\n  " + diff)
        return (True, "ok")


def _find_bash() -> str:
    """Locate a working bash interpreter.

    On Windows, prefer Git Bash over WSL bash — WSL may resolve via PATH
    but fail with Hyper-V errors when Hyper-V isn't enabled, breaking
    fixture runs. On Linux/macOS, /usr/bin/bash from PATH is canonical.
    Returns absolute path or 'bash' as last-resort.
    """
    import platform  # noqa: PLC0415
    if platform.system() == "Windows":
        for cand in (
            r"C:\Program Files\Git\bin\bash.exe",
            r"C:\Program Files (x86)\Git\bin\bash.exe",
            r"C:\Program Files\Git\usr\bin\bash.exe",
        ):
            if Path(cand).is_file():
                return cand
    found = shutil.which("bash")
    return found if found else "bash"


def _find_pwsh() -> str | None:
    """Locate a working PowerShell interpreter, or return None to skip.

    On Windows, prefer pwsh (PowerShell 7+) over powershell.exe (5.1) for
    parity with Linux. On Linux/macOS, /usr/bin/pwsh from PATH (provided by
    PowerShell 7+ install). Linux ubuntu-latest CI runner ships pwsh by
    default so the ps1 fixture lane runs in CI.
    Returns absolute path or None if no PowerShell is available — caller
    skips the lane with a warning rather than failing.
    """
    import platform  # noqa: PLC0415
    if platform.system() == "Windows":
        for cand in (
            r"C:\Program Files\PowerShell\7\pwsh.exe",
            r"C:\Program Files\PowerShell\6\pwsh.exe",
            r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
        ):
            if Path(cand).is_file():
                return cand
    found = shutil.which("pwsh")
    if found:
        return found
    return shutil.which("powershell")


def _canonical_json(s: str) -> str:
    """Return canonical-form JSON string for cross-format comparison.

    The bash hook emits jq-default formatting (2-space indent, single-space
    after colons). The PowerShell hook emits ConvertTo-Json formatting
    (4-space indent, double-space after colons). For semantic equivalence
    checks across both lanes, normalize via json.loads + json.dumps with
    sorted keys and compact separators. Empty input returns empty string.
    """
    if not s.strip():
        return ""
    try:
        return json.dumps(json.loads(s), sort_keys=True, separators=(",", ":"))
    except json.JSONDecodeError:
        return s  # malformed; let exact comparison surface the failure


def _clear_sessionstart_lock(input_dir: Path) -> None:
    """Remove a stale .session-start.lock dir left by a SIGKILLed prior hook
    run (the hook's EXIT-trap rmdir is skipped on SIGKILL). Without this, the
    next invocation silently exits 0 with no stdout and an output-producing
    fixture FAILs. Protects every sessionstart fixture, including ones with
    no setup.sh. Sequential lanes make a concurrent-race variant unreachable.

    Called after setup.sh and immediately before the hook subprocess in both
    the bash and PowerShell lanes; the lock dir, when present here, is always
    a leftover (no live hook holds it at this point).
    """
    lock = (input_dir / ".claude" / ".plugin-cache"
            / "guardians-of-the-claude" / "local" / ".session-start.lock")
    # The hook creates this lock with `mkdir` and removes it with `rmdir`
    # (empty by contract). Mirror that here. Deliberately NOT
    # shutil.rmtree(ignore_errors=True): swallowing a removal failure would
    # silently reintroduce the exact flake this guards against. Letting
    # os.rmdir raise points CI straight at the cause instead of the
    # confusing "empty output diverged" symptom, and a non-empty lock is a
    # real anomaly worth surfacing rather than nuking.
    if lock.is_dir():
        os.rmdir(lock)


def run_sessionstart_fixture(name: str) -> tuple[bool, str]:
    """Run plugin/hooks/session-start.sh against a sessionstart-orchestrator fixture.

    Each fixture has input/ (synthetic project state) and expected.json.
    Optional setup.sh per fixture handles mtime adjustment for drift legacy_mtime
    scenarios (git checkout does not preserve mtimes).
    Hook runs with cwd=input, stdin source determined by fixture name,
    SMOKE_PINNED_UTC=2026-05-07T00:00:00Z. Output byte-equal to expected.json.
    """
    fixture_dir = ROOT / "ci" / "fixtures" / "sessionstart-orchestrator" / name
    input_dir = fixture_dir / "input"
    expected_path = fixture_dir / "expected.json"
    setup_path = fixture_dir / "setup.sh"
    if not input_dir.is_dir() or not expected_path.is_file():
        return False, f"fixture missing: {fixture_dir}"

    if "clear" in name:
        stdin_payload = '{"source":"clear"}'
    elif "compact" in name:
        stdin_payload = '{"source":"compact"}'
    else:
        stdin_payload = '{"source":"startup"}'

    hook_path = ROOT / "plugin" / "hooks" / "session-start.sh"
    env = os.environ.copy()
    env["SMOKE_PINNED_UTC"] = "2026-05-07T00:00:00Z"
    bash_bin = _find_bash()

    # Optional setup.sh runs first (mtime adjustments for drift legacy_mtime fixtures).
    # setup.sh self-locates via $(dirname "$0") so cwd doesn't matter.
    if setup_path.is_file():
        try:
            subprocess.run(
                [bash_bin, str(setup_path)],
                check=True, capture_output=True,
                cwd=str(fixture_dir), env=env, timeout=10,
            )
        except subprocess.TimeoutExpired:
            return False, "setup.sh timed out"
        except subprocess.CalledProcessError as exc:
            stderr_decoded = exc.stderr.decode("utf-8", errors="replace") if exc.stderr else ""
            stdout_decoded = exc.stdout.decode("utf-8", errors="replace") if exc.stdout else ""
            return False, f"setup.sh failed (rc={exc.returncode}): stdout={stdout_decoded[:200]!r} stderr={stderr_decoded[:200]!r}"

    _clear_sessionstart_lock(input_dir)

    try:
        proc = subprocess.run(
            [bash_bin, str(hook_path)],
            input=stdin_payload.encode("utf-8"),
            capture_output=True,
            cwd=str(input_dir), env=env, timeout=10,
        )
    except subprocess.TimeoutExpired:
        return False, "hook timed out"

    # Normalize line endings before comparison.
    # Python's read_text uses universal newlines (CRLF -> LF on Windows checkout)
    # but subprocess stdout preserves whatever bash emitted (CRLF on Git Bash).
    # Without normalization, every line break would diverge on Windows.
    actual = proc.stdout.decode("utf-8", errors="replace").replace("\r\n", "\n").strip() if proc.stdout else ""
    expected = expected_path.read_text(encoding="utf-8").strip()
    if actual == expected:
        return True, "byte-equal"
    return False, f"diverged:\n  expected: {expected[:200]}\n  actual:   {actual[:200]}"


def run_sessionstart_ps1_fixture(name: str) -> tuple[bool, str]:
    """Run plugin/hooks/session-start.ps1 against a sessionstart-orchestrator
    fixture for cross-platform parity verification.

    Mirrors run_sessionstart_fixture's contract: same setup.sh handling, same
    SMOKE_PINNED_UTC, same fixture directory layout. Comparison is against
    canonical JSON form (json.loads + sorted keys + compact separators) since
    bash uses jq-default pretty format and PowerShell uses ConvertTo-Json
    formatting that differ in whitespace/indent — equivalence is semantic.
    Caller is responsible for not invoking this when _find_pwsh() returns None.
    """
    fixture_dir = ROOT / "ci" / "fixtures" / "sessionstart-orchestrator" / name
    input_dir = fixture_dir / "input"
    expected_path = fixture_dir / "expected.json"
    setup_path = fixture_dir / "setup.sh"
    if not input_dir.is_dir() or not expected_path.is_file():
        return False, f"fixture missing: {fixture_dir}"

    if "clear" in name:
        stdin_payload = '{"source":"clear"}'
    elif "compact" in name:
        stdin_payload = '{"source":"compact"}'
    else:
        stdin_payload = '{"source":"startup"}'

    hook_path = ROOT / "plugin" / "hooks" / "session-start.ps1"
    env = os.environ.copy()
    env["SMOKE_PINNED_UTC"] = "2026-05-07T00:00:00Z"
    pwsh_bin = _find_pwsh()
    if pwsh_bin is None:
        return False, "pwsh not found (caller should have skipped)"

    if setup_path.is_file():
        bash_bin = _find_bash()
        try:
            subprocess.run(
                [bash_bin, str(setup_path)],
                check=True, capture_output=True,
                cwd=str(fixture_dir), env=env, timeout=10,
            )
        except subprocess.TimeoutExpired:
            return False, "setup.sh timed out"
        except subprocess.CalledProcessError as exc:
            stderr_decoded = exc.stderr.decode("utf-8", errors="replace") if exc.stderr else ""
            stdout_decoded = exc.stdout.decode("utf-8", errors="replace") if exc.stdout else ""
            return False, f"setup.sh failed (rc={exc.returncode}): stdout={stdout_decoded[:200]!r} stderr={stderr_decoded[:200]!r}"

    _clear_sessionstart_lock(input_dir)

    try:
        proc = subprocess.run(
            [pwsh_bin, "-NoProfile", "-File", str(hook_path)],
            input=stdin_payload.encode("utf-8"),
            capture_output=True,
            cwd=str(input_dir), env=env, timeout=10,
        )
    except subprocess.TimeoutExpired:
        return False, "hook timed out"

    actual = _canonical_json(proc.stdout.decode("utf-8", errors="replace") if proc.stdout else "")
    expected = _canonical_json(expected_path.read_text(encoding="utf-8"))
    if actual == expected:
        return True, "canonical-json-equal"
    return False, f"diverged:\n  expected: {expected[:200]}\n  actual:   {actual[:200]}"


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

    # CI lane: frozen skill-flow fixture manifest.
    fixtures = [
        "migration", "beginner-path", "warm-start", "monorepo",
        # drift-state.json migration fixtures (step_0_5 isolation).
        "drift-state-cold-start",
        "drift-state-migrate-valid-anchor",
        "drift-state-migrate-all-null-anchors",
        "drift-state-corrupt-quarantine",
        "drift-state-skip-if-valid",
        # Concurrent-shell mutual exclusion (the OCC protocol + its CI
        # assertions) — DELIBERATE
        # TDD red until Task 7 (real short-lock) + Task 8 (OCC) land.
        "state-lock-concurrent",
        # OCC compare-and-commit conflict (the OCC Step C changed-commit_id
        # retry branch + the no-read-during-B / commit_id-uniqueness CI
        # assertions).
        "state-lock-occ-conflict",
        # Torn-set detection + preserve-first recovery: 4-source
        # non-uniform commit_id ⇒ quarantine all 4 to legacy-backup/{ISO}/
        # + diagnostic + STOP (no merge/reinit/commit).
        "state-lock-torn",
        # Legacy-upgrade genesis (the commit_id marker preflight `absent`
        # branch): 4-source
        # markerless legacy state ⇒ step_0_5 + genesis mints the FIRST
        # commit_id (commit-0001) and stamps the set (profile→1.3.0 +
        # commit_id) via the T8 mint/stamp/commit chain.
        "state-lock-genesis",
        # audit_run_id canonical microsecond + parse-to-datetime monotonic
        # bump: two same-pinned-microsecond /audit emissions ⇒
        # the second becomes max(existing)+1µs; all ids in canonical
        # .ffffff+00:00 form. Reuses the OCC scripted interleaving.
        "audit-run-id-collision",
    ]
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

    # SessionStart orchestrator fixtures (separate lane — exercises the hook
    # script directly rather than the skill-execution simulation).
    sessionstart_fixtures = [
        "fixture_no_signal", "fixture_drift_legacy_mtime", "fixture_drift_multi_reason",
        "fixture_unresolved_only", "fixture_unresolved_K_isolation",
        "fixture_repeated_decline_only", "fixture_all_three",
        "fixture_clear_source", "fixture_compact_source",
        "fixture_legacy_v1_0_0_read", "fixture_unknown_future_version",
        "fixture_stale_excluded", "fixture_pending_decline_count_status_guard",
        "fixture_drift_scoring_contract_bump", "fixture_drift_schema_then_scoring",
    ]
    for name in sessionstart_fixtures:
        try:
            passed, msg = run_sessionstart_fixture(name)
        except Exception as exc:  # noqa: BLE001
            passed = False
            msg = f"exception: {exc.__class__.__name__}: {exc}"
        tag = "PASS" if passed else "FAIL"
        print(f"[{tag}] sessionstart-bash/{name}: {msg}")
        if not passed:
            fail_count += 1

    # PowerShell parity lane — both bash and ps1 hooks must produce semantically
    # equivalent advisory text for each fixture. Skipped (with notice) when no
    # PowerShell interpreter is available; runs in CI on ubuntu-latest (pwsh
    # pre-installed) and on Windows local dev (pwsh 7+ or powershell.exe 5.1).
    if _find_pwsh() is None:
        print("[SKIP] sessionstart-ps1: no pwsh / powershell on PATH")
    else:
        for name in sessionstart_fixtures:
            try:
                passed, msg = run_sessionstart_ps1_fixture(name)
            except Exception as exc:  # noqa: BLE001
                passed = False
                msg = f"exception: {exc.__class__.__name__}: {exc}"
            tag = "PASS" if passed else "FAIL"
            print(f"[{tag}] sessionstart-ps1/{name}: {msg}")
            if not passed:
                fail_count += 1

    return 1 if fail_count else 0


if __name__ == "__main__":
    sys.exit(main())
