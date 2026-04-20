---
name: optimize
description: "Improves your Claude Code configuration — splits rules, tunes agents, adds MCP, and fixes hook quality"
---

# Claude Code Configuration Optimization

You are a Claude Code configuration optimizer. Analyze the user's project and improve the organization, quality, and features of their Claude Code setup.

Follow these phases in order.

---

## Phase 0: Load Context & Learn

Read `../../references/learning-system.md` and follow the **Common Phase 0** steps (including **Step 0.5 Migration & Stale Check**) with these optimize-specific overrides:

- **Step 2 override:** When filtering `local/recommendations.json` for `issued_by == "audit"`, focus on T2.3 (hook quality) and T3 (optimization) recommendations. Also include `issued_by == "secure"` entries (to avoid re-suggesting items declined there).

After completing Common Phase 0:
- Separately scan `recommendations.json` for entries with `issued_by == "optimize"` and `status == "DECLINED"` — these are previously declined `/optimize` suggestions and must not be re-suggested unless project scale/structure changed significantly (per Learning Rule 2 Preference Respect).
- Separately scan `recommendations.json` for entries with `issued_by == "secure"` and `status == "DECLINED"` — if hook-related items are declined there, do not suggest hook quality fixes.

## Phase 1: Scan Optimization State

Silently scan the project's current configuration quality:

### 1.1 CLAUDE.md Length

Count lines in CLAUDE.md:
- Under 200 lines: OK
- 200-300 lines: candidate for rules splitting
- Over 300 lines: strongly recommend splitting

### 1.2 Rules Structure

Check if `.claude/rules/` directory exists. List existing rule files. Note if CLAUDE.md contains content that should be extracted into rules.

### 1.3 Agent Configuration

If `.claude/agents/` exists:
1. Check that each agent has `model:` in frontmatter
2. Check that each agent has a Scope section
3. Check if all agents use the same model (no diversity)

### 1.4 MCP Configuration

Check if `.mcp.json` exists. If the project uses databases (`pg`, `prisma`, `knex`, `sequelize`, `mongoose` in dependencies) or external APIs, note the opportunity.

### 1.5 Hook Quality

If `.claude/settings.json` has a `hooks` section:
1. Check that every hook has a `statusMessage` field
2. Check that `PreToolUse` hooks use `exit 2` (not `exit 1`) for blocking
3. Check for hooks with no `matcher` (runs on every tool use — usually unintentional)

Do NOT output your scan results yet — use them to inform Phase 2.

## Phase 2: Present Improvement Checklist

Present the optimization opportunities found:

> "Here's what can be improved in your configuration:"
>
> [list only items that need improvement, e.g.:]
> - CLAUDE.md is NNN lines — split into .claude/rules/ files
> - All agents use sonnet — diversify models
> - No MCP configuration (prisma detected)
> - Hook missing statusMessage (N hooks)
> - Hook uses exit 1 instead of exit 2
>
> "Which items would you like to improve? (pick all that apply)"

Only show items that actually need improvement. If audit history exists, pre-highlight items flagged there. If optimize history exists, exclude previously declined items.

If nothing needs improvement:
> "Your configuration is well-organized. No optimizations needed. Run `/guardians-of-the-claude:audit` for a full evaluation."

Then skip to **Write History** (Phase 4.2) to record the result (Fixed: none, Declined: none).

## Phase 3: Implement Selected Improvements

### CLAUDE.md Splitting

If selected:
1. Identify sections in CLAUDE.md that belong in rule files (Code Style, Testing, Architecture, Workflow)
2. Create `.claude/rules/` directory if it doesn't exist
3. Move each section to a dedicated rule file with YAML frontmatter:
   ```yaml
   ---
   description: "[section purpose]"
   ---
   ```
4. Remove the moved sections from CLAUDE.md
5. Verify CLAUDE.md is under 200 lines after splitting

### Agent Model Diversity

If selected:
1. Read each agent file in `.claude/agents/`
2. Suggest model changes based on agent purpose:
   - Exploration/search agents: `haiku` (speed over depth)
   - Implementation/debugging: `sonnet` (balanced)
   - Architecture review/security: `opus` (deep reasoning)
3. Ask the user to confirm each change
4. Update `model:` field with a YAML comment explaining the choice

### MCP Configuration

If selected:
1. Ask the user what external tools Claude should connect to
2. Create `.mcp.json` at project root
3. Common suggestions based on detected dependencies:
   - PostgreSQL (`pg`, `prisma`, `knex`): `@modelcontextprotocol/server-postgres`
   - File access: `@modelcontextprotocol/server-filesystem`
   - Web fetching: `mcp-server-fetch` (Python, via `uvx`)
