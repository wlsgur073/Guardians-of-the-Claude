---
title: "MCP Integration"
description: "Connecting Claude Code to external tools and services via Model Context Protocol"
version: 1.1.0
---

# MCP Integration

## What Is MCP?

Model Context Protocol (MCP) lets Claude Code connect to external tools — databases, APIs, documentation services. MCP servers expose tools Claude can call during a session — most run as local processes, though some connect to remote or hosted services.

## Configuration

Add servers with `claude mcp add` (see [Transports](#transports) below). It saves to local scope unless you pass `--scope project` or `--scope user`. Team-shared servers live in `.mcp.json` at your project root:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "@example/mcp-server"],
      "env": {
        "API_KEY": "${API_KEY}"
      }
    }
  }
}
```

Key fields:

- **`command`** -- how to launch the server (`npx`, `uvx`, `docker`, `node`, etc.)
- **`args`** -- arguments passed to the command
- **`env`** -- environment variables the server needs (API keys, connection strings)
- **`type`** -- `stdio` (assumed when omitted), `http`, `sse`, or `ws`. Remote types take `url` (plus optional `headers`) instead of `command`; always set `type` on them, because Claude Code reads a `url` entry with no `type` as stdio and skips it

## Transports

| Type | Use for | Add with |
| ---- | ------- | -------- |
| `stdio` | Local process: `npx`, `uvx`, `docker run -i --rm`, a binary | `claude mcp add <name> -- <command> [args...]` |
| `http` | Remote servers (recommended). Supports OAuth: sign in with `/mcp` or `claude mcp login <name>` | `claude mcp add --transport http <name> <url>` |
| `sse` | Deprecated remote transport. `--transport http` falls back to it automatically (v2.1.265+) | `claude mcp add --transport sse <name> <url>` |
| `ws` | Remote WebSocket servers that push events. Header auth only, no OAuth | `claude mcp add-json` or `.mcp.json` with `"type": "ws"` |

## Deferred Tool Loading (Tool Search)

Tool search is on by default. At session start Claude sees only MCP tool names and server instructions, and it calls `ToolSearch` to load a tool's full schema when it needs one. Adding servers therefore costs little context.

- `"alwaysLoad": true` on a server entry loads all of its tools upfront. Use it sparingly, because each upfront tool consumes context.
- `ENABLE_TOOL_SEARCH` overrides the default: `false` loads everything upfront, and `auto` / `auto:N` loads tools upfront until their definitions reach 10% (or N%) of the context window, then defers them all.
- When `ANTHROPIC_BASE_URL` points to a non-first-party host, Claude Code loads tools upfront because most proxies don't forward `tool_reference` blocks. Set `ENABLE_TOOL_SEARCH=true` if your proxy does forward them.
- Large results: Claude Code warns above 10,000 tokens. A successful text result over `MAX_MCP_OUTPUT_TOKENS` (default 25,000 tokens) or over 50,000 characters is saved to a file, and Claude receives the path instead.

## Configuration Locations

| Scope | Stored in | Loads in | Shared? |
| ----- | --------- | -------- | ------- |
| Local (default for `claude mcp add`) | `~/.claude.json`, under this project's path | This project only | No (personal) |
| Project (`--scope project`) | `.mcp.json` at the project root | This project | Yes -- commit it (no literal secrets) |
| User (`--scope user`) | `~/.claude.json` | All your projects | No (personal) |
| Plugin | The plugin's `.mcp.json` or `plugin.json` `mcpServers` | Wherever the plugin is enabled | With the plugin |

When the same server is defined in more than one place, Claude Code uses the highest-precedence entry whole, with no field merging: local > project > user > plugin > claude.ai connectors. Scopes are matched by name; plugin servers and connectors are matched by endpoint (URL or command). A server your organization provides through `managedMcpServers` outranks all of these (v2.1.259+). If you sign in with a claude.ai account, connectors you added at claude.ai also appear in `/mcp`; set `"disableClaudeAiConnectors": true` to turn them off.

**Security note:** Keep literal secrets out of `.mcp.json`. Reference them as `${VAR}` (or `${VAR:-default}`), which expands from each user's environment, or add servers that carry credentials at local scope, which stays private in `~/.claude.json`. Prefer this over gitignoring `.mcp.json`, since the file exists to share servers with the team. Interactive sessions ask each user to approve `.mcp.json` servers, but `claude -p`, Agent SDK, and cloud sessions load them without asking; to block one in every mode, list it in `disabledMcpjsonServers`.

## Plugin MCP Integration

A plugin's `.mcp.json` at the plugin root loads automatically when the plugin is enabled, so no `plugin.json` entry is needed. The optional `mcpServers` manifest key adds more servers (an inline map, a `.json` path, or an `.mcpb` bundle) and merges with that file. Server entries can use `${CLAUDE_PLUGIN_ROOT}` for portable paths:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/server/index.js"]
    }
  }
}
```

