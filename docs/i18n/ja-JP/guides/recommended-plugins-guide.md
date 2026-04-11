---
title: "おすすめプラグイン"
description: "カテゴリ別に整理した Claude Code プラグインの厳選リスト"
version: 1.0.0
---

# おすすめプラグイン

Claude Code は機能を拡張する公式プラグインをサポートしています。Claude Code 内で `/plugin` を実行すると利用可能なプラグインを閲覧できます。詳細は[プラグインのドキュメント](https://code.claude.com/docs/en/discover-plugins)を参照してください。

## 開発ワークフロー

| プラグイン | 内容 |
| -------- | ---- |
| [superpowers](https://github.com/obra/superpowers) | フル開発ワークフロー -- 仕様、設計、計画、サブエージェント駆動の実装。Claude が計画から外れることなく何時間も自律的に作業できます |
| [feature-dev](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/feature-dev) | 構造化された 7 フェーズの機能開発: コードベース探索、質問、設計、実装、レビュー |
| [code-review](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-review) | 偽陽性を絞り込む信頼度スコア付きのマルチエージェント PR レビュー。実際の問題は捕捉し、ノイズはスキップします |
| [code-simplifier](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-simplifier) | 動作を維持したまま、最近変更されたコードの明瞭性と一貫性を高めます |

## コードインテリジェンス & 品質

| プラグイン | 内容 |
| -------- | ---- |
| [typescript-lsp](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/typescript-lsp) | TypeScript / JS の言語サーバー -- Claude を離れずに定義ジャンプ、参照検索、エラーチェックが行えます |
| [security-guidance](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/security-guidance) | コード生成前にセキュリティ脆弱性の可能性（XSS、インジェクションなど）を警告する pre-edit フック |
| [context7](https://github.com/upstash/context7) | 最新のライブラリドキュメントをオンデマンドで取得する MCP サーバー。API のハルシネーションがなくなります |

## UI & ブラウザ

| プラグイン | 内容 |
| -------- | ---- |
| [frontend-design](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/frontend-design) | 「いかにも AI が作りました」感のない、特徴的でプロダクション品質の UI を生成します |
| [chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) | 実行中の Chrome ブラウザを操作・検査 -- DevTools 経由でデバッグ、自動化、パフォーマンス分析が行えます |
| [figma](https://github.com/figma/mcp-server-guide) | Figma ファイルから設計コンテキストを実装ワークフローへ直接取り込めます |

## プロジェクトセットアップ

| プラグイン | 内容 |
| -------- | ---- |
| [claude-code-setup](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-code-setup) | コードベースをスキャンして、プロジェクトに最適な hooks、skills、MCP サーバー、subagents を提案します |
| [claude-md-management](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-md-management) | CLAUDE.md の品質監査と、`/revise-claude-md` でのセッション学びの取り込み |

## インストール方法

1. 利用可能なプラグインを閲覧:

   ```text
   /plugin
   ```

2. マーケットプレイスを追加してインストール:

   ```text
   /plugin marketplace add <owner>/<repo>
   /plugin install <plugin-name>@<marketplace-name>
   ```

3. インストールを確認:

   ```text
   /plugin list
   ```

> **ヒント:** 一部のプラグイン（context7 など）は MCP サーバーで、別途セットアップが必要です。インストール手順は各プラグインの README を確認してください。
