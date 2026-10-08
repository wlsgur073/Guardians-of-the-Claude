---
title: "The .claude/ Directory Structure"
description: "Understanding the .claude/ ecosystem, auto memory, and what to version control"
version: 1.2.3
---

# The .claude/ Directory Structure

Claude Code uses several directories and files to store configuration, instructions, and learnings. This guide maps the full ecosystem so you know what each piece does and what to version control.

## What Lives in .claude/

```text
your-project/
├── CLAUDE.md                     # Project instructions (root placement)
├── CLAUDE.local.md               # Personal project instructions (gitignore it)
├── .mcp.json                     # Team-shared MCP servers (commit; no inline secrets)
├── .claude/
│   ├── CLAUDE.md                 # Project instructions (alternative placement)
│   ├── settings.json             # Team-shared settings (commit this)
│   ├── settings.local.json       # Personal overrides (gitignored)
│   ├── rules/                    # Modular instruction files
│   │   ├── code-style.md
│   │   ├── testing.md
│   │   └── ...
│   ├── skills/                   # Skills: /name or auto-invoked (advanced)
│   │   └── scaffold-feature/
│   │       └── SKILL.md
│   ├── commands/                 # Older single-file form of skills (still works)
│   ├── agents/                   # Subagent definitions (advanced)
│   │   └── developer.md
│   ├── agent-memory/             # Memory for subagents with `memory: project`
│   ├── output-styles/            # Team-shared output styles
│   ├── workflows/                # Saved dynamic workflows (each becomes /<name>)
│   └── .plugin-cache/            # Plugin-written state (auto-generated, gitignored)
│       └── <plugin-name>/
└── src/
    └── CLAUDE.md                 # Folder-level instructions (lazy-loaded)
```

Apart from `.plugin-cache/` (plugin-written state), `agent-memory/` (memory that subagents write for themselves), and `workflows/` (scripts Claude writes and you save from `/workflows`), everything shown inside `.claude/` is Claude Code configuration you author. `commands/` is the older single-file form of skills: `.claude/commands/deploy.md` and `.claude/skills/deploy/SKILL.md` both create `/deploy`, and the skill wins if both exist. Prefer skills for new work, since they can bundle supporting files. `agents/` and `skills/` are advanced features -- see the [Advanced Features Guide](advanced-features-guide.md); `workflows/` is covered in the [Dynamic Workflows guide](workflows-guide.md).

Most of these have a user-level counterpart in `~/.claude/` that applies to every project: `CLAUDE.md`, `settings.json`, `rules/`, `skills/`, `commands/`, `agents/`, `agent-memory/`, `output-styles/`, and `workflows/`, plus user-only `keybindings.json` and `themes/`. Personal MCP servers and app state live in `~/.claude.json` (outside `~/.claude/`).

## Auto Memory

Auto memory is Claude's own note-taking system. When Claude learns something about your project during a session, it saves that knowledge for future sessions.

**Location:** `~/.claude/projects/<project>/memory/` -- `<project>` is derived from the git repository path, so all worktrees and subdirectories of one repo share a single memory directory. Auto memory is machine-local; it is not shared across machines.

This is stored in your home directory, not in your project. It contains:

- **MEMORY.md** -- an index, one line per memory, loaded into every session
- **Topic files** -- one file per memory, such as `user_role.md` or `feedback_testing.md`, read on demand rather than at startup. Each records its kind in a `type` frontmatter field: `user` (your role and preferences), `feedback` (corrections you give), `project` (ongoing work and decisions not derivable from code or git), or `reference` (where to find outside information)

### The 200-Line Distinction

Both MEMORY.md and CLAUDE.md reference "200 lines" but for very different reasons:

| File | Limit | Type | What happens |
| ------ | ------- | ------ | ------------- |
| MEMORY.md | 200 lines or 25KB, whichever comes first | **Hard load boundary** | Content past the limit is not loaded at session start. Claude Code tells Claude to rewrite the index when it goes over. |
| CLAUDE.md | 200 lines | **Soft adherence guideline** | The whole file loads (up to 4 MiB; larger files are skipped), with a startup warning when it exceeds the recommended length. Shorter files produce better adherence. |

