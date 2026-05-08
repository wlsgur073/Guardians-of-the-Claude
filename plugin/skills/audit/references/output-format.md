# Output Format

## Standard Output

Present results using this format. Do not show Phase/Step labels — use the friendly format.

```
Configuration Audit Results
===========================

Quality Gate: READY    (CLAUDE.md OK, test command OK)
Score: 60/100 (Grade: B)  |  Maturity: Level 3 — Optimized

⚠ Model drift since last /audit (baseline: /audit 2026-04-15, claude-opus-4-6):
  family_tier:          opus  →  sonnet
  context_window_class: 200k  →  1M

★ Most impactful: [Highest-impact change and why it matters]

Top 3 Priorities
  1. [Highest impact] — [reason and expected score effect]
  2. [Second priority] — [reason]
  3. [Third priority] — [reason]

  Next step: run /guardians-of-the-claude:optimize to improve organization.

---

Score Breakdown
  T1 Score:              1.00    ==================== 100%
  Protection (T2):       1.00    ==================== 100%
  Optimization (T3):     1.00    ==================== 100%
  Detail Score (DS):     100.0   (T2: 1.00 x 60% + T3: 1.00 x 40%) x 100
  Synergy: +5  (test + build, sensitive + rules)
  LAV: L1=0, L2=0, L3=0, L4=0, L5=-3 (Conciseness fail), L6=+1
  LAV_nonL5: +1

  Formula:
  DS: (1.00 x 0.60 + 1.00 x 0.40) x 100 = 100.0
  SB: +5 (test + build: +2, sensitive + rules: +3)
  LAV_nonL5: L1+L2+L3+L4+L6 = 0+0+0+0+1 = 1
  Cap (L5=-3 + no other negative-min Li at minimum): 60
  Final: min(100.0 x (1 + 1/50) + 5, cap=60) = min(107.0, 60) = 60

Detailed Findings
  [Detailed findings per item...]

LAV Findings
  [If any LAV items scored 0 or below, show findings and suggestions here]

All Suggestions
  * [actionable improvements from check files' conditional suggestions]

Additional CLAUDE.md Files (informational)
  Found 3 additional CLAUDE.md files in subpackages:
    * packages/api/CLAUDE.md (47 lines)
    * packages/web/CLAUDE.md (62 lines)
    * packages/shared/CLAUDE.md (28 lines)

Maturity path: [Current] → [Next level]: [specific requirement]

Since last audit (2026-03-31): 55 -> 60 (+5).
Still open: L5 conciseness flag, no MCP configuration, agent model diversity.
```

**Display caveat:** If fewer than 2 non-SKIP items remain in T2 or T3, append "(based on N of M items — others not applicable)" to the percentage display.

**Additional CLAUDE.md Files section:** Conditional rendering — when `monorepo_detection.detected == true AND subpackage_coverage.package_roots_total > 0`, the **Subpackage Score Rollup** section renders (see below) and this Additional CLAUDE.md Files section is suppressed (Score Rollup table already shows paths + scores). Otherwise (including `detected != true` or `package_roots_total == 0`), this section renders if Phase 1.5 disclosure walk found one or more `CLAUDE.md` files in subpackages outside the root and `.claude/`. List each path with its line count, limited to 20 entries; if more found, append `(+N more not shown)`. Informational disclosure, not a scoring component. When zero additional files are found, omit the entire section.

**Coverage invariant:** When monorepo is detected, every Phase 1.5 disclosed CLAUDE.md path that survives the 4-layer filter is counted in `package_root_caps.total_filtered`. Paths not displayed or not scored due to configured caps must be surfaced by count in the Subpackage Score Rollup notice (see Rollup Summary Line below).

**If previous audit results exist:** Add comparison at the end:
> "Since your last audit (DATE): score changed from X → Y. [Skills applied since last audit: /secure, /optimize.] Resolved: [issues]. Still open: [issues]."

**Top 3 Priorities section:** Always appears near the top of the output, directly after the Score line, whenever any non-PASS results exist. This is the primary action block — the user sees "what to do next" before seeing the math. This section replaces the old bottom-of-output "Insights & Recommendations" block; the same content, surfaced earlier.

**Drift Advisory Block:** Between the Score line and the `★ Most impactful` line, a **conditional** block renders when the drift state is `drift`. Silent in all other states (`match`, `missing_baseline`, `normalization_null`).

Format rules:

