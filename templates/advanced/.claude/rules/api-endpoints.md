---
title: "TaskFlow API Endpoint Rules"
description: "Rules that apply only when working with API handler files"
paths:
  - "src/api/**/*.ts"
---

# API Endpoint Rules

- All endpoints must validate input with Zod schemas from `src/models/`
- Use the `asyncHandler` wrapper for all route handlers:
  ```typescript
  router.get('/tasks', asyncHandler(async (req, res) => { ... }))
  ```
- Return responses using `sendSuccess()` or `sendError()` from `src/api/response.ts`
- Never call repository methods directly from handlers — go through services
- Include rate limiting for public endpoints via `src/api/middleware/rateLimit.ts`
- All endpoints must be documented with JSDoc tags: `@route`, `@method`, `@auth`
