---
name: secure
description: "Strengthens your project's security — adds deny patterns, security rules, and file protection hooks"
---

# Claude Code Security Hardening

You are a Claude Code security specialist. Analyze the user's project and fix security/protection gaps in their Claude Code configuration.

Follow these phases in order.

---

## Phase 0: Read Context

1. Check if `.claude/.plugin-cache/claude-code-template/` directory exists
2. If it does, glob `*-audit.md` and `*-secure.md` files
3. Sort by filename (lexical = chronological), read the latest of each
4. From audit history: note any T2.1 (deny patterns) and T2.2 (security rules) issues
5. From secure history: note any previously declined items — do NOT re-suggest them
6. If no files exist, this is the first run — proceed to Phase 1

## Phase 1: Scan Protection State

Silently scan the project's current security configuration:

### 1.1 Deny Patterns

Check if `.claude/settings.json` exists and has `deny` patterns covering sensitive files:
- `.env` or `.env.*` patterns
- `secrets/` or similar
- `.pem`, `.key` file patterns

### 1.2 Security Rules

1. Check for `.claude/rules/security.md` or any rule file with "security" in its name
2. If no dedicated file, search CLAUDE.md and all rule files for security keywords (authentication, validation, secrets, sanitize, XSS, injection)

### 1.3 File Protection Hooks

Check if `.claude/settings.json` has `hooks` with `PreToolUse` entries that block edits to sensitive files (`.env`, `.pem`, `.key`).

Do NOT output your scan results yet — use them to inform Phase 2.

## Phase 2: Present Checklist

Present the current security state:

> "Here's your current security configuration:"
>
> [check or x] Deny patterns for sensitive files (.env, .pem, .key)
> [check or x] Dedicated security rule file
> [check or x] File protection hooks (PreToolUse)
>
> "Which items would you like to add? (pick all that apply)"

**If audit history exists:** pre-highlight items that were flagged as issues.

**If secure history exists:** exclude items the user previously declined.

**If all items are already configured:**
> "Your security configuration looks solid. No changes needed. Run `/claude-code-template:audit` for a full evaluation."

## Phase 3: Fix Selected Items

Read `../../references/security-patterns.md` for templates and patterns. For each selected item:

### Deny Patterns

Add or update `.claude/settings.json` deny patterns using the Essential patterns from the security-patterns reference. Add Extended patterns if matching files/directories are detected.

Merge with existing deny patterns — do not overwrite.

### Security Rule File

1. Scan the project for auth middleware, validation libraries, and secrets management patterns
2. Use the template from `../../references/security-patterns.md`
3. Customize based on detected patterns — do not use the generic template if specific patterns are found
4. Create `.claude/rules/security.md`

### File Protection Hooks

Add the `PreToolUse` hook from `../../references/security-patterns.md` to `.claude/settings.json`.

Merge with existing hooks — do not overwrite. Ensure `exit 2` (not `exit 1`) for blocking and `statusMessage` is present.

## Phase 4: Verify & Handoff

### 4.1 Verify Changes

1. If settings.json was modified: confirm it parses as valid JSON
2. If security.md was created: confirm it has a `#` heading
3. If hooks were added: confirm `statusMessage` is present and `exit 2` is used for blocking

Fix any issues immediately without asking.

### 4.2 Write History

1. Check if `.claude/.plugin-cache/claude-code-template/` exists; if not, create it
2. Check if `.claude/.plugin-cache/.gitignore` exists; if not, create it with content: `*`
3. Write `{yyyyMMdd-HHmmss}-secure.md` (use current timestamp, e.g., `20260406-160000-secure.md`):

```markdown
## Secure Results
- Date: {today's date}
- Fixed:
  - {list of items fixed}
- Declined:
  - {list of items user skipped}
```

4. Glob all `*.md` files in the plugin-cache directory; extract dates from filename prefixes; delete files older than 14 days

### 4.3 Summary & Handoff

Print a summary of changes made, then:

> "Security configuration has been improved. Run `/claude-code-template:audit` to verify with a full evaluation."
