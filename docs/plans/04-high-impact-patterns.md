# Plan 04 — High-Impact Pattern Implementation

**Status:** not started
**Effort:** ~1 day total (3 independent patterns)
**Dependencies:** Plan 01 (confirm none already implemented), Plan 03 (for 4-C content source)

## Goal
Implement the 3 HIGH IMPACT actions from 2026-05-20 brainstorm. Each pattern is independently mergeable.

## Patterns

### 4-A. Quantified length budgets — claude-md-guide.md
- **Source:** `claude-code.md:255` ("≤25 words between tool calls, ≤100 words final")
- **Target:** `docs/guides/claude-md-guide.md` → "Writing Principles" section
- **Change:** add subsection *"Length budgets as policy"* with:
  - Paraphrased example: Anthropic uses per-response word budgets (link to release-notes URL)
  - Recommendation: per-section line budget in CLAUDE.md, not just total
  - Cross-link to our own `CLAUDE.md` line-budget doctrine (`<200` lines)
- **Verification:**
  - Frontmatter `version` bump (current `1.3.2` → `1.4.0`)
  - `python .github/scripts/check-frontmatter-parity.py` passes
  - i18n cascade: ko-KR + ja-JP mirror updates
- **Risks:** must not exceed `~130` guide budget; verify with `(Get-Content file).Count`

### 4-B. Default-stance single-sentence policy — templates/advanced
- **Source:** `Official/claude-opus-4.7.md` `<default_stance>` section
- **Target:** `templates/advanced/CLAUDE.md` OR `templates/advanced/.claude/rules/*.md`
- **Change:** add example block showing **"single-sentence policy + threshold"** pattern (paraphrased, not verbatim)
- **Verification:**
  - Frontmatter version bump
  - ko-KR + ja-JP mirror updates
  - `check-i18n-parity.py` passes
- **Decision needed:** which file to edit — main `CLAUDE.md` or a `.claude/rules/*.md` example? TBD after re-reading template.

### 4-C. Injection awareness section — trustworthy-agents-guide.md
- **Source:** `claude.ai-injections.md` threat model (see Plan 03)
- **Target:** `docs/guides/trustworthy-agents-guide.md`
- **Change:** new section *"Defending against tag-disguised user input"* (uses Plan 03 draft)
- **Verification:**
  - Guide stays under `~185` lines (per project CLAUDE.md budget)
  - Frontmatter version bumped
  - ko-KR + ja-JP mirrors updated
- **Dependency:** must wait for Plan 03 draft completion

## Scope

### In scope
- 3 independent patterns above (each a separate commit)
- i18n cascade (ko-KR + ja-JP) for each guide change
- CHANGELOG entries (user-visible doc changes get entries per project CLAUDE.md)
- Frontmatter version bumps per file

