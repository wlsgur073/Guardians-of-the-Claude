#!/usr/bin/env python3
"""Assert sample list preconditions for the curated sample set.

Assertions:
  A1: sample-list file exists
  A2: frontmatter status == "ready"
  A3: frontmatter version == "2.0.0"
  A4: sample count in [8, 10]
  A5: distinct real ecosystems >= 4 (meta-only samples excluded from count)
  A6: no "TBD" literal in any sample row cell

Soft-skip rationale: sample-list.md is a local-only curation artifact (not
shipped). Contributors without the local list should see CI green.

Exit codes:
  0 - all assertions passed, OR soft-skip (file absent OR status=draft)
  1 - one or more assertions failed
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_LIST = REPO_ROOT / "docs" / "superpowers" / "v3-roadmap" / "phase-2a-sample-list.md"


def parse_frontmatter(text: str) -> dict[str, str]:
    """Parse simple YAML frontmatter (key: value pairs)."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        mm = re.match(r'^(\w+):\s*["\']?(.*?)["\']?\s*$', line)
        if mm:
            result[mm.group(1)] = mm.group(2)
    return result


def parse_sample_table(text: str) -> list[dict[str, str]]:
    """Extract rows from the '## Sample Repositories' markdown table."""
    section_match = re.search(r"^##\s+Sample Repositories\s*$", text, re.MULTILINE)
    if not section_match:
        return []

    tail = text[section_match.end():]
    rows: list[dict[str, str]] = []
    header_cols: list[str] | None = None

    for line in tail.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if rows and header_cols is not None:
                break
            continue
        inner = stripped.strip("|").strip()
        if set(inner.replace("|", "")) <= {"-", " ", ":"}:
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if header_cols is None:
            header_cols = [c.lower() for c in cells]
            continue
        if len(cells) != len(header_cols):
            continue
        rows.append(dict(zip(header_cols, cells)))
    return rows


def main() -> int:
    # A1: file exists (soft-skip if absent)
    if not SAMPLE_LIST.exists():
        print(f"SKIP - sample-list not present at {SAMPLE_LIST.relative_to(REPO_ROOT)}")
        print("       (sample-list is a local-only curation artifact, not shipped)")
        return 0

    text = SAMPLE_LIST.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    status = fm.get("status", "").lower()

    # A2 soft-skip path: draft status (curation not yet complete)
    if status == "draft":
        print(f"SKIP - sample-list status=draft (curation not yet complete)")
        return 0

    errors: list[str] = []

    # A2: status == "ready"
    if status != "ready":
        errors.append(f"A2 FAIL: frontmatter status must be 'ready'; got {status!r}")

    # A3: version == "2.0.0"
    version = fm.get("version", "")
    if version != "2.0.0":
        errors.append(f"A3 FAIL: frontmatter version must be '2.0.0' (curated state); got {version!r}")

    rows = parse_sample_table(text)

    # A4: count in [8, 10]
    count = len(rows)
    if not (8 <= count <= 10):
        errors.append(
            f"A4 FAIL: sample count must be in [8, 10]; got {count}"
        )

    # A5: distinct real ecosystems >= 4 (exclude meta self-reference)
    ecosystems: set[str] = set()
    for row in rows:
        eco = row.get("ecosystem", "").strip().lower()
        if eco and eco != "meta":
            ecosystems.add(eco)
    if len(ecosystems) < 4:
        errors.append(
            f"A5 FAIL: distinct real ecosystems must be >= 4; "
            f"got {len(ecosystems)} ({sorted(ecosystems)})"
        )

    # A6: no "TBD" literal in any cell
    for idx, row in enumerate(rows, start=1):
        for col, val in row.items():
            if re.search(r"\bTBD\b", val, re.IGNORECASE):
                errors.append(
                    f"A6 FAIL: row {idx} column {col!r} contains 'TBD' literal: "
                    f"{val!r} (measurement incomplete)"
                )

    if errors:
        print("FAIL - sample-list preconditions NOT met:")
        for err in errors:
            print(f"  {err}")
        return 1

    print(
        f"PASS - 6/6 assertions satisfied "
        f"({count} samples, {len(ecosystems)} distinct real ecosystems, "
        f"status=ready, version={version})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
