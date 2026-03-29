---
title: "TaskFlow Code Style Rules"
description: "TypeScript conventions for the TaskFlow project"
---

# Code Style

## Naming
- Variables and functions: camelCase
- Classes and interfaces: PascalCase
- Constants: UPPER_SNAKE_CASE
- File names: kebab-case (e.g., `user-service.ts`)
- Database columns: snake_case

## Formatting
- 2-space indentation
- Max line length: 100 characters
- Trailing commas in multiline arrays and objects
- Semicolons required

## Imports
- Group imports: Node builtins, external packages, internal modules
- Use named exports: `export { UserService }` not `export default`
- Use path aliases: `@/services/user-service` not `../../../services/user-service`

## Types
- Prefer interfaces over type aliases for object shapes
- Use Zod schemas as the source of truth; derive TypeScript types with `z.infer`
- Never use `any` — use `unknown` and narrow with type guards
