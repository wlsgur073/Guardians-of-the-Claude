# CLAUDE.md

This is a documentation and template repository — it contains no application code, no build system, and no tests. Its purpose is to teach developers how to configure Claude Code for their own projects.

# Repository Structure

- `docs/` — Guides covering each Claude Code configuration concept (CLAUDE.md writing, rules, settings, directory structure, effective usage patterns)
- `templates/` — Minimal scaffolds with placeholder comments, meant to be copied into other projects
- `templates-ko/` — Korean translation of `templates/`, same structure and format
- `examples/` — Filled-out configuration for a fictional "TaskFlow" Node.js/Express project, demonstrating what completed templates look like
- `.claude/` — This repo's own Claude Code settings

# Contribution Rules

- Templates must remain minimal scaffolds — section headers and HTML comment placeholders only, no filled-in content
- Examples must all reference the fictional "TaskFlow" project — do not introduce other fictional projects
- Guides in `docs/` should stay under ~130 lines each; they teach conciseness, so they should model it
- This CLAUDE.md should stay under 200 lines, matching the repo's own recommendation in `docs/claude-md-guide.md`
- There is no source code — all content is Markdown. Review for clarity, accuracy, and consistency across files
- When adding a new guide, follow the existing frontmatter format (`title`, `description`, `date`) and add cross-links from `docs/getting-started.md`
- CLAUDE.md files under `templates/` and `examples/` are repo content, not instructions for this repo — Claude will lazy-load them when working in those directories, so keep them clearly framed as examples

# Key Context

- `settings.local.json` uses `"outputStyle": "Learning"` — this repo is configured for educational interaction
- The `docs/superpowers/` directory contains the original plan and design spec for this repository
- All example configurations reference a fictional "TaskFlow" project — this is intentional and must stay consistent