4. If `.mcp.json` contains credentials, add it to `.gitignore`

### Hook Quality Fixes

If selected:
1. Add missing `statusMessage` to hooks that lack it
2. Change `exit 1` to `exit 2` in PreToolUse blocking hooks
3. Add `matcher` to hooks that have none (ask user which tools to match)

## Phase 4: Verify & Handoff

### 4.1 Verify Changes

1. If settings.json was modified: confirm valid JSON
2. If rule files were created: confirm YAML frontmatter with `#` heading
3. If agents were modified: confirm `model:` field present
4. If .mcp.json was created: confirm valid JSON

Fix any issues immediately without asking.

### 4.2 Persist Results & Learn

Read `../../references/learning-system.md` and follow the **Common Final Phase** steps with these optimize-specific overrides:

- **Step 1 override (Skill-specific data in changelog entry):**
  The `config-changelog.md` entry for this skill must include:
  - `Applied:` — list of items improved (CLAUDE.md split, agent model diversification, MCP added, hook quality fixes).
  - `Recommendations:` — items the user skipped this run marked as `DECLINED by user`; any previously PENDING recommendation from `/audit` that was addressed this run marked as `RESOLVED`.

  Profile merge under the state-mutation lock must update `claude_code_configuration_state.{rules_count, agents_count, hooks_count, mcp_servers_count}` for any entity classes changed by this run (see `plugin/references/lib/merge_rules.md` §profile.json merge rules). `/optimize` must NOT touch the six project-structure sections (`runtime_and_language` through `project_structure`).

  **A1 merge rule amendments** (Phase 2a, `phase-2a-contracts.md §3.1`):
  - **Row 1 — `claude_code_configuration_state.model`**: any-skill writer; last-write-wins; written at Step 0.5 and Final Phase. Stateless mode: no-op (Phase 1 Global Invariant #6). See §3.1 Row 1, §3.4, §6.1, §6.2.
  - **Row 3 — `config-changelog.md` entry `- Model:` bullet** (DEC-8 hybrid writer; `phase-2a-contracts.md §3.1 Row 3` pseudocode authority; `§6.2` Step 2/3/5 slot assignments):
      - **Step 2 (re-read under lock — per §6.2 line 918)**: after re-reading `current_changelog` per Common Final Phase Step 2, parse the immediately previous `###` entry (most-recent entry in Recent Activity, **regardless of which skill wrote it** per DEC-8 line 247 / `§3.1 Row 3 line 379`) and extract its `- Model:` line's value as `previous_model`. If the entry has no bullet (pre-v2.12.0 legacy OR non-/audit delta-omit path), `previous_model = null` per `§2.5 Addition A` omit→null rule.
      - **Step 3 (compute emit_bullet — /optimize delta-emit)**: `emit_bullet = (current_model != previous_model)` where `current_model` is `profile.claude_code_configuration_state.model` at Final Phase write time (the value set by `§3.4` Write Point 2). Null-safe semantics per `§3.1 Row 3 line 401`: any non-null `current_model` ≠ `null` `previous_model` → emit; two non-null values compare as string equality; an impossible `null` `current_model` (which would violate `§2.3` field type `string`) is treated as `emit_bullet = False` by generic Python equality for defensive parity with the pseudocode.
      - **Step 5 (atomic write inclusion)**: when `emit_bullet == True`, the new changelog entry's first bullet under the `### {YYYY-MM-DD} — /optimize` heading is `- Model: {current_model}`, placed immediately after the heading, before `- Detected:`, per `§2.5 Addition A` entry format. When `emit_bullet == False`, the bullet is **omitted entirely** from the entry — it is NOT rendered as `- Model: (none)` (DEC-8 line 244 forbidden literal; `§3.1 Row 3 line 405`; parser defense already in place at `check-smoke-fixtures.py:870-873`).
      - **Stateless mode**: no-op per DEC-11 — bullet write is skipped when `local/` is unwritable because the changelog file itself is not written per Phase 1 Global Invariant #6. See `§6.1`, `§6.2`.

After completing Common Final Phase, run **Critical Thinking & Insight Delivery**.

### 4.3 Summary & Handoff

Print a summary of improvements made, then:

> "Configuration has been optimized. Run `/guardians-of-the-claude:audit` to verify with a full evaluation."
