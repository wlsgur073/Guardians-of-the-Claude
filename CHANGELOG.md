<!-- markdownlint-disable-file MD024 -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [2.10.1] - 2026-04-13

### Fixed

- `plugin/skills/audit/references/output-format.md`: **saturated-case false-reassurance copy removed.** The 100/100 generation rule previously rendered "Your configuration is in great shape. No changes needed." unconditionally whenever `Final == 100`, even when `Raw = FG × DS + SB + LAV` exceeded the 100 cap and positive LAV headroom remained — meaning LAV-dimension refinements were still available but the visible copy denied their existence. This misrepresented real quality work as nonexistent, particularly frustrating for advanced (Day 100+) users whose documented LAV improvements (e.g., L1 structural accuracy 0 → +2) moved Raw but not Final. Replaced with a two-branch conditional: when `LAV == +10` (all six LAV items at their individual maximum), render "Configuration reaches the current scoring ceiling. Re-audit on major dependency or configuration changes."; when `LAV < +10`, render "Configuration reaches the current scoring ceiling. Remaining refinements live in LAV — see the LAV breakdown under Score Breakdown for items still below their maximum. Re-audit on major changes." Both branches preserve the existing "explore advanced features" suggestion. The rule now points users toward the LAV breakdown line already rendered in Score Breakdown (`LAV: +X (L1: a + L2: b + ... + L6: f)`) as the concrete next-look location, restoring actionable signal without introducing new output surfaces.

### Changed

- `plugin/.claude-plugin/plugin.json`: version bumped `2.10.0` → `2.10.1`.
- `README.md`: version badge updated `2.10.0` → `2.10.1`.

### Notes

- **Deliberate minimum-fix scope.** A fuller excellence-headroom surface — Raw exposure on the score line, a new Level 4 — Mastered maturity tier gated by `LAV >= 8`, a dedicated "Excellence Opportunities" output section listing LAV items below their max with concrete fix hints, and a Score-unchanged-but-Raw-improved comparison variant — was designed and fully staged during this work but **reverted before ship**. Rationale: the Audit v4 Phase 2 rewrite (LAV-as-multiplier, deferred per `docs/ROADMAP.md`) will shift LAV ranges and item thresholds; introducing a `LAV >= 8` Level 4 now would require re-baselining once v4 lands, forcing users who reached "Mastered" to see their Level 4 status revoked or renumbered. UX churn outweighed the marginal discriminative-power gain for the narrow subset of projects currently hitting saturation. The fuller design remains available as starting material when v4 Phase 2 ships.
- **Inline deferral note in the generation rule.** The new `LAV < +10` branch includes a trailing sentence pointing at `docs/ROADMAP.md` "Audit v4 Phase 2" and naming the deferred surfaces explicitly (Raw exposure, Level 4 — Mastered tier, Excellence Opportunities section). This bakes the maintenance context into the spec itself rather than losing it to CHANGELOG archaeology — a future reader asking "why not add Raw exposure here too?" finds the answer immediately in the rule.
- **Symmetry with 2.10.0 step 7.5.** The 2.10.0 release added a false-reassurance guardrail for the **inflated** direction (`Final >= 80 AND LAV L5 == −3` → render warning line). This release addresses the **saturated** direction (`Final == 100 AND LAV < +10` → render directional copy pointing at the LAV breakdown). Both are informational, neither changes the score. Together they form minimum coverage of the two ways `Final == 100` can misrepresent reality under the additive-LAV model; the structural fix for both remains the deferred LAV-as-multiplier rewrite.
- **SemVer rationale.** Pure copy change in one output generation rule — no new flags, no new frontmatter fields, no new skill surface, no scoring-model math changes. Patch-level per the `CLAUDE.md` Release Process policy ("patch (z) for fixes").
- **Validation.** Local CI-equivalent scripts passed — `check-frontmatter-parity.py` (18 guide pairs OK), `check-i18n-parity.py` (58 files across 4 pairs OK), `check-json-schemas.py` (11 JSON files OK). Change is plugin-only (`plugin/skills/audit/references/output-format.md`), which is single-source — no i18n mirror update needed (parity script scopes are `templates/` and `docs/guides/`, not `plugin/`).
- **Change Propagation Checklist followed:** plugin.json, README badge, CHANGELOG entry. No i18n mirror. No `templates/`, `docs/guides/`, JSON schema, or shell-script surface touched.

