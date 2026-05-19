---
title: "scenario-contract"
description: "Scripted two-shell contention scenario for the state-lock-concurrent fixture"
version: "1.0.0"
---

# Scenario Contract — Concurrent-Shell Mutual Exclusion (spec §6 OCC + §12)

This fixture proves issue #13 criterion 5: under genuine contention on a shared
`local/`, the real short lock serializes commits and OCC forces the loser to
retry-from-fresh — never a torn or lost write. It is a deliberate TDD red while
`acquire_lock` is the documented stub (no contention detection); the real
short-lock (Task 7) + OCC compare-and-commit (Task 8) make it pass.

## Pre-state (input/local/)

The 4 canonical sources + the derived `state-summary.md` are uniform at
`commit_id = commit-0001`. This is shell A's `commit_obs`.

## Scripted interleaving (deterministic — NO real threads/sleep)

The verifier is single-threaded and clock-pinned (`SMOKE_PINNED_UTC`). The two
"shells" are an explicit scripted sequence advanced by a fixture counter; the
`commit_id` sequence is a fixed distinct progression (`commit-0001`,
`commit-0002`, `commit-0003`, …) advanced by that counter — never a reused
constant (a reused id would collapse OCC / torn / ABA detection).

1. **Shell A — Step A (short lock):** acquire short lock, snapshot the 4
   sources, capture `commit_obs = commit-0001`, release.
2. **Shell A — Step B (NO lock, NO canonical reads):** compute A's `/audit`
   deltas strictly from the Step A snapshot.
3. **Injection point — Shell B's FULL A→B→C `/audit` commit runs here**, BETWEEN
   A's Step A and A's Step C: B snapshots `commit-0001`, merges its own `/audit`
   deltas, mints `commit_id = commit-0002`, atomic-writes the 5 files (4 sources
   first, `state-summary.md` last), releases. Exactly one writer's burst is in
   flight at any instant (mutual exclusion).
4. **Shell A — Step C (short lock):** acquire short lock, re-read on-disk
   `commit_now`. `commit_now = commit-0002 != commit_obs = commit-0001` ⇒ a
   concurrent commit landed during A's Step B ⇒ bounded A→B→C retry (N=3 max):
   - A re-snapshots B's now-current state (`commit-0002`),
   - re-merges A's already-computed `/audit` deltas onto it (A's primary
     analysis is NOT re-run),
   - mints A's OWN fresh `commit_id = commit-0003`, atomic-writes the 5 files
     (sources first, summary last), releases.

## Expected post-state (../../golden/state-lock-concurrent/local/)

Final state = B's commit (`commit-0002`) then A's retried commit
(`commit-0003`) layered on top. All 4 sources + `state-summary.md` are uniform
at `commit_id = commit-0003`. `config-changelog.md` shows B's `/audit` entry
(2026-04-14) followed by A's retried `/audit` entry (2026-04-14, second
same-day entry), `entry_count` advanced by 2 from the pre-state. No torn set,
no lost write: exactly B-then-A-retry, serialized.

### Absolute post-state anchors (T8 implementer pin — not just relative deltas)

The golden's exact values, so the OCC/short-lock implementation has a fixed
target (relative "+2 from pre-state" alone underspecifies the absolute):

- `metadata.commit_id` = `commit-0003` (B's `commit-0002`, then A-retry's own
  fresh mint; never a reused constant).
- `config-changelog.md` frontmatter: `entry_count: 3`, `commit_id: commit-0003`
  (pre-state 1 entry on 2026-04-13 + B's 2026-04-14 `/audit` + A-retry's
  2026-04-14 `/audit` = 3; both 2026-04-14 entries are `/audit`).
- `profile.claude_code_configuration_state.scoring_model_ack` =
  `{"version": "audit-score-v4.2.0", "seen_count": 2}`. Rationale: the input
  fixture has NO `scoring_model_ack`, so the first `/audit` Final Phase (B's,
  `commit-0002`) writes the current contract id and `seen_count = min(0+1, 2)
  = 1`; A's retried `/audit` Final Phase re-runs the A1 Row 2 ack-write against
  B's re-snapshotted state (`{v4.2.0, seen_count: 1}` ⇒ trigger still true via
  `seen_count 1 < 2`), yielding `seen_count = min(1+1, 2) = 2`. The ack-write
  is part of the Final-Phase merge (A1 Row 2, Final Phase only) re-applied at
  retry commit time — distinct from "A's primary analysis is NOT re-run"
  (Phase 1–4 detection/scoring), which the retry skips.
