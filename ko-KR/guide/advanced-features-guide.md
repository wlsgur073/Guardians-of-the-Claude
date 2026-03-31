---
title: "고급 기능"
description: "Hooks, agents, skills — 기본 설정을 넘어 Claude Code를 확장하는 방법"
date: 2026-03-23
---

# 고급 기능

기본 CLAUDE.md + rules만으로는 부족해진 팀을 위한 세 가지 기능입니다. 먼저 [시작 가이드](getting-started.md)를 완료하세요. 완성된 예시는 `templates/advanced/`를 참고하세요.

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
- **`$CLAUDE_FILE_PATH`** / **`$CLAUDE_PROJECT_DIR`** -- 자동 주입되는 경로 변수
- **`statusMessage`** -- hook 실행 중 UI에 표시되는 텍스트
- **`PreToolUse` + `exit 1`** 은 도구 동작을 차단하고, **`PostToolUse` + `|| true`** 는 동작 후에 실행됩니다
- 기타 이벤트: `Notification`, `Stop`, `SessionStart`, `SessionEnd`, `SubagentStop`, `UserPromptSubmit`, `PreCompact` — 전체 목록은 [hooks 문서](https://code.claude.com/docs/en/hooks)를 참고하세요
- **Hook 유형:** `"type": "command"` (셸) 또는 `"type": "prompt"` (LLM 기반, `PreToolUse`, `Stop`, `SubagentStop`, `UserPromptSubmit`에서 사용 가능)

## Agents

Agents는 `.claude/agents/`에 정의하는 커스텀 역할로, 전문 범위·도구 세트·모델을 가집니다. 역할 분리, 범위 제한, 대규모 코드베이스에서의 병렬 디스패치에 유용합니다.

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
color: "green"
---

# Scope
Only modify files under `src/api/`, `src/services/`, and `src/repos/`.

## Rules
- Run `npm test` after making changes
- Use Zod schemas for all input validation
```

주요 필드:

- **`name`** / **`description`** -- agent의 이름과 전문 분야
- **`tools`** -- 허용되는 도구 (Read, Edit, Write, Bash, Grep, Glob 등)
- **`model`** -- 사용할 모델 (`sonnet`, `opus`, `haiku`, `inherit`)
- **`color`** -- UI 표시 색상 (`blue`, `cyan`, `green`, `yellow`, `magenta`, `red`)

> **예시:** 완성된 agent 정의는 `templates/advanced/.claude/agents/backend-developer.md`를 참고하세요.

## Skills

Skills는 `.claude/skills/`에 정의하는 재사용 가능한 다단계 워크플로우입니다. 각 skill은 슬래시 명령이 되어 기능 스캐폴딩이나 컴포넌트 추가 같은 반복 작업을 자동화합니다.

### 설정 방법

`.claude/skills/<skill-name>/SKILL.md` 파일을 생성합니다:

```markdown
---
name: "add-endpoint"
description: "Scaffolds a new REST API endpoint with handler, service, and tests"
allowed-tools: [Read, Edit, Write, Bash, Grep, Glob]
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
- **`allowed-tools`** -- 사용 가능한 도구 제한 (참고: skill은 `allowed-tools`, agent는 `tools`를 사용)
- **`argument-hint`** -- 슬래시 명령 메뉴에 표시되는 사용법 힌트 (예: `"<resource> [operations]"`)
- **`user-invocable`** -- 슬래시 명령 메뉴에 표시 여부 (기본값: `true`)
- **`disable-model-invocation`** -- Claude의 자동 트리거 방지 (기본값: `false`)
- **`model`** -- skill 활성 시 사용할 모델 오버라이드

Skill은 두 가지 유형이 있습니다: **user-invoked** (슬래시 명령)와 **model-invoked** (Claude가 컨텍스트 기반으로 자동 트리거). model-invoked의 description에는 트리거 문구를 포함하세요: `"Use when the user asks to 'do X' or 'do Y'."` Skill은 SKILL.md 외에 보조 파일을 포함할 수 있습니다: `references/`, `examples/`, `scripts/`.

> **참고:** 레거시 `commands/` 디렉터리는 deprecated되었습니다. 모든 skill 유형에 `skills/<name>/SKILL.md`를 사용하세요.

> **예시:** 완성된 skill 구조는 `templates/advanced/.claude/skills/add-endpoint/`를 참고하세요.

## 추가 자료

- [시작 가이드](getting-started.md) -- 기본 설정 안내
- [설정 가이드](settings-guide.md) -- 권한 및 기타 설정
- [Rules 가이드](rules-guide.md) -- 모듈식 지침 파일
