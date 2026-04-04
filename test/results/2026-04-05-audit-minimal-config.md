---
date: 2026-04-05
scenario: audit-minimal-config
template_version: v2.3.0
skill: audit
run_count: 1
scores:
  detection: [5]
  scoring: [4]
  suggestions: [5]
  false_positives: [5]
  edge_cases: [4]
average: 4.6
verdict: excellent
---

# audit-minimal-config -- /audit Evaluation (2026-04-05)

## Summary

1 run completed against a Python/FastAPI project with bare-minimum configuration (CLAUDE.md containing only a single-line heading, no `.claude/` directory, no settings.json, no rules, no hooks). Average 4.6 (excellent). Detection and Suggestions scored maximum marks; Scoring and Edge Cases lost a point each due to a borderline ambiguity in the T1.4 Project Overview classification and the large number of SKIP items collapsing T3 to a single data point.

## Simulated Audit Output

### Project Scanned

```
/tmp/audit-eval/minimal-config/
  CLAUDE.md               (1 line: "# My FastAPI Project")
  app/__init__.py          (empty)
  app/main.py              (FastAPI health endpoint)
  tests/__init__.py        (empty)
  tests/test_main.py       (pytest test for /health)
  requirements.txt         (fastapi, uvicorn, pydantic, pytest, httpx)
```

No `.claude/` directory, no `settings.json`, no `.claude/rules/`, no `.claude/agents/`, no `.mcp.json`.

### Phase 1: Foundation Checks (T1)

| Item | Result | Detail |
|------|--------|--------|
| 1.1 CLAUDE.md existence | **PASS** | Found at project root |
| 1.2 Test command | **FAIL** | CLAUDE.md contains no test command (e.g., `pytest`). Project has `tests/test_main.py` and `pytest` in requirements.txt -- a test command is clearly applicable |
| 1.3 Build command | **SKIP** | Python is interpreted -- no build step needed |
| 1.4 Project overview | **PARTIAL** | Heading "# My FastAPI Project" names the framework but provides zero descriptive text about what the project does, its structure, or its purpose |

### Phase 2: Protection Checks (T2)

| Item | Result | Detail |
|------|--------|--------|
| 2.1 Sensitive file protection | **FAIL** | No `.claude/settings.json` exists -- no deny patterns for `.env`, secrets, or credentials |
| 2.2 Security rules | **FAIL** | No `.claude/rules/` directory. No security keywords in CLAUDE.md (no mention of authentication, validation, secrets, sanitize, XSS, or injection) |
| 2.3 Hook configuration quality | **SKIP** | No `settings.json` -- no hooks section to evaluate |

### Phase 3: Optimization Checks (T3)

| Item | Result | Detail |
|------|--------|--------|
| 3.1 Directory references | **SKIP** | CLAUDE.md contains no directory path references |
| 3.2 CLAUDE.md length | **PASS** | 1 line -- well under 200-line limit |
| 3.3 Command availability | **SKIP** | CLAUDE.md references no tool-specific commands |
| 3.4 Rules path validation | **SKIP** | No `.claude/rules/` directory |
| 3.5 Agent configuration quality | **SKIP** | No `.claude/agents/` directory |
| 3.6 MCP configuration | **SKIP** | No database/API dependencies detected (fastapi, uvicorn, pydantic, pytest, httpx are not DB/external-API clients) |

### Phase 3.5: Suggestions

1. **Add test command to CLAUDE.md** -- This project has `pytest` in requirements.txt and `tests/test_main.py`. Add: `Run tests: pytest` to CLAUDE.md. This is the single highest-leverage improvement.
2. **Add project overview** -- Expand CLAUDE.md with 2-3 sentences describing what the project does, its tech stack (Python/FastAPI), and directory structure (`app/` for source, `tests/` for tests).
3. **Create `.claude/settings.json` with deny patterns** -- Add deny list for `.env`, `.env.*`, `secrets/`, and credential files to prevent accidental exposure.
4. **Add security rules** -- Create `.claude/rules/security.md` with guidelines for input validation, authentication patterns, and secrets handling appropriate for a FastAPI project.
5. **Consider adding hooks** -- A `PreToolUse` hook could enforce linting (if a linter is added) or block writes to sensitive paths.

