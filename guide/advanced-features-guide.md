---
title: "Advanced Features"
description: "Hooks, agents, and skills — extending Claude Code beyond basic configuration"
date: 2026-03-23
---

# Advanced Features

Three features for teams that have outgrown basic CLAUDE.md + rules configuration. Start with the [Getting Started Guide](getting-started.md) before adding these.

## Hooks

Hooks are shell commands that run automatically before or after Claude uses a tool. Define them in `settings.json` under the `hooks` key. Use them for auto-linting, auto-formatting, file protection, or type checking.

### Configuration

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "npx eslint --fix \"$CLAUDE_FILE_PATH\" 2>/dev/null || true",
            "statusMessage": "Auto-linting edited file"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"$CLAUDE_FILE_PATH\" | grep -qE '\\.env' && echo 'BLOCK: Protected file' && exit 1 || exit 0",
            "statusMessage": "Checking for protected files"
          }
        ]
      }
    ]
  }
}
```

Key concepts:

- **`matcher`** -- pipe-separated tool names or regex (e.g., `"Edit|Write"`, `"mcp__.*"`)
- **`$CLAUDE_FILE_PATH`** -- the file path Claude is editing, injected automatically
- **`$CLAUDE_PROJECT_DIR`** -- the project root directory
- **`statusMessage`** -- text shown in the UI while the hook runs
- **`PreToolUse` + `exit 1`** -- blocks the tool action (file protection pattern)
- **`PostToolUse` + `|| true`** -- runs after the action; prevents lint errors from interrupting Claude
- Other events: `Notification`, `Stop`, `SessionStart`, `SubagentStop` — see [hooks docs](https://code.claude.com/docs/en/hooks) for all event types

## Agents

Agents are custom role definitions in `.claude/agents/`. Each agent has a specialized scope, toolset, and model -- useful for large codebases where different areas need different expertise. Use them for role specialization (frontend, backend, testing), scope constraints, model selection, or team workflows with parallel dispatch.

### Configuration

Create `.claude/agents/<name>.md` with YAML frontmatter:

```markdown
---
name: "Backend Developer"
description: "Specializes in API layer, services, and database access"
tools:
  - Read
  - Edit
  - Write
  - Bash
model: "sonnet"
---

# Scope
Only modify files under `src/api/`, `src/services/`, and `src/repos/`.

## Rules
- Run `npm test` after making changes
- Use Zod schemas for all input validation
```

Key fields:

- **`name`** / **`description`** -- identity and specialization
- **`tools`** -- allowed tools (Read, Edit, Write, Bash, Grep, Glob, Agent, Skill)
- **`model`** -- which model (sonnet, opus, haiku)
- **`effort`** -- processing effort level (high, medium, low)

The body after frontmatter defines scope and rules in natural language.

## Skills

Skills are reusable multi-step workflows in `.claude/skills/`. Each becomes a slash command that automates repeatable processes like scaffolding features or adding components. Use them for repeated scaffolding, standardized workflows, or multi-phase processes.

### Configuration

Create `.claude/skills/<skill-name>/SKILL.md`:

```markdown
---
name: "add-endpoint"
description: "Scaffolds a new REST API endpoint with handler, service, and tests"
---

# Steps

## Step 1: Gather Information
Ask the user for the resource name and required operations.

## Step 2: Validate
Confirm the resource does not already exist. Run the test suite.

## Step 3: Execute
Create model, repository, service, handler, and test files.

## Step 4: Verify
Run build and tests to confirm everything works.
```

The four-step pattern (gather, validate, execute, verify) keeps skills predictable. Step 1 uses `AskUserQuestion` to collect inputs; Step 4 runs build/test commands to confirm the work. Each skill becomes a slash command — `/add-endpoint` invokes `.claude/skills/add-endpoint/SKILL.md`.

## Templates

See `templates/advanced/` for a complete filled example (fictional "TaskFlow" project) showing how hooks, agents, skills, and rules work together. If you already have a basic `settings.json`, add the `hooks`, `env`, and `enabledPlugins` keys rather than overwriting.

## Further Reading

- [Getting Started](getting-started.md) -- Basic setup walkthrough
- [Settings Guide](settings-guide.md) -- Permissions and other settings
- [Rules Guide](rules-guide.md) -- Modular instruction files
