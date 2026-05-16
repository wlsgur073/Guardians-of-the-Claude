---
title: "Trustworthy Agents"
description: "Five-principle, four-layer framework for evaluating Claude Code agent configuration"
version: 1.0.2
---

# Trustworthy Agents

This guide maps Anthropic's "Trustworthy Agents in Practice" framework — five principles across four architectural layers — onto concrete Claude Code configuration surfaces. Use it to evaluate whether your project's configuration provides the guarantees you intend.

## Origin & Scope

The five principles (human control, value alignment, security, transparency, privacy) and four architectural layers (model, harness, tools, environment) come from Anthropic Research's [Trustworthy Agents in Practice](https://www.anthropic.com/research/trustworthy-agents) (April 2026). This guide does *translation work*: applying that framework to the specific Claude Code surfaces in this repo — CLAUDE.md, settings.json, hooks, skills, MCP, deny patterns.

It complements the *threat-scenario lens* in [`plugin/references/security-patterns.md`](../../plugin/references/security-patterns.md), which answers "what attacks am I defending against?" This guide answers a different question: "what guarantees am I providing, and at which layer?"

## The Five Principles

### Human Control

The agent acts under human authority; humans retain the ability to inspect, override, or stop work. In Claude Code terms:

- **Plan Mode** for strategy-level oversight (see [§ Plan Mode as Strategy-Level Oversight](#plan-mode-as-strategy-level-oversight) below)
- `permissions.ask:[]` for tools that should always pause for confirmation
- `PreToolUse` hooks with `exit 2` for hard stops on dangerous operations (e.g., `git push --delete`, `rm -rf`)
- CLAUDE.md disambiguation rules for destructive operations on ambiguous identifiers

### Value Alignment

The agent pursues *your* goals — including the underlying *why*, not just the literal request. Anthropic's [Teaching Claude why](https://www.anthropic.com/research/teaching-claude-why) (May 2026) found that training Claude on principles generalizes better than training on demonstrations alone. The same logic applies to your CLAUDE.md:

- Write rationale alongside rules ("we use repository classes because handler-to-DB shortcuts have caused production data leaks" — not just "use repository classes")
- See [Getting Started](getting-started.md) for the canonical six-section CLAUDE.md structure
- Skill design that defers to human judgment on multi-valid-approach questions, rather than picking a default

### Security

The agent must not enable credential exposure, exfiltration, scope escalation, or safety bypass. The full threat catalog with named incident types lives in [`plugin/references/security-patterns.md`](../../plugin/references/security-patterns.md). Configuration surfaces:

- `permissions.deny:[]` for secret files (`.env`, `*.pem`, `*.key`, `secrets/`)
- `.claude/rules/security.md` for project-specific guarantees (auth, validation, secrets handling)
- `PreToolUse` hook protecting sensitive files by parsing stdin JSON with `jq -r '.tool_input.file_path'` (Claude Code does NOT expose a `$CLAUDE_FILE_PATH` env var; hooks receive event JSON on stdin)
- Run `/guardians-of-the-claude:secure` to apply these automatically

### Transparency

The agent's actions and reasoning are inspectable. Configuration surfaces:

- `statusMessage` in hook definitions surfaces what the hook is doing in the UI
- `.claude/.plugin-cache/<plugin>/local/config-changelog.md` records skill-issued configuration changes
- `recommendations.json` tracks issued / resolved / declined recommendations across sessions
- Subagent dispatch should produce visible threads (see [§ Subagent Observability](#subagent-observability))

### Privacy

Sensitive data does not leak into the agent's context, outputs, or external systems without user consent. Configuration surfaces:

- MCP `.mcp.json` env values use `${ENV_VAR}` placeholders, never literal credentials
- `Read(./.env)` and equivalent entries in `permissions.deny:[]`
- Secrets handling rules in `.claude/rules/security.md`
- For shared CLAUDE.md files: no inline credentials, hostnames, or internal URLs

## The Four Architectural Layers

Defense in depth: a well-trained model alone is not enough — harness, tools, and environment must coordinate.

### Model Layer

Mostly out of scope for project configuration — you pick a reputable model provider and version. What you *can* control: model selection per agent (`.claude/agents/<name>.md`), with rationale documented in YAML comments. See [Advanced Features Guide § Agents](advanced-features-guide.md#agents).

### Harness Layer

The instructions, rules, and runtime gates that shape how the agent operates. Most of your project configuration lives here:

- `CLAUDE.md` — project instructions loaded every session
- `.claude/rules/*.md` — modular instructions, path-scoped
- `.claude/settings.json` — permissions, hooks, environment
- Inline hooks in `settings.json` or external scripts in `.claude/hooks/`

Harness alone is insufficient: a perfect CLAUDE.md can still leak credentials if `permissions.deny:[]` is empty.

### Tools Layer

What the agent can invoke and with what restrictions:

- Built-in tools controlled via `permissions.allow / ask / deny`
- Skills (`.claude/skills/<name>/SKILL.md`) — see [Advanced Features § Skills](advanced-features-guide.md#skills)
- MCP servers — see [MCP Guide](mcp-guide.md)
- Per-tool granularity ("read calendar always; send invitations require approval")

Tools alone are insufficient: even narrow allows can be misused if the harness rules don't guide their use.

### Environment Layer

The OS-level boundary around the agent's actions:

- Filesystem scope (working directory, path patterns in deny rules)
- Network egress (`autoMode.environment` trust boundary; deny patterns for `Bash(curl * https://*:*)` to untrusted hosts)
- Sandboxing (`sandbox.enabled` — bubblewrap on Linux/WSL2, native Seatbelt on macOS)
- See [`security-patterns.md` § Permission and Safety Decision Principles](../../plugin/references/security-patterns.md#permission-and-safety-decision-principles)

Environment alone is insufficient: a sandbox does not stop an agent from making the wrong decision inside it.

## Layer-by-Layer Self-Audit

A diagnostic checklist — not a scoring rubric (that's what `/guardians-of-the-claude:audit` does). Walk through your current configuration and answer:

**Harness layer:**

- Does your CLAUDE.md explain *why* its rules exist, or only *what*?
- Does `settings.json` use granular `allow:` / `ask:` entries rather than wildcards like `Bash(*)`?
- Do your hooks `exit 2` for hard stops and surface a clear `statusMessage`?

**Tools layer:**

- Are deny patterns present for credential files (`.env`, `*.pem`, `*.key`, `secrets/`)?
- Do MCP servers receive credentials via `${ENV_VAR}` placeholders, never literal values?
- Are dangerous Bash subcommands (`git push --delete`, `rm -rf`, `curl|bash`) in `ask:[]` or `deny:[]`?

**Environment layer:**

- Is the agent's working directory scoped to the project, not user `$HOME`?
- For Linux/macOS users: is sandboxing enabled when running Bash commands that touch the network?
- Is `permissions.defaultMode` chosen deliberately (not just left at `default`)?

**Model layer:**

- Is the model choice per agent documented with rationale (YAML comment)?
- Are you running on a Claude Code-supported plan with the model you intend?

## Plan Mode as Strategy-Level Oversight

Plan Mode is more than a permission mode. Anthropic frames it as the shift from *step-level* oversight (approving each tool call) to *strategy-level* oversight (approving an entire plan before execution).

When to use it:

- The task scope is unclear or could expand beyond your intent
- The agent is about to make decisions in unfamiliar code
- You want a record of the plan separately from the execution

When step-level oversight is still right:

- One-off, well-defined operations
- Trusted iterative work where you'll review the diff anyway

For mechanics — how to enter Plan Mode and what it does — see [Effective Usage Guide](effective-usage-guide.md).

## Subagent Observability

When agents dispatch parallel subagents, you should retain a thread of *which subagent did what*. Configuration surfaces:

- `SubagentStop` hooks can record subagent completion events to your decision changelog
- `PostToolUse` hooks on the parent surface state changes from subagent work
- See [Advanced Features Guide § Hooks](advanced-features-guide.md#hooks) for hook event types

This guide does not prescribe a specific hook pattern — pick what matches your team's review workflow.

## Cross-references

For the defensive lens (what threats am I defending against?):

- [`plugin/references/security-patterns.md`](../../plugin/references/security-patterns.md) — Threat Catalog with named incident types

For automation:

- `/guardians-of-the-claude:secure` — applies deny patterns, security rules, file protection hooks
- `/guardians-of-the-claude:audit` — scores your config against a multi-layer rubric

For mechanics:

- [Settings Guide](settings-guide.md) — permission modes, hooks, sandbox
- [Advanced Features Guide](advanced-features-guide.md) — hooks, agents, skills
- [Effective Usage Guide](effective-usage-guide.md) — Plan Mode mechanics

## Further Reading

- Anthropic Research, [Trustworthy Agents in Practice](https://www.anthropic.com/research/trustworthy-agents) — source framework
- Anthropic Research, [Teaching Claude why](https://www.anthropic.com/research/teaching-claude-why) — Value Alignment background
- [CLAUDE.md Guide](claude-md-guide.md) — writing effective project instructions
- [Rules Guide](rules-guide.md) — modular instruction files
- [Getting Started](getting-started.md) — basic setup walkthrough
