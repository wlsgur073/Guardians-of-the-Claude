---
title: "Advanced Features"
description: "Hooks, agents, and skills — extending Claude Code beyond basic configuration"
date: 2026-03-23
---

# Advanced Features

Three features for teams that have outgrown basic CLAUDE.md + rules. Start with the [Getting Started Guide](getting-started.md) before adding these. See `templates/advanced/` for a complete filled example.

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
- **`$CLAUDE_FILE_PATH`** / **`$CLAUDE_PROJECT_DIR`** -- injected path variables
- **`statusMessage`** -- text shown in the UI while the hook runs
- **`PreToolUse` + `exit 1`** blocks the action; **`PostToolUse` + `|| true`** runs after it
- Other events: `Notification`, `Stop`, `SessionStart`, `SessionEnd`, `SubagentStop`, `UserPromptSubmit`, `PreCompact` — see [hooks docs](https://code.claude.com/docs/en/hooks) for all event types
- **Hook types:** `"type": "command"` (shell) or `"type": "prompt"` (LLM-driven, for `PreToolUse`, `Stop`, `SubagentStop`, `UserPromptSubmit`)

## Agents

Agents are custom role definitions in `.claude/agents/` with specialized scope, toolset, and model. Useful for role specialization, scope constraints, and parallel dispatch in large codebases.

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
color: "green"
---

# Scope
Only modify files under `src/api/`, `src/services/`, and `src/repos/`.

## Rules
- Run `npm test` after making changes
- Use Zod schemas for all input validation
```

Key fields:

- **`name`** / **`description`** -- identity and specialization
- **`tools`** -- allowed tools (Read, Edit, Write, Bash, Grep, Glob, etc.)
- **`model`** -- which model (`sonnet`, `opus`, `haiku`, `inherit`)
- **`color`** -- UI display color (`blue`, `cyan`, `green`, `yellow`, `magenta`, `red`)

> **Example:** See `templates/advanced/.claude/agents/backend-developer.md` for a complete agent definition.

## Skills

Skills are reusable multi-step workflows in `.claude/skills/`. Each becomes a slash command that automates repeatable processes like scaffolding features or adding components.

### Configuration

Create `.claude/skills/<skill-name>/SKILL.md`:

```markdown
---
name: "add-endpoint"
description: "Scaffolds a new REST API endpoint with handler, service, and tests"
allowed-tools: [Read, Edit, Write, Bash, Grep, Glob]
argument-hint: "<resource> [operations]"
---

# Steps

## Step 1: Gather Information
Read `references/api-conventions.md` for project patterns.
Parse `$ARGUMENTS` for resource name and operations. If empty, ask the user.

## Step 2: Validate
Confirm the resource does not already exist. Run the test suite.

## Step 3: Execute
Create model, repository, service, handler, and test files.

## Step 4: Verify
Run build and tests to confirm everything works.
```

Key fields:

- **`name`** / **`description`** -- identity and purpose
- **`allowed-tools`** -- restrict available tools (note: skills use `allowed-tools`, agents use `tools`)
- **`argument-hint`** -- usage hint for slash command menu (e.g., `"<resource> [operations]"`)
- **`user-invocable`** -- show in slash command menu (default: `true`)
- **`disable-model-invocation`** -- prevent Claude from auto-triggering (default: `false`)
- **`model`** -- override model when skill is active

Skills come in two types: **user-invoked** (slash command) and **model-invoked** (auto-triggered by Claude). Model-invoked descriptions should include trigger phrases: `"Use when the user asks to 'do X' or 'do Y'."` Skills can include supporting files alongside SKILL.md: `references/`, `examples/`, `scripts/`.

> **Note:** The legacy `commands/` directory is deprecated. Use `skills/<name>/SKILL.md` for all skill types.

> **Example:** See `templates/advanced/.claude/skills/add-endpoint/` for a complete skill with references.

## Further Reading

- [Getting Started](getting-started.md) -- Basic setup walkthrough
- [Settings Guide](settings-guide.md) -- Permissions and other settings
- [Rules Guide](rules-guide.md) -- Modular instruction files
