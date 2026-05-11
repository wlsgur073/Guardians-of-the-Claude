---
title: "settings.json 설정하기"
description: "settings 파일을 사용하여 Claude Code 동작을 설정하는 방법"
version: 1.1.1
---

# settings.json 설정하기

Settings 파일은 Claude Code의 동작을 제어합니다 -- 권한, 토글, 기능 설정 등을 포함합니다. CLAUDE.md가 지시사항을 제공하는 것과 달리, settings는 Claude가 수행할 수 있는 작업과 작동 방식을 설정합니다.

## Settings 파일 위치

Claude Code는 가장 넓은 범위부터 가장 구체적인 범위까지, 네 곳에서 settings를 읽습니다:

| 범위 | 위치 | Git에 커밋? | 목적 |
| ------- | ---------- | -------------------- | --------- |
| Managed policy | 플랫폼별 시스템 경로 | 해당 없음 | 관리자가 설정하는 조직 전체 정책 |
| User | `~/.claude/settings.json` | 아니요 | 모든 프로젝트에 적용되는 개인 설정 |
| Project | `.claude/settings.json` | 예 | 팀이 공유하는 프로젝트 설정 |
| Local | `.claude/settings.local.json` | 아니요 | 이 프로젝트에 대한 개인 오버라이드 |

동일한 설정이 여러 수준에 존재할 경우, 더 구체적인 범위가 넓은 범위를 오버라이드합니다. 모든 수준의 설정이 병합되므로 변경하려는 설정만 지정하면 됩니다.

## 어디에 무엇을 설정할 것인가

**Project** (`.claude/settings.json`) -- 프로젝트의 모든 팀원이 사용하는 공유 설정입니다. 공통 명령어에 대한 권한, 공유 deny 규칙 등을 포함합니다. 이 파일은 커밋하세요. (플러그인 **소스** 저장소는 자체 `.claude/*`를 개발 전용으로 gitignore할 수 있습니다 — 이 커밋 안내는 본 가이드를 따르는 **사용자** 프로젝트에 적용됩니다.)

**Local** (`.claude/settings.local.json`) -- 팀원에게 영향을 주지 않아야 하는 개인 오버라이드입니다. `.gitignore`에 추가하세요.

**User** (`~/.claude/settings.json`) -- 모든 프로젝트에 걸쳐 적용되는 설정입니다. 초보자에게는 거의 필요하지 않습니다.

## $schema 필드

`$schema` 필드를 추가하면 에디터에서 자동완성과 유효성 검사를 사용할 수 있습니다:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [],
    "deny": []
  }
}
```

입력하는 동안 에디터가 유효한 키를 제안하고 오류를 표시합니다.

## 초보자를 위한 주요 옵션

### permissions.allow와 permissions.deny

`Tool(specifier)` 구문을 사용하여 특정 도구 동작을 사전 승인하거나 차단합니다:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm test)",
      "Bash(npm run lint)",
      "Bash(npm run build)",
      "Bash(git diff *)",
      "Bash(git log *)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)"
    ]
  }
}
```

`allow` 목록은 신뢰할 수 있는 명령어에 대한 권한 프롬프트를 제거합니다. `deny` 목록은 Claude가 절대 수행하지 않기를 원하는 동작을 차단합니다. 테스트와 빌드 명령어부터 시작하세요 -- 가장 안전하고 가장 자주 사용되는 명령어입니다.

주요 도구 이름: `Bash(command)`, `Read(path)`, `Edit(path)`, `Write(path)`.