## [2.10.0] - 2026-04-12

### Added

- `/audit` Phase 1.5 (new): discovers additional `CLAUDE.md` files that represent true subpackage configs in a monorepo, via a four-layer filter. **Layer 1** excludes the root `CLAUDE.md` and the root `.claude/CLAUDE.md` (both already counted in T1). **Layer 2** excludes common build/cache/vendor directories (`node_modules/`, `dist/`, `build/`, `target/`, `vendor/`, `.git/`, `.next/`, `.nuxt/`, `.venv/`, `venv/`, `.cache/`, `coverage/`, `out/`, `__pycache__/`, `.pytest_cache/`). **Layer 3** requires a package manifest in the `CLAUDE.md`'s immediate parent directory — or, for nested `.claude/CLAUDE.md`, in the parent of `.claude/` (so `packages/api/.claude/CLAUDE.md` maps to package root `packages/api/`, keeping legitimate subpackage `.claude/` layouts visible). The accepted manifests are literal filenames only: `package.json`, `Cargo.toml`, `go.mod`, `pyproject.toml`, `build.gradle`, `build.gradle.kts`, `pom.xml`, `composer.json`, `Gemfile`. **Layer 4** drops Git-ignored paths on a best-effort basis via `git check-ignore`; silently skipped if the project is not inside a Git worktree, if `git` is unavailable, or if the `Bash` tool is not permitted. Windows path separators are normalized to `/` before comparisons, and directory-name matching is case-insensitive. When any file survives all four layers, an "Additional CLAUDE.md Files" disclosure section is appended to the audit output, listing each path with its line count (limited to 20 entries; appends `(+N more not shown)` if more exist). **This version is disclosure-only — files are detected but not yet scored.** Per-package scoring is deferred to Audit v4 Phase 2 (see `docs/ROADMAP.md`). Closes the "monorepo silent under-coverage" gap from the v3 audit follow-up. Zero new flags, arguments, or skill surface — pure default-behavior expansion of the existing `/audit` skill.
- `/audit` Phase 4 step 7.5 (new): false-reassurance guardrail. After computing the Final Score, if `Final` falls within the **Grade A range defined in `references/scoring-model.md`** (currently `Final >= 80`) AND `LAV L5 (Conciseness) == −3`, an informational warning line is rendered immediately below the combined Score/Maturity line: "⚠ High structural score with low conciseness signal — your CLAUDE.md may be over-configured. See L5 finding below for specifics." The condition references the grade boundary rather than hardcoding the numeric threshold, so any future recalibration of scoring-model.md grade ranges automatically propagates. The warning does **not** change the score; it surfaces the documented limitation that LAV L5's −3 cap cannot fully offset an inflated Detail Score on Overconfigured CLAUDE.md files. The full structural fix (LAV-as-multiplier model rewrite) is deferred to Audit v4 Phase 2. Zero new flags or arguments.

### Changed

