---
title: "Recommended Plugins"
description: "Curated list of Claude Code plugins organized by category"
version: 1.2.2
---

# Recommended Plugins

Claude Code installs plugins from marketplaces. Anthropic's official marketplace, `claude-plugins-official`, is added automatically the first time you start an interactive session and lists plugins Anthropic maintains plus plugins from partners and other authors. Anthropic also runs a community marketplace (`claude-community`), and anyone can publish a third-party marketplace. Browse available plugins with `/plugin` in Claude Code, or see [Plugin docs](https://code.claude.com/docs/en/plugins/install) for details.

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
| [security-guidance](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/security-guidance) | Has Claude review its own changes for vulnerabilities (injection, XSS, unsafe deserialization, etc.) in three layers: a pattern check after each file edit, a model review of each turn's diff, and an agentic review on each commit or push Claude makes. Needs Python 3.7+ on PATH |
| [claude-security](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-security) | Multi-agent vulnerability scan of a whole repo or just a diff, with every finding independently reviewed; turns the findings you choose into patches you apply. Needs a paid plan or API access and Python 3.9+ |
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

Plugins that ship into the same marketplace can compose: one plugin's skill can hand off to another, share state through files they agree on, or declare another plugin as a dependency. Coordination patterns from our own marketplace:

- **Skill-to-skill delegation.** A skill that produces a profile (e.g., `/guardians-of-the-claude:create`) writes to its project-local state directory (`.claude/.plugin-cache/<plugin>/local/`; this is not Claude Code's own plugin cache under `~/.claude/plugins/cache/`, which is replaced on every update. Use `${CLAUDE_PLUGIN_DATA}` for per-plugin data that must survive updates); subsequent skills (`/audit`, `/secure`, `/optimize`) read from it. The first-write-wins contract is documented in the plugin's reference files.
- **Shared references.** Skills inside one plugin share reference files in that plugin's own `references/` directory (`plugin/references/*.md` here). The dependency direction is one-way: skills consume references; references don't depend on skills. This matches our `security-patterns.md` ↔ skill relationship. Separate plugins can't reach each other's files by relative path, because Claude Code copies each installed plugin into its own cache directory and a `../other-plugin/...` path breaks after install. To share a file across plugins in one marketplace, symlink it into each plugin's directory; at install, Claude Code copies the target's content in its place.
- **Marketplace name as namespace.** A plugin installs as `<plugin>@<marketplace>` (e.g., `guardians-of-the-claude@guardians-of-the-claude`, where this repo gives its plugin and its marketplace the same name), and its skills run as `/<plugin>:<skill>`. To build on another plugin, declare it in `dependencies` in `plugin.json` (`"name"`, `"name@marketplace"`, or an object with a semver `version` range), and Claude Code installs it with your plugin. A dependency from a different marketplace installs only if your marketplace lists that marketplace in `allowCrossMarketplaceDependenciesOn`, or if the user already has that plugin enabled at the same scope.

For shipping a plugin into a multi-plugin marketplace: declare which references it owns vs which it consumes; document the read/write contract in `plugin/references/`; avoid skill-to-skill cycles (always one-direction dependency).

**What a plugin can ship** goes beyond skills, agents, and hooks: `.lsp.json` (language-server config for real-time code intelligence), `monitors/monitors.json` (background watchers whose stdout reaches Claude as notifications), `workflows/` (saved [dynamic workflows](workflows-guide.md), namespaced `/plugin-name:workflow-name`), `bin/` (executables added to the Bash tool's PATH while enabled), and a plugin-root `settings.json` (currently the `agent` and `subagentStatusLine` keys). Scaffold with `claude plugin init <name>` (creates the plugin in your skills directory, auto-loading as `<name>@skills-dir`), check structure with `claude plugin validate <path>` (add `--strict` to treat warnings as errors), and test behavior with `claude plugin eval` (v2.1.269+). It runs your eval cases with and without the plugin and scores the difference, and `claude plugin eval init` drafts the cases. A plugin whose `hooks/hooks.json` lists a JavaScript `modules` file is a [mod](https://code.claude.com/docs/en/plugins/mods/overview): its handlers run inside Claude Code and can draw panes, add commands, and hold or answer tool calls. Monitors and LSP servers run automatically while the plugin is enabled; workflows and `bin/` executables extend what can be invoked — review all of them at install with the same scrutiny as hook scripts.

## How to Install

1. Browse available plugins:

   ```text
   /plugin
   ```

2. Install. Every plugin listed above is in Anthropic's official marketplace, `claude-plugins-official`, which Claude Code adds for you the first time you start an interactive session:

   ```text
   /plugin install feature-dev@claude-plugins-official
   ```

   The command opens the plugin's details; choose a scope (user, project, or local) to install it. For a plugin from another marketplace, add that marketplace first:

   ```text
   /plugin marketplace add <owner>/<repo>
   /plugin install <plugin-name>@<marketplace-name>
   ```

3. Verify installation:

   ```text
   /plugin list
   ```

> **Tip:** Some plugins need software outside Claude Code. Language-server plugins such as `typescript-lsp` don't include the server, so install it first (`npm install -g typescript-language-server typescript`). The official `context7` plugin needs no local install, because it connects to Context7's hosted MCP server (it may ask you to authenticate with Context7). Check each plugin's README for its prerequisites.
