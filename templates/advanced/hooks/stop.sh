#!/usr/bin/env bash
# Stop hook -- appends one entry per turn (Claude finishes responding).
# Note: Stop fires per-turn, not per-session-end.
# Always exits 0 -- observability hook does not block.

set -e
trap 'exit 0' EXIT

OUT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}/.claude/local/hooks"
OUT_FILE="$OUT_DIR/turn-log.md"
mkdir -p "$OUT_DIR"

STDIN_JSON=$(cat)
SESSION_ID=$(printf '%s' "$STDIN_JSON" | grep -oE '"session_id"[[:space:]]*:[[:space:]]*"[^"]*"' | sed -E 's/.*"([^"]*)"$/\1/' || true)
[ -z "$SESSION_ID" ] && SESSION_ID="(unknown)"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
PWD_VAL=$(pwd)
BRANCH=$(git branch --show-current 2>/dev/null || true)
if [ -z "$BRANCH" ]; then
  BRANCH=$(git rev-parse --short HEAD 2>/dev/null || echo "(not a git repo)")
fi
MODIFIED_COUNT=$(git diff --name-only HEAD 2>/dev/null | wc -l | tr -d ' ' || echo "0")
[ -z "$MODIFIED_COUNT" ] && MODIFIED_COUNT="0"

cat >> "$OUT_FILE" <<EOF
## Turn $TIMESTAMP

- **Session ID**: $SESSION_ID
- **Working dir**: $PWD_VAL
- **Branch**: $BRANCH
- **Modified files (vs HEAD)**: $MODIFIED_COUNT

---
EOF

exit 0
