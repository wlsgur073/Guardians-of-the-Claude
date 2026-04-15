---
title: Learning System
description: Shared state management reference for /create, /audit, /secure, /optimize
version: 2.0.0
---

# Learning System

Shared reference for `/create`, `/audit`, `/secure`, `/optimize`. Defines common Phase 0, Final Phase, learning rules, changelog management, and critical thinking standards. All paths relative to `.claude/.plugin-cache/guardians-of-the-claude/`.

---

## Common Phase 0: Load Context & Learn

Insert before each skill's existing Phase 0 logic.

**Step 0 — Directory Check**: Check if `local/` exists. If not, this is cold start — skip Steps 1-3, proceed to skill's own Phase 0. Final Phase creates the directory.

**Step 1 — Load Profile & Spot-Check**: Read `local/profile.json`. If found, use as project context. Then read the project's primary manifest (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, or `pom.xml` — whichever exists) and cross-check two high-impact items:

1. Does the lock file on disk match the profile's Package Management section? (Detects package manager switches.)
2. Does the primary framework's major version match the profile's Framework & Libraries section? (Detects framework upgrades.)
If either mismatches, apply Rule 4 (Profile Drift Response) immediately before proceeding.
If profile not found, note it will be generated in Final Phase and skip spot-check.

**Step 2 — Load Previous Results**: Read `local/latest-{this-skill}.md`. Cross-skill overrides:

