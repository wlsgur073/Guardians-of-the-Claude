---
title: "TaskFlow 테스트 규칙"
description: "TaskFlow 프로젝트의 Jest 테스트 컨벤션"
---

# 테스트 컨벤션

## 프레임워크
- 단위 및 통합 테스트에 Jest와 ts-jest 사용
- HTTP 엔드포인트 테스트에 Supertest 사용

## 구조
- `src/` 디렉토리를 미러링: `tests/services/`는 `src/services/`를 테스트
- `describe` 블록은 메서드 또는 동작별로 그룹화
- 테스트 파일 네이밍: `<module>.test.ts`

## 데이터
- 테스트 데이터는 `tests/factories/`의 팩토리 사용 — 인라인 객체 생성 금지
- 각 팩토리는 기본적으로 유효한 엔티티를 반환; 테스트에 필요한 것만 오버라이드
- 예시: `createUser({ email: 'test@example.com' })`

## 데이터베이스
- 통합 테스트는 실제 PostgreSQL에 접속 — 데이터베이스를 mock하지 않음
- 각 테스트 파일은 스위트 종료 후 롤백되는 별도 트랜잭션을 사용
- 설정 및 정리에 `tests/helpers/db.ts` 사용

## 커버리지
- src/services/ 최소 80% 라인 커버리지
- 모든 에러 경로에 최소 1개의 테스트 필수
- `npm run test:cov`로 확인
