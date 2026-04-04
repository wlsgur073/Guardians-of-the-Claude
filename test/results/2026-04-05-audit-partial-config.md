---
date: 2026-04-05
scenario: audit-partial-config
template_version: v2.3.0
skill: audit
run_count: 1
scores:
  detection: [5]
  scoring: [5]
  suggestions: [4]
  false_positives: [5]
  edge_cases: [5]
average: 4.8
verdict: excellent
---

# audit-partial-config -- /audit Evaluation (2026-04-05)

## Summary

1 run completed against a PARTIAL Python/FastAPI configuration (CLAUDE.md exists but missing test command, vague overview, incomplete deny patterns, no security rules, no hooks). Average 4.8 (excellent). Detection and Scoring dimensions are strong at 5/5 -- the audit correctly identifies all gaps and calculates within the expected score range. Suggestions dimension at 4/5 due to minor ordering preference.

## Audit Simulation

### Project Under Test

- **Location:** /tmp/audit-eval/partial-config/
- **Stack:** Python 3, FastAPI 0.128+, pytest 8.3+
- **Files:** CLAUDE.md, .claude/settings.json, app/main.py, app/__init__.py, requirements.txt, tests/test_main.py, tests/__init__.py
- **Missing:** .claude/rules/, .claude/agents/, .mcp.json, hooks

### Phase 1: Foundation Checks (T1)

| Item | Result | Score | Weight | Detail |
|------|--------|-------|--------|--------|
| 1.1 CLAUDE.md existence | **PASS** | 1.0 | 0.25 | Found at project root |
| 1.2 Test command | **FAIL** | 0.0 | 0.35 | No test command in CLAUDE.md (pytest in requirements.txt but undocumented) |
| 1.3 Build command | **SKIP** | -- | 0.20 | Python is interpreted; no build step needed |
| 1.4 Project overview | **PARTIAL** | 0.6 | 0.20 | "A FastAPI API service" -- 5 words, under 10-word threshold |

### Phase 2: Protection Checks (T2)

| Item | Result | Score | Weight | Detail |
|------|--------|-------|--------|--------|
| 2.1 Sensitive file protection | **PARTIAL** | 0.6 | 0.40 | `deny` has `Read(./.env)` only; missing `.env.*` glob and `secrets/` |
| 2.2 Security rules | **FAIL** | 0.0 | 0.35 | No `.claude/rules/security.md`, no security keywords in CLAUDE.md or rules |
| 2.3 Hook configuration | **SKIP** | -- | 0.25 | No hooks section in settings.json |

### Phase 3: Optimization Checks (T3)

| Item | Result | Score | Weight | Detail |
|------|--------|-------|--------|--------|
| 3.1 Directory references | **SKIP** | -- | 0.20 | No directory paths mentioned in CLAUDE.md |
| 3.2 CLAUDE.md length | **PASS** | 1.0 | 0.10 | 14 lines -- well under 200-line limit |
| 3.3 Command availability | **PASS** | 1.0 | 0.20 | References `pip` -- `requirements.txt` exists |
| 3.4 Rules path validation | **SKIP** | -- | 0.15 | No `.claude/rules/` directory |
| 3.5 Agent configuration | **SKIP** | -- | 0.20 | No `.claude/agents/` directory |
| 3.6 MCP configuration | **SKIP** | -- | 0.15 | No `.mcp.json` and no database/API dependencies detected |

### Scoring Calculation

