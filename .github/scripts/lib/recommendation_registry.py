"""Shared library for recommendation registry validation.
Consumed by check-recommendation-registry.py (CLI) and check-smoke-fixtures.py (smoke verifier)."""
from __future__ import annotations

import json
from pathlib import Path

REGISTRY_PATH = Path("plugin/references/recommendation-registry.json")


def load_registry(path: Path = REGISTRY_PATH) -> dict:
    """Returns {key_or_alias: registry_row}. Each row referenced by canonical key and every alias."""
    data = json.loads(path.read_text(encoding="utf-8"))
    by_key = {}
    for row in data["registry"]:
        by_key[row["key"]] = row
        for alias in row.get("aliases", []):
            by_key[alias] = row
    return by_key


def check_recommendations(instances: list[dict], registry_by_key: dict) -> list[str]:
    """Lints 1+2+3 on recommendation instances. Returns list of failure messages.

    Fail-loud contract: raises KeyError if an instance is missing required fields
    (`id`, `issued_by`). Malformed instances are a CI data error and should surface
    as a traceback, not a silently-collected failure string.

    Lint ordering note: Lint 3 (alias-as-id) is checked before Lint 2 (issuer/resolver
    authorization) so that both fire independently when an instance uses an alias AND
    an unauthorized issuer. Do not short-circuit with `continue` between them.
    """
    failures = []
    for inst in instances:
        rid = inst["id"]
        # Lint 1: id exists in registry (as key or alias)
        if rid not in registry_by_key:
            failures.append(f"unknown id '{rid}' (not a registry key or alias)")
            continue
        row = registry_by_key[rid]
        # Lint 3: aliases are input-only — persisted ids MUST be canonical keys
        if rid != row["key"]:
            failures.append(
                f"id '{rid}' is an alias of canonical key '{row['key']}'; "
                f"aliases must never be persisted forward (they are input-only)"
            )
        # Lint 2: issuer authorization (independent of Lint 3; both may fire)
        if inst["issued_by"] not in row["issuers"]:
            failures.append(
                f"id '{rid}' issued_by '{inst['issued_by']}' "
                f"not in registry issuers {row['issuers']}"
            )
        # Lint 2 cont: resolver authorization
        if inst.get("status") == "RESOLVED":
            resolved = inst.get("resolved_by")
            if resolved not in row["resolvers"]:
                failures.append(
                    f"id '{rid}' resolved_by '{resolved}' "
                    f"not in registry resolvers {row['resolvers']}"
                )
    return failures
