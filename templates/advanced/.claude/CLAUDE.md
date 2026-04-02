---
title: "TaskFlow .claude/CLAUDE.md (Alternative Location)"
description: "Demo stub showing the .claude/ placement option for project instructions"
version: 2.4.0
---

<!-- These two files form a "pick one" pair — use root OR .claude/, not both. -->

# Project Instructions (Alternative Location)

This demonstrates placing project instructions in `.claude/CLAUDE.md` instead of the project root. The full example is at `templates/advanced/CLAUDE.md` (root placement).

## When to use `.claude/CLAUDE.md`
- You prefer a clean project root with fewer dotfiles
- Your root is already crowded with config files (eslint, prettier, tsconfig, etc.)
- You want instructions bundled alongside other Claude Code settings (.claude/rules/, .claude/agents/)

## When to use root `./CLAUDE.md` instead
- You want the file visible at a glance when browsing the repository
- You have a small project with few config files
- You want maximum discoverability for new contributors
