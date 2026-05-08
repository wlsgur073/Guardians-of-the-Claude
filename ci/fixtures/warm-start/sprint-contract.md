---
title: "sprint-contract"
description: "Active sprint scope for warm-start fixture"
version: "1.0.0"
---

# Sprint Contract

## In Scope

- **Vitest baseline** — finalize the Vitest unit test suite for `src/lib/` modules and wire it into the pre-merge check.
- **Playwright smoke** — author one Playwright smoke flow covering the `/login` and `/dashboard` happy path.
- **Rule split** — split CLAUDE.md guidance into `.claude/rules/` files so the root document stays under 80 lines.

## Out of Scope

- Tailwind theme overhaul.
- ESLint rule churn beyond the existing flat config.
