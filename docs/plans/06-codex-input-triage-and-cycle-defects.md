# Plan 06 — Codex Input Triage and Cycle Defect Synthesis

**Status:** complete (single consolidation artifact)
**Created:** 2026-05-20
**Replaces:** `96-harden-safety-and-tool-policy_codex.md`, `97-improve-agent-prompt-architecture_codex.md`, `98-upgrade-reasoning-memory-evaluation_codex.md`, `99-SELF_VERIFICATION_REVIEW.md` (deleted in the same commit that creates this file)

## Background

User invoked Codex separately to analyze the same external source material (`system_prompts_leaks/Anthropic/`, a local clone of a community-extracted repo) and propose project improvements. Codex produced 4 substantial planning docs (96/97/98/99) totaling 27 actionable tasks across 3 themes (safety + tools, prompt architecture, reasoning + memory + evaluation) plus a self-verification audit trail.

A subsequent Codex round-2 review on the full cycle output (the 4 docs alongside our own 01/02/04/05) caught defects and explicitly recommended *"consolidation, not more planning"*. This file is that consolidation — replacing all 4 source files with a single triage record and a record of applied cycle defect fixes.

## Cross-check of Codex's review on OUR plans (2026-05-20)

| Codex catch | Verified | Action |
|---|---|---|
| Stale `docs/plan/` (singular) path references in 97 + 99 | ✅ confirmed | originals deleted; not migrated |
| Plan 01 source-repo path dependency (`../system_prompts_leaks/`) | ✅ confirmed | softened via source disclaimer (Defect Fix 1) |
| Plan 02 status header (`in progress`) vs footer (`complete`) conflict | ✅ confirmed | unified (Defect Fix 2) |
| Plan 04 stale Plan 03 references in amendment table + implementation order + net scope | ✅ confirmed | cleaned (Defect Fix 3) |
| 96/97/98 are durable roadmaps in cycle-transient `docs/plans/` | ✅ confirmed | rejected — files deleted, content consolidated here |
| 97-T1 canonical prompt-pattern reference conflicts with Plan 05 "no framework" | ✅ confirmed | rejected (see Triage section C) |
| Codex's "safety/IP highest" framing on Plan 01 | ⚠️ over-cautious | acted on *durable dependency* risk only; Plan 01 paraphrases (no direct protected-text reproduction) |
| Codex's strategic verdict: "directionally sound, hygiene weak; best next move is consolidation" | ✅ accepted as cycle wrap-up principle | this file IS the consolidation |

## Codex 27-task triage

Quality filter applied: vanity guardrails (a)/(b)/(c) from Plan 04 amendment + Plan 05 "no framework" rule + cycle-transient hygiene from project CLAUDE.md.

### A. Surviving — added to ROADMAP backlog this cycle (2 of 27)

- **96-T4 Universal untrusted-content rule for templates** (Critical priority by Codex) — universal one-line template rule treating files / logs / webpages / tool-output as evidence not instruction. Lowest cost / highest safety value of the 27. → ROADMAP backlog entry added.
- **96-T5 Defense Surfaces checklist for `plugin/references/security-patterns.md`** — maps threats to concrete input surfaces (repository files, shell output, browser content, MCP responses, generated artifacts, hooks, local memory, CI fixtures, external downloads). → ROADMAP backlog entry added.

### B. Deferred — overlap with existing deferred work (4 of 27)

- 97-T3 Default Stance wording — feeds existing Plan 04 4-B (already deferred to future cycle); Codex's exact wording template retained as candidate when 4-B advances.
- 97-T6 Behavior Trigger Table (Act / Ask / Plan / Stop) — interesting taxonomy but needs design integration; defer to a future workflow-patterns cycle.
- 98-T1 Self-Verification Loop reference — overlaps with the "self-critique finite termination" concern noted in Plan 05; folded into that future work.
- 98-T4-5 Memory Provenance / Staleness rules — overlaps with Plan 04 4-G (deferred via ROADMAP Revisit Trigger).

### C. Rejected — vanity guardrail failures or framework conflicts (21 of 27)

