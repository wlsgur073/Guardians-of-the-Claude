---
title: Per-Package Scoring Procedure
description: Per-subpackage CLAUDE.md scoring procedure for /audit Phase 3.6 hook. Defines mechanical T1+T2+T3 (package-rebased), LAV evaluation per-package with LAV/T3 boundary rule, Synergy Bonus from package-local T1.2/T1.3 + T2.1/T2.2 pairs, cap tier resolution, Final formula, and degraded state handling. Consumed when /audit iterates monorepo_detection.package_roots_for_scoring[].
version: 1.0.0
applies_to: audit-score-v4.1.0
---

# Per-Package Scoring Procedure

This document defines the per-subpackage CLAUDE.md scoring procedure invoked by /audit Phase 3.6. For each package root in `monorepo_detection.package_roots_for_scoring[]` (capped at scored=50), if the subpackage's `CLAUDE.md` exists and is parseable, this procedure produces one entry in `claude_code_configuration_state.claude_md.subpackages[]` with required fields `[path, claude_md_path, final_score (0-100), cap_tier (50|60|100), lav_breakdown (L1-L6)]`.

## §0. Scope

**Authority**: v2.13.0 per-package scoring contract (audit-score-v4.1.0). Three binding rules: (1) ALL L1-L6 axes evaluated package-local with NO root inheritance, (2) cap tier is per-package independent, (3) rollup carries no aggregate score (see `per-package-rollup.md`).

**Inputs**:
- `package_root`: repo-relative path from `monorepo_detection.package_roots_for_scoring[i]`
- `sub_claude_md_path`: `<package_root>/CLAUDE.md`
- Subpackage directory tree rooted at `package_root` (for mechanical T1/T2/T3 file lookups)

**Output (when sub_claude_md exists and parseable)**:
- One `subpackages[]` entry: `{path, claude_md_path, final_score, cap_tier, lav_breakdown, source_evidence_indices?}`

**Output (when sub_claude_md missing or unparseable)**:
- No `subpackages[]` entry. Coverage counters updated (see `per-package-rollup.md` §1). For unparseable case, `monorepo_detection.notes[]` entry with stable code (see §7 below).

## §1. Mechanical T1+T2+T3 (Package-Rebased)

The package root is treated as the project root for mechanical evaluation. Root state is NEVER inherited.

### §1.1 T1 Foundation (per-package)

Apply `t1-foundation.md` rules with `<package_root>` as the project root:

- **T1.1 CLAUDE.md existence**: PASS (subpackage CLAUDE.md existence is the precondition for entering Phase 3.6 procedure; this is always PASS for entries that reach §1.1).
- **T1.2 Test command**: search subpackage CLAUDE.md (i.e., `<package_root>/CLAUDE.md`) for test commands. If found and runnable against package-local manifests (e.g., `<package_root>/package.json`) → PASS. If not found and subpackage has application code → FAIL. If subpackage is documentation/config only → SKIP.
- **T1.3 Build command**: same package-rebased logic against subpackage CLAUDE.md + manifests.
- **T1.4 Project overview**: search subpackage CLAUDE.md first 20 lines for description.

### §1.2 T2 Protection (per-package)

Apply `t2-protection.md` rules with `<package_root>` as the project root:

- **T2.1 Sensitive file protection**: check `<package_root>/.claude/settings.json` deny patterns. If subpackage has no `.claude/settings.json` → all T2 items SKIP. Root `.claude/settings.json` is NEVER inherited.
- **T2.2 Security rules**: check `<package_root>/.claude/rules/security.md` or subpackage CLAUDE.md security keywords.
- **T2.3 Hook configuration quality**: check `<package_root>/.claude/settings.json` hooks section.

When all T2 items SKIP (typical case — subpackages rarely have own .claude/), DS falls back to T3 only per `scoring-model.md` L83-L85.

### §1.3 T3 Optimization (per-package)

Apply `t3-optimization.md` rules with `<package_root>` as the project root:

