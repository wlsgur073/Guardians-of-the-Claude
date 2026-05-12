---
name: secure
description: "Strengthens your project's security — adds deny patterns, security rules, and file protection hooks. Use when the user asks to add security or fix security gaps in their Claude Code configuration."
---

# Claude Code Security Hardening

You are a Claude Code security specialist. Analyze the user's project and fix security/protection gaps in their Claude Code configuration.

Follow these phases in order.

---

## Phase 0: Load Context & Learn

Read `../../references/learning-system.md` and follow the **Common Phase 0** steps (including **Step 0.5 Migration & Stale Check**) with these secure-specific overrides:

- **Step 2 override:** When filtering `local/recommendations.json` for `issued_by == "audit"`, focus on T2.1 (deny patterns) and T2.2 (security rules) recommendations flagged by the last audit.

After completing Common Phase 0:
- Separately scan `recommendations.json` for entries with `issued_by == "secure"` and `status == "DECLINED"` — these are previously declined `/secure` suggestions and must not be re-suggested unless project scale/structure changed significantly (per Learning Rule 2 Preference Respect).

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

### 1.4 Autonomy Risk Policy

Read `.claude/settings.json` (and `.claude/settings.local.json` if present) and `.mcp.json` (project-scope only). Apply the 5 sub-checks defined in `plugin/skills/audit/references/checks/t2-protection.md` §T2.4:

- 4a wildcard allow: `permissions.allow[]` entries matching `Bash(*)`, `Bash(python*)`, `Bash(node*)`, `Bash(npm run *)`, `Agent(*)`, `PowerShell(*)`
- 4b bypassPermissions: `defaultMode == "bypassPermissions"` in `.claude/settings.json` without CLAUDE.md isolation note
- 4d-i / 4d-ii: `.mcp.json` `mcpServers[*].env` with literal secret (4d-i) or placeholder without migration note (4d-ii)
- 4e scoped destructive Bash: allow entries matching `git push -f`, `rm -rf`, `curl|bash`, `gh api * DELETE`, etc.

Skip 4c (advisory-only in `/audit`; `/secure` does not surface it).

For each violation, record `(sub-check ID, evidence path:line, catalog incident ID)` — used by the Phase 2 checklist and the Phase 3.4 tightening logic.

### 1.5 Permission Mode

Read `.claude/settings.json` and record the value of `permissions.defaultMode` (or note its absence — Claude Code defaults to `default` mode when unset).

### 1.6 Sandbox State

