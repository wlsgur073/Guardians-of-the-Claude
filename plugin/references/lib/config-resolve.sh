#!/usr/bin/env bash
# plugin/references/lib/config-resolve.sh — resolve the effective Guardians config by
# deep-merging three tiers: bundled defaults < user-global < per-project (later wins).
# Scalars/objects: last-wins (jq *). Additive lists (additional_deny_patterns, skip):
# union+dedup across all present tiers. Emits {config, overrides, warnings} on stdout.
# Read-only; no network; no state mutation. jq is a hard dependency (matches
# plugin/hooks/session-start.sh). Degrades loud, never silent:
#   jq absent / defaults missing -> exit 3 (stderr)
#   malformed JSON in a tier      -> exit 4 (stderr names the file)
#   unknown/typo keys             -> reported in .warnings (non-fatal)
# Test injection: GUARDIANS_CONFIG_DEFAULTS, GUARDIANS_USER_CONFIG override the
# defaults and user-global paths (mirrors usage-parser.sh's env-var pattern).
set -uo pipefail

PROJECT_DIR="${1:-.}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULTS="${GUARDIANS_CONFIG_DEFAULTS:-$SCRIPT_DIR/guardians-config.defaults.json}"
USER_CONFIG="${GUARDIANS_USER_CONFIG:-${CLAUDE_CONFIG_DIR:-${HOME:-}/.claude}/guardians/config.json}"
PROJECT_CONFIG="$PROJECT_DIR/.claude/guardians/config.json"

if ! command -v jq >/dev/null 2>&1; then
  echo "config-resolve.sh: jq not found on PATH (hard dependency)" >&2; exit 3
fi
if [ ! -f "$DEFAULTS" ]; then
  echo "config-resolve.sh: bundled defaults missing at $DEFAULTS" >&2; exit 3
fi

tier_files=(); tier_names=()
add_tier() { # $1=path $2=name
  [ -f "$1" ] || return 0
  if ! jq -e . "$1" >/dev/null 2>&1; then
    echo "config-resolve.sh: invalid JSON in $2 config at $1" >&2; exit 4
  fi
  tier_files+=("$1"); tier_names+=("$2")
}
add_tier "$DEFAULTS" "default"
add_tier "$USER_CONFIG" "user"
add_tier "$PROJECT_CONFIG" "project"

names_json="$(printf '%s\n' "${tier_names[@]}" | jq -R . | jq -s .)"
tiers_json="$(jq -s '.' "${tier_files[@]}")"

jq -n --argjson tiers "$tiers_json" --argjson names "$names_json" '
  def keyset:
    [ to_entries[]
      | if (.value | type) == "object"
        then (.key) as $s | (.value | keys_unsorted[] | "\($s).\(.)")
        else .key end ];
  ($tiers[0]) as $def
  | ($def | keyset) as $defkeys
  | (reduce $tiers[] as $c ({}; . * $c)) as $m
  | ($m
      | (if (.secure? | type) == "object"
         then .secure.additional_deny_patterns =
              ([ $tiers[].secure.additional_deny_patterns? // empty ] | add // [] | unique)
         else . end)
      | (if (.optimize? | type) == "object"
         then .optimize.skip =
              ([ $tiers[].optimize.skip? // empty ] | add // [] | unique)
         else . end)
    ) as $config
  | ([ range(1; ($tiers | length)) as $i | ($tiers[$i] | keyset[]) ] | unique) as $userkeys
  | ($userkeys - $defkeys) as $unknown
  | ([ range(1; ($tiers | length)) as $i
        | ($tiers[$i] | keyset[]) as $k
        | select($defkeys | index($k))
        | { key: $k, tier: $names[$i] } ]
      | group_by(.key) | map({ key: .[0].key, tiers: (map(.tier) | unique) })) as $overrides
  | { config: $config,
      overrides: $overrides,
      warnings: ($unknown | map({ key: ., warning: "unknown key (not in defaults); ignored" })) }
'
