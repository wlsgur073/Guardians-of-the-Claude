---
title: "Model Drift Rules"
description: "4-axis capability fingerprint + normalization table for Claude model ID detection across Anthropic, Bedrock, and Vertex. Drives /audit drift advisory via normalize_model_id → fingerprint | null."
version: "1.0.0"
fingerprint_space_version: "1.0.0"
---

# Model Drift Rules

## Architecture

`normalize_model_id` transforms a raw model ID string (provider-specific format) into a canonical 4-axis fingerprint, or `null` for unrecognized input. The fingerprint feeds the drift advisory state machine: a non-null return is compared against the stored baseline fingerprint; `null` drives the state machine to `normalization_null` (one of the silence conditions, suppressing the drift advisory).

**Signature**:

```
normalize_model_id(model_id: string) → fingerprint | null
```

**Role in drift SM**: this file is the normalization table authority. The algorithm specification carries the 5 behavior contracts (see § Behavior Contracts below). The two sources do not duplicate each other.

**Fingerprint space version**: `1.0.0` — any axis addition or per-axis enumeration extension that alters drift-comparison semantics increments this version independently of the file `version` field.

## 4-Axis Fingerprint Schema

The fingerprint is a record with exactly 4 axes. Axis naming, ordering, and closed enumeration sets are specified by the fingerprint space.

### family_tier

Identifies the capability tier of the Claude model family.

| Value | Meaning |
|---|---|
| `opus` | High-capability tier — maximum reasoning depth, largest context options |
| `sonnet` | Mid-capability tier — balanced performance and throughput |
| `haiku` | Fast tier — optimized for latency-sensitive workloads |

**Enumeration** (closed): `{opus, sonnet, haiku}`

### context_window_class

Classifies the effective context window available to the model.

| Value | Meaning |
|---|---|
| `200k` | 200 000-token context window |
| `1M` | 1 000 000-token (1M) context window |

**Enumeration** (closed): `{200k, 1M}`

### reasoning_class

Classifies the extended-reasoning capability of the model.

| Value | Meaning |
|---|---|
| `none` | Standard inference only — no extended reasoning / thinking mode |
| `extended_any` | Extended reasoning supported (thinking blocks enabled via API) |

**Enumeration** (closed): `{none, extended_any}`

### context_management_class

Classifies how the model handles long-context management.

| Value | Meaning |
|---|---|
| `manual` | Manual context management — no native compaction support |
| `compaction_capable` | Native compaction support available (Claude Code compaction algorithm) |

**Enumeration** (closed): `{manual, compaction_capable}`

## 24-Combo Enumeration

All 24 valid fingerprint combinations from the fingerprint space (3 × 2 × 2 × 2 = 24). Every fingerprint returned by `normalize_model_id` (non-null branch) MUST hold an in-set value at every axis; tuples with out-of-set values return `null` instead.

| # | family_tier | context_window_class | reasoning_class | context_management_class |
|---|---|---|---|---|
| 1 | `opus` | `200k` | `none` | `manual` |
| 2 | `opus` | `200k` | `none` | `compaction_capable` |
| 3 | `opus` | `200k` | `extended_any` | `manual` |
| 4 | `opus` | `200k` | `extended_any` | `compaction_capable` |
| 5 | `opus` | `1M` | `none` | `manual` |
| 6 | `opus` | `1M` | `none` | `compaction_capable` |
| 7 | `opus` | `1M` | `extended_any` | `manual` |
| 8 | `opus` | `1M` | `extended_any` | `compaction_capable` |
| 9 | `sonnet` | `200k` | `none` | `manual` |
| 10 | `sonnet` | `200k` | `none` | `compaction_capable` |
| 11 | `sonnet` | `200k` | `extended_any` | `manual` |
| 12 | `sonnet` | `200k` | `extended_any` | `compaction_capable` |
| 13 | `sonnet` | `1M` | `none` | `manual` |
| 14 | `sonnet` | `1M` | `none` | `compaction_capable` |
| 15 | `sonnet` | `1M` | `extended_any` | `manual` |
| 16 | `sonnet` | `1M` | `extended_any` | `compaction_capable` |
| 17 | `haiku` | `200k` | `none` | `manual` |
| 18 | `haiku` | `200k` | `none` | `compaction_capable` |
| 19 | `haiku` | `200k` | `extended_any` | `manual` |
| 20 | `haiku` | `200k` | `extended_any` | `compaction_capable` |
| 21 | `haiku` | `1M` | `none` | `manual` |
| 22 | `haiku` | `1M` | `none` | `compaction_capable` |
| 23 | `haiku` | `1M` | `extended_any` | `manual` |
| 24 | `haiku` | `1M` | `extended_any` | `compaction_capable` |

