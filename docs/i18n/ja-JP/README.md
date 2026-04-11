<p align="center">
  <img src="../../../assets/banner-v2.svg" alt="Guardians of the Claude" width="700"/>
</p>

Claude Code設定のためのメタシステム。2分のガイド付きセットアップから始めて、プロジェクトの成長に合わせて監査・セキュリティ強化・最適化のワークフローへと拡張できます。同じツール、段階的な深化。

**入門者向け:** 2分のセットアップ — Claudeが数個の質問をして、すべての設定ファイルを自動生成します。

**パワーユーザー向け:** 4つの連鎖スキル（`/create` → `/audit` → `/secure`/`/optimize`）— スキル間メモリ、プロファイルドリフト検知、決定ジャーナルに裏打ちされています。

## フィロソフィー

1. **信頼より検証** — テスト、リント、ビルドコマンドを含めて、Claudeが自分の作業を検証できるようにする。最も効果的な設定です。
2. **少ないほど良い** — 短い指示ほどClaudeの遵守率が高い。各ガイドは一度に読める分量を維持します。
3. **具体的に** — 「ちゃんと動くか確認」ではなく`npm test`。すべてのコマンドはコピー＆ペーストで即実行できること。
4. **段階的な深化** — Day 1は2分のセットアップ。Day 30は監査とセキュリティ強化を追加。Day 100はスキル間メモリと自動ドリフト検知が有効化されます。ツールがあなたと共に成長し、必要のない複雑さに対するコストは払いません。

## Day 1 — 2分クイックスタート

> **前提条件:** Claude Code がインストール済み（`claude --version` で確認）。
> **Windows** では **Git Bash** または **WSL** を使用してください — プラグインの SessionStart フックと高度なテンプレートは bash で実行されます。Bash 互換シェルがないとフックは静かに終了し、自動ガイド機能（インストール検知、ドリフト検知、再監査プロンプト）が失われます。

1. **マーケットプレイスを追加してプラグインをインストール**:

   ```text
   claude
   > /plugin marketplace add wlsgur073/Guardians-of-the-Claude
   > /plugin install guardians-of-the-claude
   ```

2. **プロジェクトでセットアップコマンドを実行**:

   ```text
   cd your-project
   claude
   > /guardians-of-the-claude:create
   ```

   **代替方法**（プラグインインストールなし）:

   | 方法 | コマンド |
   | ---- | ------- |
   | ローカルプラグイン | `claude --plugin-dir /path/to/Guardians-of-the-Claude/plugin` |
   | `@` import | `@../Guardians-of-the-Claude/plugin/skills/create/SKILL.md` |
   | 直接貼り付け | `plugin/skills/create/SKILL.md`の内容をコピーして会話に直接貼り付け |

3. **パスを選択** — Claudeがプロジェクトの状態を検出して質問します:

   | パス | タイミング | 動作 |
   | ---- | --------- | ---- |
   | **新規プロジェクト** | コードなし | 4つの質問 → `CLAUDE.md`（6セクション）+ `.claude/settings.json` |
   | **既存プロジェクト** | コードあり、Claude設定なし | 6つの質問（自動検出デフォルト）→ フル設定（CLAUDE.md + settings + rules + オプションhooks/agents/skills） |
   | **不足機能の追加** | 設定が既に存在 | 現在の設定をスキャン、設定済み/未設定を表示、必要なものだけ追加 |

   > **既に設定がありますか？** Claudeが自動検出し、回答済みの質問をスキップして不足機能のみ追加します。
   > **間違ったパスを選んだ？** 心配不要 — Claudeが不一致を検出し、自動的にパス切り替えを提案します。

4. **完了** — Claudeがすべての設定ファイルを生成し、サマリーテーブルを表示します。
   `/memory`を実行して正しくロードされたか確認してください。

5. **次のステップ（オプション）** — `claude-code-setup`プラグインをインストールすると、
   プロジェクトのスタックに合わせたMCPサーバー、hooks、skillsの推奨を受けられます。

> **ヒント:** まずプロジェクトで`/init`を実行してください — Claudeがスターター
> CLAUDE.mdを自動生成します。その後`/guardians-of-the-claude:create`で「既存プロジェクト」を
> 選択すると、`/init`が見逃した部分を補完できます。

