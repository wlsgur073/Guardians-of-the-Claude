"""Lint: skill frontmatter must not declare options/arguments; body must not embed $ARGUMENTS.

Enforces the skill interface stability contract as a CI gate.
"""
import sys
from pathlib import Path

# Windows cp949 defense: ensure stdout/stderr are UTF-8 so non-ASCII strings
# don't raise UnicodeEncodeError on Korean-locale Windows hosts.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

import yaml

FORBIDDEN_KEYS = {"options", "arguments"}
FORBIDDEN_TOKENS = {"$ARGUMENTS"}


def main() -> int:
    failures: list[str] = []
    skills = sorted(Path("plugin/skills").glob("*/SKILL.md"))
    if not skills:
        print("ERROR: no SKILL.md files found under plugin/skills/*/")
        return 1
    for skill_md in skills:
        text = skill_md.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            failures.append(f"{skill_md}: no frontmatter")
            continue
        try:
            _, frontmatter, _ = text.split("---\n", 2)
        except ValueError:
            failures.append(f"{skill_md}: malformed frontmatter delimiters")
            continue
        meta = yaml.safe_load(frontmatter) or {}
        for key in FORBIDDEN_KEYS:
            if key in meta:
                failures.append(f"{skill_md}: forbidden frontmatter key '{key}'")
        for token in FORBIDDEN_TOKENS:
            if token in text:
                failures.append(f"{skill_md}: body contains forbidden token '{token}'")
    if failures:
        print("\n".join(failures))
        return 1
    print(f"OK: all {len(skills)} skills pass stability lint.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
