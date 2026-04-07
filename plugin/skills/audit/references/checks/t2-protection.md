# T2 — Protection Checks

These checks verify that the project is safe from common mistakes. (60% of Detail Score weight)

## Weights

| Item | Weight | Rationale |
|------|--------|-----------|
| T2.1 Sensitive file protection | 0.40 | Prevents real damage (secrets exposure) |
| T2.2 Security rules | 0.35 | Defense-in-depth coverage |
| T2.3 Hook configuration quality | 0.25 | Operational correctness |

## T2.1 Sensitive File Protection

Check if `.claude/settings.json` exists and has `deny` patterns covering sensitive files.

**If settings.json exists but cannot be parsed as valid JSON** (e.g., syntax errors, trailing commas), treat deny patterns as unverifiable → **FAIL** — "settings.json contains invalid JSON — fix syntax errors so deny patterns can be verified." Note the specific parse error in suggestions.

Check for these patterns:
- `.env` or `.env.*` in deny list
- `secrets/` or similar in deny list

Scoring:
- Both present → **PASS**
- settings.json exists but deny is incomplete → **PARTIAL** — list what's missing
- settings.json exists but no deny patterns at all → **MINIMAL**
- No settings.json → **FAIL** — "Create .claude/settings.json with deny patterns"

## T2.2 Security Rules

Check if the project has security-related configuration:

1. Check for `.claude/rules/security.md` or any rule file containing "security" in its filename
2. If no dedicated file, search CLAUDE.md and all rule files for security-related keywords (authentication, validation, secrets, sanitize, XSS, injection)

Scoring:
- Dedicated security rule file exists → **PASS**
- No dedicated file but security keywords found in CLAUDE.md or rules → **PARTIAL** — "Consider extracting security rules into a dedicated `.claude/rules/security.md`"
- No security rules found anywhere, but project has security-relevant surface (web framework, API endpoints, authentication, database access, secrets handling) → **FAIL** — "No security rules detected. Consider adding rules for auth, input validation, and secrets handling"
- No security rules found and project has no security-relevant surface (pure CLI tool, library crate, utility script, documentation-only — no web framework, no auth, no API, no database) → **SKIP**

## T2.3 Hook Configuration Quality

If `.claude/settings.json` has a `hooks` section:

**If settings.json cannot be parsed as valid JSON**, the hooks section cannot be assessed → **SKIP** (the malformed JSON is already flagged in T2.1).

1. Check that every hook entry has a `statusMessage` field
2. Check that `PreToolUse` hooks use `exit 2` (not `exit 1`) for blocking — `exit 1` causes a generic error, `exit 2` provides Claude with the reason
3. Check for hooks with no `matcher` (runs on every tool use — usually unintentional)

Scoring:
- All hooks well-configured → **PASS**
- Minor issues (missing statusMessage on some hooks) → **PARTIAL**
- Serious issues (wrong exit codes, no matchers) → **MINIMAL** — list specific issues
- No hooks section → **SKIP**

### Conditional Suggestion

If no hooks configured and project has a linter config (`.eslintrc.*`, `eslint.config.*`, `.prettierrc`, `ruff.toml`, etc.) → suggest: "Consider adding a PostToolUse lint hook to catch formatting issues early."
