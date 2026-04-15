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

- **Step 2 override:** Also read `local/latest-audit.md` (for T2.3 hook quality and T3 optimization issues) and `local/latest-secure.md` (to avoid re-suggesting items declined there).

After completing Common Phase 0:
- If `local/latest-optimize.md` was found: note previously declined items. Do NOT re-suggest them.
- From secure history: if hooks were declined in /secure, do not suggest hook quality fixes.
- If legacy files exist (migration): read the latest `*-audit.md`, `*-secure.md`, and `*-optimize.md` for the same information.

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

- **Step 1 override (Write Latest Result):** `latest-optimize.md` must include:

  ```markdown
  ## Optimize Results
  - Date: {today's date}
  - Fixed:
    - {list of items improved}
  - Declined:
    - {list of items user skipped}
  ```

- **Step 2 override (Update Profile):** Update the "Claude Code Configuration State" section — specifically Rules count, Agents count, MCP status, and Hooks status if they changed.

- **Step 3 (Append to Changelog):** Record improved items as Applied, skipped items as DECLINED. If a previously PENDING recommendation from `/audit` was addressed, mark it as RESOLVED.

After completing Common Final Phase, run **Critical Thinking & Insight Delivery**.

### 4.3 Summary & Handoff

Print a summary of improvements made, then:

> "Configuration has been optimized. Run `/guardians-of-the-claude:audit` to verify with a full evaluation."
