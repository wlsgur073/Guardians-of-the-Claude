---
title: "MCP 연동"
description: "Model Context Protocol을 통해 Claude Code를 외부 도구 및 서비스에 연결하는 방법"
version: 1.0.2
---

# MCP 연동

## MCP란 무엇인가?

Model Context Protocol(MCP)은 Claude Code가 데이터베이스, API, 문서 서비스 등 외부 도구에 연결할 수 있도록 해줍니다. MCP 서버는 로컬 프로세스로 실행되며, 세션 중 Claude가 호출할 수 있는 도구를 노출합니다.

## 설정

MCP 서버는 프로젝트 루트의 `.mcp.json`에서 설정합니다:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "@example/mcp-server"],
      "env": {
        "API_KEY": "your-key-here"
      }
    }
  }
}
```

주요 필드:

- **`command`** -- 서버를 실행하는 방법 (`npx`, `uvx`, `docker`, `node` 등)
- **`args`** -- 명령에 전달되는 인자
- **`env`** -- 서버에 필요한 환경 변수 (API 키, 연결 문자열)

## 서버 유형

MCP 서버를 실행하는 세 가지 일반적인 패턴:

| 패턴 | 명령 | 예시 |
| ---- | ---- | ---- |
| Node.js 패키지 | `npx` | `npx -y @modelcontextprotocol/server-filesystem` |
| Python 패키지 | `uvx` | `uvx --from mcp-server-fetch mcp-server-fetch` |
| Docker 컨테이너 | `docker` | `docker run -i --rm mcp/postgres` |

## 지연 도구 로딩

MCP 도구는 Claude 시작 시 **즉시 로딩되지 않습니다**. 지연 도구로 표시되며 `ToolSearch`를 통해 활성화해야 합니다:

1. Claude가 세션 시작 시 지연 도구 이름 목록을 확인합니다
2. 도구가 필요할 때 Claude가 `ToolSearch`를 호출하여 전체 스키마를 가져옵니다
3. 그 후에야 Claude가 해당 도구를 실행할 수 있습니다

MCP 도구는 실제로 사용될 때까지 컨텍스트를 소비하지 않으므로, 여러 서버가 있는 프로젝트에서 효율적인 설계입니다.

## 설정 파일 위치

| 위치 | 범위 | Git에 커밋? |
| ---- | ---- | ----------- |
| `.mcp.json` (프로젝트 루트) | 프로젝트 -- 팀과 공유 | env에 비밀 정보가 없으면 가능 |
| `~/.claude/mcp.json` | 사용자 -- 모든 프로젝트에 적용 | 아니오 (개인용) |
| 플러그인 `plugin.json`의 `mcpServers` 필드 | 플러그인 -- 플러그인에 번들 | 예 |

**보안 참고:** `.mcp.json`의 `env` 필드에 API 키가 포함된 경우, `.gitignore`에 추가하고 필요한 키를 CLAUDE.md에 문서화하세요. 또는 파일 외부에서 설정된 환경 변수를 참조하세요.

## 플러그인 MCP 연동

플러그인은 `plugin.json`에서 설정 파일을 참조하여 MCP 서버를 번들할 수 있습니다:

```json
{
  "name": "my-plugin",
  "mcpServers": "./.mcp.json"
}
```

플러그인의 `.mcp.json`은 이식 가능한 경로를 위해 `${CLAUDE_PLUGIN_ROOT}`를 사용할 수 있습니다:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/server/index.js"]
    }
  }
}
```

## 실전 예제: TaskFlow

TaskFlow 프로젝트에서 개발 중 데이터베이스를 직접 쿼리하기 위해 PostgreSQL MCP 서버에 연결할 수 있습니다:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "${POSTGRES_CONNECTION_STRING}"
      }
    }
  }
}
```

Claude Code는 로드 시점에 `${POSTGRES_CONNECTION_STRING}`을 쉘 환경에서 확장합니다 — `.envrc`, `.bashrc`, 또는 CI secrets에 설정하세요. 실제 값을 git에 커밋하지 마세요.

이렇게 설정하면 Claude가 데이터베이스에 직접 쿼리할 수 있습니다 -- 스키마 확인, 마이그레이션 검증, 데이터 문제 디버깅 등을 수행할 수 있습니다.

## 주요 MCP 서버

| 서버 | 용도 |
| ---- | ---- |
| `@modelcontextprotocol/server-filesystem` | 프로젝트 외부의 파일 읽기/쓰기 |
| `@modelcontextprotocol/server-postgres` | PostgreSQL 데이터베이스 쿼리 |
| `@anthropic-ai/claude-code-mcp-server` | Claude Code를 MCP 도구로 실행 |
| `mcp-server-fetch` (Python) | 웹 콘텐츠 가져오기 및 파싱 |

## 보안 고려사항

- **신뢰할 수 있는 서버만 등록하세요** -- MCP 서버는 로컬 머신에서 임의의 코드를 실행할 수 있습니다
- **커밋된 파일에 비밀 정보를 포함하지 마세요** -- 환경 변수를 사용하거나 `.mcp.json`을 `.gitignore`에 추가하세요
- **서버 버전을 고정하세요** -- 예기치 않은 업데이트를 방지하기 위해 args에 정확한 패키지 버전을 사용하세요

## 추가 자료

- [설정 가이드](settings-guide.md) -- 권한 및 환경설정
- [고급 기능 가이드](advanced-features-guide.md) -- 훅, 에이전트, 스킬
