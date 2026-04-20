---
title: Learning System
description: Shared state management reference for /create, /audit, /secure, /optimize
version: 2.2.0
---

# Learning System

Shared reference for `/create`, `/audit`, `/secure`, `/optimize`. Defines common Phase 0, Final Phase, learning rules, changelog management, and critical thinking standards. All paths relative to `.claude/.plugin-cache/guardians-of-the-claude/`.

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

## Common Final Phase: Persist Results & Learn

Insert after each skill's existing final phase logic.

**Step 1 — Merge, Write, Render** (concurrency-aware, under state-mutation lock):

The Final Phase does NOT blindly overwrite state with the snapshot read at Phase 0. Between Phase 0 and Final Phase, another skill run in a parallel shell may have modified canonical state. The sequence below protects against serialized lost updates (stale-snapshot overwrite) by re-reading under lock and merging this skill's deltas against current state. The Phase 0 snapshot is NOT the ground truth for write; `current_*` at step 2 is.

1. **Acquire `local/.state.lock`** — See `plugin/references/lib/state_io.md` §state-mutation-lock (Final Phase: wait up to 30s behavior).

2. **Re-read current canonical state under lock**:
   - `current_profile` ← parse `local/profile.json`
   - `current_recommendations` ← parse `local/recommendations.json`
   - `current_changelog` ← read `local/config-changelog.md`

3. **Apply this skill's deltas as a merge** (per-skill merge rules — see Per-Skill Merge Rules section below). Produce `new_profile`, `new_recommendations`, `new_changelog` in memory. The same-day duplicate handling of changelog entries (see §Same-Day Duplicate Check) and the compaction check (see §Compaction Algorithm) are applied in memory during this step, before the atomic write.

4. **Render `new_state_summary`** from in-memory `new_profile` + `new_recommendations` + `new_changelog`. Do NOT re-read files from disk after step 2; rendering from in-memory state avoids TOCTOU races with step 5's writes.

5. **Atomic write all four files** (see `plugin/references/lib/state_io.md` §atomic-write):
   - `profile.json` ← `new_profile`
   - `recommendations.json` ← `new_recommendations`
   - `config-changelog.md` ← `new_changelog` (whole-file rewrite; DO NOT use `O_APPEND`)
   - `state-summary.md` ← `new_state_summary`

6. **Release `local/.state.lock`** — See `plugin/references/lib/state_io.md` §state-mutation-lock (release via `os.unlink`).

Do NOT write `latest-{skill}.md` — legacy per-skill result files are deprecated; per-skill result info surfaces through `config-changelog.md` entries and `state-summary.md`'s Recent Skill Results section.

---

## Per-Skill Merge Rules (Final Phase under state-mutation lock)

See `plugin/references/lib/merge_rules.md`.

**Note**: `local/latest-{skill}.md` is deprecated. Skill-specific result info now lives in `config-changelog.md` entries and is surfaced in `state-summary.md`'s Recent Skill Results section. Migration in Step 0.5 moves any legacy `latest-*.md` files to `local/legacy-backup/`.

---

## Same-Day Duplicate Check (Step 3a)

1. Find last `###` line in Recent Activity.
2. Extract date (`YYYY-MM-DD`) and skill name (after `— /`).
3. If today + same skill → update in place: increment run count, append detections with run number, merge recommendations to final state. Do NOT duplicate unchanged fields. Do NOT increment `entry_count` (same logical entry).
4. If different → append new entry. Increment `entry_count`.

**Example** — before (10:30:00 run):

```markdown
### 2026-04-08 — /audit
- Detected: playwright added
- Profile updated: Testing section
- Applied: (none)
- Recommendations:
  - browser automation allow — PENDING
```

After (14:15:00 run merged):

```markdown
### 2026-04-08 — /audit (2 runs)
- Detected: playwright added (run 1), typescript 5.7→5.8 (run 2)
- Profile updated: Testing section (run 1), Runtime section (run 2)
- Applied: (none)
- Recommendations:
  - browser automation allow — PENDING
```

