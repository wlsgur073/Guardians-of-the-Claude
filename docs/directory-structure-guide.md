---
title: "The .claude/ Directory Structure"
description: "Understanding the .claude/ ecosystem, auto memory, and what to version control"
date: 2026-03-18
---

# The .claude/ Directory Structure

Claude Code uses several directories and files to store configuration, instructions, and learnings. This guide maps the full ecosystem so you know what each piece does and what to version control.

## What Lives in .claude/

```text
your-project/
├── CLAUDE.md                     # Project instructions (root placement)
├── .claude/
│   ├── CLAUDE.md                 # Project instructions (alternative placement)
│   ├── settings.json             # Team-shared settings (commit this)
│   ├── settings.local.json       # Personal overrides (gitignored)
│   └── rules/                    # Modular instruction files
│       ├── code-style.md
│       ├── testing.md
│       └── ...
└── src/
    └── CLAUDE.md                 # Folder-level instructions (lazy-loaded)
```

Everything inside `.claude/` is Claude Code configuration. The root `CLAUDE.md` and any folder-level `CLAUDE.md` files sit alongside your project files.

## Auto Memory

Auto memory is Claude's own note-taking system. When Claude learns something about your project during a session, it saves that knowledge for future sessions.

**Location:** `~/.claude/projects/<project-hash>/memory/`

This is stored in your home directory, not in your project. It contains:

- **MEMORY.md** -- an index file listing all topic memories
- **Topic files** -- individual files like `user_preferences.md`, `project_architecture.md`

### The 200-Line Distinction

Both MEMORY.md and CLAUDE.md reference "200 lines" but for very different reasons:

| File | Limit | Type | What happens |
| ------ | ------- | ------ | ------------- |
| MEMORY.md | 200 lines | **Hard load boundary** | Content past line 200 is not loaded at session start. It is truncated. |
| CLAUDE.md | 200 lines | **Soft adherence guideline** | The entire file is loaded regardless of length. But shorter files produce better adherence to your instructions. |

Same number, different mechanisms. MEMORY.md has a strict cutoff; CLAUDE.md is a best-practice target.

### You Don't Manage Auto Memory

Auto memory lives outside your repository. You do not need to create, edit, or gitignore these files -- Claude manages them automatically. You can view what Claude has saved with `/memory`.

## What to .gitignore

| File | Commit? | Why |
| ------ | --------- | ----- |
| `.claude/settings.json` | Yes | Team-shared configuration -- everyone uses the same permissions |
| `.claude/rules/` | Yes | Team-shared instruction files |
| `.claude/settings.local.json` | No | Personal overrides -- each developer has their own |
| Auto memory (`~/.claude/...`) | N/A | Lives outside the repo, no action needed |

Add this to your project's `.gitignore`:

```gitignore
.claude/settings.local.json
```

The `templates/.gitignore` scaffold includes this line ready to copy.

## The Three Systems

Claude Code has three distinct systems that are all loaded at session start but serve different purposes:

| System | Author | Purpose | Location |
| -------- | -------- | --------- | ---------- |
| **CLAUDE.md** | You | Instructions you write for Claude | Project root, `.claude/`, subdirectories |
| **Auto memory** | Claude | Learnings Claude saves for itself | `~/.claude/projects/<project>/memory/` |
| **Settings** | You | Behavior configuration (permissions, toggles) | `.claude/settings.json`, `.claude/settings.local.json` |

The key insight: **CLAUDE.md is what you tell Claude. Auto memory is what Claude tells itself.** Both inform Claude's behavior, but they are written by different authors for different reasons.

## Further Reading

- [CLAUDE.md Guide](claude-md-guide.md) -- Writing effective CLAUDE.md files
- [Rules Guide](rules-guide.md) -- Organizing instructions into modular rule files
- [Settings Guide](settings-guide.md) -- Configuring settings.json options
