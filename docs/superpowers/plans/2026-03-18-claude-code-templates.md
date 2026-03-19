# Claude-Code-Templates Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a structured template repository with blank scaffolds, filled examples, and documentation guides for Claude Code beginners.

**Architecture:** Three top-level directories (`templates/`, `examples/`, `docs/`) plus root files. Templates are blank scaffolds users copy; examples are filled references using a fictional "TaskFlow" project; docs are standalone guides. No code — all markdown and JSON.

**Tech Stack:** Markdown, JSON, Git

**Spec:** `docs/superpowers/specs/2026-03-18-claude-code-templates-design.md`

---

## File Map

| Action | Path | Responsibility |
| -------- | ------ | ---------------- |
| Create | `templates/CLAUDE.md` | Root project-level scaffold with HTML comment prompts |
| Create | `templates/.claude/CLAUDE.md` | Alternative location scaffold |
| Create | `templates/.claude/settings.json` | Settings scaffold with $schema |
| Create | `templates/.claude/rules/code-style.md` | Code style scaffold |
| Create | `templates/.claude/rules/testing.md` | Testing scaffold |
| Create | `templates/.claude/rules/path-specific-example.md` | Path-scoped rule scaffold |
| Create | `templates/subdirectory-claude-md/CLAUDE.md` | Folder-level lazy-load scaffold |
| Create | `templates/.gitignore` | Claude-specific ignore patterns |
| Create | `examples/CLAUDE.md` | Filled TaskFlow root CLAUDE.md |
| Create | `examples/.claude/CLAUDE.md` | Demo stub for alternative location |
| Create | `examples/.claude/settings.json` | Filled permissions example |
| Create | `examples/.claude/rules/code-style.md` | Filled TypeScript style rules |
| Create | `examples/.claude/rules/testing.md` | Filled Jest testing rules |
| Create | `examples/.claude/rules/api-endpoints.md` | Filled path-scoped API rules |
| Create | `examples/src/CLAUDE.md` | Filled lazy-loaded source conventions |
| Create | `examples/tests/CLAUDE.md` | Filled lazy-loaded test conventions |
| Create | `docs/getting-started.md` | Step-by-step onboarding walkthrough |
| Create | `docs/claude-md-guide.md` | Deep dive on CLAUDE.md files |
| Create | `docs/rules-guide.md` | .claude/rules/ usage guide |
| Create | `docs/settings-guide.md` | settings.json options guide |
| Create | `docs/directory-structure-guide.md` | .claude/ ecosystem map |
| Create | `docs/effective-usage-guide.md` | Day-one usage patterns |
| Create | `.gitignore` | Root .gitignore for the repo itself |
| Create | `README.md` | Project entry point |

---

## Chunk 1: Templates

### Task 1: Root CLAUDE.md scaffold

**Files:**

- Create: `templates/CLAUDE.md`

- [ ] **Step 1: Create the scaffold file**

```markdown
# Project Overview
<!-- Brief description: what does your project do? Primary language/framework? -->

# Build & Run
<!-- What commands build and run your project? e.g., npm install && npm run dev -->

# Testing
<!-- How do you run tests? e.g., npm test, pytest, go test ./... -->
<!-- Include verification commands Claude can use to check its own work -->

# Code Style & Conventions
<!-- Be specific: "Use 2-space indentation" not "Format code properly" -->
<!-- Only include rules that differ from language defaults -->

# Project Structure
<!-- List key directories and their purposes -->
<!-- e.g., src/api/ → API handlers, src/models/ → data models -->

# Important Context
<!-- Anything Claude should know that isn't obvious from the code -->
<!-- e.g., "Redis required for tests", "Auth uses JWT with refresh tokens" -->

# References
<!-- Link detailed docs with @import syntax -->
<!-- e.g., @docs/architecture.md, @docs/api-design.md -->
<!-- For personal preferences: @~/.claude/my-project-instructions.md -->
```

- [ ] **Step 2: Verify the file**

Confirm: no YAML frontmatter (spec Section 4 rule), 7 sections present, each with 1-2 HTML comment prompts, under 30 lines total.

- [ ] **Step 3: Commit**

```bash
git add templates/CLAUDE.md
git commit -m "feat: add root CLAUDE.md scaffold template"
```

### Task 2: .claude/ directory scaffolds

**Files:**

- Create: `templates/.claude/CLAUDE.md`
- Create: `templates/.claude/settings.json`

- [ ] **Step 1: Create the alternative CLAUDE.md scaffold**

