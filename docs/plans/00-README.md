# Anthropic Prompt Research — Plan Index

**Created:** 2026-05-20
**Branch:** `research/anthropic-prompt-patterns`
**Source data:** local clone of `asgeirtj/system_prompts_leaks` at `../system_prompts_leaks/` (only `Anthropic/` retained by user)
**Purpose:** identify and apply patterns from Anthropic's published & community-extracted system prompts to improve our guides, skills, and templates.

## Plan Status

| # | File | Topic | Status |
|---|------|-------|--------|
| 01 | [01-claude-code-md-audit.md](01-claude-code-md-audit.md) | Audit our 12 guides vs `claude-code.md` | **complete** + self-recursive critique (only Gap 3 survives HIGH) |
| 02 | [02-opus-evolution-diff.md](02-opus-evolution-diff.md) | Opus 4.6 → 4.7 evolution patterns | **complete** (6 patterns; initial hypothesis refuted) |
| 04 | [04-high-impact-patterns.md](04-high-impact-patterns.md) | Implement HIGH IMPACT patterns | **partially shipped** — 4-F shipped this cycle (response discipline → effective-usage-guide.md); 4-G deferred (see ROADMAP Revisit Trigger); 4-A/D/E dropped; 4-B independent (next cycle); 4-C deferred to ROADMAP backlog |
| 05 | [05-content-evaluation-framework-absence.md](05-content-evaluation-framework-absence.md) | Why no self-content evaluation framework | **complete** (decision recorded; framework introduction OUT OF SCOPE until triggers fire; termination-pattern resolution added post-Codex round-3) |
| 06 | [06-codex-input-triage-and-cycle-defects.md](06-codex-input-triage-and-cycle-defects.md) | Codex 4-doc consolidation + cycle defect fixes | **complete** (replaces 96/97/98/99; 2 of 27 Codex tasks → ROADMAP backlog; 4 → existing deferred work; 21 rejected) |

> **Plan 03 removed from this cycle (2026-05-20, Codex round-2)** — the original "injection reminders → /secure skill" scope was not started this cycle and was converted to a ROADMAP "Backlog" entry. Can reopen as a separate cycle in future.
>
> **Plans 96-99 removed and consolidated into Plan 06 (2026-05-20, Codex round-3)** — Codex's externally-generated 3-file roadmap (96/97/98) plus its self-verification audit (99) consolidated into a single triage record. 27 Codex tasks triaged: 2 → ROADMAP backlog, 4 → folded into existing deferred work, 21 → rejected per Plan 04 amendment vanity guardrails and Plan 05 framework-absence rule. Cross-plan defects (Plan 01 source-repo dependency, Plan 02 status conflict, Plan 04 stale Plan 03 references) fixed inline; see Plan 06 §"Defects in our plans" for the application record.

## Key cross-plan findings
- **Self-critique result (Plan 01):** of 5 original gaps, only **Gap 3 (response discipline)** survives as HIGH. Gap 4/5 dropped, Gap 1 demoted to micro-edit, Gap 2 conditional on narrative-vs-UX intent.
- **Evolution finding (Plan 02):** initial hypothesis "explicit → inferential" was a **category error** (community-extracted vs Official file confusion). Actual pattern: 4.6→4.7 is MORE structured, not less (+21% length, new explicit sub-blocks).
- **Convergence:** Plan 02 found `<acting_vs_clarifying>` (new in Official 4.7) — a direct, citable Anthropic source for Plan 01's Gap 3. The single surviving HIGH gap has authoritative source material.

## Execution order
01 first (foundational — identifies what's already covered and what's missing). 02, 03, 04 depend on 01 findings to avoid duplication.

## Workflow constraints
- Plans are cycle-transient per project CLAUDE.md — directory will be cleaned before merge to main.
- No CHANGELOG entries for plan creation/iteration (per project CLAUDE.md `docs/plans guard`).
- No i18n mirroring (transient, English-only).
- File modifications outside `docs/plans/` require explicit user approval per memory `feedback_git_approval`.

## Source attribution constraint
- `Anthropic/Official/*` — Anthropic-published, safe to cite. **Source URL:** `https://platform.claude.com/docs/en/release-notes/system-prompts`
- `Anthropic/{root,raw,old,FlintK12}/*` — community-extracted. Use as **pattern reference** only; do NOT quote verbatim in shipped docs.
- All shipped doc additions should cite Anthropic's official release-notes URL, not this leak repo.
