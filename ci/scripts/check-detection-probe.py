#!/usr/bin/env python3
"""ci/scripts/check-detection-probe.py — schema validator for detection probe fixtures.

Validates fixture JSON schema (required fields, enum values, type-consistency
rules per the monorepo detection spec). Does NOT run the detection algorithm
against fixture inputs — runtime invocation is deferred to a future patch.

Schema (per fixture):

    {
      "name": "<tier>/<ecosystem>/<seq>-<scenario>",
      "ecosystem": "<one of VALID_ECOSYSTEMS>",
      "spec_ref": "<spec section reference>",
      "input": {
        "manifests": { "<filename>": "<file-content-as-string>" },
        "directories": ["<rel-path>"]
      },
      "expected": {
        "detected": <bool>,
        "evidence_types": ["<one of VALID_EVIDENCE_TYPES>"],
        "package_roots_count": <int >= 0>,
        "type": "monorepo" | "single_project" | null,
        "notes_codes": ["<code>"]   # optional
      }
    }

Exit codes:
    0 — every fixture validates against the schema
    1 — one or more fixtures violate the schema
    2 — ci/fixtures/detection-probe/ absent (CI soft-skip)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Windows cp949 defense — non-ASCII paths or messages must not raise
# UnicodeEncodeError on Korean-locale hosts.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass  # older Python or non-standard streams

ROOT = Path(__file__).resolve().parents[2]
PROBE_DIR = ROOT / "ci" / "fixtures" / "detection-probe"

VALID_ECOSYSTEMS = {
    "node", "rust", "go", "python", "maven", "gradle", "dual-role",
    "dotnet", "elixir", "swift", "ruby", "cpp", "dart", "erlang", "haskell",
}
VALID_EVIDENCE_TYPES = {
    "workspace_declaration",
    "heuristic_signal",
    "convention",
    "composite_build",
    "parse_error",
}
VALID_TYPES = {"monorepo", "single_project", None}
REQUIRED_TOP = ("name", "ecosystem", "spec_ref", "input", "expected")
REQUIRED_INPUT = ("manifests", "directories")
REQUIRED_EXPECTED = ("detected", "evidence_types", "package_roots_count", "type")


def validate_fixture(path: Path, fixture: dict) -> list[str]:
    """Return list of human-readable error messages for one fixture (empty = pass)."""
    errors: list[str] = []
    rel = path.relative_to(ROOT)

    # Top-level required fields
    for field in REQUIRED_TOP:
        if field not in fixture:
            errors.append(f"{rel}: missing top-level '{field}'")
    if errors:
        # Short-circuit — downstream checks need the fields above.
        return errors

    # Ecosystem enum
    if fixture["ecosystem"] not in VALID_ECOSYSTEMS:
        errors.append(
            f"{rel}: invalid ecosystem {fixture['ecosystem']!r} "
            f"(allowed: {sorted(VALID_ECOSYSTEMS)})"
        )

    # spec_ref must be non-empty string
    if not isinstance(fixture.get("spec_ref"), str) or not fixture["spec_ref"]:
        errors.append(f"{rel}: spec_ref must be non-empty string")

    # input shape
    inp = fixture["input"]
    if not isinstance(inp, dict):
        errors.append(f"{rel}: input must be object")
    else:
        for field in REQUIRED_INPUT:
            if field not in inp:
                errors.append(f"{rel}: missing input.{field}")
        if not isinstance(inp.get("manifests"), dict):
            errors.append(f"{rel}: input.manifests must be object")
        else:
            for fname, content in inp["manifests"].items():
                if not isinstance(content, str):
                    errors.append(
                        f"{rel}: input.manifests[{fname!r}] must be string "
                        f"(got {type(content).__name__})"
                    )
        if not isinstance(inp.get("directories"), list):
            errors.append(f"{rel}: input.directories must be array")
        else:
            for idx, d in enumerate(inp["directories"]):
                if not isinstance(d, str):
                    errors.append(
                        f"{rel}: input.directories[{idx}] must be string"
                    )

    # expected shape
    expected = fixture["expected"]
    if not isinstance(expected, dict):
        errors.append(f"{rel}: expected must be object")
        return errors  # cannot proceed without expected

    for field in REQUIRED_EXPECTED:
        if field not in expected:
            errors.append(f"{rel}: missing expected.{field}")

    if not isinstance(expected.get("detected"), bool):
        errors.append(f"{rel}: expected.detected must be bool")

    et = expected.get("evidence_types", [])
    if not isinstance(et, list):
        errors.append(f"{rel}: expected.evidence_types must be array")
    else:
        for item in et:
            if item not in VALID_EVIDENCE_TYPES:
                errors.append(
                    f"{rel}: invalid evidence type {item!r} "
                    f"(allowed: {sorted(VALID_EVIDENCE_TYPES)})"
                )

    prc = expected.get("package_roots_count")
    if not isinstance(prc, int) or isinstance(prc, bool) or prc < 0:
        errors.append(
            f"{rel}: expected.package_roots_count must be int >= 0 (got {prc!r})"
        )

    if expected.get("type") not in VALID_TYPES:
        errors.append(
            f"{rel}: invalid type {expected.get('type')!r} "
            f"(allowed: monorepo|single_project|null)"
        )

    # notes_codes optional but must be array of strings if present
    if "notes_codes" in expected:
        nc = expected["notes_codes"]
        if not isinstance(nc, list):
            errors.append(f"{rel}: expected.notes_codes must be array if present")
        else:
            for idx, code in enumerate(nc):
                if not isinstance(code, str):
                    errors.append(
                        f"{rel}: expected.notes_codes[{idx}] must be string"
                    )

    # Type-consistency rules (per monorepo-detection §4).
    t = expected.get("type")
    d = expected.get("detected")
    if t == "single_project" and d is True:
        errors.append(
            f"{rel}: type='single_project' + detected=true violates "
            f"type-consistency rule 1"
        )
    if t == "monorepo" and d is not True:
        errors.append(
            f"{rel}: type='monorepo' must have detected=true per "
            f"type-consistency rule 2"
        )

    return errors


def main() -> int:
    if not PROBE_DIR.exists():
        print(
            f"SKIP - detection-probe directory not present at "
            f"{PROBE_DIR.relative_to(ROOT)}"
        )
        return 2

    fixtures = sorted(PROBE_DIR.rglob("*.json"))
    if not fixtures:
        print(f"SKIP - no probe fixtures found under {PROBE_DIR.relative_to(ROOT)}")
        return 2

    all_errors: list[str] = []
    for path in fixtures:
        try:
            with path.open(encoding="utf-8") as f:
                fixture = json.load(f)
        except json.JSONDecodeError as e:
            all_errors.append(f"{path.relative_to(ROOT)}: invalid JSON - {e}")
            continue
        all_errors.extend(validate_fixture(path, fixture))

    if all_errors:
        for err in all_errors:
            print(err, file=sys.stderr)
        print(
            f"FAIL - {len(all_errors)} schema violation(s) across "
            f"{len(fixtures)} fixture(s)",
            file=sys.stderr,
        )
        return 1

    print(f"PASS - {len(fixtures)} fixtures schema-valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
