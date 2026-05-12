#!/usr/bin/env python3
"""Check that EN and i18n guide frontmatter version fields match.

Compares each file in docs/guides/ against its counterpart in
docs/i18n/ko-KR/guides/ and docs/i18n/ja-JP/guides/. Fails if any
version field differs or if a counterpart is missing.

Exit codes:
    0 - all versions match
    1 - mismatch or missing counterpart found
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

import yaml

ROOT = Path(__file__).resolve().parent.parent.parent
EN_GUIDES = ROOT / "docs" / "guides"

I18N_GUIDES: list[tuple[str, Path]] = [
    ("ko-KR", ROOT / "docs" / "i18n" / "ko-KR" / "guides"),
    ("ja-JP", ROOT / "docs" / "i18n" / "ja-JP" / "guides"),
]


def extract_frontmatter(path: Path) -> dict | None:
    raw = path.read_text(encoding="utf-8")
    # Normalize line endings so CRLF files from Windows don't break parsing
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    return yaml.safe_load(text[4:end])


def main() -> int:
    if not EN_GUIDES.exists():
        print(f"ERROR: {EN_GUIDES} does not exist")
        return 1

    errors: list[str] = []
    checked = 0

    for en_file in sorted(EN_GUIDES.glob("*.md")):
        en_fm = extract_frontmatter(en_file)
        if en_fm is None:
            errors.append(f"[no frontmatter] {en_file.relative_to(ROOT)}")
            continue
        en_ver = en_fm.get("version")

        for locale, locale_dir in I18N_GUIDES:
            i18n_file = locale_dir / en_file.name
            if not i18n_file.exists():
                errors.append(
                    f"[missing {locale}] {en_file.relative_to(ROOT)}"
                )
                continue

            i18n_fm = extract_frontmatter(i18n_file)
            if i18n_fm is None:
                errors.append(
                    f"[no frontmatter] {i18n_file.relative_to(ROOT)}"
                )
                continue

            i18n_ver = i18n_fm.get("version")
            if en_ver != i18n_ver:
                errors.append(
                    f"[version mismatch] {en_file.name}: "
                    f"EN={en_ver} vs {locale}={i18n_ver}"
                )
            checked += 1

    if errors:
        print("Frontmatter parity errors:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"OK: checked {checked} guide pair(s), all versions match.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
