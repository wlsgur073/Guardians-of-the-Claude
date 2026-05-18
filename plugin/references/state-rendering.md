---
title: State Rendering & Token Budget
description: Derived state-summary.md layout, config-changelog.md format, per-invocation token costs.
version: 1.1.1
---

## config-changelog.md Format

Frontmatter:

```yaml
---
title: Configuration Changelog
description: Decision journal for Claude Code configuration changes
version: 1.1.0
compacted_at: {YYYY-MM-DD or "never"}
entry_count: {N}
---
```

Two sections: `## Compacted History` and `## Recent Activity`. Entry format:

```markdown
### {YYYY-MM-DD} — /{skill-name}
- Model: {resolved model id; delta-omit for non-/audit skills if unchanged}
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

`/audit` additionally writes `local/qa-report.md` — a self-versioned post-audit transparency artifact, sibling to `profile.json` / `recommendations.json` / `state-summary.md` / `config-changelog.md`. Terminal-output fallback when `local/` unwritable or stateless mode active.

**Invocation**: Every skill's Final Phase Step 1 substep 4 (see §Common Final Phase above) invokes this renderer. Input is the in-memory `new_profile` + `new_recommendations` + `new_changelog` produced at substep 3; atomic write of `state-summary.md` happens at substep 5. Render is pre-write, not post-write, to avoid TOCTOU against the same Step 1's writes.

**Strict rules**:
1. `state-summary.md` is read-only from the user's perspective. Skills never read it in any Phase (hot path or otherwise). Read `profile.json` and `recommendations.json` directly.
2. **All canonical writes use atomic write** — See `plugin/references/lib/state_io.md` §atomic-write.
3. **Stale vs tampered semantics**: `state-summary.md` freshness is compared against `max(mtime(profile.json), mtime(recommendations.json), mtime(config-changelog.md))` — the renderer reads from all three sources.
   - If `state-summary.md` mtime ≥ max(source mtimes) → **fresh** (equal mtimes are safe for same-batch writes; `state-summary.md` is written LAST in the atomic batch per `final-phase.md` Step 5 write order, so equal or greater mtime is the natural fresh state).
   - If `state-summary.md` mtime < max(source mtimes) → **stale**: skill's Phase 0 re-renders, prints per-stale-event message ("state-summary.md was stale. Regenerated from current JSON state.").
   - Tamper detection via mtime alone is known to be fragile (deferred state-summary tamper mechanism overhaul). The current rule retains "newer than sources → tampered" semantics, with the caveat that same-batch writes can produce equal mtimes which are now treated as fresh per the rule above.

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

### Drift Advisory Header Inject

The `state-summary.md` header injects a one-line drift advisory immediately after `# Claude Code Configuration State` and before `## Project Profile`, sourced from `local/drift-state.json` and rendered per the drift advisory state machine (4 states: match / drift / missing_baseline / normalization_null per the A1 fixture in `ci/scripts/check-audit-drift-aware.py`).

**Format (drift state only — silent in other 3 states)**:

```
Model drift detected: <baseline.model_id> -> <last_seen.model_id>
```

This is the **state-summary header inject format**, distinct from the terminal drift block specified in `plugin/skills/audit/references/output-format.md` (which is longer and includes axis-by-axis change details). State-summary form is short for layout fit; terminal form is full for actionability.

**Note on `last_seen` semantics**: `last_seen.model_id` reflects the most-recent `/audit` Final Phase observation (/audit-only update policy). Drift derivation compares `normalize_model_id(baseline.model_id)` vs `normalize_model_id(last_seen.model_id)` — see `plugin/references/drift-state.md` for the 4-state derivation algorithm.

This sub-section is the canonical specification for the state-summary header inject format. Any prior format specification in other reference files is superseded by this section.

**Render algorithm**:
1. Read `profile.json`, `recommendations.json`.
2. Read last entry per skill from `config-changelog.md` (Recent Activity tail).
3. Produce the above Markdown verbatim, substituting values.
4. Write to `local/state-summary.md`, fully overwriting.

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
