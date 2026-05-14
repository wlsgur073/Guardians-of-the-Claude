---
title: Common Phase 0 — Load Context & Learn
description: Pre-skill state read sequence; 8-phase migration & stale check; learning rule application; migration notice template.
version: 1.0.0
---

## Common Phase 0: Load Context & Learn

Insert before each skill's existing Phase 0 logic.

**Step 0 — Directory Check**: Check if `local/` exists. If not, this is cold start — skip Steps 1-3, proceed to skill's own Phase 0. Final Phase creates the directory.

**Step 0.5 — Migration & Stale Check** (8-phase clean version)

> **Precondition**: If `local/` is not writable (privacy-sensitive projects, read-only mounts, or user-disabled), skip the entire Step 0.5 and run the skill in **stateless mode** — print one-time warning ("local/ not writable; stateless run — learning disabled") and continue to the skill's own Phase 0 without reading or writing state.

The state machine has 5 axes:
- `profile.json`: absent | present-valid | present-corrupt
- `recommendations.json`: absent | present-valid | present-corrupt
- legacy MD inputs (`project-profile.md` / `latest-*.md`): absent | present
- `state-summary.md`: absent | present-stale | present-fresh | present-tampered
- `config-changelog.md`: absent | present

Every transition below is explicit. Implicit behavior is forbidden.

1. **Acquire state-mutation lock** — See `plugin/references/lib/state_io.md` §state-mutation-lock. Step 0.5 uses the abort-immediately behavior on contention (< 60s); Final Phase uses the wait-up-to-30s behavior.

2. **Classify canonical files** (per file: absent | present-valid | present-corrupt):
   - For each of `profile.json`, `recommendations.json`: if absent, mark absent. If present, attempt JSON parse + schema validate. Mark present-valid or present-corrupt.
   - Corrupt is treated separately from absent for recovery routing.

3. **Routing decision** (based on phase 2 classification):
   - All canonical present-valid → skip phases 4–5, jump to phase 6.
   - Any canonical absent or present-corrupt → phase 4 (recovery).

4. **Recover from legacy** (per-file, never "nuke both"):
   - For each missing-or-corrupt canonical file, attempt recovery from legacy MD if present:
     - `profile.json` ← parse `project-profile.md` (fields not found → `null`)
     - `recommendations.json` ← parse `latest-{skill}.md` Recommendations sections; **resolve legacy ids through registry aliases to canonical keys** (alias is input-only, NEVER persist alias forward)
   - If parse succeeds → write canonical file via atomic write (see `plugin/references/lib/state_io.md` §atomic-write); preserve other valid canonicals untouched.
   - If parse fails OR no legacy source available → initialize empty: `profile.json = {schema_version, metadata}` only; `recommendations.json = {schema_version, metadata, recommendations: []}`. Atomic write (same spec).
   - Move ANY corrupt canonical to backup (phase 5) before overwriting (data preservation).
   - **Model field write path**: when emitting `profile.json` here, include `claude_code_configuration_state.model = <resolver output>` as a non-null string per the schema. This Step 0.5 write path applies to every skill's emission — migration, fresh bootstrap, post-validation re-write — with no new sub-phase and no `/audit`-specific branching. In stateless mode, this write is a no-op.

5. **Quarantine ALL examined legacy inputs** (success AND failure):
   - Backup path: `local/legacy-backup/{ISO-8601-UTC, e.g., 2026-04-14T13-42-09Z}/`.
   - If that path exists (re-migration in same second), append `-2`, `-3`, ... suffix.
   - Move every legacy MD file examined in phase 2 into the backup directory, regardless of recovery outcome.
   - Move corrupt canonical files (identified in phase 4) into the same backup directory **before** phase 4 overwrites them — the move must happen first.
   - **Single-source cutover**: legacy MD must NEVER coexist with valid canonical JSON in `local/` after Step 0.5.

6. **Regenerate or validate `state-summary.md`**:
   - Compute `max_source_mtime = max(mtime(profile.json), mtime(recommendations.json), mtime(config-changelog.md if present))`.
   - If `state-summary.md` is absent OR `mtime(state-summary.md) < max_source_mtime` → **stale**: invoke renderer; write result via atomic write (see `plugin/references/lib/state_io.md` §atomic-write). Print "state-summary.md was stale. Regenerated from current JSON state."
   - If `mtime(state-summary.md) > max_source_mtime` → **tampered**: print "state-summary.md is newer than all sources — manual edit detected. It will be overwritten at Final Phase. Edits to derived view are not preserved." Do NOT treat tampered file as a source of truth.
   - If equal: treat as fresh, no action.

