---
title: "scenario-contract"
description: "Legacy-upgrade genesis scenario for the state-lock-genesis fixture (spec §8 absent branch)"
version: "1.0.0"
---

# Scenario Contract — Legacy-Upgrade Genesis (spec §8 `absent` branch)

This fixture proves the spec §8 marker-preflight `absent` branch: when
ALL 4 canonical SOURCE files lack a `commit_id` marker (a pre-marker
legacy state — written before the commit_id-wrapper era), the §8
preflight classifies the set as `absent` and Step 0.5 performs the
one-time GENESIS upgrade: it MINTS the FIRST `commit_id`
(`commit-0001`), stamps the existing legacy canonical set with it,
bumps `profile.json` to the commit_id-required schema wrapper
(`1.3.0`), and echoes the minted id into the changelog frontmatter and
the regenerated `state-summary.md` header. It is the dedicated `absent`
counterpart to `state-lock-occ-conflict` (the `uniform`/OCC branch) and
`state-lock-torn` (the partial/mixed/torn branch): one classifier,
three outcomes.

`"absent"` is a distinct NON-comparable state — NOT a value, NOT `0`,
never OCC-comparable. ONLY Step 0.5 mints the genesis `commit_id`; a
later Final-Phase write path that observes `absent` means genesis did
not occur and MUST NOT proceed or invent a value (a defensive guard
routes it back / aborts — coercing `absent`→a real value and
committing is forbidden). preflight-before-validation IS the
backward-compat path; legacy fixtures need no backfill, and each
canonical file validates against the wrapper for its OWN declared
`schema_version` (the markerless input validates as commit_id-optional
legacy versions; only the genesis OUTPUT profile validates against the
commit_id-required v1.3.0 wrapper).

The fixture body is the `state-lock-occ-conflict` pre-state with EVERY
`commit_id` removed and `profile.json` left at its legacy `1.2.0`
schema, so the only variable under test is marker presence: all-absent
⇒ genesis mint+stamp+continue; all-uniform ⇒ OCC compare-and-commit;
partial/mixed ⇒ torn preserve-first stop.

## Pre-state (input/local/)

A pre-marker legacy state. NONE of the 4 SOURCE files carry a
`commit_id`; the derived `state-summary.md` likewise has no `commit_id`
header line:

- `profile.json`        → schema `1.2.0`, NO `commit_id`
- `recommendations.json` → schema `1.0.0`, NO `commit_id`
- `drift-state.json`    → schema `1.0.0`, NO `commit_id`
- `config-changelog.md` → version `1.1.0`, NO `commit_id` frontmatter, 1
  entry (2026-04-13 `/audit`)

## Detection (spec §8 marker preflight → `absent` → §8 genesis branch)

The §8 marker preflight reads `commit_id` from the 4 SOURCE files only
(summary excluded — it is the derived cache, never a classification
authority). All 4 absent ⇒ classification `absent` ⇒ legacy upgrade ⇒
Step 0.5 GENESIS. This is the SAME classifier the `uniform` (OCC) and
`torn` branches use — the `absent` outcome is its all-markerless case,
not a parallel detector.

## Recovery / upgrade (spec §8 — GENESIS: mint FIRST commit_id)

Deterministic, single-threaded, clock-pinned (`SMOKE_PINNED_UTC`):

1. **Step 0.5 runs first** (lock, classify, no legacy MD → no
   quarantine; the markerless JSON sources are present-valid against
   their own commit_id-optional legacy wrappers). It regenerates the
   summary cache from the existing sources.
2. **GENESIS mint:** the §8 preflight still reports `absent`, so the
   one-time genesis sub-step mints the FIRST `commit_id` =
   `commit-0001` from the deterministic counter (no observed nonce ⇒
   counter seeded at 0 ⇒ first mint `commit-0001`; no
   `datetime.now()`/sleep/randomness).
3. **Stamp + continue (NOT stop — genesis upgrades then proceeds):** the
   existing legacy canonical set is stamped with `commit-0001` via the
   SAME commit_id stamp/schema-bump helper the OCC commit uses:
   `profile.json` → schema `1.3.0` + `metadata.commit_id`,
   `recommendations.json` + `drift-state.json` → `metadata.commit_id`
   added, `config-changelog.md` → `commit_id:` frontmatter line
   inserted, and `state-summary.md` regenerated with the `commit_id:`
   header line. The legacy CONTENT is preserved (no `/audit`
   re-detection — `skill_sequence` is empty); genesis ADDS the marker,
   it does not re-derive the profile.

## Expected post-state (../../golden/state-lock-genesis/local/)

- `local/profile.json` — legacy content preserved, `schema_version`
  `1.2.0`→`1.3.0`, `metadata.commit_id: commit-0001` added (input
  `last_updated` 2026-04-13 kept — genesis stamps the marker, it does
  not re-run detection).
- `local/recommendations.json` — schema `1.0.0` unchanged,
  `metadata.commit_id: commit-0001` added.
- `local/drift-state.json` — schema `1.0.0` unchanged,
  `metadata.commit_id: commit-0001` added, `metadata.last_updated`
  advanced to the pinned UTC (the stamp helper refreshes drift-state's
  timestamp at commit).
- `local/config-changelog.md` — `commit_id: commit-0001` inserted into
  frontmatter directly after `entry_count:`; the single 2026-04-13
  `/audit` entry is unchanged (genesis does not append an entry).
- `local/state-summary.md` — regenerated: ` Generated at:` advanced to
  the pinned UTC, ` Source: profile.json v1.3.0, …`, and a
  ` commit_id: commit-0001` header line directly after the ` Source:`
  line.
- No `legacy-backup/` directory: genesis is not torn-recovery and there
  is no legacy MD to quarantine — it is an in-place marker upgrade.
- Exactly ONE `commit_id` minted this run (`commit-0001`); it is the
  genesis first id, distinct and never reused.
