---
title: ".claude/rules/ 사용하기"
description: "프로젝트 지침을 모듈화된 경로 범위 규칙 파일로 구성하는 방법"
date: 2026-03-18
---

# .claude/rules/ 사용하기

규칙 파일을 사용하면 프로젝트 지침을 집중된 단일 주제 모듈로 분리할 수 있습니다. 하나의 큰 CLAUDE.md 대신, 읽고 검토하기 쉬우며 코드베이스의 특정 부분에 범위를 지정할 수 있는 작은 파일 세트를 유지 관리합니다.

## Rules와 CLAUDE.md 사용 시점

**CLAUDE.md를 사용하는 경우:** 모든 세션에 필요한 핵심 지침 -- 빌드 명령, 프로젝트 개요, 테스트 지침, 주요 아키텍처 결정 사항.

**`.claude/rules/`를 사용하는 경우:** 모듈화된 주제별 지침 -- 특히 다음과 같은 경우:

- CLAUDE.md가 200줄을 넘어 분할이 필요한 경우
- 특정 파일 유형이나 디렉토리에만 적용되는 지침이 있는 경우
- 팀 구성원마다 담당 영역이 다른 경우 (프론트엔드 규칙, 백엔드 규칙, 테스트 규칙)
- 모놀리식 파일을 편집하지 않고 주제를 추가하거나 제거하고 싶은 경우

좋은 분할 방법: CLAUDE.md에는 핵심 사항(200줄 이하)을 넣고, 규칙 파일에는 세부 사항을 넣습니다.

## 파일 구조

파일당 하나의 주제를 유지하세요. 내용을 한눈에 알 수 있는 설명적인 파일명을 사용하세요:

```text
.claude/rules/
  code-style.md          # 네이밍, 포맷팅, import 규칙
  testing.md             # 테스트 프레임워크, 패턴, 커버리지 목표
  architecture.md        # 레이어 의존성 및 모듈 경계
  workflow.md            # 개발 전 체크리스트 및 리뷰 게이트
  api-design.md          # API 엔드포인트 규칙
  database.md            # 쿼리 패턴, 마이그레이션 규칙
  security.md            # 인증, 입력 검증, 시크릿 처리
```

대규모 프로젝트의 경우 규칙을 하위 디렉토리로 구성하세요:

```text
.claude/rules/
  frontend/
    components.md        # React 컴포넌트 패턴
    styling.md           # CSS/Tailwind 규칙
  backend/
    api-handlers.md      # Express 라우트 핸들러 규칙
    database.md          # PostgreSQL 쿼리 패턴
  shared/
    error-handling.md    # 공통 에러 처리 규칙
```

`paths` frontmatter가 없는 규칙 파일은 CLAUDE.md와 마찬가지로 매 세션마다 로드됩니다. 간결하게 유지하세요 -- 항상 로드되는 모든 규칙의 합계에도 동일한 "200줄 이하" 가이드라인이 적용됩니다.

## 경로 범위 지정

`paths` frontmatter 블록을 추가하면 Claude가 지정된 패턴과 일치하는 파일을 읽을 때만 규칙 파일이 로드됩니다:

```markdown
---
paths:
  - "src/api/**/*.ts"
---
# API Endpoint Rules
- All endpoints must validate input with Zod schemas
- Use the asyncHandler wrapper for all route handlers
```

경로 범위가 지정된 규칙은 매 세션이 아닌 필요할 때만 로드됩니다. 이를 통해 컨텍스트를 깔끔하게 유지할 수 있습니다 -- Claude는 API 파일을 작업할 때만 API 규칙을 확인합니다.

### Glob 패턴 참조

| 패턴 | 일치 대상 |
| --------- | --------- |
| `**/*.ts` | 모든 디렉토리의 TypeScript 파일 |
| `src/**/*` | src/ 하위의 모든 파일 |
| `*.md` | 프로젝트 루트의 Markdown 파일만 |
| `src/components/*.tsx` | 특정 디렉토리의 React 컴포넌트 |
| `src/**/*.{ts,tsx}` | 여러 확장자를 위한 중괄호 확장 |

`paths` 아래에 여러 패턴을 나열할 수 있습니다 -- 어느 패턴이든 일치하면 규칙이 로드됩니다:

```yaml
---
paths:
  - "src/api/**/*.ts"
  - "src/middleware/**/*.ts"
---
```

경로 범위가 지정된 규칙 파일의 전체 예시는 `examples/.claude/rules/api-endpoints.md`를 참고하세요.

## 사용자 수준 규칙

개인 규칙 파일을 `~/.claude/rules/`에 배치하면 모든 프로젝트에 적용됩니다:

```text
~/.claude/rules/
  personal-style.md      # 선호하는 코딩 규칙
  git-workflow.md        # 커밋 메시지 및 브랜치 작업 선호 사항
```

사용자 수준 규칙은 프로젝트 규칙보다 먼저 로드됩니다. 충돌이 발생하면 **프로젝트 규칙이 더 높은 우선순위를 가집니다** -- 팀의 규칙이 개인 선호 사항보다 우선합니다.

이는 프로젝트별이 아닌 순수하게 개인적인 선호 사항(에디터 설정, 선호하는 주석 스타일 등)에 유용합니다.

## 프로젝트 간 규칙 공유

심볼릭 링크를 사용하면 규칙 파일을 복제하지 않고도 프로젝트 간에 공유할 수 있습니다:

```bash
# 규칙 디렉토리 전체 공유
ln -s ~/shared-claude-rules .claude/rules/shared

# 단일 파일 공유
ln -s ~/company-standards/security.md .claude/rules/security.md
```

이 패턴은 조직 전체 표준에 적합합니다. 규칙 파일의 중앙 저장소를 유지하고 각 프로젝트에 심볼릭 링크를 생성하세요. 중앙 규칙이 업데이트되면 모든 프로젝트에 자동으로 변경 사항이 반영됩니다.

**참고:** 심볼릭 링크된 규칙은 읽기 시점에 해석됩니다. 심볼릭 링크 대상이 모든 개발자의 머신에 존재하는지 확인하거나, 설정 스크립트를 사용하여 생성하세요.

## 추가 참고 자료

- [CLAUDE.md 가이드](claude-md-guide.md) -- 효과적인 CLAUDE.md 파일 작성법 및 `@import` 구문
- [설정 가이드](settings-guide.md) -- 권한 및 기타 설정 구성
- [시작하기](getting-started.md) -- 규칙을 포함한 전체 설정 안내
