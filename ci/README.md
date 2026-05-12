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

- **Concurrency fixtures** — environment-dependent (process scheduling, filesystem lock behavior vary by platform); manual testing recommended.
- **Partial recovery fixtures** (e.g., `profile.json` corrupt + `recommendations.json` valid) — covered by separate local tooling outside the canonical CI lane.

## Atomic fixture runners

For faster iteration during fixture development, individual fixtures can be exercised via dedicated runners instead of the full smoke run:

- `scripts/t3_model_drift_check.py` — `t3-model-drift` (also imported by `.github/scripts/check-smoke-fixtures.py` for the full smoke run)
- `scripts/t7_optimize_e2e_check.py` — `t7-optimize-e2e`
- `scripts/t7_secure_counts_check.py` — `t7-secure-counts`
- `scripts/t7_secure_e2e_check.py` — `t7-secure-e2e`

These are not wired into a separate CI job because the full smoke run (`run-smoke.sh`) covers the same scenarios; they exist as local-only debugging entry points.

## Running locally

```bash
bash ci/scripts/run-smoke.sh
```

On Windows:

```powershell
pwsh ci/scripts/run-smoke.ps1
```