### Phase 4: Score Calculation

```
Configuration Audit Results
===========================

Quality Gate: NOT READY    (CLAUDE.md OK, test command MISSING)

Foundation Gate (FG):  0.54    ==========.......... 46% raw
  CLAUDE.md existence:  PASS   (1.0 x 0.25)
  Test command:         FAIL   (0.0 x 0.35)
  Build command:        SKIP
  Project overview:     PARTIAL (0.6 x 0.20)

Protection (T2):       0.00    .................... 0%
  Sensitive file prot:  FAIL   (0.0 x 0.40)
  Security rules:       FAIL   (0.0 x 0.35)
  Hook config quality:  SKIP

Optimization (T3):     1.00    ==================== 100%
  Directory references: SKIP
  CLAUDE.md length:     PASS   (1.0 x 0.10)
  Command availability: SKIP
  Rules path validation:SKIP
  Agent config quality: SKIP
  MCP configuration:    SKIP

Detail Score (DS):     40.0    (T2: 0.00 x 60% + T3: 1.00 x 40%) x 100

Synergy: +0  (no qualifying pairs)
LQM: +0  (overview 0 + commands 0 + patterns 0)

Score: 22/100 (Grade: D)  |  Maturity: Level 0 — Incomplete

  Breakdown:
  FG_raw: (1.0x0.25 + 0.0x0.35 + 0.6x0.20) / (0.25+0.35+0.20) = 0.37/0.80 = 0.4625
  FG: 0.15 + 0.85 x 0.4625 = 0.5431
  DS: (0.00 x 0.60 + 1.00 x 0.40) x 100 = 40.0
  SB: +0 (test FAIL, build SKIP; sensitive FAIL, security FAIL)
  LQM: +0 (overview 0 + commands 0 + patterns 0)
  Final: min(0.5431 x 40.0 + 0 + 0, 100) = 21.7 ≈ 22

Next Steps:
  1. Add test command to CLAUDE.md (unlocks Gate: READY, raises FG dramatically)
  2. Add project overview with tech stack description
  3. Create .claude/settings.json with deny patterns for .env and secrets
  4. Add .claude/rules/security.md for FastAPI security guidelines
```

## Run Details

### Run 1

**Scores:** Detection 5 | Scoring 4 | Suggestions 5 | False Positives 5 | Edge Cases 4

**Observations:**

Detection (5/5):
- Correctly identified CLAUDE.md exists (PASS) with only a single-line heading
- Correctly detected absence of test command (FAIL) despite project having `pytest` in requirements.txt and actual test files -- the skill checks CLAUDE.md content, not project capabilities
- Correctly classified build command as SKIP for Python
- Correctly identified all T2 items as FAIL due to missing `.claude/` directory entirely
- Correctly classified 5 of 6 T3 items as SKIP due to the minimal config providing no checkable surface
- Hook config correctly SKIP (no settings.json at all, not just missing hooks section)
- MCP correctly SKIP -- FastAPI/uvicorn/pydantic/pytest/httpx are not database or external API client dependencies

Scoring (4/5):
- Foundation Gate calculation correct: FG_raw = 0.4625, FG = 0.5431
- T2 = 0.00 correct (both non-SKIP items are FAIL)
- T3 = 1.00 is mechanically correct (only non-SKIP item is CLAUDE.md length at PASS) but this exposes a limitation: a 1-line CLAUDE.md gets T3 = 100% because all substantive T3 checks are SKIP and the only surviving check (length) trivially passes. This is mathematically valid per the formula but semantically misleading
- Final score of 22 (Grade D) is reasonable for a project with almost no configuration. The expectation was "<20 (Grade F) or close to it" -- 22 is close but above the F threshold
- One point deducted because T1.4 (Project Overview) has a legitimate ambiguity: "# My FastAPI Project" is a heading with zero descriptive text. PARTIAL ("heading exists but vague or too brief") vs FAIL ("empty or only commands") is debatable. Marking it FAIL would yield FG_raw = 0.3125, FG = 0.4156, Final = 0.4156 x 40.0 = 16.6 (Grade F). The scoring model should clarify: is a title-only heading with no body text PARTIAL or FAIL?

