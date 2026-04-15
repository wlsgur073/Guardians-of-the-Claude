#!/usr/bin/env bash
# Debug helper: compare fixtures/<name>/expected/ against golden/<name>/ for
# maintainers authoring new fixtures. Primarily useful when the expected/
# authorship tree drifts from the frozen golden snapshot.
set -euo pipefail
cd "$(dirname "$0")/../.."

names=("migration" "beginner-path" "warm-start" "monorepo")
if [ "$#" -gt 0 ]; then
  names=("$@")
fi

rc=0
for name in "${names[@]}"; do
  expected="ci/fixtures/${name}/expected"
  golden="ci/golden/${name}"
  if [ ! -d "$expected" ] || [ ! -d "$golden" ]; then
    echo "[SKIP] ${name}: missing expected/ or golden/"
    continue
  fi
  echo "=== ${name}: expected vs golden ==="
  if diff -r "$expected" "$golden"; then
    echo "[OK] ${name}"
  else
    rc=1
  fi
done
exit "$rc"
