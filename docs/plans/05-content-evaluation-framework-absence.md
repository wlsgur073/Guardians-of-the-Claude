# Plan 05 — Why No Self-Content Evaluation Framework

**Status:** complete (decision recorded, no further work)
**Created:** 2026-05-20
**Closes:** meta-discussion thread from the Plan 01 self-recursive critique session

## Question

Why does this project have no explicit evaluation framework for its own content (guides, skills, templates), while it has an elaborate scoring model (`plugin/skills/audit/references/scoring-model.md`) for evaluating user-authored CLAUDE.md files?

## What we have (asymmetry confirmed)

| Tool | What it evaluates | Kind |
|---|---|---|
| README "Philosophy" `:23-28` | guidance for writing CLAUDE.md (4 principles) | **writing rubric**, not evaluation tool |
| ROADMAP "North Star" `:19-43` | direction of project evolution | **vision**, not measurement |
| `plugin/skills/audit/references/scoring-model.md` | user-authored CLAUDE.md (T1/T2/T3, LAV, Quality Gate, Maturity Level) | **measurement tool for user content** |
| (none) | our own guides / skills / templates quality | **absent** |

The asymmetry is structural, not accidental.

## Hypotheses considered

| # | Hypothesis | Probability | Evidence |
|---|---|---|---|
| A | Oversight — `/audit` scoring built carefully but self-content evaluation simply forgotten | LOW (~5%) | Unlikely given deliberation visible in scoring-model.md design; we noticed asymmetry repeatedly without acting |
| B | Intentional absence — overhead exceeds value for a 12-guide, slow-changing set | **HIGH (~70%)** | Codex consultation, `/ultrareview` for major branches, and organic PR/CHANGELOG cycles already operate effectively without it |
| C | Structural — meta-system identity requires adaptation speed; a fixed rubric would constrain that | MEDIUM (~25%) | ROADMAP North Star emphasizes evolution; codified rubric resists that |

Best fit: **B + C** (intentional, with structural underpinning).

## Decision

The absence of a self-content evaluation framework is a **deliberate operational choice**, not an oversight.

Current operational mode for self-content quality:
- External review on demand (Codex consultations, `/ultrareview` for major branches)
- Organic feedback cycle (issues, PRs, CHANGELOG-tracked iteration)
- Case-by-case maintainer judgment (no codified rubric)
- Self-recursive critique as needed (ad-hoc, not formalized as a tool)

Framework introduction is **explicitly OUT OF SCOPE** until the re-evaluation triggers below fire.

**Axis hierarchy clarification (post-Codex round 2, 2026-05-20):** when meta-system narrative value is considered (e.g., for maintainer-facing references), it acts as a SECONDARY routing axis — never as a co-equal identity driver to user UX value. README Philosophy remains primary; ROADMAP North Star is its directional context, not its peer. The two-score routing rule introduced in Plan 04's amendment is a one-cycle placement aid (see Plan 04 §"Scope guard"), not an elevation of narrative to co-equal status.

## Re-evaluation triggers

Reopen this decision only if:
1. **≥3 independent contributor-confusion incidents** about guide quality criteria (issue/PR comments asking "what's the standard?")
2. **Measurable guide-quality divergence** — two guides give contradictory advice on the same topic and the inconsistency isn't caught until ship
3. **A ROADMAP milestone** requires self-content evaluation as a prerequisite (e.g., automated quality regression detection in CI)

Until any trigger fires, decisions stay case-by-case.

## Lesson captured — linguistic inflation anti-pattern

This plan exists primarily to prevent a specific recurrence pattern observed in the session that created it:

Ad-hoc Q1-Q4 socratic prompts (invented in the moment to demote one gap) were later referred to as *"the Q1-Q4 framework"* — and several turns of analysis treated this informal pattern as if it were a project-owned evaluation system. It was not. The Codex consultation prompt and subsequent meta-discussion built further conclusions on top of this inflated label before the user surfaced the question *"what's the design?"* — at which point the inflation was visible.

**Rule for future sessions:**

- Ad-hoc critical-thinking prompts are NOT a framework.
- A *framework* requires explicit design, named author, documented scope, persistence across sessions, and presence in project artifacts.
- If a recently invented question set is about to be referred to as "the X framework", first check whether it exists in `docs/`, `plugin/references/`, or `templates/`. If not, use "those Q1-Q4 questions" or "the ad-hoc critique from earlier" — never *"the framework"*.

### Resolution pattern for self-critique termination (added 2026-05-20, post-Codex round-3)

A related concern within this lesson is *finite termination of self-critique recursion* — once the Q1-Q4 inflation was named, every subsequent self-critique threatened to become another infinite regress. The Codex 99-file (since consolidated into Plan 06) demonstrated one concrete resolution. The mechanism:

1. **Role transition** — the artifact explicitly declares its role has changed (e.g., "now an audit trail and migration summary only")
2. **Source-of-truth pointer** — names where actionable content lives going forward
3. **No recursion** — the file freezes; further critique opens a new artifact rather than recursing the current one

This is one model for terminating self-critique cycles. Future sessions can apply the same pattern when self-critique reaches diminishing returns. See Plan 06's *Lesson captured — termination pattern* section for the generalization.

## Status: complete, archived

This plan is a frozen decision artifact. No follow-up work.