- `docs/ROADMAP.md`: Backlog section gains two new entries — **Audit v4 Phase 2** (per-package scoring + LAV-as-multiplier formula rewrite, both coupled to validation work) and **Audit Gap C decision** (automatic diff suggestions explicitly NOT closed inside `/audit`, with rationale referencing the zero-options principle and the Codex independent review).
- `plugin/skills/audit/SKILL.md`: new Phase 1.5 inserted between Phase 1 and Phase 2 (subpackage discovery, four-layer filter — root exclusion, build/cache/vendor exclusion, package-manifest requirement with nested `.claude/` special case, Git-ignore best-effort drop, plus Windows path-separator normalization); new step 7.5 inserted into Phase 4 between Final Score calculation and Quality Gate check (false-reassurance condition, sourced from the Grade A range in `references/scoring-model.md` rather than a hardcoded numeric threshold, with a verbatim cross-reference to the warning string in `references/output-format.md` rather than inlining it).
- `plugin/skills/audit/references/output-format.md`: new conditional "Additional CLAUDE.md Files (informational)" section spec inserted between "All Suggestions" and "Maturity path"; the exact false-reassurance warning string now lives only in the Standard Output sample block (single source of truth), and the "Score-line warning" prose section describes condition and placement without reprinting the string; sample block's Score Breakdown was recalibrated to a self-consistent Grade A + L5 = −3 scenario (Final 83, FG 1.00, T2 1.00, T3 0.50, DS 80.0, SB +5, LAV −2, Quality Cap 88) so the warning line's appearance in the sample is not inconsistent with its trigger condition.
- `plugin/.claude-plugin/plugin.json`: version bumped `2.9.7` → `2.10.0`.
- `README.md`: version badge updated `2.9.7` → `2.10.0`.

### Notes

