<p align="center">
  <img src="assets/banner-v2.svg" alt="Guardians of the Claude" width="700"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-2.9.0-brightgreen.svg" alt="Version">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License"></a>
  <img src="https://img.shields.io/badge/Claude_Code-Plugin-purple.svg" alt="Claude Code Plugin">
  <img src="https://img.shields.io/badge/Skills-4_Commands-orange.svg" alt="4 Skills">
  <a href="https://github.com/wlsgur073/Guardians-of-the-Claude/stargazers"><img src="https://img.shields.io/github/stars/wlsgur073/Guardians-of-the-Claude?style=social" alt="GitHub Stars"></a>
</p>

<p align="center">
  <b>English</b> | <a href="docs/i18n/ko-KR/README.md">한국어</a> | <a href="docs/i18n/ja-JP/README.md">日本語</a>
</p>

Starter templates and guides for configuring Claude Code. Install the
plugin, run `/guardians-of-the-claude:create`, and Claude generates all
configuration files through a guided interview.

**Audience:** Developers new to Claude Code who want a working configuration from day one.

## Philosophy

1. **Verify, don't trust** — Include test, lint, and build commands so Claude checks its own work. This is the single highest-leverage configuration you can make.
2. **Less is more** — Shorter instructions produce better adherence. Each guide stays short enough to read in one sitting.
3. **Specific over vague** — `npm test` not "make sure it works." Every command must be copy-pasteable.
4. **Start simple, grow later** — Two files get you started. Add rules, hooks, agents, and skills when you actually need them.

## Quick Start

1. **Add the marketplace and install the plugin** in Claude Code:

   ```text
   claude
   > /plugin marketplace add wlsgur073/Guardians-of-the-Claude
   > /plugin install guardians-of-the-claude
   ```

2. **Run the setup command** in your project:

   ```text
   cd your-project
   claude
   > /guardians-of-the-claude:create
   ```

   **Alternative methods** (without installing the plugin):

   | Method | Command |
   | ------ | ------- |
   | Local plugin | `claude --plugin-dir /path/to/Guardians-of-the-Claude/plugin` |
   | `@` import | `@../Guardians-of-the-Claude/plugin/skills/create/SKILL.md` |
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
> CLAUDE.md. Then run `/guardians-of-the-claude:create` choosing "Existing project"
> to fill gaps `/init` misses.

## What's Inside

```text
Guardians-of-the-Claude/
├── .claude-plugin/          ← Marketplace manifest (makes this repo a plugin marketplace)
├── plugin/                  ← Plugin package
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── hooks/
│   │   ├── hooks.json       ← SessionStart hook
│   │   └── session-start.sh
│   ├── references/
│   │   ├── security-patterns.md  ← Shared security templates (used by /create and /secure)
│   │   └── learning-system.md   ← Shared learning system reference (used by all skills)
│   └── skills/
│       ├── create/
│       │   ├── SKILL.md     ← Create skill (/guardians-of-the-claude:create)
│       │   ├── references/  ← Generation best practices
│       │   └── templates/   ← Starter & Advanced path instructions
│       ├── audit/
│       │   ├── SKILL.md     ← Audit skill (/guardians-of-the-claude:audit)
│       │   └── references/  ← Scoring model and formulas
│       ├── secure/
│       │   └── SKILL.md     ← Secure skill (/guardians-of-the-claude:secure)
│       └── optimize/
│           └── SKILL.md     ← Optimize skill (/guardians-of-the-claude:optimize)
├── templates/starter/       ← Filled starter example (fictional "TaskFlow" project)
├── templates/advanced/      ← Filled advanced example (rules, hooks, agents, skills)
├── docs/
│   ├── guides/              ← Guides explaining each concept
│   ├── i18n/ko-KR/          ← Korean translations (guides, templates)
│   ├── i18n/ja-JP/          ← Japanese translations (guides, templates)
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
| `docs/i18n/ja-JP/` | Japanese translations (guides, templates) |
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
| 9 | [Recommended Plugins](docs/guides/recommended-plugins-guide.md) | When you want to extend Claude Code |

## Recommended Plugins

Claude Code supports official plugins that extend its capabilities — from full dev workflows to code intelligence. See the **[Recommended Plugins Guide](docs/guides/recommended-plugins-guide.md)** for the full curated list organized by category.

Browse available plugins with `/plugin` in Claude Code, or see [Plugin docs](https://code.claude.com/docs/en/discover-plugins) for details.

## Statusline

Customize the Claude Code status bar to show model, context usage, cost, duration, and git branch at a glance:

```text
[Opus 4.6 (1M context)] 📁 my-project
 🌿 feature/auth | ████████░░ 80% | $1.25 | ⏱️ 3m 42s
```

One-line setup:

```bash
cp Guardians-of-the-Claude/statusline.sh ~/.claude/statusline.sh
```

Claude Code automatically detects `~/.claude/statusline.sh` — no additional configuration needed.

> **Prerequisite:** [jq](https://jqlang.org) must be installed (`brew install jq` / `apt install jq` / `choco install jq`).

## Contributing

Contributing? In this repo? Just tell Claude to do it.
...Fine, humans are welcome too. Open an issue or PR.
See [ROADMAP.md](docs/ROADMAP.md) for the project direction and how to propose changes via [GitHub Discussions](https://github.com/wlsgur073/Guardians-of-the-Claude/discussions).

## License

MIT — see [LICENSE](LICENSE).
