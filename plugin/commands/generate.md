---
description: "Guided Claude Code setup — generates CLAUDE.md, settings.json, rules, and optional hooks/agents/skills for any project"
---

# Claude Code Project Setup

You are a Claude Code configuration expert. Set up optimal Claude Code configuration through interactive conversation.

Follow these phases in order.

---

## Phase 0: Determine Path

Before scanning or asking detailed questions, ask exactly one question:

> "Is this an existing project with code, or a new/empty project you're starting from scratch?"
>
> (a) **Existing project** — I already have code, dependencies, and/or a framework set up
> (b) **New/empty project** — I'm starting from scratch or have only basic scaffolding

- If the user chooses **(a)**, follow the **ADVANCED PATH** below.
- If the user chooses **(b)**, follow the **STARTER PATH** below.

---

# STARTER PATH

For new or empty projects. Generates a minimal 5-section CLAUDE.md and basic settings.

## Phase 1S: Skip Analysis

There are no files to scan. Skip project analysis entirely. Use the language/framework defaults from the user's answers as your baseline.

## Phase 2S: Ask Questions

Ask the following questions **one at a time**.

1. **Project type and language** — Ask what kind of project and what language/framework:
   > "What are you building, and with what language/framework?"
   >
   > Project type: (a) Web API / backend (b) Frontend web app (c) CLI tool (d) Library / package (e) Other
   >
   > Then ask which language/framework. Offer common choices based on their answer:
   > - Web API: Node.js/Express, Python/FastAPI, Go, Java/Spring, etc.
   > - Frontend: React, Vue, Next.js, Svelte, etc.
   > - CLI: Node.js, Python/Click, Go/Cobra, Rust/Clap, etc.
   > - Library: Node.js, Python, Go, Rust, etc.

2. **Project description** — Ask for a 1-2 sentence description of what the project does. This becomes the `# Project Overview` content.

3. **Build, run, and test commands** — Suggest sensible defaults based on Question 1, then ask the user to confirm or customize:

   | Language | build | dev | test | lint |
   |----------|-------|-----|------|------|
   | Node.js | `npm install` | `npm run dev` | `npm test` | `npm run lint` |
   | Python | `pip install -e .` | `uvicorn main:app --reload` | `pytest` | `ruff check .` |
   | Go | `go build ./...` | `go run .` | `go test ./...` | `golangci-lint run` |
   | Rust | `cargo build` | `cargo run` | `cargo test` | `cargo clippy` |
   | Java/Spring | `./mvnw compile` | `./mvnw spring-boot:run` | `./mvnw test` | — |

   > "Here are the standard commands for [chosen framework]. Are these correct, or would you like to customize them?"

4. **Code style** — Suggest the standard conventions for the chosen language, then ask:
   > "Should I use the standard [language] conventions, or do you have specific preferences? (indentation, naming, formatting)"

## Phase 3S: Generate Files

Create files based on user answers. Follow these rules strictly:

- **Be specific and verifiable** — "Use 2-space indentation" not "Format code properly"
- **All commands must be copy-pasteable** — use actual commands, not placeholders
- **CLAUDE.md must stay under 200 lines** — be concise
- **Merge, don't overwrite** — if any config file already exists, merge new content in

### Generate:

**`CLAUDE.md`** with 5 sections:

```
# Project Overview        ← user's description + language/framework from Q1-Q2
## Build & Run            ← exact commands from Q3
## Testing                ← test commands from Q3
## Code Style & Conventions ← from Q4, only rules that differ from language defaults
## Important Context      ← note that this is a new project; any architectural decisions mentioned
```

**`.claude/settings.json`**:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [],
    "deny": []
  }
}
```

- `allow`: add test, lint, and build commands from Q3 (e.g., `"Bash(npm test)"`, `"Bash(npm run lint)"`)
- `deny`: add `"Read(.env)"`, `"Read(.env.*)"` as sensible defaults

**`.gitignore`** — append this line if not already present:

```
.claude/settings.local.json
```

Do NOT generate `.claude/rules/`, hooks, agents, or skills on the starter path.

---

# ADVANCED PATH

For existing projects with code. Scans the project and generates full configuration.

## Phase 1A: Analyze

Scan the project silently:

- Read dependency files: `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `Gemfile`, etc.
- Identify primary language, framework, project type, and directory structure
- Detect test frameworks, linters, formatters, and build tools from dependencies
- Check for existing `CLAUDE.md`, `.claude/` directory, or `.claude/rules/`

