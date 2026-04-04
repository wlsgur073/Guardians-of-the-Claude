---
id: javascript-nextjs-existing
language: JS/TS
framework: Next.js
state: existing
phase: 1
priority: high
fixture: javascript-nextjs
---

# JS/TS Next.js — Existing Project

## Project Description
An existing Next.js 14+ App Router project with TypeScript, featuring established component library and utility modules.

## Fixture Contents
- package.json
- tsconfig.json
- next.config.js
- src/app/layout.tsx
- src/app/page.tsx
- src/components/
- src/lib/

## /generate Evaluation Focus
- Detect existing component patterns and naming conventions
- Merge configuration rather than overwrite (e.g., next.config.js)
- Recognize established directory structure (components/, lib/)
- Preserve existing TypeScript strictness settings

## /audit Evaluation Focus
- Recognize Next.js project maturity from directory depth
- Identify existing test setup or lack thereof
- Appropriate suggestions for an established codebase (not starter-level advice)
