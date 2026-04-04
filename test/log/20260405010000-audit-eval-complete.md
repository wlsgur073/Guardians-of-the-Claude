# /audit Eval — 4 Config Quality Levels

**Date:** 2026-04-05
**Action:** First /audit evaluation across perfect, partial, minimal, and edge-case configurations
**Scoring model:** Foundation-Gated Multiplicative (scoring-model.md)

---

## Results Summary

| Test Case | Audit Score | Grade | Eval Avg | Expected Range | Match? |
|-----------|------------|-------|----------|----------------|--------|
| perfect-config | 100/100 | A | 5.0 | 75+ | Yes (exceeded) |
| partial-config | 32/100 | D | 4.8 | 30-50 | Yes |
| minimal-config | 22/100 | D | 4.6 | <20 | Close (boundary issue) |
| c-cmake-edge | N/A (halt) | N/A | 4.8 | Early halt | Yes |

**Overall eval average: 4.8**

---

## Detection Accuracy: Strong

All 4 scenarios had Detection score 5/5. /audit correctly identified:
- PASS items in perfect config (zero false negatives)
- FAIL items in partial config (test command, security rules)
- SKIP items across all configs (Python build, hooks, agents, MCP)
- Early halt when CLAUDE.md is missing

**False positive count: 0 across all 4 scenarios.**

---

## Scoring Model Issues Found

### Issue 1: T1.4 PARTIAL vs FAIL boundary ambiguity

A CLAUDE.md with only `# My FastAPI Project` (heading, no body text) was classified as PARTIAL (0.3 score). The SKILL.md says:
- PARTIAL: "Heading exists but vague or too brief (under 10 words)"
- FAIL: "Empty or only commands"

A heading with zero descriptive text is on the boundary. If FAIL, the score drops from 22 to ~17 (Grade F).

**Recommended fix:** Clarify in SKILL.md: "A heading with no subsequent descriptive text = FAIL. A heading followed by some text under 10 words = PARTIAL."

### Issue 2: T3 SKIP-collapse inflation

When 5 of 6 T3 items are SKIP, the sole surviving PASS item (CLAUDE.md length) makes T3 = 100%. The formula `Sigma(s_i x w_i) / Sigma(w_i) for non-SKIP items` is mathematically correct but semantically misleading — showing "Optimization: 100%" for a bare-minimum config confuses users.

**Recommended fix:** Add a display note in scoring-model.md: "If fewer than 2 non-SKIP items remain in T2 or T3, show the percentage with a caveat: 'based on N of M items (others not applicable)'."

### Issue 3: Early halt output format undefined

When CLAUDE.md is missing, SKILL.md says "stop and recommend /generate." But it doesn't define what the output should look like — should it show the standard output format with score 0? Or a different format? Current behavior varies.

**Recommended fix:** Add a halt output template to SKILL.md: show "Gate: NOT READY", the reason, and the /generate recommendation. No score breakdown.

---

## Synergy Bonus Edge Case

In perfect-config, the test+build synergy pair was correctly excluded because build is SKIP (Python). Only the security pair earned +3. This is correct per scoring-model.md: "Both items in a pair must score PASS (1.0). If either item is SKIP, the pair is not eligible."

This edge case is well-handled in the current model.

---

## Next Steps

1. Fix T1.4 boundary definition in SKILL.md
2. Add SKIP-collapse display caveat in scoring-model.md
3. Add early halt output template in SKILL.md
