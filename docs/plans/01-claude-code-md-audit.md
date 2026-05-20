# Plan 01 — Claude Code System Prompt Audit vs Our 12 Guides

**Status:** **complete** (started 2026-05-20, finished 2026-05-20)
**Effort:** ~1 day (actual: 1 session)
**Dependencies:** none — foundational

**Source disclaimer (added 2026-05-20 post-Codex round-3 review):** Line references throughout this audit (e.g., `claude-code.md:255`) point to a local snapshot of an external community-extracted repository (`asgeirtj/system_prompts_leaks`) that was cloned for one-time analysis. Line numbers are time-snapshotted as of 2026-05-20 and are NOT durable cross-repo references. For authoritative behavior references in future cycles, consult Anthropic's public release-notes (`https://platform.claude.com/docs/en/release-notes/system-prompts`); the leak repo is not a durable dependency of this project. The audit's *findings* (gap matrix, top gaps, conclusions) are paraphrased original guidance, not reproductions of protected source text.

## Goal
Read `../system_prompts_leaks/Anthropic/claude-code.md` (58.4KB) in full. Audit each guide under `docs/guides/` against it. Output a gap/alignment table.

## Why foundational
Our project teaches "how to configure Claude Code." `claude-code.md` is the actual product behavior spec our users' configurations interact with. Drift between our guides and this spec = users build inaccurate mental models.

## Scope

### In scope
- **Read fully:** `../system_prompts_leaks/Anthropic/claude-code.md`
- **Audit all 12 guides:**
  1. claude-md-guide.md
  2. rules-guide.md
  3. settings-guide.md
  4. directory-structure-guide.md
  5. getting-started.md
  6. effective-usage-guide.md
  7. advanced-features-guide.md
  8. mcp-guide.md
  9. recommended-plugins-guide.md
  10. trustworthy-agents-guide.md
  11. multi-agent-patterns-guide.md
  12. workflow-patterns-guide.md
- For each (claude-code.md topic × guide), mark: **Aligned** / **Complements** / **Diverges** / **Missing** / **N/A**
- Identify top 5 high-confidence gaps with proposed fix path

### Out of scope
- claude.ai-human-readable.md (244KB) — different product (claude.ai), separate plan if needed
- Other vendor system prompts
- Actually editing guides (audit-only; fixes belong to Plan 04)
- ko-KR / ja-JP mirrors — audit is on EN canonical

## Method
1. Read claude-code.md sections 1–end → extract topic index
2. For each guide: read → mark coverage per topic → record line refs for divergences
3. Aggregate into matrix
4. Score gaps by `impact × confidence`; pick top 5
5. Append findings to this file as `## Findings`

## Deliverables
- `## Topic Index` (from claude-code.md sections)
- `## Gap Matrix` (12 guides × N topics)
- `## Top 5 Gaps` with: file path, line ref, claude-code.md citation, proposed fix sketch
- **No file modifications outside `docs/plans/`**

## Success criteria
- Every guide has ≥1 verified data point
- Top 5 gaps each have: target file path, claude-code.md citation, fix sketch
- All citations include line numbers (`claude-code.md:LLL`)

## Risks
- `claude-code.md` captures version `2.1.143` (line 1). Current may differ → flag version-sensitive findings.
- "Aligned" can be a false-negative for newer versions — outside this audit's scope, note as caveat.
- License/ToS: no verbatim copy of `claude-code.md` text into shipped guides. Comparison reference only.

## Verification before completion
- For each "Diverges" entry: grep the guide line to confirm citation accuracy
- For each "Missing" entry: grep all 12 guides + `plugin/skills/*/SKILL.md` for that topic
- Top 5 list re-sorted by post-verification confidence

---

## Findings

_Last update: 2026-05-20 — **audit pass 2 COMPLETE** (12/12 guides + 4 skills)_

**Version-drift caveat:** `claude-code.md` reflects Claude Code v2.1.143 + Sonnet 4.6 (line 1, line 247). Current Claude Code on this session runs Opus 4.7. Findings flagged with `[VD]` may be version-sensitive.

### Audit Progress

