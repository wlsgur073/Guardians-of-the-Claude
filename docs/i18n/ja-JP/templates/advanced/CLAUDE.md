---
title: "TaskFlow CLAUDE.md (Advanced)"
description: "Node.js/Express REST API プロジェクト向けのルート CLAUDE.md 例"
version: 1.1.0
---

<!--
  サンプルスタック注記（ソースには表示、GitHub レンダリングでは非表示）

  このテンプレートは Node.js + Express + TypeScript + PostgreSQL で実装された
  TaskFlow を例示しています。TaskFlow は架空のリファレンスプロジェクトであり、
  Node/Express スタックは一つの具体的な実装例に過ぎず、確定されたデフォルトではありません。

  セクション構造とパターンを参考にしてください。実際のスタック向けには
  `/guardians-of-the-claude:create` を実行してください — Claude がマニフェストを
  検出し、同等のコマンドを生成します。

  完全なコンベンションについては templates/README.md を参照してください。
-->

# プロジェクト概要

TaskFlow はタスク管理用の REST API で、Node.js と Express で構築されています。
データ永続化に PostgreSQL、セッションキャッシュに Redis を使用します。

## ビルド & 実行

npm install
npm run dev          # :3000 ポートでホットリロード開発サーバーを起動
npm run build        # TypeScript を dist/ にコンパイル
npm run lint         # ESLint をプロジェクト全体で実行

## テスト

npm test             # Jest フルテストスイートを実行
npm run test:watch   # 開発用 watch モード
npm run test:cov     # カバレッジレポート付きでテスト実行

テストには実行中の PostgreSQL インスタンスが必要です（docker-compose.yml 参照）。
テスト実行前に `docker compose up -d` を実行してください。

## コードスタイル & コンベンション

- TypeScript strict モード、2 スペースインデント
- default export ではなく named export を使用
- エラー型は src/errors/ の AppError を拡張
- データベースクエリは src/repos/ に記述、ルートハンドラで直接呼び出し禁止
- すべての非同期ルートハンドラは asyncHandler ラッパーを使用すること

## 開発アプローチ

- リクエストが曖昧または不明確な場合、すぐに実装を開始しないこと
- まずリクエストを批判的に分析：前提、不足しているコンテキスト、可能な解釈を特定
- 分析結果を提示し、コード記述前に具体的な質問で明確化
- 明確化後、アプローチを簡潔に説明し、進行前に確認を得る

## ワークフロー

- ブランチ命名：`feat/`、`fix/`、`chore/` プレフィックス
- コミットメッセージ：conventional commits 形式
- push 前にフルテストスイート実行：`npm test && npm run lint`
- すべての PR は CI パスと 1 名以上のレビュー承認が必要

## プロジェクト構造

- src/api/         → Express ルートハンドラとミドルウェア
- src/models/      → TypeScript インターフェースと Zod バリデーションスキーマ
- src/repos/       → データベースアクセスレイヤー（エンティティごとに 1 ファイル）
- src/services/    → ビジネスロジック（ハンドラが呼び出し、repos を呼び出す）
- src/errors/      → AppError を拡張するカスタムエラー型
- tests/           → src/ 構造をミラーリング
- db/migrations/   → SQL マイグレーションファイル（npm run migrate で実行）
- .claude/rules/   → 詳細ガイドライン（コードスタイル、アーキテクチャ、テスト、ワークフロー）

## 利用可能なスキル

| スキル | 用途 |
| ------ | ---- |
| `/add-endpoint` | ハンドラ、サービス、テスト付きの新規 API エンドポイントをスキャフォールド |
| `/run-checks` | ビルド、リント、テストを順番に実行 |

## 利用可能なエージェント

| エージェント | モデル | 役割 |
| ------------ | ------ | ---- |
| `backend-developer` | sonnet | API 実装、サービス、データベースアクセス |
| `security-reviewer` | opus | セキュリティ脆弱性分析（読み取り専用） |
| `test-writer` | haiku | プロジェクトコンベンションに沿ったテスト生成 |

## 重要なコンテキスト

- 認証は JWT を使用し、リフレッシュトークンは Redis に保存
- すべての API レスポンスは src/api/response.ts の envelope 形式に従う
- レートリミットは src/api/middleware/rateLimit.ts でルートごとに設定
- 環境変数は起動時に src/config.ts を通じて検証

## 参照

@docs/architecture.md
@docs/api-conventions.md
@README.md
