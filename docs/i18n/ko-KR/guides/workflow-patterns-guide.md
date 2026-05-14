---
title: "워크플로우 패턴"
description: "인터뷰 우선 명세, Writer/Reviewer, 테스트 우선 멀티 Claude, fan-out (비용/안전 경고 포함), worktrees 및 병렬 세션"
version: 1.0.2
---

# 워크플로우 패턴

Claude Code와 시간을 어떻게 구성하느냐는 무엇을 물어보느냐만큼 중요합니다. 이 패턴들은 Anthropic 내부 팀과 외부 엔지니어링 보고서에서 반복적으로 등장합니다.

*멀티 에이전트 디스패치* (오케스트레이터가 워커를 조율하는 방식)는 [멀티 에이전트 패턴 가이드](multi-agent-patterns-guide.md)를 참고하세요. 이 가이드는 *사람인 당신*이 세션과 배치를 어떻게 구성하는지에 관한 것입니다.

## `AskUserQuestion`으로 Claude가 인터뷰하게 하기

더 큰 기능을 구현할 때, 한 번에 직접 명세를 작성하지 마세요. 먼저 Claude가 인터뷰하도록 하세요:

```text
I want to build [brief description]. Interview me in detail using the
AskUserQuestion tool.

Ask about technical implementation, UI/UX, edge cases, concerns, and
tradeoffs. Don't ask obvious questions — dig into the hard parts I might
not have considered.

Keep interviewing until we've covered everything, then write a complete
spec to SPEC.md.
```

인터뷰가 끝나면, **새로운 세션**을 시작해서 명세를 실행하세요. 새 세션은 구현에만 집중된 깔끔한 컨텍스트를 가지며, 작성된 참고 문서가 있습니다.

이것이 효과적인 이유:

- 인터뷰는 암묵적으로 처리했을 결정들을 표면으로 끌어내어 명시적으로 만들어야 합니다.
- 새로운 세션에서 재시작하면 구현이 브레인스토밍에 편향되지 않습니다.

## Writer/Reviewer 패턴 (멀티 세션)

| 세션 A (Writer) | 세션 B (Reviewer) |
|---|---|
| `Implement a rate limiter for our API endpoints` |   |
|   | `Review the rate limiter implementation in @src/middleware/rateLimiter.ts. Look for edge cases, race conditions, consistency with existing middleware patterns.` |
| `Here's the review feedback: [Session B output]. Address these issues.` |   |

Reviewer는 신선한 컨텍스트에서 세션 A가 방금 작성한 코드에 대한 편향이 없습니다. 이것은 세션 내 "내 작업을 검토해줘" 프롬프트가 놓칠 문제들을 잡아냅니다.

같은 원칙: 한 Claude가 테스트를 작성하고, 다른 Claude가 그것을 통과하는 코드를 작성하게 하세요. 경계가 명시적이 됩니다.

## 테스트 우선 멀티 Claude

1. 세션 A: `Write tests for the user signup flow covering: valid signup, duplicate email, weak password, expired invite token, rate-limit exceeded.`
2. 세션 B (새로운): `Implement the signup flow to pass tests in tests/signup.test.ts. Run the tests after each change.`

구현 전에 수용 기준을 명확하게 합니다. 하나의 세션 안에서도 동작합니다 (테스트 작성, `/clear`, 구현), 하지만 별도의 세션은 더 깔끔한 컨텍스트를 제공합니다.

## Fan-out for batch tasks

대규모 마이그레이션이나 분석에서는 작업을 여러 `claude -p` 호출에 분산시킵니다. 아래 bash 루프는 호출을 *순차적으로* 디스패치합니다; 동시성을 제한해서 병렬화하려면 `xargs -P` 또는 `ForEach-Object -Parallel`을 사용하세요.

