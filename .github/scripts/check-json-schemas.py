#!/usr/bin/env python3
"""Validate JSON files against schemas and required fields.

Uses json.schemastore.org for well-known Claude Code settings, and
required-field checks for project-specific files (plugin.json,
marketplace.json, .mcp.json).

If a remote schema cannot be fetched, logs a warning and falls back
to required-field checks only (graceful degradation).

Exit codes:
    0 - all files valid
    1 - schema violation, missing field, or invalid JSON
"""
from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path

# Windows cp949 defense: ensure stdout/stderr are UTF-8 so non-ASCII strings
# don't raise UnicodeEncodeError on Korean-locale Windows hosts.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

import jsonschema
import requests
from referencing import Registry, Resource


# FormatChecker with stdlib-only date-time validator. Avoids the jsonschema[format]
# extra (rfc3339-validator dependency) by using datetime.fromisoformat directly.
# Python 3.11+ handles trailing 'Z' via the explicit '+00:00' replacement.
_FORMAT_CHECKER = jsonschema.FormatChecker()


@_FORMAT_CHECKER.checks("date-time", raises=ValueError)
def _is_iso_date_time(instance: object) -> bool:
    if not isinstance(instance, str):
        return True
    datetime.datetime.fromisoformat(instance.replace("Z", "+00:00"))
    return True

ROOT = Path(__file__).resolve().parent.parent.parent
PROFILE_SCHEMAS_DIR = ROOT / "plugin" / "references" / "schemas"

CLAUDE_CODE_SETTINGS_SCHEMA_URL = (
    "https://json.schemastore.org/claude-code-settings.json"
)

# Each rule: (glob pattern relative to ROOT, schema URL or None, required fields or None)
RULES: list[tuple[str, str | None, list[str] | None]] = [
    # Claude Code settings (schemastore)
    ("templates/*/.claude/settings.json", CLAUDE_CODE_SETTINGS_SCHEMA_URL, None),
    (
        "docs/i18n/ko-KR/templates/*/.claude/settings.json",
        CLAUDE_CODE_SETTINGS_SCHEMA_URL,
        None,
    ),
    (
        "docs/i18n/ja-JP/templates/*/.claude/settings.json",
        CLAUDE_CODE_SETTINGS_SCHEMA_URL,
        None,
    ),
    # Plugin manifest
    ("plugin/.claude-plugin/plugin.json", None, ["name", "version"]),
    # Marketplace manifest
    (".claude-plugin/marketplace.json", None, ["name", "plugins"]),
    # MCP configuration
    ("templates/*/.mcp.json", None, ["mcpServers"]),
    ("docs/i18n/ko-KR/templates/*/.mcp.json", None, ["mcpServers"]),
    ("docs/i18n/ja-JP/templates/*/.mcp.json", None, ["mcpServers"]),
]


# Local schema validation: (schema_path, example_path) relative to ROOT.
# Profile instances use the dispatcher (see select_profile_wrapper + _profile_registry).
# Recommendations instances use the dispatcher (see select_recommendations_wrapper + _recommendations_registry).
# Other schemas are validated directly.
LOCAL_SCHEMAS: list[tuple[str, str]] = [
    (
        "plugin/references/recommendation-registry.schema.json",
        "plugin/references/recommendation-registry.json",
    ),
]

# Negative fixtures: (schema_path, negative_example_path) — each MUST be rejected.
# Profile and recommendations negative fixtures are handled by their respective
# dispatcher-aware validators below.
NEGATIVE_LOCAL_SCHEMAS: list[tuple[str, str]] = []

# Profile positive examples — dispatcher selects wrapper by schema_version literal.
PROFILE_POSITIVE_EXAMPLES: list[str] = [
    "plugin/references/schemas/examples/profile.example.json",
]

