---
title: "시작하기"
description: "프로젝트에 Claude Code 설정을 구성하는 단계별 가이드"
version: 1.2.5
---

# 시작하기

이 가이드는 첫 설치부터 정상 동작 확인까지, 프로젝트에 Claude Code 설정을 구성하는 전체 과정을 안내합니다.

## 사전 준비

- Claude Code가 설치되어 있고 정상 동작하는 상태 (`claude --version`으로 확인)
- 설정을 적용할 프로젝트
- **Windows 사용자**: 플러그인 SessionStart 훅은 bash 스크립트와 PowerShell 스크립트(`plugin/hooks/session-start.ps1`)를 함께 제공하고, advanced 템플릿의 `validate-prompt` 훅도 동일하게 `.ps1` 동반 스크립트(`templates/advanced/hooks/validate-prompt.ps1`)를 함께 제공합니다. PowerShell 5.1+ (Windows 10+ 기본 탑재) 또는 Git Bash/WSL 중 어느 쪽이든 양쪽 레이어가 모두 동작합니다 — 추가 쉘 설정 불필요

## Step 1: 설정 방법 선택

| 옵션 | 하는 일 | 적합한 경우 |
| ---- | ------ | ---------- |
| `/init` | 코드 분석 후 기본 CLAUDE.md 생성 | 빠른 시작 — 대부분의 프로젝트에 적합 |
| `/guardians-of-the-claude:create` | 대화형 인터뷰 → CLAUDE.md + 설정 + 규칙 + 선택적 기능 | 종합적인 설정 ([Day 1 빠른 시작](../README.md#day-1--2분-빠른-시작)) |

**`/init`**은 [공식 권장 첫 단계](https://code.claude.com/docs/en/best-practices)입니다 -- Claude가 코드베이스를 분석하고 CLAUDE.md를 자동 생성합니다:

```text
claude
> /init
```

**`/guardians-of-the-claude:create`**은 `/init` 스타일 분석에 더해 규칙, 권한, 선택적 고급 기능을 한 번에 생성합니다. 먼저 플러그인을 설치하세요 (`/plugin marketplace add wlsgur073/Guardians-of-the-Claude` 후 `/plugin install guardians-of-the-claude`). **둘 다 사용?** `/init`을 먼저 실행한 후, `/guardians-of-the-claude:create`에서 "기존 프로젝트"를 선택하세요 — 기존 CLAUDE.md를 감지하여 덮어쓰지 않고 병합합니다.

## Step 2: 템플릿 복사 (수동 대안)

1단계에서 `/guardians-of-the-claude:create`을 사용했다면 이 단계를 건너뛰세요 — 파일이 이미 생성되었습니다.

수동으로 참고하려면 `templates/starter/`와 `templates/advanced/`의 완성 예시(가상 "TaskFlow" 프로젝트)를 확인하세요. 각 경로의 완성된 설정이 어떤 모습인지 보여줍니다:

> **TaskFlow 예시 스택에 대한 안내:** 현재 완성된 템플릿은 Node.js/Express/TypeScript/PostgreSQL을 구체적 예시로 사용합니다. TaskFlow 자체는 가상의 레퍼런스 프로젝트입니다 (자세한 내용은 [`templates/README.md`](../../../../templates/README.md) 참조). `/create`는 프로젝트가 **반드시** Node/Express여야 하는 것은 **아닙니다** — 실제 매니페스트(`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `Gemfile`)를 탐지하거나 빈 프로젝트의 경우 스택 질문을 한 뒤, 동등한 명령어를 생성합니다.

**Starter** (입문자 추천):

```bash
# 스타터 예시를 참고하세요
# templates/starter/CLAUDE.md 및 templates/starter/.claude/settings.json 참조
```

**Advanced** (전체 설정):

```bash
# 고급 예시를 참고하세요
# templates/advanced/CLAUDE.md 및 templates/advanced/.claude/ 참조
```

`/init`으로 이미 CLAUDE.md를 생성했다면, 템플릿의 섹션을 기존 파일에 병합하세요. 템플릿은 일관된 섹션 구조를 제공하고, `/init`은 프로젝트에 특화된 내용을 제공합니다. 양쪽의 장점을 결합하세요.

## Step 3: CLAUDE.md 작성

1단계에서 `/guardians-of-the-claude:create`을 사용했다면 이 단계를 건너뛰세요 — 6개의 canonical 섹션이 이미 생성되어 있습니다. `/memory`로 CLAUDE.md가 로드되었는지 확인한 후 Step 4로 넘어가세요.

수동으로 CLAUDE.md를 작성하는 경우, 아래 섹션을 채우세요. `/audit`가 동일한 루브릭으로 채점할 수 있도록 동일한 구조를 유지하세요:

1. **Project Overview** -- 한두 문장으로: 프로젝트가 무엇을 하는지, 언어와 프레임워크.
2. **Build & Run** -- 의존성 설치와 실행에 필요한 정확한 명령어.
3. **Testing** -- Claude가 자신의 작업을 검증할 수 있는 테스트 명령어.
4. **Code Style & Conventions** -- 언어 기본값과 다른 규칙만. 구체적으로.
5. **Development Approach** -- 모호한 요청을 Claude가 어떻게 다룰지 (가정 분석 → 질문 → 접근 확인 후 구현). `/create`가 4줄 기본값을 시드합니다.
6. **Important Context** -- 명확하지 않은 것들: 필수 서비스, 인증 패턴, 환경 특이사항.

기준선을 넘어 확장이 필요해지면 `Workflow`, `Project Structure`, `References`, `Available Skills`/`Available Agents` 표를 추가할 수 있습니다 — 완성 예시는 [`templates/advanced/CLAUDE.md`](../../../../templates/advanced/CLAUDE.md)를 참고하세요. 각 섹션에 무엇을 포함하고 제외할지는 [CLAUDE.md 가이드의 포함/제외 표](claude-md-guide.md#포함할-것과-제외할-것)를 참고하세요.

## Step 4: Rules 설정 (선택)

CLAUDE.md가 200줄을 넘어가거나, 특정 파일 유형에만 적용되는 지침이 있다면 `.claude/rules/` 파일로 분리하세요.

Rules를 사용하면 좋은 경우:

- **모듈화된 구성** -- 주제별 하나의 파일 (예: `testing.md`, `code-style.md`)
- **경로 기반 스코핑** -- Claude가 해당 파일을 읽을 때만 로드되는 규칙
- **팀 협업** -- 팀원별로 다른 rule 파일을 관리

매 세션에 필요한 핵심 지침은 CLAUDE.md에 유지하세요. 전체 안내는 [Rules 가이드](rules-guide.md)를 참고하세요.

## Step 5: 권한 설정

`.claude/settings.json`을 편집해서 Claude가 자주 실행하는 명령어를 사전 승인하세요. 이렇게 하면 작업 중 권한 확인 프롬프트가 줄어듭니다:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm test)",
      "Bash(npm run lint)"
    ],
    "deny": [
      "Read(./.env)"
    ]
  }
}
```

`allow` 목록은 `Tool(specifier)` 구문을 사용합니다. 테스트와 빌드 명령어부터 시작하세요 -- 가장 안전하고 자주 사용됩니다. 모든 옵션에 대해서는 [Settings 가이드](settings-guide.md)를 참고하세요.

## Step 6: 동작 확인

프로젝트에서 Claude Code를 실행하고 모든 것이 정상적으로 로드되었는지 확인하세요:

1. `/memory` 실행 -- 로드된 모든 CLAUDE.md 파일과 rules가 표시됩니다. 파일이 나타나는지 확인하세요.
2. 간단한 작업 시도 -- Claude에게 프로젝트 구조를 설명하거나 테스트를 실행해 달라고 요청하세요.
3. Claude가 지침을 따르는지 확인 -- 규칙을 무시한다면, CLAUDE.md가 너무 길거나 지침이 너무 모호한 것일 수 있습니다.

## Step 7: 고급 기능 탐색 (선택)

기본 설정이 잘 동작하면, hooks, agents, skills 같은 고급 기능을 탐색해 보세요. [고급 기능 가이드](advanced-features-guide.md)를 참고하세요.

**스타터에서 고급으로 업그레이드:** `/guardians-of-the-claude:create`을 다시 실행하고, 첫 번째 질문에서 "기존 프로젝트"를 선택한 후 6개의 고급 질문에 답하세요. Claude가 기존 구성을 감지하여 새로운 섹션을 병합합니다.

> **팁:** `claude-code-setup` 플러그인은 감지된 스택에 맞는 추가 자동화(MCP 서버, hooks, skills)를 추천할 수 있습니다. 공식 마켓플레이스에서 설치하면 설정 후 제안을 받을 수 있습니다.

## 다음 단계

- [CLAUDE.md 가이드](claude-md-guide.md) -- 효과적인 CLAUDE.md 작성법 심화
- [Rules 가이드](rules-guide.md) -- 지침을 모듈화된 rule 파일로 구성하기
- [Settings 가이드](settings-guide.md) -- settings.json의 모든 설정 옵션
- [디렉토리 구조 가이드](directory-structure-guide.md) -- .claude/ 생태계 이해하기
- [효과적인 사용 가이드](effective-usage-guide.md) -- 첫날부터 적용할 사용 패턴과 피해야 할 안티패턴
- [고급 기능 가이드](advanced-features-guide.md) -- 팀을 위한 hooks, agents, skills
- [MCP 연동 가이드](mcp-guide.md) -- Claude를 외부 도구 및 서비스에 연결
- [추천 플러그인 가이드](recommended-plugins-guide.md) -- Claude Code를 확장하는 엄선된 플러그인
