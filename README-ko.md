# Claude Code Templates

Claude Code 설정을 위한 스타터 템플릿과 가이드. 이 리포지토리를 클론하고, 템플릿을 프로젝트에 복사한 뒤, 예시를 참고하여 내용을 채우세요.

**대상:** 첫날부터 바로 쓸 수 있는 설정을 원하는 Claude Code 입문 개발자.

## 빠른 시작

### 방법 A: 자동 설정 (권장)

1. **프로젝트 옆에 이 템플릿을 클론**합니다:

   ```bash
   git clone https://github.com/wlsgur073/Claude-Code-Templates.git
   # 결과: your-project/ 와 Claude-Code-Templates/ 가 같은 레벨에 위치
   ```

2. **프로젝트에서 Claude를 실행**하고 `@`로 설정 프롬프트를 참조하세요:

   ```
   cd your-project
   claude
   > @../Claude-Code-Templates/setup-prompt-ko.md
   ```

   > `@`는 파일 내용을 대화에 가져오는 구문입니다 — Claude가 설정 지시를
   > 읽고 자동으로 따릅니다.

3. **몇 가지 질문에 답변**하세요 — Claude가 프로젝트를 분석한 뒤, 언어/프레임워크,
   테스트 설정, 코드 스타일, 워크플로우 등을 물어봅니다.

4. **완료** — Claude가 모든 설정 파일을 생성합니다:

   | 생성 파일 | 용도 |
   | -------------- | ------- |
   | `CLAUDE.md` | 프로젝트 개요, 명령어, 스타일, 워크플로우 |
   | `.claude/settings.json` | 권한 (allow/deny) 및 선택적 hooks |
   | `.claude/rules/*.md` | 코드 스타일, 테스트, 아키텍처, 워크플로우 규칙 |
   | `.gitignore` 항목 | `.claude/settings.local.json` 제외 |

   선택적으로 자동 린트 훅, 파일 보호, 에이전트 역할,
   스킬 명령어도 설정할 수 있습니다.

### 방법 B: 수동 설정

1. **git clone**

   ```bash
   git clone https://github.com/wlsgur073/Claude-Code-Templates.git
   ```

2. **템플릿을 프로젝트에 복사**

   ```bash
   cp Claude-Code-Templates/templates-ko/CLAUDE.md your-project/CLAUDE.md
   mkdir -p your-project/.claude
   cp Claude-Code-Templates/templates-ko/.claude/settings.json your-project/.claude/settings.json
   ```

3. `examples/`를 참고하여 **템플릿 내용 채우기**

> **팁:** 프로젝트에서 먼저 `/init`을 실행하세요 — Claude가 기본 CLAUDE.md를
> 자동 생성합니다. 이후 이 템플릿을 병합하면 `/init`이 놓친 부분을 채울 수 있습니다.

## 템플릿 구조

```text
Claude-Code-Templates/
├── setup-prompt.md        ← 자동 설정 프롬프트 (영어)
├── setup-prompt-ko.md     ← 자동 설정 프롬프트 (한국어, 방법 A용)
├── templates/             ← 프로젝트에 복사할 빈 템플릿
├── templates/advanced/    ← 고급 기능 템플릿 (hooks, agents, skills)
├── templates-ko/          ← 템플릿의 한국어 번역
├── templates-ko/advanced/ ← 고급 템플릿의 한국어 번역
├── examples/              ← 실전 예시 (가상 "TaskFlow" 프로젝트)
├── examples/advanced/     ← 고급 기능 실전 예시
└── docs/                  ← 각 개념을 설명하는 가이드
```

| 디렉토리 | 용도 |
| ------------- | --------- |
| `templates/` | HTML 주석 안내가 포함된 빈 템플릿 — 복사 후 내용 채우기 |
| `templates-ko/` | 동일한 템플릿의 한국어 번역 |
| `examples/` | 실전 예시 — 편집 시 참고용 |
| `docs/` | 독립 가이드 — 각각 따로 읽을 수 있음 |

## Claude Code 메모리 작동 방식

Claude Code는 계층형 메모리 시스템으로 동작합니다:

- **CLAUDE.md** — *사용자가* 작성하는 지시사항. 매 세션마다 로드됨.
  위치: 프로젝트 루트, `.claude/`, 사용자 홈, managed policy.
- **`.claude/rules/`** — 모듈형 지시 파일. 특정 파일 경로에 범위를 제한할 수 있음.
  매 세션 또는 파일 접근 시 로드됨.
- **Auto memory** — 작업 중 *Claude가 직접* 작성하는 메모.
  `~/.claude/projects/<project>/memory/`에 저장. MEMORY.md의 처음 200줄이
  매 세션마다 로드됨.