Do NOT output your analysis yet. Use it to inform your questions.

**Safety check:** If no code files or dependency manifests are found, tell the user:

> "I didn't find any code or dependency files in this project. The Starter path is recommended for new projects — it's faster and generates a minimal config you can grow from. Would you like to switch to the Starter path, or continue with the full Advanced setup?"

If the user switches, follow the STARTER PATH. If they continue, use the **Open-ended** variant for every question in Phase 2A. Generate the same full Advanced output files.

## Phase 2A: Ask Questions

Ask the user the following questions **one at a time**. For each question, use the **Detected** variant when Phase 1A found relevant information, or the **Open-ended** variant when the project is empty or nothing was detected.

1. **Project overview**

   **Detected:**
   > "I found [language/framework] with [detected project type]. Is that correct? And in 1-2 sentences, what does this project do?"

   **Open-ended:**
   > "What language/framework is this project using, and what does it do in 1-2 sentences?"

2. **Build & run**

   **Detected:**
   > "I see [build tool] in your project. Are these your commands? build: `[detected]`, dev: `[detected]`, run: `[detected]` — or would you like to change them?"

   **Open-ended:**
   > "What commands do you use to build, run a dev server, and run the project?"

3. **Testing**

   **Detected:**
   > "I found [test framework] in your dependencies. Is `[detected test command]` your test command? Do you have a coverage target or preferred test patterns (factories, mocks, integration tests)?"

   **Open-ended:**
   > "What test framework and command will you use? Do you have a coverage target or preferred test patterns (factories, mocks, integration tests)?"

4. **Code style**

   **Detected:**
   > "I see [formatter/linter config] in your project. Should I use those settings? Anything to add for naming conventions, indentation, line length, or import ordering?"

   **Open-ended:**
   > "What are your preferences for naming conventions, formatting (indentation size, line length), and import ordering? Or should I use standard [language] conventions?"

5. **Workflow**

   **Detected:**
   > "I noticed [evidence, e.g., branch pattern in git log, commitlint config]. Is your branch convention `[detected]` and commit style `[detected]`? Any pre-development checklist items?"

   **Open-ended:**
   > "What branch naming convention and commit message style do you use? Any steps you always do before starting development?"

6. **Advanced features** — Ask: "Would you like to set up any of these optional features?"
   - (a) Auto-linting hooks — automatically runs linter after every file edit
   - (b) File protection hooks — blocks edits to `.env` and sensitive files
   - (c) Custom agent roles — specialized agents for different parts of the codebase
   - (d) Custom skill commands — reusable multi-step workflow automations
   - (e) None for now

## Phase 3A: Generate Files

Create all files based on user answers. Follow these rules strictly:

- **Be specific and verifiable** — "Use 2-space indentation" not "Format code properly"
- **Omit obvious information** — don't state what Claude can infer from reading the code
- **All commands must be copy-pasteable** — use actual project commands, not placeholders
- **Use actual directory names** — reference the project's real structure, not generic examples
- **CLAUDE.md must stay under 200 lines** — be concise
- **Merge, don't overwrite** — if `CLAUDE.md` or `settings.json` already exists, merge new content into the existing file

### Always generate:

**`CLAUDE.md`** with these sections:

```
# Project Overview        ← user's description + language/framework
## Build & Run            ← exact commands from user answers
## Testing                ← test commands + verification commands Claude can run
## Code Style & Conventions ← only rules that differ from language defaults
## Workflow               ← branch/commit conventions, pre-dev checklist
## Project Structure      ← key directories and purposes (from your analysis)
## Important Context      ← non-obvious things discovered during analysis
## References             ← @import links to relevant docs if they exist
```

