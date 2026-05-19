---
title: Common Phase 0 — Load Context & Learn
description: Pre-skill state read sequence; commit_id marker preflight, migration genesis, torn-set recovery; learning rule application; migration notice template.
version: 1.2.0
---

## Common Phase 0: Load Context & Learn

Insert before each skill's existing Phase 0 logic.

**Step 0 — Directory Check**: Check if `local/` exists. If not, this is cold start — skip Steps 1-3, proceed to skill's own Phase 0. Final Phase creates the directory.

**Step 0.5 — Migration & Stale Check**

> **Precondition**: If `local/` is not writable (privacy-sensitive projects, read-only mounts, or user-disabled), skip the entire Step 0.5 and run the skill in **stateless mode** — print one-time warning ("local/ not writable; stateless run — learning disabled") and continue to the skill's own Phase 0 without reading or writing state.

Step 0.5 classifies on-disk state via a **commit_id marker preflight**, then routes to one of: genesis (legacy upgrade), proceed (uniform state), or torn-set recovery (corrupt/partial state). It is the **sole genesis path** — only Step 0.5 may mint the first `commit_id`. Every transition below is explicit; implicit behavior is forbidden.

The 4 canonical **SOURCE** files are `profile.json`, `recommendations.json`, `config-changelog.md`, `drift-state.json`. `state-summary.md` is a **derived** view, never a source and never a recovery authority.

**§8 — Marker preflight & migration genesis**

1. **Marker preflight (binding ordering — runs before any full schema validation)**: parse only the minimal JSON/frontmatter needed to read each SOURCE file's `schema_version` and `metadata.commit_id` — a lightweight pre-parse, **NOT** full schema validation. This preflight MUST run before any full schema validation, in every lane (including CI gates). Any lane that full-schema-validates a legacy-`schema_version` file before this preflight is an **ordering bug to fix in that lane** — never a reason to base-require `commit_id`. Legacy pre-migration fixtures need no `commit_id` backfill.

2. **Version-dispatched validation target**: when a SOURCE file *is* later schema-validated, validate it against the wrapper for **its own declared `schema_version`** (legacy wrapper versions are `commit_id`-optional), never against the newest wrapper. Newest-wrapper validation of a legacy-version file is the same ordering bug as above.

3. **Classify the 4 SOURCE files by `commit_id` presence**. "Absent" is a **distinct non-comparable state** — it is NOT a value, NOT `0`, and is **never** OCC-comparable:
   - **All 4 absent `commit_id`** → legacy upgrade → **genesis** (sub-step 4).
   - **All 4 present and uniform** (same `commit_id` nonce on all 4) → proceed to full, new-version (marker-required) schema validation of each file against its declared-version wrapper, then continue to the summary freshness check (§Summary freshness) and Step 1.
   - **Partial / mixed** (some `commit_id` present and some absent, OR present but differing nonces) → **torn/corrupt** → §9 torn-set recovery (STOP). Do not proceed, do not write canonical state.

4. **Genesis** (all 4 SOURCE files absent `commit_id` — legacy pre-migration install): the migration mints the **first `commit_id`** and writes the canonical SOURCE set (recovering field values from any legacy MD inputs — `project-profile.md` → `profile.json`; `latest-{skill}.md` Recommendations → `recommendations.json` with legacy ids resolved through registry aliases to canonical keys, alias input-only and NEVER persisted forward; `config-changelog.md` anchors → `drift-state.json` via the documented `derive_from_changelog()`, falling back to a null-fields cold-start document when no usable `/audit` anchor exists). The genesis write is performed under the short lock per `plugin/references/lib/state_io.md` §State-mutation lock (Step 0.5 aborts immediately on live contention; the lock spans only the bounded write burst, no LLM work under the lock). Every legacy MD input examined is then quarantined (§9 preserve-first quarantine semantics: copy into `local/legacy-backup/{ISO-8601-UTC}/`) so legacy MD never coexists with the new canonical JSON — single-source cutover.
   - **Model field write path**: when emitting `profile.json` here, include `claude_code_configuration_state.model = <resolver output>` as a non-null string per the schema. This `.model` write path applies to every skill's emission — genesis migration, fresh bootstrap, post-validation re-write — with no new sub-phase and no `/audit`-specific branching. In stateless mode, this write is a no-op.
   - **Absent is non-comparable, not a value**: genesis is the *only* path that may create a `commit_id`. Step 0.5 always runs before the Final Phase, so a Final Phase that observes the absent state means genesis did not occur (Step 0.5 was skipped under a cold-start/stateless run): the Final Phase MUST NOT proceed and MUST NOT invent a value — it treats the state as **genesis-required** and routes back through Step 0.5, or aborts with a diagnostic if state is unwritable. Coercing absent → a real value and committing is **forbidden**. This preflight-before-validation ordering *is* the backward-compat path; there is no separate compat shim.