# Profile negative examples — dispatcher selects wrapper; each MUST be rejected.
PROFILE_NEGATIVE_EXAMPLES: list[str] = [
    "plugin/references/schemas/examples/negative/profile.missing-required.example.json",
    "plugin/references/schemas/examples/negative/profile.wrong-version.example.json",
    "plugin/references/schemas/examples/negative/profile.monorepo-without-detection.example.json",
    "plugin/references/schemas/examples/negative/profile.detection-without-monorepo.example.json",
    "plugin/references/schemas/examples/negative/profile.detected-boolean-type-null.example.json",
    "plugin/references/schemas/examples/negative/profile.detected-null-type-not-null.example.json",
]

# Recommendations positive examples — dispatcher selects wrapper by schema_version literal.
RECOMMENDATIONS_POSITIVE_EXAMPLES: list[str] = [
    "plugin/references/schemas/examples/recommendations.example.json",
    "plugin/references/schemas/examples/recommendations.v1.1.0.example.json",
]

# Recommendations negative examples — dispatcher selects wrapper; each MUST be rejected.
RECOMMENDATIONS_NEGATIVE_EXAMPLES: list[str] = [
    "plugin/references/schemas/examples/negative/recommendations.invalid-id-format.example.json",
    "plugin/references/schemas/examples/negative/recommendations.resolved-without-by.example.json",
    "plugin/references/schemas/examples/negative/recommendations.v1.0.0-with-decline-count.example.json",
    "plugin/references/schemas/examples/negative/recommendations.v1.1.0-decline-count-negative.example.json",
    "plugin/references/schemas/examples/negative/recommendations.metadata-extra.example.json",
    "plugin/references/schemas/examples/negative/recommendations.invalid-status-enum.example.json",
    "plugin/references/schemas/examples/negative/recommendations.empty-description.example.json",
    "plugin/references/schemas/examples/negative/recommendations.invalid-iso-date.example.json",
]


def _profile_registry() -> Registry:
    """Build a referencing Registry with the base profile schema registered.

    The versioned wrappers use $ref to profile.schema.base.json; the registry
    resolves those references without network I/O.
    """
    base = json.loads(
        (PROFILE_SCHEMAS_DIR / "profile.schema.base.json").read_text(encoding="utf-8")
    )
    return Registry().with_resources(
        [("profile.schema.base.json", Resource.from_contents(base))]
    )


def select_profile_wrapper(schema_version: str) -> tuple[dict, str]:
    """Select the versioned profile schema wrapper by schema_version literal.

    Returns (schema_dict, wrapper_filename). Raises ValueError on unknown version
    with a diagnostic naming the literal and the candidate path that was tried.
    """
    candidate = PROFILE_SCHEMAS_DIR / f"profile.schema.v{schema_version}.json"
    if not candidate.exists():
        raise ValueError(
            f"Unknown schema_version '{schema_version}': no wrapper found at"
            f" {candidate.relative_to(ROOT)}"
        )
    return json.loads(candidate.read_text(encoding="utf-8")), candidate.name


def _recommendations_registry() -> Registry:
    """Build a referencing Registry with the base recommendations schema registered.

    Versioned wrappers use $ref to recommendations.schema.base.json; the registry
    resolves those references without network I/O. Mirrors _profile_registry().
    """
    base = json.loads(
        (PROFILE_SCHEMAS_DIR / "recommendations.schema.base.json").read_text(encoding="utf-8")
    )
    return Registry().with_resources(
        [("recommendations.schema.base.json", Resource.from_contents(base))]
    )


def select_recommendations_wrapper(schema_version: str) -> tuple[dict, str]:
    """Select the versioned recommendations schema wrapper by schema_version literal.

    Returns (schema_dict, wrapper_filename). Raises ValueError on unknown version
    with a diagnostic naming the literal and the candidate path that was tried.
    Mirrors select_profile_wrapper's signature, return type, and registry pattern.
    """
    candidate = PROFILE_SCHEMAS_DIR / f"recommendations.schema.v{schema_version}.json"
    if not candidate.exists():
        raise ValueError(
            f"Unknown schema_version '{schema_version}': no wrapper found at"
            f" {candidate.relative_to(ROOT)}"
        )
    return json.loads(candidate.read_text(encoding="utf-8")), candidate.name


