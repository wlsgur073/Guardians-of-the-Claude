---
title: "고급 기능"
description: "Hooks, agents, skills — 기본 설정을 넘어 Claude Code를 확장하는 방법"
version: 1.2.1
---

# 고급 기능

기본 CLAUDE.md + rules만으로는 부족해진 팀을 위한 세 가지 기능입니다. 먼저 [시작 가이드](getting-started.md)를 완료하세요. 완성된 예시는 `templates/advanced/`를 참고하세요.

## Hooks

Hooks는 Claude가 도구를 사용하기 전이나 후에 자동으로 실행되는 셸 명령입니다. `settings.json`의 `hooks` 키 아래에 정의합니다. 자동 린팅, 자동 포매팅, 파일 보호, 타입 검사 등에 활용할 수 있습니다.

### Hook 설정 방법

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"$CLAUDE_FILE_PATH\" | grep -qE '(package-lock\\.json|\\.env|migrations/)' && echo 'Protected file' && exit 2 || exit 0",
            "statusMessage": "Checking for protected files"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "npx eslint --fix \"$CLAUDE_FILE_PATH\" 2>/dev/null || true",
            "statusMessage": "Auto-linting edited file"
          }
        ]
      }
    ]
  }
}
```

주요 개념:

- **`matcher`** -- 파이프(`|`)로 구분된 도구 이름 또는 정규식 (예: `"Edit|Write"`, `"mcp__.*"`)
- **`$CLAUDE_FILE_PATH`** / **`$CLAUDE_PROJECT_DIR`** -- 자동 주입되는 경로 변수
- **`statusMessage`** -- hook 실행 중 UI에 표시되는 텍스트
- **`PreToolUse` + `exit 2`** 는 도구 동작을 차단하고 Claude에게 이유를 알려줍니다 -- `.env`나 마이그레이션 디렉터리 같은 민감한 파일 보호에 사용
- **`PostToolUse` + `|| true`** 는 도구 동작 완료 후 실행됩니다 -- 자동 린팅이나 포매팅에 사용
- **`UserPromptSubmit`** 은 Claude가 사용자 입력을 처리하기 전에 실행됩니다 -- 키워드 감지나 자동 컨텍스트 주입에 사용
- 기타 이벤트: `Notification`, `Stop`, `SessionStart`, `SessionEnd`, `SubagentStop`, `PreCompact` — 전체 목록은 [hooks 문서](https://code.claude.com/docs/en/hooks)를 참고하세요
- **실용 조합:** `SessionStart`로 세션 시작 시 프로젝트 컨텍스트 주입, `PreCompact`로 자동 압축 전 핵심 메모 보존, `SubagentStop`로 에이전트 결과물을 부모 세션에 반환하기 전 검증
- **Hook 유형:** `"type": "command"` (셸) 또는 `"type": "prompt"` (LLM 기반, `PreToolUse`, `Stop`, `SubagentStop`, `UserPromptSubmit`에서 사용 가능)

### 스크립트 기반 Hook

복잡한 로직에는 외부 스크립트를 사용하세요: `"command": "bash \"${CLAUDE_PROJECT_DIR}/scripts/my-hook.sh\""`. 스크립트는 테스트 가능하고, 버전 관리가 되며, 유지보수가 더 쉽습니다. 전체 예시는 `templates/advanced/.claude/settings.json`을 참고하세요. `timeout`은 항상 명시적으로 설정하세요 — 입력 검증 3-5초, 린트/포맷 10-15초, 빌드/테스트 30초 이상.

## Agents

Agents는 `.claude/agents/`에 정의하는 커스텀 역할로, 전문 범위·도구 세트·모델을 가집니다. 역할 분리, 범위 제한, 대규모 코드베이스에서의 병렬 디스패치에 유용합니다.

### Agent 설정 방법

`.claude/agents/<name>.md` 파일을 YAML frontmatter와 함께 생성합니다:

```markdown
---
name: "Backend Developer"
description: "Specializes in API layer, services, and database access"
tools:
  - Read
  - Edit
  - Write
  - Bash
# sonnet: balances speed and quality for implementation tasks
model: "sonnet"
color: "green"
---

## Scope
Only modify files under `src/api/`, `src/services/`, `src/repos/`, and `tests/`.

## Rules
- Follow the asyncHandler wrapper pattern for all route handlers
- All database access must go through repository classes in `src/repos/`
- Use Zod schemas from `src/models/` for all input validation

## Constraints
- Never modify migration files or `package-lock.json` without explicit approval
- Never call repositories directly from route handlers — always through services

## Verification
- `npm test` passes, `npm run lint` clean, `npm run build` compiles
- New endpoints include JSDoc tags: @route, @method, @auth
```

네 가지 섹션이 agent 프롬프트를 간결하게 유지합니다: **Scope**는 agent가 다룰 수 있는 범위, **Rules**는 작업 방식, **Constraints**는 피해를 방지하는 절대 제한, **Verification**은 작업 완료 확인 방법을 정의합니다. 모든 agent에 네 섹션이 필요한 것은 아닙니다 — 복잡도에 맞게 조절하세요. 모델 선택 이유는 YAML 주석에 남겨 나중에 보는 사람이 의도를 파악할 수 있도록 합니다.

### 모델 선택

| 모델 | 적합한 용도 | 예시 agent |
| ---- | ---------- | --------- |
| `haiku` | 빠른 조회, 파일 검색, 탐색 | explorer, linter |
| `sonnet` | 구현, 디버깅, 테스트 작성 | backend-dev, debugger |
| `opus` | 아키텍처 리뷰, 심층 분석 | code-reviewer, architect |

`"inherit"`를 사용하면 상위 세션의 모델을 따릅니다. 선택 이유는 YAML 주석(`# opus: needs deep analysis for security review`)으로 남겨 자체 문서화하세요.

