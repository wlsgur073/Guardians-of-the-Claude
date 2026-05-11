---
title: "MCP 連携"
description: "Model Context Protocol を使って Claude Code を外部ツール・サービスに接続する"
version: 1.0.3
---

# MCP 連携

## MCP とは

Model Context Protocol（MCP）は、Claude Code を外部ツール — データベース、API、ドキュメンテーションサービスなど — に接続するための仕組みです。MCP サーバーはローカルのプロセスとして動作し、Claude がセッション中に呼び出せるツールを公開します。

## 構成

MCP サーバーはプロジェクトルートの `.mcp.json` で構成します。

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

主要なフィールド:

- **`command`** -- サーバーの起動方法（`npx`、`uvx`、`docker`、`node` など）
- **`args`** -- コマンドに渡す引数
- **`env`** -- サーバーに必要な環境変数（API キー、接続文字列など）

## サーバーの種類

MCP サーバーを起動する典型的な 3 パターンです。

| パターン | コマンド | 例 |
| ------- | ------ | -- |
| Node.js パッケージ | `npx` | `npx -y @modelcontextprotocol/server-filesystem` |
| Python パッケージ | `uvx` | `uvx --from mcp-server-fetch mcp-server-fetch` |
| Docker コンテナ | `docker` | `docker run -i --rm mcp/postgres` |

## 遅延ロードされるツール

MCP ツールは Claude の起動時に**すぐにはロードされません**。遅延ツールとしてリストアップされ、`ToolSearch` 経由で有効化される必要があります。

1. Claude はセッション開始時に遅延ツール名のリストを受け取ります
2. ツールが必要になると、Claude は `ToolSearch` を呼び出して完全なスキーマを取得します
3. その後でようやくツールを呼び出せます

MCP ツールは実際に使われるまでコンテキストを消費しません -- サーバーが多いプロジェクトに向いた効率的な設計です。

## 構成ファイルの場所

| 場所 | スコープ | git にコミット? |
| --- | ------ | -------------- |
| `.mcp.json`（プロジェクトルート） | プロジェクト -- チームと共有 | env にシークレットがなければ する |
| `~/.claude/mcp.json` | ユーザー -- すべてのプロジェクトに適用 | しない（個人用） |
| プラグインの `plugin.json` の `mcpServers` フィールド | プラグイン -- プラグインに同梱 | する |

**セキュリティ上の注意:** `.mcp.json` の `env` フィールドに API キーがある場合は、そのファイルを `.gitignore` に追加して、必要なキーは代わりに CLAUDE.md にドキュメント化してください。あるいは、ファイルの外で設定する環境変数を参照する形にしましょう。

## プラグインからの MCP 連携

プラグインは `plugin.json` で構成ファイルを参照することで、MCP サーバーを同梱できます。

```json
{
  "name": "my-plugin",
  "mcpServers": "./.mcp.json"
}
```

プラグインの `.mcp.json` では、ポータブルなパスのために `${CLAUDE_PLUGIN_ROOT}` を使えます。

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

## 実例: TaskFlow

TaskFlow プロジェクトでは、開発中にデータベースへ直接クエリを投げるために PostgreSQL の MCP サーバーへ接続できます。

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "${POSTGRES_CONNECTION_STRING}"
      }
    }
  }
}
```

Claude Code は `${POSTGRES_CONNECTION_STRING}` をロード時にシェル環境から展開します -- `.envrc`、`.bashrc`、または CI のシークレットで設定してください。実際の値を git にコミットしてはいけません。

これを構成すれば、Claude は直接データベースにクエリを投げ -- スキーマの確認、マイグレーションの検証、データに関する不具合のデバッグなどが行えます。

## よく使われる MCP サーバー

| サーバー | 用途 |
| ------- | ---- |
| `@modelcontextprotocol/server-filesystem` | プロジェクト外のファイルの読み書き |
| `@modelcontextprotocol/server-postgres` | PostgreSQL データベースへのクエリ |
| `@anthropic-ai/claude-code-mcp-server` | Claude Code 自体を MCP ツールとして実行 |
| `mcp-server-fetch`（Python） | Web コンテンツの取得とパース |

## セキュリティ上の考慮事項

- **信頼できるサーバーだけを登録する** -- MCP サーバーはマシン上で任意のコードを実行できます
- **シークレットをコミット対象のファイルから外す** -- 環境変数を使うか、`.mcp.json` を `.gitignore` に追加してください
- **サーバーのバージョンを固定する** -- 想定外の更新を避けるため、args に正確なパッケージバージョンを指定してください

## さらに読む

- [Settings ガイド](settings-guide.md)（権限）と [Advanced Features ガイド](advanced-features-guide.md)（hooks、agents、skills）