---

## Compaction Algorithm (Step 3b)

1. Count entries in Recent Activity. If >10, trigger compaction.
2. Select entries strictly older than 30 days (entry date < today - 30; entries exactly 30 days old stay in Recent Activity), group by quarter (`YYYY-QN`).
3. Produce compacted summary per quarter. Append to Compacted History, remove originals.

**Step 3b — Per-skill structured anchor emission** (DEC-9; `phase-2a-contracts.md §3.2` pseudocode authority, lines 436-473; `§2.5 Addition B` anchor shape authority, lines 297-319):

For each bucket being rolled into Compacted History at this compaction pass, emit a structured anchor per skill that appeared in the bucket. Anchors embed in the bucket's Compacted History metadata alongside the narrative summary produced by Step 3 — they do not replace the §Lossless Anchors narrative preservation below.

Algorithm (per bucket):

a. **Group `bucket_entries` by `skill`** — up to 4 skills per Phase 1 Environmental Assumption: `/audit`, `/create`, `/secure`, `/optimize`. A skill absent from the bucket has no anchor emitted for this bucket.

b. **Sort each skill's entries by `date` descending** (most-recent first).

c. **Compute `last_entry_date`** = the skill's most-recent entry's `date` (always non-null — entry dates are required by the entry format).

d. **Compute `last_model`** = the skill's most-recent entry whose `bullet_model` is non-null (the `- Model:` bullet value parsed per `§2.5 Addition A`). If all the skill's entries in this bucket lack a bullet (pre-v2.12.0 legacy OR `§3.1 Row 3` delta-omit path), `last_model = null` per `§2.5 line 314` generalized null rule.

e. **Compute `last_capability_fingerprint`** = `§3.5 normalize_model_id(last_model)` when `last_model` is non-null. `§3.5` may return `null` even on non-null input (DEC-2 fail-safe propagation) — propagate `null` rather than raising. When `last_model` is `null`, `last_capability_fingerprint = null`.

f. **Emit anchor dict** `{"skill": skill, "last_entry_date": last_entry_date, "last_model": last_model, "last_capability_fingerprint": last_capability_fingerprint}` into the bucket's Compacted History metadata. Anchor key order matches `§2.5 Addition B` shape.

**Cardinality**: at most one anchor per skill per bucket; up to 4 anchors per bucket maximum (`§2.5 Addition B` line 317). A 5th skill is BREAKING per Phase 1 four-skill environmental assumption.

**Bucket-local sourcing**: the algorithm scans only entries within the current bucket. It does not look back to prior buckets or to Recent Activity to recover a missing `last_model` for this skill (`§3.2 line 479`). If a bucket's `/audit` anchor ends up with `last_model = null`, that anchor carries null forward to `§4.1` reader-time baseline derivation — the consumer-side contract (see **Interactions** below) handles this case without skip-and-continue.

**Fingerprint write-time semantics**: `last_capability_fingerprint` is a write-time informational snapshot. `§4.1` re-normalizes `last_model` at *read* time for `baseline_fp` derivation; the stored fingerprint is not authoritative for drift evaluation (`§2.5 line 321` baseline-anchor-authority resolution). Stale stored values are tolerated and not rewritten on read.

**Stateless mode**: Step 3b is skipped transitively when Phase 1 Global Invariant #6 skips the changelog write (`local/` unwritable; see `phase-2a-contracts.md §6.1`). DEC-11 does not enumerate Step 3b separately — no Step 3b-specific stateless logic is required.

**Lock integration**: Step 3b executes within Final Phase Step 3 (merge deltas) per `§6.2` DEC-12 insertion map — anchors are part of the in-memory merged changelog; persistence occurs at Final Phase Step 5 (atomic write of the full changelog file). No separate lock acquisition — Step 3b rides the existing Final Phase state-mutation lock.

**Interactions** (consumer-side contract — documented here per Codex 3-way 2026-04-20 Q2 verdict, so T6 plan drafting inherits the rule verbatim; `§4.1` is the authoritative specification for reader behavior):

