---
title: "TaskFlow CLAUDE.md (Advanced)"
description: "Example root CLAUDE.md for a Node.js/Express REST API project"
version: 1.1.0
---

<!--
  EXAMPLE STACK NOTE (visible in source, hidden in GitHub render)

  This template illustrates TaskFlow implemented with Node.js + Express +
  TypeScript + PostgreSQL. TaskFlow is a fictional reference project; the
  Node/Express stack is one concrete illustration, not a committed default.

  Read this for section structure and patterns. For your actual stack,
  run `/guardians-of-the-claude:create` — Claude detects your manifests
  and generates equivalent commands.

  See templates/README.md for the full convention.
-->

# Project Overview

TaskFlow is a REST API for task management, built with Node.js and Express.
PostgreSQL for persistence, Redis for session caching.

## Build & Run

npm install
npm run dev          # starts dev server on :3000 with hot reload
npm run build        # compiles TypeScript to dist/
npm run lint         # runs ESLint across the project

## Testing

npm test             # runs the full Jest test suite
npm run test:watch   # watch mode for development
npm run test:cov     # runs tests with coverage report

Tests require a running PostgreSQL instance (see docker-compose.yml).
Run `docker compose up -d` before running tests.

## Code Style & Conventions

- TypeScript strict mode, 2-space indentation
- Use named exports, not default exports
- Error types extend AppError in src/errors/
- Database queries go in src/repos/, never in route handlers
- All async route handlers must use the asyncHandler wrapper

## Development Approach

- When a request is vague or ambiguous, do not start implementing immediately
- First, critically analyze the request: identify assumptions, missing context, and possible interpretations
- Present your analysis and ask targeted clarifying questions before writing code
- After clarifying, outline your approach briefly and get confirmation before proceeding

## Workflow

- Branch naming: `feat/`, `fix/`, `chore/` prefixes
- Commit messages: conventional commits format
- Run full test suite before pushing: `npm test && npm run lint`
- All PRs require passing CI and one review approval

## Project Structure

- src/api/         → Express route handlers and middleware
- src/models/      → TypeScript interfaces and Zod validation schemas
- src/repos/       → Database access layer (one file per entity)
- src/services/    → Business logic (called by handlers, calls repos)
- src/errors/      → Custom error types extending AppError
- tests/           → Mirrors src/ structure
- db/migrations/   → SQL migration files (run with npm run migrate)
- .claude/rules/   → Detailed guidelines (code style, architecture, testing, workflow)

## Available Skills

| Skill | Purpose |
| ----- | ------- |
| `/add-endpoint` | Scaffold new API endpoint with handler, service, and tests |
| `/run-checks` | Run build, lint, and test suite in sequence |

## Available Agents

| Agent | Model | Role |
| ----- | ----- | ---- |
| `backend-developer` | sonnet | API implementation, services, database access |
| `security-reviewer` | opus | Vulnerability analysis (read-only) |
| `test-writer` | haiku | Test generation following project conventions |

## Important Context

- Auth uses JWT with refresh tokens stored in Redis
- All API responses follow the envelope format in src/api/response.ts
- Rate limiting is configured per-route in src/api/middleware/rateLimit.ts
- Environment variables are validated at startup via src/config.ts

## References

@docs/architecture.md
@docs/api-conventions.md
@README.md