- **Header line:** `⚠ Model drift since last /audit (baseline: {scan_source}, {baseline_model_id}):` where `{scan_source}` is the **scan-winner provenance** — `/audit YYYY-MM-DD` when the scan-winner is a Recent Activity `- Model:` bullet (use that entry's `date`); `/audit compacted-bucket YYYY-MM` when the scan-winner is a Compacted History anchor (use anchor's `last_entry_date`). `{baseline_model_id}` is the scan-winner's raw `last_model` / `- Model:` value.
- **Axis lines:** render **changed axes only** — compare `baseline_fp` and `current_fp` axis-by-axis; emit one line per differing axis. Values are **user-facing** — `opus` / `sonnet` / `haiku`, `200k` / `1M`, `none` / `extended_any`, `manual` / `compaction_capable` — NOT internal enum tokens (like `opus_tier` / `1m_class`). Alignment: axis name left-justified to 22 columns, then `baseline → current`.
- **No severity label** (no `minor`, `major`, `critical`, or equivalent tier). The drift advisory specification does not define severity levels; adding one would exceed design authority.
- The block is transient terminal output only — **NOT** added to `recommendations.json` (drift advisories are not persisted as recommendations).
- **Label distinction**: "Model drift" in this block MUST differ lexically from the scoring-contract-change banner copy ("Scoring contract changed"). Both can co-render in the same `/audit` run when a scoring-contract bump AND a fingerprint drift occur simultaneously — distinct labels prevent operators from conflating two different actions.

Position rationale: drift surfaces as interpretive context for a possibly-changed Score, but must not displace the action-first "Top 3 Priorities" block. Between Score and `★ Most impactful` is the widest unobstructed slot.

Generation rules:

- **★ Most impactful line**: Identify the single non-PASS item with the highest weighted score impact. Explain WHY fixing it matters (not just "add X", but "adding X helps Claude because..."). This is the educational anchor and sits directly above the numbered priority list.
- **Priority list (1-3)**: Sort non-PASS items by score impact (weight × score gap). Show top 3. For each, explain the practical benefit and the expected score effect.
- **Next step line**: One line inside the Top 3 block suggesting which follow-up skill to run:
  - T2.1 (deny patterns), T2.2 (security rules), or file protection issues:
    > "Next step: run `/guardians-of-the-claude:secure` to fix protection gaps."
  - T2.3 (hook quality) or T3 (optimization) issues:
    > "Next step: run `/guardians-of-the-claude:optimize` to improve organization."
  - Both categories have issues: show both lines, secure first.
  - Score is 100/100 — **do not** use "Your configuration is in great shape. No changes needed." unconditionally; that copy misrepresents remaining LAV headroom when present. Branch by whether every LAV dimension is at its maximum:
    - **`LAV == +10` (all six LAV items at their max):** omit the Priority list. Show "Configuration reaches the current scoring ceiling. Re-audit on major dependency or configuration changes." Then suggest exploring advanced features the project doesn't yet use (e.g., "Consider adding specialized agents for code review vs implementation tasks").
    - **`LAV < +10` (one or more LAV items below their max):** omit the Priority list. Show "Configuration reaches the current scoring ceiling. Remaining refinements live in LAV — see the LAV breakdown under Score Breakdown for items still below their maximum. Re-audit on major changes." Then suggest exploring advanced features as above. A fuller excellence-headroom surface (Raw exposure, Level 4 — Mastered tier, Excellence Opportunities section) is tracked in `docs/ROADMAP.md` under "Audit v4 Phase 2" and intentionally deferred until the LAV-as-multiplier scoring rewrite lands — adding those surfaces now would incur UX churn when LAV ranges change.
- **Tone**: Educational and encouraging — frame gaps as opportunities, not failures. Use concrete examples from the project being audited.

**Score Breakdown section:** Follows the Top 3 Priorities block, separated by `---`. Contains the tier percentages (T1 Score, Protection, Optimization, Detail Score), Synergy/LAV bonuses, and the full Formula block showing how the final score was derived. This is the transparency tier — users who want to understand or challenge the score find the math here instead of at the top.

**Detailed Findings / LAV Findings / All Suggestions:** Per-item check results, LAV item findings (if any item scored 0 or below), and the full list of actionable suggestions from check files' conditional output. These come after Score Breakdown. Keep "All Suggestions" distinct from "Top 3 Priorities" — the former is the full list, the latter is the prioritized subset with score-impact reasoning.

**Maturity path and previous-audit comparison:** Always at the very end of the output. Show current maturity level and what condition is needed for the next level. If already Level 3, suggest advanced optimizations (hooks, agents, MCP). If previous audit results exist, append the delta comparison: "Since your last audit (DATE): score changed from X → Y. Resolved: [items]. Still open: [items]."

---

## Subpackage Score Rollup (when monorepo detected)