def validate_local_schemas(errors: list[str]) -> int:
    """Validate positive example files against their local schemas.

    Returns the count of files checked (for the total counter).
    """
    checked = 0
    for schema_path, example_path in LOCAL_SCHEMAS:
        s_rel = schema_path
        e_rel = example_path
        try:
            schema = json.loads((ROOT / schema_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"[schema load error] {s_rel}: {exc}")
            continue
        try:
            example = json.loads((ROOT / example_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"[example load error] {e_rel}: {exc}")
            continue
        try:
            jsonschema.validate(example, schema)
        except jsonschema.ValidationError as exc:
            errors.append(f"[schema violation] {e_rel} against {s_rel}: {exc.message}")
            continue
        checked += 1
    return checked


def validate_profile_positive_examples(errors: list[str]) -> int:
    """Validate profile positive examples via the schema_version dispatcher.

    Returns the count of files checked.
    """
    registry = _profile_registry()
    checked = 0
    for example_path in PROFILE_POSITIVE_EXAMPLES:
        e_rel = example_path
        try:
            instance = json.loads((ROOT / example_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"[example load error] {e_rel}: {exc}")
            continue
        sv = instance.get("schema_version")
        if sv is None:
            errors.append(f"[missing schema_version] {e_rel}: cannot dispatch without schema_version")
            continue
        try:
            schema, wrapper_name = select_profile_wrapper(sv)
        except ValueError as exc:
            errors.append(f"[dispatcher error] {e_rel}: {exc}")
            continue
        try:
            jsonschema.Draft202012Validator(schema, registry=registry).validate(instance)
        except jsonschema.ValidationError as exc:
            errors.append(
                f"[schema violation] {e_rel} against {wrapper_name}: {exc.message}"
            )
            continue
        checked += 1
    return checked


def validate_profile_negative_examples(errors: list[str]) -> None:
    """Assert that profile negative examples are REJECTED by the dispatcher.

    Unknown schema_version → dispatcher error (also counted as a rejection).
    Known schema_version + invalid shape → wrapper rejects.
    """
    registry = _profile_registry()
    for fixture_path in PROFILE_NEGATIVE_EXAMPLES:
        f_rel = fixture_path
        try:
            instance = json.loads((ROOT / fixture_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"[fixture load error] {f_rel}: {exc}")
            continue
        sv = instance.get("schema_version")
        if sv is None:
            # Missing schema_version is itself a rejection — no need to validate.
            continue
        try:
            schema, wrapper_name = select_profile_wrapper(sv)
        except ValueError:
            # Unknown schema_version — dispatcher correctly rejects; expected for negative fixtures.
            continue
        try:
            jsonschema.Draft202012Validator(schema, registry=registry).validate(instance)
            # If we reach here, the fixture was NOT rejected — schema regression.
            errors.append(
                f"[schema regression] {f_rel} was accepted by {wrapper_name} but must be rejected"
            )
        except jsonschema.ValidationError:
            pass  # expected: fixture correctly rejected


def validate_recommendations_positive_examples(errors: list[str]) -> int:
    """Validate recommendations positive examples via the schema_version dispatcher.

    Returns the count of files checked. Mirrors validate_profile_positive_examples.
    Uses FormatChecker so `format: date-time` on first_seen/last_seen/last_updated
    is enforced — non-ISO-8601 strings will reject.
    """
    registry = _recommendations_registry()
    checked = 0
    for example_path in RECOMMENDATIONS_POSITIVE_EXAMPLES:
        e_rel = example_path
        try:
            instance = json.loads((ROOT / example_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"[example load error] {e_rel}: {exc}")
            continue
        sv = instance.get("schema_version")
        if sv is None:
            errors.append(f"[missing schema_version] {e_rel}: cannot dispatch without schema_version")
            continue
        try:
            schema, wrapper_name = select_recommendations_wrapper(sv)
        except ValueError as exc:
            errors.append(f"[dispatcher error] {e_rel}: {exc}")
            continue
        try:
            jsonschema.Draft202012Validator(
                schema, registry=registry, format_checker=_FORMAT_CHECKER
            ).validate(instance)
        except jsonschema.ValidationError as exc:
            errors.append(
                f"[schema violation] {e_rel} against {wrapper_name}: {exc.message}"
            )
            continue
        checked += 1
    return checked


def validate_recommendations_negative_examples(errors: list[str]) -> None:
    """Assert that recommendations negative examples are REJECTED by the dispatcher.

    Mirrors validate_profile_negative_examples. FormatChecker enabled so
    invalid-iso-date fixture (non-ISO-8601 first_seen/last_seen) rejects.
    """
    registry = _recommendations_registry()
    for fixture_path in RECOMMENDATIONS_NEGATIVE_EXAMPLES:
        f_rel = fixture_path
        try:
            instance = json.loads((ROOT / fixture_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"[fixture load error] {f_rel}: {exc}")
            continue
        sv = instance.get("schema_version")
        if sv is None:
            continue  # missing schema_version is itself a rejection
        try:
            schema, wrapper_name = select_recommendations_wrapper(sv)
        except ValueError:
            continue  # unknown schema_version — dispatcher correctly rejects
        try:
            jsonschema.Draft202012Validator(
                schema, registry=registry, format_checker=_FORMAT_CHECKER
            ).validate(instance)
            errors.append(
                f"[schema regression] {f_rel} was accepted by {wrapper_name} but must be rejected"
            )
        except jsonschema.ValidationError:
            pass  # expected: fixture correctly rejected


def validate_negative_fixtures(errors: list[str]) -> None:
    """Assert that each negative fixture is REJECTED by its schema.

    A fixture that passes validation is a schema regression — reported as an error.
    """
    for schema_path, fixture_path in NEGATIVE_LOCAL_SCHEMAS:
        s_rel = schema_path
        f_rel = fixture_path
        try:
            schema = json.loads((ROOT / schema_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"[schema load error] {s_rel}: {exc}")
            continue
        try:
            fixture = json.loads((ROOT / fixture_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"[fixture load error] {f_rel}: {exc}")
            continue
        try:
            jsonschema.validate(fixture, schema)
            # If we reach here, the fixture was NOT rejected — schema regression
            errors.append(
                f"[schema regression] {f_rel} was accepted by {s_rel} but must be rejected"
            )
        except jsonschema.ValidationError:
            pass  # expected: fixture correctly rejected


def fetch_schema(url: str) -> dict | None:
    """Fetch schema with graceful degradation. Returns None on failure."""
    try:
        resp = requests.get(url, timeout=30, allow_redirects=True)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"WARNING: failed to fetch schema {url}: {e}")
        print("  → falling back to required-field checks only for this URL")
        return None


def main() -> int:
    errors: list[str] = []
    schema_cache: dict[str, dict | None] = {}
    total_checked = 0

    for pattern, schema_url, required in RULES:
        matches = list(ROOT.glob(pattern))
        if not matches:
            continue  # pattern may legitimately match nothing

        for path in sorted(matches):
            rel = path.relative_to(ROOT)

            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                errors.append(f"[invalid JSON] {rel}: {e}")
                continue

            # Schema validation (with graceful degradation)
            if schema_url:
                if schema_url not in schema_cache:
                    schema_cache[schema_url] = fetch_schema(schema_url)
                schema = schema_cache[schema_url]
                if schema is not None:
                    try:
                        jsonschema.validate(data, schema)
                    except jsonschema.ValidationError as e:
                        errors.append(
                            f"[schema violation] {rel}: {e.message}"
                        )
                # else: schema fetch failed, warning already printed

            # Required field validation
            if required:
                for field in required:
                    if field not in data:
                        errors.append(f"[missing field] {rel}: '{field}'")

            total_checked += 1

    total_checked += validate_local_schemas(errors)
    total_checked += validate_profile_positive_examples(errors)
    total_checked += validate_recommendations_positive_examples(errors)
    validate_negative_fixtures(errors)
    validate_profile_negative_examples(errors)
    validate_recommendations_negative_examples(errors)

    if errors:
        print("JSON schema errors:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"OK: {total_checked} JSON file(s) validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