```markdown
<!-- ALTERNATIVE LOCATION for project instructions. -->
<!-- Choose ONE location for your main CLAUDE.md: -->
<!--   ./CLAUDE.md         → visible at a glance in your project root -->
<!--   .claude/CLAUDE.md   → keeps your project root cleaner -->
<!-- Do NOT use both — Claude loads both and instructions may conflict. -->

# Project Instructions
<!-- Add your project instructions here if using this location -->
<!-- See the root templates/CLAUDE.md for the recommended section structure -->
```

- [ ] **Step 2: Create the settings.json scaffold**

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [],
    "deny": []
  }
}
```

- [ ] **Step 3: Verify files**

Confirm: `.claude/CLAUDE.md` has no frontmatter, explains the "pick one" decision. `settings.json` is valid JSON (run `python -m json.tool templates/.claude/settings.json` or equivalent).

- [ ] **Step 4: Commit**

```bash
git add templates/.claude/CLAUDE.md templates/.claude/settings.json
git commit -m "feat: add .claude/ directory scaffolds (CLAUDE.md + settings.json)"
```

### Task 3: .claude/rules/ scaffolds

**Files:**

- Create: `templates/.claude/rules/code-style.md`
- Create: `templates/.claude/rules/testing.md`
- Create: `templates/.claude/rules/path-specific-example.md`

- [ ] **Step 1: Create code-style.md scaffold**

```markdown
# Code Style

## Naming Conventions
<!-- e.g., camelCase for variables, PascalCase for classes -->

## Formatting
<!-- e.g., 2-space indentation, max line length 100 -->

## Imports
<!-- e.g., group by: stdlib, external, internal. Use named exports. -->
```

- [ ] **Step 2: Create testing.md scaffold**

```markdown
# Testing Conventions

## Test Framework
<!-- e.g., Jest, pytest, go test -->

## Test Structure
<!-- e.g., mirror src/ directory, use describe/it blocks -->

## Coverage
<!-- e.g., minimum coverage targets, what must be tested -->

## Patterns
<!-- e.g., use factories for test data, prefer integration over mocks -->
```

- [ ] **Step 3: Create path-specific-example.md scaffold**

```markdown
---
paths:
  - "src/api/**/*.{ts,js}"
---
# API Rules
<!-- This file only loads when Claude works with files matching the paths above. -->
<!-- Use this pattern for directory-specific or file-type-specific rules. -->
<!-- Common patterns: "**/*.ts", "src/components/*.tsx", "tests/**/*.test.ts" -->

<!-- Add your path-specific rules here -->
```

- [ ] **Step 4: Verify files**

Confirm: `code-style.md` and `testing.md` have no `paths` frontmatter. `path-specific-example.md` has valid YAML frontmatter with `paths` field. None have `title`/`description` frontmatter (they are scaffolds).

- [ ] **Step 5: Commit**

```bash
git add templates/.claude/rules/
git commit -m "feat: add .claude/rules/ scaffold templates (code-style, testing, path-specific)"
```

### Task 4: Subdirectory CLAUDE.md scaffold and .gitignore

**Files:**

- Create: `templates/subdirectory-claude-md/CLAUDE.md`
- Create: `templates/.gitignore`

- [ ] **Step 1: Create the subdirectory CLAUDE.md scaffold**

```markdown
<!-- FOLDER-LEVEL CLAUDE.md -->
<!-- This file loads ONLY when Claude reads files in this directory. -->
<!-- Use it for context that is specific to this part of your project. -->
<!--  -->
<!-- IMPORTANT: The directory name "subdirectory-claude-md" is a placeholder. -->
<!-- Rename it to match your actual directory, e.g.: -->
<!--   cp templates/subdirectory-claude-md/CLAUDE.md your-project/src/CLAUDE.md -->

# Directory Purpose
<!-- What does this directory contain? What is its role in the project? -->

# Conventions
<!-- Any rules specific to files in this directory -->
<!-- e.g., "All files here export a single class", "Never import from tests/" -->
```

- [ ] **Step 2: Create the .gitignore scaffold**

```gitignore
# Claude Code local settings (personal, not for version control)
.claude/settings.local.json
```

- [ ] **Step 3: Verify files**

Confirm: both files have no frontmatter. Subdirectory CLAUDE.md explains the rename instruction. `.gitignore` contains only Claude-specific patterns.

- [ ] **Step 4: Commit**

```bash
git add templates/subdirectory-claude-md/ templates/.gitignore
git commit -m "feat: add subdirectory CLAUDE.md scaffold and .gitignore template"
```

---

## Chunk 2: Examples

### Task 5: Root CLAUDE.md example (TaskFlow project)

**Files:**

- Create: `examples/CLAUDE.md`

- [ ] **Step 1: Create the filled example**

```markdown
---
title: "TaskFlow CLAUDE.md"
description: "Example root CLAUDE.md for a Node.js/Express REST API project"
---

