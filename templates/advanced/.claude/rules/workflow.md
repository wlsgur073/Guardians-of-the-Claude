---
title: "TaskFlow Development Workflow"
description: "Pre-development checklist and review gates for the TaskFlow project"
---

# Workflow

## Pre-Development Checklist

Before starting any implementation task:

1. Read the relevant sections of CLAUDE.md
2. Review existing tests for the area you will modify
3. Check `docs/api-conventions.md` if working on API endpoints
4. Run `npm test` to confirm the test suite passes before making changes

## Review Gates

Before considering work complete:

- All tests pass (`npm test`)
- Lint has zero warnings (`npm run lint`)
- TypeScript compiles without errors (`npm run build`)
- New code follows the layer structure in `architecture.md`
- API endpoints include JSDoc tags: `@route`, `@method`, `@auth`
