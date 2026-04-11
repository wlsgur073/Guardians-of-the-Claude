<!-- markdownlint-disable-file MD024 -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [2.9.6] - 2026-04-11

### Fixed

- `templates/advanced/.claude/settings.json` (EN + ko-KR): `UserPromptSubmit` hook `timeout` corrected from `5000` to `5`. Claude Code hook `timeout` is specified in **seconds** (per official docs), so the previous value resolved to ~83 minutes instead of the intended 5-second input validation budget.
- `CLAUDE.md`: self-description line corrected — the repo previously claimed "no tests" and "all content is Markdown", contradicting the existing `test/` eval framework, `plugin/hooks/*.sh`, `statusline.sh`, `.github/scripts/*.py`, and CI workflow. Phrasing now mirrors the `docs/CONTRIBUTING.md` fix landed in 2.9.5.
- `CLAUDE.md`: "run the same checks CI runs" softened to "run the same scripts CI runs" with an explicit note that `check-json-schemas.py` degrades to required-field-only checks when schemastore.org is unreachable. Local pass does not guarantee CI pass without network.
- `README.md`, `docs/i18n/ko-KR/README.md`, `docs/i18n/ja-JP/README.md`: statusline one-line install command changed from `cp Guardians-of-the-Claude/statusline.sh …` to `cp ./statusline.sh …`. The absolute folder-name form failed whenever users cloned into a directory with a different name (including this repo's own local checkout as `Claude-Code-Template`).

### Changed

- Hook `timeout` fields added where previously missing, per the "Always set `timeout` explicitly" rule in `docs/guides/advanced-features-guide.md`:
  - `plugin/hooks/hooks.json`: SessionStart hook gets `"timeout": 5`.
  - `templates/advanced/.claude/settings.json` (EN + ko-KR): PreToolUse file-protection gets `"timeout": 5`, PostToolUse ESLint gets `"timeout": 15`.
  - `plugin/skills/create/templates/advanced.md`: generator template for PreToolUse file-protection and PostToolUse auto-linting now includes `timeout`.
  - `docs/guides/advanced-features-guide.md` + ko-KR mirror: JSON example in "Hook Configuration" now shows `timeout` on both hooks. Frontmatter bumped `1.2.1` → `1.2.2`.
- `plugin/.claude-plugin/plugin.json`: version bumped `2.9.5` → `2.9.6`.
- `README.md`: version badge updated `2.9.5` → `2.9.6`.

### Notes

- Addresses Codex audit #2 — five real findings plus one bonus `timeout: 5000` unit bug that Codex missed. `#3` (Windows bash hard dependency on SessionStart hook) left open for a follow-up: the cleaner fix is `"shell": "powershell"` on the hook, which is supported by Claude Code but requires a separate `session-start.ps1` port.
- Change Propagation Checklist followed: EN guide → ko-KR guide, EN template → ko-KR template, EN README → ko-KR + ja-JP README, plugin.json version → README badge, CHANGELOG.

## [2.9.5] - 2026-04-11

### Changed

- `/audit` output format restructured to action-first (`plugin/skills/audit/references/output-format.md`, `plugin/skills/audit/SKILL.md`): Quality Gate and Score now appear at the top, immediately followed by the `★ Most impactful` line, `Top 3 Priorities` list, and `Next step` recommendation. The Score Breakdown, Formula, Detailed Findings, LAV Findings, and All Suggestions move below a `---` separator. Replaces the previous bottom-of-output "Insights & Recommendations" block.
- `plugin/hooks/session-start.sh`: SessionStart staleness check expanded to include common lockfiles (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `poetry.lock`, `uv.lock`, `Cargo.lock`, `Gemfile.lock`, `go.sum`), monorepo workspace configs (`pnpm-workspace.yaml`, `lerna.json`, `nx.json`, `turbo.json`, `rush.json`), and `.mcp.json`. Lockfile-only dependency bumps and workspace-layout edits now trigger a re-audit hint.
- `.github/workflows/docs-check.yml`: `link-check` split into `link-check-internal` (offline, `fail: true`, PR gate) and `link-check-external` (schedule-only, full network check). All JavaScript actions bumped to native Node 24 majors: `actions/checkout@v4` → `v6`, `actions/setup-python@v5` → `v6`, `actions/cache@v4` → `v5`. Composite/Docker actions (`lycheeverse/lychee-action@v2`, `ludeeus/action-shellcheck@master`) are unaffected by the Node runtime transition.
- Windows/bash prerequisite promoted from statusline footnote to the Day 1 install block across `README.md`, `docs/i18n/ko-KR/README.md`, `docs/i18n/ja-JP/README.md`, `docs/guides/getting-started.md`, and `docs/i18n/ko-KR/guides/getting-started.md`. Without Git Bash or WSL, the plugin's SessionStart hook silently exits on bare Windows shells.

### Removed

- `.github/workflows/docs-check.yml`: `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24` workflow-level env var. Introduced earlier in this cycle as a temporary Node 24 runtime bridge, now redundant after bumping all JavaScript actions to native Node 24 majors.

### Fixed

- `docs/i18n/ko-KR/guides/mcp-guide.md`: frontmatter version synced `1.0.2` → `1.0.3` to restore EN/ko-KR parity broken by an earlier commit that bumped EN without mirroring.
- `docs/guides/getting-started.md` + `docs/i18n/ko-KR/guides/getting-started.md`: dead `#quick-start` anchor repaired → `#day-1--2-minute-quickstart` (the actual GitHub auto-anchor for the `## Day 1 — 2-Minute Quickstart` heading). Frontmatter bumped `1.2.1` → `1.2.2` on both files.
- `docs/i18n/ko-KR/guides/getting-started.md`: broken relative path `[templates/README.md](../../../templates/README.md)` corrected to `../../../../templates/README.md`. The three-dot form resolved to `docs/templates/README.md`, which does not exist.
- `docs/i18n/ko-KR/templates/README.md`: broken relative path `[docs/ROADMAP.md](../../../docs/ROADMAP.md)` corrected to `../../../ROADMAP.md`. The previous path double-counted the `docs/` segment, resolving to `docs/docs/ROADMAP.md`.
- `.github/workflows/docs-check.yml`: removed `--base .` from lychee args — v0.23.0 rejects relative base paths, and the exit code 2 was previously swallowed by `fail: ${{ github.event_name == 'schedule' }}`.
- `statusline.sh`: truncated display path now uses `~/.../parent/current` for home-relative paths and `.../parent/current` for absolute paths. Previously prepended `~/**/` unconditionally, misrepresenting non-home locations.
- `docs/CONTRIBUTING.md`: corrected the "no tests" claim — CI runs Python structural checks (frontmatter parity, i18n parity, JSON schema), shellcheck, link checking, and an LLM-output eval framework in `test/`.

## [2.9.4] - 2026-04-10

### Changed

- **`templates/README.md`** (NEW, EN + ko-KR): explicit convention document clarifying that TaskFlow is a fictional reference project, that the current filled templates use Node/Express/TypeScript/PostgreSQL as **one concrete illustration** (not a committed default), and that `/create` adapts to any actual stack at runtime
- `templates/starter/CLAUDE.md` + `advanced/CLAUDE.md` (EN + ko-KR): prepended HTML comment pointing to `templates/README.md` for context — visible in source, hidden in GitHub render
- `docs/ROADMAP.md`: replaced "Template variants" backlog item with "Stack-adaptive improvements" — formalizes the explicit decision to NOT maintain per-stack template variants, and redirects future work toward improving `/create`'s runtime stack adaptation
- `docs/guides/getting-started.md` + ko-KR mirror: Step 2 strengthened with a note explaining the example stack convention and `/create`'s stack-adaptive capability; frontmatter version bumped `1.2.0` → `1.2.1`
- `plugin/.claude-plugin/plugin.json`: version bumped `2.9.3` → `2.9.4`
- `README.md`: version badge updated `2.9.3` → `2.9.4`

### Notes

- Addresses Codex critique #4 ("Node/Express bias") by clarifying positioning rather than adding per-stack template variants
- User reframing: the real problem was not the absence of variants, but the failure to communicate TaskFlow as a fictional reference concept and `/create` as the stack-adaptive mechanism
- Explicit non-goal recorded: per-stack filled template variants will not be added. Future stack-related work (if any) targets `/create` improvements only
- Completes the 4-sub-project response to the Codex critique (A: P0 fixes, B: CI pipeline, C: positioning/meta-system framing, D: TaskFlow stack-neutralization)

## [2.9.3] - 2026-04-10

### Changed

- README.md (EN/ko-KR/ja-JP): restructured around **Day 1 / Day 30 / Day 100+** time-based progression framework — beginners see a 2-minute setup front and center, power users see audit/secure/optimize + meta-system layer as natural growth
- README.md: tagline reframed from "starter templates" to "meta-system for Claude Code configuration"
- README.md Philosophy principle #4: "Start simple, grow later" → "Progressive depth" — explicitly maps to the Day 1/30/100 framework
- README.md: version badge updated `2.9.0` → `2.9.3` (catches up drift from v2.9.1 and v2.9.2 releases)
- `plugin/.claude-plugin/plugin.json`: `version` bumped `2.9.0` → `2.9.3` (catches up missed bumps from v2.9.1 and v2.9.2); `description` reframed to meta-system positioning
- `.claude-plugin/marketplace.json`: plugin `description` reframed to meta-system positioning
- `docs/ROADMAP.md`: Vision expanded from 1 paragraph to 3 paragraphs (Today/Tomorrow framing); new **"North Star — Claude Code Meta System"** section formalizes the long-term direction (progressive disclosure, learning continuity, dual audience, beyond static templates); Backlog gains "Meta-system milestones" item

### Notes

- No code changes, no skill behavior changes, no plugin structure changes — purely positioning and marketing
- Addresses Codex critique #2 ("over-engineered for beginner positioning") by embracing the meta-system identity rather than apologizing for it
- Related to Sub-project A (positioning clarity), Sub-project B (CI pipeline), and Sub-project D (stack diversity — planned)

## [2.9.2] - 2026-04-10

### Added

- GitHub Actions CI pipeline (`.github/workflows/docs-check.yml`) — 6 automated checks preventing documentation drift, i18n mismatches, and schema violations
  - **link-check** (lychee) — internal and external link validation, weekly scheduled run for link rot detection
  - **frontmatter-parity** — ensures EN/ko-KR guide `version:` fields match
  - **json-schema** — validates `settings.json` against schemastore, plus required-field checks for `plugin.json`, `marketplace.json`, `.mcp.json`
  - **i18n-parity** — bidirectional file parity check for `docs/guides/` ↔ `docs/i18n/ko-KR/guides/` and `templates/` ↔ `docs/i18n/ko-KR/templates/`
  - **shellcheck** — validates all shell scripts (`statusline.sh`, `plugin/hooks/*.sh`, `templates/advanced/scripts/*.sh`, and ko-KR mirrors)
  - **encoding-check** — detects U+FFFD replacement characters (catches the class of `보안` corruption fixed in 2.9.1)
- `.github/scripts/` — custom Python scripts for project-specific checks (frontmatter-parity, i18n-parity, json-schemas)
- `.lycheeignore` — URL exclusion list for link check (starts empty)

### Notes

- CI triggers: `push` to main, `pull_request`, weekly `schedule`, manual `workflow_dispatch`
- Link check runs in warning mode on push/PR, strict mode on schedule (external link rot tolerated day-to-day, surfaced weekly)
- All other checks run in strict mode

### Fixed

- `templates/advanced/.claude/settings.json` (EN + ko-KR): `enabledPlugins` changed from `[]` (array, schema violation) to `{}` (empty object per schemastore spec) — pre-existing bug discovered by the new `json-schema` check on its first dry-run, validating the CI's value

## [2.9.1] - 2026-04-10

### Fixed

- `directory-structure-guide.md`: plugin cache description updated from timestamp pattern to `latest-{skill}.md` + `local/` subdirectory (EN + ko-KR, v1.2.1)
- README.md (EN/ko-KR/ja-JP): ja-JP translation claim corrected — only README is translated, guides still in progress
- ko-KR/README.md: encoding corruption restored (`보안` character)
- README.md (EN/ko-KR/ja-JP): Bash/Git Bash prerequisite documented — plugin hooks and advanced templates require Unix-like shell on Windows
- `templates/advanced/.mcp.json` + `mcp-guide.md` Practical Example: hardcoded dev connection string replaced with `${POSTGRES_CONNECTION_STRING}` env var reference (EN + ko-KR, v1.0.2, verified via official Claude Code docs)
- `security-patterns.md`: `Edit(./secrets/)` and `Write(./secrets/)` promoted from Extended to Essential — unconditional write protection for secrets directory (cascades to 6 downstream files)

## [2.9.0] - 2026-04-08

### Added

- Project Learning System — persistent project profiling and decision journaling across all skills
- `plugin/references/learning-system.md` — shared reference for Common Phase 0, Learning Rules, Final Phase, Compaction, and Critical Thinking
- `project-profile.md` — auto-detected project environment stored in `.plugin-cache/local/` (tech stack, structure, configuration state)
- `config-changelog.md` — decision journal with log compaction (200-line budget, Lossless Anchor preservation)
- Learning Rules (CSA pattern): Recommendation Follow-up, Preference Respect, Stagnation Detection, Profile Drift Response
- Critical Thinking & Insight Delivery — Socratic self-verification with anti-sycophancy guidelines
- Same-Day Duplicate handling — multiple runs of the same skill merge into one changelog entry
- SessionStart hook enhanced with 3-case profile detection (no config, no profile, stale)
- `/audit` T3.1: tree diagram parsing — extracts nested paths from `├──`/`└──` characters and inline comments
- `/audit` T3.3: tool config verification — checks ESLint, TypeScript, Vitest config file existence beyond manifest
- `/audit` T3.7: environment variable documentation check — scans `.npmrc`, `.env.example`, `docker-compose.yml`, `Dockerfile` for undocumented `${VAR}` references
- `/audit` LAV (LLM Accuracy Verification) phase — replaces LQM with bidirectional scoring (-9 to +10) that cross-references CLAUDE.md claims against actual project state
- `/audit` LAV L5 (Conciseness) — penalizes redundant, generic, or filler content that wastes LLM context
- `/audit` LAV L6 (Actionability) — rewards copy-paste ready, concrete instructions
- `/audit` LAV improvement suggestions — outputs specific fixes for accuracy issues found
- `/audit` Quality Cap — prevents high mechanical scores from masking LAV-detected quality issues (LAV < 0 → cap = 90 + LAV)
- `/audit` Insights & Recommendations section — educational feedback with prioritized improvements, maturity path guidance, and project-specific tips

### Changed

- All skills: Phase 0 now loads project profile, previous results, and changelog before executing
- All skills: Final Phase now persists results to `local/` directory, updates profile, appends changelog
- `/audit`: reads full changelog for trend analysis; always regenerates profile (Layer 3 stale prevention)
- `/audit` scoring model: v2 → v3 (`LQM` → `LAV`, `max(..., 0)` score floor, Quality Cap, L1–L6 expanded evaluation)
- `/audit` T3 weights redistributed: T3.4 0.15→0.10, T3.5 0.20→0.15, new T3.7 0.10
- `/audit` architecture: monolithic SKILL.md refactored into orchestrator (~120 lines) + on-demand reference files in `references/checks/`
- `/audit` Phase 3.5 suggestions migrated into individual check reference files
- `/audit` output format extracted to `references/output-format.md` for on-demand loading
- `/create`: skips path question when profile already exists; records declined features to changelog
- `/secure`: reads latest-audit for T2 references; resolves audit recommendations when addressed
- `/optimize`: reads latest-audit + latest-secure; respects cross-skill declined items
- File storage: `{timestamp}-{skill}.md` pattern replaced by `latest-{skill}.md` (overwrite, max 7 files)
- Storage path: `.plugin-cache/guardians-of-the-claude/` → `.plugin-cache/guardians-of-the-claude/local/`

### Migration

- Existing `{timestamp}-{skill}.md` files are automatically migrated to `latest-{skill}.md` on first skill run
- Legacy files are cleaned up after migration
- No user action required

## [2.8.1] - 2026-04-06

### Added

- Change Propagation Checklist in CLAUDE.md — documents downstream dependencies when modifying files

### Changed

- `/create` Phase 0: reads `*-secure.md` and `*-optimize.md` to avoid overwriting other skills' changes
- `/audit` Phase 0: reads `*-secure.md` and `*-optimize.md` for change attribution in "Since your last audit"
- `/optimize` Phase 0: reads `*-secure.md` for declined items awareness (prevents re-suggesting)
- `/create` templates: deny patterns expanded from Read-only to full Essential set (Read/Edit/Write for `.env`)
- `security-patterns.md`: `Read(./secrets/)` promoted from Extended to Essential
- `/secure` and `/optimize`: record plugin-cache even when no changes are needed (history chain continuity)

### Fixed

- `security-patterns.md`: missing `Write(./secrets/)` in Extended deny patterns — security gap
- `/secure`: missing `.claude/rules/` directory creation step before writing `security.md`
- `/create` starter: lint command defaults suggested without dependency verification (added Phase 2.5S check)
- Deny pattern format standardized to `Read(./secrets/)` across all files (was inconsistent `Read(secrets/)` / `Read(./secrets/**)`)
- Template `settings.json` deny patterns synced with Essential patterns (EN/KR, 4 files)
- ko-KR `rules-guide.md` version 1.0.1 → 1.0.0 (match EN source)
- ko-KR `advanced-features-guide.md` version 1.2.0 → 1.2.1 + content sync (Script-Based Hooks trimmed)

## [2.8.0] - 2026-04-06

### Added

- `/create` skill — renamed from `/generate` with same functionality, updated memory strategy
- `/secure` skill — fixes security/protection gaps (deny patterns, security rules, file protection hooks)
- `/optimize` skill — improves configuration quality (rules splitting, agent diversity, MCP, hook quality)
- Shared `plugin/references/security-patterns.md` — common security templates for `/create` and `/secure`
- Plugin-cache memory system at `.claude/.plugin-cache/guardians-of-the-claude/` — timestamped Markdown files with 14-day Sliding Window retention
- Skill-aware Next Steps in `/audit` — directs users to `/secure` or `/optimize` based on findings

### Changed

- `/audit` Phase 4: Next Steps now references specific skills instead of generic suggestions
- `/audit` Phase 5: writes to plugin-cache instead of auto-memory (MEMORY.md)
- `/create` Phase 4.5: writes to plugin-cache instead of auto-memory (MEMORY.md)
- `/create` templates: `"Read(secrets/)"` added to default deny patterns (starter + advanced)
- `templates/advanced/.claude/CLAUDE.md`: added auto-discovery behavior note (EN/KR, v1.1.0)
- Hook `session-start.sh`: references `/create` instead of `/generate`
- Plugin description updated to reflect all 4 skills

### Fixed

- `directory-structure-guide.md`: "The Three Systems" → "The Four Systems" to match 4-row table (EN/KR)
- `README.md`: plugin cache added to memory system description (EN/KR)
- ko-KR translation sync: removed extra content not present in English originals (mcp-guide, effective-usage-guide)
- ko-KR translation quality: fixed 9 awkward literal translations across 6 guide files

### Deprecated

- `/generate` skill — redirects to `/create`. Will be removed in next major version.

## [2.7.1] - 2026-04-05

### Fixed

- `/generate` starter command defaults: add C/CMake and C++/CMake rows (were absent from table)
- `/generate` starter: Python install command `pip install -e .` → `pip install -r requirements.txt`
- `/generate` starter: Go lint default `golangci-lint run` → `go vet ./...` (external tool not guaranteed)
- `/generate` starter: Java assumes `mvn` by default, with note to detect wrapper before suggesting `./mvnw`
- `/generate` advanced: remove Node.js-specific passport.js reference from security rule template
- `/audit` T2.2: add SKIP condition for projects with no security-relevant surface (CLI tools, libraries)
- `/audit` T2.1/T2.3: define explicit behavior for malformed/unparseable settings.json

## [2.7.0] - 2026-04-03

### Changed

- `/audit` scoring model redesigned: additive tier-weighted → Foundation-Gated Multiplicative (`Final = min(FG × DS + SB + LQM, 100)`)
- Per-item weights within tiers replace equal weighting — test command (0.35) outweighs build command (0.20) in T1
- Penalty Cap removed — Foundation Gate naturally suppresses scores when foundations are missing
- Quality Gate changed from score-affecting to display-only label
- SKIP paths added to 1.2 test command, 1.3 build command (docs/template repos), 3.1 directory refs, 3.3 command availability
- PARTIAL added to 1.3 build command and 3.3 command availability for complete branching

### Added

- Synergy Bonus (+5 max): rewards complementary item pairs (test+build, sensitive file protection+security rules)
- LLM Quality Modifier (+8 max): constrained content quality judgment (overview accuracy, command executability, non-obvious patterns)
- Audit history includes model version (v2) for cross-version score comparison

## [2.6.0] - 2026-04-03

### Added

- MCP integration guide with Korean translation — configuration, server types, deferred tool loading, security
- Template files: 2 agents (security-reviewer, test-writer), 1 skill (run-checks), hook script (validate-prompt.sh), .mcp.json
- Guide sections: script-based hooks, agent design patterns, skill design patterns, organizing at scale, brownfield adoption
- MCP option in `/generate` and MCP suggestion in `/audit`
- Tiered scoring model for `/audit` — Foundation (50%), Protection (30%), Optimization (20%) with 4-level scale, Quality Gate, Penalty Cap, and Maturity Levels
- Memory integration in `/audit` (saves results) and `/generate` (remembers declined features)
- Philosophy section in README (EN/KO)
- Dispatch tables (skills/agents) in advanced template CLAUDE.md

### Changed

- `/generate` agent template: 2-section → 4-section (Scope/Rules/Constraints/Verification)
- CHANGELOG restored to Keep a Changelog format with concise entries
- ROADMAP simplified: removed Completed table, kept Vision + Backlog
- Guide versions bumped to v1.1.0 (advanced-features, claude-md, getting-started, effective-usage)
- `advanced-features-guide.md` line limit relaxed to ~200

### Fixed

- Dead GitHub Discussions links across 4 files
- Broken relative path in getting-started.md (`../README.md` → `../../README.md`)
- English anchor links in Korean guides restored to Korean anchors
- Korean agent `name` fields restored to English (identifiers)

## [2.5.0] - 2026-04-02

### Added

- Security rules, agent quality, and hook quality checks in `/audit`
- Incremental mode in `/generate` — detects existing config, adds only what's missing
- Self-verification phase (3.5) in `/generate` — validates output before wrapping up
- Model routing guidance (haiku/sonnet/opus) with cost tradeoff notes in advanced features guide
- Security rule file option in `/generate` advanced features

### Changed

- Agent examples: 2-section → 4-section (Scope/Rules/Constraints/Verification)
- Hook examples: added PreToolUse file protection with `exit 2` alongside PostToolUse auto-linting
- YAML model comments (`# sonnet: ...`) for self-documenting agent definitions
- Replaced YAML frontmatter `date` field with independent per-file `version` (semver)
- `/audit` scoring rebalanced to 70/30 (Essential/Alignment)

### Fixed

- Hook exit code `exit 1` → `exit 2` for proper Claude feedback on blocked actions
- Missing YAML frontmatter in 4 Korean rule files

## [2.4.0] - 2026-03-31

### Added

- `/audit` skill for validating Claude Code configuration health with weighted scoring
- `docs/ROADMAP.md` with community-driven proposal process
- `docs/plans/` directory for design and planning documents

### Changed

- Restructured directories: `guide/` → `docs/guides/`, `ko-KR/` → `docs/i18n/ko-KR/`
- Documentation quality audit across 14 files — improved clarity, conciseness, and consistency

### Fixed

- Removed deprecated `allowed-tools` from all skill frontmatter
- Updated stale path references in CONTRIBUTING.md

## [2.3.0] - 2026-03-30

### Added

- Bidirectional safety checks for project type detection in `/generate`
- Auto-routing between starter and advanced paths when project state changes mid-flow

## [2.2.2] - 2026-03-30

### Added

- Development Approach section in starter template

### Fixed

- Plugin conventions aligned with official Claude Code standards
- Template consistency: unified `repos/` directory naming, fixed deny paths

## [2.2.1] - 2026-03-30

### Changed

- Refactored monolithic SKILL.md (393 lines) into modular subdirectories: `templates/starter.md`, `templates/advanced.md`, `references/best-practices.md`

## [2.2.0] - 2026-03-29

### Added

- SessionStart hook system (`hooks.json` + `session-start.sh`)
- Plugin marketplace metadata enrichment ($schema, keywords, homepage)
- Privacy policy (`docs/PRIVACY.md`) for marketplace submission

### Changed

- Major directory restructure: `starter/`, `advanced/`, `ecosystem/` → `templates/`

## [2.1.0] - 2026-03-28

### Added

- Plugin marketplace integration with `/generate` command
- Starter/advanced path branching with empty project detection

### Changed

- Renamed command from `/setup` to `/generate`

### Fixed

- Windows case-insensitive marketplace naming issue (NTFS rename failure)

## [2.0.0] - 2026-03-27

### Added

- 3-Tier architecture: `guide/` (education) + `templates/` (examples) + `plugin/` (automation)
- Community health files: CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md
- Korean translations for all 7 guides and README

### Changed

- **Breaking:** Refactored `docs/` → `guide/` to reserve `docs/` for GitHub community health files

## [1.0.0] - 2026-03-27 [DEPRECATED]

> **Deprecated:** v1.0.0 is no longer supported. Please use v2.4.0 or later.

- Initial release with 7 configuration guides
- Starter and advanced CLAUDE.md templates for TaskFlow
- Basic plugin structure with Claude Code integration
