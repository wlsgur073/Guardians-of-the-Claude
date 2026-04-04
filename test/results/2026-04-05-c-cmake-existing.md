---
date: 2026-04-05
scenario: c-cmake-existing
template_version: v2.3.0
skill: generate
run_count: 1
scores:
  accuracy: [5]
  customization: [5]
  completeness: [5]
  conciseness: [5]
  best_practices: [5]
average: 5.0
verdict: excellent
---

# c-cmake-existing -- /generate Evaluation (2026-04-05)

## Summary

1 run completed for an EXISTING C/CMake project (has `src/main.c`, `src/utils/helpers.c`, `include/config.h`, empty `tests/` directory, and `.gitignore` with `build/` -- but no Claude Code config). Average 5.0 (excellent). All five dimensions scored maximum. The generation correctly identified the existing project structure, noted the unlinked helpers.c, handled the empty tests/ directory factually, and appended to .gitignore without overwriting.

## Run Details

### Run 1

**Scores:** Accuracy 5 | Customization 5 | Completeness 5 | Conciseness 5 | BP 5

**Observations:**
- CMake commands exactly correct: `cmake -B build` for configure, `cmake --build build` for compile, `./build/myapp` for run -- target name `myapp` extracted from actual CMakeLists.txt `project(myapp C)`
- References all actual project files: `CMakeLists.txt` (CMake 3.16, project name), `src/main.c` (entry point with `int main(void)`), `include/config.h` (`APP_VERSION "0.1.0"`, include guard pattern), `src/utils/helpers.c` (stub file)
- Critical "existing project" detail: correctly identifies that `src/utils/helpers.c` exists but is NOT linked in CMakeLists.txt (only `src/main.c` in `add_executable`) -- this is a project-specific finding that requires reading both the source tree and the build file
- `tests/` directory acknowledged as existing but empty -- does NOT invent test files or assume a test framework, states factually "The `tests/` directory exists but is empty"
- Testing section handles absence correctly: "No test framework is currently configured" -- does NOT assume CTest, Unity, CMocka, Check, or Criterion
- No prescriptive suggestions anywhere -- no "consider adding", "you should", or tool recommendations
- `.gitignore` correctly appended `.claude/settings.local.json` on a new line without overwriting existing `build/` entry
- settings.json includes run command `Bash(./build/myapp)` in allow list -- addresses the improvement noted in the c-cmake-new eval
- Code Style section derives all conventions from actual code: `void` parameter lists (from `main.c`), include guard pattern (from `config.h`), header/source separation with `src/utils/` subdir (from actual structure), quoted vs angle bracket includes (from `main.c`)
- 37 lines -- well under 200-line limit with zero filler
- All 6 starter sections present with Development Approach containing all 4 required rules verbatim

## Cross-Run Patterns

(Single run -- cross-run analysis requires 2+ additional runs)

## Improvements Identified

- [ ] Could note that CMakeLists.txt does not set a C standard explicitly (`CMAKE_C_STANDARD`) -- relevant for developers adding C11/C17 features
- [ ] Could mention the `include_directories(include)` directive in CMakeLists.txt to explain why `#include "config.h"` works without a relative path
- [ ] settings.json could include `Bash(cmake -B build -DCMAKE_BUILD_TYPE=Debug)` as an alternative configuration command

## LLM Context Note

> For existing C/CMake projects, the Phase 2.5S scan produces two critical findings that differentiate from a "new" scenario: (1) detecting source files that exist in the tree but are NOT linked in CMakeLists.txt (like helpers.c), which should be noted in Important Context so Claude does not assume all .c files compile, and (2) detecting empty directories (like tests/) that signal developer intent without actual content -- these should be acknowledged factually without inventing contents. The .gitignore merge behavior (append, not overwrite) is also essential for existing projects.

## Comparison with Previous Eval

Previous eval (c-cmake-new, 2026-04-04) scored 5.0 average. This "existing" scenario also scores 5.0. The existing scenario adds complexity through the unlinked helpers.c, empty tests/ directory, and pre-existing .gitignore -- all handled correctly. One improvement from the c-cmake-new eval (including run command in settings.json allow list) was already addressed here.
