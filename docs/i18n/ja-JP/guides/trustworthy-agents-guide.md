---
title: "信頼できるエージェント"
description: "Claude Code エージェント設定を評価するための5原則4層フレームワーク"
version: 1.0.1
---

# 信頼できるエージェント

このガイドは、Anthropic の「Trustworthy Agents in Practice」フレームワーク — 4つのアーキテクチャ層にまたがる5つの原則 — を Claude Code の具体的な設定面にマッピングします。プロジェクトの設定が意図した保証を提供しているかを評価するために使用してください。

## 出典と範囲

5つの原則(人間による制御、価値の整合、セキュリティ、透明性、プライバシー)と4つのアーキテクチャ層(モデル、ハーネス、ツール、環境)は、Anthropic Research の [Trustworthy Agents in Practice](https://www.anthropic.com/research/trustworthy-agents) (2026年4月) に基づいています。このガイドは*翻訳作業*を行います: 当該フレームワークを、このリポジトリの具体的な Claude Code の面 — CLAUDE.md、settings.json、フック、スキル、MCP、deny パターン — に適用します。

[`plugin/references/security-patterns.md`](../../../../plugin/references/security-patterns.md) の*脅威シナリオの視点*(「どのような攻撃から防御しているか?」)を補完します。このガイドは異なる問いに答えます: 「どのような保証をどの層で提供しているか?」

## 5つの原則

### 人間による制御

エージェントは人間の権限の下で行動し、人間は作業を検査・上書き・停止する能力を保持します。Claude Code の観点では:

- **Plan Mode** による戦略レベルの監督 (下記 [§ Plan Mode as Strategy-Level Oversight](#plan-mode-as-strategy-level-oversight) を参照)
- 常に確認のために一時停止すべきツールに対する `permissions.ask:[]`
- 危険な操作 (`git push --delete`、`rm -rf` など) のハードストップのための `PreToolUse` フック + `exit 2`
- 曖昧な識別子に対する破壊的操作についての CLAUDE.md 曖昧性解消ルール

### 価値の整合

エージェントは*あなたの*目標を追求します — 文字通りの要求だけでなく、その背後にある*理由*も含めて。Anthropic の [Teaching Claude why](https://www.anthropic.com/research/teaching-claude-why) (2026年5月) は、原則で Claude を訓練することが、デモンストレーションのみで訓練するよりも汎化することを示しました。同じ論理が CLAUDE.md にも当てはまります:

- ルールに加えて根拠を書く (「リポジトリクラスを使用します — ハンドラから DB への直接アクセスのショートカットが過去に本番データ漏洩を引き起こしたため」 — 単に「リポジトリクラスを使用してください」だけでなく)
- 標準の6セクション構造については [CLAUDE.md ガイド](claude-md-guide.md) を参照
- 複数の有効なアプローチがある問いに対してデフォルトを選ぶのではなく、人間の判断に委ねるスキル設計

### セキュリティ

エージェントは資格情報の露出、流出、スコープエスカレーション、または安全機構の回避を可能にしてはなりません。名前付きインシデント種別を含む完全な脅威カタログは [`plugin/references/security-patterns.md`](../../../../plugin/references/security-patterns.md) にあります。設定面:

- 秘密ファイル (`.env`、`*.pem`、`*.key`、`secrets/`) に対する `permissions.deny:[]`
- プロジェクト固有の保証 (認証、検証、秘密の取り扱い) のための `.claude/rules/security.md`
- stdin JSON を `jq -r '.tool_input.file_path'` でパースして機密ファイルを保護する `PreToolUse` フック（Claude Code は `$CLAUDE_FILE_PATH` 環境変数を公開し*ません* — フックはイベント JSON を stdin で受け取ります）
- これらを自動的に適用するには `/guardians-of-the-claude:secure` を実行

### 透明性

エージェントの行動と推論は検査可能です。設定面:

- フック定義の `statusMessage` は、フックが何をしているかを UI に表示します
- `.claude/.plugin-cache/<plugin>/local/config-changelog.md` はスキルが発行した設定変更を記録します
- `recommendations.json` はセッションをまたいで発行・解決・拒否された推奨事項を追跡します
- サブエージェントのディスパッチは可視のスレッドを生成すべきです ([§ サブエージェントの可観測性](#サブエージェントの可観測性) を参照)

### プライバシー

機密データはユーザーの同意なくエージェントのコンテキスト、出力、または外部システムに漏れません。設定面:

- MCP `.mcp.json` の env 値はリテラルの資格情報ではなく `${ENV_VAR}` プレースホルダーを使用
- `permissions.deny:[]` の `Read(./.env)` および同等の項目
- `.claude/rules/security.md` の秘密の取り扱いルール
- 共有 CLAUDE.md ファイルでは: インラインの資格情報・ホスト名・内部 URL を含めない

## 4つのアーキテクチャ層

多層防御: 十分に訓練されたモデルだけでは不十分です — ハーネス、ツール、環境が連携しなければなりません。

### モデル層

プロジェクト設定からはほぼ範囲外です — 評判の良いモデル提供者とバージョンを選択します。*制御できること*: エージェントごとのモデル選択 (`.claude/agents/<name>.md`)、YAML コメントに根拠を文書化します。[高度な機能ガイド § エージェント](advanced-features-guide.md#agents) を参照。

### ハーネス層

エージェントの動作を形作る指示、ルール、ランタイムゲート。プロジェクト設定の大部分がここに存在します:

- `CLAUDE.md` — すべてのセッションで読み込まれるプロジェクト指示
- `.claude/rules/*.md` — パススコープのモジュラー指示
- `.claude/settings.json` — 権限、フック、環境
- `settings.json` のインラインフック、または `.claude/hooks/` の外部スクリプト

ハーネスだけでは不十分です: 完璧な CLAUDE.md であっても `permissions.deny:[]` が空であれば資格情報を漏らす可能性があります。

### ツール層

エージェントが呼び出せるものと、その制限:

- `permissions.allow / ask / deny` で制御される組み込みツール
- スキル (`.claude/skills/<name>/SKILL.md`) — [高度な機能 § スキル](advanced-features-guide.md#skills) を参照
- MCP サーバー — [MCP ガイド](mcp-guide.md) を参照
- ツールごとの粒度 (「カレンダーは常に読み取り; 招待状の送信は承認が必要」)

ツールだけでは不十分です: ハーネスのルールが使い方を導かなければ、狭い許可でも誤用される可能性があります。

### 環境層

エージェントの行動を取り巻く OS レベルの境界:

- ファイルシステムのスコープ (作業ディレクトリ、deny ルールのパスパターン)
- ネットワーク送信 (`autoMode.environment` 信頼境界; 信頼できないホストへの `Bash(curl * https://*:*)` deny パターン)
- サンドボックス (`sandbox.enabled` — Linux の bubblewrap、macOS ネイティブ、WSL2)
- [`security-patterns.md` § 権限と安全性の決定原則](../../../../plugin/references/security-patterns.md#permission-and-safety-decision-principles) を参照

環境だけでは不十分です: サンドボックスは、その内部でエージェントが誤った判断を下すのを止めません。

## 層別セルフ監査

診断用のチェックリストです — スコアリングルーブリックではありません (それは `/guardians-of-the-claude:audit` の仕事です)。現在の設定を見直して答えてみてください:

**ハーネス層:**

- CLAUDE.md はルールが*なぜ*存在するかを説明していますか、それとも*何であるか*だけですか?
- `settings.json` は `Bash(*)` のようなワイルドカードではなく、粒度の細かい `allow:` / `ask:` 項目を使っていますか?
- フックはハードストップに `exit 2` を使い、明確な `statusMessage` を表示しますか?

**ツール層:**

- 資格情報ファイル (`.env`、`*.pem`、`*.key`、`secrets/`) に対する deny パターンはありますか?
- MCP サーバーはリテラル値ではなく `${ENV_VAR}` プレースホルダー経由で資格情報を受け取っていますか?
- 危険な Bash サブコマンド (`git push --delete`、`rm -rf`、`curl|bash`) は `ask:[]` または `deny:[]` にありますか?

**環境層:**

- エージェントの作業ディレクトリは、ユーザーの `$HOME` ではなくプロジェクトにスコープされていますか?
- Linux/macOS ユーザー: ネットワークに触れる Bash コマンドを実行する際にサンドボックスが有効ですか?
- `permissions.defaultMode` は意図的に選択されていますか (単に `default` のままにしていないか)?

**モデル層:**

- エージェントごとのモデル選択は、根拠 (YAML コメント) と共に文書化されていますか?
- 意図したモデルで Claude Code 対応プランで実行していますか?

## Plan Mode as Strategy-Level Oversight

Plan Mode は単なる権限モード以上のものです。Anthropic はこれを*ステップレベル*の監督 (各ツール呼び出しを承認) から*戦略レベル*の監督 (実行前にプラン全体を承認) への転換として位置付けています。

使用すべきタイミング:

- タスクのスコープが不明確、あるいは意図を超えて拡大しうるとき
- エージェントが不慣れなコードで意思決定をしようとしているとき
- 実行とは別に計画の記録を残したいとき

ステップレベルの監督が依然として適切な場合:

- 単発の、よく定義された操作
- どのみち diff をレビューする信頼できる反復作業

メカニズム — Plan Mode への入り方と動作 — については [効果的な使い方ガイド](effective-usage-guide.md) を参照。

## サブエージェントの可観測性

エージェントが並列のサブエージェントをディスパッチするとき、*どのサブエージェントが何をしたか*のスレッドを保持すべきです。設定面:

- `SubagentStop` フックはサブエージェントの完了イベントを意思決定チェンジログに記録できます
- 親の `PostToolUse` フックはサブエージェントの作業による状態変化を表示します
- フックイベントの種類については [高度な機能ガイド § フック](advanced-features-guide.md#hooks) を参照

このガイドは特定のフックパターンを規定しません — チームのレビューワークフローに合うものを選んでください。

## クロスリファレンス

防御の視点 (どのような脅威から防御しているか?):

- [`plugin/references/security-patterns.md`](../../../../plugin/references/security-patterns.md) — 名前付きインシデント種別を持つ脅威カタログ

自動化:

- `/guardians-of-the-claude:secure` — deny パターン、セキュリティルール、ファイル保護フックを適用
- `/guardians-of-the-claude:audit` — 多層ルーブリックで設定を採点

メカニズム:

- [設定ガイド](settings-guide.md) — 権限モード、フック、サンドボックス
- [高度な機能ガイド](advanced-features-guide.md) — フック、エージェント、スキル
- [効果的な使い方ガイド](effective-usage-guide.md) — Plan Mode のメカニズム

## 参考資料

- Anthropic Research, [Trustworthy Agents in Practice](https://www.anthropic.com/research/trustworthy-agents) — ソースフレームワーク
- Anthropic Research, [Teaching Claude why](https://www.anthropic.com/research/teaching-claude-why) — 価値の整合の背景
- [CLAUDE.md ガイド](claude-md-guide.md) — 効果的なプロジェクト指示の書き方
- [ルールガイド](rules-guide.md) — モジュラー指示ファイル
- [はじめに](getting-started.md) — 基本セットアップガイド