Not all 24 combinations are currently occupied by known model IDs. Unoccupied combinations remain valid fingerprint tuples (representable) but produce `null` from the normalization table if no matching raw pattern exists.

## Provider Coverage

Three providers are covered: **Anthropic**, **Bedrock**, and **Vertex**.

### Anthropic

Model IDs use the form `claude-{family}-{major}-{minor}` — no provider prefix. Pattern family: prefix `claude-` followed by family name.

Examples: `claude-opus-4-7`, `claude-sonnet-4-6`, `claude-haiku-4-5`

### Bedrock

Model IDs are prefixed with `anthropic.` — e.g., `anthropic.claude-{family}-{major}-{minor}`. The `anthropic.` prefix is stripped during normalization; the remainder follows the Anthropic pattern family.

Examples: `anthropic.claude-opus-4-6`, `anthropic.claude-sonnet-4-6`

### Vertex

Model IDs use a date-version suffix: `claude-{family}-{major}-{minor}@{YYYYMMDD}`. The `@YYYYMMDD` suffix is stripped during normalization; the remainder follows the Anthropic pattern family. Note: context window class for Vertex model IDs may differ from the Anthropic-direct equivalent (see Normalization Table).

Examples: `claude-opus-4-6@20241022`, `claude-sonnet-4-6@20240901`

## Normalization Table

Raw pattern → normalized ID → 4-axis fingerprint. Evidence-status column: `observed` / `hypothesized` / `extrapolated` (see Evidence Status Labels). Only `observed` rows are active in v2.12.0.

Matching policy: longest-match when multiple rules overlap (per the matching-policy contract below). The `raw_pattern` column uses suffix-wildcard notation: `claude-opus-4-7*` matches `claude-opus-4-7` and any trailing date-less variant (e.g., `-latest`).

| raw_pattern | normalized_id | family_tier | context_window_class | reasoning_class | context_management_class | evidence_status |
|---|---|---|---|---|---|---|
| `claude-opus-4-7@*` | `opus-4.7-vertex` | `opus` | `1M` | `extended_any` | `compaction_capable` | `observed` |
| `claude-opus-4-7*` | `opus-4.7-anthropic` | `opus` | `1M` | `extended_any` | `compaction_capable` | `observed` |
| `anthropic.claude-opus-4-7*` | `opus-4.7-bedrock` | `opus` | `1M` | `extended_any` | `compaction_capable` | `observed` |
| `claude-opus-4-6@*` | `opus-4.6-vertex` | `opus` | `1M` | `extended_any` | `compaction_capable` | `observed` |
| `claude-opus-4-6*` | `opus-4.6-anthropic` | `opus` | `1M` | `extended_any` | `compaction_capable` | `observed` |
| `anthropic.claude-opus-4-6*` | `opus-4.6-bedrock` | `opus` | `1M` | `extended_any` | `compaction_capable` | `observed` |
| `claude-sonnet-4-6@*` | `sonnet-4.6-vertex` | `sonnet` | `1M` | `extended_any` | `compaction_capable` | `observed` |
| `claude-sonnet-4-6*` | `sonnet-4.6-anthropic` | `sonnet` | `1M` | `extended_any` | `compaction_capable` | `observed` |
| `anthropic.claude-sonnet-4-6*` | `sonnet-4.6-bedrock` | `sonnet` | `200k` | `extended_any` | `compaction_capable` | `observed` |
| `claude-sonnet-4-5@*` | `sonnet-4.5-vertex` | `sonnet` | `1M` | `extended_any` | `compaction_capable` | `observed` |
| `claude-sonnet-4-5*` | `sonnet-4.5-anthropic` | `sonnet` | `1M` | `extended_any` | `compaction_capable` | `observed` |
| `anthropic.claude-sonnet-4-5*` | `sonnet-4.5-bedrock` | `sonnet` | `200k` | `extended_any` | `compaction_capable` | `observed` |
| `claude-haiku-4-5@*` | `haiku-4.5-vertex` | `haiku` | `200k` | `extended_any` | `compaction_capable` | `observed` |
| `claude-haiku-4-5*` | `haiku-4.5-anthropic` | `haiku` | `200k` | `extended_any` | `compaction_capable` | `observed` |
| `anthropic.claude-haiku-4-5*` | `haiku-4.5-bedrock` | `haiku` | `200k` | `extended_any` | `compaction_capable` | `observed` |