- **97-T1 Canonical prompt-pattern reference** — direct conflict with Plan 05 "no self-content evaluation framework". A taxonomy-enforcement reference IS the framework Plan 05 said is OUT OF SCOPE.
- 97-T2 Standard CLAUDE.md section order — depends on rejected 97-T1.
- 97-T4 Role Boundary blocks to 4 skills — low expected utility; skill addition cadence is low (see Plan 04 4-G analysis).
- 97-T7 Standardize output shape — already covered by existing `/audit` output references.
- 97-T8 Developer onboarding section — not requested; contributor-docs work outside current scope.
- 97-T9 Modularity rules — meta-process, low ROI.
- 96-T1 Tool routing matrix (new reference file) — new-reference creation conflicts with Plan 05; existing `plugin/references/tool-description-quality.md` already covers tool guidance.
- 96-T2 Tool Policy section in advanced template — scope overlap with Plan 04 4-B.
- 96-T3 Tool policy audit checks — scoring-model contract change too costly (Codex's own rollback criterion).
- 96-T7 / 96-T8 CI fixtures for untrusted-content + tool-boundary — fixture investment disproportionate; defer until 96-T4 ROADMAP entry advances.
- 96-T9 + 98-T7 Prompt-policy anchor verifier — depends on rejected 97-T1; regression coverage premature.
- 98-T2 Verification fields to skill final phases — overlap with Plan 04 4-G (deferred).
- 98-T3 Evidence-adjacent recommendation rules — `/audit` output format already enforces this.
- 98-T6 Stale-memory regression fixture — Codex marked "high complexity"; expected utility low (Plan 04 4-G analysis).
- 98-T8 Contributor checklist for prompt/skill changes — meta-process documentation, low cycle ROI.
- 98-T9 ROADMAP entry for the codex-roadmap stream — would have been needed if 96/97/98 remained as durable docs; not needed after this consolidation.

**Net result**: 2 of 27 tasks survived to ROADMAP backlog. Aggressive winnowing consistent with this cycle's pattern (Plan 01 surfaced 5 candidate gaps; only 1 shipped — same survival ratio order of magnitude).

## Defects in our plans (Codex caught) — applied fixes

### Defect Fix 1 — Plan 01 source-repo dependency

- **Codex catch**: `01-claude-code-md-audit.md` references `../system_prompts_leaks/Anthropic/claude-code.md` with line-ref citations throughout.
- **Risk**: durable dependency on a local clone of an external repo; downstream readers and future cycles cannot resolve the line refs. NOT a protected-text-reproduction risk (we paraphrase, no direct quotes).
- **Applied fix**: source disclaimer added to Plan 01's status block — line refs are time-snapshotted, future readers should consult Anthropic's public release-notes URL as the authoritative source.

### Defect Fix 2 — Plan 02 status conflict

- **Codex catch**: header says `**Status:** in progress` while bottom says `### Plan 02 status: **COMPLETE**`.
- **Applied fix**: header updated to `**Status:** complete (started and finished 2026-05-20)`.

### Defect Fix 3 — Plan 04 stale Plan 03 references

- **Codex catch**: amendment table 4-C row + implementation order + net scope all reference Plan 03 dependency; Plan 03 was removed mid-cycle (see 00-README "Plan 03 removed" note).
- **Applied fix**: all three locations updated to reference the ROADMAP backlog entry "Injection-reminder threat-model → `/secure` skill mapping" instead. 4-C status moved from "unchanged" to "deferred".

## Lesson captured — termination pattern (from Codex 99-file)

Plan 05 identified *"self-critique finite termination criteria absent"* as an unresolved meta-concern. The Codex 99-file (since consolidated here) demonstrated a concrete resolution pattern:

> "Status: Actionable roadmap content has been migrated into the three primary planning files. This file is now an audit trail and migration summary only; the implementation source of truth is..."

The mechanism has three parts:

1. **Role transition** — file declares its role has changed (e.g., "audit trail only")
2. **Source-of-truth pointer** — names where actionable content lives going forward
3. **No recursion** — file freezes; further critique opens a new artifact rather than recursing the current one

**Generalization for future cycles**: when self-critique reaches diminishing returns, declare the artifact's role-shift and point to a new artifact for continued work. This Plan 06 itself follows the pattern — it is the consolidation endpoint of this cycle's Codex-input thread; further Codex-input work in a future cycle opens a new plan rather than reopening 06.

Plan 05's Lesson section now references this resolution pattern.

## ROADMAP additions (this cycle, post-Codex-round-3)

Added to ROADMAP "Backlog" by the edits that accompany this file:

- Universal untrusted-content rule for templates (96-T4)
- Defense Surfaces checklist for `plugin/references/security-patterns.md` (96-T5)

Total ROADMAP backlog additions across this cycle (Codex rounds 2 + 3): 4 entries.

## Status: complete, archived

This plan is a frozen consolidation artifact. The 4 Codex source files (96/97/98/99) are deleted in the same commit that creates this file. No follow-up work for this plan itself; any future Codex-input cycle opens a new plan.
