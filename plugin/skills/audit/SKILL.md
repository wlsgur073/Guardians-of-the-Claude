---
name: audit
description: "Validates your Claude Code configuration — checks essential settings, project alignment, and suggests improvements"
---

# Claude Code Configuration Audit

You are a Claude Code configuration auditor. Analyze the user's project and report on the health of their Claude Code setup.

Follow these phases in order. Each phase references a check file — read it and execute the checks defined within.

## Install Integrity Pre-Check

Before Phase 0 (below) and before any state mutation or lock acquisition, verify the runtime scoring-contract constant matches the canonical declaration in `plugin/references/scoring-model.md` frontmatter. Mismatch is a **broken-install error** (install-integrity check, `/audit`-scoped), not a warning.

**Steps:**

1. Load `plugin/references/scoring-model.md` frontmatter and extract `scoring_contract_id`.
2. Read the hardcoded `CURRENT_SCORING_CONTRACT_ID` constant from runtime code.
3. If the two values differ, **abort the run immediately** with a fatal diagnostic:

   ```
   BROKEN INSTALL: scoring_contract_id mismatch
     frontmatter: <value-from-md>
     runtime:     <value-from-constant>
   Resolution: reinstall the plugin or sync the runtime constant to match frontmatter.
   ```

4. Do NOT proceed to Phase 0; do NOT acquire the state-mutation lock. This check is read-only (no state side effects), so stateless mode runs it identically.

This substep precedes Phase 0 deliberately so that a broken install never reaches stateful paths. Placement before Phase 0 is an `/audit` implementation choice — the install-integrity contract specifies purpose and failure mode but leaves ordering open.

---

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

## Phase 1.5: Subpackage Discovery and Monorepo Detection

This phase performs both subpackage `CLAUDE.md` disclosure and monorepo classification, emitting `monorepo_detection` evidence (`detected`, `package_roots`, `package_roots_for_scoring`, `evidence`, `notes`) consumed by Phase 3.6 per-package scoring.

**Path normalization (Windows):** Normalize candidate path separators to `/` before any comparison, and match directory names case-insensitively.

### Subpackage CLAUDE.md disclosure walk (4-layer filter)

Walk the project for additional `CLAUDE.md` files that represent true subpackage configs in a monorepo. Use `Glob` with pattern `**/CLAUDE.md`, then apply all filter layers below in order — a candidate must pass every layer to be reported.

**Layer 1 — Root exclusion:** Exclude the root `CLAUDE.md` and the root `.claude/CLAUDE.md` (both already counted in T1.1).

**Layer 2 — Build/cache/vendor exclusion:** Exclude candidates whose path contains any segment matching: `node_modules/`, `dist/`, `build/`, `target/`, `vendor/`, `.git/`, `.next/`, `.nuxt/`, `.venv/`, `venv/`, `.cache/`, `coverage/`, `out/`, `__pycache__/`, `.pytest_cache/`.

**Layer 3 — Package root + manifest requirement:** Determine each candidate's **package root**:

- Normal case: the directory immediately containing `CLAUDE.md`.
- Nested `.claude/` exception: if the path is `…/.claude/CLAUDE.md`, the package root is the **parent of `.claude/`**. Example: `packages/api/.claude/CLAUDE.md` → package root `packages/api/`. This keeps legitimate subpackage `.claude/CLAUDE.md` layouts visible.

Keep the candidate only if its package root contains at least one of the manifest patterns listed below. Most patterns are literal filenames; four are single-segment globs (`*.csproj`, `*.fsproj`, `*.gemspec`, `*.cabal`) for ecosystems where the manifest filename varies per project. Glob match is single-segment only (e.g., `*.csproj` matches `Project.csproj`, NOT `nested/Project.csproj`) and case-insensitive on Windows.

| Ecosystem | Manifest pattern(s) |
|---|---|
| Node | `package.json` |
| Rust | `Cargo.toml` |
| Go | `go.mod` |
| Python | `pyproject.toml`, `setup.py`, `setup.cfg` |
| Java/Maven | `pom.xml` |
| Java/Gradle | `build.gradle`, `build.gradle.kts` |
| .NET | `*.csproj`, `*.fsproj` |
| Elixir | `mix.exs` |
| Swift | `Package.swift` |
| Ruby | `Gemfile`, `*.gemspec` |
| C/C++ | `CMakeLists.txt`, `BUILD.bazel`, `BUILD`, `conanfile.txt`, `conanfile.py`, `meson.build` |
| Dart/Flutter | `pubspec.yaml` |
| Erlang | `rebar.config` |
| Haskell | `*.cabal` |
| PHP | `composer.json` |

