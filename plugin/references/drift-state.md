---
title: Drift Advisory Derivation (canonical via drift-state.json)
description: Model bullet emission policy + drift advisory state machine reading drift-state.json (replaces the changelog scan, now removed).
version: 2.0.1
---

## Model Bullet Emission (config-changelog.md)

The `- Model:` bullet captures the resolved Claude model ID at the top of each changelog entry. Hybrid writer policy shared by all four skills:

**Step 2 (re-read under lock)** — after re-reading `current_changelog`, parse the immediately previous `###` entry (most-recent entry in Recent Activity, **regardless of which skill wrote it**) and extract its `- Model:` line value as `previous_model`. Absent bullet (pre-v2.12.0 legacy OR delta-omit path) maps to `previous_model = null`.

**Step 3 (compute `emit_bullet`)** — skill-specific branch:

- **`/audit` always-emit**: `emit_bullet = True` unconditionally. `/audit` is the baseline anchor for drift derivation; always-emitting guarantees consistent Model bullet presence across the changelog.
- **`/create`, `/secure`, `/optimize` delta-emit**: `emit_bullet = (current_model != previous_model)` with null-safe equality. `current_model` is `profile.claude_code_configuration_state.model` at Final Phase write time. Two non-null values compare as string equality; non-null `current_model` against `null` `previous_model` emits.

**Step 5 (atomic write)** — when `emit_bullet == True`, the bullet is the first line under the `### {YYYY-MM-DD} — /{skill}` heading:

```
- Model: {current_model}
```

placed immediately before `- Detected:`. When `emit_bullet == False`, the bullet is **omitted entirely** — the literal `- Model: (none)` is forbidden (parser defense in `check-smoke-fixtures.py:870-873`).

**Stateless mode** — when `local/` is unwritable, no changelog write occurs and no model bullet is emitted by any skill.

---

## Drift Advisory Derivation (canonical: read `drift-state.json`)

The drift advisory state machine derives its inputs from `local/drift-state.json` (the canonical aggregate state file). No scan of `config-changelog.md` is performed for drift purposes; the changelog scan path is removed.

**Inputs** (read at Final Phase Step 2 — re-read under state-mutation lock):

- `drift_state` ← parse `local/drift-state.json` (post-Phase-0.5 always present; absence indicates manual deletion → the Final Phase lock already held satisfies the lock precondition; perform the cold-start write in place (`baseline=null, last_seen=null, legacy_migration=null`), do NOT re-acquire the lock or re-enter Phase 0.5)
- `current_model_id` ← `profile.claude_code_configuration_state.model` (Step 0.5 phase 4 write target)
- `current_skill` ← the skill currently running (diagnostic only; does NOT branch derivation logic — cross-skill invariance)

**Update step** (Final Phase Step 3, within the delta-merge — `/audit` only):

If running `/audit`, update `drift_state` in memory BEFORE drift derivation:

1. If `baseline` is non-null:
   - Compute `cur_fp = normalize_model_id(current_model_id)` and `base_fp = normalize_model_id(baseline.model_id)`.
   - If `cur_fp` is non-null AND `base_fp` is non-null AND `cur_fp == base_fp`: append `current_audit_run_id` to `baseline.audit_run_ids` (FIFO; if length > 50, drop oldest).
   - Else: do NOT append (null normalization → uncertain match; drift → not baseline-confirming).
2. Else if `baseline` is null (cold-start first /audit):
   - Set `baseline = {model_id: current_model_id, first_observed_at: now, audit_run_ids: [current_audit_run_id]}`.
3. Always update `last_seen = {model_id: current_model_id, audit_run_id: current_audit_run_id, observed_at: now}`.

For non-`/audit` skills, `drift_state` is read-only in Final Phase (skip the update step entirely).

**Derivation** (Final Phase Step 3, after the optional update; consumed by the Step 4 renderer — all skills):

Reduce to fingerprint equality via the 4-state machine in `plugin/references/model-drift-rules.md` `normalize_model_id`:

```
A1 fixture inputs:
  current_fp       <- normalize_model_id(last_seen.model_id)
                      (NOT current_model_id of running skill —
                       last_seen is the /audit-time observation;
                       for /audit, last_seen was just updated in
                       the Update step above)
  baseline_present <- (baseline is non-null)
  baseline_fp      <- normalize_model_id(baseline.model_id)
                      if baseline_present else None

State machine output (per ci/scripts/check-audit-drift-aware.py A1):
  - current_fp is None OR (baseline_present AND baseline_fp is None)
      -> normalization_null
  - NOT baseline_present
      -> missing_baseline
  - current_fp == baseline_fp
      -> match
  - otherwise
      -> drift
```

**Render trigger**:

- `drift` → state-summary renderer injects the header line (see `plugin/references/state-rendering.md` § Drift Advisory Header Inject). `/audit` terminal additionally renders the axis-wise drift block per `plugin/skills/audit/references/output-format.md`.
- `match` / `missing_baseline` / `normalization_null` → **silent** at both sinks.

**Transience**: The drift advisory state machine MUST NOT add, modify, or remove entries in `recommendations.json`. The advisory is NOT persisted as a registry entry; the aggregate state IS persisted as `drift-state.json`.

**Stateless mode**: When `local/` is unwritable, the Step 0.5 phase 4 drift-state sub-step is skipped; `drift-state.json` is not written. Final Phase lock acquisition aborts. `/audit` terminal drift block may still render from an in-memory snapshot if available (audit-specific behavior); non-`/audit` skills are fully silent.

**Cross-skill invariance**: Every skill produces the same derivation output for the same `(drift_state, current_model_id)` pair (modulo the `/audit`-only `last_seen` update). There is no per-skill branching inside the derivation function itself.

---

## Concurrency & Idempotence

Concurrency concerns here apply solely to the one-shot Phase 0.5 migration; the steady-state derivation specified above is pure-functional over an already-parsed `drift_state` and introduces no new concurrency surface.

`derive_from_changelog()` (the Phase 0.5 migration helper) is **pure** — the same changelog snapshot produces logically equivalent output. Two concurrent migrations from the same snapshot produce **parsed-object-equal** output modulo `metadata.last_updated` (which records wall-clock write time and may differ by seconds between concurrent runs). The Phase 0.5 idempotence guard validates via parsed-object equality (Python `dict` after `json.loads`), not byte-equality.

The state-mutation lock acquisition is a known fragility (check-then-act on the lock file is not an atomic acquire); a hardening effort tracks the exclusive-acquire fix separately. Phase 0.5's idempotence guard (re-read → skip-if-valid → write → readback) provides partial mitigation in the single-developer default deployment.

---