| Guide / Skill | Read | Audited |
|---|---|---|
| claude-md-guide.md | yes | yes |
| rules-guide.md | yes | yes |
| getting-started.md | yes | yes |
| effective-usage-guide.md | yes | yes |
| advanced-features-guide.md | yes | yes |
| trustworthy-agents-guide.md | yes | yes |
| settings-guide.md | yes | yes |
| directory-structure-guide.md | yes | yes |
| mcp-guide.md | yes | yes |
| recommended-plugins-guide.md | yes | yes |
| multi-agent-patterns-guide.md | yes | yes |
| workflow-patterns-guide.md | yes | yes |
| plugin/skills/create/SKILL.md | yes | yes |
| plugin/skills/audit/SKILL.md | yes | yes |
| plugin/skills/secure/SKILL.md | yes | yes |
| plugin/skills/optimize/SKILL.md | yes | yes |

### Topic Index (claude-code.md, lines 1-950)

| ID | Topic | Ref |
|---|---|---|
| T1 | Identity, versioning, model identity, knowledge cutoff | `:1`, `:247-251` |
| T2 | Harness contract (output as markdown, permission modes, `<system-reminder>` semantics, hook output, tool preferences, file_path:line refs, parallel independent calls) | `:67-73` |
| T3 | Text output rules (pre-call announcement, status updates, no internal narration, complete sentences for cold readers, end-of-turn 1-2 sentence summary, code comments default off, no planning docs unless asked) | `:74-86` |
| T4 | Session-specific guidance (subagent dispatch doctrine, Explore for >3 query exploration, Skill invocation discipline) | `:87-91` |
| T5 | Auto memory system (4 types user/feedback/project/reference, save process 2-step + MEMORY.md index, exclusion list, "Before recommending" verification doctrine, memory vs plans vs tasks) | `:92-238` |
| T6 | Environment block (cwd, platform/OS/shell, model identity, knowledge cutoff, access modes CLI/desktop/web/IDE, Fast mode behavior) | `:240-256` |
| T7 | Length limits (≤25 words between tool calls, ≤100 words final unless detail required) | `:255` |
| T8 | Tools inventory + per-tool semantics (Agent variants, Bash, Edit, Glob, Grep, Read, ScheduleWakeup, Skill, ToolSearch, Write) | `:257-950` |
| T9 | Git commit protocol within Bash tool (6-point safety protocol, HEREDOC requirement, Co-Authored-By trailer with Claude Sonnet 4.6 noreply, 4-step process) | `:442-494` |
| T10 | PR creation protocol (gh CLI, 4-parallel branch-state check, PR template Summary + Test plan, 🤖 footer, title <70 chars) | `:496-531` |
| T11 | Built-in skills inventory (update-config, keybindings-help, simplify, less-permission-prompts, loop, schedule, claude-api, init, review, security-review) | User Message system-reminder |
| T12 | Deferred tools mechanism + ToolSearch schema-fetching pattern | User Message system-reminder |

### Gap Matrix (12/12 guides)

Legend: **A**=Aligned, **C**=Complements, **D**=Diverges (intentional or accidental), **M**=Missing, **·**=Not applicable

| Guide | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | T10 | T11 | T12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude-md-guide | · | C | · | · | C | · | **D** | · | · | · | · | · |
| rules-guide | · | · | · | · | · | · | C | · | · | · | · | · |
| getting-started | · | A | · | A | A | · | A | · | · | · | C | · |
| effective-usage | · | A | **M** | C | C | · | A | · | · | · | C | · |
| advanced-features | · | A | · | A | · | · | · | C | · | · | C | · |
| trustworthy-agents | · | A | · | C | · | A | · | A | · | · | · | · |
| settings-guide | · | A | · | · | C | A | · | · | · | · | · | · |
| directory-structure | · | · | · | · | **A** (excellent 200-line distinction `:48-58`) | · | · | · | · | · | · | · |
| mcp-guide | · | · | · | · | · | · | · | · | · | · | · | **C** (deferred tools + ToolSearch explained in MCP context `:47-55`) |
| recommended-plugins | · | · | · | · | · | · | · | · | · | · | C | · |
| multi-agent-patterns | · | · | · | A | · | · | C (worker output budget ~1-2k tokens `:65-73`) | · | · | · | · | · |
| workflow-patterns | · | · | · | C | · | · | · | · | · | · | · | · |

**Cross-cutting observations from full matrix:**
- **T1** (identity/version): NEVER directly addressed in any guide — Claude Code as product is the assumed background context
- **T9 (git commits) & T10 (PR creation)**: NEVER discussed in any guide. We tell users *what* CLAUDE.md does but not *how* Claude Code handles git/PRs by default. (Intentional gap? Or oversight? — see Demoted section.)
- **T11** (built-in skills): only `/init` and `/memory` mentioned consistently across guides; `/loop`, `/schedule`, `/sandbox`, `/btw`, `/rename` mentioned sporadically
- **T12** (deferred tools): mcp-guide is the ONLY guide that explains the mechanism (in MCP context). General concept not generally covered.

