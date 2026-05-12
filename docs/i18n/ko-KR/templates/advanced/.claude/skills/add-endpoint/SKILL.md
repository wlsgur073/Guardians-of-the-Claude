---
name: "add-endpoint"
description: "TaskFlow용 REST API 엔드포인트를 핸들러, 서비스, 레포지토리, 테스트, Zod 스키마와 함께 스캐폴딩"
argument-hint: "<resource> [operations]"
---

# 단계

## 단계 1: 정보 수집

TaskFlow API 패턴을 위해 `references/api-conventions.md`를 읽습니다.

`$ARGUMENTS`에서 리소스 이름과 작업을 파싱합니다 (예: `/add-endpoint comment create,read,list,delete`). `$ARGUMENTS`가 비어 있으면 사용자에게 질문합니다:
- 리소스 이름은 무엇인가요? (예: "comment")
- 어떤 CRUD 작업이 필요한가요? (예: "create, read, list, delete")
- 기존 엔티티에 속하나요? (예: task 댓글이라면 "tasks")

## 단계 2: 검증

- `src/api/`에 해당 리소스가 이미 존재하지 않는지 확인
- 중첩 리소스인 경우 상위 엔티티가 존재하는지 확인
- 변경 전 테스트 스위트가 통과하는지 확인 (`npm test`)

## 단계 3: 실행

기존 패턴을 따라 다음 파일을 생성합니다:

1. `src/models/<resource>.ts` -- Zod 스키마와 TypeScript 타입
2. `src/repos/<resource>-repo.ts` -- 데이터베이스 쿼리가 포함된 레포지토리 클래스
3. `src/services/<resource>-service.ts` -- 비즈니스 로직이 포함된 서비스 클래스
4. `src/api/<resource>.ts` -- asyncHandler 래퍼를 사용하는 라우트 핸들러
5. `tests/services/<resource>-service.test.ts` -- 서비스 단위 테스트
6. `tests/api/<resource>.test.ts` -- Supertest를 사용한 API 통합 테스트

`src/api/index.ts`에 새 라우트를 등록합니다.

## 단계 4: 검증

- `npm run build`를 실행하여 TypeScript 컴파일 확인
- `npm test`를 실행하여 모든 테스트 통과 확인
- `src/api/index.ts`에 새 라우트가 등록되었는지 확인