**Layer 4 — Git-ignore drop (best-effort):** If a `.git` entry (file or directory) exists at the project root — Git worktrees and submodules use a `.git` **file pointer** rather than a directory, so a plain directory check would incorrectly disable this layer for them — run `git check-ignore -q <path>` on each remaining candidate via `Bash`. `git check-ignore` returns exit `0` when the path is ignored (drop the candidate) or exit `1` when it is not ignored (keep the candidate). Any other exit code indicates a per-candidate error (broken index, unusual path, permission, etc.) — in that case, treat the candidate as **not ignored** (keep it, conservative default) and continue processing the remaining candidates, never aborting the layer. If there is no `.git` entry at the project root at all, or `git` is unavailable, or the `Bash` tool is not permitted, **silently skip this layer** — do not fail the audit and do not emit a warning.

**Never walk ancestors** looking for a manifest — always use the immediate package root as defined in Layer 3. "Any ancestor up to repo root" would over-match on any repo whose root already has a `package.json` or equivalent.

**Workspace declaration files** (consumed by per-ecosystem parsing rules in `references/checks/monorepo-detection.md`, NOT used in Layer 3 package-root identification):

| Ecosystem | File(s) |
|---|---|
| Node | `pnpm-workspace.yaml` |
| Go | `go.work` |
| Java/Gradle | `settings.gradle`, `settings.gradle.kts` |
| .NET | `*.sln` |
| C/C++ (Bazel) | `WORKSPACE`, `MODULE.bazel` |
| Dart/Flutter | `melos.yaml` |
| Haskell | `cabal.project`, `stack.yaml` |

For workspace declaration parsing per ecosystem and the full detection algorithm (Phase A through E), read `references/checks/monorepo-detection.md`.

After filtering, limit displayed disclosure results to 20 files; if more remain, append `(+N more not shown)`. For each reported file, record its repository-relative path and line count. Line count is newline count (`wc -l` semantics) including blank lines.

## Phase 2: Protection Checks (T2)

If no `.claude/settings.json` exists and no security-relevant surface detected (no web framework, no API, no database), you may skip loading `references/checks/t2-protection.md` — score all T2 items as SKIP.

Otherwise, read `references/checks/t2-protection.md` and execute all T2 checks. Score each item using the 4-level scale defined in the check file. Note any conditional suggestions.

## Phase 3: Optimization Checks (T3)

If this is a documentation-only project with no `.claude/rules/`, no `.claude/agents/`, and no `.mcp.json`, you may skip loading `references/checks/t3-optimization.md` — score all T3 items as SKIP.

Otherwise, read `references/checks/t3-optimization.md` and execute all T3 checks. Score each item using the 4-level scale. Items that are not applicable to this project should be marked SKIP. Note any conditional suggestions.

## Phase 3.5: LLM Accuracy Verification (LAV)

Read `references/checks/lav.md` and execute the LAV evaluation.

This phase cross-references CLAUDE.md claims against actual project state. Use the information gathered during T1–T3 to inform your evaluation. Apply the LAV/T3 Boundary Rule to avoid double-counting with mechanical checks.

## Phase 3.6: Per-Package Scoring (when monorepo detected)

If `monorepo_detection.detected == true` AND `monorepo_detection.package_roots_for_scoring[]` is non-empty, iterate per-package scoring after Phase 3.5 LAV completes:

1. Read `references/checks/per-package-scoring.md` and execute the per-package scoring procedure for each package root in `monorepo_detection.package_roots_for_scoring[:scored_cap]`.
2. Read `references/checks/per-package-rollup.md` and emit the rollup output (min, median, worst, coverage counters) per the rendering rules.
3. **Per-package findings are transient.** Per-package score rows (`subpackages[]`) and coverage counters (`subpackage_coverage`) ARE persisted per `plugin/references/lib/merge_rules.md` `/audit` ownership. Statistical aggregates (`min`, `median`, `worst`) are computed-on-render per `references/checks/per-package-rollup.md` §4 (No Persistence). Any advisory-style observations surfaced for individual subpackages render to terminal output only — they MUST NOT be added to `recommendations.json`. Persistence semantics for per-package recommendations are deferred to a later minor; v2.13.0 maintains a transient-by-default contract for per-subpackage findings.

If `monorepo_detection.detected != true` OR `package_roots_for_scoring[]` is empty, skip Phase 3.6 entirely.

## Phase 4: Summary

Read `../../references/scoring-model.md` for the complete scoring formula, then calculate results.

Apply the scoring model in this order:

