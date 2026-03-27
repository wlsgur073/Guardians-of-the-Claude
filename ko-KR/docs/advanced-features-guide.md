---
title: "고급 기능"
description: "Hooks, agents, skills — 기본 설정을 넘어 Claude Code를 확장하는 방법"
date: 2026-03-23
---

# 고급 기능

기본 CLAUDE.md + rules 설정만으로는 부족해진 팀을 위한 세 가지 기능입니다. 이 기능들을 추가하기 전에 먼저 [시작 가이드](../getting-started.md)를 완료하세요.

## Hooks

Hooks는 Claude가 도구를 사용하기 전이나 후에 자동으로 실행되는 셸 명령입니다. `settings.json`의 `hooks` 키 아래에 정의합니다. 자동 린팅, 자동 포매팅, 파일 보호, 타입 검사 등에 활용할 수 있습니다.

### 설정 방법

```json
{
  "hooks": {
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
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"$CLAUDE_FILE_PATH\" | grep -qE '\\.env' && echo 'BLOCK: Protected file' && exit 1 || exit 0",
            "statusMessage": "Checking for protected files"
          }
        ]
      }
    ]
  }
}
```

주요 개념:

- **`matcher`** -- 파이프(`|`)로 구분된 도구 이름 또는 정규식 (예: `"Edit|Write"`, `"mcp__.*"`)
- **`$CLAUDE_FILE_PATH`** -- Claude가 편집 중인 파일 경로로, 자동으로 주입됩니다
- **`$CLAUDE_PROJECT_DIR`** -- 프로젝트 루트 디렉터리
- **`statusMessage`** -- hook 실행 중 UI에 표시되는 텍스트
- **`PreToolUse` + `exit 1`** -- 도구 동작을 차단합니다 (파일 보호 패턴)
- **`PostToolUse` + `|| true`** -- 도구 동작 후에 실행되며, 린트 오류가 Claude를 중단시키지 않도록 합니다
- 기타 이벤트: `Notification`, `Stop`, `SessionStart`, `SubagentStop` — 전체 이벤트 목록은 [hooks 문서](https://code.claude.com/docs/en/hooks)를 참고하세요

## Agents

Agents는 `.claude/agents/`에 정의하는 커스텀 역할입니다. 각 agent는 전문 범위, 도구 세트, 모델을 가지며, 코드베이스의 영역별로 다른 전문성이 필요한 대규모 프로젝트에 유용합니다. 역할 분리(프론트엔드, 백엔드, 테스트), 범위 제한, 모델 선택, 병렬 디스패치를 통한 팀 워크플로우 등에 활용할 수 있습니다.

### 설정 방법

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
model: "sonnet"
---

# Scope
Only modify files under `src/api/`, `src/services/`, and `src/repos/`.

## Rules
- Run `npm test` after making changes
- Use Zod schemas for all input validation
```

주요 필드:

- **`name`** / **`description`** -- agent의 이름과 전문 분야
- **`tools`** -- 허용되는 도구 (Read, Edit, Write, Bash, Grep, Glob, Agent, Skill)
- **`model`** -- 사용할 모델 (sonnet, opus, haiku)
- **`effort`** -- 처리 노력 수준 (high, medium, low)

frontmatter 뒤의 본문에서 범위와 규칙을 자연어로 정의합니다.

## Skills

Skills는 `.claude/skills/`에 정의하는 재사용 가능한 다단계 워크플로우입니다. 각 skill은 슬래시 명령이 되어 기능 스캐폴딩이나 컴포넌트 추가 같은 반복 작업을 자동화합니다. 반복적인 스캐폴딩, 표준화된 워크플로우, 다단계 프로세스 등에 활용할 수 있습니다.

### 설정 방법

`.claude/skills/<skill-name>/SKILL.md` 파일을 생성합니다:

```markdown
---
name: "add-endpoint"
description: "Scaffolds a new REST API endpoint with handler, service, and tests"
---

# Steps

## Step 1: Gather Information
Ask the user for the resource name and required operations.

## Step 2: Validate
Confirm the resource does not already exist. Run the test suite.

## Step 3: Execute
Create model, repository, service, handler, and test files.

## Step 4: Verify
Run build and tests to confirm everything works.
```

4단계 패턴(수집, 검증, 실행, 확인)은 skill의 동작을 예측 가능하게 만듭니다. Step 1에서는 `AskUserQuestion`으로 입력을 수집하고, Step 4에서는 빌드/테스트 명령을 실행하여 작업을 확인합니다. 각 skill은 슬래시 명령이 됩니다 — `/add-endpoint`를 입력하면 `.claude/skills/add-endpoint/SKILL.md`가 실행됩니다.

## 템플릿

`templates/advanced/`의 고급 스캐폴드를 프로젝트의 `.claude/` 디렉터리에 복사하세요. 이미 기본 `settings.json`이 있다면, 파일을 덮어쓰지 말고 `hooks`, `env`, `enabledPlugins` 키만 추가하세요. 완성된 TaskFlow 버전은 `examples/advanced/`를 참고하세요.

## 추가 자료

- [시작 가이드](../getting-started.md) -- 기본 설정 안내
- [설정 가이드](../settings-guide.md) -- 권한 및 기타 설정
- [Rules 가이드](../rules-guide.md) -- 모듈식 지침 파일
