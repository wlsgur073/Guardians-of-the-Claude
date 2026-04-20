#!/usr/bin/env python3
"""T7 C1 fixture runner — /optimize end-to-end (first exerciser of handle_optimize).

Exercises handle_optimize Final Phase end-to-end: profile merge (counts for
changed entity classes only), recommendation resolution, changelog entry,
state-summary render. Phase 2a is the first to exercise /optimize end-to-end
per design §1.2 C1.

Fixture: ci/fixtures/t7-optimize-e2e/
  input/local/ — post-/audit state with PENDING split-rules + agent-diversity
  expected/local/ — post-/optimize state (rules_count+1=3, agents_count+2=2,
                    hooks+mcp unchanged; six project-structure sections untouched)

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

FIXTURE_DIR = ROOT / "ci" / "fixtures" / "t7-optimize-e2e"
INPUT_DIR = FIXTURE_DIR / "input"
EXPECTED_DIR = FIXTURE_DIR / "expected"

# run_fixture reads SMOKE_PINNED_UTC from os.environ directly; ensure it is set.
_DEFAULT_PINNED_UTC = "2026-04-14T00:00:00Z"
PINNED_UTC = os.environ.setdefault("SMOKE_PINNED_UTC", _DEFAULT_PINNED_UTC)


def handle_optimize_e2e(ctx: csf.RunContext, state: csf.WorkspaceState) -> csf.WorkspaceState:
    """Handle /optimize end-to-end for t7-optimize-e2e fixture.

    /optimize splits CLAUDE.md into rule files (+1 rule) and configures 2 agents.
    Exercises counts co-ownership: rules_count+1, agents_count+2; hooks and mcp
    unchanged. Six project-structure sections (runtime_and_language through
    project_structure) are NOT modified per merge_rules.md §profile.json."""
    date = ctx.pinned_utc.split("T")[0]

    # /optimize only updates CCS counts for changed entity classes;
    # does NOT touch the six project-structure sections.
    profile_delta = {
        "metadata": {
            "last_updated": ctx.pinned_utc,
            "source_files_checked": [
                ".claude/rules/coding.md",
                ".claude/agents/review.md",
                ".claude/agents/test.md",
            ],
        },
        "claude_code_configuration_state": {
            "rules_count": 3,
            "agents_count": 2,
            "hooks_count": 2,
            "mcp_servers_count": 0,
        },
    }
    state.profile = csf.merge_profile(state.profile, profile_delta, "optimize")

    rec_delta = [
        {
            "id": "split-rules",
            "description": "Split CLAUDE.md into rule files",
            "issued_by": "audit",
            "status": "RESOLVED",
            "pending_count": 1,
            "first_seen": "2026-04-14T00:00:00Z",
            "last_seen": "2026-04-14T00:00:00Z",
            "resolved_by": "optimize",
            "declined_reason": None,
        },
        {
            "id": "agent-diversity",
            "description": "Diversify agent models",
            "issued_by": "audit",
            "status": "RESOLVED",
            "pending_count": 1,
            "first_seen": "2026-04-14T00:00:00Z",
            "last_seen": "2026-04-14T00:00:00Z",
            "resolved_by": "optimize",
            "declined_reason": None,
        },
    ]
    state.recommendations = csf.merge_recommendations(
        state.recommendations, rec_delta, ctx.pinned_utc
    )

    entry = (
        f"### {date} — /optimize\n"
        f"- Detected: CLAUDE.md monolithic, no agents\n"
        f"- Profile updated: rules_count, agents_count\n"
        f"- Applied: CLAUDE.md split into rule files, 2 agents configured\n"
        f"- Resolved: split-rules — RESOLVED, agent-diversity — RESOLVED\n"
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

    original_optimize = csf.SKILL_HANDLERS["optimize"]
    csf.SKILL_HANDLERS["optimize"] = handle_optimize_e2e
    try:
        scenario = {
            "skill_sequence": ["optimize"],
            "pre_run": [],
        }
        passed, msg = csf.run_fixture(
            name="t7-optimize-e2e",
            src_dir=INPUT_DIR,
            golden_dir=EXPECTED_DIR,
            scenario=scenario,
        )
    finally:
        csf.SKILL_HANDLERS["optimize"] = original_optimize

    tag = "PASS" if passed else "FAIL"
    print(f"[{tag}] t7-optimize-e2e: {msg}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
