---
title: "멀티 에이전트 패턴"
description: "Orchestrator-Worker, 노력 스케일링, 서브 에이전트 컨텍스트 예산, 너비 우선 탐색, 병렬 디스패치 — Claude Code 서브에이전트 워크플로우를 위한 안내"
version: 1.0.1
---

# 멀티 에이전트 패턴

코딩 작업이 충분히 열린 형태여서 몇 단계가 걸릴지 예측할 수 없을 때, 단일 에이전트는 하나의 컨텍스트 창에서 어려움을 겪습니다. 멀티 에이전트 구성 — 오케스트레이터 하나와 여러 워커 — 은 이런 유형의 작업을 더 잘 처리하지만, 비용이 따릅니다.

이 가이드는 여러 Claude 인스턴스를 디스패치할 때 Anthropic과 다른 팀들이 효과적임을 확인한 패턴을 다룹니다. *단일 에이전트* 설정(Scope, Rules, Constraints, Verification)은 [고급 기능 가이드 — Agents](advanced-features-guide.md#agents)를 참고하세요. 더 넓은 워크플로우 패턴(Writer/Reviewer, fan-out, worktrees)은 [워크플로우 패턴 가이드](workflow-patterns-guide.md)를 참고하세요.

## 멀티 에이전트를 선택하는 경우

| 작업 형태 | 권장 방법 |
|---|---|
| 단계 수를 예측할 수 없는 열린 형태의 리서치 | 멀티 에이전트 (오케스트레이터 + 워커) |
| 순차적이고 고정된 단계 작업 | 프롬프트 체이닝을 활용한 단일 에이전트 |
| 많은 파일에 걸친 대규모 코드베이스 변경 | 오케스트레이터 + 파일 또는 모듈별 병렬 워커 |
| 알려진 파일의 단순 버그 수정 | 단일 에이전트 — 멀티 에이전트 오버헤드는 낭비 |

비용 참고: 멀티 에이전트 실행은 일반적으로 단일 채팅 세션보다 약 15배의 토큰을 사용합니다. 확장하기 전에 지출을 정당화하세요: 지연 시간, 병렬성, 또는 품질이 비용을 초과해야 합니다.

## 패턴: Orchestrator-Worker

리드 에이전트가 작업을 분해하고, 워커 에이전트들이 하위 작업을 실행하며, 리드가 결과를 종합합니다.

*모든* 워커에 대해, 리드는 네 가지를 명시합니다:

1. **Objective** — 정확하게 기술된 달성 목표
2. **Output format** — 반환 형태 (예: "1–2k 토큰 분량의 요약")
3. **Tool guidance** — 선호하거나 피해야 할 도구
4. **Boundaries** — 건드리거나 탐색해서는 안 되는 것

Anthropic은 이렇게 보고합니다: "상세한 작업 설명이 없으면, 에이전트들은 작업을 중복하거나, 빈틈을 남기거나, 필요한 정보를 찾지 못합니다."

오케스트레이터 프롬프트 예시:

```text
Spawn three workers in parallel. For each, specify the objective, output format, tool guidance, and boundaries.

Worker A — Investigate authentication flow.
  Objective: trace how a logged-in user's request reaches the database.
  Output format: 1–2k token summary listing each layer + the file that owns it.
  Tools: prefer Grep/Read; avoid Bash unless tracing runtime behavior.
  Boundaries: only src/auth/ and src/api/middleware/; do not enter src/services/.

Worker B — ...
```

## 노력 스케일링 규칙

리드가 단순한 작업에 과도하게 투자하지 않도록, 이 규칙들을 오케스트레이터의 시스템 프롬프트에 포함하세요:

| 작업 복잡도 | 워커 수 | 워커당 도구 호출 수 |
|---|---|---|
| 단순 사실 조회 | 1 | 3–10 |
| 중간 수준 분석 | 2–4 | 10–30 |
| 복잡한 리서치 | 10+ | 30+ (분리된 책임으로) |

흔한 실패 패턴은 리드가 하나의 Grep으로 답할 수 있는 질문에 10개의 워커를 생성하는 것입니다. 디스패치 전에 조율하세요.

## 서브 에이전트 컨텍스트 예산

각 워커는 전체 대화 기록이 아닌 **정제된 요약(~1–2k 토큰)**을 반환해야 합니다. 이유:

- 리드의 컨텍스트 창이 여러 워커의 결과를 종합하기 위해 깔끔하게 유지됩니다.
- 워커 내부의 도구 호출 결과는 내부적인 사항이지, 리드의 관심사가 아닙니다.
- 리드가 더 깊은 세부 내용이 필요하면, 전체 기록을 받는 대신 워커에게 후속 질문을 합니다.

안티패턴: 워커가 50k 토큰의 원시 출력을 반환 → 리드가 여러 워커의 결과를 자신의 창에 담을 수 없게 됩니다.

## 너비 우선 탐색 전략

작업이 탐색적일 때:

1. 전체 영역을 조사하는 넓은 쿼리로 시작합니다.
2. 드릴다운하기 전에 전체 범위를 평가합니다.
3. 그런 다음에만 워커들을 특정 방향에 할당합니다.

잘못된 브랜치를 먼저 깊이 파고들면 호출이 낭비됩니다.

## 병렬 디스패치 입문

로컬 병렬 디스패치(Bash 루프에서 여러 `claude -p` 호출, 또는 `git worktree`로 세션 격리)에 대해서는 [워크플로우 패턴 — 배치 작업을 위한 Fan-out](workflow-patterns-guide.md#fan-out-for-batch-tasks)을 참고하세요. 해당 가이드에는 비용 및 안전 경고가 포함되어 있습니다; 이를 읽지 않고 fan-out을 실행하지 마세요.

Claude Code의 `Agent` 도구를 통한 *내장* 서브에이전트 디스패치의 경우, 위의 오케스트레이터-워커 패턴이 그대로 적용됩니다 — 부모 세션이 리드이고, 각 `Agent` 호출이 워커입니다.

## 추가 자료

- [고급 기능 가이드 — Agents](advanced-features-guide.md#agents) — 단일 에이전트 설계 (Scope, Rules, Constraints, Verification)
- [워크플로우 패턴 가이드](workflow-patterns-guide.md) — fan-out, Writer/Reviewer, worktrees
- [멀티 에이전트 리서치 시스템 구축기](https://www.anthropic.com/engineering/multi-agent-research-system) (Anthropic Engineering)
- [효과적인 에이전트 구축](https://www.anthropic.com/engineering/building-effective-agents) — 워크플로우 vs. 에이전트 분류법
- [병렬 Claude 팀으로 C 컴파일러 구축](https://www.anthropic.com/engineering/building-c-compiler) — 극단적 병렬성 사례 연구