### Top 5 Gaps (final — 12/12 + 4 skills coverage)

#### Gap 1. Word-budget policy missing — `[HIGH]`
- **claude-code.md** `:255` — `keep text between tool calls to ≤25 words. Keep final responses to ≤100 words`
- **Our gap (verified 12/12):** `claude-md-guide.md:48-51` has 200-line file budget; no per-response word budget anywhere in any guide
- **Proposed fix:** add *"Length budgets as policy"* subsection to `claude-md-guide.md` "Writing Principles" — feeds Plan 04 Pattern 4-A
- **Source attribution:** paraphrase + cite Anthropic release-notes URL (NOT leak repo)
- **Risk:** none — direct citation possible

#### Gap 2. Memory/state verification doctrine — `[HIGH]` *(elevated, was Gap 3 in pass 1)*
- **claude-code.md** `:221-231` — `A memory that names a specific function, file, or flag is a claim that it existed when the memory was written... Before recommending it: check the file exists / grep for it`
- **NEW finding from skill audit:** `plugin/skills/audit/SKILL.md` Phase 3.7 ("Output Validation — Oracle Check", `:140-152`) **internally implements this exact doctrine**: *"Re-execute the rule's own primitive on the cited evidence. The rule's output is the hypothesis; the re-run is the oracle. The finding is valid only when the two agree."*
- **Our gap:** `trustworthy-agents-guide.md` Transparency principle (`:46-53`) covers inspectability of changelog & recommendations.json, but NOT the *"hypothesis vs oracle"* verification doctrine. We **practice** it (in `/audit`) but don't **publish** it.
- **Proposed fix:** add subsection to `trustworthy-agents-guide.md` Transparency principle titled *"Verification before assertion"*. Cite `/audit` Phase 3.7 as our own exemplar + Anthropic's auto-memory doctrine as same-pattern. **Self-grounded** — no external claim, just naming what we already do.
- **Synergy:** strongest gap of all five because we already DO this; only need to surface the pattern.

#### Gap 3. "What good Claude responses look like" missing — `[MEDIUM]` *(was Gap 4)*
- **claude-code.md** `:74-86` — text output discipline: pre-call announcement, status updates at key moments, no narration of internal deliberation, end-of-turn 1-2 sentence summary
- **Our gap (verified 12/12):** `effective-usage-guide.md` "Writing Effective Prompts" (`:83-94`) teaches user→Claude direction. Nothing teaches what *good Claude responses look like*.
- **Verified against unread guides:** `multi-agent-patterns-guide.md:65-73` discusses *worker→lead* output budget (~1-2k token summary), which is **different topic** (sub-agent context economy ≠ main-session response discipline). `workflow-patterns-guide.md` covers session organization, not response shape. Gap confirmed.
- **Proposed fix:** new subsection in `effective-usage-guide.md` titled *"What good Claude responses look like"* — short bullet list. Helps users diagnose when Claude over-narrates and what to push back on.

#### Gap 4. Fast mode toggle undocumented — `[MEDIUM]` `[VD]` *(was Gap 5)*
- **claude-code.md** `:251` — `Fast mode for Claude Code uses Claude Opus 4.6 with faster output (it does not downgrade to a smaller model). It can be toggled with /fast`
- **Our gap (verified 12/12):** Confirmed missing — searched `settings-guide.md` (Permission Modes section line 109-121) and all other guides; `/fast` and "Fast mode" appear nowhere.
- **Version drift `[VD]`:** leak says "only Opus 4.6"; current Claude Code reports "Fast mode... available on Opus 4.6 and Opus 4.7". Use forward-compatible wording (e.g., *"on supported Opus models"*).
- **Proposed fix:** brief mention in `effective-usage-guide.md` Permission Modes table sidebar OR `settings-guide.md` Permission Modes section

#### Gap 5. `file_path:line_number` clickable convention — `[MEDIUM]` *(NEW, found in pass 2)*
- **claude-code.md** `:72` — `Reference code as file_path:line_number — it's clickable`
- **Our gap:** NEVER mentioned across 12/12 guides. This is a Claude Code feature that improves response usability — `src/api/tasks.ts:45` becomes a clickable navigation link in supported terminals/IDEs.
- **Proposed fix:** one-sentence note in `effective-usage-guide.md` "Writing Effective Prompts" — *"Claude Code emits `file:line` references that are clickable in supported terminals/IDEs; encouraging Claude to use line refs in responses improves navigation"*.
- **Confidence:** MEDIUM — simple, low-cost, high UX leverage. Likely a *power-user* gap.

