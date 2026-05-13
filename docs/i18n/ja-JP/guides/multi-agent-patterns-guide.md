---
title: "マルチエージェントパターン"
description: "オーケストレーター-ワーカー、努力スケーリング、サブエージェントコンテキスト予算、幅優先探索、並列ディスパッチ — Claude Code サブエージェントワークフロー向け"
version: 1.0.0
---

# マルチエージェントパターン

コーディングタスクが十分にオープンエンドで、何ステップかかるか予測できない場合、単一エージェントは1つのコンテキストウィンドウでは苦労します。マルチエージェント構成 — 1つのオーケストレーターと複数のワーカー — は、このようなタスクをより上手く処理しますが、コストがかかります。

このガイドでは、Anthropic などが複数の Claude インスタンスをディスパッチする際に効果的と判断したパターンを紹介します。*単一エージェント*のセットアップ（Scope、Rules、Constraints、Verification）については、[高度な機能ガイド — Agents](advanced-features-guide.md#agents) を参照してください。より広いワークフローパターン（Writer/Reviewer、fan-out、worktrees）については、[ワークフローパターンガイド](workflow-patterns-guide.md) を参照してください。

## マルチエージェントを選ぶ場合

| タスクの形態 | 推奨 |
|---|---|
| ステップ数が予測できないオープンエンドのリサーチ | マルチエージェント（オーケストレーター + ワーカー） |
| 順次的で固定ステップのタスク | プロンプトチェーニングを使った単一エージェント |
| 多くのファイルに変更が及ぶ大規模コードベースの改修 | オーケストレーター + ファイルまたはモジュールごとの並列ワーカー |
| 既知のファイルの単純なバグ修正 | 単一エージェント — マルチエージェントのオーバーヘッドは無駄 |

コストの注意: マルチエージェントの実行は、通常、単一のチャットセッションの約 15 倍のトークンを使用します。スケールアップする前に支出を正当化してください: レイテンシー、並列性、または品質がコストを上回る必要があります。

## パターン: オーケストレーター-ワーカー

リードエージェントがタスクを分解し、ワーカーエージェントがサブタスクを実行し、リードが結果を統合します。

*すべての*ワーカーに対して、リードは4つのことを指定します:

1. **Objective** — 達成すること、正確に記述する
2. **Output format** — 返却の形態（例: "1–2k トークンの要約"）
3. **Tool guidance** — 優先または回避すべきツール
4. **Boundaries** — 触れてはいけない、または探索してはいけないこと

Anthropic は次のように報告しています: "詳細なタスク説明がないと、エージェントは作業を重複させたり、ギャップを残したり、必要な情報を見つけられないことがあります。"

オーケストレーターのプロンプト例:

```text
Spawn three workers in parallel. For each, specify the objective, output format, tool guidance, and boundaries.

Worker A — Investigate authentication flow.
  Objective: trace how a logged-in user's request reaches the database.
  Output format: 1–2k token summary listing each layer + the file that owns it.
  Tools: prefer Grep/Read; avoid Bash unless tracing runtime behavior.
  Boundaries: only src/auth/ and src/api/middleware/; do not enter src/services/.

Worker B — ...
```

## 努力スケーリングのルール

リードが単純なタスクに過度に投資しないよう、これらのルールをオーケストレーターのシステムプロンプトに埋め込んでください:

| タスクの複雑さ | ワーカー数 | ワーカーあたりのツール呼び出し数 |
|---|---|---|
| 単純な事実確認 | 1 | 3–10 |
| 中程度の分析 | 2–4 | 10–30 |
| 複雑なリサーチ | 10+ | 役割を分担して |

よくある失敗パターンは、1回の Grep で答えられる質問に対してリードが 10 個のワーカーをスポーンすることです。ディスパッチ前に調整してください。

## サブエージェントのコンテキスト予算

各ワーカーは全トランスクリプトではなく、**要約した概要（〜1–2k トークン）**を返すべきです。理由:

- リードのコンテキストウィンドウが複数ワーカーの結果を統合するためにクリーンな状態を保てます。
- ワーカー内のツール呼び出し結果はワーカー内部の関心事であり、リードのものではありません。
- リードがより深い詳細を必要とする場合、全トレイルを取り込むのではなくワーカーにフォローアップを求めます。

アンチパターン: ワーカーが 50k トークンの生の出力を返す → リードが自分のウィンドウに複数ワーカーの結果を収めることができなくなります。

## 幅優先探索戦略

タスクが探索的な場合:

1. 全体を把握する広いクエリから始める。
2. 掘り下げる前に全体を評価する。
3. その後にのみワーカーを特定の方向にコミットする。

まず深く入ると、間違ったブランチを選んだ場合に呼び出しを無駄にします。

## 並列ディスパッチ入門

ローカルの並列ディスパッチ（Bash ループで多くの `claude -p` 呼び出しを実行する、または `git worktree` でセッションを分離する）については、[ワークフローパターン — バッチタスクの Fan-out](workflow-patterns-guide.md#fan-out-for-batch-tasks) を参照してください。そのガイドにはコストと安全に関する警告が含まれています; それを読まずに fan-out を実行しないでください。

Claude Code の `Agent` ツールによる*組み込み*のサブエージェントディスパッチの場合、上記のオーケストレーター-ワーカーパターンが直接対応します — 親セッションがリードであり、各 `Agent` 呼び出しがワーカーです。

## さらに読む

- [高度な機能ガイド — Agents](advanced-features-guide.md#agents) — 単一エージェント設計（Scope、Rules、Constraints、Verification）
- [ワークフローパターンガイド](workflow-patterns-guide.md) — fan-out、Writer/Reviewer、worktrees
- [マルチエージェントリサーチシステムの構築方法](https://www.anthropic.com/engineering/multi-agent-research-system)（Anthropic Engineering）
- [効果的なエージェントの構築](https://www.anthropic.com/engineering/building-effective-agents) — ワークフロー vs. エージェントの分類
- [並列 Claude チームによる C コンパイラの構築](https://www.anthropic.com/engineering/building-c-compiler) — 極端な並列性のケーススタディ
