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


def load_registry_rows(path: Path = REGISTRY_PATH) -> list[dict]:
    """Returns the raw registry array (one dict per recommendation key).

    Unlike load_registry() — which maps every key AND alias to its row, so iterating its
    values double-counts aliased rows — this returns each row exactly once, which is what
    the registry-definition lint below needs.
    """
    return json.loads(path.read_text(encoding="utf-8"))["registry"]


# Phase-0 recommendation load filters: the set of `issued_by` values each skill loads
# when it reads recommendations.json. Mirror of plugin/references/phase-0.md Step 2
# ("/secure: issued_by == audit"; "/optimize: audit or secure"; "/create: issued_by in
# [secure, optimize]"; "/audit: all"). Keep in sync with that file. A resolver whose
# accepted set shares no issuer with a key it resolves can never load that key.
SKILL_LOAD_FILTERS: dict[str, set[str]] = {
    "audit": {"audit", "secure", "optimize", "create"},  # /audit loads ALL recommendations
    "secure": {"audit"},
    "optimize": {"audit", "secure"},
    "create": {"secure", "optimize"},
}


def check_registry_resolver_liveness(rows: list[dict]) -> list[str]:
    """Forward-direction registry lint: every declared resolver must be able to LOAD
    the key it resolves.

    A resolver R can resolve key K only if R's Phase-0 load filter (SKILL_LOAD_FILTERS)
    accepts at least one of K's `issuers`. If the intersection is empty, R never sees K,
    so it can never set resolved_by=R — a dead pointer. The instance-level lints in
    check_recommendations() only validate the REVERSE direction (a persisted resolved_by
    must be a registered resolver), so they cannot catch a registered-but-unloadable
    resolver. This closes that gap.

    Args:
        rows: the raw registry array (each row has "key", "issuers", "resolvers").
    Returns:
        Human-readable failure messages; empty list == every resolver is loadable.
    """
    failures: list[str] = []
    for row in rows:
        key = row["key"]
        issuers = set(row.get("issuers", []))
        for resolver in row.get("resolvers", []):
            accepted = SKILL_LOAD_FILTERS.get(resolver)
            if accepted is None:
                failures.append(
                    f"key '{key}' lists resolver '{resolver}', which is not a known "
                    f"Phase-0 skill {sorted(SKILL_LOAD_FILTERS)}"
                )
            # "Dead" = the resolver can load NONE of this key's issuers (existential test).
            # A multi-issuer key whose resolver loads only SOME of its issuers still resolves
            # those instances, so it is intentionally not flagged; revisit if multi-issuer
            # keys are ever introduced and stricter (universal) coverage is wanted.
            elif issuers.isdisjoint(accepted):
                failures.append(
                    f"key '{key}' resolver '{resolver}' can never load it: "
                    f"'{resolver}' loads issued_by in {sorted(accepted)}, "
                    f"but key issuers are {sorted(issuers)}"
                )
    return failures


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
            if resolved is None:
                failures.append(
                    f"id '{rid}' status RESOLVED requires non-null resolved_by "
                    f"(found null); registry resolvers: {row['resolvers']}"
                )
            elif resolved not in row["resolvers"]:
                failures.append(
                    f"id '{rid}' resolved_by '{resolved}' "
                    f"not in registry resolvers {row['resolvers']}"
                )
    return failures
