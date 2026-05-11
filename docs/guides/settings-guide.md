---
title: "Configuring settings.json"
description: "How to configure Claude Code behavior with settings files"
version: 1.1.1
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

**Project** (`.claude/settings.json`) -- Team-shared configuration that everyone on the project uses. Permissions for common commands, shared deny rules. Commit this file. (Plugin **source** repositories may gitignore their own `.claude/*` as dev-only — this commit guidance applies to **user** projects following this guide.)

**Local** (`.claude/settings.local.json`) -- Personal overrides that should not affect your teammates. Add this to `.gitignore`.

**User** (`~/.claude/settings.json`) -- Preferences that apply across all your projects. Rarely needed for beginners.

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

### permissions.allow and permissions.deny

Pre-approve or block specific tool actions using `Tool(specifier)` syntax:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm test)",
      "Bash(npm run lint)",
      "Bash(npm run build)",
      "Bash(git diff *)",
      "Bash(git log *)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)"
    ]
  }
}
```

The `allow` list eliminates permission prompts for commands you trust. The `deny` list blocks actions you never want Claude to perform. Start with your test and build commands -- those are the safest and most common.

Common tool names: `Bash(command)`, `Read(path)`, `Edit(path)`, `Write(path)`.

For the full permission rule syntax, see the [official permissions documentation](https://code.claude.com/docs/en/permissions#permission-rule-syntax).

### autoMemoryEnabled

Controls whether Claude automatically saves learnings about your project to its memory system. Enabled by default.

```json
{
  "autoMemoryEnabled": false
}
```

See the [auto memory documentation](https://code.claude.com/docs/en/memory#enable-or-disable-auto-memory) for details.

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

The `hooks` key runs shell commands before/after tool use (e.g., auto-linting). The `env` key sets environment variables for Claude's commands. The `enabledPlugins` key lists official plugins. See the [Advanced Features Guide](advanced-features-guide.md) for details and examples.

## Permission Modes and Safety (Advanced)

Claude Code offers six permission modes (prompt cadence) and an OS-level sandbox for Bash subprocesses (blast radius). These are independent axes — pick each based on the work, not as alternatives.

### permissions.defaultMode

Sets the default mode for new sessions: `default` (reads only), `acceptEdits` (auto-approve file edits + common filesystem commands), `plan` (read-only research), `auto` (classifier-based autonomous), `dontAsk` (only pre-approved tools), or `bypassPermissions` (no checks; isolated environments only).

```json
{ "permissions": { "defaultMode": "acceptEdits" } }
```

Auto mode availability requires the Anthropic API on Max, Team, Enterprise, or API plans (not Pro; not Bedrock, Vertex, or Foundry); Claude Sonnet 4.6, Opus 4.6, or Opus 4.7 (Max plan: Opus 4.7 only); and admin enablement on Team and Enterprise. Cycle modes with `Shift+Tab` in the CLI. See the [permission modes documentation](https://code.claude.com/docs/en/permission-modes) for full requirements and the protected-paths list.

### autoMode

When `defaultMode` is `auto`, a classifier evaluates each action against your declared trusted infrastructure. Configure with `autoMode.environment` (and optionally `allow`, `soft_deny`, `hard_deny`). Note: the classifier reads `autoMode` from user (`~/.claude/settings.json`), local (`.claude/settings.local.json`), and managed scopes only — it deliberately ignores `autoMode` in shared `.claude/settings.json` so a checked-in repo cannot inject its own allow rules.

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

The literal string `"$defaults"` preserves built-in rules; your entries extend trust additively. Anthropic reports a 0.4% false-positive rate on real internal traffic (n=10,000 benign tool calls) and a 17% false-negative rate on real overeager actions (n=52) — both Stage 1 + Stage 2 full-pipeline figures from Anthropic-internal measurements, not user-environment guarantees. See the [auto mode configuration reference](https://code.claude.com/docs/en/auto-mode-config) and the `claude auto-mode defaults` / `claude auto-mode config` / `claude auto-mode critique` CLI subcommands.

### sandbox

OS-level isolation for Bash subprocesses (Seatbelt on macOS, bubblewrap on Linux/WSL2; WSL1 unsupported). Independent of permission mode. Enable via the `/sandbox` command or in settings:

```json
{
  "sandbox": {
    "enabled": true,
    "filesystem": { "allowWrite": ["~/.npm", "/tmp/jest"] }
  }
}
```

Linux/WSL2 require `bubblewrap` and `socat` packages. Anthropic reports an 84% reduction in permission prompts when sandboxing is active — Anthropic-internal usage measurement, not a guarantee for arbitrary environments. Effective sandboxing requires both filesystem and network isolation. See the [sandboxing documentation](https://code.claude.com/docs/en/sandboxing) for `denyWrite`/`denyRead`, custom proxies, and security limitations.

## What NOT to Put in Project Settings

Some settings are restricted from `.claude/settings.json` for security reasons. For example, `autoMemoryDirectory` cannot be set in project settings because a shared repository could redirect memory writes to a sensitive location on a developer's machine.

If you try to set a restricted option in project settings, Claude Code will ignore it. Use user-level or local settings for these options instead.

## Further Reading

- [Getting Started](getting-started.md) -- Full setup walkthrough including permissions
- [Directory Structure Guide](directory-structure-guide.md) -- Where settings files live in the .claude/ ecosystem
- [Rules Guide](rules-guide.md) -- Modular instruction files (separate from settings)
