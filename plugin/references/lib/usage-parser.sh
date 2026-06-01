#!/usr/bin/env bash
# plugin/references/lib/usage-parser.sh — read-only token-usage summary over local transcripts.
# Reads ~/.claude/projects/**/*.jsonl, aggregates token counts + heuristic attribution,
# emits a compact JSON summary on stdout. NEVER selects or emits message text content — counts and
# metadata (model, timestamps, tool names) only. Zero network. jq is a hard dependency
# (matches plugin/hooks/session-start.sh). Fails open: bad lines are skipped, missing
# fields default to 0/empty, a missing/unreadable projects dir yields an empty-but-valid summary.
# jq absence is a hard-dependency error (nonzero exit), NOT a fail-open case (see guard below).
set -uo pipefail   # NOTE: no -e — a single bad transcript line must not abort the run.

PROJECTS_DIR="${GUARDIANS_USAGE_PROJECTS_DIR:-${CLAUDE_CONFIG_DIR:-${HOME:-}/.claude}/projects}"
PRICES="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/model-prices.json"

emit_empty() {
  jq -n '{
    schema_version: "1.0.0",
    window: { sessions: 0, first: null, last: null },
    totals: { input: 0, output: 0, cache_read: 0, cache_creation: 0, est_cost_usd: 0, cost_tier: "local-estimate", unknown_models: [] },
    by_model: [],
    cache: { cache_read_ratio: 0 },
    by_day: [],
    top_sessions: [],
    attribution: {
      method: "heuristic",
      by_tool: [],
      by_mcp_server: [],
      by_skill: [ { name: "Skill", invocations: 0 } ],
      main_vs_subagent: { main: 0, subagent: 0 }
    }
  }'
}

if ! command -v jq >/dev/null 2>&1; then
  echo "usage-parser.sh: jq not found on PATH (hard dependency); cannot produce a summary" >&2
  exit 3
fi
if [ ! -d "$PROJECTS_DIR" ]; then
  emit_empty; exit 0
fi

# Pass 1 — one usage record per assistant message (session = file basename).
records=$(
  find "$PROJECTS_DIR" -type f -name '*.jsonl' 2>/dev/null | while IFS= read -r f; do
    jq -cR --arg session "$(basename "$f" .jsonl)" '
      fromjson?
      | select(.type=="assistant" and (.message.usage != null))
      | { session:$session, ts:(.timestamp // ""), model:(.message.model | strings // "unknown"),
          sidechain:(.isSidechain // false),
          i:(.message.usage.input_tokens | numbers // 0), o:(.message.usage.output_tokens | numbers // 0),
          cr:(.message.usage.cache_read_input_tokens | numbers // 0),
          cc:(.message.usage.cache_creation_input_tokens | numbers // 0) }
    ' "$f" 2>/dev/null
  done
)

# Pass 2 — tool/MCP/skill invocation counts (attribution, heuristic).
tools=$(
  find "$PROJECTS_DIR" -type f -name '*.jsonl' 2>/dev/null | while IFS= read -r f; do
    jq -cR 'fromjson? | select(.type=="assistant") | .message.content[]?
           | select(.type=="tool_use") | {name:.name}' "$f" 2>/dev/null
  done
)

[ -z "$records" ] && { emit_empty; exit 0; }

# Aggregate. Prices joined in jq; cost is a labelled local estimate.
printf '%s\n' "$records" | jq -s \
  --slurpfile prices "$PRICES" \
  --argjson toolarr "$(printf '%s\n' "$tools" | jq -s '.')" '
  ($prices[0].prices) as $P | ($prices[0].default) as $D |
  def price(m): ($P[m] // $D);
  {
    schema_version:"1.0.0",
    window:{ sessions:( [.[].session] | unique | length ),
             first:( [.[].ts] | map(select(.!="")) | min ),
             last:(  [.[].ts] | map(select(.!="")) | max ) },
    totals:( reduce .[] as $r ({i:0,o:0,cr:0,cc:0}; {i:(.i+$r.i),o:(.o+$r.o),cr:(.cr+$r.cr),cc:(.cc+$r.cc)}) )
      | { input:.i, output:.o, cache_read:.cr, cache_creation:.cc },
    by_model:( group_by(.model) | map({ model:.[0].model,
        input:(map(.i)|add), output:(map(.o)|add),
        cache_read:(map(.cr)|add), cache_creation:(map(.cc)|add) }) ),
    by_day:( group_by(.ts[0:10]) | map({ date:(.[0].ts[0:10]),
        input:(map(.i)|add), output:(map(.o)|add) }) | map(select(.date!="")) ),
    top_sessions:( group_by(.session)
        | map({ session:.[0].session, tokens:(map(.i+.o)|add) })
        | sort_by(-.tokens) | .[0:5] ),
    main_vs_subagent:( { main:( map(select(.sidechain|not)) | length ),
                         subagent:( map(select(.sidechain)) | length ) } )
  }
  | .cache = { cache_read_ratio: ( if (.totals.input + .totals.cache_read + .totals.cache_creation) > 0
        then ((.totals.cache_read) / (.totals.input + .totals.cache_read + .totals.cache_creation) * 100 | floor) / 100 else 0 end ) }
  | .totals.est_cost_usd = ( [ .by_model[]
        | (price(.model)) as $p
        | (.input/1e6*$p.input + .output/1e6*$p.output
           + .cache_read/1e6*$p.cache_read + .cache_creation/1e6*$p.cache_creation) ] | add | (.*100|round)/100 )
  | .totals.cost_tier = "local-estimate"
  | .totals.unknown_models = ( [ .by_model[].model ] | map(select($P[.] == null)) )
  | .attribution = { method:"heuristic",
      by_tool:( $toolarr | group_by(.name) | map({name:.[0].name, invocations:length}) | sort_by(-.invocations) ),
      # capture the full server segment between the __ delimiters (mcp__plugin_github_github__x -> "plugin_github_github"; mcp__github__x -> "github")
      by_mcp_server:( $toolarr | map(.name) | map(select(startswith("mcp__")))
          | map(try (capture("^mcp__(?<s>[A-Za-z0-9_]+)__") | .s)) | group_by(.)
          | map({name:.[0], invocations:length}) | sort_by(-.invocations) ),
      by_skill:( $toolarr | map(select(.name=="Skill")) | {name:"Skill", invocations:length} | [.] ),
      main_vs_subagent:.main_vs_subagent }
  | del(.main_vs_subagent)
'
