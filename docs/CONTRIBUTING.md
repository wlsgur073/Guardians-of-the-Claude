# Contributing to Claude Code Template

Thank you for your interest in contributing! This project helps developers configure Claude Code effectively through guides, templates, and examples.

## How This Repo Works

This is a **documentation and template repository** — it contains no application code, no build system, and no tests. All content is Markdown. Contributions focus on improving the quality and clarity of documentation, templates, and examples.

## Types of Contributions

We welcome the following types of contributions:

- **Guide improvements** — Clarify explanations, fix inaccuracies, or add missing details in `guide/`
- **Template improvements** — Expand or refine the TaskFlow examples in `templates/`
- **Translations** — Add or improve Korean translations in `ko-KR/`
- **Typo and grammar fixes** — Always welcome

## Before You Start

Please read the root [`CLAUDE.md`](../CLAUDE.md) file — it contains the detailed contribution rules for this repository, including:

- All templates must reference the fictional "TaskFlow" project
- Templates and guides use YAML frontmatter (`title`, `description`, `date`)
- Guides should stay under ~130 lines

## Getting Started

1. **Fork** this repository
2. **Create a branch** from `main` with a descriptive name (e.g., `docs/fix-settings-guide-typo`)
3. **Make your changes** following the rules in `CLAUDE.md`. Use a branch prefix that matches the commit type (e.g., `feat/`, `fix/`, `docs/`)
4. **Submit a pull request** back to `main`

## Commit Convention

This project follows [Conventional Commits](https://www.conventionalcommits.org/):

```
type: short description
```

| Type | Use for |
|------|---------|
| `feat` | New guides, templates, examples, or significant additions |
| `fix` | Corrections to existing content |
| `docs` | Documentation-only changes (README updates, cross-link fixes) |
| `chore` | Maintenance tasks (.gitignore, file reorganization) |
| `refactor` | Restructuring without changing content meaning |

Keep the subject line concise (under 72 characters). Use the commit body for additional context when needed.

## Pull Request Guidelines

- **One concern per PR** — Keep pull requests focused on a single change
- **Describe your changes** — Explain what you changed and why
- **Reference issues** — Link related issues if applicable (e.g., `Closes #12`)
- **Check cross-references** — If you rename or move files, update all links that point to them
- **Translation parity** — If you modify `templates/`, update `ko-KR/` accordingly

## Code of Conduct

This project follows the [Contributor Covenant 3.0](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.