- **SemVer rationale (minor bump despite no new flags or skills):** B1 (subpackage discovery) and A1 (false-reassurance guardrail) extend `/audit`'s scope to consider new files and a new warning condition that did not exist before. By the strict letter of the SemVer policy in `CLAUDE.md` ("minor only when adding user-callable surface — new skill, new SKILL.md frontmatter field, new template variant, new flag"), this is borderline between patch and minor. Treating it as minor (`2.10.0`) signals to users that `/audit` gained meaningful new capabilities (monorepo awareness, scoring transparency) even though no new commands, flags, or arguments were added. Users running the same command on the same project may see new output sections.
- **Zero new options, flags, or `$ARGUMENTS`.** Both new behaviors are pure default-behavior changes. The "no skill options or arguments" principle (memory `feedback_no_skill_options_or_args`) was applied throughout — the independent review's earlier suggestion to add `/optimize --dry-run` for Gap C was rejected for the same reason, and Gap C was deferred entirely instead.
- **Three-way prioritization (Claude + Codex + project owner)** drove this scope. Both AIs independently arrived at the same priority order (B → A → C). Codex caught a numbers-reversal bug in the original framing of the conciseness gap (the project owner had written "58 vs 85" with the directionality reversed) and surfaced the meta-critique that "B/A/C are different classes of gap (coverage / calibration / convenience), not three points on the same scale." The B/A split into pre/post sub-deliverables (B1 disclosure-first, A1 guardrail-first, B2 + A2 deferred to v2.11.0+) came from Codex; the rejection of `/optimize --dry-run` for Gap C came from the project owner's zero-options principle.
- **Memory correction (project-internal):** the local memory file `project_audit_v3_gap.md` was updated to disambiguate the "(58 vs 85)" notation that originally caused the numbers-reversal bug — now explicitly written as `ours=85, theirs=58, +27 over-rating`. Future audits of audit v3 should not repeat the same mistake.
- **Phase 2 (B2 + A2) is on the roadmap, not in this release.** It requires score-shift validation work and visible user messaging because existing audit scores may move when the LAV-as-multiplier model lands. Shipping it without that preparation would erode user trust in audit scores — exactly the failure mode the conciseness gap itself describes.
- **Second-pass review (2026-04-12, pre-tag):** an independent review by Codex on the pre-tag Phase 1 implementation caught four issues that became the final refinement pass. (1) The original Phase 1.5 filter — raw build/cache/vendor exclusion with no manifest check — would produce 15/15 false positives when run against this very repo, and a naive "immediate-parent manifest" upgrade would still leak two fixture files that happen to ship a `go.mod` and a `Cargo.toml` (`test/eval-v2/go-web-new/CLAUDE.md` and `test/eval-v2/rust-cli-new/CLAUDE.md`); the fix is a four-layer filter combining manifest requirement with a best-effort Git-ignore drop (`/test/` is `.gitignore`d, which catches the two fixtures that slip through the manifest layer). (2) The false-reassurance condition originally proposed as `Grade == A` in step 7.5 has an ordering bug, because Grade is determined in step 9, two steps after the check — the fix references the Grade A range in `scoring-model.md` rather than computing Grade inline. (3) The inline warning-string duplication between `SKILL.md` and `output-format.md` should resolve to a single source, and the cleanest single source is the Standard Output sample block (not the prose section), so the sample block was recalibrated to a self-consistent Grade A + L5 = −3 case where the warning line belongs. (4) Windows path-separator normalization and case-insensitive directory-name matching needed to be specified explicitly in Phase 1.5 so the filter works on NTFS. All four issues were addressed before v2.10.0 tag creation.
- **Conservative manifest list (deliberate false-negative tradeoff).** Phase 1.5 Layer 3 recognizes exactly 9 literal manifest filenames in v2.10.0: `package.json`, `Cargo.toml`, `go.mod`, `pyproject.toml`, `build.gradle`, `build.gradle.kts`, `pom.xml`, `composer.json`, `Gemfile`. Projects using `setup.py`, `setup.cfg`, `Package.swift`, `mix.exs`, `*.csproj`, or `*.gemspec` as the only manifest at the package root will not be reported. This is a deliberate precision-over-recall tradeoff for a disclosure-only section — noisy findings train users to ignore the section entirely, which defeats the feature's purpose. The manifest list may expand in v2.11.0+ if user feedback surfaces real monorepo gaps.
- **Verification pass (2026-04-12, post-Codex).** After the four Codex findings were resolved, a targeted manual verification on this repo (exhaustive 9-manifest scan cross-referenced against all 15 subpackage CLAUDE.md candidates, plus live `git check-ignore` probes) surfaced three additional small defects in the refinement work itself. (1) The recalibrated Standard Output sample block's "Next step" line still pointed at `/guardians-of-the-claude:secure` even though the new T2 = 1.00 / T3 = 0.50 scenario has no protection gaps — corrected to `/guardians-of-the-claude:optimize` with the prior "(or /optimize, or both — see rules below)" meta-annotation removed (sample block is now fully self-consistent with a single Next step variant). (2) Phase 1.5 Layer 4's `.git/` directory check would silently disable the git-ignore filter for Git worktree and submodule users, because those environments use a `.git` **file pointer** rather than a directory — fixed to accept either a file or a directory at the project root. (3) Layer 4 had no per-candidate error-handling rule: if `git check-ignore` returned a non-0 / non-1 exit code on a specific candidate (broken index, unusual path, permission, etc.), the spec left the auditor LLM to improvise — added an explicit conservative rule ("treat as not ignored, keep the candidate, continue processing; never abort the layer"). All three defects were introduced by the refinement pass itself, not by the original v4 Phase 1 code, and were caught before v2.10.0 tag creation.
- **Change Propagation Checklist:** the new audit behavior is plugin-only (`plugin/skills/audit/`), which is single-source. No i18n mirror updates needed (the i18n parity script checks `templates/` and `docs/guides/`, not `plugin/`). ROADMAP, CHANGELOG, plugin.json, README badge all updated.

## [2.9.7] - 2026-04-11

### Added

- `docs/i18n/ja-JP/guides/` (9 files): full Japanese translation of all guides — `getting-started.md`, `claude-md-guide.md`, `rules-guide.md`, `settings-guide.md`, `directory-structure-guide.md`, `effective-usage-guide.md`, `advanced-features-guide.md`, `mcp-guide.md`, `recommended-plugins-guide.md`. Translated directly from EN sources (not via the ko-KR mirror) to avoid two-stage translation loss. Frontmatter `version` fields kept in lockstep with EN. Natural Japanese tech-doc conventions applied: です/ます polite form throughout, standard tech katakana loanwords (フック / プラグイン / スキル / エージェント / リポジトリ / コミット / フロントマター), code identifiers preserved as ASCII (`CLAUDE.md`, `/init`, `npm test`, `Tool(specifier)`), idiom-level 意訳 for English metaphors that resist literal translation (e.g., "kitchen sink session" → 「何でも放り込んだセッション」, "trust-then-verify gap" → 「信頼すれども検証せず」, "rule of thumb" → 「目安」).

