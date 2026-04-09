---
title: "Advanced Features"
description: "Hooks, agents, and skills -- extending Claude Code beyond basic configuration"
version: 1.2.1
---

# Advanced Features

Three features for teams that have outgrown basic CLAUDE.md + rules. Start with the [Getting Started Guide](getting-started.md) before adding these. See `templates/advanced/` for a complete filled example.

## Hooks

Hooks are shell commands that run automatically before or after Claude uses a tool. Define them in `settings.json` under the `hooks` key. Use them for auto-linting, auto-formatting, file protection, or type checking.

### Hook Configuration

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"$CLAUDE_FILE_PATH\" | grep -qE '(package-lock\\.json|\\.env|migrations/)' && echo 'Protected file' && exit 2 || exit 0",
            "statusMessage": "Checking for protected files"
          }
        ]
      }
    ],
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
    ]
  }
}
```

Key concepts:

- **`matcher`** -- pipe-separated tool names or regex (e.g., `"Edit|Write"`, `"mcp__.*"`)
- **`$CLAUDE_FILE_PATH`** / **`$CLAUDE_PROJECT_DIR`** -- injected path variables
- **`statusMessage`** -- text shown in the UI while the hook runs
- **`PreToolUse` + `exit 2`** blocks the action and tells Claude why -- use for protecting sensitive files like `.env` or migration directories
- **`PostToolUse` + `|| true`** runs after the action completes -- use for auto-linting or formatting
- **`UserPromptSubmit`** runs before Claude processes user input -- use for keyword detection or automatic context injection
- Other events: `Notification`, `Stop`, `SessionStart`, `SessionEnd`, `SubagentStop`, `PreCompact` -- see [hooks docs](https://code.claude.com/docs/en/hooks) for all event types
- **Practical combinations:** `SessionStart` for project context injection at startup, `PreCompact` for preserving critical notes before auto-compaction, `SubagentStop` for validating agent output before returning to the parent session
- **Hook types:** `"type": "command"` (shell) or `"type": "prompt"` (LLM-driven, for `PreToolUse`, `Stop`, `SubagentStop`, `UserPromptSubmit`)

### Script-Based Hooks

For complex logic, use external scripts: `"command": "bash \"${CLAUDE_PROJECT_DIR}/scripts/my-hook.sh\""`. Scripts are testable, version-controlled, and easier to maintain. See `templates/advanced/.claude/settings.json` for a complete example. Always set `timeout` explicitly — input validation 3-5s, lint/format 10-15s, build/test 30s+.

## Agents

Agents are custom role definitions in `.claude/agents/` with specialized scope, toolset, and model. Useful for role specialization, scope constraints, and parallel dispatch in large codebases.

### Agent Configuration

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
# sonnet: balances speed and quality for implementation tasks
model: "sonnet"
color: "green"
---

## Scope
Only modify files under `src/api/`, `src/services/`, `src/repos/`, and `tests/`.

## Rules
- Follow the asyncHandler wrapper pattern for all route handlers
- All database access must go through repository classes in `src/repos/`
- Use Zod schemas from `src/models/` for all input validation

## Constraints
- Never modify migration files or `package-lock.json` without explicit approval
- Never call repositories directly from route handlers — always through services

## Verification
- `npm test` passes, `npm run lint` clean, `npm run build` compiles
- New endpoints include JSDoc tags: @route, @method, @auth
```

Four sections keep agent prompts focused: **Scope** defines what the agent can touch, **Rules** define how it works, **Constraints** set hard limits that prevent damage, and **Verification** tells it how to confirm work is done. Not every agent needs all four -- scale to complexity. Put the model choice rationale in a YAML comment so future readers understand the intent.

### Model Selection

| Model | Best for | Example agents |
| ----- | -------- | -------------- |
| `haiku` | Fast lookup, file search, exploration | explorer, linter |
| `sonnet` | Implementation, debugging, test writing | backend-dev, debugger |
| `opus` | Architecture review, deep analysis | code-reviewer, architect |

Use `"inherit"` to match the parent session's model. Put the reasoning in a YAML comment (`# opus: needs deep analysis for security review`) so the choice is self-documenting.

**Cost tradeoff:** `haiku` is ~60x cheaper than `opus`. Default to `sonnet`; use `haiku` for high-volume read-only tasks, `opus` only when a single mistake is expensive (security review, architecture decisions).

### Agent Design Patterns

**One agent, one perspective.** Don't combine implementation, review, and testing in a single agent -- split them into focused roles.

**Read-only agents:** Remove Edit and Write from `tools` to create analysis-only agents. Useful for security review, architecture analysis, and code exploration.

**Agent pipeline:** Chain agents for multi-stage workflows: `backend-developer` (implement) → `security-reviewer` (review) → `test-writer` (test).

## Skills

Skills are reusable multi-step workflows in `.claude/skills/`. Each becomes a slash command that automates repeatable processes like scaffolding features or adding components.

### Skill Configuration

Create `.claude/skills/<skill-name>/SKILL.md`:

```markdown
---
name: "add-endpoint"
description: "Scaffolds a new REST API endpoint with handler, service, and tests"
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
- **`argument-hint`** -- usage hint for slash command menu (e.g., `"<resource> [operations]"`)
- **`user-invocable`** -- show in slash command menu (default: `true`)
- **`disable-model-invocation`** -- prevent Claude from auto-triggering (default: `false`)
- **`model`** -- override model when skill is active

Skills come in two types: **user-invoked** (slash command) and **model-invoked** (auto-triggered by Claude). Model-invoked descriptions should include trigger phrases: `"Use when the user asks to 'do X' or 'do Y'."` Skills can include supporting files alongside SKILL.md: `references/`, `examples/`, `scripts/`.

### Skill Design Patterns

**Argument parsing:** Use `$ARGUMENTS` to accept parameters. Parse flags and positional args in Step 1 -- if empty, ask the user.

**Reference files:** Put project conventions, examples, or API docs in `references/` alongside SKILL.md. Read them at the step where they're needed, not upfront -- this saves context.

**Fallback pattern:** When a skill depends on an optional tool (MCP server, CI system), provide two paths: Path A uses the tool when available, Path B falls back to a manual alternative.

> **Note:** The legacy `commands/` directory is deprecated. Use `skills/<name>/SKILL.md` for all skill types.

### Plugin Skills in Practice

The `guardians-of-the-claude` plugin demonstrates a skill-per-role workflow with four skills that chain together:

| Skill | Purpose |
| ----- | ------- |
| `/guardians-of-the-claude:create` | Guided setup wizard -- generates CLAUDE.md, settings, rules, and optional features |
| `/guardians-of-the-claude:audit` | Comprehensive configuration evaluation with scoring |
| `/guardians-of-the-claude:secure` | Fixes security gaps -- deny patterns, security rules, file protection hooks |
| `/guardians-of-the-claude:optimize` | Improves config quality -- rules splitting, agent diversity, MCP, hook quality |

**Recommended workflow:** `/create` → `/audit` → `/secure` or `/optimize` → `/audit` (re-verify). Each skill hands off to the next, and they share state via timestamped files in `.claude/.plugin-cache/`.

## Further Reading

- [Getting Started](getting-started.md) -- Basic setup walkthrough
- [Settings Guide](settings-guide.md) -- Permissions and other settings
- [MCP Integration Guide](mcp-guide.md) -- Connecting to external tools via MCP
- [Rules Guide](rules-guide.md) -- Modular instruction files
