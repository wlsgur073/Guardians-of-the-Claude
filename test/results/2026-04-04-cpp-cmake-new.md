---
date: 2026-04-04
scenario: cpp-cmake-new
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

# cpp-cmake-new -- /generate Evaluation (2026-04-04)

## Summary

1 run completed. Average 5.0 (excellent). All five dimensions scored maximum. The generation correctly identified the project as C++20 (not C), applied Phase 2.5S scanning to detect namespaces, classes, and modern C++ idioms, avoided hallucinating test commands, and produced output clearly distinct from the c-cmake-new (C language) scenario.

## Run Details

### Run 1

**Scores:** Accuracy 5 | Customization 5 | Completeness 5 | Conciseness 5 | BP 5

**Observations:**
- CMake commands exactly correct: `cmake -B build` for configure, `cmake --build build` for build, `./build/myapp` for run — target name extracted from `project(myapp CXX)` in CMakeLists.txt
- Correctly identifies C++20 standard from `CMAKE_CXX_STANDARD 20` and `CMAKE_CXX_STANDARD_REQUIRED ON` — does not downgrade to C or generic C++
- References concrete C++ project details: `myapp::App` class, `myapp` namespace, `explicit` constructor, `std::move` ownership transfer, `const` member functions — these are C++-specific idioms that clearly differentiate from a C project
- Code style section derives conventions from actual code: namespace usage pattern, `include/`/`src/` separation, include guard style (`#ifndef`/`#define`/`#endif`), `explicit` and `const` correctness
- Testing section correctly handles absence — states "No test framework is currently configured" and suggests C++ frameworks (Google Test, Catch2) rather than C frameworks (Unity, Check, Criterion)
- All 6 starter sections present: Project Overview, Build & Run, Testing, Code Style & Conventions, Development Approach (with all 4 required rules), Important Context
- 38 lines — well under the 200-line limit with no filler or redundancy
- Does NOT reference `tests/`, `lib/`, `build/`, or any non-existent directory — only `src/` and `include/` which actually exist
- Does NOT suggest `ctest`, `make test`, `clang-tidy`, or any test/lint commands that don't exist in the project
- settings.json correctly allows build and run commands (no test/lint since none exist) and denies .env reads
- .gitignore created with `.claude/settings.local.json` as required (file did not previously exist)
- Project overview mentions `src/main.cpp` as entry point with `myapp::App` instantiation — grounded in actual `main.cpp` content

## Cross-Run Patterns

(Single run — cross-run analysis requires 2+ additional runs)

## Improvements Identified

- [ ] Could add `build/` to `.gitignore` as a CMake out-of-source build directory that should not be committed
- [ ] Could mention `cmake -B build -DCMAKE_BUILD_TYPE=Debug` as a common development variant in Build & Run
- [ ] Could note `CMAKE_CXX_STANDARD_REQUIRED ON` in code style to emphasize the standard is enforced, not optional

## LLM Context Note

> For C++20 projects with CMake and no test framework, the critical differentiator from C projects is recognizing C++-specific language features: namespaces, classes, `std::string`, `std::move`, `explicit`, `const` member functions. Phase 2.5S scanning must read source files (not just CMakeLists.txt) to detect these patterns. The `project(myapp CXX)` directive confirms C++ but the code style section should derive its conventions from actual idioms found in the source, not generic C++ advice. Test framework suggestions must be C++-appropriate (Google Test, Catch2) rather than C-appropriate (Unity, Check). The Testing section SKIP handling remains the key differentiator — acknowledge absence rather than assume CTest is available.

## Comparison with Previous Eval

First evaluation — no previous data. However, this scenario is a direct companion to c-cmake-new (also scored 5.0). The key distinction: this project uses C++20 features (namespaces, classes, std::string, std::move, explicit, const) while c-cmake-new uses pure C (void params, printf, define macros). The generated outputs are appropriately differentiated.
