---
title: "TaskFlow .claude/CLAUDE.md (Alternative Location)"
description: "Demo stub showing the .claude/ placement option for project instructions"
version: 1.2.0
---

<!-- These two files form a "pick one" pair — use root OR .claude/, not both. -->

# Project Instructions (Alternative Location)

This demonstrates placing project instructions in `.claude/CLAUDE.md` instead of the project root. The full example — Identity-DNA, Trust Boundary, Memory framework, Development Approach, and Verification — lives in `templates/advanced/CLAUDE.md` (root placement); placing the same content here would duplicate the canonical source and contradict the "pick one" pair pattern below.

Claude auto-discovers `CLAUDE.md` in both the project root and `.claude/` directory — no extra configuration required. Do not place instructions in both locations, as they may conflict.

## When to use `.claude/CLAUDE.md`
- You prefer a clean project root with fewer dotfiles
- Your root is already crowded with config files (eslint, prettier, tsconfig, etc.)
- You want instructions bundled alongside other Claude Code settings (.claude/rules/, .claude/agents/)

## When to use root `./CLAUDE.md` instead
- You want the file visible at a glance when browsing the repository
- You have a small project with few config files
- You want maximum discoverability for new contributors
