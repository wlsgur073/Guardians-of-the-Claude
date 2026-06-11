---
name: optimize
description: "Improves your Claude Code configuration — splits rules, tunes agents, adds MCP, and fixes hook quality (modifies files). Use when the user asks to optimize, improve, or organize their Claude Code setup."
---

# Claude Code Configuration Optimization

You are a Claude Code configuration optimizer. Analyze the user's project and improve the organization, quality, and features of their Claude Code setup.

Follow these phases in order.

---

## Phase 0: Load Context & Learn

Read `../../references/learning-system.md` and follow the **Common Phase 0** steps (including **Step 0.5 Migration & Stale Check**) with these optimize-specific overrides:

- **Step 2 override:** When filtering `local/recommendations.json` for `issued_by == "audit"`, focus on T2.3 (hook quality) and T3 (optimization) recommendations. Also include `issued_by == "secure"` entries (to avoid re-suggesting items declined there). Also pick up the Phase 3.8 usage/fitness advisory keys (vessel-fit, mcp-unused, cache-stabilize, effort-downgrade).

After completing Common Phase 0:
- Separately scan `recommendations.json` for entries with `issued_by == "optimize"` and `status == "DECLINED"` — these are previously declined `/optimize` suggestions and must not be re-suggested unless project scale/structure changed significantly (per Learning Rule 2 Preference Respect).
- Separately scan `recommendations.json` for entries with `issued_by == "secure"` and `status == "DECLINED"` — if hook-related items are declined there, do not suggest hook quality fixes.
- **Resolve effective config:** If `~/.claude/guardians/config.json` OR `<project>/.claude/guardians/config.json` exists, run `bash plugin/references/lib/config-resolve.sh "<project-dir>"` and read `.config.optimize.skip` plus `.overrides` / `.warnings`. If neither file exists, skip the helper (zero added cost). Honor ONLY `config.optimize.*`. If the helper exits non-zero (invalid config JSON), report `config at <path> is invalid — skips NOT applied` and proceed with no skips.

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

Only show items that actually need improvement. If audit history exists, pre-highlight items flagged there. If optimize history exists, exclude previously declined items. Also exclude any optimization category listed in `config.optimize.skip` (from Phase 0) from the proposals shown this run — this suppresses suggestions by the user's explicit choice; report it (Phase 4.2), do not hide it silently.

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

### Token Usage & Fitness Fixes

If any of these `issued_by:"audit"` recommendations are present and the user selected them:

- **`mcp-unused`**: **verify-only** — the absence signal is cross-project (the parser aggregates all of `~/.claude/projects`), so it shows the server was not observed across recent local usage, not that *this* project does not need it. Ask the user to confirm the server is genuinely unused **in this project** before removing or commenting it out from `.mcp.json`; never disable it on the global signal alone (a short or cross-project window may simply not have exercised a server the project still needs).
- **`vessel-fit`**: move the misfiled automation to the right primitive — e.g., add a hook entry to `.claude/settings.json`, create a `.claude/skills/<name>/SKILL.md`, or add the MCP server — and remove the misfiled instruction from CLAUDE.md. Confirm the target primitive with the user before editing.
- **`cache-stabilize`**: advise stabilizing the system prompt / enabling extended prompt-cache TTL. This is an advisory note, not a destructive edit.
- **`effort-downgrade`**: lower the agent's model/effort tier in the relevant `.claude/agents/*.md` after confirming with the user.

As with the other Phase 3 fixes, ask the user to confirm each change before applying it.

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
  - `Recommendations:` — items the user skipped this run marked as `DECLINED by user`; any previously PENDING recommendation from `/audit` that was addressed this run marked as `RESOLVED`. The usage/fitness keys (vessel-fit, mcp-unused, cache-stabilize, effort-downgrade) resolve through this same RESOLVED/DECLINED + decline_count machinery.
  - `Config skips:` — if `config.optimize.skip` suppressed any category this run, record "Skipped N categories per config (<names>)" so the suppression is transparent in the changelog and summary, not a silent omission.

  For DECLINED items, increment `decline_count` per `plugin/references/lib/merge_rules.md §recommendations.json merge rules`: PENDING -> DECLINED sets `decline_count = 1`; DECLINED -> DECLINED re-record increments `decline_count++`. Monotonic — never decremented. Writes always emit schema 1.1.0; reading a 1.0.0 file performs lazy migration (inflate missing `decline_count` to 0). The repeated-decline trigger in `plugin/hooks/session-start.sh` reads this field after status==DECLINED filter and renders `"declined N times total"` for the rec with the highest `decline_count`.

  Profile merge (lock-free in Final Phase Step B, against the Step A snapshot) must update `claude_code_configuration_state.{rules_count, agents_count, hooks_count, mcp_servers_count}` for any entity classes changed by this run (see `plugin/references/lib/merge_rules.md` §profile.json merge rules). `/optimize` must NOT touch the six project-structure sections (`runtime_and_language` through `project_structure`).

  **A1 merge rule amendments** (applied summary; mechanism in `plugin/references/lib/merge_rules.md`):
  - **Row 1 — `claude_code_configuration_state.model`**: any-skill writer; last-write-wins; written at Step 0.5 and Final Phase. Stateless mode: no-op.
  - **Row 3 — `config-changelog.md` entry `- Model:` bullet**: `/optimize` delta-emits per the shared hybrid writer policy. See `plugin/references/learning-system.md § Model Bullet Emission` for full mechanics; this skill emits only when the resolved model differs from the immediately previous entry's bullet value.

After completing Common Final Phase, run **Critical Thinking & Insight Delivery**.

### 4.3 Summary & Handoff

Print a summary of improvements made, then:

> "Configuration has been optimized. Run `/guardians-of-the-claude:audit` to verify with a full evaluation."
