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

import json
import sys
from pathlib import Path

import jsonschema
import requests

ROOT = Path(__file__).resolve().parent.parent.parent

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


# Local schema validation: (schema_path, example_path) relative to ROOT
LOCAL_SCHEMAS: list[tuple[str, str]] = [
    (
        "plugin/references/schemas/profile.schema.json",
        "plugin/references/schemas/examples/profile.example.json",
    ),
    (
        "plugin/references/schemas/recommendations.schema.json",
        "plugin/references/schemas/examples/recommendations.example.json",
    ),
    (
        "plugin/references/recommendation-registry.schema.json",
        "plugin/references/recommendation-registry.json",
    ),
]

# Negative fixtures: (schema_path, negative_example_path) — each MUST be rejected
NEGATIVE_LOCAL_SCHEMAS: list[tuple[str, str]] = [
    (
        "plugin/references/schemas/profile.schema.json",
        "plugin/references/schemas/examples/negative/profile.missing-required.example.json",
    ),
    (
        "plugin/references/schemas/profile.schema.json",
        "plugin/references/schemas/examples/negative/profile.wrong-version.example.json",
    ),
    (
        "plugin/references/schemas/recommendations.schema.json",
        "plugin/references/schemas/examples/negative/recommendations.invalid-id-format.example.json",
    ),
    (
        "plugin/references/schemas/recommendations.schema.json",
        "plugin/references/schemas/examples/negative/recommendations.resolved-without-by.example.json",
    ),
]


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
    validate_negative_fixtures(errors)

    if errors:
        print("JSON schema errors:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"OK: {total_checked} JSON file(s) validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
