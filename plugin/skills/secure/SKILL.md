---
name: secure
description: "Strengthens your project's security — adds deny patterns, security rules, and file protection hooks"
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

If all items are already configured:
> "Your security configuration looks solid. No changes needed. Run `/guardians-of-the-claude:audit` for a full evaluation."

Then skip to **Write History** (Phase 4.2) to record the result (Fixed: none, Declined: none).

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

  **A1 merge rule amendments** (applied summary; mechanism in `plugin/references/lib/merge_rules.md`):
  - **Row 1 — `claude_code_configuration_state.model`**: any-skill writer; last-write-wins; written at Step 0.5 and Final Phase. Stateless mode: no-op (Phase 1 Global Invariant #6).
  - **Row 3 — `config-changelog.md` entry `- Model:` bullet**: `/secure` delta-emits per the shared hybrid writer policy. See `plugin/references/learning-system.md § Model Bullet Emission` for full mechanics; this skill emits only when the resolved model differs from the immediately previous entry's bullet value.

After completing Common Final Phase, run **Critical Thinking & Insight Delivery**.

### 4.3 Summary & Handoff

Print a summary of changes made, then:

> "Security configuration has been improved. Run `/guardians-of-the-claude:audit` to verify with a full evaluation."
