---
title: "Claude-Code-Templates Design Spec"
description: "A structured template repository that provides blank scaffolds and filled examples for Claude Code's core configuration files, along with documentation guides."
date: 2026-03-18
status: draft
---

# Claude-Code-Templates Design Spec

## 1. Overview

Claude-Code-Templates is a structured template repository for developers new to Claude Code. Users clone the repo and copy scaffold files into their own projects, using filled examples as a reference. The project is language/framework agnostic, English-only, and scoped to core configuration (CLAUDE.md, settings, rules, directory structure).

### Goals

- Provide a clone-and-go starting point for Claude Code beginners
- Teach the Claude Code memory system through realistic, filled examples
- Keep scope focused on core configuration — no hooks, MCP, skills, or advanced workflows

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
    └── directory-structure-guide.md       ← .claude/ folder, auto memory, logs
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
6. **Docs Index** — links to each guide in `docs/`
7. **Contributing + License**

Target length: under 100 lines.

## 4. Templates (Blank Scaffolds)

All markdown files include YAML frontmatter with at minimum `title` and `description` fields.

### 4.1 `templates/CLAUDE.md`

Root project-level scaffold with commented section headers:

- Project Overview
- Build & Run
- Testing
- Code Style & Conventions
- Project Structure
- Important Context
- References (demonstrating @import syntax)

Each section contains HTML comments guiding the user on what to fill in, with concrete prompts (e.g., "What command builds your project?").

### 4.2 `templates/.claude/CLAUDE.md`

Minimal scaffold noting this is the alternative location. Explains that users should choose EITHER root or `.claude/` — not both.

### 4.3 `templates/.claude/settings.json`

Near-empty JSON with a comment pointing to `docs/settings-guide.md`:

```jsonc
{
  // See docs/settings-guide.md for all available options
}
```

### 4.4 `templates/.claude/rules/*.md`

Three scaffold files:

- **`code-style.md`** — no frontmatter paths (loads always), sections for naming, formatting, imports
- **`testing.md`** — no frontmatter paths, sections for test framework, coverage, patterns
- **`path-specific-example.md`** — includes `paths` frontmatter to demonstrate glob scoping

### 4.5 `templates/subdirectory-claude-md/CLAUDE.md`

Scaffold for folder-level lazy-loaded CLAUDE.md. Contains:

- HTML comment explaining lazy loading behavior
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

Brief example showing the alternative location with a note about choosing one location.

### 5.3 `examples/.claude/settings.json`

Shows the most common beginner use case — pre-approving safe commands:

```json
{
  "permissions": {
    "allow": [
      "npm test",
      "npm run lint",
      "npm run build"
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

Action-oriented onboarding walkthrough (~80 lines):

1. Prerequisites — Claude Code installed, a project to configure
2. Copy the templates — which files to copy where, with exact commands
3. Fill in your CLAUDE.md — walk through each section
4. Set up rules (optional) — when to use `.claude/rules/` vs keeping everything in CLAUDE.md
5. Verify it works — launch Claude Code, run `/memory` to confirm files are loaded
6. What's next — links to other guides

### 6.2 `docs/claude-md-guide.md`

Deep dive on writing effective CLAUDE.md files:

- The hierarchy — managed policy → project root → user, with precedence diagram
- Two locations — `./CLAUDE.md` vs `./.claude/CLAUDE.md`, when to use which
- Folder-level CLAUDE.md — lazy loading behavior, when Claude discovers them
- Writing principles — under 200 lines, specific/verifiable, structured with headers
- The `@import` syntax — referencing external files, path resolution, personal imports
- Common mistakes — too long, too vague, conflicting instructions
- The `/init` shortcut — Claude can auto-generate a starting CLAUDE.md

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
- Key options for beginners — `permissions.allow`, `permissions.deny`, `autoMemoryEnabled`, `claudeMdExcludes`
- What NOT to put in project settings — security-restricted options like `autoMemoryDirectory`

### 6.5 `docs/directory-structure-guide.md`

Maps the `.claude/` ecosystem:

- `.claude/` directory — contents: CLAUDE.md, settings.json, settings.local.json, rules/
- Auto memory — `~/.claude/projects/<project>/memory/`, MEMORY.md index, topic files, 200-line cap
- What to .gitignore — `settings.local.json` yes; `settings.json` and `rules/` no (team-shared)
- The distinction — CLAUDE.md = what you tell Claude; auto memory = what Claude tells itself; settings = behavior configuration

## 7. Cross-Cutting Concerns

### Frontmatter

Every markdown file in the project includes YAML frontmatter. Minimum fields:

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
