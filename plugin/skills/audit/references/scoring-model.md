# Scoring Model

## Architecture

The scoring model uses a **Foundation-Gated Multiplicative** structure. Foundation (T1) acts as a gate multiplier on the Detail Score (T2 + T3), reflecting the reality that without solid foundations, protection and optimization scores are less meaningful.

```markdown
Final = min(max(FG x DS + SB + LAV, 0), cap)
         |       |      |     |
         |       |      |     +-- LAV: LLM Accuracy Verification (-9 ~ +10)
         |       |      +-------- Synergy Bonus: complementary item pairs (max +5)
         |       +--------------- Detail Score: Protection (T2) + Optimization (T3)
         +----------------------- Foundation Gate: T1 items as a multiplier
```

## Item Weights

### T1 — Foundation (Gate)

| Item | Weight | Rationale |
| ------ | -------- | ----------- |
| CLAUDE.md existence | 0.25 | Prerequisite for all configuration |
| Test command | 0.35 | Highest-leverage single item |
| Build command | 0.20 | Compile-time error checking |
| Project overview | 0.20 | Context for Claude's understanding |

### T2 — Protection (Detail x 0.60)

| Item | Weight | Rationale |
| ------ | -------- | ----------- |
| Sensitive file protection | 0.40 | Prevents real damage (secrets exposure) |
| Security rules | 0.35 | Defense-in-depth coverage |
| Hook configuration quality | 0.25 | Operational correctness |

### T3 — Optimization (Detail x 0.40)

| Item | Weight | Rationale |
| ------ | -------- | ----------- |
| Directory references | 0.20 | Configuration accuracy |
| CLAUDE.md length | 0.10 | Maintainability signal |
| Command availability | 0.20 | Tool chain integrity |
| Rules path validation | 0.10 | Rule targeting accuracy |
| Agent configuration quality | 0.15 | Agent effectiveness |
| MCP configuration | 0.15 | External tool integration |
| Environment variable documentation | 0.10 | Setup completeness |

## Item Scoring (4-Level Scale)

| Result | Score | When to use |
| -------- | ------- | ------------- |
| PASS | 1.0 | Fully implemented — meets all criteria |
| PARTIAL | 0.6 | Exists but incomplete (e.g., `.env` in deny but `secrets/` missing) |
| MINIMAL | 0.3 | Bare minimum present (e.g., CLAUDE.md exists but no test command or project overview) |
| FAIL | 0.0 | Missing entirely |
| SKIP | — | Not applicable — remove from denominator |

## Formula

```markdown
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

4. LAV (LLM Accuracy Verification)
   LAV = sum of L1–L6 scores                  Range: -9 ~ +10
   See references/checks/lav.md for evaluation structure.

5. Quality Cap
   If LAV < 0, the final score is capped to prevent high mechanical scores
   from masking quality issues detected by LLM evaluation:

   LAV >= 0  →  cap = 100 (no restriction)
   LAV < 0   →  cap = 90 + LAV
                 LAV = -1  → cap = 89
                 LAV = -4  → cap = 86
                 LAV = -9  → cap = 81

6. Final Score
   Raw   = max(FG x DS + SB + LAV, 0)
   Final = min(Raw, cap)                       Range: 0 – 100
   The max(..., 0) floor prevents negative scores.
   The Quality Cap prevents high DS from masking LAV-detected quality issues.
```

## Synergy Bonus

Complementary item pairs earn bonus points when BOTH achieve PASS (1.0):

| Pair | Bonus | Rationale |
| ------ | ------- | ----------- |
| Test command + Build command | +2 | CI pipeline completeness |
| Sensitive file protection + Security rules | +3 | Comprehensive security posture |

Maximum total synergy bonus: **+5 points**

Both items in a pair must score PASS (1.0). If either item is SKIP, PARTIAL, MINIMAL, or FAIL, the pair is not eligible.

## Quality Gate

The Quality Gate is a **display-only label** independent of the score calculation. The Foundation Gate (FG) naturally suppresses scores when foundations are missing, making a separate score penalty redundant.

Conditions (ALL applicable must be met for READY):

- CLAUDE.md exists (root or `.claude/CLAUDE.md`) — always required
- Test command is present in CLAUDE.md — waived if test command is SKIP

Display: **"Gate: READY"** or **"Gate: NOT READY"**

## Grade

| Grade | Score Range |
| ------- | ------------ |
| A | >= 80 |
| B | >= 60 |
| C | >= 40 |
| D | >= 20 |
| F | < 20 |

## Maturity Level

Maturity levels are cumulative — each level requires the previous level to be satisfied:

| Level | Condition | Meaning |
| ------- | ----------- | --------- |
| Level 1 — Basic | FG_raw >= 0.7 | Claude can work effectively |
| Level 2 — Protected | Level 1 AND T2_Score >= 0.6 | Project is safe from common mistakes |
| Level 3 — Optimized | Level 2 AND T3_Score >= 0.5 | Configuration is well-organized and maintainable |

If Level 1 is not met, display **"Level 0 — Incomplete"**.
