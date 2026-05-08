---
title: "qa-report"
description: "Post-audit transparency artifact for monorepo at 2026-04-14T00:00:00Z"
version: "1.0.0"
---

## Score Summary

| Final | Bucket | DS | SB | LAV_nonL5 | cap |
|---|---|---|---|---|---|
| 28.5 | distributed_config | 25.0 | 0 | 7 | 100 |

## LAV Item Rationale

| Item | Score | Evidence cited | Counterfactual to next band |
|---|---|---|---|
| L1 | +2 | CLAUDE.md surfaces both packages via `pnpm --filter api` and `pnpm --filter web` workspace targets, consistent with `packages/*` resolved roots in profile. | — |
| L2 | +2 | `pnpm install`, `pnpm --filter api dev`, `pnpm --filter web dev` documented; package manager matches `pnpm` in profile. | — |
| L3 | +1 | "Important Context" warns against crossing package boundaries without updating dependencies — workspace-specific gotcha. | Score would reach +3 if CLAUDE.md cited an H2/H3 section with ≤10 lines of project-specific patterns or gotchas. |
| L4 | +1 | Five sections (Project Overview, Build & Run, Testing, Code Style & Conventions, Important Context) with consistent heading hierarchy. | — |
| L5 | +1 | 27 lines, no filler prose, no overlap with per-package CLAUDE.md content. | — |
| L6 | +1 | Filter commands include exact filter targets (`pnpm --filter api`, `pnpm --filter web`). | — |

## Bucket Rationale

The live classifier emitted Bucket = distributed_config and Final = 28.5. Profile signals satisfy the distributed_config rubric path: `project_structure.type` = monorepo, `monorepo_detection.detected` = true, `subpackage_coverage.with_claude_md` = 2 (≥2 required). Three of four supporting signals hold (workspace ratio 2/2 = 1.0 ≥ 0.5; root compactness 27 lines ≤ 150; verbose-prose-sparse-config exclusion) — Section 2.3 fails (mean L6 = 0) — above the 2-of-4 threshold.

## Recommendations Linkage

No active recommendations.
