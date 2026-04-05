---
name: audit
description: "Validates your Claude Code configuration — checks essential settings, project alignment, and suggests improvements"
---

# Claude Code Configuration Audit

You are a Claude Code configuration auditor. Analyze the user's project and report on the health of their Claude Code setup.

Follow these phases in order. After all phases, present a summary.

## Phase 0: Check Previous Audit

Before starting checks, look for previous audit results in memory:

1. Read the user's MEMORY.md index — look for an `audit-history` entry
2. If found, read the audit-history memory file and note the previous score, date, and top issues
3. Keep previous results in mind — you will compare them in Phase 4

If no previous audit exists, skip this and proceed to Phase 1.

## Phase 1: Foundation Checks (T1)

These checks form the **Foundation Gate** — they determine what percentage of the Detail Score (Protection + Optimization) applies to the final score. A missing foundation item suppresses the entire score.

### 1.1 CLAUDE.md Existence

Check if `CLAUDE.md` exists at the project root or `.claude/CLAUDE.md`.

- Found → **PASS**
- Neither exists → **FAIL** — stop and recommend running `/claude-code-template:generate` first. Do NOT proceed to T1.2 or any subsequent phase. Use the Early Halt output format (see scoring-model.md)

### 1.2 Test Command

Search CLAUDE.md for a test command (e.g., `npm test`, `pytest`, `go test`, `cargo test`, `dotnet test`, `mvn test`). This is the single highest-leverage item in any CLAUDE.md.

- Found and runnable → **PASS**
- Found but command may not work (e.g., references a tool not in dependencies) → **PARTIAL**
- Not found → **FAIL** — "Add a test command so Claude can verify its work"
- No application code in the project (documentation-only, template, or config-only repositories) → **SKIP**

### 1.3 Build Command

Search CLAUDE.md for a build/compile command (e.g., `npm run build`, `tsc`, `go build`, `cargo build`, `mvn package`).

- Found and runnable → **PASS**
- Found but manifest or tool not available (e.g., references `cargo build` but no `Cargo.toml`) → **PARTIAL**
- Interpreted language with no build step needed (Python, Ruby) → **SKIP**
- No application code in the project (documentation-only, template, or config-only repositories) → **SKIP**
- Not found for a compiled language → **FAIL** — "Add a build command for compile-time error checking"

### 1.4 Project Overview

Check if CLAUDE.md has a project description in the first 20 lines (a heading followed by text explaining what the project is/does).

- Clear description with language/framework mentioned → **PASS**
- Heading exists with some descriptive text but vague or too brief (under 10 words) → **PARTIAL**
- Heading exists but no descriptive text follows (title only), or only commands with no context → **FAIL** — "Add a brief project overview so Claude understands context"

## Phase 2: Protection Checks (T2)

These checks verify that the project is safe from common mistakes. (60% of Detail Score weight)

### 2.1 Sensitive File Protection

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

### 2.2 Security Rules

Check if the project has security-related configuration:

1. Check for `.claude/rules/security.md` or any rule file containing "security" in its filename
2. If no dedicated file, search CLAUDE.md and all rule files for security-related keywords (authentication, validation, secrets, sanitize, XSS, injection)

Scoring:
- Dedicated security rule file exists → **PASS**
- No dedicated file but security keywords found in CLAUDE.md or rules → **PARTIAL** — "Consider extracting security rules into a dedicated `.claude/rules/security.md`"
- No security rules found anywhere, but project has security-relevant surface (web framework, API endpoints, authentication, database access, secrets handling) → **FAIL** — "No security rules detected. Consider adding rules for auth, input validation, and secrets handling"
- No security rules found and project has no security-relevant surface (pure CLI tool, library crate, utility script, documentation-only — no web framework, no auth, no API, no database) → **SKIP**

### 2.3 Hook Configuration Quality

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

## Phase 3: Optimization Checks (T3)

These checks verify that the configuration is well-organized and maintainable. (40% of Detail Score weight)

### 3.1 Directory References

Extract directory paths mentioned in CLAUDE.md (e.g., `src/api/`, `tests/`, `db/migrations/`). For each, check if the directory actually exists in the project.

- No directory paths mentioned in CLAUDE.md → **SKIP**
- All mentioned directories exist → **PASS**
- Most exist, 1-2 missing → **PARTIAL**
- Many missing → **FAIL** — list the directories mentioned but not found

### 3.2 CLAUDE.md Length

Count the lines in CLAUDE.md.

- Under 200 lines → **PASS**
- 200–300 lines → **PARTIAL** — "Consider splitting into `.claude/rules/` files"
- Over 300 lines → **MINIMAL** — "Strongly recommend splitting — long CLAUDE.md reduces effectiveness"

### 3.3 Command Availability

If CLAUDE.md references `npm` commands, check that `package.json` exists.
If it references `cargo` commands, check that `Cargo.toml` exists.
If it references `go` commands, check that `go.mod` exists.
If it references `python`/`pip` commands, check that `requirements.txt` or `pyproject.toml` exists.