# Project Overview
TaskFlow is a REST API for task management, built with Node.js and Express.
PostgreSQL for persistence, Redis for session caching.

# Build & Run
npm install
npm run dev          # starts dev server on :3000 with hot reload
npm run build        # compiles TypeScript to dist/

# Testing
npm test             # runs the full Jest test suite
npm run test:watch   # watch mode for development
npm run test:cov     # runs tests with coverage report

Tests require a running PostgreSQL instance (see docker-compose.yml).
Run `docker compose up -d` before running tests.

# Code Style & Conventions
- TypeScript strict mode, 2-space indentation
- Use named exports, not default exports
- Error types extend AppError in src/errors/
- Database queries go in src/repositories/, never in route handlers
- All async route handlers must use the asyncHandler wrapper

# Project Structure
- src/api/         → Express route handlers and middleware
- src/models/      → TypeScript interfaces and Zod validation schemas
- src/repos/       → Database access layer (one file per entity)
- src/services/    → Business logic (called by handlers, calls repos)
- src/errors/      → Custom error types extending AppError
- tests/           → Mirrors src/ structure
- db/migrations/   → SQL migration files (run with npm run migrate)

# Important Context
- Auth uses JWT with refresh tokens stored in Redis
- All API responses follow the envelope format in src/api/response.ts
- Rate limiting is configured per-route in src/api/middleware/rateLimit.ts
- Environment variables are validated at startup via src/config.ts

# References
@docs/architecture.md
@docs/api-conventions.md
@README.md
```

- [ ] **Step 2: Verify the file**

Confirm: has YAML frontmatter with `title` and `description`. Under 50 lines. Uses `@import` syntax. Sections match the scaffold structure. Instructions are concrete and verifiable (not vague).

- [ ] **Step 3: Commit**

```bash
git add examples/CLAUDE.md
git commit -m "feat: add filled CLAUDE.md example (TaskFlow project)"
```

### Task 6: .claude/ directory examples

**Files:**

- Create: `examples/.claude/CLAUDE.md`
- Create: `examples/.claude/settings.json`

- [ ] **Step 1: Create the alternative location demo stub**

```markdown
---
title: "TaskFlow .claude/CLAUDE.md (Alternative Location)"
description: "Demo stub showing the .claude/ placement option for project instructions"
---

<!-- This is the ALTERNATIVE location for project instructions (.claude/CLAUDE.md). -->
<!-- The fully realized example is at examples/CLAUDE.md (root placement). -->
<!-- These two files form a "pick one" pair — use root OR .claude/, not both. -->
<!--  -->
<!-- Choose root ./CLAUDE.md if you want the file visible at a glance. -->
<!-- Choose .claude/CLAUDE.md if you prefer a cleaner project root. -->

# Project Instructions
See the root examples/CLAUDE.md for the full example of what goes here.
```

- [ ] **Step 2: Create the filled settings.json**

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(npm test)",
      "Bash(npm run lint)",
      "Bash(npm run build)",
      "Bash(npm run migrate)",
      "Bash(docker compose up -d)",
      "Bash(git diff *)",
      "Bash(git log *)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ]
  }
}
```

- [ ] **Step 3: Verify files**

Confirm: `CLAUDE.md` has frontmatter, is intentionally minimal (stub). `settings.json` is valid JSON (validate with `node -e "JSON.parse(require('fs').readFileSync('examples/.claude/settings.json','utf8'))"`). Permission rules use `Tool(specifier)` syntax.

- [ ] **Step 4: Commit**

```bash
git add examples/.claude/CLAUDE.md examples/.claude/settings.json
git commit -m "feat: add .claude/ directory examples (stub CLAUDE.md + settings.json)"
```

### Task 7: .claude/rules/ examples

**Files:**

- Create: `examples/.claude/rules/code-style.md`
- Create: `examples/.claude/rules/testing.md`
- Create: `examples/.claude/rules/api-endpoints.md`

- [ ] **Step 1: Create code-style.md example**

