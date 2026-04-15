---
title: Per-Skill Merge Rules
description: Canonical merge rules for profile.json, recommendations.json, and config-changelog.md. Each skill's Final Phase references this file instead of duplicating the rules inline.
version: 1.2.0
---

# Per-Skill Merge Rules

Authoritative source: `docs/superpowers/v3-roadmap/phase-1-contracts.md` §Shared Primitive 4. This file is the skill-facing projection.

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
| `metadata` | Any skill (updates `last_updated`, appends to `source_files_checked`) |
| `claude_code_configuration_state.claude_md` | `/create`, `/audit` |
| `claude_code_configuration_state.settings_json` | `/secure` |
| `claude_code_configuration_state.rules_count` | Any skill that adds or removes rules |
| `claude_code_configuration_state.agents_count` | Any skill that adds or removes agents |
| `claude_code_configuration_state.hooks_count` | Any skill that adds or removes hooks |
| `claude_code_configuration_state.mcp_servers_count` | Any skill that adds or removes MCP servers |

`/secure` and `/optimize` **must not** touch the six project-structure sections (`runtime_and_language` through `project_structure`).

### Bootstrap exception: first-run `settings_json` initialization

When `current_profile` has no `claude_code_configuration_state.settings_json` at all (e.g., first run on a fresh workspace before `/secure` has executed), `/create` and `/audit` MAY initialize this field with their detection of whether `.claude/settings.json` exists (shape: `{"exists": bool, "has_permissions": bool}`). `/secure` owns all subsequent edits once the field is populated. This is the only ownership exception in the table above.

---

## recommendations.json merge rules

Merge by canonical `id` (key). Never rewrite the whole array.

**If a key already exists in `current_recommendations`**: merge — update `status`, `pending_count`, `last_seen`, and conditionally `resolved_by` (when transitioning to RESOLVED) or `declined_reason` (when transitioning to DECLINED). Preserve `first_seen` and all other historical fields.

**If a key does not exist in current**: add as a new entry. The key must pass registry CI lint — it must be a canonical registry key or a registered alias. (Note: aliases are input-only; when persisting, always normalize to the canonical key.)

**Entries not touched by this skill**: preserve exactly as-is. Never delete an entry unless this skill is explicitly marking it STALE per Learning Rule R3.

**`metadata.last_updated`**: refreshed to the Final Phase's pinned-UTC timestamp on every atomic write, regardless of whether any recommendation entry changed. This keeps the payload's `metadata.last_updated` consistent with the file's mtime (since Task 4's Final Phase atomically writes all four canonical files). Individual entry timestamps (`first_seen`, `last_seen`) follow separate rules per entry.

---

## config-changelog.md merge rules

Use whole-file read-modify-write under the state-mutation lock. Read the entire file into memory, apply changes, then atomic-write the result (see `state_io.md §atomic-write`). Do not use `O_APPEND`.

**Same-day update semantics**: if an entry for this skill already exists in today's Recent Activity section, update that entry in place (append new actions to its body). Otherwise append a new entry to the Recent Activity tail.

**Compaction**: apply the Compaction rule (per `§config-changelog Format` in `learning-system.md`) after the update if Recent Activity exceeds its cap.

**Rationale**: the changelog requires same-day in-place updates, which pure append cannot express. Reading and rewriting the whole file under the lock is correct and not a performance concern given the bounded log size (compaction enforces the cap).
