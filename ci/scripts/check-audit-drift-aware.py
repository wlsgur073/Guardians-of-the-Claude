#!/usr/bin/env python3
"""Drift-aware /audit structural + state-machine validator.

Covers 6 assertions:
  A1 drift advisory state machine simulation (5 fixtures)
  A2 .model field in Step 0.5 profile.json write set (learning-system.md)
  A3 install-integrity pre-Phase-0 substep in /audit SKILL.md
  A4 Final Phase triggers (model write + scoring-model-change banner + drift advisory)
  A5 output-format.md drift block position (between Score and ★ Most impactful)
  A6 output-format.md drift block format (changed-axes-only + baseline annotation + no severity)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# A1: drift advisory state machine
# ---------------------------------------------------------------------------

Fingerprint = dict  # {family_tier: opus|sonnet|haiku, context_window_class: 200k|1M, reasoning_class: none|extended_any, context_management_class: manual|compaction_capable}


def drift_state(
    current_fp: Fingerprint | None,
    baseline_present: bool,
    baseline_fp: Fingerprint | None,
) -> str:
    """Pure drift advisory state machine (silence evaluation order).

    Returns one of: "match", "missing_baseline", "normalization_null", "drift".
    """
    # Silence evaluation order (short-circuit, deterministic).
    if current_fp is None or (baseline_present and baseline_fp is None):
        return "normalization_null"
    if not baseline_present:
        return "missing_baseline"
    if current_fp == baseline_fp:
        return "match"
    return "drift"


# Fixture table.
A1_FIXTURES = [
    (
        "match",
        {"family_tier": "opus", "context_window_class": "200k",
         "reasoning_class": "extended_any", "context_management_class": "manual"},
        True,
        {"family_tier": "opus", "context_window_class": "200k",
         "reasoning_class": "extended_any", "context_management_class": "manual"},
        "match",
    ),
    (
        "drift",
        {"family_tier": "sonnet", "context_window_class": "1M",
         "reasoning_class": "extended_any", "context_management_class": "manual"},
        True,
        {"family_tier": "opus", "context_window_class": "200k",
         "reasoning_class": "extended_any", "context_management_class": "manual"},
        "drift",
    ),
    (
        "normalization_null_current",
        None,
        True,
        {"family_tier": "opus", "context_window_class": "200k",
         "reasoning_class": "extended_any", "context_management_class": "manual"},
        "normalization_null",
    ),
    (
        "normalization_null_baseline",
        {"family_tier": "opus", "context_window_class": "200k",
         "reasoning_class": "extended_any", "context_management_class": "manual"},
        True,
        None,
        "normalization_null",
    ),
    (
        "missing_baseline",
        {"family_tier": "opus", "context_window_class": "200k",
         "reasoning_class": "extended_any", "context_management_class": "manual"},
        False,
        None,
        "missing_baseline",
    ),
]


def check_a1_state_machine() -> list[str]:
    failures = []
    for name, current, present, baseline, expected in A1_FIXTURES:
        actual = drift_state(current, present, baseline)
        if actual != expected:
            failures.append(f"A1 {name}: expected {expected!r}, got {actual!r}")
    return failures


# ---------------------------------------------------------------------------
# A2: Step 0.5 — .model field emission in profile.json write set
# ---------------------------------------------------------------------------


def check_a2_write_point_1() -> list[str]:
    """Verify .model field is part of the Step 0.5 profile.json write set."""
    failures = []
    learning_md = (
        REPO_ROOT / "plugin" / "references" / "learning-system.md"
    ).read_text(encoding="utf-8")

    step_05_match = re.search(
        r"\*\*Step 0\.5 — Migration & Stale Check\*\*.*?(?=\n## |\n---)",
        learning_md,
        flags=re.DOTALL,
    )
    if not step_05_match:
        failures.append("A2: Step 0.5 section not found in learning-system.md")
        return failures

    step_05 = step_05_match.group(0)

    if ".model" not in step_05:
        failures.append("A2: Step 0.5 missing .model field in profile.json write set")

    return failures


# ---------------------------------------------------------------------------
# A3: Install-integrity pre-Phase-0 substep in /audit SKILL.md
# ---------------------------------------------------------------------------


def check_a3_install_integrity() -> list[str]:
    """Verify /audit SKILL.md declares an install-integrity check before Phase 0."""
    failures = []
    skill_md = (
        REPO_ROOT / "plugin" / "skills" / "audit" / "SKILL.md"
    ).read_text(encoding="utf-8")

    phase_0_idx = skill_md.find("## Phase 0")
    if phase_0_idx == -1:
        failures.append("A3: Phase 0 heading not found in /audit SKILL.md")
        return failures

    pre_phase_0 = skill_md[:phase_0_idx]

    required_markers = [
        ("install-integrity", "A3: no 'install-integrity' mention before Phase 0"),
        ("scoring_contract_id", "A3: no 'scoring_contract_id' mention before Phase 0"),
        ("abort", "A3: pre-Phase-0 check missing abort-on-mismatch language"),
    ]
    for marker, msg in required_markers:
        if marker not in pre_phase_0:
            failures.append(msg)
    return failures


# ---------------------------------------------------------------------------
# A4: Final Phase triggers — model write + banner + drift advisory
# ---------------------------------------------------------------------------


def check_a4_final_phase_triggers() -> list[str]:
    """Verify Phase 5 declares model write + banner + drift advisory triggers."""
    failures = []
    skill_md = (
        REPO_ROOT / "plugin" / "skills" / "audit" / "SKILL.md"
    ).read_text(encoding="utf-8")

    phase_5_match = re.search(
        r"## Phase 5:.*?(?=\n## |\Z)",
        skill_md,
        flags=re.DOTALL,
    )
    if not phase_5_match:
        failures.append("A4: Phase 5 section not found in /audit SKILL.md")
        return failures
    phase_5 = phase_5_match.group(0)

    required = [
        ("Final Phase model write", "A4: Phase 5 missing Final Phase model write trigger"),
        ("scoring-model-change banner", "A4: Phase 5 missing scoring-model-change banner reference"),
        ("drift advisory", "A4: Phase 5 missing drift advisory trigger"),
        ("stateless", "A4: Phase 5 missing stateless mode guard"),
        ("transient", "A4: Phase 5 does not mark drift advisory as transient"),
    ]
    for marker, msg in required:
        if marker not in phase_5:
            failures.append(msg)
    return failures


# ---------------------------------------------------------------------------
# A5: output-format.md drift block position (between Score and Most impactful)
# ---------------------------------------------------------------------------


def check_a5_drift_block_position() -> list[str]:
    """Verify drift block example appears between Score line and Most impactful."""
    failures = []
    of_md = (
        REPO_ROOT / "plugin" / "skills" / "audit" / "references" / "output-format.md"
    ).read_text(encoding="utf-8")

    drift_header = "Model drift since last /audit"
    if drift_header not in of_md:
        failures.append(f"A5: '{drift_header}' marker not found in output-format.md")
        return failures

    score_idx = of_md.find("Score:")
    most_impactful_idx = of_md.find("Most impactful")
    drift_idx = of_md.find(drift_header)
    if score_idx == -1 or most_impactful_idx == -1:
        failures.append("A5: cannot locate Score or Most impactful anchors")
        return failures
    if not (score_idx < drift_idx < most_impactful_idx):
        failures.append(
            f"A5: drift block position wrong (Score={score_idx}, Drift={drift_idx}, MostImpactful={most_impactful_idx})"
        )
    return failures


# ---------------------------------------------------------------------------
# A6: output-format.md drift block format (changed-axes-only + baseline + no severity + conditional)
# ---------------------------------------------------------------------------


def check_a6_drift_block_format() -> list[str]:
    """Verify drift block description includes 4 format requirements."""
    failures = []
    of_md = (
        REPO_ROOT / "plugin" / "skills" / "audit" / "references" / "output-format.md"
    ).read_text(encoding="utf-8")

    required = [
        ("changed axes only", "A6: drift block format must specify changed-axes only"),
        ("baseline", "A6: drift block format must mention baseline source annotation"),
        ("No severity label", "A6: drift block must document no-severity-label rule"),
        ("conditional", "A6: drift block must be documented as conditional"),
    ]
    for marker, msg in required:
        if marker.lower() not in of_md.lower():
            failures.append(msg)
    return failures


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

CHECKS = [
    ("A1 drift state machine", check_a1_state_machine),
    ("A2 Step 0.5 .model write set", check_a2_write_point_1),
    ("A3 Install-integrity pre-Phase-0", check_a3_install_integrity),
    ("A4 Phase 5 Final triggers", check_a4_final_phase_triggers),
    ("A5 Drift block position", check_a5_drift_block_position),
    ("A6 Drift block format", check_a6_drift_block_format),
]


def main() -> int:
    all_failures: list[str] = []
    for label, check in CHECKS:
        try:
            failures = check()
        except Exception as exc:  # noqa: BLE001 — validator must never re-raise mid-run
            failures = [f"{label}: raised {exc!r}"]
        if failures:
            print(f"[FAIL] {label}")
            for f in failures:
                print(f"        - {f}")
            all_failures.extend(failures)
        else:
            print(f"[PASS] {label}")
    if all_failures:
        print(f"\n{len(all_failures)} assertion(s) failed", file=sys.stderr)
        return 1
    print("\nAll drift-aware assertions passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