- **`§4.1 DEC-6` scan order for `/audit` baseline derivation**: consumers read `bullet_model` from Recent Activity (reverse-chronological) first; if exhausted, fall through to Compacted History buckets (reverse-chronological); within each bucket, the first `/audit` anchor reached supplies `baseline_last_model` for `baseline_fp` normalization. If exhausted across all Compacted History buckets, `baseline_present = false` → `missing_baseline` silence per `§4.1` silence evaluation order.

- **First-anchor-wins** (`§3.2 line 479` + `§4.1` silence evaluation order step 1 at `contracts.md:669`): if the first `/audit` anchor reached by the scan has `last_model = null`, `§4.1` yields `normalization_null` silence (`baseline_present == true` AND `baseline_fp == null` → `normalization_null`). `§4.1` does **NOT** skip past this anchor to search for an older non-null anchor. Step 3b emits bucket-local `last_model` values faithfully (per-bucket most-recent non-null); the first-anchor-wins semantics are a reader-side terminator contract, not an emit-side filter.

- **Anchor-vs-bullet authority per skill**: `/audit` always-emits the `- Model:` bullet (`§3.1 Row 3` writer policy), so any `/audit` anchor in a bucket has a non-null `last_model` **unless** the bucket's `/audit` entries are all pre-v2.12.0 legacy (legacy entries have no bullet, mapping to `null` per `§2.5 Addition A`). Non-/audit anchors (`/create`, `/secure`, `/optimize`) may have `last_model = null` when all that skill's entries in the bucket delta-omitted (per `§3.1 Row 3` delta-emit policy). These null-anchor cases are the exact trigger for the first-anchor-wins rule above.

- **§Lossless Anchors interaction** (narrative preservation below): §3.2 structured anchors are a supplement to, not a replacement for, the narrative §Lossless Anchors preservation. The narrative summary (dates, skill names+counts, applied changes, etc.) preserves human-readable audit trail; the structured anchors provide machine-readable state for `§4.1` drift derivation. Both are emitted during Step 3's per-bucket output.

4. Three-tier resolution: **year-level** (>2 years) → **quarter-level** (older than current quarter) → **entry-level** (recent, full detail).
5. Update frontmatter: `compacted_at`, `entry_count`.

**Lossless Anchors** (MUST preserve): dates, skill names+counts, applied changes, PENDING/RESOLVED/DECLINED/STALE statuses, declined features, detected project changes.

**Lossy Narrative** (MAY summarize): detailed descriptions, specific filenames, verbose detection details, resolved recommendations (compress to count).

**Example** — before (3 entries, ~21 lines):

```markdown
### 2026-04-15 — /audit
- Detected: Next.js 15, pnpm, Vitest (first scan)
- Profile: generated
- Applied: (none)
- Recommendations:
  - /secure (deny patterns missing) — PENDING
  - rules/ split (CLAUDE.md >150 lines) — PENDING

### 2026-04-22 — /secure
- Applied: 8 deny patterns, 2 file protection hooks
- Profile updated: Configuration State (Hooks 0→2)
- Resolved: "/secure (deny patterns)" from 2026-04-15

### 2026-04-30 — /audit
- Detected: playwright added (devDependencies)
- Profile updated: Testing section (E2E: Playwright)
- Applied: (none)
- Recommendations:
  - rules/ split — PENDING (2x)
  - custom agent — DECLINED by user
```

After compaction (~4 lines):

```markdown
- **2026-Q2 (Apr)**: 2 audits, 1 secure.
  Applied: deny patterns + file protection hooks.
  Open: rules/ split (2x pending). Declined: custom agent.
  Detected changes: playwright added.
```

---

## Legacy Project Profile Format (pre-v2.11.0)

> **Note**: Current canonical format is `profile.json` — see `plugin/references/schemas/profile.schema.base.json` (shape) and `profile.schema.v1.0.0.json` / `profile.schema.v1.1.0.json` (versioned validators). This legacy MD format is still parsed by Phase 0.5 migration (Task 3) to convert existing installations.

