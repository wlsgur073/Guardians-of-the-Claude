---
title: Per-Skill Merge Rules
description: Canonical merge rules for profile.json, recommendations.json, and config-changelog.md. Each skill's Final Phase references this file instead of duplicating the rules inline.
version: 1.3.0
---

# Per-Skill Merge Rules

These rules govern how each skill's Final Phase applies its changes to canonical state. The Final Phase does **not** blindly overwrite state with the Phase 0 snapshot. Under the state-mutation lock (see `state_io.md §state-mutation-lock`), it re-reads current canonical state and merges this skill's deltas against that current state — protecting against lost updates from parallel shell sessions.

---

## profile.json merge rules

Each skill owns specific top-level sections of `profile.json`. It replaces **only the fields it owns** in this run. All other fields must be preserved from the re-read `current_profile`.

**Section ownership**:

| Section | Owning skills |
|---|---|
| `runtime_and_language` | `/create`, `/audit` |
| `framework_and_libraries` | `/create`, `/audit` |
| `package_management` | `/create`, `/audit` |
| `testing` | `/create`, `/audit` |
| `build_and_dev` | `/create`, `/audit` |
| `project_structure` | `/create`, `/audit` |
| `monorepo_detection` | `/audit` |
| `metadata` | Any skill (updates `last_updated`, appends to `source_files_checked`) |
| `claude_code_configuration_state.claude_md` | `/create`, `/audit` |
| `claude_code_configuration_state.claude_md.subpackages` | `/audit` |
| `claude_code_configuration_state.claude_md.subpackage_coverage` | `/audit` |
| `claude_code_configuration_state.settings_json` | `/secure` |
| `claude_code_configuration_state.rules_count` | Any skill that adds or removes rules |
| `claude_code_configuration_state.agents_count` | Any skill that adds or removes agents |
| `claude_code_configuration_state.hooks_count` | Any skill that adds or removes hooks |
| `claude_code_configuration_state.mcp_servers_count` | Any skill that adds or removes MCP servers |

`/secure` and `/optimize` **must not** touch the six project-structure sections (`runtime_and_language` through `project_structure`).

### Bootstrap exception: first-run `settings_json` initialization

When `current_profile` has no `claude_code_configuration_state.settings_json` at all (e.g., first run on a fresh workspace before `/secure` has executed), `/create` and `/audit` MAY initialize this field with their detection of whether `.claude/settings.json` exists (shape: `{"exists": bool, "has_permissions": bool}`). `/secure` owns all subsequent edits once the field is populated. This is the only ownership exception in the table above.

### project_structure / monorepo_detection consistency precondition (v1.2.0 new)

Any writer that updates `project_structure.type` MUST re-read `current_profile` under the state-mutation lock and produce a profile that validates against the type-consistency invariants in the v1.2.0 wrapper schema.

`/audit` is the only writer that owns `monorepo_detection` and the only writer that may transition monorepo state. On each writable `/audit` run, it MUST recompute detection and write `monorepo_detection` plus `project_structure.type` in the same locked transaction:

- If recomputed `monorepo_detection.detected == true`, set `project_structure.type = "monorepo"`.
- If recomputed `monorepo_detection.detected == false`, set `project_structure.type = "single_project"`.
- If detection is unavailable or indeterminate, set `monorepo_detection = null` or `detected = null`; `project_structure.type` may be `null`.

Non-`/audit` writers do not own `monorepo_detection`:

- If `current_profile.monorepo_detection.detected == true`, they MUST preserve `project_structure.type = "monorepo"`.
- If `current_profile.monorepo_detection.detected == false`, they MUST NOT write `project_structure.type = null` or `"monorepo"`; they may preserve or write `"single_project"`.
- If `current_profile.monorepo_detection == null` or `.detected == null`, they may write `"single_project"` or `null` according to their analysis, but MUST NOT write `"monorepo"` because they cannot also write `monorepo_detection.detected = true`.

This handles the stale-workspace edge case: when `/audit` re-reads stale current state, recomputes `detected = false` after the user removed the workspace declaration, then writes `detected = false` and `type = "single_project"` in one transaction.

