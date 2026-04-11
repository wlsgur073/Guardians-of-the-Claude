<p align="center">
  <img src="../../../assets/banner-v2.svg" alt="Guardians of the Claude" width="700"/>
</p>

Claude Code 설정을 위한 메타 시스템. 2분 빠른 시작부터 시작해서, 프로젝트가 성장하면 감사, 보안 강화, 최적화 워크플로우로 자연스럽게 확장됩니다. 하나의 도구, 점진적으로 깊어지는 경험.

**입문자용:** 2분 빠른 시작 — Claude가 몇 가지 질문을 묻고 모든 설정 파일을 자동으로 생성합니다.

**파워 유저용:** 4개 체인 스킬 (`/create` → `/audit` → `/secure`/`/optimize`) — 스킬 간 메모리, 프로파일 드리프트 탐지, 결정 저널로 뒷받침됩니다.

<p align="center">
  <a href="../../../README.md">English</a> | <b>한국어</b> | <a href="../ja-JP/README.md">日本語</a>
</p>

## 철학

1. **신뢰보다 검증** — 테스트, 린트, 빌드 명령어를 포함해서 Claude가 스스로 작업을 검증하게 하세요. 가장 효과적인 설정입니다.
2. **짧을수록 좋다** — 짧은 지시사항일수록 Claude가 더 잘 따릅니다. 각 가이드는 한 번에 읽을 수 있는 분량을 유지합니다.
3. **구체적으로** — "잘 작동하는지 확인"이 아니라 `npm test`. 모든 명령어는 복사해서 바로 실행할 수 있어야 합니다.
4. **점진적 심화** — Day 1은 2분 설정. Day 30은 감사와 보안 강화 추가. Day 100은 스킬 간 메모리와 자동 드리프트 탐지가 해제됩니다. 도구가 사용자와 함께 성장하며, 필요하지 않은 복잡성에 대한 비용은 내지 않습니다.

## Day 1 — 2분 빠른 시작

> **필수 조건:** Claude Code 설치 (`claude --version`으로 확인).
> **Windows**에서는 **Git Bash** 또는 **WSL**을 사용하세요 — 플러그인 SessionStart 훅과 고급 템플릿이 bash에서 실행됩니다. Bash 호환 쉘이 없으면 훅이 조용히 종료되어 자동 안내 기능(설치 감지, 드리프트 감지, 재감사 안내)을 잃습니다.

1. **마켓플레이스를 추가하고 플러그인을 설치**합니다:

   ```text
   claude
   > /plugin marketplace add wlsgur073/Guardians-of-the-Claude
   > /plugin install guardians-of-the-claude
   ```

2. **프로젝트에서 설정 커맨드를 실행**하세요:

   ```text
   cd your-project
   claude
   > /guardians-of-the-claude:create
   ```

   **대체 방법** (플러그인 설치 없이):

   | 방법 | 명령어 |
   | ---- | ------ |
   | 로컬 플러그인 | `claude --plugin-dir /path/to/Guardians-of-the-Claude/plugin` |
   | `@` import | `@../Guardians-of-the-Claude/plugin/skills/create/SKILL.md` |
   | 직접 붙여넣기 | `plugin/skills/create/SKILL.md`의 내용을 복사하여 대화에 직접 붙여넣기 |

3. **경로를 선택**하세요 — Claude가 새 프로젝트인지 기존 프로젝트인지 물어봅니다:

   | 경로 | 시기 | 동작 |
   | ---- | ---- | ---- |
   | **새 프로젝트** | 코드 없음 | 4개 질문 → `CLAUDE.md` (6섹션) + `.claude/settings.json` |
   | **기존 프로젝트** | 코드 있음, Claude 설정 없음 | 6개 질문 (자동 감지 기본값) → 전체 설정 (CLAUDE.md + settings + rules + 선택적 hooks/agents/skills) |
   | **부족한 기능 추가** | 설정이 이미 존재 | 현재 설정을 스캔하고, 설정된 항목과 누락된 항목을 보여준 뒤, 필요한 것만 추가 |

   > **이미 설정이 있나요?** Claude가 자동으로 감지하여 이미 답한 질문을 건너뛰고 부족한 기능만 추가할 수 있도록 안내합니다.
   > **잘못 선택했나요?** 걱정 마세요 — Claude가 불일치를 감지하고 자동으로 경로 전환을 제안합니다.

4. **완료** — Claude가 모든 설정 파일을 생성하고 요약 테이블을 출력합니다.
   `/memory`를 실행하여 모든 파일이 정상 로드되었는지 확인하세요.

5. **다음 단계 (선택)** — `claude-code-setup` 플러그인을 설치하면 프로젝트 스택에
   맞는 MCP 서버, hooks, skills를 추천받을 수 있습니다.

