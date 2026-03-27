---
title: "Getting Started"
description: "Step-by-step guide to set up Claude Code configuration for your project"
date: 2026-03-18
---

# Getting Started

This guide walks you through setting up Claude Code configuration for your project, from first install to a verified working setup.

## Prerequisites

- Claude Code installed and working (run `claude --version` to confirm)
- A project you want to configure

## Step 1: Run /init (or Use Automated Setup)

Start by running `/init` inside Claude Code. This is the [officially recommended first step](https://code.claude.com/docs/en/best-practices) -- Claude analyzes your codebase and auto-generates a CLAUDE.md tailored to your project.

**Prefer a one-step setup?** Use our automated setup prompt instead -- it runs `/init`-style analysis plus generates rules, permissions, and optional advanced features in one go. See the [Quick Start](../README.md#quick-start) for details.

**Starting a brand new project?** The setup prompt supports empty projects too. Run `@setup-prompt.md` and choose "New/empty project" -- Claude guides you through selecting a tech stack and generates a minimal starter configuration. No existing code required.

```text
claude
> /init
```

The output from `/init` gives you a solid starting point. Our templates fill gaps that `/init` typically misses -- things like permission configuration, modular rule files, and folder-level instructions. The two are complementary: merge them rather than choosing one over the other.

## Step 2: Copy the Templates (Manual Alternative)

If you used `@setup-prompt.md` in Step 1, skip this step -- your files are already generated. The setup prompt's starter path produces output matching the `starter/` template, and the advanced path matches `advanced/`.

If you prefer to copy templates manually, choose your starting point:

**Starter** (recommended for beginners):

```bash
# Copy the minimal CLAUDE.md scaffold (5 sections)
cp Claude-Code-Templates/starter/CLAUDE.md your-project/CLAUDE.md

# Copy settings scaffold
mkdir -p your-project/.claude
cp Claude-Code-Templates/starter/.claude/settings.json your-project/.claude/settings.json
```

**Advanced** (for full configuration):

```bash
# Copy the full CLAUDE.md scaffold (8 sections)
cp Claude-Code-Templates/advanced/CLAUDE.md your-project/CLAUDE.md

# Copy settings, rules, and advanced features
cp -r Claude-Code-Templates/advanced/.claude your-project/.claude
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

## What's Next

- [CLAUDE.md Guide](claude-md-guide.md) -- Deep dive on writing effective CLAUDE.md files
- [Rules Guide](rules-guide.md) -- Organizing instructions into modular rule files
- [Settings Guide](settings-guide.md) -- All settings.json configuration options
- [Directory Structure Guide](directory-structure-guide.md) -- Understanding the .claude/ ecosystem
- [Effective Usage Guide](effective-usage-guide.md) -- Day-one usage patterns and anti-patterns to avoid
- [Advanced Features Guide](advanced-features-guide.md) -- Hooks, agents, and skills for teams
