# Anthropic Engineering Insights — Applicability Review (Round 2)

**Status**: Draft (evaluation basis, not an approved change)
**Created**: 2026-04-22
**Last revised**: 2026-04-29 (Tier 2 narrative paraphrase sweep across Loops 10–11; previous 2026-04-22 calibrations recorded as Loop 9)
**Scope**: Second review round covering five additional sources. Continues [Round 1](./anthropic-engineering-insights-review.md), which remains authoritative for its four sources.

---

## Purpose

This document captures proposals derived from a second batch of Anthropic materials, with a deliberate expansion in scope: one of the five sources is the **canonical Claude Code Best Practices documentation**, which functions as a *parity target* rather than a mere source of ideas — drift between canonical docs and this repository's teaching content is a direct teaching loss.

This document reflects the **converged state after eight self-review loops**. Corrections discovered during the loops are recorded in the "Convergence Audit Trail" section below so future reviewers can assess how the proposals were calibrated. As with Round 1, no change is authorized by this document; it exists as a decision basis.

---

## Source Material

Five sources in this round. One is canonical documentation (binding for our teaching content), four are engineering posts (principle-level guidance).

1. **Claude Code Best Practices** (canonical docs, parity target) — <https://code.claude.com/docs/en/best-practices>
2. How we built our multi-agent research system — <https://www.anthropic.com/engineering/multi-agent-research-system>
3. Desktop Extensions — <https://www.anthropic.com/engineering/desktop-extensions>
4. Writing tools for agents — <https://www.anthropic.com/engineering/writing-tools-for-agents>
5. A postmortem of three recent issues — <https://www.anthropic.com/engineering/a-postmortem-of-three-recent-issues>

---

## TL;DR

| ID    | Proposal                                                          | Confidence        | Effort       | Relation to Round 1    |
|-------|-------------------------------------------------------------------|-------------------|--------------|------------------------|
| E     | Best Practices parity audit of our teaching content               | Medium-high       | Low-medium   | New                    |
| A'-rt | Subagent runtime briefing refinement (4-component structure)      | Medium-high       | Medium       | Refines Round 1 A'     |
| A'-ev | LLM-as-judge rubric in `test/` framework                          | Medium            | Medium       | New (layer split from A') |
| C'    | Dual-layer SKILL audit (scope-reduced)                            | Medium            | Medium       | Refines Round 1 C'     |
| D     | Think-tool-style prompting in /audit                              | Medium            | Low-medium   | Unchanged from Round 1 |
| F     | Phase-boundary contract check (renamed)                           | Low-medium        | Medium       | Renamed from Round 1 F |
| B     | "Agent Patterns" guide                                            | Low-medium        | Medium-high  | Deferred from Round 1  |
| —     | DXT mention in MCP guide                                          | **Skipped**       | —            | New, scope-conditional |

Approximate priority: **E ≈ A'-rt > A'-ev ≈ C' > D > F > B**.

---

## Cross-Cutting Themes

### Round 2 Pattern: "Plausible output masks real defects"

A recurrent motif across Round 2 sources: Claude produces output that *looks* right, and downstream checks fail to detect when it isn't. The pattern is strong in two sources, partial in a third, and a stretch in the fourth — treated here as a **2-source pattern**, not a universal cross-cut.

| Source                   | Manifestation                                                                                                        | Fit       |
|--------------------------|----------------------------------------------------------------------------------------------------------------------|-----------|
| Best Practices           | "Trust-then-verify gap: Claude produces a plausible-looking implementation that doesn't handle edge cases"           | Strong    |
| Postmortem (three issues)| "Claude often recovers well from isolated mistakes" — masks degradation at aggregate                                  | Strong    |
| Writing Tools for Agents | cryptic identifiers degrade precision (our paraphrase — the article discusses resolving UUIDs and returning high-signal information, but does not use the phrase "agents hallucinate more with cryptic IDs") | Partial   |
| Multi-Agent Research     | "scouring the web endlessly for nonexistent sources" — plausible activity without yield                              | Weak      |

### Relation to Round 1

Round 1's unifying theme was **"boundary information loss"** (chunk boundary in RAG, subagent dispatch boundary, tool-call boundary, generator-consumer boundary). Round 2's pattern is **logically downstream** (our synthesis across rounds; no single article asserts this chain):