### Demoted / dropped from earlier passes
- **Old Gap 2 (Co-Authored-By override doc)** — DROPPED post-socratic critique 2026-05-20.
  - Reason: meta/educational value real but practical user value marginal (verified via Q1-Q4 socratic check). Pattern of *"user CLAUDE.md > Claude Code default"* is abstract architecture mental model, not daily-use knowledge.
  - Keep as internal note in this plan file. Do NOT ship.

### Skill audit observations (4 skills)

- `/create`, `/audit`, `/secure`, `/optimize` are **all aligned** with Claude Code's expectations — no behavioral divergences.
- **`/audit` Phase 3.7** (`:140-152`) is the verification-before-assertion doctrine in action — strongest anchor for Gap 2.
- **`/create`, `/audit`, `/secure`, `/optimize` all use the `learning-system.md` memory schema** for persistence — this is structurally similar to (though not identical to) Claude Code's auto-memory 4-type taxonomy. Our plugin learning-state design **converges with** Anthropic's memory design.
- **Skills practice, guides teach** — none of the 4 skills explicitly TEACH Claude Code product expectations; they execute on them. The gap between "we already do X internally" and "we publish X as guidance" is the structural opportunity for Plan 04.

### Plan 04 Pattern impact reassessment (post-audit)

| Pattern | Plan 04 entry | Status | Notes |
|---|---|---|---|
| Word budget → claude-md-guide | 4-A | confirmed | Gap 1; high-value, low-risk |
| Default stance → advanced template | 4-B | confirmed | Not audit-blocked; standalone work |
| Injection awareness → trustworthy-agents | 4-C | confirmed | Plan 03 dependency |
| **NEW 4-D** Memory verification → trustworthy-agents | NEW | **promote to HIGH** | Gap 2; strongest synergy (we already practice it) |
| **NEW 4-E** file_path:line refs → effective-usage | NEW | proposed | Gap 5; easy win |
| **DROPPED** Co-Authored-By override doc | — | dropped | Was Gap 2 in pass 1; socratic-failed |

Plan 04 needs amendment: add 4-D and 4-E; reorder by impact (4-D > 4-A > 4-C > 4-E > 4-B).

### Verification status (all gaps, post 12/12)
- Gap 1: ✅ confirmed missing across all 12 guides
- Gap 2: ✅ confirmed; `/audit` Phase 3.7 anchor verified at `audit/SKILL.md:140-152`
- Gap 3: ✅ confirmed missing across all 12 guides (multi-agent + workflow guides cover different domain)
- Gap 4: ✅ confirmed missing from settings-guide.md and all other guides
- Gap 5: ✅ confirmed missing across all 12 guides

### Plan 01 status: **COMPLETE**

Next plan to execute (per `00-README.md` ordering): Plan 02 (Opus 4.6 → 4.7 diff). Plan 04 needs amendment per the post-critique table below (NOT simple "+4-D+4-E" addition).

---

## Post-Completion Self-Recursive Critique (2026-05-20)

User requested second-pass socratic critique on the remaining 5 gaps using the same Q1-Q4 framework that demoted the original Gap 2 (Co-Authored-By). This section records the result.

### Method (Q1-Q4 framework)
- **Q1**: Must the user explicitly know this concept to use Claude Code well?
- **Q2**: Does this match a real, frequent user pain point?
- **Q3**: What is the actual marginal UX improvement, not the abstract pattern interest?
- **Q4**: What cognitive bias may have inflated the original rating?

### Per-Gap Re-Verdicts

#### Gap 1 — Word-budget policy → **DROP subsection; merge as illustration**
- **Category-error finding:** Anthropic's ≤25/≤100 word budget is Claude Code's **own internal behavior config**, NOT user-authored CLAUDE.md guidance. Different abstraction layers.
- Our existing "Be specific and verifiable" principle (`claude-md-guide.md:50`) already covers the general lesson.
- Adding a dedicated subsection over-engineers; word budget belongs as a 1-sentence illustration within existing principle, not a new pattern.
- Original HIGH rating reflected **appeal-to-authority bias** ("Anthropic does it → must be high-value").

