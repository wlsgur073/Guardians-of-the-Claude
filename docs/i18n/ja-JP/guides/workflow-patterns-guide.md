---
title: "ワークフローパターン"
description: "インタビュー優先の仕様策定、Writer/Reviewer、テスト先行マルチ Claude、fan-out（コスト・安全警告付き）、worktrees と並列セッション"
version: 1.0.1
---

# ワークフローパターン

Claude Code との時間をどのように構成するかは、何を尋ねるかと同じくらい重要です。これらのパターンは Anthropic の内部チームや外部のエンジニアリング報告書に繰り返し登場します。

*マルチエージェントディスパッチ*（オーケストレーターがワーカーを調整する方式）については、[マルチエージェントパターンガイド](multi-agent-patterns-guide.md) を参照してください。このガイドは、*人間であるあなた*がセッションとバッチをどのように構成するかに関するものです。

## `AskUserQuestion` で Claude にインタビューさせる

大きな機能を実装する際は、一度に自分で仕様を書こうとしないでください。まず Claude にインタビューさせましょう。

```text
I want to build [brief description]. Interview me in detail using the
AskUserQuestion tool.

Ask about technical implementation, UI/UX, edge cases, concerns, and
tradeoffs. Don't ask obvious questions — dig into the hard parts I might
not have considered.

Keep interviewing until we've covered everything, then write a complete
spec to SPEC.md.
```

インタビューが終わったら、**新しいセッション**を開始して仕様を実行します。新しいセッションは実装だけに集中したクリーンなコンテキストを持ち、書かれた参照文書があります。

なぜこれが効果的か:

- インタビューにより、暗黙的に処理していた決定が表面に出て、明示的にする必要があります。
- 新しいセッションで再開することで、実装がブレインストーミングに偏らなくなります。

## Writer/Reviewer パターン（マルチセッション）

| セッション A (Writer) | セッション B (Reviewer) |
|---|---|
| `Implement a rate limiter for our API endpoints` |   |
|   | `Review the rate limiter implementation in @src/middleware/rateLimiter.ts. Look for edge cases, race conditions, consistency with existing middleware patterns.` |
| `Here's the review feedback: [Session B output]. Address these issues.` |   |

Reviewer はフレッシュなコンテキストで、セッション A が書いたコードへの偏りがありません。これは、セッション内の「自分の作業をレビューして」というプロンプトでは見逃してしまう問題を捉えます。

同じ原則: 一方の Claude にテストを書かせ、もう一方にそれを通過するコードを書かせましょう。境界が明確になります。

## テスト先行マルチ Claude

1. セッション A: `Write tests for the user signup flow covering: valid signup, duplicate email, weak password, expired invite token, rate-limit exceeded.`
2. セッション B（新規）: `Implement the signup flow to pass tests in tests/signup.test.ts. Run the tests after each change.`

実装前に受け入れ基準を明確にします。一つのセッション内でも機能します（テスト作成、`/clear`、実装）が、別々のセッションの方がよりクリーンなコンテキストを提供します。

## バッチタスクの Fan-out

大規模なマイグレーションや分析のために、多くの `claude -p` 呼び出しを並列で実行します。

> **⚠️ コストと安全に関する警告**
>
> - ループ内の `claude -p` は呼び出しごとにトークンコストが発生します。2,000 ファイルのマイグレーションは数時間かかり、$100 以上の費用がかかる場合があります。
> - 常に 2–3 ファイルでドライランを先に行い、スケールアップ前に出力を検証してください。
> - 無人実行の権限をスコープするために `--allowedTools` を使用してください: `claude -p "..." --allowedTools "Edit,Bash(git commit:*)"`
> - Auto モードは `-p` 実行でクラシファイアの拒否が続くと中断します — 代わりに対応する人間がいません。閾値については [Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode) を参照してください。

パターン:

1. **タスクリストを生成**: `Have Claude list all 2,000 Python files that need migrating and write them to files.txt`.
2. **ループ**:

   ```bash
   for file in $(cat files.txt); do
     claude -p "Migrate $file from React to Vue. Return OK or FAIL." \
       --allowedTools "Edit,Bash(git commit:*)"
   done
   ```

**Windows PowerShell 同等の例:**

```powershell
Get-Content files.txt | ForEach-Object { claude -p "Migrate $_ from React to Vue. Return OK or FAIL." --allowedTools "Edit,Bash(git commit:*)" }
```

3. **最初の 2–3 件で調整してからスケール**: 初期段階で壊れたプロンプトを捉え; 出力の形を確認してから全セットで実行してください。

JSON 構造化出力（スクリプトでの解析）には `--output-format json` を追加してください。ストリーミングには `--output-format stream-json` を使用してください。

## Worktrees と並列セッション

本当に分離された並列作業が必要な場合（例: リスクのあるリファクタリングを実験しながら本線の作業を続ける場合）は、`git worktree` を使用してください。

```bash
git worktree add ../feature-x feature-x
cd ../feature-x
claude  # this session works on feature-x branch only; main worktree is untouched
```

worktree を使い終わったら、きれいに削除してください。

```bash
git worktree remove ../feature-x
git worktree list  # 削除を確認
```

`git worktree remove` を使わずにディレクトリだけを削除すると、古い worktree 登録が残り続けます。孤立したエントリを整理するには `git worktree prune` を実行してください。

| オプション | 最適な用途 |
|---|---|
| `git worktree`（CLI） | 同一マシン、完全な分離、手動調整 |
| デスクトップアプリのマルチセッション | 視覚的なセッション管理 |
| Web の Claude Code | Anthropic ホスティング、分離された VM |

マルチセッションを使わない*べき*とき: 小さく集中したタスク。セッション間のコンテキスト切り替えにはオーバーヘッドがあります — タスクが本当に独立していない限り、得るものより失うものが多くなります。

## さらに読む

- [マルチエージェントパターンガイド](multi-agent-patterns-guide.md) — オーケストレーターがワーカーをディスパッチする方式（人間が調整するマルチセッションとの比較）
- [Claude Code: Best practices for agentic coding](https://code.claude.com/docs/en/best-practices) — ここで取り上げる多くのパターンのアップストリームソース
- [Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode) — ヘッドレスおよびオートパイロットの詳細
