# templates/ — TaskFlow Reference Examples

This directory contains filled configuration examples (`CLAUDE.md`, `.claude/settings.json`, rules, hooks, agents, skills) for a fictional project called **TaskFlow** — a task-management REST API used throughout this repo as a reference.

## About TaskFlow

TaskFlow is **not a specific tech stack**. It is a conceptual project:

- A REST API for task management (users, tasks, comments)
- Persistent storage and session caching
- Authentication, input validation, structured error handling
- Typical backend concerns: rate limiting, database migrations, automated tests

The same fictional project is referenced in the guides, in `plugin/skills/create/SKILL.md`, and in all example code snippets. This keeps documentation cross-references simple — you only need to learn one imaginary project to understand every example in this repo.

## About the current filled examples

The current templates under `starter/` and `advanced/` use **Node.js / Express / TypeScript / PostgreSQL / Redis / Jest** as a concrete illustration. This is **not** a commitment to Node/Express as the "default" stack. It is one implementation chosen because:

- Node/Express is a well-known starting point for REST APIs
- Cross-references to specific files (`src/api/`, `src/services/`, `src/repos/`) are easier to write when there is one shared example
- The ecosystem has stable, widely-understood tooling (npm, Jest, ESLint, TypeScript)

**If your actual stack is different, that is the expected case.** When you run:

```text
> /guardians-of-the-claude:create
```

Claude Code adapts to your actual project by:

1. **Detecting existing manifests** — `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `Gemfile`, and others
2. **Asking stack questions** when the project is empty — language, framework, build/test/lint commands
3. **Generating equivalent commands** — `pytest` instead of `npm test`, `ruff check` instead of `eslint`, `cargo build` instead of `npm run build`, and so on

The generated `CLAUDE.md` follows the same section structure as these templates but with commands and paths that match your actual stack.

## Why no per-stack variants?

This repo intentionally does **not** maintain `templates/python/`, `templates/go/`, `templates/nextjs/`, or similar per-stack directories. Reasons:

- **Maintenance scales linearly** with the number of stacks, and independently with each stack's ecosystem updates (new framework versions, new lint tools, new test runners)
- **Stacks evolve faster than documentation** — a six-month-old filled template is already partly misleading, and users cannot tell which parts are current
- **The real product is `/create`** — Claude adapts at runtime in a way that static templates cannot match. Static templates are a starting point for reading; `/create` is a starting point for building
- **Maintainer capacity is finite** — one high-quality example beats five half-maintained ones

See [`docs/ROADMAP.md`](../docs/ROADMAP.md) for the project direction and the "Stack-adaptive improvements" backlog item.

## How to read these templates

**Do** look at:

- Section structure (what sections a `CLAUDE.md` should have)
- Patterns (how rules are split, how agents are scoped, how hooks are wired)
- Conventions (naming, commit style, verification gates, review gates)
- The **why** behind each choice (documented in comments or in guide cross-references)

**Do not** copy verbatim:

- Exact `npm` / `Jest` commands — substitute your stack's equivalents
- Node-specific paths (`src/api/`, `src/services/`, `src/repos/`) — use your project's layout
- Package-specific code in examples (`asyncHandler`, Zod schemas, `ts-jest` setup) — use your stack's equivalents

If you want a guided generation instead of reading a reference, run `/guardians-of-the-claude:create` and Claude will produce a tailored `CLAUDE.md` and `settings.json` for your actual project.
