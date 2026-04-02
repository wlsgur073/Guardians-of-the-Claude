---
title: "TaskFlow CLAUDE.md (Starter)"
description: "Minimal 6-section example for a Node.js/Express REST API project"
version: 2.4.0
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
- Database queries go in src/repos/, never in route handlers
- All async route handlers must use the asyncHandler wrapper

## Development Approach

- When a request is vague or ambiguous, do not start implementing immediately
- First, critically analyze the request: identify assumptions, missing context, and possible interpretations
- Present your analysis and ask targeted clarifying questions before writing code
- After clarifying, outline your approach briefly and get confirmation before proceeding

## Important Context

- Auth uses JWT with refresh tokens stored in Redis
- All API responses follow the envelope format in src/api/response.ts
- Rate limiting is configured per-route in src/api/middleware/rateLimit.ts
- Environment variables are validated at startup via src/config.ts
