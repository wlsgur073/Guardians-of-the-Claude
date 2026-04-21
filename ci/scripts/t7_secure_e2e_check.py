#!/usr/bin/env python3
"""/secure end-to-end fixture runner.

Exercises handle_secure Final Phase end-to-end: profile merge (settings_json +
counts), recommendation resolution, changelog entry, state-summary render.

Fixture: ci/fixtures/t7-secure-e2e/
  input/local/ — post-/audit state with PENDING add-deny-patterns recommendation
  expected/local/ — post-/secure state (settings_json created, rules_count=1,
                    hooks_count=1, recommendation RESOLVED)

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

FIXTURE_DIR = ROOT / "ci" / "fixtures" / "t7-secure-e2e"
INPUT_DIR = FIXTURE_DIR / "input"
EXPECTED_DIR = FIXTURE_DIR / "expected"

# run_fixture reads SMOKE_PINNED_UTC from os.environ directly; ensure it is set.
_DEFAULT_PINNED_UTC = "2026-04-14T00:00:00Z"
PINNED_UTC = os.environ.setdefault("SMOKE_PINNED_UTC", _DEFAULT_PINNED_UTC)


def handle_secure_e2e(ctx: csf.RunContext, state: csf.WorkspaceState) -> csf.WorkspaceState:
    """Handle /secure end-to-end for t7-secure-e2e fixture.

    /secure creates settings.json with deny patterns, creates a security rule
    file, and adds a file-protection hook. Resolves the add-deny-patterns
    recommendation from /audit."""
    date = ctx.pinned_utc.split("T")[0]

    profile_delta = {
        "metadata": {
            "last_updated": ctx.pinned_utc,
            "source_files_checked": [".claude/settings.json", ".claude/rules/security.md"],
        },
        "claude_code_configuration_state": {
            "settings_json": {"exists": True, "has_permissions": True},
            "rules_count": 1,
            "agents_count": 0,
            "hooks_count": 1,
            "mcp_servers_count": 0,
        },
    }
    state.profile = csf.merge_profile(state.profile, profile_delta, "secure")

    rec_delta = [
        {
            "id": "deny-env",
            "description": "Add deny patterns for .env / credential files",
            "issued_by": "audit",
            "status": "RESOLVED",
            "pending_count": 1,
            "first_seen": "2026-04-14T00:00:00Z",
            "last_seen": "2026-04-14T00:00:00Z",
            "resolved_by": "secure",
            "declined_reason": None,
        }
    ]
    state.recommendations = csf.merge_recommendations(
        state.recommendations, rec_delta, ctx.pinned_utc
    )

    entry = (
        f"### {date} — /secure\n"
        f"- Detected: settings.json missing, 1 deny pattern gap\n"
        f"- Profile updated: settings_json, rules_count, hooks_count\n"
        f"- Applied: settings.json created with deny patterns, security rule file created, file-protection hook added\n"
        f"- Resolved: deny-env — RESOLVED\n"
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

    original_secure = csf.SKILL_HANDLERS["secure"]
    csf.SKILL_HANDLERS["secure"] = handle_secure_e2e
    try:
        scenario = {
            "skill_sequence": ["secure"],
            "pre_run": [],
        }
        passed, msg = csf.run_fixture(
            name="t7-secure-e2e",
            src_dir=INPUT_DIR,
            golden_dir=EXPECTED_DIR,
            scenario=scenario,
        )
    finally:
        csf.SKILL_HANDLERS["secure"] = original_secure

    tag = "PASS" if passed else "FAIL"
    print(f"[{tag}] t7-secure-e2e: {msg}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
