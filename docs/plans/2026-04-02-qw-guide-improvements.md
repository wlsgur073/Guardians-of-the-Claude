# Quick Win Guide Improvements (QW-1~3)

**Date:** 2026-04-02
**Branch:** `feat/qw-guide-improvements`
**Status:** Implemented

## Context

oh-my-claudecode(OMC) 분석을 통해 교육적으로 가치 있는 패턴을 선별하여 가이드와 템플릿에 반영. OMC의 복잡성을 그대로 가져오는 것이 아니라, Claude Code 네이티브 패턴에 맞게 재설계.

## Implemented (Quick Wins)

### QW-1. Agent Prompt Structure

에이전트 예시를 2섹션(Scope/Rules)에서 4섹션 구조로 강화:
- **Scope** -- agent가 다룰 수 있는 범위
- **Rules** -- 작업 방식
- **Constraints** -- 피해를 방지하는 절대 제한
- **Verification** -- 작업 완료 확인 방법

YAML 주석(`# sonnet: balances speed and quality`)으로 모델 선택 이유를 자체 문서화. 모든 섹션 `##`(H2) 사용으로 markdownlint MD025 준수.

**Files:** `advanced-features-guide.md`, `backend-developer.md`

### QW-2. Hook Event Diversity

단일 PostToolUse 예시에서 PreToolUse + PostToolUse 2개 훅 예시로 확장:
- `PreToolUse` + `exit 2` -- 파일 보호 패턴 (`.env`, `package-lock.json`, `migrations/`)
- `UserPromptSubmit` -- 키워드 감지, 자동 컨텍스트 주입 용도 설명 추가

템플릿 `settings.json`의 훅 순서를 가이드와 일치하도록 PreToolUse → PostToolUse로 정렬. `exit 1` → `exit 2` 수정.

**Files:** `advanced-features-guide.md`, `settings.json`

### QW-3. Model Routing Guidance

에이전트 섹션에 모델 선택 기준표 추가:

| Model | Best for |
|-------|----------|
| `haiku` | 탐색, 파일 검색 |
| `sonnet` | 구현, 디버깅, 테스트 |
| `opus` | 아키텍처 리뷰, 심층 분석 |

**Files:** `advanced-features-guide.md`

## Pending (Future Work)

아래 항목들은 별도 구현 사이클에서 진행:

- **HI-1.** READ-ONLY 에이전트 패턴 (분석/구현 분리)
- **HI-2.** 에이전트 카탈로그 패턴 (3-4개 에이전트 세트)
- **HI-3.** 커밋 프로토콜 패턴 (AI 협업 시 커밋 컨텍스트 보존)
- **NH-1.** AGENTS.md 경계 명시 (Codex CLI 지침 파일과의 분리)
- **NH-2.** AI 생성 코드 리뷰 체크리스트
- **NH-3.** 훅 기반 세션 상태 관리

## Constraints

- `advanced-features-guide.md` 줄 제한: ~150-160 (130에서 완화)
- 템플릿은 TaskFlow 프로젝트 컨텍스트 유지
- 한국어 번역(`docs/i18n/ko-KR/`) 영문과 동기화 완료
