---
title: "TaskFlow src/ Conventions"
description: "Lazy-loaded conventions for the TaskFlow source directory"
---

# src/ Conventions
- Business logic lives in `services/`, not in API handlers
- All database access goes through repository classes in `repos/`
- Never import directly from `tests/`
- Each service class handles one entity (e.g., `TaskService`, `UserService`)
- Shared utilities go in `src/utils/` — keep them pure functions