Plugin tools are named `mcp__plugin_<plugin>_<server>__<tool>`. Use that full name in permission rules and hook matchers; a hook matcher written against the bare server key never fires.

## Practical Example: TaskFlow

A TaskFlow project might connect to its PostgreSQL database through DBHub (`@bytebase/dbhub`) so Claude can check schema, verify migrations, or debug data issues during development:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@bytebase/dbhub@1.4.0"],
      "env": {
        "DSN": "${POSTGRES_CONNECTION_STRING}"
      }
    }
  }
}
```

DBHub reads its connection string from `DSN` (or a `--dsn` argument). Claude Code expands `${POSTGRES_CONNECTION_STRING}` from your shell environment at load time. Set it in your `.envrc`, `.bashrc`, or CI secrets, and point it at a read-only database user so Claude's queries can't modify data. Pin the version you reviewed, and never commit the actual value to git.

## Common MCP Servers

| Server | Purpose |
| ------ | ------- |
| `@modelcontextprotocol/server-filesystem` | Avoid for files outside the project: your `Read`/`Edit` deny rules don't cover its tools. Add the directory with `--add-dir` or `permissions.additionalDirectories` instead |
| `@bytebase/dbhub` | Query PostgreSQL and other relational databases (use a read-only user) |
| `claude mcp serve` (built in) | Run Claude Code itself as a stdio MCP server for other clients |
| `mcp-server-fetch` (Python) | Raw or `localhost` pages only, which built-in `WebFetch` summarizes or refuses. Otherwise prefer `WebFetch`: `WebFetch(domain:...)` rules don't cover this server, so list it under `permissions.ask` |

## Security Considerations

- **Only register servers you trust** -- MCP servers can execute arbitrary code on your machine.
- **Pin and review what runs locally.** A *pinned, reviewed* server is an auditable snapshot. `npx -y <pkg>` with no version is local execution with **remote supply-chain behavior** — it can pull new code on any run. Pin exact versions.
- **Treat remote/hosted connectors as mutable.** A remote connector can change behavior *after* you approve it. Re-evaluate it periodically; prefer a pinned local server when behavior must stay fixed.
- **Vet new connectors with throwaway data and minimal scope.** Before pointing a server at real credentials or production data, exercise it with fake inputs and read-only / minimal scopes in a contained environment — especially for tools with side effects.
- **Keep secrets out of committed files** -- use `${VAR}` references or local scope, never literal values.
- **Organization control** -- admins can deploy a fixed server set with `managed-mcp.json`, provide remote servers to every user with `managedMcpServers`, or filter servers with `allowedMcpServers` / `deniedMcpServers`. Match on `serverUrl` or `serverCommand`, because `serverName` is only a user-chosen label. See [Managed MCP configuration](https://code.claude.com/docs/en/managed-mcp).

## Further Reading

- [Official MCP reference](https://code.claude.com/docs/en/mcp)
- [Settings Guide](settings-guide.md) (permissions) and [Advanced Features Guide](advanced-features-guide.md) (hooks, agents, skills)
- [External-Integration Capability Governance](../../plugin/references/external-integration-governance.md) -- governing what an integrated capability may read/write/return, and how to disable it
