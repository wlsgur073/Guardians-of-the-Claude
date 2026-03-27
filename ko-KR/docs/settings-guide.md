---
title: "settings.json 설정하기"
description: "settings 파일을 사용하여 Claude Code 동작을 설정하는 방법"
date: 2026-03-18
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

**Project** (`.claude/settings.json`) -- 프로젝트의 모든 팀원이 사용하는 공유 설정입니다. 공통 명령어에 대한 권한, 공유 deny 규칙 등을 포함합니다. 이 파일은 커밋하세요.

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

## Project Settings에 넣으면 안 되는 것

일부 설정은 보안상의 이유로 `.claude/settings.json`에서 제한됩니다. 예를 들어, `autoMemoryDirectory`는 공유 저장소가 개발자 머신의 민감한 위치로 메모리 쓰기를 리다이렉트할 수 있기 때문에 project settings에서 설정할 수 없습니다.

제한된 옵션을 project settings에 설정하려고 하면 Claude Code가 이를 무시합니다. 이러한 옵션에는 user 수준 또는 local settings를 사용하세요.

## 추가 자료

- [시작하기](getting-started.md) -- 권한을 포함한 전체 설정 안내
- [디렉터리 구조 가이드](directory-structure-guide.md) -- .claude/ 생태계에서 settings 파일의 위치
- [Rules 가이드](rules-guide.md) -- settings와 별도인 모듈식 지시사항 파일
