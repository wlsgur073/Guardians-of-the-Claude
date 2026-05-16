---
title: "高度な機能"
description: "Hooks、agents、skills -- 基本的な構成を超えて Claude Code を拡張する"
version: 1.3.4
---

# 高度な機能

基本的な CLAUDE.md とルールでは物足りなくなったチーム向けの 3 つの機能です。これらを追加する前に、まず[はじめにガイド](getting-started.md)を読んでください。完全な記入済み例は `templates/advanced/` を参照してください。

## Hooks

フックは、Claude がツールを使う前後に自動的に実行されるシェルコマンドです。`settings.json` の `hooks` キーで定義します。自動 lint、自動フォーマット、ファイル保護、型チェックなどに使えます。

### フックの構成

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path // empty' | grep -qE '(package-lock\\.json|\\.env|migrations/)' && { echo 'Protected file'; exit 2; } || exit 0",
            "timeout": 5,
            "statusMessage": "Checking for protected files"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "FILE=$(jq -r '.tool_input.file_path // empty'); [ -n \"$FILE\" ] && npx eslint --fix \"$FILE\" 2>/dev/null || true",
            "timeout": 15,
            "statusMessage": "Auto-linting edited file"
          }
        ]
      }
    ]
  }
}
```

主要な概念:

- **`matcher`** -- パイプ区切りのツール名または正規表現（例: `"Edit|Write"`、`"mcp__.*"`）
- **Hook 入力 (stdin)** -- フックは stdin でイベント JSON を受け取ります（例: `{"tool_input": {"file_path": "..."}}`）; `jq -r '.tool_input.file_path // empty'` でパースしてください。パス関連の環境変数は **`$CLAUDE_PROJECT_DIR`**（プロジェクトルート）のみで — ファイルパスは環境変数として公開され*ません*
- **`statusMessage`** -- フック実行中に UI に表示されるテキスト
- **`PreToolUse` + `exit 2`** は操作をブロックして理由を Claude に伝えます -- `.env` やマイグレーションディレクトリのような機密ファイルの保護に使ってください
- **`PostToolUse` + `|| true`** は操作の完了後に実行されます -- 自動 lint やフォーマットに使ってください
- **`UserPromptSubmit`** は Claude がユーザー入力を処理する前に実行されます -- キーワード検出や自動コンテキスト注入に使えます
- その他のイベント: `Notification`、`Stop`、`SessionStart`、`SessionEnd`、`SubagentStop`、`PreCompact` -- 全イベントタイプは [hooks ドキュメント](https://code.claude.com/docs/en/hooks)を参照してください
- **実用的な組み合わせ:** 起動時のプロジェクトコンテキスト注入には `SessionStart`、自動コンパクション前の重要メモ保護には `PreCompact`、親セッションに戻る前のエージェント出力検証には `SubagentStop`
- **フックの種類:** `"type": "command"`（シェル）または `"type": "prompt"`（LLM 駆動、`PreToolUse`、`Stop`、`SubagentStop`、`UserPromptSubmit` で利用可能）

### スクリプトベースのフック

複雑なロジックには外部スクリプトを使ってください: `"command": "bash \"${CLAUDE_PROJECT_DIR}/scripts/my-hook.sh\""`。スクリプトはテストが書け、バージョン管理ができ、メンテナンスもしやすくなります。完全な例は `templates/advanced/.claude/settings.json` を参照してください。`timeout` は必ず明示的に設定してください -- 入力検証は 3〜5 秒、lint / フォーマットは 10〜15 秒、ビルド / テストは 30 秒以上が目安です。

## Agents

エージェントは `.claude/agents/` に置く独自の役割定義で、専用のスコープ・ツールセット・モデルを持ちます。役割の専門化、スコープの制約、大規模コードベースでの並列ディスパッチに有用です。

### エージェントの構成

`.claude/agents/<name>.md` を作成し、YAML フロントマターを記述します。

```markdown
---
name: "Backend Developer"
description: "Specializes in API layer, services, and database access"
tools:
  - Read
  - Edit
  - Write
  - Bash
# sonnet: 実装タスクに対して速度と品質のバランスが取れている
model: "sonnet"
color: "green"
---

