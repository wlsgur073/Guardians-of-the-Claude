---
title: Common Final Phase — Persist Results & Learn
description: Post-skill merge, write, render sequence under state-mutation lock; per-skill merge rules pointer.
version: 1.1.0
---

## Common Final Phase: Persist Results & Learn

Insert after each skill's existing final phase logic.

**Step 1 — Merge, Write, Render** (concurrency-aware, under state-mutation lock):

The Final Phase does NOT blindly overwrite state with the snapshot read at Phase 0. Between Phase 0 and Final Phase, another skill run in a parallel shell may have modified canonical state. The sequence below protects against serialized lost updates (stale-snapshot overwrite) by re-reading under lock and merging this skill's deltas against current state. The Phase 0 snapshot is NOT the ground truth for write; `current_*` at step 2 is.

1. **Acquire `local/.state.lock`** — See `plugin/references/lib/state_io.md` §state-mutation-lock (Final Phase: wait up to 30s behavior).

2. **Re-read current canonical state under lock**:
   - `current_profile` ← parse `local/profile.json`
   - `current_recommendations` ← parse `local/recommendations.json`
   - `current_changelog` ← read `local/config-changelog.md`
   - `current_drift_state` ← parse `local/drift-state.json`

3. **Apply this skill's deltas as a merge** (per-skill merge rules — see Per-Skill Merge Rules section below). Produce `new_profile`, `new_recommendations`, `new_changelog` in memory. The same-day duplicate handling of changelog entries (see §Same-Day Duplicate Check) and the compaction check (see §Compaction Algorithm) are applied in memory during this step, before the atomic write.

4. **Render `new_state_summary`** from in-memory `new_profile` + `new_recommendations` + `new_changelog`. Do NOT re-read files from disk after step 2; rendering from in-memory state avoids TOCTOU races with step 5's writes.

5. **Atomic write all canonical files** (see `plugin/references/lib/state_io.md` §atomic-write):
   - **Source files** (relative order within this group does not matter; all four must be written before state-summary.md):
     - `profile.json` ← `new_profile`
     - `recommendations.json` ← `new_recommendations`
     - `config-changelog.md` ← `new_changelog` (whole-file rewrite; DO NOT use `O_APPEND`)
     - `drift-state.json` ← `new_drift_state` (mutated only by `/audit` Final Phase; non-`/audit` skills re-write the same content read as `current_drift_state` at Step 2 to preserve atomic-write group consistency)
   - **Derived view (LAST in the batch)**:
     - `state-summary.md` ← `new_state_summary` (written last so mtime(state-summary.md) >= max_source_mtime — satisfies the freshness predicate checked in plugin/references/phase-0.md §Step 0.5 phase 6)

6. **Release `local/.state.lock`** — See `plugin/references/lib/state_io.md` §state-mutation-lock (release via `os.unlink`).

Do NOT write `latest-{skill}.md` — legacy per-skill result files are deprecated; per-skill result info surfaces through `config-changelog.md` entries and `state-summary.md`'s Recent Skill Results section.

---

## Per-Skill Merge Rules (Final Phase under state-mutation lock)

See `plugin/references/lib/merge_rules.md`.

**Inline summaries in skill docs**: each owning skill's SKILL.md (e.g., `plugin/skills/audit/SKILL.md` Phase 5) carries an applied-view summary of its `claude_code_configuration_state.{model, scoring_model_ack}` and `- Model:` bullet behavior. `merge_rules.md` is the mechanism reference; the section below describes the changelog `- Model:` hybrid writer behavior shared across skills.

**Note**: `local/latest-{skill}.md` is deprecated. Skill-specific result info now lives in `config-changelog.md` entries and is surfaced in `state-summary.md`'s Recent Skill Results section. Migration in Step 0.5 moves any legacy `latest-*.md` files to `local/legacy-backup/`.

---