`monorepo_detection`, `claude_md.subpackages`, and `claude_md.subpackage_coverage` are full-replace on each writable `/audit` run: deterministic recomputation of the per-package score snapshot replaces the previous list (no key-merge by `path`, since per-package scores have no historical-trend semantic in this version).

---

## recommendations.json merge rules

Merge by canonical `id` (key). Never rewrite the whole array.

**If a key already exists in `current_recommendations`**: merge — update `status`, `pending_count`, `last_seen`, and conditionally `resolved_by` (when transitioning to RESOLVED) or `declined_reason` (when transitioning to DECLINED). Preserve `first_seen` and all other historical fields.

**If a key does not exist in current**: add as a new entry. The key must pass registry CI lint — it must be a canonical registry key or a registered alias. (Note: aliases are input-only; when persisting, always normalize to the canonical key.)

**Entries not touched by this skill**: preserve exactly as-is. Never delete an entry unless this skill is explicitly marking it STALE per Learning Rule R3.

**`metadata.last_updated`**: refreshed to the Final Phase's pinned-UTC timestamp on every atomic write, regardless of whether any recommendation entry changed. This keeps the payload's `metadata.last_updated` consistent with the file's mtime (since Task 4's Final Phase atomically writes all four canonical files). Individual entry timestamps (`first_seen`, `last_seen`) follow separate rules per entry.

**`decline_count`** (added in schema 1.1.0): an integer field on each recommendation entry (minimum 0, default 0). Increment behavior:

- **PENDING -> DECLINED transition**: set `decline_count = (current.decline_count or 0) + 1`. First decline (count was 0 or absent in legacy 1.0.0 file) sets `decline_count = 1`.
- **DECLINED -> DECLINED re-record** (same skill or any of the four state-writing skills records a fresh DECLINE event for an already-DECLINED rec): increment `decline_count++`.
- **PENDING -> PENDING** (no status change): preserve `current.decline_count` exactly. No-op even if `pending_count` increments via the existing `pending_count` rule.
- **DECLINED -> PENDING** (re-transition: rec was declined, then user re-considered): preserve `current.decline_count` exactly. **Monotonic — never decremented.** A subsequent DECLINE on this PENDING rec will increment from the preserved historical value, which is rendered by SessionStart's repeated-decline trigger as `"declined N times total"` (cumulative semantics).
- **RESOLVED transitions**: `decline_count` preserved as-is regardless of what it was before. RESOLVED is independent of the decline pathway.

**Applies to all four state-writing skills**: `/create`, `/audit`, `/secure`, `/optimize`. Schema `issued_by` enum permits `"create"` and `/create`'s Phase 4.5 `Recommendations:` line writes DECLINED entries marked "DECLINED by user" (per `plugin/skills/create/SKILL.md`). Excluding `/create` from this rule produces silent under-counting on re-runs.

**Lazy migration on first 1.1.0 write**: when a state-writing skill reads a 1.0.0 file (no `decline_count` field), it inflates missing `decline_count` to 0 in-memory and emits `1.1.0` schema on the next atomic write. Pre-existing DECLINED entries start at `decline_count = 0` (no historical reconstruction from `config-changelog.md` — the field is forward-looking advisory).

---

## config-changelog.md merge rules

Use whole-file read-modify-write under the state-mutation lock. Read the entire file into memory, apply changes, then atomic-write the result (see `state_io.md §atomic-write`). Do not use `O_APPEND`.

**Same-day update semantics**: if an entry for this skill already exists in today's Recent Activity section, update that entry in place (append new actions to its body). Otherwise append a new entry to the Recent Activity tail.

**Compaction**: apply the Compaction rule (per `§config-changelog Format` in `learning-system.md`) after the update if Recent Activity exceeds its cap.

**Rationale**: the changelog requires same-day in-place updates, which pure append cannot express. Reading and rewriting the whole file under the lock is correct and not a performance concern given the bounded log size (compaction enforces the cap).
