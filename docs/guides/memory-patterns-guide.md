---
title: "Memory Patterns"
description: "How Claude's persistent memory works — the four memory types, frontmatter schema, MEMORY.md index, what-NOT-to-save rules, and the boundary between memory, plan, and task."
version: 1.0.1
---

# Memory Patterns

Claude Code's auto-memory system gives Claude persistent context across sessions — who you are, how you prefer to work, what the project is about, where related resources live. This guide covers the schema your project should expect, what does and doesn't belong in memory, and how memory differs from in-conversation state.

Auto-memory is enabled by default (`autoMemoryEnabled: true` in `settings.json`); see the [official memory documentation](https://code.claude.com/docs/en/memory) for storage location and toggle. This guide documents the *patterns* — not the toggle mechanics.

## The four memory types

Memory entries are categorized into four types, each with its own when-to-save and how-to-use rules.

**`user`** — Information about the user's role, goals, responsibilities, and knowledge. Build up an understanding of who the user is so future conversations can tailor responses. Example: "User is a senior backend engineer; deep Go expertise; new to React in this project."

**`feedback`** — Guidance the user has given about how to approach work. Both corrections ("don't do X") and confirmations ("yes, exactly — keep doing that"). Save with a `**Why:**` line and a `**How to apply:**` line so the rule survives edge cases. Example: "Integration tests must hit a real database, not mocks. Why: prior incident where mock/prod divergence masked a broken migration. How to apply: any test under `tests/integration/*`."

**`project`** — Information about ongoing work, goals, initiatives, bugs, or incidents that aren't derivable from the code or git history. Convert relative dates to absolute when saving ("Thursday" → "2026-03-05"). Example: "Auth middleware rewrite is driven by compliance requirements around session token storage — not tech-debt cleanup."

**`reference`** — Pointers to where information lives in external systems. Example: "Pipeline bugs are tracked in Linear project `INGEST`."

## Frontmatter format

Each memory file is a separate markdown file with frontmatter:

```markdown
---
name: {short-kebab-case-slug}
description: {one-line summary — used to decide relevance in future conversations}
metadata:
  type: {user, feedback, project, reference}
---

{memory content — for feedback/project, structure as: rule/fact + **Why:** + **How to apply:**}
```

Link related memories with `[[their-name]]` references. A `[[name]]` that doesn't match an existing memory yet is fine — it marks something worth writing later, not an error.

## The MEMORY.md index

`MEMORY.md` is the index, not a memory itself. Each entry is one line under ~150 characters: `- [Title](file.md) — one-line hook`. No frontmatter. Lines past 200 are truncated when loaded into Claude's context, so keep the index concise.

Organize semantically by topic, not chronologically. Update or remove entries that turn out to be wrong or outdated. Never write duplicate memories — check the existing index first.

## What NOT to save

The memory system is for facts that span conversations. The following do NOT belong in memory:

- **Code patterns, conventions, architecture, file paths, or project structure** — derivable from the current project state.
- **Git history, recent changes, or who-changed-what** — `git log` / `git blame` are authoritative.
- **Debugging solutions or fix recipes** — the fix is in the code; the commit message has the context.
- **Anything already documented in CLAUDE.md files** — duplication causes drift.
- **Ephemeral task details** — in-progress work, temporary state, conversation context.

These exclusions apply even when the user asks. If asked to save a PR list or activity summary, ask what was *surprising* or *non-obvious* about it — that's the part worth keeping.

## Verify before recommending

Memory records become stale over time. A memory naming a specific function, file, or flag is a claim that it existed *when the memory was written*. Before recommending it:

- If the memory names a file path: check the file exists.
- If the memory names a function or flag: grep for it.
- If the user is about to act on a recommendation (not just asking about history), verify first.

A memory that summarizes repo state (activity logs, architecture snapshots) is frozen in time. If the user asks about *recent* or *current* state, prefer `git log` or reading the code over recalling the snapshot.

## Memory vs plan vs task vs plugin compaction

Memory is one of several persistence mechanisms. Use the right one:

| Mechanism | Scope | When to use |
|---|---|---|
| **Memory** (auto-memory files) | Cross-conversation | Facts that should apply in future sessions: user identity, feedback rules, project state, external references |
| **Plan** (in-conversation plan from `/superpowers:writing-plans` or `EnterPlanMode`) | Current conversation | Multi-step approach the user has approved before implementation |
| **Task** (`TaskCreate` / `TaskUpdate` / `TaskList`) | Current conversation | Tracking discrete steps within the current implementation |
| **Plugin compaction** ([`plugin/references/compaction.md`](../../plugin/references/compaction.md)) | Plugin-internal state | Plugin's own summarization of its state — distinct from agent memory; do not modify from outside the plugin |

If you're tempted to save in-conversation state to memory, use Tasks. If you're tempted to save planning decisions to memory, use a Plan. Memory is the slow-and-durable mechanism; tasks and plans are the fast-and-ephemeral mechanisms.

Plugin compaction is a separate concern: it's the plugin's own internal-state summarization, not agent memory, and follows its own rules.

## Further reading

- [Getting Started](getting-started.md) — basic setup walkthrough
- [CLAUDE.md Guide](claude-md-guide.md) — writing project instructions that complement memory
- [Verification Discipline](../../plugin/references/verification-discipline.md) — verify-before-recommending applied operationally
- [External-Integration Capability Governance](../../plugin/references/external-integration-governance.md) — governing an *external* retriever/memory connected alongside in-context memory
