# Usage & Fitness Advisory (NON-SCORING)

This advisory is **non-scoring**: results route to Phase 4 "All Suggestions" terminal output and emit **registered** recommendation keys into `recommendations.json`. It MUST NOT alter any T1/T2/T3 item score, weight, or `scoring_contract_id` (`audit-score-v4.2.0`), and MUST NOT add a `qa-report.md` section.

## D2 — Primitive Fitness (non-scoring advisory)

For each automation/instruction found in config, check whether it lives in the right Claude Code primitive. Rule sources: `docs/guides/{memory-patterns,rules,settings,multi-agent-patterns,mcp}-guide.md`. Cross-reference project direction via the CLAUDE.md purpose statement and the audit sprint-contract scope.

| Signal (detect) | Misfit | Recommend (key) |
|---|---|---|
| CLAUDE.md contains a "whenever / each time / before / after X, do Y" imperative | Claude cannot self-trigger reliably | relocate to a hook → `vessel-fit` |
| CLAUDE.md embeds a long multi-step procedure (>~25 lines, ordered steps) | belongs in a skill | extract to a skill → `vessel-fit` |
| CLAUDE.md or an agent describes hardcoded external API/tool calls | belongs in MCP | add an MCP server → `vessel-fit` |
