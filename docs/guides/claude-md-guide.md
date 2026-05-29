---
title: "Writing Effective CLAUDE.md Files"
description: "How to write, organize, and maintain CLAUDE.md files for Claude Code"
version: 1.4.3
---

# Writing Effective CLAUDE.md Files

## What Is CLAUDE.md?

CLAUDE.md is a markdown file containing persistent instructions that Claude reads at the start of every session. It is not enforced configuration -- it is context that shapes Claude's behavior. Think of it as a briefing document: the better you write it, the better Claude performs in your project.

## The Hierarchy

Claude loads instructions from multiple locations, with more specific scopes taking precedence over broader ones:

| Scope | Location | Purpose |
| ------- | ---------- | --------- |
| Managed policy | Platform-specific system paths | Organization-wide instructions set by admins |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team-shared project instructions (committed to git) |
| User | `~/.claude/CLAUDE.md` | Personal preferences applied to all projects |

When instructions conflict, more specific locations win. A project-level rule overrides a user-level preference. Managed policies set by your organization take highest priority.

## Two Locations for Project Instructions

You can place your project CLAUDE.md in either of two locations:

- **`./CLAUDE.md`** (project root) -- Visible at a glance. Anyone browsing the repo sees it immediately.
- **`./.claude/CLAUDE.md`** -- Keeps your project root cleaner. Good for repos that already have many root-level config files.

**Pick one, not both.** Claude loads both if they exist, and instructions may conflict. The root location is more common and what `/init` generates.

## Folder-Level CLAUDE.md

You can place a CLAUDE.md in any subdirectory. These files are lazy-loaded: Claude reads them only when it accesses files in that directory.

Use folder-level files for context that is specific to one part of your project:

- `src/CLAUDE.md` -- source code conventions
- `tests/CLAUDE.md` -- testing patterns and helpers
- `docs/CLAUDE.md` -- documentation standards

This keeps your root CLAUDE.md focused on project-wide instructions while providing deeper context exactly where it is needed. Alternatively, consider using `.claude/rules/` files for path-scoped instructions -- see the [Rules Guide](rules-guide.md).

## Writing Principles