> **팁:** 프로젝트에서 먼저 `/init`을 실행하세요 — Claude가 기본 CLAUDE.md를
> 자동 생성합니다. 이후 `/guardians-of-the-claude:create`에서 "기존 프로젝트"를
> 선택하면 `/init`이 놓친 부분을 채울 수 있습니다.

**여기서 멈춰도 됩니다.** 설정은 자체적으로 동작합니다. 아래 Day 30과 Day 100+ 섹션은 더 원할 때 다음에 일어나는 일을 설명합니다.

## Day 30 — 감사, 보안 강화, 최적화

프로젝트에 실제 코드와 실제 사용 사례가 쌓이면, 3개의 스킬이 설정 건강성을 유지하는 데 도움을 줍니다:

| 스킬 | 실행 시점 | 동작 |
| ---- | -------- | ---- |
| `/guardians-of-the-claude:audit` | 프로젝트에 큰 변화가 있을 때 | 현재 Claude Code 설정을 점수화(0-100), 드리프트 식별, 다음 단계 권장 |
| `/guardians-of-the-claude:secure` | 감사가 보안 공백을 발견했을 때 | deny 패턴, 보안 규칙, 파일 보호 훅 추가 |
| `/guardians-of-the-claude:optimize` | 감사가 품질 공백을 발견했을 때 | 비대해진 CLAUDE.md를 rules/로 분리, 에이전트 다양화, MCP 권장 |

**일반적인 흐름:** `/create` → (수 주간 개발) → `/audit` → `/secure` 또는 `/optimize` → `/audit` 재검증.

## Day 100+ — 메타 시스템 활성화

여러 번 스킬을 실행하면, 플러그인은 **메타 시스템 레이어**를 활성화합니다 — 시간이 지남에 따라 프로젝트에 적응하는 지속적 학습:

- **프로젝트 프로파일** — 자동 탐지된 기술 스택, 구조, 설정 상태 (`project-profile.md`)
- **결정 저널** — 모든 스킬 실행이 압축된 changelog에 추가되어 세션 간 컨텍스트가 보존됩니다 (`config-changelog.md`)
- **스킬 간 메모리** — `/optimize`는 `/secure`가 이미 한 일을 알고, `/audit`은 이전에 거절된 항목을 기억합니다
- **프로파일 드리프트 탐지** — 프로젝트가 패키지 매니저를 바꾸거나 프레임워크 메이저 버전을 업그레이드하면, 플러그인이 감지하고 권장사항을 재평가합니다
- **정체 감지** — 같은 권장사항이 3번 무시되면, 플러그인이 거절로 표시할지 묻습니다

**이 내용을 읽지 않아도 플러그인을 사용할 수 있습니다.** 자동으로 실행됩니다. 내부를 이해하고 싶다면 [learning-system.md](../../../plugin/references/learning-system.md)를 참고하세요.

## 템플릿 구조

```text
Guardians-of-the-Claude/
├── .claude-plugin/          ← 마켓플레이스 매니페스트 (플러그인 마켓플레이스)
├── plugin/                  ← 플러그인 패키지
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── hooks/
│   │   ├── hooks.json       ← SessionStart 훅
│   │   └── session-start.sh
│   ├── references/
│   │   ├── security-patterns.md  ← 공유 보안 템플릿 (/create, /secure 공용)
│   │   └── learning-system.md   ← 공유 학습 시스템 레퍼런스 (전 스킬 공용)
│   └── skills/
│       ├── create/
│       │   ├── SKILL.md     ← 생성 스킬 (/guardians-of-the-claude:create)
│       │   ├── references/  ← 생성 모범 사례
│       │   └── templates/   ← Starter & Advanced 경로 지침
│       ├── audit/
│       │   ├── SKILL.md     ← 감사 스킬 (/guardians-of-the-claude:audit)
│       │   └── references/  ← 스코어링 모델 및 산출 공식
│       ├── secure/
│       │   └── SKILL.md     ← 보안 강화 스킬 (/guardians-of-the-claude:secure)
│       └── optimize/
│           └── SKILL.md     ← 최적화 스킬 (/guardians-of-the-claude:optimize)
├── templates/starter/       ← 스타터 실전 예시 (가상 "TaskFlow" 프로젝트)
├── templates/advanced/      ← 고급 기능 실전 예시 (rules, hooks, agents, skills)
├── docs/
│   ├── guides/              ← 가이드
│   ├── i18n/ko-KR/          ← 한국어 번역 (가이드, 템플릿)
│   ├── i18n/ja-JP/          ← 일본어 README (가이드 번역 진행 중)
│   ├── plans/               ← 설계 및 계획 문서
│   └── *.md                 ← 커뮤니티 문서 및 프로젝트 로드맵
└── CHANGELOG.md             ← 버전 이력 (Keep a Changelog 형식)
```

