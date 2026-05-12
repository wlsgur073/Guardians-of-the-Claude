<p align="center">
  <img src="../../../assets/banner-v2.svg" alt="Guardians of the Claude" width="700"/>
</p>

<p align="center">
  <a href="../../../README.md">English</a> | <a href="../ko-KR/README.md">한국어</a> | <b>日本語</b>
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
> **Windows** ではプラグインの SessionStart フックと advanced テンプレートの `UserPromptSubmit` フックの両方が bash + PowerShell の 2 エントリを同梱しているため、**PowerShell 5.1+（Windows 10+ に標準搭載）または Git Bash/WSL** のいずれかがあれば両レイヤーとも動作します — 追加設定は不要です。

1. **マーケットプレイスを追加してプラグインをインストール**:

   ```text
   claude
   > /plugin marketplace add wlsgur073/Guardians-of-the-Claude
   > /plugin install guardians-of-the-claude@guardians
   > /reload-plugins
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
   | **New project** | コードなし | 4つの質問 → `CLAUDE.md`（6セクション）+ `.claude/settings.json` |
   | **Existing project** | コードあり、Claude設定なし | 6つの質問（自動検出デフォルト）→ フル設定（CLAUDE.md + settings + rules + オプションhooks/agents/skills） |
   | **Add missing features** | 設定が既に存在 | 現在の設定をスキャン、設定済み/未設定を表示、必要なものだけ追加 |

   > **既に設定がありますか？** Claudeが自動検出し、回答済みの質問をスキップして不足機能のみ追加します。
   > **間違ったパスを選んだ？** 心配不要 — Claudeが不一致を検出し、自動的にパス切り替えを提案します。

4. **完了** — Claudeがすべての設定ファイルを生成し、サマリーテーブルを表示します。
   `/memory`を実行して正しくロードされたか確認してください。

5. **次のステップ（オプション）** — `claude-code-setup`プラグインをインストールすると、
   プロジェクトのスタックに合わせたMCPサーバー、hooks、skillsの推奨を受けられます。

> **ヒント:** まずプロジェクトで`/init`を実行してください — Claudeがスターター
> CLAUDE.mdを自動生成します。その後`/guardians-of-the-claude:create`で「Existing project」を
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

## Day 100+ — メタシステムへのエンゲージメント

複数のスキルを実行すると、プラグインは**メタシステムレイヤー**を活性化します — 時間の経過とともにプロジェクトに適応する持続的学習：

- **プロジェクトプロファイル** — 自動検出された技術スタック、構造、設定状態（`profile.json`、人間が読めるビューは `state-summary.md`）
- **決定ジャーナル** — すべてのスキル実行が圧縮されたchangelogに追加され、セッション間でコンテキストが保持されます（`config-changelog.md`）
- **スキル間メモリ** — `/optimize`は`/secure`が既に行ったことを知り、`/audit`は以前拒否された項目を記憶します
- **プロファイルドリフト検知** — プロジェクトがパッケージマネージャーを変更したりフレームワークのメジャーバージョンをアップグレードすると、プラグインが検知して推奨事項を再評価します
- **停滞検知** — 同じ推奨事項が3回無視されると、プラグインが拒否としてマークするか尋ねます

**この内容を読まなくてもプラグインは使えます。** 自動的に実行されます。内部を理解したい場合は[learning-system.md](../../../plugin/references/learning-system.md)を参照してください。

## v2.11+ State形式とstateless mode

**v2.11 マイグレーション**（v2.10.x からアップグレードするユーザー向け）: state 形式が Markdown ファイルから JSON へ変更されました。アップグレード後に初めてスキルを実行すると、`local/project-profile.md` + `local/latest-*.md` が `local/profile.json` + `local/recommendations.json` へ自動変換され、オリジナルは `local/legacy-backup/<ISO-8601-UTC>/` 配下に保存されます。一方向のマイグレーション — ロールバックには手動復元と v2.10.x への固定が必要です。パース失敗時のリカバリと完全なマイグレーション詳細は [CHANGELOG.md](../../../CHANGELOG.md) の v2.11.0 エントリを参照してください。

**Stateless mode**（v2.12.0 以降）: `local/` に書き込めない場合（読み取り専用マウント、プライバシー重視のプロジェクト、ユーザー無効化）、スキルは一度だけ警告を出力し、すべての state ファイル書き込みをスキップします — 学習状態はセッション間で永続化されません。プライバシー重視のプロジェクトは旧バージョンを固定する代わりに stateless mode に依存できます。

**マイグレーション失敗の報告**: [GitHub Issues](https://github.com/wlsgur073/Guardians-of-the-Claude/issues) に警告出力と（可能であれば）パース失敗ファイルの redacted スニペットを添えて報告してください。テレメトリは自動収集されません。

## CI smoke レーン（移行ブリッジ）

v3.0 リリースまで、または二人目のメンテナが参加するまで（いずれか早い方）、CI smoke レーン（`ci/fixtures/` + `ci/golden/`）は最小 4 つのフィクスチャセット（`migration` / `beginner-path` / `warm-start` / `monorepo`）を検証します。より広範な評価はメンテナローカルで実施されます。

終了条件を満たした後、smoke レーンはすべての release-gate チェックに昇格し、この移行期の注記は README から削除されます。

## テンプレート構造

```text
Guardians-of-the-Claude/
├── .claude-plugin/          ← マーケットプレイスマニフェスト（プラグインマーケットプレイス）
├── plugin/                  ← プラグインパッケージ
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── hooks/
│   │   ├── hooks.json       ← SessionStartフック（bash + powershell デュアルエントリ）
│   │   ├── session-start.sh ← bash 状態チェック（Linux/macOS/Git Bash/WSL）
│   │   └── session-start.ps1 ← PowerShell ポート（Windows 10+）
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
│   ├── i18n/ja-JP/          ← 日本語翻訳（ガイド、テンプレート）
│   └── *.md                 ← コミュニティファイルとプロジェクトロードマップ
└── CHANGELOG.md             ← バージョン履歴（Keep a Changelog形式）
```

## Claude Codeメモリの仕組み

Claude Codeは階層型メモリシステムで動作します：CLAUDE.md（ユーザーの指示）、`.claude/rules/`（モジュール式ルールファイル）、自動メモリ（Claudeが自身で書くメモ）、プラグインキャッシュ（プラグインが管理する状態）。詳細は[ディレクトリ構造ガイド](guides/directory-structure-guide.md)を参照してください。

> **最重要原則：** Claudeが自分の作業を検証できるようにしてください —
> CLAUDE.mdにテスト、リント、ビルドコマンドを含めましょう。
> これだけで成果物の品質が大きく変わります。

## ドキュメント

まずここから始めて、自分のレベルに合ったパスを進んでください:

| ステップ | ガイド | 対象 |
| ------- | ----- | ---- |
| 1 | [はじめに](guides/getting-started.md) | 全員 — セットアップガイド |
| 2 | [CLAUDE.md ガイド](guides/claude-md-guide.md) | 全員 — 効果的な指示の書き方 |
| 3 | [Settings ガイド](guides/settings-guide.md) | 全員 — 権限と環境設定 |
| 4 | [Rules ガイド](guides/rules-guide.md) | CLAUDE.mdが約100行を超えた時 |
| 5 | [ディレクトリ構造](guides/directory-structure-guide.md) | `.claude/`の構造を理解したい時 |
| 6 | [効果的な使い方](guides/effective-usage-guide.md) | Claude Codeを1日使った後 |
| 7 | [高度な機能](guides/advanced-features-guide.md) | hooks、agents、skillsが必要な時 |
| 8 | [MCP 連携](guides/mcp-guide.md) | 外部ツールを接続したい時 |
| 9 | [おすすめプラグイン](guides/recommended-plugins-guide.md) | Claude Codeを拡張したい時 |

## 推奨プラグイン

Claude Codeは公式（Anthropic公式）プラグインとコミュニティプラグインの両方で機能を拡張できます。カテゴリ別の詳細リストは**[おすすめプラグインガイド](guides/recommended-plugins-guide.md)**を参照してください。

Claude Codeで`/plugin`を実行してプラグインを検索するか、[プラグインドキュメント](https://code.claude.com/docs/en/discover-plugins)を参照してください。

## ステータスライン

Claude Code下部のステータスバーをカスタマイズして、モデル、コンテキスト使用量、コスト、経過時間、gitブランチを一目で確認できます:

```text
[Opus 4.7 (1M context)] 📁 my-project
 🌿 feature/auth | ████████░░ 80% | $1.25 | ⏱️ 3m 42s
```

ワンライン設定:

```bash
cp ./statusline.sh ~/.claude/statusline.sh
```

Claude Codeが`~/.claude/statusline.sh`を自動検出します — 追加設定不要。

> **前提条件:**
> - [jq](https://jqlang.org)がインストールされている必要があります（`brew install jq` / `apt install jq` / `choco install jq`）
> - `statusline.sh` を実行するための Bash 互換シェルが必要です。**Windows** では **Git Bash** または **WSL** を使用してください。（プラグインフックと advanced テンプレートのフックは `.sh` と `.ps1` の両方を同梱しているため、statusline 自体を除けば PowerShell のみの Windows でも動作します。）

## コントリビュート

コントリビュート？ここで？Claudeにやらせればいいのに...（笑）
...冗談です、もちろん歓迎します。IssueやPRをお気軽にどうぞ。
プロジェクトの方向性と提案は[ROADMAP.md](../../ROADMAP.md)を確認し、[GitHub Discussions](https://github.com/wlsgur073/Guardians-of-the-Claude/discussions)で参加してください。

## ライセンス

MIT — [LICENSE](../../../LICENSE)参照。