Suggestions (5/5):
- All 5 suggestions are directly actionable and relevant to this specific project
- Correctly prioritized test command as the highest-leverage improvement
- Did not suggest irrelevant items (no MCP, no agents, no model routing -- all correctly omitted for this minimal project)
- Suggestion to add `pytest` references the actual dependency in requirements.txt -- project-specific, not generic

False Positives (5/5):
- Zero false positives detected
- Build command correctly SKIP for Python (not FAIL)
- MCP correctly SKIP (no DB/API deps)
- Hook config correctly SKIP (not FAIL -- absence of settings.json means hooks are not applicable, not misconfigured)
- Did not flag requirements.txt dependencies as requiring MCP (they are standard Python packages, not external service clients)
- T3.6 correctly did not flag `httpx` as an external API dependency (it is an HTTP client library that MAY be used for external APIs but is also used as the FastAPI test transport)

Edge Cases (4/5):
- T3 collapse: When 5 of 6 T3 items are SKIP, T3_Score is determined by a single trivially-passing item (CLAUDE.md length). This inflates T3 to 1.00, which contributes 40% of the Detail Score. The formula handles this correctly per the math, but the output "Optimization (T3): 100%" may confuse users who have almost no configuration. The scoring model could benefit from a note about degenerate T3 cases
- LQM correctly all zeros: no overview content to evaluate, no commands to check executability, no patterns documented. Binary/3-level format makes this unambiguous
- Synergy bonus correctly zero: no qualifying pairs can form when test is FAIL and protection items are both FAIL
- Quality Gate correctly NOT READY: CLAUDE.md exists but test command is FAIL (not SKIP, so no waiver)
- Maturity Level correctly Level 0: FG_raw = 0.4625 < 0.7 threshold for Level 1
- One point deducted for the T3 collapse edge case: the scoring model does not have guidance for when nearly all items in a tier are SKIP, creating a potentially misleading percentage display

## Cross-Run Patterns

(Single run -- cross-run analysis requires 2+ additional runs)

## Improvements Identified

- [ ] **Clarify T1.4 boundary between PARTIAL and FAIL** -- A heading-only CLAUDE.md (title with zero body text) could reasonably be either PARTIAL ("heading exists but too brief") or FAIL ("empty"). The scoring model in `plugin/skills/audit/SKILL.md` Phase 1.4 should specify: a heading with no subsequent descriptive text = FAIL; a heading with some descriptive text under 10 words = PARTIAL
- [ ] **Add degenerate-tier guidance to scoring model** -- When 5 of 6 T3 items are SKIP, T3_Score is determined by a single trivially-passing item. `references/scoring-model.md` could note: "If a tier has only 1 non-SKIP item, display a note: `(1 of N items applicable)`" to avoid implying comprehensive coverage
- [ ] **Consider a minimum-items threshold for tier display** -- If a tier has fewer than 2 non-SKIP items, the percentage may be statistically meaningless. The output format could display "N/A (insufficient data)" instead of a percentage bar when only 1 item is scored

## LLM Context Note

> For minimal-configuration projects (CLAUDE.md exists but contains only a title), the audit correctly produces a low score (22, Grade D) driven by: (1) Foundation Gate suppression from missing test command (FAIL) and weak overview (PARTIAL), (2) complete T2 failure from absent settings.json and security rules, and (3) T3 inflation from SKIP-item collapse (only CLAUDE.md length survives as PASS). Two areas need scoring model refinement: the T1.4 PARTIAL vs FAIL boundary for heading-only files, and degenerate T3 display when nearly all items are SKIP. The LQM and Synergy systems correctly contribute zero for this scenario.

## Comparison with Previous Eval

No previous audit eval exists for comparison. This is the first /audit evaluation in the test suite.
