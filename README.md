<p align="center">
  <img src="assets/banner.svg" alt="Claude Code Template" width="700"/>
</p>

Starter templates and guides for configuring Claude Code. Clone this repo,
copy the scaffolds into your project, and fill them in using the examples
as reference.

**Audience:** Developers new to Claude Code who want a working configuration
from day one.

**[한국어 README](ko-KR/README.md)**

## Quick Start

1. **Clone this repo** next to your project:

   ```bash
   git clone https://github.com/wlsgur073/Claude-Code-Templates.git
   # Result: your-project/ and Claude-Code-Templates/ are siblings
   ```

2. **Run Claude in your project** and reference the setup prompt with `@`:

   ```
   cd your-project
   claude
   > @../Claude-Code-Templates/setup-prompt.md
   ```

   > `@` imports the file's content into the conversation — Claude reads
   > the setup instructions and follows them automatically.

3. **Choose your path** — Claude asks whether this is a new or existing project:

   | Path | Questions | Generated files |
   | ---- | --------- | --------------- |
   | **New project** | 4 quick questions (tech stack, description, commands, style) | `CLAUDE.md` (5 sections) + `.claude/settings.json` |
   | **Existing project** | 6 questions with auto-detected defaults | `CLAUDE.md` (8 sections) + `.claude/settings.json` + `.claude/rules/*.md` + optional hooks/agents/skills |

4. **Done** — Claude generates all configuration files and prints a summary table.
   Run `/memory` to verify everything loaded correctly.

> **Tip:** Run `/init` in your project first — Claude auto-generates a starter
> CLAUDE.md. Then merge our template to fill gaps `/init` misses.

## What's Inside

```text
Claude-Code-Templates/
├── setup-prompt.md        ← Automated setup prompt (used in Quick Start)
├── starter/               ← Minimal scaffold for beginners (CLAUDE.md + settings.json)
├── advanced/              ← Full scaffold (rules, hooks, agents, skills, statusline)
├── ecosystem/             ← Ready-to-use components catalog (coming soon)
├── examples/starter/      ← Filled starter example (fictional "TaskFlow" project)
├── examples/advanced/     ← Filled advanced example (rules, hooks, agents, skills)
├── guide/                 ← Guides explaining each concept
├── docs/                  ← GitHub community health files (CoC, Contributing, Security)
└── ko-KR/                 ← Korean translations (mirrors root structure)
```

| Directory | Purpose |
| ------------- | --------- |
| `starter/` | Minimal scaffold — 5-section CLAUDE.md + settings.json, for quick setup |
| `advanced/` | Full scaffold — rules, hooks, agents, skills, statusline |
| `ecosystem/` | Ready-to-use skills, hooks, and agents — copy directly into your project |
| `examples/starter/` | Filled starter example — minimal TaskFlow configuration |
| `examples/advanced/` | Filled advanced example — rules, hooks, agents, skills |
| `guide/` | Standalone guides — read any one without the others |
| `ko-KR/` | Korean translations — same structure as root |

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
| [Getting Started](guide/getting-started.md) | Step-by-step setup walkthrough |
| [CLAUDE.md Guide](guide/claude-md-guide.md) | Writing effective CLAUDE.md files |
| [Rules Guide](guide/rules-guide.md) | .claude/rules/ usage and path-scoping |
| [Settings Guide](guide/settings-guide.md) | settings.json configuration |
| [Directory Structure](guide/directory-structure-guide.md) | The .claude/ ecosystem |
| [Effective Usage](guide/effective-usage-guide.md) | Day-one usage patterns |
| [Advanced Features](guide/advanced-features-guide.md) | Hooks, agents, and skills |

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

## Statusline

Customize the Claude Code status bar to show model, context usage, cost, duration, and git branch at a glance:

```
[Opus 4.6 (1M context)] 📁 my-project
 🌿 feature/auth | ████████░░ 80% | $1.25 | ⏱️ 3m 42s
```

**One-line setup:**

```bash
cp Claude-Code-Templates/advanced/statusline.sh ~/.claude/statusline.sh
```

Claude Code automatically detects `~/.claude/statusline.sh` — no additional configuration needed.

> **Prerequisite:** [jq](https://jqlang.org) must be installed (`brew install jq` / `apt install jq` / `choco install jq`).

## Contributing

Contributing? In this repo? Just tell Claude to do it.
...Fine, humans are welcome too. Open an issue or PR.

## License

MIT — see [LICENSE](LICENSE).