### Changed

- `CLAUDE.md`: new `### Release Process` subsection under Contribution Rules, documenting (1) the project's SemVer policy — patch (z) for fixes and platform-compat work, minor (y) only when adding user-callable surface, major (x) for breaking contract changes; (2) the GitHub Release format convention — title is the version only (`vX.Y.Z`), body is the matching `CHANGELOG.md` section copied verbatim, no Highlights/Summary/curation; (3) the `gh release` HEREDOC pitfall — markdown bodies with backticks break HEREDOC parsing, so always pass notes via temp file with `-F <file>`. CLAUDE.md grew from 58 → 64 lines (still well under the 200-line cap). Authored after 2.9.6 was tagged but before 2.9.7, so it ships in this release.
- `README.md` + `docs/i18n/ko-KR/README.md`: language switcher no longer marks `日本語` as `(WIP — README only)` / `(WIP — README 전용)`. Japanese support now covers the README plus all 9 guides; only example templates under `templates/` remain in English (deferred to a follow-up release).
- `docs/i18n/ja-JP/README.md`: documentation table replaces the "ガイドの日本語翻訳は準備中です" notice with localized link text and updates 11 guide link paths from `../../guides/...` (English) to `guides/...` (now-translated Japanese). Directory description cells now read `日本語翻訳（README、ガイド）` instead of `日本語README（ガイド翻訳は準備中）`.
- `plugin/.claude-plugin/plugin.json`: version bumped `2.9.6` → `2.9.7`.
- `README.md`: version badge updated `2.9.6` → `2.9.7`.

### Notes

- Per the SemVer policy newly documented in `CLAUDE.md` in this release, expanding documentation translations is **patch-level work** — no new user-callable surface (no skills, flags, frontmatter fields, or template variants added). The same content is simply now available in a new language.
- Translation methodology: each guide was translated directly from the EN source rather than from the ko-KR mirror, to avoid two-stage translation loss. ko-KR was consulted only as a structural reference for link path conventions (relative `guides/...` form).
- The translations went through two review passes, both folded into this release. **Pre-commit self-review** caught (1) `directory-structure-guide.md` redundant subject in the auto-memory definition (`Claude が将来のセッションのために` — duplicating `Claude` already established in the prior sentence); (2) `getting-started.md` Step 3 cross-link text said `含める/含めない` while the anchor target heading said `含めるものと除外するもの` — now consistent on both ends. **Post-commit independent review** (using a dedicated `ja-translation-reviewer` agent for outside-perspective verification) caught five additional issues: (3) `claude-md-guide.md` "Organizing at Scale" section collapsed two distinct field lists ("each skill's name/purpose and each agent's name/model/role") into one undifferentiated 4-field list — restored the EN distinction so readers don't infer that skills have a `model` field or agents have a `purpose` field; (4) `directory-structure-guide.md` referred to `config-changelog.md` as `判断記録` while `README.md` (existing translation) calls the same file `決定ジャーナル` — standardized on `決定ジャーナル` to match the more visible README, eliminating the cross-document name drift; (5) `directory-structure-guide.md` line 26 had a half-width `)` paired with full-width `（` in a code-block comment (`スキル定義（高度)`) — fixed to balanced full-width `（高度）`; (6) `recommended-plugins-guide.md` `code-review` row had `本物の問題` (literal calque feel — `本物` typically contrasts with `偽物`) — replaced with `実際の問題`, more natural for a bug-triage context; (7) `recommended-plugins-guide.md` `figma` row reordered for natural Japanese flow with `引き込む` → `取り込む`, the more idiomatic verb for "pulling content in".
- Phase 2 (template translation) is deferred to a later release. Templates are mostly code/config rather than prose, so the translation surface there is small but non-zero (`templates/README.md`, `templates/starter/CLAUDE.md`, `templates/advanced/CLAUDE.md`, advanced rules and skill SKILL.md files). The i18n parity script (`check-i18n-parity.py`) currently checks only ko-KR pairs, so leaving `docs/i18n/ja-JP/templates/` partially populated does not break CI.
- Change Propagation Checklist followed: EN README → ko-KR + ja-JP README, plugin.json version → README badge, CHANGELOG.

