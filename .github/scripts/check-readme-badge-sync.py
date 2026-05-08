#!/usr/bin/env python3
"""Verify README badge version matches plugin.json version.

Exit codes:
    0 - badge matches plugin.json
    1 - mismatch or unable to parse
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PLUGIN_JSON = ROOT / "plugin" / ".claude-plugin" / "plugin.json"
README = ROOT / "README.md"

# Shields.io badge URL fragment: ".../version-2.17.1-..." or "...-v2.17.1-..."
# Capture the version literal between dashes after "version-" or after a leading "v".
BADGE_RE = re.compile(r"version-v?([0-9]+\.[0-9]+\.[0-9]+)", re.IGNORECASE)


def main() -> int:
    try:
        manifest = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL - could not read plugin.json: {exc}")
        return 1

    expected = manifest.get("version", "")
    if not expected:
        print("FAIL - plugin.json has no 'version' field")
        return 1

    try:
        readme_text = README.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"FAIL - could not read README.md: {exc}")
        return 1

    matches = BADGE_RE.findall(readme_text)
    if not matches:
        print("FAIL - no version badge found in README.md")
        print("       (expected pattern 'version-X.Y.Z' in shields.io badge URL)")
        return 1

    mismatched = [m for m in matches if m != expected]
    if mismatched:
        print(f"FAIL - README badge version(s) {mismatched} do not match plugin.json {expected!r}")
        return 1

    print(f"PASS - README badge version {expected!r} matches plugin.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