- No tool-specific commands referenced in CLAUDE.md → **SKIP**
- All referenced tool manifests found → **PASS**
- Multiple tools referenced, some manifests found, others missing → **PARTIAL** — list the missing ones
- Single tool referenced and its manifest missing, or all referenced manifests missing → **FAIL** — "CLAUDE.md references `{tool}` but `{manifest}` not found"

### 3.4 Rules Path Validation

If `.claude/rules/` directory exists, read each rule file. If a rule has a `paths:` field in its frontmatter, check that at least one matching file exists using Glob.

- All paths match → **PASS**
- No rules directory → **SKIP**
- Some paths have no matches → **PARTIAL** — list the rules with unmatched paths

### 3.5 Agent Configuration Quality

If `.claude/agents/` directory exists with agent files:

1. Check that each agent has a `model:` field in its YAML frontmatter
2. Check that each agent has at least a Scope section defining its boundaries
3. Check if all agents use the same model (no diversity)

Scoring:
- All agents have model + scope, and model diversity present → **PASS**
- Some agents lack model or scope → **PARTIAL** — list which agents need improvement
- All agents use the same model → **PARTIAL** — "All agents use `[model]`. Consider `haiku` for exploration, `opus` for review tasks"
- No agents directory → **SKIP**

### 3.6 MCP Configuration

Check if `.mcp.json` exists at the project root.

If the project uses databases (check for `pg`, `prisma`, `knex`, `sequelize`, `mongoose` in dependencies) or external APIs:
- `.mcp.json` exists with relevant servers → **PASS**
- `.mcp.json` exists but doesn't cover detected tools → **PARTIAL**
- No `.mcp.json` but database/API dependencies detected → **MINIMAL** — "Consider adding a `.mcp.json` with a matching MCP server"
- No `.mcp.json` and no database/API dependencies → **SKIP**

## Phase 3.5: Suggestions

Based on what you found in Phase 1–3, provide actionable improvement suggestions. Only suggest items that are relevant to this specific project.

**Hooks:** If no hooks and project has a linter config → suggest PostToolUse lint hook.

**Rules Splitting:** If CLAUDE.md is over 150 lines and no `.claude/rules/` → suggest extracting.

**Agents:** If more than 3 distinct top-level source directories → suggest specialized agents.

**Skills:** If repetitive patterns in project structure → suggest creating a skill.

**Model Routing:** If all agents use the same model → suggest differentiating.

## Phase 4: Summary

Read `references/scoring-model.md` for the complete scoring formula, then calculate and present results.

Apply the scoring model in this order:

1. **Score each item** using the 4-level scale (PASS=1.0, PARTIAL=0.6, MINIMAL=0.3, FAIL=0.0, SKIP=excluded)
2. **Calculate Foundation Gate** — `FG_raw = weighted average of non-SKIP T1 items`, `FG = 0.15 + 0.85 × FG_raw`
3. **Calculate Detail Score** — `DS = (T2_weighted × 0.60 + T3_weighted × 0.40) × 100`
4. **Calculate Synergy Bonus** — check qualifying pairs (test + build, sensitive file protection + security rules)
5. **Evaluate LQM** — answer 3 constrained judgment questions about CLAUDE.md content quality (see scoring model)
6. **Calculate Final** — `min(FG × DS + SB + LQM, 100)`
7. **Check Quality Gate** — CLAUDE.md exists AND test command present; test condition waived if SKIP (display label only)
8. **Determine Grade** (A/B/C/D/F) and **Maturity Level** (0–3)

Present results using the output format defined in the scoring model reference. Do not show Phase/Step labels — use the friendly format.

**If previous audit results exist (from Phase 0):** Add a comparison line at the end:
> "Since your last audit (DATE): score changed from X → Y. Resolved: [issues]. Still open: [issues]."

**Next Steps section:** Always include this at the end if there are any non-PASS results. If the score is 100/100, replace with: "Your configuration is in great shape. No changes needed."

## Phase 5: Save Audit Results

After presenting the summary, save results to memory:

1. Read MEMORY.md — check if `audit-history` entry exists
2. Write (or update) the audit-history memory file:

```markdown
---
name: audit-history
description: Previous /audit results for tracking configuration health over time
type: project
---

## Latest (YYYY-MM-DD)
Model: v2 (foundation-gated)
Score: XX/100 (Grade: X)
Gate: READY/NOT READY
Maturity: Level N — Name
Top issues: [2-3 bullet summary of non-PASS items]

## Previous (YYYY-MM-DD)
Score: XX/100 (Grade: X)
Top issues: [2-3 bullet summary]
```

- If an existing "Latest" entry exists, move it to "Previous" (keep only 2 snapshots)
- Write new "Latest" with today's results
3. Update MEMORY.md index if the `audit-history` entry doesn't exist yet:
   - Add: `- [Audit history](audit-history.md) — Latest /audit score and top issues`
