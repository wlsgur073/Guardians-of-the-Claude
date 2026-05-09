# Anthropic Engineering Insights — Decision Backlog

**Status**: Active (routing artifact; bucket assignments are recommendations, not approvals)
**Created**: 2026-05-09
**Scope**: Single entry point that consolidates 22 proposals from [R1](./anthropic-engineering-insights-review.md), [R2](./anthropic-engineering-insights-review-round-2.md), [R3](./anthropic-engineering-insights-review-round-3.md), [R4](./anthropic-engineering-insights-review-round-4.md), [R5](./anthropic-engineering-insights-review-round-5.md) into one decision table. Five round documents remain authoritative for their reasoning; this file is the routing layer.

---

## Purpose

The 5-round review series produced 22 proposals + 7 explicit source skips across ~160K of analysis. Reading the series end-to-end is no longer the right entry point for execution decisions. This backlog assigns each proposal to one of four buckets — **adopt / pilot / defer / skip** — with a one-line rationale and the prerequisite that gates each move.

The taxonomy and stop conditions below are the converged output of:
1. The series' own self-described maturity signal (R5 § "Plan Series Maturity Signal").
2. Two independent re-reads with explicit instructions to surface blind spots; the second pass adjusted bucket assignments, split proposals where prerequisites differed, redefined defer conditions, and tightened stop criteria.

No proposal is authorized by this document. A bucket assignment is a recommended next state, not a commit.

---

## Decision Table

