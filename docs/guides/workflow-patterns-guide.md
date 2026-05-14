---
title: "Workflow Patterns"
description: "Interview-first specs, Writer/Reviewer, test-first multi-Claude, fan-out (with cost/safety warnings), worktrees and parallel sessions"
version: 1.0.1
---

# Workflow Patterns

How you structure your time with Claude Code matters as much as what you ask. These patterns appear repeatedly in Anthropic's internal teams and external engineering reports.

For *multi-agent dispatch* (an orchestrator coordinating workers), see [Multi-Agent Patterns Guide](multi-agent-patterns-guide.md). This guide is about how *you, the human*, organize sessions and batches.

## Let Claude interview you with `AskUserQuestion`

For larger features, do not write the spec yourself in one shot. Have Claude interview you first:

```text
I want to build [brief description]. Interview me in detail using the
AskUserQuestion tool.

Ask about technical implementation, UI/UX, edge cases, concerns, and
tradeoffs. Don't ask obvious questions — dig into the hard parts I might
not have considered.

Keep interviewing until we've covered everything, then write a complete
spec to SPEC.md.
```

When the interview is done, start a **fresh session** to execute the spec. The new session has clean context focused entirely on implementation, and you have a written reference.

Why this works:

- The interview surfaces decisions you would have made implicitly and now must make explicitly.
- Restarting in a fresh session means the implementation is not biased by the brainstorm.

## Writer/Reviewer pattern (multi-session)

| Session A (Writer) | Session B (Reviewer) |
|---|---|
| `Implement a rate limiter for our API endpoints` |   |
|   | `Review the rate limiter implementation in @src/middleware/rateLimiter.ts. Look for edge cases, race conditions, consistency with existing middleware patterns.` |
| `Here's the review feedback: [Session B output]. Address these issues.` |   |

The reviewer, in fresh context, has no bias toward the code Session A just wrote. This catches issues that an in-session "review my work" prompt would miss.

Same principle: have one Claude write tests, another write the code to pass them. Boundaries become explicit.

## Test-first multi-Claude

1. Session A: `Write tests for the user signup flow covering: valid signup, duplicate email, weak password, expired invite token, rate-limit exceeded.`
2. Session B (fresh): `Implement the signup flow to pass tests in tests/signup.test.ts. Run the tests after each change.`

Forces acceptance criteria to crystallize before implementation. Works inside one session too (write tests, `/clear`, implement) but separate sessions give cleaner context.

## Fan-out for batch tasks

For large migrations or analyses, run many `claude -p` invocations in parallel.

> **⚠️ Cost and safety warning**
>
> - `claude -p` in a loop incurs token cost per invocation. A 2,000-file migration may run for hours and cost $100+.
> - Always dry-run on 2–3 files first; verify outputs before scaling.
> - Use `--allowedTools` to scope permissions for unattended runs: `claude -p "..." --allowedTools "Edit,Bash(git commit:*)"`
> - Auto mode aborts after repeated classifier denials in `-p` runs — there is no human to fall back to. See [Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode) for thresholds.

Pattern:

1. **Generate the task list**: `Have Claude list all 2,000 Python files that need migrating and write them to files.txt`.
2. **Loop**:

   ```bash
   for file in $(cat files.txt); do
     claude -p "Migrate $file from React to Vue. Return OK or FAIL." \
       --allowedTools "Edit,Bash(git commit:*)"
   done
   ```

**PowerShell equivalent (Windows):**

```powershell
Get-Content files.txt | ForEach-Object { claude -p "Migrate $_ from React to Vue. Return OK or FAIL." --allowedTools "Edit,Bash(git commit:*)" }
```

3. **Refine on first 2–3, then scale**: catch broken prompts early; only run on the full set after you have seen the output shape.

For JSON-structured output (parsing in your script), add `--output-format json`. For streaming, `--output-format stream-json`.

## Worktrees and parallel sessions

When you need genuinely isolated parallel work (e.g., experimenting on a risky refactor while continuing main-line work), use `git worktree`:

```bash
git worktree add ../feature-x feature-x
cd ../feature-x
claude  # this session works on feature-x branch only; main worktree is untouched
```

When done with a worktree, remove it cleanly:

```bash
git worktree remove ../feature-x
git worktree list  # confirm it's gone
```

Stale worktree registrations accumulate if you only delete the directory without `git worktree remove`. Run `git worktree prune` to clean up orphaned entries.

| Option | Best for |
|---|---|
| `git worktree` (CLI) | Same machine, full isolation, manual coordination |
| Desktop app multi-session | Visual session management |
| Claude Code on the web | Anthropic-hosted, isolated VMs |

When *not* to multi-session: small focused tasks. Switching context between sessions has overhead — you lose more than you gain unless the tasks are truly independent.

## Further reading

- [Multi-Agent Patterns Guide](multi-agent-patterns-guide.md) — orchestrator dispatching workers (vs human-orchestrated multi-session)
- [Claude Code: Best practices for agentic coding](https://code.claude.com/docs/en/best-practices) — upstream source for many patterns here
- [Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode) — for headless and auto-pilot details