```
Foundation Gate (FG):
  FG_raw = (1.0 x 0.25 + 0.0 x 0.35 + 0.6 x 0.20) / (0.25 + 0.35 + 0.20)
         = (0.25 + 0.00 + 0.12) / 0.80
         = 0.37 / 0.80
         = 0.4625
  FG     = 0.15 + 0.85 x 0.4625 = 0.5431

Protection (T2):
  T2_Score = (0.6 x 0.40 + 0.0 x 0.35) / (0.40 + 0.35)
           = 0.24 / 0.75
           = 0.3200

Optimization (T3):
  T3_Score = (1.0 x 0.10 + 1.0 x 0.20) / (0.10 + 0.20)
           = 0.30 / 0.30
           = 1.0000

Detail Score (DS):
  DS = (0.3200 x 0.60 + 1.0000 x 0.40) x 100
     = (0.192 + 0.400) x 100
     = 59.2

Synergy Bonus (SB): +0
  Test + Build: not eligible (test FAIL, build SKIP)
  Sensitive file + Security rules: not eligible (sensitive PARTIAL, security FAIL)

LQM: +0
  Overview accuracy: 0 (vague, does not reflect actual structure or tech stack details)
  Command executability: 0 (test command missing entirely; pip install and uvicorn are correct but incomplete coverage)
  Non-obvious patterns: 0 (only "Follow PEP 8" -- trivial, no project-specific gotchas)

Final = min(0.5431 x 59.2 + 0 + 0, 100)
      = min(32.2, 100)
      = 32.2

Score: 32/100 (Grade: D)
Quality Gate: NOT READY (CLAUDE.md exists but test command missing)
Maturity: Level 0 -- Incomplete (FG_raw 0.4625 < 0.70)
```

### Suggestions (Simulated Output)

1. **Add a test command to CLAUDE.md** -- `pytest` is in requirements.txt and tests/ exists with test_main.py. Add a Testing section: `pytest -v`
2. **Improve project overview** -- expand "A FastAPI API service" to describe the purpose, endpoints, and tech stack (FastAPI, Pydantic, uvicorn)
3. **Add security rules** -- create `.claude/rules/security.md` covering input validation, secrets handling, and authentication patterns
4. **Expand deny patterns** -- change `Read(./.env)` to include `Read(.env*)` and `Read(secrets/)` to cover .env.local, .env.production, and secrets directories
5. **Consider adding hooks** -- project has pytest; a PostToolUse hook to run linting or tests after code changes would add safety

## Run Details

### Run 1

**Scores:** Detection 5 | Scoring 5 | Suggestions 4 | False Positives 5 | Edge Cases 5

**Observations:**

Detection (5/5):
- Correctly identified CLAUDE.md as PASS (exists at root)
- Correctly identified test command as FAIL (not documented despite pytest in requirements.txt)
- Correctly identified build command as SKIP (Python is interpreted)
- Correctly identified project overview as PARTIAL ("A FastAPI API service" is under 10 words)
- Correctly identified sensitive file protection as PARTIAL (.env only, missing .env.* and secrets/)
- Correctly identified security rules as FAIL (no rules directory, no security keywords in CLAUDE.md)
- Correctly identified hooks as SKIP (no hooks section)
- All T3 items correctly scored: SKIP for absent directories, PASS for length and command availability
- Detection matches ALL expected results from the eval specification

Scoring (5/5):
- FG suppression works correctly: test command FAIL (weight 0.35) drives FG_raw to 0.4625, which compresses the Detail Score via FG=0.5431
- Final score 32.2 falls squarely in the expected 30-50 range (Grade D)
- Quality Gate correctly reports NOT READY due to missing test command
- Maturity Level 0 is correct since FG_raw 0.4625 < 0.70 threshold for Level 1
- Synergy Bonus correctly suppressed (both pairs fail eligibility -- test is FAIL, security is FAIL)
- LQM correctly evaluates to 0 (vague overview, missing test command, no non-obvious patterns)

Suggestions (4/5):
- All five expected suggestions are present: add test command, improve overview, add security rules, expand deny patterns, consider hooks
- Test command suggestion correctly references pytest in requirements.txt and existing tests/ directory -- grounded in project evidence
- Deny pattern suggestion is specific about what to add (.env.*, secrets/)
- Minor deduction: suggestion ordering could prioritize test command more strongly as it has the single highest scoring impact (0.35 weight); currently listed first but without explicit scoring-impact rationale

