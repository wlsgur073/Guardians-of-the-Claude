---
title: "Claude-Code-Templates Design Spec"
description: "A structured template repository that provides blank scaffolds and filled examples for Claude Code's core configuration files, along with documentation guides."
date: 2026-03-18
status: draft
---

# Claude-Code-Templates Design Spec

## 1. Overview

Claude-Code-Templates is a structured template repository for developers new to Claude Code. Users clone the repo and copy scaffold files into their own projects, using filled examples as a reference. The project is language/framework agnostic, English-only, and scoped to core configuration (CLAUDE.md, settings, rules, directory structure) plus essential usage patterns sourced from official documentation.

### Goals

- Provide a clone-and-go starting point for Claude Code beginners
- Teach the Claude Code memory system through realistic, filled examples
- Cover essential day-one usage patterns (context management, session management, effective prompting) sourced from official best practices
- Keep scope focused on core configuration + fundamental usage — no hooks, MCP, skills, or advanced workflows

### Audience

Developers who are brand new to Claude Code and need a starter template they can clone and use immediately.

## 2. Repository Structure

```
Claude-Code-Templates/
├── README.md                              ← Overview, philosophy, quick start
├── LICENSE                                ← MIT (existing)
├── .gitignore
│
├── templates/                             ← Blank scaffolds to copy
│   ├── CLAUDE.md                          ← Project-level scaffold (root)
│   ├── .claude/
│   │   ├── CLAUDE.md                      ← Alternative project-level location
│   │   ├── settings.json                  ← Settings scaffold
│   │   └── rules/
│   │       ├── code-style.md              ← Scaffold: coding conventions
│   │       ├── testing.md                 ← Scaffold: test policies
│   │       └── path-specific-example.md   ← Scaffold: with paths frontmatter
│   ├── subdirectory-claude-md/
│   │   └── CLAUDE.md                      ← Scaffold for folder-level lazy loading
│   └── .gitignore                         ← Claude-specific ignore patterns
│
├── examples/                              ← Filled reference versions
│   ├── CLAUDE.md                          ← Realistic root CLAUDE.md with @imports
│   ├── .claude/
│   │   ├── CLAUDE.md                      ← Example alternative location
│   │   ├── settings.json                  ← Example with permissions config
│   │   └── rules/
│   │       ├── code-style.md              ← Example: filled style rules
│   │       ├── testing.md                 ← Example: filled test conventions
│   │       └── api-endpoints.md           ← Example: path-scoped to src/api/**
│   ├── src/
│   │   └── CLAUDE.md                      ← Example: lazy-loaded source conventions
│   └── tests/
│       └── CLAUDE.md                      ← Example: lazy-loaded test conventions
│
└── docs/
    ├── getting-started.md                 ← Step-by-step setup walkthrough
    ├── claude-md-guide.md                 ← Writing effective CLAUDE.md files
    ├── rules-guide.md                     ← .claude/rules/ usage & path-scoping
    ├── settings-guide.md                  ← settings.json options explained
    ├── directory-structure-guide.md       ← .claude/ folder, auto memory, logs
    └── effective-usage-guide.md           ← Essential day-one usage patterns
```

## 3. README.md

The README serves as the entry point. Contents:

1. **One-liner** — what this repo is and who it's for
2. **Tree diagram** — simplified visual of the repository structure
3. **Quick Start (3 steps):**
   1. Clone this repo
   2. Copy `templates/` files into your project
   3. Fill in the scaffolds using `examples/` as reference
4. **What's Inside** — table mapping directories to purposes
5. **How Claude Code Memory Works** — short conceptual overview:
   - The layered hierarchy: managed policy → project → user
   - CLAUDE.md vs `.claude/rules/` vs auto memory
   - Key insight: CLAUDE.md is what you tell Claude; auto memory is what Claude tells itself
6. **The #1 Rule** — one sentence: "Give Claude a way to verify its work — include test commands, lint commands, and build commands in your CLAUDE.md."
7. **Docs Index** — links to each guide in `docs/`, including the new `effective-usage-guide.md`
8. **Contributing + License**

Target length: under 120 lines (expanded to accommodate the verification callout).

## 4. Templates (Blank Scaffolds)

Template scaffolds do NOT include YAML frontmatter — they are meant to be copied directly into user projects, so they should not contain repo-specific metadata that users would need to remove. Scaffolds use HTML comments for in-file guidance instead.

