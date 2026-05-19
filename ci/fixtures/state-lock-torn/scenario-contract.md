---
title: "scenario-contract"
description: "Torn-set detection + preserve-first recovery scenario for the state-lock-torn fixture"
version: "1.0.0"
---

# Scenario Contract — Torn-Set Detection + Preserve-First Recovery (spec §9)

This fixture proves the spec §9 torn-set path: when the 4 canonical
SOURCE files carry a NON-UNIFORM `commit_id` (a crash interrupted a
prior writer mid-burst, between source writes, leaving mixed nonces),
the §8 marker preflight classifies the set as TORN and recovery is
PRESERVE-FIRST then STOP — every source is quarantined byte-for-byte
into `legacy-backup/{ISO-8601-UTC}/`, a precise per-file diagnostic is
surfaced, and NO merge / reinit / commit / new `commit_id` is
performed. It is the dedicated torn-set counterpart to
`state-lock-concurrent` / `state-lock-occ-conflict`: those prove the
OCC `uniform` branch serializes; this proves the `torn` branch
detect→preserve→STOP.

The fixture body is byte-identical (modulo `commit_id`) to
`state-lock-occ-conflict` so the only variable under test is source
nonce uniformity: uniform ⇒ OCC compare-and-commit; non-uniform ⇒
torn-set preserve-first stop.

## Pre-state (input/local/)

The 4 canonical sources carry MISMATCHED `commit_id` (a torn set — a
prior writer crashed between source atomic-writes):

- `profile.json`        → `commit-0001`
- `recommendations.json` → `commit-0002`
- `drift-state.json`    → `commit-0001`
- `config-changelog.md` → `commit-0003`

The derived `state-summary.md` carries `commit_id: commit-0001`. The
summary is the derived cache, NEVER a torn-classification authority
(spec §9): torn is determined SOLELY by the 4 sources' mutual
non-uniformity. A stale/absent `commit_id` on the summary ALONE is NOT
torn (the sources-first/summary-last write order makes a
post-sources/pre-summary crash a normal interruption, not a torn set).

## Detection (spec §8 marker preflight → §9 torn branch)

The §8 marker preflight reads `commit_id` from the 4 SOURCE files only
(summary excluded). `{commit-0001, commit-0002, commit-0001,
commit-0003}` is non-uniform ⇒ classification `torn`. This is the same
classifier the `uniform` (OCC) and `absent` (legacy/genesis) branches
use — the torn branch is its partial/mixed outcome, not a parallel
detector.

## Recovery (spec §9 — PRESERVE-FIRST, then STOP)

Deterministic, single-threaded, clock-pinned (`SMOKE_PINNED_UTC`):

1. **PRESERVE FIRST (before anything else):** all 4 SOURCE files are
   copied BYTE-FOR-BYTE into `local/legacy-backup/{ISO-8601-UTC}/`
   (ISO dir name from the pinned clock — `2026-04-14T00-00-00Z` —
   deterministic; reuses the existing legacy-backup quarantine path).
2. **Diagnostic:** a precise message names each of the 4 SOURCE files
   and its observed `commit_id` (or `absent`).
3. **STOP:** NO auto-merge, NO auto-reinit, NO commit, NO new
   `commit_id` minted. The derived summary is NEVER a recovery
   authority. Reinitialization is an explicit user action only — NOT
   modelled here (this fixture asserts detect→preserve→STOP only).

## Expected post-state (../../golden/state-lock-torn/local/)

- `local/legacy-backup/2026-04-14T00-00-00Z/{profile.json,
  recommendations.json, drift-state.json, config-changelog.md}` —
  the 4 sources, byte-for-byte preserved (their original mismatched
  `commit_id`s kept verbatim; nothing re-stamped).
- `local/{profile.json, recommendations.json, drift-state.json,
  config-changelog.md, state-summary.md}` — the originals UNCHANGED
  (no merge, no regen, no commit_id mint). Byte-identical to
  input/local/.
- No new `commit_id` anywhere: the torn-recovery path preserves+stops;
  it never routes through the commit_id stamp/schema-bump helper.
