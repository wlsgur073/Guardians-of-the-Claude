---
title: "Sprint Contract"
description: "Scope contract for the current work cycle"
version: "1.0.0"
---

# Sprint Contract

이 파일은 현재 sprint의 scope 경계를 정의합니다. In Scope에 명시되지 않은
작업은 사용자가 이 파일을 명시적으로 갱신하지 않는 한 contract 밖에 있습니다.

## In Scope

- **Task CRUD endpoints** — Task entity에 대한 생성/조회/수정/삭제 REST endpoint,
  인증된 사용자로 범위 제한.
- **User 인증 베이스라인** — 이메일/비밀번호 가입과 로그인, refresh-token rotation을
  갖춘 JWT access token.
- **Task 소유권 규칙** — Task 레코드는 인증된 사용자로 범위 제한; 사용자 간
  접근은 repository layer에서 차단.
- **검증 전략** — Endpoint, service, 소유권 규칙에 대한 Jest 테스트 커버리지;
  `src/services/`는 최소 80% line coverage.

## Deferred

- **Comment entity** — Reason: 중첩 리소스 설계 필요; Task CRUD가 안정화될
  때까지 보류.
- **OAuth providers** — Reason: provider 선정, callback 보안 설계, secret 분리
  처리 필요.
- **이메일 알림** — Reason: SMTP/provider 설정과 메시지 템플릿 결정에 의존.
- **실시간 업데이트 (WebSocket)** — Reason: 핵심 REST API ship 이후;
  session affinity 설계 필요.
