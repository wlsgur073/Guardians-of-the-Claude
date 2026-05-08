#!/usr/bin/env python3
"""Verify CHANGELOG.md release headings produce the documented anchor slug.

For each `## [X.Y.Z] - YYYY-MM-DD` heading (or `## [Unreleased]`), derive the
GitHub-flavored slug per CLAUDE.md convention:
    - drop `[`, `]`, `.`
    - replace spaces with `-`
    - lowercase

Then assert no two headings produce the same slug (collision check) and that
each slug matches the expected pattern.

Exit codes:
    0 - all headings produce well-formed unique slugs
    1 - malformed heading or slug collision
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CHANGELOG = ROOT / "CHANGELOG.md"

# Heading patterns:
#   ## [Unreleased]
#   ## [X.Y.Z] - YYYY-MM-DD
#   ## [X.Y.Z] - YYYY-MM-DD [ANNOTATION]
HEADING_RE = re.compile(
    r"^##\s+\[(?P<inner>[^\]]+)\](?:\s*-\s*(?P<date>\d{4}-\d{2}-\d{2})(?:\s+\[(?P<annotation>[^\]]+)\])?)?\s*$",
    re.MULTILINE,
)

# Slug pattern after derivation:
#   "unreleased"  OR  "xyz-yyyy-mm-dd" (digits + hyphens + lowercase)
#   OR  "xyz-yyyy-mm-dd-annotation" (with optional trailing lowercase annotation)
SLUG_RE = re.compile(r"^(?:unreleased|[0-9]+[0-9-]*-\d{4}-\d{2}-\d{2}(?:-[a-z]+)?)$")


def derive_slug(inner: str, date: str | None, annotation: str | None = None) -> str:
    """Apply GitHub's heading-to-slug rules per CLAUDE.md convention."""
    raw = f"[{inner}]"
    if date:
        raw = f"{raw} - {date}"
    if annotation:
        raw = f"{raw} [{annotation}]"
    # Drop `[`, `]`, `.`
    s = raw.translate(str.maketrans("", "", "[]."))
    # Spaces -> `-`
    s = s.replace(" ", "-")
    # Lowercase
    return s.lower()


def main() -> int:
    text = CHANGELOG.read_text(encoding="utf-8")
    errors: list[str] = []
    seen: dict[str, str] = {}

    for match in HEADING_RE.finditer(text):
        inner = match.group("inner")
        date = match.group("date")
        annotation = match.group("annotation")
        heading = match.group(0)
        slug = derive_slug(inner, date, annotation)

        if not SLUG_RE.match(slug):
            errors.append(
                f"FAIL - heading {heading!r} produced malformed slug {slug!r} "
                f"(expected 'unreleased' or 'X.Y.Z-YYYY-MM-DD' lowercase)"
            )
            continue

        if slug in seen:
            errors.append(
                f"FAIL - slug collision {slug!r}: heading {heading!r} collides with {seen[slug]!r}"
            )
            continue

        seen[slug] = heading

    # Count-assertion safety net: catch silent skips where HEADING_RE fails to match
    # a heading that broad level-2 bracket scan sees.
    broad_count = len(re.findall(r"^##\s+\[", text, re.MULTILINE))
    parsed = sum(1 for _ in HEADING_RE.finditer(text))
    if parsed != broad_count:
        errors.append(
            f"FAIL - silent-skip detected: {broad_count} level-2 release headings present, "
            f"but only {parsed} matched the structured pattern. "
            f"Inspect CHANGELOG.md for malformed heading lines."
        )

    if errors:
        for err in errors:
            print(err)
        return 1

    print(f"PASS - {len(seen)} CHANGELOG heading(s) produce unique well-formed slugs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