**ここで止めても大丈夫です。** 設定はそれ自体で動作します。以下のDay 30とDay 100+のセクションでは、さらに必要になった場合に次に何が起こるかを説明しています。

## Day 30 — 監査・セキュリティ強化・最適化

プロジェクトに実際のコードと実際の利用が積み重なると、3つのスキルが設定の健全性維持を支援します：

| スキル | 実行タイミング | 動作 |
| ------ | ------------- | ---- |
| `/guardians-of-the-claude:audit` | プロジェクトに大きな変更があった後 | 現在のClaude Code設定をスコアリング（0-100）、ドリフト識別、次のステップを推奨 |
| `/guardians-of-the-claude:secure` | 監査でセキュリティギャップが見つかった後 | denyパターン、セキュリティルール、ファイル保護フックを追加 |
| `/guardians-of-the-claude:optimize` | 監査で品質ギャップが見つかった後 | 肥大化したCLAUDE.mdをrules/に分割、エージェント多様化、MCP推奨 |

**典型的なフロー:** `/create` → （数週間の開発） → `/audit` → `/secure` または `/optimize` → `/audit` で再検証。

## Day 100+ — メタシステム活性化

複数のスキルを実行すると、プラグインは**メタシステムレイヤー**を活性化します — 時間の経過とともにプロジェクトに適応する持続的学習：

- **プロジェクトプロファイル** — 自動検出された技術スタック、構造、設定状態（`project-profile.md`）
- **決定ジャーナル** — すべてのスキル実行が圧縮されたchangelogに追加され、セッション間でコンテキストが保持されます（`config-changelog.md`）
- **スキル間メモリ** — `/optimize`は`/secure`が既に行ったことを知り、`/audit`は以前拒否された項目を記憶します
- **プロファイルドリフト検知** — プロジェクトがパッケージマネージャーを変更したりフレームワークのメジャーバージョンをアップグレードすると、プラグインが検知して推奨事項を再評価します
- **停滞検知** — 同じ推奨事項が3回無視されると、プラグインが拒否としてマークするか尋ねます

**この内容を読まなくてもプラグインは使えます。** 自動的に実行されます。内部を理解したい場合は[learning-system.md](../../../plugin/references/learning-system.md)を参照してください。

## テンプレート構造

```text
Guardians-of-the-Claude/
├── .claude-plugin/          ← マーケットプレイスマニフェスト（プラグインマーケットプレイス）
├── plugin/                  ← プラグインパッケージ
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── hooks/
│   │   ├── hooks.json       ← SessionStartフック
│   │   └── session-start.sh
│   ├── references/
│   │   ├── security-patterns.md  ← 共有セキュリティテンプレート（/createと/secure共用）
│   │   └── learning-system.md   ← 共有学習システムリファレンス（全スキル共用）
│   └── skills/
│       ├── create/
│       │   ├── SKILL.md     ← 生成スキル（/guardians-of-the-claude:create）
│       │   ├── references/  ← 生成ベストプラクティス
│       │   └── templates/   ← Starter & Advancedパス指示
│       ├── audit/
│       │   ├── SKILL.md     ← 監査スキル（/guardians-of-the-claude:audit）
│       │   └── references/  ← スコアリングモデルと計算式
│       ├── secure/
│       │   └── SKILL.md     ← セキュリティ強化スキル（/guardians-of-the-claude:secure）
│       └── optimize/
│           └── SKILL.md     ← 最適化スキル（/guardians-of-the-claude:optimize）
├── templates/starter/       ← スターター実例（架空の「TaskFlow」プロジェクト）
├── templates/advanced/      ← 上級機能実例（rules, hooks, agents, skills）
├── docs/
│   ├── guides/              ← ガイド
│   ├── i18n/ko-KR/          ← 韓国語翻訳（ガイド、テンプレート）
│   ├── i18n/ja-JP/          ← 日本語README（ガイド翻訳は準備中）
│   ├── plans/               ← 設計・計画ドキュメント
│   └── *.md                 ← コミュニティファイルとプロジェクトロードマップ
└── CHANGELOG.md             ← バージョン履歴（Keep a Changelog形式）
```

