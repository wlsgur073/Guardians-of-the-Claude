#!/usr/bin/env bash
# Run the smoke verifier over ci/fixtures/* and diff against ci/golden/*.
# Per Phase 1 Task 6 Step 8 (docs/superpowers/v3-roadmap/phase-1-plan.md).
set -euo pipefail
cd "$(dirname "$0")/../.."
: "${SMOKE_PINNED_UTC:=2026-04-14T00:00:00Z}"
export SMOKE_PINNED_UTC
exec python .github/scripts/check-smoke-fixtures.py "$@"
