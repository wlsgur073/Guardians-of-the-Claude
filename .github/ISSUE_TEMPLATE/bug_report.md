---
name: Bug report
about: Something in this plugin or a shipped template is not behaving as documented
labels: bug
---

## What happened

What did you run, what did Claude do, what did you expect?

## Reproduction

1. Install method: (DPT-style local marketplace / `--plugin-dir` / `@`-import / direct paste)
2. Command run: `/guardians-of-the-claude:...`
3. Project state at run time: (new project / existing project with no Claude config / existing with Claude config)

## Environment

- OS: (Linux / macOS / Windows + Git Bash / Windows + WSL)
- Claude Code version: `claude --version`
- Plugin version: see `plugin/.claude-plugin/plugin.json` (`version` field)
- `bash` version: `bash --version | head -1`
- `jq` version: `jq --version`

## Output / logs

```text
(paste error output or unexpected skill output here)
```
