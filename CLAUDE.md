# CLAUDE.md
<!-- Last reviewed: 2026-04-22 -->

This is a documentation and template repository — no application source code and no runtime build system, but CI validates it via Python structural checks (frontmatter parity, i18n parity, JSON schemas), shellcheck, link checking, and an LLM-output eval framework in `test/`. Its purpose is to teach developers how to configure Claude Code for their own projects.

## Repository Structure

- `.claude-plugin/` — Marketplace manifest (makes this repo a plugin marketplace)
- `plugin/` — Plugin package containing `.claude-plugin/plugin.json`, `skills/create/SKILL.md` (`/guardians-of-the-claude:create`), `skills/audit/SKILL.md` (`/guardians-of-the-claude:audit`), `skills/secure/SKILL.md` (`/guardians-of-the-claude:secure`), `skills/optimize/SKILL.md` (`/guardians-of-the-claude:optimize`), `references/security-patterns.md` (shared), `references/learning-system.md` (shared), and `hooks/hooks.json`
- `CHANGELOG.md` — Version history in Keep a Changelog format
- `templates/starter/` — Minimal filled example for TaskFlow (6-section CLAUDE.md + basic settings.json)
- `templates/advanced/` — Full filled example for TaskFlow (rules, hooks, agents, skills, MCP)
- `docs/guides/` — Guides covering each Claude Code configuration concept (CLAUDE.md writing, rules, settings, directory structure, effective usage patterns, advanced features, MCP integration, recommended plugins)
- `docs/i18n/ko-KR/` — Korean translations (`guides/`, `templates/`, `README.md`)
- `docs/i18n/ja-JP/` — Japanese translations (`guides/`, `templates/`, `README.md`)
- `docs/plans/` — Design and planning documents for feature work
- `docs/*.md` — GitHub community health files and project governance (CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md, PRIVACY.md, ROADMAP.md)
- `.claude/` — This repo's own Claude Code settings
- `test/` — Skill evaluation framework (rubrics, scenarios, fixtures, scripts) and results. Not a unit test suite — used to grade skill output quality. See `test/testing-strategy.md`.
- `ci/` — CI smoke lane: fixtures, golden snapshots, and scripts for plugin regression testing (run by `.github/workflows/smoke.yml`; shipped, unlike gitignored `test/`). Template clone users can ignore; plugin contributors who change skill output must update fixtures/goldens. See `ci/README.md`.
- `.github/workflows/docs-check.yml` — CI with 17 jobs (link-check-internal, link-check-external, frontmatter-parity, json-schema, registry-lint, skill-stability-lint, i18n-parity, shellcheck, encoding-check, preflight-schema, scoring-formula-simulation, scoring-model-lav-linkage, changelog-parser-check, sample-list-preconditions, audit-goldens-check, audit-drift-aware-check, scoring-contract-consistency). Python validators live in `.github/scripts/`.
- `.github/workflows/smoke.yml` — CI smoke lane (2 jobs: smoke fixtures, verifier drift tripwire); triggers on PRs touching `plugin/**`/`templates/**`/`ci/**` and on version tags.

## Contribution Rules

- Templates must all reference the fictional "TaskFlow" project — do not introduce other fictional projects
- Templates (under `templates/`) and guides (under `docs/guides/`) use YAML frontmatter with `title`, `description`, and `version` fields — each file has its own independent semver starting from `1.0.0`; bump the version when modifying the file's content
- Guides in `docs/guides/` should stay concise — most under ~130 lines, `advanced-features-guide.md` under ~200 (covers 3 topics with code examples)
- This CLAUDE.md should stay under 200 lines, matching the repo's own recommendation in `docs/guides/claude-md-guide.md`
- There is no application source code — primary content is Markdown, supported by JSON/YAML configs, shell scripts (`plugin/hooks/*.sh`, `statusline.sh`, `templates/advanced/scripts/*.sh`), and Python CI validators in `.github/scripts/`. Review for clarity, accuracy, and consistency across files
- When adding a new guide, follow the existing frontmatter format (`title`, `description`, `version`) and add cross-links from `docs/guides/getting-started.md`
- CLAUDE.md files under `templates/` are repo content, not instructions for this repo — Claude will lazy-load them when working in those directories, so keep them clearly framed as examples
- `/test/` is gitignored (`.gitignore:21`) — internal eval docs and local tooling live there but do not ship. Edits under `test/` are local-only; do not add CHANGELOG entries for `test/*` changes. CI-visible validation belongs in `.github/scripts/*.py`.
- `ci/` is shipped (CI smoke lane for plugin regression) — skill-output changes must update `ci/fixtures/` and re-freeze `ci/golden/`; CHANGELOG entries apply to user-visible `ci/` changes (unlike local-only `test/*`).
- `ci/fixtures/**` and `ci/golden/**` are CI test inputs/snapshots — legacy-state fixtures intentionally preserve pre-migration artifacts (e.g., `project-profile.md` "5 sections" for migration scenarios). Do not normalize to current canonical; these files exist to verify migration semantics.

