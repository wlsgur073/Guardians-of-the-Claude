---
id: c-cmake-existing
language: C
framework: CMake
state: existing
phase: 1
priority: medium
fixture: c-cmake
---

# C CMake — Existing Project

## Project Description
An existing C project with CMake, featuring organized source files with utility modules and a test directory.

## Fixture Contents
- CMakeLists.txt
- src/main.c
- src/utils/string_utils.c
- src/utils/string_utils.h
- include/
- tests/test_string_utils.c

## /generate Evaluation Focus
- Detect existing header/source file organization
- Recognize src/utils/ module structure
- Preserve existing CMakeLists.txt build targets
- Suggest additions consistent with existing naming conventions

## /audit Evaluation Focus
- Test framework detection (CTest integration, Unity, Check, or custom)
- Recognize project complexity from source organization
- Appropriate suggestions for an established C codebase