> **⚠️ 비용 및 안전 경고**
>
> - 루프에서 `claude -p`는 호출당 토큰 비용이 발생합니다. 수천 개 파일의 마이그레이션은 몇 시간 걸리며 상당한 비용이 누적될 수 있습니다 — 확장 전에 항상 모델의 토큰당 가격으로 비용을 추정하세요.
> - 항상 2–3개 파일에 먼저 드라이런하고, 확장하기 전에 출력을 검증하세요.
> - 무인 실행을 위해 `--allowedTools`로 권한을 범위 지정하세요: `claude -p "..." --allowedTools "Edit,Bash(git commit *)"`
> - Auto 모드는 `-p` 실행에서 반복적인 분류기 거부 후 중단됩니다 — 대신할 사람이 없습니다. 임계값은 [Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)를 참고하세요.

패턴:

1. **작업 목록 생성**: `Have Claude list all 2,000 Python files that need migrating and write them to files.txt`.
2. **루프**:

   ```bash
   # 순차 (한 번에 하나)
   for file in $(cat files.txt); do
     claude -p "Migrate $file from React to Vue. Return OK or FAIL." \
       --allowedTools "Edit,Bash(git commit *)"
   done

   # 제한된 병렬 (동시 워커 4개)
   cat files.txt | xargs -I {} -P 4 \
     claude -p "Migrate {} from React to Vue. Return OK or FAIL." \
       --allowedTools "Edit,Bash(git commit *)"
   ```

**Windows PowerShell 동등 예시:**

```powershell
# 순차
Get-Content files.txt | ForEach-Object { claude -p "Migrate $_ from React to Vue. Return OK or FAIL." --allowedTools "Edit,Bash(git commit *)" }

# 제한된 병렬 (워커 4개; PowerShell 7+ 필요)
Get-Content files.txt | ForEach-Object -Parallel { claude -p "Migrate $_ from React to Vue. Return OK or FAIL." --allowedTools "Edit,Bash(git commit *)" } -ThrottleLimit 4
```

3. **처음 2–3개로 정제 후 확장**: 초반에 잘못된 프롬프트를 잡아내고; 출력 형태를 확인한 후에만 전체 세트에 실행하세요.

JSON 구조화된 출력 (스크립트에서 파싱)을 위해 `--output-format json`을 추가하세요. 스트리밍을 위해서는 `--output-format stream-json`을 사용하세요.

## Worktrees and parallel sessions

진정으로 격리된 병렬 작업이 필요할 때 (예: 위험한 리팩토링을 실험하면서 메인 라인 작업을 계속할 때), `git worktree`를 사용하세요:

```bash
git worktree add ../feature-x feature-x
cd ../feature-x
claude  # this session works on feature-x branch only; main worktree is untouched
```

worktree 사용이 끝나면 깔끔하게 제거하세요:

```bash
git worktree remove ../feature-x
git worktree list  # 제거 확인
```

`git worktree remove` 없이 디렉토리만 삭제하면 오래된 worktree 등록 항목이 쌓입니다. 고아 항목을 정리하려면 `git worktree prune`을 실행하세요.

| 옵션 | 최적 사용 사례 |
|---|---|
| `git worktree` (CLI) | 같은 머신, 완전한 격리, 수동 조율 |
| 데스크톱 앱 멀티 세션 | 시각적 세션 관리 |
| 웹의 Claude Code | Anthropic 호스팅, 격리된 VM |

멀티 세션을 사용하지 *말아야 할* 때: 소규모의 집중된 작업. 세션 간 컨텍스트 전환에는 오버헤드가 있습니다 — 작업이 진정으로 독립적이지 않으면 얻는 것보다 잃는 것이 많습니다.

## 추가 자료

- [멀티 에이전트 패턴 가이드](multi-agent-patterns-guide.md) — 오케스트레이터가 워커를 디스패치하는 방식 (사람이 조율하는 멀티 세션과 비교)
- [Claude Code: Best practices for agentic coding](https://code.claude.com/docs/en/best-practices) — 여기서 다루는 많은 패턴의 업스트림 소스
- [Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode) — 헤드리스 및 자동 파일럿 세부 사항
