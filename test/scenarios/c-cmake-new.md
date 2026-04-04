---
id: c-cmake-new
language: C
framework: CMake
state: new
phase: 1
priority: high
fixture: c-cmake
---

# C CMake — New Project

## Project Description
A new C project using CMake as the build system, with a basic source file and CMakeLists.txt.

## Fixture Contents
- CMakeLists.txt
- src/main.c
- include/

## /generate Evaluation Focus
- cmake/make build commands (`cmake -B build`, `cmake --build build`)
- C-specific patterns and guidance (memory safety warnings, null checks, buffer overflow prevention)
- include/ vs src/ directory structure convention
- Compiler flag recommendations (-Wall -Wextra -Werror)

## /audit Evaluation Focus
- Build command detection (cmake --build or make)
- No test framework assumption (C has no standard test runner)
- Correct identification as a C project (not C++)
