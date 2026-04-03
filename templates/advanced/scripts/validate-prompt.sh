#!/usr/bin/env bash
# Warns when user prompt mentions migration-related keywords.
# Used as a UserPromptSubmit hook to prevent accidental migration changes.

PROMPT_TEXT=$(cat)

if echo "$PROMPT_TEXT" | grep -qiE '(migration|migrate|schema change|alter table|drop table)'; then
  echo "Migration-related keywords detected. Remember:"
  echo "  - Migration files are protected (PreToolUse hook blocks edits)"
  echo "  - Run 'npm run migrate' to apply existing migrations"
  echo "  - Create new migrations with 'npm run migrate:create <name>'"
  exit 0
fi

exit 0
