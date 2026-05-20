# Plan 02 — Opus 4.6 → 4.7 Evolution Study

**Status:** **complete** (started and finished 2026-05-20)
**Effort:** ~0.5 day (actual: 1 session)
**Dependencies:** Plan 01 ✅ complete (top gap = Gap 3 response discipline; some 4.x evolution may inform that)

## Goal
Diff `Anthropic/Official/claude-opus-4.6.md` (18.7KB) vs `Anthropic/Official/claude-opus-4.7.md` (24KB). Categorize deltas. Derive evolution patterns. Map to our guides.

## Initial hypothesis (from 2026-05-20 brainstorm) — **REFUTED post-analysis**
~~4.6's `<search_first>` mandatory rule became 4.7's inline `<product_information>` guidance — "explicit rules softened to inferential judgment."~~

**Correction (2026-05-20):** the original hypothesis was a **category error**. The `<search_first>` observation came from comparing **community-extracted** `Anthropic/claude-opus-4.6.md` (root, includes tools+ops content) against **Official** `Anthropic/Official/claude-opus-4.7.md` (behavior only). Different file types, not a valid version diff.

**Actual finding from Official 4.6 vs Official 4.7 comparison:** the pattern is the **OPPOSITE** — 4.7 is *longer* (187 vs 154 lines), *more structured*, and *more explicit*. See Findings below.

## Scope

### In scope
- Side-by-side semantic diff of Official 4.6 vs 4.7
- Per section: classify delta as **Added** / **Removed** / **Strengthened** / **Weakened** / **Restructured** / **Unchanged**
- Identify recurring evolution patterns (≥2 instances)
- Map each pattern to a guide section that could reference it

### Out of scope
- Community-extracted versions (signal-to-noise lower)
- Earlier models (3.7 / 4 / 4.5)
- Sonnet vs Opus comparison

## Method
1. Re-read Official 4.6 fully (only ~250 lines read in prior session)
2. Re-read Official 4.7 fully (only first 80 lines read)
3. For each 4.7 section, find counterpart in 4.6, classify delta
4. Cluster deltas → pattern catalog
5. For each pattern with ≥2 instances: identify target guide & section

## Deliverables
- `## Diff Table` (row per section: 4.6 / 4.7 / delta type / change summary)
- `## Pattern Catalog` (≥3 patterns expected, each with ≥2 instances)
- `## Guide Mapping` (which of our guides could cite which pattern + where)

## Success criteria
- ≥3 evolution patterns identified with ≥2 instances each
- Mapping to ≥2 guides with specific line refs
- Each pattern citation uses Anthropic's official release-notes URL as source (not leak repo path)

## Risks
- N=2 versions is small — patterns may be coincidence, not doctrine. Note confidence per pattern.
- 4.7 is currently active; Anthropic may release a hot-patch invalidating findings. Date-stamp.

---

## Findings

_Last update: 2026-05-20_

### Diff Table (Official 4.6 vs Official 4.7)

| Section | 4.6 ref | 4.7 ref | Delta type | Summary |
|---|---|---|---|---|
| `<product_information>` | `:3-23` | `:3-27` | Restructured | 4.7: Opus-only family; mobile app for Claude Code; Cowork promoted from beta; **PowerPoint NEW** beta |
| `<refusal_handling>` | `:25-39` | `:29-58` | **Strengthened + Added** | 4.7: new `<critical_child_safety_instructions>` subblock (5 numbered rules with NEVER/MUST NOT); 4.6's 1-paragraph soft version replaced |
| Refusal — saying less | (n/a) | `:46` | Added | "If the conversation feels risky or off, saying less and giving shorter replies is safer" |
| Refusal — respect end-of-conv | (n/a) | `:56` | Added | "If a user indicates they are ready to end the conversation, Claude does not request that the user stay" |
| `<legal_and_financial_advice>` | `:41-45` | `:60-64` | Unchanged | Identical |
| `<lists_and_bullets>` | `:49-61` | `:68-80` | Unchanged | Identical content |
| **`<acting_vs_clarifying>`** | (n/a) | `:84-92` | **Added (NEW BLOCK)** | "Make a reasonable attempt now, not interview"; "Acting with tools preferred over asking"; "See task through to complete answer" |
| **`<capability_check>`** | (n/a) | `:94-100` | **Added (NEW BLOCK)** | "Before concluding Claude lacks a capability... call tool_search"; "'I don't have access to X' is only correct after tool_search confirms" |
| Tone — focused & concise | (n/a) | `:104` | Added | "Claude keeps responses focused and concise so as to avoid overwhelming the user with overly-long responses" |
| Tone — vocab avoidance ("genuinely/honestly/straightforward") | `:79` | (removed) | **Removed** | Either over-specified in 4.6 or model now internalizes |
| Tone — emotes/asterisks rule | `:77` | (removed) | **Removed** | Same as above |
| `<user_wellbeing>` — means restriction | (n/a) | `:124` | Added | "When discussing means restriction... Claude does not name, list, or describe specific methods" |
| `<user_wellbeing>` — disordered eating specific | (n/a) | `:132` | Added | "No specific numbers, targets, or step-by-step plans" |
| `<anthropic_reminders>` | `:105-113` | `:144-152` | Unchanged | Identical |
| `<evenhandedness>` — single-word decline | (n/a) | `:168` | Added | New decline-short-answer rule for contested topics |
| `<responding_to_mistakes_and_criticism>` — anti-sycophancy | (n/a) | `:175-176` | **Added (significant)** | "Avoid collapsing into self-abasement"; "If person becomes abusive, Claude avoids becoming increasingly submissive" |
| `<election_info>` (subblock) | `:143-149` | (removed) | **Removed** | Time-bound 2024 election context aged out |
| `<knowledge_cutoff>` — cutoff date | `:141` (May 2025) | `:182` (January 2026) | Updated | Cutoff advanced ~8 months |
| **Overall length** | 154 lines | 187 lines | +33 lines (+21%) | Net growth despite removals |