**비용 트레이드오프:** `haiku`는 `opus` 대비 ~60배 저렴합니다. 기본은 `sonnet`을 사용하고, 대량 읽기 전용 작업에는 `haiku`, 단 한 번의 실수도 비용이 큰 작업(보안 리뷰, 아키텍처 결정)에만 `opus`를 사용하세요.

### 에이전트 설계 패턴

**하나의 에이전트, 하나의 관점.** 구현, 리뷰, 테스트를 하나의 에이전트에 결합하지 마세요 -- 집중된 역할로 분리하세요.

**읽기 전용 에이전트:** `tools`에서 Edit과 Write를 제거하여 분석 전용 에이전트를 만들 수 있습니다. 보안 리뷰, 아키텍처 분석, 코드 탐색에 유용합니다.

**에이전트 파이프라인:** 다단계 워크플로우를 위해 에이전트를 연결하세요: `backend-developer` (구현) → `security-reviewer` (리뷰) → `test-writer` (테스트).

## Skills

Skills는 `.claude/skills/`에 정의하는 재사용 가능한 다단계 워크플로우입니다. 각 skill은 슬래시 명령이 되어 기능 스캐폴딩이나 컴포넌트 추가 같은 반복 작업을 자동화합니다.

### Skill 설정 방법

`.claude/skills/<skill-name>/SKILL.md` 파일을 생성합니다:

```markdown
---
name: "add-endpoint"
description: "Scaffolds a new REST API endpoint with handler, service, and tests"
argument-hint: "<resource> [operations]"
---

# Steps

## Step 1: Gather Information
Read `references/api-conventions.md` for project patterns.
Parse `$ARGUMENTS` for resource name and operations. If empty, ask the user.

## Step 2: Validate
Confirm the resource does not already exist. Run the test suite.

## Step 3: Execute
Create model, repository, service, handler, and test files.

## Step 4: Verify
Run build and tests to confirm everything works.
```

주요 필드:

- **`name`** / **`description`** -- skill의 이름과 용도
- **`argument-hint`** -- 슬래시 명령 메뉴에 표시되는 사용법 힌트 (예: `"<resource> [operations]"`)
- **`user-invocable`** -- 슬래시 명령 메뉴에 표시 여부 (기본값: `true`)
- **`disable-model-invocation`** -- Claude의 자동 트리거 방지 (기본값: `false`)
- **`model`** -- skill 활성 시 사용할 모델 오버라이드

Skill은 두 가지 유형이 있습니다: **user-invoked** (슬래시 명령)와 **model-invoked** (Claude가 컨텍스트 기반으로 자동 트리거). model-invoked의 description에는 트리거 문구를 포함하세요: `"Use when the user asks to 'do X' or 'do Y'."` Skill은 SKILL.md 외에 보조 파일을 포함할 수 있습니다: `references/`, `examples/`, `scripts/`.

### 스킬 설계 패턴

**인자 파싱:** `$ARGUMENTS`를 사용하여 매개변수를 받으세요. Step 1에서 플래그와 위치 인자를 파싱하세요 -- 비어 있으면 사용자에게 물어보세요.

**참조 파일:** 프로젝트 규칙, 예시, API 문서를 SKILL.md 옆의 `references/`에 넣으세요. 처음부터가 아니라 필요한 단계에서 읽으세요 -- 이렇게 하면 컨텍스트를 절약할 수 있습니다.

**폴백 패턴:** skill이 선택적 도구(MCP 서버, CI 시스템)에 의존하는 경우, 두 가지 경로를 제공하세요: 경로 A는 도구가 사용 가능할 때, 경로 B는 수동 대안으로 폴백합니다.

> **참고:** 레거시 `commands/` 디렉터리는 deprecated되었습니다. 모든 skill 유형에 `skills/<name>/SKILL.md`를 사용하세요.

### 플러그인 스킬 실전 예시

`claude-code-template` 플러그인은 역할별 스킬 워크플로우를 보여주는 네 가지 스킬로 구성됩니다:

| Skill | 용도 |
| ----- | ------- |
| `/claude-code-template:create` | 가이드 기반 설정 마법사 -- CLAUDE.md, settings, rules, 선택적 기능 생성 |
| `/claude-code-template:audit` | 종합적인 설정 평가 및 점수 산출 |
| `/claude-code-template:secure` | 보안 개선 -- deny 패턴, 보안 규칙, 파일 보호 hooks |
| `/claude-code-template:optimize` | 설정 품질 개선 -- rules 분리, 에이전트 다양화, MCP, hook 품질 |

**권장 워크플로우:** `/create` → `/audit` → `/secure` 또는 `/optimize` → `/audit` (재검증). 각 스킬은 다음 스킬로 연결되며, `.claude/.plugin-cache/`의 타임스탬프 파일로 상태를 공유합니다.

## 추가 자료

- [시작 가이드](getting-started.md) -- 기본 설정 안내
- [설정 가이드](settings-guide.md) -- 권한 및 기타 설정
- [MCP 연동 가이드](mcp-guide.md) -- MCP를 통해 외부 도구 연결
- [Rules 가이드](rules-guide.md) -- 모듈식 지침 파일
