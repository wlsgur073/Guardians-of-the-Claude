<!-- markdownlint-disable-file MD024 -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [2.19.1] - 2026-05-14

### Fixed

- **Fan-out section claimed "in parallel" but bash loop was sequential** in `docs/guides/workflow-patterns-guide.md` (EN + ko-KR + ja-JP, frontmatter `1.0.1` → `1.0.2`). Reworded to "distribute work across many invocations" and added a bounded-parallel example (`xargs -P 4` and PowerShell `ForEach-Object -Parallel ... -ThrottleLimit 4`) alongside the sequential loop. Also aligned the `--allowedTools` value to upstream form `"Bash(git commit *)"` (no colon).

- **Effort-scaling table over-extrapolated Anthropic source numbers** in `docs/guides/multi-agent-patterns-guide.md` (EN + ko-KR + ja-JP, frontmatter `1.0.1` → `1.0.2`). Previous values `Medium analysis 2–4 / 10–30` and `Complex research 10+ / 30+ per worker` were not in the source. Aligned with the [multi-agent research system writeup](https://www.anthropic.com/engineering/multi-agent-research-system): `Direct comparison 2–4 / 10–15`, `Complex research 10+ / per-worker count not pinned by source`. Added footnote citing the article's "3–5 subagents per parallel batch" figure.

- **`/audit` Phase 3 gate omitted `.claude/skills/`** in `plugin/skills/audit/SKILL.md:120`. A documentation-only project with only `.claude/skills/` would skip loading `t3-optimization.md` and therefore skip the v2.19.0 Skill Description Quality advisory. Added `.claude/skills/` to the non-skip condition, restoring the applicability documented in CHANGELOG v2.19.0.

- **i18n cross-language anchor mismatch** between `multi-agent-patterns-guide.md` and `workflow-patterns-guide.md`. ko-KR and ja-JP workflow-patterns mirrors had translated the `## Fan-out for batch tasks` heading (`## 배치 작업을 위한 Fan-out`, `## バッチタスクの Fan-out`), breaking the `#fan-out-for-batch-tasks` slug that the multi-agent guide linked to. Restored the heading to English in both locale mirrors per CLAUDE.md cross-language anchor consistency rule.

- **Unsourced `$100+` dollar estimate** in the fan-out warning of `docs/guides/workflow-patterns-guide.md` (EN + ko-KR + ja-JP). The figure was a local extrapolation; Anthropic's [best-practices article](https://code.claude.com/docs/en/best-practices) does not give a dollar estimate for fan-out runs. Replaced with a qualitative warning advising readers to estimate using their model's per-token pricing.

- **`ワークロードスケーリング` residue in ja-JP `multi-agent-patterns-guide.md` frontmatter `description`.** The v2.19.0 polish pass updated the body heading to `努力スケーリング` but left the frontmatter line unchanged. Corrected.

- **Skill-description-quality regex rendered ambiguously** in the `Trigger phrase present` row of `plugin/skills/audit/references/checks/t3-optimization.md:141`. The form `Use when\|When to use\|...` reads as escaped literal pipes inside a markdown table cell rather than regex alternation. Converted to an explicit "matches any of" enumeration listing the four trigger phrases without regex syntax.

- **CHANGELOG v2.19.0 line 41 + 45** stated the new T4/T5 guides shipped at `frontmatter version 1.0.0`, but the same release's polish pass patch-bumped them to `1.0.1`. Updated the entries to reflect the final shipped value.

## [2.19.0] - 2026-05-14

### Added

- **CLAUDE.md workflow rules (2 entries from Phase-1-citation cleanup session)** — captured two reusable patterns surfaced during the v2.12.0-era dangling-citation sweep (commit `7fbe59b`):
  - *Verifying Changes Locally*: self-generated end-of-turn "next-task" speculation needs the same grep verification as agent claims — pattern-matching commit-log names (e.g., `T5 Task` / `DEC-N` in `git log -S`) without grepping shipped docs creates phantom TODOs. Same standard regardless of trigger source (subagent vs. own pattern recognition).
  - *Plugin Development Rules*: no inline citations to internal-planning IDs in shipped docs — `plugin/references/` and `plugin/skills/SKILL.md` must not cite IDs whose definitions live only in gitignored `docs/superpowers/plans/` (e.g., `Phase N Global Invariant #M`). Restate the behavioral rule in-place. CLAUDE.md grew 101 → 103 lines, well under the 200-line ceiling.

- **CLAUDE.md workflow rules (4 entries from v2.18.0-cycle session learnings)** — captured four reusable patterns surfaced during the multi-cycle review and release work:
  - *Repository Structure*: `.claude/.plugin-cache/<plugin-name>/local/` reference path with read/write contract (read for status, do NOT manually edit; plugin auto-updates on next skill invocation).
  - *Change Propagation Checklist*: i18n single-mirror agent findings require cross-mirror check before fixing — single-mirror fix creates new ko-KR ↔ ja-JP divergence; either fix both or document as cross-mirror design intent (memory closure pattern).
  - *Verifying Changes Locally*: agent claims about external facts (GitHub Actions versions, package availability, transitive deps, "dead code" claims) reflect agent training cutoff and must be verified via `gh api` / `pip show` / `grep` for module callers before commit propagation. The v2.18.0 cycle caught two such retreat candidates.
  - *Verifying Changes Locally*: `check-hook-script-parity.py` scope clarification — it validates *byte-equal i18n locale mirrors* (EN ↔ ko-KR ↔ ja-JP), NOT sh ↔ ps1 *behavioral* parity. The latter requires manual cross-script review when modifying either side. CLAUDE.md grew 94 → 98 lines, well under the 200-line ceiling.

- **Trustworthy Agents framework guide** (`docs/guides/trustworthy-agents-guide.md` + ko-KR + ja-JP mirrors) mapping Anthropic's five-principle, four-architectural-layer framework onto concrete Claude Code configuration surfaces. Complements (does not duplicate) the existing Threat Catalog in `plugin/references/security-patterns.md`. Cross-linked from `getting-started.md`, `effective-usage-guide.md` (Plan Mode strategy framing), and `advanced-features-guide.md` Further Reading. Trigger: Anthropic Research "Trustworthy Agents in Practice" (2026-04-09) — normative guidance per `docs/ROADMAP.md:83` trigger #2.

- **CLAUDE.md workflow rules (3 entries from trustworthy-agents-guide session learnings)** — captured three reusable i18n-specific patterns surfaced while writing a new top-level guide and its ko-KR + ja-JP mirrors:
  - *Change Propagation Checklist*: new i18n guide atomic-commit rule — adding a new guide (vs. editing an existing one) requires committing all 3 language files (EN + ko-KR + ja-JP) in the SAME commit; staging EN alone causes `check-i18n-parity.py` (structural mirror check) to fail. Existing-guide edits don't have this constraint.
  - *Change Propagation Checklist*: i18n guide relative-path depth — files at `docs/i18n/<locale>/guides/` are 2 directories deeper than `docs/guides/`, so relative links to `plugin/...` need `../../../../` (4 up), not `../../` (2 up). Copying paths verbatim from EN silently breaks i18n cross-links; only `lychee` catches it locally.
  - *Change Propagation Checklist*: cross-language anchor consistency — when a guide deep-links into another guide's heading via `file.md#anchor`, keep the target heading in English across all 3 language versions so the same anchor ID resolves uniformly; translate section bodies, not cross-referenced heading text. CLAUDE.md grew 98 → 101 lines, well under the 200-line ceiling.

- `effective-usage-guide.md`: user-level session commands — `/btw` (side questions without context growth), `/rename` (session labels for `--resume`), `Ctrl+G` (plan-mode editor open), partial compaction via `Esc + Esc → Summarize from here`. Common Failure Patterns section compressed from 5 sub-headings to a single table for readability.

- `claude-md-guide.md`: mid-session update patterns — `#` prompt shortcut for appending learnings, and custom compaction directives embedded in CLAUDE.md that survive auto-compaction.

- `plugin/references/tool-description-quality.md` (NEW): principles for writing skill and tool descriptions — domain expert framing, trigger phrase patterns, dual-format responses, actionable error messages, evaluation-driven iteration.

- `/audit` advisory check: skill `description` quality — non-scoring, surfaces in Phase 4 "All Suggestions" output. Runs only when `.claude/skills/` exists in the audited project. Scoring contract `audit-score-v4.2.0` is unchanged.

- `advanced-features-guide.md`: cross-link to the new reference (patch bump 1.3.0 → 1.3.1).

- New guide: `docs/guides/multi-agent-patterns-guide.md` — Orchestrator-Worker pattern (4-axis worker spec — objective, output format, tool guidance, boundaries), effort scaling rules, sub-agent context budget (1–2k token summaries), breadth-first search strategy, parallel dispatch primer. ko-KR and ja-JP mirrors included; frontmatter version 1.0.1 (introduced at 1.0.0, patch-bumped to 1.0.1 during the same release polish pass).

- Cross-link added to `advanced-features-guide.md` Agents section (patch bump 1.3.1 → 1.3.2).

- New guide: `docs/guides/workflow-patterns-guide.md` — interview-first specification (`AskUserQuestion`), Writer/Reviewer multi-session, test-first multi-Claude, fan-out for batch tasks (with explicit cost and safety warnings — dry-run, `--allowedTools`, auto-mode fallback), worktrees and parallel sessions. ko-KR and ja-JP mirrors included; frontmatter version 1.0.1 (introduced at 1.0.0, patch-bumped to 1.0.1 during the same release polish pass).

- Cross-links added to `getting-started.md` "What's Next" for the new workflow-patterns + multi-agent-patterns guides; combined patch bump 1.2.6 → 1.2.7.

### Changed

- **Philosophy #4 wording renamed across all README mirrors and the Day-based progression frame compressed.** Reflects that AI tooling improves continuously rather than reaching a static depth, and brings the Day-based adoption frame in line with modern AI tool adoption cadence (weekly/bi-weekly rather than monthly/quarterly).
  - EN canonical (`README.md:17,28,81,83,95`): tagline + Philosophy #4 + body reference + 2 headings updated. `Progressive depth` → `Continuous reinforcement`; `Day 30` → `Day 7`; `Day 100+` → `Day 14+`.
  - ko-KR mirror (`docs/i18n/ko-KR/README.md:5,20,73,75,87`): `점진적 심화` → `점진적 강화`; tagline phrase reflowed `깊어지는` → `강화되는`; Day numbers compressed.
  - ja-JP mirror (`docs/i18n/ja-JP/README.md:9,20,73,75,87`): `段階的な深化` → `段階的な強化`; Day numbers compressed.
  - `docs/ROADMAP.md:24-26`: "Progressive disclosure" North Star axis description updated to Day 7 / Day 14 references. The **axis name** `Progressive disclosure` is preserved — it remains one of the 4 North Star axes.
- **Intentional EN ↔ ko-KR / ja-JP nuance divergence (documented, not drift).** EN reads `Continuous reinforcement` (emphasis on ongoing repetition), while ko-KR reads `점진적 강화` and ja-JP reads `段階的な強化` (both emphasis on gradual growth). This was the agreed framing. The `check-i18n-parity.py` validator checks file-structure parity, not semantic synonymity, so this nuance gap is invisible to CI — recorded here so future i18n review does not "fix" it.
- **Rationale.** "AI tooling develops daily, learning continuously, Day 100 is too long" — user-stated framing rationale, 2026-05-13. Calendar anchors `Day 7` (one week, natural weekly anchor) and `Day 14+` (two-week milestone with `+` preserving "beyond" semantics from the old `Day 100+`).
- **Day-frame language precision adjustment (follow-up to the rename above).** Replaced misleading verbs in user-facing copy that implied threshold-based feature unlock — the plugin has no `days_since_install` field and no `if day_N then enable_X` gates; all skills (`/create`, `/audit`, `/secure`, `/optimize`) are available from the first run. The Day framing communicates *typical user discovery cadence*, not *feature unlock schedule*. Audit confirmed zero references to `Day N` in `plugin/` (skills + references + hooks); `Rule 3 — Stagnation Detection` triggers on changelog entry counts (3+ consecutive), not elapsed days.
  - `README.md:28`: `Day 14 unlocks cross-skill memory and automated drift detection.` → `Day 14 is when cross-skill memory and automated drift detection come into their own.`
  - `README.md:97`: `After multiple skill runs, the plugin activates its meta-system layer` → `Over multiple skill runs, the plugin's meta-system layer fills out`
  - `docs/i18n/ko-KR/README.md:20`: `… 활성화됩니다` → `… 본격적으로 진가를 발휘합니다`
  - `docs/i18n/ko-KR/README.md:87` heading: `## Day 14+ — 메타 시스템 활성화` → `## Day 14+ — 메타 시스템 활용` (also fixes pre-existing translation drift — EN reads `Meta-System Engagement`, JA reads `エンゲージメント`, but KO read `활성화` = "activation"; "활용" = "utilization" matches the engagement nuance)
  - `docs/i18n/ko-KR/README.md:89`: `여러 번 스킬을 실행하면, 플러그인은 메타 시스템 레이어를 활성화합니다` → `스킬을 거듭 실행하면서, 플러그인의 메타 시스템 레이어가 충실해집니다`
  - `docs/i18n/ja-JP/README.md:20`: `… 有効化されます` → `… 本領を発揮します`
  - `docs/i18n/ja-JP/README.md:89`: `複数のスキルを実行すると、プラグインは … を活性化します` → `スキルを繰り返し実行する中で、プラグインの … が充実していきます`
  - `docs/ROADMAP.md:24-25` left unchanged — "Day 14 users rely on…" is descriptive of user habit (depend on / count on), not a feature-gate claim.
- **Polish pass on Anthropic Engineering 2026 patterns documentation** — reconciled `#` shortcut wording across `effective-usage-guide.md` and `claude-md-guide.md`; added Principle 3 scope note and parallel-structure examples to `tool-description-quality.md`; clarified `/audit` advisory check applicability; switched `multi-agent-patterns-guide.md` effort scaling 3rd-row column to numeric metric; corrected ja-JP "ワークロードスケーリング" translation; added PowerShell equivalent and `git worktree` cleanup guidance to `workflow-patterns-guide.md`. Patch bumps across affected guides.

### Fixed

- **`/audit` Phase 1.5 Layer 2 gains test-fixture path-prefix exclusion** — fixes the audit-of-audit pathology where this plugin auditing its own source repo treated four CI verifier fixtures (`ci/fixtures/monorepo/input/` plus three `sessionstart-orchestrator/*` fixtures that legitimately ship `package.json` or other manifest files for the smoke verifier) as real subpackages via Phase B.5 disclosure walk inclusion. Layer 2 now combines two exclusion checks: 2a (existing — segment match against `node_modules`, `dist`, `build`, etc.) and 2b (NEW — path prefix match against `ci/fixtures/`). Updated in `plugin/skills/audit/SKILL.md` Phase 1.5 + `plugin/skills/audit/references/checks/monorepo-detection.md` §3 algorithm pseudocode and Layer 2 prose. Resolves recommendation `monorepo-detection-fixture-pollution-gap` (PENDING since 2026-05-10). Maintainer-declared `test_fixtures` spec field (the more general fix option) intentionally deferred — extension requires explicit prefix-list addition or a new spec field, scope note in `monorepo-detection.md` §3 records the boundary.

- **Dangling `Phase 1 Global Invariant #6` and `Phase 1 Environmental Assumption` citations removed** — 12 occurrences across `plugin/references/learning-system.md` (5) and 4 SKILL.md files (`audit` 4, `secure` 1, `create` 1, `optimize` 1) referenced an undefined internal-planning artifact (no definition in shipped repo or gitignored `docs/superpowers/plans/` and `specs/`; originated from v2.12.0 design-doc scaffolding per `git log -S` evidence). Surrounding prose preserves all behavioral content; runtime behavior unchanged. `plugin/references/learning-system.md` frontmatter version bumped `2.3.5` → `2.3.6`.

## [2.18.0] - 2026-05-12

### Added

- **Permission Modes and Sandboxing teaching content** in
  `docs/guides/settings-guide.md` (bumped to v1.1.0) — new
  "Permission Modes and Safety (Advanced)" section covering
  `permissions.defaultMode` (six modes — `default`, `acceptEdits`,
  `plan`, `auto`, `dontAsk`, `bypassPermissions`), `autoMode`
  configuration with explicit scope-precedence note (the classifier
  deliberately ignores `autoMode` in shared `.claude/settings.json`),
  and `sandbox` configuration. Anthropic-internal measurement claims
  (84% prompt reduction; 0.4% FP / 17% FN at Stage 1 + Stage 2
  full-pipeline) carry explicit qualifiers and separate denominators
  (n=10,000 benign tool calls; n=52 real overeager actions). i18n
  mirrors (`ko-KR`, `ja-JP`) bumped to v1.1.0 in lockstep.
- **`templates/advanced/.claude/settings.json` permission/sandbox
  demonstration** — added `permissions.defaultMode: "acceptEdits"` and
  a `sandbox` block with `excludedCommands: ["docker *"]` (matching the
  docker-sandbox incompatibility note in canonical sandboxing docs).
  `autoMode` intentionally not in shared project settings; users
  configure it in user / local / managed scopes per the guide section.
  i18n mirrors updated to match structure.
- **`plugin/skills/secure/SKILL.md` Phase 1.4–1.6 informational scans**
  for `permissions.defaultMode`, sandbox state (multi-scope-aware
  reporting), and Auto Mode trust environment (notes the
  shared-project scope ignore rule). Phase 2 adds a "Permission and
  Safety State (informational)" subsection. Phase 3 fix actions remain
  limited to 1.1–1.3 — permission mode, sandbox, and Auto Mode are
  decision points (plan tier, platform prerequisites, trust model),
  not surfaces `/secure` should auto-write.
- **`plugin/references/security-patterns.md` Permission and Safety
  Decision Principles section** — work-type-by-mode mapping with full
  Auto Mode eligibility (Anthropic API only on Max / Team / Enterprise
  / API plans; Sonnet 4.6, Opus 4.6, or Opus 4.7 — Max plan: Opus 4.7
  only; admin enablement on Team / Enterprise), sandboxing-by-blast-
  radius criteria including the canonical "effective sandboxing
  requires both filesystem and network isolation" warning, and a
  combination-guidance table framed as "principle, not flowchart".
- **Five-round Anthropic engineering insights review series** in
  `docs/plans/` (`anthropic-engineering-insights-review.md` and
  `…-round-2.md` through `…-round-5.md`) — review of Anthropic
  engineering blog posts mapped against repo surfaces (skills,
  guides, templates, CI scripts).
- **`docs/plans/decision-backlog.md`** — single entry point
  consolidating the review series' 22 proposals into adopt / pilot /
  defer / skip buckets with one-line rationale and prerequisite per
  row. Defines explicit stop conditions for further review rounds.
- **Best Practices parity refinement** in
  `docs/guides/claude-md-guide.md` (bumped to v1.2.0) — added
  context-rot rationale to the 200-line guidance, citing model recall
  degradation from long contexts as the documented mechanism behind
  length-pressure motivation. Framing kept conservative ("one
  motivation behind length limits") to avoid post-hoc rationalization.
  i18n mirrors (`ko-KR`, `ja-JP`) bumped to v1.2.0 in lockstep.
- **Agent Skills authoring guidance** in
  `docs/guides/advanced-features-guide.md` (bumped to v1.3.0) — new
  Progressive Disclosure subsection (three-level loading: metadata /
  SKILL.md body / supporting files), distinguished skill-local
  `references/` (canonical bundled-skill structure) from shared
  `plugin/references/*.md` (non-canonical, cross-skill content only),
  enhanced `name`/`description` field documentation to surface the
  trigger-phrasing role, added evaluation-driven iteration design
  pattern, and added install-from-trusted-sources security note.
  i18n mirrors bumped to v1.3.0 in lockstep.
- **`docs/plans/oracle-coverage-map.md`** — discovery artifact mapping
  the 14 `/audit` rules (Tiers 1-3) against the 11
  `.github/scripts/check-*.py` CI validators. Surfaces null direct
  oracle coverage as the substantive finding (CI scripts validate
  this repo's content; `/audit` rules evaluate user projects —
  disjoint domains) and reframes the downstream "Oracle check"
  terminology toward rule-internal determinism (re-execute the rule's
  own primitives on subagent claims) rather than external CI re-run.
  `decision-backlog.md` L-row updated with shipped marker.
- **Skill description trigger phrasing** across all four plugin
  skills (`plugin/skills/{create,audit,secure,optimize}/SKILL.md`) —
  added "Use when the user asks to …" trigger guidance per the new
  Agent Skills authoring section in `advanced-features-guide` v1.3.0
  (closes a self-consistency gap where the recently-shipped guide
  recommended trigger phrasing that our own skills did not follow).
  `/audit` and `/optimize` descriptions additionally clarify the
  detect-vs-modify boundary — `/audit` "lists improvement
  opportunities (does not modify files)", `/optimize` "fixes hook
  quality (modifies files)" — to reduce skill-purpose overlap in
  the slash-command menu.
- **`/audit` SKILL.md inline ID glosses** — added one-line pointers
  on first reference for `L1`–`L6` (LAV components, definitions in
  `references/checks/lav.md`) in Phase 4 and `B1`–`B5` (sprint-
  contract parser branches, definitions in
  `references/checks/sprint-contract.md`) in Phase 4.5, so a reader
  of `SKILL.md` does not need to fetch the reference files before
  parsing the surrounding text.
- **`/audit` Phase 3.7 Output Validation contract** in
  `plugin/skills/audit/SKILL.md` — every finding from Phase 1–3.6
  must trace to a deterministic primitive (`Read`, `Grep`, `Glob`,
  line count, JSON parse) actually invoked against project state,
  with hypothesis-vs-oracle agreement before surfacing and BOTH-
  sides surfacing on disagreement. Reframes the original Round 4
  "Oracle check" terminology toward rule-internal determinism per
  the null-coverage finding in
  `docs/plans/oracle-coverage-map.md`; conditional recommendations
  and free-text remediation language are explicitly carved out as
  not requiring an oracle. `decision-backlog.md` A'-postcheck row
  updated with shipped marker.

### Fixed

- **`.github/workflows/docs-check.yml` encoding-check job: PCRE byte-match
  correctness.** Replaced `grep -lP '\xef\xbf\xbd'` with
  `grep -l $'\xef\xbf\xbd'` (bash ANSI-C quoting). Under Ubuntu's UTF-8
  locale, PCRE2 interprets `\xhh` escapes as Unicode codepoints
  (U+00EF, U+00BF, U+00BD) rather than as bytes, silently failing to
  match the actual U+FFFD UTF-8 byte sequence. The bash `$'...'` form
  injects the literal three-byte sequence into grep's pattern argument,
  restoring the intended detection. The job had been GREEN since v2.11.1
  shipped in 2026-04-22 despite the embedded glyph in CHANGELOG.md L812
  going undetected for the full window.
- **`CHANGELOG.md` L812: removed embedded U+FFFD glyph** that the v2.11.1
  notes used as a visual citation of the corruption being described. With
  the encoding-check fix above, leaving the glyph in place would now
  cause the job to fail on every push. Replaced the parenthetical glyph
  with a descriptive phrase ("the U+FFFD glyph (the standard Unicode
  'unknown character' placeholder)") and added an explicit note that the
  literal glyph is intentionally NOT embedded.
- **`ci/fixtures/monorepo/expected/` alignment with golden snapshot.**
  `expected/audit-output.md` now shows the v2.13.0 Subpackage Score
  Rollup table instead of the pre-v2.13.0 "scheduled for a future audit
  release" placeholder, and the missing `expected/local/qa-report.md`
  was added to mirror `ci/golden/monorepo/local/qa-report.md`.
  `compare-golden.{sh,ps1}` (the maintainer debug helper) now reports
  `[OK] monorepo` instead of byte mismatch + missing-file errors.
  `ci/fixtures/**` smoke test (`check-smoke-fixtures.py`) is unaffected
  — it consumes `expected.json` per fixture, not the `expected/`
  directory contents.
- **`docs/i18n/ko-KR/README.md` + `docs/i18n/ja-JP/README.md` ja-JP
  template label drift.** The Repository Structure tree described
  ja-JP as carrying a partial-template subset, but
  `docs/i18n/ja-JP/templates/` has been at full structural parity
  with `docs/i18n/ko-KR/templates/` (28 files: starter + advanced with
  `.claude/` agents/rules/skills, hooks, `.mcp.json`, `sprint-contract.md`).
  Both i18n READMEs now describe ja-JP as "guides + templates", matching
  the root README phrasing. Drift fix per `CLAUDE.md` `Change Propagation
  Checklist` semantics — no frontmatter version bump.
- **`README.md` (root) + `docs/i18n/ko-KR/README.md` +
  `docs/i18n/ja-JP/README.md` plugin-scope cascade.** All three READMEs
  still described Claude Code as supporting "official plugins" only,
  after `docs/guides/recommended-plugins-guide.md` v1.0.1 had broadened
  to "official + community". The guide-side wording update did not
  cascade to the three README mirrors. All three READMEs now match the
  guide wording ("official (Anthropic-maintained) and community
  plugins").
- **`docs/i18n/ko-KR/README.md` + `docs/i18n/ja-JP/README.md` L159
  Repository Structure row.** The earlier ja-JP template-label-drift
  fix above covered the framing prose but missed the directory listing
  in each i18n README, which still read "부분 템플릿" / "部分テンプレート".
  Both rows now read "템플릿" / "テンプレート" — no "partial" qualifier,
  matching the actual structural parity already in place.
- **`CHANGELOG.md` Unreleased Removed entry arithmetic.** The phrasing
  "16 routing rows: Adopt 3, Pilot 3, Defer 5, Skip 2" did not sum
  (3+3+5+2 = 13). The original decision table held 13 rows (Adopt 3,
  Pilot 3, Defer 5, Skip 2 — confirmed against the deleted file's git
  history); the conflation came from mixing row count with the higher
  proposal count. Entry rewritten as "proposals routed across 13
  decision rows".
- **`plugin/skills/audit/references/oracle-coverage-map.md` L81 stale
  reference.** Text referenced "the backlog's Defer bucket"; the
  backlog file (`docs/plans/decision-backlog.md`) was removed in the
  same-cycle docs/plans/ cleanup and the LLM-judge cluster's tracking
  moved to `docs/ROADMAP.md` "Revisit Triggers" → "LLM-as-judge evals
  for `/audit` rubrics" row. Reference now updated.
- **`/plugin install` command form + `/reload-plugins` follow-up
  missing across all install instructions.** Anthropic's canonical
  plugin docs (`code.claude.com/docs/en/discover-plugins`) specify
  `/plugin install plugin-name@marketplace-name` as the install
  form, and require `/reload-plugins` to activate after install.
  Six locations — `README.md:40`,
  `docs/guides/getting-started.md:31`, and their ko-KR + ja-JP
  mirrors — all showed `/plugin install guardians-of-the-claude`
  without the marketplace suffix or the reload step. All six now
  use `/plugin install guardians-of-the-claude@guardians`
  (marketplace name from `.claude-plugin/marketplace.json`)
  followed by `/reload-plugins`.
- **`docs/i18n/ko-KR/statusline.sh` stale path-truncation logic.**
  The ko-KR mirror retained the pre-fix logic (`MAX_PATH_LEN=40` and
  unconditional `~/**/${PARENT}/${CURRENT}` truncation); root
  `statusline.sh` had been updated to track an `IS_HOME` flag and
  branch the truncated form, so non-home paths no longer get a
  misleading `~/` prefix. ko-KR file now matches root byte-for-byte.
  (No ja-JP `statusline.sh` exists; statusline mirror is ko-KR
  only.)
- **`docs/i18n/ja-JP/guides/{advanced-features-guide,mcp-guide}.md`
  frontmatter `title:` + H1 untranslated.** Of the nine ja-JP
  guides, these two were the only files whose `title:` and `# H1`
  were still in English (`"Advanced Features"`, `"MCP Integration"`)
  while body content was fully translated. Both now read
  `"高度な機能"` and `"MCP 連携"` respectively, matching the body-
  language consistency of the other seven ja-JP guides. The
  corresponding link labels in `docs/i18n/ja-JP/README.md`
  Documentation table (rows 7 and 8) updated to match in lockstep.
- **`docs/i18n/ja-JP` `/create` prompt-option references unified
  to original English.** The ja-JP doc set quoted the `/create`
  option label as `「既存プロジェクト」` (translated) in three
  locations and as `「Existing project」` (original) in two —
  readers could not tell which form would appear at the actual
  prompt. ja-JP now quotes the English original (`"Existing
  project"`, plus the paired `"New project"` and
  `"Add missing features"` rows in the path-selection table)
  everywhere it cites the `/create` option list, matching the
  actual prompt label produced by `plugin/skills/create/SKILL.md`.
  Sentences that use 既存プロジェクト as a generic phrase rather
  than a prompt-option quote (e.g., `effective-usage-guide.md` L91
  section heading) are intentionally retained.
- **`docs/i18n/ko-KR` `/create` prompt-option references unified
  to original English** (continuation of the ja-JP policy from
  the previous entry). ko-KR was self-consistent on "기존 프로젝트"
  but mismatched the actual prompt label that `plugin/skills/create/
  SKILL.md` produces ("Existing project"). Five locations updated:
  `README.md` path-selection table (3 rows) and follow-up tip
  quote; `guides/getting-started.md` Step 1 quote and the
  Starter→Advanced upgrade quote; `guides/effective-usage-guide.md`
  Onboarding section quote. Generic uses of "기존 프로젝트" as a
  phrase rather than a prompt-option quote (e.g.,
  `effective-usage-guide.md` L90 section heading, `README.md` L52
  path-selection intro prose) intentionally retained — symmetric
  with the ja-JP carve-out.
- **`.gitignore` add `.pytest_cache/` entry.** Existing Python
  cache section ignored `__pycache__/` and `*.pyc` but not
  `.pytest_cache/`, leaving `git status` noise from local pytest
  runs against the `.github/scripts/` validators.
- **`/audit` T2.4 Autonomy Risk Policy check** (weight 0.15) — new T2 item with 5 sub-checks:
  - 4a wildcard allow detection in `permissions.allow[]` (`Bash(*)`, `Bash(python*)`, `Bash(npm run *)`, `Agent(*)`, `PowerShell(*)`)
  - 4b `bypassPermissions` misuse in shared `.claude/settings.json` without CLAUDE.md disposable-environment note
  - 4c auto mode without `autoMode.environment` — advisory-only (no scoring impact) per docs default-strict trust boundary
  - 4d MCP credential exposure in project-scope `.mcp.json` (4d-i literal/defaulted secrets MINIMAL, 4d-ii placeholders without migration note PARTIAL)
  - 4e scoped destructive Bash allow (`git push -f`, `rm -rf`, `curl|bash`, `gh api * DELETE`)
  Each finding cites a Threat Catalog incident ID with anchor link to `security-patterns.md`.
- **Threat Catalog in `plugin/references/security-patterns.md`** — new `## Threat Catalog` H2 with 4 taxonomic categories (Overeager Behavior, Honest Mistakes, Prompt Injection, Model Misalignment) and 6 named incidents with kebab-case IDs (`scope-escalation`, `credential-exploration`, `data-exfiltration`, `safety-bypass`, `agent-inferred-parameters`, `tool-output-injection`). Each incident has Scenario / Trigger / Mitigation prose + Cross-Reference Table summarizing incident → mitigation surface → catalog citation target.
- **`/secure` autonomy scan and tightening** — new scan subsection (1.4 Autonomy Risk Policy) detects the same 4a/4b/4d/4e violations as `/audit` T2.4 (4c skipped). New fix subsection (3.4 Autonomy Tightening) auto-mutates 4a wildcards (narrow per project signals or move to `ask:[]`) and 4e scoped destructive allows (move to `ask:[]`). Provides suggestion-only output for 4b and 4d sub-checks where mutation could expose secrets or alter major permission modes.
- **`ci/fixtures/t2-4-violations/`** — new CI fixture exercising all 5 T2.4 sub-checks with intentional violations (`bypassPermissions`, `Bash(*)`, `Agent(*)`, `rm -rf:*`, `git push --force:*`, literal `sk-` API key, `${VAR}` placeholder). Expected output marker file ships now; byte-exact golden snapshot pending real `/audit` invocation against the fixture (post-merge step).
- **Synergy Bonus rationale corrected** in `ci/fixtures/t2-4-violations/expected/audit-output.txt` — the SB ineligibility marker now cites the actual cause (T2.1 PARTIAL, deny list missing `secrets/` pattern) rather than T2.4 score impact. Synergy Bonus eligibility depends on T2.1 and T2.2 both reaching PASS, independent of T2.4 per `scoring-model.md`.
- **Internal cycle vocabulary removed from shipped surfaces** — `ci/fixtures/t2-4-violations/expected/audit-output.txt` header replaced an internal task identifier with "once a real `/audit` invocation freezes the golden snapshot"; `plugin/skills/audit/references/checks/t2-protection.md` substituted `/secure`'s internal phase label with the descriptive "Autonomy Tightening step", keeping the runtime-loaded reference free of internal vocabulary.
- **i18n parity restored (drift only, no `version` bump)** — `docs/i18n/ko-KR/guides/advanced-features-guide.md:170` and `docs/i18n/ja-JP/guides/advanced-features-guide.md:170` removed editorial expansions absent from the EN canonical (a per-directory enumeration after "supporting files" and a judgmental "비표준"/"非標準" qualifier). `docs/i18n/ja-JP/guides/directory-structure-guide.md:67` translated "decision changelog" as "決定 changelog" (was "決定ジャーナル", which conflicted with the same-guide line-100 "Decision journal" concept and the ja-JP `README.md` "圧縮された changelog" loanword precedent). `docs/i18n/ko-KR/guides/mcp-guide.md:130` aligned the parenthetical "(hooks, agents, skills)" to English loanwords matching the rest of the ko-KR guide set.
- **i18n template link hops normalized** — `docs/i18n/ko-KR/guides/getting-started.md` and `docs/i18n/ja-JP/guides/getting-started.md` (lines 39 and 70 in both files) corrected the `templates/README.md` and `templates/advanced/CLAUDE.md` link targets from `../../../../templates/...` (4 hops to root EN) to `../templates/...` (1 hop to same-language i18n mirror). Aligns with the line-22 `README.md` link pattern in both files; `docs/i18n/{ko-KR,ja-JP}/templates/README.md` and the corresponding `templates/advanced/CLAUDE.md` mirrors verified to exist before the redirect.
- **`plugin/hooks/session-start.sh` repeated-declines selection bug** — the jq pipeline at line 214 used `sort_by([-(.decline_count), .last_seen]) | reverse | .[0]`. The `sort_by` already orders descending by `decline_count` via the negation, so the additional `| reverse` flipped the order back and `.[0]` ended up selecting the recommendation with the *lowest* `decline_count` instead of the highest. The PowerShell sibling `session-start.ps1:236` was already correct (`Sort-Object _dc -Descending` then `[0]`), so the two scripts diverged behaviorally on the same input. Fix removes the negation while keeping `| reverse`, so `.[0]` is highest `decline_count` with newest `last_seen` as the tie-break (matching the intent stated in the immediately preceding comment).
- **Scoring formula simulation sample count synced to 6** — `.github/workflows/docs-check.yml` job name and step name plus `plugin/references/scoring-model.md` acceptance note were left at "5-sample simulation" after `ci/scripts/check-scoring-formula.py` gained the `t2_4_minimal` sample (raising the actual count to 6). Updated all three references to "6-sample" to match the script's docstring and `SAMPLES` list.
- **`referencing==0.37.0` pinned explicitly to prevent transitive drift** — `jsonschema==4.23.0` declares `referencing` as a runtime dependency (added in jsonschema 4.18.0) and three validators (`check-json-schemas.py`, `check-smoke-fixtures.py`, `preflight-schema.py`) import the `Registry`/`Resource` API directly. Without an explicit pin the resolved version drifts inside jsonschema's allowed range, so a future jsonschema patch could pull a newer `referencing` with breaking API changes. `.github/workflows/docs-check.yml` `json-schema` job and `CLAUDE.md` "Verifying Changes Locally" first-time-setup line both add `referencing==0.37.0` (matches the version bundled with the current pinned jsonschema).
- **Windows `cp949` `UnicodeError` guard added to 9 validators** — `.github/scripts/check-{frontmatter-parity,i18n-parity,json-schemas,smoke-fixtures,readme-badge-sync,changelog-anchor-slug,recommendation-registry,skill-stability,hook-script-parity}.py` all gained the standard `sys.stdout.reconfigure(encoding="utf-8")` / `sys.stderr.reconfigure(encoding="utf-8")` `try`/`except (AttributeError, OSError)` block immediately after the stdlib import group, matching the pattern already in `ci/scripts/preflight-schema.py`. CI on Ubuntu was unaffected, but local Windows execution under a Korean or Japanese locale raised `UnicodeEncodeError` when these scripts printed em-dashes or non-ASCII paths — surfaced when `CLAUDE.md` "Verifying Changes Locally" recommends running them before push.
- **`templates/advanced/hooks/{stop,subagent-stop,pre-compact}.ps1` bash self-skip guard added** — the three observability hooks (file-append behavior into `.claude/local/hooks/*.md` and `.jsonl`) lacked the `if (Get-Command bash ...) { exit 0 }` guard that `validate-prompt.ps1` (lines 18–24) already had. On dual-interpreter systems (e.g., Windows with Git Bash + PowerShell) both the bash hook entry and the ps1 entry fired and appended to the same file, producing two records per turn / subagent completion / compact event. The new guard defers to the bash hook when both are on PATH, matching the precedence rationale documented in `validate-prompt.ps1`. Both i18n mirrors (`docs/i18n/ko-KR/templates/advanced/hooks/`, `docs/i18n/ja-JP/templates/advanced/hooks/`) updated identically so `check-hook-script-parity.py` byte-equal invariant stays satisfied.
- **`statusline.sh` `FIVE_H_RESET` epoch/ISO dual handling** — line 71 used `$((FIVE_H_RESET - NOW))` which assumes the `.rate_limits.five_hour.resets_at` field is a Unix epoch integer. If Claude Code delivers an ISO-8601 string instead, bash arithmetic would emit a syntax error and the remaining-time display silently broke. Defensive conversion now detects numeric-epoch (`^[0-9]+$`) versus ISO and converts the latter via GNU `date -d` falling back to BSD `date -j -f`, falling back to empty (no display) on parse failure rather than letting the arithmetic error propagate.
- **`ci/README.md` documents `t3`/`t7_*` scripts as intentional atomic fixture runners** — `ci/scripts/t3_model_drift_check.py`, `t7_optimize_e2e_check.py`, `t7_secure_counts_check.py`, and `t7_secure_e2e_check.py` had no separate CI job and looked like dead code on first scan. Verification showed `t3_model_drift_check.py` is imported by `.github/scripts/check-smoke-fixtures.py` and the `t7` trio is exercised by the full smoke run via `SKILL_HANDLERS`. New `## Atomic fixture runners` section enumerates them as intentional local-only debugging entry points so future scans do not flag them again.
- **Script logic clarifications (4 minor improvements)**:
  - `ci/scripts/check-scoring-contract-consistency.py:44` — hardcoded `>= 8` golden-count threshold extracted into a named `MIN_GOLDENS` module constant with a comment explaining the floor (1 self + 7 real-project goldens). Same fail-loud behavior, named symbol for future change visibility.
  - `CLAUDE.md` cross-platform gotchas (`< /dev/stdin` rule) narrowed in scope: the rule applies *only when piping stdin through jq* (SessionStart-style JSON payloads), and the whole-stdin `cat` / `[Console]::In.ReadToEnd()` pattern used by `UserPromptSubmit` / `Stop` / `SubagentStop` / `PreCompact` hooks is documented as a separate valid pattern.
  - `.github/scripts/check-smoke-fixtures.py:287` `acquire_lock` docstring gained an explicit "Caller contract until Phase 2+" paragraph stating that the current implementation does NOT detect contention and that two concurrent acquires would silently overwrite each other; future multi-shell fixtures must implement fcntl/msvcrt support *before* landing.
  - `.github/scripts/lib/recommendation_registry.py:53` — separated the `resolved_by is None` case from the `not in resolvers` case so the failure message no longer prints the ambiguous Python `'None'` literal and instead reads "RESOLVED requires non-null resolved_by".
- **ko-KR i18n drift fixes (5 substantive corrections, drift only — no `version` bump)**:
  - `docs/i18n/ko-KR/README.md:113` — corrected mistranslated heading from "템플릿 구조" to "내부 구성" so it accurately reflects the EN canonical "What's Inside" (whole-repo tree, not just templates).
  - `docs/i18n/ko-KR/guides/claude-md-guide.md:91` — removed an EN-absent qualifier "커스텀" before "skill과 agent" that was narrowing the EN canonical's "multiple skills and agents" semantics.
  - `docs/i18n/ko-KR/guides/advanced-features-guide.md` — unified "에이전트"→"agent" and "스킬"→"Skill" English loanwords throughout (was mixed: section headings used Korean while body used English), matching the convention already adopted in the rest of the ko-KR guide set after `mcp-guide.md` was aligned.
  - `docs/i18n/ko-KR/templates/advanced/.claude/agents/backend-developer.md:28` — renamed "## 제약 사항" to "## 제한사항" so all three sibling agent files (backend-developer / security-reviewer / test-writer) use the same Korean rendering of the EN "Constraints" heading.
  - `docs/i18n/ko-KR/templates/advanced/.claude/skills/add-endpoint/SKILL.md` — translated the four "## Step N:" headings to "## 단계 N:" so the file matches the sibling `run-checks/SKILL.md` (which already used "단계") inside the same `skills/` directory.
- **ja-JP i18n drift fixes (3 corrections, drift only — no `version` bump)**:
  - `docs/i18n/ja-JP/guides/recommended-plugins-guide.md:15` — unified the in-file mix of Japanese-transliterated `subagent` and English-loanword `subagents` to the English form, matching the rest of the file.
  - `docs/i18n/ja-JP/README.md:11-13` — moved the language switcher block above the intro paragraph so the structural ordering matches the EN canonical (banner → switcher → intro), instead of the previous (banner → intro → switcher).
  - `docs/i18n/ja-JP/README.md:87` — retranslated the "Day 100+" section heading to preserve the EN canonical's "Engagement" nuance (user-engagement / participation), changing the previous wording that read closer to "activation" (a feature-on connotation).
- **ko-KR cross-file spelling sweep (drift only — no `version` bump)** — two parallel cross-file inconsistencies were unified per user direction:
  - "directory" loanword: 7 occurrences of the alternative Korean spelling across 5 files (`docs/i18n/ko-KR/guides/{settings-guide,advanced-features-guide}.md`, `docs/i18n/ko-KR/templates/advanced/.claude/{CLAUDE.md,rules/testing.md,rules/architecture.md}`) were normalized to the more prevalent variant already used by 21 occurrences across 6 sibling files.
  - "no" response word: 4 occurrences of the verb-ending form `아니오` across 3 files (`docs/i18n/ko-KR/guides/{claude-md-guide,directory-structure-guide,mcp-guide}.md`) were normalized to the standard interjection form `아니요` per the National Institute of Korean Language convention (the verb-ending form `아니오` is grammatically reserved for sentence-final verb conjugations like `~이오`, not yes/no responses).

### Changed

- **`docs/PRIVACY.md` clarified separation of remote transmission vs
  local state files.** Previous wording ("does not collect, store, or
  transmit any user data" + "does not store any information outside your
  project directory") created ambiguity against the visible local state
  files (`profile.json`, `recommendations.json`, `config-changelog.md`,
  `state-summary.md`, `qa-report.md`). The policy now distinguishes the
  two: no remote transmission / telemetry / network access (unchanged
  promise), AND explicit description of the local state files written
  inside the project directory to support cross-skill learning. Added a
  Stateless mode section explaining the no-state-write fallback when
  `local/` is unwritable.
- **`README.md` "Unwritable `local/` handling" updated to reflect current
  stateless mode implementation.** Previous text said "NOT yet
  implemented in v2.11.0 — privacy-sensitive projects ... should pin
  v2.10.x until a future minor", which was outdated since v2.12.0
  shipped the full Final Phase persistence-bypass. Updated text now
  documents stateless mode (one-time warning, all state file writes
  skipped, learning state non-persistent across sessions) as the
  recommended approach for privacy-sensitive projects. ko-KR + ja-JP
  README mirrors updated in lockstep.
- **`README.md` Statusline prerequisites scope narrowed.** Previous text
  ("plugin hooks and advanced templates use Unix shell syntax") implied
  the entire plugin requires Bash, but plugin hooks and advanced-template
  hooks ship both `.sh` and `.ps1` ports. Updated text now scopes the
  Bash dependency to `statusline.sh` itself and explicitly notes that
  PowerShell-only Windows works for everything else. ko-KR + ja-JP
  README mirrors updated in lockstep.
- **`docs/ROADMAP.md` Audit v4 backlog item — v2.13.0 status updated
  from "(planned)" to "(released 2026-05-01)".** With both v2.12.0 and
  v2.13.0 now shipped, the bullet is marked "(COMPLETE)" with a
  parenthetical noting Audit v4 Phase 2 (Raw exposure surfaces,
  Excellence Opportunities tier) remains a future item if the
  LAV-as-multiplier formula is revisited.
- **`docs/guides/recommended-plugins-guide.md` wording broadened**
  (bumped to v1.0.1). Previous opening line ("Claude Code supports
  official plugins that extend its capabilities") understated the actual
  table contents, which mix Anthropic-maintained official plugins
  (`feature-dev`, `code-review`, `code-simplifier`, `typescript-lsp`,
  `security-guidance`, etc.) with at least one community plugin
  (`superpowers` from obra/superpowers). New line: "supports both
  official (Anthropic-maintained) and community plugins". ko-KR + ja-JP
  guide mirrors bumped to v1.0.1 in lockstep.
- **`docs/ROADMAP.md` Backlog section split into Backlog / Completed /
  Will Not Pursue.** The previous single list mixed three states —
  accepted-but-unscheduled items, a "(COMPLETE)" Audit v4 entry
  (shipped in v2.12.0 + v2.13.0), and an "explicitly NOT closed"
  diff-suggestion entry — making "remaining work" ambiguous on first
  read. Each item now lives in a dedicated section with its own
  header definition. The previously-titled "Audit Gap C decision"
  item retitled to "Automatic diff suggestions inside `/audit`",
  dropping the internal label and reusing the same trigger language.
- **`CLAUDE.md` advanced-features-guide length cap widened from
  `~200` to `~210`.** Anthropic's canonical "under 200 lines" target
  (per the official Memory documentation) applies to CLAUDE.md files,
  not to repo guides. `advanced-features-guide.md` is the longest
  guide by intent (three topics with code examples plus a Further
  Reading navigation block); at the time of writing it is 204 lines.
  The previous `~200` self-rule was 4 lines below current length; the
  new `~210` boundary keeps the conciseness spirit without forcing
  trims of useful navigation content. Explanatory parenthetical
  appended to the `CLAUDE.md` Contribution Rules bullet for clarity.
- **`docs/guides/settings-guide.md` (EN + ko-KR + ja-JP, bumped to
  v1.1.1): 1-line disclaimer added to the "Project
  (`.claude/settings.json`) — Commit this file" guidance.** New
  parenthetical clarifies that the commit guidance applies to
  **user** projects, while plugin **source** repositories
  (including this one) may gitignore their own `.claude/*` as
  dev-only. The `.gitignore:17-18` comment already declared that
  intent; the disclaimer surfaces it where the guidance itself
  lives so a contributor reading the guide alongside the ignore
  file does not see them as contradictions.
- **`README.md` (EN + ko-KR + ja-JP) two micro-tightenings from
  the `/claude-md-management:claude-md-improver` audit.**
  (1) "What's Inside" tree + directory-purpose table dual
  representation collapsed to tree-only: each tree line already
  carries an inline purpose comment, making the parallel six-row
  table redundant; the ROADMAP link previously hosted in that
  table already exists in the Contributing section, so no link
  loss. (2) `v2.11 Migration` section condensed from five
  paragraphs to three: full migration detail and parse-failure
  recovery delegated to the `CHANGELOG.md` v2.11.0 entry, which
  hosts the canonical record; stateless-mode summary and
  failure-report guidance retained inline since both remain
  user-facing for any current version. ko-KR + ja-JP mirrors
  updated in lockstep.
- **Scoring contract**: `audit-score-v4.1.0` → `audit-score-v4.2.0`. T2 weights renormalized in `plugin/references/scoring-model.md`: T2.1 0.40 → 0.35, T2.2 0.35 → 0.30, T2.3 0.25 → 0.20, T2.4 NEW 0.15 (sum 1.00 preserved). LAV/T3 Boundary Rule table gains a T2.4 ↔ L3 row to prevent double-penalty across the mechanical and LAV layers. Contract bump triggers `scoring_contract_id` banner in next `/audit` runs.
- **`/secure` Phase 1 subsection numbering**: existing 1.4 Permission Mode / 1.5 Sandbox State / 1.6 Auto Mode Trust Environment renumbered to 1.5 / 1.6 / 1.7 to accommodate the new 1.4 Autonomy Risk Policy. The autonomy-related subsection cluster (1.4-1.7) is now ordered as: actionable risk scan first (1.4), then permission/sandbox/auto-mode descriptive state (1.5-1.7). The Phase 2 cross-reference "Phase 1.4-1.6" updated to "Phase 1.5-1.7".
- **Cascade updates after contract bump** (sibling references aligned to v4.2.0):
  - 15 `ci/fixtures/audit-goldens/*/golden.json` files — `scoring_contract_id` metadata stamp only (no scoring math changes; goldens compute correctly under v4.2.0)
  - `ci/scripts/check-audit-goldens.py` canonical assertion
  - `plugin/hooks/session-start.sh` and `.ps1` `EXPECTED_SCORE` drift comparison variable
  - 5 audit reference-check docs `applies_to:` frontmatter (`distributed-config-bucket.md`, `monorepo-detection.md`, `per-package-rollup.md`, `per-package-scoring.md`, `sprint-contract.md`)
- **`/audit` output format** — Detailed Findings placeholder in `output-format.md` documents the T2.4 evidence citation pattern: `T2.4 <severity> — <sub-check>: <path:line>. Threat: <id list>. See security-patterns.md#<primary id>.`
- **Scoring formula simulation** — `ci/scripts/check-scoring-formula.py` gains a 6th sample exercising a T2.4 MINIMAL case (DS 93.7, LAV all-positive, cap-bound at 100) to verify renormalized weights produce expected outer-formula behavior.
- **`templates/advanced/sprint-contract.md` frontmatter format unified** — switched from quoted `version: "1.0.0"` to unquoted `version: 1.0.0` in the EN file plus its `docs/i18n/ko-KR/templates/advanced/` and `docs/i18n/ja-JP/templates/advanced/` mirrors, matching the unquoted-version pattern used across the other 16 frontmatter blocks in this repo.

### Removed

- **`docs/plans/` completed planning artifacts** — Removed R1-R5 round
  documents (`anthropic-engineering-insights-review*.md`),
  `decision-backlog.md`, and `false-positive-sampling-attempt.md` after
  routing-complete state (proposals routed across 13 decision rows:
  Adopt 3, Pilot 3, Defer 5, Skip 2; shipped results absorbed into prior
  CHANGELOG entries; deferred unblock conditions extracted to
  `docs/ROADMAP.md` "Revisit Triggers"). `oracle-coverage-map.md`
  relocated to `plugin/skills/audit/references/` (active dependency from
  `/audit` Phase 3.7). `docs/plans/` directory removed entirely;
  recreate when a new planning cycle resumes.

## [2.17.3] - 2026-05-08

### Fixed

- **`recommendations.json` `format: date-time` enforcement gap** — the
  `Draft202012Validator` invocation in `check-json-schemas.py`'s recommendations
  validator path did not enable `FormatChecker`, so non-ISO-8601 strings on
  `first_seen` / `last_seen` / `metadata.last_updated` passed silently. v2.17.2
  T6 surfaced this gap (the planned `recommendations.invalid-iso-date` negative
  fixture had to be dropped because it was accepted as valid). Patch now uses
  an instance-level `FormatChecker` with a stdlib-only `date-time` checker
  (`datetime.fromisoformat` after `Z` → `+00:00` swap), avoiding the
  `jsonschema[format]` extra (`rfc3339-validator`) dependency.

### Added

- **`recommendations.invalid-iso-date.example.json` negative fixture** —
  registered in `RECOMMENDATIONS_NEGATIVE_EXAMPLES`. Sets `first_seen` to
  `"05/08/2026"` (US-locale slash format, not ISO-8601). Verifies the
  FormatChecker activation rejects it. Total recommendations negative fixtures:
  8 (was 7).

### Changed

- `CLAUDE.md` L60 wording disambiguated — "All 11 must pass GREEN" became
  "All 11 Python validators must pass GREEN" with explicit 6-routine /
  5-release-only category breakdown plus a note that `lychee` is a separate
  non-Python link checker excluded from the count. Closes a wording ambiguity
  surfaced during the v2.17.2 release-prep review.
- `plugin/.claude-plugin/plugin.json`: version bumped `2.17.2` → `2.17.3`.
- `README.md`: version badge `2.17.2` → `2.17.3`.

## [2.17.2] - 2026-05-08

### Removed

- **Dead `check-sample-list-preconditions.py` CI job** — script hardcoded a path
  (`docs/superpowers/v3-roadmap/phase-2a-sample-list.md`) that never shipped
  (gitignored from inception) and is permanently unreachable after the
  v3-roadmap directory was deleted on 2026-05-07. Soft-skip path preserved CI
  green but the docs-check job was a no-op consuming a CI slot. Removes script,
  workflow job, and updates `CLAUDE.md` job count 20 → 22 (one removed, three
  added below — net +2).

### Added

- **README badge sync verifier** (`.github/scripts/check-readme-badge-sync.py`,
  CI job `readme-badge-sync`) — compares README shields.io version badge to
  `plugin/.claude-plugin/plugin.json` version. Catches the cascade-miss class
  that left v2.17.0 shipping with `2.16.0` badge until v2.17.1 caught it.
- **Annotated tag SHA propagation verifier**
  (`.github/scripts/check-tag-sha-propagation.py`, CI job
  `tag-sha-propagation`) — converts CLAUDE.md prose rule into scripted check;
  compares `git rev-parse v<tag>` (local annotated SHA) to `refs/tags/v<tag>`
  on origin (NOT `^{commit}` peeled). Soft-skip when no tag context.
- **CHANGELOG anchor slug derivation validator**
  (`.github/scripts/check-changelog-anchor-slug.py`, CI job
  `changelog-anchor-slug`) — derives GitHub-flavored slug per CLAUDE.md
  convention from each `## [X.Y.Z] - YYYY-MM-DD` heading and asserts
  well-formedness + collision-free. Tolerates trailing-annotation headings
  like `[1.0.0] - 2026-03-27 [DEPRECATED]` and emits a count-assertion safety
  net to detect silent skips.
- **profile.schema v1.2.0 type-consistency negative fixtures (4 files)** —
  `profile.monorepo-without-detection`, `profile.detection-without-monorepo`,
  `profile.detected-boolean-type-null`, `profile.detected-null-type-not-null`
  cover the 4 if/then invariants linking `project_structure.type` and
  `monorepo_detection.detected`. Closes the negative-coverage gap.
- **recommendations.schema status/minLength negative fixtures (2 files)** —
  covers `status` enum violation and `description: minLength: 1`. (Date
  format-checker fixture deferred — `Draft202012Validator` does not enforce
  `format: date-time` by default; enabling FormatChecker is minor-surface
  scope, not patch.)

### Changed

- `CLAUDE.md` Release Process: README badge sync verifier rule, scripted tag
  SHA propagation rule (replaces prose), and CHANGELOG anchor slug verifier
  rule codified.
- `CLAUDE.md`: docs-check job count 20 → 22 (one removed, three added).
- `CLAUDE.md`: release-time validator sweep updated 8 → 11 with category split
  (6 routine + 5 release-only).
- `plugin/.claude-plugin/plugin.json`: version bumped `2.17.1` → `2.17.2`.
- `README.md`: version badge `2.17.1` → `2.17.2`.

### Notes

- Audit category P7 (advanced template hooks parity audit) executed locally
  with zero shipping-relevant findings; cosmetic drift (subagent-stop bash
  manual-JSON vs ps1 ConvertTo-Json; validate-prompt ps1 dual-fire deferral)
  noted as expected and not a bug.

## [2.17.1] - 2026-05-07

### Fixed

- **Linux smoke fixtures (8/13 false-fire fix)** — non-drift sessionstart-orchestrator
  fixtures (no_signal, unresolved_only, unresolved_K_isolation,
  repeated_decline_only, legacy_v1_0_0_read, unknown_future_version,
  stale_excluded, pending_decline_count_status_guard) now ship `setup.sh` that
  pins all `input/` files to a deterministic old timestamp then bumps
  `local/profile.json` to the latest. Restores Linux 8/13 FAIL to 13/13 PASS.
  Root cause: `actions/checkout` lexicographic order on Linux ext4 leaves
  `.claude/settings.json` strictly newer than `local/profile.json`,
  false-firing legacy_mtime drift in fixtures meant to be silent.

- **`recommendations.schema.{base,v1.0.0,v1.1.0}.json` metadata closure
  regression** — wrappers previously closed only at root scope plus per-item;
  nested `metadata` was silently open and accepted `metadata.extra: "anything"`.
  `profile.schema.v1.1.0.json` precedent closes metadata via per-property
  `allOf $ref + unevaluatedProperties: false`. Patch extracts metadata into
  `recommendations.schema.base.json $defs/metadata` and applies the same
  per-property closure to v1.0.0 + v1.1.0. Adds negative fixture
  `recommendations.metadata-extra.example.json` registered in
  `check-json-schemas.py` to assert rejection. Tightening only — existing
  files lacking `metadata.extra` remain valid.

- **`session-start.ps1` date locale bug** (uncovered by new ps1 fixture lane)
  — `ConvertFrom-Json` auto-converts ISO 8601 strings to `[DateTime]` in
  PowerShell 5.1+ and 7+, and `-split "T"` then stringifies via current
  culture, producing `04/29/2026 00:00:00` on en-US instead of the
  bash-equivalent `2026-04-29`. Fixed by detecting the DateTime case and
  formatting via `InvariantCulture` `yyyy-MM-dd`. Drift and repeated-decline
  families do not display dates and were unaffected.

- **README.md version badge** — was stale at `2.16.0` after v2.17.0 release
  (cascade missed). Bumped directly to `2.17.1`.

### Added

- **PowerShell sessionstart fixture lane** — `check-smoke-fixtures.py` gains
  `_find_pwsh()` (Windows pwsh-7-then-powershell-5.1; Linux pwsh from PATH),
  `_canonical_json()`, and `run_sessionstart_ps1_fixture()` mirroring the
  bash variant. Each of the 13 sessionstart-orchestrator fixtures now runs
  through BOTH `session-start.sh` AND `session-start.ps1`; equivalence is
  checked via canonical JSON (sorted keys + compact separators) since bash
  uses jq-default pretty format and ps1 uses `ConvertTo-Json` formatting that
  differ in whitespace. Lane gracefully skipped when no PowerShell
  interpreter is available; ubuntu-latest CI ships pwsh by default. Total
  smoke runs: 4 skill-flow + 13 sessionstart-bash + 13 sessionstart-ps1 = 30.

### Changed

- `CLAUDE.md` Release Process: pre-publish smoke-status gate codified —
  the smoke workflow triggered by tag push (`push: tags: ['v*']`) MUST
  conclude `success` before `gh release create`. Polling sequence handles
  tag-trigger registration delay then blocks on
  `gh run watch <id> --exit-status`. Without this gate v2.17.0 published
  76 seconds after Linux smoke FAILED on tag SHA, leaving main RED.

- `CLAUDE.md`: cross-platform shell/fixture gotchas codified — 5 entries on
  Git Bash `/dev/stdin` absence, subprocess CRLF vs `Path.read_text()` LF
  normalization, Windows `bash` resolving to WSL (Git Bash explicit path
  preference / `_find_bash()` helper), fixture mtime not preserved by git
  checkout (setup.sh required), and jq `fromdateiso8601` Z-suffix handling.
  Also extends `Verifying Changes Locally` with file `open(encoding='utf-8')`
  note + lists 4 release-only Python validators alongside the routine 4 +
  lychee.

- `plugin/hooks/session-start.sh` source-filter comment rewritten: jq is a
  HARD dependency throughout the hook (source parsing, profile/recs JSON
  reads, final emit_digest output). The fail-open near the source filter
  only protects against a malformed stdin payload, not against jq absence.

- `CHANGELOG.md` v2.17.0 entry: gains a supersession header pointing readers
  to v2.17.1.

- `plugin/.claude-plugin/plugin.json`: version bumped `2.17.0` → `2.17.1`.

- `README.md`: version badge updated `2.16.0` → `2.17.1` (also restores the
  v2.17.0 cascade miss).

### Notes

- Linux smoke divergence pattern (`actions/checkout` lexicographic order
  leaving `.claude/settings.json` strictly newer than `local/profile.json`
  on ext4) was masked on Windows NTFS by lower-resolution mtime + different
  checkout ordering. Local Windows sanity is now formally a fast precheck;
  only Linux CI conclusion qualifies as a release gate.
- Manifest content fingerprint persisted in `profile.json` (long-term
  replacement for live mtime comparison entirely) is deferred to v2.18.0
  design.

## [2.17.0] - 2026-05-07

> **Superseded by v2.17.1** — Linux smoke 8/13 fixtures false-fired
> `legacy_mtime` drift due to `actions/checkout` mtime ordering on ext4
> (`.claude/settings.json` checked out after `local/profile.json` lexicographically).
> Recommendations schema wrappers also left nested `metadata` open contrary to
> the `profile` precedent. v2.17.1 ships fixture `setup.sh` mtime pinning,
> per-property metadata closure on both wrappers, a codified pre-publish smoke
> gate in `CLAUDE.md` Release Process, an honest jq hard-dependency note in the
> hook source, and a PowerShell fixture lane in the smoke runner.

### Added

- **SessionStart Orchestrator** — `plugin/hooks/session-start.{sh,ps1}` extended
  from a 4-case mutually-exclusive bootstrap-detection hook to a gate-then-stack
  state-aware re-entry digest. After bootstrap cases (no config / no profile)
  early-return with their existing prompts, three trigger families stack into a
  capped 2000-char multi-line digest in fixed priority order: drift (manifest
  staleness with absorbed prior stale-detection + schema version mismatch +
  ecosystem change + scoring contract bump), unresolved recommendations
  (PENDING items >= N days old or surface count >= K, default N=7 K=3), and
  repeated declines (DECLINED items with decline_count >= M, default M=3).
  Source filter limits emission to `startup` and `resume` only via `hooks.json`
  `matcher: "startup|resume"` first-line filter (script-side stdin parser
  remains as defense-in-depth); `clear` and `compact` silenced. Lock-based
  first-wins de-duplication (atomic `mkdir local/.session-start.lock` with 30s
  TTL) prevents duplicate emit on machines with both bash and PowerShell
  interpreters.

- **`recommendations.json` schema additive minor (1.0.0 -> 1.1.0)** via
  versioned-wrapper architecture — 3 new schema files
  (`recommendations.schema.base.json` open at every scope,
  `recommendations.schema.v1.0.0.json` frozen with `unevaluatedProperties: false`
  at wrapper scope, `recommendations.schema.v1.1.0.json` adds `decline_count`
  integer field with same closure). Pre-existing 1.0.0 files accepted via
  parser inflation; writes from all four state-writing skills (`/create`,
  `/audit`, `/secure`, `/optimize`) populate and increment the field.
  `check-json-schemas.py` registers the 3 new schemas + new
  `select_recommendations_wrapper(schema_version)` dispatcher mirroring
  existing `select_profile_wrapper`. `merge_rules.md` cascade adds
  `decline_count` increment-on-DECLINE-transition contract spanning all 4
  state-writing skills.

- **CI smoke lane extended** — `check-smoke-fixtures.py` adds
  `run_sessionstart_fixture` covering 13 sessionstart-orchestrator fixtures
  (no_signal / drift_legacy_mtime / drift_multi_reason / unresolved_only /
  unresolved_K_isolation / repeated_decline_only / all_three / clear_source /
  compact_source / legacy_v1_0_0_read / unknown_future_version /
  stale_excluded / pending_decline_count_status_guard) alongside existing 4
  skill-flow fixtures = 17 total CI runs. Fixtures use `SMOKE_PINNED_UTC` env
  var for deterministic now_utc; mtime-sensitive fixtures source `setup.sh`
  first to manipulate file mtimes (git checkout does not preserve mtimes).

### Changed

- `CLAUDE.md`: 3 release-flow learnings codified — Change Propagation Checklist
  gains `templates/` path-rename → CLAUDE.md `Repository Structure` cascade
  target; Release Process gains pre-publish release notes verification grep +
  branch+tag same-name `push --delete` disambiguation note.

### Notes

- Auto-mode deny counter trigger is not shipped in this release; a future
  v2.18.0 will design the PermissionDenied collector and re-evaluate the
  auto-mode territory.
- Schema migration follows the prior versioned-wrapper precedent + closure-keyword
  pattern: base schemas are open, versioned wrappers close with
  `unevaluatedProperties: false` (NOT `additionalProperties: false`, which
  evaluates within the base scope and rejects wrapper-added fields).
  Forward-only compatibility contract: new plugin supports current minor +
  N-1; downgrade and mixed-version local state are unsupported.
- Threshold calibration: N=7 days / K=3 surfaces / M=3 declines locked after
  7-scenario sanity check across all boundaries (empty / under-N-and-K /
  N-boundary / K-boundary / under-M / M-boundary / above-M); full 27-combination
  matrix deferred to a v2.17.x patch if production noise/signal feedback
  surfaces.

## [2.16.0] - 2026-05-06

### Added

- **Advanced template hook templates** — three new lifecycle observability
  hooks (PreCompact, SubagentStop, Stop) ship under
  `templates/advanced/hooks/`, each with bash + PowerShell dual-entry.
  Outputs land in `<project>/.claude/local/hooks/` (gitignored).
- **`templates/advanced/.claude/.gitignore`** — ignores `local/` directory
  (skill state + hook outputs).
- **`.github/scripts/check-hook-script-parity.py`** validator and new
  **`hook-script-parity`** CI job verify byte-equal mirroring of
  `templates/advanced/hooks/*.{sh,ps1}`, `.gitignore`, and `settings.json`
  across EN / ko-KR / ja-JP.
- **Root `.gitattributes`** entries for advanced template config assets
  (`.gitignore` and `settings.json` paths) to enforce LF line endings on
  Windows checkouts. Wildcard `*.sh` / `*.ps1` rules already covered hook
  scripts.

### Changed

- `templates/advanced/scripts/validate-prompt.{sh,ps1}` moved to
  `templates/advanced/hooks/validate-prompt.{sh,ps1}` for directory
  unification. `templates/advanced/.claude/settings.json` UserPromptSubmit
  wire path updated accordingly. Behavior unchanged. Empty `scripts/`
  directory removed in EN and both i18n mirrors.
- `docs/guides/getting-started.md` (+ ko-KR / ja-JP mirrors): validate-prompt
  path reference updated. Frontmatter version bumped `1.2.4` → `1.2.5`.
- `CLAUDE.md`: docs-check job count updated to 20 with full names listed;
  shell-script path list aligned with `validate-prompt` move
  (`templates/advanced/scripts/*.sh` → `hooks/*.sh`).
- `plugin/.claude-plugin/plugin.json`: version bumped `2.15.0` → `2.16.0`.
- `README.md`: version badge updated `2.15.0` → `2.16.0`.

### i18n

- `docs/i18n/ko-KR/templates/advanced/hooks/` and
  `docs/i18n/ja-JP/templates/advanced/hooks/` mirrored byte-equal,
  including `.gitignore` and `settings.json` under `.claude/`.

### Notes

- **SemVer rationale.** Minor (y) — adds new user-callable surface
  (active-wired hook templates in the advanced template) without breaking
  existing skill contracts. No schema changes, no breaking field shapes.
- **Boundary preserved.** Starter template, plugin SessionStart hook, skill
  bodies, `profile.json` schema, `audit-score-v4.1.0` scoring contract, and
  `recommendation-registry.json` all unchanged.

## [2.15.0] - 2026-05-05

### Added

- **qa-report.md post-audit transparency artifact** — `/audit` writes a
  new `local/qa-report.md` file after the Summary phase. Self-versioned
  (independent semver, starting `1.0.0`), sibling to existing canonical
  state files. Section list: 4 always-present sections (Score Summary /
  LAV Item Rationale / Bucket Rationale / Recommendations Linkage) + 1
  conditional section (Sprint Contract Coverage, present if and only if
  `<project-root>/sprint-contract.md` is present and contains an
  extractable `## In Scope` section).
- **LAV-time counterfactual generation** — each LAV item (L1-L6) gains a
  "Counterfactual to next band" cell describing what evidence would lift
  the score one band, framed as hypothetical observation only (never
  imperative). Generation occurs immediately after each score commits;
  scores are immutable (counterfactual analysis MUST NOT change the
  just-committed L1-L6 score). Material counterfactuals require exactly
  one piece of evidence; multi-piece deltas render as `—`.
- **Optional `<project-root>/sprint-contract.md` read** — `/audit` parses
  the user-managed `sprint-contract.md` (created by `/create` Advanced in
  v2.14.0) after audit-fact freeze, extracts `## In Scope` bullets, and
  aligns them with LAV evidence in the qa-report Sprint Contract Coverage
  table. Read is optional, read-only, non-fatal on any failure
  (frontmatter advisory / missing header / unreadable file all degrade
  gracefully).
- **CI validator `check-qa-report-shape.py`** — enforces section-list
  invariance, generator-authored forbidden-token absence, and
  imperative-mood absence in shipped golden fixtures. Wired into
  `docs-check.yml` as the 19th CI job.
- **3 qa-report.md golden snapshots** — `ci/golden/{beginner-path,monorepo,warm-start}/local/qa-report.md`
  covering absent / valid / per-package contexts. Smoke fixture verifier
  extended to byte-diff `qa-report.md` per fixture.

### Changed

- **`/audit` execution gains a new render step** between the Summary and
  Persist phases. The render emits `local/qa-report.md` from
  already-frozen audit facts only. Stateless mode and unwritable `local/`
  both fall back to terminal-output rendering (no silent skip).
- **`plugin/references/learning-system.md`** documents `qa-report.md` as
  a sibling canonical state file (frontmatter bump 2.3.4 → 2.3.5).
- **LAV scoring is unchanged.** A pre-release calibration probe (42
  cells: 7 cases × 6 LAV items, each scored under both control and
  treatment prompts) showed 0 calibration shift between the two prompts,
  so the planned LAV prompt hardening was dropped from this release.
  `audit-score-v4.1.0` stays. `profile.json` schema stays at 1.2.0 (no
  new durable state introduced).
- `plugin/.claude-plugin/plugin.json`: version bumped `2.14.0` → `2.15.0`.
- `README.md`: version badge updated `2.14.0` → `2.15.0`.

### Notes

- **SemVer rationale.** Minor (y) — adds new user-callable surface
  (`qa-report.md` artifact emitted by `/audit` + Sprint Contract Coverage
  table when `sprint-contract.md` is present) without breaking existing
  skill contracts. No schema changes, no breaking field shapes.
- **Static sprint-contract.md lifecycle preserved** — `/audit`'s read of
  `sprint-contract.md` is read-only; the file remains user-managed (per
  v2.14.0 contract). Edits to `sprint-contract.md` are still user-driven.
- **Invocation-agnostic write** — `qa-report.md` rendering follows the
  same write/terminal rule in every `/audit` invocation context
  (subagent / reviewer / direct user / hook-triggered). No
  context-specific branching.
- **Forward-compatible versioning** — `qa-report.md` frontmatter starts at
  `1.0.0`. Future additive changes to the section list or render contract
  are minor `1.x.0` bumps.
- **Change Propagation Checklist followed.** Files touched:
  `plugin/skills/audit/references/qa-report-template.md` (NEW) +
  `plugin/skills/audit/references/checks/sprint-contract.md` (NEW) +
  `plugin/skills/audit/references/checks/lav.md` (counterfactual section
  appended) + `plugin/skills/audit/SKILL.md` (new render step inserted) +
  `plugin/references/learning-system.md` (canonical state file list
  expansion + frontmatter bump) + `.github/workflows/docs-check.yml`
  (new validator job) + `.github/scripts/check-qa-report-shape.py` (NEW
  validator) + `.github/scripts/check-smoke-fixtures.py` (`qa-report.md`
  byte-diff extension) + 3 `ci/golden/*/local/qa-report.md` (NEW) + 1
  `ci/fixtures/*/sprint-contract.md` (NEW input fixture for valid-state
  path coverage) + `plugin/.claude-plugin/plugin.json` (version bump) +
  `README.md` (badge bump) + `CHANGELOG.md` (this entry).
- **Validation.** 15 validators GREEN on local pre-release sweep + 1 expected SKIP (sample-list, local-only curation artifact): `check-frontmatter-parity.py` (18 pairs), `check-i18n-parity.py` (60 files / 4 pairs), `check-json-schemas.py` (14 JSON), `check-qa-report-shape.py` (3 goldens), `check-recommendation-registry.py` (2 negative examples rejected), `check-skill-stability.py` (4 skills), `check-changelog-parser.py` (6/6), `check-scoring-formula.py` (5/5 samples), `check-scoring-model-lav-linkage.py` (4/4), `check-audit-goldens.py` (15/15 with A1-A10), `check-detection-probe.py` (56 fixtures), `check-audit-drift-aware.py` (6/6), `check-scoring-contract-consistency.py` (canonical = audit-score-v4.1.0), `preflight-schema.py` (10/10), `check-smoke-fixtures.py` (4/4 with `SMOKE_PINNED_UTC` pinning).

## [2.14.0] - 2026-05-03

### Added

- **Sprint Contract artifact** — `/create` Advanced path now generates a
  `sprint-contract.md` file at the project root, capturing the user's
  scope commitments for the current work cycle. Schema: YAML frontmatter
  (`title`, `description`, `version`) + boundary sentence + `## In Scope`
  section (flat bullets, bold noun phrase + clarifying sentence) +
  `## Deferred` section (each item with `Reason: ...`). Independent semver
  starting `1.0.0`.
- **Phase 2B negotiation step** in `/create` Advanced path — two
  conversational questions (In Scope / Deferred) inserted between Phase 2A
  questions and Phase 3A generation. Empty user responses fall back to
  explicit placeholders (`- Initial setup — to be defined` /
  `- None recorded during initial setup`). Zero-options principle
  preserved (no flags, no `$ARGUMENTS`).
- **Phase 2A-Incremental gap detection** — existing-project re-run now
  scans for `sprint-contract.md` presence and offers it as missing-item
  option (g) when absent.
- **i18n templates** — `sprint-contract.md` template added in EN
  (`templates/advanced/`) plus ko-KR and ja-JP mirrors under
  `docs/i18n/<lang>/templates/advanced/`.

### Changed

- `plugin/skills/create/templates/advanced.md`: new Phase 2B inserted
  between Phase 2A and Phase 3A; Phase 3A "Always generate" gains
  `sprint-contract.md` write step (Advanced path only); Phase 2A-Incremental
  scan list and missing-items checklist updated to include
  `sprint-contract.md`.
- `plugin/.claude-plugin/plugin.json`: version bumped `2.13.1` → `2.14.0`.
- `README.md`: version badge updated `2.13.1` → `2.14.0`.

### Notes

- **SemVer rationale.** Minor (y) — adds new user-callable surface (`/create` Advanced Phase 2B negotiation step + `sprint-contract.md` artifact + Phase 2A-Incremental gap detection of the new file) without breaking existing skill contracts. Starter path is zero-impact; existing Advanced workflows gain two new conversational questions and one new generated file. No schema changes, no breaking field shapes.
- **Static lifecycle** — `sprint-contract.md` is user-managed after
  creation. `/audit`, `/secure`, and `/optimize` do NOT interact with the
  file. User edits manually if scope evolves.
- **Starter zero-impact** — Starter path generates no `sprint-contract.md`.
  Verified via existing `beginner-path` smoke fixture (negative assertion
  implicit — Starter fixture's expected output does not include
  `sprint-contract.md`).
- **No new CI surface** — `sprint-contract.md` is markdown free-form content
  (no JSON schema). Existing validators absorb the new files automatically:
  `check-frontmatter-parity.py` + `check-i18n-parity.py` enforce the
  EN/ko-KR/ja-JP parity invariants on the trio, `check-skill-stability.py`
  covers the `advanced.md` Phase 2B edits, `check-json-schemas.py` validates
  the `plugin.json` version bump, and `check-changelog-parser.py` validates
  this entry. No new validator script added.
- **Idempotency** — re-running `/create` Advanced on a project with existing
  `sprint-contract.md` preserves the file (skips negotiation, emits 1-line
  terminal notice).
- **profile.json schema unchanged** — `sprint-contract.md` presence is NOT
  tracked in `profile.json` (standalone artifact, no skill state-machine
  coupling). Future `/audit`-based features that want to read scope content
  will use filesystem-direct access.
- **Forward-compatible versioning** — `sprint-contract.md` frontmatter starts
  at `1.0.0`. Future additive changes (e.g., parse anchors for downstream
  feature integration) are minor `1.x.0` bumps.
- **Change Propagation Checklist followed.** Files touched: `templates/advanced/sprint-contract.md` (NEW EN template) + `docs/i18n/ko-KR/templates/advanced/sprint-contract.md` (NEW KR mirror) + `docs/i18n/ja-JP/templates/advanced/sprint-contract.md` (NEW JP mirror) + `plugin/skills/create/templates/advanced.md` (Phase 2B insertion + Phase 3A always-generate entry + Phase 2A-Incremental gap-detection updates) + `plugin/.claude-plugin/plugin.json` (version bump) + `README.md` (badge bump) + `CHANGELOG.md` (this entry). Frontmatter parity (3-trio) + i18n parity validators auto-applied per CLAUDE.md change-propagation rule.
- **Validation.** 13 validators GREEN on local pre-release sweep + 1 expected SKIP (sample-list, local-only curation artifact): `check-frontmatter-parity.py` (18 pairs), `check-i18n-parity.py` (60 files / 4 pairs), `check-json-schemas.py` (14 JSON), `check-skill-stability.py` (4 skills), `check-changelog-parser.py` (6/6), `check-scoring-formula.py` (5/5 samples), `check-scoring-model-lav-linkage.py` (4/4), `check-audit-goldens.py` (15/15 with A1-A10), `check-detection-probe.py` (56 fixtures), `check-audit-drift-aware.py` (6/6), `check-scoring-contract-consistency.py` (canonical = audit-score-v4.1.0), `preflight-schema.py` (10/10), `check-smoke-fixtures.py` (4/4 with `SMOKE_PINNED_UTC` pinning). Manual conversational scenarios verified via code-path inspection: `advanced.md` Phase 2B existence-check guard + Phase 3A `sprint-contract.md` write step (covers Advanced first-run, re-run idempotency, empty-response placeholder fallback, and ko-KR / ja-JP locale variants) + Starter zero-impact via `templates/starter.md` grep showing 0 sprint-contract references + atomic-write primitive at `plugin/references/lib/state_io.md` unchanged in v2.14.0 (graceful-abort path preserved for write-failure scenarios).

## [2.13.1] - 2026-05-02

### Added

- **6 synthetic monorepo audit-goldens fixtures** covering 6 ecosystems with the `synthetic/` slug prefix and `source_type=synthetic` labeling (excluded from empirical OSS denominators per scoring-model semantics):
  - `synthetic-rust-cargo-workspace` (Rust): `Cargo.toml [workspace] members` declares 3 sub-crates, 2 with sub-CLAUDE.md
  - `synthetic-go-work-monorepo` (Go): `go.work` declares 2 sub-modules, 0 with sub-CLAUDE.md (low-adoption baseline)
  - `synthetic-gradle-composite` (Java/Gradle): `settings.gradle.kts` mixes `includeBuild('build-logic')` with multi-project `include(':app', ':lib')` — first audit-goldens fixture exercising the `composite_build` evidence type
  - `synthetic-python-uv-workspace` (Python): `pyproject.toml [tool.uv.workspace] members` declares 5 sub-packages, 3 with sub-CLAUDE.md (diverse final_scores 80/65/45 demonstrating per-package variance)
  - `synthetic-dotnet-sln-4non-id` (.NET): `Solution.sln` declares 4 csproj sub-projects, all 4 with sub-CLAUDE.md (pairwise distinct final_scores 90/75/60/40 — non-identical even-count distribution exercising the per-package-rollup median-of-evens path)
  - `synthetic-tied-worst-rollup-k4` (Rust): `Cargo.toml [workspace] members` declares 4 sub-crates, all 4 with sub-CLAUDE.md tied at final_score 60.0 — exercises the `(and K-N more tied)` rollup display path per `per-package-rollup.md` §2.3 with K=4, N=3
  - `nrwl/nx` Node baseline retained from v2.13.0

- **Detection probe fixture infrastructure** — 56 fixtures across 14 ecosystems organized into three tiers under `ci/fixtures/detection-probe/` (Tier A 29 fixtures across Node + Rust + Go + Python + Maven + Gradle + dual-role-manifest scenarios; Tier B 14 fixtures across .NET + Elixir + Swift + Ruby; Tier C 13 fixtures across C/C++ + Dart + Erlang + Haskell). Each fixture exercises `monorepo-detection.md` parsing rules with positive / negative / edge-case scenarios. New validator `ci/scripts/check-detection-probe.py` wired into CI as 18th job validating fixture schema invariants.

- **`distributed_config` bucket rubric** in `plugin/skills/audit/references/checks/distributed-config-bucket.md` (NEW shipped, ~81 lines). Required conditions (`with_claude_md >= 2` + `project_structure.type == "monorepo"` + `monorepo_detection.detected == true`), 4 supporting signals with `>=2` threshold (distributed config ratio `>= 0.5`, root CLAUDE.md compactness `<= 150` lines, mean L6 actionability ratio `>= 0.5` over scored subpackages, verbose-prose-sparse-config exclusion), exclusion conditions (excessive root `> 1000` lines, all scored subpackages `final_score < 30`), and advisory numeric guardrails (`with_claude_md ∈ [3, 20]`, `distributed_config_ratio ∈ [0.5, 1.0]`). Captures monorepos that distribute Claude Code configuration across sub-package CLAUDE.md files rather than centralizing in root.

### Changed

- **`classify_bucket()` extension** in `ci/scripts/check-audit-goldens.py`. New `classify_bucket_full(data: dict) -> str` orchestrator wraps existing `classify_bucket(profile: dict) -> str` (signature preserved, backward compatible). Evaluation order: Outlier short-circuits + verbose-prose-sparse-config Outlier → `distributed_config` (NEW, applied via `classify_bucket_distributed(data: dict) -> bool`) → Advanced/Intermediate/Starter. `VALID_BUCKETS` set extended with `"distributed_config"`. `validate_golden()` now calls `classify_bucket_full(data)` so the A6 bucket-rubric assertion covers all paths.

- **3 audit-goldens fixtures reclassified** to `distributed_config` per the new rubric. Each fixture's `expected_bucket` and `bucket_rationale` updated:
  - `synthetic-rust-cargo-workspace`: Intermediate → distributed_config (4/4 supporting signals — ratio 0.67, compactness 120 lines, mean L6 0.5, verbose-prose-sparse-config exclusion holds)
  - `synthetic-python-uv-workspace`: Intermediate → distributed_config (4/4 supporting signals — ratio 0.6, compactness 140 lines, mean L6 0.67, verbose-prose-sparse-config exclusion holds)
  - `synthetic-dotnet-sln-4non-id`: Advanced → distributed_config (3/4 supporting signals — ratio 1.0, mean L6 0.75, verbose-prose-sparse-config exclusion holds; root compactness signal fails at 180 > 150)

- `plugin/references/scoring-model.md` frontmatter `1.0.2` → `1.0.3` — cross-references to `per-package-scoring.md` and `per-package-rollup.md` added adjacent to the Scoring Formula section (downstream skill navigation aid). Edits shipped within the v2.13.0 brand but not captured in that release's CHANGELOG entry; recorded here for documentation completeness.

- `plugin/skills/audit/references/checks/monorepo-detection.md` §3 sub-step Phase A.5 renamed to Phase B.5 — its position in the algorithm body is between Phase B (heuristic signals) and Phase C (4-layer filter); the prior "A.5" naming implied an A-adjacent position and was inconsistent with the algorithm code order. The 5-phase A/B/C/D/E structure is preserved with B.5 as the disclosure-walk sub-step. Documentation clarity only — algorithm behavior unchanged. The v2.13.0 release note's phase-sequence shorthand reads correctly under the new naming as `workspace declaration → heuristic → disclosure walk inclusion → 4-layer filter → cap`.

- `plugin/skills/audit/references/checks/monorepo-detection.md` frontmatter `version` field unquoted (`"1.0.0"` → `1.0.0`) for stylistic alignment with sibling reference docs (`per-package-rollup.md`, `per-package-scoring.md`). YAML parse-equivalent — no semantic change.

### Notes

- **SemVer rationale.** Patch (z) — adds new fixtures, new shipped rubric doc, and validator extension via wrapper pattern that preserves existing function signatures (backward compatible). No new user-callable skill surface, no breaking schema changes, no migration required for existing users. Per CLAUDE.md release process: patch covers fixes and platform-compat work; this release also covers test-surface expansion and validator additivity which fits the patch envelope (no contract change).

- **Validation set scope.** Empirical measurement of 10 OSS monorepo candidates was conducted, with 6 accepted and 4 rejected per detection criteria. The "popular OSS monorepo + root CLAUDE.md" intersection was found near-empty in 2026 (`nrwl/nx` is the lone real-OSS exemplar across the candidate set + existing audit-goldens). All 6 new fixtures in v2.13.1 are labeled synthetic, excluded from empirical OSS denominators per scoring-model semantics. The synthetic fixture set provides three distinct cardinality coverage areas: ≥2 fixtures with `scored_count >= 3` (synthetic-python-uv 3 + synthetic-dotnet 4 + synthetic-tied 4), ≥1 fixture with even-count `scored_count` of 4 with non-identical middle values (synthetic-dotnet 90/75/60/40), and ≥1 fixture K≥4 worst-tie (synthetic-tied uniform 60/60/60/60).

- **Bucket distribution.** Post-v2.13.1 audit-goldens count is 15 fixtures across 5 buckets — Outlier×6 (5 baseline + synthetic-tied-worst-rollup-k4), Intermediate×3 (2 baseline + synthetic-gradle-composite), Starter×3 (2 baseline + synthetic-go-work-monorepo), distributed_config×3 (synthetic-rust-cargo-workspace + synthetic-python-uv-workspace + synthetic-dotnet-sln-4non-id), Advanced×0 (no fixtures meet the Advanced rubric thresholds — empirical OSS reality preserved).

- **Validation.** 13 validators GREEN on local pre-release sweep: `check-frontmatter-parity.py`, `check-i18n-parity.py`, `check-json-schemas.py`, `check-audit-goldens.py` (15/15 with A1-A10), `check-detection-probe.py` (56 fixtures schema-valid), `check-audit-drift-aware.py`, `check-scoring-contract-consistency.py` (canonical = `audit-score-v4.1.0`), `check-scoring-formula.py`, `check-scoring-model-lav-linkage.py`, `check-changelog-parser.py`, `check-sample-list-preconditions.py`, `preflight-schema.py` (10 assertions), `check-smoke-fixtures.py` (4 fixtures GREEN with `SMOKE_PINNED_UTC` pinning).

- `plugin/.claude-plugin/plugin.json`: version bumped `2.13.0` → `2.13.1`.
- `README.md`: version badge updated `2.13.0` → `2.13.1`.

### Per-fixture score matrix

| Fixture | Bucket (v2.13.1) | Baseline (v2.13.0) | v2.13.1 | Delta | New | Reason |
|---|---|---|---|---|---|---|
| exa-networks-exabgp | Outlier | 22.68 | 22.68 | 0.0 | no | Bucket and score unchanged |
| guardians-of-the-claude | Outlier | 60.112 | 60.112 | 0.0 | no | Self-reference, bucket and score unchanged |
| nrwl-nx | Outlier | 46.84 | 46.84 | 0.0 | no | Verbose-prose-sparse-config Outlier path takes precedence over distributed_config check (lines 226 + zero mechanical config) |
| rilldata-rill | Intermediate | 26.168 | 26.168 | 0.0 | no | Bucket and score unchanged |
| stacksjs-ts-collect | Starter | 4.16 | 4.16 | 0.0 | no | Bucket and score unchanged |
| the-cafe-git-ai-commit | Starter | 9.152 | 9.152 | 0.0 | no | Bucket and score unchanged |
| ubolonton-emacs-module-rs | Intermediate | 27.536 | 27.536 | 0.0 | no | Bucket and score unchanged |
| vercel-next-js | Outlier | 25.6 | 25.6 | 0.0 | no | Bucket and score unchanged |
| wesm-moneyflow | Outlier | 48.38 | 48.38 | 0.0 | no | Bucket and score unchanged |
| synthetic-go-work-monorepo | Starter | new | 12.0 | new | yes | Synthetic Go workspace fixture; with_claude_md=0 fails distributed_config required condition (>=2) |
| synthetic-gradle-composite | Intermediate | new | 43.6 | new | yes | Synthetic Gradle composite-build fixture; with_claude_md=1 fails distributed_config required condition (>=2) |
| synthetic-rust-cargo-workspace | distributed_config | new | 38.4 | new | yes | Synthetic Rust cargo workspace fixture; reclassified from Intermediate (4/4 supporting signals) |
| synthetic-python-uv-workspace | distributed_config | new | 50.6 | new | yes | Synthetic Python uv workspace fixture; reclassified from Intermediate (4/4 supporting signals) |
| synthetic-dotnet-sln-4non-id | distributed_config | new | 63.6 | new | yes | Synthetic .NET solution fixture; reclassified from Advanced (3/4 supporting signals; root compactness fails at 180 > 150) |
| synthetic-tied-worst-rollup-k4 | Outlier | new | 45.2 | new | yes | Synthetic Rust cargo workspace K=4 worst-tie fixture; verbose-prose-sparse-config Outlier path (lines=220 + zero mechanical config) precedes distributed_config check |

## [2.13.0] - 2026-05-01

### Added

- **Per-package `CLAUDE.md` scoring with rollup output for monorepos.** `/audit` now scores each subpackage `CLAUDE.md` independently using the same LAV/scoring formula and emits a Subpackage Score Rollup section in the audit output (min/median/worst across LAV components + counts of scored / disclosure-only / total subpackages). Subpackages without `CLAUDE.md` contribute to coverage metrics (`scored_count`, `disclosure_only_count`) but no score row. Cap policy: display=20 / scored=50 — projects above the scored cap have remaining subpackages reported as visible unscored counts. Phase 3.6 Per-Package Scoring runs after the root LAV computation; structure is treated as a facet contributing to scoring inputs, not a sole-criterion bucket override. New reference docs: `plugin/skills/audit/references/checks/per-package-scoring.md` (per-package LAV + Score Boost + cap + Final + degraded modes) and `plugin/skills/audit/references/checks/per-package-rollup.md` (rollup format + scored_count=0 fixture handling).

- **Deterministic monorepo detection** codified in `plugin/skills/audit/references/checks/monorepo-detection.md` (217 lines). Workspace-declaration parsing across 14 ecosystems, 7 directory heuristic patterns with High/Medium/Low confidence semantics, a 5-phase algorithm (workspace declaration → disclosure walk inclusion → heuristic → 4-layer filter → cap), a 5-type evidence schema (`workspace_declaration` / `heuristic_signal` / `convention` / `composite_build` / `parse_error`), and cap policy. Detection is deterministic — no LLM-runtime heuristic, no deep manifest parsing beyond declared globs, no cross-ecosystem inference.

- **`profile.json` schema 1.2.0 (additive)** with two new field families:
  - `project_structure.monorepo_detection { detected, evidence[], package_roots[], package_roots_for_scoring[], package_root_caps, notes[] }` — replaces the v2.10-era fixture-only `is_monorepo` boolean with structured detection output.
  - `claude_code_configuration_state.claude_md.subpackages[]` — array of `{ path, exists, section_count }` per disclosed subpackage. `/audit` is the sole writer; full-list replace under one Final Phase lock (no per-row partial merge — per-package scores have no historical-trend semantic in this version).
  - Cross-field type consistency: schema rejects `type:single_project + monorepo_detection.detected:true`; `type:monorepo` requires `detected:true`; `null` only with absent/null detection.

- **`/create` `monorepo_detection` write-precondition decision table** in `plugin/skills/create/SKILL.md`. Documents the merge-rule boundary: `/create` does not author `monorepo_detection` (no write path); `/audit` is the sole writer. Surfaces this contract to future contributors before they add a write path.

- **Outlier rubric — verbose-prose-sparse-config path.** `classify_bucket()` in `ci/scripts/check-audit-goldens.py` now classifies `CLAUDE.md` files with rich prose but minimal mechanical configuration (rules / hooks / agents / MCP all near-zero) as Outlier. Captures real-world projects where the maintainer documented intent extensively but never wired up Claude Code automation surfaces.

- **`audit-goldens` validator monorepo invariants.**
  - **A8** `monorepo_detection` shape: `detected` boolean + `evidence[]` non-empty disjoint with `package_roots_for_scoring[]` non-empty when `detected:true`.
  - **A9** `subpackage_coverage` consistency: `scored_count + disclosure_only_count + unscored_count == total_count`.
  - **A10** per-row subpackage invariants: `section_count >= 0`, `exists` boolean, `path` non-empty string.
  Conditional on fixture shape — A8/A9/A10 only run when `monorepo_detection.detected:true` to avoid false positives on single-project fixtures.

- **`nrwl/nx` audit-goldens fixture** — first native monorepo with sub-`CLAUDE.md` adoption (`pnpm-workspace.yaml` + `packages/devkit/CLAUDE.md` 62 lines + `packages/nx/src/native/CLAUDE.md` 51 lines). Validates the per-package scoring path with real-world workspace metadata; brings the audit-goldens count to 9 fixtures.

- **`CLAUDE.md` "Verifying Changes Locally"** gains the `SMOKE_PINNED_UTC` env var pin example for `check-smoke-fixtures.py` (matches the value used in `.github/workflows/smoke.yml`). Local validation now reproduces the CI smoke-lane byte-diff verification deterministically.

### Changed

- **Scoring contract bumped** `audit-score-v4.0.0` → `audit-score-v4.1.0`, triggered by the monorepo audit reporting semantics change below. Source-of-truth `plugin/references/scoring-model.md` frontmatter updated; 8 audit-goldens + 8 generated profile.json fixtures regenerated to match; 5 hand-authored t6-* fixtures normalized to current contract with `seen_count: 2` (silent steady — isolates banner trigger from drift/silence test scope). Banner trigger fires on next audit run for users on the previous contract — expected behavior. `scoring-model.md` frontmatter version 1.0.1 → 1.0.2.

- **"Monorepo => Outlier" sole short-circuit retired.** Structure now contributes to scoring inputs (subpackage rollup, coverage metrics) instead of forcing the Outlier bucket as a sole criterion. Existing fixtures previously gated by `is_monorepo:true` re-classify via the `claude_md_lines > 250` Outlier path with the same bucket result (validated against `vercel/next-js` — bucket unchanged, score delta = 0). Removes the contract-declaration vs implementation mismatch that the v4.1.0 bump exposed.

- **`/audit` `SKILL.md` — Phase 1.5 expansion + Phase 3.6 hook + always-regenerate list extended.** Phase 1.5 Subpackage Discovery now consumes the manifest list defined in `monorepo-detection.md` (workspace-declaration files across 14 ecosystems + 7 heuristic patterns) instead of a hard-coded subset. Phase 3.6 Per-Package Scoring is invoked after root LAV computation. Always-regenerate list extended to include `subpackages[]` and `monorepo_detection`. **Per-package findings are transient by default** — score rows (`subpackages[]`) and coverage counters (`subpackage_coverage`) persist per `merge_rules.md` `/audit` ownership; advisory-style observations surfaced for individual subpackages render to terminal output only and MUST NOT be added to `recommendations.json`. Statistical aggregates (`min`, `median`, `worst`) are computed-on-render per `per-package-rollup.md` §4. Persistence semantics for per-package recommendations are deferred to a later minor.

- **`output-format.md` Subpackage Score Rollup conditional rendering.** Section renders only when `subpackages[]` non-empty; rollup `total_count` invariant matches `subpackages[].length`. Canonical "Subpackage" heading style applied consistently across `per-package-scoring.md` and `per-package-rollup.md`. New **"Polyglot Example (Mixed Ecosystems)"** subsection demonstrates that the rollup format is ecosystem-agnostic — paths follow each ecosystem's native convention (`crates/<name>` Rust, `packages/<name>` Node, `python/<name>` Python, `services/<name>` heuristic-gated), while the LAV multiplier, cap tiers, and per-row table format render identically across ecosystems.

- **`plugin/references/lib/merge_rules.md`** gains the `/audit`-only ownership entry for `monorepo_detection` + `claude_md.subpackages` + `claude_md.subpackage_coverage` and a `project_structure` consistency precondition. Frontmatter version 1.2.1 → 1.3.0.

- **`plugin/references/learning-system.md`** adds cross-references for `per-package-scoring.md` and `per-package-rollup.md` so downstream skill implementations have a single navigation anchor.

- **JSON Schema architecture extended to `base + v1.0.0 + v1.1.0 + v1.2.0` wrappers.** `profile.schema.base.json` extended with `monorepo_detection` + `subpackages[]` field shapes; `profile.schema.v1.2.0.json` is the new sibling wrapper selecting `unevaluatedProperties: false` at every nested level (continues the v2.12.0 base+wrapper pattern). Dispatchers in `.github/scripts/check-json-schemas.py` and `.github/scripts/check-smoke-fixtures.py` route by `schema_version` literal. `ci/scripts/preflight-schema.py` extended to **10 assertions** covering v1.2.0 closure-coverage gates and cross-field type-consistency rejection.

- **Smoke runner per-skill target-version rule.** `.github/scripts/check-smoke-fixtures.py` now allows different skills within a fixture to emit different `schema_version` values (e.g., `/audit` emits v1.2.0 with `monorepo_detection`; `/secure` and `/optimize` continue at v1.2.0 without authoring those fields per the `/audit`-only ownership rule). Replaces the previous fixture-wide single-version assumption.

- **`audit-goldens` 8 existing fixtures migrated to schema 1.2.0.** Each fixture declares `monorepo_detection` (with `detected:false` + empty evidence/roots arrays for single-project fixtures). Vestigial `is_monorepo` boolean removed from all 8 fixtures.

- **Smoke goldens migrated to schema 1.2.0** across 4 canonical fixtures (`migration` / `beginner-path` / `warm-start` / `monorepo`). State-summary cascade: smoke runner's `Source: profile.json v{schema_version}` inline interpolation propagates the new schema_version into all 4 `state-summary.md` goldens. Same migration applied to 5 t6-* fixtures and 3 t7-* fixtures (8 profile.json + 7 state-summary.md cascade).

### Removed

- **Vestigial `is_monorepo` field** removed from `REQUIRED_PROFILE_KEYS` in `ci/scripts/check-audit-goldens.py` (was a fixture-only flag, never declared in the JSON schema).
- **`is_monorepo` boolean field** removed from the 8 pre-existing audit-goldens fixtures. Replaced by structured `monorepo_detection`.

### Migration

- **`profile.json` schema auto-upgrade on first writable `/audit` run.** v2.11.x / v2.12.x `local/profile.json` with `schema_version: "1.1.0"` is upgraded to `schema_version: "1.2.0"` on the first writable `/audit` invocation after upgrade. Existing fields are preserved; new fields populated automatically:
  - `project_structure.monorepo_detection` from manifest scan + heuristic detection per `monorepo-detection.md`.
  - `claude_code_configuration_state.claude_md.subpackages[]` from disclosure walk (per-subpackage `path` + `exists` + `section_count`).

  Additive-only — no breaking changes to existing field shapes. No manual action required.

- **Single-project users are unaffected.** Schema declares both new field families as optional with empty defaults; existing single-project workflows render `detected:false` / empty `subpackages[]` and continue unchanged.

- **`audit-score-v4.1.0` contract banner.** Users on `audit-score-v4.0.0` (v2.12.x) see the scoring-contract-change banner on their next two `/audit` runs (per the v2.12.0 two-write acknowledgement protocol). Persistence-backed; skipped in stateless mode.

### Fixed

- **Shipped surface boundary cleanup** (3 files): `plugin/references/lib/state_io.md` and `plugin/references/lib/merge_rules.md` (line 9 each) had a redundant authoritative-source pointer to a maintainer-local document not present in the published tree. The pointer is removed; frontmatter description already provides self-contained intent. `docs/ROADMAP.md` lines 53-54 (Audit v4 forward-plan section) rewritten with version-centric phrasing in place of internal workstream labels — public roadmap now reads correctly without referring to maintainer-internal organizational vocabulary. Frontmatter versions bumped: `state_io.md` 1.0.0 → 1.0.1, `merge_rules.md` 1.2.0 → 1.2.1 (content modification per file-version semver).

### Notes

- **SemVer rationale.** Minor (y) — adds new user-callable surface (per-package scoring + monorepo detection + Subpackage Score Rollup output section + new reference docs + new schema version 1.2.0) without breaking existing skill contracts. Schema 1.2.0 is additive-only.

- **Validation set scope.** v2.13.0 ships per-package scoring with **1 native monorepo sample (`nrwl/nx`)** as initial coverage. Empirical reality: major popular OSS frameworks have effectively 0 sub-`CLAUDE.md` adoption today, so single-sample is acceptable for v2.13.0's initial validation goal. Wider validation (25-40 monorepo candidates across ≥5 ecosystems) is scheduled for v2.13.1.

- **Validation.** 13 validators GREEN on local pre-release sweep: `check-frontmatter-parity.py`, `check-i18n-parity.py`, `check-json-schemas.py`, `check-audit-goldens.py` (9/9 with A1-A10), `check-audit-drift-aware.py`, `check-scoring-contract-consistency.py` (canonical = `audit-score-v4.1.0`), `check-scoring-formula.py`, `check-scoring-model-lav-linkage.py`, `check-changelog-parser.py`, `check-sample-list-preconditions.py`, `preflight-schema.py` (10 assertions), `check-smoke-fixtures.py` (4 fixtures GREEN with `SMOKE_PINNED_UTC` pinning), and `lychee` link check.

- **`plugin/.claude-plugin/plugin.json`:** version bumped `2.12.3` → `2.13.0`.
- **`README.md`:** version badge updated `2.12.3` → `2.13.0`.

- **Change Propagation Checklist followed:** `plugin.json`, `README.md` badge, `CHANGELOG.md`. Fix scopes touched: `plugin/skills/audit/` (SKILL.md + references/checks/* + references/output-format.md), `plugin/skills/create/SKILL.md`, `plugin/references/` (scoring-model.md + learning-system.md + lib/merge_rules.md + lib/state_io.md + schemas/*), `ci/scripts/check-audit-goldens.py`, `.github/scripts/check-smoke-fixtures.py`, `ci/scripts/preflight-schema.py`, `ci/fixtures/audit-goldens/**` (8 migrated + 1 new), `ci/fixtures/migration|beginner-path|warm-start|monorepo/**` (4 smoke fixtures), `ci/fixtures/t6-*/**` + `ci/fixtures/t7-*/**` (8 fixtures). No `security-patterns.md`, no shell-script surface, no i18n mirror updates required (changes are plugin-only — single source).

## [2.12.3] - 2026-04-26

### Changed

- **Internal design labels removed across remaining shipped artifacts** (~115 hits across 29 files): `plugin/references/` (learning-system + model-drift-rules + output-format), 4 SKILL.md (`/audit`, `/create`, `/secure`, `/optimize`), 6 CI validators, `.github/workflows/docs-check.yml` job names + warnings, and 14 JSON fixtures under `ci/fixtures/scoring-model-simulation/`, `ci/fixtures/audit-goldens/`, and `ci/fixtures/t3-model-drift/`. References to gitignored maintainer-internal documents (`DEC-N` decision IDs, `phase-2a-*.md` paths, `Phase 2a` task identifiers, `§N` design section anchors) replaced with named-concept descriptions or removed where trace-only. The shipped surface now reads correctly in isolation.
- **`Model Bullet Emission` shared section** added to `plugin/references/learning-system.md`. The 4 SKILL.md Row 3 instruction blocks now point to a single source-of-truth, eliminating cross-file drift risk for the changelog `- Model:` writer policy.
- **Validator realignments** (no behavior change): `ci/scripts/check-audit-drift-aware.py` A4 substring updated to match post-cleanup SKILL.md wording (`"Final Phase model write"`); `.github/workflows/docs-check.yml` 7 job names + 4 warning strings rewritten as semantic descriptions naming the missing artifact directly.
- **JSON fixture metadata generalized**: `sample-*.json` `design_authority`, `golden.json` `bucket_rationale`, and `test-cases.json` `notes` fields now describe behavior in self-contained language (`per the bucket rubric`, `per the monorepo short-circuit rule`, `per the model-drift rules`). Validator assertions unchanged — `check-audit-goldens.py` 8/8, `check-scoring-formula.py` 5/5, `t3_model_drift_check.py` 16/16 PASS confirm semantic equivalence.

## [2.12.2] - 2026-04-25

### Changed

- **`plugin/references/scoring-model.md` internal design labels removed.** Frontmatter description, `## Formula` section heading, formula commentary note, count-source footnote, and the L5 row in the LAV Axis Summary table each carried references to gitignored maintainer-only documents (`DEC-N` decision IDs, a `phase-2a-contracts.md` path, and a `T7(C2) commit \`4499893\`` provenance pin). The cleanup leaves the spec reading correctly in isolation. The scoring formula and `scoring_contract_id` (`audit-score-v4.0.0`) are unchanged. Frontmatter version bumped `1.0.0` → `1.0.1`.
- **`ci/scripts/check-scoring-model-lav-linkage.py` realigned to the post-cleanup spec.** A3 (count-source footnote) previously pinned the substring `T7(C2) commit \`4499893\``, which would have made the validator verify its own internal-ref violation. `COUNT_SOURCE_SUBSTRINGS` is now a 3-element tuple of durable shipped facts (profile count field name, skill co-ownership clause, `merge_rules.md` path); the assertion fails only when one of these structural elements is missing. A4 (`DS_SB_CAP_HASH`) recomputed for the post-edit `## Formula` block. Residual internal task labels (`T2b`, `D2`) removed from comments, docstrings, and the final PASS log line.

## [2.12.1] - 2026-04-24

### Added

- **`check-scoring-contract-consistency.py` CI validator (17th job in `docs-check.yml`).** Cross-checks `plugin/references/scoring-model.md` frontmatter `scoring_contract_id` against all `ci/fixtures/audit-goldens/*/golden.json` entries and the install-integrity prose in `plugin/skills/audit/SKILL.md`. Adds Python-level validation for scoring-contract identifier consistency across the three canonical sites — build-time validators already covered value correctness; this extends coverage to the identifier-agreement dimension.

### Changed

- **Smoke-fixture runner supports `profile.json` schema v1.1.0** via wrapper dispatch (`profile.schema.v1.0.0.json` vs `profile.schema.v1.1.0.json` selected by declared `schema_version`). `merge_profile` bumps output `schema_version` to `1.1.0` and propagates `model` + `scoring_model_ack` from `/audit` delta. `handle_audit` / `handle_secure` / `handle_optimize` emit the `- Model:` changelog bullet per the hybrid writer policy (`/audit` always; other skills emit only when the resolved model differs from the immediately previous entry).
- **`plugin/references/learning-system.md` changelog entry template bumped to v1.1.0** with a new first-position `- Model:` bullet in the entry format. Describes the hybrid writer policy inline for downstream skill implementations.
- **Drift-aware test fixtures use canonical axis enums.** `ci/scripts/check-audit-drift-aware.py` A1_FIXTURES migrated from non-canonical labels (`opus_tier`, `200k_class`, `thinking`, `standard`) to the canonical 4-axis enums defined in `plugin/references/model-drift-rules.md` (`opus|sonnet|haiku / 200k|1M / none|extended_any / manual|compaction_capable`). `drift_state` compares fingerprints structurally, so the migration is semantically equivalent — all drift-aware assertions continue to pass.

### Fixed

- **`merge_profile` `/audit` branch now propagates `model` + `scoring_model_ack`.** Previously `_audit_detect_profile` emitted these fields in the profile delta but the merge step dropped them, causing byte diff in first-run fixtures and `KeyError` on changelog entry assembly in fixtures with prior state lacking `model`. `/audit` is the authoritative writer for both fields; merge now propagates them explicitly.
- **Expected `profile.json` `scoring_model_ack` format realigned from single-line to multi-line.** `_object_is_inline` expands 2+field objects whose values include a string; the hand-authored single-line shape violated this invariant, causing byte diff after the merge-propagation fix surfaced it.
- **`ci/scripts/preflight-schema.py` forces UTF-8 I/O.** Reconfigures `sys.stdout` / `sys.stderr` to UTF-8 on startup so the validator doesn't raise `UnicodeEncodeError` when non-ASCII appears in schema paths or error messages on Korean-locale (cp949) hosts. Silent fallback on older Python or non-standard streams.
- **Schema description fields are now self-contained.** `plugin/references/schemas/recommendations.schema.json` and `plugin/references/schemas/recommendation-registry.schema.json` description strings no longer reference internal design documents that aren't accessible from the repo; descriptions read correctly in isolation.

## [2.12.0] - 2026-04-23

### Added

- **`state-summary.md` drift advisory header + `/audit` terminal drift block.** When the resolved Claude model ID differs from the baseline `/audit` entry's model (baseline derived via reverse-chronological scan of `config-changelog.md` — Recent Activity entries first, then Compacted History buckets with first-anchor-wins), the generated `state-summary.md` injects a one-line header `Model drift: <baseline_model_id> -> <current_model_id>` immediately after the `# Claude Code Configuration State` H1, before `## Project Profile`. `/audit` additionally renders an axis-wise terminal drift block from the same derivation. Silent on non-drift states (`match`, `missing_baseline`, `normalization_null`). All four skills (`/audit`, `/create`, `/secure`, `/optimize`) share the renderer path. The single shared derivation lives in a new `plugin/references/learning-system.md § Drift Advisory Derivation` subsection (4-branch silence evaluation order + A2 transience + stateless + cross-skill invariance clauses). Advisory is transient — never persists to `recommendations.json`. CI smoke fixtures under `ci/fixtures/t6-*` cover drift render, normalization-null silence, cross-skill sink, and stateless render skip.
- **`config-changelog.md` hybrid `- Model:` writer with Lossless Anchors.** Entry format at v1.1.0 adds a `- Model: <resolved model id>` bullet as the first entry line. `/audit` always writes the bullet; `/create`, `/secure`, and `/optimize` write it only when the resolved model differs from the immediately previous entry's bullet value (delta-omit on unchanged). Legacy v1.0.0 entries parse with `bullet_model: null` and are treated as delta-omit for baseline derivation. Compaction Algorithm Step 3b emits a structured per-skill anchor in each Compacted History bucket so drift baselines survive history compaction.
- **`/audit` scoring-contract-change banner with two-write acknowledgement.** When `scoring-model.md` frontmatter `scoring_contract_id` advances (e.g., `audit-score-v3.x.x` → `audit-score-v4.0.0`), `/audit` surfaces a short banner on the first two writable runs, tracked via `profile.claude_code_configuration_state.scoring_model_ack.seen_count` (0 → 1 → 2). Persistence-backed; skipped in stateless mode.

### Changed

- **`/audit` scoring now uses the conservative LAV item-aware multiplier.** `Final = min(DS × (1 + LAV_nonL5 / 50) + SB, cap)`, with `LAV_nonL5 = L1 + L2 + L3 + L4 + L6` and cap tiers `{50, 60, 100}` driven by the L5 conciseness result (`cap = 60` if `L5 == -3` with no other `Li` at its minimum; `cap = 50` if `L5 == -3` with at least one other `Li` at its minimum; `cap = 100` otherwise). Replaces the v2.10.0 Foundation-Gated Multiplicative formula. Scoring-contract-id bumped to `audit-score-v4.0.0` in `plugin/references/scoring-model.md` frontmatter with a runtime install-integrity assertion (mismatch = broken-install error). 5-sample simulation goldens under `ci/fixtures/scoring-model-simulation/`; 8 real-project goldens under `ci/fixtures/audit-goldens/` validated by `ci/scripts/check-audit-goldens.py` A1-A7 (includes self-quality-gate check).
- **Stateless `/audit` runs skip the persistence-backed scoring-contract banner but retain the transient drift advisory.** Persistence-backed surfaces (scoring-model-change banner + `scoring_model_ack` write) are suppressed when `local/` is unwritable; current-state-derived surfaces (drift advisory + Score Breakdown) continue to render.
- **`plugin/skills/audit/SKILL.md` drift advisory block trimmed to terminal-sink-specific.** Previously carried the full derivation inline. Derivation now lives in shared `learning-system.md § Drift Advisory Derivation`; the block here contains only the `/audit` terminal render trigger + pointer to the shared reader-side derivation + transience clause + stateless terminal-retain clause.
- **JSON Schema architecture factored into `base + v1.0.0 + v1.1.0` wrappers.** `plugin/references/schemas/profile.schema.base.json` holds the structural skeleton without closure; `profile.schema.v1.0.0.json` and `profile.schema.v1.1.0.json` are sibling wrappers selecting `unevaluatedProperties: false` at every nested level. Dispatcher in `.github/scripts/check-json-schemas.py` loads the wrapper by `schema_version` literal. 4-assertion preflight probe at `ci/scripts/preflight-schema.py` gates schema commits in CI.
- **New CI validators wired into `docs-check.yml`.** 7 new jobs: `preflight-schema`, `scoring-formula-simulation`, `scoring-model-lav-linkage`, `changelog-parser-check`, `sample-list-preconditions`, `audit-goldens-check`, `audit-drift-aware-check`. Totals: 16 jobs in `docs-check.yml` + 2 jobs in `smoke.yml` (`smoke` fixture runner + `verifier-drift-tripwire`).
- **GitHub Releases — all 27 versions (v1.0.0 through v2.11.2) compacted to the Option A "Highlights + CHANGELOG link" pattern.** Each release body is now ~500–1200 bytes (down from up to 12163 bytes for v2.10.0, median ~700), showing a `## Highlights` section with 3–5 short pointer bullets plus a `**Full details:**` link to the matching CHANGELOG section. Per-release reduction: 50–94%. Releases that already had human-curated `## Highlights` blocks (v2.11.x, v2.10.x, v2.9.0, v2.6.0, v2.5.0) preserved those blocks verbatim. Older releases synthesized bullets from CHANGELOG via first-sentence extraction with priority Added → Fixed → Changed (trivial version-bump Changed entries filtered out). v1.0.0 (pre-CHANGELOG era) manually curated. CHANGELOG.md itself unchanged — it remains the source of truth for full rationale, validation notes, and SemVer reasoning. Motivation: prior "copy CHANGELOG verbatim" bodies created heavy redundancy between the Releases page and CHANGELOG.md on the same repo.
- `CLAUDE.md` Release Process L60: rewrote the `**Body:**` rule from "copy CHANGELOG verbatim + optional Highlights" to "`## Highlights` + `**Full details:**` CHANGELOG link". Added the anchor URL slug convention (drop `[ ] .`, spaces → hyphens, lowercase) so future releases follow the compact pattern by default.

### Migration

- **`profile.json` schema auto-upgrade on first writable `/audit` run.** v2.11.x `local/profile.json` with `schema_version: "1.0.0"` is upgraded to `schema_version: "1.1.0"` on the first writable `/audit` invocation after upgrade. Existing fields are preserved; `claude_code_configuration_state.model` (resolved Claude model ID, string) and `claude_code_configuration_state.scoring_model_ack` (object with `version` + `seen_count` fields) are added automatically. Additive-only — no breaking changes to existing field shapes. No manual action required.
- **`config-changelog.md` version 1.1.0 hybrid writer behavior.** New changelog entries are written with frontmatter `version: 1.1.0`. `/audit` always writes a `- Model:` bullet as the first entry line; `/create`, `/secure`, and `/optimize` write it only when the resolved model changes vs the immediately previous entry. Existing v1.0.0 changelog entries remain readable (parsed as `bullet_model: null`) and do not need manual migration.
- **Stateless mode — unwritable `local/`.** When `local/` cannot be written, the transient drift advisory still renders in the `/audit` terminal from an in-memory changelog snapshot. On-disk schema upgrade (profile.json + config-changelog.md) is deferred until a later writable `/audit` run; persistence-backed surfaces (scoring-contract banner + `scoring_model_ack` tracking) are suppressed entirely.

### Fixed

- **`plugin/references/learning-system.md` L398–L399 render-sequence wording.** Previously said "immediately after writing the two JSON files" which contradicted the authoritative `§ Common Final Phase Step 1 substep 4` ("render from in-memory `new_profile` / `new_recommendations` / `new_changelog` before atomic write"). Substep 5 includes `state-summary.md` in the atomic write batch; rendering is pre-write, not post-write, to avoid TOCTOU against the same Step 1's writes. Updated the `§ State Rendering` Invocation clause to cite substep 4 and explain the pre-write rationale.
- `CLAUDE.md` line 20 (Repository Structure): stale CI job count corrected — `.github/workflows/docs-check.yml` now has **9 jobs** (not 7), adding `registry-lint` and `skill-stability-lint` which were introduced in v2.11.0 but never propagated into CLAUDE.md's structure description. Also added a new bullet pointing to `.github/workflows/smoke.yml` (CI smoke lane with 2 jobs: `smoke` fixtures runner and `verifier-drift-tripwire`), which was added in v2.11.0 but not mentioned in the Repository Structure section at all. Detected by post-v2.11.2 full-repo audit; no functional impact, but stale structure description reduces Claude's accuracy when suggesting CI-related changes.
- `.github/workflows/smoke.yml`: bumped `actions/checkout@v4` → `actions/checkout@v6` and `actions/setup-python@v5` → `actions/setup-python@v6` to match the major versions already used in `docs-check.yml`. Both major versions are current and functional, but divergent action versions across two workflows in the same repo increases maintenance surface and Node runtime variance — keeping them synchronized is low-cost hygiene. No behavior change.
- `docs/i18n/ko-KR/README.md` line 199 and `docs/i18n/ja-JP/README.md` line 199 (Statusline section example): model label `Opus 4.6` → `Opus 4.7`. EN `README.md` line 207 was already updated to `Opus 4.7`; both i18n mirrors carried the stale 4.6 label. Pure drift-to-parity fix — no frontmatter version bump (README has no frontmatter, and per `MEMORY.md` i18n-bump semantics parity-restoration is not a semantic change warranting a bump).

## [2.11.2] - 2026-04-22

### Fixed

- `docs/i18n/ko-KR/README.md` line 20 (Philosophy section, "Progressive depth" bullet): "해제됩니다" corrected to "활성화됩니다" to remove the semantic inversion risk. Stand-alone "해제" in Korean tech prose leans toward "dismiss / cancel / disable" rather than "unlock"; the EN source ("Day 100 unlocks cross-skill memory and automated drift detection") describes feature *enablement*, and the ja-JP mirror already uses "有効化されます" (activated). Aligns ko-KR wording with both EN intent and ja-JP phrasing.
- `docs/i18n/ja-JP/README.md`: trilingual language switcher (`English / 한국어 / 日本語`) added between the intro paragraphs and the `## フィロソフィー` heading, mirroring the placement in `docs/i18n/ko-KR/README.md`. The ja-JP page previously had no in-document navigation back to the EN or ko-KR variants, forcing users to edit the URL to switch languages. Current language marked in `<b>` tags matching the EN and ko-KR patterns.
- `README.md` lines 156 and 168 describing the `docs/i18n/ja-JP/` directory: corrected both entries to match the actual inventory and to match the `docs/i18n/ko-KR/` entry style. Line 156 previously said "README, guides, partial templates" and line 168 said "guides; templates deferred" — both inaccurate (ja-JP ships the full template tree: `starter/CLAUDE.md`, `advanced/CLAUDE.md`, and all `.claude/` subfiles — see 2.11.1 UTF-8 restoration work) and self-contradicting. Both lines now read "Japanese translations (guides, templates)".
- `ci/README.md` lines 4-5 and 29-30: replaced direct references to the gitignored `docs/superpowers/v3-roadmap/phase-0-design.md` path with an explicit "maintainer-local" label and a pointer to GitHub Issues / Discussions for contributors who need the underlying rationale. Public cloners previously saw a file-path reference that does not exist in the published tree; contributors reading the CI README now understand the source is internal and have an actionable fallback.
- `plugin/hooks/session-start.sh` line 2 and `plugin/hooks/session-start.ps1` line 16: **SessionStart probe path updated from legacy `project-profile.md` to v2.11 canonical `profile.json`.** All four skills' Final Phase writes `profile.json` (and never `project-profile.md`, which Step 0.5 quarantines to `legacy-backup/`), so the hooks' existence check (`[ ! -f "$PROFILE" ]` / `Test-Path`) always failed after v2.11 migration. Net effect: every v2.11+ user saw the misleading Case 2 message "Claude Code configuration exists but no project profile has been generated yet" on every session even after a successful `/create` run. The Case 3 staleness comparison against manifest mtimes was broken by the same stale path. Hook messages themselves are unchanged — only the probe target was wrong.
- `plugin/skills/create/SKILL.md` line 26 (Phase 0.5 Determine Path): "**If project-profile.md was loaded in Phase 0:**" branch rewritten against `profile.json` using the schema-accurate field names from `plugin/references/schemas/profile.schema.json` (`project_structure`, `claude_code_configuration_state` with `claude_md` / `settings_json` sub-objects). The previous branch was unreachable in v2.11+ because Step 0.5 quarantines `project-profile.md` before any skill logic runs, so the Incremental-path auto-routing optimization that skipped the redundant "existing vs new" question never fired after migration.
- Feature documentation drift — `README.md` line 98, `docs/i18n/ko-KR/README.md` line 90, `docs/i18n/ja-JP/README.md` line 90 (Day 100+ Project Profile bullet), and `docs/guides/directory-structure-guide.md` line 67 + its two i18n mirrors (Plugin Cache example): v2.10-era filenames `project-profile.md` and `latest-{skill}.md` replaced with v2.11 canonical `profile.json`, `recommendations.json`, and the derived `state-summary.md`. The v2.11 Migration sections elsewhere in the same files still reference the legacy names intentionally (they describe the v2.10 → v2.11 conversion path). `directory-structure-guide.md` bumped `1.2.1` → `1.2.2` on EN + ko-KR + ja-JP (content update, not parity-restoration drift fix, so version bump warranted per `MEMORY.md` i18n-bump semantics).

### Changed

- `plugin/.claude-plugin/plugin.json`: version bumped `2.11.1` → `2.11.2`.
- `README.md`: version badge updated `2.11.1` → `2.11.2`.

### Notes

- **SemVer rationale.** Patch — no user-callable surface, no new frontmatter fields, no scoring-model math, no schema changes. The session-start hook fix restores intended probe behavior (`profile.json` instead of legacy `project-profile.md`); hook contract, output messages, and exit codes are unchanged. Patch-level per `CLAUDE.md` Release Process ("patch (z) for fixes and platform-compat work").
- **User-visible behavior change.** v2.11+ users whose `local/profile.json` exists will stop seeing the misleading "no project profile has been generated yet" message on every session start. The Case 3 staleness comparison against manifest mtimes also becomes functional again. v2.10.x users mid-migration (no `profile.json` yet, still have legacy `project-profile.md`) continue to see Case 2, which prompts `/audit` — and `/audit` runs Step 0.5 migration on first invocation, restoring correct hook behavior from the next session onward.
- **Change Propagation Checklist followed:** `plugin.json`, `README.md` badge, `CHANGELOG.md`. Fix scopes touched: `plugin/hooks/` (first post-v2.11 update of this subtree — previously last touched in commit `3640c59` pre-v2.11), `plugin/skills/create/SKILL.md`, `README.md` + ko-KR + ja-JP mirrors (Day 100+ bullet), `docs/guides/directory-structure-guide.md` + ko-KR + ja-JP mirrors (Plugin Cache example). No `security-patterns.md`, no scoring model, no JSON schemas, no skill contract surface.
- **Validation.** Local CI-equivalent scripts passed — `check-frontmatter-parity.py` (18 guide pairs), `check-i18n-parity.py` (58 files across 4 pairs), `check-json-schemas.py` (14 JSON files), `check-skill-stability.py` (4 skills), `check-recommendation-registry.py` (positive + 2 negative examples).
- **Root-cause prevention candidate.** The v2.11.0 migration updated `learning-system.md`, four skill SKILL.md files, and JSON schemas, but missed `plugin/hooks/session-start.{sh,ps1}` — the hooks consume the same state files but were not listed as downstream in the Change Propagation Checklist. Adding `plugin/hooks/` as a downstream target whenever `learning-system.md` or skill Final Phase contracts change is a candidate addition to the `CLAUDE.md` checklist for a future patch.

## [2.11.1] - 2026-04-22

### Fixed

- `docs/i18n/ja-JP/templates/advanced/CLAUDE.md`: **restored 74 U+FFFD replacement characters across 20 lines.** The file contained valid UTF-8 byte sequences (`EF BF BD`) that rendered as the U+FFFD glyph (the standard Unicode "unknown character" placeholder), breaking 18 Japanese sentences. The literal glyph is intentionally NOT embedded in this changelog entry to keep the file clean for the encoding-check CI job. Root cause was likely an earlier edit pass that saved the file while replacement characters were visible in the editor, committing them as file content. Reconstruction used `docs/i18n/ja-JP/templates/starter/CLAUDE.md` as byte-exact source for the shared prefix/convention text; the advanced-only line 68 zenkaku closing paren `）` was inferred from the line's parenthetical structure. Verification: full-repo U+FFFD scan = 0 hits post-fix.
- `docs/i18n/ja-JP/templates/README.md` line 3: "架空" kanji restored (3 U+FFFD chars where the file previously read `架___のプロジェクト`). Same class of corruption as the advanced/CLAUDE.md case.
- `CLAUDE.md` line 11 and `plugin/skills/create/templates/starter.md` line 3: **`5-section` → `6-section`** propagation gap corrected. The spec at `plugin/skills/create/templates/starter.md` line 69 explicitly generates "`CLAUDE.md` with 6 sections", the actual filled example `templates/starter/CLAUDE.md` frontmatter describes itself as "Minimal 6-section example", and the user-facing guide `docs/guides/getting-started.md` line 59 promises "the six canonical sections". Only these two files still said "5-section"; the other 5 references in the repo already agreed on 6. `ci/fixtures/migration/**/project-profile.md` and `ci/golden/migration/**/project-profile.md` intentionally retain "5 sections" since those fixtures represent pre-migration legacy state being migrated away from.
- `docs/i18n/ko-KR/guides/recommended-plugins-guide.md` line 17: restored missing content in the code-review plugin description. EN source reads "Multi-agent PR review with confidence scoring to filter false positives. Catches real issues, skips noise"; ko-KR had only "멀티 에이전트 PR 리뷰. 신뢰도 기반 스코어링으로 오탐 필터링" (the second clause dropped). Restored via 의역 to "멀티 에이전트 PR 리뷰. 신뢰도 기반 스코어링으로 노이즈를 걸러내고 실제 이슈만 포착" — preserves the EN catches/skips rhythm while matching the nominalized-ending style of other rows in the same table (e.g., `code-simplifier`: "기존 동작은 그대로 유지").

### Changed

- `docs/i18n/ko-KR/guides/effective-usage-guide.md` line 98: anti-pattern heading "주방 싱크대 세션" (literal 直訳 of "Kitchen Sink Session") localized to "잡다한 세션" (의역). Aligns with ja-JP's existing 意訳 approach (`何でも放り込んだセッション`, established in 2.9.7). The slightly evaluative tone of "잡다한" is intentional for an anti-pattern section — heading signal matches section purpose. Body content unchanged.
- `plugin/.claude-plugin/plugin.json`: version bumped `2.11.0` → `2.11.1`.
- `README.md`: version badge updated `2.11.0` → `2.11.1`.

### Notes

- **No frontmatter `version:` bumps on the four affected i18n guides/templates** — all fixes restore parity with the EN source rather than introducing new content. CI `check-frontmatter-parity.py` and `check-i18n-parity.py` still report 18 guide pairs OK + 58 files across 4 pairs bidirectional parity.
- **SemVer rationale.** Pure documentation and i18n correction. No skill behavior changes, no new user-callable surface, no new frontmatter fields, no scoring-model math changes. Patch-level per the `CLAUDE.md` Release Process policy ("patch (z) for fixes and platform-compat work").
- **UTF-8 corruption detection gap.** The `check-frontmatter-parity.py` and `check-i18n-parity.py` scripts pass on files with U+FFFD replacement characters stored as valid UTF-8 bytes — they check file count and version field parity, not byte-level content integrity. A lightweight scanner (e.g. `grep -l $'\xef\xbf\xbd'` or a Python `text.count(chr(0xFFFD))` walker) would catch this class of corruption; addition to CI is a candidate for a future patch (not in this release per minimum-scope principle).
- **Audit methodology that surfaced these issues.** A four-phase cross-file audit (programmatic sweeps for versions/cross-refs/command IDs/heading parity → parallel Explore subagents comparing EN against ko-KR and ja-JP → verification pass filtering LLM false positives → wave-based fixes) surfaced 6 verified issues out of 8 raw agent claims (3 of the 8 were hallucinated line numbers or misread diffs; discarded after direct file verification). The methodology is reproducible and worth re-running before future releases if translation drift is suspected.
- **Change Propagation Checklist followed:** `plugin.json`, `README.md` badge, `CHANGELOG.md` entry. Fix scopes touched: `docs/i18n/ja-JP/templates/**` (2 files), `docs/i18n/ko-KR/guides/**` (2 files), `CLAUDE.md`, `plugin/skills/create/templates/starter.md`. No `security-patterns.md`, no scoring model, no JSON schemas, no shell-script surface touched.
- **Validation.** Local CI-equivalent scripts passed — `check-frontmatter-parity.py` (18 guide pairs OK), `check-i18n-parity.py` (58 files across 4 pairs OK), `check-json-schemas.py` (14 JSON files OK). Full-repo U+FFFD scan = 0 hits post-fix.

## [2.11.0] - 2026-04-16

### Added

- JSON state schemas at `plugin/references/schemas/` (draft 2020-12): `profile.schema.json`, `recommendations.schema.json`. Each pins its version via `"schema_version": { "const": "1.0.0" }` for explicit version dispatch. `$id` is intentionally omitted (URL identifiers are mutable — repo rename / branch drift risk).
- Recommendation registry at `plugin/references/recommendation-registry.json` + `plugin/references/schemas/recommendation-registry.schema.json`. Single source for recommendation keys, authorized issuers, resolvers, and aliases. 7 initial entries cover current `/audit` recommendations; each lists the legacy `audit-*` id as an alias for migration compatibility.
- Shared validation library at `.github/scripts/lib/recommendation_registry.py` consumed by both `.github/scripts/check-recommendation-registry.py` (CLI lint) and `.github/scripts/check-smoke-fixtures.py` (smoke verifier) — single source for alias/key/issuer/resolver rules.
- Shared **State Rendering** spec in `plugin/references/learning-system.md` producing read-only `local/state-summary.md` via atomic write (temp file + rename). Stale-vs-tampered semantics: summary older than any source = stale (regenerate); newer than all sources = tampered (warn, do not use as source).
- **`Step 0.5 Migration & Stale Check`** (8-phase clean version) in Common Phase 0. Acquires state-mutation lock (`local/.state.lock`, 60s stale auto-release), classifies canonical files (5-axis state machine), validates per file, recovers from legacy with alias resolution, quarantines ALL examined legacy inputs to `local/legacy-backup/<ISO-8601-UTC>/` (single-source cutover), and regenerates or warns on `state-summary.md` before releasing the lock.
- **Per-Skill Merge Rules** section in `learning-system.md`: `profile.json` section ownership, `recommendations.json` by-key merge (preserve untouched), `config-changelog.md` whole-file read-modify-write (no `O_APPEND`).
- **Final Phase 6-step concurrency-aware sequence** in 4 skills (`/create`, `/audit`, `/secure`, `/optimize`): acquire lock → re-read current state → merge this skill's deltas → render summary from in-memory post-merge state → atomic-write all 4 files → release lock.
- **Schema Evolution Policy** + **Recommendation ID Registry** + **Migration Notice** sections in `learning-system.md`.
- Shared primitives at `plugin/references/lib/state_io.md` (atomic write + state-mutation lock + deterministic I/O) and `plugin/references/lib/merge_rules.md` (per-skill merge rules + bootstrap exception).
- CI smoke lane at `ci/fixtures/` + `ci/golden/` with 4 canonical fixtures (`migration` / `beginner-path` / `warm-start` / `monorepo`) and Python reference verifier at `.github/scripts/check-smoke-fixtures.py`. Verifier uses functional dispatch + `FIXTURE_SCENARIOS` manifest, runs actual simulation for every fixture (not just expected==golden diff), and asserts 5 semantic invariants (schema valid, registry lint, aliases never persist, legacy quarantined, summary derived from current sources) before byte diff.
- `.github/workflows/smoke.yml` with two jobs: `smoke` (runs verifier with `SMOKE_PINNED_UTC` for deterministic timestamps) and `verifier-drift-tripwire` (catches PRs that change skill markdown without updating the verifier or fixtures — requires `no-verifier-impact` PR label to bypass).
- `.github/workflows/docs-check.yml` gains a `registry-lint` job running `check-recommendation-registry.py` on fixtures + negative examples.
- `ci/scripts/run-smoke.{sh,ps1}` + `ci/scripts/compare-golden.{sh,ps1}` + `ci/scripts/build-manifest.{sh,ps1}` (cross-platform). `build-manifest` generates `eval-manifest.json` for releases (`maintainer_signoff` and `parser_robustness` fields filled post-hoc).
- `.gitattributes` enforcing LF newlines under `ci/fixtures/**` + `ci/golden/**` for cross-platform byte equality.
- `.github/scripts/check-skill-stability.py` enforcing the skill interface stability contract (frontmatter must not declare `options:`/`arguments:`; body must not embed `$ARGUMENTS`); wired as `skill-stability-lint` job in `.github/workflows/docs-check.yml`.

### Changed

- Four skills (`/create`, `/audit`, `/secure`, `/optimize`) write `profile.json` + `recommendations.json` in Final Phase Step 1 using the new 6-step sequence above. Legacy `latest-*.md` format retired.
- `config-changelog.md` remains MD canonical (unchanged structure) but writes are now whole-file read-modify-write (atomic temp+rename) to support same-day entry updates without `O_APPEND` reliance.
- Recommendation `id` model: stable kebab-case key (no skill prefix) + separate `issued_by` field. Cross-skill resolution via canonical key is natural; legacy `audit-*` prefixed ids are accepted on input via registry aliases but never persisted forward (Lint 3 enforces this).
- `plugin/references/learning-system.md` cumulative bump from `1.x` to `2.2.0` (5 new sections — State Rendering, Schema Evolution Policy, Recommendation ID Registry, Per-Skill Merge Rules, Migration Notice — plus bootstrap exception clarification across two follow-up bumps).
- `plugin/.claude-plugin/plugin.json`: version bumped `2.10.1` → `2.11.0`.
- `README.md`: version badge updated `2.10.1` → `2.11.0`; new `v2.11 Migration` and `CI smoke lane (transitional bridge)` sections inserted after Day 100+.

### Migration

- Existing v2.10.x users: on first invocation of any skill, legacy MD files under `local/` are parsed into JSON (with alias resolution for recommendation ids) and moved to `local/legacy-backup/<ISO-8601-UTC>/`. A one-time notice is printed.
- Partial recovery: if `profile.json` is corrupt but `recommendations.json` is valid, only the corrupt file is moved to backup; the valid file is preserved (Step 0.5 phase 4 per-file recovery).
- Single-source cutover: once JSON canonical exists, any lingering legacy MD is quarantined to `legacy-backup/`; legacy MD never coexists with valid JSON in `local/`.
- If parsing fails, failing files are preserved under `legacy-backup/`; skill continues with empty state (deny-and-continue). PENDING counts and DECLINED history are NOT auto-restored — see README `v2.11 Migration` section for manual restoration.
- `state-summary.md` replaces separate `project-profile.md` + `latest-*.md` files as the read-only human-readable view. Derived from current JSON + `config-changelog.md` on every skill run.
- **Forward-only migration:** once canonical JSON exists in `local/`, there is no automated path back to MD-primary state. Rollback requires manual restoration from `local/legacy-backup/<ISO-8601-UTC>/` and pinning v2.10.x.
- **Unwritable `local/` handling:** when `local/` cannot be read, Step 0.5 prints a one-time warning (`local/ not writable`) and skips state load. Full Final Phase persistence-bypass (skipping all JSON writes when `local/` is unwritable) is declared in the Step 0.5 contract but is NOT yet implemented in v2.11.0; privacy-sensitive projects that require zero state writes should pin v2.10.x until a future minor.

### Notes

- CI smoke lane is currently a **transitional bridge** to wider evaluation. Until v3.0 ships or a second maintainer joins (whichever comes first), the lane validates 4 canonical fixtures only. Wider evaluation runs maintainer-local in gitignored `test/` (14 parser robustness cases via `LOCAL_FIXTURES_DIR` env var).
- Concurrency fixtures are out of Phase 1 scope; manual testing for multi-shell concurrent skill runs is recommended. Supported scope: multi-shell same-user on same machine (state-mutation lock covers it). Unsupported: multi-user shared `local/`.
- 4 skills are hardcoded in registry schema enums (`["audit", "create", "secure", "optimize"]`). Adding a 5th skill is a breaking change requiring schema enum updates + per-skill merge rules + new schema-version dispatcher route.
- **No telemetry collected.** Migration failure modes surface via user-visible warning + preserved `legacy-backup/`. Maintainers track recurring patterns in internal notes for Phase 2a fixes.
- Versioned-dispatcher behavioral contract (per Schema Evolution Policy in `learning-system.md`) is declared in this release; first actual implementation arrives in Phase 2a (v2.12.0) when `profile.json.claude_code_configuration_state.model` is added as additive minor (1.0.0 → 1.1.0).

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
