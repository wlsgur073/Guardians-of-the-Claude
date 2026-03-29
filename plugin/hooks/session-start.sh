#!/usr/bin/env bash

if [ ! -f "CLAUDE.md" ] && [ ! -f ".claude/settings.json" ]; then
  cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "This project has no Claude Code configuration yet. The claude-code-template plugin is installed — suggest the user run /claude-code-template:generate to set up CLAUDE.md and .claude/ configuration through a guided interview."
  }
}
EOF
fi

exit 0