## Scope
`src/api/`、`src/services/`、`src/repos/`、`tests/` 配下のファイルのみ変更すること。

## Rules
- すべてのルートハンドラで asyncHandler ラッパーパターンに従うこと
- データベースアクセスはすべて `src/repos/` のリポジトリクラス経由で行うこと
- すべての入力検証には `src/models/` の Zod スキーマを使うこと

## Constraints
- 明示的な承認なしに、マイグレーションファイルや `package-lock.json` を変更しないこと
- ルートハンドラからリポジトリを直接呼び出さないこと -- 必ずサービス経由で

## Verification
- `npm test` がパスし、`npm run lint` が警告なし、`npm run build` がコンパイル成功すること
- 新しいエンドポイントには JSDoc タグを含めること: @route、@method、@auth
```

4 つのセクションがエージェントのプロンプトを集中させます。**Scope** はエージェントが触れる範囲を定義し、**Rules** は動作のしかたを定義し、**Constraints** は損害を防ぐための厳格な制限を設け、**Verification** は作業完了の確認方法を伝えます。すべてのエージェントが 4 つすべてを必要とするわけではありません -- 複雑さに応じて取捨選択してください。

### モデルの選び方

| モデル | 適した用途 | エージェント例 |
| ----- | --------- | ------------ |
| `haiku` | 高速な調査、ファイル検索、探索 | explorer、linter |
| `sonnet` | 実装、デバッグ、テスト作成 | backend-dev、debugger |
| `opus` | アーキテクチャレビュー、深い分析 | code-reviewer、architect |

親セッションのモデルに合わせるには `"inherit"` を使ってください。選択理由は YAML コメント（`# opus: セキュリティレビューには深い分析が必要`）に残し、選択がそれ自体で説明されるようにしましょう。

**コストのトレードオフ:** `haiku` は `opus` のおよそ 60 分の 1 のコストです。デフォルトは `sonnet` で構いません。大量の読み取り専用タスクには `haiku` を、ミス 1 回の代償が大きい場面（セキュリティレビュー、アーキテクチャ判断）にだけ `opus` を使ってください。

### エージェント設計のパターン

**1 エージェント、1 視点。** 実装・レビュー・テストを 1 つのエージェントに混ぜないでください -- 集中した役割に分割しましょう。

**読み取り専用エージェント:** `tools` から Edit と Write を取り除けば、解析専用のエージェントになります。セキュリティレビュー、アーキテクチャ分析、コード探索に有用です。

**エージェントパイプライン:** 多段階のワークフローではエージェントを連鎖させましょう: `backend-developer`（実装）→ `security-reviewer`（レビュー）→ `test-writer`（テスト）。

マルチエージェントディスパッチパターン（オーケストレーター-ワーカー、サブエージェントコンテキスト予算、努力スケーリング）については、[マルチエージェントパターンガイド](multi-agent-patterns-guide.md) を参照してください。

## Skills

スキルは `.claude/skills/` に置く再利用可能な複数ステップのワークフローです。それぞれがスラッシュコマンドとなり、機能のスキャフォールドやコンポーネント追加などの繰り返し作業を自動化します。

### スキルの構成

`.claude/skills/<skill-name>/SKILL.md` を作成します。

```markdown
---
name: "add-endpoint"
description: "Scaffolds a new REST API endpoint with handler, service, and tests"
argument-hint: "<resource> [operations]"
---

# Steps

## Step 1: Gather Information
Read `references/api-conventions.md` for project patterns.
Parse `$ARGUMENTS` for resource name and operations. If empty, ask the user.

## Step 2: Validate
Confirm the resource does not already exist. Run the test suite.

## Step 3: Execute
Create model, repository, service, handler, and test files.

## Step 4: Verify
Run build and tests to confirm everything works.
```

主要なフィールド:

- **`name`** / **`description`** -- 識別子とトリガ表現。Claude はスキルを起動するか判断する際に両フィールドを読むため、description には起動条件を明示してください（例: `"Use when the user asks to ..."`）
- **`argument-hint`** -- スラッシュコマンドメニューの使い方ヒント（例: `"<resource> [operations]"`）
- **`user-invocable`** -- スラッシュコマンドメニューに表示するかどうか（デフォルト: `true`）
- **`disable-model-invocation`** -- Claude の自動トリガを無効にする（デフォルト: `false`）
- **`model`** -- スキル実行中に使うモデルを上書き

