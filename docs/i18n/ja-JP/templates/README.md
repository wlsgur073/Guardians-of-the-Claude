# templates/ — TaskFlow リファレンス例

このディレクトリには、架空のプロジェクト **TaskFlow** に対する完成済みの設定例（`CLAUDE.md`、`.claude/settings.json`、rules、hooks、agents、skills）が含まれています。TaskFlow はこのリポジトリ全体でリファレンスとして使用されるタスク管理 REST API です。

## TaskFlow について

TaskFlow は**特定の技術スタックではありません。** 以下のような概念的プロジェクトです：

- タスク管理用 REST API（users、tasks、comments）
- 永続ストレージとセッションキャッシュ
- 認証、入力バリデーション、構造化されたエラーハンドリング
- 典型的なバックエンドの関心事：レートリミット、データベースマイグレーション、自動テスト

この架空のプロジェクトはガイド、`plugin/skills/create/SKILL.md`、およびすべてのサンプルコードで同じように参照されます。ドキュメント間のクロスリファレンスがシンプルになるよう、リポジトリのすべての例を理解するために覚えるべき架空プロジェクトは一つだけです。

## 現在の完成済み例について

`starter/` と `advanced/` 配下の現行テンプレートは、具体的な実装として **Node.js / Express / TypeScript / PostgreSQL / Redis / Jest** を使用しています。これは Node/Express を「デフォルト」スタックとして確定したものでは**ありません。** 以下の理由で選ばれた一つの実装に過ぎません：

- Node/Express は REST API のよく知られた出発点です
- 特定のファイル（`src/api/`、`src/services/`、`src/repos/`）へのクロスリファレンスは、共有された一つの例で書く方が容易です
- エコシステムが安定しており、広く理解されたツール（npm、Jest、ESLint、TypeScript）を備えています

**実際のスタックが異なるのはむしろ一般的です。** 以下のコマンドを実行すると：

```text
> /guardians-of-the-claude:create
```

Claude Code はユーザーの実際のプロジェクトに適応します：

1. **既存マニフェストの検出** — `package.json`、`pyproject.toml`、`go.mod`、`Cargo.toml`、`pom.xml`、`Gemfile` など
2. **空プロジェクトの場合はスタック質問** — 言語、フレームワーク、build/test/lint コマンド
3. **同等のコマンド生成** — `npm test` の代わりに `pytest`、`eslint` の代わりに `ruff check`、`npm run build` の代わりに `cargo build` など

生成される `CLAUDE.md` はこれらのテンプレートと同じセクション構造に従いますが、ユーザーの実際のスタックに合ったコマンドとパスを持ちます。

## なぜスタック別バリエーションを作らないのか？

このリポジトリは意図的に `templates/python/`、`templates/go/`、`templates/nextjs/` のようなスタック別ディレクトリを**維持していません。** 理由：

- **メンテナンスがスタック数に線形比例**し、各スタックのエコシステム更新（フレームワーク新バージョン、新 lint ツール、新テストランナー）ごとに独立して管理が必要です
- **スタックはドキュメントより速く進化します** — 6ヶ月前の完成テンプレートはすでに部分的に誤解を招く可能性があり、どの部分が最新かユーザーが判断しにくくなります
- **真の製品は `/create`** — Claude はランタイムで適応し、これは静的テンプレートでは実現できない方法です。静的テンプレートは**読むための**出発点であり、`/create` は**作るための**出発点です
- **メンテナンス能力は有限です** — 一つの高品質な例は、5つの半端に管理された例よりも優れています

プロジェクトの方向性と「Stack-adaptive improvements」バックログアイテムについては [`docs/ROADMAP.md`](../../../ROADMAP.md) を参照してください。

## これらのテンプレートの読み方

**参考にすべきもの：**

- セクション構造（CLAUDE.md が持つべきセクション）
- パターン（rules の分割方法、agents のスコープ設定、hooks の接続方法）
- コンベンション（命名、コミットスタイル、verification gate、review gate）
- 各選択の**理由**がコメントやガイドのクロスリファレンスに文書化されています

**そのままコピーしないもの：**

- `npm` / `Jest` の具体的なコマンド — ユーザーのスタックの同等物に置き換え
- Node 固有のパス（`src/api/`、`src/services/`、`src/repos/`）— プロジェクトのレイアウトを使用
- サンプル内のパッケージ固有コード（`asyncHandler`、Zod スキーマ、`ts-jest` 設定）— スタックの同等物を使用

リファレンスを読む代わりにガイド付き生成を希望する場合は、`/guardians-of-the-claude:create` を実行してください。Claude がユーザーの実際のプロジェクトに合った `CLAUDE.md` と `settings.json` を生成します。
