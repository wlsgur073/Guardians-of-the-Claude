---
title: "Workflow Patterns"
description: "Interview-first specs, Writer/Reviewer, test-first multi-Claude, fan-out (with cost/safety warnings), worktrees and parallel sessions"
version: 1.0.4
---

# Workflow Patterns

How you structure your time with Claude Code matters as much as what you ask. These patterns appear repeatedly in Anthropic's internal teams and external engineering reports.

For *multi-agent dispatch* (an orchestrator coordinating workers), see [Multi-Agent Patterns Guide](multi-agent-patterns-guide.md). This guide is about how *you, the human*, organize sessions and batches. It is also distinct from Claude Code's **dynamic workflows** feature (Claude-authored orchestration scripts) — that's the [Dynamic Workflows Guide](workflows-guide.md).

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

For large migrations or analyses, distribute work across many Claude invocations. Try the built-in options first. `/batch <instruction>` plans the change, splits it into 5–30 units and, once you approve the plan, runs one worktree-isolated subagent per unit. A [dynamic workflow](workflows-guide.md) scripts larger or cross-checked fan-outs. To drive the fan-out from your own script, loop over `claude -p`. The bash loop below dispatches calls sequentially; add `xargs -P` or `ForEach-Object -Parallel` if you want bounded concurrency.

> **⚠️ Cost and safety warning**
>
> - `claude -p` in a loop incurs token cost per invocation. A multi-thousand-file migration can run for hours and accumulate substantial cost — always estimate with your model's per-token pricing before scaling.
> - Always dry-run on 2–3 files first; verify outputs before scaling.
> - Use `--allowedTools` to pre-approve what the run needs and `--permission-mode dontAsk` to deny everything else: `claude -p "..." --allowedTools "Edit,Bash(git commit *)" --permission-mode dontAsk`. Without `--permission-mode` or a `defaultMode` setting, `-p` starts in `default`, or in `auto` in sessions that don't fetch feature flags, such as on third-party providers or with telemetry off (v2.1.285+).
> - In auto mode, repeated classifier blocks do **not** stop a `-p` run. The blocked action is skipped and Claude keeps working, so review each run's output instead of counting on an abort. See [When auto mode falls back](https://code.claude.com/docs/en/permission-modes#when-auto-mode-falls-back) for the thresholds.

Pattern:

1. **Generate the task list**: `Have Claude list all 2,000 Python files that need migrating and write them to files.txt`.
2. **Loop**:

   ```bash
   # Sequential (one at a time)
   for file in $(cat files.txt); do
     claude -p "Migrate $file from React to Vue. Return OK or FAIL." \
       --allowedTools "Edit,Bash(git commit *)" --permission-mode dontAsk
   done

   # Bounded parallel (4 workers at a time)
   cat files.txt | xargs -I {} -P 4 \
     claude -p "Migrate {} from React to Vue. Return OK or FAIL." \
       --allowedTools "Edit,Bash(git commit *)" --permission-mode dontAsk
   ```

**PowerShell equivalents (Windows):**

```powershell
# Sequential
Get-Content files.txt | ForEach-Object { claude -p "Migrate $_ from React to Vue. Return OK or FAIL." --allowedTools "Edit,Bash(git commit *)" --permission-mode dontAsk }

# Bounded parallel (4 workers; requires PowerShell 7+)
Get-Content files.txt | ForEach-Object -Parallel { claude -p "Migrate $_ from React to Vue. Return OK or FAIL." --allowedTools "Edit,Bash(git commit *)" --permission-mode dontAsk } -ThrottleLimit 4
```

3. **Refine on first 2–3, then scale**: catch broken prompts early; only run on the full set after you have seen the output shape.

For JSON-structured output (parsing in your script), add `--output-format json`. For streaming, add `--output-format stream-json --verbose`.

## Worktrees and parallel sessions

When you need genuinely isolated parallel work (e.g., experimenting on a risky refactor while continuing main-line work), start Claude in its own git worktree:

```bash
claude --worktree feature-x   # or -w; creates .claude/worktrees/feature-x/ on new branch worktree-feature-x
```

The new branch starts from the repository's default branch on the remote (set `worktree.baseRef` to `"head"` to branch from your current `HEAD`); to work on an existing branch, create the worktree yourself with `git worktree add ../feature-x feature-x` and run `claude` there. Run `claude -w` with another name in a second terminal for a second isolated session, and add `.claude/worktrees/` to `.gitignore`. On exit, Claude removes a clean worktree automatically (a named session asks first) and asks whether to keep or remove one that has changes. `claude -p --worktree` runs have no exit prompt: remove those with `git worktree remove`, running `git worktree unlock` first if git refuses. Remove worktrees you created with `git worktree add` the same way, and run `git worktree prune` for orphaned entries.

| Option | Best for |
|---|---|
| `claude --worktree <name>` (CLI) | Same machine, full isolation, manual coordination |
| Agent view (`claude agents`, research preview) | Dispatching background sessions and watching them from one screen; each moves into its own worktree before editing |
| Desktop app parallel sessions | Visual session management, optionally one worktree per session |
| Claude Code on the web | Anthropic-managed cloud sessions |
| Cross-session messaging | Letting sessions you run yourself pass findings to each other |

When *not* to multi-session: small focused tasks. Switching context between sessions has overhead — you lose more than you gain unless the tasks are truly independent.

## Further reading

- [Multi-Agent Patterns Guide](multi-agent-patterns-guide.md) — orchestrator dispatching workers (vs human-orchestrated multi-session)
- [Claude Code: Best practices for agentic coding](https://code.claude.com/docs/en/best-practices) — upstream source for many patterns here
- [Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode) — for headless and auto-pilot details