```markdown
---
title: "TaskFlow Code Style Rules"
description: "TypeScript conventions for the TaskFlow project"
---

# Code Style

## Naming
- Variables and functions: camelCase
- Classes and interfaces: PascalCase
- Constants: UPPER_SNAKE_CASE
- File names: kebab-case (e.g., `user-service.ts`)
- Database columns: snake_case

## Formatting
- 2-space indentation
- Max line length: 100 characters
- Trailing commas in multiline arrays and objects
- Semicolons required

## Imports
- Group imports: Node builtins, external packages, internal modules
- Use named exports: `export { UserService }` not `export default`
- Use path aliases: `@/services/user-service` not `../../../services/user-service`

## Types
- Prefer interfaces over type aliases for object shapes
- Use Zod schemas as the source of truth; derive TypeScript types with `z.infer`
- Never use `any` — use `unknown` and narrow with type guards
```

- [ ] **Step 2: Create testing.md example**

```markdown
---
title: "TaskFlow Testing Rules"
description: "Jest testing conventions for the TaskFlow project"
---

# Testing Conventions

## Framework
- Jest with ts-jest for unit and integration tests
- Supertest for HTTP endpoint tests

## Structure
- Mirror the `src/` directory: `tests/services/` tests `src/services/`
- Use `describe` blocks grouped by method or behavior
- Test file naming: `<module>.test.ts`

## Data
- Use factories in `tests/factories/` for test data — never create objects inline
- Each factory returns a valid entity by default; override only what the test needs
- Example: `createUser({ email: 'test@example.com' })`

## Database
- Integration tests hit real PostgreSQL — do not mock the database
- Each test file gets a fresh transaction that rolls back after the suite
- Use `tests/helpers/db.ts` for setup and teardown

## Coverage
- Minimum 80% line coverage for src/services/
- All error paths must have at least one test
- Run `npm run test:cov` to check
```

- [ ] **Step 3: Create api-endpoints.md example (path-scoped)**

````markdown
---
title: "TaskFlow API Endpoint Rules"
description: "Rules that apply only when working with API handler files"
paths:
  - "src/api/**/*.ts"
---

# API Endpoint Rules

- All endpoints must validate input with Zod schemas from `src/models/`
- Use the `asyncHandler` wrapper for all route handlers:
  ```typescript
  router.get('/tasks', asyncHandler(async (req, res) => { ... }))
  ```

- Return responses using `sendSuccess()` or `sendError()` from `src/api/response.ts`
- Never call repository methods directly from handlers — go through services
- Include rate limiting for public endpoints via `src/api/middleware/rateLimit.ts`
- All endpoints must be documented with JSDoc tags: `@route`, `@method`, `@auth`

```

- [ ] **Step 4: Verify files**

Confirm: all three have YAML frontmatter with `title` and `description`. `api-endpoints.md` additionally has `paths` field with glob pattern. Content is specific to the fictional TaskFlow project. Each is under 40 lines.

- [ ] **Step 5: Commit**

```bash
git add examples/.claude/rules/
git commit -m "feat: add .claude/rules/ examples (code-style, testing, api-endpoints)"
```

### Task 8: Folder-level CLAUDE.md examples

**Files:**

- Create: `examples/src/CLAUDE.md`
- Create: `examples/tests/CLAUDE.md`

- [ ] **Step 1: Create src/ CLAUDE.md example**

```markdown
---
title: "TaskFlow src/ Conventions"
description: "Lazy-loaded conventions for the TaskFlow source directory"
---

# src/ Conventions
- Business logic lives in `services/`, not in API handlers
- All database access goes through repository classes in `repos/`
- Never import directly from `tests/`
- Each service class handles one entity (e.g., `TaskService`, `UserService`)
- Shared utilities go in `src/utils/` — keep them pure functions
````

- [ ] **Step 2: Create tests/ CLAUDE.md example**

```markdown
---
title: "TaskFlow tests/ Conventions"
description: "Lazy-loaded conventions for the TaskFlow test directory"
---

# Test Conventions
- Mirror the `src/` directory structure
- Use factories in `tests/factories/` for test data — don't create objects inline
- Integration tests hit real PostgreSQL — no mocking the database
- Each test file manages its own transaction rollback via `tests/helpers/db.ts`
- Run a single test file with: `npm test -- tests/services/task-service.test.ts`
```

- [ ] **Step 3: Verify files**

Confirm: both have YAML frontmatter. Both are 5-10 lines of content (short and focused). Content is consistent with the TaskFlow project used elsewhere in examples.

- [ ] **Step 4: Commit**

```bash
git add examples/src/ examples/tests/
git commit -m "feat: add folder-level CLAUDE.md examples (src/ and tests/)"
```

---

