# Anthropic Engineering Insights — Applicability Review (Round 4)

**Status**: Draft (evaluation basis, not an approved change)
**Created**: 2026-04-22
**Last revised**: 2026-04-29 (post-R5 class-level provenance sweep at Loop 13; Tier 2 narrative paraphrase sweep at Loop 14)
**Scope**: Fourth review round covering five additional sources. Continues [Round 1](./anthropic-engineering-insights-review.md), [Round 2](./anthropic-engineering-insights-review-round-2.md), and [Round 3](./anthropic-engineering-insights-review-round-3.md).

---

## Purpose

This document captures proposals from the fourth batch of Anthropic engineering materials. Two observations about this round:

1. **Round 4 deepens Round 2, rather than opening a new axis.** Where Round 3 introduced "runtime scope limitation" as a new lifecycle stage, Round 4's contribution is to answer a question Round 2 raised but left abstract: *what makes a good verifier?* The star source (Demystifying Evals) provides concrete grader typology, YAML rubric schemas, and the pass@k / pass^k metric pair. These turn Round 2's Proposal A'-ev from a principle ("introduce LLM-as-judge rubric") into an executable specification.

2. **Two of five sources are explicitly skipped with recorded rationale.** AI-Resistant Technical Evaluations targets human hiring, not AI agent evaluation — a genuine domain mismatch. Building a C Compiler operates at a scale (16 parallel agents, $20K API cost) that does not transfer to our project; only its "oracle" vocabulary is absorbed into Proposal L. Recording these skips avoids future re-analysis thinking the sources were missed.

This document reflects the **converged state after twelve self-review loops**. Corrections are recorded in the "Convergence Audit Trail" section. No change is authorized by this document.

---

## Source Material

Five sources. Star source marked; skipped sources with rationale recorded below.

1. **Demystifying evals for AI agents** (★ star source) — <https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents>
2. Advanced tool use — <https://www.anthropic.com/engineering/advanced-tool-use>
3. Effective harnesses for long-running agents — <https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents>
4. AI-resistant technical evaluations — <https://www.anthropic.com/engineering/AI-resistant-technical-evaluations> (**skipped**: hiring domain, not AI agent evaluation)
5. Building a C compiler with parallel Claude agents — <https://www.anthropic.com/engineering/building-c-compiler> (**partial skip**: main content is scale-mismatched; only the "oracle" vocabulary is absorbed)

---

## TL;DR

| ID      | Proposal                                                                              | Confidence      | Effort       | Relation to prior rounds |
|---------|---------------------------------------------------------------------------------------|-----------------|--------------|--------------------------|
| K       | Materialize R2 A'-ev with YAML schema, grader types, tier split, "Unknown", pass@k/^k | Medium-high     | Medium       | Extends R2 A'-ev         |
| L       | Add "oracle" vocabulary to R2 A'-rt (CI scripts as oracle)                            | Medium          | Very low     | Extends R2 A'-rt         |
| O       | Short MCP-guide section on Programmatic Tool Calling                                  | Low             | Low          | New (R3 H neighbor)      |
| B-cond  | If R2 B is pursued, add harness-patterns subsection                                   | Low             | Low          | Extends R2 B, conditional |
| —       | Article 4 (AI-resistant evals): main content                                          | **Skip**        | —            | Domain mismatch          |
| —       | Article 5 (C compiler): main content                                                  | **Skip**        | —            | Scale mismatch; oracle absorbed into L |

Approximate priority: **K > L > O > B-cond**.

---

## Cross-Cutting Themes

### Round 4 Pattern: "Verifier quality as upper bound on agent quality"

Three of the five sources converge on one claim:

> **The quality of the verifier is the upper bound on the quality of the agent. Improving the agent beyond what the verifier can distinguish produces no measurable gain.**

| Source | Manifestation | Fit |
|---|---|---|
| Building a C compiler | *"So it's important that the task verifier is nearly perfect, otherwise Claude will solve the wrong problem."* | Strong |
| Effective harnesses | Feature list (JSON) + smoke test + git log as the harness's verification substrate | Strong |
| Demystifying evals | Bad graders let agents "easily 'cheat' the eval" — grader design is first-order (article: "The agent shouldn't be able to easily 'cheat' the eval") | Strong |
| Advanced tool use | Programmatic Tool Calling optimizes inflow, not verification (adjacent, not same) | Adjacent |
| AI-resistant evals | Evaluation design as anti-gaming (adjacent direction: resist gaming, not raise verifier quality) | Adjacent |

