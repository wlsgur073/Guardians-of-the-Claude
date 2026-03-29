# CLAUDE.md

This is a documentation and template repository — it contains no application code, no build system, and no tests. Its purpose is to teach developers how to configure Claude Code for their own projects.

## Repository Structure

- `.claude-plugin/` — Marketplace manifest (makes this repo a plugin marketplace)
- `plugin/` — Plugin package containing `.claude-plugin/plugin.json`, `skills/generate/SKILL.md` (`/claude-code-template:generate`), and `hooks/hooks.json`
- `templates/starter/` — Minimal filled example for TaskFlow (5-section CLAUDE.md + basic settings.json)
- `templates/advanced/` — Full filled example for TaskFlow (rules, hooks, agents, skills)
- `guide/` — Guides covering each Claude Code configuration concept (CLAUDE.md writing, rules, settings, directory structure, effective usage patterns)
- `ko-KR/` — Korean translations (`guide/`, `README.md`)
- `docs/` — GitHub community health files (CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md)
- `.claude/` — This repo's own Claude Code settings

## Contribution Rules

- Templates must all reference the fictional "TaskFlow" project — do not introduce other fictional projects
- Templates (under `templates/`) and guides (under `guide/`) use YAML frontmatter with `title`, `description`, and `date` fields
- Guides in `guide/` should stay under ~130 lines each; they teach conciseness, so they should model it
- This CLAUDE.md should stay under 200 lines, matching the repo's own recommendation in `guide/claude-md-guide.md`
- There is no source code — all content is Markdown. Review for clarity, accuracy, and consistency across files
- When adding a new guide, follow the existing frontmatter format (`title`, `description`, `date`) and add cross-links from `guide/getting-started.md`
- CLAUDE.md files under `templates/` are repo content, not instructions for this repo — Claude will lazy-load them when working in those directories, so keep them clearly framed as examples

## Plugin Development Rules

- Skills go in `plugin/skills/<name>/SKILL.md` — do NOT use `commands/` (legacy)
- Each skill must have YAML frontmatter with `name` and `description` fields
- Plugin version is managed in `plugin/.claude-plugin/plugin.json` only — do NOT duplicate version in `.claude-plugin/marketplace.json`
- Marketplace name (`wlsgur073-plugins`) must NOT match the GitHub repo name case pattern to avoid Windows NTFS rename failures

