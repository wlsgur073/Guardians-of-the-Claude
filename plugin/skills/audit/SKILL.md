---
name: audit
description: "Validates your Claude Code configuration — checks essential settings, project alignment, and suggests improvements"
---

# Claude Code Configuration Audit

You are a Claude Code configuration auditor. Analyze the user's project and report on the health of their Claude Code setup.

Follow these phases in order. After all phases, present a summary.

## Phase 1: Essential Checks

These checks verify settings that directly impact Claude's effectiveness.

### 1.1 CLAUDE.md Existence

Check if `CLAUDE.md` exists at the project root or `.claude/CLAUDE.md`. If neither exists, report **FAIL** and stop — recommend running `/claude-code-template:generate` first.

### 1.2 Test Command

Search CLAUDE.md for a test command (e.g., `npm test`, `pytest`, `go test`, `cargo test`, `dotnet test`, `mvn test`). This is the single highest-leverage item in any CLAUDE.md.

- Found → **PASS**
- Not found → **FAIL** — "Add a test command so Claude can verify its work"

### 1.3 Build Command

Search CLAUDE.md for a build/compile command (e.g., `npm run build`, `tsc`, `go build`, `cargo build`, `mvn package`).

- Found → **PASS**
- Not found → **WARN** — "Add a build command for compile-time error checking"

### 1.4 Sensitive File Protection

Check if `.claude/settings.json` exists and has `deny` patterns covering sensitive files.

Check for these patterns:
- `.env` or `.env.*` in deny list
- `secrets/` or similar in deny list

Scoring:
- Both present → **PASS**
- settings.json exists but deny is incomplete → **WARN** — list what's missing
- No settings.json → **WARN** — "Create .claude/settings.json with deny patterns"

### 1.5 Project Overview

Check if CLAUDE.md has a project description in the first 20 lines (a heading followed by text explaining what the project is/does).

- Has description → **PASS**
- Empty or only commands → **WARN** — "Add a brief project overview so Claude understands context"

### 1.6 Security Rules

Check if the project has security-related configuration:

1. Check for `.claude/rules/security.md` or any rule file containing "security" in its filename
2. If no dedicated file, search CLAUDE.md and all rule files for security-related keywords (authentication, validation, secrets, sanitize, XSS, injection)

Scoring:
- Dedicated security rule file exists → **PASS**
- No dedicated file but security keywords found in CLAUDE.md or rules → **WARN** — "Consider extracting security rules into a dedicated `.claude/rules/security.md`"
- No security rules found anywhere → **WARN** — "No security rules detected. Consider adding rules for auth, input validation, and secrets handling"

## Phase 2: Alignment Checks

These checks verify that the configuration matches the actual project state.

### 2.1 Directory References

Extract directory paths mentioned in CLAUDE.md (e.g., `src/api/`, `tests/`, `db/migrations/`). For each, check if the directory actually exists in the project.

- All exist → **PASS**
- Some missing → **WARN** — list the directories mentioned but not found

### 2.2 CLAUDE.md Length

Count the lines in CLAUDE.md.

- Under 200 lines → **PASS**
- 200–300 lines → **WARN** — "Consider splitting into `.claude/rules/` files"
- Over 300 lines → **WARN** — "Strongly recommend splitting — long CLAUDE.md reduces effectiveness"

### 2.3 Command Availability

If CLAUDE.md references `npm` commands, check that `package.json` exists.
If it references `cargo` commands, check that `Cargo.toml` exists.
If it references `go` commands, check that `go.mod` exists.
If it references `python`/`pip` commands, check that `requirements.txt` or `pyproject.toml` exists.

- Manifest found → **PASS**
- Manifest missing → **WARN** — "CLAUDE.md references `{tool}` but `{manifest}` not found"

### 2.4 Rules Path Validation

If `.claude/rules/` directory exists, read each rule file. If a rule has a `paths:` field in its frontmatter, check that at least one matching file exists using Glob.

- All paths match → **PASS**
- No rules directory → **SKIP**
- Some paths have no matches → **WARN** — list the rules with unmatched paths

### 2.5 Agent Configuration Quality

If `.claude/agents/` directory exists with agent files:

1. Check that each agent has a `model:` field in its YAML frontmatter
2. Check that each agent has at least a Scope section defining its boundaries
3. Check if all agents use the same model (no diversity)

Scoring:
- All agents have model + scope, and model diversity present → **PASS**
- Some agents lack model or scope → **WARN** — list which agents need improvement
- All agents use the same model → **WARN** — "All agents use `[model]`. Consider `haiku` for exploration, `opus` for review tasks"
- No agents directory → **SKIP**

### 2.6 Hook Configuration Quality

