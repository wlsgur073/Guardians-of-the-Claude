# Usage & Fitness Advisory (NON-SCORING)

This advisory is **non-scoring**: results route to Phase 4 "All Suggestions" terminal output and emit **registered** recommendation keys into `recommendations.json`. It MUST NOT alter any T1/T2/T3 item score, weight, or `scoring_contract_id` (`audit-score-v4.2.0`), and MUST NOT add a `qa-report.md` section.

## D2 — Primitive Fitness (non-scoring advisory)

For each automation/instruction found in config, check whether it lives in the right Claude Code primitive. Rule sources: `docs/guides/{memory-patterns,rules,settings,multi-agent-patterns,mcp}-guide.md`. Cross-reference project direction via the CLAUDE.md purpose statement and the audit sprint-contract scope.

| Signal (detect) | Misfit | Recommend (key) |
|---|---|---|
| CLAUDE.md contains a "whenever / each time / before / after X, do Y" imperative | Claude cannot self-trigger reliably | relocate to a hook → `vessel-fit` |
| CLAUDE.md embeds a long multi-step procedure (>~25 lines, ordered steps) | belongs in a skill | extract to a skill → `vessel-fit` |
| CLAUDE.md or an agent describes hardcoded external API/tool calls | belongs in MCP | add an MCP server → `vessel-fit` |

## D1 — Usage Analytics (non-scoring advisory, L2)

Invoke `plugin/references/lib/usage-parser.sh` and read its compact JSON summary — do NOT read raw `~/.claude/projects/*.jsonl` yourself (the helper already aggregates COUNTS only; reading raw transcripts wastes tokens and risks reading message content). The summary spans **all** your local Claude Code projects under `~/.claude/projects` (not just the current repo), so present the usage report as cross-project ("across your local Claude Code usage"), never as this project alone. If the summary is empty (`window.sessions == 0` — no transcripts), skip D1 silently. Then evaluate:

| Summary signal | Recommend (key) |
|---|---|
| a server configured in the project's `.mcp.json` does NOT appear in `attribution.by_mcp_server[]` — the helper lists only servers that were actually invoked, so an unused server is ABSENT from the list (it is never present with `invocations == 0`) | `mcp-unused` |
| `cache.cache_read_ratio < 0.3` (low prompt-cache reuse) | `cache-stabilize` |
| `attribution.main_vs_subagent.subagent` is a large share of activity AND an agent config uses a high effort tier / large model for mechanical work | `effort-downgrade` |

**Name-matching note:** the helper's `by_mcp_server` names are the full segment between the `mcp__…__` delimiters (e.g. `plugin_github_github`, or `github` for the bare form). When matching against `.mcp.json` server keys, compare tolerantly — a configured server may appear under either form. Only flag `mcp-unused` when you are confident the configured server genuinely had zero invocations over the window. Because `by_mcp_server` aggregates **all** local projects, absence proves only "not observed across your recent local usage," NOT "unused in this repo" — so emit `mcp-unused` as a **verify-only** signal (ask the user to confirm the server is not needed in this project), never as a confident disable.

**Honesty:** always label cost as a local estimate (cite `totals.cost_tier`) and as a **floor** — any model absent from the bundled price table is listed in `totals.unknown_models` and counted as $0, so true cost is higher whenever that list is non-empty. Label attribution as heuristic (`attribution.method == "heuristic"` — correlation, not exact). Keep `mcp-unused` conservative — a short window may simply not have exercised a legitimately-needed server.
