---
title: "TaskFlow Architecture Rules"
description: "Layer structure and dependency direction for the TaskFlow project"
---

# Architecture

## Layer Structure

Top to bottom:

1. **API Handlers** (`src/api/`) -- HTTP request/response, input validation
2. **Services** (`src/services/`) -- Business logic, orchestration
3. **Repositories** (`src/repos/`) -- Database access, SQL queries
4. **Models** (`src/models/`) -- Zod schemas, TypeScript interfaces

## Dependency Direction

- Handlers call Services -- never Repositories or Models directly
- Services call Repositories -- never access the database directly
- Repositories use Models for type safety
- No circular dependencies between layers
- Shared utilities in `src/utils/` may be imported by any layer

## Module Boundaries

- Each entity (Task, User, Comment) has its own file in each layer
- Cross-entity calls go through Services, not direct Repository access
- The `src/errors/` directory is shared infrastructure -- any layer may import from it
