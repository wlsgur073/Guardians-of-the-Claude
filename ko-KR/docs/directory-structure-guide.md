---
title: ".claude/ 디렉토리 구조"
description: ".claude/ 생태계, 자동 메모리, 버전 관리 대상 이해하기"
date: 2026-03-18
---

# .claude/ 디렉토리 구조

Claude Code는 설정, 지침, 학습 내용을 저장하기 위해 여러 디렉토리와 파일을 사용합니다. 이 가이드에서는 전체 구조를 설명하여 각 요소의 역할과 버전 관리 대상을 파악할 수 있도록 합니다.

## .claude/ 내부 구성

```text
your-project/
├── CLAUDE.md                     # 프로젝트 지침 (루트 배치)
├── .claude/
│   ├── CLAUDE.md                 # 프로젝트 지침 (대체 배치)
│   ├── settings.json             # 팀 공유 설정 (커밋 대상)
│   ├── settings.local.json       # 개인 설정 오버라이드 (gitignore 대상)
│   ├── rules/                    # 모듈화된 지침 파일
│   │   ├── code-style.md
│   │   ├── testing.md
│   │   └── ...
│   ├── agents/                   # 에이전트 정의 (고급 기능)
│   │   └── developer.md
│   └── skills/                   # 스킬 정의 (고급 기능)
│       └── scaffold-feature/
│           └── SKILL.md
└── src/
    └── CLAUDE.md                 # 폴더별 지침 (지연 로드)
```

`.claude/` 내부의 모든 것은 Claude Code 설정입니다. 루트 `CLAUDE.md`와 폴더별 `CLAUDE.md` 파일은 프로젝트 파일과 함께 위치합니다. `agents/`와 `skills/` 디렉토리는 고급 기능입니다 -- [고급 기능 가이드](advanced-features-guide.md)를 참고하세요.

## 자동 메모리

자동 메모리는 Claude의 자체 메모 시스템입니다. Claude가 세션 중에 프로젝트에 대해 학습한 내용을 저장하여 이후 세션에서 활용합니다.

**위치:** `~/.claude/projects/<project-hash>/memory/`

이 파일은 프로젝트 디렉토리가 아닌 홈 디렉토리에 저장됩니다. 포함 내용은 다음과 같습니다:

- **MEMORY.md** -- 모든 주제별 메모리를 나열하는 인덱스 파일
- **주제 파일** -- `user_preferences.md`, `project_architecture.md` 등 개별 파일

### 200줄 기준의 차이

MEMORY.md와 CLAUDE.md 모두 "200줄"을 언급하지만 그 이유는 매우 다릅니다:

| 파일 | 제한 | 유형 | 동작 |
| ------ | ------- | ------ | ------------- |
| MEMORY.md | 200줄 | **하드 로드 경계** | 200줄을 초과하는 내용은 세션 시작 시 로드되지 않습니다. 잘려나갑니다. |
| CLAUDE.md | 200줄 | **소프트 준수 가이드라인** | 파일 길이에 관계없이 전체가 로드됩니다. 하지만 짧은 파일일수록 지침 준수율이 높아집니다. |

같은 숫자지만 메커니즘이 다릅니다. MEMORY.md는 엄격한 컷오프가 있고, CLAUDE.md는 권장 목표값입니다.

### 자동 메모리는 직접 관리할 필요 없음

자동 메모리는 저장소 외부에 존재합니다. 이 파일들을 직접 생성, 편집, gitignore 할 필요가 없습니다 -- Claude가 자동으로 관리합니다. `/memory` 명령으로 Claude가 저장한 내용을 확인할 수 있습니다.

## .gitignore 설정

| 파일 | 커밋? | 이유 |
| ------ | --------- | ----- |
| `.claude/settings.json` | 예 | 팀 공유 설정 -- 모든 구성원이 동일한 권한을 사용합니다 |
| `.claude/rules/` | 예 | 팀 공유 지침 파일 |
| `.claude/settings.local.json` | 아니오 | 개인 설정 오버라이드 -- 각 개발자가 자신만의 설정을 가집니다 |
| 자동 메모리 (`~/.claude/...`) | 해당 없음 | 저장소 외부에 존재하므로 별도 조치 불필요 |

프로젝트의 `.gitignore`에 다음을 추가하세요:

```gitignore
.claude/settings.local.json
```

`templates/.gitignore` 스캐폴드에 이 줄이 복사할 수 있도록 이미 포함되어 있습니다.

## 세 가지 시스템

Claude Code에는 세션 시작 시 모두 로드되지만 서로 다른 목적을 가진 세 가지 시스템이 있습니다:

| 시스템 | 작성자 | 목적 | 위치 |
| -------- | -------- | --------- | ---------- |
| **CLAUDE.md** | 사용자 | 사용자가 Claude에게 작성하는 지침 | 프로젝트 루트, `.claude/`, 하위 디렉토리 |
| **자동 메모리** | Claude | Claude가 스스로 저장하는 학습 내용 | `~/.claude/projects/<project>/memory/` |
| **설정** | 사용자 | 동작 설정 (권한, 토글) | `.claude/settings.json`, `.claude/settings.local.json` |

핵심 요점: **CLAUDE.md는 사용자가 Claude에게 전달하는 내용입니다. 자동 메모리는 Claude가 스스로에게 전달하는 내용입니다.** 둘 다 Claude의 동작에 영향을 주지만, 서로 다른 작성자가 서로 다른 목적으로 작성합니다.

## 추가 자료

- [CLAUDE.md 가이드](claude-md-guide.md) -- 효과적인 CLAUDE.md 파일 작성법
- [Rules 가이드](rules-guide.md) -- 지침을 모듈화된 규칙 파일로 구성하기
- [Settings 가이드](settings-guide.md) -- settings.json 옵션 설정하기
