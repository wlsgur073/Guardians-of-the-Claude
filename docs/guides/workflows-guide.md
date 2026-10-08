---
title: "Dynamic Workflows"
description: "Claude-authored orchestration scripts — starting, approving, saving, and governing multi-agent workflow runs"
version: 1.0.1
---

# Dynamic Workflows

A dynamic workflow is a JavaScript script that orchestrates subagents at scale. Claude writes the script for the task you describe; a runtime executes it in the background while your session stays responsive, and only the final result lands in your context. Requires Claude Code v2.1.154+ (individual subfeatures below arrived in later versions — the official docs note each), on all paid plans, with Anthropic API access, and on Bedrock, Google Cloud's Agent Platform, and Foundry (on Pro, enable it from the Dynamic workflows row in `/config`).

## When a workflow beats a subagent

The difference is **who holds the plan**. With subagents and skills, Claude orchestrates turn by turn and every intermediate result lands in a context window. A workflow moves the plan into code: the script holds the loop, the branching, and the intermediate results, so it can coordinate dozens to hundreds of agents — and encode quality patterns like adversarial cross-checking of findings before they are reported.

Reach for one when a task is larger than one conversation can coordinate (codebase-wide audits, many-file migrations, cross-checked research), or when you want the orchestration itself to be reviewable and rerunnable. For orchestrator *patterns* — what to fan out, what to verify — see the [Multi-Agent Patterns Guide](multi-agent-patterns-guide.md).

## Starting and watching a run

- **Ask in your prompt.** Include the keyword `ultracode`, or just say "use a workflow" — a direct request counts as the same opt-in. Claude writes a script for the task instead of working turn by turn.
- **`/effort ultracode`** turns on automatic workflow planning for every substantive task in the session, at whatever effort level the session already runs (v2.1.284+; earlier versions forced `xhigh`). Turn it off with `/effort ultracode off`; picking another effort level no longer does. `claude --effort ultracode` starts a session with it on at `xhigh`, and `"ultracode": true` in settings starts every session with it on. While it is on, the `Large workflow` warning, the auto-mode first-launch approval and the session's concurrent-subagent limit are skipped, and every request uses more tokens.
- **`/deep-research <question>`** is the bundled workflow: parallel web searches, source cross-checking, claim voting, one cited report. It runs only when you invoke it.
- **`/workflows`** lists runs and opens a progress view — per-phase agent counts, token totals, drill-down into any agent's prompt and result, pause/resume/stop controls.

The `ultracode` keyword is an opt-in **only in a prompt a human typed** (interactive prompt, IDE panel, Remote Control, or SDK input stamped as human). It does not trigger from `-p` prompts, scheduled tasks, webhook payloads, or PR comments relayed into the conversation — relayed external content cannot activate the keyword opt-in.

## The approval gate and what the script may do

Before a run starts, Claude Code shows the planned phases with **Yes / Yes-don't-ask-again (per workflow, per project) / View raw script / No**. Whether you are prompted depends on permission mode: `default` and `acceptEdits` prompt every run (until you grant don't-ask-again for that workflow in that project); `auto` prompts on first launch only, and not at all under ultracode; `bypassPermissions` starts the run immediately. `claude -p` and the Agent SDK never show the prompt, but they evaluate the Workflow tool call like any other tool call, so deny and ask rules and `dontAsk` apply. To allow launches there, use a `Workflow` permission rule (every workflow) or `Workflow(<name>)` (one saved workflow), auto mode's classifier, an allowing `PreToolUse` hook, or `--permission-prompt-tool`/`canUseTool`. **Don't ask again** is offered only for bundled, saved or plugin workflows run by name, not for a script Claude just wrote. Treat the script as code under review — `View raw script` (or `Ctrl+G` to open it in your editor) before granting a standing **don't ask again**.

Two trust facts worth internalizing:

- **Workflow subagents use your permission rules and the normal subagent permission-mode rules.** They do not get a special mode. When your session is in `acceptEdits`, `auto` or `bypassPermissions`, they run in that same mode. Otherwise they run in the mode their agent definition sets (never `bypassPermissions`), or in your session's mode. Anything that would prompt pauses the run mid-way, so pre-approve what a long run needs. Keep your `deny` rules tight, since they apply here too. In auto mode, the classifier does not treat the prompt a script passes to `agent()` as a request from you.
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

- **`workflowSizeGuideline`** (`/config` → Dynamic workflow size, or any settings file, which takes precedence and hides the `/config` row): `small` (<5 agents), `medium` (<10 — the default; Pro plans default to `small` on v2.1.271+), `large` (<50), `unrestricted`. Advisory, not a cap — a prompt that calls for a different scale overrides it.
- **Runtime caps** always apply: 1,000 agents per run, up to 4,096 items per `parallel()`/`pipeline()` call, and 16 concurrent agents by default (fewer on limited CPUs). On v2.1.269+, `CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS` sets the concurrency from 1 to 256; higher values use more memory.
- **Large-run warning**: a run that schedules more than 25 agents (or the count of a size guideline you chose yourself) or projects past 1.5M tokens flags `Large workflow` in the task panel — advisory; stop it from `/workflows` if unintended.
- **Cost**: a run can use far more tokens than the same task in conversation and counts toward plan usage. Gauge spend on a small slice first (one directory, a narrow question). Each agent's model is resolved the same way as a subagent's. A model the script names for a stage comes first, then the agent definition's `model`, then `CLAUDE_CODE_SUBAGENT_MODEL` (a default since v2.1.251, not an override), then your session's model. To force one model onto every workflow agent, also set `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` (v2.1.257+). An org `availableModels` allowlist substitutes blocked models and warns in the progress view.
- **Turning it off or on**: the `/config` **Dynamic workflows** toggle writes `enableWorkflows` to your user settings; `true` turns workflows on where your plan defaults them off, as on Pro. `"disableWorkflows": true` turns them off for everyone a settings file reaches (managed settings, or the Claude Code admin settings page, for a whole org). `CLAUDE_CODE_DISABLE_WORKFLOWS=1` turns them off for a session. To keep workflows but stop the `ultracode` keyword from starting one, set `"workflowKeywordTriggerEnabled": false`. Disabling removes the bundled commands, the `ultracode` keyword trigger, and the `/effort ultracode` option.

## Further Reading

- [Settings Guide](settings-guide.md) — where the workflow keys (`enableWorkflows`, `workflowSizeGuideline`, `workflowKeywordTriggerEnabled`, `ultracode`, `disableWorkflows`) sit among the other governance keys
- [Multi-Agent Patterns Guide](multi-agent-patterns-guide.md) — orchestration patterns the script encodes
- [Workflow Patterns Guide](workflow-patterns-guide.md) — how *you, the human*, structure sessions (a different topic than this feature)
- [Official workflows documentation](https://code.claude.com/docs/en/workflows) — script API, resume semantics, full reference