**`.claude/settings.json`**:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [],
    "deny": []
  }
}
```

- `allow`: add test, lint, and build commands (e.g., `"Bash(npm test)"`, `"Bash(npm run lint)"`)
- `deny`: add sensitive file patterns (e.g., `"Read(.env)"`, `"Read(.env.*)"`)

**`.claude/rules/code-style.md`**:

```
# Code Style
## Naming Conventions     ← from user answers
## Formatting             ← indentation, line length, trailing commas, etc.
## Imports                ← import grouping and ordering
```

Include `✗ bad / ✓ good` code examples for non-obvious rules.

**`.claude/rules/testing.md`**:

```
# Testing Conventions
## Test Framework         ← detected framework
## Test Structure         ← directory layout, file naming
## Coverage               ← targets from user answers
## Patterns               ← factories, mocks, integration patterns
```

**`.claude/rules/architecture.md`**:

```
# Architecture
## Layer Structure        ← detected layers from project analysis
## Dependency Direction   ← inferred dependency rules
## Module Boundaries      ← module organization patterns
```

**`.claude/rules/workflow.md`**:

```
# Workflow
## Pre-Development Checklist
- Read relevant CLAUDE.md sections
- Review existing tests for the area to modify
- Check git status for uncommitted changes
[+ user's specific checklist items]

## Review Gates
- All tests pass
- Lint has zero warnings
- Build succeeds
[+ user's specific gates]
```

**`.gitignore`** — append this line if not already present:

```
.claude/settings.local.json
```

### Conditionally generate (only if user opted in):

**Auto-linting hooks** — add `hooks` key to `.claude/settings.json`:

```json
"hooks": {
  "PostToolUse": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        {
          "type": "command",
          "command": "[detected-linter-command] --fix \"$CLAUDE_FILE_PATH\" 2>/dev/null || true",
          "statusMessage": "Auto-linting edited file"
        }
      ]
    }
  ]
}
```

Replace `[detected-linter-command]` with the actual linter (e.g., `npx eslint`, `ruff`, `gofmt`).

**File protection hooks** — add `PreToolUse` to hooks:

```json
"PreToolUse": [
  {
    "matcher": "Edit|Write",
    "hooks": [
      {
        "type": "command",
        "command": "echo \"$CLAUDE_FILE_PATH\" | grep -qE '\\.(env|pem|key)' && echo 'BLOCK: Protected file' && exit 1 || exit 0",
        "statusMessage": "Checking for protected files"
      }
    ]
  }
]
```

**Agent roles** — ask user for role name and scope, then create `.claude/agents/<name>.md`:

```markdown
---
name: "[Role Name]"
description: "[Specialization]"
tools:
  - Read
  - Edit
  - Write
  - Bash
  - Grep
  - Glob
model: "sonnet"
---

# Scope
[Directories this agent modifies]

## Rules
[Domain-specific rules]
```

After creating each agent, ask:

> "Would you like to add another agent role, or move on?"

Repeat until the user says to move on.

**Skill commands** — ask user for skill purpose, then create `.claude/skills/<name>/SKILL.md`:

```markdown
---
name: "[skill-name]"
description: "[What this skill automates]"
---

# Steps

## Step 1: Gather Information
[What to ask the user]

## Step 2: Validate
[Pre-checks before proceeding]

## Step 3: Execute
[Files to create or modify]

## Step 4: Verify
[Build/test commands to confirm]
```

After creating each skill, ask:

> "Would you like to add another skill, or move on to the summary?"

Repeat until the user says to move on.

---

# SHARED

## Phase 4: Wrap Up

After generating all files:

1. Print a summary table listing every created/modified file and what it contains
2. If you merged into existing files, explain what was added
3. Tell the user: "Run `/memory` to verify all configuration files are loaded"
4. Suggest trying a simple task to test the configuration works

**If the user followed the Starter path**, also add:

> You're using a starter configuration. As your project grows and you want rule files, hooks, agents, or skills, run `/claude-code-template:generate` again and choose "Existing project" to upgrade to the full configuration.
