---
title: Learning Rules — CSA Pattern
description: Context/Signal/Action rules for recommendation lifecycle (R1 Recommendation Follow-up, R2 Preference Respect, R3 Stagnation Detection, R4 Profile Drift Response).
version: 1.0.0
---

## Learning Rules (CSA Pattern)

Rule 1 — Recommendation Follow-up

- Context: PENDING entries in `recommendations.json` plus any matching unresolved entries in `config-changelog.md`'s Recent Activity.
- Signal: PENDING status in `recommendations.json` and the most recent entry for the corresponding `resolvers[]` skill in `config-changelog.md` does not mark it RESOLVED.
- Action: Re-state with `(Nx pending)` count where N = previous count + 1. Count increments across all skills (not just the current skill). Explain what remains unaddressed.

Rule 2 — Preference Respect

- Context: DECLINED entries in `recommendations.json` + `local/profile.json`.
- Signal: `status == "DECLINED"` in `recommendations.json`, or DECLINED annotation in any skill's `config-changelog.md` entry (cross-skill scope).
- Action: Do NOT re-suggest unless project scale/structure changed significantly. If re-suggesting, acknowledge the previous decline.

Rule 3 — Stagnation Detection

- Context: Last 3+ entries in changelog (any skill, not audit-only). Cross-check `recommendations.json` for current PENDING statuses.
- Signal: Same PENDING recommendation appears in 3+ entries consecutively (non-audit entries that don't mention the item do not break the chain). OR `Applied: (none)` in 3 consecutive entries.
- Action: Ask user to (a) apply now, (b) mark declined, (c) defer. If user defers, increment PENDING count per Rule 1. No response after prompt → STALE on next compaction.
- STALE application: During compaction (Step 3b), if an item is PENDING with count N≥3 and no apply/decline/defer action was recorded in any entry since the count reached 3, mark it STALE in the compacted summary. The (Nx) count itself is sufficient evidence — no intermediate status tracking is needed.

Rule 4 — Profile Drift Response

- Context: `local/profile.json` vs current manifests.
- Signal: Spot-check mismatch (lock file type or framework major version).
- Action: Update mismatched section immediately. Re-evaluate related recommendations. Note drift in changelog.

---
