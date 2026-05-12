# CLAUDE.md
<!-- Last reviewed: 2026-05-11 -->

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
- `docs/*.md` — GitHub community health files and project governance (CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md, PRIVACY.md, ROADMAP.md)
- `.claude/` — This repo's own Claude Code settings
- `.claude/.plugin-cache/<plugin-name>/local/` — plugin-managed state (`recommendations.json`, `profile.json`, `state-summary.md`, `config-changelog.md`). Read for status (`PENDING`/`RESOLVED`/`DECLINED`/`decline_count`); do NOT manually edit (plugin auto-updates on next skill invocation via `issued_by`/`resolver` matching).
- `test/` — Skill evaluation framework (rubrics, scenarios, fixtures, scripts) and results. Not a unit test suite — used to grade skill output quality. See `test/testing-strategy.md`.
- `ci/` — CI smoke lane: fixtures, golden snapshots, and scripts for plugin regression testing (run by `.github/workflows/smoke.yml`; shipped, unlike gitignored `test/`). Template clone users can ignore; plugin contributors who change skill output must update fixtures/goldens. See `ci/README.md`.
- `.github/workflows/docs-check.yml` — CI with 22 jobs (link-check-internal, link-check-external, frontmatter-parity, json-schema, registry-lint, skill-stability-lint, i18n-parity, shellcheck, encoding-check, preflight-schema, scoring-formula-simulation, scoring-model-lav-linkage, changelog-parser-check, audit-goldens-check, audit-drift-aware-check, scoring-contract-consistency, detection-probe-check, qa-report-shape-check, hook-script-parity, readme-badge-sync, tag-sha-propagation, changelog-anchor-slug). Python validators live in `.github/scripts/`.
- `.github/workflows/smoke.yml` — CI smoke lane (2 jobs: smoke fixtures, verifier drift tripwire); triggers on PRs touching `plugin/**`/`templates/**`/`ci/**` and on version tags.

## Contribution Rules

