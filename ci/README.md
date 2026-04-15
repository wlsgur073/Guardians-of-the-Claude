# CI Smoke Lane

Canonical smoke fixtures + golden snapshots for CI regression testing of
Guardians-of-the-Claude. Scope and policy per Phase 0 spec
(`docs/superpowers/v3-roadmap/phase-0-design.md` §4).

## Structure

- `fixtures/{name}/input/` — inputs fed to the Python reference verifier
- `fixtures/{name}/expected/` — intended output (authored by humans)
- `golden/{name}/` — frozen reference snapshot (byte-for-byte target)
- `scripts/run-smoke.sh` (+ `.ps1`) — runs verifier across all 4 fixtures
- `scripts/compare-golden.sh` (+ `.ps1`) — diff helper for local debugging
- `scripts/build-manifest.sh` (+ `.ps1`) — generates eval-manifest.json

**Verifier references (read-only)**: `plugin/references/schemas/*.schema.json`, `plugin/references/recommendation-registry.json`. These are the plugin's canonical schemas + registry — fixtures exercise them but do not duplicate them.

## Out of scope (Phase 1)

**Concurrency fixtures** — CI concurrency testing is environment-dependent (process scheduling, filesystem lock behavior across platforms). Phase 1 smoke lane does NOT cover multi-skill concurrent Final Phase runs; manual testing is the recommended approach. Revisit in Phase 2+ if automation becomes tractable.

**Partial recovery fixtures** (e.g., `profile.json` corrupt + `recommendations.json` valid) — Phase 0 Q4 decision caps smoke lane at 4 fixtures. Partial recovery cases live in gitignored `test/fixtures/migration/` (Task 7).

## Transitional Bridge

Until this lane is fully automated + covers all release gates, the wider
evaluation stays in local gitignored `test/` (maintainer-only). Bridge
exit condition: **before v3.0 or before second maintainer — whichever
comes first — smoke lane must cover all release-gate checks**. See
phase-0-design.md §4.5.

## Running locally

```bash
bash ci/scripts/run-smoke.sh
```

On Windows:

```powershell
pwsh ci/scripts/run-smoke.ps1
```

## Maintainer-only local lane (gitignored)

The verifier also supports iterating over a local directory of case
subdirectories via the `LOCAL_FIXTURES_DIR` environment variable. Used for
Task 7 parser robustness cases under gitignored `test/fixtures/migration/`
(not shipped; maintainer-local only):

```bash
LOCAL_FIXTURES_DIR=test/fixtures/migration \
SMOKE_PINNED_UTC="2026-04-14T00:00:00Z" \
python .github/scripts/check-smoke-fixtures.py
```

Each subdirectory (`case-XX/`) must contain `input/` and `expected/`. An
optional `scenario.json` overrides the default migration-only scenario
(`{"skill_sequence": [], "pre_run": []}`). Shared verifier — same 5
semantic assertions as the CI lane, no duplicated logic.
