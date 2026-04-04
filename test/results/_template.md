---
date: YYYY-MM-DD
scenario: <scenario-id>
template_version: <e.g., v2.3.0>
skill: <generate | audit>
run_count: <3-5>
scores:
  dimension_1: [run1, run2, run3]
  dimension_2: [run1, run2, run3]
  dimension_3: [run1, run2, run3]
  dimension_4: [run1, run2, run3]
  dimension_5: [run1, run2, run3]
average: <overall average across all dimensions and runs>
verdict: <excellent | acceptable | needs_work | poor>
---

# <scenario-id> -- <skill> Evaluation (YYYY-MM-DD)

## Summary

<2-3 sentences: run count, overall average, which dimensions are consistently strong/weak>

## Run Details

### Run 1

**Scores:** D1 _ | D2 _ | D3 _ | D4 _ | D5 _

**Observations:**
- <specific observation about what the skill did well>
- <specific observation about what went wrong or could improve>
- <any notable behavior or edge case encountered>

### Run 2

**Scores:** D1 _ | D2 _ | D3 _ | D4 _ | D5 _

**Observations:**
- ...

### Run 3

**Scores:** D1 _ | D2 _ | D3 _ | D4 _ | D5 _

**Observations:**
- ...

## Cross-Run Patterns

- <pattern that appeared consistently across runs>
- <dimensions with high variance and possible explanation>
- <any run that was an outlier and why>

## Improvements Identified

- [ ] <actionable improvement 1 — reference specific file/rule to change>
- [ ] <actionable improvement 2>
- [ ] <actionable improvement 3>

## LLM Context Note

> <2-4 sentences summarizing the key finding in a format useful for LLM context.
> This section can be extracted and fed into /generate or /audit as prior knowledge.
> Focus on: what the skill struggles with for this scenario type, and what to do differently.>

## Comparison with Previous Eval

<If this scenario was tested before, note: previous date, previous average, score delta, what changed>
