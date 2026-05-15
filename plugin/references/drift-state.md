---
title: Drift Advisory Derivation (Current Algorithm)
description: First-anchor-wins reverse-chronological scan for model drift; model bullet emission policy; will be replaced by drift-state.json approach in Phase C.
version: 1.0.0
---

## Model Bullet Emission (config-changelog.md)

The `- Model:` bullet captures the resolved Claude model ID at the top of each changelog entry. Hybrid writer policy shared by all four skills:

**Step 2 (re-read under lock)** — after re-reading `current_changelog`, parse the immediately previous `###` entry (most-recent entry in Recent Activity, **regardless of which skill wrote it**) and extract its `- Model:` line value as `previous_model`. Absent bullet (pre-v2.12.0 legacy OR delta-omit path) maps to `previous_model = null`.

**Step 3 (compute `emit_bullet`)** — skill-specific branch:

- **`/audit` always-emit**: `emit_bullet = True` unconditionally. `/audit` is the baseline anchor for drift derivation; always-emitting guarantees the reverse-scan terminator carries non-null `last_model`.
- **`/create`, `/secure`, `/optimize` delta-emit**: `emit_bullet = (current_model != previous_model)` with null-safe equality. `current_model` is `profile.claude_code_configuration_state.model` at Final Phase write time. Two non-null values compare as string equality; non-null `current_model` against `null` `previous_model` emits.

**Step 5 (atomic write)** — when `emit_bullet == True`, the bullet is the first line under the `### {YYYY-MM-DD} — /{skill}` heading:

```
- Model: {current_model}
```

placed immediately before `- Detected:`. When `emit_bullet == False`, the bullet is **omitted entirely** — the literal `- Model: (none)` is forbidden (parser defense in `check-smoke-fixtures.py:870-873`).

**Stateless mode** — when `local/` is unwritable, no changelog write occurs and no model bullet is emitted by any skill.

---

## Drift Advisory Derivation

The `state-summary.md` header and the `/audit` terminal drift block are two render sinks for a single underlying advisory state. The derivation is pure: same inputs produce the same state regardless of which skill invokes the render. All four skills call this derivation via the shared renderer invocation above.

**Inputs**:

- `current_model_id`: the value written at Common Phase 0 Step 0.5 phase 4 into `profile.json → claude_code_configuration_state.model` (see §Common Phase 0).
- `changelog_text`: in-memory `new_changelog` content at Final Phase Step 1 substep 3.
- `current_skill`: the skill currently running (one of `/audit`, `/create`, `/secure`, `/optimize`).

**Algorithm**:

1. Compute `current_fp = normalize_model_id(current_model_id)` per `plugin/references/model-drift-rules.md`. May return `null` for unrecognized models (fail-safe).
2. Scan `changelog_text` for the baseline `/audit` anchor in **reverse-chronological order**:
   - First scan Recent Activity entries (most-recent first) for `/audit` entries with a non-null `- Model:` bullet. If found, `baseline_last_model = bullet value`; stop.
   - If Recent Activity exhausted without match, scan Compacted History buckets (most-recent bucket first). Within each bucket, locate the structured `/audit` anchor (emitted per §Compaction Algorithm Step 3b). The **first** `/audit` anchor reached wins (first-anchor-wins rule); do NOT skip past a null anchor to search for an older non-null one.
   - If all buckets exhausted with no `/audit` anchor: `baseline_present = false`.
3. Compute `baseline_fp`:
   - `baseline_present == false` → `baseline_fp = null` (meaning: no prior baseline; `missing_baseline` state below).
   - `baseline_present == true` AND `baseline_last_model is null` → `baseline_fp = null` (anchor exists but delta-omit path; `normalization_null` state below).
   - `baseline_present == true` AND `baseline_last_model` non-null → `baseline_fp = normalize_model_id(baseline_last_model)`. May itself return `null` (normalization-table boundary case).
4. Silence evaluation order (short-circuit):
   a. `current_fp == null` OR (`baseline_present == true` AND `baseline_fp == null`) → `normalization_null`
   b. `baseline_present == false` → `missing_baseline`
   c. `current_fp == baseline_fp` → `match`
   d. otherwise → `drift`
5. Return `(state, baseline_model_id_string, current_model_id_string)`. The two raw strings are consumed by the render paths for user-facing display (not the normalized fingerprint dicts).

**Render trigger**:

- `drift` → state-summary renderer injects a one-line header immediately after `# Claude Code Configuration State`, before `## Project Profile`: `Model drift: <baseline_model_id_string> -> <current_model_id_string>`. `/audit` terminal additionally renders the axis-wise block (see `plugin/skills/audit/references/output-format.md`).
- `match` / `missing_baseline` / `normalization_null` → **silent** at both sinks. No informational fallback line. Silence is by design: the A2 `recommendations.json` boundary keeps drift transient, and non-drift states carry no user-actionable information.

**Transience (A2 compliance)**:

The derivation MUST NOT add, modify, or remove entries in `recommendations.json`. The advisory is recomputed at every render-time call; it is not persisted as a stored recommendation. Schema files (`recommendations.schema.json`, `recommendation-registry.schema.json`) carry comments excluding drift advisories from registry scope.

**Stateless mode**:

When `local/` is unwritable, Final Phase Step 1 is never reached (lock acquisition aborts before substep 2); therefore the state-summary header is not rendered for any skill. The `/audit` terminal drift block is derived from an in-memory-only changelog snapshot when available and renders even without persistence (`/audit`-specific behavior; see `plugin/skills/audit/SKILL.md` stateless guard). Non-`/audit` skills have no terminal drift sink; stateless silence is total for those skills.

**Cross-skill invariance**:

Every skill produces the same derivation output for the same `(current_model_id, changelog_text)` pair. There is no per-skill branching inside the derivation. `current_skill` is accepted as an input only for diagnostics / logging, not as a decision variable.

---
