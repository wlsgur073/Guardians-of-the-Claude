---
title: Compaction — Same-Day Duplicate & Quarter Rollup
description: In-memory compaction algorithm during Final Phase Step 3; lossless anchors preservation; per-skill structured anchor emission.
version: 1.0.1
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

**Step 3b — Per-skill structured anchor emission**:

For each bucket being rolled into Compacted History at this compaction pass, emit a structured anchor per skill that appeared in the bucket. Anchors embed in the bucket's Compacted History metadata alongside the narrative summary produced by Step 3 — they do not replace the §Lossless Anchors narrative preservation below.

Algorithm (per bucket):

a. **Group `bucket_entries` by `skill`** — up to 4 skills (`/audit`, `/create`, `/secure`, `/optimize`). A skill absent from the bucket has no anchor emitted for this bucket.

b. **Sort each skill's entries by `date` descending** (most-recent first).

c. **Compute `last_entry_date`** = the skill's most-recent entry's `date` (always non-null — entry dates are required by the entry format).

d. **Compute `last_model`** = the skill's most-recent entry whose `bullet_model` is non-null (the `- Model:` bullet value parsed per the changelog entry format). If all the skill's entries in this bucket lack a bullet (pre-v2.12.0 legacy OR delta-omit path), `last_model = null` per the generalized null rule.

e. **Compute `last_capability_fingerprint`** = `normalize_model_id(last_model)` when `last_model` is non-null. `normalize_model_id` may return `null` even on non-null input (fail-safe propagation) — propagate `null` rather than raising. When `last_model` is `null`, `last_capability_fingerprint = null`.

f. **Emit anchor dict** `{"skill": skill, "last_entry_date": last_entry_date, "last_model": last_model, "last_capability_fingerprint": last_capability_fingerprint}` into the bucket's Compacted History metadata. Anchor key order matches the canonical anchor shape.

**Cardinality**: at most one anchor per skill per bucket; up to 4 anchors per bucket maximum. A 5th skill is BREAKING — the algorithm assumes exactly the 4 skills enumerated above.

**Bucket-local sourcing**: the algorithm scans only entries within the current bucket. It does not look back to prior buckets or to Recent Activity to recover a missing `last_model` for this skill. If a bucket's `/audit` anchor ends up with `last_model = null`, that anchor carries null forward to reader-time baseline derivation — the consumer-side contract (see **Interactions** below) handles this case without skip-and-continue.

**Fingerprint write-time semantics**: `last_capability_fingerprint` is a write-time informational snapshot. The drift advisory state machine re-normalizes `last_model` at *read* time for `baseline_fp` derivation; the stored fingerprint is not authoritative for drift evaluation (baseline-anchor-authority resolution). Stale stored values are tolerated and not rewritten on read.

**Stateless mode**: Step 3b is skipped transitively because the changelog write is skipped (`local/` unwritable). Stateless mode does not enumerate Step 3b separately — no Step 3b-specific stateless logic is required.

**Lock integration**: Step 3b executes within Final Phase Step 3 (merge deltas) per the lock insertion map — anchors are part of the in-memory merged changelog; persistence occurs at Final Phase Step 5 (atomic write of the full changelog file). No separate lock acquisition — Step 3b rides the existing Final Phase state-mutation lock.

**Interactions** (consumer-side contract — Phase C migration cutover):

- **Drift advisory derivation reads `drift-state.json`** (not changelog reverse-scan). See `plugin/references/drift-state.md` § Drift Advisory Derivation (canonical: read `drift-state.json`) for the canonical read path. Step 3b's structured anchor emission (`last_model` + `last_capability_fingerprint` per bucket) is preserved for migration source (Step 0.5 phase 4's `derive_from_changelog()` reads the same anchor format), but post-migration the changelog scan path is removed.

- **Anchor-vs-bullet authority preserved**: `/audit` always-emits the `- Model:` bullet (writer policy unchanged), so any `/audit` anchor in a bucket has a non-null `last_model` unless all `/audit` entries are pre-v2.12.0 legacy. Non-`/audit` anchors may have `last_model = null` when all that skill's entries in the bucket delta-omitted (delta-emit policy). Migration's `audit_observations` filter excludes null-Model entries; `derive_from_changelog()` falls to `cold_start()` if the filter yields an empty list.

- **Lossy reconstruction acknowledgment**: a Compacted bucket retains only the LAST `/audit` entry per bucket, so an installation whose oldest `/audit` observation was rolled into a Compacted bucket whose *last* `/audit` was a different model loses the original first-observation truth. Best-effort recovery uses the oldest survivable anchor (recorded in `legacy_migration.source_changelog_anchor_run_id`).

- **Step 3b emit unchanged**: bucket-local `last_model` and `last_capability_fingerprint` emission remains exactly as specified above. Phase C does not modify the Step 3b algorithm; only consumer interpretation (now via `drift-state.json`, not reverse-scan) evolves.

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
