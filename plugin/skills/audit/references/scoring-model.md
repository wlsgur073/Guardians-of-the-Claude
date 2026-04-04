# Scoring Model

## Architecture

The scoring model uses a **Foundation-Gated Multiplicative** structure. Foundation (T1) acts as a gate multiplier on the Detail Score (T2 + T3), reflecting the reality that without solid foundations, protection and optimization scores are less meaningful.

```
Final = min(FG x DS + SB + LQM, 100)
         |       |      |     |
         |       |      |     +-- LQM: LLM quality judgment (max +8)
         |       |      +-------- Synergy Bonus: complementary item pairs (max +5)
         |       +--------------- Detail Score: Protection (T2) + Optimization (T3)
         +----------------------- Foundation Gate: T1 items as a multiplier
```

## Item Weights

### T1 — Foundation (Gate)

| Item | Weight | Rationale |
|------|--------|-----------|
| CLAUDE.md existence | 0.25 | Prerequisite for all configuration |
| Test command | 0.35 | Highest-leverage single item |
| Build command | 0.20 | Compile-time error checking |
| Project overview | 0.20 | Context for Claude's understanding |

### T2 — Protection (Detail x 0.60)

| Item | Weight | Rationale |
|------|--------|-----------|
| Sensitive file protection | 0.40 | Prevents real damage (secrets exposure) |
| Security rules | 0.35 | Defense-in-depth coverage |
| Hook configuration quality | 0.25 | Operational correctness |

### T3 — Optimization (Detail x 0.40)

| Item | Weight | Rationale |
|------|--------|-----------|
| Directory references | 0.20 | Configuration accuracy |
| CLAUDE.md length | 0.10 | Maintainability signal |
| Command availability | 0.20 | Tool chain integrity |
| Rules path validation | 0.15 | Rule targeting accuracy |
| Agent configuration quality | 0.20 | Agent effectiveness |
| MCP configuration | 0.15 | External tool integration |

## Item Scoring (4-Level Scale)

| Result | Score | When to use |
|--------|-------|-------------|
| PASS | 1.0 | Fully implemented — meets all criteria |
| PARTIAL | 0.6 | Exists but incomplete (e.g., `.env` in deny but `secrets/` missing) |
| MINIMAL | 0.3 | Bare minimum present (e.g., CLAUDE.md exists but no test command or project overview) |
| FAIL | 0.0 | Missing entirely |
| SKIP | — | Not applicable — remove from denominator |

## Formula

```
1. Foundation Gate (FG)
   FG_raw = Sigma(s_i x w_i) / Sigma(w_i)     for non-SKIP T1 items
   FG     = 0.15 + 0.85 x FG_raw              Range: 0.15 – 1.0

   Floor 0.15: even with zero foundation, T2/T3 status is minimally visible
   so users can see what else needs work.

2. Detail Score (DS)
   T2_Score = Sigma(s_i x w_i) / Sigma(w_i)   for non-SKIP T2 items
   T3_Score = Sigma(s_i x w_i) / Sigma(w_i)   for non-SKIP T3 items
   DS       = (T2_Score x 0.60 + T3_Score x 0.40) x 100

   If T2 is all SKIP: DS = T3_Score x 100.
   If T3 is all SKIP: DS = T2_Score x 100.
   If both are all SKIP: DS = 0.

   Display caveat: if fewer than 2 non-SKIP items remain in T2 or T3,
   append "(based on N of M items — others not applicable)" to the
   percentage display so users do not misread a high percentage as
   comprehensive coverage.

3. Synergy Bonus (SB)
   SB = sum of applicable bonuses             Max: +5

4. LLM Quality Modifier (LQM)
   LQM = sum of applicable judgments           Max: +8

5. Final Score
   Final = min(FG x DS + SB + LQM, 100)       Range: 0 – 100
```

## Synergy Bonus

Complementary item pairs earn bonus points when BOTH achieve PASS (1.0):

| Pair | Bonus | Rationale |
|------|-------|-----------|
| Test command + Build command | +2 | CI pipeline completeness |
| Sensitive file protection + Security rules | +3 | Comprehensive security posture |

Maximum total synergy bonus: **+5 points**

Both items in a pair must score PASS (1.0). If either item is SKIP, PARTIAL, MINIMAL, or FAIL, the pair is not eligible.

## LLM Quality Modifier (LQM)

After completing all mechanical checks (Phases 1-3), the auditor evaluates 3 constrained judgment questions about CLAUDE.md content quality. These use binary or 3-level answers to minimize scoring variability across sessions.

