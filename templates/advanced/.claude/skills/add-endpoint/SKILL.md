---
name: "add-endpoint"
description: "Scaffolds a new REST API endpoint for TaskFlow with handler, service, repository, tests, and Zod schemas"
---

# Steps

## Step 1: Gather Information

Ask the user:
- What is the resource name? (e.g., "comment")
- What CRUD operations are needed? (e.g., "create, read, list, delete")
- Does it belong to an existing entity? (e.g., "tasks" for task comments)

## Step 2: Validate

- Confirm the resource does not already exist in `src/api/`
- Check that the parent entity exists if this is a nested resource
- Verify the test suite passes before making changes (`npm test`)

## Step 3: Execute

Create the following files following existing patterns:

1. `src/models/<resource>.ts` -- Zod schemas and TypeScript types
2. `src/repos/<resource>-repo.ts` -- Repository class with database queries
3. `src/services/<resource>-service.ts` -- Service class with business logic
4. `src/api/<resource>.ts` -- Route handler using asyncHandler wrapper
5. `tests/services/<resource>-service.test.ts` -- Service unit tests
6. `tests/api/<resource>.test.ts` -- API integration tests with Supertest

Register the new routes in `src/api/index.ts`.

## Step 4: Verify

- Run `npm run build` to confirm TypeScript compiles
- Run `npm test` to confirm all tests pass
- Verify the new routes are registered in `src/api/index.ts`
