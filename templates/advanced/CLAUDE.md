---
title: "TaskFlow CLAUDE.md"
description: "Example root CLAUDE.md for a Node.js/Express REST API project"
date: "2026-03-18"
---

# Project Overview

TaskFlow is a REST API for task management, built with Node.js and Express.
PostgreSQL for persistence, Redis for session caching.

## Build & Run

npm install
npm run dev          # starts dev server on :3000 with hot reload
npm run build        # compiles TypeScript to dist/

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
- Database queries go in src/repositories/, never in route handlers
- All async route handlers must use the asyncHandler wrapper

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

## Important Context

- Auth uses JWT with refresh tokens stored in Redis
- All API responses follow the envelope format in src/api/response.ts
- Rate limiting is configured per-route in src/api/middleware/rateLimit.ts
- Environment variables are validated at startup via src/config.ts

## References

@docs/architecture.md
@docs/api-conventions.md
@README.md
