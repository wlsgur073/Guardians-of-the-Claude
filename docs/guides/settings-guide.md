---
title: "Configuring settings.json"
description: "How to configure Claude Code behavior with settings files"
version: 1.3.2
---

# Configuring settings.json

Settings files control Claude Code behavior -- permissions, toggles, and feature configuration. Unlike CLAUDE.md (which provides instructions), settings configure what Claude is allowed to do and how it operates.

## Settings File Locations

Claude Code reads settings from four locations, listed from broadest to most specific:

| Scope | Location | Committed to git? | Purpose |
| ------- | ---------- | -------------------- | --------- |
| Managed policy | Platform-specific system paths | N/A | Organization-wide policies set by admins |
| User | `~/.claude/settings.json` | No | Personal preferences across all projects |
| Project | `.claude/settings.json` | Yes | Team-shared project configuration |
| Local | `.claude/settings.local.json` | No | Personal overrides for this project |

When the same setting appears at multiple levels, more specific scopes override broader ones. Settings from all levels are merged -- you only need to specify the settings you want to change.

## What Goes Where

- **Project** (`.claude/settings.json`) — team-shared configuration. Permissions for common commands, shared deny rules. Commit it. (Plugin **source** repositories may gitignore their own `.claude/*` as dev-only — this commit guidance applies to **user** projects following this guide.)
- **Local** (`.claude/settings.local.json`) — personal overrides that should not affect teammates. Add to `.gitignore`.
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
      "Bash(git push --delete *)",
      "Bash(* --no-verify)"
    ]
  }
}
```

The `allow` list eliminates prompts for trusted routine commands; `ask` inserts confirmation for actions where the cost of being wrong is real (publishing, force-push, dependency surface); `deny` blocks actions you never want — even with confirmation. Common tool names: `Bash(command)`, `Read(path)`, `Edit(path)`, `Write(path)`.

For the full permission rule syntax, see the [official permissions documentation](https://code.claude.com/docs/en/permissions#permission-rule-syntax). For the threat-model rationale behind which patterns belong in which tier, see [`plugin/references/security-patterns.md`](../../plugin/references/security-patterns.md).

### autoMemoryEnabled

Controls whether Claude automatically saves learnings about your project to its memory system. Enabled by default; disable via `{ "autoMemoryEnabled": false }`. See the [auto memory documentation](https://code.claude.com/docs/en/memory#enable-or-disable-auto-memory) for details.

### claudeMdExcludes

Skip specific CLAUDE.md files by path or glob pattern. Useful in monorepos where some CLAUDE.md files are irrelevant to your work:

```json
{
  "claudeMdExcludes": [
    "packages/legacy-app/CLAUDE.md",
    "vendor/**/CLAUDE.md"
  ]
}
```

See the [memory documentation](https://code.claude.com/docs/en/memory#exclude-specific-claudemd-files) for details.

### hooks, env, enabledPlugins (Advanced)

The `hooks` key runs shell commands before/after tool use (e.g., auto-linting); `disableAllHooks` turns every hook off globally. The `env` key sets environment variables for Claude's commands. The `enabledPlugins` key lists official plugins. See the [Advanced Features Guide](advanced-features-guide.md) for details and examples.

## Permission Modes and Safety (Advanced)

Claude Code offers six permission modes (prompt cadence) and an OS-level sandbox for Bash subprocesses (blast radius). These are independent axes — pick each based on the work, not as alternatives.

### permissions.defaultMode

Sets the default mode for new sessions: `default` (reads only; displayed as **Manual** — `manual` is accepted as an alias in the CLI and settings, but prefer the canonical `default`), `acceptEdits` (auto-approve edits + common filesystem commands), `plan` (read-only research), `auto` (classifier-based autonomous), `dontAsk` (only pre-approved tools), `bypassPermissions` (no checks; isolated environments only). Cycle modes with `Shift+Tab` in the CLI.

```json
{ "permissions": { "defaultMode": "acceptEdits" } }
```

Auto mode is available to all users on every provider (Anthropic API, Claude Platform on AWS, Bedrock, Google Cloud's Agent Platform, Foundry, and gateway sessions). Starting August 14, 2026, it is the default permission mode for **new** sessions on Pro, Max, and Team plans — a default you set yourself stays in place unless you accept the one-time switch prompt, and org-managed defaults are unchanged. Supported models: on the Anthropic API and Claude Platform on AWS, Claude Opus 4.6+, Sonnet 4.6+, or any Fable model (Fable 5.1 / Fable 5); on the other providers, only Sonnet 5, Opus 4.7+, and the Fable models — Sonnet 4.5, Opus 4.5, Haiku, and Claude 3 models are not supported anywhere. By default the classifier allows pushes to any branch of the working repo — deploy-named branches like `production` are judged separately and push *content* is still checked — add `permissions.ask` rules for a human checkpoint before pushes. See the [permission modes documentation](https://code.claude.com/docs/en/permission-modes) for full requirements and the protected-paths list.

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

The literal string `"$defaults"` preserves built-in rules; your entries extend trust additively. Anthropic reports a 0.4% false-positive and 17% false-negative rate on internal traffic — Anthropic-internal measurements, not user-environment guarantees. See the [auto mode configuration reference](https://code.claude.com/docs/en/auto-mode-config) and the `claude auto-mode defaults` / `config` / `critique` subcommands.

### sandbox

OS-level isolation for Bash subprocesses (Seatbelt on macOS, bubblewrap on Linux/WSL2; WSL1 unsupported). Independent of permission mode. Enable via `/sandbox` or in settings:

```json
{
  "sandbox": {
    "enabled": true,
    "filesystem": { "allowWrite": ["~/.npm", "/tmp/jest"] }
  }
}
```

Linux/WSL2 require `bubblewrap` and `socat` packages. Sandboxing lets safe commands run inside defined boundaries without per-command approval — reducing permission prompts. Effective sandboxing requires both filesystem and network isolation. See the [sandboxing documentation](https://code.claude.com/docs/en/sandboxing) for `denyWrite`/`denyRead`, custom proxies, and security limitations.

**Fast mode** (`/fast`, or `"fastMode": true` in user settings) serves the same Opus model with faster output at separate premium pricing — it is not a smaller model and not an effort setting. As of September 2026 it covers Opus 5 / Opus 4.8 only — no Fable, Sonnet, or Haiku — on the Anthropic API and on subscription plans with usage credits enabled (not on Bedrock, Google Cloud, Foundry, or Claude Platform on AWS); set `fastModePerSessionOptIn` to require an explicit `/fast` each session for cost control. **Reasoning effort** is an independent quality↔latency dial set at runtime: lower effort trades response depth for speed and cost, so prefer higher effort for hard, security-sensitive, or long-running coding work. The two dials combine. Both evolve quickly — verify specifics against the current canonical docs.

**Model governance**: `availableModels` restricts which models users can select (pair with `enforceAvailableModels` to cover the default model), and `fallbackModel` lists substitutes when the primary is unavailable. Model aliases track the current generation — `fable` (Fable 5.1, the frontier tier for the hardest, longest-running work), `opus` (Opus 5; Opus 4.6 on Foundry), `sonnet` (Sonnet 5 on the Anthropic API; older Sonnets on some cloud providers), `haiku` (Haiku 4.5), and `best` (Fable where available, otherwise Opus) — and the `ANTHROPIC_DEFAULT_{OPUS,SONNET,HAIKU,FABLE}_MODEL` variables pin an alias to a specific ID. **Workflows**: `workflowSizeGuideline` and `disableWorkflows` govern the dynamic-workflows feature — see the [Dynamic Workflows Guide](workflows-guide.md).

## What NOT to Put in Project Settings

Some settings are restricted from `.claude/settings.json` for security reasons — for example, `autoMemoryDirectory` cannot be set in project settings because a shared repository could redirect memory writes to a sensitive location on a developer's machine. If you try to set a restricted option in project settings, Claude Code will ignore it; use user-level or local settings for these options instead.

## Further Reading

- [Getting Started](getting-started.md) -- Full setup walkthrough including permissions
- [Directory Structure Guide](directory-structure-guide.md) -- Where settings files live in the .claude/ ecosystem
- [Rules Guide](rules-guide.md) -- Modular instruction files (separate from settings)
