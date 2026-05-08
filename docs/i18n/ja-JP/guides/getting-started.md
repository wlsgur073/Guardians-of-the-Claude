---
title: "はじめに"
description: "プロジェクトに Claude Code 設定をセットアップするためのステップバイステップガイド"
version: 1.2.5
---

# はじめに

このガイドでは、Claude Code 設定の初回インストールから動作確認まで、プロジェクトのセットアップ手順を一通り説明します。

## 前提条件

- Claude Code がインストール済みで動作していること（`claude --version` で確認）
- 設定したいプロジェクトがあること
- **Windows をお使いの場合**: プラグインの SessionStart フックは bash スクリプトと PowerShell スクリプト（`plugin/hooks/session-start.ps1`）の両方を同梱しており、advanced テンプレートの `validate-prompt` フックも同様に `.ps1` 版（`templates/advanced/hooks/validate-prompt.ps1`）を `.sh` 版と並べて同梱しています。PowerShell 5.1+（Windows 10+ に標準搭載）または Git Bash/WSL のいずれかがあれば両レイヤーとも動作するため、追加のシェル設定は不要です

## Step 1: セットアップ方法を選ぶ

| 選択肢 | 内容 | 適したケース |
| ------ | ---- | ----------- |
| `/init` | コードを解析して基本的な CLAUDE.md を生成 | 手早く始めたい場合 -- 多くのプロジェクトに適しています |
| `/guardians-of-the-claude:create` | 対話形式で CLAUDE.md + 設定 + ルール + 任意の機能を生成 | 包括的なセットアップ（[Day 1 — 2分クイックスタート](../README.md#day-1--2分クイックスタート)） |

**`/init`** は[公式に推奨されている最初のステップ](https://code.claude.com/docs/en/best-practices)です。Claude がコードベースを解析して CLAUDE.md を自動生成します。

```text
claude
> /init
```

**`/guardians-of-the-claude:create`** は `/init` と同様の解析に加えて、ルール・権限・任意の高度な機能まで生成します。先にプラグインをインストールしてください（`/plugin marketplace add wlsgur073/Guardians-of-the-Claude` のあと `/plugin install guardians-of-the-claude`）。**両方使いたい場合は** `/init` を先に実行し、次に `/guardians-of-the-claude:create` で「Existing project」を選択してください。既存の CLAUDE.md を検出して上書きせずにマージします。

## Step 2: テンプレートをコピーする（手動で行う場合）

Step 1 で `/guardians-of-the-claude:create` を使用した場合はこの手順をスキップしてください。ファイルはすでに生成されています。

手動でテンプレートを参照したい場合は、`templates/starter/` と `templates/advanced/` にある記入済みの例（架空の「TaskFlow」プロジェクト）を確認してください。それぞれのパスで完成した設定がどのような形になるかを示しています。

> **TaskFlow のサンプルスタックについて:** 現在の記入済みテンプレートでは、具体的な例として Node.js / Express / TypeScript / PostgreSQL を使用しています。TaskFlow 自体は架空のリファレンスプロジェクトです（詳細は [`templates/README.md`](../../../../templates/README.md) を参照）。`/create` はプロジェクトが Node/Express であることを **要求しません** -- 実際のマニフェスト（`package.json`、`pyproject.toml`、`go.mod`、`Cargo.toml`、`pom.xml`、`Gemfile`）を検出するか、空のプロジェクトであればスタックに関する質問を行い、それに応じたコマンドを生成します。

**Starter**（初心者向け）:

```bash
# starter のサンプルを参考にしてください
# templates/starter/CLAUDE.md および templates/starter/.claude/settings.json を参照
```

**Advanced**（フル構成）:

```bash
# advanced のサンプルを参考にしてください
# templates/advanced/CLAUDE.md および templates/advanced/.claude/ を参照
```

`/init` ですでに CLAUDE.md を生成済みであれば、テンプレートのセクションをそこにマージしてください。テンプレートは一貫したセクション構造を提供し、`/init` はプロジェクト固有の内容を提供します。両者の良いところを組み合わせましょう。

## Step 3: CLAUDE.md を埋める

Step 1 で `/guardians-of-the-claude:create` を使用した場合はこの手順をスキップしてください。6 つの正規セクションはすでに生成されています。`/memory` で CLAUDE.md が読み込まれていることを確認したら Step 4 に進んでください。

CLAUDE.md を手動で書く場合は、以下のセクションを順に埋めていきます。`/audit` が同じルーブリックで採点できるよう、構造はそのまま保ってください。

1. **Project Overview** -- 1〜2 文で、プロジェクトの概要・使用言語・フレームワークを記述します。
2. **Build & Run** -- 依存関係のインストールとプロジェクト実行に必要な正確なコマンド。
3. **Testing** -- Claude が自身の作業を検証するために使えるテストコマンド。
4. **Code Style & Conventions** -- 言語のデフォルトと異なるルールのみを、具体的に記述します。
5. **Development Approach** -- 曖昧な依頼への対応方法（前提を分析し、的を絞った質問をし、コーディングの前にアプローチを確認する）。`/create` はここに 4 行のデフォルトを差し込みます。
6. **Important Context** -- 自明ではない情報: 必要なサービス、認証パターン、環境固有のクセなど。

ベースラインを超えるプロジェクトでは、`Workflow`、`Project Structure`、`References`、または `Available Skills` / `Available Agents` のテーブルを追加できます。記入済みの例は [`templates/advanced/CLAUDE.md`](../../../../templates/advanced/CLAUDE.md) を参照してください。各セクションに何を含めて何を除外すべきかは、[CLAUDE.md ガイドの「含めるものと除外するもの」](claude-md-guide.md#含めるものと除外するもの)を参照してください。

## Step 4: ルールをセットアップする（任意）

CLAUDE.md が 200 行を超えてきた場合や、特定のファイルタイプにのみ適用したい指示がある場合は、それらを `.claude/rules/` のファイルに移してください。

ルールの利用が向いているのは次のようなケースです。

- **モジュール化された構成** -- 1 ファイル 1 トピック（例: `testing.md`、`code-style.md`）
- **パススコープ** -- マッチするファイルを Claude が読み込んだときにのみロードされるルール
- **チームでの分担** -- 領域ごとに別のメンバーがルールファイルをオーナーシップ

毎セッションで必要となる中核的な指示は CLAUDE.md に残してください。詳細な解説は [Rules ガイド](rules-guide.md) を参照してください。

## Step 5: 権限を設定する

`.claude/settings.json` を編集して、Claude が頻繁に実行するコマンドを事前承認しておきましょう。これによりワークフロー中の権限プロンプトを減らせます。

```json
{
  "permissions": {
    "allow": [
      "Bash(npm test)",
      "Bash(npm run lint)"
    ],
    "deny": [
      "Read(./.env)"
    ]
  }
}
```

`allow` リストは `Tool(specifier)` の構文を使います。まずはテストとビルドのコマンドから始めてください。最も安全で頻度の高いものです。利用可能なすべてのオプションは [Settings ガイド](settings-guide.md) を参照してください。

## Step 6: 動作を確認する

プロジェクトで Claude Code を起動して、すべてが読み込まれていることを確認します。

1. `/memory` を実行 -- 読み込まれている CLAUDE.md とルールがすべて表示されます。自分のファイルが含まれているか確認してください。
2. 簡単なタスクを試す -- プロジェクト構成を説明させたり、テストを実行させたりしてみましょう。
3. Claude が指示に従っているか確認 -- ルールが無視される場合、CLAUDE.md が長すぎるか、指示が曖昧すぎる可能性があります。

## Step 7: 高度な機能を試す（任意）

基本的な設定が動作したら、より洗練されたワークフローのために hooks、agents、skills を試してみてください。詳細は [Advanced Features ガイド](advanced-features-guide.md) を参照してください。

**Starter から Advanced へのアップグレード:** `/guardians-of-the-claude:create` をもう一度実行し、最初のプロンプトで「Existing project」を選択して、Advanced の 6 つの質問に回答してください。Claude は既存の設定を検出し、新しいセクションをマージします。

> **ヒント:** `claude-code-setup` プラグインを使うと、検出されたスタックに合わせた追加の自動化（MCP サーバー、フック、スキル）を提案してもらえます。セットアップ後の追加提案を得たい場合は、公式マーケットプレイスからインストールしてください。

## 次に読むもの

- [CLAUDE.md ガイド](claude-md-guide.md) -- 効果的な CLAUDE.md ファイルの書き方を深く解説
- [Rules ガイド](rules-guide.md) -- 指示をモジュール化されたルールファイルに整理する
- [Settings ガイド](settings-guide.md) -- settings.json のすべての設定オプション
- [Directory Structure ガイド](directory-structure-guide.md) -- `.claude/` エコシステムを理解する
- [Effective Usage ガイド](effective-usage-guide.md) -- 初日からの使い方パターンと避けるべきアンチパターン
- [Advanced Features ガイド](advanced-features-guide.md) -- チーム向けの hooks、agents、skills
- [MCP Integration ガイド](mcp-guide.md) -- Claude と外部ツール・サービスを連携する
- [Recommended Plugins ガイド](recommended-plugins-guide.md) -- Claude Code を拡張する厳選プラグイン