## [2.9.6] - 2026-04-11

### Added

- `plugin/hooks/session-start.ps1`: new PowerShell port of `session-start.sh`, functionally identical (same four-case state machine, same manifest staleness list, same JSON output contract). Closes the Windows bash hard dependency noted as "left open for a follow-up" in the original 2.9.6 draft. Three PS-specific defenses worth noting: (1) uses `$ProfilePath` instead of `$Profile` to avoid shadowing PowerShell's built-in automatic variable, (2) sets `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8` at script start so non-ASCII `additionalContext` survives Windows PowerShell 5.1's default OEM/Windows-1252 stdout encoding, (3) source file stays ASCII-only because PS 5.1 reads BOM-less `.ps1` files with the system ANSI codepage. Verified: Cases 1-4 output matches `session-start.sh` byte-for-byte under both bash and `powershell.exe`.
- `templates/advanced/scripts/validate-prompt.ps1` (EN + ko-KR): new PowerShell port of `validate-prompt.sh`, completing the cross-platform pattern at the template-example layer (the plugin hook layer was already covered by `session-start.ps1` earlier in this release). Reuses the same encoding hardening (`[Console]::OutputEncoding = UTF-8`, ASCII-only source) as `session-start.ps1`. One enhancement over `session-start.ps1`: this script guards with `Get-Command bash -ErrorAction SilentlyContinue` and exits 0 silently when bash is also on PATH, so dual-interpreter systems (e.g., Windows with Git Bash + PowerShell) only emit the migration warning once instead of duplicating it via both hook entries. Reads stdin via `[Console]::In.ReadToEnd()` instead of `$input` because `$input` is a lazy enumerator that splits multi-line prompts; `ReadToEnd` matches `cat` byte-for-byte.

### Fixed