| 디렉토리 | 용도 |
| ------------- | --------- |
| `templates/starter/` | 스타터 실전 예시 — 최소 TaskFlow 설정 |
| `templates/advanced/` | 고급 실전 예시 — rules, hooks, agents, skills |
| `docs/guides/` | 독립 가이드 — 각각 따로 읽을 수 있음 |
| `docs/i18n/ko-KR/` | 한국어 번역 (가이드, 템플릿) |
| `docs/i18n/ja-JP/` | 일본어 README (가이드 번역 진행 중) |
| `docs/plans/` | 설계 및 계획 문서 |
| `docs/*.md` | 커뮤니티 문서 및 프로젝트 [로드맵](../../ROADMAP.md) |

## Claude Code 메모리 작동 방식

Claude Code는 계층형 메모리 시스템으로 동작합니다: CLAUDE.md (사용자의 지시사항), `.claude/rules/` (모듈형 규칙 파일), 자동 메모리 (Claude가 직접 작성하는 메모), 플러그인 캐시 (플러그인이 관리하는 상태). 자세한 내용은 [디렉토리 구조 가이드](guides/directory-structure-guide.md)를 참고하세요.

> **가장 중요한 원칙:** Claude가 자기 작업을 스스로 검증할 수 있게 하세요 —
> CLAUDE.md에 테스트, 린트, 빌드 명령어를 포함하세요.
> 이것 하나만으로 결과물의 품질이 크게 달라집니다.

## 문서

시작 후, 자신의 수준에 맞는 순서를 따르세요:

| 단계 | 가이드 | 필요한 사람 |
| ---- | ----- | ---------- |
| 1 | [시작하기](guides/getting-started.md) | 모든 사용자 — 설정 안내 |
| 2 | [CLAUDE.md 가이드](guides/claude-md-guide.md) | 모든 사용자 — 효과적인 지시 작성법 |
| 3 | [설정 가이드](guides/settings-guide.md) | 모든 사용자 — 권한 및 환경설정 |
| 4 | [규칙 가이드](guides/rules-guide.md) | CLAUDE.md가 ~100줄을 초과할 때 |
| 5 | [디렉토리 구조](guides/directory-structure-guide.md) | `.claude/` 구조를 이해하고 싶을 때 |
| 6 | [효과적인 사용법](guides/effective-usage-guide.md) | Claude Code를 하루 사용한 후 |
| 7 | [고급 기능](guides/advanced-features-guide.md) | 훅, 에이전트, 스킬이 필요할 때 |
| 8 | [MCP 연동](guides/mcp-guide.md) | 외부 도구를 연결하고 싶을 때 |
| 9 | [추천 플러그인](guides/recommended-plugins-guide.md) | Claude Code를 확장하고 싶을 때 |

## 추천 플러그인

Claude Code는 공식 플러그인으로 기능을 확장할 수 있습니다 — 전체 개발 워크플로우부터 코드 인텔리전스까지. 카테고리별 전체 목록은 **[추천 플러그인 가이드](guides/recommended-plugins-guide.md)**를 참고하세요.

Claude Code에서 `/plugin`으로 탐색하거나, [플러그인 문서](https://code.claude.com/docs/en/discover-plugins)를 참고하세요.

## 상태 표시줄 (Statusline)

Claude Code 하단 상태 표시줄을 커스터마이즈하여 모델, 컨텍스트 사용량, 비용, 소요 시간, git 브랜치를 한눈에 볼 수 있습니다:

```text
[Opus 4.6 (1M context)] 📁 my-project
 🌿 feature/auth | ████████░░ 80% | $1.25 | ⏱️ 3m 42s
```

한 줄 설정:

```bash
cp ./statusline.sh ~/.claude/statusline.sh
```

Claude Code가 `~/.claude/statusline.sh`를 자동으로 감지합니다 — 추가 설정 불필요.

> **필수 조건:**
> - [jq](https://jqlang.org)가 설치되어 있어야 합니다 (`brew install jq` / `apt install jq` / `choco install jq`)
> - Bash 호환 쉘이 필요합니다. **Windows**에서는 **Git Bash** 또는 **WSL**을 사용하세요 — 플러그인 훅과 고급 템플릿이 Unix 쉘 구문(`bash`, `grep` 등)을 사용합니다

## 참여

참여요? 여기에서요? Claude한테 시키면 되는데.. (피식)
...좋아요, 사람도 환영합니다. 이슈나 PR을 열어주세요.
프로젝트 방향성과 제안은 [ROADMAP.md](../../ROADMAP.md)를 확인하고 [GitHub Discussions](https://github.com/wlsgur073/Guardians-of-the-Claude/discussions)에서 참여하세요.

## 라이선스

MIT — [LICENSE](../../../LICENSE) 참조.
