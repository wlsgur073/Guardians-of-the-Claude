#!/usr/bin/env bash
# UserPromptSubmit hook: reminds Claude about migration safeguards when the prompt
# mentions migration-related keywords. Plain stdout on exit 0 is added to Claude's
# context (not shown in the transcript). Matches only the `prompt` field: the payload
# also carries cwd, transcript_path and (when a custom title is set) session_title.

PROMPT_TEXT=$(jq -r '.prompt // empty' 2>/dev/null)

if printf '%s' "$PROMPT_TEXT" | grep -qiE '(migration|migrate|schema change|alter table|drop table)'; then
  echo "Migration-related keywords detected. Remember:"
  echo "  - Migration files are protected (PreToolUse hook blocks edits)"
  echo "  - Run 'npm run migrate' to apply existing migrations"
  echo "  - Create new migrations with 'npm run migrate:create <name>'"
fi

exit 0
