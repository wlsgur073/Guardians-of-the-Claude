# Output Format

## Standard Output

Present results using this format. Do not show Phase/Step labels — use the friendly format.

```
Configuration Audit Results
===========================

Quality Gate: READY    (CLAUDE.md OK, test command OK)

Foundation Gate (FG):  1.00    ==================== 100%

Protection (T2):       0.70    ==============...... 70%
Optimization (T3):     0.50    ==========.......... 50%
Detail Score (DS):     62.0    (T2: 0.70 x 60% + T3: 0.50 x 40%) x 100

Synergy: +2  (test + build)
LAV: +4  (L1: +2 + L2: +2 + L3: 0 + L4: 0)

Score: 68/100 (Grade: B)  |  Maturity: Level 3 — Optimized

  Breakdown:
  FG: 0.15 + 0.85 x 1.00 = 1.00
  DS: (0.70 x 0.60 + 0.50 x 0.40) x 100 = 62.0
  SB: +2 (test + build)
  LAV: +4 (L1: +2 + L2: +2 + L3: 0 + L4: 0)
  Final: min(max(1.00 x 62.0 + 2 + 4, 0), 100) = 68

[Detailed findings per item...]

LAV Findings:
  [If any LAV items scored 0 or below, show findings and suggestions here]

Suggestions
  * [actionable improvements from check files' conditional suggestions]

Since last audit (2026-03-31): 65 -> 68 (+3). Note: scoring model changed (v2 -> v3).
Still open: no MCP configuration, agent model diversity.
```

**Display caveat:** If fewer than 2 non-SKIP items remain in T2 or T3, append "(based on N of M items — others not applicable)" to the percentage display.

**If previous audit results exist:** Add comparison at the end:
> "Since your last audit (DATE): score changed from X → Y. [Skills applied since last audit: /secure, /optimize.] Resolved: [issues]. Still open: [issues]."

**Next Steps section:** Always include if there are any non-PASS results:

- If any T2.1 (deny patterns), T2.2 (security rules), or file protection issues:
  > "Security improvements needed: run `/claude-code-template:secure` to fix protection gaps."

- If any T2.3 (hook quality) or T3 (optimization) issues:
  > "Configuration improvements available: run `/claude-code-template:optimize` to improve organization."

- If both categories have issues, show both lines (secure first).

- If score is 100/100: "Your configuration is in great shape. No changes needed."

## Early Halt Output

When CLAUDE.md does not exist (T1.1 FAIL), the audit halts immediately. Use this output instead of the standard format:

```
Configuration Audit Results
===========================

Quality Gate: NOT READY

CLAUDE.md not found at project root or .claude/CLAUDE.md.
Cannot proceed with audit — CLAUDE.md is a prerequisite for all checks.

Detected project signals:
  * [list any dependency manifests, source files, or frameworks found]

Recommendation: Run /claude-code-template:create to create initial configuration.
```

Do not produce a numeric score, grade, or maturity level. The halt is not a score of zero — it means the audit could not be performed.
