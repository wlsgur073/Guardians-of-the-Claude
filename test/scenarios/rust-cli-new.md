---
id: rust-cli-new
language: Rust
framework: clap
state: new
phase: 1
priority: high
fixture: rust-cli
---

# Rust CLI — New Project

## Project Description
A new Rust CLI application using clap for argument parsing, initialized with cargo new.

## Fixture Contents
- Cargo.toml
- src/main.rs

## /generate Evaluation Focus
- cargo build/test/run commands
- Cargo.toml awareness (dependencies, edition, metadata)
- clippy lint command (`cargo clippy`)
- Rust project structure conventions (src/lib.rs, modules)

## /audit Evaluation Focus
- cargo test detection as the test command
- Rust-specific build command recognition (cargo build --release)
- clippy and rustfmt as recommended tooling