- `templates/advanced/.claude/settings.json` (EN + ko-KR): `UserPromptSubmit` hook `timeout` corrected from `5000` to `5`. Claude Code hook `timeout` is specified in **seconds** (per official docs), so the previous value resolved to ~83 minutes instead of the intended 5-second input validation budget.
- `CLAUDE.md`: self-description line corrected — the repo previously claimed "no tests" and "all content is Markdown", contradicting the existing `test/` eval framework, `plugin/hooks/*.sh`, `statusline.sh`, `.github/scripts/*.py`, and CI workflow. Phrasing now mirrors the `docs/CONTRIBUTING.md` fix landed in 2.9.5.
- `CLAUDE.md`: "run the same checks CI runs" softened to "run the same scripts CI runs" with an explicit note that `check-json-schemas.py` degrades to required-field-only checks when schemastore.org is unreachable. Local pass does not guarantee CI pass without network.
- `README.md`, `docs/i18n/ko-KR/README.md`, `docs/i18n/ja-JP/README.md`: statusline one-line install command changed from `cp Guardians-of-the-Claude/statusline.sh …` to `cp ./statusline.sh …`. The absolute folder-name form failed whenever users cloned into a directory with a different name (including this repo's own local checkout as `Claude-Code-Template`).
- `plugin/hooks/session-start.sh`: removed the v2.9.0 cache-rename migration block (`mv .claude/.plugin-cache/claude-code-template → guardians-of-the-claude`). The SessionStart hook is now strictly read-only, matching its `description` field. Users still on the pre-rename cache (unlikely this far from v2.9.0) will simply regenerate it on next `/audit`.
- `plugin/hooks/session-start.sh`: the three U+2014 em-dashes in `additionalContext` strings replaced with ASCII `--` so the bash and PowerShell hook entries produce byte-identical output. Bash on UTF-8 systems handled the em-dash fine, but forcing identity with the PS port removes a class of "why do the two hook entries send Claude Code different text" drift.
- `README.md` + `docs/i18n/ko-KR/README.md`: the three-language header now marks `日本語` as `(WIP — README only)` / `(WIP — README 전용)`. Previously English-side users clicked through to `docs/i18n/ja-JP/README.md` expecting a full Japanese translation and only discovered the "ガイドの日本語翻訳は準備中です" notice after the click. `docs/i18n/ja-JP/README.md` has no top-level language switcher so needed no edit.
- `docs/guides/getting-started.md` + `docs/i18n/ko-KR/guides/getting-started.md`: Step 3 section list unified with the **6 canonical sections** that `/create` actually generates (per `plugin/skills/create/templates/starter.md:69` and `templates/starter/CLAUDE.md`). The prior 8-item list included `Workflow`, `Project Structure`, and `References` — fine for advanced configurations, but users who ran `/create` ended Step 3 confused because their generated file only had 6 headers. The three optional sections are now mentioned once as "add when you outgrow the baseline" with a link to `templates/advanced/CLAUDE.md`. `Development Approach` (previously missing from the guide's list despite being one of the 6 `/create` generates) is now included. Frontmatter bumped `1.2.2` → `1.2.3` on both EN and ko-KR.

### Changed

- `plugin/skills/create/templates/advanced.md`: agent scaffold template now includes a YAML comment explaining the `sonnet` model choice (`# sonnet: balanced speed/quality for implementation tasks`), mirroring the idiom established in `docs/guides/advanced-features-guide.md:83`. Any `/create` run that generates a new agent file will propagate this rationale comment, and future readers see why the model was picked instead of finding a bare `model: "sonnet"` declaration.
- `plugin/hooks/hooks.json`: `SessionStart.hooks` now contains **two command entries** — the original `bash session-start.sh` plus a new `powershell -NoProfile -ExecutionPolicy Bypass -File session-start.ps1`. On platforms missing one interpreter, that entry exits with `ENOENT` and Claude Code silently skips it; the other entry runs. Windows 10+ users no longer need Git Bash or WSL for the SessionStart auto-guidance to work. Description field reworded to call out the read-only contract explicitly.
- `README.md` + `docs/i18n/ko-KR/README.md` + `docs/i18n/ja-JP/README.md` + `docs/guides/getting-started.md` + `docs/i18n/ko-KR/guides/getting-started.md`: Windows prerequisite note rewritten to reflect the new dual-hook setup — PowerShell 5.1+ **or** Git Bash/WSL both work for the plugin hook, but `templates/advanced/scripts/*.sh` still needs bash. Guide frontmatter bumped `1.2.2` → `1.2.3` on both EN and ko-KR.
- Hook `timeout` fields added where previously missing, per the "Always set `timeout` explicitly" rule in `docs/guides/advanced-features-guide.md`:
  - `plugin/hooks/hooks.json`: SessionStart hook gets `"timeout": 5` (now applied to both bash and powershell entries).
  - `templates/advanced/.claude/settings.json` (EN + ko-KR): PreToolUse file-protection gets `"timeout": 5`, PostToolUse ESLint gets `"timeout": 15`.
  - `plugin/skills/create/templates/advanced.md`: generator template for PreToolUse file-protection and PostToolUse auto-linting now includes `timeout`.
  - `docs/guides/advanced-features-guide.md` + ko-KR mirror: JSON example in "Hook Configuration" now shows `timeout` on both hooks. Frontmatter bumped `1.2.1` → `1.2.2`.
- `templates/advanced/.claude/settings.json` (EN + ko-KR): `UserPromptSubmit` hook now contains **two command entries** — the original `bash validate-prompt.sh` plus a new `powershell -NoProfile -ExecutionPolicy Bypass -File validate-prompt.ps1`. Mirrors the dual-entry pattern from `plugin/hooks/hooks.json`. Bare Windows shells (PowerShell-only, no Git Bash/WSL) no longer leave this hook silently broken on the advanced template.
- `docs/guides/getting-started.md` + `docs/i18n/ko-KR/guides/getting-started.md`: Step 3 ("Fill in Your CLAUDE.md") now opens with an explicit "If you used `/create`, skip this step" directive matching Step 2's pattern. Previously the section started with "Open your CLAUDE.md and work through each section. `/create` generates the six canonical sections below; keep the same structure if you are writing the file by hand", which conflated "describing `/create`'s output" with "instructions for hand-writing". Users who ran `/create` reached Step 3 unsure whether anything more was required. Frontmatter bumped `1.2.3` → `1.2.4` on both EN and ko-KR.
- `README.md` + `docs/i18n/ko-KR/README.md` + `docs/i18n/ja-JP/README.md` + `docs/guides/getting-started.md` + `docs/i18n/ko-KR/guides/getting-started.md`: Windows prerequisite note rewritten again — no longer says "advanced template scripts still require bash" because the only such script (`validate-prompt`) now ships a `.ps1` companion. The note now states that **both** the plugin hook layer and the advanced template hook layer ship parallel bash + PowerShell entries, so PowerShell 5.1+ or Git Bash/WSL works end-to-end with no extra setup.
- `plugin/.claude-plugin/plugin.json`: version bumped `2.9.5` → `2.9.6`.
- `README.md`: version badge updated `2.9.5` → `2.9.6`.

### Notes

- Addresses Codex audit #2 **and** Codex audit #3 in a single release. Audit #3 surfaced five findings. Four ship in this release: Windows bash hard dependency (the v2.9.6 follow-up item, now closed via the PowerShell port), SessionStart hook silently mutating `.plugin-cache` at session start (migration block removed), Step 3 section-list drift in `getting-started.md` vs. the 6-section output `/create` actually generates, and Japanese language-switcher over-promising. The fifth finding — `validate.sh` bash-only lock-in — was closed without a shipping change: `test/` is gitignored (see `.gitignore:21`, per the "internal eval docs not distributed" rule), so external contributors never reach that script in the first place. Local-only documentation of the bash requirement was still added to `test/testing-strategy.md` for anyone who does wander into the directory.
- One runtime bug was discovered after the Codex-flagged fixes: the initial `session-start.ps1` port produced corrupted Case 1 output (`installed ??suggest`) because Windows PowerShell 5.1 reads BOM-less `.ps1` files with the system ANSI codepage and writes stdout with the same encoding, mangling U+2014. Fix: ASCII-only strings in the script source, plus `[Console]::OutputEncoding = UTF-8` as a second-layer defense. `session-start.sh` strings normalized to match so the two hook entries produce byte-identical `additionalContext`.
- Change Propagation Checklist followed: EN guide → ko-KR guide, EN template → ko-KR template, EN README → ko-KR + ja-JP README, plugin.json version → README badge, CHANGELOG.
- The PowerShell port now extends past the plugin layer into the advanced template's example hooks, so the audit #3 "Windows bash hard dependency" finding is closed at **both** layers (plugin hook + template example). The new `validate-prompt.ps1` introduces a `Get-Command bash` guard idiom that `session-start.ps1` lacks — this is the cleaner pattern for hooks whose output is user-visible (UserPromptSubmit, PostToolUse) where duplicate output on dual-interpreter systems would be observable. `session-start.ps1` produces `additionalContext` JSON which Claude Code merges/dedupes more gracefully, so backporting the guard there is optional and deferred.

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
