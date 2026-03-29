# CLAUDE.md

This is a documentation and template repository — it contains no application code, no build system, and no tests. Its purpose is to teach developers how to configure Claude Code for their own projects.

## Repository Structure

- `.claude-plugin/` — Marketplace manifest (makes this repo a plugin marketplace)
- `plugin/` — Plugin package containing `.claude-plugin/plugin.json` and `commands/generate.md` (`/claude-code-template:generate`)
- `starter/` — Minimal scaffold for beginners (CLAUDE.md with 5 sections + settings.json)
- `advanced/` — Full scaffold including rules, hooks, agents, skills, and statusline
- `ecosystem/` — Ready-to-use components catalog (skills, hooks, agents) — structure only, content coming soon
- `examples/starter/` — Minimal filled example for TaskFlow (5-section CLAUDE.md + basic settings.json)
- `examples/advanced/` — Full filled example for TaskFlow (rules, hooks, agents, skills)
- `guide/` — Guides covering each Claude Code configuration concept (CLAUDE.md writing, rules, settings, directory structure, effective usage patterns)
- `ko-KR/` — Korean translations mirroring the root structure (`starter/`, `advanced/`, `ecosystem/`, `guide/`, `README.md`)
- `docs/` — GitHub community health files (CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md)
- `.claude/` — This repo's own Claude Code settings

## Contribution Rules

- Scaffolds in `starter/` and `advanced/` must remain minimal — section headers and HTML comment placeholders only, no filled-in content
- Examples must all reference the fictional "TaskFlow" project — do not introduce other fictional projects
- Scaffolds (under `starter/`, `advanced/`) have no YAML frontmatter. Examples (under `examples/`) and guides (under `guide/`) use YAML frontmatter with `title`, `description`, and `date` fields
- When modifying files under `starter/`, `advanced/`, or `ecosystem/`, mirror the same changes to `ko-KR/` to maintain Korean translation parity
- `ecosystem/` contains ready-to-use components, not scaffolds — these are meant to be copied directly into projects
- Guides in `guide/` should stay under ~130 lines each; they teach conciseness, so they should model it
- This CLAUDE.md should stay under 200 lines, matching the repo's own recommendation in `guide/claude-md-guide.md`
- There is no source code — all content is Markdown. Review for clarity, accuracy, and consistency across files
- When adding a new guide, follow the existing frontmatter format (`title`, `description`, `date`) and add cross-links from `guide/getting-started.md`
- CLAUDE.md files under `starter/`, `advanced/`, and `examples/` are repo content, not instructions for this repo — Claude will lazy-load them when working in those directories, so keep them clearly framed as examples

## Key Context

- All example configurations reference a fictional "TaskFlow" project — this is intentional and must stay consistent
