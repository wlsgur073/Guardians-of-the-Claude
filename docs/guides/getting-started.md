---
title: "Getting Started"
description: "Step-by-step guide to set up Claude Code configuration for your project"
version: 1.2.1
---

# Getting Started

This guide walks you through setting up Claude Code configuration for your project, from first install to a verified working setup.

## Prerequisites

- Claude Code installed and working (run `claude --version` to confirm)
- A project you want to configure

## Step 1: Choose Your Setup Method

| Option | What it does | Best for |
| ------ | ------------ | -------- |
| `/init` | Analyzes code, generates basic CLAUDE.md | Quick start -- good for many projects |
| `/guardians-of-the-claude:create` | Guided interview → CLAUDE.md + settings + rules + optional features | Comprehensive setup ([Quick Start](../../README.md#quick-start)) |

**`/init`** is the [officially recommended first step](https://code.claude.com/docs/en/best-practices) -- Claude analyzes your codebase and auto-generates a CLAUDE.md:

```text
claude
> /init
```

**`/guardians-of-the-claude:create`** runs `/init`-style analysis plus generates rules, permissions, and optional advanced features. Install the plugin first (`/plugin marketplace add wlsgur073/Guardians-of-the-Claude`, then `/plugin install guardians-of-the-claude`). **Using both?** Run `/init` first, then `/guardians-of-the-claude:create` choosing "Existing project" -- it detects your existing CLAUDE.md and merges rather than overwrites.

## Step 2: Copy the Templates (Manual Alternative)

If you used `/guardians-of-the-claude:create` in Step 1, skip this step -- your files are already generated.

If you prefer to reference templates manually, see `templates/starter/` and `templates/advanced/` for filled examples (fictional "TaskFlow" project). These show what a completed configuration looks like for each path:

> **Note on the TaskFlow example stack:** The current filled templates use Node.js/Express/TypeScript/PostgreSQL as a concrete illustration. TaskFlow itself is a fictional reference project (see [`templates/README.md`](../../templates/README.md)). `/create` does **not** require your project to be Node/Express — it detects your actual manifest (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `Gemfile`) or asks stack questions for empty projects, then generates equivalent commands.

**Starter** (recommended for beginners):

```bash
# Use the starter example as reference
# See templates/starter/CLAUDE.md and templates/starter/.claude/settings.json
```

**Advanced** (for full configuration):

```bash
# Use the advanced example as reference
# See templates/advanced/CLAUDE.md and templates/advanced/.claude/
```

If `/init` already created a CLAUDE.md, merge the template sections into it. The template provides a consistent section structure; `/init` provides project-specific content. Combine the best of both.

## Step 3: Fill in Your CLAUDE.md

Open your CLAUDE.md and work through each section. The HTML comments in the scaffold tell you what to write:

1. **Project Overview** -- One or two sentences: what does this project do, what language/framework?
2. **Build & Run** -- The exact commands to build and run your project.
3. **Testing** -- How to run tests. Include verification commands Claude can use to check its own work.
4. **Code Style & Conventions** -- Only rules that differ from language defaults. Be specific.
5. **Workflow** -- Branch naming, commit conventions, pre-development checklist.
6. **Project Structure** -- Key directories and their purposes.
7. **Important Context** -- Non-obvious things: required services, auth patterns, environment quirks.
8. **References** -- Link to detailed docs with `@import` syntax.

For detailed guidance on what to include and what to leave out, see the [include/exclude table in the CLAUDE.md Guide](claude-md-guide.md#what-to-include-vs-exclude).

## Step 4: Set Up Rules (Optional)

If your CLAUDE.md is growing past 200 lines, or you have instructions that only apply to specific file types, move them into `.claude/rules/` files.

Use rules when you want:

- **Modular organization** -- one topic per file (e.g., `testing.md`, `code-style.md`)
- **Path-scoping** -- rules that load only when Claude reads matching files
- **Team collaboration** -- different team members own different rule files

Keep core instructions that every session needs in CLAUDE.md. See the [Rules Guide](rules-guide.md) for the full walkthrough.

## Step 5: Configure Permissions

Edit `.claude/settings.json` to pre-approve commands Claude runs frequently. This reduces permission prompts during your workflow:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm test)",
      "Bash(npm run lint)"
    ],
    "deny": [
      "Read(./.env)"
    ]
  }
}
```

The `allow` list uses `Tool(specifier)` syntax. Start with your test and build commands -- those are the safest and most common. See the [Settings Guide](settings-guide.md) for all available options.

## Step 6: Verify It Works

Launch Claude Code in your project and confirm everything is loaded:

1. Run `/memory` -- this shows all loaded CLAUDE.md files and rules. Confirm your files appear.
2. Try a simple task -- ask Claude to explain your project structure or run your test suite.
3. Check that Claude follows your instructions -- if it ignores a rule, the CLAUDE.md may be too long or the instruction may be too vague.

## Step 7: Explore Advanced Features (Optional)

Once your basic configuration is working, explore hooks, agents, and skills for more sophisticated workflows. See the [Advanced Features Guide](advanced-features-guide.md).

**Upgrading from Starter to Advanced:** Run `/guardians-of-the-claude:create` again, choose "Existing project" at the first prompt, and answer the 6 Advanced questions. Claude detects your existing configuration and merges the new sections in.

> **Tip:** The `claude-code-setup` plugin can recommend additional automations (MCP servers, hooks, skills) tailored to your detected stack. Install it from the official marketplace for post-setup suggestions.

## What's Next

- [CLAUDE.md Guide](claude-md-guide.md) -- Deep dive on writing effective CLAUDE.md files
- [Rules Guide](rules-guide.md) -- Organizing instructions into modular rule files
- [Settings Guide](settings-guide.md) -- All settings.json configuration options
- [Directory Structure Guide](directory-structure-guide.md) -- Understanding the .claude/ ecosystem
- [Effective Usage Guide](effective-usage-guide.md) -- Day-one usage patterns and anti-patterns to avoid
- [Advanced Features Guide](advanced-features-guide.md) -- Hooks, agents, and skills for teams
- [MCP Integration Guide](mcp-guide.md) -- Connecting Claude to external tools and services
- [Recommended Plugins Guide](recommended-plugins-guide.md) -- Curated plugins to extend Claude Code
