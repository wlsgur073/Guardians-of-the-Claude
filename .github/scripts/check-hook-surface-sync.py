#!/usr/bin/env python3
"""Verify README hook count claims match plugin/hooks/hooks.json.

Catches the drift class where the README advertises N hooks but the plugin
manifest registers a different count.

The check pattern is intentionally narrow: only "runs N Claude Code hook(s)"
phrasings are validated, because that is the precise contractual claim the
Trust Model section makes about plugin surface. Broader phrases such as
"the SessionStart hook" are reference, not a quantified contract, and are
NOT matched to avoid false positives.

Exit codes:
    0 - all quantified hook claims match, or README makes no such claim
    1 - mismatch or unable to parse README / hooks.json
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

ROOT = Path(__file__).resolve().parent.parent.parent
HOOKS_JSON = ROOT / "plugin" / "hooks" / "hooks.json"
README = ROOT / "README.md"

WORD_TO_INT = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}

CLAIM_RE = re.compile(
    r"runs\s+(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+"
    r"Claude\s+Code\s+hooks?",
    re.IGNORECASE,
)


def main() -> int:
    try:
        manifest = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL - could not read plugin/hooks/hooks.json: {exc}")
        return 1

    events = manifest.get("hooks", {})
    actual_count = len(events)
    actual_names = sorted(events.keys())

    try:
        readme_text = README.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"FAIL - could not read README.md: {exc}")
        return 1

    claims = CLAIM_RE.findall(readme_text)
    if not claims:
        print(
            "PASS - README makes no quantified hook claim "
            f"(pattern 'runs N Claude Code hook(s)'); manifest registers "
            f"{actual_count} event(s): {actual_names}"
        )
        return 0

    mismatched = []
    for raw in claims:
        claimed = int(raw) if raw.isdigit() else WORD_TO_INT.get(raw.lower(), -1)
        if claimed != actual_count:
            mismatched.append((raw, claimed))

    if mismatched:
        print(
            f"FAIL - README claims hook count(s) {mismatched} "
            f"but plugin/hooks/hooks.json registers {actual_count} event(s): "
            f"{actual_names}"
        )
        print(
            "       Update README to match the manifest, or update "
            "plugin/hooks/hooks.json to match the documented surface."
        )
        return 1

    print(
        f"PASS - README hook claim(s) match manifest "
        f"({actual_count} event(s): {actual_names})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