Check whether `sandbox.enabled` is `true` in `.claude/settings.json` (project scope). Note that sandbox settings can also be set in user (`~/.claude/settings.json`), local (`.claude/settings.local.json`), or managed scopes — if absent in project scope, report "project setting absent" rather than "sandboxing is off" (the effective state may differ across scopes per Claude Code's [settings precedence](https://code.claude.com/docs/en/settings#settings-precedence)).

### 1.7 Auto Mode Trust Environment

Check whether `autoMode.environment` is configured in user (`~/.claude/settings.json`), local (`.claude/settings.local.json`), or managed scopes. The classifier ignores `autoMode` in shared project settings (`.claude/settings.json`).

Do NOT output your scan results yet — use them to inform Phase 2.

## Phase 2: Present Checklist

Present the current security state:

> "Here's your current security configuration:"
>
> [check or x] Deny patterns for sensitive files (.env, .pem, .key)
> [check or x] Dedicated security rule file
> [check or x] File protection hooks (PreToolUse)
> [check or x] Autonomy risk policy
>   - Wildcard allow: <N violations or "—">
>   - Destructive scoped allow: <N violations or "—">
>   - bypassPermissions without isolation note: <yes/no>
>   - .mcp.json credential exposure: <N violations or "—">
>
> "Which items would you like to add? (pick all that apply)"

**If audit history exists:** pre-highlight items that were flagged as issues.

**If secure history exists:** exclude items the user previously declined.

If all items are already configured:
> "Your security configuration looks solid. No changes needed. Run `/guardians-of-the-claude:audit` for a full evaluation."

Then skip to **Write History** (Phase 4.2) to record the result (Fixed: none, Declined: none).

### Permission and Safety State (informational)

After the checklist above (regardless of which items were selected), also report the current permission and safety state from Phase 1.5–1.7:

> Permission mode (`defaultMode`): `<value>` (or "not set — defaults to `default`")
> Sandboxing: enabled / disabled / not configured
> Auto Mode trust environment: configured / not configured

If any are not set and the user wants guidance, point to `docs/guides/settings-guide.md` § "Permission Modes and Safety (Advanced)" plus the canonical [permission modes](https://code.claude.com/docs/en/permission-modes), [auto mode configuration](https://code.claude.com/docs/en/auto-mode-config), and [sandboxing](https://code.claude.com/docs/en/sandboxing) documentation. These are decision points (plan tier, platform prerequisites, trust model) — `/secure` does not auto-configure them.

For decision principles when choosing among modes and whether to enable sandboxing, see `../../references/security-patterns.md` § "Permission and Safety Decision Principles".

## Phase 3: Fix Selected Items

Read `../../references/security-patterns.md` for templates and patterns. For each selected item:

### Deny Patterns

Add or update `.claude/settings.json` deny patterns using the Essential patterns from the security-patterns reference. Add Extended patterns if matching files/directories are detected.

Merge with existing deny patterns — do not overwrite.

### Security Rule File

1. Scan the project for auth middleware, validation libraries, and secrets management patterns
2. Use the template from `../../references/security-patterns.md`
3. Customize based on detected patterns — do not use the generic template if specific patterns are found
4. Create `.claude/rules/` directory if it doesn't exist
5. Create `.claude/rules/security.md`

### File Protection Hooks

Add the `PreToolUse` hook from `../../references/security-patterns.md` to `.claude/settings.json`.

Merge with existing hooks — do not overwrite. Ensure `exit 2` (not `exit 1`) for blocking and `statusMessage` is present.

### 3.4 Autonomy Tightening

For each user-confirmed sub-check from the scan (1.4), the fix strategy differs by mutation safety:

**Auto-mutate (4a wildcard allow, 4e scoped destructive allow)**:

1. Parse `.claude/settings.json` `permissions.allow[]`.
2. For each violating entry:
   - **4a wildcard**: replace with narrower allows OR move to `permissions.ask[]`.
     - `Bash(*)` → `ask:["Bash(*)"]`
     - `Bash(python*)` → if project has `pyproject.toml` or `setup.py`, narrow to `allow:["Bash(python -m pytest:*)", "Bash(python -m ruff:*)"]`; else `ask:["Bash(python*)"]`
     - `Bash(npm run *)` → if `package.json` `scripts` detected, narrow to per-script allows (e.g., `Bash(npm run test:*)`, `Bash(npm run lint:*)`); else `ask:["Bash(npm run *)"]`
     - `Agent(*)` → `ask:["Agent(*)"]`
   - **4e scoped destructive**: move entry from `allow:[]` to `ask:[]` unchanged.
3. Atomic write back. Preserve existing JSON indentation (read first character of any nested array for indent detection — default 2-space).
4. Print unified diff to user.

**Suggestion-only (4b bypassPermissions, 4d-i literal secret, 4d-ii placeholder)**:

Print a suggestion block. Do NOT mutate user files.

- **4b**: "`.claude/settings.json` sets `defaultMode: \"bypassPermissions\"` (line N) but CLAUDE.md has no disposable-environment note. Either remove the default mode from project-shared settings (recommended — move to `settings.local.json` so each user opts in) or add a note to CLAUDE.md explaining this is for a disposable VM/container. Threat: safety-bypass. See security-patterns.md#safety-bypass."
- **4d-i**: "`.mcp.json` line N contains what appears to be a literal credential in `<server>.env.<key>`. Do NOT remove it via this skill — that could expose the value in git history. Recommended manual steps: (1) rotate the credential, (2) move the MCP server config to `~/.claude.json` (user-scope), (3) re-add via `${ENV_VAR}` placeholder. Threat: credential-exploration. See security-patterns.md#credential-exploration."
- **4d-ii**: "`.mcp.json` line N uses `${VAR}` placeholder in project-scope. This is acceptable but undocumented. Recommended: add a CLAUDE.md note pointing to how teammates supply the env var (vault, dotenv pattern, OAuth flow). Threat: credential-exploration (low). See security-patterns.md#credential-exploration."

Always merge — never overwrite existing `allow:[]` / `ask:[]` / `deny:[]` entries unrelated to the violation being fixed.

## Phase 4: Verify & Handoff

### 4.1 Verify Changes

1. If settings.json was modified: confirm it parses as valid JSON
2. If security.md was created: confirm it has a `#` heading
3. If hooks were added: confirm `statusMessage` is present and `exit 2` is used for blocking

Fix any issues immediately without asking.

### 4.2 Persist Results & Learn

Read `../../references/learning-system.md` and follow the **Common Final Phase** steps with these secure-specific overrides:

- **Step 1 override (Skill-specific data in changelog entry):**
  The `config-changelog.md` entry for this skill must include:
  - `Applied:` — list of items fixed (deny patterns added, security rule file created, file protection hooks added).
  - `Recommendations:` — items the user skipped this run marked as `DECLINED by user`; any previously PENDING recommendation from `/audit` that was addressed this run marked as `RESOLVED`.

  For DECLINED items, increment `decline_count` per `plugin/references/lib/merge_rules.md §recommendations.json merge rules`: PENDING -> DECLINED sets `decline_count = 1`; DECLINED -> DECLINED re-record increments `decline_count++`. Monotonic — never decremented. Writes always emit schema 1.1.0; reading a 1.0.0 file performs lazy migration (inflate missing `decline_count` to 0). The repeated-decline trigger in `plugin/hooks/session-start.{sh,ps1}` reads this field after status==DECLINED filter and renders `"declined N times total"` for the rec with the highest `decline_count`.

  Profile merge under the state-mutation lock must update the `claude_code_configuration_state.settings_json` section (owned by `/secure`), plus `hooks_count` and `rules_count` if they changed (see `plugin/references/lib/merge_rules.md` §profile.json merge rules).

  Additionally, when 3.4 mutates `.claude/settings.json`, update `profile.json claude_code_configuration_state.settings_json.deny_patterns_count` if deny entries changed, and append a `Resolved:` entry for any `/audit` T2.4 PENDING recommendations now addressed.

  **A1 merge rule amendments** (applied summary; mechanism in `plugin/references/lib/merge_rules.md`):
  - **Row 1 — `claude_code_configuration_state.model`**: any-skill writer; last-write-wins; written at Step 0.5 and Final Phase. Stateless mode: no-op (Phase 1 Global Invariant #6).
  - **Row 3 — `config-changelog.md` entry `- Model:` bullet**: `/secure` delta-emits per the shared hybrid writer policy. See `plugin/references/learning-system.md § Model Bullet Emission` for full mechanics; this skill emits only when the resolved model differs from the immediately previous entry's bullet value.

After completing Common Final Phase, run **Critical Thinking & Insight Delivery**.

### 4.3 Summary & Handoff

Print a summary of changes made, then:

> "Security configuration has been improved. Run `/guardians-of-the-claude:audit` to verify with a full evaluation."
