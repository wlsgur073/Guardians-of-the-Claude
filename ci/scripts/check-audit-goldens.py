#!/usr/bin/env python3
"""Re-apply scoring formula + bucket rubric to real-project audit goldens.

Assertions per golden (6 always + A7 self-only + A8/A9/A10 monorepo-only):
  A1: JSON schema required keys present
  A2: scoring_contract_id == "audit-score-v4.1.0"
  A3: LAV_nonL5 == L1 + L2 + L3 + L4 + L6 (L5 routed via cap tier instead)
  A4: cap matches cap tier rule (60 / 50 / 100)
  A5: re-computed Final matches expected_final_score within +/-0.001
  A6: expected_bucket matches bucket rubric (profile + distributed_config monorepo signals)
  A7 (slug == "guardians-of-the-claude"): expected_final_score in [53, 63]
  A8 (monorepo_detection.detected==true only): detection backing + cap invariants
  A9 (monorepo_detection.detected==true only): subpackage_coverage 4-counter invariants
  A10 (monorepo_detection.detected==true only): subpackages[] per-row invariants

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
    "has_meta_marketplace",
    "has_symlink_claude_md",
}
REQUIRED_SCORING_KEYS = {
    "DS", "SB", "L1", "L2", "L3", "L4", "L5", "L6", "LAV_nonL5", "cap"
}
VALID_BUCKETS = {"Starter", "Intermediate", "Advanced", "Outlier", "distributed_config"}
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

    # Outlier (verbose-prose-sparse-config): >=200 lines + zero formal config
    # Captures projects that consolidate guidance into CLAUDE.md prose rather
    # than splitting into separate rules/hooks/agents/MCP files. Common in mature
    # monorepos where the workspace orchestrator's design intent is explained
    # narratively rather than enforced by per-file config.
    if lines >= 200 and rules == 0 and hooks == 0 and agents == 0 and mcp == 0:
        return "Outlier"

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


def classify_bucket_distributed(data: dict) -> bool:
    """Apply distributed-config rubric per distributed-config-bucket.md.

    Required (ALL): with_claude_md >= 2 + project_structure.type=monorepo +
    monorepo_detection.detected=true.
    Supporting (>=2 of 4): ratio >= 0.5 + lines <= 150 +
    mean(L6) >= 0.5 + NOT verbose-prose-sparse-config.
    Exclusion (any -> False): lines > 1000 OR all subpackages final_score < 30.
    """
    profile = data["profile"]
    project_structure = data.get("project_structure", {})
    monorepo = project_structure.get("monorepo_detection", {})
    coverage = (
        data.get("claude_code_configuration_state", {})
        .get("claude_md", {})
        .get("subpackage_coverage", {})
    )
    subpackages = (
        data.get("claude_code_configuration_state", {})
        .get("claude_md", {})
        .get("subpackages", [])
    )

    # Required: type=monorepo + detected=true
    if project_structure.get("type") != "monorepo":
        return False
    if not monorepo.get("detected"):
        return False

    # Required: with_claude_md >= 2
    with_cm = coverage.get("with_claude_md", 0)
    if with_cm < 2:
        return False

    # Exclusion 1: claude_md_lines > 1000
    lines = profile["claude_md_lines"] or 0
    if lines > 1000:
        return False

    # Exclusion 2: all scored subpackages have final_score < 30
    if subpackages and all(sp.get("final_score", 100) < 30 for sp in subpackages):
        return False

    # Supporting signals (>=2 of 4)
    package_roots_total = coverage.get("package_roots_total", 0)
    signals = 0

    # Signal 1: distributed config ratio
    if package_roots_total > 0 and with_cm / package_roots_total >= 0.5:
        signals += 1

    # Signal 2: root CLAUDE.md compactness
    if lines <= 150:
        signals += 1

    # Signal 3: subpackage-local actionability (mean L6 >= 0.5 over scored)
    if subpackages:
        l6_values = [sp.get("lav_breakdown", {}).get("L6", 0) for sp in subpackages]
        if l6_values and sum(l6_values) / len(l6_values) >= 0.5:
            signals += 1

    # Signal 4: verbose-prose-sparse-config exclusion
    rules = profile["rules_count"] or 0
    hooks = profile["hooks_count"] or 0
    agents = profile["agents_count"] or 0
    mcp = profile["mcp_count"] or 0
    mechanical_config = rules + hooks + agents + mcp
    if not (lines > 250 and mechanical_config < 4):
        signals += 1

    return signals >= 2


def classify_bucket_full(data: dict) -> str:
    """Apply full bucket rubric including distributed_config check.

    Evaluation order (per distributed-config-bucket.md §0):
    1. Outlier short-circuits + verbose-prose-sparse-config Outlier (via classify_bucket)
    2. distributed_config (if rubric matches)
    3. Advanced / Intermediate / Starter / UNMATCHED (existing branches)
    """
    profile_bucket = classify_bucket(data["profile"])
    if profile_bucket == "Outlier":
        return "Outlier"
    if classify_bucket_distributed(data):
        return "distributed_config"
    return profile_bucket


def check_a8_detection_backing(profile: dict) -> tuple[bool, str]:
    """A8(a): detection MUST be backed by evidence[] OR package_roots_for_scoring[].

    Per monorepo-detection.md §3 detection algorithm L170-172: detected=true can
    arise from filtered_roots-only path WITHOUT evidence entries, so disjunction
    (not conjunction) is the correct invariant.
    """
    mono = profile.get("project_structure", {}).get("monorepo_detection")
    if mono is None or not mono.get("detected"):
        return (True, "skipped (not monorepo)")
    evidence = mono.get("evidence", [])
    roots_for_scoring = mono.get("package_roots_for_scoring", [])
    if len(evidence) == 0 and len(roots_for_scoring) == 0:
        return (False, "A8(a) violated: detected=true requires non-empty evidence[] OR package_roots_for_scoring[] (per monorepo-detection.md §3)")
    return (True, "A8(a) ok")


def check_a8_caps(profile: dict) -> tuple[bool, str]:
    """A8(b)/(c)/(d): cap invariants for monorepo_detection."""
    mono = profile.get("project_structure", {}).get("monorepo_detection")
    if mono is None or not mono.get("detected"):
        return (True, "skipped (not monorepo)")
    package_roots = mono.get("package_roots", [])
    roots_for_scoring = mono.get("package_roots_for_scoring", [])
    caps = mono.get("package_root_caps", {})
    # A8(b) display cap (per monorepo-detection.md §5)
    if len(package_roots) > 20:
        return (False, f"A8(b) violated: package_roots length {len(package_roots)} > display cap 20")
    # A8(c) scored cap (per same)
    if len(roots_for_scoring) > 50:
        return (False, f"A8(c) violated: package_roots_for_scoring length {len(roots_for_scoring)} > scored cap 50")
    # A8(d) cap surface invariant: filtered set is superset of scored prefix
    total_filtered = caps.get("total_filtered")
    if total_filtered is not None and total_filtered < len(roots_for_scoring):
        return (False, f"A8(d) violated: total_filtered {total_filtered} < len(package_roots_for_scoring) {len(roots_for_scoring)}")
    return (True, "A8(b)/(c)/(d) ok")


def check_a9_subpackage_coverage(profile: dict) -> tuple[bool, str]:
    """A9: subpackage_coverage 4-counter invariants (per per-package-rollup.md §1.1)."""
    mono = profile.get("project_structure", {}).get("monorepo_detection")
    if mono is None or not mono.get("detected"):
        return (True, "skipped (not monorepo)")
    coverage = (
        profile.get("claude_code_configuration_state", {})
        .get("claude_md", {})
        .get("subpackage_coverage")
    )
    if coverage is None:
        return (False, "A9: subpackage_coverage missing when detected=true")
    required_fields = ["package_roots_total", "with_claude_md", "without_claude_md", "scored_count"]
    for field in required_fields:
        if field not in coverage:
            return (False, f"A9(a) violated: required field '{field}' missing in subpackage_coverage")
    # A9(b) total invariant
    if coverage["package_roots_total"] != coverage["with_claude_md"] + coverage["without_claude_md"]:
        return (False,
                f"A9(b) violated: package_roots_total={coverage['package_roots_total']} != "
                f"with_claude_md ({coverage['with_claude_md']}) + without_claude_md ({coverage['without_claude_md']})")
    # A9(c) scored bound (strict inequality indicates degraded scoring per per-package-scoring.md §7)
    if not (0 <= coverage["scored_count"] <= coverage["with_claude_md"]):
        return (False,
                f"A9(c) violated: scored_count={coverage['scored_count']} not in "
                f"[0, with_claude_md={coverage['with_claude_md']}]")
    return (True, "A9 ok")


def check_a10_subpackage_rows(profile: dict) -> tuple[bool, str]:
    """A10: subpackages[] per-row invariants (per per-package-scoring.md §3.1/§5/§6)."""
    mono = profile.get("project_structure", {}).get("monorepo_detection")
    if mono is None or not mono.get("detected"):
        return (True, "skipped (not monorepo)")
    subpackages = (
        profile.get("claude_code_configuration_state", {})
        .get("claude_md", {})
        .get("subpackages", [])
    )
    if len(subpackages) == 0:
        return (True, "A10 ok (empty subpackages[])")
    required = ["path", "claude_md_path", "final_score", "cap_tier", "lav_breakdown"]
    valid_lav_keys = {"L1", "L2", "L3", "L4", "L5", "L6"}
    valid_lav_ranges = {
        "L1": [-3, 0, 2],
        "L2": [-2, 0, 2],
        "L3": [0, 1, 3],
        "L4": [-1, 0, 1],
        "L5": [-3, 0, 1],
        "L6": [0, 1],
    }
    for idx, sp in enumerate(subpackages):
        # A10(a) required fields
        for f in required:
            if f not in sp:
                return (False, f"A10(a) violated at index {idx}: missing '{f}'")
        # A10(b) final_score range (per schema 1.2.0 + per-package-scoring.md §6)
        if not (0 <= sp["final_score"] <= 100):
            return (False, f"A10(b) violated at index {idx}: final_score={sp['final_score']} not in [0, 100]")
        # A10(c) cap_tier enum (per per-package-scoring.md §5)
        if sp["cap_tier"] not in (50, 60, 100):
            return (False, f"A10(c) violated at index {idx}: cap_tier={sp['cap_tier']} not in {{50, 60, 100}}")
        # A10(d) LAV breakdown shape + value ranges (per per-package-scoring.md §3.1)
        if set(sp["lav_breakdown"].keys()) != valid_lav_keys:
            return (False,
                    f"A10(d) violated at index {idx}: lav_breakdown keys "
                    f"{sorted(sp['lav_breakdown'].keys())} != L1-L6")
        for axis, val in sp["lav_breakdown"].items():
            if val not in valid_lav_ranges[axis]:
                return (False,
                        f"A10(d) violated at index {idx}: {axis}={val} not in {valid_lav_ranges[axis]}")
    return (True, "A10 ok")


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
    if data["scoring_contract_id"] != "audit-score-v4.1.0":
        errors.append(
            f"{slug} A2: scoring_contract_id must be 'audit-score-v4.1.0'; "
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

    # A6: expected_bucket matches bucket rubric (incl. distributed_config check)
    computed_bucket = classify_bucket_full(data)
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

    # A8/A9/A10: monorepo-specific assertions
    # Each function early-returns (True, "skipped (not monorepo)") when
    # monorepo_detection is None OR detected is not True, so single_project
    # fixtures bypass these assertions and remain GREEN.
    for label, (ok, msg) in [
        ("A8(a)", check_a8_detection_backing(data)),
        ("A8(b/c/d)", check_a8_caps(data)),
        ("A9", check_a9_subpackage_coverage(data)),
        ("A10", check_a10_subpackage_rows(data)),
    ]:
        if not ok:
            errors.append(f"{slug} {label}: {msg}")

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
        f"A6 bucket rubric / A7 self quality gate / A8 monorepo_detection invariants / "
        f"A9 subpackage_coverage invariants / A10 subpackages[] per-row invariants)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