スキルには 2 種類あります: **ユーザー起動型**（スラッシュコマンド）と **モデル起動型**（Claude が自動的にトリガ）です。モデル起動型の description には、トリガとなる表現を含めてください: `"Use when the user asks to 'do X' or 'do Y'."`。スキルは SKILL.md と並べてサポートファイルを置けます: `references/`、`examples/`、`scripts/`。

### Progressive Disclosure

スキルはコンテキストを 3 段階でロードしてウィンドウを軽く保ちます — スキルの**メタデータ**（最初にロード、トリガ判定用）、SKILL.md の**本文**（スキル起動時にロード）、**サポートファイル**（ワークフロー内で必要なときにのみロード）。skill-local の `references/` を SKILL.md と並べて束ねるのが canonical な Agent Skills 構造です。共有の `plugin/references/*.md` は、コンテンツが本当に cross-skill な場合のみ使用してください。

### スキル設計のパターン

**引数の解析:** `$ARGUMENTS` でパラメータを受け取ります。Step 1 でフラグと位置引数をパースしてください -- 空であればユーザーに尋ねましょう。

**リファレンスファイル:** プロジェクトの規約・例・API ドキュメントは SKILL.md と並べて `references/` に置いてください。最初にまとめて読み込むのではなく、必要なステップで読み込みましょう -- これによりコンテキストを節約できます。

**フォールバックパターン:** スキルが任意のツール（MCP サーバー、CI システム）に依存する場合、2 つの経路を用意してください: パス A はツールが利用できる場合に使い、パス B はツールがない場合の手動代替手段です。

**評価駆動の反復:** まず例として呼び出しと期待される出力を書き、その評価が通るまで SKILL.md を反復改善します。各パスの後に、成功したアプローチと典型的な失敗を Claude がスキルテキストに反映するようにしてください。

**Description の品質が重要です:** トリガーフレーズ、ドメイン専門家の観点による表現、デュアルフォーマット応答、実行可能なエラーメッセージは、Claude が適切なタイミングでスキルをトリガーするかどうかに大きく影響します。全体の原則については [`plugin/references/tool-description-quality.md`](../../../../plugin/references/tool-description-quality.md) を参照してください。

**セキュリティ:** スキルは実行可能な指示です — 信頼できるソースからのみインストールし、見慣れない SKILL.md は呼び出す前にレビューしてください。スクリプトを実行する前にレビューするのと同じように扱ってください。

> **注意:** レガシーの `commands/` ディレクトリは非推奨です。すべてのスキルタイプに `skills/<name>/SKILL.md` を使ってください。

### 実例: プラグインのスキル

`guardians-of-the-claude` プラグインは、連鎖して動作する 4 つのスキルによる「役割ごとに 1 スキル」のワークフローを示しています。

| スキル | 用途 |
| ----- | ---- |
| `/guardians-of-the-claude:create` | 対話形式のセットアップウィザード -- CLAUDE.md、設定、ルール、任意の機能を生成 |
| `/guardians-of-the-claude:audit` | 採点付きの包括的な構成評価 |
| `/guardians-of-the-claude:secure` | セキュリティの隙を埋める -- deny パターン、セキュリティルール、ファイル保護フック |
| `/guardians-of-the-claude:optimize` | 構成の品質を改善する -- ルール分割、エージェント多様性、MCP、フック品質 |

**推奨ワークフロー:** `/create` → `/audit` → `/secure` または `/optimize` → `/audit`（再検証）。各スキルは次のスキルへと引き継がれ、`.claude/.plugin-cache/` のタイムスタンプ付きファイルを通して状態を共有します。

## さらに読む

- [はじめに](getting-started.md) -- 基本セットアップのウォークスルー
- [Settings ガイド](settings-guide.md) -- 権限などの設定
- [MCP Integration ガイド](mcp-guide.md) -- MCP を介した外部ツールとの接続
- [Rules ガイド](rules-guide.md) -- モジュール化された指示ファイル
- [信頼できるエージェントガイド](trustworthy-agents-guide.md) -- エージェント設定を評価するための5原則フレームワーク
