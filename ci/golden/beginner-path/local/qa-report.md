---
title: "qa-report"
description: "Post-audit transparency artifact for beginner-path at 2026-04-14T00:00:00Z"
version: "1.0.0"
---

## Score Summary

| Final | Bucket | DS | SB | LAV_nonL5 | cap |
|---|---|---|---|---|---|
| 46.2 | Starter | 42.0 | 0 | 5 | 100 |

## LAV Item Rationale

| Item | Score | Evidence cited | Counterfactual to next band |
|---|---|---|---|
| L1 | 0 | CLAUDE.md describes a Next.js App Router scaffold but does not enumerate `src/` or `app/` directory layout. | Score would reach +2 if CLAUDE.md cited a correctly-named directory or file path. |
| L2 | +2 | `npm run dev`, `npm run build`, `npm start` documented under "Build & Run" with package.json scripts present. | — |
| L3 | +1 | "Important Context" notes the Starter scaffold posture and the `/audit` / `/secure` follow-up cadence. | Score would reach +3 if CLAUDE.md cited an H2/H3 section with ≤10 lines of project-specific patterns or gotchas. |
| L4 | +1 | Five top-level sections (Project Overview, Build & Run, Testing, Code Style & Conventions, Important Context) with consistent H2 hierarchy. | — |
| L5 | +1 | 29 lines, no filler prose, no duplicated guidance across CLAUDE.md and rule files. | — |
| L6 | +1 | Concrete commands include flags and entry points (`npm run dev`, `npm run build`, `npm start`). | — |

## Bucket Rationale

The live classifier emitted Bucket = Starter and Final = 46.2. Profile signals match the Starter rubric path: CLAUDE.md length 29 lines (within 20-80), `rules_count` 0, `hooks_count` 0, `agents_count` 0, `mcp_servers_count` 0. No Outlier short-circuit triggered (no meta-marketplace, lines well under 250).

## Recommendations Linkage

No active recommendations.