### Out of scope (deferred — needs separate plan if pursued)
- **XML-tag structuring pattern** (Pattern 3 in original brainstorm): defer — may be over-engineering for general users
- **Memory schema education**: defer — outside project scope (we teach configuration, not Claude's memory schema)
- **Memory verification doctrine** (Pattern 5): defer — already implicit in trustworthy-agents-guide.md (Plan 01 will confirm)

## Method (per pattern)
1. Confirm gap exists via Plan 01 audit findings
2. Draft change in this plan file under `## Drafts`
3. Get user approval for draft
4. Apply to actual files (EN canonical first → ko-KR → ja-JP)
5. Run pre-push validators per project CLAUDE.md release-time sweep
6. Stage + show diff to user → get commit approval (per `feedback_git_approval`)
7. Commit (no Co-Authored-By trailer per `feedback_no_co_authored_by`)

## Deliverables (per pattern)
- Draft text in this plan file
- After approval: actual file changes (3 separate commits, ordered A → B → C)
- CHANGELOG `## [Unreleased]` entry per pattern (per `project_unreleased_changelog_pattern`)

## Success criteria
- All 3 patterns merged independently
- All i18n mirrors in sync
- Guide line-count budgets respected
- All validators GREEN before push
- No verbatim leak-repo text in any shipped file

## Risks
- May overlap with existing content → Plan 01 audit mitigates
- ko-KR / ja-JP translation drift → cascade checklist per project CLAUDE.md
- Mid-cycle: project CLAUDE.md mentions "v2.18.0 shipped ~6 docs/plans bullets for 0 files released" — cycle hygiene matters; clean docs/plans/ before release

---

## Amendment (2026-05-20) — post Plan 01 self-critique + Plan 02 P2 source + Codex consultation

**The original Patterns section (4-A/B/C) and earlier-proposed 4-D/4-E above are SUPERSEDED.** See the revised entry table below.

### Why amendment

Three inputs reshape the plan:
1. **Plan 01 self-recursive critique**: only Gap 3 (response discipline) survives as HIGH; Gap 1 demoted to micro-edit, Gap 4/5 dropped, Gap 2 conditional.
2. **Plan 02 P2 finding**: Anthropic Official 4.7 added `<acting_vs_clarifying>` and `<capability_check>` — a *publicly-cited* source for Gap 3.
3. **Codex consultation (2026-05-20)**: introduced two-score routing rule (UX × Doctrine) + warned against grounding our identity in *external internal patterns*.

### Codex routing rule (operational)

Every recommendation gets **two scores**:
- **User UX Value** — does the user benefit directly when writing their CLAUDE.md?
- **System Doctrine Value** — does it strengthen cross-skill consistency, maintainer judgment, or ROADMAP North Star milestones?

Routing:

| UX | Doctrine | Placement |
|---|---|---|
| HIGH | HIGH | both — `docs/guides/` (user wording) + `plugin/references/` (maintainer wording) |
| HIGH | LOW/MED | `docs/guides/` (user-facing) |
| LOW/MED | HIGH | `plugin/references/` (maintainer-facing) |
| LOW | LOW | drop |

**Scope guard (Codex round-2 clarification, 2026-05-20):** this routing rule is a one-cycle placement aid, NOT a recurring evaluation framework. It does not introduce weights, scoring rituals, or repeated bureaucracy. Reusing it in a future cycle is optional; codifying it as project process is OUT OF SCOPE per Plan 05.

### Vanity guardrail (Codex #2 protection)

System Doctrine Value HIGH requires **at least one** of:
- (a) strengthens `/audit` ↔ `/secure` ↔ `/optimize` consistency
- (b) prevents future contributors from repeating an avoidable mistake
- (c) directly contributes to a ROADMAP North Star milestone

Vanity signals (HIGH → demote):
- "interesting finding" without (a)/(b)/(c) match
- alignment with external *private/internal* doctrine treated as self-justification
- maintainer themselves would not consult it

### External source attribution boundary (Codex #3 protection)

| External reference type | Use |
|---|---|
| Anthropic public release-notes (e.g., `platform.claude.com/docs/.../system-prompts`) | ✅ source attribution OK — *citing a public standard* |
| Anthropic *internal* / leak / inferred / private doctrine | ❌ identity grounding NOT OK |

Boundary rule: external public docs are *reference*, never *identity anchor*.

### Revised entry table

| Entry | Status | UX | Doctrine | Placement |
|---|---|---|---|---|
| **4-F NEW (HEADLINE)** Response discipline | promote | HIGH | HIGH | `docs/guides/effective-usage-guide.md` + (optional) `plugin/references/` |
| 4-G NEW (conditional) Memory/state verification doctrine | conditional ship | LOW | MED-HIGH | `plugin/references/verification-doctrine.md` (NEW maintainer file) |
| 4-B Default-stance template example | unchanged from original | (TBD) | (TBD) | `templates/advanced/` |
| 4-C Injection awareness section | **deferred** — Plan 03 work moved to ROADMAP "Backlog" entry *Injection-reminder threat-model → `/secure` skill mapping* (2026-05-20, Codex round-2) | (TBD) | (TBD) | `docs/guides/trustworthy-agents-guide.md` |
| 4-A Word budget | DEMOTED → optional micro-edit | LOW | LOW | drop, or 1-line illustration within existing "Be specific" content |
| 4-D Memory verification (was new) | RE-ROUTED → merged into 4-G | — | — | (see 4-G) |
| 4-E file_path:line refs (was new) | DROPPED | LOW | LOW | — |

### 4-F (NEW HEADLINE) — Response discipline

**Source**: Anthropic Official Opus 4.7 system prompt — `<acting_vs_clarifying>` + `<capability_check>` blocks (public release-notes, not internal/leak)
**Target file**: `docs/guides/effective-usage-guide.md`
**Change**: new subsection *"What good Claude responses look like"* — 4–6 short bullets diagnosable patterns + a CLAUDE.md encoding example

**Codex reframe applied (#3 boundary rule)**:
- ❌ NOT framed as "mirroring Anthropic's internal pattern"
- ❌ NOT framed as "self-grounded by Claude Code internal doctrine"
- ✅ Framed as "Claude Code response patterns users can diagnose against"
- ✅ Source = Anthropic *public* release-notes URL only
- ✅ Identity = ours (the diagnostic vocabulary is for our users), reference = theirs (public docs)

**i18n cascade required**: ko-KR + ja-JP mirrors per project CLAUDE.md.

### 4-G — Memory/state verification doctrine — **DEFERRED**

**Status:** deferred to observation period — see ROADMAP "Revisit Triggers" entry *"Memory/state verification doctrine naming (4-G)"*.

**Why deferred (verified 2026-05-20 — supersedes earlier vanity-guardrail check above)**:

Original guardrail assessment was wrong on two of three axes once directly verified:

- **(a) cross-skill consistency — PARTIAL FAIL on re-read**: only `/audit` Phase 3.7 (`audit/SKILL.md:140-152`) implements the *hypothesis-vs-oracle re-execution* (narrow) pattern. `/secure` Phase 4.1 (`secure/SKILL.md:161-167`) and `/optimize` Phase 4.1 (`optimize/SKILL.md:127-135`) implement *integrity verification of generated artifacts* — a different sub-family within the broader *verify-before-completing* family. Three skills are NOT practicing the same narrow doctrine.
- **(b) contributor protection — fact-check INVERTED on git log**: skill-addition history is NOT "2y+ unchanged" as originally claimed. Actual: 4-skill burst 2026-03-31 → 2026-04-06, then 6-week plateau as of 2026-05-20. 7-week data cannot distinguish burst-vs-plateau extrapolation.
- (c) ROADMAP contribution — unchanged: peripheral / weak.

**Decision axis (unresolvable with current data):**

| Interpretation | Action |
|---|---|
| Narrow doctrine + plateau | drop |
| Broad doctrine + burst | ship (as *"every skill ends with a Verify Phase"* meta-contract) |

7-week skill-addition history is insufficient to choose. Defer until ROADMAP trigger fires.

**Lesson archived to Plan 05 candidate list (for future inclusion):** "self-critique that names unverified assumptions without verifying them" is itself an anti-pattern — observed here when initial guardrail-check assumed (a)/(b)/(c) passed without re-reading the cited skill phases. Verification cost was small (re-read + 1 git log command); naming-without-verifying produced a wrong recommendation that would have shipped without challenge.

### Net Plan 04 scope (final)

| Layer | Entries | Effort |
|---|---|---|
| User-facing new (shipped this cycle) | **1** (4-F) | ✅ shipped 2026-05-20 |
| Maintainer-facing new (deferred) | **1** (4-G) | deferred — see ROADMAP Revisit Trigger |
| User-facing existing (deferred to future cycles) | 4-B (independent, next cycle); 4-C (depends on ROADMAP backlog) | per their original entries |
| Dropped/demoted | 4-A (demoted), 4-D (rerouted-then-deferred via 4-G), 4-E (dropped) | 0 |

### Implementation order

1. **4-F** first — largest user value, source confirmed, Codex reframe applied
2. **4-G** if narrative work decision = YES (separate user decision, not automatic)
3. **4-B** independent (next cycle); **4-C** deferred — depends on ROADMAP backlog entry *Injection-reminder threat-model → `/secure` skill mapping* advancing in a future cycle

### Amendment status: applied 2026-05-20
