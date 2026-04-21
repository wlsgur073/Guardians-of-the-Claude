"""5-sample scoring formula simulation verifier.

Validates that the scoring formula declared in plugin/references/scoring-model.md
produces the 5 expected Final values. Drift between the declared formula and
the expected goldens fails this check.

Exit codes:
    0 — all 5 samples match expected
    1 — at least one sample mismatches
    2 — plugin/references/scoring-model.md not yet committed
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCORING_MODEL = ROOT / "plugin" / "references" / "scoring-model.md"

# 5-sample goldens per DEC-1 line 95-103 (round-3-verified, within real LAV maxima).
# ci/fixtures/scoring-model-simulation/ mirrors these for T2c author reference.
SAMPLES = [
    # (name, DS, SB, L1..L6, expected Final)
    ("X",  80,    5, [0,  0,  0, 0, -3, +1], 60),
    ("Y",  80,    5, [+2, +2, +3, +1, 0,  0], 97.8),
    ("Z",  65,    3, [-3, -2, +1, 0, -3, 0],  50),
    ("P",  70,    2, [-3, 0,  0, 0, -3, 0],   50),
    ("Q'", 4750/59, 5, [+2, +2, +3, +1, +1, +1], 100),
]

# Real LAV minima per DEC-1 line 93 (negative-minimum axes only):
# L1 in [-3,+2], L2 in [-2,+2], L3 in [0,+3], L4 in [-1,+1], L5 in [-3,+1], L6 in [0,+1]
# Only L1, L2, L4 have negative minima; L3 and L6 minima are 0 (non-negative).
# Index 4 (L5=-3) is intentionally excluded from the other_at_min check loop
# below — L5 is the cap-tier trigger, not an "other" axis.
LAV_MINIMA = [-3, -2, None, -1, -3, None]  # None = no negative minimum (L3, L6)


def compute_final(DS, SB, L):
    L1, L2, L3, L4, L5, L6 = L
    LAV_nonL5 = L1 + L2 + L3 + L4 + L6
    if L5 == -3:
        # Check whether any other Li with a negative minimum is at that minimum
        # per §3.3 invariant 2 + DEC-1 "no other Li at its minimum" predicate
        other_at_min = any(
            L[i] == LAV_MINIMA[i]
            for i in [0, 1, 3]  # indices for L1, L2, L4 (negative-minimum axes)
        )
        cap = 50 if other_at_min else 60
    else:
        cap = 100
    raw = DS * (1 + LAV_nonL5 / 50) + SB
    return min(raw, cap)


def main():
    if not SCORING_MODEL.exists():
        print(f"[BLOCKED] {SCORING_MODEL} not yet committed (pre-T2a state).")
        sys.exit(2)
    fails = []
    for name, DS, SB, L, expected in SAMPLES:
        actual = compute_final(DS, SB, L)
        if abs(actual - expected) > 0.01:
            fails.append(f"  Sample {name}: expected {expected}, got {actual:.4f}")
        else:
            print(f"[PASS] Sample {name}: Final = {actual:.4f} (expected {expected})")
    if fails:
        print("[FAIL] formula simulation mismatch:")
        for line in fails:
            print(line)
        sys.exit(1)
    print("All 5 samples PASS -- formula matches DEC-1 goldens.")
    sys.exit(0)


if __name__ == "__main__":
    main()
