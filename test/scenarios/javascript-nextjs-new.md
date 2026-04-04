---
id: javascript-nextjs-new
language: JS/TS
framework: Next.js
state: new
phase: 1
priority: high
fixture: javascript-nextjs
---

# JS/TS Next.js — New Project

## Project Description
A new Next.js 14+ project using the App Router with TypeScript, created via create-next-app.

## Fixture Contents
- package.json
- tsconfig.json
- next.config.js
- src/app/layout.tsx
- src/app/page.tsx

## /generate Evaluation Focus
- next dev/build/start commands from package.json scripts
- TypeScript awareness (tsconfig.json, .tsx files)
- App Router structure recognition (src/app/ directory convention)
- Next.js-specific patterns (server components, metadata API)

## /audit Evaluation Focus
- Build command detection (next build or npm run build)
- TypeScript configuration recognition
- Correct identification of Next.js App Router (not Pages Router)
