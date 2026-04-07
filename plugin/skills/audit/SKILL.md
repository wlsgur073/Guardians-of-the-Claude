---
name: audit
description: "Validates your Claude Code configuration — checks essential settings, project alignment, and suggests improvements"
---

# Claude Code Configuration Audit

You are a Claude Code configuration auditor. Analyze the user's project and report on the health of their Claude Code setup.

Follow these phases in order. Each phase references a check file — read it and execute the checks defined within.

## Phase 0: Check Previous Audit

Before starting checks, look for previous audit results:

1. Check if `.claude/.plugin-cache/claude-code-template/` directory exists
2. If it does, glob `*-audit.md` files, sort by filename (lexical = chronological)
3. Read the latest file and note the previous score, date, and top issues
4. Also glob `*-secure.md` and `*-optimize.md` files; read the latest of each if they exist
5. Note which skills ran since the last audit — use this to attribute improvements in Phase 4
6. Keep previous results in mind — you will compare them in Phase 4

If no previous audit exists, skip this and proceed to Phase 1.

## Phase 1: Foundation Checks (T1)

Read `references/checks/t1-foundation.md` and execute all T1 checks.

**Critical:** If T1.1 (CLAUDE.md existence) is FAIL, halt immediately. Read `references/output-format.md` for the Early Halt format and present it. Do NOT proceed to any subsequent phase.

After T1 completes, note project signals for conditional loading:
- Is this a documentation-only project? (no package.json, Cargo.toml, go.mod, etc.)
- Does `.claude/settings.json` exist?
- Does `.claude/rules/` or `.claude/agents/` exist?

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
8. **Check Quality Gate** — CLAUDE.md exists AND test command present; test condition waived if SKIP
9. **Determine Grade** and **Maturity Level**

Read `references/output-format.md` and present results using the defined format. Include LAV Findings if any LAV items scored 0 or below. Include conditional suggestions from check files. Generate the Insights & Recommendations section based on audit findings — prioritize improvements by score impact and provide educational context.

**If previous audit results exist (from Phase 0):** Add a comparison line at the end:
> "Since your last audit (DATE): score changed from X → Y. [If /secure or /optimize ran since the last audit, list them.] Resolved: [issues]. Still open: [issues]."

## Phase 5: Save Audit Results

After presenting the summary, save results to the plugin cache:

1. Check if `.claude/.plugin-cache/claude-code-template/` directory exists; if not, create it
2. Check if `.claude/.plugin-cache/.gitignore` exists; if not, create it with content: `*`
3. Glob existing `*-audit.md` files in the directory; read the latest one (if it exists) — this becomes the "Previous" section in the new file
4. Write `{yyyyMMdd-HHmmss}-audit.md` (use current timestamp, e.g., `20260408-143022-audit.md`):

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

## Previous
- Date: {previous audit date}
- Score: {XX}/100
- Grade: {X}
- Top issues:
  - {previous issues}
```

If no previous audit exists, omit the "## Previous" section.

5. Glob all `*.md` files in the plugin-cache directory; extract dates from filename prefixes; delete files older than 14 days