### 4.1 `templates/CLAUDE.md`

Root project-level scaffold with commented section headers:

- Project Overview
- Build & Run
- Testing
- Code Style & Conventions
- Project Structure
- Important Context
- References (demonstrating @import syntax)

Each section contains 1-2 HTML comments guiding the user on what to fill in, with concrete prompts. Examples:

- Project Overview: `<!-- Brief description: what does your project do? Primary language/framework? -->`
- Build & Run: `<!-- What commands build and run your project? e.g., npm install && npm run dev -->`
- Testing: `<!-- How do you run tests? e.g., npm test, pytest, go test ./... -->`
- Code Style & Conventions: `<!-- Be specific: "Use 2-space indentation" not "Format code properly" -->`
- Project Structure: `<!-- List key directories and their purposes -->`
- Important Context: `<!-- Anything Claude should know that isn't obvious from the code -->`
- References: `<!-- Link detailed docs: @docs/architecture.md, @docs/api-design.md -->`

### 4.2 `templates/.claude/CLAUDE.md`

Minimal scaffold noting this is the alternative location. Explains that users should choose EITHER root or `.claude/` — not both. Provides a decision rule: use root `./CLAUDE.md` if you want the file visible at a glance; use `.claude/CLAUDE.md` if you prefer a cleaner project root.

### 4.3 `templates/.claude/settings.json`

