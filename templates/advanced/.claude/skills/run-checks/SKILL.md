---
name: "run-checks"
description: "Runs build, lint, and test checks in sequence with clear pass/fail reporting"
argument-hint: "[--fix]"
---

# Steps

## Step 1: Parse Arguments

Read `$ARGUMENTS`. If `--fix` is present, lint will run with auto-fix enabled.

## Step 2: Build

Run `npm run build` to verify TypeScript compiles without errors.
If the build fails, report the errors and stop — do not proceed to lint or test.

## Step 3: Lint

Run `npm run lint` (or `npm run lint -- --fix` if `--fix` was requested).
Report any remaining warnings or errors.

## Step 4: Test

Run `npm test` to execute the full test suite.
Report any failures with test names and error messages.

## Step 5: Summary

Print a summary table:

| Check | Status |
| ----- | ------ |
| Build | pass / fail |
| Lint  | pass / fail (N warnings) |
| Test  | pass / fail (N/M passed) |

If all checks pass, confirm the project is ready for commit.
If any check fails, suggest the most likely fix based on the error output.
