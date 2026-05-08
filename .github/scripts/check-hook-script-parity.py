#!/usr/bin/env python3
"""Check byte-equal mirroring of hook code/config assets across EN and i18n.

For each configured target file, ensures the EN version is byte-identical to
each i18n locale mirror. Reports any byte mismatch or missing mirror file.

Exit codes:
    0 - all targets are byte-equal across all locales
    1 - byte mismatch or missing mirror file
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

# Targets: hook scripts, .gitignore, and settings.json
TARGETS: list[Path] = [
    ROOT / "templates/advanced/hooks/pre-compact.sh",
    ROOT / "templates/advanced/hooks/pre-compact.ps1",
    ROOT / "templates/advanced/hooks/subagent-stop.sh",
    ROOT / "templates/advanced/hooks/subagent-stop.ps1",
    ROOT / "templates/advanced/hooks/stop.sh",
    ROOT / "templates/advanced/hooks/stop.ps1",
    ROOT / "templates/advanced/hooks/validate-prompt.sh",
    ROOT / "templates/advanced/hooks/validate-prompt.ps1",
    ROOT / "templates/advanced/.claude/.gitignore",
    ROOT / "templates/advanced/.claude/settings.json",
]

LOCALES = ["ko-KR", "ja-JP"]


def i18n_path(en_path: Path, locale: str) -> Path:
    """Map EN target path to i18n mirror path."""
    rel = en_path.relative_to(ROOT)
    return ROOT / "docs" / "i18n" / locale / rel


def main() -> int:
    errors: list[str] = []
    checked = 0

    for en in TARGETS:
        if not en.exists():
            errors.append(f"[missing in EN] {en.relative_to(ROOT)}")
            continue
        en_bytes = en.read_bytes()

        for locale in LOCALES:
            mirror = i18n_path(en, locale)
            if not mirror.exists():
                errors.append(f"[missing in {locale}] {mirror.relative_to(ROOT)}")
                continue
            if mirror.read_bytes() != en_bytes:
                errors.append(
                    f"[byte mismatch in {locale}] "
                    f"{mirror.relative_to(ROOT)} "
                    f"(expected byte-equal with {en.relative_to(ROOT)})"
                )
            checked += 1

    if errors:
        print("hook-script-parity errors:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(
        f"OK: {checked} byte-equal check(s) across {len(LOCALES)} locale(s), "
        f"hook script parity confirmed."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
