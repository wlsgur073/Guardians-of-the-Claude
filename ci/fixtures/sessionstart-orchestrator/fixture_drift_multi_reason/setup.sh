#!/usr/bin/env bash
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
touch -t 202604140000 "$HERE/input/.claude/.plugin-cache/guardians-of-the-claude/local/profile.json"
touch -t 202605070000 "$HERE/input/package.json"
