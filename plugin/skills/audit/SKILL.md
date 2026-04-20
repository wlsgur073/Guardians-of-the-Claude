---
name: audit
description: "Validates your Claude Code configuration — checks essential settings, project alignment, and suggests improvements"
---

# Claude Code Configuration Audit

You are a Claude Code configuration auditor. Analyze the user's project and report on the health of their Claude Code setup.

Follow these phases in order. Each phase references a check file — read it and execute the checks defined within.

## Phase 0: Load Context & Learn

Read `../../references/learning-system.md` and follow the **Common Phase 0** steps (including **Step 0.5 Migration & Stale Check**) with these audit-specific overrides:

- **Step 2 override:** Read all recommendations in `local/recommendations.json` (no filter by `issued_by`). `/audit` surveys the entire recommendation history for trend analysis and stagnation detection.
- **Step 3 override:** Read the **full** `config-changelog.md` (both Compacted History and Recent Activity), not just Recent Activity. This enables trend analysis across the project's entire configuration history, including which skills ran since the last audit.

## Phase 1: Foundation Checks (T1)

Read `references/checks/t1-foundation.md` and execute all T1 checks.

**Critical:** If T1.1 (CLAUDE.md existence) is FAIL, halt immediately. Read `references/output-format.md` for the Early Halt format and present it. Do NOT proceed to any subsequent phase.

After T1 completes, note project signals for conditional loading:
- Is this a documentation-only project? (no package.json, Cargo.toml, go.mod, etc.)
- Does `.claude/settings.json` exist?
- Does `.claude/rules/` or `.claude/agents/` exist?

## Phase 1.5: Subpackage CLAUDE.md Discovery

Walk the project for additional `CLAUDE.md` files that represent true subpackage configs in a monorepo. Use `Glob` with pattern `**/CLAUDE.md`, then apply all filter layers below in order — a candidate must pass every layer to be reported.

**Path normalization (Windows):** Normalize candidate path separators to `/` before any comparison, and match directory names case-insensitively.

**Layer 1 — Root exclusion:** Exclude the root `CLAUDE.md` and the root `.claude/CLAUDE.md` (both already counted in T1.1).

**Layer 2 — Build/cache/vendor exclusion:** Exclude candidates whose path contains any segment matching: `node_modules/`, `dist/`, `build/`, `target/`, `vendor/`, `.git/`, `.next/`, `.nuxt/`, `.venv/`, `venv/`, `.cache/`, `coverage/`, `out/`, `__pycache__/`, `.pytest_cache/`.

**Layer 3 — Package root + manifest requirement:** Determine each candidate's **package root**:

- Normal case: the directory immediately containing `CLAUDE.md`.
- Nested `.claude/` exception: if the path is `…/.claude/CLAUDE.md`, the package root is the **parent of `.claude/`**. Example: `packages/api/.claude/CLAUDE.md` → package root `packages/api/`. This keeps legitimate subpackage `.claude/CLAUDE.md` layouts visible.

Keep the candidate only if its package root contains at least one of these manifest files (literal filenames, no glob): `package.json`, `Cargo.toml`, `go.mod`, `pyproject.toml`, `build.gradle`, `build.gradle.kts`, `pom.xml`, `composer.json`, `Gemfile`. This list is deliberately conservative for v2.10.0; projects using `setup.py`, `setup.cfg`, `Package.swift`, `mix.exs`, `*.csproj`, or `*.gemspec` as the only manifest will be silently missed (documented false-negative tradeoff — see CHANGELOG).

**Layer 4 — Git-ignore drop (best-effort):** If a `.git` entry (file or directory) exists at the project root — Git worktrees and submodules use a `.git` **file pointer** rather than a directory, so a plain directory check would incorrectly disable this layer for them — run `git check-ignore -q <path>` on each remaining candidate via `Bash`. `git check-ignore` returns exit `0` when the path is ignored (drop the candidate) or exit `1` when it is not ignored (keep the candidate). Any other exit code indicates a per-candidate error (broken index, unusual path, permission, etc.) — in that case, treat the candidate as **not ignored** (keep it, conservative default) and continue processing the remaining candidates, never aborting the layer. If there is no `.git` entry at the project root at all, or `git` is unavailable, or the `Bash` tool is not permitted, **silently skip this layer** — do not fail the audit and do not emit a warning.

**Never walk ancestors** looking for a manifest — always use the immediate package root as defined in Layer 3. "Any ancestor up to repo root" would over-match on any repo whose root already has a `package.json` or equivalent.

After filtering, limit displayed results to 20 files; if more remain, append `(+N more not shown)` in the output. For each reported file, record its repository-relative path and line count. Line count is newline count (`wc -l` semantics) including blank lines. **Do not score these files in this version** — this phase is disclosure only. If the filtered result is empty, do not render the "Additional CLAUDE.md Files" section in the output at all.

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

Read `../../references/scoring-model.md` for the complete scoring formula, then calculate results.

Apply the scoring model in this order:

1. **Score each item** using the 4-level scale (PASS=1.0, PARTIAL=0.6, MINIMAL=0.3, FAIL=0.0, SKIP=excluded)
2. **Calculate T1 Score** — `T1_Score = weighted average of non-SKIP T1 items` (used for Maturity Level Level 1 condition)
3. **Calculate Detail Score** — `DS = (T2_weighted × 0.60 + T3_weighted × 0.40) × 100`
4. **Calculate Synergy Bonus** — check qualifying pairs
5. **Calculate LAV components** — L1, L2, L3, L4, L5, L6 individually from Phase 3.5
6. **Calculate cap tier** — per DEC-1: `cap = 60` if L5 = −3 AND no other negative-minimum Li at its minimum; `cap = 50` if L5 = −3 AND at least one other Li at its negative minimum (L1 = −3, L2 = −2, or L4 = −1); `cap = 100` otherwise
7. **Calculate Final** — `min(DS × (1 + LAV_nonL5 / 50) + SB, cap)` where `LAV_nonL5 = L1 + L2 + L3 + L4 + L6` (L5 routed via cap tier per step 6)
8. **Check Quality Gate** — CLAUDE.md exists AND test command present; test condition waived if SKIP
9. **Determine Grade** and **Maturity Level**

Read `references/output-format.md` and present results using the defined action-first format: Quality Gate and Score first, then the `★ Most impactful` line and `Top 3 Priorities` block (with a `Next step` line pointing at `/secure` or `/optimize`), then the `---` separator and the Score Breakdown / Formula, then Detailed Findings, LAV Findings (if any item scored 0 or below), All Suggestions (from check files' conditional output), and finally the Maturity path. Prioritize Top 3 items by weighted score impact and explain the practical benefit of each.

**If previous audit results exist (from Phase 0):** Add a comparison line at the end:
> "Since your last audit (DATE): score changed from X → Y. [If /secure or /optimize ran since the last audit, list them.] Resolved: [issues]. Still open: [issues]."

## Phase 5: Persist Results & Learn

Read `../../references/learning-system.md` and follow the **Common Final Phase** steps with these audit-specific overrides:

- **Step 1 override (Skill-specific data in changelog entry):**
  The `config-changelog.md` entry for `/audit` must include:
  - `Detected:` — project changes observed (framework/package manager/testing etc. diffs).
  - `Profile updated:` — sections refreshed this run (for `/audit`, always all owned sections; see below).
  - `Applied:` — always `(none)` for `/audit` (audit does not mutate user files).
  - `Recommendations:` — all PENDING/DECLINED items emitted this run with appropriate status.

  The score itself (`XX/100`, grade, maturity level) is a user-facing snapshot surfaced in the terminal output of Phase 4 and in `state-summary.md`'s Recent Skill Results section. It must NOT be written into the `config-changelog.md` entry as a field — the changelog is learning data, not a report ledger.

  Profile merge under the state-mutation lock: `/audit` is the authoritative full refresh (Layer 3 of stale prevention). Always regenerate all `/audit`-owned sections — `runtime_and_language`, `framework_and_libraries`, `package_management`, `testing`, `build_and_dev`, `project_structure`, and `claude_code_configuration_state.claude_md` — from detected state, regardless of whether changes were detected. Other sections (e.g., `claude_code_configuration_state.settings_json` owned by `/secure`) must be preserved from the re-read `current_profile` (see `plugin/references/lib/merge_rules.md` §profile.json merge rules).

  **A1 merge rule amendments** (Phase 2a, `phase-2a-contracts.md §3.1`):
  - **Row 1 — `claude_code_configuration_state.model`**: any-skill writer; last-write-wins; written at Step 0.5 and Final Phase. Stateless mode: no-op (Phase 1 Global Invariant #6). See §3.1 Row 1, §3.4, §6.1, §6.2.
  - **Row 2 — `claude_code_configuration_state.scoring_model_ack`**: `/audit` exclusive writer; full-object replacement; Final Phase only. Stateless mode: no-op per DEC-11. See §3.1 Row 2, §5.1, §6.1, §6.2.
  - **Row 3 — `config-changelog.md` entry `- Model:` bullet** (DEC-8 hybrid writer; `phase-2a-contracts.md §3.1 Row 3` pseudocode authority; `§6.2` Step 2/3/5 slot assignments):
      - **Step 2 (re-read under lock — per §6.2 line 918 "previous-bullet re-read: all skills")**: after re-reading `current_changelog` per Common Final Phase Step 2, parse the immediately previous `###` entry (most-recent entry in Recent Activity, regardless of which skill wrote it) and extract its `- Model:` line's value. If the entry has no bullet (pre-v2.12.0 legacy OR non-/audit delta-omit path), the value is `null` per `§2.5 Addition A` omit→null rule. For `/audit` this Step 2 re-read is informational — Phase 1 baseline already performs the changelog re-read (`learning-system.md:148`), and /audit does not branch on the re-read value at Step 3.
      - **Step 3 (compute emit_bullet — /audit always-emit)**: `emit_bullet = True` unconditionally per DEC-8 writer policy (`design.md:255`) and `§3.1 Row 3 line 378` (reverse-scan simplicity — `§4.1 DEC-6` baseline derivation terminates at the first `/audit` entry; always-emit guarantees non-null `last_model` at that terminator without skipping null bullets).
      - **Step 5 (atomic write inclusion)**: the new changelog entry's first bullet under the `### {YYYY-MM-DD} — /audit` heading is `- Model: {full-resolved-id}` where `{full-resolved-id}` is `profile.claude_code_configuration_state.model` at Final Phase write time (the value set by `§3.4` Write Point 2). Place the bullet immediately after the heading, before `- Detected:`, per `§2.5 Addition A` entry format.
      - **Stateless mode**: no-op per DEC-11 — bullet write is skipped when `local/` is unwritable because the changelog file itself is not written per Phase 1 Global Invariant #6. See `§6.1`, `§6.2`.

After completing Common Final Phase, run **Critical Thinking & Insight Delivery** from the learning system reference. Apply Socratic verification to audit recommendations before presenting them.
