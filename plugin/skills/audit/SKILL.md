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

## Phase 4: Summary

Calculate the score using this weighted point system (100 points total):

**Essential Checks (60 points):**
- CLAUDE.md existence: 15 pts (PASS=15, FAIL=0)
- Test command: 15 pts (PASS=15, FAIL=0)
- Build command: 10 pts (PASS=10, WARN=5, FAIL=0)
- Sensitive file protection: 10 pts (PASS=10, WARN=5, FAIL=0)
- Project overview: 10 pts (PASS=10, WARN=5, FAIL=0)

**Alignment Checks (40 points):**
- Directory references: 10 pts (PASS=10, WARN=5, FAIL=0)
- CLAUDE.md length: 10 pts (PASS=10, WARN=5, FAIL=0)
- Command availability: 10 pts (PASS=10, WARN=5, FAIL=0)
- Rules path validation: 10 pts (PASS=10, WARN=5, FAIL=0)

**SKIP handling:** If a check is SKIP, remove its points from the denominator and scale proportionally to 100.

Present results as a summary table with emoji indicators:

```
Configuration Audit Results
═══════════════════════════

Essential Checks (45/60)
  🟢 [PASS] CLAUDE.md found at project root
  🟢 [PASS] Test command found: npm test
  🟢 [PASS] Build command found: npm run build
  🟡 [WARN] Sensitive files: .env protected, but secrets/ not in deny list
  🟢 [PASS] Project overview present

Alignment Checks (30/40)
  🟢 [PASS] All referenced directories exist
  🟢 [PASS] CLAUDE.md length: 87 lines
  🟢 [PASS] Command manifest found: package.json
  ⚪ [SKIP] No .claude/rules/ directory

Suggestions
  • Add a PostToolUse hook for auto-linting: npx eslint --fix
  • Add secrets/ to deny patterns in .claude/settings.json

Score: 83/100
  Essential: 45/60  |  Alignment: 30/40
```

Adjust the table to reflect actual findings. Calculate the real score based on the point system above. Only show suggestions that apply to this project. Do not show Phase/Step labels — use the friendly format above.