전체 permission 규칙 구문은 [공식 permissions 문서](https://code.claude.com/docs/en/permissions#permission-rule-syntax)를 참고하세요.

### autoMemoryEnabled

Claude가 프로젝트에 대한 학습 내용을 메모리 시스템에 자동으로 저장하는지 여부를 제어합니다. 기본값은 활성화 상태입니다.

```json
{
  "autoMemoryEnabled": false
}
```

자세한 내용은 [auto memory 문서](https://code.claude.com/docs/en/memory#enable-or-disable-auto-memory)를 참고하세요.

### claudeMdExcludes

경로 또는 glob 패턴으로 특정 CLAUDE.md 파일을 건너뜁니다. 모노레포에서 작업과 관련 없는 CLAUDE.md 파일이 있을 때 유용합니다:

```json
{
  "claudeMdExcludes": [
    "packages/legacy-app/CLAUDE.md",
    "vendor/**/CLAUDE.md"
  ]
}
```

자세한 내용은 [memory 문서](https://code.claude.com/docs/en/memory#exclude-specific-claudemd-files)를 참고하세요.

### hooks, env, enabledPlugins (고급)

`hooks` 키는 도구 사용 전후에 셸 명령어를 실행합니다 (예: 자동 린팅). `env` 키는 Claude의 명령어에 환경 변수를 설정합니다. `enabledPlugins` 키는 공식 플러그인을 나열합니다. 자세한 내용과 예제는 [고급 기능 가이드](advanced-features-guide.md)를 참고하세요.

## Permission Modes 및 안전 옵션 (고급)

Claude Code는 6가지 permission mode(프롬프트 빈도)와 Bash 서브프로세스용 OS 수준 sandbox(피해 범위)를 제공합니다. 두 축은 독립적입니다 — 작업 성격에 따라 각각 선택하세요. 둘 중 하나만 고르는 것이 아닙니다.

### permissions.defaultMode

새 세션의 기본 mode를 설정합니다: `default` (읽기만), `acceptEdits` (파일 편집 + 일반 파일시스템 명령 자동 승인), `plan` (편집 없이 read-only 조사), `auto` (classifier 기반 자율), `dontAsk` (사전 승인된 도구만), `bypassPermissions` (검사 없음; 격리 환경 전용).

```json
{ "permissions": { "defaultMode": "acceptEdits" } }
```

Auto mode 이용 조건: Anthropic API 사용 + Max / Team / Enterprise / API plan (Pro 제외; Bedrock / Vertex / Foundry 제외) + Claude Sonnet 4.6, Opus 4.6, Opus 4.7 중 한 모델 (Max plan은 Opus 4.7 한정) + Team / Enterprise는 admin 활성화 필요. CLI에서 `Shift+Tab`으로 mode 순환. 전체 요건과 protected paths 목록은 [permission modes 문서](https://code.claude.com/docs/en/permission-modes)를 참고하세요.

### autoMode

`defaultMode`가 `auto`일 때, classifier가 사용자가 선언한 신뢰 인프라 기준으로 각 동작을 평가합니다. `autoMode.environment` (그리고 선택적으로 `allow`, `soft_deny`, `hard_deny`)로 설정합니다. 주의: classifier는 `autoMode`를 user (`~/.claude/settings.json`), local (`.claude/settings.local.json`), managed scope에서만 읽습니다 — 공유 `.claude/settings.json`의 `autoMode`는 의도적으로 무시되어, 체크인된 저장소가 자체 allow rule을 주입하지 못하도록 설계됩니다.

```json
{
  "autoMode": {
    "environment": [
      "$defaults",
      "Source control: github.com/your-org"
    ]
  }
}
```

리터럴 문자열 `"$defaults"`는 빌트인 규칙을 보존하며, 사용자 항목은 신뢰를 추가로 확장합니다. Anthropic 보고에 따르면 실제 내부 트래픽 (n=10,000 정상 도구 호출)에서 false-positive 비율 0.4%, 실제 over-eager 동작 (n=52)에서 false-negative 비율 17% — 모두 Stage 1 + Stage 2 full-pipeline 수치이며 Anthropic 내부 측정값입니다. 사용자 환경 일반화 보장 아님. [auto mode 설정 reference](https://code.claude.com/docs/en/auto-mode-config)와 `claude auto-mode defaults` / `claude auto-mode config` / `claude auto-mode critique` CLI 서브커맨드를 참고하세요.

### sandbox

Bash 서브프로세스를 OS 수준에서 격리합니다 (macOS는 Seatbelt, Linux/WSL2는 bubblewrap; WSL1 미지원). Permission mode와 독립적입니다. `/sandbox` 명령어 또는 settings로 활성화:

```json
{
  "sandbox": {
    "enabled": true,
    "filesystem": { "allowWrite": ["~/.npm", "/tmp/jest"] }
  }
}
```

Linux/WSL2는 `bubblewrap`과 `socat` 패키지가 필요합니다. Anthropic 보고에 따르면 sandbox 활성화 시 권한 프롬프트가 84% 감소 — Anthropic 내부 사용 측정값이며, 임의 환경에서의 보장은 아닙니다. 효과적인 sandboxing은 파일시스템과 네트워크 격리 *모두*가 필요합니다. `denyWrite`/`denyRead`, custom proxy, 보안 한계는 [sandboxing 문서](https://code.claude.com/docs/en/sandboxing)를 참고하세요.

## Project Settings에 넣으면 안 되는 것

일부 설정은 보안상의 이유로 `.claude/settings.json`에서 제한됩니다. 예를 들어, `autoMemoryDirectory`는 공유 저장소가 개발자 머신의 민감한 위치로 메모리 쓰기를 리다이렉트할 수 있기 때문에 project settings에서 설정할 수 없습니다.

제한된 옵션을 project settings에 설정하려고 하면 Claude Code가 이를 무시합니다. 이러한 옵션에는 user 수준 또는 local settings를 사용하세요.

## 추가 자료

- [시작하기](getting-started.md) -- 권한을 포함한 전체 설정 안내
- [디렉터리 구조 가이드](directory-structure-guide.md) -- .claude/ 생태계에서 settings 파일의 위치
- [Rules 가이드](rules-guide.md) -- settings와 별도인 모듈식 지시사항 파일
