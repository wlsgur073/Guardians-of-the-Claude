---
title: "Recommended Plugins"
description: "Curated list of Claude Code plugins organized by category"
version: 1.2.0
---

# Recommended Plugins

Claude Code supports both official (Anthropic-maintained) and community plugins that extend its capabilities. Browse available plugins with `/plugin` in Claude Code, or see [Plugin docs](https://code.claude.com/docs/en/discover-plugins) for details.

## Development Workflow

| Plugin | What it does |
| ------ | ------------ |
| [superpowers](https://github.com/obra/superpowers) | Full dev workflow -- spec, design, plan, subagent-driven implementation. Claude works autonomously for hours without drifting from your plan |
| [feature-dev](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/feature-dev) | Structured 7-phase feature development: discovery, codebase exploration, clarifying questions, architecture design, implementation, quality review, summary |
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

## Cross-plugin coordination

Plugins that ship into the same marketplace can compose — one plugin's skill can hand off to another, share state via the plugin cache, or cross-reference each other's references. Coordination patterns from our own marketplace:

- **Skill-to-skill delegation.** A skill that produces a profile (e.g., `/guardians-of-the-claude:create`) writes to the plugin cache; subsequent skills (`/audit`, `/secure`, `/optimize`) read from it. The first-write-wins contract is documented in the plugin's reference files.
- **Shared references.** Plugins under a single marketplace can share reference files via `plugin/references/*.md`. The dependency direction is one-way: skills consume references; references don't depend on skills. This matches our `security-patterns.md` ↔ skill relationship.
- **Marketplace name as namespace.** Skills install as `<plugin>@<marketplace>` (e.g., `guardians-of-the-claude@guardians`). The marketplace name namespaces a coherent set of related plugins; cross-marketplace coordination is intentionally NOT supported.

For shipping a plugin into a multi-plugin marketplace: declare which references it owns vs which it consumes; document the read/write contract in `plugin/references/`; avoid skill-to-skill cycles (always one-direction dependency).

**What a plugin can ship** goes beyond skills, agents, and hooks: `.lsp.json` (language-server config for real-time code intelligence), `monitors/monitors.json` (background watchers whose stdout reaches Claude as notifications), `workflows/` (saved [dynamic workflows](workflows-guide.md), namespaced `/plugin-name:workflow-name`), `bin/` (executables added to the Bash tool's PATH while enabled), and a plugin-root `settings.json` (currently the `agent` and `subagentStatusLine` keys). Scaffold with `claude plugin init <name>` (creates the plugin in your skills directory, auto-loading as `<name>@skills-dir`) and check structure with `claude plugin validate <path>` (add `--strict` to treat warnings as errors). Monitors and LSP servers run automatically while the plugin is enabled; workflows and `bin/` executables extend what can be invoked — review all of them at install with the same scrutiny as hook scripts.

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
