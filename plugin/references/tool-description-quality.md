---
title: "Skill & Tool Description Quality"
description: "Domain expert framing, dual-format responses, error message design, evaluation-driven iteration"
version: 1.0.0
---

# Skill & Tool Description Quality

Skill `description` fields are pre-loaded into the system prompt at session start. Claude reads them to decide whether to trigger the skill. Poorly written descriptions mean skills never fire when relevant — well-tuned ones beat raw functionality. Apply these principles when authoring or reviewing any skill, tool, or hook description.

## 4 principles

### 1. Domain expert framing

Write as if onboarding a new team member: surface specialized query formats, niche terminology, and the relationships between resources. Avoid generic phrasing.

- Avoid: `"Manages user data."`
- Prefer: `"Searches active customer accounts by email, phone, or order ID. Returns the canonical CRM record; surface deactivated accounts separately via the `include_inactive` flag."`

### 2. Trigger phrase pattern

Include an explicit phrasing of when to use the skill so Claude can match user intent at decision time:

- `"Use when the user asks to ..."`
- `"When ... fails, ..."`
- `"Apply during ..."`

Skills without a trigger phrase often miss activation even when relevant.

### 3. Dual-format responses (for tools that return data)

Support a `response_format` enum with at least two modes:

| Mode | Typical token count | Use case |
|---|---|---|
| `"concise"` | 50–80 | Quick lookup / chained tool calls |
| `"detailed"` | 150–250 | Full record / human-readable output |

This saves context when many tools chain together.

### 4. Meaningful error messages

Replace opaque traceback dumps with actionable improvements. The agent needs to know *how to fix* the call, not just that it failed.

- Avoid: `"Error: invalid argument"`
- Prefer: `"Error: \`path\` must be an absolute path (received: ./src/file.ts). Try /home/user/project/src/file.ts, or use the \`resolve_path\` tool first."`

## Iterative refinement

Description quality is rarely right on the first draft. Use evaluation-driven iteration:

1. Concatenate transcripts of recent skill invocations (~20–50 sessions).
2. Have Claude analyze where the skill should have triggered but did not, or triggered when it should not have.
3. Propose description refinements based on observed failure modes.
4. Re-run a small eval set; measure trigger rate and parameter-error rate.

Anthropic reports gains of ~40% in completion time on tool-using benchmarks after such refinement cycles.

## Anti-patterns

- Wrapping every API endpoint mechanically into a separate tool — consolidate workflows instead (e.g., one `schedule_event` instead of three separate `check_availability` / `create_event` / `send_invite`).
- Generic parameter names — `user` should be `user_id` or `user_email`.
- Cryptic IDs as parameters — resolve to semantic names where possible (e.g., `project_name` rather than `proj_alphanum`).
- Sparse documentation that assumes fields are self-explanatory.
- Treating tool/skill design as one-shot — descriptions evolve as Claude's usage patterns surface gaps.

## References

- [Writing effective tools for agents — with agents](https://www.anthropic.com/engineering/writing-tools-for-agents) (Anthropic Engineering)
- [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) (Anthropic Engineering)
- [Raising the bar on SWE-bench Verified with Claude 3.5 Sonnet](https://www.anthropic.com/engineering/swe-bench-sonnet) (Anthropic Engineering — minimalist tool design, error-proof interfaces)
