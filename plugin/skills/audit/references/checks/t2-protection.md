# T2 — Protection Checks

These checks verify that the project is safe from common mistakes. (60% of Detail Score weight)

## Weights

| Item | Weight | Rationale |
| ------ | -------- | ----------- |
| T2.1 Sensitive file protection | 0.35 | Prevents real damage (secrets exposure) |
| T2.2 Security rules | 0.30 | Defense-in-depth coverage |
| T2.3 Hook configuration quality | 0.20 | Operational correctness |
| T2.4 Autonomy risk policy | 0.15 | Permission posture for autonomous execution |

## T2.1 Sensitive File Protection

Check if `.claude/settings.json` exists and has `deny` patterns covering sensitive files.

**If settings.json exists but cannot be parsed as valid JSON** (e.g., syntax errors, trailing commas), treat deny patterns as unverifiable → **FAIL** — "settings.json contains invalid JSON — fix syntax errors so deny patterns can be verified." Note the specific parse error in suggestions.

Check for these patterns:
- `.env` or `.env.*` in deny list
- `secrets/` or similar in deny list

Additionally, check for **operation coverage gaps** in deny patterns:
- If deny patterns use operation-specific syntax (e.g., `Read(file_path=**/*.pem)`), verify that all three operation types (Read, Edit, Write) are covered for each sensitive file pattern
- Common sensitive file extensions to check beyond `.env`: `*.pem`, `*.key`, `*.p12`, `*.pfx`, `*.cert`, `*.jks`
- If a sensitive file type is covered by deny for some operations but relies on hooks for others, note this as weaker protection — hook failures (see T2.3 check 4-5) would leave those operations unprotected

Scoring:
- Core patterns present (`.env`, `secrets/`) AND no operation coverage gaps → **PASS**
- Core patterns present but operation coverage gaps on extended file types (e.g., `*.pem` only has Read deny) → **PARTIAL** — list which file types and operations lack deny coverage
- settings.json exists but deny is incomplete (missing `.env` or `secrets/`) → **PARTIAL** — list what's missing
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
4. **Portability check:** Flag known non-portable patterns in hook commands that silently fail on some platforms:
   - `grep -P` or `grep -oP` → PCRE not available on macOS/Windows Git Bash; use `grep -E` (extended regex) or `sed` instead
   - `readlink -f` → not supported on macOS; use `realpath` or `cd "$(dirname "$0")" && pwd` instead
   - `sed -i ''` vs `sed -i` → BSD sed (macOS) requires empty string arg, GNU sed does not; use `sed -i.bak` with cleanup or a temp file instead
   - `date -d` → GNU-only flag for date parsing; macOS uses `date -j -f`; avoid date arithmetic in hooks or use portable alternatives
   - `xargs -r` → `--no-run-if-empty` not available on macOS/BSD; use `xargs` with an `if` guard instead
5. **Silent failure detection:** Flag patterns where command errors are suppressed in a way that masks complete hook failure:
   - Variable assignment with `2>/dev/null` (e.g., `VAR=$(cmd 2>/dev/null)`) — if `cmd` fails, `VAR` is empty and subsequent conditions silently never trigger
   - Piped commands where intermediate failures are hidden (e.g., `cmd1 | cmd2` without `set -o pipefail`)
6. **Event type appropriateness:** Check if safety-critical operations use the correct hook event type:
   - If CLAUDE.md contains safety rules with strong language ("never", "must not", "forbidden", "do not", "금지") AND corresponding hooks exist as `PostToolUse` → flag as inappropriate — PostToolUse only warns after the action is already complete; safety-critical operations should use `PreToolUse` with `exit 2` to prevent the action
   - If `PostToolUse` hooks contain blocking-intent keywords in their command or statusMessage (e.g., "BLOCK", "PREVENT", "FORBID", "DANGER") → flag as contradictory — the hook intends to prevent but can only react

Scoring:
- All hooks well-configured, no portability issues → **PASS**
- Minor issues (missing statusMessage on some hooks) → **PARTIAL**
- Portability issues found (non-portable commands in hook) → **PARTIAL** — list specific patterns with portable alternatives
- Safety-critical operations using PostToolUse instead of PreToolUse → **PARTIAL** — "Consider moving safety-critical hook to PreToolUse with exit 2 for prevention instead of post-hoc warning"
- Serious issues (wrong exit codes, no matchers, silent failure patterns masking protection logic) → **MINIMAL** — list specific issues
- No hooks section → **SKIP**

### Conditional Suggestion

If no hooks configured and project has a linter config (`.eslintrc.*`, `eslint.config.*`, `.prettierrc`, `ruff.toml`, etc.) → suggest: "Consider adding a PostToolUse lint hook to catch formatting issues early."

## T2.4 Autonomy Risk Policy

Verifies the project's Claude Code permission policy is consistent with the autonomy-infrastructure framing in Anthropic's Auto Mode and Managed Agents engineering articles. Detects 5 sub-checks across `.claude/settings.json` (project + local) and `.mcp.json` (project-scope only — user-scope `~/.claude.json` is per-user and out of audit scope).

**Read sources** (in order, first match wins per file):
1. `.claude/settings.json` (project-shared, version-controlled)
2. `.claude/settings.local.json` (project-local, gitignored)
3. `.mcp.json` (project-scope)

Each violation records: `(sub-check ID, evidence path:line, catalog incident ID list)`.