Valid JSON with the `$schema` field for editor autocomplete and an empty permissions block as a starting point:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [],
    "deny": []
  }
}
```

JSON does not support comments, so the scaffold relies on the `$schema` field for discoverability and the `docs/settings-guide.md` guide for explanation.

### 4.4 `templates/.claude/rules/*.md`

Three scaffold files:

- **`code-style.md`** — no frontmatter paths (loads always), sections for naming, formatting, imports
- **`testing.md`** — no frontmatter paths, sections for test framework, coverage, patterns
- **`path-specific-example.md`** — includes `paths` frontmatter to demonstrate glob scoping

### 4.5 `templates/subdirectory-claude-md/CLAUDE.md`

Scaffold for folder-level lazy-loaded CLAUDE.md. The directory name `subdirectory-claude-md` is a placeholder — users should rename it to match their actual project directory (e.g., `src/`, `tests/`, `lib/`). The getting-started guide (Section 6.1) will explain this with an example copy command:

```bash
cp templates/subdirectory-claude-md/CLAUDE.md your-project/src/CLAUDE.md
```

Contains:

- HTML comment explaining lazy loading behavior and the rename instruction
- Section headers: Directory Purpose, Conventions

### 4.6 `templates/.gitignore`

Claude-specific patterns:

```
# Claude Code local settings (personal, not for version control)
.claude/settings.local.json
```

## 5. Examples (Filled Reference Versions)

All examples use a fictional "TaskFlow" project (REST API for task management, Node.js/Express, PostgreSQL, Redis) to create a coherent, believable reference. All markdown files include YAML frontmatter.

### 5.1 `examples/CLAUDE.md`

Realistic root CLAUDE.md demonstrating:

- Concrete, verifiable instructions (not vague)
- Under 200 lines total
- `@import` syntax for referencing detailed docs
- Section structure matching the scaffold exactly

### 5.2 `examples/.claude/CLAUDE.md`

A short demonstration stub (not a full second example) showing what the alternative location looks like. Contains a brief note explaining this is the `.claude/` placement option, paired with `examples/CLAUDE.md` (the root placement option) to form a "pick one" demonstration pair. The root version is the fully realized example; this file is intentionally minimal.

### 5.3 `examples/.claude/settings.json`

Shows the most common beginner use case — pre-approving safe commands. Uses the correct permission rule syntax `Tool(specifier)` per the [official docs](https://code.claude.com/docs/en/settings):

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(npm test)",
      "Bash(npm run lint)",
      "Bash(npm run build)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)"
    ]
  }
}
```

### 5.4 `examples/.claude/rules/`

Three filled files:

- **`code-style.md`** — TypeScript conventions, naming, formatting
- **`testing.md`** — Jest practices, real database usage, factory pattern
- **`api-endpoints.md`** — path-scoped to `src/api/**/*.ts`, demonstrates Zod validation, response helpers, asyncHandler pattern

### 5.5 `examples/src/CLAUDE.md` and `examples/tests/CLAUDE.md`

Short, focused folder-level files (5-10 lines each) showing lazy-loading in practice.

## 6. Documentation Guides

Each guide is standalone — readable without the others, with cross-references linking between them. All include YAML frontmatter with `title`, `description`, and `date` fields.

### 6.1 `docs/getting-started.md`

Action-oriented onboarding walkthrough (~100 lines):

1. Prerequisites — Claude Code installed, a project to configure
2. **Run `/init` first** — Claude analyzes your codebase and auto-generates a starting CLAUDE.md. This is the officially recommended first step per [best practices](https://code.claude.com/docs/en/best-practices). Our templates fill gaps that `/init` misses, not replace it.
3. Copy the templates — which files to copy where, with exact commands. Explain that `/init` output and our templates are complementary: merge them.
4. Fill in your CLAUDE.md — walk through each section, referencing the include/exclude table in `claude-md-guide.md`
5. Set up rules (optional) — when to use `.claude/rules/` vs keeping everything in CLAUDE.md
6. Configure permissions — brief intro to `.claude/settings.json` with a link to `settings-guide.md`
7. Verify it works — launch Claude Code, run `/memory` to confirm files are loaded, try a simple task
8. What's next — links to `effective-usage-guide.md` and other guides

### 6.2 `docs/claude-md-guide.md`

Deep dive on writing effective CLAUDE.md files:

- The hierarchy — managed policy → project root → user, with precedence diagram
- Two locations — `./CLAUDE.md` vs `./.claude/CLAUDE.md`, when to use which
- Folder-level CLAUDE.md — lazy loading behavior, when Claude discovers them
- Writing principles — under 200 lines, specific/verifiable, structured with headers
- **What to include vs exclude** — adapted from [best practices](https://code.claude.com/docs/en/best-practices):

  | Include | Exclude |
  |---------|---------|
  | Bash commands Claude can't guess | Anything Claude can figure out by reading code |
  | Code style rules that differ from defaults | Standard language conventions Claude already knows |
  | Testing instructions and preferred test runners | Detailed API documentation (link to docs instead) |
  | Repository etiquette (branch naming, PR conventions) | Information that changes frequently |
  | Architectural decisions specific to your project | Long explanations or tutorials |
  | Dev environment quirks (required env vars) | File-by-file descriptions of the codebase |
  | Common gotchas or non-obvious behaviors | Self-evident practices like "write clean code" |

- The `@import` syntax — referencing external files, path resolution, personal imports
- **Pruning your CLAUDE.md** — treat it like code: review when things go wrong, prune regularly. For each line, ask: "Would removing this cause Claude to make mistakes?" If not, cut it. Bloated CLAUDE.md files cause Claude to ignore actual instructions. You can add emphasis (e.g., "IMPORTANT" or "YOU MUST") for critical rules.
- Common mistakes — too long, too vague, conflicting instructions, putting things Claude can already infer
- The `/init` shortcut — Claude can auto-generate a starting CLAUDE.md. Mention `CLAUDE_CODE_NEW_INIT=true` for the interactive multi-phase flow.

### 6.3 `docs/rules-guide.md`

Focused on `.claude/rules/`:

- When to use rules vs CLAUDE.md
- File structure — one topic per file, descriptive filenames, subdirectory organization
- Path-scoping — the `paths` frontmatter, glob pattern table, when rules load
- User-level rules — `~/.claude/rules/` for personal cross-project preferences
- Sharing rules — symlinks for cross-project reuse

### 6.4 `docs/settings-guide.md`

Explains settings.json:

- Settings file locations — project, local, user, managed policy
- What goes where — project for team-shared, local for personal overrides, merge behavior
- Key options for beginners — `permissions.allow`, `permissions.deny` (using `Tool(specifier)` syntax per [permission rule syntax](https://code.claude.com/docs/en/permissions#permission-rule-syntax)), `autoMemoryEnabled` (per [auto memory docs](https://code.claude.com/docs/en/memory#enable-or-disable-auto-memory)), `claudeMdExcludes` (per [memory docs](https://code.claude.com/docs/en/memory#exclude-specific-claudemd-files))
- The `$schema` field — point to `https://json.schemastore.org/claude-code-settings.json` for editor autocomplete
- What NOT to put in project settings — security-restricted options like `autoMemoryDirectory`

### 6.5 `docs/directory-structure-guide.md`

