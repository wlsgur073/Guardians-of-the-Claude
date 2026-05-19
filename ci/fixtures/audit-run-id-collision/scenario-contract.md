---
title: "scenario-contract"
description: "Two same-microsecond /audit emissions; the second must bump to max(existing)+1µs (canonical-microsecond audit_run_id + monotonic bump)"
version: "1.0.0"
---

# Scenario Contract — audit_run_id Canonical Microsecond + Monotonic Bump

This fixture proves the `audit_run_id` sub-second fix: when two
`/audit` emissions resolve to the SAME pinned microsecond, the second
emission's id must become `max(existing parsed) + 1 microsecond` — never a
duplicate, never a lexicographic misorder. It also proves the CANONICAL
form: every emitted `audit_run_id` is ISO-8601 UTC with exactly 6
fractional digits and an explicit `+00:00` offset
(`2026-…T…:…:….ffffff+00:00`); the bare-`Z` suffix is normalized away.

It reuses the `state-lock-occ-conflict` scripted-interleaving driver
(`run_occ_scenario`) because that driver already produces exactly TWO
`/audit` write bursts at the SAME pinned clock (shell B's commit, then
shell A's retried commit) — the natural same-microsecond collision the
canonical-microsecond + monotonic-bump rule addresses. The ONLY pre-state
difference vs. `state-lock-occ-conflict` is
`drift-state.json`: here the drift ledger is ALREADY ESTABLISHED (non-null
`baseline` + `last_seen`, baseline model `claude-opus-4-7` matching the
`/audit` model) so the drift-state.md Update step's append branch fires
and the `audit_run_id` collision is observable. (`state-lock-occ-conflict`
has `baseline:null,last_seen:null` — a cold-start the verifier OCC path
leaves unchanged, which is why its golden carries no `audit_run_id`.)

## Pre-state (input/local/)

The 4 canonical sources + the derived `state-summary.md` are uniform at
`commit_id = commit-0001` (shell A's `commit_obs`). `drift-state.json` has
an established ledger: `baseline.model_id = claude-opus-4-7`,
`baseline.audit_run_ids = ["2026-04-13T00:00:00.000000+00:00"]`,
`last_seen.audit_run_id = "2026-04-13T00:00:00.000000+00:00"` — both
already in the canonical microsecond form (the input itself models the
canonical form; `first_observed_at` / `observed_at` are plain timestamps,
NOT `audit_run_id`-family, so they stay bare-`Z`).

## Scripted interleaving (deterministic — NO real threads/sleep/wallclock)

Single-threaded, clock-pinned (`SMOKE_PINNED_UTC = 2026-04-14T00:00:00Z`).
The two "shells" are a scripted sequence; the `commit_id` sequence is a
fixed distinct progression (`commit-0001`, `commit-0002`, `commit-0003`).
The candidate `audit_run_id` base is ALWAYS the pinned clock; the +1µs is
derived purely from the on-disk `max` of the snapshot's existing ids — so
the same input yields byte-identical output every run (determinism is
preserved BECAUSE the bump reads on-disk values, not the wall clock).

1. **Shell A — Step A (short lock):** snapshot the 4 sources, capture
   `commit_obs = commit-0001`, release. Snapshot `audit_run_ids =
   ["2026-04-13T00:00:00.000000+00:00"]`.
2. **Shell A — Step B (NO lock, NO canonical reads):** compute A's
   `/audit` deltas + drift-state Update step from the Step A snapshot. The
   verifier asserts zero canonical reads in this window
   (`ASSERT_NO_READ_DURING_B`).
3. **Injection point — Shell B's FULL A→B→C `/audit` commit runs here**,
   BETWEEN A's Step A and A's Step C: B snapshots `commit-0001`, computes
   its `/audit` deltas. B's drift-state Update step: candidate base =
   pinned `2026-04-14T00:00:00Z`; `max(existing)` =
   `2026-04-13T00:00:00.000000+00:00`; candidate (04-14) > max (04-13) ⇒
   NOT bumped ⇒ canonical `2026-04-14T00:00:00.000000+00:00`. Append
   (baseline fingerprint matches). B mints `commit-0002`, atomic-writes
   the 5 files, releases.
4. **Shell A — Step C (short lock):** re-read `commit_now = commit-0002 !=
   commit_obs = commit-0001` ⇒ bounded A→B→C retry (N=3 max):
   - A re-snapshots B's now-current state. `baseline.audit_run_ids =
     ["2026-04-13T00:00:00.000000+00:00",
     "2026-04-14T00:00:00.000000+00:00"]`,
     `last_seen.audit_run_id = "2026-04-14T00:00:00.000000+00:00"`.
   - A re-runs ONLY the drift-state Update step on that snapshot:
     candidate base = pinned `2026-04-14T00:00:00Z`; `max(existing)` =
     `2026-04-14T00:00:00.000000+00:00`; candidate (`…000000`) **≤** max
     (`…000000`, EQUAL) ⇒ **BUMP** ⇒ `max + 1µs =
     2026-04-14T00:00:00.000001+00:00`. This is the monotonic-bump
     collision fix: two same-microsecond emissions ⇒ the second becomes
     max+1µs.
   - A mints its OWN fresh `commit_id = commit-0003`, atomic-writes the 5
     files, releases.

Every successful write burst (B's `commit-0002`, A-retry's `commit-0003`)
yields a distinct `commit_id` (`ASSERT_COMMITID_UNIQUE`).

## Expected post-state (../../golden/audit-run-id-collision/local/)

All 4 sources + `state-summary.md` uniform at `commit_id = commit-0003`.
`config-changelog.md` shows B's `/audit` (2026-04-14) then A's retried
`/audit` (2026-04-14, second same-day entry), `entry_count: 3`. Profile
`scoring_model_ack = {v4.2.0, seen_count: 2}` (identical mechanics to
`state-lock-occ-conflict`).

`drift-state.json` (the canonical-microsecond + monotonic-bump proof):

- `baseline.audit_run_ids = ["2026-04-13T00:00:00.000000+00:00",
  "2026-04-14T00:00:00.000000+00:00",
  "2026-04-14T00:00:00.000001+00:00"]` — the pre-existing id, B's
  non-colliding emission, then A-retry's bumped (`+1µs`) emission. All
  three in canonical 6-fractional-digit `+00:00` form; ascending as
  PARSED datetimes (string-sort would also work here only because the
  forms are uniform — the canonical-microsecond rule still mandates
  parse-to-datetime since a mixed
  `…Z` / `…ffffff` ledger misorders lexicographically).
- `last_seen.audit_run_id = "2026-04-14T00:00:00.000001+00:00"` (A-retry's
  bumped id). `last_seen.observed_at = "2026-04-14T00:00:00Z"` (a plain
  pinned-clock timestamp — NOT `audit_run_id`-family, NOT canonicalized).
- No FIFO trim (3 ≤ 50); no torn set; no lost write: exactly
  pre-existing + B + A-retry, serialized.