**Table notes**:

- Bedrock rows (`anthropic.claude-*`) MUST be matched before Anthropic-direct rows (`claude-*`) to prevent the shorter Anthropic pattern from matching a Bedrock prefix. Longest-match ordering in the runner handles this automatically.
- Vertex rows (`claude-*@*`) MUST be matched before Anthropic-direct rows (`claude-*`) since the `@` suffix distinguishes them. Longest-match ordering handles this.
- All three `claude-opus-4-6` variants (Anthropic direct, Bedrock, Vertex) normalize to `1M` context as of 2026-04-20. Prior table revisions modeled Bedrock as `200k`; Bedrock has since upgraded Opus 4.6 to 1M per the AWS model card, and the table is aligned to current provider reality.
- **Sonnet 4.5 transitional state (as of 2026-04-20)**: Anthropic-direct (`claude-sonnet-4-5*`) and Vertex (`claude-sonnet-4-5@*`) currently serve Sonnet 4.5 at `1M` context via beta/preview; Anthropic's 1M beta retires April 30, 2026 per public release notes. Post-retirement, the Anthropic-direct row will drop to `200k` (alongside Bedrock, which is `200k` from launch). A patch release aligned to the retirement date will update the Anthropic (and possibly Vertex) rows. As of 2026-04-20 all three Sonnet 4.5 rows are `observed`; evidence: AWS Claude Sonnet 4.5 model card (Bedrock), Vertex Claude Sonnet 4.5 model card (Vertex GA), Anthropic release notes (1M beta retirement).

## Evidence Status Labels

### observed

Directly verified against Anthropic, Bedrock, or Vertex public documentation or official model capability announcements. **Active by default in v2.12.0** — these rows drive normalization output.

### hypothesized

Inferred from pattern-matching adjacent observed entries; flagged for future verification against primary sources. **NOT active** per the evidence-hygiene requirement. Rows with this status are excluded from normalization output until promoted to `observed`.

### extrapolated

Extended from adjacent observed patterns with lowest confidence; requires independent primary-source verification before activation. **NOT active**. Subject to removal if primary sources contradict the extrapolation.

## Non-Covered Providers

### Microsoft Foundry

Microsoft Foundry was evaluated for inclusion in the normalization provider set and dropped during design closure (2026-04-18). Rationale: Foundry uses operator-chosen deployment names rather than provider-stable model IDs, making normalization infeasible without an additional deployment-naming convention contract. Any Foundry deployment-name input returns `null` from the fail-safe semantics; the `/audit` drift advisory is suppressed via the `normalization_null` silence condition.

**Future Foundry patch**: if a Foundry deployment-naming convention emerges (enabling stable model ID inference), a future patch release may add Foundry to the provider set. Such an extension would shift previously-`null` Foundry IDs to `match`/`drift` state — a contract-significant change requiring contract-extension review.

### Future / Unknown Providers

Unrecognized provider prefixes and ID formats not matching any in-set provider's pattern family return `null` from the function's fail-safe. No advisory is emitted. Pattern families for future providers may be added to this table without altering existing row semantics (additive extension).

## Behavior Contracts

`normalize_model_id` behavior is specified by 5 contracts:

1. **Totality** — every string input produces either a fingerprint or `null`; no exceptions, no partial records.
2. **Canonicalization** — non-null return holds canonical axis values only; no raw provider tokens in output.
3. **Fail-safe `null`** — unrecognized patterns, unparseable formats within a matched family, and out-of-fingerprint-space combinations all return `null`.
4. **Matching policy** — longest-match across overlapping rules; absent rule → contract #3 first condition.
5. **Determinism / pure** — same input → same output within a scoring-contract version; no I/O, no state, no randomness.

This file provides the normalization table and evidence-status metadata consumed by `normalize_model_id`'s implementation. The algorithm specification is the authority; do not re-specify algorithm logic here.