**Reading the IDs**: Single and primed letters (`L`, `D`, `H`, `O`, `A'`, `C'`) are stable proposal references whose statements live in the round documents (see [References](#references)). Hyphens split a proposal into halves with separate prerequisites (`A'-postcheck`, `K-schema`, `A'-briefing`, `K-judge`, `K-ref`); plus signs combine proposals that move as one decision (`P + G`, `E + E-ext`). The **Unit** column's `U-`-prefixed labels group rows that move together — rows sharing a Unit move as one decision; rows without a Unit are independent.

### Adopt (move on)

| ID | Proposal | Round | Unit | Rationale | Prerequisite |
|---|---|---|---|---|---|
| **P + G** | Auto Mode + Sandboxing parity (combined permissions/safety sweep) | R5 / R3 | **U-perm** | P and G share target files (settings guide + `templates/advanced/.claude/settings.json` + `/secure` SKILL.md) and i18n cascade. Splitting creates rework + risk of contradictory wording around manual / Auto Mode / Sandbox / `--dangerously-skip-permissions`. | Read shared surfaces; fetch Auto Mode docs pair (`permission-modes`, `auto-mode-config`) + official sandboxing docs |
| **E + E-ext (+ J)** | Best Practices parity audit + Progressive Disclosure axis (+ optional context-rot rationale) | R2 / R3 | **U-bestp** | E and E-ext are bundled by source (canonical Anthropic framing for our project's primary subject). J is at most a 1–2-sentence sub-item inside `claude-md-guide.md` if rationale is needed; not standalone. | Read 5 E target files; bundled with E-ext; J folded in or skipped during E execution |
| **L** | Oracle coverage map (`.github/scripts/check-*.py` × audit rules) | R4 | — | Discovery, not pilot — a 1-page matrix with zero rollout risk. Prerequisite knowledge for K (eval framework upper bound) and the post-check half of A'. **Shipped 2026-05-09** — see [oracle-coverage-map.md](./oracle-coverage-map.md). | List CI scripts; map each to the rules they verify |

### Pilot (small contained step, can stop after)

| ID | Proposal | Round | Unit | Rationale | Prerequisite |
|---|---|---|---|---|---|
| **C'** | Dual-layer SKILL audit (scope-reduced), pilot on `/audit` | R2 | — | Pilot first; full rollout decided by yield. If pilot finds nothing, do not roll out to other skills. | Read `plugin/skills/audit/SKILL.md` |
| **A'-postcheck** | Deterministic post-check half of A' / A'-rt (split out) | R1 / R2 | — | The post-check half overlaps with L and is valuable independent of cause distribution. Unblocks once L reveals concrete oracle coverage. | L completed first |
| **K-schema** | YAML rubric schema + deterministic graders only (split from K family) | R4 | — | Schema scaffolding does not depend on judge calibration. R5 K-ref blocks LLM-judge trust, not framework cleanup. `llm_rubric` grader stays disabled / experimental. | L completed first |

### Defer (blocked on evidence or external trigger)

| ID | Proposal | Round | Unit | Defer reason | Unblock condition |
|---|---|---|---|---|---|
| **A'-briefing** | 4-component briefing template half of A' / A'-rt (split out) | R1 / R2 | — | Central premise (briefing-gap as dominant cause) is unmeasured | 2-stage causal sampling: n=5 hypothesis → n=15–20 decision gate |
| **D** | Think-tool-style reasoning checkpoints | R1 | — | Differs from A' — D can pilot on one phase if hallucination/criterion-ambiguity signal appears at n=5; does **not** require the n=15–20 briefing-gap gate | n=5 sampling with hallucination/ambiguity signal |
| **A'-ev / K-judge / K-ref** | LLM-as-judge adoption (judge half of K family) | R2 / R4 / R5 | **U-judge** | R5 K-ref converted judge adoption to a high-effort evidence project; same-family judge bias makes uncalibrated adoption net-negative | 20–50 human-scored audit outputs as calibrated ground truth |
| **F / F-ext** | Phase-Boundary Contract Check + intra-phase notes | R2 / R3 | — | Re-gated: the question is **not** "do contracts exist?" but "are there phase-boundary failures or state-loss pain in `/audit`?" If pain is real, minimal contracts may be justified even if none exist now. | Evidence of phase-boundary failure / state-loss pain (from C' pilot or false-positive sampling) |
| **B / B-cond** | Agent Patterns guide + harness subsection | R1 / R2 / R4 | — | Strategically aligned with `project_meta_system_vision` memory but doubly conditional. **User-side signal is mandatory** — without external demand, B is mission drift toward "Anthropic concepts explained." | E + C' results delivering verified pattern-to-skill mappings **and** explicit user demand |

### Skip (do not pursue)

| ID | Proposal | Round | Reason |
|---|---|---|---|
| **H** | Code-execution MCP guide section | R3 | Narrow audience; consolidation lowers cost but does not create demand |
| **O** | Programmatic Tool Calling guide section | R4 | Same as H. Revisit only if `mcp-guide.md` is being reworked for other reasons or users ask |

---

## Explicit Source-Level Skips (sources reviewed and dismissed)

| Source | Round | Reason |
|---|---|---|
| Contextual Retrieval (direct adoption) | R1 | No RAG system in repo; principle absorbed into A' family |
| Desktop Extensions | R2 | Targets Claude Desktop, not Claude Code plugins |
| Just-in-time retrieval for `/audit` subagents | R3 | Research vs verification paradigm mismatch |
| AI-Resistant Technical Evaluations | R4 | Hiring domain, not AI agent evaluation |
| Building a C Compiler — main content | R4 | 16-agent / $20K scale mismatch; oracle vocabulary absorbed into L |
| Eval Awareness in BrowseComp — main content | R5 | Open-internet scenario; theoretical note absorbed into K-ref #3 |
| Harness Design for Long-Running Apps — main content | R5 | 20× cost ratio mismatch; self-eval bias warning absorbed into K-ref #1/#2 |
| Managed Agents | R5 | Hosted platform product, out of scope |

---

## Recommended Sequence

Serial execution. Tracks share attention and release discipline as a single maintainer, even when files do not overlap.

1. **Read-only sweep over U-perm shared surfaces** — settings guide, `templates/advanced/.claude/settings.json`, `plugin/skills/secure/SKILL.md`, plus official Auto Mode docs pair and Sandboxing docs.
2. **Ship U-perm (P + G combined)** — single permissions/safety parity sweep covering manual / Auto Mode / Sandbox / `--dangerously-skip-permissions` as one decision framework. Honest budget: medium effort over 5 surfaces × i18n (ko-KR + ja-JP) + frontmatter version bumps.
3. **Ship U-bestp (E + E-ext + optional J)** as a separate parity sweep after U-perm stabilizes.
4. **Track 2 diagnostics** (after Track 1 clears):
   - L: oracle coverage map (1 page)
   - False-positive n=5 hypothesis sampling
   - C' pilot read of `/audit` SKILL.md
5. **Choose runtime / eval changes** — A'-postcheck, K-schema, then evidence-gated decisions on A'-briefing, D, F/F-ext, K-judge.

**Do not start**:
- K-judge / U-judge cluster (without 20–50-item calibrated ground truth)
- A'-briefing (without causal sampling)
- B / B-cond (without external user signal)
- H / O (clean skip)
- Round 6 of the review series (without trigger — see below)

---

## Stop Conditions for Round 6

The series should stop accumulating rounds. Round 6 requires a triggering event, not curiosity. Defensible triggers:

1. New canonical Claude Code feature **or normative docs change affecting configuration** ships from Anthropic.
2. New canonical Anthropic guidance directly about Claude Code skills / plugins / evals — **not** generic engineering posts.
3. Empirical failure cluster — user-reported or internal — not covered by R1–R5. **Cluster threshold**: ≥3 independent reports, **or** one high-severity security / data-loss issue.
4. An **implemented** proposal fails in a measured way and the failure mode points outside the current backlog.

A single referenced quote going stale (formerly in scope as a trigger) is **maintenance work**, not a Round 6 trigger. Patch citations in place.

Curiosity-driven mining of further engineering blog posts is explicitly out of scope. Decline new rounds without a trigger.

---

## References

### Round documents (authoritative for proposal reasoning)
- [Round 1](./anthropic-engineering-insights-review.md) — Contextual Retrieval, Building Effective Agents, SWE-bench, Think Tool
- [Round 2](./anthropic-engineering-insights-review-round-2.md) — Best Practices, Multi-Agent Research, Desktop Extensions, Writing Tools, Postmortem
- [Round 3](./anthropic-engineering-insights-review-round-3.md) — Agent Skills, Context Engineering, Sandboxing, Code Execution with MCP
- [Round 4](./anthropic-engineering-insights-review-round-4.md) — Demystifying Evals, Advanced Tool Use, Effective Harnesses, AI-Resistant Evals (skip), C Compiler (partial skip)
- [Round 5](./anthropic-engineering-insights-review-round-5.md) — Auto Mode, Eval Awareness (skip), Harness Design (skip), Managed Agents (skip)

### Internal repo surfaces referenced
- `plugin/skills/audit/SKILL.md`, `plugin/skills/secure/SKILL.md` — primary skill surfaces under review
- `docs/guides/` (settings, claude-md, advanced-features, mcp, effective-usage) — primary guide surfaces under review
- `templates/starter/CLAUDE.md`, `templates/advanced/CLAUDE.md`, `templates/advanced/.claude/settings.json` — template surfaces
- `.github/scripts/check-*.py` — oracle candidates for L
- `test/` (gitignored, local-only) — eval framework, subject of K-schema and U-judge
- `ci/` smoke lane — bridge candidate between local `test/` and shipped regression checks
