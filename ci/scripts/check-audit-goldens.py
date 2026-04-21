#!/usr/bin/env python3
"""Re-apply scoring formula + bucket rubric to real-project audit goldens.

Assertions per golden (6 always + A7 self-only):
  A1: JSON schema required keys present
  A2: scoring_contract_id == "audit-score-v4.0.0"
  A3: LAV_nonL5 == L1 + L2 + L3 + L4 + L6 (L5 routed via cap tier instead)
  A4: cap matches cap tier rule (60 / 50 / 100)
  A5: re-computed Final matches expected_final_score within +/-0.001
  A6: expected_bucket matches bucket rubric applied to profile
  A7 (slug == "guardians-of-the-claude"): expected_final_score in [53, 63]

Exit codes:
  0 - all goldens pass
  1 - one or more assertions failed
  2 - ci/fixtures/audit-goldens/ absent (CI soft-skip)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GOLDENS_DIR = REPO_ROOT / "ci" / "fixtures" / "audit-goldens"

REQUIRED_TOP_KEYS = {
    "scoring_contract_id",
    "sample",
    "profile",
    "scoring_inputs",
    "expected_bucket",
    "expected_final_score",
    "bucket_rationale",
}
REQUIRED_PROFILE_KEYS = {
    "claude_md_lines",
    "rules_count",
    "hooks_count",
    "agents_count",
    "mcp_count",
    "deny_count",
    "is_monorepo",
    "has_meta_marketplace",
    "has_symlink_claude_md",
}
REQUIRED_SCORING_KEYS = {
    "DS", "SB", "L1", "L2", "L3", "L4", "L5", "L6", "LAV_nonL5", "cap"
}
VALID_BUCKETS = {"Starter", "Intermediate", "Advanced", "Outlier"}
VALID_CAPS = {50, 60, 100}
SELF_SLUG = "guardians-of-the-claude"
SELF_SCORE_MIN = 53.0
SELF_SCORE_MAX = 63.0


def compute_final(DS: float, SB: float, L1: int, L2: int, L3: int, L4: int,
                  L6: int, cap: int) -> float:
    """Scoring formula: Final = min(DS * (1 + LAV_nonL5 / 50) + SB, cap)."""
    lav_non_l5 = L1 + L2 + L3 + L4 + L6
    return min(DS * (1 + lav_non_l5 / 50.0) + SB, cap)


def compute_expected_cap(L1: int, L2: int, L4: int, L5: int) -> int:
    """Cap tier rule."""
    if L5 == -3:
        # Check if any other Li at its minimum (L1=-3, L2=-2, L4=-1)
        if L1 == -3 or L2 == -2 or L4 == -1:
            return 50
        return 60
    return 100


def classify_bucket(profile: dict) -> str:
    """Apply bucket rubric to profile signals. Returns bucket name."""
    # Short-circuits for Outlier bucket
    if profile["is_monorepo"]:
        return "Outlier"
    if profile["claude_md_lines"] is not None and profile["claude_md_lines"] > 250:
        return "Outlier"
    if profile["has_meta_marketplace"]:
        return "Outlier"

    # Extract counts (may be null for monorepo short-circuit cases; already handled)
    lines = profile["claude_md_lines"]
    rules = profile["rules_count"] or 0
    hooks = profile["hooks_count"] or 0
    agents = profile["agents_count"] or 0
    mcp = profile["mcp_count"] or 0
    deny = profile["deny_count"] or 0

    if lines is None:
        return "Outlier"  # defensive — should not reach here for non-short-circuit samples

    # Advanced: 100-250 lines (200-250 exception) + rules>=3 + >=2 of {hooks>=1, agents>=1, MCP>=1, deny>=5}
    if 100 <= lines <= 250 and rules >= 3:
        signal_count = sum([hooks >= 1, agents >= 1, mcp >= 1, deny >= 5])
        if signal_count >= 2:
            return "Advanced"

    # Intermediate: 60-200 lines + (rules 2-5 OR hooks 1-2) + agents<=1 + MCP<=1
    if 60 <= lines <= 200:
        rules_ok = 2 <= rules <= 5
        hooks_ok = 1 <= hooks <= 2
        if (rules_ok or hooks_ok) and agents <= 1 and mcp <= 1:
            return "Intermediate"

    # Starter: 20-80 lines + rules<=1 + hooks=0 + agents=0 + MCP=0
    if 20 <= lines <= 80 and rules <= 1 and hooks == 0 and agents == 0 and mcp == 0:
        return "Starter"

    # Rubric-unmatched (should not occur for curated v2.0.0 samples)
    return "UNMATCHED"


def validate_golden(path: Path) -> list[str]:
    """Validate one golden; return list of error messages."""
    errors: list[str] = []
    slug = path.parent.name

    # Load
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"{slug}: JSON parse error: {e}"]

    # A1: required keys
    missing_top = REQUIRED_TOP_KEYS - data.keys()
    if missing_top:
        errors.append(f"{slug} A1: missing top-level keys: {sorted(missing_top)}")
        return errors

    missing_profile = REQUIRED_PROFILE_KEYS - data["profile"].keys()
    if missing_profile:
        errors.append(f"{slug} A1: missing profile keys: {sorted(missing_profile)}")
    missing_scoring = REQUIRED_SCORING_KEYS - data["scoring_inputs"].keys()
    if missing_scoring:
        errors.append(f"{slug} A1: missing scoring_inputs keys: {sorted(missing_scoring)}")

    if errors:
        return errors

    # A2: scoring_contract_id
    if data["scoring_contract_id"] != "audit-score-v4.0.0":
        errors.append(
            f"{slug} A2: scoring_contract_id must be 'audit-score-v4.0.0'; "
            f"got {data['scoring_contract_id']!r}"
        )

    si = data["scoring_inputs"]

    # A3: LAV_nonL5 == L1+L2+L3+L4+L6
    expected_lav = si["L1"] + si["L2"] + si["L3"] + si["L4"] + si["L6"]
    if si["LAV_nonL5"] != expected_lav:
        errors.append(
            f"{slug} A3: LAV_nonL5 must equal L1+L2+L3+L4+L6; "
            f"stored={si['LAV_nonL5']} computed={expected_lav}"
        )

    # A4: cap matches cap tier rule
    expected_cap = compute_expected_cap(si["L1"], si["L2"], si["L4"], si["L5"])
    if si["cap"] != expected_cap:
        errors.append(
            f"{slug} A4: cap must be {expected_cap} per cap tier rule "
            f"(L5={si['L5']}, L1={si['L1']}, L2={si['L2']}, L4={si['L4']}); "
            f"got {si['cap']}"
        )
    if si["cap"] not in VALID_CAPS:
        errors.append(f"{slug} A4: cap must be in {VALID_CAPS}; got {si['cap']}")

    # A5: Final matches formula within +/-0.001
    expected_final = compute_final(
        si["DS"], si["SB"], si["L1"], si["L2"], si["L3"], si["L4"], si["L6"], si["cap"]
    )
    stored_final = data["expected_final_score"]
    if abs(stored_final - expected_final) > 0.001:
        errors.append(
            f"{slug} A5: expected_final_score mismatch per scoring formula; "
            f"stored={stored_final} computed={expected_final:.4f}"
        )

    # A6: expected_bucket matches bucket rubric applied to profile
    computed_bucket = classify_bucket(data["profile"])
    stored_bucket = data["expected_bucket"]
    if stored_bucket not in VALID_BUCKETS:
        errors.append(f"{slug} A6: bucket must be in {VALID_BUCKETS}; got {stored_bucket!r}")
    elif computed_bucket != stored_bucket:
        errors.append(
            f"{slug} A6: expected_bucket does not match bucket rubric applied to profile; "
            f"stored={stored_bucket!r} computed={computed_bucket!r}"
        )

    # A7: self-reference quality gate
    if slug == SELF_SLUG:
        if not (SELF_SCORE_MIN <= stored_final <= SELF_SCORE_MAX):
            errors.append(
                f"{slug} A7: self Final must be in [{SELF_SCORE_MIN}, {SELF_SCORE_MAX}] "
                f"per self-reference quality gate; got {stored_final}"
            )

    return errors


def main() -> int:
    if not GOLDENS_DIR.exists():
        print(
            f"SKIP - audit-goldens directory not present at "
            f"{GOLDENS_DIR.relative_to(REPO_ROOT)}"
        )
        return 2

    golden_paths = sorted(GOLDENS_DIR.glob("*/golden.json"))
    if not golden_paths:
        print(f"SKIP - no golden.json files found under {GOLDENS_DIR.relative_to(REPO_ROOT)}")
        return 2

    all_errors: list[str] = []
    pass_count = 0
    for path in golden_paths:
        errs = validate_golden(path)
        if errs:
            all_errors.extend(errs)
        else:
            pass_count += 1

    if all_errors:
        print(f"FAIL - {len(all_errors)} assertion(s) failed across "
              f"{len(golden_paths)} golden(s):")
        for err in all_errors:
            print(f"  {err}")
        return 1

    print(
        f"PASS - {pass_count}/{len(golden_paths)} goldens passed all assertions "
        f"(A1 schema / A2 contract-ID / A3 LAV_nonL5 / A4 cap tier / A5 Final +/-0.001 / "
        f"A6 bucket rubric / A7 self quality gate)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
