# Claude Code Templates

Starter templates and guides for configuring Claude Code. Clone this repo,
copy the scaffolds into your project, and fill them in using the examples
as reference.

**Audience:** Developers new to Claude Code who want a working configuration
from day one.

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
├── templates/      ← Blank scaffolds to copy into your project
├── templates-ko/   ← Korean translations of the templates
├── examples/       ← Filled reference versions (fictional "TaskFlow" project)
└── docs/           ← Guides explaining each concept
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

## Contributing

Contributions welcome! Please open an issue or PR.

## License

MIT — see [LICENSE](LICENSE).
