<p align="center">
  <img src="../../../assets/banner-v2.svg" alt="Claude Code Template" width="700"/>
</p>

Claude Code設定のためのスターターテンプレートとガイド。プラグインをインストールし、
`/claude-code-template:create`を実行すると、Claudeが対話形式のインタビューを通じて
すべての設定ファイルを自動生成します。

**対象:** 初日から使える設定が欲しいClaude Code入門開発者。

## フィロソフィー

1. **信頼より検証** — テスト、リント、ビルドコマンドを含めて、Claudeが自分の作業を検証できるようにする。最も効果的な設定です。
2. **少ないほど良い** — 短い指示ほどClaudeの遵守率が高い。各ガイドは一度に読める分量を維持します。
3. **具体的に** — 「ちゃんと動くか確認」ではなく`npm test`。すべてのコマンドはコピー＆ペーストで即実行できること。
4. **シンプルに始め、必要に応じて拡張** — 2つのファイルで開始。Rules、hooks、agents、skillsは実際に必要になってから追加。

## クイックスタート

1. **マーケットプレイスを追加してプラグインをインストール**:

   ```text
   claude
   > /plugin marketplace add wlsgur073/Claude-Code-Template
   > /plugin install claude-code-template@wlsgur073-plugins
   ```

2. **プロジェクトでセットアップコマンドを実行**:

   ```text
   cd your-project
   claude
   > /claude-code-template:create
   ```

   **代替方法**（プラグインインストールなし）:

   | 方法 | コマンド |
   | ---- | ------- |
   | ローカルプラグイン | `claude --plugin-dir /path/to/Claude-Code-Template/plugin` |
   | `@` import | `@../Claude-Code-Template/plugin/skills/create/SKILL.md` |
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
> CLAUDE.mdを自動生成します。その後`/claude-code-template:create`で「既存プロジェクト」を
> 選択すると、`/init`が見逃した部分を補完できます。

## テンプレート構造

```text
Claude-Code-Template/
├── .claude-plugin/          ← マーケットプレイスマニフェスト（プラグインマーケットプレイス）
├── plugin/                  ← プラグインパッケージ
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── hooks/
│   │   ├── hooks.json       ← SessionStartフック
│   │   └── session-start.sh
│   ├── references/
│   │   └── security-patterns.md  ← 共有セキュリティテンプレート（/createと/secure共用）
│   └── skills/
│       ├── create/
│       │   ├── SKILL.md     ← 生成スキル（/claude-code-template:create）
│       │   ├── references/  ← 生成ベストプラクティス
│       │   └── templates/   ← Starter & Advancedパス指示
│       ├── audit/
│       │   ├── SKILL.md     ← 監査スキル（/claude-code-template:audit）
│       │   └── references/  ← スコアリングモデルと計算式
│       ├── secure/
│       │   └── SKILL.md     ← セキュリティ強化スキル（/claude-code-template:secure）
│       ├── optimize/
│       │   └── SKILL.md     ← 最適化スキル（/claude-code-template:optimize）
│       └── generate/
│           └── SKILL.md     ← 非推奨 — /createにリダイレクト
├── templates/starter/       ← スターター実例（架空の「TaskFlow」プロジェクト）
├── templates/advanced/      ← 上級機能実例（rules, hooks, agents, skills）
├── docs/
│   ├── guides/              ← ガイド
│   ├── i18n/ko-KR/          ← 韓国語翻訳（ガイド、テンプレート）
│   ├── i18n/ja-JP/          ← 日本語翻訳（ガイド、テンプレート）
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
| `docs/i18n/ja-JP/` | 日本語翻訳（ガイド、テンプレート） |
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
cp Claude-Code-Template/statusline.sh ~/.claude/statusline.sh
```

Claude Codeが`~/.claude/statusline.sh`を自動検出します — 追加設定不要。

> **前提条件:** [jq](https://jqlang.org)がインストールされている必要があります（`brew install jq` / `apt install jq` / `choco install jq`）。

## コントリビュート

コントリビュート？ここで？Claudeにやらせればいいのに...（笑）
...冗談です、もちろん歓迎します。IssueやPRをお気軽にどうぞ。
プロジェクトの方向性と提案は[ROADMAP.md](../../ROADMAP.md)を確認し、[GitHub Discussions](https://github.com/wlsgur073/Claude-Code-Template/discussions)で参加してください。

## ライセンス

MIT — [LICENSE](../../../LICENSE)参照。
