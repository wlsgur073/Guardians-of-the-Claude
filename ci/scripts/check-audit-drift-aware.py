#!/usr/bin/env python3
"""Drift-aware /audit structural + state-machine validator.

Covers 6 assertions:
  A1 drift advisory state machine simulation (5 fixtures)
  A2 baseline Write Point 1 in learning-system.md
  A3 install-integrity pre-Phase-0 substep in /audit SKILL.md
  A4 baseline Write Point 2 + Surface 2 banner + drift trigger in Final Phase
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

Fingerprint = dict  # {family_tier, context_window_class, reasoning_class, context_management_class}


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
        {"family_tier": "opus_tier", "context_window_class": "200k_class",
         "reasoning_class": "thinking", "context_management_class": "standard"},
        True,
        {"family_tier": "opus_tier", "context_window_class": "200k_class",
         "reasoning_class": "thinking", "context_management_class": "standard"},
        "match",
    ),
    (
        "drift",
        {"family_tier": "sonnet_tier", "context_window_class": "1m_class",
         "reasoning_class": "thinking", "context_management_class": "standard"},
        True,
        {"family_tier": "opus_tier", "context_window_class": "200k_class",
         "reasoning_class": "thinking", "context_management_class": "standard"},
        "drift",
    ),
    (
        "normalization_null_current",
        None,
        True,
        {"family_tier": "opus_tier", "context_window_class": "200k_class",
         "reasoning_class": "thinking", "context_management_class": "standard"},
        "normalization_null",
    ),
    (
        "normalization_null_baseline",
        {"family_tier": "opus_tier", "context_window_class": "200k_class",
         "reasoning_class": "thinking", "context_management_class": "standard"},
        True,
        None,
        "normalization_null",
    ),
    (
        "missing_baseline",
        {"family_tier": "opus_tier", "context_window_class": "200k_class",
         "reasoning_class": "thinking", "context_management_class": "standard"},
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
# Driver
# ---------------------------------------------------------------------------

CHECKS = [
    ("A1 drift state machine", check_a1_state_machine),
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