When `monorepo_detection.detected == true` AND `subpackage_coverage.package_roots_total > 0`, render a Subpackage Score Rollup block AFTER the root Score Breakdown section. This follows the summary-first style of audit output (root summary → details → subpackage summary → subpackage details).

### Rollup Summary Line

```
Subpackage Score Rollup
  min={X}, median={Y}, worst={path(s)} ({N} scored, {M} without CLAUDE.md, {K} unscored)
```

Append `(total {T} filtered, {U} unscored beyond scoring cap)` to the counter line **only when `T > 50 OR U > 0`** (display cap exceeded or scoring cap exceeded); otherwise render the standard 3-counter line.

- If `scored_count == 0` (per `checks/per-package-rollup.md` §3): `min=n/a, median=n/a, worst=n/a (0 scored, M without CLAUDE.md, K unscored)`.
- `K = with_claude_md - scored_count` (unscored due to parse errors / LAV failures).
- Worst tie format (per `checks/per-package-rollup.md` §2.3): `"<first N tie-sorted paths> (and K-N more tied)"` with N=3 suggested. Example (5 subpackages tied at `final_score=42`, sorted ascending): `worst = "packages/api, packages/billing, packages/web (and 2 more tied)"`.

### Per-Subpackage Score Table

Render the table sorted ascending by repo-relative path. Apply display cap = 20 (`monorepo_detection.package_root_caps.display`). The variable `total_filtered = subpackage_coverage.package_roots_total` (= `with_claude_md + without_claude_md` per `checks/per-package-rollup.md` §1.1).

```
Subpackage Scores (showing first 20 of {total_filtered}; ascending by path)
  Path                          | Status        | Score | Cap | LAV (L1-L6)
  ------------------------------|---------------|-------|-----|-------------
  packages/api                  | scored        | 75.5  | 100 | 2,2,1,0,0,1
  packages/cli                  | no CLAUDE.md  | n/a   | n/a | n/a
  packages/web                  | unscored      | n/a   | n/a | n/a (parse error)
  ...
  (+{total_filtered - 20} more not shown)
```

Status values:
- `scored`: subpackage has entry in `subpackages[]` (final_score, cap_tier, lav_breakdown all populated)
- `no CLAUDE.md`: subpackage has no CLAUDE.md file (counted in `subpackage_coverage.without_claude_md`)
- `unscored`: subpackage has CLAUDE.md but parse/LAV failure; row omitted from `subpackages[]`, note in `monorepo_detection.notes[]`

When `total_filtered ≤ 20`: render full list, no `(+N more)` notice.

### Polyglot Example (Mixed Ecosystems)

Subpackage paths follow each ecosystem's native convention — the rollup format is ecosystem-agnostic. The same table renders for projects mixing multiple ecosystems in a single workspace:

```
Subpackage Score Rollup
  min=42.0, median=70.4, worst=services/api (4 scored, 1 without CLAUDE.md, 0 unscored)

Subpackage Scores (showing first 20 of 5; ascending by path)
  Path                          | Status        | Score | Cap | LAV (L1-L6)
  ------------------------------|---------------|-------|-----|-------------
  crates/parser                 | scored        | 75.0  | 100 | 2,2,1,0,0,1
  packages/devkit               | scored        | 72.5  | 100 | 2,2,1,0,0,1
  python/ml-utils               | scored        | 68.2  | 100 | 2,1,1,0,0,1
  scripts/build                 | no CLAUDE.md  | n/a   | n/a | n/a
  services/api                  | scored        | 42.0  | 60  | 2,1,1,0,-3,0
```

Path conventions illustrated: `crates/<name>` (Rust `Cargo.toml [workspace] members`), `packages/<name>` (Node `package.json workspaces` or `pnpm-workspace.yaml`), `python/<name>` (Python `[tool.uv.workspace] members` or `[tool.hatch.workspace] members`), `services/<name>` (heuristic Medium-confidence pattern per `references/checks/monorepo-detection.md` §2 — gated by ≥2 manifest-bearing subdirectories or co-occurrence with a higher-confidence signal). The LAV multiplier and cap tiers operate identically across ecosystems; only the path strings vary.

### Section Order

The audit output sections are ordered summary-first (matching existing root output style at L11-L23):

1. Quality Gate + Score (root)
2. Top 3 Priorities (root)
3. Score Breakdown (root)
4. **Subpackage Score Rollup** (only when monorepo detected)
5. **Per-Subpackage Score Table** (only when monorepo detected)

This places aggregate summary before per-row details at both root and subpackage levels.

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

Recommendation: Run /guardians-of-the-claude:create to create initial configuration.
```

Do not produce a numeric score, grade, or maturity level. The halt is not a score of zero — it means the audit could not be performed.
