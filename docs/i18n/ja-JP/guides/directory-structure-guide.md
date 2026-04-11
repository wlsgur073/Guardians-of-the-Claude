---
title: ".claude/ ディレクトリ構造"
description: ".claude/ エコシステム、自動メモリ、バージョン管理対象を理解する"
version: 1.2.1
---

# .claude/ ディレクトリ構造

Claude Code は構成・指示・学びを保存するために、いくつかのディレクトリとファイルを使用します。このガイドはエコシステム全体を地図のように示し、各要素が何をするのか、何をバージョン管理すべきかを明確にします。

## .claude/ には何があるのか

```text
your-project/
├── CLAUDE.md                     # プロジェクト指示（ルートに配置）
├── .claude/
│   ├── CLAUDE.md                 # プロジェクト指示（代替の配置場所）
│   ├── settings.json             # チーム共有の設定（コミットする）
│   ├── settings.local.json       # 個人の上書き（gitignore 対象）
│   ├── rules/                    # モジュール化された指示ファイル
│   │   ├── code-style.md
│   │   ├── testing.md
│   │   └── ...
│   ├── agents/                   # エージェント定義（高度）
│   │   └── developer.md
│   ├── skills/                   # スキル定義（高度）
│   │   └── scaffold-feature/
│   │       └── SKILL.md
│   └── .plugin-cache/            # プラグインの状態ファイル（自動生成、gitignore 対象）
│       └── <plugin-name>/
└── src/
    └── CLAUDE.md                 # フォルダレベル指示（遅延ロード）
```

`.claude/` の内側にあるものはすべて Claude Code の設定です。ルートの `CLAUDE.md` やフォルダレベルの `CLAUDE.md` は、プロジェクトのファイルと並んで配置されます。`agents/` と `skills/` は高度な機能です -- [Advanced Features ガイド](advanced-features-guide.md)を参照してください。

## 自動メモリ

自動メモリは Claude 自身のノート機能です。セッション中にプロジェクトについて何かを学ぶと、Claude はそれを将来のセッションのために保存します。

**場所:** `~/.claude/projects/<project-hash>/memory/`

これはプロジェクト内ではなく、ホームディレクトリに保存されます。次のものが含まれます。

- **MEMORY.md** -- すべてのトピックメモリを列挙したインデックスファイル
- **トピックファイル** -- `user_preferences.md`、`project_architecture.md` のような個別ファイル

### 「200 行」の違い

MEMORY.md と CLAUDE.md は「200 行」という同じ数字を使いますが、その理由はまったく異なります。

| ファイル | 制限 | 種類 | 何が起きるか |
| ------- | ---- | ---- | ----------- |
| MEMORY.md | 200 行 | **ロードの厳密な境界** | 200 行を超えた内容はセッション開始時にロードされません。切り捨てられます。 |
| CLAUDE.md | 200 行 | **準拠のための緩い目安** | 長さに関係なくファイル全体がロードされます。ただし、短いほうが指示への準拠度が高くなります。 |

数字は同じでも、仕組みは別物です。MEMORY.md には厳密なカットオフがあり、CLAUDE.md はベストプラクティス上の目標値です。

### 自動メモリは管理しなくてよい

自動メモリはリポジトリの外に存在します。これらのファイルを作成したり編集したり gitignore に追加したりする必要はありません -- Claude が自動的に管理します。Claude が何を保存しているかは `/memory` で確認できます。

## プラグインキャッシュ

一部のプラグインは、プロジェクトごとの状態を `.claude/.plugin-cache/<plugin-name>/` に保存します。このディレクトリはプラグインによって**自動生成される**もので、手動で編集したりバージョン管理にコミットしたりすべきではありません。プラグインは `.plugin-cache/` 内に独自の `.gitignore` を管理し、キャッシュファイルが git から除外されることを保証します。

例: `guardians-of-the-claude` プラグインは、プロジェクトプロファイル、決定ジャーナル、最新のスキル実行結果を `local/` サブディレクトリに保存します（`project-profile.md`、`config-changelog.md`、`latest-{skill}.md`）。これらのファイルにより、スキルはセッションをまたいでプロジェクトのコンテキスト・ユーザーの好み・保留中の推奨事項を覚えていられます。

## .gitignore に何を入れるか

| ファイル | コミットするか | 理由 |
| ------- | ------------ | ---- |
| `.claude/settings.json` | する | チーム共有の構成 -- 全員が同じ権限を使う |
| `.claude/rules/` | する | チーム共有の指示ファイル |
| `.claude/settings.local.json` | しない | 個人の上書き -- 開発者ごとに異なる |
| `.claude/.plugin-cache/` | しない | プラグインが管理する状態ファイル -- 自動生成される |
| 自動メモリ（`~/.claude/...`） | -- | リポジトリの外にあるので何もしなくてよい |

プロジェクトの `.gitignore` に次の行を追加してください。

```gitignore
.claude/settings.local.json
.claude/.plugin-cache/
```

## 4 つのシステム

Claude Code には、セッション開始時にすべて読み込まれる 4 つの異なるシステムがあり、それぞれが別の目的を持っています。

| システム | 書き手 | 用途 | 場所 |
| ------- | ----- | ---- | --- |
| **CLAUDE.md** | あなた | あなたが Claude のために書く指示 | プロジェクトルート、`.claude/`、サブディレクトリ |
| **自動メモリ** | Claude | Claude が自分のために保存する学び | `~/.claude/projects/<project>/memory/` |
| **設定** | あなた | 動作の構成（権限、各種スイッチ） | `.claude/settings.json`、`.claude/settings.local.json` |
| **プラグインキャッシュ** | プラグイン | プラグインが管理するプロジェクトごとの状態 | `.claude/.plugin-cache/<plugin-name>/` |

ここで重要なのは次の対比です。**CLAUDE.md はあなたが Claude に伝えるもの。自動メモリは Claude が自分自身に伝えるもの。プラグインキャッシュはプラグインが自分自身に伝えるもの。** 各システムは、別の書き手が別の目的のために書いています。

## さらに読む

- [CLAUDE.md ガイド](claude-md-guide.md) -- 効果的な CLAUDE.md ファイルの書き方
- [Rules ガイド](rules-guide.md) -- 指示をモジュール化されたルールファイルに整理する
- [Settings ガイド](settings-guide.md) -- settings.json のオプションを構成する
