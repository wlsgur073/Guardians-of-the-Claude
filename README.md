# Claude Code Templates

Starter templates and guides for configuring Claude Code. Clone this repo,
copy the scaffolds into your project, and fill them in using the examples
as reference.

**Audience:** Developers new to Claude Code who want a working configuration
from day one.

**[한국어 README](README-ko.md)**

## Quick Start

1. **Clone this repo**

   ```bash
   git clone https://github.com/wlsgur073/Claude-Code-Templates.git
   ```

2. **Copy templates into your project**

   ```bash
   # Copy the essentials
   cp Claude-Code-Templates/templates/CLAUDE.md your-project/CLAUDE.md
   mkdir -p your-project/.claude
   cp Claude-Code-Templates/templates/.claude/settings.json your-project/.claude/settings.json
   ```

3. **Fill in the scaffolds** using `examples/` as reference

> **Tip:** Run `/init` in your project first — Claude auto-generates a starter
> CLAUDE.md. Then merge our template to fill gaps `/init` misses.

## What's Inside

```text
Claude-Code-Templates/
├── templates/             ← Blank scaffolds to copy into your project
├── templates/advanced/    ← Advanced feature scaffolds (hooks, agents, skills)
├── templates-ko/          ← Korean translations of the templates
├── templates-ko/advanced/ ← Korean translations of advanced scaffolds
├── examples/              ← Filled reference versions (fictional "TaskFlow" project)
├── examples/advanced/     ← Filled advanced feature examples
└── docs/                  ← Guides explaining each concept
```

| Directory | Purpose |
| ------------- | --------- |
| `templates/` | Blank scaffolds with HTML comment prompts — copy and fill in |
| `templates-ko/` | Same scaffolds translated to Korean |
| `examples/` | Realistic filled examples — use as a reference while editing |
| `docs/` | Standalone guides — read any one without the others |

## How Claude Code Memory Works

Claude Code has a layered memory system:

- **CLAUDE.md** — instructions *you* write. Loaded every session.
  Locations: project root, `.claude/`, user home, managed policy.
- **`.claude/rules/`** — modular instruction files, optionally scoped
  to specific file paths. Loaded every session or on file access.
- **Auto memory** — notes *Claude* writes for itself as you work.
  Stored at `~/.claude/projects/<project>/memory/`. First 200 lines
  of MEMORY.md loaded every session.

> **The #1 Rule:** Give Claude a way to verify its work — include test commands,
> lint commands, and build commands in your CLAUDE.md. This is the single
> highest-leverage thing you can do.

## Docs

| Guide | What it covers |
| ------- | --------------- |
| [Getting Started](docs/getting-started.md) | Step-by-step setup walkthrough |
| [CLAUDE.md Guide](docs/claude-md-guide.md) | Writing effective CLAUDE.md files |
| [Rules Guide](docs/rules-guide.md) | .claude/rules/ usage and path-scoping |
| [Settings Guide](docs/settings-guide.md) | settings.json configuration |
| [Directory Structure](docs/directory-structure-guide.md) | The .claude/ ecosystem |
| [Effective Usage](docs/effective-usage-guide.md) | Day-one usage patterns |
| [Advanced Features](docs/advanced-features-guide.md) | Hooks, agents, and skills |

## Recommended Plugins

Claude Code supports official plugins that extend its capabilities.
Install via `/install-plugin` in Claude Code, or see
[Plugin docs](https://docs.anthropic.com/en/docs/claude-code/plugins) for details.

### Development Workflow

| Plugin | What it does |
| ------ | ------------ |
| [superpowers](https://github.com/obra/superpowers) | Full dev workflow — spec → design → plan → subagent-driven implementation. Claude works autonomously for hours without drifting from your plan |
| [feature-dev](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/feature-dev) | Structured 7-phase feature development: explore codebase → ask questions → design → implement → review |
| [code-review](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-review) | Multi-agent PR review with confidence scoring to filter false positives. Catches real issues, skips noise |
| [code-simplifier](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-simplifier) | Refines recently modified code for clarity and consistency while preserving all behavior |

### Code Intelligence & Quality

| Plugin | What it does |
| ------ | ------------ |
| [typescript-lsp](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/typescript-lsp) | TypeScript/JS language server — go-to-definition, find references, and error checking without leaving Claude |
| [security-guidance](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/security-guidance) | Pre-edit hook that warns about potential security vulnerabilities (XSS, injection, etc.) before code is written |
| [context7](https://github.com/upstash/context7) | MCP server that fetches up-to-date library docs on demand. No more hallucinated APIs |

### UI & Browser

| Plugin | What it does |
| ------ | ------------ |
| [frontend-design](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/frontend-design) | Generates distinctive, production-grade UIs that don't look like "AI made this" |
| [chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) | Control and inspect a live Chrome browser — debug, automate, and analyze performance via DevTools |
| [figma](https://github.com/figma/mcp-server-guide) | Pull design context directly from Figma files into your implementation workflow |

### Project Setup

| Plugin | What it does |
| ------ | ------------ |
| [claude-code-setup](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-code-setup) | Scans your codebase and recommends the best hooks, skills, MCP servers, and subagents for your project |
| [claude-md-management](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-md-management) | Audit CLAUDE.md quality + capture session learnings with `/revise-claude-md` |

## Contributing

Contributing? In this repo? Just tell Claude to do it.
...Fine, humans are welcome too. Open an issue or PR.

## License

MIT — see [LICENSE](LICENSE).