- **Target under 200 lines.** This is a soft guideline, not a hard cap. Claude loads the entire file regardless of length, but shorter files produce better adherence to your instructions. Long contexts also interact with a documented phenomenon ("context rot") in which model recall from long contexts degrades as context fills — keeping CLAUDE.md short reduces unnecessary context pressure.
- **Use markdown headers and bullets.** Structure makes instructions scannable for both Claude and humans.
- **Be specific and verifiable.** Write "Use 2-space indentation" not "Format code properly." Write "Run `npm test` to verify" not "Make sure it works."
- **Avoid conflicting instructions.** If your CLAUDE.md says one thing and a rule file says another, Claude may follow either. Audit for contradictions.
- **Prefer model-agnostic rules.** Write rules that hold regardless of which Claude model runs them. If a rule genuinely depends on model-specific behavior, name the model/version it targets and revisit it when `/audit` reports model drift — a broadly-worded instruction tuned to one model can degrade others (Anthropic's [Apr 2026 postmortem](https://www.anthropic.com/engineering/april-23-postmortem)).

## Identity-DNA

The top of CLAUDE.md should declare *what Claude is* in your project. This identity-DNA stabilizes voice across long sessions and prevents drift toward generic-assistant behavior. It has four parts: a role declaration, a mental model for the user, a mental model for the agent, and a deliverable invariant.

**Role declaration template:**

```markdown
You are a [role] working on [project]. Your job is to [primary outcome].
You write [deliverable], not commentary about deliverables.
```

For TaskFlow: "You are a Rust backend engineer working on TaskFlow. Your job is to ship correct, tested code that fits the existing service-repository-handler layering. You write code and migrations, not explanations about what you would write."

**Mental model for the user.** Describes who the user is to Claude. Example: "The user is your collaborator with domain authority. They catch design errors you miss because they hold context you can't see — deadlines, prior incidents, stakeholder pressure. Read their requests for what they're actually trying to achieve, not just the literal ask."

**Mental model for the agent.** Describes how Claude should hold its own role. Example: "You are embedded in this project, not visiting it. Code you read is the spec; conventions you encounter are the law. You don't 'answer questions about' the codebase — you change the codebase. When uncertain, read more files before guessing."

**Deliverable invariant.** Names what the primary artifact is and what chat is for. Example: "The code, document, or migration you produce is the primary artifact. Chat is the cover note — terse status, blockers, what's next." This invariant takes different forms per surface: CLI ships as file diffs (chat is short), mobile ships as answer paragraphs (chat IS the answer), document-embedded ships as document edits (chat is the cover note).

## What to Include vs Exclude

This is the most important decision when writing your CLAUDE.md:

| Include | Exclude |
| --------- | --------- |
| Bash commands Claude cannot guess | Anything Claude can figure out by reading code |
| Code style rules that differ from defaults | Standard language conventions Claude already knows |
| Testing instructions and preferred test runners | Detailed API documentation (link to docs instead) |
| Repository etiquette (branch naming, PR conventions) | Information that changes frequently |
| Architectural decisions specific to your project | Long explanations or tutorials |
| Dev environment quirks (required env vars, services) | File-by-file descriptions of the codebase |
| Common gotchas or non-obvious behaviors | Self-evident practices like "write clean code" |

The rule of thumb: if Claude would make a mistake without this information, include it. If Claude would figure it out on its own, leave it out.

## The @import Syntax

Reference external files to keep your CLAUDE.md focused while linking to deeper context:

```markdown
## References
See @README.md for project overview
@docs/architecture.md
@docs/api-conventions.md
```

Key details:

- **Relative paths** resolve from the file containing the `@import`: `@docs/guide.md`
- **Absolute paths** start from the filesystem root: `@/home/user/notes.md`
- **Personal imports** reference your home directory: `@~/.claude/my-project-instructions.md`
- **Max depth** is 5 hops -- an imported file can import another, up to 5 levels deep.

Use `@import` to point Claude at existing documentation rather than duplicating content in your CLAUDE.md.

## Organizing at Scale

When your project has multiple skills and agents, add quick-reference tables to your CLAUDE.md listing each skill's name/purpose and each agent's name/model/role. This helps Claude discover what is available without browsing directories. Keep definitions in their respective files -- the CLAUDE.md table is just a reference.

## Pruning Your CLAUDE.md

Treat your CLAUDE.md like code -- review it regularly and prune aggressively.

For each line, ask: **"Would removing this cause Claude to make mistakes?"** If the answer is no, cut it. A bloated CLAUDE.md causes Claude to dilute attention across too many instructions, and important rules get lost in the noise.

When a rule is critical, add emphasis to make it stand out:

- "IMPORTANT: Never commit directly to main"
- "YOU MUST run the test suite before committing"

Reserve emphasis for rules that truly matter. If everything is marked IMPORTANT, nothing is.

**Which rules earn that emphasis?** Match a rule's *form* to the cost of getting it wrong. When an error would be costly enough that you want guaranteed, predictable compliance rather than a judgment call -- deleting data, committing secrets, skipping tests before a release -- write the rule as a rigid directive (`IMPORTANT` / `YOU MUST` / `never`). Otherwise, prefer a rule that states the *why* and lets Claude's judgment adapt: rigid rules cannot anticipate every situation, and the rationale is what lets Claude apply the rule to a case you did not foresee. Anthropic's [constitution](https://www.anthropic.com/constitution) makes the same trade-off -- favoring "good values and judgment over strict rules," and reserving fixed rules for when "the costs of errors are severe enough that predictability and evaluability become critical." Either way, explain the rule (see the [Trustworthy Agents Guide](trustworthy-agents-guide.md)) -- even a rigid directive works better with its reason attached.

## Updating Mid-Session

Two mechanisms keep CLAUDE.md responsive to what you learn during a session:

- **Direct prompt + `/memory`** — When you discover a rule mid-session (e.g., "always run `npm run typecheck` after edits"), tell Claude directly: `"add this to CLAUDE.md"` or `"remember this"`. Claude saves to CLAUDE.md or auto memory as appropriate. Run `/memory` to browse, open, and edit memory files. For the auto-memory entry schema — four types, frontmatter, `MEMORY.md` index format, and verify-before-recommending discipline — see the [Memory Patterns Guide](memory-patterns-guide.md). See also the [official memory docs](https://code.claude.com/docs/en/memory) for auto memory's storage location and toggle.
- **Custom compaction directives** — Embed instructions inside CLAUDE.md that survive auto-compaction. Example: `"When compacting, always preserve the full list of modified files and any test commands."` Because the directive lives in CLAUDE.md, it reloads every session and applies whenever compaction triggers.

## Common Mistakes

1. **Too long** -- A 500-line CLAUDE.md means Claude pays less attention to each line. Split into [rules files](rules-guide.md) or prune.
2. **Too vague** -- "Follow best practices" tells Claude nothing. "Use factories for test data, never inline objects" tells Claude exactly what to do.
3. **Conflicting instructions** -- Your CLAUDE.md says "use default exports" but a rule file says "use named exports." Audit all files together.
4. **Stating the obvious** -- Claude already knows standard language conventions, how to write functions, and common library APIs. Focus on what is unique to your project.

## The /init Shortcut

If you are starting from scratch, run `/init` inside Claude Code. Claude analyzes your codebase and produces a starting CLAUDE.md. This is the officially recommended starting point per [best practices](https://code.claude.com/docs/en/best-practices). Treat the output as a draft -- review it, merge in sections from our templates, and prune anything unnecessary.