Frontmatter:

```yaml
---
title: Project Profile
description: Auto-detected project environment for consistent Claude Code recommendations
generated_by: guardians-of-the-claude
last_updated: {YYYY-MM-DD}
source_files_checked:
  - {manifest files checked}
---
```

Sections use `- Key: Value` format. Use "Not detected" when absent:

```markdown
## Runtime & Language
- Runtime: {e.g. Node.js 22.x}
- Language: {e.g. TypeScript 5.7}
- Module system: {e.g. ESM}

## Framework & Libraries
- Framework: {e.g. Next.js 15 (App Router)}
- UI: {e.g. React 19}
- Styling: {e.g. Tailwind CSS v4}

## Package Management
- Manager: {e.g. pnpm}
- Lock file: {e.g. pnpm-lock.yaml}

## Testing
- Unit: {e.g. Vitest}
- E2E: {e.g. Playwright}

## Build & Dev
- Bundler: {e.g. Turbopack}
- Linter: {e.g. ESLint 9 (flat config)}
- Formatter: {e.g. Prettier}

## Project Structure
- Type: {e.g. Single project (not monorepo)}
- Source convention: {e.g. src/}
- Key directories: {e.g. src/app/, src/components/, src/lib/}

## Claude Code Configuration State
- CLAUDE.md: {exists/missing (section count)}
- settings.json: {exists/missing (permissions note)}
- Rules: {count} files
- Agents: {count} files
- Hooks: {count} configured
- MCP: {count} servers
```

---

## config-changelog.md Format

Frontmatter:

```yaml
---
title: Configuration Changelog
description: Decision journal for Claude Code configuration changes
version: 1.0.0
compacted_at: {YYYY-MM-DD or "never"}
entry_count: {N}
---
```

Two sections: `## Compacted History` and `## Recent Activity`. Entry format:

```markdown
### {YYYY-MM-DD} — /{skill-name}
- Detected: {changes or (none)}
- Profile updated: {sections or (none)}
- Applied: {changes or (none)}
- Resolved: {previously PENDING items now addressed, or (none)}
- Recommendations:
  - {description} — {PENDING | DECLINED by user}
```

Fields with no data use `(none)`. Recommendation statuses:

| Status | Meaning |
| -------- | --------- |
| PENDING | Recommended but not yet addressed |
| PENDING (Nx) | Recommended N times across multiple runs |
| RESOLVED | Previously PENDING, now addressed |
| DECLINED | User explicitly chose not to adopt |
| STALE | PENDING 3+ times with no user response; auto-archived |

Changelog entries must NOT include audit scores. Scores are user-facing snapshots shown in `/audit`'s terminal output and the Recent Skill Results section of `state-summary.md` only — never persisted in `config-changelog.md` or `recommendations.json`.

---

## State Rendering

Skills write `profile.json` + `recommendations.json` as **canonical state**. The derived `state-summary.md` is a human-readable view produced by the shared renderer defined below — never a source.

**Invocation**: Every skill's Final Phase Step 1 calls this renderer immediately after writing the two JSON files.

**Strict rules**:
1. `state-summary.md` is read-only from the user's perspective. Skills never read it in any Phase (hot path or otherwise). Read `profile.json` and `recommendations.json` directly.
2. **All canonical writes use atomic write** — See `plugin/references/lib/state_io.md` §atomic-write.
3. **Stale vs tampered semantics**: `state-summary.md` freshness is compared against `max(mtime(profile.json), mtime(recommendations.json), mtime(config-changelog.md))` — the renderer reads from all three sources.
   - If `state-summary.md` mtime < max(source mtimes) → **stale**: skill's Phase 0 re-renders, prints per-stale-event message ("state-summary.md was stale. Regenerated from current JSON state.").
   - If `state-summary.md` mtime > all source mtimes → **tampered**: user edited derived view. Warn ("state-summary.md is newer than all sources — manual edit detected. It will be overwritten at Final Phase. Edits to derived view are not preserved; modify JSON or use config-changelog.md."), do NOT treat as a source of truth, continue normally.
   - If equal: treat as fresh, no action.