Maps the `.claude/` ecosystem:

- `.claude/` directory — contents: CLAUDE.md, settings.json, settings.local.json, rules/
- Auto memory — `~/.claude/projects/<project>/memory/`, MEMORY.md index, topic files, 200-line cap
- What to .gitignore — `settings.local.json` yes; `settings.json` and `rules/` no (team-shared)
- The distinction — CLAUDE.md = what you tell Claude; auto memory = what Claude tells itself; settings = behavior configuration

### 6.6 `docs/effective-usage-guide.md`

Essential day-one usage patterns that complement the configuration guides. Sourced from [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works) and [Best practices](https://code.claude.com/docs/en/best-practices). Covers usage fundamentals, not advanced features.

**The #1 constraint: context window**

- Claude's context window holds your conversation, file contents, command outputs, CLAUDE.md, and system instructions. It fills up fast.
- Performance degrades as context fills — Claude may "forget" earlier instructions or make more mistakes.
- This is WHY configuration matters: a well-written CLAUDE.md reduces wasted context; good session habits keep context clean.

**The #1 practice: give Claude a way to verify its work**

- Include test commands, lint commands, build commands in your CLAUDE.md so Claude can self-check.
- Provide verification criteria in prompts: test cases, expected outputs, screenshots.
- This is the single highest-leverage thing you can do, per the official best practices.

**The recommended workflow: explore → plan → implement → commit**

- Use Plan Mode (`Shift+Tab` twice) to explore the codebase and create a plan before coding.
- Review the plan, then switch to Normal Mode for implementation.
- Skip planning for trivial tasks (typo fixes, log line additions) — planning adds overhead.

**Session management essentials**

- `Esc` — interrupt Claude mid-action. Context is preserved.
- `Esc + Esc` or `/rewind` — rewind to a previous checkpoint (conversation and/or code).
- `/clear` — reset context between unrelated tasks. **Use frequently.**
- `/compact` — summarize conversation to free context. Add focus: `/compact focus on the API changes`.
- `--continue` / `--resume` — pick up where you left off across sessions.

**Permission modes**

- `Shift+Tab` cycles through: Default → Auto-accept edits → Plan mode.
- Default: Claude asks before edits and commands.
- Auto-accept edits: Claude edits freely, still asks for commands.
- Plan mode: read-only tools only, creates a plan you approve before execution.

**Writing effective prompts**

- Be specific upfront: reference files, mention constraints, point to patterns.
- Delegate, don't dictate: give context and direction, let Claude figure out the details.
- Provide rich content: use `@` for files, paste images, pipe data with `cat error.log | claude`.

**Common failure patterns to avoid**

Five anti-patterns from the official best practices:

1. **Kitchen sink session** — mixing unrelated tasks in one session. Fix: `/clear` between tasks.
2. **Correcting over and over** — repeated failed corrections pollute context. Fix: after two failures, `/clear` and write a better initial prompt.
3. **Over-specified CLAUDE.md** — too long, important rules get lost. Fix: ruthlessly prune.
4. **Trust-then-verify gap** — plausible output that doesn't handle edge cases. Fix: always provide verification.
5. **Infinite exploration** — unscoped investigation fills context. Fix: scope narrowly or use subagents.

## 7. Cross-Cutting Concerns

### Frontmatter

Every markdown file in `docs/` and `examples/` includes YAML frontmatter. Scaffold files in `templates/` are an exception — they are starting points the user copies into their own project, so they should NOT include repo-specific frontmatter that the user would need to remove. Instead, template scaffolds use HTML comments for guidance.

For files that do include frontmatter, minimum fields are:

- `title` — document title
- `description` — one-line summary

Additional fields where appropriate:

- `date` — for docs and spec files
- `paths` — for path-scoped `.claude/rules/` files (this is Claude Code functionality, not just metadata)

### Writing Style

- Concise and action-oriented — tell the user what to do, not just what exists
- Specific over vague — "Run `/memory`" not "check your configuration"
- Under 200 lines per markdown file where possible
- Use markdown headers, bullets, and code blocks — not dense paragraphs

### What Is Explicitly Out of Scope

- Hooks configuration
- MCP server setup
- Skills / custom slash commands
- Auto memory templates (Claude writes these — we only explain the system)
- Advanced workflows (subagents, worktrees, multi-AI review)
- Language/framework-specific content
- Non-English translations
