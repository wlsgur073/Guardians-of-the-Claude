---
title: "TaskFlow CLAUDE.md"
description: "Node.js/Express REST API 프로젝트를 위한 루트 CLAUDE.md 예시"
version: 1.1.0
---

<!--
  예시 스택 안내 (소스에는 보이지만 GitHub 렌더에서는 숨김)

  이 템플릿은 Node.js + Express + TypeScript + PostgreSQL로 구현된
  TaskFlow를 예시로 보여줍니다. TaskFlow는 가상의 레퍼런스 프로젝트이며,
  Node/Express 스택은 하나의 구체적 구현일 뿐 확정된 기본값이 아닙니다.

  섹션 구조와 패턴을 참고하세요. 실제 스택을 위해서는
  `/guardians-of-the-claude:create`을 실행하세요 — Claude가 매니페스트를
  탐지하여 동등한 명령어를 생성합니다.

  전체 컨벤션은 templates/README.md를 참조하세요.
-->

# 프로젝트 개요

TaskFlow는 작업 관리를 위한 REST API로, Node.js와 Express로 구축되었습니다.
데이터 영속성에 PostgreSQL, 세션 캐싱에 Redis를 사용합니다.

## 빌드 & 실행

npm install
npm run dev          # :3000 포트에서 핫 리로드 개발 서버 시작
npm run build        # TypeScript를 dist/로 컴파일
npm run lint         # ESLint 전체 프로젝트 실행

## 테스트

npm test             # Jest 전체 테스트 스위트 실행
npm run test:watch   # 개발용 watch 모드
npm run test:cov     # 커버리지 리포트와 함께 테스트 실행

테스트에는 실행 중인 PostgreSQL 인스턴스가 필요합니다 (docker-compose.yml 참고).
테스트 실행 전에 `docker compose up -d`를 실행하세요.

## 코드 스타일 & 컨벤션

- TypeScript strict 모드, 2칸 들여쓰기
- default export가 아닌 named export 사용
- 에러 타입은 src/errors/의 AppError를 확장
- 데이터베이스 쿼리는 src/repos/에 작성, 라우트 핸들러에서 직접 호출 금지
- 모든 비동기 라우트 핸들러는 asyncHandler 래퍼를 사용할 것

## 개발 접근 방식

- 요청이 모호하거나 불분명할 때, 즉시 구현을 시작하지 말 것
- 먼저 요청을 비판적으로 분석: 가정, 누락된 컨텍스트, 가능한 해석 식별
- 분석 결과를 제시하고 코드 작성 전에 구체적인 질문으로 명확화
- 명확화 후, 접근 방식을 간략히 설명하고 진행 전에 확인 받기

## 워크플로우

- 브랜치 네이밍: `feat/`, `fix/`, `chore/` 접두사
- 커밋 메시지: conventional commits 형식
- push 전 전체 테스트 스위트 실행: `npm test && npm run lint`
- 모든 PR은 CI 통과와 1명 이상의 리뷰 승인 필요

## 프로젝트 구조

- src/api/         → Express 라우트 핸들러와 미들웨어
- src/models/      → TypeScript 인터페이스와 Zod 검증 스키마
- src/repos/       → 데이터베이스 접근 레이어 (엔티티별 1파일)
- src/services/    → 비즈니스 로직 (핸들러가 호출, repos를 호출)
- src/errors/      → AppError를 확장하는 커스텀 에러 타입
- tests/           → src/ 구조를 미러링
- db/migrations/   → SQL 마이그레이션 파일 (npm run migrate로 실행)
- .claude/rules/   → 상세 가이드라인 (코드 스타일, 아키텍처, 테스트, 워크플로우)

## 사용 가능한 스킬

| 스킬 | 용도 |
| ---- | ---- |
| `/add-endpoint` | 핸들러, 서비스, 테스트가 포함된 새 API 엔드포인트 스캐폴딩 |
| `/run-checks` | 빌드, 린트, 테스트를 순서대로 실행 |

## 사용 가능한 에이전트

| 에이전트 | 모델 | 역할 |
| -------- | ---- | ---- |
| `backend-developer` | sonnet | API 구현, 서비스, 데이터베이스 접근 |
| `security-reviewer` | opus | 보안 취약점 분석 (읽기 전용) |
| `test-writer` | haiku | 프로젝트 컨벤션에 맞는 테스트 생성 |

## 중요 컨텍스트

- 인증은 JWT를 사용하며 리프레시 토큰은 Redis에 저장
- 모든 API 응답은 src/api/response.ts의 envelope 형식을 따름
- Rate limiting은 src/api/middleware/rateLimit.ts에서 라우트별로 설정
- 환경 변수는 시작 시 src/config.ts를 통해 검증

## 참조

@docs/architecture.md
@docs/api-conventions.md
@README.md