1. **Score each item** using the 4-level scale (PASS=1.0, PARTIAL=0.6, MINIMAL=0.3, FAIL=0.0, SKIP=excluded)
2. **Calculate T1 Score** — `T1_Score = weighted average of non-SKIP T1 items` (used for Maturity Level Level 1 condition)
3. **Calculate Detail Score** — `DS = (T2_weighted × 0.60 + T3_weighted × 0.40) × 100`
4. **Calculate Synergy Bonus** — check qualifying pairs
5. **Calculate LAV components** — L1, L2, L3, L4, L5, L6 individually from Phase 3.5
6. **Calculate cap tier** — `cap = 60` if L5 = −3 AND no other negative-minimum Li at its minimum; `cap = 50` if L5 = −3 AND at least one other Li at its negative minimum (L1 = −3, L2 = −2, or L4 = −1); `cap = 100` otherwise
7. **Calculate Final** — `min(DS × (1 + LAV_nonL5 / 50) + SB, cap)` where `LAV_nonL5 = L1 + L2 + L3 + L4 + L6` (L5 routed via cap tier per step 6)
8. **Check Quality Gate** — CLAUDE.md exists AND test command present; test condition waived if SKIP
9. **Determine Grade** and **Maturity Level**

Read `references/output-format.md` and present results using the defined action-first format: Quality Gate and Score first, then the `★ Most impactful` line and `Top 3 Priorities` block (with a `Next step` line pointing at `/secure` or `/optimize`), then the `---` separator and the Score Breakdown / Formula, then Detailed Findings, LAV Findings (if any item scored 0 or below), All Suggestions (from check files' conditional output), and finally the Maturity path. Prioritize Top 3 items by weighted score impact and explain the practical benefit of each.

**If previous audit results exist (from Phase 0):** Add a comparison line at the end:
> "Since your last audit (DATE): score changed from X → Y. [If /secure or /optimize ran since the last audit, list them.] Resolved: [issues]. Still open: [issues]."

## Phase 4.5: Render qa-report.md

After Phase 4 completes, all scoring facts are frozen (LAV L1-L6 scores, DS, SB, cap, Final, bucket). Render `qa-report.md` from these frozen facts only.

Read `references/qa-report-template.md` for the full template skeleton (5-section list, S1-S5 render rules, S5 negative-transparency filter scope).

**Steps:**

1. **Sprint contract parse (optional, post-freeze)**: read `references/checks/sprint-contract.md` and execute the parser. Always capture the resulting branch state (B1/B2/B3/B4/B5); capture extracted In Scope items only when state is B4 or B2.
2. **Section 1-4 render** (always): emit Score Summary + LAV Item Rationale (with counterfactual column from LAV-time generation, see `references/checks/lav.md` Counterfactual Generation section) + Bucket Rationale + Recommendations Linkage (3-state branch by `local/recommendations.json` state).
3. **Section 5 conditional render**: if sprint-contract parse reached B4 (valid) or B2 (frontmatter advisory), emit Sprint Contract Coverage with In Scope ↔ LAV mapping (P4 alignment rule). Otherwise omit.
4. **Negative-transparency filter** (S5): apply forbidden-token filter to generator-authored regions only. User-quoted content (CLAUDE.md evidence, sprint contract labels/bodies, and file paths, command strings, and identifiers extracted from the audited project) passes through verbatim.
5. **Write target**: `local/qa-report.md`. If `local/` is unwritable (same check that triggers stateless mode per Phase 1 Global Invariant #6) or stateless mode is active, render to terminal output instead of writing — no silent skip.

**Invocation-agnostic**: this phase MUST NOT branch on invocation context (subagent / reviewer / direct user / hook-triggered). The same write/terminal rule applies in every context.

## Phase 5: Persist Results & Learn

Read `../../references/learning-system.md` and follow the **Common Final Phase** steps with these audit-specific overrides:

- **Step 1 override (Skill-specific data in changelog entry):**
  The `config-changelog.md` entry for `/audit` must include:
  - `Detected:` — project changes observed (framework/package manager/testing etc. diffs).
  - `Profile updated:` — sections refreshed this run (for `/audit`, always all owned sections; see below).
  - `Applied:` — always `(none)` for `/audit` (audit does not mutate user files).
  - `Recommendations:` — all PENDING/DECLINED items emitted this run with appropriate status.
  For DECLINED items, increment `decline_count` per `plugin/references/lib/merge_rules.md §recommendations.json merge rules`: PENDING -> DECLINED sets `decline_count = 1`; DECLINED -> DECLINED re-record increments `decline_count++`. Monotonic — never decremented. Writes always emit schema 1.1.0; reading a 1.0.0 file performs lazy migration (inflate missing `decline_count` to 0). The repeated-decline trigger in `plugin/hooks/session-start.{sh,ps1}` reads this field after status==DECLINED filter and renders `"declined N times total"` for the rec with the highest `decline_count`.

  The score itself (`XX/100`, grade, maturity level) is a user-facing snapshot surfaced in the terminal output of Phase 4 and in `state-summary.md`'s Recent Skill Results section. It must NOT be written into the `config-changelog.md` entry as a field — the changelog is learning data, not a report ledger.

  Profile merge under the state-mutation lock: `/audit` is the authoritative full refresh (Layer 3 of stale prevention). Always regenerate all `/audit`-owned sections — `runtime_and_language`, `framework_and_libraries`, `package_management`, `testing`, `build_and_dev`, `project_structure`, `monorepo_detection`, and `claude_code_configuration_state.claude_md` — from detected state, regardless of whether changes were detected. When `monorepo_detection.detected` flips from `true` to `false` or `null`, full-replace regeneration must clear stale `claude_md.subpackages` and reset `claude_md.subpackage_coverage` counters per `merge_rules.md` full-replace semantics. Other sections (e.g., `claude_code_configuration_state.settings_json` owned by `/secure`) must be preserved from the re-read `current_profile` (see `plugin/references/lib/merge_rules.md` §profile.json merge rules).

  **A1 merge rule amendments** (applied summary; mechanism in `plugin/references/lib/merge_rules.md`):
  - **Row 1 — `claude_code_configuration_state.model`**: any-skill writer; last-write-wins; written at Step 0.5 and Final Phase. Stateless mode: no-op (Phase 1 Global Invariant #6).
  - **Row 2 — `claude_code_configuration_state.scoring_model_ack`**: `/audit` exclusive writer; full-object replacement; Final Phase only. Stateless mode: no-op.
  - **Row 3 — `config-changelog.md` entry `- Model:` bullet**: `/audit` always-emits per the shared hybrid writer policy. See `plugin/references/learning-system.md § Model Bullet Emission` for full mechanics; this skill's branch is the always-emit terminator (Phase 1 baseline already re-reads `current_changelog`, and `/audit` does not branch on the re-read value).

- **Stateless guard (Phase 5 top-level branch)**: if `local/` is unwritable (Phase 1 Global Invariant #6):
  - SKIP Step 2 `scoring_model_ack` re-read.
  - SKIP Step 3 ack delta computation + scoring-model-change banner trigger (persistence-backed banner fully skipped to avoid double-warning after stateless degradation notice).
  - RETAIN drift advisory derivation — current-state transient, no file write.
  - Proceed to Phase 1 Global Invariant #6 degradation warning; no JSON state writes, no changelog write.

  Non-stateless path continues below.

- **Step 2 additions (re-read under lock, `/audit`-specific fields):**
  - Re-read `profile.claude_code_configuration_state.model` for drift advisory baseline input.
  - Re-read `profile.claude_code_configuration_state.scoring_model_ack` for scoring-contract-change banner trigger decision.

- **Step 3 additions (compute deltas):**
  - **Final Phase model write** — set `profile.claude_code_configuration_state.model = <resolver output>`; merge under A1 Row 1 last-write-wins.
  - **Scoring-model-change banner** (copy: "Scoring contract changed" — must NOT collide with the drift advisory copy "Model drift since last /audit"): apply the trigger rule:

    ```
    if ack.version != current_scoring_contract_id OR ack.seen_count < 2:
        schedule banner render;
        ack.version = current_scoring_contract_id;
        ack.seen_count = min(ack.seen_count + 1, 2)
    else:
        silent
    ```

    **Stateless skip**: when `local/` is unwritable, the banner trigger is fully skipped — no ack read, no ack mutation, no banner render — to avoid double-warning after stateless degradation notice.
  - **Drift advisory — terminal render trigger** (derivation lives in shared `plugin/references/learning-system.md § Drift Advisory Derivation`; this block specifies only the `/audit` terminal render):
    1. On `drift` state returned from the shared derivation, render the terminal drift block per `references/output-format.md` (between Score line and ★ Most impactful; changed-axes-only + baseline annotation + no severity label).
    2. On `match` / `missing_baseline` / `normalization_null` states: terminal is silent (symmetric with state-summary header silence).
    3. Advisory is **transient** — NOT added to `recommendations.json` (see `plugin/references/learning-system.md § Drift Advisory Derivation` Transience clause).
    4. **Stateless mode**: drift advisory retained — current-state derived from in-memory changelog snapshot; when no baseline is available, advisory resolves to `missing_baseline` silence. `/audit` terminal render proceeds even without `local/` persistence; `state-summary.md` is not written in stateless mode (Final Phase Step 1 fully skipped).

- **Step 5 additions (atomic write):**
  - Write `.model` into `profile.json` (part of `profile.json` file set; no new lock primitive).
  - Write updated `scoring_model_ack` when banner fired (A1 Row 2 full-object replacement).

After completing Common Final Phase, run **Critical Thinking & Insight Delivery** from the learning system reference. Apply Socratic verification to audit recommendations before presenting them.
