#!/usr/bin/env bash
# SubagentStop hook -- appends one JSONL line per subagent completion.
# Always exits 0 -- observability hook does not block.

set -e
trap 'exit 0' EXIT

OUT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}/.claude/local/hooks"
OUT_FILE="$OUT_DIR/subagent-log.jsonl"
mkdir -p "$OUT_DIR"

STDIN_JSON=$(cat)

extract() {
  printf '%s' "$STDIN_JSON" | grep -oE "\"$1\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" | sed -E 's/.*"([^"]*)"$/\1/' || true
}

SESSION_ID=$(extract "session_id")
AGENT_ID=$(extract "agent_id")
AGENT_TYPE=$(extract "agent_type")

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
PWD_VAL=$(pwd)

emit_field() {
  if [ -z "$2" ]; then
    printf '"%s":null' "$1"
  else
    local escaped
    escaped=$(printf '%s' "$2" | sed 's/\\/\\\\/g; s/"/\\"/g')
    printf '"%s":"%s"' "$1" "$escaped"
  fi
}

LINE='{'
LINE+="\"ts\":\"$TIMESTAMP\","
LINE+="\"event\":\"subagent_stop\","
LINE+="$(emit_field session_id "$SESSION_ID"),"
LINE+="$(emit_field agent_id "$AGENT_ID"),"
LINE+="$(emit_field agent_type "$AGENT_TYPE"),"
LINE+="\"cwd\":\"$PWD_VAL\""
LINE+='}'

echo "$LINE" >> "$OUT_FILE"
exit 0