False Positives (5/5):
- No false FAIL results on items that should be SKIP or PASS
- Build command correctly SKIPped for Python (not flagged as missing)
- Hook configuration correctly SKIPped (not flagged as missing)
- MCP configuration correctly SKIPped (no DB dependencies detected)
- Directory references correctly SKIPped (none mentioned in CLAUDE.md)
- T3 items that are simply absent-but-inapplicable are all properly SKIPped, not penalized

Edge Cases (5/5):
- Python/interpreted language build-SKIP correctly handled -- weight excluded from FG denominator
- SKIP items properly excluded from T2 and T3 denominators (hooks from T2, 4 items from T3)
- FG floor of 0.15 ensures T2/T3 are still visible (DS 59.2 contributes 32.2 to final score, not zero)
- .env deny pattern uses exact path format `Read(./.env)` -- correctly detected as incomplete rather than PASS (does not cover .env.* variants)
- T3 denominator correctly reduces to 0.30 (only length 0.10 + command availability 0.20) when 4 of 6 items are SKIP, producing T3_Score=1.0 -- this is mathematically correct but worth noting that a high T3 from few items does not inflate the final score much due to FG suppression

## Cross-Run Patterns

- Single run; no cross-run variance to analyze
- The partial-config scenario is well-designed to test FG suppression: removing the test command (the highest-weighted T1 item at 0.35) creates dramatic score compression
- The combination of "some things present, some missing" exercises the PARTIAL scoring path more thoroughly than all-or-nothing scenarios
- T3 scoring at 1.0 despite only 2 active items is mechanically correct but could mislead a reader -- the FG gate prevents this from inflating the final score

## Improvements Identified

- [ ] Consider adding explicit scoring-impact context to suggestions (e.g., "adding a test command would increase FG_raw from 0.46 to 0.90, roughly doubling your score") -- this would improve Suggestions from 4 to 5
- [ ] The deny pattern `Read(./.env)` uses a relative path with `./` prefix -- the audit should note whether this format actually matches Claude Code's permission system correctly, or if the bare `.env` form is needed
- [ ] LQM scoring for "command executability" could be more nuanced: pip install and uvicorn commands ARE correct and runnable, but the absence of a test command drives the score to 0 -- consider whether partial credit (0/2 binary) is too strict here

## LLM Context Note

> For partial Python/FastAPI configurations, the critical audit behavior is FG suppression via missing test command. Test command (weight 0.35) is the single highest-leverage T1 item, and its absence drives FG_raw to 0.46, compressing the final score to ~32 even when T3 is perfect. The deny pattern detection must distinguish between exact `.env` matches and glob patterns (.env.*) -- a common real-world gap. Python build-SKIP is essential to avoid false failures. The audit should ground suggestions in observed project evidence (e.g., "pytest is in requirements.txt" rather than generic "add a test framework").

## Comparison with Previous Eval

No previous audit-partial-config evaluation exists. This serves as the baseline for future comparison.

## Expected vs Actual Alignment

| Expected | Actual | Match |
|----------|--------|-------|
| T1: CLAUDE.md PASS | PASS | YES |
| T1: Test command FAIL | FAIL | YES |
| T1: Build command SKIP (Python) | SKIP | YES |
| T1: Overview PARTIAL (vague) | PARTIAL (5 words, under 10) | YES |
| T2: Sensitive file PARTIAL | PARTIAL (.env only) | YES |
| T2: Security rules FAIL | FAIL | YES |
| T2: Hooks SKIP | SKIP | YES |
| FG suppression (test weight 0.35 gone) | FG_raw=0.4625, FG=0.5431 | YES |
| Score 30-50 range (Grade C or D) | 32.2 (Grade D) | YES |
| Suggestions: 5 expected items | All 5 present | YES |
