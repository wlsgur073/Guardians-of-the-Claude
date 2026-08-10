---
title: "Dynamic Workflows"
description: "Claude-authored orchestration scripts — starting, approving, saving, and governing multi-agent workflow runs"
version: 1.0.0
---

# Dynamic Workflows

A dynamic workflow is a JavaScript script that orchestrates subagents at scale. Claude writes the script for the task you describe; a runtime executes it in the background while your session stays responsive, and only the final result lands in your context. Requires Claude Code v2.1.154+ (individual subfeatures below arrived in later versions — the official docs note each), on paid plans via the Anthropic API, Bedrock, Google Cloud's Agent Platform, and Foundry (on Pro, enable it from the Dynamic workflows row in `/config`).

## When a workflow beats a subagent

The difference is **who holds the plan**. With subagents and skills, Claude orchestrates turn by turn and every intermediate result lands in a context window. A workflow moves the plan into code: the script holds the loop, the branching, and the intermediate results, so it can coordinate dozens to hundreds of agents — and encode quality patterns like adversarial cross-checking of findings before they are reported.

Reach for one when a task is larger than one conversation can coordinate (codebase-wide audits, many-file migrations, cross-checked research), or when you want the orchestration itself to be reviewable and rerunnable. For orchestrator *patterns* — what to fan out, what to verify — see the [Multi-Agent Patterns Guide](multi-agent-patterns-guide.md).

## Starting and watching a run

- **Ask in your prompt.** Include the keyword `ultracode`, or just say "use a workflow" — a direct request counts as the same opt-in. Claude writes a script for the task instead of working turn by turn.
- **`/effort ultracode`** combines `xhigh` reasoning effort with automatic workflow planning for every substantive task in the session. Session-scoped; drop back with `/effort high`.
- **`/deep-research <question>`** is the bundled workflow: parallel web searches, source cross-checking, claim voting, one cited report. It runs only when you invoke it.
- **`/workflows`** lists runs and opens a progress view — per-phase agent counts, token totals, drill-down into any agent's prompt and result, pause/resume/stop controls.

The `ultracode` keyword is an opt-in **only in a prompt a human typed** (interactive prompt, IDE panel, Remote Control, or SDK input stamped as human). It does not trigger from `-p` prompts, scheduled tasks, webhook payloads, or PR comments relayed into the conversation — relayed external content cannot activate the keyword opt-in.

## The approval gate and what the script may do

Before a run starts, Claude Code shows the planned phases with **Yes / Yes-don't-ask-again (per workflow, per project) / View raw script / No**. Whether you are prompted depends on permission mode: `default` and `acceptEdits` prompt every run (until you grant don't-ask-again for that workflow in that project); `auto` prompts on first launch only, and not at all under ultracode; `bypassPermissions`, `claude -p`, and the Agent SDK never prompt. Treat the script as code under review — `View raw script` (or `Ctrl+G` to open it in your editor) before granting a standing **don't ask again**.

Two trust facts worth internalizing:

- **Workflow subagents always run in `acceptEdits` mode and inherit your tool allowlist, regardless of your session's permission mode.** File edits are auto-approved. Shell commands, web fetches, and MCP tools outside your allowlist still prompt mid-run — pre-approve what a long run needs, and keep your `deny` rules tight since they apply here too.
- Every run writes its script to a file under your session directory in `~/.claude/projects/`, so you can read, diff, or edit the orchestration Claude wrote and relaunch from the edited version.

## Saving and reusing workflows

From `/workflows`, press `s` on a run to save its script as a command:

| Location | Scope | Wins on name conflict? |
|---|---|---|
| `.claude/workflows/` (project) | Everyone who clones the repo | Beats a same-named personal workflow; in monorepos the copy closest to your working directory wins |
| `~/.claude/workflows/` (personal) | Every project, only you | — |

Saved workflows run as `/<name>` and accept input: "Run /triage-issues on issues 1024, 1025, and 1030" reaches the script as a structured `args` global. Plugins can ship workflows too — a `workflows/` directory at the plugin root runs namespaced as `/plugin-name:workflow-name`, keeping plugin names from colliding with your project and personal workflow names.

A project-saved workflow is repo content: review `.claude/workflows/` in PRs like any executable, since everyone who clones the repo can invoke it by name.

## Governing size, cost, and availability

- **`workflowSizeGuideline`** (`/config`, or any settings file): `small` (<5 agents), `medium` (<15 — the default), `large` (<50), `unrestricted`. Advisory, not a cap — a prompt that calls for a different scale overrides it.
- **Runtime caps** always apply: at most 16 concurrent agents (fewer on limited CPUs) and 1,000 agents per run.
- **Large-run warning**: a run that schedules more than 25 agents (or your guideline's count) or projects past 1.5M tokens flags `Large workflow` in the task panel — advisory; stop it from `/workflows` if unintended.
- **Cost**: a run can use far more tokens than the same task in conversation and counts toward plan usage. Gauge spend on a small slice first (one directory, a narrow question). Agents use your session's model unless the script routes a stage elsewhere or `CLAUDE_CODE_SUBAGENT_MODEL` overrides both; an org `availableModels` allowlist substitutes blocked models and warns in the progress view.
- **Turning it off**: `"disableWorkflows": true` in settings (or managed settings for the whole org), the `/config` toggle, or `CLAUDE_CODE_DISABLE_WORKFLOWS=1`. Disabling removes the bundled commands, the `ultracode` keyword trigger, and the `/effort ultracode` option.

## Further Reading

- [Settings Guide](settings-guide.md) — where `workflowSizeGuideline` / `disableWorkflows` live among the other governance keys
- [Multi-Agent Patterns Guide](multi-agent-patterns-guide.md) — orchestration patterns the script encodes
- [Workflow Patterns Guide](workflow-patterns-guide.md) — how *you, the human*, structure sessions (a different topic than this feature)
- [Official workflows documentation](https://code.claude.com/docs/en/workflows) — script API, resume semantics, full reference