### Sub-check 4a — Wildcard allow

Detect entries in `permissions.allow[]` matching any of:
- `Bash(*)`
- `Bash(python*)`, `Bash(node*)`, `Bash(ruby*)`, `Bash(perl*)`, `Bash(deno*)`, `Bash(bun*)` (and other wildcarded interpreters)
- `Bash(npm run *)`, `Bash(pnpm run *)`, `Bash(yarn run *)` (package manager run commands)
- `Agent(*)` or `Agent(<any-name>*)` patterns
- `PowerShell(*)` (when PowerShell tool enabled)

These rules grant arbitrary code execution. Note that auto mode automatically drops these rules at runtime per docs `/en/permission-modes`; the audit fires regardless because users frequently operate in default/acceptEdits modes where these allows are live.

**Citations:** `scope-escalation`, `safety-bypass`.

### Sub-check 4b — bypassPermissions misuse

Detect when `permissions.defaultMode == "bypassPermissions"` AND `.claude/settings.json` is the source (project-shared, version-controlled), AND CLAUDE.md does NOT contain any of: "disposable", "VM only", "VM-only", "container only", "container-only", "isolated environment", "sandbox only".

Local-scope `settings.local.json` is exempt — local sessions are user-chosen risk.

**Citations:** `safety-bypass`.

### Sub-check 4c — autoMode environment (advisory only)

When `permissions.defaultMode == "auto"` AND `autoMode.environment` is not defined: emit advisory in suggestions section only, **DO NOT** score against T2.4. Rationale: per Claude Code docs `/en/permission-modes`, omitting `autoMode.environment` yields the strictest default trust boundary (working directory + repo remotes only). Penalizing the strict default is incorrect.

Advisory wording: "auto mode is active without a custom `autoMode.environment`. This is the strict default. If routine actions are blocked frequently, see https://code.claude.com/docs/en/auto-mode-config for extending trusted infrastructure."

**Citations:** `data-exfiltration`, `credential-exploration` (advisory context only).

### Sub-check 4d — MCP credential exposure

Read `.mcp.json` at project root. For each `mcpServers[*].env` entry, classify:

- **4d-i (MINIMAL):** Value is a literal secret-looking string OR a defaulted secret `${VAR:-actual-secret-value}` where the default contains a token pattern (`sk-`, `ghp_`, `xox[bp]-`, base64 string ≥40 chars, or any string ≥20 chars with mixed case + digits).
- **4d-ii (PARTIAL):** Value is a `${VAR}` placeholder (no default) in a project-scope `.mcp.json` AND CLAUDE.md does not contain a phrase pointing to user-scope migration or vault pattern (search for: "user-scope", "~/.claude.json", "vault", "OAuth", "credential rotation").
- **SKIP:** `.mcp.json` absent, or all `env` entries are placeholders AND a migration note exists.

User-scope `~/.claude.json` is out of audit scope — that file is per-user and not in the audited project tree.

**Citations:** `credential-exploration`.

### Sub-check 4e — Scoped destructive Bash allow

Detect entries in `permissions.allow[]` matching any of (regex against entry string after `Bash(` prefix and before `:*)` or `)` suffix):

- `git push -f`, `git push --force`, `git push --force-with-lease`
- `git push --delete`, `git branch -D`
- `rm -rf`, `rm -f`
- `curl * | bash`, `curl * | sh`, `wget * | bash`, `wget * | sh`
- `gh api * --method DELETE`, `gh api * -X DELETE`
- Production deploy verbs: `aws deploy *`, `kubectl delete *`, `helm uninstall *` (project-detected)

These are narrower than 4a wildcards but match the verbs the auto-mode classifier blocks by default. Survival in default mode allow is the threat.

**Citations:** `scope-escalation`, `data-exfiltration`, `safety-bypass`.

### Scoring

Aggregate sub-checks 4a, 4b, 4d, 4e (4c is advisory only and contributes nothing to score):

- **PASS:** zero violations across 4a/4b/4d/4e.
- **PARTIAL:** at least one 4a OR 4d-ii OR 4e violation, AND zero 4b OR 4d-i violations.
- **MINIMAL:** at least one 4b OR 4d-i violation.
- **SKIP:** `.claude/settings.json` absent (T2.1 already fails) OR (`.claude/settings.json` exists with no `permissions` key AND `.mcp.json` absent).

**Severity precedence**: when multiple sub-checks fire simultaneously, the highest-tier severity wins. MINIMAL overrides PARTIAL — e.g., 4a (PARTIAL-tier) + 4d-i (MINIMAL-tier) at once resolves to MINIMAL.

### Evidence format

Each finding renders in qa-report Section 2 evidence column and `/audit` Detailed Findings as:

```
T2.4 <severity> — <sub-check>: <evidence path:line>.
Threat: <catalog ID(s)>. See security-patterns.md#<primary catalog ID>.
```

Example:

```
T2.4 PARTIAL — 4a: .claude/settings.json:14 contains Bash(*).
Threat: scope-escalation, safety-bypass. See security-patterns.md#scope-escalation.
```

### Conditional Suggestion

If T2.4 fires PARTIAL or MINIMAL: suggest running `/guardians-of-the-claude:secure` — its Autonomy Tightening step fixes 4a/4e automatically and provides actionable suggestions for 4b/4d (which require manual handling due to mutation safety).