> Information lost at a boundary → subsequent agent generates plausible-but-wrong output → self-recovery masks the defect from evaluators.

Taken together: **restore context at boundaries (Round 1)** *and* **verify output with mechanisms that cannot be masked by self-recovery (Round 2)**.

---

## Proposals

### E — Best Practices Parity Audit

#### Background

Claude Code Best Practices is the canonical documentation our repository exists to teach. Unlike engineering blog posts (principle-level, may or may not apply), canonical docs are binding for teaching content: any drift becomes teaching loss for downstream users.

#### Proposal

Perform a parity audit against the canonical document. The checklist below covers CLAUDE.md authoring, skill authoring, and session-management vocabulary — so the audit target set spans multiple guides:

**Primary targets** (CLAUDE.md scope — items 1–5 of checklist):
- `docs/guides/claude-md-guide.md`
- `templates/starter/CLAUDE.md`
- `templates/advanced/CLAUDE.md`

**Secondary targets** (for checklist items outside CLAUDE.md scope — items 6–8):
- `docs/guides/advanced-features-guide.md` — skill authoring items (e.g., `disable-model-invocation: true` is already documented at L163)
- `docs/guides/effective-usage-guide.md` — session-management items (`/rewind` / checkpointing vocabulary, confirmed present at L54–55). The Writer/Reviewer parallel-session pattern named in checklist item 7 is **not currently documented** in any guide under `docs/guides/` — its audit answer should be recorded as a gap rather than as coverage from this file. (Earlier drafts listed Writer/Reviewer as a covered item here; corrected 2026-04-23 post-Codex review after repo-wide grep confirmed absence.)

Earlier drafts restricted the target set to three CLAUDE.md-scoped files while including skills- and session-management items in the checklist — a scope/content mismatch that made items 6–8 unanchored. Corrected 2026-04-23 post-Codex review.

Checklist, derived directly from the canonical document's prescriptions:

1. **Verification-first framing** — is verification positioned as the highest-leverage practice, per the canonical tip *"This is the single highest-leverage thing you can do"*?
2. **Include/exclude table format** — adopted for CLAUDE.md content guidance?
3. **Pruning meta-rule present** — *"For each line, ask: Would removing this cause Claude to make mistakes? If not, cut it"*?
4. **`@path/to/import` syntax** — demonstrated in at least one example?
5. **Common failure patterns section** — covers all five canonical items (article's actual names): kitchen sink session / correcting over and over / over-specified CLAUDE.md / trust-then-verify gap / infinite exploration? (Earlier drafts paraphrased "Correcting over and over" as "repeated corrections"; corrected to article's actual name 2026-04-29 post-Tier 2 sweep.)
6. **`disable-model-invocation: true`** — documented for skills whose workflows have side effects and should be manually triggered?
7. **Writer/Reviewer parallel-session pattern** — described in advanced guides?
8. **Checkpointing / `/rewind` vocabulary** — current and accurate?

#### Source Evidence