Three strong matches to the central claim; two adjacent matches. Treated as a **3-source pattern** with neighbors.

### Relation to Rounds 1–3

- **Round 1** — restore context at boundaries (boundary information loss)
- **Round 2** — verify output against self-recovery masking (plausible output masks defects)
- **Round 3** — limit what loads at runtime (deliberate scope limitation)
- **Round 4** — raise verifier quality first (verifier quality is the upper bound)

Round 4's contribution is not a new lifecycle stage but a **depth cut into Round 2's stage**: R2 said "verify"; R4 says "here is what makes verification work."

---

## Proposals

### K — Materialize R2 A'-ev with Concrete Schema and Metrics

#### Background

Round 2 Proposal A'-ev introduced LLM-as-judge in the `test/` framework with a redefined five-metric rubric. The proposal was confidence Medium, held back partly because the rubric was described at concept level, not schema level. Demystifying Evals provides concrete YAML rubric structures, explicit grader typology, calibration techniques, and metric pairs — enough to turn A'-ev into an executable specification.

#### Proposal

Five specific refinements to A'-ev:

**1. Adopt YAML rubric schema as the `test/` configuration format.**
The article presents two schemas verbatim; the coding-agent schema fits our context:

```yaml
graders:
  - type: deterministic_tests   # CI scripts (.github/scripts/check-*.py)
  - type: llm_rubric            # our 5-rubric from R2 A'-ev (redefined)
  - type: static_analysis       # linting where applicable
  - type: state_check           # file state assertions
  - type: tool_calls            # expected Read/Grep/Glob invocation patterns
```

**2. Use the three canonical grader types (per article) with our YAML sub-types mapped underneath.**

The Demystifying Evals article identifies three canonical grader categories (code-based / model-based / human-based). Our YAML in item 1 above enumerates **five sub-types**, which are all instances of the first two canonical categories:

- **Code-based (deterministic)** — YAML sub-types: `deterministic_tests`, `static_analysis`, `state_check`, `tool_calls`. Reuse R2 A'-rt's post-check for rules CI can verify.
- **Model-based (LLM-as-judge)** — YAML sub-type: `llm_rubric`. Uses the redefined five-rubric for subjective findings.
- **Human-based**: periodic spot-check against LLM-judge output for calibration. (Not represented in YAML because it is an evaluation-time process, not a runtime grader.)