## Chunk 3: Documentation Guides

### Task 9: Getting Started guide

**Files:**

- Create: `docs/getting-started.md`

- [ ] **Step 1: Write the guide**

Structure (~100 lines):

````markdown
---
title: "Getting Started"
description: "Step-by-step guide to set up Claude Code configuration for your project"
date: 2026-03-18
---

# Getting Started

## Prerequisites
- Claude Code installed and working (`claude --version`)
- A project you want to configure

## Step 1: Run /init
[Explain that /init is the officially recommended starting point. Claude
analyzes your codebase and auto-generates a CLAUDE.md. Our templates
fill gaps /init misses.]

## Step 2: Copy the Templates
[Exact copy commands for each file. Explain which are required vs optional.]
```bash
# Required: copy the root CLAUDE.md scaffold
cp templates/CLAUDE.md your-project/CLAUDE.md

# Required: copy settings scaffold
mkdir -p your-project/.claude
cp templates/.claude/settings.json your-project/.claude/settings.json

# Optional: copy rules scaffolds
mkdir -p your-project/.claude/rules
cp templates/.claude/rules/*.md your-project/.claude/rules/

# Optional: add folder-level CLAUDE.md to specific directories
cp templates/subdirectory-claude-md/CLAUDE.md your-project/src/CLAUDE.md

# Recommended: add Claude-specific .gitignore entries
cat templates/.gitignore >> your-project/.gitignore
```

[Note: merge /init output with template scaffold — they are complementary.]

## Step 3: Fill in Your CLAUDE.md

[Walk through each section with prompts. Reference the include/exclude
table in claude-md-guide.md.]

## Step 4: Set Up Rules (Optional)

[When to use .claude/rules/ vs keeping everything in CLAUDE.md.
Link to rules-guide.md.]

## Step 5: Configure Permissions

[Brief intro to .claude/settings.json with one example.
Link to settings-guide.md.]

## Step 6: Verify It Works

[Launch Claude Code, run /memory, confirm files are loaded.
Try a simple task to verify.]

## What's Next

[Links to effective-usage-guide.md and all other docs.]

```

- [ ] **Step 2: Verify the guide**

Confirm: has frontmatter with `title`, `description`, `date`. Under 120 lines. Action-oriented with exact commands. References other guides via links. `/init` is Step 1.

- [ ] **Step 3: Commit**

```bash
git add docs/getting-started.md
git commit -m "docs: add getting-started guide"
````

### Task 10: CLAUDE.md Guide

**Files:**

- Create: `docs/claude-md-guide.md`

- [ ] **Step 1: Write the guide**

Structure (~180 lines):

```markdown
---
title: "Writing Effective CLAUDE.md Files"
description: "How to write, organize, and maintain CLAUDE.md files for Claude Code"
date: 2026-03-18
---

# Writing Effective CLAUDE.md Files

## What Is CLAUDE.md?
[One paragraph: persistent instructions Claude reads every session.]

## The Hierarchy
[Managed policy → project root → user. Precedence diagram.
Table with scope, location, purpose for each level.]

## Two Locations
[./CLAUDE.md vs ./.claude/CLAUDE.md. Decision rule:
root = visible at a glance, .claude/ = cleaner project root.]

## Folder-Level CLAUDE.md
[Lazy loading behavior. When Claude discovers them.
Use for directory-specific context.]

## Writing Principles
- Target under 200 lines (soft guideline, not hard cap)
- Use markdown headers and bullets
- Write specific, verifiable instructions
- Avoid conflicting instructions across files

## What to Include vs Exclude
[The table from spec Section 6.2 — Include column and Exclude column.]

## The @import Syntax
[How to reference external files. Path resolution.
Personal imports from ~/.claude/. Max depth of 5 hops.]

## Pruning Your CLAUDE.md
[Treat it like code. "Would removing this cause mistakes?"
Emphasis techniques ("IMPORTANT", "YOU MUST") for critical rules.
If Claude ignores instructions, the file is probably too long.]

## Common Mistakes
[Too long, too vague, conflicting instructions,
including things Claude can already infer from code.]

## The /init Shortcut
[/init auto-generates a CLAUDE.md. CLAUDE_CODE_NEW_INIT=true
for interactive multi-phase flow.]
```

- [ ] **Step 2: Verify the guide**

Confirm: has frontmatter. Under 200 lines. Includes the include/exclude table. Covers all bullet points from spec Section 6.2. Standalone — readable without other guides.

- [ ] **Step 3: Commit**