| Question | Points | Format |
|----------|--------|--------|
| Does the project overview accurately reflect the current codebase state, tech stack, and purpose? | 0 / 1 / 3 | 3-level |
| Are the documented commands copy-paste executable and correct for this project's toolchain? | 0 / 2 | Binary |
| Are project-specific non-obvious patterns, gotchas, or conventions documented? | 0 / 1 / 3 | 3-level |

Maximum LQM: **+8 points**

### Scoring guidelines

**Overview accuracy (0/1/3):**
- 3: Overview matches actual project structure, tech stack, and purpose as observed during audit
- 1: Overview exists but is partially outdated or missing key aspects
- 0: Overview is misleading, severely outdated, or absent

**Command executability (0/2):**
- 2: All documented commands reference correct tools and appear runnable as-is
- 0: Commands are missing, reference wrong tools, or require undocumented modifications

**Non-obvious patterns (0/1/3):**
- 3: Project-specific gotchas, conventions, or patterns documented that cannot be inferred from code alone
- 1: Some non-obvious information present but incomplete
- 0: No project-specific patterns or gotchas documented

### Design constraints

LQM is intentionally small (max 8% of total score) to preserve scoring reliability:
- Constrained formats (binary/3-level) keep typical session-to-session variability within +/-2 points
- LQM cannot rescue a mechanically weak project (e.g., score 40 + LQM 8 = 48, still Grade C)
- LQM rewards quality documentation at grade boundaries (e.g., 74 + 6 = 80, B to A)
- LQM has diminishing impact as mechanical scores approach 100 due to the score cap

## Quality Gate

The Quality Gate is a **display-only label** independent of the score calculation. The Foundation Gate (FG) naturally suppresses scores when foundations are missing, making a separate score penalty redundant.

Conditions (ALL applicable must be met for READY):
- CLAUDE.md exists (root or `.claude/CLAUDE.md`) — always required
- Test command is present in CLAUDE.md — waived if test command is SKIP

Display: **"Gate: READY"** or **"Gate: NOT READY"**

## Grade

| Grade | Score Range |
|-------|------------|
| A | >= 80 |
| B | >= 60 |
| C | >= 40 |
| D | >= 20 |
| F | < 20 |

## Maturity Level

Maturity levels are cumulative — each level requires the previous level to be satisfied:

| Level | Condition | Meaning |
|-------|-----------|---------|
| Level 1 — Basic | FG_raw >= 0.7 | Claude can work effectively |
| Level 2 — Protected | Level 1 AND T2_Score >= 0.6 | Project is safe from common mistakes |
| Level 3 — Optimized | Level 2 AND T3_Score >= 0.5 | Configuration is well-organized and maintainable |

If Level 1 is not met, display **"Level 0 — Incomplete"**.

## Output Format

```
Configuration Audit Results
===========================

Quality Gate: READY    (CLAUDE.md OK, test command OK)

Foundation Gate (FG):  1.00    ==================== 100%

Protection (T2):       0.70    ==============...... 70%
Optimization (T3):     0.50    ==========.......... 50%
Detail Score (DS):     62.0    (T2: 0.70 x 60% + T3: 0.50 x 40%) x 100

Synergy: +2  (test + build)
LQM: +6  (overview 3 + commands 2 + patterns 1)

Score: 70/100 (Grade: B)  |  Maturity: Level 3 — Optimized

  Breakdown:
  FG: 0.15 + 0.85 x 1.00 = 1.00
  DS: (0.70 x 0.60 + 0.50 x 0.40) x 100 = 62.0
  SB: +2 (test + build)
  LQM: +6 (overview 3 + commands 2 + patterns 1)
  Final: 1.00 x 62.0 + 2 + 6 = 70

[Detailed findings per item...]

Suggestions
  * [actionable improvements]

Since last audit (2026-03-31): 65 -> 70 (+5). Note: scoring model changed (v1 -> v2).
Still open: no MCP configuration, agent model diversity.
```

## Early Halt Output Format

When CLAUDE.md does not exist (T1.1 FAIL), the audit halts immediately. Use this output instead of the standard format:

```
Configuration Audit Results
===========================

Quality Gate: NOT READY

CLAUDE.md not found at project root or .claude/CLAUDE.md.
Cannot proceed with audit — CLAUDE.md is a prerequisite for all checks.

Detected project signals:
  * [list any dependency manifests, source files, or frameworks found]

Recommendation: Run /claude-code-template:generate to create initial configuration.
```

Do not produce a numeric score, grade, or maturity level. The halt is not a score of zero — it means the audit could not be performed.
