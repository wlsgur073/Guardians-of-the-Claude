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

- **Progressive disclosure** — Day 1 users experience a 2-minute setup; Day 7
  users discover audit, security hardening, and optimization; Day 14 users
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
- **Additional language translations** — Community-driven translations of specific guides or templates on request (EN is the canonical single source; translations are on-demand rather than CI-enforced mirrors)
- **Stack-adaptive improvements** — Enhance `/create` for better support of diverse stacks (improved manifest detection, stack-specific command defaults in question templates, expanded starter command table). Note: we intentionally do NOT maintain per-stack filled templates. TaskFlow is a fictional reference project, and the Node/Express example illustrates one concrete implementation. `/create` handles stack adaptation at runtime by detecting manifests or asking users. See [`templates/README.md`](../templates/README.md) for the convention
- **Meta-system milestones** — Periodically review the North Star and propose discrete sub-projects that advance it (see [GitHub Discussions](https://github.com/wlsgur073/Guardians-of-the-Claude/discussions) for the current thread)
- **Post-ship validation mechanism for user-facing guide additions** — the project's first Philosophy principle ("Verify, don't trust") applies to ourselves too. Currently we ship guide sections without a feedback mechanism to verify they improve user behavior. Initial scope: lightweight signals such as a future `/audit` question "does the project teach users what good Claude behavior looks like?", user docs review channels, and support-issue examples.
- **Hook lifecycle dispatch system** — adopt the `hooks.d/<event>/<priority>-<name>.sh` pattern (priority-ordered shell scripts under one directory per lifecycle event) to replace the current flat `plugin/hooks/*.sh` layout once hook surface grows. Today the plugin registers only `SessionStart` (one single-purpose bash script), so flat layout is adequate. Schedule trigger: adding a third Claude Code hook event (e.g., `SessionEnd`, `UserPromptSubmit`, `PreCompact`), OR a single hook event needing multiple distinct concerns (e.g., session-start auto-brief plus telemetry plus project-detection becoming three separable scripts). Sub-decisions when scheduled: dispatcher script location (top-level `hooks/dispatch.sh` vs per-event), priority numbering convention (`00-99`), no-op semantics for empty event directories, `.gitkeep` vs README-per-directory for discoverability.
- **Exact per-skill / per-MCP token attribution via OpenTelemetry** — the bundled usage helper (`plugin/references/lib/usage-parser.sh`) summarizes token counts from local Claude Code transcripts, so attribution of which skill or MCP server consumed tokens is heuristic (inferred from transcript structure, not measured per-call). A future enhancement could read Claude Code's OpenTelemetry metrics/logs export for exact per-skill and per-MCP attribution, making the `/audit` usage report and the `mcp-unused` recommendation precise rather than inferred. Sub-decisions when scheduled: opt-in detection of an OTel exporter (no network dependency added by default), graceful fallback to the transcript heuristic when no exporter is configured, and reconciling the two attribution sources when both are present.
- **Usage-parser robustness hardening for large / edge-case transcript directories** — the bundled `plugin/references/lib/usage-parser.sh` currently buffers all derived records in memory and passes the tool array via `--argjson` (adequate for typical installs, but can hit memory / `ARG_MAX` limits on long-lived ones). Future work: stream aggregation in a single `jq` reduce pass; disambiguate duplicate session basenames across project subdirectories (today two same-named `*.jsonl` files merge into one session); tolerate MCP server names containing characters outside `[A-Za-z0-9_]` in the `by_mcp_server` capture. Deferred from the v3.1.0 usage-analytics feature; the current implementation is correct for typical single-machine usage.

## Completed

Items previously listed in Backlog that have shipped. Retained for context on past direction; full version history lives in [CHANGELOG.md](../CHANGELOG.md).

- **3-tier config deep merge for skill rule customization.** Shipped in v3.2.0 (2026-06-11) as a two-knob system: `/secure` `additional_deny_patterns` (union, add-only) and `/optimize` `skip`, resolved by a bundled bash+jq helper across plugin defaults / user-global / per-project configs. `/audit` customization deferred — the Quality Gate is condition-based, not a numeric threshold, so no clean knob exists yet.
- **State-file permission contract for `state_io.md`.** Shipped in v3.2.0 (2026-06-11). Made the owner-only (`0o600`) property of state files an explicit, documented contract instead of an incidental side effect: `atomic_write` now sets the mode on the temp fd *before* `os.replace` publishes the file (POSIX-guarded `os.fchmod`), the state-mutation lock directory is created `0o700` (with `0o700` for the per-user cache directory recommended in the same section), and a new "State-file permissions (POSIX 0600)" section explains why the temp-file-then-rename idiom already yields `0o600` (mkstemp + inode-preserving rename), why no migration is needed, the Windows no-op, and what `0o600` does not protect against. No change to which files are written.
- **Audit v4 — two coupled improvements.** **v2.12.0 (released 2026-04-23)** rewrote `scoring-model.md` — rule/agent/MCP additive points moved to load-bearing-evidence basis, and LAV converted from additive (−9 ~ +10) to a Detail Score multiplier so severely Overconfigured CLAUDE.md files cannot escape the conciseness penalty via inflated mechanical scores (concrete evidence from v2.10.0: ours=85 vs. claude-md-improver=58 on the same Overconfigured fixture, +27 over-rating). v2.12.0 also added the first model-drift rules (`plugin/references/model-drift-rules.md`, per-model pattern matrix) and the first additive schema bump (profile schema 1.0.0 → 1.1.0 adding `claude_code_configuration_state.model`) — first actual implementation of the versioned-dispatcher behavioral contract from v2.11.0. **v2.13.0 (released 2026-05-01)** added per-package `CLAUDE.md` scoring with rollup output for monorepos (extends v2.10.0's disclosure-only walk). Both releases shipped with validation-set re-baselining and visible CHANGELOG score-delta matrices because existing audit scores shifted. Audit v4 Phase 2 (Raw exposure surfaces, Excellence Opportunities tier) remains a future item if the LAV-as-multiplier formula is revisited.
- **Defense Surfaces checklist for security reference.** **v2.19.9 (released 2026-05-21)** added a new `### Defense Surfaces Catalog` section to `plugin/references/security-patterns.md` mapping 11 input surfaces (repository files, dependency scripts, shell output, browser content, MCP responses, generated artifacts, quoted/pasted external content and attachments, hook code and hook output, persistent local state, CI fixtures, external downloads) to existing threats and defensive postures, with an "Authorized Security Work" footnote covering user-scoped pre-authorization for destructive techniques.
- **Universal untrusted-content rule for templates.** **v2.19.9 (released 2026-05-21)** added a one-line rule under the existing Trust Boundary section of starter and advanced templates (with ko-KR and ja-JP mirrors) instructing agents to treat content from the 11 named input surfaces as evidence, not instruction. Cross-references the Defense Surfaces Catalog for the canonical surface list.
- **Injection-reminder threat-model → `/secure` skill mapping.** **v2.19.9 (released 2026-05-21)** added an "Injection Reminder Mapping" sub-section to `plugin/skills/secure/SKILL.md` mapping 6 injection reminder types (image content, cyber-action, system-instruction, ethics, IP, long-conversation) to Defense Surfaces and `/secure` check patterns. 2 of 6 produce mechanical checks; 4 are advisory references.

## Will Not Pursue

Items reviewed and explicitly declined. Reopen only if the listed evidence appears.

- **Automatic diff suggestions inside `/audit`** — Producing concrete diff suggestions in the `/audit` output would either require merging `/audit` and `/optimize` (violates "skill per role") or adding a `--dry-run` style flag (violates the zero-options principle: skills must not expose flags or `$ARGUMENTS`). Independent review (2026-04-11) also noted that diff suggestions amplify whatever the audit currently believes, so coupling them to an uncalibrated audit (before audit v4 score recalibration ships) would turn diagnosis errors into action errors. `/audit`'s existing advice quality may improve incrementally over time as a default-behavior improvement, but no flag, argument, or new skill will be added. **Reopen only if** user pain reports surface.
- **Default-stance pattern example for advanced template** — Anthropic's public Opus 4.7 system prompt (published 2026-04-16) carries an attempt-first default stance in `<acting_vs_clarifying>`, directing Claude to make an immediate attempt when minor request details are unspecified and to ask upfront only when the missing information makes the request unanswerable at all. This pattern is calibrated for the general chat context where misinterpretation cost is low. The advanced template's intentionally-opposite ask-first "Development Approach" section — cascaded across `templates/advanced/CLAUDE.md` and `plugin/skills/create/templates/{advanced,starter}.md` — targets production-code template editing where ambiguous requests can affect APIs, data models, security, migrations, or user-visible behavior with non-trivial blast radius. Paraphrasing the Opus 4.7 pattern into the advanced template would teach the wrong stance for this context, and a maintainer-adapted production-stance variant could not honestly attribute itself to the Opus 4.7 pattern it diverges from. **Reopen only if** user pain reports surface that the ask-first stance over-clarifies on low-risk reversible details, OR a production-adapted default-stance is brainstormed as a separate backlog item with explicit non-Opus-4.7 attribution.

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
| New Anthropic engineering insights review round | One of four conditions: ① canonical Claude Code docs change, ② new skills/plugins/evals normative guidance, ③ empirical failure cluster (≥3 independent reports OR one high-severity issue), or ④ implemented proposal failure outside current coverage | Generic blog mining without a trigger is out of scope. Checked 2026-05-16 (anthropic.com/news, Jan–May 2026): canonical Claude Code docs changed in-window but produced zero shipped-content defects — only discretionary additive items, weighed and declined here; the new-normative-guidance, failure-cluster, and implemented-proposal-failure conditions were unmet (the Agent Skills open-standard framing predates this check). Blog/news mining structurally cannot satisfy the failure-cluster or proposal-failure conditions (internal repository evidence only) — only the first two conditions are reachable this way. Re-checked 2026-06-01: condition ① fired once — the late-May 2026 canonical change bringing auto mode to all plans made the shipped "auto mode not on Pro" availability statement defective (corrected in v3.1.1); ② was unmet (no new normative skills/plugins/evals guidance in-window) and ③④ remain structurally unreachable. Re-checked 2026-06-02 against a third-party Claude Code workflow article cluster: no trigger met. Shipped one self-derived doc change (the append/promote/prune CLAUDE.md-maintenance rule, `claude-md-guide.md` v1.4.4); declined a downstream PR-evidence-contract template (out of scope for a solo-maintainer config repo); deferred — NOT promoted to Backlog — a set of source-mined candidates (MCP visible-tool-surface wording, recommendation state-machine user docs, instruction-density rubric, operating-envelope positioning, `/audit` proof-surface grouping, remote-environment security checklist, agent route-map / `llms.txt`). |
| Memory/state verification doctrine naming | (1) a second skill adopts the *hypothesis-vs-oracle re-execution* pattern (narrow doctrine broadens beyond `/audit`-only), OR (2) an explicit narrative-work mandate is opened by the maintainer for a future cycle | 7-week skill-addition history (4-skill burst 2026-03-31 → 2026-04-06, then 6-week plateau as of 2026-05-20) is too short to choose between narrow doctrine (`/audit`-unique pattern → drop) and broad doctrine (verify-before-completing family across 3 skills → ship as meta-contract). The observation data-capture mechanism for skill-addition cadence and pattern adoption is also undesigned — relies on manual fact-check today. Designing that mechanism is itself a separate future task. |
| Symbol-density / rationale-sparsity advisory | Real user CLAUDE.md evidence shows opaque-code / rationale-sparse files causing audit pain | Named as a guide principle (claude-md-guide §Pruning); a non-scoring `/audit` advisory was considered and deferred — overlaps existing LAV L3-L6 and risks false positives on terse-but-correct style |
| `/secure` adversarial fixtures | A second `/secure` correctness defect escapes the happy-path `t7_secure_*` fixtures | `ci/scripts/t7_secure_*` cover happy-path state only; adversarial cases (wildcard allow, `bypassPermissions`, malformed `.mcp.json`, placeholder-vs-literal secret) are sound but unbuilt — no observed escape yet |
| `/audit` self-checks framed as adversarial-robustness | A Trustworthy Agents guide rework touches the self-audit section for another reason | `/audit` already ships self-defenses (install-integrity abort, Phase 3.7 oracle, state-summary tamper detection); framing them as "don't trust your own assurance apparatus" is additive doc-only, no pain driving it |
| Recommendation dedup lint + `/create` variant knobs | Conflicting/duplicate recommendation IDs surface across `/audit`, `/secure`, `/optimize`, OR `/create` variant choices prove hard to maintain as prose | Cross-skill recommendation consistency may already be partly covered by `check-recommendation-registry.py` (verify overlap before building); `/create` variant-knob refactor is speculative without maintenance pain |

## Propose a Change

Have an idea or suggestion for this roadmap?

1. Open a new discussion in [GitHub Discussions](https://github.com/wlsgur073/Guardians-of-the-Claude/discussions)
2. Describe your idea and why it would help
3. The community discusses, then the maintainer decides

Every decision (accept or decline) will include a comment explaining the reasoning.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contribution process.
