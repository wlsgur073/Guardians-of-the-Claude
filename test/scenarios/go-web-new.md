---
id: go-web-new
language: Go
framework: net/http
state: new
phase: 1
priority: high
fixture: go-web
---

# Go Web — New Project

## Project Description
A new Go web service using the net/http standard library for HTTP handling, with Go modules initialized.

## Fixture Contents
- go.mod
- main.go
- handlers/

## /generate Evaluation Focus
- go build/test/run commands
- Go module awareness (go.mod, module path)
- Handler structure and organization patterns
- Go-specific conventions (error handling, interface design)

## /audit Evaluation Focus
- go test detection as the test command
- Go-specific project layout recognition (cmd/, internal/, pkg/)
- Standard library usage patterns vs third-party dependencies
