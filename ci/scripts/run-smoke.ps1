#!/usr/bin/env pwsh
# Run the smoke verifier over ci/fixtures/* and diff against ci/golden/*.
# Per Phase 1 Task 6 Step 8 (docs/superpowers/v3-roadmap/phase-1-plan.md).
$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot/../.."
if (-not $env:SMOKE_PINNED_UTC) { $env:SMOKE_PINNED_UTC = "2026-04-14T00:00:00Z" }
python .github/scripts/check-smoke-fixtures.py $args
exit $LASTEXITCODE
