#!/usr/bin/env bash
# Force package.json mtime newer than profile.json mtime.
# Profile is touched to a base time; package.json to a later time.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
touch -t 202604140000 "$HERE/input/.claude/.plugin-cache/guardians-of-the-claude/local/profile.json"
touch -t 202605070000 "$HERE/input/package.json"