7. **Print migration notice** (only if phase 4 actually ran a recovery): see `learning-system.md` §Migration Notice. Include the backup path used in phase 5.

8. **Release lock** — See `plugin/references/lib/state_io.md` §state-mutation-lock (release via `os.unlink`). Continue to Step 1 normally.

**Scenario matrix** (every combination explicit):

| profile.json | recs.json | legacy MD | summary | Behavior |
|---|---|---|---|---|
| absent | absent | absent | absent | Fresh first run. Init empty canonicals (phase 4 fallback). Renderer creates summary at Final Phase. |
| absent | absent | absent | present | Ghost summary. Quarantine summary to legacy-backup, init empty canonicals. |
| absent | absent | present | * | Migration: parse legacy → canonicals (phase 4); summary regenerated (phase 6). |
| absent | present-valid | absent | * | Partial canonical: init empty profile.json, preserve recommendations.json (phase 4 per-file). |
| absent | present-corrupt | * | * | Same + corrupt recommendations.json moved to backup, init empty (phase 4). |
| present-valid | absent | absent | * | Partial canonical: init empty recommendations.json, preserve profile.json. |
| present-valid | present-valid | absent | absent | Cache miss: regenerate summary immediately (phase 6 stale path). |
| present-valid | present-valid | absent | present-stale | Phase 6 stale path: regenerate. |
| present-valid | present-valid | absent | present-tampered | Phase 6 tampered path: warn, will overwrite at Final Phase. |
| present-valid | present-valid | absent | present-fresh | No-op (phases 4–5 skipped, phase 6 no-op). |
| present-valid | present-valid | present | * | Single-source violation: quarantine legacy MD (phase 5) regardless of summary state, then phase 6. |
| present-corrupt | * | * | * | Phase 4 per-file recovery for profile.json (legacy if available, else empty); other axes evaluated independently. |

*`*` in a cell means the row applies regardless of that axis — the behavior delegates to the corresponding phase (e.g., `summary = *` defers to phase 6's mtime-based stale/tampered/fresh resolution; `legacy MD = *` defers to phase 4's per-file recovery logic).*

After Step 0.5, proceed to Step 1 normally.

**Step 1 — Load Profile & Spot-Check**: Read `local/profile.json`. If found, use as project context. Then read the project's primary manifest (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, or `pom.xml` — whichever exists) and cross-check two high-impact items:

1. Does the lock file on disk match the profile's Package Management section? (Detects package manager switches.)
2. Does the primary framework's major version match the profile's Framework & Libraries section? (Detects framework upgrades.)
If either mismatches, apply Rule 4 (Profile Drift Response) immediately before proceeding.
If profile not found, note it will be generated in Final Phase and skip spot-check.

**Step 2 — Load Previous Results**: Read `local/recommendations.json`. Cross-skill overrides:

- `/secure`: filter for recommendations where `issued_by == "audit"` and `status == "PENDING"`.
- `/optimize`: same, plus filter for `issued_by == "secure"`.
- `/create`: filter for `issued_by in ["secure", "optimize"]` to avoid overwriting other skills' work.
- `/audit`: all recommendations.

**Step 3 — Load Changelog & Apply Learning Rules**: Read `local/config-changelog.md`. `/audit` reads full file; other skills read Recent Activity only. If found, apply Learning Rules below. Then proceed to skill's own Phase 0.

---

## Migration Notice (printed once after legacy→JSON conversion)

> ℹ️ Legacy state files converted to JSON.
> - `project-profile.md` + `latest-*.md` → `profile.json` + `recommendations.json`
> - Human-readable summary: `local/state-summary.md` (read-only, auto-regenerated)
> - Originals preserved under `local/legacy-backup/{ISO-8601-UTC}/`

Fallback variant when partial parse failure occurs:

> ⚠️ Some legacy MD files could not be parsed.
> Originals preserved in `local/legacy-backup/`. Learning Rules (PENDING
> counts, DECLINED history) will re-accumulate from this run forward.
> To restore counts manually, consult legacy-backup and re-run the
> relevant skill with the recommendation re-declared.

---
