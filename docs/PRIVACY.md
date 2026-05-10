# Privacy Policy

## guardians-of-the-claude plugin

This plugin does not transmit any data outside your project. It does write local state files inside your project directory to support cross-skill learning (recommendation history, decision journal, derived state snapshot). All storage is local; no remote endpoints are contacted.

### What this plugin does

- Runs an interactive interview inside Claude Code
- Generates configuration files (CLAUDE.md, settings.json, rules, hooks, agents, skills) locally in your project directory
- Writes local state files under `<project-root>/.claude/.plugin-cache/guardians-of-the-claude/local/` — `profile.json`, `recommendations.json`, `config-changelog.md`, `state-summary.md`, `qa-report.md`, and (during legacy-format migration) `legacy-backup/<ISO-8601-UTC>/`. These files contain detected project metadata (language/framework/tooling), recommendation history with PENDING/RESOLVED/DECLINED statuses, and a decision journal of skill runs

### What this plugin does NOT do

- Does not collect analytics or telemetry
- Does not send data to external servers
- Does not access the network
- Does not write any files outside your project directory
- Does not include any of your project content in the plugin or marketplace metadata

### Stateless mode

If `local/` cannot be written (read-only mount, privacy-sensitive project, user-disabled), the skills automatically enter stateless mode — they print a one-time warning and skip all state file writes. Cross-skill learning is disabled in this mode but the skills still run. See the README "Unwritable `local/` handling" note for details.

### Contact

If you have questions about this privacy policy, open an issue at [github.com/wlsgur073/Guardians-of-the-Claude](https://github.com/wlsgur073/Guardians-of-the-Claude/issues).
