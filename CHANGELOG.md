<!-- markdownlint-disable-file MD024 -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Model routing guidance table (haiku/sonnet/opus) in advanced features guide
- `UserPromptSubmit` hook event explanation in guide and key concepts

### Changed

- Restructured agent example from 2-section (Scope/Rules) to 4-section pattern (Scope/Rules/Constraints/Verification)
- Expanded hook examples from single PostToolUse to PreToolUse + PostToolUse with file protection pattern
- Added YAML model comment pattern (`# sonnet: ...`) for self-documenting agent definitions
- Aligned hook order (PreToolUse → PostToolUse) between guide and template
- Relaxed `advanced-features-guide.md` line limit from ~130 to ~160 (now 157 lines)
- Korean translations synced for advanced features guide, agent template, and settings

### Fixed

- Hook exit code `exit 1` → `exit 2` for proper Claude feedback on blocked actions
- Added `migrations/` and `package-lock.json` to hook file protection pattern in guide
- Agent template heading `# Scope` → `## Scope` for markdownlint MD025 compliance

## [2.4.0] - 2026-03-31

### Added

- `/audit` skill for validating Claude Code configuration health (`plugin/skills/audit/SKILL.md`)
- `docs/ROADMAP.md` with governance process for community-driven roadmap proposals
- Roadmap proposals section in `docs/CONTRIBUTING.md`
- `docs/plans/` for design and planning documents

### Changed

- Restructured directories: `guide/` → `docs/guides/`, `ko-KR/` → `docs/i18n/ko-KR/`
- Cross-references from advanced features guide to template examples (agents, skills)
- Korean translations for all template files (`ko-KR/templates/`)
- Removed Current Priorities section from ROADMAP.md
- Documentation quality audit: improved clarity, conciseness, accuracy, and consistency across 14 files
- Trimmed `advanced-features-guide.md` to meet 130-line guide limit (144 → 128)
- Normalized em-dash style (`—` → `--`) across all guides
- Unified frontmatter date format (quoted → unquoted) across templates

### Fixed

- Removed deprecated `allowed-tools` from all skill frontmatter
- Updated stale `ko-KR/` path references in CONTRIBUTING.md
- Added missing `/audit` skill references to README.md and CLAUDE.md
- Removed redundant explanations in directory-structure-guide.md and CONTRIBUTING.md

## [2.3.0] - 2026-03-30

### Added

- Bidirectional safety checks for project type detection in generate skill
- Enhanced skill patterns with auto-routing between starter and advanced paths

## [2.2.2] - 2026-03-30

### Fixed

- Plugin conventions aligned with official Claude Code standards
- Template consistency: unified `repos/` directory naming, fixed deny paths

### Added

- `allowed-tools` convention documented in CLAUDE.md
- Development Approach section added to starter template

## [2.2.1] - 2026-03-30

### Changed

- Refactored monolithic SKILL.md (393 lines) into modular subdirectories
  - `templates/starter.md` — starter path instructions
  - `templates/advanced.md` — advanced path instructions
  - `references/best-practices.md` — generation quality standards

## [2.2.0] - 2026-03-29

### Changed

- Major directory restructure: `starter/`, `advanced/`, `ecosystem/` → `templates/`
- Moved `statusline.sh` to repository root

### Added

- SessionStart hook system (`hooks.json` + `session-start.sh`)
- Plugin metadata enrichment: `$schema`, keywords, homepage, tools frontmatter
- Privacy policy (`docs/PRIVACY.md`) for plugin marketplace submission

## [2.1.0] - 2026-03-28

### Added

- Plugin marketplace integration with `/generate` command
- Starter/advanced path branching with empty project support
- Automated setup prompt for one-step project configuration

### Fixed

- Windows case-insensitive marketplace naming issue (NTFS rename failure)

### Changed

- Renamed command from `/setup` to `/generate`

## [2.0.0] - 2026-03-27

### Added

- 3-Tier architecture: `guide/` (education) + `templates/` (examples) + `plugin/` (automation)
- Community health files: CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md
- Korean translations for all 7 guides and README (`ko-KR/`)
- Korean statusline template

### Changed

- **Breaking:** Refactored `docs/` → `guide/` to reserve `docs/` for GitHub community health files
- Replaced cost display with 5-hour rate limit bar in statusline

## [1.0.0] - 2026-03-27 [DEPRECATED]

> **Deprecated:** v1.0.0 is no longer supported. The directory structure, plugin system, and usage workflow changed significantly in v2.0.0. Please use v2.4.0 or later.

### Added

- Initial release with 7 configuration guides
- Starter and advanced CLAUDE.md templates for TaskFlow
- Basic plugin structure with Claude Code integration
- `.gitattributes` to enforce LF line endings