| ディレクトリ | 用途 |
| ----------- | ---- |
| `templates/starter/` | スターター実例 — 最小限のTaskFlow設定 |
| `templates/advanced/` | 上級実例 — rules, hooks, agents, skills |
| `docs/guides/` | 独立ガイド — それぞれ単独で読める |
| `docs/i18n/ko-KR/` | 韓国語翻訳（ガイド、テンプレート） |
| `docs/i18n/ja-JP/` | 日本語README（ガイド翻訳は準備中） |
| `docs/plans/` | 設計・計画ドキュメント |
| `docs/*.md` | コミュニティファイルとプロジェクト[ロードマップ](../../ROADMAP.md) |

## Claude Codeメモリの仕組み

Claude Codeは階層型メモリシステムで動作します：CLAUDE.md（ユーザーの指示）、`.claude/rules/`（モジュール式ルールファイル）、自動メモリ（Claudeが自身で書くメモ）、プラグインキャッシュ（プラグインが管理する状態）。詳細は[ディレクトリ構造ガイド](../../guides/directory-structure-guide.md)を参照してください。

> **最重要原則：** Claudeが自分の作業を検証できるようにしてください —
> CLAUDE.mdにテスト、リント、ビルドコマンドを含めましょう。
> これだけで成果物の品質が大きく変わります。

## ドキュメント

まずここから始めて、自分のレベルに合ったパスを進んでください:

> **注意:** ガイドの日本語翻訳は準備中です。以下のリンクは英語版を参照します。

| ステップ | ガイド | 対象 |
| ------- | ----- | ---- |
| 1 | [Getting Started](../../guides/getting-started.md) | 全員 — セットアップガイド |
| 2 | [CLAUDE.md Guide](../../guides/claude-md-guide.md) | 全員 — 効果的な指示の書き方 |
| 3 | [Settings Guide](../../guides/settings-guide.md) | 全員 — 権限と環境設定 |
| 4 | [Rules Guide](../../guides/rules-guide.md) | CLAUDE.mdが約100行を超えた時 |
| 5 | [Directory Structure](../../guides/directory-structure-guide.md) | `.claude/`の構造を理解したい時 |
| 6 | [Effective Usage](../../guides/effective-usage-guide.md) | Claude Codeを1日使った後 |
| 7 | [Advanced Features](../../guides/advanced-features-guide.md) | hooks、agents、skillsが必要な時 |
| 8 | [MCP Integration](../../guides/mcp-guide.md) | 外部ツールを接続したい時 |
| 9 | [Recommended Plugins](../../guides/recommended-plugins-guide.md) | Claude Codeを拡張したい時 |

## 推奨プラグイン

Claude Codeは公式プラグインで機能を拡張できます。カテゴリ別の詳細リストは**[推奨プラグインガイド](../../guides/recommended-plugins-guide.md)**を参照してください。

Claude Codeで`/plugin`を実行してプラグインを検索するか、[プラグインドキュメント](https://code.claude.com/docs/en/discover-plugins)を参照してください。

## ステータスライン

Claude Code下部のステータスバーをカスタマイズして、モデル、コンテキスト使用量、コスト、経過時間、gitブランチを一目で確認できます:

```text
[Opus 4.6 (1M context)] 📁 my-project
 🌿 feature/auth | ████████░░ 80% | $1.25 | ⏱️ 3m 42s
```

ワンライン設定:

```bash
cp ./statusline.sh ~/.claude/statusline.sh
```

Claude Codeが`~/.claude/statusline.sh`を自動検出します — 追加設定不要。

> **前提条件:**
> - [jq](https://jqlang.org)がインストールされている必要があります（`brew install jq` / `apt install jq` / `choco install jq`）
> - Bash互換シェルが必要です。**Windows**では **Git Bash** または **WSL** を使用してください — プラグインフックと高度なテンプレートはUnixシェル構文（`bash`, `grep` など）を使用します

## コントリビュート

コントリビュート？ここで？Claudeにやらせればいいのに...（笑）
...冗談です、もちろん歓迎します。IssueやPRをお気軽にどうぞ。
プロジェクトの方向性と提案は[ROADMAP.md](../../ROADMAP.md)を確認し、[GitHub Discussions](https://github.com/wlsgur073/Guardians-of-the-Claude/discussions)で参加してください。

## ライセンス

MIT — [LICENSE](../../../LICENSE)参照。
