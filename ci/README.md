# CI Smoke Lane

Canonical regression fixtures + golden snapshots for Guardians-of-the-Claude. CI runs this lane via `.github/workflows/smoke.yml`.

## Structure

- `fixtures/{name}/input/` — inputs fed to the Python reference verifier
- `fixtures/{name}/expected/` — intended output (authored by humans)
- `golden/{name}/` — frozen reference snapshot (byte-for-byte target)
- `scripts/run-smoke.{sh,ps1}` — runs verifier across all fixtures
- `scripts/compare-golden.{sh,ps1}` — diff helper for local debugging
- `scripts/build-manifest.{sh,ps1}` — generates eval-manifest.json

**Verifier references (read-only)**: `plugin/references/schemas/*.schema.json`, `plugin/references/recommendation-registry.json` — the plugin's canonical schemas + registry. Fixtures exercise them but do not duplicate them.

## Out of scope

- **Multi-process OS-race testing** — actual concurrent-process scheduling and OS-level filesystem-lock races are environment-dependent (vary by platform); manual testing recommended. The *deterministic* state-lock concurrency fixtures that simulate these scenarios (`state-lock-concurrent`, `state-lock-occ-conflict`, `state-lock-torn`, `state-lock-genesis`) **are** in the smoke lane.
- **Partial recovery fixtures** (e.g., `profile.json` corrupt + `recommendations.json` valid) — covered by separate local tooling outside the canonical CI lane.

## Atomic fixture runners

For faster iteration during fixture development, individual fixtures can be exercised via dedicated runners instead of the full smoke run:

- `scripts/t3_model_drift_check.py` — `t3-model-drift` (the 16-case model-fingerprint conformance suite over `test-cases.json`)
- `scripts/t7_optimize_e2e_check.py` — `t7-optimize-e2e`
- `scripts/t7_secure_counts_check.py` — `t7-secure-counts`
- `scripts/t7_secure_e2e_check.py` — `t7-secure-e2e`

These runners are CI-gated by the `atomic-fixture-runners-check` job in `.github/workflows/docs-check.yml`, which runs them on every push to `main`, on pull requests, and on version tags. They remain runnable standalone for fast local iteration. Note the **smoke** lane (`run-smoke.sh`) still does **not** execute them: `check-smoke-fixtures.py` imports the t3 `model-drift-rules.md` parser for the drift-state fixtures but does not run `test-cases.json`, and the `t7-*` scenarios are not in the smoke fixture set — the docs-check job is their gate.

## Running locally

**Prerequisites:** Python 3.x with `pip install jsonschema==4.23.0 pyyaml==6.0.2` (matching `.github/workflows/smoke.yml`), `jq` on `PATH` (a hard dependency of the SessionStart hook the fixtures exercise), and a POSIX `bash` (Git Bash on Windows — the verifier prefers the Git Bash binary over WSL bash).

```bash
bash ci/scripts/run-smoke.sh
```

On Windows:

```powershell
pwsh ci/scripts/run-smoke.ps1
```
