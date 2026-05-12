#!/usr/bin/env python3
"""Check bidirectional file parity between EN and i18n directories.

For each configured (EN, i18n) directory pair, ensures every file in
EN has an i18n counterpart and vice versa. Reports both missing files
(EN present, i18n absent) and orphan files (i18n present, EN absent).

Exit codes:
    0 - all directories are in parity
    1 - missing or orphan files found
"""
from __future__ import annotations

import sys
from pathlib import Path

# Windows cp949 defense: ensure stdout/stderr are UTF-8 so non-ASCII strings
# don't raise UnicodeEncodeError on Korean-locale Windows hosts.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

ROOT = Path(__file__).resolve().parent.parent.parent

PAIRS: list[tuple[Path, Path]] = [
    (
        ROOT / "docs" / "guides",
        ROOT / "docs" / "i18n" / "ko-KR" / "guides",
    ),
    (
        ROOT / "templates",
        ROOT / "docs" / "i18n" / "ko-KR" / "templates",
    ),
    (
        ROOT / "docs" / "guides",
        ROOT / "docs" / "i18n" / "ja-JP" / "guides",
    ),
    (
        ROOT / "templates",
        ROOT / "docs" / "i18n" / "ja-JP" / "templates",
    ),
]


def list_relative_files(root: Path) -> set[Path]:
    """Return all files under root as paths relative to root."""
    if not root.exists():
        return set()
    return {
        p.relative_to(root)
        for p in root.rglob("*")
        if p.is_file()
    }


def main() -> int:
    all_errors: list[str] = []
    total_checked = 0

    for en_root, i18n_root in PAIRS:
        if not en_root.exists():
            all_errors.append(
                f"[missing directory] {en_root.relative_to(ROOT)}"
            )
            continue

        # Derive locale label from i18n path (e.g. "ko-KR", "ja-JP")
        i18n_rel = i18n_root.relative_to(ROOT)
        locale = i18n_rel.parts[2] if len(i18n_rel.parts) > 2 else str(i18n_rel)

        en_files = list_relative_files(en_root)
        i18n_files = list_relative_files(i18n_root)

        missing = en_files - i18n_files
        orphan = i18n_files - en_files

        for f in sorted(missing):
            all_errors.append(
                f"[missing in {locale}] {(en_root / f).relative_to(ROOT)}"
            )
        for f in sorted(orphan):
            all_errors.append(
                f"[orphan in {locale}] {(i18n_root / f).relative_to(ROOT)}"
            )

        total_checked += len(en_files)

    if all_errors:
        print("i18n parity errors:")
        for e in all_errors:
            print(f"  - {e}")
        return 1

    print(
        f"OK: {total_checked} file(s) checked across {len(PAIRS)} pair(s), "
        f"bidirectional parity confirmed."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
