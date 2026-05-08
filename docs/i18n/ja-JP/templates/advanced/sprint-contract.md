---
title: "Sprint Contract"
description: "Scope contract for the current work cycle"
version: "1.0.0"
---

# Sprint Contract

このファイルは現在のスプリントのスコープ境界を定義します。In Scope に
記載されていない作業は、ユーザーがこのファイルを明示的に更新しない限り
contract の対象外です。

## In Scope

- **Task CRUD endpoints** — Task エンティティに対する作成/取得/更新/削除の
  REST エンドポイント、認証済みユーザーにスコープ限定。
- **User 認証ベースライン** — メール/パスワードでのサインアップとログイン、
  refresh-token ローテーションを伴う JWT アクセストークン。
- **Task 所有権ルール** — Task レコードは認証済みユーザーにスコープ限定;
  ユーザー間アクセスは repository 層でブロック。
- **検証戦略** — エンドポイント、サービス、所有権ルールに対する Jest
  テストカバレッジ; `src/services/` は最低 80% line coverage。

## Deferred

- **Comment エンティティ** — Reason: ネストされたリソース設計が必要;
  Task CRUD 安定化まで保留。
- **OAuth プロバイダー** — Reason: プロバイダー選定、コールバックセキュリティ
  設計、シークレットの分離処理が必要。
- **メール通知** — Reason: SMTP/プロバイダーセットアップとメッセージテンプレート
  決定に依存。
- **リアルタイム更新 (WebSocket)** — Reason: コア REST API のリリース後;
  セッションアフィニティ設計が必要。
