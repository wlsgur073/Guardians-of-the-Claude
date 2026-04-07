# LAV — LLM Accuracy Verification

LAV supersedes and replaces all three LQM (LLM Quality Modifier) questions. The LQM section is removed from the scoring model.

LAV executes after mechanical checks (T1–T3). The auditor cross-references CLAUDE.md claims against actual project state to evaluate accuracy, reliability, and documentation quality.

## LAV/T3 Boundary Rule

LAV evaluates holistic accuracy that **cannot be mechanically verified**. If a deficiency is already captured by a T3 mechanical check, LAV must not penalize the same deficiency again:

- If T3.1 already detected a missing directory (PARTIAL/FAIL), L1 should score **0** for that specific issue. L1 penalizes only structural inaccuracies beyond T3.1's mechanical detection scope (e.g., wrong architecture descriptions, outdated component relationships, misleading technology claims).
- If T3.3 already detected a missing tool config (PARTIAL/FAIL), L2 should score **0** for that specific issue. L2 penalizes only command reliability issues beyond T3.3's scope (e.g., undocumented prerequisite steps, wrong command flags, missing workflow context).
- If T3.7 already detected undocumented env vars (PARTIAL/FAIL), L2 should not re-penalize the same env var gap.

Mechanical checks and LAV form complementary layers, not redundant penalties.

## Evaluation Structure

Answer each question after reviewing CLAUDE.md against the actual project state:

| # | Question | Score | Nature |
|---|---|---|---|
| L1 | Is the documented project structure (directories, components, architecture) consistent with the actual codebase? | -3 / 0 / +2 | Accuracy |
| L2 | Are all documented commands and workflows executable without undocumented prerequisites? | -2 / 0 / +2 | Reliability |
| L3 | Are project-specific patterns, gotchas, or conventions (not derivable from code alone) documented? | 0 / +1 / +3 | Documentation quality |
| L4 | Is CLAUDE.md structured for effective LLM consumption? (clear sections, appropriate detail) | 0 / +1 | Structural quality |

**Range: -5 to +8**

## Scoring Guidelines

**L1 Structure Accuracy (-3/0/+2):**
- **+2**: Documented structure matches reality exactly, all major directory/component info is current
- **0**: Mostly matches but minor discrepancies exist
- **-3**: Non-existent directories, wrong component names, or misleading architecture descriptions

**L2 Command Reliability (-2/0/+2):**
- **+2**: All documented commands reference correct tools and config files, immediately executable
- **0**: Commands exist but some prerequisites unclear
- **-2**: Non-executable commands documented, or required environment setup missing

**L3 Patterns/Gotchas (0/+1/+3):**
- **+3**: Project-specific gotchas, conventions, caveats well-documented (not inferable from code alone)
- **+1**: Some non-obvious information present but incomplete
- **0**: No project-specific patterns or gotchas documented

**L4 Structural Quality (0/+1):**
- **+1**: Clear section organization, appropriate detail level, LLM can quickly find needed info
- **0**: Structure unclear or disorganized

## Improvement Suggestions

For every LAV item scored **0 or below**, output a specific improvement suggestion with the finding and a concrete fix:

```
LAV Findings:
  L1 (-3): Structure inaccurate
    → components/ lists hub/, motion/ but actual subdirs are dashboard/, detail/
    → Suggestion: Update tree diagram to match actual structure

  L2 (-2): Command reliability insufficient
    → pnpm lint documented but eslint.config.js not found
    → Suggestion: Add ESLint config or remove lint command from CLAUDE.md
```

If all LAV items score above 0, output: "LAV: No accuracy issues found."
