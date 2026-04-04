# Parallel Eval Batch 2 — 6 Additional Scenarios

**Date:** 2026-04-05 00:05
**Action:** Second parallel eval cycle — cpp, existing states, Django, Express, Go CLI
**Template version:** v2.3.0 with Phase 2.5S improvements

---

## Results Summary (Batch 2)

| Scenario | Avg Score | Verdict | Key Finding |
|----------|-----------|---------|-------------|
| cpp-cmake-new | 5.0 | excellent | C++20 correctly distinguished from C |
| python-fastapi-existing | 4.8 | excellent | Conciseness -1: prescriptive "add ruff" advice |
| javascript-nextjs-existing | 4.8 | excellent | Conciseness -1: redundant ESLint/CommonJS notes |
| python-django-new | 5.0 | excellent | SECRET_KEY security issue detected |
| javascript-express-new | 4.8 | excellent | Completeness -1: missing linter/test-dir absence note |
| go-cli-new | 4.6 | excellent | Customization -1, Completeness -1; result format incorrect |

## Cumulative Results (Batch 1 + 2)

| Scenario | Score | State |
|----------|-------|-------|
| python-fastapi-new (pre) | 4.0 | new |
| python-fastapi-new (post) | 5.0 | new |
| javascript-nextjs-new | 5.0 | new |
| rust-cli-new | 5.0 | new |
| java-springboot-new | 5.0 | new |
| c-cmake-new | 5.0 | new |
| go-web-new | 5.0 | new |
| cpp-cmake-new | 5.0 | new |
| python-django-new | 5.0 | new |
| python-fastapi-existing | 4.8 | existing |
| javascript-nextjs-existing | 4.8 | existing |
| javascript-express-new | 4.8 | new |
| go-cli-new | 4.6 | new |

**Average across all post-improvement runs:** 4.88

---

## Cross-Scenario Patterns Found

### Pattern 1: "existing" state triggers conciseness issues

Both existing-state scenarios (fastapi-existing, nextjs-existing) lost points on Conciseness. The cause: when the project has more files/directories, the generator adds more context, which introduces low-value notes (prescriptive tool suggestions, redundant config observations).

**Affected:** python-fastapi-existing (Conciseness 4), javascript-nextjs-existing (Conciseness 4)
**Root cause:** No guidance in best-practices.md about conciseness thresholds for existing projects
**Recommended fix:** Add rule: "For existing projects, only document what the project IS, not what it SHOULD add. Tool suggestions belong in /audit, not in generated CLAUDE.md."

### Pattern 2: Missing-resource documentation inconsistency

express-new lost a Completeness point for not explicitly noting the absence of a linter and test directory. Meanwhile, c-cmake-new and java-springboot-new correctly noted missing test frameworks. The template doesn't clearly specify when absences should be documented vs silently skipped.

**Recommended fix:** Add to starter.md: "If a standard tool is absent (test runner, linter, formatter), note it in Important Context so Claude doesn't assume it exists."

### Pattern 3: Result format deviation (go-cli-new)

One agent wrote the result in audit-style format (score/grade/gate) instead of rubric format (dimensions/average/verdict). This makes automated parsing inconsistent.

**Root cause:** The agent prompt referenced "rubric" but the agent also simulated /audit and mixed the formats.
**Impact:** Low — one-off deviation, manually recoverable.
**Lesson:** Agent prompts should explicitly forbid mixing rubric eval with /audit simulation.

### Pattern 4: Agent working directory safety

The go-cli-new agent accidentally overwrote the repo's CLAUDE.md when using the Write tool. It self-corrected with git checkout, but this is a safety concern for parallel agent execution.

**Recommended mitigation:** Use `isolation: "worktree"` for eval agents, or ensure agents only write to /tmp paths.

---

## Remaining Phase 1 Scenarios

| Scenario | Status |
|----------|--------|
| rust-cli-existing | Not tested |
| java-springboot-existing | Not tested |
| c-cmake-existing | Not tested |
| monorepo-new | Not tested |

## Next Steps

1. Fix Pattern 1: Add conciseness guidance for existing projects to best-practices.md
2. Fix Pattern 2: Add absent-tool documentation rule to starter.md
3. Run remaining 4 Phase 1 scenarios (rust-cli-existing, java-springboot-existing, c-cmake-existing, monorepo-new)
4. Use `isolation: "worktree"` or /tmp-only writes for safety
