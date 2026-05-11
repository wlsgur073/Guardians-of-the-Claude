# Roadmap

## Vision

Guardians of the Claude aims to be **the definitive meta-system for Claude Code
configuration** — a single tool that scales from a 2-minute beginner quickstart
to a self-learning, self-auditing, self-optimizing configuration harness for
power users.

**Today:** Starter templates, guides, and 4 guided skills (`/create`, `/audit`,
`/secure`, `/optimize`) that generate and maintain CLAUDE.md, settings.json,
rules, hooks, agents, and skills.

**Tomorrow:** A progressive meta-system where beginners never see complexity
they don't need, and power users get a layer that learns project context,
tracks decisions across sessions, and evolves configuration intelligently
over time.

## North Star — Claude Code Meta System

The long-term direction of this project is to evolve from "templates and
guides" into a comprehensive **meta-system** for Claude Code configuration:

- **Progressive disclosure** — Day 1 users experience a 2-minute setup; Day 30
  users discover audit, security hardening, and optimization; Day 100 users
  rely on cross-skill learning and automated drift detection
- **Learning continuity** — Persistent project profile, decision changelog,
  and cross-skill memory let the system remember context across sessions and
  sub-projects. See `plugin/references/learning-system.md` for the current
  implementation
- **Both audiences, one tool** — The same plugin serves Claude Code newcomers
  ("help me write my first CLAUDE.md") and experienced users ("audit my
  config, flag drift, suggest optimizations") without forcing either group
  to compromise
- **Beyond static templates** — While templates are a good starting point, the
  end-state is less about providing examples and more about dynamic
  configuration intelligence tailored to each project's actual state

This is a multi-year direction. Current work (v2.x) lays the foundation —
learning system, cross-skill memory, critical thinking, and decision
journaling. Later major versions may explore: configuration analytics,
team-level config sharing, deeper integration with the Claude Code plugin
ecosystem, and contribution-graph-aware recommendations.

## Backlog

Items reviewed and accepted but not yet scheduled:

- **Interactive plugin onboarding** — Improve the SessionStart hook experience with smarter project detection
- **Additional language translations** — Expand beyond Korean (community-driven)
- **Stack-adaptive improvements** — Enhance `/create` for better support of diverse stacks (improved manifest detection, stack-specific command defaults in question templates, expanded starter command table). Note: we intentionally do NOT maintain per-stack filled templates. TaskFlow is a fictional reference project, and the Node/Express example illustrates one concrete implementation. `/create` handles stack adaptation at runtime by detecting manifests or asking users. See [`templates/README.md`](../templates/README.md) for the convention
- **Meta-system milestones** — Periodically review the North Star and propose discrete sub-projects that advance it (see [GitHub Discussions](https://github.com/wlsgur073/Guardians-of-the-Claude/discussions) for the current thread)
- **Audit v4 — two coupled improvements (COMPLETE).** **v2.12.0 (released 2026-04-23)** rewrote `scoring-model.md` — rule/agent/MCP additive points moved to load-bearing-evidence basis, and LAV converted from additive (−9 ~ +10) to a Detail Score multiplier so severely Overconfigured CLAUDE.md files cannot escape the conciseness penalty via inflated mechanical scores (concrete evidence from v2.10.0: ours=85 vs. claude-md-improver=58 on the same Overconfigured fixture, +27 over-rating). v2.12.0 also added the first model-drift rules (`plugin/references/model-drift-rules.md`, per-model pattern matrix) and the first additive schema bump (profile schema 1.0.0 → 1.1.0 adding `claude_code_configuration_state.model`) — first actual implementation of the versioned-dispatcher behavioral contract from v2.11.0. **v2.13.0 (released 2026-05-01)** added per-package `CLAUDE.md` scoring with rollup output for monorepos (extends v2.10.0's disclosure-only walk). Both releases shipped with validation-set re-baselining and visible CHANGELOG score-delta matrices because existing audit scores shifted. Audit v4 Phase 2 (Raw exposure surfaces, Excellence Opportunities tier) remains a future item if the LAV-as-multiplier formula is revisited.
- **Audit Gap C decision (automatic diff suggestions) — explicitly NOT closed inside `/audit`.** Producing concrete diff suggestions in the `/audit` output would either require merging `/audit` and `/optimize` (violates "skill per role") or adding a `--dry-run` style flag (violates the zero-options principle: skills must not expose flags or `$ARGUMENTS`). Independent review (2026-04-11) also noted that diff suggestions amplify whatever the audit currently believes, so coupling them to an uncalibrated audit (before audit v4 score recalibration ships) would turn diagnosis errors into action errors. `/audit`'s existing advice quality may improve incrementally over time as a default-behavior improvement, but no flag, argument, or new skill will be added. Revisit only if user pain reports surface.

See [CHANGELOG.md](../CHANGELOG.md) for version history.

## Revisit Triggers

These are not scheduled work and not part of the backlog. They are areas
reviewed and explicitly set aside; reopen only when the listed trigger
evidence exists. Recorded here so the trigger conditions survive periodic
cleanup of planning artifacts.

| Area | Reopen only if | Why dormant now |
|---|---|---|
| `/audit` subagent briefing refinement | Per-finding rejection logging mechanism exists, then n=5 hypothesis sample → n=15-20 decision gate | No data-capture mechanism for cause-classifiable rejection data |
| `/audit` reasoning checkpoints (think-tool style) | n=5 real-failure sample shows hallucination or criterion-ambiguity signal | No trigger signal observed |
| LLM-as-judge evals for `/audit` rubrics | 20-50 human-scored audit outputs exist as calibrated ground truth | Same-family judge bias makes uncalibrated adoption net-negative |
| Phase-boundary contracts / intra-phase notes for `/audit` | Evidence of phase-boundary failure or state-loss pain | No observed pain reports |
| Agent Patterns guide + harness subsection | Explicit user demand | Without external demand, becomes mission drift toward "Anthropic concepts explained" |
| MCP guide: code-execution / programmatic-tool-calling sections | User demand, or MCP guide rework for other reasons | Narrow audience; consolidation lowers cost but does not create demand |
| New Anthropic engineering insights review round | Canonical Claude Code docs change, new skills/plugins/evals normative guidance, empirical failure cluster (≥3 independent reports OR one high-severity issue), or implemented proposal failure outside current coverage | Generic blog mining without a trigger is out of scope |

## Propose a Change

Have an idea or suggestion for this roadmap?

1. Open a new discussion in [GitHub Discussions](https://github.com/wlsgur073/Guardians-of-the-Claude/discussions)
2. Describe your idea and why it would help
3. The community discusses, then the maintainer decides

Every decision (accept or decline) will include a comment explaining the reasoning.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contribution process.