```bash
git add docs/claude-md-guide.md
git commit -m "docs: add CLAUDE.md writing guide"
```

### Task 11: Rules Guide

**Files:**

- Create: `docs/rules-guide.md`

- [ ] **Step 1: Write the guide**

Structure (~120 lines):

```markdown
---
title: "Using .claude/rules/"
description: "How to organize project instructions into modular, path-scoped rule files"
date: 2026-03-18
---

# Using .claude/rules/

## When to Use Rules vs CLAUDE.md
[Rules: modular, topic-specific, or path-scoped.
CLAUDE.md: core instructions every session needs.
Rule of thumb: if CLAUDE.md is growing past 200 lines, split into rules.]

## File Structure
[One topic per file. Descriptive filenames. Subdirectory organization.
Example directory tree.]

## Path-Scoping
[The paths frontmatter. Glob pattern table:]

| Pattern | Matches |
| --------- | --------- |
| `**/*.ts` | All TypeScript files in any directory |
| `src/**/*` | All files under src/ |
| `*.md` | Markdown files in project root |
| `src/components/*.tsx` | React components in a specific directory |
| `src/**/*.{ts,tsx}` | Brace expansion for multiple extensions |

[When path-scoped rules load (on file read, not every session).]

## User-Level Rules
[~/.claude/rules/ for personal cross-project preferences.
Loaded before project rules. Project rules have higher priority.]

## Sharing Rules Across Projects
[Symlinks. Example commands.]
```

- [ ] **Step 2: Verify the guide**

Confirm: has frontmatter. Includes the glob pattern table. Covers all bullet points from spec Section 6.3. Under 150 lines.

- [ ] **Step 3: Commit**

```bash
git add docs/rules-guide.md
git commit -m "docs: add .claude/rules/ usage guide"
```

### Task 12: Settings Guide

**Files:**

- Create: `docs/settings-guide.md`

- [ ] **Step 1: Write the guide**

Structure (~150 lines):

````markdown
---
title: "Configuring settings.json"
description: "How to configure Claude Code behavior with settings files"
date: 2026-03-18
---

# Configuring settings.json

## Settings File Locations
[Table: project (.claude/settings.json), local (.claude/settings.local.json),
user (~/.claude/settings.json), managed policy. Explain merge behavior.
More specific scopes override broader ones.]

## What Goes Where
[Project: team-shared config (permissions, env vars).
Local: personal overrides (not committed, gitignored).
User: personal preferences across all projects.]

## The $schema Field
[Point to https://json.schemastore.org/claude-code-settings.json
for editor autocomplete and validation.]

## Key Options for Beginners

### permissions.allow and permissions.deny
[Tool(specifier) syntax. Examples:]
```json
{
  "permissions": {
    "allow": [
      "Bash(npm test)",
      "Bash(npm run lint)",
      "Bash(git diff *)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)"
    ]
  }
}
```

[Link to official permission rule syntax docs.]

### autoMemoryEnabled

[Toggle auto memory. Default: true. Link to auto memory docs.]

### claudeMdExcludes

[Skip CLAUDE.md files by path/glob. Useful in monorepos.
Link to memory docs.]

## What NOT to Put in Project Settings

[Security-restricted options like autoMemoryDirectory.
Rejected from .claude/settings.json to prevent shared repos
from redirecting memory writes to sensitive locations.]

````

- [ ] **Step 2: Verify the guide**

Confirm: has frontmatter. Permission examples use `Tool(specifier)` syntax. Links to official docs for each key setting. Under 180 lines.

- [ ] **Step 3: Commit**

```bash
git add docs/settings-guide.md
git commit -m "docs: add settings.json configuration guide"
```

### Task 13: Directory Structure Guide

**Files:**

- Create: `docs/directory-structure-guide.md`

- [ ] **Step 1: Write the guide**

Structure (~120 lines):

````markdown
---
title: "The .claude/ Directory Structure"
description: "Understanding the .claude/ ecosystem, auto memory, and what to version control"
date: 2026-03-18
---

# The .claude/ Directory Structure

## What Lives in .claude/
[Tree diagram showing:]
```

your-project/
├── .claude/
│   ├── CLAUDE.md              # Alternative project instructions location
│   ├── settings.json          # Team-shared settings (commit this)
│   ├── settings.local.json    # Personal overrides (gitignored)
│   └── rules/                 # Modular instruction files
│       ├── code-style.md
│       ├── testing.md
│       └── ...

```