Same number, different mechanisms. MEMORY.md has a strict cutoff; CLAUDE.md is a best-practice target.

### Managing Auto Memory

Auto memory lives outside your repository, so there is nothing to create or gitignore -- Claude writes the files itself. They are plain markdown you can read, edit, or delete at any time: run `/memory` to browse the folder and toggle auto memory on or off (saved as `autoMemoryEnabled` in `~/.claude/settings.json`). To turn it off for one project, set `"autoMemoryEnabled": false` in that project's settings; `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` disables it via the environment, and `autoMemoryDirectory` stores it elsewhere.

## Plugin Cache

Some plugins store per-project state in `.claude/.plugin-cache/<plugin-name>/`. This directory is **auto-generated** by plugins and should not be manually edited or committed to version control. Keep it out of git by adding `.claude/.plugin-cache/` to your project's `.gitignore` (see below).

Example: The `guardians-of-the-claude` plugin stores a project profile, decision changelog, and accumulated recommendations in a `local/` subdirectory (`profile.json`, `recommendations.json`, `config-changelog.md`, plus the derived human-readable `state-summary.md`). These files let skills remember project context, user preferences, and pending recommendations across sessions.

## What to .gitignore

| File | Commit? | Why |
| ------ | --------- | ----- |
| `.claude/settings.json` | Yes | Team-shared configuration -- everyone uses the same permissions |
| `.claude/rules/`, `skills/`, `commands/`, `agents/`, `output-styles/`, `workflows/`, `agent-memory/` | Yes | Team-shared instructions, extensions, and project-scoped subagent memory |
| `.mcp.json` | Yes, if no inline secrets | Team-shared MCP servers -- reference secrets as `${VAR}` (see the [MCP Guide](mcp-guide.md)) |
| `.claude/settings.local.json` | No | Personal overrides -- each developer has their own |
| `CLAUDE.local.md` | No | Personal project instructions |
| `.claude/worktrees/` | No | Worktrees Claude Code creates; otherwise they show as untracked files |
| `.claude/agent-memory-local/` | No | Subagent memory with `memory: local`, meant to stay out of version control |
| `.claude/.plugin-cache/` | No | Plugin-managed state files -- auto-generated |
| Auto memory (`~/.claude/...`) | N/A | Lives outside the repo, no action needed |

Add this to your project's `.gitignore`:

```gitignore
.claude/settings.local.json
CLAUDE.local.md
.claude/worktrees/
.claude/agent-memory-local/
.claude/.plugin-cache/
```

## The Four Systems

Four systems shape a session. Claude Code loads CLAUDE.md and the auto memory index into context and applies your settings; plugin state is read by the plugin that owns it, not by Claude Code itself:

| System | Author | Purpose | Location |
| -------- | -------- | --------- | ---------- |
| **CLAUDE.md** | You | Instructions you write for Claude | `~/.claude/CLAUDE.md`, project root or `.claude/`, `CLAUDE.local.md`, subdirectories |
| **Auto memory** | Claude | Learnings Claude saves for itself | `~/.claude/projects/<project>/memory/` |
| **Settings** | You | Behavior configuration (permissions, hooks, toggles) | `~/.claude/settings.json`, `.claude/settings.json`, `.claude/settings.local.json`, managed settings |
| **Plugin cache** | Plugins | Per-project state for plugins that use this convention, such as this repo's plugin (Claude Code's own per-plugin data directory is `~/.claude/plugins/data/<id>/`) | `.claude/.plugin-cache/<plugin-name>/` |

The key insight: **CLAUDE.md is what you tell Claude. Auto memory is what Claude tells itself. Plugin cache is what plugins tell themselves.** Each system is written by a different author for different reasons.

## Further Reading

- [CLAUDE.md Guide](claude-md-guide.md) -- Writing effective CLAUDE.md files
- [Rules Guide](rules-guide.md) -- Organizing instructions into modular rule files
- [Settings Guide](settings-guide.md) -- Configuring settings.json options
