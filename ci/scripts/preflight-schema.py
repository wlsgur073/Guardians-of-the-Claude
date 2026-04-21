#!/usr/bin/env python3
"""Preflight schema probe — 4-assertion schema closure probe.

Validates that profile.schema.v1.1.0.json enforces unevaluatedProperties
closure correctly under JSON Schema draft 2020-12, and that this enforcement
is draft-version-dependent (control assertion via draft-07 mislabel).

Exit codes:
    0 — all 4 assertions pass (schema correct)
    1 — one or more assertions fail (schema broken)
    2 — profile.schema.v1.1.0.json not yet committed
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, Draft7Validator
    from referencing import Registry, Resource
except ImportError as exc:
    print(f"[FATAL] jsonschema or referencing not installed: {exc}", file=sys.stderr)
    print("Install with: pip install jsonschema==4.23.0", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMAS_DIR = ROOT / "plugin" / "references" / "schemas"
SCHEMA_PATH = SCHEMAS_DIR / "profile.schema.v1.1.0.json"
BASE_PATH = SCHEMAS_DIR / "profile.schema.base.json"
FIXTURES_DIR = ROOT / "ci" / "fixtures" / "preflight-schema"

FIXTURE_1 = FIXTURES_DIR / "fixture-1-valid-v1.1.0.json"
FIXTURE_2 = FIXTURES_DIR / "fixture-2-unknown-root.json"
FIXTURE_3 = FIXTURES_DIR / "fixture-3-unknown-nested.json"
FIXTURE_4_SCHEMA = FIXTURES_DIR / "fixture-4-draft07-schema.json"


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def build_registry(base_schema: dict) -> Registry:
    """Register the base schema so $ref resolution works for versioned wrappers."""
    return Registry().with_resources(
        [("profile.schema.base.json", Resource.from_contents(base_schema))]
    )


def is_valid(
    validator_cls, schema: dict, instance: dict, registry: Registry | None = None
) -> tuple[bool, str]:
    """Return (valid, error_message). error_message is empty string if valid."""
    kwargs = {"registry": registry} if registry is not None else {}
    validator = validator_cls(schema, **kwargs)
    errors = list(validator.iter_errors(instance))
    if errors:
        return False, "; ".join(e.message for e in errors[:3])
    return True, ""


def main() -> int:
    # T0 gate: schema must exist before assertions can run.
    if not SCHEMA_PATH.exists():
        print(
            "Preflight probe blocked: profile.schema.v1.1.0.json not yet committed"
            " — this is a T1 prerequisite",
            file=sys.stderr,
        )
        return 2

    print(f"Schema found: {SCHEMA_PATH.relative_to(ROOT)}")
    base_schema = load_json(BASE_PATH)
    registry = build_registry(base_schema)
    schema_v110 = load_json(SCHEMA_PATH)
    schema_draft07_control = load_json(FIXTURE_4_SCHEMA)

    fixture1 = load_json(FIXTURE_1)
    fixture2 = load_json(FIXTURE_2)
    fixture3 = load_json(FIXTURE_3)

    all_passed = True

    # ------------------------------------------------------------------
    # Assertion 1: fixture-1 (valid v1.1.0 instance) must be ACCEPTED
    # ------------------------------------------------------------------
    valid, err = is_valid(Draft202012Validator, schema_v110, fixture1, registry=registry)
    if valid:
        print("[ASSERT 1] PASS — valid v1.1.0 instance accepted by Draft202012Validator")
    else:
        print(f"[ASSERT 1] FAIL — valid v1.1.0 instance unexpectedly rejected: {err}")
        all_passed = False

    # ------------------------------------------------------------------
    # Assertion 2: fixture-2 (unknown root property) must be REJECTED
    # ------------------------------------------------------------------
    valid, err = is_valid(Draft202012Validator, schema_v110, fixture2, registry=registry)
    if not valid:
        print("[ASSERT 2] PASS — unknown root property rejected by unevaluatedProperties closure")
    else:
        print(
            "[ASSERT 2] FAIL — unknown root property '_extra' was NOT rejected"
            " (unevaluatedProperties closure missing or broken at root)"
        )
        all_passed = False

    # ------------------------------------------------------------------
    # Assertion 3: fixture-3 (unknown nested property) must be REJECTED
    # ------------------------------------------------------------------
    valid, err = is_valid(Draft202012Validator, schema_v110, fixture3, registry=registry)
    if not valid:
        print(
            "[ASSERT 3] PASS — unknown nested property rejected by"
            " unevaluatedProperties closure on claude_code_configuration_state"
        )
    else:
        print(
            "[ASSERT 3] FAIL — unknown nested property 'unexpected' was NOT rejected"
            " (unevaluatedProperties closure missing or broken on claude_code_configuration_state)"
        )
        all_passed = False

    # ------------------------------------------------------------------
    # Assertion 4: CONTROL — under draft-07 mislabel, fixtures 2+3 must be ACCEPTED
    # This proves that unevaluatedProperties enforcement is draft-2020-12-dependent.
    # The draft-07 validator ignores unevaluatedProperties (unknown keyword).
    # draft-07 schema is self-contained (no $ref to base) — no registry needed.
    # ------------------------------------------------------------------
    valid2_draft07, err2 = is_valid(Draft7Validator, schema_draft07_control, fixture2)
    valid3_draft07, err3 = is_valid(Draft7Validator, schema_draft07_control, fixture3)

    if valid2_draft07 and valid3_draft07:
        print(
            "[ASSERT 4] PASS — draft-07 control: both fixture-2 and fixture-3 accepted"
            " under draft-07 mislabel (unevaluatedProperties ignored, confirming"
            " that 2020-12 $schema declaration on real wrapper is load-bearing)"
        )
    else:
        failures = []
        if not valid2_draft07:
            failures.append(f"fixture-2 unexpectedly rejected under draft-07: {err2}")
        if not valid3_draft07:
            failures.append(f"fixture-3 unexpectedly rejected under draft-07: {err3}")
        print(
            "[ASSERT 4] FAIL — draft-07 control failed: " + "; ".join(failures)
        )
        all_passed = False

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print()
    if all_passed:
        print("All 4 preflight assertions PASSED — T1 schema is correctly structured.")
        return 0
    else:
        print("One or more preflight assertions FAILED — T1 schema has structural issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