- *"Give Claude a way to verify its work ... This is the single highest-leverage thing you can do."* (Best Practices)
- *"CLAUDE.md is loaded every session, so only include things that apply broadly ... Would removing this cause Claude to make mistakes?"* (Best Practices)
- *"Use `disable-model-invocation: true` for workflows with side effects that you want to trigger manually"* (Best Practices, Create skills section; earlier drafts dropped the article's "Use" prefix — restored 2026-04-29 post-Tier 2 sweep iteration 2)
- Common failure patterns — five items listed verbatim in Best Practices

#### Risks / Tradeoffs

- If current content is already well-aligned, audit yields few changes. The audit itself is cheap; a null finding is a successful outcome.
- Parity means matching **intent and coverage**, not wording — avoid verbatim duplication.
- Canonical docs evolve; any parity established needs periodic re-verification.

#### Prerequisites

Read the five target files listed in the Proposal section (three CLAUDE.md-scoped primary targets + two secondary-scope guides for skill-authoring and session-management checklist items). No other dependency. (Earlier drafts said "three target files" here while the Proposal had expanded to five — stale scope corrected 2026-04-23 post-Codex review.)

#### Confidence

**Medium-high**. Source is canonical; drift has direct, non-speculative cost.

---

### A'-rt — Subagent Runtime Briefing Refinement (4-Component Structure)

#### Background

Round 1 Proposal A' called for enriching subagent briefings to restore context lost at the dispatch boundary. Round 2's Multi-Agent article provides the concrete four-component briefing structure that Anthropic reports as effective in practice. This refines A' from a principle to a usable template.

#### Proposal

Adopt the four-component briefing structure for every `/audit` subagent dispatch:

- **Objective** — the specific question being asked of this subagent
- **Output format** — expected deliverable shape (finding record schema, summary length, severity vocabulary)
- **Tool and source guidance** — which files, which rule sets, which tools to prioritize
- **Task boundaries** — explicit scope limits that prevent scope creep

Codify as a template in `plugin/skills/audit/SKILL.md`, not as implicit practice.

#### Source Evidence

- Multi-Agent Research System (paraphrased): vague instructions (e.g., "research the semiconductor shortage") led to duplicated effort and misalignment. Only the word "vague" is literal in the source; surrounding phrasing is a paraphrase.
- Multi-Agent Research System (structural claim, not verbatim): the article describes a four-component briefing — objective, output format, tool/source guidance, task boundaries. The four-component concept is the article's; the exact labeling as a single string is summarizer synthesis.

#### Risks / Tradeoffs

- *"agents typically use about 4× more tokens than chat interactions, and multi-agent systems use about 15× more tokens than chats"* (Multi-Agent) — longer briefings contribute. (Earlier drafts compressed "typically use about" → "use ~"; corrected to literal 2026-04-29 post-Tier 2 sweep.)
- *"token usage by itself explains 80% of the variance"* (Multi-Agent, in BrowseComp evaluation context) — adding briefing text changes the dominant variable. (Earlier drafts italicized "Token usage alone explains 80% of performance variance in BrowseComp evaluation" — paraphrase + appended context inside the italic; corrected to literal article fragment with separate context note 2026-04-29 post-Tier 2 sweep.)
- If the root cause of false positives is model hallucination rather than briefing gap, briefing enrichment has limited effect.

#### Prerequisites

1. Sample 5 recent `/audit` false-positive cases; classify by cause (briefing-gap / hallucination / criterion-ambiguity / other)
2. Read current `plugin/skills/audit/SKILL.md` to determine existing briefing structure
3. Use the initial 5-case sample only for hypothesis generation. If briefing-gap appears materially common, expand to a larger sample (target ~15–20 cases) before using the distribution as an adoption gate. (Earlier drafts used n=5, ≥40% as a direct decision threshold — only two cases, within chance variance. Parallel flaw to R1 L93; corrected 2026-04-23 post-Codex review.)

#### Confidence

**Medium-high**, conditional on the prerequisite sampling result.

---

### A'-ev — LLM-as-Judge Rubric in `test/` Framework

#### Background

Round 1's Proposal A' conflated two layers: runtime post-check within `/audit` execution and evaluation-time rubric in the `test/` framework. Round 2's self-review separated these: LLM-as-judge, as described in the Multi-Agent article, is a **measurement tool at evaluation time**, not a runtime component of the agent loop. Runtime application would be an extension of the pattern not evidenced by the article.

#### Proposal

Introduce a five-metric LLM-as-judge rubric into the `test/` eval framework, with **domain-appropriate redefinitions** for our audit context (the Multi-Agent rubric targets research agents, not audit agents):

| Original (Multi-Agent)     | Our Redefinition                                                               |
|----------------------------|--------------------------------------------------------------------------------|
| Factual accuracy           | Finding claim matches the cited file's actual contents                         |
| Citation fidelity          | `file:line` references are valid and point to the claimed content              |
| Completeness               | All rules within declared scope were evaluated                                 |
| Source quality → **Rule-scope adherence** | Evaluation stayed within declared rule set; no scope creep          |
| Tool efficiency            | Read/Grep/Glob choices fit the check type                                      |

Output format: single LLM call returning 0.0–1.0 scores plus pass/fail grade per finding.

#### Source Evidence

- *"a single LLM call with a single prompt outputting scores from 0.0-1.0 and a pass-fail grade was the most consistent and aligned with human judgements"* (Multi-Agent Research System; earlier drafts paraphrased to "outputting 0.0–1.0 scores plus pass/fail grades proved most consistent" — corrected to literal 2026-04-29 post-Tier 2 sweep)
- Human reviewers surfaced edge cases automation missed — the article reports "our early agents consistently chose SEO-optimized content farms over authoritative but less highly-ranked sources like academic PDFs or personal blogs" (Multi-Agent Research System). This argues for validation against human spot-checks. (Earlier drafts prepended "noticed that" and truncated the "like academic PDFs or personal blogs" tail; both corrected 2026-04-29 post-Tier 2 sweep. Original 2026-04-23 fix corrected an earlier "single summary quote" rendering.)

#### Risks / Tradeoffs

- `test/` is gitignored and internal; this work does not ship. Low leverage beyond internal calibration.
- LLM-as-judge has documented biases (noted in the article). The redefined rubric should be validated against a human-scored ground truth before trust.
- Adds cost to each eval run (one judge call per finding).

#### Prerequisites

1. Read current `test/` rubric structure **if present in the local checkout** (per `CLAUDE.md:19,32` and `.gitignore:21`, `test/` is gitignored and local-only — if absent in the executing environment, treat this prerequisite as blocked pending access to the local eval workspace; CI-visible validation lives under `.github/scripts/*.py`, which is not a substitute for the rubric here).
2. Validate the redefined rubric on 20–50 manually-scored historical audit outputs spanning the main failure modes. If only 5 outputs are available initially, treat them as a smoke test rather than sufficient validation — at n=5, one disagreement shifts the observed error rate by 20 percentage points across any single rubric metric, and a hand-picked small set can miss entire failure modes. (Earlier drafts proposed n=5 as sufficient validation; corrected 2026-04-23 post-Codex review.)
3. Compare judge output variance vs manual variance

#### Confidence

**Medium**. Layer separation resolves the Round 1 conflation; remaining uncertainty is redefinition adequacy.

---

### C' — Dual-Layer SKILL Audit (Scope-Reduced)

#### Background

Round 1's C' proposed auditing both the frontmatter (trigger signal) and body (usage specification) of each skill. Round 2 refines scope: the Writing Tools for Agents article's principles transfer unevenly.

- **Transfer strongly**: naming, namespacing, description-as-onboarding, avoiding tool overlap, error-message design
- **Do not transfer**: ResponseFormat enum verbosity control, fine-grained parameter structure (our skills use only `$ARGUMENTS`)

Round 1's audit included ResponseFormat-class items that do not apply to our markdown-based skills.

#### Proposal (Round 2 revision)

Retain Round 1's two-pass structure. Remove items related to structured I/O. Retain:

1. **Trigger audit (frontmatter)** — `description:` clarity, consistent "use when …" vocabulary across the four skills (`/create`, `/audit`, `/secure`, `/optimize`)
2. **Usage audit (body)** — interface-level error prevention (SWE-bench principle), explicit preconditions for irreversible actions
3. **Apply two of four Writing Tools anti-patterns** that transfer:
   - Unclear purpose boundaries / overlap between skills
   - Low-signal references (internal identifiers vs descriptive names)

#### Source Evidence

- SWE-bench engineering (Round 1): *"The replacement will only occur if there is exactly one match of `old_str`"* — interface-level error prevention (earlier drafts substituted "the tool" for the article's "The replacement"; corrected to literal 2026-04-29 post-Tier 2 sweep iteration 2)
- Building Effective Agents (Round 1): the Appendix 2 section heading is *"Prompt engineering your tools"*, and the ACI/HCI analogy is verbatim *"plan to invest just as much effort in creating good agent-computer interfaces (ACI)"* (earlier drafts compressed these into a fabricated single quote "prompt engineering your tools deserves equal effort as overall prompts"; corrected to verbatim heading + ACI fragment 2026-04-29 post-Tier 2 sweep iteration 2)
- Writing Tools for Agents: *"Namespacing (grouping related tools under common prefixes)"*, *"clearly communicate specific and actionable improvements, rather than opaque error codes or tracebacks"* (Earlier drafts paraphrased the first as "Namespace related tools with consistent prefixes" and restructured the error-pattern sentence into pseudo-rules "Unhelpful pattern: ... Helpful pattern: ..."; replaced with article's actual sentences 2026-04-29 post-Tier 2 sweep.)

#### Risks / Tradeoffs

- If skills are already well-specified, yield is low
- Over-tightening a trigger description lowers recall (skill not invoked when it should be)

#### Prerequisites

Pilot on one skill (`/audit` recommended — largest and the locus of known false-positive issues). Decide full rollout based on pilot yield.

#### Confidence

**Medium**, pending pilot.

---

### D — Think-Tool-Style Prompting in /audit (Unchanged from Round 1)

Proposal carried forward from Round 1 without modification. Summary: insert explicit reasoning checkpoints at `/audit` phase boundaries that enumerate applicable rules and verify information collection.

See [Round 1 Proposal D](./anthropic-engineering-insights-review.md) for full detail.

**Confidence**: **Medium**.

---

### F — Phase-Boundary Contract Check (Renamed from Round 1)

#### Background

Round 1 introduced a "Recovery-masking rubric" for the `test/` framework. Two issues surfaced in Round 2 self-review:

1. The term "Recovery Masking" may not be a canonical phrase from the source article. It appeared in the WebFetch summary but cannot be confirmed as verbatim without re-reading the original. Building a proposal around an uncertain term is fragile.
2. The concept was stretched from population-level statistical degradation (postmortem context) to single-run qualitative degradation (our context). The transfer is partial-isomorphism, not direct application: mechanism is similar, measurement framework differs.

#### Proposal

Rename and redefine as **Phase-Boundary Contract Check**: for each phase of `/audit`, verify that the output of Phase N satisfies the declared input contract of Phase N+1. This is a precise mechanical check, not a recovery-masking heuristic.

#### Source Evidence

- Postmortem fragment (extracted from a longer sentence, not a standalone motif): the article notes that "Claude often recovers well from isolated mistakes" while explaining why evaluations missed user-reported degradation. The principle that graceful self-recovery can hide defects motivates cross-phase contract validation.
- This proposal is **inspired by** the postmortem but defined independently to avoid concept abuse.

#### Risks / Tradeoffs

- Requires declared contracts between `/audit` phases; they may not currently exist, in which case this is not a check but a structural introduction.
- Explicit contract declaration increases SKILL.md length, conflicting with the repository's conciseness ethos.

#### Prerequisites

- Read `/audit` SKILL.md to determine whether phase contracts are currently implicit, explicit, or nonexistent
- Decide whether contracts should be formalized at all (structural change, not just a check)

#### Confidence

**Low-medium**. Escapes the uncertain-term problem of Round 1 but demands concrete contract definition.

---

### B — "Agent Patterns" Guide (Deferred)

Status unchanged from Round 1. Deferred until Proposals E, A'-rt, and C' produce verified pattern-to-skill mappings. See [Round 1 Proposal B](./anthropic-engineering-insights-review.md) for details.

**Confidence**: Low-medium.

---

### DXT — Skipped (Scope-Conditional)

#### Why skipped

- Desktop Extensions package MCP servers for **Claude Desktop**, not Claude Code plugins. Our primary audience is Claude Code plugin authors.
- Desktop-targeted MCP distribution is a minority workflow for our readers.
- Adding a DXT mention in `docs/guides/mcp-guide.md` would misplace Desktop-focused content in a Code-focused guide, risking reader confusion that exceeds the information value for most readers.

#### Condition for revisit

If a future guide is added dedicated to "MCP server development and distribution" (as distinct from MCP integration into Claude Code plugins), a DXT section becomes appropriate **in that guide**. Not in the current set.

#### Source

Desktop Extensions engineering post.

---

## Convergence Audit Trail

This section is a permanent record of corrections found during self-review, retained so future reviewers can assess how the proposals were calibrated.

| Loop | Target                             | Findings | Notable corrections                                                                                                      |
|------|------------------------------------|----------|--------------------------------------------------------------------------------------------------------------------------|
| 1    | Initial extraction from 5 sources  | —        | N/A                                                                                                                      |
| 2    | Critique of Loop 1                 | ~4       | LLM-as-judge layer conflation; rubric 3/5 transfer; Writing Tools ≠ structured tools; Recovery Masking treated as direct |
| 3    | Critique of Loop 2                 | ~7       | Loop 2 itself over-corrective: rubric 5/5 with redefinition; `disable-model-invocation` both framings valid; cross-cut 2-solid not 4-source |
| 4    | Critique of Loop 3                 | 1        | Loop 3's challenge to "LLM-as-judge = eval-only" was slightly excessive given article context                             |
| 5    | Critique of Loop 4                 | 0        | Loop 4 finding confirmed                                                                                                 |
| 6    | Broader sweep                      | 0        | No new issues                                                                                                            |
| 7    | Citation provenance check          | 1        | "Recovery Masking" may be summarizer coinage rather than canonical article term                                          |
| 8    | Critique of Loop 7                 | 0        | Finding accepted; Proposal F renamed to avoid reliance on uncertain term                                                 |
| 9    | Post-R5 cross-round re-review      | 4        | Loop 7's provenance check stopped after one instance (Recovery Masking); a class-level sweep on re-review finds: (a) 4-component briefing quote was summarizer synthesis, not article verbatim; (b) "Vague instructions" mostly paraphrased, only "vague" literal; (c) "Claude often recovers well..." is a fragment from a longer sentence, not a standalone motif; (d) "causally downstream" overstated a cross-round synthesis as article claim. All four corrected in-place (2026-04-22); proposal substance unchanged. |

| 10   | Tier 2 narrative paraphrase sweep  | 7        | Loop 9 (Tier 1 sweep) extended to Tier 2 across narrative claims and additional italicized quotes that prior loops had not exhaustively examined. Findings: (a) line 58 cross-cutting table cell "endless web searching for nonexistent sources" — paraphrase; article actual: "scouring the web endlessly for nonexistent sources"; (b) line 99 checklist item "repeated corrections" — paraphrase; article uses "Correcting over and over" as the pattern name; (c) line 151 italic "Agents use ~4× more tokens..." — compression of article's "agents typically use about 4×..."; (d) line 152 italic "Token usage alone explains 80% of performance variance in BrowseComp evaluation" — paraphrase + appended context; article verbatim is just "token usage by itself explains 80% of the variance"; (e) line 189 italic LLM-judge sentence rephrased multiple ways from article's "a single LLM call with a single prompt outputting scores from 0.0-1.0 and a pass-fail grade was the most consistent..."; (f) line 190 SEO content farms quote prepended "noticed that" and truncated tail "like academic PDFs or personal blogs"; (g) line 235 Writing Tools italics — both reformulated as "Namespace related tools with consistent prefixes" + "Unhelpful pattern: ... Helpful pattern: ..." pseudo-rules versus article's actual phrasing. All seven corrected in-place (2026-04-29). Tier 2 sweep also confirmed: Multi-Agent four-component briefing structure verbatim ("an objective, an output format, guidance on the tools and sources to use, and clear task boundaries"); 90.2% multi-agent advantage verbatim; 4×/15× token figures and 80% variance figure verbatim with exact phrasing now restored. |

| 11   | Tier 2 sweep iteration 2 (self-critique of Loop 10) | 3 | Loop 10 sweep was thorough but missed three additional Source-Evidence-section issues. Findings: (a) line 108 italic *"`disable-model-invocation: true` for workflows..."* dropped article's "Use" prefix — restored to literal "Use `disable-model-invocation: true`..."; (b) line 233 italic *"the tool will only occur if there is exactly one match of `old_str`"* substituted "the tool" for article's actual word "The replacement" — corrected; (c) line 234 italic *"prompt engineering your tools deserves equal effort as overall prompts"* was a fabricated compression of the Appendix 2 section heading + ACI/HCI analogy — replaced with verbatim heading and ACI fragment as separate citations. All three corrected in-place (2026-04-29). The discovery pattern (Loop 10 → 11 needed) confirms the methodology lesson recorded in `feedback_literal-quote-sweep-methodology.md`: even Tier 2 sweeps benefit from iteration; "all verified" claims should be tested against another pass before convergence is declared. |

**Convergence re-validated at Loop 11** after Tier 2 sweep iteration 2. Loop 7's design lesson — single-instance provenance findings should trigger class-level sweeps — extended through Loop 10's Tier 2 sweep and now re-iterated through Loop 11's self-critique. The recurrence pattern (Loop 7 "all verified" → Loop 9 corrections → Loop 10 "all verified" → Loop 11 corrections) is itself the methodological lesson — saved as memory entry `feedback_literal-quote-sweep-methodology.md` (2026-04-29).

---

## Unverified Assumptions (Cumulative — Rounds 1 + 2)

Items added or refined in Round 2 are marked with ⚡.

1. **False-positive root cause distribution** (impacts A'-rt). Classification into briefing-gap / hallucination / criterion-ambiguity has not been measured.
2. **Current `/audit` structural pattern** — Orchestrator-Workers vs Prompt Chaining — not verified against SKILL.md.
3. **Skill description quality** (impacts C'). Room-for-improvement presumed; pilot required to confirm.
4. **Benchmark transferability** (impacts D, A'-rt, A'-ev). τ-Bench / Multi-Agent internal benchmark figures (e.g., 54% airline improvement, 90.2% multi-agent advantage, 15× token cost) may not transfer linearly to our audit workflow.
5. ⚡ **"Recovery Masking" term provenance**. The phrase may be a summarizer coinage rather than a canonical article term. Proposal F has been renamed to avoid reliance.
6. ⚡ **LLM-as-judge applicability at runtime**. The article presents it as an evaluation-time measurement tool; runtime application would extend the pattern beyond what the article evidences.
7. ⚡ **Parity drift magnitude**. Proposal E presumes non-zero drift between our guides and canonical docs; unverified until Read.
8. ⚡ **Cross-article synthesis strength**. The Round 2 pattern "plausible output masks real defects" is strong in two sources (Best Practices, Postmortem), partial in one (Writing Tools), weak in one (Multi-Agent). Treated as a 2-source pattern rather than a universal cross-cut.

---

## Recommended Next Step

A single Read round unlocks verification for nearly all proposals:

| File to Read                              | Unlocks                                            |
|-------------------------------------------|----------------------------------------------------|
| `docs/guides/claude-md-guide.md`          | Proposal E primary (CLAUDE.md scope)               |
| `templates/starter/CLAUDE.md`             | Proposal E primary (CLAUDE.md scope)               |
| `templates/advanced/CLAUDE.md`            | Proposal E primary (CLAUDE.md scope)               |
| `docs/guides/advanced-features-guide.md`  | Proposal E secondary (skill-authoring checklist items) |
| `docs/guides/effective-usage-guide.md`    | Proposal E secondary (session-management checklist items) |
| `plugin/skills/audit/SKILL.md`            | Proposals A'-rt, C', D, F                          |

After this Read, proposals move from hypothesis to actionable diff plans. This document together with Round 1 provides the decision framework; Read unlocks execution.

An alternative narrower first step: run the **two-stage causal sampling exercise** from Proposal A' in Round 1 (see its Prerequisites section — Stage 1 hypothesis-generation at n=5, then Stage 2 decision-gate at n≈15–20) — that disambiguates whether A'-rt's briefing-gap hypothesis is worth pursuing before any doc work. (Earlier drafts compressed this reference to "classify 5 false-positive cases", which replicated the single-exercise phrasing that R1 already moved away from — parallel stale copy to R1 L257; corrected 2026-04-23 post-Codex review.)

---

## References

### External (primary sources)

- **Claude Code Best Practices** (canonical docs) — <https://code.claude.com/docs/en/best-practices>
- Anthropic Engineering — *How we built our multi-agent research system*: <https://www.anthropic.com/engineering/multi-agent-research-system>
- Anthropic Engineering — *Desktop Extensions*: <https://www.anthropic.com/engineering/desktop-extensions>
- Anthropic Engineering — *Writing tools for agents*: <https://www.anthropic.com/engineering/writing-tools-for-agents>
- Anthropic Engineering — *A postmortem of three recent issues*: <https://www.anthropic.com/engineering/a-postmortem-of-three-recent-issues>

### Internal (this repository)

- [Round 1 plan: `anthropic-engineering-insights-review.md`](./anthropic-engineering-insights-review.md) — covers Contextual Retrieval, Building Effective Agents, SWE-bench engineering, Think Tool
- `CLAUDE.md` § "Contribution Rules" (length budgets, frontmatter conventions)
- `plugin/skills/audit/SKILL.md` — subject of Proposals A'-rt, C', D, F pilot
- `plugin/skills/create/SKILL.md`, `plugin/skills/secure/SKILL.md`, `plugin/skills/optimize/SKILL.md` — additional subjects of Proposal C'
- `docs/guides/claude-md-guide.md`, `templates/starter/CLAUDE.md`, `templates/advanced/CLAUDE.md` — primary subjects of Proposal E (CLAUDE.md scope); `docs/guides/advanced-features-guide.md` and `docs/guides/effective-usage-guide.md` — secondary subjects (skill-authoring / session-management checklist items)
- `test/` eval framework — subject of Proposal A'-ev
- Memory entries referenced: `feedback_subagent_verification.md`, `project_meta_system_vision.md`, `feedback_plans_scope.md`
