---
title: "TaskFlow tests/ Conventions"
description: "Lazy-loaded conventions for the TaskFlow test directory"
---

# Test Conventions
- Mirror the `src/` directory structure
- Use factories in `tests/factories/` for test data — don't create objects inline
- Integration tests hit real PostgreSQL — no mocking the database
- Each test file manages its own transaction rollback via `tests/helpers/db.ts`
- Run a single test file with: `npm test -- tests/services/task-service.test.ts`
