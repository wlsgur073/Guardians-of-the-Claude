# templates/ — TaskFlow 레퍼런스 예시

이 디렉토리는 가상의 프로젝트 **TaskFlow**에 대한 완성된 설정 예시(`CLAUDE.md`, `.claude/settings.json`, rules, hooks, agents, skills)를 담고 있습니다. TaskFlow는 이 저장소 전반에서 레퍼런스로 사용되는 가상의 작업 관리 REST API입니다.

## TaskFlow에 대하여

TaskFlow는 **특정 기술 스택이 아닙니다.** 다음과 같은 개념적 프로젝트입니다:

- 작업 관리를 위한 REST API (users, tasks, comments)
- 영속 저장소와 세션 캐시
- 인증, 입력 검증, 구조화된 에러 처리
- 전형적인 백엔드 관심사: rate limiting, 데이터베이스 마이그레이션, 자동화된 테스트

이 가상 프로젝트는 가이드, `plugin/skills/create/SKILL.md`, 그리고 모든 예제 코드에서 동일하게 참조됩니다. 문서 간 교차 참조가 단순해지도록 — 저장소의 모든 예제를 이해하기 위해 하나의 가상 프로젝트만 기억하면 됩니다.

## 현재 완성된 예시에 대하여

`starter/`와 `advanced/` 아래의 현재 템플릿은 **Node.js / Express / TypeScript / PostgreSQL / Redis / Jest**를 구체적 구현으로 사용합니다. 이는 Node/Express를 "기본" 스택으로 확정한 것이 **아닙니다.** 다음과 같은 이유로 선택된 하나의 구현일 뿐입니다:

- Node/Express는 REST API의 잘 알려진 출발점입니다
- 특정 파일 (`src/api/`, `src/services/`, `src/repos/`)에 대한 교차 참조가 하나의 공유 예제로 작성하면 쉬워집니다
- 생태계가 안정적이고 널리 이해되는 도구(npm, Jest, ESLint, TypeScript)를 갖고 있습니다

**실제 스택이 다른 것이 오히려 일반적입니다.** 다음 명령을 실행하면:

```text
> /guardians-of-the-claude:create
```

Claude Code는 사용자의 실제 프로젝트에 적응합니다:

1. **기존 매니페스트 탐지** — `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `Gemfile` 등
2. **빈 프로젝트의 경우 스택 질의** — 언어, 프레임워크, build/test/lint 명령어
3. **동등한 명령어 생성** — `npm test` 대신 `pytest`, `eslint` 대신 `ruff check`, `npm run build` 대신 `cargo build` 등

생성된 `CLAUDE.md`는 이 템플릿과 동일한 섹션 구조를 따르지만, 사용자 실제 스택에 맞는 명령어와 경로를 가집니다.

## 왜 스택별 변형을 만들지 않는가?

이 저장소는 의도적으로 `templates/python/`, `templates/go/`, `templates/nextjs/` 같은 스택별 디렉토리를 **유지하지 않습니다.** 이유:

- **유지보수가 스택 수에 선형 비례**하고, 각 스택의 생태계 업데이트(프레임워크 신 버전, 새 lint 도구, 새 테스트 러너)마다 독립적으로 관리해야 합니다
- **스택은 문서보다 빠르게 진화합니다** — 6개월 된 완성 템플릿은 이미 부분적으로 오해의 소지가 있고, 사용자가 어느 부분이 최신인지 판단하기 어렵습니다
- **진짜 제품은 `/create`** — Claude는 런타임에 적응하며, 이는 정적 템플릿이 따라올 수 없는 방식입니다. 정적 템플릿은 **읽기 위한** 출발점이고, `/create`는 **만들기 위한** 출발점입니다
- **유지보수 역량은 유한합니다** — 하나의 고품질 예제가 5개의 반쯤 관리되는 예제보다 낫습니다

프로젝트 방향과 "Stack-adaptive improvements" 백로그 항목은 [`docs/ROADMAP.md`](../../../docs/ROADMAP.md)를 참고하세요.

## 이 템플릿들을 어떻게 읽어야 하는가

**참고해야 할 것:**

- 섹션 구조 (CLAUDE.md가 가져야 할 섹션들)
- 패턴 (rules 분리 방식, agents scoping, hooks 연결 방식)
- 컨벤션 (네이밍, 커밋 스타일, verification gate, review gate)
- 각 선택의 **왜**가 주석이나 가이드 교차 참조에 문서화되어 있습니다

**문자 그대로 복사하지 말 것:**

- 정확한 `npm` / `Jest` 명령 — 사용자 스택의 등가물로 교체
- Node 특화 경로(`src/api/`, `src/services/`, `src/repos/`) — 프로젝트 레이아웃 사용
- 예제 내 패키지 특화 코드(`asyncHandler`, Zod 스키마, `ts-jest` 설정) — 스택 등가물 사용

레퍼런스를 읽는 대신 가이드 기반 생성을 원한다면, `/guardians-of-the-claude:create`을 실행하세요. Claude가 사용자 실제 프로젝트에 맞는 `CLAUDE.md`와 `settings.json`을 생성합니다.
