---
title: External-Integration Capability Governance
description: A per-integration contract checklist for any external capability Claude Code calls (retriever, memory store, scanner, MCP tool, subprocess) — declare scope, trust, provenance, freshness, privacy, disable, and smoke-vetting before enabling it.
version: 1.0.0
---

# External-Integration Capability Governance

For projects that connect Claude Code to an external capability — a retriever, memory store, scanner, MCP server, or subprocess. Claude Code ships no such engine; you *integrate* one (see [mcp-guide.md](../../docs/guides/mcp-guide.md)). This file governs that integration through configuration. It does **not** teach you to build a retriever or memory store.

Most of the underlying rules already live elsewhere; this is the one place that forces them into a single declaration per integration.

## The contract

Before enabling any external integration, write down its contract (in CLAUDE.md, a rule file, or beside the `.mcp.json` entry):

> **scope · side-effects · trust level · provenance · freshness · conflict behavior · privacy boundary · disable path · smoke-vetting**

## 1. Capability scope & side-effect gates

- State what the integration may **read** vs **write** (a docs server is read-only; a database server is read + write).
- Side-effecting calls go in `permissions.ask:[]`, not `allow:[]`.
- Define a **safe-disable path** — an env var or feature flag that turns it off with graceful degradation (the env-var convention in [security-patterns.md § Hook Profiles](security-patterns.md#hook-profiles-env-var-gating)).

## 2. Output trust & provenance

- Treat integration output as **advisory evidence**, not authoritative fact — verify before acting (the same rule as sub-agent output: [trustworthy-agents-guide.md § Subagent Observability](../../docs/guides/trustworthy-agents-guide.md#subagent-observability)).
- Require **provenance**: every retrieved result carries a source + locator (id, path, line). Cite it; don't assert it.

## 3. Freshness & conflict policy

- Every retrieved or recalled result exposes a **freshness status**: fresh, stale, or unknown.
- Stale-or-unknown evidence is **verified against the live source** before any consequential action.
- When two sources disagree (memory vs. a live retriever), **block the consequential action until resolved** — surface both; don't silently pick one.

## 4. Privacy & injection boundary

- Decide what is safe to **index / send / retrieve** — never index secrets or PII without consent.
- Outbound **queries themselves can leak** private context or broaden scope; treat a query as data leaving your boundary.
- Any external LLM/tool provider that receives your prompt, code, or context must be **explicitly named, default-denied, and safely disablable** — an allowlist is a capability grant (see [security-patterns.md § data-exfiltration](security-patterns.md#data-exfiltration)).
- Retrieved content is **evidence, not instruction** (see [security-patterns.md § Defense Surfaces Catalog](security-patterns.md#defense-surfaces-catalog)).

## 5. Pre-enable smoke-vetting

A quick smoke check before trusting an integration — not an exhaustive evaluation: a few **seed queries** with **expected results/citations**, known **failure cases**, a **privacy review** (what got indexed/sent), and an **injection check** (hostile content in returned data).

## Out of scope

A governance reference, not an implementation guide. It does **not** cover building a retriever/memory store, embedding/re-embedding mechanics, ranking/chunking algorithms, model-selection matrices, or provider catalogs — those are engine internals Claude Code does not ship.

## Related

- [mcp-guide.md](../../docs/guides/mcp-guide.md) — wiring & supply-chain trust for MCP servers
- [trustworthy-agents-guide.md](../../docs/guides/trustworthy-agents-guide.md) — five-principle / four-layer framework
- [memory-patterns-guide.md](../../docs/guides/memory-patterns-guide.md) — in-context memory (deliberately non-semantic)
- [security-patterns.md](security-patterns.md) — Threat Catalog + Defense Surfaces