### Change Propagation Checklist

A single change can ripple across the repo. When modifying any file, check downstream:

- **`security-patterns.md`** → `/create` templates (`starter.md`, `advanced.md`) → filled examples (`templates/*/settings.json` EN + ko-KR + ja-JP, 6 files)
- **`docs/guides/*.md`** → `docs/i18n/ko-KR/guides/*.md` and `docs/i18n/ja-JP/guides/*.md` — sync content + match frontmatter `version`
- **`templates/starter/` or `advanced/`** → `docs/i18n/ko-KR/templates/` and `docs/i18n/ja-JP/templates/` — mirror structure and content
- **Skill SKILL.md** (behavior change) → verify other skills' Phase 0 reading scope still covers the change; update `CHANGELOG.md`
- **Deny pattern format change** → grep `Read\(.*secrets` or similar across all files to ensure consistency
- **Root `README.md` → i18n mirrors** (ko-KR, ja-JP): sync content + language switcher, but NOT the badge row (version/license/status badges are language-neutral, EN-only by design — absence in translations is not drift)
- **i18n frontmatter `version:` bump semantics:** bump when new content is added/translated, NOT when fixing drift to restore parity with EN (drift fixes return already-agreed content to parity — no semantic change)

### Verifying Changes Locally

Before pushing, run the same scripts CI runs. Note: `check-json-schemas.py` fetches the Claude Code settings schema from schemastore.org and degrades to required-field-only checks on network failure, so full schema validation locally requires connectivity. First-time setup: `pip install pyyaml==6.0.2 jsonschema==4.23.0 requests==2.32.3`

- `python .github/scripts/check-frontmatter-parity.py` — confirms EN and i18n files have matching `version` fields
- `python .github/scripts/check-i18n-parity.py` — confirms i18n directories mirror EN structure (stdlib only)
- `python .github/scripts/check-json-schemas.py` — validates `plugin.json`, `marketplace.json`, `settings.json` schemas
- `lychee 'README.md' 'docs/**/*.md' 'plugin/**/*.md' 'CHANGELOG.md' 'templates/**/*.md'` — link check (requires [lychee](https://github.com/lycheeverse/lychee))
- Python inline scripts on Windows: prepend `import sys; sys.stdout.reconfigure(encoding="utf-8")` before printing non-ASCII / U+FFFD / mixed CJK — default `cp949` codec raises `UnicodeEncodeError`

### Release Process

- **SemVer:** patch (z) for fixes and platform-compat work (e.g., adding a `.ps1` companion to an existing `.sh` hook — no new user-callable surface); minor (y) only when adding user-callable surface (new skill, new SKILL.md frontmatter field, new template variant, new `/audit` flag); major (x) for breaking contract changes
- **GitHub Release title:** version only (`vX.Y.Z`) — no subtitle or theme. **Body:** `## Highlights` section with 3–5 short pointer bullets summarizing the release, followed by `**Full details:** [CHANGELOG — vX.Y.Z](<anchor URL>)`. CHANGELOG.md remains the source of truth for full rationale, validation, and notes — the release body is intentionally minimal to avoid redundancy. No `## Summary` prose, no self-curated "What's new" headers, no emojis. Anchor URL format: `https://github.com/<owner>/<repo>/blob/main/CHANGELOG.md#<slug>` where `<slug>` is the GitHub slug of `[X.Y.Z] - YYYY-MM-DD` (drop `[`, `]`, `.`; spaces → hyphens; lowercase). Past releases set the pattern: `gh release view <prev> --json name,body`
- **`gh release` with markdown body:** HEREDOC breaks on backticks and special chars in markdown — always write notes to a temp file and pass with `-F <file>`, then delete the file. Full sequence: stage specific files → commit → `git tag vX.Y.Z` → push commits → push tag → `gh release create vX.Y.Z --title "vX.Y.Z" -F notes.md`
- **CHANGELOG `## [Unreleased]` bucket:** post-release docs/i18n fixes accumulate in a `## [Unreleased]` section at the top of CHANGELOG. Each fix commit includes its own Unreleased entry (atomic, self-describing). At next patch release, rename `## [Unreleased]` → `## [X.Y.Z] - YYYY-MM-DD`. Promote triggers: security-adjacent fix lands → release immediately; 5+ accumulated items or 30+ days stale → suggest release.

## Plugin Development Rules

- Skills go in `plugin/skills/<name>/SKILL.md` — do NOT use `commands/` (legacy)
- Each skill must have YAML frontmatter with `name` and `description` fields
- `allowed-tools` is no longer supported in skill frontmatter; agents use `tools` for tool restriction
- Plugin version is managed in `plugin/.claude-plugin/plugin.json` only — do NOT duplicate version in `.claude-plugin/marketplace.json`
- Marketplace name (`guardians`) must NOT match the GitHub repo name case pattern to avoid Windows NTFS rename failures