- `/secure`: also read `local/latest-audit.md` (T2 references).
- `/optimize`: also read `local/latest-audit.md` + `local/latest-secure.md`.
- `/create`: also read `local/latest-secure.md` + `local/latest-optimize.md` (to avoid overwriting other skills' changes).
- `/audit`: no additional files.
- If no latest file found: check parent directory for legacy `*-{this-skill}.md`. Read most recent if found.

**Step 3 — Load Changelog & Apply Learning Rules**: Read `local/config-changelog.md`. `/audit` reads full file; other skills read Recent Activity only. If found, apply Learning Rules below. Then proceed to skill's own Phase 0.

---

## Learning Rules (CSA Pattern)

Rule 1 — Recommendation Follow-up

- Context: PENDING in `recommendations.json` (or changelog) + `latest-*.md` existence.
- Signal: PENDING and corresponding skill's latest shows not addressed.
- Action: Re-state with `(Nx pending)` count where N = previous count + 1. Count increments across all skills (not just the current skill). Explain what remains unaddressed.

Rule 2 — Preference Respect

- Context: DECLINED in `recommendations.json` (or changelog) + `local/profile.json`.
- Signal: Previously DECLINED feature in any skill's changelog entry (cross-skill scope).
- Action: Do NOT re-suggest unless project scale/structure changed significantly. If re-suggesting, acknowledge the previous decline.

Rule 3 — Stagnation Detection

- Context: Last 3+ entries in changelog (any skill, not audit-only). Cross-check `recommendations.json` for current PENDING statuses.
- Signal: Same PENDING recommendation appears in 3+ entries consecutively (non-audit entries that don't mention the item do not break the chain). OR `Applied: (none)` in 3 consecutive entries.
- Action: Ask user to (a) apply now, (b) mark declined, (c) defer. If user defers, increment PENDING count per Rule 1. No response after prompt → STALE on next compaction.
- STALE application: During compaction (Step 3b), if an item is PENDING with count N≥3 and no apply/decline/defer action was recorded in any entry since the count reached 3, mark it STALE in the compacted summary. The (Nx) count itself is sufficient evidence — no intermediate status tracking is needed.

Rule 4 — Profile Drift Response

- Context: `local/profile.json` vs current manifests.
- Signal: Spot-check mismatch (lock file type or framework major version).
- Action: Update mismatched section immediately. Re-evaluate related recommendations. Note drift in changelog.

---

## Common Final Phase: Persist Results & Learn

Insert after each skill's existing final phase logic.

**Step 1 — Write Latest Result**: Create `local/` if not exists. Write `local/latest-{this-skill}.md` (overwrite). `latest-audit.md` includes score as user-facing snapshot; others include result summary, files created/modified, features declined.

**Step 2 — Update Profile**: If `local/profile.json` absent, generate from detected state. If present and changes detected, update relevant sections per merge rules (see `plugin/references/lib/merge_rules.md`). `/audit` always regenerates entirely. Update `metadata.last_updated`.

**Step 3 — Append to Changelog**: If absent, create with frontmatter (`entry_count: 1`, `compacted_at: never`), `## Compacted History` section containing `(none)`, `## Recent Activity` section, and first entry. Run Same-Day Duplicate Check (Step 3a), then Compaction Check (Step 3b).

**Step 4 — Legacy Cleanup**: Glob for `*-{this-skill}.md` in parent directory. Delete if found.

---

## Same-Day Duplicate Check (Step 3a)

1. Find last `###` line in Recent Activity.
2. Extract date (`YYYY-MM-DD`) and skill name (after `— /`).
3. If today + same skill → update in place: increment run count, append detections with run number, merge recommendations to final state. Do NOT duplicate unchanged fields. Do NOT increment `entry_count` (same logical entry).
4. If different → append new entry. Increment `entry_count`.

**Example** — before (10:30:00 run):

```markdown
### 2026-04-08 — /audit
- Detected: playwright added
- Profile updated: Testing section
- Applied: (none)
- Recommendations:
  - browser automation allow — PENDING
```

After (14:15:00 run merged):

```markdown
### 2026-04-08 — /audit (2 runs)
- Detected: playwright added (run 1), typescript 5.7→5.8 (run 2)
- Profile updated: Testing section (run 1), Runtime section (run 2)
- Applied: (none)
- Recommendations:
  - browser automation allow — PENDING
```

---

## Compaction Algorithm (Step 3b)

1. Count entries in Recent Activity. If >10, trigger compaction.
2. Select entries strictly older than 30 days (entry date < today - 30; entries exactly 30 days old stay in Recent Activity), group by quarter (`YYYY-QN`).
3. Produce compacted summary per quarter. Append to Compacted History, remove originals.
4. Three-tier resolution: **year-level** (>2 years) → **quarter-level** (older than current quarter) → **entry-level** (recent, full detail).
5. Update frontmatter: `compacted_at`, `entry_count`.

**Lossless Anchors** (MUST preserve): dates, skill names+counts, applied changes, PENDING/RESOLVED/DECLINED/STALE statuses, declined features, detected project changes.

**Lossy Narrative** (MAY summarize): detailed descriptions, specific filenames, verbose detection details, resolved recommendations (compress to count).

**Example** — before (3 entries, ~21 lines):

```markdown
### 2026-04-15 — /audit
- Detected: Next.js 15, pnpm, Vitest (first scan)
- Profile: generated
- Applied: (none)
- Recommendations:
  - /secure (deny patterns missing) — PENDING
  - rules/ split (CLAUDE.md >150 lines) — PENDING

### 2026-04-22 — /secure
- Applied: 8 deny patterns, 2 file protection hooks
- Profile updated: Configuration State (Hooks 0→2)
- Resolved: "/secure (deny patterns)" from 2026-04-15

### 2026-04-30 — /audit
- Detected: playwright added (devDependencies)
- Profile updated: Testing section (E2E: Playwright)
- Applied: (none)
- Recommendations:
  - rules/ split — PENDING (2x)
  - custom agent — DECLINED by user
```

After compaction (~4 lines):

```markdown
- **2026-Q2 (Apr)**: 2 audits, 1 secure.
  Applied: deny patterns + file protection hooks.
  Open: rules/ split (2x pending). Declined: custom agent.
  Detected changes: playwright added.
```

---

## Legacy Project Profile Format (pre-v2.11.0)

> **Note**: Current canonical format is `profile.json` — see `plugin/references/schemas/profile.schema.json`. This legacy MD format is still parsed by Phase 0.5 migration (Task 3) to convert existing installations.

Frontmatter:

```yaml
---
title: Project Profile
description: Auto-detected project environment for consistent Claude Code recommendations
generated_by: guardians-of-the-claude
last_updated: {YYYY-MM-DD}
source_files_checked:
  - {manifest files checked}
---
```

Sections use `- Key: Value` format. Use "Not detected" when absent:

```markdown
## Runtime & Language
- Runtime: {e.g. Node.js 22.x}
- Language: {e.g. TypeScript 5.7}
- Module system: {e.g. ESM}

## Framework & Libraries
- Framework: {e.g. Next.js 15 (App Router)}
- UI: {e.g. React 19}
- Styling: {e.g. Tailwind CSS v4}

## Package Management
- Manager: {e.g. pnpm}
- Lock file: {e.g. pnpm-lock.yaml}

## Testing
- Unit: {e.g. Vitest}
- E2E: {e.g. Playwright}

## Build & Dev
- Bundler: {e.g. Turbopack}
- Linter: {e.g. ESLint 9 (flat config)}
- Formatter: {e.g. Prettier}

## Project Structure
- Type: {e.g. Single project (not monorepo)}
- Source convention: {e.g. src/}
- Key directories: {e.g. src/app/, src/components/, src/lib/}

## Claude Code Configuration State
- CLAUDE.md: {exists/missing (section count)}
- settings.json: {exists/missing (permissions note)}
- Rules: {count} files
- Agents: {count} files
- Hooks: {count} configured
- MCP: {count} servers
```

---

## config-changelog.md Format

Frontmatter:

```yaml
---
title: Configuration Changelog
description: Decision journal for Claude Code configuration changes
version: 1.0.0
compacted_at: {YYYY-MM-DD or "never"}
entry_count: {N}
---
```

Two sections: `## Compacted History` and `## Recent Activity`. Entry format:

```markdown
### {YYYY-MM-DD} — /{skill-name}
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

Changelog entries must NOT include audit scores. Scores are user-facing snapshots in `local/latest-audit.md` only.

---

## State Rendering

Skills write `profile.json` + `recommendations.json` as **canonical state**. The derived `state-summary.md` is a human-readable view produced by the shared renderer defined below — never a source.

**Invocation**: Every skill's Final Phase Step 1 calls this renderer immediately after writing the two JSON files.

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

{For each skill in [create, audit, secure, optimize] with a latest-{skill} entry in config-changelog:}
### /{skill} — {latest entry date}
{One-line summary from the entry's Applied or Detected field}
```

**Render algorithm**:
1. Read `profile.json`, `recommendations.json`.
2. Read last entry per skill from `config-changelog.md` (Recent Activity tail).
3. Produce the above Markdown verbatim, substituting values.
4. Write to `local/state-summary.md`, fully overwriting.

---

## Schema Evolution Policy

`profile.schema.json` and `recommendations.schema.json` follow SemVer:

- **Patch (z)**: clarifications, docs, no structural change.
- **Minor (y)**: add optional fields. The plugin's parser/validator continues to accept JSON files from the previous minor (N-1). Validity is parser-relative, not schema-file-relative — each per-version schema file remains a single-version validator (pinned by `"schema_version": { "const": "x.y.z" }`).
- **Major (x)**: remove or rename a field, or change its type.

Migration parser MUST support the current minor AND the previous minor (N-1). A major bump triggers a one-time migration rewrite.

The `schema_version` field in the JSON payload tracks the payload's schema version, independent from `plugin.json` version.

**Versioned dispatch (behavioral contract)**: When v1.1.0 ships, a sibling schema file `recommendations.schema.v1.1.0.json` is added beside the v1.0.0 file. The plugin's parser/validator reads each instance's `schema_version`, selects the matching versioned schema, and validates. Migration logic lives in the same imperative code path. Schema-level `oneOf` aggregation is **not** the canonical mechanism (it gets noisy and brittle as versions accumulate); an aggregate schema may exist later as editor-tooling convenience only. The dispatcher's file location is TBD at v1.1.0 — only the contract is fixed now.

**Aliases enable id renames across schema versions**: see `recommendation-registry.json` (`aliases[]` field) — a recommendation key can be renamed in a later schema version while the old key continues to resolve transparently to the new entry. ID stability is **not** assumed; aliases are the migration mechanism.

**All timestamps MUST be ISO-8601 UTC** across `profile.json`, `recommendations.json`, `recommendation-registry.json`, and `state-summary.md` (header `Generated at`).

---

## Recommendation ID Registry

The canonical registry is **`plugin/references/recommendation-registry.json`** — machine-readable, schema-validated, the single source of truth for recommendation identities, allowed issuers/resolvers, and aliases. See Task 2.5 for its schema and initial data.

**Identity model**: each recommendation has a stable `key` (lowercase kebab-case, e.g., `deny-env`) — independent of which skill issues or resolves it. The registry stores allowed `issuers[]` and `resolvers[]` per key; CI lints enforce that skill code emits only registered keys (or aliases) and only claims to issue/resolve where the registry authorizes.

**Aliases**: a key can be renamed across schema versions via the `aliases[]` field — backward references continue to resolve transparently. ID stability is not assumed; aliases are the migration mechanism.

**Generated table** (optional): a human-readable summary of the registry may be embedded inline below this section, generated by tooling from `recommendation-registry.json`. Do not maintain such a table by hand — it will drift.

---

## Token Budget

Per-data-source cost:

| Data | Tokens | Read by |
| ------ | -------- | --------- |
| `profile.json` | ~300 | All skills |
| `latest-{skill}.md` | ~200 | All skills |
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

## Critical Thinking & Insight Delivery

### Anti-Sycophancy Principle

| Sycophantic (avoid) | Critical (prefer) |
| --- | --- |
| "Done. I added 3 deny patterns." | "I added 3 deny patterns. However, your `/api` route handles file uploads — this endpoint may need an additional allow rule for multipart processing, or requests will be silently blocked." |
| "Your configuration looks good." | "Your configuration covers common cases. One thing: you have MCP servers configured but no deny pattern for MCP tool names — if a server exposes a destructive tool, there is no guardrail." |
| "I recommend adding agents." | "Agents could help, but your project has only 2 rule files and a straightforward structure. A well-written rule file might achieve the same result with less complexity at this scale." |

### Socratic Verification

After completing main work, critically examine output across three categories:

Challenge the recommendation:

- If a skeptical senior engineer reviewed this, what would they question?
- Is there a simpler way to achieve the same outcome that I did not consider?
- Am I recommending this because it is genuinely best, or because it is the most common pattern?

Challenge the assumptions:

- What am I assuming about this project that I have not verified?
- Does the profile say one thing while the actual project state says another?
- Did the user ask for X, but would they actually be better served by Y?

Find the blind spots:

- What could go wrong with what I just did that the user would not notice until later?
- Is there a dependency or interaction between my changes and existing configuration that I have not addressed?
- What question should the user be asking that they are not asking?

### Insight Quality

Must be project-specific, actionable/educational, concise (2-3 sentences). NOT generic advice, NOT restating what was done, NOT praising choices.

### Dialogue over Monologue

When self-verification reveals something worth discussing, present as question/observation inviting user judgment — not as a directive.
