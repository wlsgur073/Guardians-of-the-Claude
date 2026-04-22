---
title: "추천 플러그인"
description: "카테고리별로 정리된 Claude Code 추천 플러그인 목록"
version: 1.0.0
---

# 추천 플러그인

Claude Code는 기능을 확장하는 공식 플러그인을 지원합니다. Claude Code에서 `/plugin`으로 탐색하거나, [플러그인 문서](https://code.claude.com/docs/en/discover-plugins)를 참고하세요.

## 개발 워크플로우

| 플러그인 | 설명 |
| ------ | ------------ |
| [superpowers](https://github.com/obra/superpowers) | 전체 개발 워크플로우 -- 스펙 → 설계 → 계획 → 서브에이전트 기반 구현. Claude가 계획에서 벗어나지 않고 자율 작업 |
| [feature-dev](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/feature-dev) | 구조화된 7단계 기능 개발: 코드베이스 탐색 → 질문 → 설계 → 구현 → 리뷰 |
| [code-review](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-review) | 멀티 에이전트 PR 리뷰. 신뢰도 기반 스코어링으로 노이즈를 걸러내고 실제 이슈만 포착 |
| [code-simplifier](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-simplifier) | 최근 수정된 코드를 명확하고 일관되게 리팩터링. 기존 동작은 그대로 유지 |

## 코드 인텔리전스 & 품질

| 플러그인 | 설명 |
| ------ | ------------ |
| [typescript-lsp](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/typescript-lsp) | TypeScript/JS 언어 서버 -- 정의로 이동, 참조 찾기, 에러 체크를 Claude 안에서 바로 |
| [security-guidance](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/security-guidance) | 코드 작성 전 보안 취약점(XSS, 인젝션 등)을 경고하는 Pre-edit 훅 |
| [context7](https://github.com/upstash/context7) | 최신 라이브러리 문서를 즉시 가져오는 MCP 서버. API 할루시네이션 방지 |

## UI & 브라우저

| 플러그인 | 설명 |
| ------ | ------------ |
| [frontend-design](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/frontend-design) | "AI가 만든 것 같지 않은" 독특하고 프로덕션 수준의 UI 생성 |
| [chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) | 실시간 Chrome 브라우저 제어 및 검사 -- 디버깅, 자동화, 성능 분석 |
| [figma](https://github.com/figma/mcp-server-guide) | Figma 디자인 파일에서 컨텍스트를 직접 가져와 구현에 활용 |

## 프로젝트 셋업

| 플러그인 | 설명 |
| ------ | ------------ |
| [claude-code-setup](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-code-setup) | 코드베이스를 스캔하고 프로젝트에 최적화된 hooks, skills, MCP 서버, 서브에이전트를 추천 |
| [claude-md-management](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-md-management) | CLAUDE.md 품질 감사 + `/revise-claude-md`로 세션 학습 내용 반영 |

## 설치 방법

1. 사용 가능한 플러그인 탐색:

   ```text
   /plugin
   ```

2. 마켓플레이스 추가 및 설치:

   ```text
   /plugin marketplace add <owner>/<repo>
   /plugin install <plugin-name>@<marketplace-name>
   ```

3. 설치 확인:

   ```text
   /plugin list
   ```

> **팁:** 일부 플러그인(예: context7)은 별도 설정이 필요한 MCP 서버입니다. 각 플러그인의 README에서 설치 방법을 확인하세요.
