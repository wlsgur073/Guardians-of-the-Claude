# /audit Evaluation Rubric

Rubric for evaluating `/audit` skill output quality. Score each dimension on a 1-5 scale per run.

---

## Dimensions

### 1. Detection Accuracy

**Measures:** Does `/audit` correctly identify which configuration items are present, missing, or incomplete?

| Score | Criteria |
|-------|----------|
| 1 | Multiple items misidentified (present items marked missing, or missing items marked present) |
| 2 | Some detection errors. Gets the obvious items right but misses or misidentifies subtle ones |
| 3 | Most items correctly identified. One or two detection errors on edge cases |
| 4 | All items correctly identified. At most one borderline judgment call that could go either way |
| 5 | Perfect detection. Every item's status (PASS/PARTIAL/MINIMAL/FAIL/SKIP) is correct |

**Alignment with scoring-model.md:** Check that each T1/T2/T3 item result matches what is actually in the project.

### 2. Scoring Correctness

**Measures:** Does the final score match the formula defined in `scoring-model.md`?

| Score | Criteria |
|-------|----------|
| 1 | Final score is off by more than 15 points from the correct calculation |
| 2 | Score is off by 8-15 points. Formula steps have errors in multiple components |
| 3 | Score is off by 3-7 points. Minor miscalculation in one component (e.g., wrong weight) |
| 4 | Score is off by 1-2 points. Rounding or LQM judgment difference only |
| 5 | Score matches the formula exactly. FG, DS, SB, LQM all correctly calculated and shown |

**Verification checklist:**
- [ ] Foundation Gate (FG) = 0.15 + 0.85 x FG_raw (range 0.15-1.0)
- [ ] Detail Score (DS) = (T2 x 0.60 + T3 x 0.40) x 100
- [ ] Synergy Bonus: only awarded when BOTH items in a pair score PASS (1.0)
- [ ] LQM: within constrained ranges (overview 0/1/3, commands 0/2, patterns 0/1/3)
- [ ] Final = min(FG x DS + SB + LQM, 100)
- [ ] Grade and Maturity Level consistent with the calculated score

### 3. Suggestion Quality

**Measures:** Are the improvement suggestions actionable, relevant, and prioritized?

| Score | Criteria |
|-------|----------|
| 1 | Suggestions are vague ("improve your config") or irrelevant to the project |
| 2 | Some suggestions are actionable but most are generic or low-priority |
| 3 | Suggestions are relevant. Some could be more specific or better prioritized |
| 4 | Actionable and well-prioritized suggestions. Most reference specific files or configurations |
| 5 | Every suggestion is specific, actionable, project-relevant, and ordered by impact |

**Key indicator:** Can the user implement each suggestion without additional research?

### 4. False Positive Rate

**Measures:** Does `/audit` flag issues that don't actually exist?

| Score | Criteria |
|-------|----------|
| 1 | 3+ false positives. Flags correctly configured items as missing or broken |
| 2 | 2 false positives that could mislead the user |
| 3 | 1 false positive, or warnings that are technically correct but misleading in context |
| 4 | No false positives. All flagged items are genuine issues |
| 5 | No false positives, and nuanced handling of borderline cases (e.g., PARTIAL vs FAIL is well-judged) |

**Common false positive patterns to watch for:**
- Flagging test command as missing when it's present in a non-obvious format
- Flagging security rules as missing when the project doesn't need them
- Flagging build command as missing for interpreted languages

### 5. Edge Case Handling

**Measures:** Does `/audit` correctly handle non-standard project types and SKIP conditions?

| Score | Criteria |
|-------|----------|
| 1 | Crashes or gives nonsensical results for edge cases |
| 2 | Handles some edge cases but applies standard criteria to non-standard projects |
| 3 | Recognizes most edge cases. SKIP items mostly correct but some misjudged |
| 4 | Good edge case handling. SKIP, PARTIAL judgments are well-reasoned |
| 5 | Excellent edge case handling. Docs-only projects, non-standard build systems, multi-language repos all handled correctly |

**Edge cases to test:**
- Documentation-only repository (no app code): test/build commands should be SKIP
- Interpreted language (Python, Ruby): build command should be SKIP
- Monorepo: per-package vs root-level config detection
- Pre-existing broken config: graceful handling, not confusion

---

## Scoring Process

1. Prepare a project with **known configuration state** (you should know the correct audit result before running)
2. Run `/audit` on the project
3. Compare the audit output against your expected results
4. Score each dimension based on alignment with expected results
5. Record scores and specific observations per run
6. After all runs (3-5), calculate averages and identify patterns

## Verdict Scale

| Verdict | Average | Meaning |
|---------|---------|---------|
| excellent | >= 4.5 | /audit is reliable for this scenario |
| acceptable | >= 3.5 | Functional but some calibration needed |
| needs_work | >= 2.5 | Significant scoring or detection issues |
| poor | < 2.5 | Major issues — scoring model needs rework for this scenario type |

## Cross-Skill Validation

After evaluating both `/generate` and `/audit` on the same scenario:

- Run `/audit` on `/generate`'s output — the audit score should be high (>= 75) if `/generate` is working correctly
- If `/generate` scores well in rubric but `/audit` gives a low score, either `/generate`'s rubric is too lenient or `/audit`'s scoring model has gaps
- If `/generate` scores poorly but `/audit` gives a high score, `/audit` may be missing important quality signals
