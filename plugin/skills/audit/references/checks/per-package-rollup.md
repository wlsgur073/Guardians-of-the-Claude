---
title: Per-Package Rollup Procedure
description: Per-subpackage score rollup procedure for /audit Phase 3.6 hook output. Defines coverage counters (4 fields), min/median/worst computation over scored_count, median even-count handling, worst tie semantics, n/a rendering when scored_count=0, and runtime invariants. No aggregate score (v2.13.0 contract).
version: 1.0.0
applies_to: audit-score-v4.1.0
---

# Per-Package Rollup Procedure

This document defines the rollup output emitted by /audit Phase 3.6 hook — a subpackage score rollup line summarizing min/median/worst across scored subpackages, plus coverage counters. The rollup is **computed on render** — no `min`, `median`, `worst` fields are persisted in `profile.json` (v2.13.0 contract: no aggregate score).

## §0. Scope

**Authority**: v2.13.0 per-package scoring contract (audit-score-v4.1.0) — no aggregate score; rollup is min/median/worst/counts + per-package score rows. Coverage counters ARE persisted (`subpackage_coverage` schema 1.2.0). Statistical aggregates (min/median/worst) are computed-on-render from `subpackages[].final_score`.

**Inputs**:
- `subpackages[]`: array of per-package score rows (from `per-package-scoring.md`)
- `subpackage_coverage`: 4 counters {package_roots_total, with_claude_md, without_claude_md, scored_count}

**Outputs**:
- Persisted: `subpackage_coverage` 4 fields
- Rendered (terminal output, NOT persisted): min, median, worst, K (unscored), counts

## §1. Coverage Counters (persisted in subpackage_coverage)

- **`package_roots_total`**: count of distinct paths in `monorepo_detection.package_roots_for_scoring[]` BEFORE coverage filtering. Includes subpackages with and without CLAUDE.md.
- **`with_claude_md`**: count of subpackages where `<package_root>/CLAUDE.md` exists (independent of whether scoring succeeded).
- **`without_claude_md`**: count of subpackages where `<package_root>/CLAUDE.md` does NOT exist.
- **`scored_count`**: count of entries in `subpackages[]`. Equals number of successfully scored subpackages.

### §1.1 Runtime Invariants

```
package_roots_total = with_claude_md + without_claude_md
0 ≤ scored_count ≤ with_claude_md
```

The strict inequality `scored_count < with_claude_md` indicates degraded scoring (parse errors / LAV failures per `per-package-scoring.md` §7).

## §2. Min / Median / Worst Computation (over scored_count subset)

Computed only over `subpackages[]` entries (i.e., scored subpackages). The cardinality is `scored_count` per §1.

### §2.1 Min

`min = lowest final_score in subpackages[]`. When `scored_count == 0`, `min = n/a`.

### §2.2 Median

For `scored_count > 0`, compute median of `final_score` values:
- **Odd count**: middle value
- **Even count**: **average** of two middle values. Schema permits float (`final_score: number`), so `(60 + 71) / 2 = 65.5` is valid.

When `scored_count == 0`, `median = n/a`.

### §2.3 Worst

`worst = path(s) at the min final_score, tie-sorted ascending by repo-relative path, render first N with tie count`.

- If single subpackage at min: `worst = "<that path>"` (single path)
- If multiple subpackages at min (tie): `worst = "<first N tie-sorted paths> (and K-N more tied)"` where N is a small render limit (suggest N=3) and K is total tie count.
  - Example (5 subpackages tied at `final_score=42`, sorted ascending): `worst = "packages/api, packages/billing, packages/web (and 2 more tied)"` (N=3, K=5, K-N=2).
- When `scored_count == 0`: `worst = n/a`.

## §3. n/a Rendering When scored_count == 0

When `scored_count == 0` (e.g., monorepo with subpackages but none have CLAUDE.md, or all parse errors):

- min = n/a
- median = n/a
- worst = n/a

Coverage counters still rendered. Two example scenarios for `scored_count == 0` (rendered shape per `output-format.md`):

- **Parse-error scenario** (with_claude_md=2, scored_count=0):
  ```
  Subpackage Score Rollup
    min=n/a, median=n/a, worst=n/a (0 scored, 0 without CLAUDE.md, 2 unscored)
  ```
  Both subpackages had CLAUDE.md but failed to parse.

- **No-CLAUDE.md scenario** (with_claude_md=0, scored_count=0):
  ```
  Subpackage Score Rollup
    min=n/a, median=n/a, worst=n/a (0 scored, 2 without CLAUDE.md, 0 unscored)
  ```
  Subpackages discovered via workspace declaration but none have CLAUDE.md yet.

The abstract rollup line template (see `output-format.md` Rollup Summary Line for full rendering rules):
```
Subpackage Score Rollup
  min={X}, median={Y}, worst={path(s)} ({N} scored, {M} without CLAUDE.md, {K} unscored)
```
where `M = subpackage_coverage.without_claude_md` and `K = with_claude_md - scored_count`.

## §4. No Persistence

`min`, `median`, `worst`, K (unscored = with_claude_md - scored_count) are **NOT** persisted in `profile.json`. They are computed on each terminal render from `subpackages[]` + `subpackage_coverage`. Schema 1.2.0 `subpackage_coverage` has only the 4 counter fields — adding statistical aggregates would require schema bump (out of scope for v2.13.0).

Downstream tools (e.g., delta-comparison) should recompute from `subpackages[].final_score`.
