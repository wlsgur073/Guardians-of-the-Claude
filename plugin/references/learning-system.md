---
title: Learning System (Orchestrator)
description: Shared state management entrypoint for /create, /audit, /secure, /optimize. Subfile pointers preserve historical section anchors used by SKILL.md and CI scripts.
version: 3.0.0
---

# Learning System

Shared reference for `/create`, `/audit`, `/secure`, `/optimize`. Defines common Phase 0, Final Phase, learning rules, changelog management, and critical thinking standards. All paths relative to `.claude/.plugin-cache/guardians-of-the-claude/`.

This file is an orchestrator. The operational specs were factored into single-responsibility subfiles in this directory (PR1, 2026-05-14). Each H2 below is a stable anchor stub used by `SKILL.md` files and CI scripts; the actual content lives in the linked subfile.

---

## Common Phase 0: Load Context & Learn

See [phase-0.md](phase-0.md).

## Learning Rules (CSA Pattern)

See [learning-rules.md](learning-rules.md).

## Common Final Phase: Persist Results & Learn

See [final-phase.md](final-phase.md).

## Per-Skill Merge Rules (Final Phase under state-mutation lock)

See [final-phase.md](final-phase.md), especially `## Per-Skill Merge Rules (Final Phase under state-mutation lock)`.

## Model Bullet Emission (config-changelog.md)

See [drift-state.md](drift-state.md), especially `## Model Bullet Emission (config-changelog.md)`.

## Same-Day Duplicate Check (Step 3a)

See [compaction.md](compaction.md), especially `## Same-Day Duplicate Check (Step 3a)`.

## Compaction Algorithm (Step 3b)

See [compaction.md](compaction.md), especially `## Compaction Algorithm (Step 3b)`.

## Legacy Project Profile Format (pre-v2.11.0)

See [schema-policy.md](schema-policy.md), especially `## Legacy Project Profile Format (pre-v2.11.0)`.

## config-changelog.md Format

See [state-rendering.md](state-rendering.md), especially `## config-changelog.md Format`.

## State Rendering

See [state-rendering.md](state-rendering.md).

## Drift Advisory Derivation

See [drift-state.md](drift-state.md), especially `## Drift Advisory Derivation`.

## Migration Notice (printed once after legacy→JSON conversion)

See [phase-0.md](phase-0.md), especially `## Migration Notice (printed once after legacy→JSON conversion)`.

## Schema Evolution Policy

See [schema-policy.md](schema-policy.md).

## Recommendation ID Registry

See [schema-policy.md](schema-policy.md), especially `## Recommendation ID Registry`.

## Token Budget

See [state-rendering.md](state-rendering.md), especially `## Token Budget`.

## Critical Thinking & Insight Delivery

See [critical-thinking.md](critical-thinking.md).