- **T3.1 Directory references**: extract paths from subpackage CLAUDE.md, check existence under `<package_root>/`.
- **T3.2 CLAUDE.md length**: count lines of subpackage CLAUDE.md.
- **T3.3 Command availability**: check subpackage CLAUDE.md commands against `<package_root>/package.json` etc.
- **T3.4-T3.7**: same package-rebased logic against `<package_root>/.claude/rules/`, `<package_root>/.claude/agents/`, `<package_root>/.mcp.json`, subpackage env-var files.

### §1.4 DS Computation (per-package)

After T1/T2/T3 evaluation:

```
T2_Score = sum(s_i × w_i) / sum(w_i)   for non-SKIP T2 items
T3_Score = sum(s_i × w_i) / sum(w_i)   for non-SKIP T3 items
DS = (T2_Score × 0.60 + T3_Score × 0.40) × 100

If T2 is all SKIP: DS = T3_Score × 100
If T3 is all SKIP: DS = T2_Score × 100
If both are all SKIP: DS = 0
```

This is identical to root DS formula (`scoring-model.md` L78-L85).

## §2. LAV/T3 Boundary Rule (per-package)

Apply `lav.md` L7-L15 boundary rule with subpackage context:

- If subpackage T3.1 detected missing directory (PARTIAL/FAIL) → subpackage L1 scores **0** for that issue. Subpackage L1 penalizes only structural inaccuracies beyond T3.1's mechanical scope.
- If subpackage T3.3 detected missing tool config (PARTIAL/FAIL) → subpackage L2 scores **0** for that issue.
- If subpackage T3.7 detected undocumented env vars (PARTIAL/FAIL) → subpackage L2 scores 0 (same axis).

**Critical**: T3 mechanical detection happens BEFORE LAV evaluation per `scoring-model.md` precedent. The boundary rule is applied per-subpackage independently. Root T3 detections do NOT suppress subpackage LAV (no root inheritance).

Mechanical and LAV layers are complementary per-package, not redundant.

## §3. LAV Evaluation (per-package)

Apply `lav.md` L23-L28 ranges and L34-L62 guidelines per subpackage. ALL six axes evaluated package-local using subpackage CLAUDE.md content + subpackage directory state. Root LAV is NEVER inherited.

### §3.1 Axis Application

| Axis | Range | Subpackage input | Note |
|---|---|---|---|
| L1 — Structure Accuracy | -3 / 0 / +2 | subpackage CLAUDE.md vs subpackage directory tree | Subject to §2 boundary rule (T3.1 paired) |
| L2 — Command Reliability | -2 / 0 / +2 | subpackage CLAUDE.md commands vs subpackage manifest/config | Subject to §2 boundary rule (T3.3 / T3.7 paired) |
| L3 — Patterns/Gotchas | 0 / +1 / +3 | subpackage CLAUDE.md project-specific gotchas | No boundary rule |
| L4 — Structural Quality | -1 / 0 / +1 | subpackage CLAUDE.md section organization | No boundary rule |
| L5 — Conciseness | -3 / 0 / +1 | subpackage CLAUDE.md content density (qualitative; NO size-based threshold) | Routed via cap tier (NOT in LAV_nonL5 sum) |
| L6 — Actionability | 0 / +1 | subpackage CLAUDE.md command/path concreteness | No boundary rule |

`LAV_nonL5 = L1 + L2 + L3 + L4 + L6` (range -6 to +9, excludes L5).

### §3.2 No Re-calibration for Short Subpackages

Subpackage CLAUDE.md is typically shorter than root (~30-50 lines vs ~100-200). L4/L5 guidelines remain qualitative per `lav.md` — no size-based threshold re-calibration. A short subpackage CLAUDE.md may earn +1 L5 if content is sparse but unique; +1 L4 if minimal but clear. This is consistent with root scoring and avoids re-spec burden.

## §4. Synergy Bonus per-package

