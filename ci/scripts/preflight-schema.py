#!/usr/bin/env python3
"""Preflight schema probe — 10-assertion schema closure probe (v1.1.0 + v1.2.0).

Validates that profile.schema.v1.1.0.json and profile.schema.v1.2.0.json
enforce unevaluatedProperties closure correctly under JSON Schema draft
2020-12, that draft-version-dependent enforcement is preserved (control
assertion via draft-07 mislabel), and that v1.2.0 cross-field
type-consistency invariants reject inconsistent project_structure.type
and monorepo_detection.detected pairs.

Exit codes:
    0 — all 10 assertions pass (schema correct)
    1 — one or more assertions fail (schema broken)
    2 — profile.schema.v1.1.0.json or profile.schema.v1.2.0.json not yet committed
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Windows cp949 defense: ensure stdout/stderr are UTF-8 so non-ASCII in schema
# paths or error messages doesn't raise UnicodeEncodeError on Korean-locale hosts.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass  # older Python or non-standard streams

try:
    from jsonschema import Draft202012Validator, Draft7Validator
    from referencing import Registry, Resource
except ImportError as exc:
    print(f"[FATAL] jsonschema or referencing not installed: {exc}", file=sys.stderr)
    print("Install with: pip install jsonschema==4.23.0", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMAS_DIR = ROOT / "plugin" / "references" / "schemas"
SCHEMAS = {
    "1.1.0": SCHEMAS_DIR / "profile.schema.v1.1.0.json",
    "1.2.0": SCHEMAS_DIR / "profile.schema.v1.2.0.json",
}
BASE_PATH = SCHEMAS_DIR / "profile.schema.base.json"
FIXTURES_DIR = ROOT / "ci" / "fixtures" / "preflight-schema"

FIXTURE_1_V110 = FIXTURES_DIR / "fixture-1-valid-v1.1.0.json"
FIXTURE_2 = FIXTURES_DIR / "fixture-2-unknown-root.json"
FIXTURE_3 = FIXTURES_DIR / "fixture-3-unknown-nested.json"
FIXTURE_4_SCHEMA = FIXTURES_DIR / "fixture-4-draft07-schema.json"
FIXTURE_1_V120 = FIXTURES_DIR / "fixture-1-valid-v1.2.0.json"
FIXTURE_5_S71 = FIXTURES_DIR / "fixture-5-single-project-detected-true.json"
FIXTURE_6_S72 = FIXTURES_DIR / "fixture-6-monorepo-detected-false.json"
FIXTURE_7_S73 = FIXTURES_DIR / "fixture-7-null-detected-false.json"
FIXTURE_8_UNKNOWN_CLAUDE_MD = FIXTURES_DIR / "fixture-8-unknown-claude-md-property.json"
FIXTURE_9_NULL_DETECTED_NON_NULL_TYPE = FIXTURES_DIR / "fixture-9-null-detected-non-null-type.json"


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
    # T0 gate: both schemas must exist before assertions can run.
    missing = [v for v, p in SCHEMAS.items() if not p.exists()]
    if missing:
        print(
            f"Preflight probe blocked: schema(s) not yet committed for version(s) {missing}",
            file=sys.stderr,
        )
        return 2

    for ver, path in SCHEMAS.items():
        print(f"Schema {ver} found: {path.relative_to(ROOT)}")
    base_schema = load_json(BASE_PATH)
    registry = build_registry(base_schema)
    schemas = {ver: load_json(p) for ver, p in SCHEMAS.items()}
    schema_draft07_control = load_json(FIXTURE_4_SCHEMA)

    fixture1_v110 = load_json(FIXTURE_1_V110)
    fixture2 = load_json(FIXTURE_2)
    fixture3 = load_json(FIXTURE_3)

    all_passed = True

    # ------------------------------------------------------------------
    # Assertion 1: fixture-1 (valid v1.1.0 instance) must be ACCEPTED
    # ------------------------------------------------------------------
    valid, err = is_valid(Draft202012Validator, schemas["1.1.0"], fixture1_v110, registry=registry)
    if valid:
        print("[ASSERT 1] PASS — valid v1.1.0 instance accepted by Draft202012Validator")
    else:
        print(f"[ASSERT 1] FAIL — valid v1.1.0 instance unexpectedly rejected: {err}")
        all_passed = False

    # ------------------------------------------------------------------
    # Assertion 2: fixture-2 (unknown root property) must be REJECTED
    # ------------------------------------------------------------------
    valid, err = is_valid(Draft202012Validator, schemas["1.1.0"], fixture2, registry=registry)
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
    valid, err = is_valid(Draft202012Validator, schemas["1.1.0"], fixture3, registry=registry)
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
    # Assertion 5: fixture-1-valid-v1.2.0 must be ACCEPTED by v1.2.0 wrapper
    # ------------------------------------------------------------------
    fixture1_v120 = load_json(FIXTURE_1_V120)
    valid, err = is_valid(Draft202012Validator, schemas["1.2.0"], fixture1_v120, registry=registry)
    if valid:
        print("[ASSERT 5] PASS — valid v1.2.0 instance accepted by Draft202012Validator")
    else:
        print(f"[ASSERT 5] FAIL — valid v1.2.0 instance unexpectedly rejected: {err}")
        all_passed = False

    # ------------------------------------------------------------------
    # Assertion 6: fixture-5 (type=single_project + detected=true) must be REJECTED
    # ------------------------------------------------------------------
    fixture5 = load_json(FIXTURE_5_S71)
    valid, err = is_valid(Draft202012Validator, schemas["1.2.0"], fixture5, registry=registry)
    if not valid:
        print("[ASSERT 6] PASS — type/detected inconsistency (single_project + detected:true) rejected")
    else:
        print("[ASSERT 6] FAIL — type/detected inconsistency NOT rejected (cross-field reverse implication if/then missing or broken)")
        all_passed = False

    # ------------------------------------------------------------------
    # Assertion 7: fixture-6 (type=monorepo + detected=false) must be REJECTED
    # ------------------------------------------------------------------
    fixture6 = load_json(FIXTURE_6_S72)
    valid, err = is_valid(Draft202012Validator, schemas["1.2.0"], fixture6, registry=registry)
    if not valid:
        print("[ASSERT 7] PASS — type/detected inconsistency (monorepo + detected:false) rejected")
    else:
        print("[ASSERT 7] FAIL — type/detected inconsistency NOT rejected (cross-field forward implication if/then missing or broken)")
        all_passed = False

    # ------------------------------------------------------------------
    # Assertion 8: fixture-7 (type=null + detected=false) must be REJECTED
    # under the strict null-fallback rule (only null/null is the no-decision state)
    # ------------------------------------------------------------------
    fixture7 = load_json(FIXTURE_7_S73)
    valid, err = is_valid(Draft202012Validator, schemas["1.2.0"], fixture7, registry=registry)
    if not valid:
        print("[ASSERT 8] PASS — type/detected inconsistency (null + detected:false) rejected")
    else:
        print("[ASSERT 8] FAIL — strict null-fallback rule NOT enforced (boolean-detected → non-null type if/then missing or broken)")
        all_passed = False

    # ------------------------------------------------------------------
    # Assertion 9: fixture-8 (unknown property under claude_md) must be REJECTED
    # by claude_md unevaluatedProperties closure.
    # ------------------------------------------------------------------
    fixture8 = load_json(FIXTURE_8_UNKNOWN_CLAUDE_MD)
    valid, err = is_valid(Draft202012Validator, schemas["1.2.0"], fixture8, registry=registry)
    if not valid:
        print("[ASSERT 9] PASS — unknown property under claude_md rejected by unevaluatedProperties closure")
    else:
        print("[ASSERT 9] FAIL — unknown property under claude_md NOT rejected (claude_md closure missing or broken)")
        all_passed = False

    # ------------------------------------------------------------------
    # Assertion 10: fixture-9 (detected:null + type:single_project) must be REJECTED
    # under the §7.3 biconditional reading (degraded detection requires degraded type).
    # ------------------------------------------------------------------
    fixture9 = load_json(FIXTURE_9_NULL_DETECTED_NON_NULL_TYPE)
    valid, err = is_valid(Draft202012Validator, schemas["1.2.0"], fixture9, registry=registry)
    if not valid:
        print("[ASSERT 10] PASS — type/detected inconsistency (detected:null + type:single_project) rejected")
    else:
        print("[ASSERT 10] FAIL — biconditional null-detected → null-type if/then missing or broken")
        all_passed = False

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print()
    if all_passed:
        print("All 10 preflight assertions PASSED — v1.1.0 + v1.2.0 schemas are correctly structured.")
        return 0
    else:
        print("One or more preflight assertions FAILED — v1.1.0 or v1.2.0 schema has structural issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
