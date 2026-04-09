# ADVANCED PATH

For existing projects with code. Scans the project and generates full configuration.

## Phase 2A-Incremental: Add Missing Features

Use this path when Phase 0 detected existing Claude Code configuration.

Scan the current configuration silently:

1. Read `CLAUDE.md` — check which sections exist (Overview, Build, Test, Code Style, Workflow, etc.)
2. Read `.claude/settings.json` — check for permissions, hooks, env
3. Check `.claude/rules/` — list existing rule files
4. Check `.claude/agents/` — list existing agent files
5. Check `.claude/skills/` — list existing skill directories
6. Check `.mcp.json` — check if MCP servers are configured

Present a checklist of what's already configured and what's missing:

> "Here's what I found in your current setup:"
>
> ✓ CLAUDE.md (with [N] sections)
> ✓ settings.json (permissions configured)
> ✗ Security rule file
> ✓ code-style.md rule
> ✗ Hooks (no auto-linting or file protection)
> ✗ Agents (none defined)
> ✗ Skills (none defined)
> ✗ MCP servers (no .mcp.json)
>
> "Which of the missing items would you like to add? (pick all that apply)"
>
> - (a) Security rule file
> - (b) Auto-linting hooks
> - (c) File protection hooks
> - (d) Custom agent roles
> - (e) Custom skill commands
> - (f) Other (describe what you need)

Adjust the checklist based on what actually exists and what's missing. Only show unconfigured items as options.

For each selected item, follow the corresponding generation logic in Phase 3A below (jump directly to the relevant conditional section). Skip Phase 1A and Phase 2A — the project is already analyzed and configured.

After generating all selected items, return to SKILL.md for Phase 4.

---

## Phase 1A: Analyze

Scan the project silently, checking for **actual source code and dependency manifests**:

1. Search for dependency manifests: `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `Gemfile`, etc.
2. Search for source code files: `*.ts`, `*.js`, `*.py`, `*.go`, `*.rs`, `*.java`, etc.
3. If manifests or code found: identify language, framework, project type, directory structure, test frameworks, linters, and formatters
4. Check for existing `CLAUDE.md`, `.claude/` directory, or `.claude/rules/`

CRITICAL — Config files are NOT evidence of a project:

- `.claude/` configuration files, `CLAUDE.md`, rule files, agent definitions, and skill files are NOT source code
- Even if `CLAUDE.md` or `.claude/` exists, they do NOT satisfy the safety check below
- Only files matching step 1 (dependency manifests) or step 2 (source code with language-specific extensions) count as evidence

Do NOT output your analysis yet. Use it to inform your questions.

**Safety check (MANDATORY):** If no source code files (from step 2) AND no dependency manifests (from step 1) are found, you MUST tell the user — regardless of what they selected in Phase 0 and regardless of whether CLAUDE.md or .claude/ exists:

> "I scanned this project but didn't find any source code files or dependency manifests (e.g., package.json, pyproject.toml). This looks like a new or empty project. The Starter path is recommended — it's faster and generates a minimal config you can grow from. Would you like to switch to the Starter path, or continue with the full Advanced setup?"

If the user switches, follow the STARTER PATH (read `templates/starter.md`). If they continue, use the **Open-ended** variant for every question in Phase 2A. Do NOT assume or hallucinate project details — ask the user directly.

## Phase 2A: Ask Questions

Ask the user the following questions **one at a time**. For each question, use the **Detected** variant when Phase 1A found relevant information, or the **Open-ended** variant when the project is empty or nothing was detected.

1. **Project overview**

   Detected:
   > "I found [language/framework] with [detected project type]. Is that correct? And in 1-2 sentences, what does this project do?"

   Open-ended:
   > "What language/framework is this project using, and what does it do in 1-2 sentences?"

2. **Build & run**

   Detected:
   > "I see [build tool] in your project. Are these your commands? build: `[detected]`, dev: `[detected]`, run: `[detected]` — or would you like to change them?"

   Open-ended:
   > "What commands do you use to build, run a dev server, and run the project?"

3. **Testing**

   Detected:
   > "I found [test framework] in your dependencies. Is `[detected test command]` your test command? Do you have a coverage target or preferred test patterns (factories, mocks, integration tests)?"

   Open-ended:
   > "What test framework and command will you use? Do you have a coverage target or preferred test patterns (factories, mocks, integration tests)?"

4. **Code style**

   Detected:
   > "I see [formatter/linter config] in your project. Should I use those settings? Anything to add for naming conventions, indentation, line length, or import ordering?"

   Open-ended:
   > "What are your preferences for naming conventions, formatting (indentation size, line length), and import ordering? Or should I use standard [language] conventions?"

5. **Workflow**

   Detected:
   > "I noticed [evidence, e.g., branch pattern in git log, commitlint config]. Is your branch convention `[detected]` and commit style `[detected]`? Any pre-development checklist items?"

   Open-ended:
   > "What branch naming convention and commit message style do you use? Any steps you always do before starting development?"

6. **Advanced features** — Ask: "Would you like to set up any of these optional features? (pick all that apply)"
   - (a) Auto-linting hooks — automatically runs linter after every file edit
   - (b) File protection hooks — blocks edits to `.env` and sensitive files
   - (c) Security rule file — explicit rules for auth, input validation, and secrets handling
   - (d) Custom agent roles — specialized agents for different parts of the codebase
   - (e) Custom skill commands — reusable multi-step workflow automations
   - (f) MCP server configuration — connect Claude to databases, APIs, or external tools
   - (g) None for now

## Phase 3A: Generate Files

Create all files based on user answers. Follow the generation rules in `references/best-practices.md`.

### Always generate

**`CLAUDE.md`** with these sections:

```markdown
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

