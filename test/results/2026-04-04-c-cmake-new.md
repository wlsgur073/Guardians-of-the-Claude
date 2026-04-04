---
date: 2026-04-04
scenario: c-cmake-new
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

# c-cmake-new -- /generate Evaluation (2026-04-04)

## Summary

1 run completed. Average 5.0 (excellent). All five dimensions scored maximum. The generation correctly applied Phase 2.5S scanning to identify a minimal C/CMake project with no test framework, avoided hallucinating test commands or non-existent directories, and included concrete details from the actual source code.

## Run Details

### Run 1

**Scores:** Accuracy 5 | Customization 5 | Completeness 5 | Conciseness 5 | BP 5

**Observations:**
- CMake commands exactly correct: `cmake -B build` for configure, `cmake --build build` for build, `./build/myapp` for run — matching the project target name from CMakeLists.txt
- References all three actual project files: `CMakeLists.txt` (project name `myapp`, CMake 3.16), `src/main.c` (entry point), `include/config.h` (`APP_VERSION`, include guard pattern)
- References concrete source detail: `APP_VERSION "0.1.0"` define in `config.h`, `int main(void)` signature, `printf("myapp %s\n", APP_VERSION)` as entry behavior
- All 6 starter sections present: Project Overview, Build & Run, Testing, Code Style & Conventions, Development Approach (with all 4 required rules), Important Context
- Testing section correctly handles absence — states "No test framework is currently configured" and prompts to update when one is added; does NOT assume CTest, Unity, Check, or any framework
- 42 lines — well under the 200-line limit with no filler or redundancy
- Does NOT reference `tests/`, `lib/`, `build/`, or any non-existent directory — only `src/` and `include/` which actually exist
- Does NOT suggest `ctest`, `make test`, or any test/lint commands that don't exist in the project
- settings.json correctly allows only build commands (no test/lint since none exist) and denies .env reads
- .gitignore includes `.claude/settings.local.json` as required by starter template
- Code style section derives conventions from actual code: `void` in empty params (from `main.c`), include guard pattern (from `config.h`), `include/` and `src/` separation (from actual structure)

## Cross-Run Patterns

(Single run — cross-run analysis requires 2+ additional runs)

## Improvements Identified

- [ ] Could add `build/` to `.gitignore` as a CMake out-of-source build directory that should not be committed
- [ ] Could mention `cmake -B build -DCMAKE_BUILD_TYPE=Debug` as a common development variant
- [ ] settings.json could pre-allow `Bash(./build/myapp)` for convenience since it's the run command

## LLM Context Note

> For C projects with CMake and no test framework, /generate performs well when Phase 2.5S scanning is applied. The critical success factors: (1) recognizing the absence of any test infrastructure and NOT inventing test commands (no CTest, Unity, Check, or Criterion), (2) extracting the project target name from CMakeLists.txt to construct the correct run command, (3) reading source files to identify concrete details like APP_VERSION and the include guard pattern. The Testing section SKIP handling (acknowledging absence rather than assuming) is the key differentiator for C projects.

## Comparison with Previous Eval

First evaluation — no previous data.
