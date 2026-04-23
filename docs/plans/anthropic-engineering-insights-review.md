# Anthropic Engineering Insights — Applicability Review

**Status**: Draft (evaluation basis, not an approved change)
**Created**: 2026-04-22
**Last revised**: 2026-04-22 (three minor calibrations from cross-round self-review — see end of Unifying Theme, end of Proposal A' Source Evidence, and Contextual Retrieval Skip rationale)
**Scope**: Assesses whether patterns from four Anthropic engineering posts transfer to this repository (documentation + plugin marketplace, no runtime application code).

---

## Purpose

This document captures proposals derived from a focused, two-pass review of four Anthropic engineering posts. Each proposal is paired with source evidence, risks, and explicit prerequisites. **No change is authorized by this document.** It exists as a basis for later judgment on whether to proceed.

The review was performed in two passes:

1. **Pass 1** — extract ideas from each article and map to project surface area.
2. **Pass 2** — critique Pass 1 against the article texts; downgrade overclaims, surface underclaims, and identify cross-article themes.

The content below reflects the Pass 2 state.

---

## Source Material

1. [Contextual Retrieval](https://www.anthropic.com/engineering/contextual-retrieval) (Anthropic Engineering)
2. [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) (Anthropic Engineering)
3. [SWE-bench Sonnet — engineering](https://www.anthropic.com/engineering/swe-bench-sonnet) (Anthropic Engineering)
4. [The "think" Tool](https://www.anthropic.com/engineering/claude-think-tool) (Anthropic Engineering)

---

## TL;DR

| #  | Proposal                                          | Confidence        | Effort       | Primary target                                    |
|----|---------------------------------------------------|-------------------|--------------|---------------------------------------------------|
| A' | Subagent briefing + deterministic post-check      | Medium-high       | Medium       | Known subagent false-positive rate (38–50%)       |
| D  | Think-tool-style prompting in `/audit` SKILL.md    | Medium            | Low-medium   | Policy-heavy, sequential reasoning inside `/audit` |
| C' | Dual-layer SKILL audit (trigger + usage)          | Medium            | Medium       | Trigger clarity and usage-spec robustness         |
| B  | "Agent Patterns" guide addition                   | Low-medium        | Medium-high  | Strategic positioning (meta-system narrative)     |
| —  | Contextual Retrieval — direct adoption            | Skipped           | —            | Not a RAG system; insight absorbed into A'        |

Confidence ordering: **A' > D > C' > B**. All are contingent on the "Unverified Assumptions" ledger at the end of this document.

---

## Unifying Theme (Cross-Article Synthesis)

All four articles share a common failure mode and a common response:

> **Information is lost at a boundary, and reconstructing it at that boundary improves downstream quality.**

| Article                   | The boundary                            | The reconstruction mechanism                          | Fit to theme |
|---------------------------|-----------------------------------------|-------------------------------------------------------|--------------|
| Contextual Retrieval      | Chunk boundary in an embedding index    | Prepend 50–100 tokens of situating context            | Strong       |
| The "think" Tool          | Boundary between tool calls             | Insert an explicit reasoning slot mid-response        | Strong       |
| SWE-bench engineering     | Boundary between failure and fix        | Reproducer script as an observable intermediate state | Adjacent — intermediate-state observability rather than strict boundary restoration |
| Building Effective Agents | Boundary between generator and consumer | Evaluator pass that revisits output with criteria     | Strong       |

Our project's known pain point — subagent false positives at 38–50% (per the private memory entry `feedback_subagent_verification.md`) — may reflect this failure mode at the parent→subagent dispatch boundary: briefing context can be lost across the handoff, and findings are surfaced without a reconstruction step. The current evidence establishes the rate, not the dominant cause; whether boundary loss is causally responsible is unmeasured (see Unverified Assumptions #1). Earlier drafts presented the memory as a markdown-linked citation pointing to `../../CLAUDE.md`, which misrepresented a pointer-through-CLAUDE.md as a direct file link; corrected to plain prose attribution 2026-04-23 post-Codex review.

---

## Proposal A' — Subagent Briefing + Deterministic Post-check

### Background

Memory entry `feedback_subagent_verification.md` (2026-04-22) records that 38–50% of `/audit` subagent claims are false positives or hallucinations, and that claims are verified by re-reading cited files before inclusion. This practice is currently implicit — not codified in `plugin/skills/audit/SKILL.md`.

### Proposal

Two-part enhancement:

1. **Briefing at dispatch.** When a subagent is spawned, the dispatch message should explicitly carry:
   - The parent session's assumption (the *question being asked*)
   - The bounded scope (which files, which rule set)
   - The acceptance criteria for a valid finding (what makes a claim reportable)

2. **Deterministic post-check before surfacing.** Codify in SKILL.md that every subagent-originated finding must pass a deterministic check (e.g., re-read cited file, regex match, CI script invocation) before being listed. Implicit practice becomes explicit procedure.

### Source Evidence

- **Contextual Retrieval** (Anthropic) — *inspiring principle, not direct technique*. The article reports: "Contextual Embeddings reduced the top-20-chunk retrieval failure rate by 35% (5.7% → 3.7%)" and "Combining Contextual Embeddings and Contextual BM25 reduced the top-20-chunk retrieval failure rate by 49% (5.7% → 2.9%)" — with a further reduction to 67% when combined with reranking. The architectural pattern — restore context at the boundary — is portable. Note: we are not adopting the RAG technique, only the boundary-restoration *principle*.
- **Building Effective Agents** (Anthropic) — *cited pattern with explicit modification*: The Evaluator-Optimizer pattern is described as *"one LLM generates responses while another provides iterative feedback"*, suitable when *"clear evaluation criteria where iterative refinement adds measurable value"* exists. For our case, an LLM-plus-deterministic check is a tighter fit than strict LLM-vs-LLM evaluation — less cost, criteria are often verifiable. The article supports the principle of second-stage validation; the deterministic variant is our adaptation, not the article's prescription.

### Risks / Tradeoffs

- **Root cause uncertainty.** If false positives are driven by model-level hallucination rather than briefing gap, briefing enrichment has limited effect.
- **Token cost.** Every dispatch carries a longer briefing.
- **Criterion completeness.** Deterministic checks only work where the rule is checkable. For judgment-heavy findings ("is this finding worth surfacing?"), a second-stage LLM pass would still be required.

### Prerequisites

Before adopting, run a **two-stage causal sampling**:

**Stage 1 — hypothesis generation (n=5).** Pull 5 recent `/audit` runs where subagent findings were rejected as false positive. Classify each by cause:
- Briefing-gap (subagent lacked context the parent had)
- Model hallucination (subagent had sufficient context but fabricated)
- Criterion ambiguity (subagent read correctly but interpreted rule differently)
- Other

A 5-case sample is suitable for identifying *candidate* dominant causes only; it is not statistically sufficient for a gating decision (≥40% of 5 = 2 cases, well within chance variance). Earlier drafts proposed ≥40% as a decision threshold at n=5 — corrected 2026-04-23 post-Codex review.

**Stage 2 — decision gate (n≈15–20).** If Stage 1 suggests briefing-gap as a plausible dominant cause, collect a larger sample (target 15–20 cases). Adopt A' only if briefing-gap is materially common in the larger sample. If hallucination dominates at either stage, prioritize Proposal D instead.

### Confidence

**Medium-high**, conditional on the prerequisite sampling exercise.

---

## Proposal D — Think-tool-style Prompting in `/audit` SKILL.md

### Background

The "think" tool provides Claude an explicit reasoning slot between tool calls. It cannot be embedded directly into a SKILL.md (skills are markdown instructions, not MCP tool definitions). However, the *prompting pattern* that Anthropic reports as effective — *"list applicable rules, verify information collection, check policy compliance, and iterate over tool results"* — is portable as instructional text inside SKILL.md.

### Proposal

Add explicit reasoning checkpoints in `plugin/skills/audit/SKILL.md` at phase boundaries:

- **Before each phase**: the agent enumerates applicable rules (e.g., CLAUDE.md contribution rules, frontmatter parity rules, i18n parity rules) that are in scope for the phase.
- **After each phase**: the agent verifies which rules were actually checked versus which are still outstanding, and records any deferred items.

This turns the phase structure from implicit linear execution into explicit rule-indexed execution.

### Source Evidence

- **The "think" Tool** (Anthropic):
  - τ-Bench **Airline** domain: **54% relative improvement** (0.570 vs. 0.370 baseline with optimized prompting).
  - τ-Bench **Retail** domain: 0.812 pass¹ vs. 0.783 baseline.
  - **SWE-Bench**: 1.6% average improvement (*p* < .001).
  - Recommended for *"tool output analysis, policy-heavy environments, and sequential decision making"*.
- The `/audit` workflow matches the "policy-heavy + sequential" profile where the larger gains were measured.

### Risks / Tradeoffs

- The article explicitly warns the technique **does not help** in simple tasks or non-sequential tool calls. Adding prompting complexity where it doesn't fit can degrade baseline performance.
- SKILL.md body length grows. Repository convention (`CLAUDE.md` § "Contribution Rules") favors concise skill content; this tension must be resolved deliberately.
- The τ-Bench Airline 54% figure is from a specific benchmark; transfer to our internal `/audit` workflow is hypothesized, not measured.

### Prerequisites

Read current `plugin/skills/audit/SKILL.md` and identify which phases have multi-rule policy load worth explicit enumeration vs. which phases are near-trivial. Apply the pattern only to the former.

### Confidence

**Medium**. Higher fit than Pass 1 initially credited (the pattern transfers as prompt text, not as tool schema), but dependent on concrete phase structure.

---

## Proposal C' — Dual-layer SKILL Audit (Trigger + Usage)

### Background

Pass 1 of the review conflated two distinct surfaces: the frontmatter `description:` field and the SKILL.md body. Pass 2 correction:

- **Frontmatter `description:`** — a one-line **trigger**, read when Claude decides *whether* to invoke the skill.
- **SKILL.md body** — the **usage specification**, read when Claude decides *how* to behave once the skill is invoked.

A meaningful audit must address both layers.

### Proposal

Two-pass review of each skill under `plugin/skills/`:

1. **Trigger audit (frontmatter).**
   - Does `description:` specify bounded "use when …" signals?
   - Is trigger vocabulary consistent across the four skills (`/create`, `/audit`, `/secure`, `/optimize`)?
   - Are there known cases of over-triggering (invoked when not needed) or under-triggering (not invoked when needed)?

2. **Usage audit (body).**
   - Does the body embed interface-level error prevention (per SWE-bench principle), or rely on implicit convention?
   - Are irreversible actions guarded with explicit preconditions?
   - Does the body make the skill's assumptions explicit, so that an invocation under a wrong assumption is rejected rather than silently mis-executed?

### Source Evidence

- **SWE-bench Sonnet engineering** (Anthropic): two interface-level error-prevention choices from `str_replace_editor`. On ambiguous edits: "The replacement will only occur if there is exactly one match of `old_str`. If there are more or fewer matches, the model is shown an appropriate error message for it to retry." On path handling: the article describes how "sometimes models could mess up relative file paths after the agent had moved out of the root directory. To prevent this, we simply made the tool always require an absolute path." (The "anti-hallucination mechanism" label used in earlier drafts is our synthesis, not the article's phrasing — corrected 2026-04-23.) The principle: **push error prevention into the interface specification rather than catching errors after the fact.**
- **Building Effective Agents** (Anthropic): invokes an HCI/ACI analogy — "one rule of thumb is to think about how much effort goes into human-computer interfaces (HCI), and plan to invest just as much effort in creating good agent-computer interfaces (ACI)." The Appendix 2 heading "Prompt engineering your tools" reinforces that tool interface design deserves the same craft as overall prompts. (Earlier drafts compressed this into a single paraphrased quote — corrected 2026-04-23.)

### Risks / Tradeoffs

- Scope unknown until at least one skill is piloted.
- If current skills are already well-specified, yield is low.
- Over-tightening a trigger description lowers recall (skill not invoked when it should be).

### Prerequisites

Pilot the method on **one skill** first — recommend `/audit`, because it is the largest and the locus of known false-positive issues. Decide full rollout based on pilot findings.

### Confidence

**Medium**, pending pilot.

---

## Proposal B — "Agent Patterns" Guide (Deferred)

### Background

Building Effective Agents enumerates six-to-seven patterns (Augmented LLM, Prompt Chaining, Routing, Parallelization, Orchestrator-Workers, Evaluator-Optimizer, Autonomous Agents). Four recur in Claude Code plugin/skill design: Prompt Chaining, Routing, Orchestrator-Workers, Evaluator-Optimizer.

### Proposal

Add a new section in `docs/guides/advanced-features-guide.md` — or a new short guide — documenting the four relevant patterns, with this repository's own skills as worked examples.

### Source Evidence

- **Building Effective Agents** (Anthropic): enumerates patterns with use-case guidance.
- Project north star per memory `project_meta_system_vision.md`: "Claude Code configuration meta-system". Agent-pattern literacy directly serves this positioning.

### Risks / Tradeoffs

- Using our skills as examples requires first *verifying* which pattern each skill instantiates. That verification is itself Proposal C' output. B therefore depends on C' for factual grounding.
- `docs/guides/advanced-features-guide.md` is already near its ~200-line budget (CLAUDE.md § "Contribution Rules"). A new guide may be cleaner than expansion.
- Immediate feature ROI is low. Value is educational and positional.

### Prerequisites

Proposals A', D, and C' executed (or deliberately skipped) first. Pattern labels grounded in actual SKILL.md content rather than Pass 1 speculation.

### Confidence

**Low-medium**. Strategically valuable; tactically deferred.

---

## Contextual Retrieval — Direct Adoption Skipped

### Rationale

- No RAG system in this repository. No embedding or chunking pipeline exists or is planned.
- Total corpus size (skills, guides, templates, i18n mirrors) is plausibly under the 200K-token threshold cited by the article; the exact token count has not been measured. The article states: "If your knowledge base is smaller than 200,000 tokens (about 500 pages of material), you can just include the entire knowledge base in the prompt." (Prompt caching as the mechanism is discussed in an adjacent passage; earlier drafts of this document conflated the two paragraphs into a single quoted sentence — corrected 2026-04-23.)
- Users building RAG systems *using* our templates may benefit from the technique in their own projects, but that is a user-guide concern, not a repository change.

### Residual Insight

The architectural principle — **restore context at the boundary** — is absorbed into Proposal A' (subagent dispatch boundary). The retrieval-specific technique is not adopted.

---

## Unverified Assumptions (Honest Ledger)

This section exists so that a later reader can challenge the proposals by attacking their premises directly.

1. **False-positive root cause** (impacts A', D). The 38–50% false-positive rate is documented; its *cause distribution* is not. A' presumes briefing-gap as a dominant cause; D presumes model-reasoning as a dominant cause. Neither is measured.
2. **`/audit` internal structure** (impacts B). Whether `/audit` exhibits Orchestrator-Workers (dynamic decomposition) or Prompt Chaining (fixed phases) has not been verified against the actual SKILL.md. Pattern labels in this document are tentative.
3. **Current skill description quality** (impacts C'). The proposal presumes improvement is available. Pilot is required to confirm or refute.
4. **Benchmark transferability** (impacts D). τ-Bench Airline's 54% was on an airline customer-service benchmark. Whether the effect transfers linearly to a documentation-repository audit workflow is a hypothesis, not a measurement.
5. **Subjective ROI ranking** (impacts all). A' > D > C' > B reflects the author's estimate. A positioning-first ordering (B first) is defensible. A safety-first ordering (C' body audit first, to harden `/secure`) is also defensible.
6. **The "boundary information loss" unifying frame** is a useful synthesis but is not itself asserted by any single article. It is a pattern the author extracted across the four.

---

## Recommended Next Step

Before committing to any proposal, run the **two-stage causal sampling exercise** from Proposal A' (Prerequisites section above):

- **Stage 1 (n=5)** — classify 5 recent false-positive cases by cause (briefing-gap / model hallucination / criterion ambiguity / other) for hypothesis generation only; n=5 is not statistically sufficient for a gating decision.
- **Stage 2 (n≈15–20)** — if Stage 1 suggests briefing-gap as a plausible dominant cause, expand to 15–20 cases before using the distribution to gate A' vs D vs C'.

(Earlier drafts reverted to a single 5-case exercise at this location and treated its distribution as decision-enabling — reintroducing the same undersized-sample problem Proposal A' was corrected to avoid. Stale copy corrected 2026-04-23 post-Codex review.)

The distribution disambiguates which proposals are worth pursuing:

- Briefing-gap dominant → A' first.
- Hallucination dominant → A' value drops; prioritize D (the prompting pattern changes in-context reasoning).
- Criterion ambiguity dominant → prioritize C' (tighten the SKILL.md usage spec).

Any of these verdicts remains compatible with B being deferred.

---

## References

### External (primary source)

- Anthropic Engineering — *Contextual Retrieval*: https://www.anthropic.com/engineering/contextual-retrieval
- Anthropic Engineering — *Building Effective Agents*: https://www.anthropic.com/engineering/building-effective-agents
- Anthropic Engineering — *Raising the bar on SWE-bench Verified*: https://www.anthropic.com/engineering/swe-bench-sonnet
- Anthropic Engineering — *The "think" tool*: https://www.anthropic.com/engineering/claude-think-tool

### Internal (this repository)

- `CLAUDE.md` — § "Contribution Rules" (length budgets, frontmatter conventions)
- `plugin/skills/audit/SKILL.md` — subject of Proposals A', D, C' pilot
- `plugin/skills/create/SKILL.md`, `plugin/skills/secure/SKILL.md`, `plugin/skills/optimize/SKILL.md` — additional subjects of Proposal C'
- `docs/guides/advanced-features-guide.md` — candidate surface for Proposal B
- Memory entries referenced: `feedback_subagent_verification.md`, `project_meta_system_vision.md`, `feedback_no_per_stack_variants.md`, `feedback_doc_reframing.md`
