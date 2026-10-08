---
title: "Configuring settings.json"
description: "How to configure Claude Code behavior with settings files"
version: 1.3.3
---

# Configuring settings.json

Settings files control Claude Code behavior -- permissions, toggles, and feature configuration. Unlike CLAUDE.md (which provides instructions), settings configure what Claude is allowed to do and how it operates.

## Settings File Locations

Claude Code reads settings from four locations, listed from broadest to most specific:

| Scope | Location | Committed to git? | Purpose |
| ------- | ---------- | -------------------- | --------- |
| Managed policy | `managed-settings.json` in a system directory, MDM/OS policy, or server-managed settings from the claude.ai admin console | N/A | Organization-wide policies set by admins |
| User | `~/.claude/settings.json` | No | Personal preferences across all projects |
| Project | `.claude/settings.json` | Yes | Team-shared project configuration |
| Local | `.claude/settings.local.json` | No | Personal overrides for this project |

Precedence, highest first: managed policy (your own files and `--settings` cannot override it, apart from a few security keys where a stricter lower value wins), then `--settings` on the command line, then local, project, and user. Settings from all levels are merged -- you only need to specify the settings you want to change, and list keys such as `permissions.allow` combine across files.

## What Goes Where

- **Project** (`.claude/settings.json`) — team-shared configuration. Permissions for common commands, shared deny rules. Commit it. (Plugin **source** repositories may gitignore their own `.claude/*` as dev-only — this commit guidance applies to **user** projects following this guide.)
- **Local** (`.claude/settings.local.json`) — personal overrides that should not affect teammates; "Yes, and don't ask again" approvals are saved here. Claude Code keeps it out of git when it creates the file; add it to `.gitignore` yourself only if you create it by hand.
- **User** (`~/.claude/settings.json`) — preferences across all projects. Rarely needed for beginners.

## The $schema Field

Add the `$schema` field to get editor autocomplete and validation:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [],
    "deny": []
  }
}
```

Your editor will suggest valid keys and flag errors as you type.

## Key Options for Beginners

### The three permission tiers

Permission entries categorize actions into three behavioral tiers, not just "allow" or "deny." Understanding the tiers lets you tune the prompt cadence precisely:

| Tier | Setting | When to use |
|---|---|---|
| **Regular** | (default; no entry needed) | Routine operations Claude handles every session — reading project files, running tests, basic git queries. Default permission behavior applies. |
| **Explicit-permission** | `permissions.ask: [...]` | Actions needing per-call approval — `npm install` (new dependency surface), `gh pr merge` (visible to others), `git push --force` (overwrites upstream). Use for "I want a confirmation prompt before this runs." |
| **Prohibited** | `permissions.deny: [...]` | Never permitted regardless of context — reads on `.env` / `*.pem` / `*.key`; destructive Bash patterns like `rm -rf *`; safety-bypass flags like `--no-verify`. Use for "this should never happen, period." |

`permissions.allow: [...]` is a *fourth* entry — it bypasses the prompt for routine actions, e.g., `Bash(npm test)`. Think of `allow` as a fast-path on the Regular tier, not a separate tier.

Example covering all four entries:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm test)",
      "Bash(npm run lint)",
      "Bash(npm run build)"
    ],
    "ask": [
      "Bash(npm install:*)",
      "Bash(gh pr merge:*)",
      "Bash(git push --force-with-lease:*)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Bash(rm -rf *)",
      "Bash(git push *--delete*)",
      "Bash(git commit *--no-verify*)",
      "Bash(git push *--no-verify*)"
    ]
  }
}
```

The `allow` list eliminates prompts for trusted routine commands; `ask` inserts confirmation for actions where the cost of being wrong is real (publishing, force-push, dependency surface); `deny` blocks actions you never want — even with confirmation. Common tool names: `Bash(command)`, `Read(path)`, `Edit(path)`. File-path rules use only `Read` and `Edit`: `Edit(path)` covers every tool that writes files, while a `Write(path)` rule is never consulted and triggers a startup warning.

