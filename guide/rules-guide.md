---
title: "Using .claude/rules/"
description: "How to organize project instructions into modular, path-scoped rule files"
date: 2026-03-18
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

A good split: CLAUDE.md holds the essentials (under 200 lines), and rule files hold the details.

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

Rule files without `paths` frontmatter are loaded every session, just like CLAUDE.md. Keep them concise -- the same "under 200 lines" guideline applies to the combined total of all always-loaded rules.

## Path-Scoping

Add a `paths` frontmatter block to make a rule file load only when Claude reads files matching the specified patterns:

```markdown
---
paths:
  - "src/api/**/*.ts"
---
# API Endpoint Rules
- All endpoints must validate input with Zod schemas
- Use the asyncHandler wrapper for all route handlers
```

Path-scoped rules are loaded on demand, not every session. This keeps context clean -- Claude only sees API rules when working on API files.

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

See `templates/advanced/.claude/rules/api-endpoints.md` for a complete path-scoped rule example.

## User-Level Rules

Place personal rule files in `~/.claude/rules/` to apply them across all your projects:

```text
~/.claude/rules/
  personal-style.md      # Your preferred coding conventions
  git-workflow.md        # Your commit message and branching preferences
```

User-level rules are loaded before project rules. When they conflict, **project rules take higher priority** -- the team's conventions override your personal preferences.

This is useful for preferences that are truly personal (editor-like settings, preferred comment style) rather than project-specific.

## Sharing Rules Across Projects

Use symlinks to share rule files between projects without duplicating them:

```bash
# Share an entire directory of rules
ln -s ~/shared-claude-rules .claude/rules/shared

# Share a single file
ln -s ~/company-standards/security.md .claude/rules/security.md
```

This pattern works well for organization-wide standards. Maintain a central repository of rule files and symlink them into each project. When the central rules update, every project picks up the changes automatically.

**Note:** Symlinked rules are resolved at read time. Make sure the symlink targets exist on every developer's machine, or use a setup script to create them.

## Further Reading

- [CLAUDE.md Guide](claude-md-guide.md) -- Writing effective CLAUDE.md files and the `@import` syntax
- [Settings Guide](settings-guide.md) -- Configuring permissions and other settings
- [Getting Started](getting-started.md) -- Full setup walkthrough including rules
