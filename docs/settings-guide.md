---
title: "Configuring settings.json"
description: "How to configure Claude Code behavior with settings files"
date: 2026-03-18
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

**Project** (`.claude/settings.json`) -- Team-shared configuration that everyone on the project uses. Permissions for common commands, shared deny rules. Commit this file.

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

## What NOT to Put in Project Settings

Some settings are restricted from `.claude/settings.json` for security reasons. For example, `autoMemoryDirectory` cannot be set in project settings because a shared repository could redirect memory writes to a sensitive location on a developer's machine.

If you try to set a restricted option in project settings, Claude Code will ignore it. Use user-level or local settings for these options instead.

## Further Reading

- [Getting Started](getting-started.md) -- Full setup walkthrough including permissions
- [Directory Structure Guide](directory-structure-guide.md) -- Where settings files live in the .claude/ ecosystem
- [Rules Guide](rules-guide.md) -- Modular instruction files (separate from settings)
