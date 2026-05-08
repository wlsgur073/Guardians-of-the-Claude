#!/usr/bin/env python3
"""Validate qa-report.md golden fixtures against artifact-shape rules.

Enforced rules:
  - Section list invariance: Score Summary → LAV Item Rationale → Bucket Rationale
    → Recommendations Linkage must appear in order (Sprint Contract Coverage is
    conditional and not enforced as required).
  - Forbidden tokens: roadmap phase identifiers, decision identifiers, internal
    task identifiers, internal release identifiers, gitignored paths.
  - Imperative-mood absence in LAV Item Rationale rows: counterfactual cells must
    use hypothetical-observation phrasing (no Add / Document / Update / Remove
    cell-leading verbs).
"""
from __future__ import annotations

import re
import sys
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
GOLDEN_GLOB = "ci/golden/**/qa-report.md"

REQUIRED_SECTIONS_ORDERED = [
    "## Score Summary",
    "## LAV Item Rationale",
    "## Bucket Rationale",
    "## Recommendations Linkage",
]
CONDITIONAL_SECTION = "## Sprint Contract Coverage"

FORBIDDEN_TOKENS = [
    re.compile(r"\bPhase\s+[0-9]+[a-z]?\b"),
    re.compile(r"\bDEC-[0-9]+\b"),
    re.compile(r"\bT-[a-z0-9]+\b"),
    re.compile(r"\bv[0-9]+\.[0-9]+\.[0-9]+\b"),
    re.compile(r"docs/superpowers/"),
    re.compile(r"(?:^|[\s/])test/"),
]

IMPERATIVE_PATTERNS = [
    re.compile(r"\|\s*Add\s+", re.IGNORECASE),
    re.compile(r"\|\s*Document\s+", re.IGNORECASE),
    re.compile(r"\|\s*Update\s+", re.IGNORECASE),
    re.compile(r"\|\s*Remove\s+", re.IGNORECASE),
]


def check_section_order(content: str, path: pathlib.Path) -> list[str]:
    errors: list[str] = []
    last_idx = -1
    for section in REQUIRED_SECTIONS_ORDERED:
        idx = content.find(section)
        if idx == -1:
            errors.append(f"{path}: missing required section {section!r}")
            continue
        if idx <= last_idx:
            errors.append(f"{path}: section {section!r} out of order")
        last_idx = idx
    return errors


def check_forbidden_tokens(content: str, path: pathlib.Path) -> list[str]:
    errors: list[str] = []
    for pattern in FORBIDDEN_TOKENS:
        for match in pattern.finditer(content):
            errors.append(
                f"{path}: forbidden token {match.group()!r} at byte {match.start()}"
            )
    return errors


def check_imperative_mood(content: str, path: pathlib.Path) -> list[str]:
    errors: list[str] = []
    in_lav_section = False
    for line in content.splitlines():
        if line.startswith("## LAV Item Rationale"):
            in_lav_section = True
            continue
        if in_lav_section and line.startswith("## "):
            in_lav_section = False
            continue
        if in_lav_section:
            for pattern in IMPERATIVE_PATTERNS:
                if pattern.search(line):
                    errors.append(
                        f"{path}: imperative-mood violation in LAV row {line!r}"
                    )
    return errors


def main() -> int:
    paths = sorted(REPO_ROOT.glob(GOLDEN_GLOB))
    if not paths:
        print(
            f"WARN: no golden qa-report.md files found at {GOLDEN_GLOB}",
            file=sys.stderr,
        )
        return 0
    all_errors: list[str] = []
    for path in paths:
        content = path.read_text(encoding="utf-8")
        all_errors.extend(check_section_order(content, path))
        all_errors.extend(check_forbidden_tokens(content, path))
        all_errors.extend(check_imperative_mood(content, path))
    if all_errors:
        print("\n".join(all_errors), file=sys.stderr)
        return 1
    print(f"OK: {len(paths)} qa-report.md goldens validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