```markdown
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
- `deny`: add Essential deny patterns: `"Read(./.env)"`, `"Read(./.env.*)"`, `"Edit(./.env)"`, `"Edit(./.env.*)"`, `"Write(./.env)"`, `"Write(./.env.*)"`, `"Read(./secrets/)"`

**`.claude/rules/code-style.md`**:

```markdown
# Code Style
## Naming Conventions     ← from user answers
## Formatting             ← indentation, line length, trailing commas, etc.
## Imports                ← import grouping and ordering
```

Include `✗ bad / ✓ good` code examples for non-obvious rules.

**`.claude/rules/testing.md`**:

```markdown
# Testing Conventions
## Test Framework         ← detected framework
## Test Structure         ← directory layout, file naming
## Coverage               ← targets from user answers
## Patterns               ← factories, mocks, integration patterns
```

**`.claude/rules/architecture.md`**:

```markdown
# Architecture
## Layer Structure        ← detected layers from project analysis
## Dependency Direction   ← inferred dependency rules
## Module Boundaries      ← module organization patterns
```

**`.claude/rules/workflow.md`**:

```markdown
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

```gitignore
.claude/settings.local.json
```

### Conditionally generate (only if user opted in)

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
        "command": "echo \"$CLAUDE_FILE_PATH\" | grep -qE '\\.(env|pem|key)' && echo 'BLOCK: Protected file' && exit 2 || exit 0",
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

## Scope
[Directories this agent can touch]

## Rules
[How it works — domain-specific patterns and conventions]

## Constraints
[Hard limits — what it must never do, e.g., "Never modify migration files"]

## Verification
[How to confirm work is done — test commands, checks to run]
```

Not every agent needs all four sections — scale to complexity. **Scope** and **Rules** are essential; add **Constraints** when the agent could cause damage, and **Verification** when quality checks are available.

Available `color` values: `blue`, `cyan`, `green`, `yellow`, `magenta`, `red`.

After creating the agent body, ask about model selection:

> "What model should this agent use?"
>
> - (a) **haiku** — fastest, cheapest. Best for read-only exploration and file search
> - (b) **sonnet** — balanced. Best for implementation, debugging, and testing (recommended)
> - (c) **opus** — deepest reasoning. Best for architecture review and security analysis
> - (d) **inherit** — use the parent session's model

Use the selection in the agent's `model:` field with a YAML comment explaining the choice:
`# haiku: read-only exploration, speed over depth`

Then ask:

> "Would you like to add another agent role, or move on?"

Repeat until the user says to move on.

**Skill commands** — ask user for skill purpose, then create `.claude/skills/<name>/SKILL.md`:

```markdown
---
name: "[skill-name]"
description: "[What this skill automates]"
argument-hint: "<required-arg> [optional-arg]"
---

# Steps

## Step 1: Gather Information
Parse `$ARGUMENTS` for the required parameters. If `$ARGUMENTS` is empty, ask the user.

## Step 2: Validate
[Pre-checks before proceeding]

## Step 3: Execute
[Files to create or modify]

## Step 4: Verify
[Build/test commands to confirm]
```

If the skill needs project-specific context (coding conventions, API patterns, example files), create a `references/` directory alongside SKILL.md with supporting markdown files.

**Security rule file** — read `../../references/security-patterns.md` for the template, then create `.claude/rules/security.md`:

```markdown
# Security Rules

## Authentication
- [Detected auth pattern — or ask the user what authentication method the project uses]
- Never log authentication tokens or credentials
- Never hardcode secrets — use environment variables

## Input Validation
- All user input must be validated before use (framework validators, schema libraries, etc.)
- Never trust client-side validation alone — always validate server-side
- Sanitize output to prevent injection attacks when rendering user content

## Secrets Handling
- Never commit `.env`, `.pem`, `.key`, or credential files
- Environment variables are validated at startup (fail fast on missing vars)
- API keys and connection strings must be loaded from environment, never from source code
```

Customize the rules based on what you detected in the project (auth middleware, validation libraries, secret management patterns). If nothing was detected, use the generic template above and ask the user to fill in project-specific details.

After creating each skill, ask:

> "Would you like to add another skill, or move on to the summary?"

Repeat until the user says to move on.

**MCP server configuration** — ask the user what external tools Claude should connect to, then create `.mcp.json` at the project root:

```json
{
  "mcpServers": {
    "[server-name]": {
      "command": "[npx|uvx|docker]",
      "args": ["[package-or-image]"],
      "env": {}
    }
  }
}
```

Common suggestions based on detected project:
- PostgreSQL detected (`pg`, `prisma`, `knex` in dependencies) → suggest `@modelcontextprotocol/server-postgres`
- File access needed → suggest `@modelcontextprotocol/server-filesystem`
- Web fetching needed → suggest `mcp-server-fetch` (Python, via `uvx`)

If the `.mcp.json` contains API keys or connection strings with credentials, add `.mcp.json` to `.gitignore` and note the required env vars in CLAUDE.md.
