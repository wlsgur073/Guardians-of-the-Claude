---
title: "Using .claude/rules/"
description: "How to organize project instructions into modular, path-scoped rule files"
version: 1.0.2
---

# Using .claude/rules/

Rule files let you break your project instructions into focused, single-topic modules. Instead of one large CLAUDE.md, you maintain a set of small files that are easier to read, review, and scope to specific parts of your codebase.

## When to Use Rules vs CLAUDE.md

**Use CLAUDE.md for** core instructions that every session needs: build commands, project overview, testing instructions, key architectural decisions.

**Use `.claude/rules/` for** modular, topic-specific instructions -- especially when:

- Your CLAUDE.md is growing past 200 lines and needs to be split up
- You have instructions that apply only to certain file types or directories
- Different team members own different areas (frontend rules, backend rules, testing rules)
- You want to add or remove a topic without editing a monolithic file

A good split: CLAUDE.md holds the essentials (under 200 lines), and rule files hold the details. For task-specific procedures that don't need to be in context every session, use a skill instead -- skills load only when invoked or when Claude judges them relevant.

## File Structure

Keep one topic per file. Use descriptive filenames that make the content obvious at a glance:

```text
.claude/rules/
  code-style.md          # Naming, formatting, import conventions
  testing.md             # Test framework, patterns, coverage targets
  architecture.md        # Layer dependencies and module boundaries
  workflow.md            # Pre-development checklist and review gates
  api-design.md          # API endpoint conventions
  database.md            # Query patterns, migration rules
  security.md            # Auth, input validation, secrets handling
```

For larger projects, organize rules into subdirectories:

```text
.claude/rules/
  frontend/
    components.md        # React component patterns
    styling.md           # CSS/Tailwind conventions
  backend/
    api-handlers.md      # Express route handler rules
    database.md          # PostgreSQL query patterns
  shared/
    error-handling.md    # Cross-cutting error conventions
```

Rule files without `paths` frontmatter are loaded every session, just like CLAUDE.md. Keep them concise -- as a rule of thumb, keep the combined always-loaded total within the same ~200-line budget recommended for CLAUDE.md.

## Path-Scoping

Add a `paths` frontmatter block to make a rule file load only when Claude reads, writes, or edits a file matching the specified patterns:

```markdown
---
paths:
  - "src/api/**/*.ts"
---
# API Endpoint Rules
- All endpoints must validate input with Zod schemas
- Use the asyncHandler wrapper for all route handlers
```

Path-scoped rules are loaded on demand, not every session. This keeps context clean -- Claude only sees API rules when working on API files. Run `/context` to see which rules loaded at launch; an `InstructionsLoaded` hook can log each on-demand load (`load_reason: path_glob_match`) along with the rule's `paths` globs and the file that triggered it.

### Glob Pattern Reference

| Pattern | Matches |
| --------- | --------- |
| `**/*.ts` | All TypeScript files in any directory |
| `src/**/*` | All files under src/ |
| `*.md` | Markdown files in project root only |
| `src/components/*.tsx` | React components in a specific directory |
| `src/**/*.{ts,tsx}` | Brace expansion for multiple extensions |

Multiple patterns can be listed under `paths` -- the rule loads if any pattern matches:

```yaml
---
paths:
  - "src/api/**/*.ts"
  - "src/middleware/**/*.ts"
---
```

`paths` is the only frontmatter field Claude Code reads from a rule. Other fields are silently ignored, and `paths` accepts a YAML list or a comma-separated string. If the frontmatter YAML doesn't parse, the rule loads every session as if it had no `paths`; run `claude --debug` to see the parse error.

See `templates/advanced/.claude/rules/api-endpoints.md` for a complete path-scoped rule example.

## User-Level Rules

Place personal rule files in `~/.claude/rules/` to apply them across all your projects:

```text
~/.claude/rules/
  personal-style.md      # Your preferred coding conventions
  git-workflow.md        # Your commit message and branching preferences
```

User-level rules load before project rules, so a project rule appears later in Claude's context. Neither set overrides the other: if a user rule and a project rule conflict, Claude may follow either one. Keep personal rules to truly personal preferences (comment style, commit message format) that don't contradict your team's conventions.

## Sharing Rules Across Projects

Use symlinks to share rule files between projects without duplicating them:

```bash
# Share an entire directory of rules
ln -s ~/shared-claude-rules .claude/rules/shared

# Share a single file
ln -s ~/company-standards/security.md .claude/rules/security.md
```

This pattern works well for organization-wide standards: maintain a central repository of rule files and symlink them into each project, so every project picks up updates automatically. Make sure the symlink targets exist on every developer's machine, or use a setup script to create them.

**Note:** A symlink whose target is outside the project is treated like an external `@import`. Its rules don't load until you approve external imports in the one-time dialog at session start (v2.1.284+; earlier versions skip them without asking), and even then only rules **without** `paths` frontmatter load. Symlinks to network paths (UNC shares, `/net`, `/Network`) are not followed. To share personal rules without the approval step, keep them in `~/.claude/rules/`.

## Further Reading

- [CLAUDE.md Guide](claude-md-guide.md) -- Writing effective CLAUDE.md files and the `@import` syntax
- [Settings Guide](settings-guide.md) -- Configuring permissions and other settings
- [Getting Started](getting-started.md) -- Full setup walkthrough including rules
