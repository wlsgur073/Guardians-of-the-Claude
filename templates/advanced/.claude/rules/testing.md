---
title: "TaskFlow Testing Rules"
description: "Jest testing conventions for the TaskFlow project"
---

# Testing Conventions

## Framework
- Jest with ts-jest for unit and integration tests
- Supertest for HTTP endpoint tests

## Structure
- Mirror the `src/` directory: `tests/services/` tests `src/services/`
- Use `describe` blocks grouped by method or behavior
- Test file naming: `<module>.test.ts`

## Data
- Use factories in `tests/factories/` for test data — never create objects inline
- Each factory returns a valid entity by default; override only what the test needs
- Example: `createUser({ email: 'test@example.com' })`

## Database
- Integration tests hit real PostgreSQL — do not mock the database
- Each test file gets a fresh transaction that rolls back after the suite
- Use `tests/helpers/db.ts` for setup and teardown

## Coverage
- Minimum 80% line coverage for src/services/
- All error paths must have at least one test
- Run `npm run test:cov` to check
