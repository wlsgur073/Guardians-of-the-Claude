# /generate Evaluation Rubric

Rubric for evaluating `/generate` skill output quality. Score each dimension on a 1-5 scale per run.

---

## Dimensions

### 1. Accuracy

**Measures:** Are generated commands, file paths, and technical references correct for the target stack?

| Score | Criteria |
|-------|----------|
| 1 | Multiple commands fail to execute. Wrong package manager, incorrect paths, or references to tools not in the project |
| 2 | Some commands work but others have errors. Mostly correct tool references with notable mistakes |
| 3 | Most commands are correct. Minor issues like slightly wrong flags or optional dependency references |
| 4 | All core commands work. At most one trivial issue (e.g., missing optional flag) |
| 5 | Every command is copy-paste executable. Paths, tools, and flags are all correct for this specific project |

**Alignment with best-practices.md:** "All commands must be copy-pasteable — use actual project commands, not placeholders"

### 2. Customization

**Measures:** Is the output tailored to this specific project, or could it apply to any project of the same type?

| Score | Criteria |
|-------|----------|
| 1 | Completely generic. Could be any project. No reference to actual project files or structure |
| 2 | Mentions the language/framework but nothing project-specific. Reads like a template |
| 3 | References actual directory structure but security rules, hooks, or agent suggestions are generic |
| 4 | Most sections are project-specific. One or two areas could be more tailored |
| 5 | Fully tailored. References actual file paths, detected patterns, project-specific conventions and gotchas |

**Alignment with best-practices.md:** "Use actual directory names", "Security rules should reference detected patterns"

### 3. Completeness

**Measures:** Does the output cover all features relevant to this project type?

| Score | Criteria |
|-------|----------|
| 1 | Missing essential sections (no test command, no project overview) |
| 2 | Has basics but missing multiple relevant features (e.g., no security rules for a web API) |
| 3 | Core sections present. Missing one or two features that would benefit this project type |
| 4 | Comprehensive coverage. Only missing advanced/optional features |
| 5 | All relevant features covered for this project type, including security, hooks, or agents where appropriate |

**Note:** Completeness is relative to the project — a CLI tool doesn't need API security rules. Score based on what the project actually needs, not a universal checklist.

### 4. Conciseness

**Measures:** Information density and adherence to the 200-line limit.

| Score | Criteria |
|-------|----------|
| 1 | Over 200 lines, or significant filler/redundant content |
| 2 | Under 200 lines but contains obvious redundancy or unnecessary sections |
| 3 | Appropriate length. Minor areas where content could be tighter |
| 4 | Well-edited. Every section earns its space. One or two lines could be trimmed |
| 5 | Under 200 lines, every line provides unique value. No redundancy, no filler |

**Alignment with best-practices.md:** "CLAUDE.md must stay under 200 lines — be concise"

### 5. Best Practices Compliance

**Measures:** Adherence to all rules defined in `best-practices.md`.

| Score | Criteria |
|-------|----------|
| 1 | Multiple best-practice violations (placeholders, generic rules, missing statusMessage, etc.) |
| 2 | Several violations. Some rules followed but pattern is inconsistent |
| 3 | Most rules followed. One or two violations |
| 4 | All major rules followed. At most one minor deviation |
| 5 | Full compliance with every applicable rule in best-practices.md |

**Checklist (score based on applicable items):**
- [ ] Commands are copy-pasteable, not placeholders
- [ ] Uses actual directory names, not generic examples
- [ ] Skills use `$ARGUMENTS` where applicable
- [ ] Skills bundle reference files in `references/`
- [ ] Hooks include `statusMessage`
- [ ] Security rules reference detected patterns
- [ ] Agent model comments explain the model choice
- [ ] Advanced features presented as multi-select

---

## Scoring Process

1. Run `/generate` on the prepared scenario project directory
2. Score each dimension immediately after the run (do not compare between runs while scoring)
3. Record scores and specific observations per run
4. After all runs (3-5), calculate averages and identify patterns

## Verdict Scale

Based on the average score across all dimensions:

| Verdict | Average | Meaning |
|---------|---------|---------|
| excellent | >= 4.5 | Template performs well for this scenario |
| acceptable | >= 3.5 | Functional but has clear improvement areas |
| needs_work | >= 2.5 | Significant weaknesses that should be addressed |
| poor | < 2.5 | Major issues — template needs rework for this scenario type |