**Layout** (exact):

```markdown
<!-- ─────────────────────────────────────────────
 Generated from JSON state — DO NOT EDIT.
 Read-only view. Manual edits will be overwritten
 on next skill invocation.
 Generated at: {ISO-8601 UTC}
 Source: profile.json v{schema_version}, recommendations.json v{schema_version}
───────────────────────────────────────────────── -->

# Claude Code Configuration State

## Project Profile
- Runtime: {profile.runtime_and_language.runtime or "Not detected"}
- Language: {profile.runtime_and_language.language or "Not detected"}
- Framework: {profile.framework_and_libraries.framework or "Not detected"}
- Package Manager: {profile.package_management.manager or "Not detected"}
- Testing: {profile.testing.unit or "Not detected"} / {profile.testing.e2e or "Not detected"}
- Build: {profile.build_and_dev.bundler or "Not detected"}
- Structure: {profile.project_structure.type or "Not detected"}
- Config: CLAUDE.md {✓ | ✗}, settings.json {✓ | ✗}, Rules {N}, Agents {N}, Hooks {N}, MCP {N}

## Open Recommendations
{For each r in recommendations where status in [PENDING, DECLINED]:}
- **[{status}{× N if pending_count > 1}]** {description} — from /{issued_by}{" (first: " + first_seen_date + ")" if PENDING}{" — " + declined_reason if DECLINED}

{If list empty:} *No open recommendations.*

## Recent Skill Results

{For each skill in [create, audit, secure, optimize] with a most-recent entry in config-changelog's Recent Activity:}
### /{skill} — {most recent entry date}
{One-line summary from the entry's Applied or Detected field}
```

**Render algorithm**:
1. Read `profile.json`, `recommendations.json`.
2. Read last entry per skill from `config-changelog.md` (Recent Activity tail).
3. Produce the above Markdown verbatim, substituting values.
4. Write to `local/state-summary.md`, fully overwriting.

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

## Schema Evolution Policy

Profile and recommendation schemas follow SemVer:

- **Patch (z)**: clarifications, docs, no structural change.
- **Minor (y)**: add optional fields. The parser/validator accepts N-1 minor — each per-version schema file is a single-version validator (pinned by `"schema_version": { "const": "x.y.z" }`).
- **Major (x)**: remove or rename a field, or change its type.

Migration parser MUST support the current minor AND the previous minor (N-1). A major bump triggers a one-time migration rewrite. The `schema_version` field in the JSON payload tracks payload version, independent from `plugin.json` version.

**Base + versioned-wrapper architecture (v2.12.0, profile schema)**: `profile.schema.base.json` holds the shared property shape via `$defs` without closing the schema. Versioned wrappers (`profile.schema.v1.0.0.json`, `profile.schema.v1.1.0.json`, etc.) compose the base via `$ref` and close with `unevaluatedProperties: false` at every scope the wrapper extends. The canonical specification is `phase-2a-contracts.md §2.1–§2.4`.

**Why `unevaluatedProperties` not `additionalProperties`**: `additionalProperties: false` placed in a base schema evaluates within the base's own scope — it rejects fields added by versioned wrappers (those fields look "additional" to the base). `unevaluatedProperties: false` at wrapper scope counts all declarations reached through `allOf`/`$ref` composition as "evaluated," so wrapper-added fields pass while truly unknown fields are rejected. This keyword requires JSON Schema draft 2019-09 or later; wrappers declare `"$schema": "https://json-schema.org/draft/2020-12/schema"` explicitly. Pre-2019-09 validators silently ignore `unevaluatedProperties`, leaving the schema appearing strict but not enforcing — the T0 preflight probe (`ci/scripts/preflight-schema.py`) verifies draft 2020-12 enforcement before T1 schema commits.