**Expansion order**: start with `deterministic_tests` + `llm_rubric` — the two highest-leverage sub-types, one per code/model category. Add the other code-based sub-types (`static_analysis`, `state_check`, `tool_calls`) as specific failure modes warrant. Human-based review remains a complementary, out-of-band calibration step in this Round 4 baseline. (Prior phrasing "must precede trust in llm_rubric output" contradicted the pre-patch rollout model — corrected 2026-04-23 post-Codex review. Round 4 state here preserves the pre-K-ref baseline per R5's Document Handling principle; no forward reference to K-ref is inserted.)

Earlier drafts said "use all three grader types explicitly" while the YAML showed five sub-types and the Risks section said "start with two" — a 3-layer inconsistency. Corrected 2026-04-23 post-Codex review into the canonical-type / YAML-sub-type hierarchy above.

The article frames these as complementary: *"LLM-as-judge graders should be closely calibrated with human experts to gain confidence that there is little divergence between the human grading and model grading"* (earlier drafts truncated the "that there is little divergence..." tail; restored to literal 2026-04-29 post-Tier 2 sweep)

**3. Split evals into Capability vs Regression tiers.**

The article discusses both anchors independently — "20-50 simple tasks" as the starting scope for agent evaluations, and regression evals that have "nearly 100% pass rate" on prior-resolved issues. We synthesize these into an explicit two-tier framework (the pairing is our structural synthesis — the article does not present them as a single framework):

- **Capability tier**: 20–50 tasks derived from real failure cases, starting at low pass rate, targets the skill's weakest areas. Graduates to regression as the skill saturates.
- **Regression tier**: near-100% baseline, catches backsliding.

Both tiers are live; graduation is explicit.

**4. Allow "Unknown" in judge responses.**
The article recommends: *"To avoid hallucinations, give the LLM a way out, like providing an instruction to return 'Unknown' when it doesn't have enough information"* (Demystifying Evals). Our judge prompt should include an equivalent affordance — e.g., "If information is insufficient to grade this assertion, respond Unknown" — as a specific technique to reduce hallucination in LLM-as-judge. (Earlier drafts dropped the article's lead-in "To avoid hallucinations,"; restored 2026-04-29 post-R5 sweep.)

**5. Introduce pass@k and pass^k metrics at the `test/` framework level.**
- `pass@k` — probability `/audit` catches the core issue in at least one of k runs (single-success mode)
- `pass^k` — probability `/audit` succeeds on all k independent trials for the same fixture (consistency-under-success mode — an agent that repeats the *same wrong answer* across k runs is perfectly consistent but still scores 0 on pass^k, so "consistency" alone is not the right gloss). (Earlier drafts glossed this as "produces consistent findings"; corrected 2026-04-23 post-Codex review to match the article's literal definition.)

The article frames these as complementary: *"By k=10, they tell opposite stories: pass@k approaches 100% while pass^k falls to 0%"*; both are needed. (Earlier drafts italicized a paraphrased gloss "tell opposite stories about consistency requirements" that does not appear in the source; replaced with the literal sentence 2026-04-29 post-R5 sweep.)

**Scope note**: pass@k / pass^k apply to how we evaluate `/audit` across fixtures and reruns in `test/`, not within a single `/audit` execution.

#### Source Evidence

- *"LLM-as-judge graders should be closely calibrated with human experts to gain confidence that there is little divergence between the human grading and model grading"* (Demystifying Evals; earlier drafts truncated the "that there is..." tail — restored 2026-04-29 post-Tier 2 sweep)
- Two YAML rubric schemas presented literally in the article (coding-agent and conversational-agent variants)
- `pass@k` / `pass^k` definitions and framing — literal in article
- Capability vs Regression tier distinction — literal in article
- "Unknown" response technique — literal in article
- Three grader types (code, model, human) and their tradeoffs — structured in article

#### Risks / Tradeoffs

- `test/` is gitignored and internal to the repository. Work here does not ship to external users; value is calibration of our own development process.
- Judge calibration requires human ground truth. A statistically useful ground-truth set targets 20–50 manually-scored historical audit outputs spanning the main failure modes; earlier drafts budgeted "5–10" which functions only as an initial smoke test, not as calibration for a trust gate. Building either set is non-trivial and has not been costed. (Sample-size target updated 2026-04-23 post-Codex review.)
- pass^k is noise-dominated at small k. Small fixture sets may not produce a statistically useful pass^k.
- Grader proliferation (five YAML sub-types per eval) adds orchestration complexity; the expansion order in item 2 above (start with `deterministic_tests` + `llm_rubric`, add others as failure modes warrant) mitigates this.

#### Prerequisites

1. Read the current `test/` rubric configuration **if present in the local checkout** (per `CLAUDE.md`, `test/` is gitignored and local-only) to decide whether the YAML schema replaces or supplements existing structure. If `test/` is absent in the executing environment, mark Proposal K as requiring access to the local eval workspace before this decision can be made; `.github/scripts/*.py` is the CI-visible surface but does not contain the rubric.
2. Build a 5–10 item ground-truth set for judge calibration (manual scoring)
3. Pilot the YAML schema on one fixture before full conversion
4. Measure variance of pass^k at a realistic k (3, 5) before committing to it as a primary metric

#### Confidence

**Medium-high**. The article's concrete templates resolve the abstractness that held A'-ev at Medium in Round 2. Remaining uncertainty is calibration cost.

---

### L — Add "Oracle" Vocabulary to R2 A'-rt

#### Background

Round 2 Proposal A'-rt specified a deterministic post-check where subagent findings are validated by re-reading cited files before being surfaced. The C compiler article names the same pattern: *"So it's important that the task verifier is nearly perfect, otherwise Claude will solve the wrong problem"*, with GCC serving as a known-good oracle validating their new compiler.

For `/audit`, the oracle is our CI scripts (`.github/scripts/check-*.py`) where they cover the rule being checked. This proposal makes the vocabulary explicit.

#### Proposal

1. Rename R2 A'-rt's "deterministic post-check" step to "Oracle check" in the SKILL.md text.
2. Add an explicit rule: *"Where a CI script (oracle) can decide the finding, the subagent's output is a hypothesis; the oracle's output is authoritative. A finding is surfaced only when hypothesis and oracle agree — or, when they disagree, the disagreement itself is surfaced for human review."*
3. Where no oracle exists (subjective judgment rules), fall back to the LLM-judge layer from Proposal K.
4. Produce a short oracle-coverage map: which CI script covers which rule. This reveals the effective upper bound of `/audit`'s deterministic reliability.

#### Source Evidence

- *"So it's important that the task verifier is nearly perfect, otherwise Claude will solve the wrong problem."* (C compiler article)
- Oracle-based debugging pattern (GCC as known-good compiler) — described in C compiler article
- Demystifying Evals' first-order treatment of graders supports the same principle in a different vocabulary

#### Risks / Tradeoffs

- Naming alone changes nothing substantive. The real improvement comes from producing the oracle-coverage map and identifying rules without oracle coverage — those are the audit's true weak points.
- Disagreement between hypothesis and oracle is rarer in practice than either-alone output; dedicating a surfacing path for disagreements adds UI surface.

#### Prerequisites

- Read `plugin/skills/audit/SKILL.md`
- List `.github/scripts/check-*.py` and map each to the rules it verifies

#### Confidence

**Medium**. Vocabulary is cleanly aligned with existing practice; the substantive win depends on oracle-coverage mapping, which is the actual new work.

---

### O — MCP Guide: Short Section on Programmatic Tool Calling

#### Background

Advanced Tool Use describes a pattern where Claude writes code to orchestrate multiple tool calls, controlling what enters its context window. The article cites *"Claude writes code that calls multiple tools, processes their outputs, and controls what information actually enters its context window"* and a 37% token-reduction example. The pattern applies narrowly: large parallel tool invocation, heavy intermediate data, complex control flow. It is adjacent in audience to Round 3's Proposal H (code-execution MCP paragraph).

#### Proposal

Add a short section to `docs/guides/mcp-guide.md` — parallel to, and possibly consolidated with, R3 Proposal H — titled something like *"When to consider Programmatic Tool Calling"*.

Content: one paragraph on the pattern, one on applicability conditions, one on the anti-pattern list. The article's "Less beneficial when" trio for PTC: (a) making simple single-tool invocations, (b) working on tasks where Claude should see and reason about all intermediate results, (c) running quick lookups with small responses. Note: the "fewer than ten tools" threshold cited in even earlier drafts of this proposal belongs to the article's **Tool Search Tool** section, not Programmatic Tool Calling — do not conflate. (First corrected 2026-04-23 for Tool-Search-Tool conflation; refined 2026-04-23 post-Codex review to add item (b), which was still missing from the intermediate correction.)

#### Source Evidence

- Pattern description and 37% token reduction example — Advanced Tool Use
- Anti-patterns listed literally in the article

#### Risks / Tradeoffs

- Narrow audience overlap with R3 H. These two sections may benefit from consolidation into one "Advanced MCP patterns" subsection rather than two separate insertions.
- Single-example numbers (37%) can be misread as general expectations — cite with explicit qualification.

#### Prerequisites

- Read current `docs/guides/mcp-guide.md` (shared prerequisite with R3 H)
- Decide whether O and H are merged or kept separate

#### Confidence

**Low**. Correct inclusion criterion; small audience.

---

### B-cond — Harness Subsection in R2 B (Conditional)

#### Background

The Effective Harnesses article introduces vocabulary (harness / feature list / progress file / init script / session initialization checklist / failure modes table) that naturally extends R2's deferred Proposal B (Agent Patterns guide). Since B is itself conditional on prior proposals delivering verified pattern-to-skill mappings, this proposal is doubly conditional.

#### Proposal

If R2 Proposal B is pursued, add a "Long-running harness patterns" subsection drawing from Effective Harnesses. Key content:

- Harness vs model distinction
- Feature-list JSON as a verification substrate
- Session initialization checklist pattern
- Four failure modes table — article's actual names: "Claude declares victory on the entire project too early" / "Claude leaves the environment in a state with bugs or undocumented progress" / "Claude marks features as done prematurely" / "Claude has to spend time figuring out how to run the app" (earlier drafts paraphrased these inaccurately as "premature completion / half-implemented / undocumented bugs / inappropriate marking" — corrected 2026-04-29 post-R5 sweep)

#### Source Evidence

- *"Inspiration for these practices came from knowing what effective software engineers do every day"* (Effective Harnesses)
- Failure-modes table presented literally in the article

#### Risks / Tradeoffs

- Doubly conditional (B must be pursued; harness section must be scoped to avoid overlap with the Agent Patterns core)
- Our repository teaches single-session Claude Code skills, not multi-window agent engineering; a harness section may pull the guide's scope

#### Prerequisites

- R2 Proposal B must be activated first
- Scope decision: include long-running patterns in B, or split into a separate advanced guide?

#### Confidence

**Low (conditional)**.

---

### Explicitly Skipped

#### AI-Resistant Technical Evaluations (Article 4)

The article targets human technical interviews where candidates may use AI assistance. Earlier drafts described article principles as "exploiting distribution gaps, requiring multi-stage reasoning with feedback, and building tools during assessment" — none of these phrases appear verbatim in the article, and the closest matches are scattered concepts not stated as principles. The article's actual stated design goals are "Representative of real work", "High signal", "No specific domain knowledge", and "Fun" (already corrected at line 276 below in Loop 13). The subject matter is **hiring**, not **agent evaluation infrastructure**. (Three-principle fabrication corrected 2026-04-29 post-Tier 2 sweep.)

The article's actual design goals — *"Representative of real work"*, *"High signal"*, *"No specific domain knowledge"*, *"Fun"* — apply to human take-home tests, not to AI agent evaluation. The closest transferable framing is hiring-context advice: *"Longer-horizon problems are harder for AI to solve completely, so candidates can use AI tools (as they would on the job) while still needing to demonstrate their own skills."* This generates no proposal for our project. (Earlier drafts attributed an italicized "evaluations should reward novel reasoning, not pattern matching" meta-principle to this article; that phrase does not appear in the source — corrected 2026-04-29 post-R5 sweep.) No concrete action.

Skip with recorded rationale.

#### Building a C Compiler with Parallel Claude Agents (Article 5, main content)

The project uses 16 Claude Opus 4.6 instances over 2,000 sessions producing 100,000 lines of code at ~$20,000 API cost. Our project operates at a categorically different scale (single-session skills, no parallel agent coordination, no API-cost budget scope).

The article describes transferable patterns using its own phrasing — "Parallelism also enables specialization" (multi-agent role assignment), a "synchronization algorithm" using filesystem locks ("Claude takes a 'lock' on a task by writing a text file to current_tasks/"), and the centrality of high-quality task verifiers (the article's section heading is "Write extremely high-quality tests"). All three require infrastructure we do not have. The only element absorbed is the **oracle vocabulary**, which folds into Proposal L. (Earlier drafts compressed these into "parallel specialization / lock-file synchronization / task-verifier primacy" — three coinages presented as if article phrases; replaced with article's actual wording 2026-04-29 post-Tier 2 sweep.)

Skip main content with recorded rationale.

---

## Convergence Audit Trail

| Loop | Target                                | Findings | Notable corrections |
|------|---------------------------------------|----------|---------------------|
| 1    | Initial extraction from 5 sources     | —        | N/A |
| 2    | Critique of Loop 1                    | 4        | ① Advanced Tool Use: skip confirmed; ② Harness "medium applicability" overstated — 75% overlap with R2 C'/D/F; ③ Demystifying Evals refinements: weekly transcripts is operational, not proposal; ④ AI-resistant evals: domain-mismatch skip confirmed |
| 3    | Critique of Loop 2                    | 3        | ① Harness failure-modes overlap quantified at 75%; ② pass@k/pass^k applicability requires specifics, not generic adoption; ③ Oracle pattern is already implicit in R2 A'-rt |
| 4    | Critique of Loop 3                    | 2        | ① Loop 3 under-claimed harness vocabulary value for re-reading /audit through its lens; ② pass@k and pass^k both apply but measure opposite things |
| 5    | Critique of Loop 4                    | 1        | Harness failure-modes proposal dropped as standalone — absorbed as sub-items where they overlap R2 C'/D/F |
| 6    | Critique of Loop 5                    | 1        | Oracle proposal dropped as standalone — folded into R2 A'-rt as vocabulary refinement (became Proposal L) |
| 7    | Citation / provenance sweep           | 0        | All quoted phrases verified literal against fetch output |
| 8    | Proposal derivation                   | —        | Four proposals identified (K, L, O, B-cond) |
| 9    | Proposal calibration                  | 1        | K priority "High" overstated — test/ is gitignored internal; Medium-high is accurate |
| 10   | Scope correction on pass@k/pass^k     | 1        | Metrics apply at `test/` framework level across fixtures, not within a single /audit execution |
| 11   | Verification of Loop 10               | 0        | Scope correction stands |
| 12   | Final over/under claim sweep          | 0        | No new corrections |
| 13   | Post-R5 class-level provenance sweep  | 5        | Loop 7 had declared "All quoted phrases verified literal"; rigorous class-level sweep against fresh WebFetch output finds: (a) line 131 italic *"tell opposite stories about consistency requirements"* — paraphrased gloss not in article; replaced with literal *"By k=10, they tell opposite stories: pass@k approaches 100% while pass^k falls to 0%"*; (b) line 247 (B-cond) failure-mode names did not match article's actual four modes — corrected to article's verbatim names ("declares victory on the entire project too early" / "leaves the environment in a state with bugs or undocumented progress" / "marks features as done prematurely" / "has to spend time figuring out how to run the app"); (c) line 276 (AI-Resistant Evals skip) italic *"evaluations should reward novel reasoning, not pattern matching"* was fabricated — replaced with article's actual design goals ("Representative of real work" / "High signal" / "No specific domain knowledge" / "Fun") plus the verbatim hiring-context closest-fit framing; (d) lines 58, 168, 181 italic *"The task verifier is nearly perfect..."* truncated article's lead-in "So it's important that" — extended to literal across all three sites; (e) line 125 italic "give the LLM a way out..." dropped article's lead-in "To avoid hallucinations," — extended to literal. All five corrected in-place (2026-04-29); proposal substance unchanged. This is the third Round in which a Loop 7 "all verified" declaration was overturned by a later class-level sweep (R2 Loop 9, R3 Loop 11, R4 Loop 13) — the recurrence is itself the methodological finding: single-instance verification under "verified literal" framing systematically misses the class. |

| 14   | Tier 2 narrative paraphrase sweep     | 4        | Loop 13 (Tier 1 sweep) extended to Tier 2. Findings: (a) line 113 + line 137 italic *"LLM-as-judge graders should be closely calibrated with human experts to gain confidence."* truncated article's tail "that there is little divergence between the human grading and model grading" — restored at both sites; (b) line 274 (AI-Resistant Evals skip) narrative listed three "principles" — "exploiting distribution gaps, requiring multi-stage reasoning with feedback, building tools during assessment" — none verbatim; closest article concepts are scattered references, not stated principles. Replaced with explicit acknowledgment + reference to article's actual design goals (already corrected at line 276 in Loop 13); (c) line 282-285 (C Compiler skip) narrative listed three patterns — "parallel specialization, lock-file synchronization, task-verifier primacy" — none verbatim. Replaced with article's actual wording. Tier 2 sweep also confirmed: 2 YAML schemas verbatim, 5 grader sub-types match article exactly, oracle vocabulary verbatim, three grader categories ("code-based, model-based, and human") verbatim, "Capability or 'quality' evals" verbatim (R4's "tier" framing already self-acknowledged as our synthesis at line 117). All four corrected in-place (2026-04-29). |

**Convergence re-validated at Loop 14** after Tier 2 sweep.

---

## Unverified Assumptions (Cumulative — Rounds 1 + 2 + 3 + 4)

Items added in Round 4 marked with ⚡⚡⚡. Round 3 items marked ⚡⚡ and Round 2 items ⚡ are retained from prior documents.

**Carried from Rounds 1–3:**

1. False-positive root cause distribution (impacts R2 A'-rt)
2. Current `/audit` structural pattern — Orchestrator-Workers vs Prompt Chaining
3. Skill description quality (impacts R2 C')
4. External-benchmark transferability
5. ⚡ "Recovery Masking" term provenance
6. ⚡ LLM-as-judge runtime applicability
7. ⚡ Parity drift magnitude vs Best Practices canonical docs
8. ⚡ R2 cross-article synthesis strength (plausible output — 2-source pattern)
9. ⚡⚡ Progressive Disclosure teaching presence in our guides
10. ⚡⚡ Current sandboxing coverage in guides / templates / `/secure`
11. ⚡⚡ Official sandboxing docs content
12. ⚡⚡ 84% permission-prompt reduction transferability
13. ⚡⚡ 98.7% code-execution savings generalizability
14. ⚡⚡ Intra-phase note-taking necessity in `/audit`

**Added in Round 4:**

15. ⚡⚡⚡ **Current `test/` rubric structure** — K proposes YAML schema adoption; whether this replaces or supplements existing config depends on what is currently there
16. ⚡⚡⚡ **Judge calibration cost realism** — building a 5–10 item human ground-truth set is non-trivial work; whether its cost is recoverable from judge reliability gain is unverified
17. ⚡⚡⚡ **pass^k statistical validity at our fixture scale** — small k values dominate with noise; the minimum useful k for our fixture count is unmeasured
18. ⚡⚡⚡ **Oracle coverage upper bound** — CI scripts (`.github/scripts/check-*.py`) verify some subset of `/audit` rules; the coverage percentage determines the upper bound of Proposal L's substantive benefit, and has not been mapped

### Cross-Cutting Meta-Principle Surfaced in Rounds 2 + 4

From Round 2 (plausible-output masking) + Round 4 (verifier as upper bound):

> Verification infrastructure quality is a load-bearing constraint on agent reliability. Investment in agent capability past what the verifier can distinguish produces no measurable gain.

Applied to our project: investing in `/audit` capability before `test/` rubric + CI oracle quality produces diminishing returns. This is a strategic prioritization implication, not itself a proposal.

---

## Recommended Next Step

Round 4 proposals share prerequisites with earlier rounds. The most efficient path:

| Single Read / mapping action | Unlocks |
|-------------------------------|---------|
| `plugin/skills/audit/SKILL.md` | R2 A'-rt, C', D, F; R3 F-ext; R4 L |
| `docs/guides/claude-md-guide.md` | R2 E; R3 J |
| `templates/starter/CLAUDE.md`, `templates/advanced/CLAUDE.md` | R2 E |
| Current `test/` rubric config (local-only per CLAUDE.md; blocked if absent in checkout) | R4 K |
| `.github/scripts/check-*.py` listing → rule coverage map | R4 L |
| `docs/guides/mcp-guide.md` | R3 H; R4 O |
| 20–50 historical `/audit` outputs with manual scoring (5–10 = smoke-test size only; not calibration-grade) | R4 K (calibration ground truth) |

After this consolidated Read sweep plus one small dataset-construction task, most proposals across all four rounds move from hypothesis to actionable diff plans.

A defensible lighter first step: **K alone**, because it delivers the largest reframe (A'-ev going from abstract to concrete) with scope contained to the `test/` framework, which does not ship.

---

## References

### External (primary sources)

- Anthropic Engineering — *Demystifying evals for AI agents*: <https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents>
- Anthropic Engineering — *Advanced tool use*: <https://www.anthropic.com/engineering/advanced-tool-use>
- Anthropic Engineering — *Effective harnesses for long-running agents*: <https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents>
- Anthropic Engineering — *AI-resistant technical evaluations*: <https://www.anthropic.com/engineering/AI-resistant-technical-evaluations> (skipped — hiring domain)
- Anthropic Engineering — *Building a C compiler with parallel Claude agents*: <https://www.anthropic.com/engineering/building-c-compiler> (partial skip — scale mismatch; oracle vocabulary absorbed into L)

### Internal (this repository)

- [Round 1 plan: `anthropic-engineering-insights-review.md`](./anthropic-engineering-insights-review.md) — Contextual Retrieval, Building Effective Agents, SWE-bench, Think Tool
- [Round 2 plan: `anthropic-engineering-insights-review-round-2.md`](./anthropic-engineering-insights-review-round-2.md) — Best Practices, Multi-Agent Research System, Desktop Extensions, Writing Tools, Postmortem
- [Round 3 plan: `anthropic-engineering-insights-review-round-3.md`](./anthropic-engineering-insights-review-round-3.md) — Agent Skills, Context Engineering, Sandboxing, Code Execution with MCP
- `plugin/skills/audit/SKILL.md` — subject of L (and R2 A'-rt, C', D, F; R3 F-ext)
- `test/` eval framework — subject of K (and R2 A'-ev)
- `.github/scripts/check-*.py` — oracle candidates for L
- `docs/guides/mcp-guide.md` — subject of O (and R3 H)
- `CLAUDE.md` § "Contribution Rules"
- Memory entries referenced: `feedback_subagent_verification.md`, `project_meta_system_vision.md`, `feedback_plans_scope.md`
