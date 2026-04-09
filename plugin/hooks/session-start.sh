#!/usr/bin/env bash
PROFILE=".claude/.plugin-cache/guardians-of-the-claude/local/project-profile.md"
OLD_CACHE=".claude/.plugin-cache/claude-code-template"
NEW_CACHE=".claude/.plugin-cache/guardians-of-the-claude"

# Migration: rename old cache directory if it exists
if [ -d "$OLD_CACHE" ] && [ ! -d "$NEW_CACHE" ]; then
  mv "$OLD_CACHE" "$NEW_CACHE"
fi

# Case 1: No Claude Code configuration at all
if [ ! -f "CLAUDE.md" ] && [ ! -f ".claude/settings.json" ]; then
  cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "This project has no Claude Code configuration yet. The guardians-of-the-claude plugin is installed — suggest the user run /guardians-of-the-claude:create to set up CLAUDE.md and .claude/ configuration through a guided interview."
  }
}
EOF
  exit 0
fi

# Case 2: Configuration exists but no profile yet
if [ ! -f "$PROFILE" ]; then
  cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Claude Code configuration exists but no project profile has been generated yet. Running /guardians-of-the-claude:audit will generate a project profile for more accurate recommendations across all skills."
  }
}
EOF
  exit 0
fi

# Case 3: Profile exists — check for staleness
STALE="false"
for f in package.json tsconfig.json pyproject.toml go.mod Cargo.toml \
         pom.xml Gemfile requirements.txt .claude/settings.json; do
  if [ -f "$f" ] && [ "$f" -nt "$PROFILE" ]; then
    STALE="true"
    STALE_FILE="$f"
    break
  fi
done

if [ "$STALE" = "true" ]; then
  cat << EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Project profile may be outdated — $STALE_FILE was modified since the last profile update. Running /guardians-of-the-claude:audit will refresh the profile and check for new recommendations."
  }
}
EOF
  exit 0
fi

# Case 4: Everything is fresh — no additional context needed
exit 0
