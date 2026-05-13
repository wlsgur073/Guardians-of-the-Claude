---
title: "신뢰할 수 있는 에이전트"
description: "Claude Code 에이전트 구성을 평가하기 위한 다섯 가지 원칙과 네 가지 계층 프레임워크"
version: 1.0.0
---

# 신뢰할 수 있는 에이전트

이 가이드는 Anthropic의 "Trustworthy Agents in Practice" 프레임워크 — 네 가지 아키텍처 계층에 걸친 다섯 가지 원칙 — 을 Claude Code의 구체적인 구성 표면에 매핑합니다. 프로젝트 구성이 의도한 보장을 제공하는지 평가하는 데 사용하세요.

## 출처와 범위

다섯 가지 원칙(인간의 통제, 가치 정렬, 보안, 투명성, 프라이버시)과 네 가지 아키텍처 계층(모델, 하네스, 도구, 환경)은 Anthropic Research의 [Trustworthy Agents in Practice](https://www.anthropic.com/research/trustworthy-agents) (2026년 4월)에서 가져왔습니다. 이 가이드는 *번역 작업*을 수행합니다: 해당 프레임워크를 이 저장소의 구체적인 Claude Code 표면 — CLAUDE.md, settings.json, 훅, 스킬, MCP, deny 패턴 — 에 적용합니다.

이는 [`plugin/references/security-patterns.md`](../../../../plugin/references/security-patterns.md)의 *위협 시나리오 관점*("어떤 공격으로부터 방어하고 있는가?")을 보완합니다. 이 가이드는 다른 질문에 답합니다: "어떤 보장을 제공하고 있으며, 어느 계층에서 제공하는가?"

## 다섯 가지 원칙

### 인간의 통제

에이전트는 인간의 권한 아래 행동하며, 인간은 작업을 검사하고 무효화하거나 중단할 수 있는 능력을 유지합니다. Claude Code의 관점에서:

- **Plan Mode**로 전략 수준 감독 (아래 [§ Plan Mode as Strategy-Level Oversight](#plan-mode-as-strategy-level-oversight) 참조)
- 항상 확인을 위해 일시 중지해야 하는 도구에 대한 `permissions.ask:[]`
- 위험한 작업(예: `git push --delete`, `rm -rf`)에 대한 강제 중단을 위한 `PreToolUse` 훅 + `exit 2`
- 모호한 식별자에 대한 파괴적 작업에 대한 CLAUDE.md 모호성 해소 규칙

### 가치 정렬

에이전트는 *당신의* 목표를 추구합니다 — 문자 그대로의 요청만이 아니라 근본적인 *이유*까지 포함합니다. Anthropic의 [Teaching Claude why](https://www.anthropic.com/research/teaching-claude-why) (2026년 5월)는 원칙으로 Claude를 훈련시키는 것이 시연만으로 훈련시키는 것보다 더 잘 일반화된다는 사실을 발견했습니다. 동일한 논리가 CLAUDE.md에도 적용됩니다:

- 규칙과 함께 근거를 작성하세요 ("저장소 클래스를 사용합니다 — 핸들러에서 DB로 직접 접근하는 단축 경로가 프로덕션 데이터 유출을 일으킨 적이 있기 때문" — 단순히 "저장소 클래스를 사용하세요"만이 아니라)
- 표준 6개 섹션 구조는 [CLAUDE.md 가이드](claude-md-guide.md)를 참조하세요
- 여러 유효한 접근 방식이 존재하는 질문에 대해 기본값을 선택하기보다 인간의 판단에 맡기는 스킬 설계

### 보안

에이전트는 자격 증명 노출, 유출, 범위 확대 또는 안전 우회를 가능하게 해서는 안 됩니다. 명명된 사고 유형이 포함된 전체 위협 카탈로그는 [`plugin/references/security-patterns.md`](../../../../plugin/references/security-patterns.md)에 있습니다. 구성 표면:

- 비밀 파일(`.env`, `*.pem`, `*.key`, `secrets/`)에 대한 `permissions.deny:[]`
- 프로젝트별 보장(인증, 검증, 비밀 처리)을 위한 `.claude/rules/security.md`
- `$CLAUDE_FILE_PATH` 매칭으로 민감한 파일을 보호하는 `PreToolUse` 훅
- 이러한 항목을 자동으로 적용하려면 `/guardians-of-the-claude:secure`를 실행하세요

### 투명성

에이전트의 행동과 추론은 검사 가능합니다. 구성 표면:

- 훅 정의의 `statusMessage`는 훅이 수행 중인 작업을 UI에 표시합니다
- `.claude/.plugin-cache/<plugin>/local/config-changelog.md`는 스킬이 발행한 구성 변경 사항을 기록합니다
- `recommendations.json`은 세션 전반에 걸쳐 발행된/해결된/거부된 권장 사항을 추적합니다
- 서브에이전트 디스패치는 표시 가능한 스레드를 생성해야 합니다 ([§ 서브에이전트 관측성](#서브에이전트-관측성) 참조)

### 프라이버시

민감한 데이터는 사용자 동의 없이 에이전트의 컨텍스트, 출력 또는 외부 시스템으로 누출되지 않습니다. 구성 표면:

- MCP `.mcp.json` env 값은 리터럴 자격 증명이 아닌 `${ENV_VAR}` 플레이스홀더를 사용합니다
- `permissions.deny:[]`의 `Read(./.env)` 및 이에 준하는 항목
- `.claude/rules/security.md`의 비밀 처리 규칙
- 공유 CLAUDE.md 파일의 경우: 인라인 자격 증명, 호스트명 또는 내부 URL 없음

## 네 가지 아키텍처 계층

심층 방어: 잘 훈련된 모델만으로는 충분하지 않습니다 — 하네스, 도구, 환경이 협력해야 합니다.

### 모델 계층

대부분의 프로젝트 구성에서는 범위 밖입니다 — 평판이 좋은 모델 제공자와 버전을 선택합니다. *제어할 수 있는 것*: 에이전트별 모델 선택(`.claude/agents/<name>.md`), YAML 주석에 근거를 문서화합니다. [고급 기능 가이드 § 에이전트](advanced-features-guide.md#agents)를 참조하세요.

### 하네스 계층

에이전트의 작동 방식을 형성하는 지침, 규칙, 런타임 게이트. 대부분의 프로젝트 구성이 여기에 있습니다:

- `CLAUDE.md` — 모든 세션에서 로드되는 프로젝트 지침
- `.claude/rules/*.md` — 경로 범위가 지정된 모듈형 지침
- `.claude/settings.json` — 권한, 훅, 환경
- `settings.json`의 인라인 훅 또는 `.claude/hooks/`의 외부 스크립트

하네스만으로는 불충분합니다: 완벽한 CLAUDE.md도 `permissions.deny:[]`가 비어 있으면 여전히 자격 증명을 유출할 수 있습니다.

### 도구 계층

에이전트가 호출할 수 있는 것과 어떤 제한이 있는지:

- `permissions.allow / ask / deny`로 제어되는 내장 도구
- 스킬(`.claude/skills/<name>/SKILL.md`) — [고급 기능 § 스킬](advanced-features-guide.md#skills) 참조
- MCP 서버 — [MCP 가이드](mcp-guide.md) 참조
- 도구별 세분성("일정 항상 읽기; 초대장 보내기는 승인 필요")

도구만으로는 불충분합니다: 하네스 규칙이 사용을 안내하지 않으면 좁은 허용도 오용될 수 있습니다.

### 환경 계층

에이전트 행동 주변의 OS 수준 경계:

- 파일 시스템 범위(작업 디렉터리, deny 규칙의 경로 패턴)
- 네트워크 송신(`autoMode.environment` 신뢰 경계; 신뢰할 수 없는 호스트에 대한 `Bash(curl * https://*:*)` deny 패턴)
- 샌드박스(`sandbox.enabled` — Linux의 bubblewrap, macOS 네이티브, WSL2)
- [`security-patterns.md` § 권한 및 안전 결정 원칙](../../../../plugin/references/security-patterns.md#permission-and-safety-decision-principles) 참조

환경만으로는 불충분합니다: 샌드박스는 그 안에서 에이전트가 잘못된 결정을 내리는 것을 막지 않습니다.

## 계층별 자체 점검

진단 체크리스트입니다 — 점수 루브릭이 아닙니다(그것은 `/guardians-of-the-claude:audit`이 하는 일입니다). 현재 구성을 검토하고 답해 보세요:

**하네스 계층:**

- CLAUDE.md는 규칙이 *왜* 존재하는지를 설명합니까, 아니면 *무엇인지*만 설명합니까?
- `settings.json`은 `Bash(*)`와 같은 와일드카드 대신 세분화된 `allow:` / `ask:` 항목을 사용합니까?
- 훅은 강제 중단에 대해 `exit 2`를 사용하고 명확한 `statusMessage`를 표시합니까?

**도구 계층:**

- 자격 증명 파일(`.env`, `*.pem`, `*.key`, `secrets/`)에 대한 deny 패턴이 있습니까?
- MCP 서버는 리터럴 값이 아닌 `${ENV_VAR}` 플레이스홀더를 통해 자격 증명을 받습니까?
- 위험한 Bash 하위 명령(`git push --delete`, `rm -rf`, `curl|bash`)이 `ask:[]` 또는 `deny:[]`에 있습니까?

**환경 계층:**

- 에이전트의 작업 디렉터리는 사용자 `$HOME`이 아닌 프로젝트로 범위가 지정되어 있습니까?
- Linux/macOS 사용자: 네트워크에 접근하는 Bash 명령을 실행할 때 샌드박스가 활성화되어 있습니까?
- `permissions.defaultMode`가 의도적으로 선택되었습니까(단순히 `default`로 남겨두지 않고)?

**모델 계층:**

- 에이전트별 모델 선택이 근거(YAML 주석)와 함께 문서화되어 있습니까?
- 의도한 모델로 Claude Code 지원 플랜에서 실행 중입니까?

## Plan Mode as Strategy-Level Oversight

Plan Mode는 단순한 권한 모드 이상입니다. Anthropic은 이를 *단계 수준* 감독(각 도구 호출 승인)에서 *전략 수준* 감독(실행 전 전체 계획 승인)으로의 전환으로 표현합니다.

언제 사용할까요:

- 작업 범위가 명확하지 않거나 의도를 벗어나 확장될 수 있을 때
- 에이전트가 익숙하지 않은 코드에서 결정을 내리려고 할 때
- 실행과 별도로 계획의 기록을 원할 때

언제 단계 수준 감독이 여전히 적합한가요:

- 일회성, 잘 정의된 작업
- 어차피 diff를 검토할 신뢰할 수 있는 반복 작업

메커니즘 — Plan Mode 진입 방법과 동작 — 에 대해서는 [효과적 사용 가이드](effective-usage-guide.md)를 참조하세요.

## 서브에이전트 관측성

에이전트가 병렬 서브에이전트를 디스패치할 때, *어떤 서브에이전트가 무엇을 했는지*에 대한 스레드를 유지해야 합니다. 구성 표면:

- `SubagentStop` 훅은 서브에이전트 완료 이벤트를 결정 체인지로그에 기록할 수 있습니다
- 부모의 `PostToolUse` 훅은 서브에이전트 작업의 상태 변경을 표시합니다
- 훅 이벤트 유형은 [고급 기능 가이드 § 훅](advanced-features-guide.md#hooks) 참조

이 가이드는 특정 훅 패턴을 규정하지 않습니다 — 팀의 검토 워크플로에 맞는 것을 선택하세요.

## 교차 참조

방어 관점(어떤 위협으로부터 방어하는가?):

- [`plugin/references/security-patterns.md`](../../../../plugin/references/security-patterns.md) — 명명된 사고 유형이 있는 위협 카탈로그

자동화:

- `/guardians-of-the-claude:secure` — deny 패턴, 보안 규칙, 파일 보호 훅 적용
- `/guardians-of-the-claude:audit` — 다중 계층 루브릭으로 구성 점수 매김

메커니즘:

- [설정 가이드](settings-guide.md) — 권한 모드, 훅, 샌드박스
- [고급 기능 가이드](advanced-features-guide.md) — 훅, 에이전트, 스킬
- [효과적 사용 가이드](effective-usage-guide.md) — Plan Mode 메커니즘

## 추가 자료

- Anthropic Research, [Trustworthy Agents in Practice](https://www.anthropic.com/research/trustworthy-agents) — 출처 프레임워크
- Anthropic Research, [Teaching Claude why](https://www.anthropic.com/research/teaching-claude-why) — 가치 정렬 배경
- [CLAUDE.md 가이드](claude-md-guide.md) — 효과적인 프로젝트 지침 작성
- [규칙 가이드](rules-guide.md) — 모듈형 지침 파일
- [시작하기](getting-started.md) — 기본 설정 단계
