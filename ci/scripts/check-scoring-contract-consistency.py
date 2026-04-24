#!/usr/bin/env python3
"""Scoring-contract-id consistency validator.

Closes the Python-level gap for Quality Gate G-E by cross-checking:
  A1 plugin/references/scoring-model.md frontmatter scoring_contract_id is present
  A2 every ci/fixtures/audit-goldens/*/golden.json has matching scoring_contract_id
  A3 plugin/skills/audit/SKILL.md contains the install-integrity section referencing scoring_contract_id
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCORING_MODEL_PATH = REPO_ROOT / "plugin" / "references" / "scoring-model.md"
GOLDENS_DIR = REPO_ROOT / "ci" / "fixtures" / "audit-goldens"
AUDIT_SKILL_PATH = REPO_ROOT / "plugin" / "skills" / "audit" / "SKILL.md"


def read_scoring_model_frontmatter() -> dict:
    text = SCORING_MODEL_PATH.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{SCORING_MODEL_PATH}: no frontmatter")
    end_marker = text.find("\n---", 3)
    if end_marker == -1:
        raise ValueError(f"{SCORING_MODEL_PATH}: unterminated frontmatter")
    return yaml.safe_load(text[3:end_marker])


def check_a1_canonical() -> tuple[str, list[str]]:
    fm = read_scoring_model_frontmatter()
    cid = fm.get("scoring_contract_id")
    if not cid:
        return None, ["A1: scoring-model.md frontmatter missing scoring_contract_id"]
    return cid, []


def check_a2_goldens(canonical_cid: str) -> list[str]:
    failures = []
    goldens = sorted(GOLDENS_DIR.glob("*/golden.json"))
    if len(goldens) < 8:
        failures.append(f"A2: expected >= 8 goldens, found {len(goldens)}")
    for golden_path in goldens:
        with golden_path.open(encoding="utf-8") as f:
            golden = json.load(f)
        golden_cid = golden.get("scoring_contract_id")
        if golden_cid != canonical_cid:
            failures.append(
                f"A2: {golden_path.relative_to(REPO_ROOT)}: "
                f"scoring_contract_id={golden_cid!r} != canonical {canonical_cid!r}"
            )
    return failures


def check_a3_install_integrity() -> list[str]:
    text = AUDIT_SKILL_PATH.read_text(encoding="utf-8")
    if "install-integrity" not in text:
        return ["A3: /audit SKILL.md missing 'install-integrity' marker"]
    if "scoring_contract_id" not in text:
        return ["A3: /audit SKILL.md missing 'scoring_contract_id' reference in install-integrity prose"]
    return []


def main() -> int:
    all_failures: list[str] = []

    canonical_cid, a1_failures = check_a1_canonical()
    all_failures.extend(a1_failures)

    if canonical_cid:
        all_failures.extend(check_a2_goldens(canonical_cid))

    all_failures.extend(check_a3_install_integrity())

    if all_failures:
        for f in all_failures:
            print(f"[FAIL] {f}")
        print(f"\n{len(all_failures)} assertion(s) failed", file=sys.stderr)
        return 1
    print(f"[PASS] A1/A2/A3 all satisfied (canonical = {canonical_cid})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