**§9 — Torn-set detection & recovery**

5. **Detection scope = the 4 SOURCE files only.** A non-uniform `commit_id` across the 4 SOURCE files ⇒ **torn**. A stale or absent `commit_id` on the **derived** `state-summary.md` *alone* is **NOT** torn — it only triggers summary regeneration (the sources-first / summary-last write order makes a post-sources / pre-summary crash a normal interruption, not corruption).

6. **Recovery = preserve-first, then STOP** (no auto-merge, no auto-reinit):
   - **Preserve first**: BEFORE anything else, copy all 4 SOURCE files **byte-for-byte** into `local/legacy-backup/{ISO-8601-UTC}/` (reuse the existing legacy-backup quarantine pattern; if the path exists in the same second, append `-2`, `-3`, … suffix).
   - **Diagnose**: emit a precise diagnostic naming each of the 4 SOURCE files and its observed `commit_id` (or "absent").
   - **STOP**: do not auto-merge and do not auto-reinitialize. The 4 independent sources cannot be reconstructed from one another or from the derived summary; the derived summary is **NEVER** a recovery authority. Reinitialization / cold-start is only an explicit, user-acknowledged action.
   - **Fresh-nonce guarantee**: any recovery / reinitialization mints a brand-new `commit_id` that no prior holder could have observed — so a stale in-flight Final-Phase holder's compare-and-commit check fails and it aborts (ABA closed without any monotonic counter).

**§Summary freshness** (uniform-state path only; reached from sub-step 3 "all 4 present and uniform"):

- Compute `max_source_mtime = max(mtime(profile.json), mtime(recommendations.json), mtime(config-changelog.md), mtime(drift-state.json))`.
- If `state-summary.md` is absent OR `mtime(state-summary.md) < max_source_mtime` → **stale**: invoke the renderer and write the result via atomic write (see `plugin/references/lib/state_io.md` §Atomic write). Print "state-summary.md was stale. Regenerated from current JSON state."
- If `mtime(state-summary.md) > max_source_mtime` → **tampered**: print "state-summary.md is newer than all sources — manual edit detected. It will be overwritten at Final Phase. Edits to derived view are not preserved." Do NOT treat a tampered derived file as a source of truth.
- If equal: treat as fresh, no action.

**Print migration notice** (only when genesis actually ran): see `learning-system.md` §Migration Notice. Include the `local/legacy-backup/{ISO-8601-UTC}/` path used.

**Routing summary** (every state explicit):

| `commit_id` across 4 SOURCE files | Classification | Behavior |
|---|---|---|
| All 4 absent | legacy upgrade | **Genesis**: mint first `commit_id`, recover field values from legacy MD if present (else cold-start), write canonical SOURCE set under the short lock, quarantine legacy MD to `legacy-backup`, print migration notice. |
| All 4 present and uniform | healthy | Full declared-version schema validation, then §Summary freshness (stale/tampered/fresh), then Step 1. |
| Partial (some present, some absent) | torn | **§9 STOP**: preserve all 4 SOURCE files byte-for-byte to `legacy-backup`, diagnose, STOP. No auto-merge, no auto-reinit. |
| Present but differing nonces | torn | Same as partial — **§9 STOP**. |
| Uniform sources but derived summary stale/absent `commit_id` | NOT torn | Summary regeneration only (§Summary freshness) — derived-view staleness is a normal post-sources/pre-summary interruption, never recovery. |

After Step 0.5 completes (genesis written, or uniform-state validated, or — for torn — Step 0.5 has STOPPED and control does not reach here), proceed to Step 1 normally.

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
