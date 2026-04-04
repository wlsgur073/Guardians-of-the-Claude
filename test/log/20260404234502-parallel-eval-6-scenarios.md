# Parallel Eval — 6 High-Priority Scenarios

**Date:** 2026-04-04 23:45
**Action:** First parallel eval cycle across 6 languages/frameworks
**Template version:** v2.3.0 with Phase 2.5S + path/dependency verification improvements

---

## Results Summary

| Scenario | Avg Score | Verdict | Notes |
|----------|-----------|---------|-------|
| python-fastapi-new (Run 1, pre-improvement) | 4.0 | acceptable | 4 issues found |
| python-fastapi-new (Run 2, post-improvement) | 5.0 | excellent | All 4 issues resolved |
| javascript-nextjs-new | 5.0 | excellent | .gitignore gap noted |
| rust-cli-new | 5.0 | excellent | Clean |
| java-springboot-new | 5.0 | excellent | Correctly detected no mvnw |
| c-cmake-new | 5.0 | excellent | Correctly handled no test framework |
| go-web-new | 5.0 | excellent | .gitignore gap noted |

**A/B comparison (python-fastapi-new):** 4.0 → 5.0 (+1.0). Template improvements (Phase 2.5S pre-scan, path verification, dependency verification) resolved all 4 Run 1 issues.

---

## Cross-Framework Pattern: .gitignore Not Created

**Found in:** javascript-nextjs-new, go-web-new
**Not found in:** c-cmake-new (correctly created .gitignore)

The starter template says: "append this line if not already present" for `.claude/settings.local.json` in `.gitignore`. When the fixture has no `.gitignore` at all, two agents skipped creation entirely while one created it.

**Root cause:** The template instruction "append this line if not already present" is ambiguous — "not already present" implies a file exists to check. When no `.gitignore` exists, the instruction doesn't clearly say "create it."

**Recommended fix:** Change starter.md instruction to: "If `.gitignore` exists, append this line if not already present. If `.gitignore` does not exist, create it with this line."

---

## Template Improvements Validated

The 3 rules added to best-practices.md after Run 1 were effective across all 6 frameworks:

1. **Verify paths exist before referencing** — No agent referenced non-existent directories (vs Run 1 which hallucinated `app/models/`)
2. **Verify command dependencies** — No agent suggested commands for uninstalled packages (vs Run 1 which suggested `pytest --cov` without pytest-cov)
3. **Include project-specific details** — Every agent referenced actual code details (endpoints, structs, classes, defines)

Phase 2.5S (Pre-Generation Scan) was the single highest-impact change — forcing a file/dependency scan before generation prevented the entire class of hallucination bugs.

---

## Edge Cases Handled Well

| Edge Case | Scenario | Handling |
|-----------|----------|----------|
| No test framework | c-cmake-new | Testing section explicitly notes absence, suggests CTest/Unity |
| No mvnw wrapper | java-springboot-new | Uses `mvn` instead of `./mvnw` |
| No test runner in package.json | javascript-nextjs-new | Honest about no test runner installed |
| Stdlib-only Go project | go-web-new | No framework commands suggested |
| Rust edition 2024 | rust-cli-new | Correctly referenced in output |

---

## Gaps for Next Eval Cycle

1. **.gitignore creation ambiguity** — Fix starter.md instruction (see above)
2. **Only "new" state tested** — "existing" state scenarios not yet evaluated
3. **Only starter path tested** — Advanced path (rules, hooks, agents, skills) not evaluated
4. **Single-run per scenario** — Multi-run averaging not yet performed (need 3-5 runs for variance measurement)
5. **Self-eval bias** — Same LLM generated and evaluated, which may inflate scores

## Takeaways

- Phase 2.5S pre-generation scan is the most impactful template improvement — it prevents the entire category of "hallucinated reference" bugs
- The eval infrastructure (scenarios, rubrics, result logs, scripts) works end-to-end across 6 different language ecosystems
- Cross-framework parallel testing surfaces patterns (like the .gitignore issue) that single-scenario testing would miss
