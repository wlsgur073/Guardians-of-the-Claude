#!/usr/bin/env bash
# Force profile.json to be the newest mtime in input/.
# Defense against git checkout lexicographic order + ext4 high-resolution mtime
# that can otherwise leave .claude/settings.json newer than profile.json on
# Linux runners and false-fire legacy_mtime drift.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
find "$HERE/input" -type f -exec touch -t 202604140000 {} +
touch -t 202605070000 "$HERE/input/.claude/.plugin-cache/guardians-of-the-claude/local/profile.json"
