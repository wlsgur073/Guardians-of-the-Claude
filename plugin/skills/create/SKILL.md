---
name: create
description: "Guided Claude Code setup — creates CLAUDE.md, settings.json, rules, and optional hooks/agents/skills for any project"
---

# Claude Code Project Setup

You are a Claude Code configuration expert. Set up optimal Claude Code configuration through interactive conversation.

Follow these phases in order.

---

## Phase 0: Load Context & Learn

Read `../../references/learning-system.md` and follow the **Common Phase 0** steps
(including **Step 0.5 Migration & Stale Check**) with these create-specific overrides:

- **Step 2 override:** When filtering `local/recommendations.json`, focus on `issued_by in ["secure", "optimize"]` (to avoid overwriting changes those skills applied). This is declared in `learning-system.md` as a create-specific cross-skill override.

After completing Common Phase 0:
- From `/create`-issued recommendations in `recommendations.json`: note previously DECLINED features. Do NOT re-suggest declined features in Phase 2A Question 6 unless the user asks.

## Phase 0.5: Determine Path

**If `profile.json` was loaded in Phase 0:** The project type is already known. Use the profile's `project_structure` field to determine if this is an existing project. If the profile's `claude_code_configuration_state` indicates `claude_md` and `settings_json` are present, route directly to the Incremental path (Phase 2A-Incremental) without asking. Otherwise, skip to the "existing vs new" question below.

First, silently check if Claude Code configuration already exists:

1. Check for `CLAUDE.md` (root or `.claude/CLAUDE.md`)
2. Check for `.claude/settings.json`
3. Check for `.claude/rules/` directory

**If both CLAUDE.md and settings.json exist** → ask:

> "I see you already have Claude Code configuration set up. What would you like to do?"
>
> (a) **Add missing features** — keep existing config, add what's missing (rules, hooks, agents, skills, security)
> (b) **Start fresh** — regenerate configuration from scratch (existing files will be merged, not overwritten)

If the user chooses (a), read `references/best-practices.md` then `templates/advanced.md` and follow the **Incremental path** (Phase 2A-Incremental).

If the user chooses (b), continue to the question below.

**If no existing config (or user chose "start fresh")** → ask:

> "Is this an existing project with code, or a new/empty project you're starting from scratch?"
>
> (a) **Existing project** — I already have code, dependencies, and/or a framework set up
> (b) **New/empty project** — I'm starting from scratch or have only basic scaffolding

---

## Route to Path

Based on the user's choice, read the generation rules and the appropriate path file (Phases 1–3 are defined in each path file):

If the user chooses (b) New/empty project:

1. Read `references/best-practices.md` — common generation rules
2. Read `templates/starter.md` — follow the Starter path instructions

If the user chooses (a) Existing project:

1. Read `references/best-practices.md` — common generation rules
2. Read `templates/advanced.md` — follow the Advanced path instructions (references `../references/security-patterns.md` for security configuration)

After completing all generation steps from the path file, return here for Phase 4.

---

## Phase 3.5: Quick Verify

After generating files, run a quick sanity check before wrapping up:

1. **CLAUDE.md** — confirm it has at least: Project Overview, Build & Run, Testing sections
2. **settings.json** — confirm it has valid `permissions` with both `allow` and `deny` arrays
3. **Rule files** (if created) — confirm each has YAML frontmatter with at least a `#` heading
4. **Agent files** (if created) — confirm each has `model:` in frontmatter and a Scope section
5. **Cross-references** — confirm any directories mentioned in CLAUDE.md actually exist in the project
6. **Command dependencies** — confirm every suggested command only references packages listed in the project's dependency manifest (e.g., if `pytest --cov` is suggested, verify `pytest-cov` is in requirements.txt; if `eslint` is suggested, verify it's in package.json)

If any check fails, fix it immediately before proceeding. Do not ask the user — just correct the issue and note it in the Phase 4 summary.

---

## Phase 4: Wrap Up

After generating all files:

1. Print a summary table listing every created/modified file and what it contains
2. If you merged into existing files, explain what was added
3. Tell the user: "Run `/memory` to verify all configuration files are loaded"
4. Suggest trying a simple task to test the configuration works

5. Suggest: "Run `/guardians-of-the-claude:audit` to evaluate your new configuration."

**If the user followed the Starter path**, also add:

> You're using a starter configuration. As your project grows and you want rule files, hooks, agents, or skills, run `/guardians-of-the-claude:create` again and choose "Existing project" to upgrade to the full configuration.

## Phase 4.5: Persist Results & Learn

Read `../../references/learning-system.md` and follow the **Common Final Phase** steps with these create-specific overrides:

- **Step 1 override (Skill-specific data in changelog entry):**
  The `config-changelog.md` entry for this skill must include:
  - `Detected:` — include the path taken (`starter`, `advanced`, or `incremental`) so future runs can reason about what scaffold the project started from.
  - `Applied:` — list of files created or modified this run (CLAUDE.md, settings.json, rules/*, agents/*, hooks, skills, MCP config).
  - `Recommendations:` — features the user explicitly skipped in Phase 2A Question 6 marked as `DECLINED by user`. This enables Learning Rule 2 (Preference Respect) in future runs.

  Each DECLINED entry written this run must increment `decline_count` per `plugin/references/lib/merge_rules.md §recommendations.json merge rules`: if the rec is a fresh DECLINE (no current entry, or current entry was PENDING), set `decline_count = 1`; if re-recording a DECLINE on an already-DECLINED rec, increment `decline_count++` (monotonic — never decremented even when a previously-DECLINED rec re-transitions to PENDING). Writes always emit schema 1.1.0; reading a 1.0.0 file performs lazy migration in-memory (inflate missing `decline_count` to 0) before the merge.

  Profile merge under the state-mutation lock: `/create` owns the project-structure sections (`runtime_and_language`, `framework_and_libraries`, `package_management`, `testing`, `build_and_dev`, `project_structure`) and `claude_code_configuration_state.claude_md`. It must update `claude_code_configuration_state.{rules_count, agents_count, hooks_count, mcp_servers_count}` for entity classes it added (see `plugin/references/lib/merge_rules.md` §profile.json merge rules). Sections owned exclusively by `/secure` (`settings_json`) must be preserved from the re-read `current_profile`.

  Sections owned exclusively by `/audit` (`monorepo_detection`) must be preserved. Per `plugin/references/lib/merge_rules.md §project_structure / monorepo_detection consistency precondition`:

  | `current_profile.monorepo_detection.detected` | `project_structure.type` rule for `/create` |
  |---|---|
  | `true` | preserve `"monorepo"` |
  | `false` | preserve existing value if present; when writing `project_structure.type`, write `"single_project"` only (must NOT write `"monorepo"` or `null`) |
  | `null` (or `monorepo_detection == null`) | may write `"single_project"` or `null` (must NOT write `"monorepo"`) |

  Never write `monorepo_detection` itself — `/audit` is exclusive owner.

  **A1 merge rule amendments** (applied summary; mechanism in `plugin/references/lib/merge_rules.md`):
  - **Row 1 — `claude_code_configuration_state.model`**: any-skill writer; last-write-wins; written at Step 0.5 and Final Phase. Stateless mode: no-op (Phase 1 Global Invariant #6).
  - **Row 3 — `config-changelog.md` entry `- Model:` bullet**: `/create` delta-emits per the shared hybrid writer policy. See `plugin/references/learning-system.md § Model Bullet Emission` for full mechanics; this skill emits only when the resolved model differs from the immediately previous entry's bullet value.

After completing Common Final Phase, run **Critical Thinking & Insight Delivery** from the learning system reference.