## Auto Memory
[Location: ~/.claude/projects/<project>/memory/
MEMORY.md index + topic files.
Key distinction: the 200-line limit for MEMORY.md is a HARD LOAD BOUNDARY
(content past line 200 is not loaded at session start). The 200-line target
for CLAUDE.md is a SOFT ADHERENCE GUIDELINE (CLAUDE.md is loaded in full,
but shorter files produce better adherence). Same number, different reasons.]

## What to .gitignore
[settings.local.json: YES — personal, not for version control.
settings.json: NO — team-shared, commit it.
.claude/rules/: NO — team-shared, commit them.
Auto memory: lives outside the repo (~/.claude/projects/), no action needed.]

## The Three Systems
[CLAUDE.md = what YOU tell Claude (instructions you write).
Auto memory = what CLAUDE tells itself (learnings it saves).
Settings = behavior configuration (permissions, toggles).
Each serves a different purpose. CLAUDE.md and auto memory are both
loaded every session but are written by different authors.]
````

- [ ] **Step 2: Verify the guide**

Confirm: has frontmatter. Clearly distinguishes the 200-line hard cap vs soft guideline. Covers all bullet points from spec Section 6.5. Under 150 lines.

- [ ] **Step 3: Commit**

```bash
git add docs/directory-structure-guide.md
git commit -m "docs: add .claude/ directory structure guide"
```

### Task 14: Effective Usage Guide

**Files:**

- Create: `docs/effective-usage-guide.md`

- [ ] **Step 1: Write the guide**

Structure (~180 lines):

```markdown
---
title: "Effective Usage Patterns"
description: "Essential day-one patterns for using Claude Code effectively"
date: 2026-03-18
---

# Effective Usage Patterns

This guide covers the essential patterns every Claude Code user should know
from day one. Sourced from the official
[How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works) and
[Best practices](https://code.claude.com/docs/en/best-practices) documentation.

## The #1 Constraint: Context Window

Claude's context window holds your conversation, file contents, command outputs,
CLAUDE.md, and system instructions. It fills up fast, and performance degrades
as it fills — Claude may "forget" earlier instructions or make more mistakes.

This is WHY configuration matters:
- A well-written CLAUDE.md reduces wasted context
- Good session habits keep context clean
- Knowing when to use /clear prevents degradation

## The #1 Practice: Give Claude a Way to Verify Its Work

[Content from spec Section 6.6. Verification criteria, test commands,
screenshots. The single highest-leverage thing you can do.]

## The Recommended Workflow

[Explore → Plan → Implement → Commit. Plan Mode with Shift+Tab.
Skip planning for trivial tasks.]

## Session Management Essentials

| Command | What it does |
| --------- | ------------- |
| `Esc` | Interrupt Claude mid-action. Context is preserved. |
| Press `Esc` twice | Open rewind menu — restore conversation, code, or both |
| `/rewind` | Same as double-Esc — open the rewind menu |
| `/clear` | Reset context. **Use between unrelated tasks.** |
| `/compact` | Summarize to free context. Add focus: `/compact focus on the API changes` |
| `/context` | See what's using space in your context window |
| `--continue` | Resume most recent conversation |
| `--resume` | Choose from recent conversations |

## Permission Modes

[Shift+Tab cycles through modes. Table with Default, Auto-accept edits, Plan mode.]

## Writing Effective Prompts

[Be specific. Delegate don't dictate. Provide rich content with @, images, pipes.]

## Common Failure Patterns

[The 5 anti-patterns with fixes, per spec Section 6.6.]
```

- [ ] **Step 2: Verify the guide**

Confirm: has frontmatter. Sources linked. Covers all 7 subsections from spec Section 6.6. No mention of hooks, MCP, skills, or subagents (out of scope). Under 200 lines.

- [ ] **Step 3: Commit**

```bash
git add docs/effective-usage-guide.md
git commit -m "docs: add effective usage patterns guide"
```

---

## Chunk 4: Root Files and Finalization

### Task 15: Root .gitignore

**Files:**

- Create: `.gitignore`

- [ ] **Step 1: Create the root .gitignore**

```gitignore
# OS files
.DS_Store
Thumbs.db

# Editor files
*.swp
*.swo
*~
.idea/
.vscode/

# Claude Code (this repo's own local settings)
.claude/settings.local.json

# Node (if contributors install anything for tooling)
node_modules/
```

- [ ] **Step 2: Commit**

```bash
git add .gitignore
git commit -m "feat: add root .gitignore"
```

### Task 16: README.md

**Files:**

- Create: `README.md`

- [ ] **Step 1: Write the README**

Target: under 120 lines. Structure:

