---
title: State Rendering & Token Budget
description: Derived state-summary.md layout, config-changelog.md format, per-invocation token costs.
version: 1.0.0
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
   - If `state-summary.md` mtime < max(source mtimes) → **stale**: skill's Phase 0 re-renders, prints per-stale-event message ("state-summary.md was stale. Regenerated from current JSON state.").
   - If `state-summary.md` mtime > all source mtimes → **tampered**: user edited derived view. Warn ("state-summary.md is newer than all sources — manual edit detected. It will be overwritten at Final Phase. Edits to derived view are not preserved; modify JSON or use config-changelog.md."), do NOT treat as a source of truth, continue normally.
   - If equal: treat as fresh, no action.

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
