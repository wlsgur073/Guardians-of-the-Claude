# Eval-Driven Testing Strategy

A testing strategy for template and skill repositories that uses **iterative evaluation loops** to progressively improve template quality. Designed for projects where Markdown is both code and data, with LLM-driven skills (`/generate`, `/audit`) as the primary outputs.

---

## Why Eval-Driven, Not Traditional Testing

Traditional software tests verify deterministic outputs: `f(x) = y`, always. LLM-driven skills produce non-deterministic outputs — running `/generate` twice on the same project yields different results. This makes exact-match testing fundamentally inapplicable.

Eval-Driven Development replaces pass/fail with **scored dimensions measured across multiple runs**, enabling systematic quality improvement despite output variability.

```
Traditional Testing:  code  -> test  -> Pass/Fail       (one-time gate)
Eval-Driven:          template -> run -> evaluate -> improve -> re-run  (iterative loop)
```

---

## The Eval Loop

```
+-- 1. Select Scenario (from scenarios/matrix.md)
|
+-- 2. Setup (scripts/setup-scenario.sh creates project directory)
|
+-- 3. Execute (run /generate or /audit, 3-5 times per scenario)
|
+-- 4. Evaluate (score each run against rubrics/)
|
+-- 5. Record (write results to results/YYYY-MM-DD-<scenario>.md)
|
+-- 6. Analyze
|     +-- Consistently low dimensions  -> template improvement target
|     +-- High variance dimensions     -> skill prompt ambiguity
|     +-- Scenario-specific weakness   -> stack-specific support needed
|
+-- 7. Improve Templates
|
+-- 8. Comparative Test (A/B: before vs after, same scenarios)
|     +-- Confirm improvement
|     +-- Check for regression in other scenarios
|
+-- 9. Next Cycle -> (back to step 1)
```

---

## Eval Techniques

### Rubric-Based Evaluation

Score LLM outputs against predefined quality dimensions instead of exact-match comparison. Each dimension uses a 1-5 scale with explicit criteria for each level.

- `/generate` rubric: Accuracy, Customization, Completeness, Conciseness, Best Practices
- `/audit` rubric: Detection, Scoring, Suggestions, False Positives, Edge Cases

See `rubrics/generate-rubric.md` and `rubrics/audit-rubric.md` for full criteria.

### Multi-Run Averaging

Run each scenario 3-5 times to separate **template weakness** from **LLM output variance**.

- If a dimension is consistently low (e.g., Customization 2-3 across all runs) -> real template issue
- If a dimension swings widely (e.g., Completeness 2-5 across runs) -> skill prompt is ambiguous
- Report both average and range per dimension

### Comparative Testing (A/B)

Compare template versions on identical scenarios to measure improvement:

1. Record baseline scores with current template (version A)
2. Modify template
3. Re-run same scenarios with modified template (version B)
4. Compare: improvements must not cause regressions in other scenarios

### Adversarial Testing

Design extreme or atypical scenarios to expose template assumptions:

- Projects with no package manager (pure shell scripts)
- Multi-language monorepos
- Projects with pre-existing broken CLAUDE.md
- Projects with committed sensitive files (.env tracked)

### Ablation Study

Remove specific rules/sections from templates, re-run scenarios, measure impact:

- Quantifies each rule's contribution to output quality
- Prevents template bloat by identifying low-value rules
- Example: remove "Security rules should reference detected patterns" from best-practices.md, measure Customization score drop

---

## Structural Validation (Complementary)

Automated checks that run independently of the eval loop. These verify the **repository's own structural integrity**, not LLM output quality.

Implemented in `scripts/validate.sh`:

### Schema Validation
- YAML frontmatter: required fields present and correctly typed
- JSON files: valid syntax, required keys present
- Semver format: version fields match `X.Y.Z` pattern

### Property-Based Checks
- All guide files have `title`, `description`, `version` in frontmatter
- All internal links resolve to existing files
- All templates reference "TaskFlow" (per contribution rules)
- No file contains deprecated keywords (`allowed-tools`)
- Guide files stay under line limits (~130, advanced ~200)

### Cross-Reference Consistency
- Guides <-> Templates: recommended patterns are reflected
- `/generate` templates <-> `templates/` examples: structural alignment
- `/audit` scoring criteria <-> `/generate` output structure: compatibility
- Guides "not recommended" patterns do not appear in templates

---

## Directory Structure

```
test/
  testing-strategy.md               <- This file
  scenarios/
    matrix.md                       <- Master matrix with phases and priorities
    <language>-<framework>-<state>.md  <- Individual scenario definitions
  rubrics/
    generate-rubric.md              <- /generate evaluation criteria (5 dimensions)
    audit-rubric.md                 <- /audit evaluation criteria (5 dimensions)
  results/
    _template.md                    <- Result log format template
    YYYY-MM-DD-<scenario>.md        <- Accumulated result logs
  fixtures/
    <language>-<framework>/         <- Minimal project skeletons per stack
  scripts/
    setup-scenario.sh               <- Creates test project directory from fixtures
    validate.sh                     <- Static structural validation for main repo
```

## Result Log Format

Each result file uses **YAML frontmatter (machine-parseable) + Markdown body (human-readable)** to serve dual purposes:

1. **Human reference**: Review past findings, track improvement trends
2. **LLM context**: Extract `LLM Context Note` section to feed into `/generate` for informed generation

Key fields in frontmatter: `date`, `scenario`, `template_version`, `skill`, `run_count`, `scores` (per-dimension arrays), `average`, `verdict`.

See `results/_template.md` for the complete format.

## Naming Conventions

- Scenario files: `<language>-<framework>-<state>.md` (e.g., `python-fastapi-new.md`)
- Result logs: `YYYY-MM-DD-<scenario>.md` (e.g., `2026-04-04-python-fastapi-new.md`)
- Same-day re-evaluation: append version suffix (e.g., `2026-04-04-python-fastapi-new-v2.md`)
- Fixture directories: `<language>-<framework>/` matching scenario fixture field

## Eval Cycle Checklist

Use this checklist when running a full eval cycle:

- [ ] Select scenario(s) from matrix — check which haven't been tested recently
- [ ] Run `setup-scenario.sh` to prepare test project directory
- [ ] Execute skill 3-5 times, scoring each run against rubric
- [ ] Record results using `_template.md` format
- [ ] Identify consistently low dimensions and cross-run patterns
- [ ] If improving templates: run comparative test (A/B) on affected scenarios
- [ ] Verify no regressions in other scenarios after template changes
- [ ] Update scenario priority if coverage gaps are found
