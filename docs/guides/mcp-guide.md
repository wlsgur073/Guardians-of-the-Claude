---
title: "MCP Integration"
description: "Connecting Claude Code to external tools and services via Model Context Protocol"
version: 1.0.1
---

# MCP Integration

## What Is MCP?

Model Context Protocol (MCP) lets Claude Code connect to external tools — databases, APIs, documentation services. MCP servers run as local processes and expose tools that Claude can call during a session.

## Configuration

MCP servers are configured in `.mcp.json` at your project root:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "@example/mcp-server"],
      "env": {
        "API_KEY": "your-key-here"
      }
    }
  }
}
```

Key fields:

- **`command`** -- how to launch the server (`npx`, `uvx`, `docker`, `node`, etc.)
- **`args`** -- arguments passed to the command
- **`env`** -- environment variables the server needs (API keys, connection strings)

## Server Types

Three common patterns for launching MCP servers:

| Pattern | Command | Example |
| ------- | ------- | ------- |
| Node.js package | `npx` | `npx -y @modelcontextprotocol/server-filesystem` |
| Python package | `uvx` | `uvx --from mcp-server-fetch mcp-server-fetch` |
| Docker container | `docker` | `docker run -i --rm mcp/postgres` |

## Deferred Tool Loading

MCP tools are **not loaded immediately** when Claude starts. They appear as deferred tools and must be activated via `ToolSearch`:

1. Claude sees a list of deferred tool names at session start
2. When a tool is needed, Claude calls `ToolSearch` to fetch its full schema
3. Only then can Claude invoke the tool

MCP tools don't consume context until they're actually used — an efficient design for projects with many servers.

## Configuration Locations

| Location | Scope | Committed to git? |
| -------- | ----- | ------------------ |
| `.mcp.json` (project root) | Project -- shared with team | Yes, if no secrets in env |
| `~/.claude/mcp.json` | User -- applies to all projects | No (personal) |
| Plugin `plugin.json` `mcpServers` field | Plugin -- bundled with plugin | Yes |

**Security note:** If your `.mcp.json` contains API keys in the `env` field, add it to `.gitignore` and document the required keys in your CLAUDE.md instead. Alternatively, reference environment variables that are set outside the file.

## Plugin MCP Integration

Plugins can bundle MCP servers by referencing a config file in `plugin.json`:

```json
{
  "name": "my-plugin",
  "mcpServers": "./.mcp.json"
}
```

The plugin's `.mcp.json` can use `${CLAUDE_PLUGIN_ROOT}` for portable paths:

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

## Practical Example: TaskFlow

A TaskFlow project might connect to a PostgreSQL MCP server for direct database queries during development:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://dev:dev@localhost:5432/taskflow_dev"
      }
    }
  }
}
```

With this configured, Claude can query the database directly — checking schema, verifying migrations, or debugging data issues.

## Common MCP Servers

| Server | Purpose |
| ------ | ------- |
| `@modelcontextprotocol/server-filesystem` | Read/write files outside the project |
| `@modelcontextprotocol/server-postgres` | Query PostgreSQL databases |
| `@anthropic-ai/claude-code-mcp-server` | Run Claude Code as an MCP tool |
| `mcp-server-fetch` (Python) | Fetch and parse web content |

## Security Considerations

- **Only register servers you trust** -- MCP servers can execute arbitrary code on your machine
- **Keep secrets out of committed files** -- use environment variables or `.gitignore` your `.mcp.json`
- **Pin server versions** -- use exact package versions in args to avoid unexpected updates

## Further Reading

- [Settings Guide](settings-guide.md) -- Permissions and preferences
- [Advanced Features Guide](advanced-features-guide.md) -- Hooks, agents, and skills