### Pattern Catalog

#### P1. **Soft prose → structured numbered rules** (3 instances)
- Child safety: 1 paragraph → 5 numbered rules with NEVER/MUST NOT (4.6:29 → 4.7:33-44)
- Tone — adding `<acting_vs_clarifying>` and `<capability_check>` as named sub-blocks where 4.6 had no equivalent structure
- Wellbeing — adding two specific rule paragraphs (means restriction, disordered eating)

**Refutation of pass-1 hypothesis:** I expected the opposite ("explicit → inferential"). Actual: **stronger language and more structure as models mature**, not less. The model getting capable does not mean prompts get simpler — apparently it means Anthropic now feels safer being more directive.

**Confidence:** HIGH (3 distinct instances)

#### P2. **New behavior axes for known user friction** (2 instances)
- `<acting_vs_clarifying>` — addresses "Claude over-asks for clarification" complaint
- `<capability_check>` — addresses "Claude says it can't when it actually can via tool_search" complaint

**Pattern:** prompts evolve to patch *specific observable failure modes* in the previous version. The new sections read like *bug-fix patches in prompt form*.

**Confidence:** HIGH (clear cause-effect from user-feedback friction → prompt patch)

#### P3. **Anti-sycophancy / boundary maintenance** (2 instances)
- 4.7 adds explicit "avoid collapsing into self-abasement" paragraph
- 4.7 adds "saying less is safer" + "respects user's request to stop" — anti-clinginess

**Pattern:** explicitly defending model self-respect/integrity from social pressure dynamics in extended conversations.

**Confidence:** MEDIUM (2 instances, related but not identical)

#### P4. **Time-bound content lifecycle** (2 instances)
- Election info removed (2024 election was relevant when 4.6 shipped, less so for 4.7)
- Knowledge cutoff date moves forward (May 2025 → January 2026)

**Pattern:** prompts contain time-decaying content that must be pruned per release.

**Confidence:** HIGH (well-defined mechanism)

#### P5. **Style over-specification → backed off** (2 instances)
- 4.6 had "avoids saying 'genuinely/honestly/straightforward'" — REMOVED in 4.7
- 4.6 had emotes/asterisks rule — REMOVED in 4.7

**Pattern:** either (a) Anthropic concluded these were over-engineered, or (b) the model internalizes these without explicit prompting once it's more capable. Either way — style nano-rules don't survive into next version.

**Confidence:** MEDIUM (2 instances; mechanism interpretation unclear)

#### P6. **Granular safety axes added** (2 instances)
- Means restriction rule (new in 4.7)
- Disordered eating specific guidance (new in 4.7)

**Pattern:** general wellbeing concerns evolve into axis-specific rules as edge cases surface.

**Confidence:** HIGH (clear additions in same section)

### Guide Mapping (which of our guides could cite which pattern)

| Pattern | Target guide | Application |
|---|---|---|
| **P2 (acting_vs_clarifying)** | `effective-usage-guide.md` | **Direct source for Gap 3 (response discipline)**. Paraphrase the 4.7 `<acting_vs_clarifying>` block as *"what good Claude responses look like"* — this is the headline application. |
| P1 (more structure not less) | `claude-md-guide.md` "Writing Principles" | counter the "shorter is always better" assumption: validates "be specific and verifiable" principle |
| P3 (anti-sycophancy) | `trustworthy-agents-guide.md` | Could inform a self-respect / push-back doctrine — but optional, may be too internal |
| P4 (time-bound content) | `claude-md-guide.md` "Pruning Your CLAUDE.md" | reinforces existing pruning advice with evidence: Anthropic itself prunes |
| P5 (over-spec → backed off) | `claude-md-guide.md` "Common Mistakes" | new bullet: *"Don't over-specify style nano-rules; trust the model"* — cautionary pattern |
| P6 (granular safety) | (out of scope for our project) | n/a |

### Implications for Plan 04 (post-Plan 01 self-critique + Plan 02 findings)

The biggest finding for Plan 04 scope:

**Gap 3 (response discipline) — the only HIGH gap after self-critique — now has a direct, citable source in Anthropic Official 4.7's `<acting_vs_clarifying>` block.** This means:
- The recommended guide addition can paraphrase Anthropic's own 2026-active language
- Source attribution = Anthropic's release-notes URL (safe)
- We are NOT inventing the doctrine; we are surfacing what Anthropic just published

This dramatically strengthens the case for shipping Gap 3 (= Plan 04 entry 4-F).

Secondary applications (P1, P4, P5) are MEDIUM/LOW impact additions to existing sections, not new sections — they extend existing claude-md-guide.md content without requiring restructure.

### Plan 02 status: **COMPLETE**

Next plan to consider: Plan 03 (injection reminders → /secure skill) or Plan 04 amendment (apply Plan 01 + Plan 02 findings).
