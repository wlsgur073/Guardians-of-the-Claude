# Privacy Policy

## guardians-of-the-claude plugin

The plugin's own code (skills, hook, and helper scripts) contacts no remote endpoints. It does write local state files inside your project directory to support cross-skill learning (recommendation history, decision journal, derived state snapshot). Because the plugin runs inside Claude Code, everything that enters the conversation (your prompts, the project files Claude reads while running the skills, the `SessionStart` hook's short state digest, and Claude's outputs) goes to your configured model provider like any other Claude Code conversation, under Claude Code's [data usage](https://code.claude.com/docs/en/data-usage) policies.

### What this plugin does

- Runs an interactive interview inside Claude Code
- Generates configuration files (CLAUDE.md, settings.json, rules, hooks, agents, skills) locally in your project directory
- Writes local state files under `<project-root>/.claude/.plugin-cache/guardians-of-the-claude/local/` — `profile.json`, `recommendations.json`, `config-changelog.md`, `state-summary.md`, `qa-report.md`, and (during legacy-format migration) `legacy-backup/<ISO-8601-UTC>/`. These files contain detected project metadata (language/framework/tooling), recommendation history with PENDING/RESOLVED/DECLINED statuses, and a decision journal of skill runs
- Reads some local Claude Code data outside the project, read-only: `/audit`'s usage report runs `plugin/references/lib/usage-parser.sh`, which aggregates token counts and metadata (model, timestamps, session IDs, tool names; never message text) from the session transcripts Claude Code keeps under `~/.claude/projects/` (or `$CLAUDE_CONFIG_DIR/projects/`) for **all** your local projects; `/secure` and `/optimize` read `~/.claude/guardians/config.json` (or `$CLAUDE_CONFIG_DIR/guardians/config.json`) when it exists; and `/secure` checks your user-level `~/.claude/settings.json` and managed settings for `autoMode.environment`

### What this plugin does NOT do

- Does not collect analytics or telemetry
- Does not send data to external servers
- Does not access the network
- Does not write any files outside your project directory
- Does not include any of your project content in the plugin or marketplace metadata

### Stateless mode

If `local/` cannot be written (read-only mount, privacy-sensitive project, user-disabled), the skills automatically enter stateless mode — they print a one-time warning and skip all state file writes. Cross-skill learning is disabled in this mode but the skills still run. See the README "v2.11+ State Format & Stateless Mode" section for details.

### Contact

If you have questions about this privacy policy, open an issue at [github.com/wlsgur073/guardians-of-the-claude](https://github.com/wlsgur073/guardians-of-the-claude/issues).
