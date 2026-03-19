---
title: "Writing Effective CLAUDE.md Files"
description: "How to write, organize, and maintain CLAUDE.md files for Claude Code"
date: 2026-03-18
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

This keeps your root CLAUDE.md focused on project-wide instructions while providing deeper context exactly where it is needed. See `examples/src/CLAUDE.md` and `examples/tests/CLAUDE.md` for working examples.

## Writing Principles

- **Target under 200 lines.** This is a soft guideline, not a hard cap. Claude loads the entire file regardless of length, but shorter files produce better adherence to your instructions.
- **Use markdown headers and bullets.** Structure makes instructions scannable for both Claude and humans.
- **Be specific and verifiable.** Write "Use 2-space indentation" not "Format code properly." Write "Run `npm test` to verify" not "Make sure it works."
- **Avoid conflicting instructions.** If your CLAUDE.md says one thing and a rule file says another, Claude may follow either. Audit for contradictions.

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
# References
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

## Pruning Your CLAUDE.md

Treat your CLAUDE.md like code -- review it regularly and prune aggressively.

For each line, ask: **"Would removing this cause Claude to make mistakes?"** If the answer is no, cut it. A bloated CLAUDE.md causes Claude to dilute attention across too many instructions, and important rules get lost in the noise.

When a rule is critical, add emphasis to make it stand out:

- "IMPORTANT: Never commit directly to main"
- "YOU MUST run the test suite before committing"

Reserve emphasis for rules that truly matter. If everything is marked IMPORTANT, nothing is.

## Common Mistakes

1. **Too long** -- A 500-line CLAUDE.md means Claude pays less attention to each line. Split into [rules files](rules-guide.md) or prune.
2. **Too vague** -- "Follow best practices" tells Claude nothing. "Use factories for test data, never inline objects" tells Claude exactly what to do.
3. **Conflicting instructions** -- Your CLAUDE.md says "use default exports" but a rule file says "use named exports." Audit all files together.
4. **Stating the obvious** -- Claude already knows standard language conventions, how to write functions, and common library APIs. Focus on what is unique to your project.

## The /init Shortcut

If you are starting from scratch, Claude can generate a CLAUDE.md for you:

```text
claude
> /init
```

Claude analyzes your codebase and produces a starting CLAUDE.md based on what it finds. This is the officially recommended starting point per [best practices](https://code.claude.com/docs/en/best-practices).

For a more interactive experience with a multi-phase flow, set the environment variable before launching:

```bash
CLAUDE_CODE_NEW_INIT=true claude
> /init
```

Either way, treat the output as a draft. Review it, merge in sections from our templates, and prune anything unnecessary.