> **가장 중요한 원칙:** Claude가 자기 작업을 스스로 검증할 수 있게 하세요 —
> CLAUDE.md에 테스트, 린트, 빌드 명령어를 포함하세요.
> 이것 하나만으로 결과물의 품질이 크게 달라집니다.

## 문서

| 가이드 | 다루는 내용 |
| ------- | --------------- |
| [Getting Started](docs/getting-started.md) | 단계별 설정 안내 |
| [CLAUDE.md Guide](docs/claude-md-guide.md) | 효과적인 CLAUDE.md 작성법 |
| [Rules Guide](docs/rules-guide.md) | .claude/rules/ 사용법과 경로 스코핑 |
| [Settings Guide](docs/settings-guide.md) | settings.json 설정 |
| [Directory Structure](docs/directory-structure-guide.md) | .claude/ 생태계 |
| [Effective Usage](docs/effective-usage-guide.md) | 첫날부터 쓰는 사용 패턴 |
| [Advanced Features](docs/advanced-features-guide.md) | Hooks, agents, skills |

## 추천 플러그인

Claude Code는 기능을 확장하는 공식 플러그인을 지원합니다.
Claude Code에서 `/install-plugin`으로 설치하거나, [플러그인 문서](https://docs.anthropic.com/en/docs/claude-code/plugins)를 참고하세요.

### 개발 워크플로우 추천

| 플러그인 | 설명 |
| ------ | ------------ |
| [superpowers](https://github.com/obra/superpowers) | 전체 개발 워크플로우 — 스펙 → 설계 → 계획 → 서브에이전트 기반 구현. Claude가 계획에서 벗어나지 않고 자율 작업 |
| [feature-dev](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/feature-dev) | 구조화된 7단계 기능 개발: 코드베이스 탐색 → 질문 → 설계 → 구현 → 리뷰 |
| [code-review](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-review) | 멀티 에이전트 PR 리뷰. 신뢰도 기반 스코어링으로 오탐 필터링 |
| [code-simplifier](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-simplifier) | 최근 수정된 코드를 명확하고 일관되게 리팩터링. 기존 동작은 그대로 유지 |

### 코드 인텔리전스 & 품질

| 플러그인 | 설명 |
| ------ | ------------ |
| [typescript-lsp](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/typescript-lsp) | TypeScript/JS 언어 서버 — 정의로 이동, 참조 찾기, 에러 체크를 Claude 안에서 바로 |
| [security-guidance](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/security-guidance) | 코드 작성 전 보안 취약점(XSS, 인젝션 등)을 경고하는 Pre-edit 훅 |
| [context7](https://github.com/upstash/context7) | 최신 라이브러리 문서를 즉시 가져오는 MCP 서버. API 할루시네이션 방지 |

### UI & 브라우저

| 플러그인 | 설명 |
| ------ | ------------ |
| [frontend-design](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/frontend-design) | "AI가 만든 것 같지 않은" 독특하고 프로덕션 수준의 UI 생성 |
| [chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) | 실시간 Chrome 브라우저 제어 및 검사 — 디버깅, 자동화, 성능 분석 |
| [figma](https://github.com/figma/mcp-server-guide) | Figma 디자인 파일에서 컨텍스트를 직접 가져와 구현에 활용 |

### 프로젝트 셋업

| 플러그인 | 설명 |
| ------ | ------------ |
| [claude-code-setup](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-code-setup) | 코드베이스를 스캔하고 프로젝트에 최적화된 hooks, skills, MCP 서버, 서브에이전트를 추천 |
| [claude-md-management](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-md-management) | CLAUDE.md 품질 감사 + `/revise-claude-md`로 세션 학습 내용 반영 |

## 상태 표시줄 (Statusline)

Claude Code 하단 상태 표시줄을 커스터마이즈하여 모델, 컨텍스트 사용량, 비용, 소요 시간, git 브랜치를 한눈에 볼 수 있습니다:

```
[Opus 4.6 (1M context)] 📁 my-project
 🌿 feature/auth | ████████░░ 80% | $1.25 | ⏱️ 3m 42s
```

**한 줄 설정:**

```bash
cp Claude-Code-Templates/templates/statusline.sh ~/.claude/statusline.sh
```

Claude Code가 `~/.claude/statusline.sh`를 자동으로 감지합니다 — 추가 설정 불필요.

> **필수 조건:** [jq](https://jqlang.org)가 설치되어 있어야 합니다 (`brew install jq` / `apt install jq` / `choco install jq`).

## 참여

참여요? 여기에서요? Claude한테 시키면 되는데.. (피식)
...좋아요, 사람도 환영합니다. 이슈나 PR을 열어주세요.

## 라이선스

MIT — [LICENSE](LICENSE) 참조.
