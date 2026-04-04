---
id: rust-cli-existing
language: Rust
framework: clap
state: existing
phase: 1
priority: medium
fixture: rust-cli
---

# Rust CLI — Existing Project

## Project Description
An existing Rust CLI application with clap, featuring an established command module structure and multiple subcommands.

## Fixture Contents
- Cargo.toml
- src/main.rs
- src/commands/mod.rs
- src/commands/run.rs
- src/commands/init.rs

## /generate Evaluation Focus
- Detect existing module structure (src/commands/ submodules)
- Recognize existing command pattern and naming conventions
- Preserve Cargo.toml dependency organization
- Suggest additions that match existing code style

## /audit Evaluation Focus
- Test coverage awareness (unit tests in modules, integration tests in tests/)
- Project complexity recognition from module depth
- Appropriate suggestions for an established Rust codebase