#### Gap 2 — Memory verification doctrine → **MEDIUM (narrative-purpose only)**
- Two distinct value vectors were conflated:
  - **User UX value:** marginal — sophisticated meta-knowledge users rarely encode in CLAUDE.md (this is Claude Code's job to handle, not user's)
  - **Project self-narrative value:** real — naming our `/audit` Phase 3.7 pattern strengthens trustworthy-agents-guide positioning
- These are *different work types*, not one. Original HIGH rating mixed them.
- **Action:** keep ONLY if narrative work is the explicit intent. If goal is user UX, drop.

#### Gap 3 — Response discipline ("what good responses look like") → **HIGH (PROMOTED)**
- Real, frequent user pain point: "Claude over-narrates / explains too much / shows internal thought process"
- Diagnostic value real: users gain ability to recognize over-narration patterns AND can write CLAUDE.md rules to prevent them
- Verified against unread-pass `multi-agent-patterns-guide.md` and `workflow-patterns-guide.md` — domain truly uncovered
- **The only gap that survives a hostile re-verification as HIGH.**

#### Gap 4 — Fast mode toggle → **DROP**
- Niche feature: Opus models + sequential workflows only
- Narrow audience: excludes Pro/Free users (which is most of our user base), excludes Sonnet/Haiku users
- "missing from guides" does NOT entail "must be added" — link to Anthropic official docs suffices
- Original MEDIUM was inflated by **discovery momentum** ("we found it missing → must fix")

#### Gap 5 — file_path:line clickable refs → **DROP**
- Claude already follows this convention internally (`claude-code.md:72`)
- User CLAUDE.md command would have marginal reinforcement effect at best
- Pass-2 self-critique already flagged this as power-user-only; LOW value across normal users
- Original MEDIUM was inflated by "easy win" framing without weighing actual win size

### Revised Top Gaps Table

| Gap | Pass 1 → Pass 2 → Critique | Final action |
|---|---|---|
| 1. Word-budget | HIGH → HIGH → **drop subsection** | merge as 1-sentence illustration in existing "Be specific" content |
| 2. Memory verification | HIGH → HIGH → **MEDIUM (narrative only)** | conditional: keep IF narrative work intent, drop IF UX work intent |
| 3. Response discipline | MEDIUM → MEDIUM → **HIGH** | promote to headline addition |
| 4. Fast mode | MEDIUM → MEDIUM → **drop** | external Anthropic docs link only |
| 5. file_path:line | MEDIUM (new) → MEDIUM → **drop** | redundant with Claude default behavior |

### Plan 04 amendment (final, post-critique)

| Pattern | Status post-critique |
|---|---|
| 4-B (Default stance) | unchanged — keep |
| 4-C (Injection awareness, Plan 03 dep) | unchanged — keep |
| **4-F NEW** (Response discipline → `effective-usage-guide.md`) | promote — this is the headline addition |
| 4-A (Word budget) | demoted to 1-sentence illustration within existing principle |
| 4-D (Memory verification) | conditional — keep only if narrative-work intent declared |
| 4-E (file_path:line) | dropped |

**Net Plan 04 scope shrinks:** from 5 candidate patterns to **3 confirmed (4-B, 4-C, 4-F) + 1 conditional (4-D) + 1 micro-edit (4-A)**.

### Key takeaway

The initial gap inventory was inflated by 4 cognitive patterns:
1. **Appeal-to-authority bias** — Anthropic doing X ≠ users need to know X
2. **Discovery momentum** — "finding a gap" was conflated with "the gap matters"
3. **Self-narrative confusion** — project identity value was mixed with user UX value
4. **Pattern-recognition pleasure** — interesting structural observations rated higher than mundane-but-valuable ones

After two rounds of socratic critique, **only 1 of 5 gaps survives as genuinely HIGH** (Gap 3, response discipline). This is a useful negative result — knowing which gaps NOT to ship saves user attention.

### Self-critique of the self-critique
- **Hindsight over-correction risk:** after a successful Gap 2 (Co-Authored-By) demote, I might now under-rate gaps with real but modest value.
- **Test:** Gap 3 was MEDIUM under pass 2; under hostile re-verification it PROMOTED to HIGH. Surviving aggressive critique = real finding (not over-correction artifact).
- **Confidence:** HIGH for Gap 3 promotion, HIGH for Gap 4/5 demotion, MEDIUM for Gap 1 category-error claim (could use second opinion).
