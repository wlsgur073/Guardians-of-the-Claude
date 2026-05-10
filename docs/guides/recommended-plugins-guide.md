---
title: "Recommended Plugins"
description: "Curated list of Claude Code plugins organized by category"
version: 1.0.1
---

# Recommended Plugins

Claude Code supports both official (Anthropic-maintained) and community plugins that extend its capabilities. Browse available plugins with `/plugin` in Claude Code, or see [Plugin docs](https://code.claude.com/docs/en/discover-plugins) for details.

## Development Workflow

| Plugin | What it does |
| ------ | ------------ |
| [superpowers](https://github.com/obra/superpowers) | Full dev workflow -- spec, design, plan, subagent-driven implementation. Claude works autonomously for hours without drifting from your plan |
| [feature-dev](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/feature-dev) | Structured 7-phase feature development: explore codebase, ask questions, design, implement, review |
| [code-review](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-review) | Multi-agent PR review with confidence scoring to filter false positives. Catches real issues, skips noise |
| [code-simplifier](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-simplifier) | Refines recently modified code for clarity and consistency while preserving all behavior |

## Code Intelligence & Quality

| Plugin | What it does |
| ------ | ------------ |
| [typescript-lsp](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/typescript-lsp) | TypeScript/JS language server -- go-to-definition, find references, and error checking without leaving Claude |
| [security-guidance](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/security-guidance) | Pre-edit hook that warns about potential security vulnerabilities (XSS, injection, etc.) before code is written |
| [context7](https://github.com/upstash/context7) | MCP server that fetches up-to-date library docs on demand. No more hallucinated APIs |

## UI & Browser

| Plugin | What it does |
| ------ | ------------ |
| [frontend-design](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/frontend-design) | Generates distinctive, production-grade UIs that don't look like "AI made this" |
| [chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) | Control and inspect a live Chrome browser -- debug, automate, and analyze performance via DevTools |
| [figma](https://github.com/figma/mcp-server-guide) | Pull design context directly from Figma files into your implementation workflow |

## Project Setup

| Plugin | What it does |
| ------ | ------------ |
| [claude-code-setup](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-code-setup) | Scans your codebase and recommends the best hooks, skills, MCP servers, and subagents for your project |
| [claude-md-management](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-md-management) | Audit CLAUDE.md quality + capture session learnings with `/revise-claude-md` |

## How to Install

1. Browse available plugins:

   ```text
   /plugin
   ```

2. Add a marketplace and install:

   ```text
   /plugin marketplace add <owner>/<repo>
   /plugin install <plugin-name>@<marketplace-name>
   ```

3. Verify installation:

   ```text
   /plugin list
   ```

> **Tip:** Some plugins (like context7) are MCP servers that need separate setup. Check each plugin's README for installation instructions.
