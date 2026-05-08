#!/usr/bin/env bash
# PreCompact hook -- captures pre-compact snapshot for post-compaction debugging.
# Trigger: per-compaction (manual or auto). Output: file-only.
# Always exits 0 -- observability hook does not block compaction.

set -e
trap 'exit 0' EXIT

OUT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}/.claude/local/hooks"
OUT_FILE="$OUT_DIR/pre-compact-snapshot.md"
mkdir -p "$OUT_DIR"

STDIN_JSON=$(cat)
SESSION_ID=$(printf '%s' "$STDIN_JSON" | grep -oE '"session_id"[[:space:]]*:[[:space:]]*"[^"]*"' | sed -E 's/.*"([^"]*)"$/\1/' || true)
TRIGGER=$(printf '%s' "$STDIN_JSON" | grep -oE '"trigger"[[:space:]]*:[[:space:]]*"[^"]*"' | sed -E 's/.*"([^"]*)"$/\1/' || true)
[ -z "$SESSION_ID" ] && SESSION_ID="(unknown)"
[ -z "$TRIGGER" ] && TRIGGER="(unspecified)"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
PWD_VAL=$(pwd)
BRANCH=$(git branch --show-current 2>/dev/null || true)
if [ -z "$BRANCH" ]; then
  BRANCH=$(git rev-parse --short HEAD 2>/dev/null || echo "(not a git repo)")
fi
GIT_STATUS=$(git status --porcelain 2>/dev/null || echo "(not a git repo)")
[ -z "$GIT_STATUS" ] && GIT_STATUS="(clean)"
RECENT_COMMITS=$(git log -5 --oneline 2>/dev/null || echo "(no commits)")

DENY_RE='(KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|AUTH|BEARER|DATABASE_URL|DB_URL|REDIS_URL|MONGO_URI|AWS_|GITHUB_|STRIPE_|ANTHROPIC_|OPENAI_|API_)'
ALLOW_RE='^(NODE_ENV|PORT|CI|LANG|LC_.*|TZ|PWD|CLAUDE_PROJECT_DIR|CLAUDE_CODE_REMOTE)$'
ENV_OUT=""
while IFS='=' read -r name val; do
  [ -z "$name" ] && continue
  if printf '%s' "$name" | grep -qE "$ALLOW_RE"; then
    if printf '%s' "$name" | grep -iqE "$DENY_RE"; then
      continue
    fi
    ENV_OUT="${ENV_OUT}${name}=${val}"$'\n'
  fi
done < <(env)

cat > "$OUT_FILE" <<EOF
# Pre-Compact Snapshot

**Timestamp**: $TIMESTAMP
**Session ID**: $SESSION_ID
**Trigger**: $TRIGGER
**Working dir**: $PWD_VAL
**Branch**: $BRANCH

## Git Status
\`\`\`
$GIT_STATUS
\`\`\`

## Recent Commits
\`\`\`
$RECENT_COMMITS
\`\`\`

## Environment (sanitized)
\`\`\`
$ENV_OUT
\`\`\`
EOF

exit 0
