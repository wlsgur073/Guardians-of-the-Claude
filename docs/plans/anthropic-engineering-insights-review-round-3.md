# Anthropic Engineering Insights — Applicability Review (Round 3)

**Status**: Draft (evaluation basis, not an approved change)
**Created**: 2026-04-22
**Last revised**: 2026-04-29 (Tier 2 narrative paraphrase sweep across Loops 12–13; previous 2026-04-22 calibrations recorded as Loop 11)
**Scope**: Third review round covering four additional sources. Continues [Round 1](./anthropic-engineering-insights-review.md) and [Round 2](./anthropic-engineering-insights-review-round-2.md), both of which remain authoritative for their respective source bundles.

---

## Purpose

This document captures proposals derived from a third batch of Anthropic materials. Two structural characteristics distinguish this round:

1. **Most proposals are extensions, not new standalones.** Four of six proposals (E-ext, F-ext, and J relate to existing proposals; H is standalone; G is new) refine axes already recorded in Round 2. This reflects that the current review set overlaps substantially with topics previously covered, and that the value here is additive evidence and canonical framing rather than new directions.
2. **One source is a canonical engineering reference for our project's domain.** *Equipping agents for the real world with agent skills* describes Anthropic's Agent Skills concept — the skill system that Claude Code plugins (our marketplace's subject) implement and teach following the article's principles. Named Anthropic concepts (e.g., "Progressive Disclosure") appear here as design anchors, not as one view among many.

This document reflects the **converged state after ten self-review loops**. Corrections discovered during the loops are recorded in the "Convergence Audit Trail" section. As with prior rounds, no change is authorized by this document; it exists as a decision basis.

---

## Source Material

Four sources in this round. One is canonical engineering reference for our project's domain; one is a canonical blog on a feature (sandboxing) with a separate official docs parity target; two are general engineering posts.

1. **Equipping agents for the real world with Agent Skills** — <https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills> (canonical engineering reference for our domain)
2. Effective context engineering for AI agents — <https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>
3. Claude Code sandboxing — <https://www.anthropic.com/engineering/claude-code-sandboxing> (blog post = motivation source; parity target is official docs)
4. Code execution with MCP — <https://www.anthropic.com/engineering/code-execution-with-mcp>

---

## TL;DR

| ID      | Proposal                                                          | Confidence      | Effort      | Relation to prior rounds |
|---------|-------------------------------------------------------------------|-----------------|-------------|--------------------------|
| G       | Sandboxing teaching content check                                  | Medium-high     | Low-medium  | New                      |
| E-ext   | Extend R2 Proposal E with Progressive Disclosure axis              | Medium-high     | Low         | Extends R2 E             |
| F-ext   | Extend R2 Proposal F with intra-phase note-taking sub-item         | Medium          | Low         | Extends R2 F             |
| J       | Add context-rot / n² rationale for CLAUDE.md length limit          | Low-medium      | Very low    | New (pedagogical)        |
| H       | MCP guide: short section on code-execution pattern                 | Low             | Low         | New                      |
| —       | Just-in-time retrieval for /audit subagents                        | **Skip**        | —           | Paradigm mismatch        |

Approximate priority: **G ≈ E-ext > F-ext > J > H > skip**.

---

## Cross-Cutting Themes

### Round 3 Pattern: "Deliberate scope limitation at runtime"

All four sources converge on one design motif: **limit what the model sees at each step to only what is needed at that step.**

| Source                       | Manifestation                                                                 | Fit       |
|------------------------------|-------------------------------------------------------------------------------|-----------|
| Agent Skills                 | Progressive Disclosure — metadata / SKILL.md / supporting files loaded in stages | Strong    |
| Context Engineering          | "Smallest possible set of high-signal tokens"; just-in-time retrieval          | Strong    |
| Code execution with MCP      | Tool definitions loaded on-demand via filesystem-of-code-files                 | Strong    |
| Claude Code sandboxing       | Scope limitation applied to filesystem/network, not to model context           | Adjacent  |

Three sources exhibit the same mechanism (deferred loading for attention/cost reasons); sandboxing applies the scope-limitation *concept* to a different axis (security isolation, not attention). Treated here as a **3-source mechanism pattern** with sandboxing as a concept neighbor.

### Relation to Rounds 1 and 2

- **Round 1** emphasized *restoring* context at boundaries (boundary information loss).
- **Round 2** emphasized *verifying* output that might mask defects (plausible-output masking).
- **Round 3** emphasizes *limiting* context at runtime so only what is needed is loaded.

Our cross-round synthesis (not asserted by any single article; a pattern extracted across the three rounds): **limit what loads (R3) → restore what matters at boundaries (R1) → verify what comes out against masking (R2)**. This ordering is heuristic rather than causal.

---

## Proposals

### G — Sandboxing Teaching Content Check

#### Background

Claude Code sandboxing provides filesystem and network isolation, preventing a prompt-injected agent from modifying sensitive files or exfiltrating data. The Anthropic blog cites *"In our internal usage, we've found that sandboxing safely reduces permission prompts by 84%"* — a strong operational value signal. (Earlier drafts compressed to "reduces permission prompts by 84% internally", reordering "internally" as a tail modifier and dropping "we've found" + "safely"; restored to article's actual sentence 2026-04-29 post-Tier 2 sweep.) The topic is commonly raised by Claude Code users and aligns naturally with our `/secure` skill.

Our repository is a documentation and plugin marketplace; sandboxing is squarely a topic readers expect us to cover. Absent coverage is a teaching gap; weak coverage understates the feature's importance.

#### Proposal

Audit whether the following surfaces cover sandboxing coherently:

- Relevant settings guide (e.g., `docs/guides/settings-guide.md`)
- `templates/advanced/.claude/settings.json` — does it demonstrate sandbox configuration?
- `plugin/skills/secure/SKILL.md` — does it recommend sandboxing for high-risk workflows?

**Parity target distinction**:
- The **blog post** is the motivation source — cite it for *why* sandboxing matters and the 84% figure (qualified as Anthropic-internal).
- The **official docs** (on code.claude.com) are the specifics source — the authoritative reference for configuration syntax, sandbox profiles, and platform differences (Linux bubblewrap, macOS seatbelt).

Any teaching content should pull motivation from the blog and specifics from the docs; do not attempt to derive specifics from the blog alone (the blog is deliberately thin on configuration syntax).

#### Source Evidence

- *"Claude can only access or modify specific directories. This is particularly important in preventing a prompt-injected Claude from modifying sensitive system files."* (Sandboxing blog)
- *"Without network isolation, a compromised agent could exfiltrate sensitive files like SSH keys; without filesystem isolation, a compromised agent could easily escape the sandbox."* (Sandboxing blog)
- *"In our internal usage, we've found that sandboxing safely reduces permission prompts by 84%"* (Sandboxing blog — qualified: Anthropic internal measurement; earlier drafts compressed to "Sandboxing reduces permission prompts by 84% internally" — corrected to literal 2026-04-29 post-Tier 2 sweep)

#### Risks / Tradeoffs

- The 84% figure is Anthropic-internal; transferability to general users is not guaranteed. Use with qualification.
- The blog post is deliberately thin on configuration specifics; relying on it alone for how-to content will produce incomplete guidance.
- Sandboxing availability and feature set may evolve; teaching content needs periodic refresh.

#### Prerequisites

1. Read the settings guide and `templates/advanced/.claude/settings.json`
2. Read `plugin/skills/secure/SKILL.md`
3. Fetch official sandboxing docs once (likely at `code.claude.com/docs/en/sandboxing`)

#### Confidence

**Medium-high**. High-value topic with a canonical source pair (blog + docs) — parity drift cost is clear.

---

### E-ext — Extend R2 Proposal E with Progressive Disclosure Axis

#### Background

Round 2 Proposal E proposed a parity audit of our teaching content against Claude Code Best Practices. Round 3's Agent Skills article introduces named canonical concepts specific to the skills domain — most notably **Progressive Disclosure** as a three-level design principle. These concepts deserve their own axis in the parity audit because they are (a) canonical Anthropic framing, and (b) directly about our project's primary subject (plugins/skills).

#### Proposal

Add the following checklist items to R2 Proposal E:

1. Does our plugin/skill development guidance explicitly name and explain **Progressive Disclosure** (three levels — metadata / SKILL.md / supporting files)?
2. Is our use of **skill-local** supporting files (e.g., `plugin/skills/create/references/` and `plugin/skills/audit/references/`, which match the article's canonical bundled-skill structure) presented as the primary example of this pattern, while `plugin/references/*.md` is distinguished as a related-but-non-canonical shared-reference approach? (Earlier drafts presented `plugin/references/*.md` as the sole example, partially reintroducing the same overclaim the Risks section correction already walked back — corrected 2026-04-23 post-Codex review.)
3. Is the article's design guidance — *"Pay special attention to the `name` and `description` of your skill. Claude will use these when deciding whether to trigger the skill in response to its current task"* — reflected in our guide?
4. Is the skill-development workflow reflected — *"Start with evaluation: […]"* and *"Iterate with Claude: […] ask Claude to capture its successful approaches and common mistakes into reusable context"*?
5. Is the security guidance present — *"We recommend installing skills only from trusted sources. When installing a skill from a less-trusted source, thoroughly audit it before use"* — relevant for our marketplace repo?

#### Source Evidence

- *"A skill is a directory containing a `SKILL.md file`."* (Agent Skills blog) — the article's actual continuation is "This file must start with YAML frontmatter…", not "that contains organized folders of instructions, scripts, and resources that give agents additional capabilities". Earlier drafts had "restored" the latter continuation as if verbatim — Tier 2 sweep against fresh fetch confirms it is paraphrase, not in the article. Truncated to verified verbatim portion 2026-04-29 post-Tier 2 sweep; the 2026-04-23 "restoration" note is now superseded.
- Progressive Disclosure three levels as described in the article (metadata → SKILL.md → supporting files)
- *"The amount of context that can be bundled into a skill is effectively unbounded"* — the article's rationale for progressive disclosure
- Development workflow and security guidance quoted above

#### Risks / Tradeoffs

- We **partially instantiate** Progressive Disclosure. The article's canonical bundled-skill pattern (skill-local `references/`) is used in `plugin/skills/create/` and `plugin/skills/audit/` — the latter nests a `checks/` sub-directory holding multi-tier check files. `plugin/skills/secure/` and `plugin/skills/optimize/` rely on the shared `plugin/references/` directory instead, which is related but not the article's canonical bundled-skill structure. Whether we **teach** the pattern explicitly is a separate audit question — not yet verified. (Earlier drafts described our structure as uniformly `plugin/skills/*/SKILL.md` with `plugin/references/*.md`, which misrepresented the mixed pattern — corrected 2026-04-23 post-Codex review.)
- Over-citing a blog post where official docs should be the reference: the article is canonical engineering *framing*; official skills docs may have normative authority.

#### Prerequisites

- Identify the plugin/skill development guide(s) in `docs/guides/` and Read them
- Combined with R2 Proposal E prerequisites (reads of `docs/guides/claude-md-guide.md` and `templates/*/CLAUDE.md`)

#### Confidence

**Medium-high**. Source is canonical engineering framing of the exact feature we teach; any drift is a direct teaching gap.

---

### F-ext — Intra-Phase Note-Taking Sub-Item for R2 F

#### Background

Round 2 Proposal F introduced a *Phase-Boundary Contract Check* — a check that Phase N's output satisfies Phase N+1's input contract. Round 3's Context Engineering article describes **Structured Note-Taking** (for example, Claude Code's to-do list pattern or a custom agent maintaining a `NOTES.md` file — the full article quote appears in Source Evidence below) as a first-class pattern for agentic memory across complex tasks.

F and note-taking are adjacent but distinct:
- **F (Phase-Boundary Contract Check)** — inter-phase validation
- **Note-taking** — intra-phase accumulation of findings across many operations

#### Proposal

Add an intra-phase sub-item to R2 F: if `/audit` accumulates findings within a single phase across many file reads or subagent calls, adopt an explicit scratchpad / NOTES-file pattern rather than holding state implicitly in conversation history.

This is a sub-item, not a separate proposal: it only applies if phase-internal accumulation is substantial in the actual SKILL.md structure.

#### Source Evidence

- *"Like Claude Code creating a to-do list, or your custom agent maintaining a NOTES.md file, this simple pattern allows the agent to track progress across complex tasks."* (Context Engineering)
- Context rot rationale (article presents these as separate sentences; verbatim where quoted): *"as the number of tokens in the context window increases, the model's ability to accurately recall information from that context decreases"* and separately attributes this to *"transformer architecture's n² pairwise token relationships"* — motivates externalizing state rather than holding it in context. (Earlier drafts concatenated these into a single italic quote with "..." that misrepresented the article's two-sentence structure; corrected to two separate verbatim fragments 2026-04-29 post-Tier 2 sweep.)

#### Risks / Tradeoffs

- If `/audit` phases are short and single-pass, no intra-phase accumulator is needed. Adding one creates ceremony without payoff.
- Externalized notes introduce file state that must be cleaned up between runs.

#### Prerequisites

- Read `plugin/skills/audit/SKILL.md` to determine whether intra-phase state accumulates substantially
- Adopt only if the audit of F (from R2) surfaces concrete accumulation pain

#### Confidence

**Medium**. Conditional on F being pursued and on intra-phase state being non-trivial.

---

### J — Context-Rot Rationale for CLAUDE.md Length Limit

#### Background

Our `CLAUDE.md` declares *"This CLAUDE.md should stay under 200 lines, matching the repo's own recommendation in `docs/guides/claude-md-guide.md`"*. The rule is stated but the underlying mechanism is not. Context Engineering describes **context rot** — *"as the number of tokens in the context window increases, the model's ability to accurately recall information from that context decreases"* (article phrasing), with a separate-sentence attribution to *"transformer architecture's n² pairwise token relationships"* — which provides a principled rationale for length limits generally. (Earlier drafts joined the two passages with "..." as if a single quote; corrected to separate verbatim fragments 2026-04-29 post-Tier 2 sweep.)

#### Proposal

Add one to two sentences to `docs/guides/claude-md-guide.md` that explain *why* CLAUDE.md length matters, citing context rot as the mechanism. Example framing (not prescriptive wording):

> CLAUDE.md is read every turn, so longer files increase context load and can dilute attention to the most important instructions. Context length growth also interacts with a documented phenomenon ("context rot") in which model recall from long contexts degrades as context fills. Keeping CLAUDE.md short is not merely stylistic; it improves the odds of consistent adherence by reducing unnecessary context pressure.

(Earlier drafts rendered this as "performance guarantee" and causally linked n² attention cost directly to accuracy degradation — the Risks section immediately below had already acknowledged this conflation; main-body framing corrected 2026-04-23 post-Codex review to match the more careful framing the Risks section already demanded.)

#### Source Evidence

- "context rot" (verbatim term; Context Engineering) plus the article's separate-sentence elaborations: *"as the number of tokens in the context window increases, the model's ability to accurately recall information from that context decreases"*; *"transformer architecture's n² pairwise token relationships"*; and inner fragment *"models have less experience with, and fewer specialized parameters for, context-wide dependencies"*. (Earlier drafts concatenated all into a single italic quote bridging multiple article passages; replaced with verbatim term + separate verbatim fragments 2026-04-29 post-Tier 2 sweep.)

#### Risks / Tradeoffs

- The n² relationship describes attention compute, not directly accuracy; the article's framing collapses two concepts. Teaching material should be careful not to claim more than the source does.
- Our 200-line limit was set independently of this article; framing the article as the "reason" for the limit is post-hoc rationalization. Prefer framing as *"a well-documented mechanism that motivates such limits"*.

#### Prerequisites

Read `docs/guides/claude-md-guide.md` to see how length guidance is currently framed.

#### Confidence

**Low-medium**. Very low effort; modest pedagogical value; conservative framing required.

---

### H — MCP Guide Section on Code-Execution Pattern

#### Background

The Code Execution with MCP article describes an alternative to direct tool calls: the agent writes code against MCP servers treated as a filesystem of code files, with on-demand loading of tool definitions. The article cites a token reduction *"from 150,000 tokens to 2,000 tokens—a time and cost saving of 98.7%"* **in one Google Drive → Salesforce workflow example** — a single data point, not a generalizable expectation. (Earlier drafts truncated to "150,000 tokens to 2,000 tokens, representing a 98.7%" plus standalone "reduction" word — paraphrased connector inside italic markers; restored to literal 2026-04-29 post-Tier 2 sweep iteration 2.)

This pattern applies narrowly. The article does not formalize a checklist; the conditions below are our synthesis from its examples (article phrases in parentheses where applicable):
- Hundreds to thousands of tools across multiple MCP servers (article: "hundreds or thousands of tools across dozens of MCP servers")
- Large-dataset filtering in the execution environment (article example: 10,000-row spreadsheet)
- Complex control flow (loops, conditionals, retry logic)
- PII tokenization / privacy-preserving workflows

For typical plugin authors, direct tool calls remain simpler. The pattern is worth knowing about but should not be oversold. (Earlier drafts framed the four bullets as if directly enumerated by the article; reframed as our synthesis from examples 2026-04-29 post-Tier 2 sweep.)

#### Proposal

Add a short section to `docs/guides/mcp-guide.md` titled something like *"When to consider the code-execution MCP pattern"*. Content: one paragraph describing the pattern's applicability conditions, one sentence on the single-example 98.7% number with context, and one sentence on the security tradeoff (*"requires a secure execution environment with appropriate sandboxing, resource limits, and monitoring"* — cite the article).

#### Source Evidence

- Token-reduction example quoted above (Code Execution with MCP article)
- *"Code execution introduces its own complexity. Running agent-generated code requires a secure execution environment with appropriate sandboxing, resource limits, and monitoring."* (same article)
- Applicability conditions listed in the article (large tool counts, large datasets, complex control flow, PII handling, state persistence)

#### Risks / Tradeoffs

- Narrow audience — most readers will not benefit. Overselling the pattern misleads readers into adopting complexity for no gain.
- Single-example 98.7% figure can be misread as a general expectation; cite with explicit qualification.
- Pattern intersects with sandboxing (Proposal G) — a future refactor could cross-reference rather than duplicate.

#### Prerequisites

Read current `docs/guides/mcp-guide.md` to determine placement and current coverage.

#### Confidence

**Low**. Correct inclusion criterion; small audience.

---

### Skipped — Just-in-Time Retrieval for /audit Subagents

The Context Engineering article describes runtime just-in-time retrieval where agents hold lightweight identifiers (file paths, queries, links) and dereference them on demand. This pattern fits **research** tasks with open-ended exploration. `/audit` is a **verification** task where subagents must return concrete findings suitable for immediate surfacing — returning identifiers would require the parent to re-read and re-verify, adding roundtrips without compression gain.

Paradigm mismatch; not pursued.

---

## Convergence Audit Trail

| Loop | Target                               | Findings | Notable corrections                                                                                                                                                                        |
|------|--------------------------------------|----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1    | Initial extraction from 4 sources    | —        | N/A                                                                                                                                                                                        |
| 2    | Critique of Loop 1                   | 4        | ① structured note-taking is new axis, not validation-only; ② "canonical for our domain" was strong — prefer "canonical engineering reference"; ③ sandboxing fetch thin → split motivation vs specifics; ④ code-exec MCP overselling risk |
| 3    | Critique of Loop 2                   | 3        | ① just-in-time retrieval is paradigm-mismatched for /audit (research vs verification); ② sandboxing parity target is **official docs**, not blog; ③ "future direction signal" framing over-reads the code-exec article |
| 4    | Critique of Loop 3                   | 2        | ① Loop 3 overcorrected note-taking — intra-phase accumulator remains valid even if just-in-time retrieval is not; ② removed "future direction signal" framing                              |
| 5    | Critique of Loop 4                   | 1        | Intra-phase note-taking overlaps Round 2 Proposal F — merge as F sub-item rather than standalone                                                                                           |
| 6    | Citation / provenance sweep          | 0        | All 10+ quoted phrases verified literal against fetch output; no fabricated citations                                                                                                      |
| 7    | Proposal derivation                  | —        | 5 proposals + 1 skip identified                                                                                                                                                            |
| 8    | Proposal calibration                 | 3        | ① Progressive Disclosure *instantiated* vs *taught* — flag as assumption; ② 84% is Anthropic-internal measurement, not a user-environment guarantee; ③ 98.7% is a single-example figure     |
| 9    | Merge check                          | 1        | Standalone note-taking proposal withdrawn in favor of F sub-item                                                                                                                           |
| 10   | Final over/under claim sweep         | 0        | No new corrections                                                                                                                                                                         |
| 11   | Post-R5 class-level provenance sweep | 5        | Loop 6 had declared "All 10+ quoted phrases verified literal"; a rigorous class-level sweep (modeled on R2 Loop 9) finds: (a) three truncated quotes in E-ext checklist — lines 131/132/133 each abbreviated the source text without ellipsis markers; extended to full source or marked with […]; (b) parenthetical quote in F-ext background (line 162) was a mid-sentence fragment — replaced with paraphrase plus cross-reference to Source Evidence; (c) "exact feature" at line 14 overclaims scope (Agent Skills concept vs Claude Code plugin implementation) — softened; (d) arrow lifecycle (lines 63-67) was cross-round author synthesis presented without qualifier — marked as our synthesis, "heuristic rather than causal". All five corrected in-place (2026-04-22); proposal substance unchanged. |

| 12   | Tier 2 narrative paraphrase sweep    | 6        | Loop 11 (Tier 1 sweep) extended to Tier 2 across narrative claims and additional italicized quotes. Findings: (a) line 78 + line 100 G italic *"reduces permission prompts by 84% internally"* truncated and reordered article's actual *"In our internal usage, we've found that sandboxing safely reduces permission prompts by 84%"* — restored at both sites; (b) line 138 skill definition italic — the 2026-04-23 "restoration" of "that contains organized folders of instructions, scripts, and resources that give agents additional capabilities" turned out to NOT be article-verbatim; the article's actual continuation is "This file must start with YAML frontmatter…". Truncated to verified verbatim portion ("A skill is a directory containing a `SKILL.md file`."); (c) line 178 + line 200 + line 212 context-rot italics each concatenated separate article passages as if a single quote with "..." — all three replaced with article's actual two-sentence structure (verbatim fragments separated explicitly); (d) line 234 H applicability conditions framed as bullet enumeration — article presents through examples rather than as a formal checklist; reframed as our synthesis from examples. Tier 2 sweep also confirmed: "Linux bubblewrap and MacOS seatbelt" verbatim, Progressive Disclosure three-level structure verbatim ("first level"/"second level"/"third level (and beyond)"), security recommendation verbatim, "effectively unbounded" verbatim, NOTES.md/to-do verbatim, just-in-time identifiers verbatim, "Structured note-taking" verbatim. All six corrected in-place (2026-04-29). |

| 13   | Tier 2 sweep iteration 2 (self-critique of Loop 12) | 1 | Loop 12 sweep was thorough but missed one additional H Background italic. Finding: line 233 italic *"150,000 tokens to 2,000 tokens, representing a 98.7%"* (followed by standalone "reduction") used the word "representing" as a connector inside the italic, while the article's actual phrasing is "from 150,000 tokens to 2,000 tokens—a time and cost saving of 98.7%". Replaced with literal article phrasing as a single italic. Corrected in-place (2026-04-29). The Loop 12 → 13 pattern confirms methodology lesson recorded in `feedback_literal-quote-sweep-methodology.md`: Tier 2 sweep iterations are also subject to single-pass blind spots and benefit from a second self-critique pass. |

**Convergence re-validated at Loop 13** after Tier 2 sweep iteration 2. R3 baseline now established at Tier 1 + Tier 2 + Tier 2 self-critique. The 2026-04-23 "restoration" attempt at line 138 illustrates a fail-mode where audit-trail notes can themselves codify paraphrase as if it were truncation-being-restored — flagged as methodological lesson: any "restored truncation" claim should be verified against fresh source fetch, not memory of an earlier loop.

---

## Unverified Assumptions (Cumulative — Rounds 1 + 2 + 3)

Items added or refined in Round 3 marked with ⚡⚡. Round 2 additions marked ⚡ (from Round 2 doc).

**From Rounds 1–2 (carried forward):**

1. False-positive root cause distribution (impacts R2 A'-rt)
2. Current `/audit` structural pattern — Orchestrator-Workers vs Prompt Chaining
3. Skill description quality (impacts R2 C')
4. External-benchmark transferability (τ-Bench, Multi-Agent, etc.)
5. ⚡ "Recovery Masking" term provenance
6. ⚡ LLM-as-judge runtime applicability
7. ⚡ Parity drift magnitude vs Best Practices canonical docs
8. ⚡ Cross-article synthesis strength — R2 "plausible output" pattern is 2-source

**Added in Round 3:**

9. ⚡⚡ **Progressive Disclosure teaching presence** — our plugin structure instantiates the pattern, but whether our guides *name and teach* the pattern is unverified (impacts E-ext)
10. ⚡⚡ **Current sandboxing coverage in guides / templates / `/secure`** — unverified until Read (impacts G)
11. ⚡⚡ **Official sandboxing docs content** — blog is the motivation source, docs are the specifics source, but docs have not been fetched (impacts G)
12. ⚡⚡ **84% permission-prompt reduction transferability** — Anthropic-internal measurement; generalization to arbitrary user environments is not claimed by the article
13. ⚡⚡ **98.7% code-execution savings generalizability** — derived from a single example workflow; not a baseline expectation
14. ⚡⚡ **Intra-phase note-taking necessity in `/audit`** — F-ext is conditional on phase-internal accumulation being non-trivial; unverified against actual SKILL.md

---

## Recommended Next Step

Round 3 proposals require three additions beyond the Round 2 prerequisite set:

| Additional action                                                                    | Unlocks                   |
|--------------------------------------------------------------------------------------|---------------------------|
| Read plugin/skill development guide(s) in `docs/guides/`                              | E-ext                     |
| Read settings-related guide and `templates/advanced/.claude/settings.json`                    | G                         |
| Read `plugin/skills/secure/SKILL.md`                                                  | G                         |
| One WebFetch of official sandboxing docs                                              | G (parity target confirmation) |
| Read `docs/guides/mcp-guide.md`                                           | H                         |

Combined with Round 2's prerequisite set (`claude-md-guide.md`, `templates/*/CLAUDE.md`, `plugin/skills/audit/SKILL.md`), a **single consolidated Read round** activates proposals across all three documents.

An alternative lighter first step: **G alone** — because sandboxing is the highest-value new topic with a clear external source pair, addressing it first is defensible even without the full Read sweep.

---

## References

### External (primary sources)

- Anthropic Engineering — *Equipping agents for the real world with Agent Skills*: <https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills>
- Anthropic Engineering — *Effective context engineering for AI agents*: <https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>
- Anthropic Engineering — *Claude Code sandboxing*: <https://www.anthropic.com/engineering/claude-code-sandboxing> (motivation source; specifics source is official docs)
- Anthropic Engineering — *Code execution with MCP*: <https://www.anthropic.com/engineering/code-execution-with-mcp>

### Internal (this repository)

- [Round 1 plan: `anthropic-engineering-insights-review.md`](./anthropic-engineering-insights-review.md) — covers Contextual Retrieval, Building Effective Agents, SWE-bench, Think Tool
- [Round 2 plan: `anthropic-engineering-insights-review-round-2.md`](./anthropic-engineering-insights-review-round-2.md) — covers Claude Code Best Practices, Multi-Agent Research System, Desktop Extensions, Writing Tools for Agents, Postmortem
- `CLAUDE.md` § "Contribution Rules"
- `plugin/skills/audit/SKILL.md` — subject of F-ext (and R2 D, F, A'-rt)
- `plugin/skills/secure/SKILL.md` — subject of G
- `docs/guides/claude-md-guide.md` — subject of J (and R2 E)
- `docs/guides/mcp-guide.md` — subject of H
- `templates/advanced/.claude/settings.json` — subject of G
- Memory entries referenced: `feedback_subagent_verification.md`, `project_meta_system_vision.md`, `feedback_plans_scope.md`
