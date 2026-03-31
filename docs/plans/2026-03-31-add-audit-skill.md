# Add /audit Skill

**Date:** 2026-03-31
**Branch:** `add-audit-skill`
**Status:** In Progress

## Context

`/generate`로 생성한 설정이 시간이 지나며 프로젝트와 괴리가 생길 수 있다. `/audit`는 기존 Claude Code 설정의 건강 상태를 검증하고 개선을 제안하는 스킬. audit(객관 검증)과 review(정성 평가)를 하나의 스킬로 통합.

## Design

### Phase 구성
1. **Phase 1: Essential Checks** — 빠지면 Claude 성능에 직접 영향
   - CLAUDE.md 존재 여부 및 테스트/빌드 명령어 포함 확인
   - settings.json deny 패턴 (.env, secrets) 확인
   - 프로젝트 개요 섹션 존재 확인

2. **Phase 2: Alignment Checks** — 설정과 프로젝트의 정합성
   - CLAUDE.md에 언급된 디렉터리가 실제 존재하는지
   - CLAUDE.md 길이 (200줄 초과 시 rules 분리 제안)
   - rules의 paths 필드와 실제 파일 매칭
   - 참조된 명령어 실행 가능 여부 (package.json 등 확인)

3. **Phase 3: Suggestions** — 있으면 좋은 개선 제안
   - hooks 미사용 시 제안
   - 대규모 프로젝트에 agents 제안
   - 반복 작업 감지 시 skill 생성 제안

### 출력 형식
각 Phase 결과를 요약 테이블로 출력하고, 마지막에 종합 개선 제안 제시.

### 파일
- `plugin/skills/audit/SKILL.md` — 단일 파일로 시작, 비대해지면 모듈화
