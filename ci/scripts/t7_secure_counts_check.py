#!/usr/bin/env python3
"""T7 C2 fixture runner — /secure counts co-ownership.

Exercises the merge_profile /secure branch's counts update (rules_count,
agents_count, hooks_count, mcp_servers_count) added in Phase 2a T7 C2.
Before T7 implementation: these counts were NOT updated by the /secure branch.
After T7 C2: merge_profile propagates counts from /secure delta.

Fixture: ci/fixtures/t7-secure-counts/
  input/local/ — baseline post-/audit state (rules_count=5, hooks_count=3)
  expected/local/ — post-/secure state (rules_count=7, hooks_count=4,
                    settings_json updated, agents+mcp unchanged)

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
    print("Run from repo root: python ci/scripts/t7_secure_counts_check.py", file=sys.stderr)
    sys.exit(2)

FIXTURE_DIR = ROOT / "ci" / "fixtures" / "t7-secure-counts"
INPUT_DIR = FIXTURE_DIR / "input"
EXPECTED_DIR = FIXTURE_DIR / "expected"

# run_fixture reads SMOKE_PINNED_UTC from os.environ directly; ensure it is set.
_DEFAULT_PINNED_UTC = "2026-04-14T00:00:00Z"
PINNED_UTC = os.environ.setdefault("SMOKE_PINNED_UTC", _DEFAULT_PINNED_UTC)


def handle_secure_counts(ctx: csf.RunContext, state: csf.WorkspaceState) -> csf.WorkspaceState:
    """Handle /secure with rule and hook additions for t7-secure-counts fixture.

    /secure adds 2 deny-pattern rules and 1 protection hook, and updates
    settings_json. Exercises the C2 counts co-ownership path in merge_profile."""
    date = ctx.pinned_utc.split("T")[0]

    profile_delta = {
        "metadata": {
            "last_updated": ctx.pinned_utc,
            "source_files_checked": [".claude/settings.json"],
        },
        "claude_code_configuration_state": {
            "settings_json": {"exists": True, "has_permissions": True},
            "rules_count": 7,
            "agents_count": 0,
            "hooks_count": 4,
            "mcp_servers_count": 0,
        },
    }
    state.profile = csf.merge_profile(state.profile, profile_delta, "secure")
    state.recommendations = csf.merge_recommendations(
        state.recommendations, [], ctx.pinned_utc
    )

    entry = (
        f"### {date} — /secure\n"
        f"- Detected: 2 deny patterns missing, 1 hook gap\n"
        f"- Profile updated: settings_json, rules_count, hooks_count\n"
        f"- Applied: 2 deny patterns added, 1 file-protection hook added\n"
        f"- Resolved: (none)\n"
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

    # Patch SKILL_HANDLERS for this fixture
    original_secure = csf.SKILL_HANDLERS["secure"]
    csf.SKILL_HANDLERS["secure"] = handle_secure_counts
    try:
        scenario = {
            "skill_sequence": ["secure"],
            "pre_run": [],
        }
        passed, msg = csf.run_fixture(
            name="t7-secure-counts",
            src_dir=INPUT_DIR,
            golden_dir=EXPECTED_DIR,
            scenario=scenario,
        )
    finally:
        csf.SKILL_HANDLERS["secure"] = original_secure

    tag = "PASS" if passed else "FAIL"
    print(f"[{tag}] t7-secure-counts: {msg}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
