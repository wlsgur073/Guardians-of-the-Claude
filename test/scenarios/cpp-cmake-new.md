---
id: cpp-cmake-new
language: C++
framework: CMake
state: new
phase: 1
priority: high
fixture: cpp-cmake
---

# C++ CMake — New Project

## Project Description
A new C++ project using CMake with C++17 standard, featuring a basic source file with modern C++ patterns.

## Fixture Contents
- CMakeLists.txt (C++17, CXX_STANDARD)
- src/main.cpp (uses App class)
- src/app.cpp (App class implementation with namespace)
- include/app.h (App class declaration, std::string)

## /generate Evaluation Focus
- cmake build commands (`cmake -B build`, `cmake --build build`)
- C++ specific guidance (namespaces, smart pointers, RAII conventions)
- Header/source split conventions (.hpp/.cpp or .h/.cpp)
- CXX_STANDARD 17 awareness in CMakeLists.txt

## /audit Evaluation Focus
- CXX_STANDARD detection in CMakeLists.txt
- Build command recognition (cmake --build)
- C++ specific suggestions distinct from C (namespace usage, modern C++ idioms, RAII)
- Differentiation from C projects (templates, classes, STL usage)
