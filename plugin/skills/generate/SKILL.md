---
name: generate
description: "Guided Claude Code setup — generates CLAUDE.md, settings.json, rules, and optional hooks/agents/skills for any project"
---

# Claude Code Project Setup

You are a Claude Code configuration expert. Set up optimal Claude Code configuration through interactive conversation.

Follow these phases in order.

---

## Phase 0: Determine Path

First, silently check if Claude Code configuration already exists:

1. Check for `CLAUDE.md` (root or `.claude/CLAUDE.md`)
2. Check for `.claude/settings.json`
3. Check for `.claude/rules/` directory

**If both CLAUDE.md and settings.json exist** → ask:

> "I see you already have Claude Code configuration set up. What would you like to do?"
>
> (a) **Add missing features** — keep existing config, add what's missing (rules, hooks, agents, skills, security)
> (b) **Start fresh** — regenerate configuration from scratch (existing files will be merged, not overwritten)

If the user chooses (a), read `references/best-practices.md` then `templates/advanced.md` and follow the **Incremental path** (Phase 2A-Incremental).

If the user chooses (b), continue to the question below.

**If no existing config (or user chose "start fresh")** → ask:

> "Is this an existing project with code, or a new/empty project you're starting from scratch?"
>
> (a) **Existing project** — I already have code, dependencies, and/or a framework set up
> (b) **New/empty project** — I'm starting from scratch or have only basic scaffolding

---

## Route to Path

Based on the user's choice, read the generation rules and the appropriate path file (Phases 1–3 are defined in each path file):

**If the user chooses (b) New/empty project:**

1. Read `references/best-practices.md` — common generation rules
2. Read `templates/starter.md` — follow the Starter path instructions

**If the user chooses (a) Existing project:**

1. Read `references/best-practices.md` — common generation rules
2. Read `templates/advanced.md` — follow the Advanced path instructions

After completing all generation steps from the path file, return here for Phase 4.

---

## Phase 3.5: Quick Verify

After generating files, run a quick sanity check before wrapping up:

1. **CLAUDE.md** — confirm it has at least: Project Overview, Build & Run, Testing sections
2. **settings.json** — confirm it has valid `permissions` with both `allow` and `deny` arrays
3. **Rule files** (if created) — confirm each has YAML frontmatter with at least a `#` heading
4. **Agent files** (if created) — confirm each has `model:` in frontmatter and a Scope section
5. **Cross-references** — confirm any directories mentioned in CLAUDE.md actually exist in the project

If any check fails, fix it immediately before proceeding. Do not ask the user — just correct the issue and note it in the Phase 4 summary.

---

## Phase 4: Wrap Up

After generating all files:

1. Print a summary table listing every created/modified file and what it contains
2. If you merged into existing files, explain what was added
3. Tell the user: "Run `/memory` to verify all configuration files are loaded"
4. Suggest trying a simple task to test the configuration works

**If the user followed the Starter path**, also add:

> You're using a starter configuration. As your project grows and you want rule files, hooks, agents, or skills, run `/claude-code-template:generate` again and choose "Existing project" to upgrade to the full configuration.
