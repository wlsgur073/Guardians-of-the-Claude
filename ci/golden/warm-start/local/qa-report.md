---
title: "qa-report"
description: "Post-audit transparency artifact for warm-start at 2026-04-14T00:00:00Z"
version: "1.0.0"
---

## Score Summary

| Final | Bucket | DS | SB | LAV_nonL5 | cap |
|---|---|---|---|---|---|
| 72.2 | Intermediate | 65.0 | 2 | 4 | 100 |

## LAV Item Rationale

| Item | Score | Evidence cited | Counterfactual to next band |
|---|---|---|---|
| L1 | 0 | `project_structure.key_directories` lists `src/app/`, `src/components/`, `src/lib/`; CLAUDE.md does not detail per-component responsibilities. | Score would reach +2 if CLAUDE.md cited a correctly-named directory or file path. |
| L2 | +2 | Vitest unit suite and Playwright e2e suite declared in `package.json` scripts; ESLint and Prettier configured. | — |
| L3 | +1 | Tailwind v4 + Turbopack + ESM module-system are noted as project-wide constraints. | Score would reach +3 if CLAUDE.md cited an H2/H3 section with ≤10 lines of project-specific patterns or gotchas. |
| L4 | 0 | Five sections present but the open `split-rules` recommendation indicates rule files would improve organization. | Score would reach +1 if CLAUDE.md cited a deduplicated bullet list or removed redundant section. |
| L5 | 0 | Density acceptable; the open `split-rules` recommendation suggests some guidance overlaps between CLAUDE.md and inline content. | Score would reach +1 if CLAUDE.md cited a deduplicated bullet list reducing prose-rule overlap. |
| L6 | +1 | Concrete commands include flags (`vitest run`, `playwright test --project=chromium`) and exact paths. | — |

## Bucket Rationale

The live classifier emitted Bucket = Intermediate and Final = 72.2. Profile signals match the Intermediate rubric path: CLAUDE.md length 120 lines (within 60-200), `rules_count` 2 (within 2-5), `hooks_count` 2 (within 1-2), `agents_count` 1 (≤1), `mcp_servers_count` 0 (≤1). No Outlier short-circuit triggered.

## Recommendations Linkage

- See `local/recommendations.json` for active recommendations.

## Sprint Contract Coverage

| In Scope item | LAV items aligned | Coverage |
|---|---|---|
| Vitest baseline | L1, L2, L6 | LAV evidence cites `src/lib/`, Vitest commands. |
| Playwright smoke | L2, L6 | LAV evidence cites Playwright commands. |
| Rule split | L4, L5 | LAV evidence cites `split-rules` and CLAUDE.md organization. |

(5/6 LAV items aligned)