For the full permission rule syntax, see the [official permissions documentation](https://code.claude.com/docs/en/permissions#permission-rule-syntax). For the threat-model rationale behind which patterns belong in which tier, see [`plugin/references/security-patterns.md`](../../plugin/references/security-patterns.md).

### autoMemoryEnabled

Controls whether Claude automatically saves learnings about your project to its memory system. Enabled by default; disable via `{ "autoMemoryEnabled": false }`. See the [auto memory documentation](https://code.claude.com/docs/en/memory#enable-or-disable-auto-memory) for details.

### claudeMdExcludes

Skip specific CLAUDE.md files by path or glob pattern. Useful in monorepos where some CLAUDE.md files are irrelevant to your work:

```json
{
  "claudeMdExcludes": [
    "**/packages/legacy-app/CLAUDE.md",
    "**/vendor/**/CLAUDE.md"
  ]
}
```

See the [memory documentation](https://code.claude.com/docs/en/memory#exclude-specific-claude-md-files) for details.

### hooks, env, enabledPlugins (Advanced)

The `hooks` key runs your own commands (or prompts, agents, HTTP requests, MCP tools) at lifecycle points such as before/after a tool call (e.g., auto-linting); `disableAllHooks` turns hooks off along with any custom status line and file-suggestion command, but outside managed settings it leaves managed hooks running. The `env` key sets environment variables for every session and the subprocesses it starts. The `enabledPlugins` key turns individual plugins on or off, keyed by `plugin-name@marketplace-name`. See the [Advanced Features Guide](advanced-features-guide.md) for details and examples.

## Permission Modes and Safety (Advanced)

Claude Code offers six permission modes (prompt cadence) and an OS-level sandbox for the shell commands Claude runs (blast radius). These are independent axes — pick each based on the work, not as alternatives.

### permissions.defaultMode

Sets the default mode for new sessions: `default` (reads only; displayed as **Manual** — `manual` is accepted as an alias in the CLI and settings, but prefer the canonical `default`), `acceptEdits` (auto-approve edits + common filesystem commands), `plan` (research without edits), `auto` (classifier-based autonomous), `dontAsk` (only pre-approved tools), `bypassPermissions` (skips prompts, but `deny` rules still block and `ask` rules still prompt; isolated environments only). `auto` and `bypassPermissions` take effect only from `~/.claude/settings.json`, managed settings, `--settings`, or `--permission-mode`, never from `.claude/settings.json` / `.claude/settings.local.json`. Cycle modes with `Shift+Tab` in the CLI.

```json
{ "permissions": { "defaultMode": "acceptEdits" } }
```

Auto mode is available to all users on every provider (Anthropic API, Claude Platform on AWS, Bedrock, Google Cloud's Agent Platform, Foundry, and gateway sessions). With Claude Code v2.1.283+, it is the built-in starting mode for interactive terminal and VS Code sessions on every plan and provider whenever no `permissions.defaultMode` is set (earlier versions: Pro, Max, and Team only) — a `defaultMode` you set still wins (Claude Code may offer once to switch it), `claude -p` and the Agent SDK usually start in `default`, and admins can remove auto mode with `permissions.disableAutoMode: "disable"`. Supported models: on the Anthropic API and Claude Platform on AWS, Claude Opus 4.6+, Sonnet 4.6+, Haiku 5.5, or any Fable model; on Bedrock, Google Cloud's Agent Platform, Foundry, and Claude apps gateway sessions, only Sonnet 5+, Opus 4.7+, Haiku 5.5, and the Fable models — Sonnet 4.5, Opus 4.5, Haiku 4.5, and Claude 3 models are not supported anywhere. By default the classifier allows pushes to any branch of the working repo — deploy-named branches like `production` are judged separately and push *content* is still checked — add `permissions.ask` rules for a human checkpoint before pushes. See the [permission modes documentation](https://code.claude.com/docs/en/permission-modes) for full requirements and the protected-paths list.

### autoMode

When `defaultMode` is `auto`, a classifier evaluates each action against your declared trusted infrastructure. Configure with `autoMode.environment` (and optionally `allow`, `soft_deny`, `hard_deny`). The classifier reads `autoMode` from user (`~/.claude/settings.json`) and managed scopes, plus the `--settings` flag, only — it deliberately ignores **both** project files, `.claude/settings.json` and `.claude/settings.local.json`, since either could be written by a checked-in repo or a build step to inject allow rules. (Older versions read `settings.local.json`; move any `autoMode` block there to user settings.)

```json
{
  "autoMode": {
    "environment": [
      "$defaults",
      "Source control: github.com/your-org"
    ]
  }
}
```

The literal string `"$defaults"` preserves built-in rules; your entries extend trust additively. Anthropic reports a 0.4% false-positive and 17% false-negative rate on internal traffic — Anthropic-internal measurements, not user-environment guarantees. See the [auto mode configuration reference](https://code.claude.com/docs/en/auto-mode-config), `/auto-mode-setup` (drafts `environment` entries for you; Pro, Max, or Team), and the `claude auto-mode defaults` / `config` / `critique` / `reset` subcommands; `autoMode.classifyAllShell: true` sends every shell command through the classifier even when an allow rule matches.

### sandbox

OS-level isolation for the shell commands Claude runs — Bash, PowerShell, and Monitor commands and their child processes (Seatbelt on macOS, bubblewrap on Linux/WSL2; not available on WSL1 or native Windows, where commands run unsandboxed). Independent of permission mode. Enable via `/sandbox` or in settings:

```json
{
  "sandbox": {
    "enabled": true,
    "filesystem": { "allowWrite": ["~/.npm", "/tmp/jest"] }
  }
}
```

Linux/WSL2 require `bubblewrap` and `socat` packages. Sandboxing lets safe commands run inside defined boundaries without per-command approval — reducing permission prompts. Effective sandboxing requires both filesystem and network isolation. See the [sandboxing documentation](https://code.claude.com/docs/en/sandboxing) for `denyWrite`/`denyRead`, custom proxies, and security limitations.

**Fast mode** (`/fast`, or `"fastMode": true` in user settings) serves the same Opus model with faster output at separate premium pricing — it is not a smaller model and not an effort setting. As of October 2026 it covers Opus 5.5 (the fast-mode default since v2.1.280; $8/$40 per MTok), Opus 5, and Opus 4.8 ($10/$50) only — no Fable, Sonnet, or Haiku — on the Anthropic API and on subscription plans with usage credits enabled, after an Owner enables it on Team/Enterprise (not on Bedrock, Google Cloud, Foundry, or Claude Platform on AWS); set `fastModePerSessionOptIn` to require an explicit `/fast` each session for cost control. **Reasoning effort** is an independent quality↔latency dial — set it with `/effort` (saved per model under `modelSettings`) or `--effort` for one session, and cap it with `maxEffortLevel`. Opus 5.5, Sonnet 5.5, and Haiku 5.5 default to `medium` (most other models to `high`); lower effort trades response depth for speed and cost, so raise it for hard, security-sensitive, or long-running coding work. The two dials combine. Both evolve quickly — verify specifics against the current canonical docs.

**Model governance**: `availableModels` restricts which models users can select (pair with `enforceAvailableModels` to cover the default model); an entry like `claude-opus-5` also permits later versions such as Opus 5.5, so use the managed-only `deniedModels` or `availableModelsMatch: "exact"` (v2.1.283+) to hold a release back; `fallbackModel` lists up to three substitutes when the primary is overloaded or unavailable. Model aliases track the current generation — `fable` (Fable 5.1, the frontier tier for the hardest, longest-running work; Fable 5 in Claude apps gateway sessions), `opus` (Opus 5.5; Opus 4.6 on Foundry), `sonnet` (Sonnet 5.5 on the Anthropic API; Sonnet 4.6 or 4.5 on cloud providers), `haiku` (Haiku 5.5 on the Anthropic API; Haiku 4.5 elsewhere), and `best` (Fable where available, otherwise Opus); the 5.5 models need Claude Code v2.1.280 (Opus), v2.1.284 (Sonnet), and v2.1.293 (Haiku) or later — and the `ANTHROPIC_DEFAULT_{OPUS,SONNET,HAIKU,FABLE}_MODEL` variables pin an alias to a specific ID. **Workflows**: `enableWorkflows`, `workflowSizeGuideline`, `workflowKeywordTriggerEnabled`, `ultracode`, and `disableWorkflows` govern the dynamic-workflows feature — see the [Dynamic Workflows Guide](workflows-guide.md).

## What NOT to Put in Project Settings

Some settings never take effect from `.claude/settings.json` because a cloned repository or build step could write them — for example the `autoMode` classifier block and `permissions.defaultMode` values `auto` / `bypassPermissions` (both are ignored in `.claude/settings.local.json` too). Apart from a few noted exceptions, any key whose Scope in the [settings index](https://code.claude.com/docs/en/settings-reference#settings-index) reads `User, local, or managed`, `User or managed`, `Managed`, or `Global config` is ignored in the shared file; set it in `~/.claude/settings.json`, managed settings, or `~/.claude.json` as its Scope says. Separately, `permissions.allow` rules and `additionalDirectories` from a committed file apply only after each teammate accepts the workspace trust dialog for that folder (repository `extraKnownMarketplaces` entries also need the folder itself trusted), while `deny` and `ask` rules apply right away. Hooks and the `env` block are not gated this way: a trusted parent folder is enough for them, and `claude -p` uses them in a folder never trusted. A few `env` variables, such as `CLAUDE_CONFIG_DIR`, `HOME`, and the OpenTelemetry exporter variables that turn telemetry on, are ignored in project and local settings altogether.

## Further Reading

- [Getting Started](getting-started.md) -- Full setup walkthrough including permissions
- [Directory Structure Guide](directory-structure-guide.md) -- Where settings files live in the .claude/ ecosystem
- [Rules Guide](rules-guide.md) -- Modular instruction files (separate from settings)
