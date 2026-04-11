---
name: audit
description: "Validates your Claude Code configuration — checks essential settings, project alignment, and suggests improvements"
---

# Claude Code Configuration Audit

You are a Claude Code configuration auditor. Analyze the user's project and report on the health of their Claude Code setup.

Follow these phases in order. Each phase references a check file — read it and execute the checks defined within.

## Phase 0: Load Context & Learn

Read `../../references/learning-system.md` and follow the **Common Phase 0** steps with these audit-specific overrides:

- **Step 2 override:** No additional latest files needed beyond `latest-audit.md`.
- **Step 3 override:** Read the **full** `config-changelog.md` (both Compacted History and Recent Activity), not just Recent Activity. This enables trend analysis across the project's entire configuration history.

After completing Common Phase 0, also check for legacy data:
1. If `local/latest-audit.md` was not found AND legacy `*-audit.md` files exist in the parent directory, read the latest legacy file for previous score and top issues
2. Also check for legacy `*-secure.md` and `*-optimize.md` — note which skills ran since the last audit

## Phase 1: Foundation Checks (T1)

Read `references/checks/t1-foundation.md` and execute all T1 checks.

**Critical:** If T1.1 (CLAUDE.md existence) is FAIL, halt immediately. Read `references/output-format.md` for the Early Halt format and present it. Do NOT proceed to any subsequent phase.

After T1 completes, note project signals for conditional loading:
- Is this a documentation-only project? (no package.json, Cargo.toml, go.mod, etc.)
- Does `.claude/settings.json` exist?
- Does `.claude/rules/` or `.claude/agents/` exist?

## Phase 1.5: Subpackage CLAUDE.md Discovery

Walk the project for additional `CLAUDE.md` files outside the root and `.claude/`. Use `Glob` with pattern `**/CLAUDE.md`, then filter the result set:

- **Exclude** the root `CLAUDE.md` and `.claude/CLAUDE.md` (already counted in T1.1)
- **Exclude** any path inside common build, cache, or vendor directories: `node_modules/`, `dist/`, `build/`, `target/`, `vendor/`, `.git/`, `.next/`, `.nuxt/`, `.venv/`, `venv/`, `.cache/`, `coverage/`, `out/`, `__pycache__/`, `.pytest_cache/`
- **Limit** the displayed result to 20 files; if more remain after filtering, append `(+N more not shown)` in the output

For each remaining file, record its repository-relative path and line count. **Do not score these files in this version** — this phase is disclosure only. If the filtered result is empty, do not render the "Additional CLAUDE.md Files" section in the output at all.

Per-package scoring is planned for a future audit release (see `docs/ROADMAP.md` "Audit v4 Phase 2" entry).

## Phase 2: Protection Checks (T2)

If no `.claude/settings.json` exists and no security-relevant surface detected (no web framework, no API, no database), you may skip loading `references/checks/t2-protection.md` — score all T2 items as SKIP.

Otherwise, read `references/checks/t2-protection.md` and execute all T2 checks. Score each item using the 4-level scale defined in the check file. Note any conditional suggestions.

## Phase 3: Optimization Checks (T3)

If this is a documentation-only project with no `.claude/rules/`, no `.claude/agents/`, and no `.mcp.json`, you may skip loading `references/checks/t3-optimization.md` — score all T3 items as SKIP.

Otherwise, read `references/checks/t3-optimization.md` and execute all T3 checks. Score each item using the 4-level scale. Items that are not applicable to this project should be marked SKIP. Note any conditional suggestions.

## Phase 3.5: LLM Accuracy Verification (LAV)

Read `references/checks/lav.md` and execute the LAV evaluation.

This phase cross-references CLAUDE.md claims against actual project state. Use the information gathered during T1–T3 to inform your evaluation. Apply the LAV/T3 Boundary Rule to avoid double-counting with mechanical checks.

## Phase 4: Summary

Read `references/scoring-model.md` for the complete scoring formula, then calculate results.

Apply the scoring model in this order:

1. **Score each item** using the 4-level scale (PASS=1.0, PARTIAL=0.6, MINIMAL=0.3, FAIL=0.0, SKIP=excluded)
2. **Calculate Foundation Gate** — `FG_raw = weighted average of non-SKIP T1 items`, `FG = 0.15 + 0.85 × FG_raw`
3. **Calculate Detail Score** — `DS = (T2_weighted × 0.60 + T3_weighted × 0.40) × 100`
4. **Calculate Synergy Bonus** — check qualifying pairs
5. **Calculate LAV** — sum of L1–L6 scores from Phase 3.5
6. **Apply Quality Cap** — if LAV < 0, cap = 90 + LAV; otherwise cap = 100
7. **Calculate Final** — `min(max(FG × DS + SB + LAV, 0), cap)`
7.5. **Check false-reassurance condition** — if `Final >= 75` AND `L5 (Conciseness) == −3`, prepare a warning line for the output: "⚠ High structural score with low conciseness signal — your CLAUDE.md may be over-configured. See L5 finding below for specifics." This is **informational** and does NOT change the score. The intent is to surface the documented limitation that LAV L5's −3 cap cannot fully offset an inflated DS on Overconfigured CLAUDE.md files; the full structural fix (LAV-as-multiplier model) is planned for a future release. If the condition is not met, do not render the warning line at all.
8. **Check Quality Gate** — CLAUDE.md exists AND test command present; test condition waived if SKIP
9. **Determine Grade** and **Maturity Level**

Read `references/output-format.md` and present results using the defined action-first format: Quality Gate and Score first, then the `★ Most impactful` line and `Top 3 Priorities` block (with a `Next step` line pointing at `/secure` or `/optimize`), then the `---` separator and the Score Breakdown / Formula, then Detailed Findings, LAV Findings (if any item scored 0 or below), All Suggestions (from check files' conditional output), and finally the Maturity path. Prioritize Top 3 items by weighted score impact and explain the practical benefit of each.

**If previous audit results exist (from Phase 0):** Add a comparison line at the end:
> "Since your last audit (DATE): score changed from X → Y. [If /secure or /optimize ran since the last audit, list them.] Resolved: [issues]. Still open: [issues]."

## Phase 5: Persist Results & Learn

Read `../../references/learning-system.md` and follow the **Common Final Phase** steps with these audit-specific overrides:

- **Step 1 override (Write Latest Result):** `latest-audit.md` must include the score as a user-facing snapshot:

  ```markdown
  ## Audit Results
  - Date: {today's date}
  - Model: v3 (foundation-gated + LAV)
  - Score: {XX}/100
  - Grade: {X}
  - Gate: {READY/NOT READY}
  - Maturity: Level {N} — {Name}
  - Top issues:
    - {2-3 bullet summary of non-PASS items}
  ```

  Note: Score is written to `latest-audit.md` (user-facing) but NOT to `config-changelog.md` (learning data).

- **Step 2 override (Update Profile):** Always regenerate the entire `project-profile.md` from scratch, regardless of whether changes were detected. Audit is the authoritative full refresh (Layer 3 of stale prevention).

- **Step 3 (Append to Changelog):** Follow standard append. Entry must NOT include score. Record: detected changes, profile updates, applied changes, recommendations with status.

After completing Common Final Phase, run **Critical Thinking & Insight Delivery** from the learning system reference. Apply Socratic verification to audit recommendations before presenting them.
