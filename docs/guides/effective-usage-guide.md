---
title: "Effective Usage Patterns"
description: "Essential day-one patterns for using Claude Code effectively"
version: 1.3.2
---

# Effective Usage Patterns

This guide covers the essential patterns every Claude Code user should know from day one. Sourced from the official [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works) and [Best practices](https://code.claude.com/docs/en/best-practices) documentation.

## The #1 Constraint: Context Window

Claude's context window holds your conversation, file contents, command outputs, CLAUDE.md, and system instructions. It fills up fast, and performance degrades as it fills -- Claude may "forget" earlier instructions or make more mistakes.

This is why configuration matters:

- A well-written CLAUDE.md reduces wasted context (fewer corrections needed)
- Good session habits keep context clean (see Session Management below)
- Knowing when to use `/clear` prevents degradation

## The #1 Practice: Give Claude a Way to Verify Its Work

Include test commands, lint commands, and build commands in your CLAUDE.md so Claude can self-check:

```markdown
## Testing
npm test             # run full test suite
npm run lint         # check for style issues
npm run build        # verify TypeScript compiles
```

When prompting, provide verification criteria: expected outputs, test cases, screenshots. Claude produces dramatically better results when it can verify its own work rather than relying on plausible-looking output.

This is the single highest-leverage thing you can do, per the official best practices.

## The Recommended Workflow

For non-trivial tasks, follow this cycle:

1. **Explore** -- Ask Claude to read relevant files and understand the current state
2. **Plan** -- Use Plan Mode to create a plan before coding
3. **Implement** -- Switch to Normal Mode and execute the plan
4. **Commit** -- Review changes and commit

**Plan Mode:** Press `Shift+Tab` twice to enter Plan Mode. Claude uses read-only tools to explore and creates an implementation plan for your approval. Review the plan, then switch back to Normal Mode for execution.

For the strategic significance of Plan Mode in the broader trustworthy-agents framework, see the [Trustworthy Agents Guide § Plan Mode as Strategy-Level Oversight](trustworthy-agents-guide.md#plan-mode-as-strategy-level-oversight).

**Skip planning for trivial tasks** -- typo fixes, log line additions, simple renames. Planning adds overhead that is not worth it for small changes.

## Session Management Essentials

| Command | What it does |
| --------- | ------------- |
| `Esc` | Interrupt Claude mid-action. Context is preserved. |
| `Esc` twice | Open the rewind menu -- restore conversation, code, or both to a checkpoint |
| `/rewind` | Same as double-Esc -- open the rewind menu |
| `/clear` | Reset context between unrelated tasks. **Use frequently.** |
| `/compact` | Summarize conversation to free context. Add focus: `/compact focus on the API changes` |
| `/memory` | Browse and edit memory files (CLAUDE.md, CLAUDE.local.md, rules, auto memory). To add a learning mid-session, ask Claude directly: `add this to CLAUDE.md` or `remember this`. |
| `/context` | See what is using space in your context window. Use to diagnose when context is getting full. |
| `--continue` | Resume your most recent conversation (launch flag) |
| `--resume` | Choose from recent conversations to resume (launch flag) |
| `/btw` | Side question — answer renders in a dismissible overlay and does NOT enter conversation history. Use to check a detail without growing context. |
| `/rename` | Name the current session (treat sessions like branches). Helps `claude --resume` show meaningful labels. |
| `Ctrl+G` (in plan mode) | Open the current plan in your text editor for direct edits before Claude proceeds. |
| `Esc + Esc` → **Summarize from here** | Partial compaction — pick a checkpoint and condense messages forward of it while keeping earlier context intact. |

**The most underused command is `/clear`.** When you finish one task and start another, clear the context. Leftover context from the previous task confuses Claude and wastes space.

## Permission Modes

`Shift+Tab` cycles through three modes:

| Mode | Behavior |
| ------ | ---------- |
| **Default** | Claude asks before edits and commands |
| **Auto-accept edits** | Claude edits files freely, still asks for commands |
| **Plan mode** | Read-only tools only. Creates a plan you approve before execution. |

Start with Default mode. Move to Auto-accept when you trust the task is low-risk. Use Plan mode for complex tasks where you want to review the approach first.

## Writing Effective Prompts

**Be specific upfront.** Reference files, mention constraints, point to patterns:

```text
Refactor src/api/tasks.ts to use the asyncHandler wrapper
from src/api/middleware.ts. Follow the pattern in src/api/users.ts.
```

**Delegate, don't dictate.** Give context and direction, let Claude figure out the implementation details. Over-specifying every step wastes your time and Claude's context.

**Provide rich content.** Use `@` to reference files, paste images of errors or designs, pipe data with `cat error.log | claude`. The more relevant context Claude has upfront, the fewer back-and-forth corrections needed.

## Adopting Claude Code in Existing Projects

1. **Explore existing tooling first** -- Check for linter configs, test frameworks, and build tools. Add their commands to your CLAUDE.md.
2. **Use `/init` or `/guardians-of-the-claude:create`** -- Both detect existing project structure. Choose "Existing project" when prompted.
3. **Grow incrementally** -- Start with `CLAUDE.md` + `settings.json`. Add rules, hooks, agents, and skills only when you encounter a repeatable need.

## Common Failure Patterns

| Pattern | Why it hurts | Fix |
| --------- | -------------- | ----- |
| **Kitchen Sink Session** — unrelated tasks share one context | Context from task A confuses task B | `/clear` between tasks |
| **Correcting Over and Over** | Failed attempts pollute context with noise | After two failed corrections, `/clear` and write a better prompt with what you learned |
| **Over-Specified CLAUDE.md** | Long files dilute Claude's attention | Prune ruthlessly, or split into [rule files](rules-guide.md) |
| **Trust-Then-Verify Gap** | Plausible-looking output is not the same as correct output | Provide verification criteria; include test commands in CLAUDE.md so Claude can self-check |
| **Infinite Exploration** | Unscoped "investigate the codebase" reads dozens of files and burns context | Scope narrowly: "Check only `src/auth/` for token expiration handling" |

## Further Reading

- [CLAUDE.md Guide](claude-md-guide.md) -- Writing effective instructions
- [Settings Guide](settings-guide.md) -- Configuring permissions to reduce prompts
- [Getting Started](getting-started.md) -- Full setup walkthrough
