#!/usr/bin/env python3
"""CLI entrypoint: runs registry lints against positive fixtures (expect pass)
and negative fixtures (expect fail).

Exit codes:
    0 - all fixtures behaved as expected
    1 - any positive fixture failed lints, or any negative fixture passed lints
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure .github/scripts is on sys.path so "from lib.recommendation_registry import ..." works
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.recommendation_registry import load_registry, check_recommendations

ROOT = Path(__file__).resolve().parent.parent.parent

# Positive fixtures: recommendations.json instances that must PASS all lints.
# ci/fixtures/ does not yet exist (Task 5 creates it); gracefully handle no matches.
POSITIVE_GLOBS: list[str] = [
    "ci/fixtures/**/recommendations.json",
]

# Negative fixtures: explicitly enumerated to avoid matching Task 1's structural
# negatives (recommendations.invalid-id-format.example.json,
# recommendations.resolved-without-by.example.json), which are schema-level
# failures and may produce unpredictable results under lint checks.
NEGATIVE_PATHS: list[str] = [
    "plugin/references/schemas/examples/negative/recommendations.unknown-id.example.json",
    "plugin/references/schemas/examples/negative/recommendations.unauthorized-issuer.example.json",
]


def main() -> int:
    registry = load_registry(ROOT / "plugin/references/recommendation-registry.json")
    total_failures = 0

    # Positive fixtures: must pass all lints
    for pattern in POSITIVE_GLOBS:
        for path in sorted(ROOT.glob(pattern)):
            insts = json.loads(path.read_text(encoding="utf-8")).get("recommendations", [])
            failures = check_recommendations(insts, registry)
            if failures:
                total_failures += len(failures)
                for msg in failures:
                    print(f"[FAIL] {path.relative_to(ROOT)}: {msg}")

    # Negative fixtures: must be rejected (at least one lint failure)
    for rel in NEGATIVE_PATHS:
        path = ROOT / rel
        try:
            insts = json.loads(path.read_text(encoding="utf-8")).get("recommendations", [])
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] {rel}: could not load fixture: {exc}")
            total_failures += 1
            continue
        failures = check_recommendations(insts, registry)
        if not failures:
            total_failures += 1
            print(f"[FAIL] {rel}: negative fixture must fail lints but passed")
        else:
            print(f"[OK] {rel}: correctly rejected ({len(failures)} failure(s))")

    return 0 if total_failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
