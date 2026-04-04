---
id: go-cli-new
language: Go
framework: Cobra
state: new
phase: 1
priority: medium
fixture: go-cli
---

# Go CLI — New Project

## Project Description
A new Go CLI tool using the Cobra library for command structure, with Go modules and a basic root command.

## Fixture Contents
- go.mod
- go.sum
- main.go
- cmd/root.go

## /generate Evaluation Focus
- go build/install commands
- Cobra command structure awareness (cmd/ directory convention)
- Go module dependency management (go mod tidy)
- CLI-specific patterns (flags, arguments, help text)

## /audit Evaluation Focus
- go test detection as the test command
- CLI-specific patterns recognition (command hierarchy, flag handling)
- Cobra project structure awareness (cmd/ directory)
