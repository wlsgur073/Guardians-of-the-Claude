# ADVANCED PATH

For existing projects with code. Scans the project and generates full configuration.

## Phase 1A: Analyze

Scan the project silently, checking for **actual source code and dependency manifests**:

1. Search for dependency manifests: `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `Gemfile`, etc.
2. Search for source code files: `*.ts`, `*.js`, `*.py`, `*.go`, `*.rs`, `*.java`, etc.
3. If manifests or code found: identify language, framework, project type, directory structure, test frameworks, linters, and formatters
4. Check for existing `CLAUDE.md`, `.claude/` directory, or `.claude/rules/`

**IMPORTANT:** `.claude/` configuration files, `CLAUDE.md`, rule files, agent definitions, and skill files are NOT source code. Do NOT infer project type from these files alone. Only actual source code files and dependency manifests count as evidence of an existing project.

Do NOT output your analysis yet. Use it to inform your questions.

**Safety check (MANDATORY):** If no source code files AND no dependency manifests are found, you MUST tell the user — regardless of what they selected in Phase 0:

> "I scanned this project but didn't find any source code files or dependency manifests (e.g., package.json, pyproject.toml). This looks like a new or empty project. The Starter path is recommended — it's faster and generates a minimal config you can grow from. Would you like to switch to the Starter path, or continue with the full Advanced setup?"

If the user switches, follow the STARTER PATH (read `templates/starter.md`). If they continue, use the **Open-ended** variant for every question in Phase 2A. Do NOT assume or hallucinate project details — ask the user directly.

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

Create all files based on user answers. Follow the generation rules in `references/best-practices.md`.

### Always generate:

**`CLAUDE.md`** with these sections:

```
# Project Overview        ← user's description + language/framework
## Build & Run            ← exact commands from user answers
## Testing                ← test commands + verification commands Claude can run
## Code Style & Conventions ← only rules that differ from language defaults
## Development Approach    ← iterative self-refinement rules (see below)
## Workflow               ← branch/commit conventions, pre-dev checklist
## Project Structure      ← key directories and purposes (from your analysis)
## Important Context      ← non-obvious things discovered during analysis
## References             ← @import links to relevant docs if they exist
```

The **Development Approach** section must include these rules:

```
## Development Approach
- When a request is vague or ambiguous, do not start implementing immediately
- First, critically analyze the request: identify assumptions, missing context, and possible interpretations
- Present your analysis and ask targeted clarifying questions before writing code
- After clarifying, outline your approach briefly and get confirmation before proceeding
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
color: "blue"
---

# Scope
[Directories this agent modifies]

## Rules
[Domain-specific rules]
```

Available `color` values: `blue`, `cyan`, `green`, `yellow`, `magenta`, `red`.

After creating each agent, ask:

> "Would you like to add another agent role, or move on?"

Repeat until the user says to move on.

**Skill commands** — ask user for skill purpose, then create `.claude/skills/<name>/SKILL.md`:

```markdown
---
name: "[skill-name]"
description: "[What this skill automates]"
# Optional fields:
# allowed-tools: [Read, Edit, Write, Bash, Grep, Glob]
# argument-hint: "<required-arg> [optional-arg]"
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