SB is computed from package-local eligible item outcomes only. Two pairs (per `scoring-model.md` L143-L150):

### §4.1 Test command + Build command pair (T1.2/T1.3)

Uses package-local **T1.2/T1.3** semantics against the subpackage CLAUDE.md / package root.

- If subpackage T1.2 == PASS AND subpackage T1.3 == PASS → +2
- If either is SKIP/PARTIAL/MINIMAL/FAIL → 0

### §4.2 Sensitive file protection + Security rules pair (T2.1/T2.2)

Uses package-local **T2.1/T2.2** semantics against subpackage `.claude/settings.json` and security rules.

- If subpackage T2.1 == PASS AND subpackage T2.2 == PASS → +3
- If either is SKIP/PARTIAL/MINIMAL/FAIL → 0

### §4.3 Inheritance rule

Root SB is **NEVER inherited**. Subpackage without own settings.json typically has T2.1+T2.2 SKIP → §4.2 pair earns 0. Subpackage without own test/build commands typically has T1.2+T1.3 FAIL/SKIP → §4.1 pair earns 0. Many subpackages will have SB = 0.

Maximum SB per subpackage: +5 (both pairs PASS).

**Note**: SB is NOT persisted in `subpackages[]` schema — it is an intermediate value consumed only by the Final formula (§6).

## §5. Cap Tier per-package

Identical rule to root cap tier (`scoring-model.md` L100-L103), applied per subpackage independently:

```
cap = 60  if L5 == -3 AND no other Li at its minimum (L1 ≥ -2, L2 ≥ -1, L4 ≥ 0)
cap = 50  if L5 == -3 AND at least one other Li at its minimum (L1 = -3, L2 = -2, or L4 = -1)
cap = 100 otherwise
```

Each subpackage's own L5 + L1/L2/L4 minimums determine that subpackage's cap_tier. Stored in `subpackages[i].cap_tier` enum {50, 60, 100}.

## §6. Final Formula per-package

```
Final = min(DS × (1 + LAV_nonL5 / 50) + SB, cap)
```

- DS: from §1.4
- LAV_nonL5: from §3.1
- SB: from §4 (package-local, may be 0)
- cap: from §5

Result naturally bounded by schema range [0, 100] (schema requires final_score: number 0-100, no null; formula output is bounded above by cap ≤ 100 and from below by valid input ranges — no separate clamp per `scoring-model.md` L109).

Stored in `subpackages[i].final_score` (schema 1.2.0).

## §7. Degraded State Handling

When a subpackage has a CLAUDE.md file (so it counts toward `with_claude_md`) but cannot be scored, **omit the entry from `subpackages[]`** and emit a stable note code in `monorepo_detection.notes[]`. This produces `with_claude_md > scored_count` divergence (intentional per schema 1.2.0 closure — both fields are independent counters).

### §7.1 Parse error path

Trigger: subpackage CLAUDE.md exists but cannot be read/parsed (encoding error, broken UTF-8, file too large, permission denied).

Action:
- Increment `subpackage_coverage.with_claude_md` (the file exists)
- Do NOT increment `subpackage_coverage.scored_count`
- Do NOT emit `subpackages[]` entry
- Append to `monorepo_detection.notes[]`:
  ```json
  { "code": "subpackage_claude_md_parse_error", "details": "<package_root>/CLAUDE.md: <error description>" }
  ```

### §7.2 LAV evaluation failure path

Trigger: subpackage CLAUDE.md parses, T1/T2/T3 mechanical succeeds, but LAV evaluation fails (LLM degraded mode, timeout, rate limit).

Action: same as §7.1, but with note code:
```json
{ "code": "lav_evaluation_failed_subpackage", "details": "<package_root>: <reason>" }
```

### §7.3 No placeholder rows

Schema 1.2.0 requires `final_score`, `cap_tier`, and full `lav_breakdown` — placeholder values (e.g., final_score=0, cap_tier=50, all L scores at min) misrepresent and are NOT permitted. Omit the entry instead.