**Versioned dispatch**: the parser/validator reads each instance's `schema_version` literal, selects the matching `profile.schema.v<version>.json` wrapper, and validates. Unknown versions fail with a diagnostic naming the literal and the candidate path tried. Schema-level `oneOf` aggregation is not the canonical mechanism.

**Aliases enable id renames across schema versions**: see `recommendation-registry.json` (`aliases[]` field) — a recommendation key can be renamed in a later schema version while the old key continues to resolve transparently to the new entry. ID stability is **not** assumed; aliases are the migration mechanism.

**All timestamps MUST be ISO-8601 UTC** across `profile.json`, `recommendations.json`, `recommendation-registry.json`, and `state-summary.md` (header `Generated at`).

---

## Recommendation ID Registry

The canonical registry is **`plugin/references/recommendation-registry.json`** — machine-readable, schema-validated, the single source of truth for recommendation identities, allowed issuers/resolvers, and aliases. See Task 2.5 for its schema and initial data.

**Identity model**: each recommendation has a stable `key` (lowercase kebab-case, e.g., `deny-env`) — independent of which skill issues or resolves it. The registry stores allowed `issuers[]` and `resolvers[]` per key; CI lints enforce that skill code emits only registered keys (or aliases) and only claims to issue/resolve where the registry authorizes.

**Aliases**: a key can be renamed across schema versions via the `aliases[]` field — backward references continue to resolve transparently. ID stability is not assumed; aliases are the migration mechanism.

**Generated table** (optional): a human-readable summary of the registry may be embedded inline below this section, generated by tooling from `recommendation-registry.json`. Do not maintain such a table by hand — it will drift.

---

## Token Budget

Per-data-source cost:

| Data | Tokens | Read by |
| ------ | -------- | --------- |
| `profile.json` | ~300 | All skills |
| `recommendations.json` (filtered) | ~200 | All skills |
| `config-changelog.md` (Recent only) | ~550 | /create, /secure, /optimize |
| `config-changelog.md` (full) | ~1,300 | /audit only |
| Manifest spot-check | ~200 | All skills (Step 1) |

Per-invocation total:

| Skill | Tokens |
| ------- | -------- |
| `/create`, `/secure`, `/optimize` | ~1,250 |
| `/audit` | ~2,000 |

This is comparable to re-scanning manifests from scratch (~2,000+) while providing richer accumulated context. Keep file budgets enforced (profile ~30 lines, changelog 200 lines) to maintain these costs.

---

## Critical Thinking & Insight Delivery

### Anti-Sycophancy Principle

| Sycophantic (avoid) | Critical (prefer) |
| --- | --- |
| "Done. I added 3 deny patterns." | "I added 3 deny patterns. However, your `/api` route handles file uploads — this endpoint may need an additional allow rule for multipart processing, or requests will be silently blocked." |
| "Your configuration looks good." | "Your configuration covers common cases. One thing: you have MCP servers configured but no deny pattern for MCP tool names — if a server exposes a destructive tool, there is no guardrail." |
| "I recommend adding agents." | "Agents could help, but your project has only 2 rule files and a straightforward structure. A well-written rule file might achieve the same result with less complexity at this scale." |

### Socratic Verification

After completing main work, critically examine output across three categories:

Challenge the recommendation:

- If a skeptical senior engineer reviewed this, what would they question?
- Is there a simpler way to achieve the same outcome that I did not consider?
- Am I recommending this because it is genuinely best, or because it is the most common pattern?

Challenge the assumptions:

- What am I assuming about this project that I have not verified?
- Does the profile say one thing while the actual project state says another?
- Did the user ask for X, but would they actually be better served by Y?

Find the blind spots:

- What could go wrong with what I just did that the user would not notice until later?
- Is there a dependency or interaction between my changes and existing configuration that I have not addressed?
- What question should the user be asking that they are not asking?

### Insight Quality

Must be project-specific, actionable/educational, concise (2-3 sentences). NOT generic advice, NOT restating what was done, NOT praising choices.

### Dialogue over Monologue

When self-verification reveals something worth discussing, present as question/observation inviting user judgment — not as a directive.