- Templates must all reference the fictional "TaskFlow" project — do not introduce other fictional projects
- Templates (under `templates/`) and guides (under `docs/guides/`) use YAML frontmatter with `title`, `description`, and `version` fields — each file has its own independent semver starting from `1.0.0`; bump the version when modifying the file's content
- Guides in `docs/guides/` should stay concise — most under ~130 lines, `advanced-features-guide.md` under ~210 (covers 3 topics with code examples; widened from ~200 since 4 lines of nav links push the floor; Anthropic's 200-line target applies to CLAUDE.md, not guides)
- This CLAUDE.md should stay under 200 lines, matching the repo's own recommendation in `docs/guides/claude-md-guide.md`
- There is no application source code — primary content is Markdown, supported by JSON/YAML configs, shell scripts (`plugin/hooks/*.sh`, `statusline.sh`, `templates/advanced/hooks/*.sh`), and Python CI validators in `.github/scripts/`. Review for clarity, accuracy, and consistency across files
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
- **i18n single-mirror review findings → cross-mirror check first** — when an agent reviews ko-KR or ja-JP only and surfaces a finding, check whether the *other* mirror has the identical pattern before fixing. Single-mirror fix creates new ko-KR ↔ ja-JP divergence; either fix both or document as cross-mirror design intent (memory closure pattern)
- **`templates/` path/structural rename** → grep `CLAUDE.md` `Repository Structure` for stale path mentions (`*.sh` lists, dir paths); CLAUDE.md is consistently missed as a cascade target

### Verifying Changes Locally

Before pushing, run the same scripts CI runs. Note: `check-json-schemas.py` fetches the Claude Code settings schema from schemastore.org and degrades to required-field-only checks on network failure, so full schema validation locally requires connectivity. First-time setup: `pip install pyyaml==6.0.2 jsonschema==4.23.0 referencing==0.37.0 requests==2.32.3`

- `python .github/scripts/check-frontmatter-parity.py` — confirms EN and i18n files have matching `version` fields
- `python .github/scripts/check-i18n-parity.py` — confirms i18n directories mirror EN structure (stdlib only)
- `python .github/scripts/check-json-schemas.py` — validates `plugin.json`, `marketplace.json`, `settings.json` schemas
- `lychee 'README.md' 'docs/**/*.md' 'plugin/**/*.md' 'CHANGELOG.md' 'templates/**/*.md'` — link check (requires [lychee](https://github.com/lycheeverse/lychee))
- `SMOKE_PINNED_UTC="2026-04-14T00:00:00Z" python .github/scripts/check-smoke-fixtures.py` — smoke fixture byte-diff verifier (env var required, value matches `.github/workflows/smoke.yml`)
- Python on Windows: prepend `import sys; sys.stdout.reconfigure(encoding="utf-8")` before printing non-ASCII / U+FFFD / mixed CJK; use `open(path, encoding='utf-8')` for files with em-dashes / non-ASCII (e.g., schema descriptions) — default `cp949` codec raises `UnicodeEncodeError` / `UnicodeDecodeError`
- **All 11 Python validators must pass GREEN before tag/push** (release-time sweep):
  - 6 routine (run on every push/PR via docs-check): `check-frontmatter-parity.py`, `check-i18n-parity.py`, `check-json-schemas.py`, `check-smoke-fixtures.py`, `check-readme-badge-sync.py`, `check-changelog-anchor-slug.py`
  - 5 release-only (manual or release-flow): `check-recommendation-registry.py`, `check-skill-stability.py`, `check-qa-report-shape.py`, `check-hook-script-parity.py`, `check-tag-sha-propagation.py` (post-tag-push only)
  - `lychee` link checker is a separate non-Python tool, NOT counted in the "All 11"
- `jsonschema.Draft202012Validator` does NOT enforce `format` keyword by default — pass `format_checker=FormatChecker()` with a custom checker registered (`.github/scripts/check-json-schemas.py:_FORMAT_CHECKER` shows the stdlib-only `datetime.fromisoformat` pattern that avoids the `jsonschema[format]` extra / `rfc3339-validator` dependency).
- **Agent review findings about external facts** (GitHub Actions versions, package availability, transitive deps, "dead code" claims) reflect agent training cutoff and may be wrong — verify with `gh api`, `pip show`, or `grep` for module callers before propagating to commits. Agent claims about *file content this repo owns* are typically reliable; *external/version claims* are not.
- `check-hook-script-parity.py` validates *byte-equal i18n locale mirrors* (EN ↔ ko-KR ↔ ja-JP) of hook scripts, NOT sh ↔ ps1 *behavioral* parity (output equivalence on same input). Behavioral divergence between sh and ps1 implementations escapes CI — when modifying either side, manually cross-check the sibling against the same input scenarios.

**Cross-platform shell/fixture gotchas** (encountered when authoring hook scripts or extending the smoke runner):

- `< /dev/stdin` does NOT exist on Git Bash. Hook scripts reading **SessionStart-style JSON payloads through jq** should use jq's default stdin (`jq -r '.field' 2>/dev/null`) without redirection. The whole-stdin `cat` / `[Console]::In.ReadToEnd()` pattern used by `UserPromptSubmit` / `Stop` / `SubagentStop` / `PreCompact` hooks is a separate, valid pattern (no jq pipeline involved) — this rule applies only when piping stdin through jq.
- `subprocess.stdout` preserves source line endings (CRLF on Git Bash); `Path.read_text(encoding='utf-8')` uses universal newlines (CRLF→LF). Normalize both sides via `.replace("\r\n", "\n").strip()` before byte comparison.
- Windows `bash` via PATH may resolve to WSL bash (fails with Hyper-V error if virtualization disabled). Python subprocess invoking shell should prefer explicit Git Bash path (`C:\Program Files\Git\bin\bash.exe`) — see `_find_bash()` in `.github/scripts/check-smoke-fixtures.py`.
- CI fixtures requiring file mtime ordering (e.g., `legacy_mtime` drift trigger in `ci/fixtures/sessionstart-orchestrator/`): git checkout does NOT preserve mtimes. Each such fixture ships `setup.sh` with `touch -t YYYYMMDDHHMM <file>`; the smoke runner sources it before invoking the hook.
- jq `fromdateiso8601` accepts `Z` suffix directly. Do NOT pre-convert via `sub("Z$"; "+00:00")` — some jq builds reject the offset format.

### Release Process

- **SemVer:** patch (z) for fixes and platform-compat work (e.g., adding a `.ps1` companion to an existing `.sh` hook — no new user-callable surface); minor (y) only when adding user-callable surface (new skill, new SKILL.md frontmatter field, new template variant, new `/audit` flag); major (x) for breaking contract changes
- **GitHub Release title:** version only (`vX.Y.Z`) — no subtitle or theme. **Body:** `## Highlights` section with 3–5 short pointer bullets summarizing the release, followed by `**Full details:** [CHANGELOG — vX.Y.Z](<anchor URL>)`. CHANGELOG.md remains the source of truth for full rationale, validation, and notes — the release body is intentionally minimal to avoid redundancy. No `## Summary` prose, no self-curated "What's new" headers, no emojis. Anchor URL format: `https://github.com/<owner>/<repo>/blob/main/CHANGELOG.md#<slug>` where `<slug>` is the GitHub slug of `[X.Y.Z] - YYYY-MM-DD` (drop `[`, `]`, `.`; spaces → hyphens; lowercase). Past releases set the pattern: `gh release view <prev> --json name,body`
- **`gh release` with markdown body:** HEREDOC breaks on backticks and special chars in markdown — always write notes to a temp file and pass with `-F <file>`, then delete the file. Full sequence: stage specific files → commit → `git tag -a vX.Y.Z -m "vX.Y.Z — <feature>"` (annotated, not lightweight) → `git push --follow-tags origin main` (atomic commits+tag push) → `gh release create vX.Y.Z --title "vX.Y.Z" -F notes.md`
- **CHANGELOG `## [Unreleased]` bucket:** post-release docs/i18n fixes accumulate in a `## [Unreleased]` section at the top of CHANGELOG. Each fix commit includes its own Unreleased entry (atomic, self-describing). At next patch release, rename `## [Unreleased]` → `## [X.Y.Z] - YYYY-MM-DD`. Promote triggers: security-adjacent fix lands → release immediately; 5+ accumulated items or 30+ days stale → suggest release.
- **Pre-push self-regression grep:** before `git push --follow-tags`, grep working tree for retired vocab from same-cycle renames (heading labels, retired internal IDs) — catches incomplete cascades that escape per-task review. Cheap insurance vs forced post-push fix-up commit.
- **Pre-publish release notes verification:** before `gh release create`, grep actual implementation file (hook script, validator) against any specific technical claim in body (regex, allow-list, threshold) — catches spec-vs-claim drift that pre-push grep misses.
- **README badge sync verifier:** before `git push --follow-tags`, run `python .github/scripts/check-readme-badge-sync.py` to confirm the README shields.io version badge matches `plugin/.claude-plugin/plugin.json`. Catches the stale-badge cascade miss class (v2.17.0 shipped with `2.16.0` badge until v2.17.1 caught it manually).
- **CHANGELOG anchor slug verifier:** CI job `changelog-anchor-slug` runs `python .github/scripts/check-changelog-anchor-slug.py` on every push/PR. Catches slug typos that would silently 404 in release-body anchor URLs.
- **Annotated tag SHA verify post-push:** run `python .github/scripts/check-tag-sha-propagation.py v<tag>` after push; PASS confirms `git rev-parse v<tag>` (local annotated tag object SHA) matches `refs/tags/v<tag>` on origin (not `^{commit}` peeled). FAIL means the annotation didn't propagate — re-push with `git push origin refs/tags/v<tag>` to fix.
- **Pre-publish smoke-status gate (post-tag-push):** the smoke workflow triggered by the tag push (`push: tags: ['v*']` in `.github/workflows/smoke.yml`) MUST conclude `success` before `gh release create`. Tag-trigger run registration has a few-second delay, so poll then block on `--exit-status`: `TAG_SHA=$(git rev-list -n 1 v<tag>^{commit})` → `until SMOKE_RUN=$(gh run list --commit "$TAG_SHA" --workflow=smoke.yml --json databaseId --jq '.[0].databaseId') && [ -n "$SMOKE_RUN" ]; do sleep 2; done` → `gh run watch "$SMOKE_RUN" --exit-status`. Without this gate v2.17.0 published 76 seconds after Linux smoke FAILED on tag SHA, leaving main RED. Local Windows sanity stays as fast precheck, not a release gate — only Linux CI conclusion qualifies.
- **Branch+tag same-name `push --delete`:** `git push origin --delete v2.X.0` errors with "matches more than one" when both branch and tag share the name; use `git push origin --delete refs/heads/v2.X.0` (explicit refspec) to remove the staging branch only (tag preserved).
- **`eval-manifest.json` sealed at v2.11.0:** the file froze at maintainer signoff 2026-04-16 and v2.12.0–v2.14.0 releases skipped entry-add. Release plans that stipulate updating this file should follow precedent (skip) unless smoke-runner re-execution actually occurs.

## Plugin Development Rules

- Skills go in `plugin/skills/<name>/SKILL.md` — do NOT use `commands/` (legacy)
- Each skill must have YAML frontmatter with `name` and `description` fields
- `allowed-tools` is no longer supported in skill frontmatter; agents use `tools` for tool restriction
- Plugin version is managed in `plugin/.claude-plugin/plugin.json` only — do NOT duplicate version in `.claude-plugin/marketplace.json`
- Marketplace name (`guardians`) must NOT match the GitHub repo name case pattern to avoid Windows NTFS rename failures
