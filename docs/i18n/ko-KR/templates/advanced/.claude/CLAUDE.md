---
title: "TaskFlow .claude/CLAUDE.md (대안 위치)"
description: ".claude/ 디렉터리 내 프로젝트 지시문 배치 옵션을 보여주는 데모 스텁"
version: 2.4.0
---

<!-- 이 두 파일은 "하나만 선택" 쌍입니다 — 루트 또는 .claude/ 중 하나만 사용하세요. -->

# 프로젝트 지시문 (대안 위치)

프로젝트 루트 대신 `.claude/CLAUDE.md`에 지시문을 배치하는 방법을 보여줍니다. 전체 예시는 `templates/advanced/CLAUDE.md` (루트 배치)를 참고하세요.

## `.claude/CLAUDE.md`를 사용할 때
- 프로젝트 루트를 깔끔하게 유지하고 싶을 때
- 루트에 이미 설정 파일이 많을 때 (eslint, prettier, tsconfig 등)
- 다른 Claude Code 설정(.claude/rules/, .claude/agents/)과 함께 묶고 싶을 때

## 루트 `./CLAUDE.md`를 사용할 때
- 저장소 탐색 시 파일이 한눈에 보이길 원할 때
- 설정 파일이 적은 소규모 프로젝트일 때
- 새 기여자의 접근성을 최대화하고 싶을 때
