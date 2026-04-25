---
title: "Scoring Model"
description: "Conservative scoring formula for /audit — LAV item-aware multiplier with cap tier {50, 60, 100}"
version: "1.0.1"
scoring_contract_id: "audit-score-v4.0.0"
---

# Scoring Model

## Architecture

The scoring model uses an **LAV Item-Aware Multiplier** structure. The Detail Score (T2 + T3) is multiplied by a factor derived from the non-L5 LAV components, with the L5 (Conciseness) finding routed through a cap-tier mechanism rather than the multiplier — preventing high mechanical scores from masking severely overconfigured CLAUDE.md files.

```
Final = min(DS × (1 + LAV_nonL5 / 50) + SB, cap)
  LAV_nonL5 = L1 + L2 + L3 + L4 + L6
  cap = 60  if L5 == −3 AND no other Li at its minimum
  cap = 50  if L5 == −3 AND at least one other Li at its minimum
  cap = 100 otherwise
```

## Item Weights

### T1 — Foundation

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

#### T2.2 SKIP Condition

T2.2 (Security Rules) is SKIP when the project has no network input surface:

- **Evidence for SKIP:** No web framework in dependency manifest (no express, fastapi, flask, django, spring-boot, gin, actix-web, etc.) AND no HTTP server/router patterns in source code
- **Default behavior:** SKIP for CLI tools, libraries, build tools, documentation-only projects
- **Override:** Auditor may change SKIP to PARTIAL if file I/O based security risks are identified (e.g., CLI that parses untrusted files)

The `/audit` skill determines this at runtime by inspecting the project, not from pre-declared metadata.

### T3 — Optimization (Detail x 0.40)

| Item | Weight | Rationale |
| ------ | -------- | ----------- |
| Directory references | 0.20 | Configuration accuracy |
| CLAUDE.md length | 0.10 | Maintainability signal |
| Command availability | 0.20 | Tool chain integrity |
| Rules path validation¹ | 0.10 | Rule targeting accuracy |
| Agent configuration quality¹ | 0.15 | Agent effectiveness |
| MCP configuration¹ | 0.15 | External tool integration |
| Environment variable documentation | 0.10 | Setup completeness |

¹ Count sourced from `profile.claude_code_configuration_state.*_count` fields; co-owned across `/audit` + `/secure` + `/create` per `plugin/references/lib/merge_rules.md` §profile.json.

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
1. Detail Score (DS)
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

2. Synergy Bonus (SB)
   SB = sum of applicable bonuses             Max: +5

3. LAV (LLM Accuracy Verification)
   LAV_nonL5 = L1 + L2 + L3 + L4 + L6        Range: -6 ~ +9 (excludes L5)
   L5 ∈ [−3, +1]                              Routed via cap tier (below)
   See references/checks/lav.md for evaluation structure.

4. Cap Tier
   cap = 60  if L5 == −3 AND no other Li at its minimum (L1≥−2, L2≥−1, L4≥0)
   cap = 50  if L5 == −3 AND at least one other Li at its minimum (L1=−3, L2=−2, or L4=−1)
   cap = 100 otherwise

   Real LAV maxima (lav.md:23-28): L1∈[−3,+2], L2∈[−2,+2], L3∈[0,+3], L4∈[−1,+1], L6∈[0,+1].

5. Final Score
   Final = min(DS × (1 + LAV_nonL5 / 50) + SB, cap)
   Range: bounded above by cap; lower bound governed by inputs (no separate clamp).
```

(Note: the v2.12.0 LAV item-aware multiplier replaces the v2.10.0 Foundation-Gated Multiplicative formula. FG is no longer a multiplier on DS — acceptance verified by 5-sample simulation under `ci/scripts/check-scoring-formula.py`.)

## LAV Axis Summary

| Axis | Range | Nature | Included in `LAV_nonL5` |
|---|---|---|---|
| L1 — Structure Accuracy | −3 / 0 / +2 | Accuracy | Yes |
| L2 — Command Reliability | −2 / 0 / +2 | Reliability | Yes |
| L3 — Patterns / Gotchas documentation | 0 / +1 / +3 | Documentation quality | Yes |
| L4 — Structural Quality | −1 / 0 / +1 | Structural quality | Yes |
| L5 — Content Conciseness | −3 / 0 / +1 | Conciseness | **No** — routed via cap tier |
| L6 — Actionability | 0 / +1 | Actionability | Yes |

`LAV_nonL5` sum range: **−6 to +9** (excluding L5). Full axis definitions + scoring guidelines in `plugin/skills/audit/references/checks/lav.md` line 23-28 (ranges) and line 34-62 (per-axis guidance).

### LAV/T3 Boundary Rule

LAV axes evaluate holistic accuracy that cannot be mechanically verified. When a T3 mechanical item already detects a deficiency, the paired LAV axis scores **0** for that specific issue — preventing double-penalty (lav.md line 7-15).

| Mechanical item | Paired LAV axis | Non-overlapping LAV scope |
|---|---|---|
| T3.1 Directory references | L1 Structure Accuracy | Wrong architecture descriptions, outdated component relationships |
| T3.3 Command availability | L2 Command Reliability | Undocumented prerequisite steps, wrong command flags, missing workflow context |
| T3.7 Environment variable docs | L2 Command Reliability | (same axis, different evidence surface) |

Mechanical and LAV layers are complementary, not redundant.

## Synergy Bonus

Complementary item pairs earn bonus points when BOTH achieve PASS (1.0):

| Pair | Bonus | Rationale |
| ------ | ------- | ----------- |
| Test command + Build command | +2 | CI pipeline completeness |
| Sensitive file protection + Security rules | +3 | Comprehensive security posture |

Maximum total synergy bonus: **+5 points**

Both items in a pair must score PASS (1.0). If either item is SKIP, PARTIAL, MINIMAL, or FAIL, the pair is not eligible.

## Quality Gate

The Quality Gate is a **display-only label** independent of the score calculation.

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
| Level 1 — Basic | T1_Score >= 0.7 | Claude can work effectively |
| Level 2 — Protected | Level 1 AND T2_Score >= 0.6 | Project is safe from common mistakes |
| Level 3 — Optimized | Level 2 AND T3_Score >= 0.5 | Configuration is well-organized and maintainable |

If Level 1 is not met, display **"Level 0 — Incomplete"**.
