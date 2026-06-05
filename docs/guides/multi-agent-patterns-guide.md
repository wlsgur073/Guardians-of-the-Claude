---
title: "Multi-Agent Patterns"
description: "Orchestrator-Worker, effort scaling, sub-agent context budget, breadth-first search, parallel dispatch — for Claude Code subagent workflows"
version: 1.2.0
---

# Multi-Agent Patterns

When a coding task is open-ended enough that you cannot predict how many steps it will take, a single agent in one context window struggles. Multi-agent setups — one orchestrator plus several workers — handle this kind of task better, at a cost.

This guide covers the patterns Anthropic and others have found effective when dispatching multiple Claude instances. For *single-agent* setup (Scope, Rules, Constraints, Verification), see [Advanced Features Guide — Agents](advanced-features-guide.md#agents). For broader workflow patterns (Writer/Reviewer, fan-out, worktrees), see [Workflow Patterns Guide](workflow-patterns-guide.md).

## When to choose multi-agent

| Task shape | Recommendation |
|---|---|
| Open-ended research with unpredictable step counts | Multi-agent (orchestrator + workers) |
| Sequential, fixed-step task | Single agent with prompt chaining |
| Large codebase change touching many files | Orchestrator + parallel worker per file or module |
| Simple bug fix in a known file | Single agent — multi-agent overhead is wasted |

Cost note: multi-agent runs typically use about 15× the tokens of a single chat session. Justify the spend before scaling: latency, parallelism, or quality must outweigh cost.

## Pattern: Orchestrator-Worker

A lead agent decomposes the task; worker agents execute sub-tasks; the lead synthesizes results.

For *every* worker, the lead specifies four things:

1. **Objective** — what to achieve, stated precisely
2. **Output format** — what shape the return should take (e.g., "1–2k token summary of findings")
3. **Tool guidance** — which tools to prefer or avoid
4. **Boundaries** — what NOT to touch or explore

Anthropic reports: "Without detailed task descriptions, agents duplicate work, leave gaps, or fail to find necessary information."

Example orchestrator prompt fragment:

```text
Spawn three workers in parallel. For each, specify the objective, output format, tool guidance, and boundaries.

Worker A — Investigate authentication flow.
  Objective: trace how a logged-in user's request reaches the database.
  Output format: 1–2k token summary listing each layer + the file that owns it.
  Tools: prefer Grep/Read; avoid Bash unless tracing runtime behavior.
  Boundaries: only src/auth/ and src/api/middleware/; do not enter src/services/.

Worker B — ...
```

## Effort scaling rules

Embed these rules into the orchestrator's system prompt so the lead does not over-invest in simple tasks:

| Task complexity | Worker count | Tool calls per worker |
|---|---|---|
| Simple fact-finding | 1 | 3–10 |
| Direct comparison | 2–4 | 10–15 |
| Complex research | 10+ | Divide responsibilities; per-worker count varies by sub-task* |

\* Anthropic's [multi-agent research system writeup](https://www.anthropic.com/engineering/multi-agent-research-system) does not pin a per-worker tool-call count for the complex tier. The same article notes that the lead agent "spins up **3–5 subagents in parallel** rather than serially".

A common failure mode is the lead spawning 10 workers for a question that one Grep would answer. Calibrate before dispatching.

## Sub-agent context budget

Each worker should return a **distilled summary (~1–2k tokens)**, not its full transcript. Rationale:

- The lead's context window stays clean for synthesis across workers.
- Tool call results within a worker are an internal concern, not the lead's.
- If the lead needs deeper detail, it asks the worker a follow-up rather than ingesting the full trail.

Anti-pattern: worker returns 50k tokens of raw output → lead cannot fit results from multiple workers in its own window.

## Breadth-first search strategy

When the task is exploratory:

1. Start with a broad query that surveys the landscape.
2. Evaluate the breadth before drilling.
3. Only then commit workers to a specific direction.

Going deep first wastes calls if you picked the wrong branch.

## Parallel dispatch primer

For local parallel dispatch via `claude -p` loops, see [Workflow Patterns — Fan-out for batch tasks](workflow-patterns-guide.md#fan-out-for-batch-tasks) — includes cost and safety warnings; do not run a fan-out without reading them. For `git worktree` session isolation as a separate parallelism mechanism, see [Workflow Patterns — Worktrees and parallel sessions](workflow-patterns-guide.md#worktrees-and-parallel-sessions).

For Claude Code's *built-in* subagent dispatch via the `Agent` tool, the orchestrator-worker pattern above maps directly — the parent session is the lead, each `Agent` invocation is a worker.

## Plan dependency waves before dispatch

Before firing parallel workers, sketch the task graph — even informally:

1. **Parallel waves** — group tasks with no dependencies into wave 1; dependents into wave 2+.
2. **Dependency matrix** — each later-wave task names the wave-1 task it depends on.
3. **Per-task acceptance + verification owner** — each worker gets one acceptance criterion and a named verifier (the worker itself, or the orchestrator).

Anti-pattern: firing every worker at once when task B consumes task A's output — B then races on stale or missing state. The [Effort scaling rules](#effort-scaling-rules) above tell you *how many* workers; this tells you *in what order*.

## Multi-surface identity invariance

Different surfaces shape *how* Claude communicates, but the role and deliverable invariant stay constant. A CLI session, a mobile chat, and a document-embedded helper all run with the same identity DNA — but each surface enforces a different output discipline.

| Surface | Identity (constant) | Output discipline (variant) |
|---|---|---|
| **CLI / Claude Code** | Same role declaration | Terse status updates; file diff is the deliverable; chat is the cover note |
| **Mobile / chat** | Same role declaration | The answer paragraph IS the deliverable; complete sentences; bounded length |
| **Document-embedded** (Excel, Word) | Same role declaration | The document edit is the deliverable; chat is a brief receipt |

When Claude moves between surfaces, the user mental model and agent mental model stay the same; what shifts is what counts as the "deliverable" and how chat relates to it. This invariance is what makes a single CLAUDE.md identity-DNA section adapt to multi-surface use without needing per-surface variants.

See [`claude-md-guide.md` § Identity-DNA](claude-md-guide.md#identity-dna) for the role-declaration template; the surface variants there are concrete examples of this invariance pattern.

## Peer message protocol

When an orchestrator delegates work to a worker (subagent), the inter-agent protocol carries three load-bearing elements beyond the four prerequisites already named in the Orchestrator-Worker pattern:

1. **Return-format contract.** Reinforces "Output format" above with peer-specific shape — verbatim raw output, a structured summary, or a yes/no verdict. Without an explicit contract, the orchestrator has to reparse free-form replies.
2. **Verification handoff.** Does the worker self-verify (read-back, scope-checked reporting per [`verification-discipline.md`](../../plugin/references/verification-discipline.md)), or does the orchestrator verify what the worker returns? Either is fine; ambiguity is not.
3. **Inspectability invariant.** Cross-agent threads should remain inspectable per [`trustworthy-agents-guide.md` § Subagent Observability](trustworthy-agents-guide.md#subagent-observability) — hook events recording subagent completion let the user see who-did-what across the parallel dispatch.

**Concrete example.** Orchestrator delegates "verify this Edit landed correctly" to a verification worker:

- Return-format: one-line verdict ("MATCH" / "MISMATCH: [reason]") plus the byte-compared lines.
- Verification handoff: worker performs read-back; orchestrator treats verdict as evidence (still subject to tool-success ≠ task-correct).
- Inspectability: `SubagentStop` hook records the worker's verdict in the decision changelog.

These elements are not tools — they are disciplines encoded in how peers prompt each other. State them explicitly in each dispatch.

## Further reading

- [Advanced Features Guide — Agents](advanced-features-guide.md#agents) — single-agent design (Scope, Rules, Constraints, Verification)
- [Workflow Patterns Guide](workflow-patterns-guide.md) — fan-out, Writer/Reviewer, worktrees
- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) (Anthropic Engineering)
- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — workflows-vs-agents taxonomy
- [Building a C compiler with a team of parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler) — extreme parallelism case study