If `.claude/settings.json` has a `hooks` section:

1. Check that every hook entry has a `statusMessage` field
2. Check that `PreToolUse` hooks use `exit 2` (not `exit 1`) for blocking — `exit 1` causes a generic error, `exit 2` provides Claude with the reason
3. Check for hooks with no `matcher` (runs on every tool use — usually unintentional)

Scoring:
- All hooks well-configured → **PASS**
- Missing `statusMessage` or incorrect exit codes → **WARN** — list specific issues
- No hooks section → **SKIP**

## Phase 3: Suggestions

Based on what you found in Phase 1 and 2, provide actionable improvement suggestions. Only suggest items that are relevant to this specific project.

### 3.1 Hooks

If `.claude/settings.json` has no `hooks` section and the project has a linter config (`.eslintrc*`, `pyproject.toml` with `[tool.ruff]`, etc.):
- Suggest a PostToolUse lint hook

### 3.2 Rules Splitting

If CLAUDE.md is over 150 lines and `.claude/rules/` does not exist:
- Suggest extracting code style, testing, and workflow sections into separate rule files

### 3.3 Agents

If the project has more than 3 distinct top-level source directories (e.g., `frontend/`, `backend/`, `infra/`):
- Suggest creating specialized agents for each area

### 3.4 Skills

If you notice repetitive patterns in the project structure (e.g., multiple similar route handlers, repeated component scaffolding):
- Suggest creating a skill to automate the pattern

### 3.5 Model Routing

If `.claude/agents/` exists and all agents use the same model:
- Suggest differentiating models: "Consider `haiku` for exploration agents, `sonnet` for implementation, `opus` for review. This optimizes cost and matches each agent's reasoning needs."

## Phase 4: Summary

Calculate the score using this weighted point system (100 points total):

**Essential Checks (70 points):**
- CLAUDE.md existence: 15 pts (PASS=15, FAIL=0)
- Test command: 15 pts (PASS=15, FAIL=0)
- Build command: 10 pts (PASS=10, WARN=5, FAIL=0)
- Sensitive file protection: 10 pts (PASS=10, WARN=5, FAIL=0)
- Project overview: 10 pts (PASS=10, WARN=5, FAIL=0)
- Security rules: 10 pts (PASS=10, WARN=5, FAIL=0)

**Alignment Checks (30 points):**
- Directory references: 6 pts (PASS=6, WARN=3, FAIL=0)
- CLAUDE.md length: 6 pts (PASS=6, WARN=3, FAIL=0)
- Command availability: 6 pts (PASS=6, WARN=3, FAIL=0)
- Rules path validation: 6 pts (PASS=6, WARN=3, FAIL=0)
- Agent configuration quality: 3 pts (PASS=3, WARN=1, FAIL=0)
- Hook configuration quality: 3 pts (PASS=3, WARN=1, FAIL=0)

**SKIP handling:** If a check is SKIP, remove its points from the denominator and scale proportionally to 100.

Present results as a summary table with emoji indicators (🟢 pass, 🟡 warn, ⚪ skip):

```
Configuration Audit Results
═══════════════════════════

Essential Checks (60/70)
  🟢 [PASS] CLAUDE.md found at project root
  🟢 [PASS] Test command found: npm test
  🟢 [PASS] Build command found: npm run build
  🟡 [WARN] Sensitive files: .env protected, but secrets/ not in deny list
  🟢 [PASS] Project overview present
  🟡 [WARN] Security keywords found in CLAUDE.md, but no dedicated security rule file

Alignment Checks (27/30)
  🟢 [PASS] All referenced directories exist
  🟢 [PASS] CLAUDE.md length: 87 lines
  🟢 [PASS] Command manifest found: package.json
  ⚪ [SKIP] No .claude/rules/ directory
  🟡 [WARN] Agent "backend-dev": all agents use sonnet — consider model diversity
  ⚪ [SKIP] No hooks configured

Suggestions
  • Add a PostToolUse hook for auto-linting: npx eslint --fix
  • Add secrets/ to deny patterns in .claude/settings.json
  • Extract security rules into .claude/rules/security.md
  • Consider haiku for exploration agents, opus for review

Score: 87/100
  Essential: 60/70  |  Alignment: 27/30

Next Steps
  → Run /claude-code-template:generate to add missing items interactively
  → Or ask Claude Code directly: "add a security rule for my project"
```

Adjust the table to reflect actual findings. Calculate the real score based on the point system above. Only show suggestions that apply to this project. Do not show Phase/Step labels — use the friendly format above.

**Next Steps section:** Always include this at the end if there are any WARN or FAIL results. If the score is 100/100, replace with: "Your configuration is in great shape. No changes needed."