````markdown
# Claude Code Templates

Starter templates and guides for configuring Claude Code. Clone this repo,
copy the scaffolds into your project, and fill them in using the examples
as reference.

**Audience:** Developers new to Claude Code who want a working configuration
from day one.

## Quick Start

1. **Clone this repo**
   ```bash
   git clone https://github.com/wlsgur073/Claude-Code-Templates.git
   ```

1. **Copy templates into your project**

   ```bash
   # Copy the essentials
   cp Claude-Code-Templates/templates/CLAUDE.md your-project/CLAUDE.md
   mkdir -p your-project/.claude
   cp Claude-Code-Templates/templates/.claude/settings.json your-project/.claude/settings.json
   ```

2. **Fill in the scaffolds** using `examples/` as reference

> **Tip:** Run `/init` in your project first — Claude auto-generates a starter
> CLAUDE.md. Then merge our template to fill gaps `/init` misses.

## What's Inside

```
Claude-Code-Templates/
├── templates/    ← Blank scaffolds to copy into your project
├── examples/     ← Filled reference versions (fictional "TaskFlow" project)
└── docs/         ← Guides explaining each concept
```

| Directory | Purpose |
| ----------- | --------- |
| `templates/` | Blank scaffolds with HTML comment prompts — copy and fill in |
| `examples/` | Realistic filled examples — use as a reference while editing |
| `docs/` | Standalone guides — read any one without the others |

## How Claude Code Memory Works

Claude Code has a layered memory system:

- **CLAUDE.md** — instructions *you* write. Loaded every session.
  Locations: project root, `.claude/`, user home, managed policy.
- **`.claude/rules/`** — modular instruction files, optionally scoped
  to specific file paths. Loaded every session or on file access.
- **Auto memory** — notes *Claude* writes for itself as you work.
  Stored at `~/.claude/projects/<project>/memory/`. First 200 lines
  of MEMORY.md loaded every session.

> **The #1 Rule:** Give Claude a way to verify its work — include test commands,
> lint commands, and build commands in your CLAUDE.md. This is the single
> highest-leverage thing you can do.

## Docs

| Guide | What it covers |
| ------- | --------------- |
| [Getting Started](docs/getting-started.md) | Step-by-step setup walkthrough |
| [CLAUDE.md Guide](docs/claude-md-guide.md) | Writing effective CLAUDE.md files |
| [Rules Guide](docs/rules-guide.md) | .claude/rules/ usage and path-scoping |
| [Settings Guide](docs/settings-guide.md) | settings.json configuration |
| [Directory Structure](docs/directory-structure-guide.md) | The .claude/ ecosystem |
| [Effective Usage](docs/effective-usage-guide.md) | Day-one usage patterns |

## Contributing

Contributions welcome! Please open an issue or PR.

## License

MIT — see [LICENSE](LICENSE).

````

- [ ] **Step 2: Verify the README**

Confirm: under 120 lines. Includes: one-liner, quick start (3 steps), tree diagram, "What's Inside" table, memory overview, verification callout, docs index, contributing, license. Links to all 6 guides.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add README with quick start, memory overview, and docs index"
```

### Task 17: Final Verification

- [ ] **Step 1: Verify directory structure matches spec**

Run: `find . -not -path './.git/*' -not -path './docs/superpowers/*' -type f | sort`

Expected output should match the spec's tree in Section 2 (plus LICENSE and root .gitignore).

- [ ] **Step 2: Verify all docs/ and examples/ markdown files have frontmatter**

Run: `for f in docs/*.md examples/**/*.md examples/*.md; do echo "=== $f ==="; head -5 "$f"; done`

Confirm: all have `---` delimited YAML with at minimum `title` and `description`.

- [ ] **Step 3: Verify all templates/ files have NO frontmatter**

Run: `for f in templates/*.md templates/**/*.md; do echo "=== $f ==="; head -3 "$f"; done`

Confirm: none start with `---` (except `path-specific-example.md` which has `paths` frontmatter — this is Claude Code functionality, not repo metadata, and is acceptable).

- [ ] **Step 4: Verify settings.json files are valid JSON**

Run: `node -e "JSON.parse(require('fs').readFileSync('templates/.claude/settings.json','utf8')); console.log('templates OK')" && node -e "JSON.parse(require('fs').readFileSync('examples/.claude/settings.json','utf8')); console.log('examples OK')"`

Expected: both print OK.

- [ ] **Step 5: Final commit (if any fixes needed)**

```bash
git add -A
git commit -m "fix: address issues found during final verification"
```
