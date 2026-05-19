---
title: Common Final Phase — Persist Results & Learn
description: "Post-skill OCC merge/write sequence: lock-free merge from an immutable snapshot, short-lock compare-and-commit."
version: 1.2.1
---

## Common Final Phase: Persist Results & Learn

Insert after each skill's existing final phase logic.

**OCC merge/commit** (optimistic concurrency, three short steps):

Between Phase 0 and the Final Phase, another skill run in a parallel shell may have committed canonical state. The Final Phase does NOT blindly overwrite state with the Phase 0 snapshot. It also does NOT hold a lock across merge or render work. Instead it uses optimistic concurrency in three steps. Step A takes an immutable snapshot inside a short lock. Step B then merges lock-free from that snapshot. Step C re-acquires the short lock to compare-and-commit. The lock is held only across the two bounded read/write bursts in Steps A and C — never across LLM work.

**Step A — Snapshot (short lock)**:

1. Acquire the short lock — see `plugin/references/lib/state_io.md` §State-mutation lock.
2. Read all 4 source files into an in-memory snapshot:
   - `snap_profile` ← parse `local/profile.json`
   - `snap_recommendations` ← parse `local/recommendations.json`
   - `snap_changelog` ← read `local/config-changelog.md`
   - `snap_drift_state` ← parse `local/drift-state.json`
3. Capture `commit_obs` ← the uniform source `commit_id` (all 4 source files carry the same `commit_id`; this single value is the optimistic-concurrency observation token).
4. Classify markers per §8: if **all marker files are absent**, this is genesis — defer to Step 0.5 (migration/genesis) and do not proceed with A→B→C here. If the marker set is **partial/mixed** (some present, some absent), this is a torn set — stop per §9 (torn-set recovery); do not merge or write.
5. Release the short lock.

**Step B — Merge & render (NO lock, NO canonical reads)**:

Apply this skill's deltas / merge / render **entirely from the Step A in-memory snapshot**. During Step B you MUST NOT read any of `local/profile.json`, `local/recommendations.json`, `local/config-changelog.md`, `local/drift-state.json`, or `local/state-summary.md` — the canonical files are off-limits for the whole of Step B; the snapshot captured at Step A is the sole input.

1. Apply this skill's deltas as a merge (per-skill merge rules — see the Per-Skill Merge Rules section below) against `snap_profile` / `snap_recommendations` / `snap_changelog` / `snap_drift_state`. Produce `new_profile`, `new_recommendations`, `new_changelog`, `new_drift_state` in memory (non-`/audit` skills set `new_drift_state := snap_drift_state` unchanged — only `/audit` mutates it; see Step C). The same-day duplicate handling of changelog entries (see §Same-Day Duplicate Check) and the compaction check (see §Compaction Algorithm) are applied in memory during this step.
2. Render `new_state_summary` from in-memory `new_profile` + `new_recommendations` + `new_changelog`. Rendering is purely from in-memory state — consistent with the Step B no-canonical-read rule and avoiding any TOCTOU race with Step C's writes.

**Step C — Compare-and-commit (short lock)**:

1. Acquire the short lock.
2. Re-read the 4 source files' `commit_id` → `commit_now`.
3. **If `commit_now != commit_obs`** (a concurrent commit landed during Step B): release the lock and retry **A→B→C only** — re-snapshot, re-merge *this skill's already-computed deltas* against the new snapshot, and re-commit. The skill's primary analysis that precedes the Common Final Phase is NEVER re-run. Bound the retry to **N = 3** attempts; if still conflicting after the 3rd attempt, abort with: `state not persisted due to concurrent activity; re-run.`
4. **If `commit_now == commit_obs`** (no concurrent commit): mint a fresh `commit_id`; atomic-write all 5 files stamped with that `commit_id` (see `plugin/references/lib/state_io.md` §atomic-write) — the 4 source files first in any order, then `state-summary.md` last:
   - `profile.json` ← `new_profile`
   - `recommendations.json` ← `new_recommendations`
   - `config-changelog.md` ← `new_changelog` (whole-file rewrite; DO NOT use `O_APPEND`)
   - `drift-state.json` ← `new_drift_state` (mutated only by `/audit`; non-`/audit` skills re-write the same content carried in `snap_drift_state` to preserve atomic-write group consistency)
   - `state-summary.md` ← `new_state_summary` (written LAST so mtime(state-summary.md) >= max_source_mtime — satisfies the freshness predicate checked in `plugin/references/phase-0.md` §Summary freshness)
5. Release the short lock.

Step 0.5 (migration) performs the equivalent short-lock A→C around its own write burst and is the sole genesis path (§8) — see `plugin/references/phase-0.md` §Step 0.5; it is not duplicated here.

Do NOT write `latest-{skill}.md` — legacy per-skill result files are deprecated; per-skill result info surfaces through `config-changelog.md` entries and `state-summary.md`'s Recent Skill Results section.

---

## Per-Skill Merge Rules (applied lock-free in Step B)

See `plugin/references/lib/merge_rules.md`.

**Inline summaries in skill docs**: each owning skill's SKILL.md (e.g., `plugin/skills/audit/SKILL.md` Phase 5) carries an applied-view summary of its `claude_code_configuration_state.{model, scoring_model_ack}` and `- Model:` bullet behavior. `merge_rules.md` is the mechanism reference; the section below describes the changelog `- Model:` hybrid writer behavior shared across skills.

**Note**: `local/latest-{skill}.md` is deprecated. Skill-specific result info now lives in `config-changelog.md` entries and is surfaced in `state-summary.md`'s Recent Skill Results section. Migration in Step 0.5 moves any legacy `latest-*.md` files to `local/legacy-backup/`.

---
