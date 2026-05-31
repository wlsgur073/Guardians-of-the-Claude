#!/usr/bin/env python3
"""Usage/fitness recommendation lifecycle end-to-end fixture runner.

Proves the new usage/fitness recommendation key cycle end-to-end through the
deterministic STATE-mutation layer (no markdown skill execution): /audit emits
a PENDING `mcp-unused` recommendation, then /optimize transitions it to
RESOLVED. Exercises merge_recommendations (insert then status transition),
merge_profile (audit regenerates profile + counts; optimize co-owns counts and
drops the now-unused MCP server count to 0), changelog entries for both skills,
and the state-summary render.

Fixture: ci/fixtures/t8-usage-recs-e2e/
  input/local/    — starting state: valid profile (1 MCP server),
                    empty recommendations, empty changelog
  expected/local/ — after [audit, optimize]: mcp-unused RESOLVED,
                    mcp_servers_count 1 -> 0, two changelog entries

Exit codes:
    0 — fixture PASS (byte-exact match against expected/)
    1 — fixture FAIL (semantic assertion or byte diff mismatch)
    2 — setup error (missing file or import failure)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / ".github" / "scripts"))

try:
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location(
        "check_smoke_fixtures",
        ROOT / ".github" / "scripts" / "check-smoke-fixtures.py",
    )
    csf = _ilu.module_from_spec(_spec)
    sys.modules["check_smoke_fixtures"] = csf
    _spec.loader.exec_module(csf)
except Exception as exc:
    print(f"[FATAL] cannot import check-smoke-fixtures.py: {exc}", file=sys.stderr)
    sys.exit(2)

FIXTURE_DIR = ROOT / "ci" / "fixtures" / "t8-usage-recs-e2e"
INPUT_DIR = FIXTURE_DIR / "input"
EXPECTED_DIR = FIXTURE_DIR / "expected"

# run_fixture reads SMOKE_PINNED_UTC from os.environ directly; ensure it is set.
_DEFAULT_PINNED_UTC = "2026-04-14T00:00:00Z"
PINNED_UTC = os.environ.setdefault("SMOKE_PINNED_UTC", _DEFAULT_PINNED_UTC)


def handle_audit_e2e(ctx: csf.RunContext, state: csf.WorkspaceState) -> csf.WorkspaceState:
    """Reference /audit Final Phase for t8-usage-recs-e2e.

    /audit analyzes local usage and finds an MCP server with no invocations
    over the analyzed window. It regenerates the project profile (audit-owned
    sections + counts) and emits a PENDING `mcp-unused` recommendation that
    /optimize can later resolve. The MCP server count is unchanged at this
    stage (detection only — /optimize applies the fix)."""
    date = ctx.pinned_utc.split("T")[0]

    profile_delta = {
        "metadata": {
            "last_updated": ctx.pinned_utc,
            "source_files_checked": ["package.json", "tsconfig.json"],
        },
        "runtime_and_language": {
            "runtime": "Node.js 22.x",
            "language": "TypeScript 5.7",
            "module_system": "ESM",
        },
        "framework_and_libraries": {
            "framework": "Next.js 15 (App Router)",
            "ui": "React 19",
            "styling": "Tailwind CSS v4",
        },
        "package_management": {
            "manager": "pnpm",
            "lock_file": "pnpm-lock.yaml",
        },
        "testing": {
            "unit": "Vitest",
            "e2e": "Playwright",
        },
        "build_and_dev": {
            "bundler": "Turbopack",
            "linter": "ESLint 9 (flat config)",
            "formatter": "Prettier",
        },
        "project_structure": {
            "type": "single_project",
            "source_convention": "src/",
            "key_directories": ["src/app/", "src/components/", "src/lib/"],
        },
        "claude_code_configuration_state": {
            "claude_md": {"exists": True, "section_count": 5},
            "settings_json": {"exists": True, "has_permissions": True},
            "rules_count": 2,
            "agents_count": 1,
            "hooks_count": 2,
            "mcp_servers_count": 1,
        },
    }
    state.profile = csf.merge_profile(state.profile, profile_delta, "audit")

    rec_delta = [
        {
            "id": "mcp-unused",
            "description": "Disable an MCP server with no invocations over the analyzed window",
            "issued_by": "audit",
            "status": "PENDING",
            "pending_count": 1,
            "first_seen": ctx.pinned_utc,
            "last_seen": ctx.pinned_utc,
            "resolved_by": None,
            "declined_reason": None,
        },
    ]
    state.recommendations = csf.merge_recommendations(
        state.recommendations, rec_delta, ctx.pinned_utc
    )

    entry = (
        f"### {date} — /audit\n"
        f"- Detected: 1 MCP server with no invocations over the analyzed window\n"
        f"- Profile updated: generated\n"
        f"- Applied: (none)\n"
        f"- Resolved: (none)\n"
        f"- Recommendations:\n"
        f"  - Disable an MCP server with no invocations over the analyzed window — PENDING"
    )
    state.changelog = csf._changelog_with_entry(state.changelog, entry)

    csf._final_phase_write(ctx, state)
    return state


def handle_optimize_e2e(ctx: csf.RunContext, state: csf.WorkspaceState) -> csf.WorkspaceState:
    """Reference /optimize Final Phase for t8-usage-recs-e2e.

    /optimize disables the unused MCP server, dropping mcp_servers_count from
    1 to 0 (it co-owns counts per merge_rules.md §profile.json), and transitions
    the `mcp-unused` recommendation to RESOLVED. Other counts and the six
    project-structure sections are untouched."""
    date = ctx.pinned_utc.split("T")[0]

    profile_delta = {
        "metadata": {
            "last_updated": ctx.pinned_utc,
            "source_files_checked": [".claude/settings.json"],
        },
        "claude_code_configuration_state": {
            "rules_count": 2,
            "agents_count": 1,
            "hooks_count": 2,
            "mcp_servers_count": 0,
        },
    }
    state.profile = csf.merge_profile(state.profile, profile_delta, "optimize")

    rec_delta = [
        {
            "id": "mcp-unused",
            "status": "RESOLVED",
            "last_seen": ctx.pinned_utc,
            "resolved_by": "optimize",
        },
    ]
    state.recommendations = csf.merge_recommendations(
        state.recommendations, rec_delta, ctx.pinned_utc
    )

    entry = (
        f"### {date} — /optimize\n"
        f"- Detected: 1 unused MCP server\n"
        f"- Profile updated: mcp_servers_count\n"
        f"- Applied: disabled unused MCP server\n"
        f"- Resolved: mcp-unused — RESOLVED\n"
        f"- Recommendations: (none)"
    )
    state.changelog = csf._changelog_with_entry(state.changelog, entry)

    csf._final_phase_write(ctx, state)
    return state


def main() -> int:
    if not INPUT_DIR.exists():
        print(f"[FATAL] input dir missing: {INPUT_DIR}", file=sys.stderr)
        return 2
    if not EXPECTED_DIR.exists():
        print(f"[FATAL] expected dir missing: {EXPECTED_DIR}", file=sys.stderr)
        return 2

    original_audit = csf.SKILL_HANDLERS["audit"]
    original_optimize = csf.SKILL_HANDLERS["optimize"]
    csf.SKILL_HANDLERS["audit"] = handle_audit_e2e
    csf.SKILL_HANDLERS["optimize"] = handle_optimize_e2e
    try:
        scenario = {
            "skill_sequence": ["audit", "optimize"],
            "pre_run": [],
        }
        passed, msg = csf.run_fixture(
            name="t8-usage-recs-e2e",
            src_dir=INPUT_DIR,
            golden_dir=EXPECTED_DIR,
            scenario=scenario,
        )
    finally:
        csf.SKILL_HANDLERS["audit"] = original_audit
        csf.SKILL_HANDLERS["optimize"] = original_optimize

    tag = "PASS" if passed else "FAIL"
    print(f"[{tag}] t8-usage-recs-e2e: {msg}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
