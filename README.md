<p align="center">
  <img src="assets/banner.svg" alt="Claude Code Template" width="700"/>
</p>

Starter templates and guides for configuring Claude Code. Install the
plugin, run `/claude-code-template:create`, and Claude generates all
configuration files through a guided interview.

**Audience:** Developers new to Claude Code who want a working configuration
from day one.

**[한국어 README](docs/i18n/ko-KR/README.md)**

## Philosophy

1. **Verify, don't trust** — Include test, lint, and build commands so Claude checks its own work. This is the single highest-leverage configuration you can make.
2. **Less is more** — Shorter instructions produce better adherence. Each guide stays short enough to read in one sitting.
3. **Specific over vague** — `npm test` not "make sure it works." Every command must be copy-pasteable.
4. **Start simple, grow later** — Two files get you started. Add rules, hooks, agents, and skills when you actually need them.

## Quick Start

1. **Add the marketplace and install the plugin** in Claude Code:

   ```text
   claude
   > /plugin marketplace add wlsgur073/Claude-Code-Template
   > /plugin install claude-code-template@wlsgur073-plugins
   ```

2. **Run the setup command** in your project:

   ```text
   cd your-project
   claude
   > /claude-code-template:create
   ```

   **Alternative methods** (without installing the plugin):

   | Method | Command |
   | ------ | ------- |
   | Local plugin | `claude --plugin-dir /path/to/Claude-Code-Template/plugin` |
   | `@` import | `@../Claude-Code-Template/plugin/skills/create/SKILL.md` |
   | Direct paste | Copy the contents of `plugin/skills/create/SKILL.md` and paste directly into the conversation |

3. **Choose your path** — Claude detects your project state and asks what to do:

   | Path | When | What happens |
   | ---- | ---- | ------------ |
   | **New project** | No code yet | 4 quick questions → `CLAUDE.md` (6 sections) + `.claude/settings.json` |
   | **Existing project** | Code exists, no Claude config | 6 questions with auto-detected defaults → full config (CLAUDE.md + settings + rules + optional hooks/agents/skills) |
   | **Add missing features** | Config already exists | Scans current setup, shows what's configured vs missing, lets you add only what you need |

   > **Already have a config?** Claude auto-detects it and offers to add missing features without re-answering questions you've already covered.
   > **Picked the wrong path?** No worries — Claude detects mismatches and suggests switching automatically.

4. **Done** — Claude generates all configuration files and prints a summary table.
   Run `/memory` to verify everything loaded correctly.

5. **Next step (optional)** — Install the `claude-code-setup` plugin to get
   tailored recommendations for MCP servers, hooks, and skills based on your stack.

> **Tip:** Run `/init` in your project first — Claude auto-generates a starter
> CLAUDE.md. Then run `/claude-code-template:create` choosing "Existing project"
> to fill gaps `/init` misses.

## What's Inside

```text
Claude-Code-Template/
├── .claude-plugin/          ← Marketplace manifest (makes this repo a plugin marketplace)
├── plugin/                  ← Plugin package
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── hooks/
│   │   ├── hooks.json       ← SessionStart hook
│   │   └── session-start.sh
│   ├── references/
│   │   └── security-patterns.md  ← Shared security templates (used by /create and /secure)
│   └── skills/
│       ├── create/
│       │   ├── SKILL.md     ← Create skill (/claude-code-template:create)
│       │   ├── references/  ← Generation best practices
│       │   └── templates/   ← Starter & Advanced path instructions
│       ├── audit/
│       │   ├── SKILL.md     ← Audit skill (/claude-code-template:audit)
│       │   └── references/  ← Scoring model and formulas
│       ├── secure/
│       │   └── SKILL.md     ← Secure skill (/claude-code-template:secure)
│       ├── optimize/
│       │   └── SKILL.md     ← Optimize skill (/claude-code-template:optimize)
│       └── generate/
│           └── SKILL.md     ← Deprecated — redirects to /create
├── templates/starter/       ← Filled starter example (fictional "TaskFlow" project)
├── templates/advanced/      ← Filled advanced example (rules, hooks, agents, skills)
├── docs/
│   ├── guides/              ← Guides explaining each concept
│   ├── i18n/ko-KR/          ← Korean translations (guides, templates)
│   ├── plans/               ← Design and planning documents
│   └── *.md                 ← Community health files and project roadmap
└── CHANGELOG.md             ← Version history (Keep a Changelog format)
```

| Directory | Purpose |
| ------------- | --------- |
| `templates/starter/` | Filled starter example — minimal TaskFlow configuration |
| `templates/advanced/` | Filled advanced example — rules, hooks, agents, skills |
| `docs/guides/` | Standalone guides — read any one without the others |
| `docs/i18n/ko-KR/` | Korean translations (guides, templates) |
| `docs/plans/` | Design and planning documents |
| `docs/*.md` | Community health files and project [roadmap](docs/ROADMAP.md) |

## How Claude Code Memory Works

Claude Code uses a layered memory system: CLAUDE.md (your instructions), `.claude/rules/` (modular rule files), auto memory (Claude's own notes), and plugin cache (plugin-managed state). See the [Directory Structure Guide](docs/guides/directory-structure-guide.md) for details.

> **The #1 Rule:** Give Claude a way to verify its work — include test commands,
> lint commands, and build commands in your CLAUDE.md. This is the single
> highest-leverage thing you can do.

## Docs

Start here, then follow the path that matches your level:

| Step | Guide | Who needs it |
| ---- | ----- | ------------ |
| 1 | [Getting Started](docs/guides/getting-started.md) | Everyone — setup walkthrough |
| 2 | [CLAUDE.md Guide](docs/guides/claude-md-guide.md) | Everyone — writing effective instructions |
| 3 | [Settings Guide](docs/guides/settings-guide.md) | Everyone — permissions and preferences |
| 4 | [Rules Guide](docs/guides/rules-guide.md) | When CLAUDE.md exceeds ~100 lines |
| 5 | [Directory Structure](docs/guides/directory-structure-guide.md) | When you want to understand `.claude/` |
| 6 | [Effective Usage](docs/guides/effective-usage-guide.md) | After your first day with Claude Code |
| 7 | [Advanced Features](docs/guides/advanced-features-guide.md) | When you need hooks, agents, or skills |
| 8 | [MCP Integration](docs/guides/mcp-guide.md) | When you want to connect external tools |

## Recommended Plugins

Claude Code supports official plugins that extend its capabilities.
Browse available plugins with `/plugin` in Claude Code, or see
[Plugin docs](https://code.claude.com/docs/en/discover-plugins) for details.

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

```text
[Opus 4.6 (1M context)] 📁 my-project
 🌿 feature/auth | ████████░░ 80% | $1.25 | ⏱️ 3m 42s
```

**One-line setup:**

```bash
cp Claude-Code-Template/statusline.sh ~/.claude/statusline.sh
```

Claude Code automatically detects `~/.claude/statusline.sh` — no additional configuration needed.

> **Prerequisite:** [jq](https://jqlang.org) must be installed (`brew install jq` / `apt install jq` / `choco install jq`).

## Contributing

Contributing? In this repo? Just tell Claude to do it.
...Fine, humans are welcome too. Open an issue or PR.
See [ROADMAP.md](docs/ROADMAP.md) for the project direction and how to propose changes via [GitHub Discussions](https://github.com/wlsgur073/Claude-Code-Template/discussions).

## License

MIT — see [LICENSE](LICENSE).
