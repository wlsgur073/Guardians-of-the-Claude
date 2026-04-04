---
id: monorepo-new
language: Multi
framework: npm workspaces
state: new
phase: 1
priority: medium
fixture: monorepo
---

# Multi-Language Monorepo — New Project

## Project Description
A monorepo using npm workspaces containing a Next.js frontend and an Express backend as separate packages.

## Fixture Contents
- package.json (root, workspaces: ["packages/*"])
- packages/web/package.json (Next.js)
- packages/web/src/app/page.tsx
- packages/api/package.json (Express)
- packages/api/src/index.js

## /generate Evaluation Focus
- Root-level vs package-level command distinction
- npm workspaces awareness (workspace scripts, dependencies)
- Shared configuration vs per-package configuration
- Multi-package project structure handling (packages/web, packages/api)
- Graceful handling of different tech stacks in a single repo

## /audit Evaluation Focus
- Monorepo detection from workspaces configuration
- Per-package test and build command identification
- Cross-package consistency checks (shared linting, TypeScript config)
- Correct identification of each package's framework (Next.js in web, Express in api)
