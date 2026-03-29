---
title: "시작하기"
description: "프로젝트에 Claude Code 설정을 구성하는 단계별 가이드"
date: 2026-03-18
---

# 시작하기

이 가이드는 첫 설치부터 정상 동작 확인까지, 프로젝트에 Claude Code 설정을 구성하는 전체 과정을 안내합니다.

## 사전 준비

- Claude Code가 설치되어 있고 정상 동작하는 상태 (`claude --version`으로 확인)
- 설정을 적용할 프로젝트

## 1단계: 설정 방법 선택

| 옵션 | 하는 일 | 적합한 경우 |
| ---- | ------ | ---------- |
| `/init` | 코드 분석 후 기본 CLAUDE.md 생성 | 빠른 시작 — 대부분의 프로젝트에 적합 |
| `/claude-code-template:setup` | 대화형 인터뷰 → CLAUDE.md + 설정 + 규칙 + 선택적 기능 | 종합적인 설정 ([빠른 시작](../README.md#quick-start)) |

**`/init`**은 [공식 권장 첫 단계](https://code.claude.com/docs/en/best-practices)입니다 -- Claude가 코드베이스를 분석하고 CLAUDE.md를 자동 생성합니다:

```text
claude
> /init
```

**`/claude-code-template:setup`**은 `/init` 스타일 분석에 더해 규칙, 권한, 선택적 고급 기능을 한 번에 생성합니다. 먼저 플러그인을 설치하세요 (`/plugin marketplace add wlsgur073/Claude-Code-Template` 후 `/plugin install claude-code-template@wlsgur073-claude-code-template`). **둘 다 사용?** `/init`을 먼저 실행한 후, `/claude-code-template:setup`에서 "기존 프로젝트"를 선택하세요 — 기존 CLAUDE.md를 감지하여 덮어쓰지 않고 병합합니다.

## Step 2: 템플릿 복사 (수동 대안)

1단계에서 `/claude-code-template:setup`을 사용했다면 이 단계를 건너뛰세요 — 파일이 이미 생성되었습니다. 설정 커맨드의 스타터 경로는 `starter/` 템플릿 구조와, 고급 경로는 `advanced/` 구조와 동일한 결과를 생성합니다.

수동으로 템플릿을 복사하려면, 시작점을 선택하세요:

**Starter** (입문자 추천):

```bash
# 미니멀 CLAUDE.md 스캐폴드 복사 (5섹션)
cp Claude-Code-Template/starter/CLAUDE.md your-project/CLAUDE.md

# settings 스캐폴드 복사
mkdir -p your-project/.claude
cp Claude-Code-Template/starter/.claude/settings.json your-project/.claude/settings.json
```

**Advanced** (전체 설정):

```bash
# 전체 CLAUDE.md 스캐폴드 복사 (8섹션)
cp Claude-Code-Template/advanced/CLAUDE.md your-project/CLAUDE.md

# settings, rules, 고급 기능 복사
cp -r Claude-Code-Template/advanced/.claude your-project/.claude
```

`/init`으로 이미 CLAUDE.md를 생성했다면, 템플릿의 섹션을 기존 파일에 병합하세요. 템플릿은 일관된 섹션 구조를 제공하고, `/init`은 프로젝트에 특화된 내용을 제공합니다. 양쪽의 장점을 결합하세요.

## Step 3: CLAUDE.md 작성

CLAUDE.md를 열고 각 섹션을 채워 나가세요. 스캐폴드의 HTML 주석이 무엇을 작성해야 하는지 안내합니다:

1. **Project Overview** -- 한두 문장으로: 이 프로젝트가 무엇을 하는지, 어떤 언어/프레임워크를 사용하는지.
2. **Build & Run** -- 프로젝트를 빌드하고 실행하는 정확한 명령어.
3. **Testing** -- 테스트 실행 방법. Claude가 자신의 작업을 검증할 수 있는 확인 명령어를 포함하세요.
4. **Code Style & Conventions** -- 언어 기본값과 다른 규칙만 작성하세요. 구체적으로 작성하세요.
5. **Workflow** -- 브랜치 네이밍, 커밋 컨벤션, 개발 전 체크리스트.
6. **Project Structure** -- 주요 디렉토리와 각각의 용도.
7. **Important Context** -- 명확하지 않은 것들: 필수 서비스, 인증 패턴, 환경 관련 특이사항.
8. **References** -- `@import` 구문으로 상세 문서 링크.

무엇을 포함하고 무엇을 제외할지에 대한 자세한 가이드는 [CLAUDE.md 가이드의 포함/제외 표](claude-md-guide.md#what-to-include-vs-exclude)를 참고하세요.

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

**스타터에서 고급으로 업그레이드:** `/claude-code-template:setup`을 다시 실행하고, 첫 번째 질문에서 "기존 프로젝트"를 선택한 후 6개의 고급 질문에 답하세요. Claude가 기존 구성을 감지하여 새로운 섹션을 병합합니다.

## 다음 단계

- [CLAUDE.md 가이드](claude-md-guide.md) -- 효과적인 CLAUDE.md 작성법 심화
- [Rules 가이드](rules-guide.md) -- 지침을 모듈화된 rule 파일로 구성하기
- [Settings 가이드](settings-guide.md) -- settings.json의 모든 설정 옵션
- [디렉토리 구조 가이드](directory-structure-guide.md) -- .claude/ 생태계 이해하기
- [효과적인 사용 가이드](effective-usage-guide.md) -- 첫날부터 적용할 사용 패턴과 피해야 할 안티패턴
- [고급 기능 가이드](advanced-features-guide.md) -- 팀을 위한 hooks, agents, skills
