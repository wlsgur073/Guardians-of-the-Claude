---
title: "Model Drift Rules"
description: "4-axis capability fingerprint + normalization table for Claude model ID detection across Anthropic, Bedrock, and Vertex. Drives /audit drift advisory via normalize_model_id → fingerprint | null."
version: "1.5.0"
fingerprint_space_version: "1.1.0"
---

# Model Drift Rules

## Architecture

`normalize_model_id` transforms a raw model ID string (provider-specific format) into a canonical 4-axis fingerprint, or `null` for unrecognized input. The fingerprint feeds the drift advisory state machine: a non-null return is compared against the stored baseline fingerprint; `null` drives the state machine to `normalization_null` (one of the silence conditions, suppressing the drift advisory).

**Signature**:

```
normalize_model_id(model_id: string) → fingerprint | null
```

**Role in drift SM**: this file is the normalization table authority. The algorithm specification carries the 5 behavior contracts (see § Behavior Contracts below). The two sources do not duplicate each other.

**Fingerprint space version**: `1.1.0` — any axis addition or per-axis enumeration extension that alters drift-comparison semantics increments this version independently of the file `version` field. (1.0.0 → 1.1.0: `family_tier` enumeration extended with `fable`; purely additive — every 1.0.0 fingerprint remains valid and compares unchanged.)

## 4-Axis Fingerprint Schema

The fingerprint is a record with exactly 4 axes. Axis naming, ordering, and closed enumeration sets are specified by the fingerprint space.

### family_tier

Identifies the capability tier of the Claude model family.

| Value | Meaning |
|---|---|
| `opus` | High-capability tier — deep reasoning, largest context options (topped by `fable` since fingerprint space 1.1.0) |
| `sonnet` | Mid-capability tier — balanced performance and throughput |
| `haiku` | Fast tier — optimized for latency-sensitive workloads |
| `fable` | Frontier tier — above `opus` in capability (Claude Fable 5 / 5.1 line; added in fingerprint space 1.1.0) |

**Enumeration** (closed): `{opus, sonnet, haiku, fable}`

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

## 32-Combo Enumeration

All 32 valid fingerprint combinations from the fingerprint space (4 × 2 × 2 × 2 = 32). Every fingerprint returned by `normalize_model_id` (non-null branch) MUST hold an in-set value at every axis; tuples with out-of-set values return `null` instead. Combos 1–24 are unchanged from fingerprint space 1.0.0; combos 25–32 were added with the `fable` family tier in 1.1.0.

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
| 25 | `fable` | `200k` | `none` | `manual` |
| 26 | `fable` | `200k` | `none` | `compaction_capable` |
| 27 | `fable` | `200k` | `extended_any` | `manual` |
| 28 | `fable` | `200k` | `extended_any` | `compaction_capable` |
| 29 | `fable` | `1M` | `none` | `manual` |
| 30 | `fable` | `1M` | `none` | `compaction_capable` |
| 31 | `fable` | `1M` | `extended_any` | `manual` |
| 32 | `fable` | `1M` | `extended_any` | `compaction_capable` |

Not all 32 combinations are currently occupied by known model IDs. Unoccupied combinations remain valid fingerprint tuples (representable) but produce `null` from the normalization table if no matching raw pattern exists.

## Provider Coverage

Three providers are covered: **Anthropic**, **Bedrock**, and **Vertex**.

### Anthropic

Model IDs use the form `claude-{family}-{major}[-{minor}]` — no provider prefix; the minor segment is absent on the dateless `.0` releases of the Claude 5 generation (`claude-opus-5`, `claude-sonnet-5`, `claude-fable-5`). Pattern family: prefix `claude-` followed by family name.

Examples: `claude-fable-5-1`, `claude-opus-5`, `claude-sonnet-5`, `claude-haiku-4-5` (current); `claude-opus-4-8`, `claude-sonnet-4-6` (legacy)

### Bedrock

Model IDs are prefixed with `anthropic.` — e.g., `anthropic.claude-{family}-{major}[-{minor}]`. The `anthropic.` prefix is stripped during normalization; the remainder follows the Anthropic pattern family (minor segment optional as above).

Examples: `anthropic.claude-fable-5-1`, `anthropic.claude-opus-5`, `anthropic.claude-sonnet-4-6`

### Vertex

Dated-snapshot model IDs use a date-version suffix: `claude-{family}-{major}-{minor}@{YYYYMMDD}`. The `@YYYYMMDD` suffix is stripped during normalization; the remainder follows the Anthropic pattern family. Note: a dated-snapshot row may carry its own context window class because Google Cloud sets lifecycle and context independently — as of 2026-09-08 the Sonnet 4.5 row does (Google still offers the 1M Preview that the Anthropic API retired; see Normalization Table). **Every model from the 4.6 generation on (Opus 4.6+, Sonnet 4.6+, the Claude 5 family) uses the bare first-party ID with no `@` suffix on Google Cloud**, so those are matched by the Anthropic-direct patterns — pattern-indistinguishable by design (see Table notes). Dated `@YYYYMMDD` IDs exist only for the 4.5 generation and earlier (Sonnet 4.5, Opus 4.5, Haiku 4.5, and older models); the table registers `@*` rows only for Sonnet 4.5 and Haiku 4.5.

Examples: `claude-sonnet-4-5@20250929`, `claude-haiku-4-5@20251001` (dated snapshots); `claude-fable-5-1`, `claude-opus-5` (current-generation, bare)

## Normalization Table

Raw pattern → normalized ID → 4-axis fingerprint. Evidence-status column: `observed` / `hypothesized` / `extrapolated` (see Evidence Status Labels). Only `observed` rows are active in v2.12.0. Lifecycle column: `current` / `legacy` (see Lifecycle Status Labels) — orthogonal to evidence status and never deactivates a row.

Matching policy: longest-match when multiple rules overlap (per the matching-policy contract below). The `raw_pattern` column uses suffix-wildcard notation: `claude-opus-4-7*` matches `claude-opus-4-7` and any trailing date-less variant (e.g., `-latest`).

| raw_pattern | normalized_id | family_tier | context_window_class | reasoning_class | context_management_class | lifecycle | evidence_status |
|---|---|---|---|---|---|---|---|
| `claude-fable-5-1*` | `fable-5.1-anthropic` | `fable` | `1M` | `extended_any` | `compaction_capable` | `current` | `observed` |
| `anthropic.claude-fable-5-1*` | `fable-5.1-bedrock` | `fable` | `1M` | `extended_any` | `compaction_capable` | `current` | `observed` |
| `claude-fable-5*` | `fable-5-anthropic` | `fable` | `1M` | `extended_any` | `compaction_capable` | `legacy` | `observed` |
| `anthropic.claude-fable-5*` | `fable-5-bedrock` | `fable` | `1M` | `extended_any` | `compaction_capable` | `legacy` | `observed` |
| `claude-opus-5*` | `opus-5-anthropic` | `opus` | `1M` | `extended_any` | `compaction_capable` | `current` | `observed` |
| `anthropic.claude-opus-5*` | `opus-5-bedrock` | `opus` | `1M` | `extended_any` | `compaction_capable` | `current` | `observed` |
| `claude-opus-4-8*` | `opus-4.8-anthropic` | `opus` | `1M` | `extended_any` | `compaction_capable` | `legacy` | `observed` |
| `anthropic.claude-opus-4-8*` | `opus-4.8-bedrock` | `opus` | `1M` | `extended_any` | `compaction_capable` | `legacy` | `observed` |
| `claude-opus-4-7*` | `opus-4.7-anthropic` | `opus` | `1M` | `extended_any` | `compaction_capable` | `legacy` | `observed` |
| `anthropic.claude-opus-4-7*` | `opus-4.7-bedrock` | `opus` | `1M` | `extended_any` | `compaction_capable` | `legacy` | `observed` |
| `claude-opus-4-6*` | `opus-4.6-anthropic` | `opus` | `1M` | `extended_any` | `compaction_capable` | `legacy` | `observed` |
| `anthropic.claude-opus-4-6*` | `opus-4.6-bedrock` | `opus` | `1M` | `extended_any` | `compaction_capable` | `legacy` | `observed` |
| `claude-sonnet-5*` | `sonnet-5-anthropic` | `sonnet` | `1M` | `extended_any` | `compaction_capable` | `current` | `observed` |
| `anthropic.claude-sonnet-5*` | `sonnet-5-bedrock` | `sonnet` | `1M` | `extended_any` | `compaction_capable` | `current` | `observed` |
| `claude-sonnet-4-6*` | `sonnet-4.6-anthropic` | `sonnet` | `1M` | `extended_any` | `compaction_capable` | `legacy` | `observed` |
| `anthropic.claude-sonnet-4-6*` | `sonnet-4.6-bedrock` | `sonnet` | `1M` | `extended_any` | `compaction_capable` | `legacy` | `observed` |
| `claude-sonnet-4-5@*` | `sonnet-4.5-vertex` | `sonnet` | `1M` | `extended_any` | `compaction_capable` | `legacy` | `observed` |
| `claude-sonnet-4-5*` | `sonnet-4.5-anthropic` | `sonnet` | `200k` | `extended_any` | `compaction_capable` | `legacy` | `observed` |
| `anthropic.claude-sonnet-4-5*` | `sonnet-4.5-bedrock` | `sonnet` | `200k` | `extended_any` | `compaction_capable` | `legacy` | `observed` |
| `claude-haiku-4-5@*` | `haiku-4.5-vertex` | `haiku` | `200k` | `extended_any` | `compaction_capable` | `current` | `observed` |
| `claude-haiku-4-5*` | `haiku-4.5-anthropic` | `haiku` | `200k` | `extended_any` | `compaction_capable` | `current` | `observed` |
| `anthropic.claude-haiku-4-5*` | `haiku-4.5-bedrock` | `haiku` | `200k` | `extended_any` | `compaction_capable` | `current` | `observed` |

**Table notes**:

- Bedrock rows (`anthropic.claude-*`) MUST be matched before Anthropic-direct rows (`claude-*`) to prevent the shorter Anthropic pattern from matching a Bedrock prefix. Longest-match ordering in the runner handles this automatically.
- Vertex rows (`claude-*@*`) MUST be matched before Anthropic-direct rows (`claude-*`) since the `@` suffix distinguishes them. Longest-match ordering handles this.
- **Claude 5 family (Opus 5, Sonnet 5; added 2026-08-10)**: Sonnet 5 shipped 2026-06-30 (date corrected 2026-09-08 from the catalog's release/retirement record), Opus 5 2026-07-24. Both normalize to `1M` on Anthropic-direct and Bedrock. Evidence: Anthropic model catalog (both models "1M context window, 128K max output"), Anthropic Bedrock docs context-window statement ("Claude Fable 5.1, Claude Fable 5, Claude Opus 5, Claude Opus 4.8, Claude Opus 4.7, Claude Opus 4.6, Claude Sonnet 5, and Claude Sonnet 4.6 have a 1M-token context window on Amazon Bedrock" — wording as re-verified 2026-09-08; the Google Cloud page carries the same list).
- **No Vertex (`@*`) rows from the 4.6 generation on**: Opus 4.6+, Sonnet 4.6+, and the Claude 5 family use the **bare first-party ID** on Google Cloud (no `@YYYYMMDD` suffix), so the Anthropic-direct patterns (`claude-fable-5-1*`, `claude-fable-5*`, `claude-opus-5*`, `claude-sonnet-5*`, `claude-opus-4-8*`, `claude-opus-4-7*`, `claude-opus-4-6*`, `claude-sonnet-4-6*`) also match Google Cloud usage — a separate Vertex row is unrepresentable by pattern, and the former `claude-opus-4-7@*` / `claude-opus-4-6@*` / `claude-sonnet-4-6@*` rows were removed on 2026-09-08 as ID shapes that never shipped (a dated input still normalizes through the wildcard row to the same fingerprint). The `@*` rows remain only for Sonnet 4.5 and Haiku 4.5 — dated Google Cloud IDs exist for the 4.5 generation and earlier (Opus 4.5 too, but it has no row). Evidence: Anthropic model catalog ("every Claude model ID is a pinned snapshot, including the dateless IDs used from the 4.6 generation on"), Anthropic's Google Cloud model-ID table (bare `claude-opus-4-7`, `claude-opus-4-6`, `claude-sonnet-4-6`; dated `claude-sonnet-4-5@20250929`, `claude-haiku-4-5@20251001`), Anthropic SDK Vertex client docs.
- **Claude Fable 5 (registered with fingerprint space 1.1.0)**: the `fable` family tier was added as a purely additive enumeration extension — no 1.0.0 fingerprint changes meaning, and stored baselines compare unchanged. Both variants normalize to `1M`. Evidence: Anthropic model catalog (Fable 5 "1M context window, 128K max output"; adaptive thinking always on; compaction supported) for Anthropic-direct, and the Bedrock docs context-window statement above (which names Claude Fable 5 explicitly) for Bedrock. As with the rest of the Claude 5 family, Vertex current-generation usage is matched by the bare Anthropic-direct pattern. **Relabeled `legacy` 2026-09-08**: once Fable 5.1 shipped, the catalog moved Fable 5 to its Legacy-models list (still available; retirement not sooner than 2027-06-09) — recognition and normalization output are unchanged.
- **Claude Fable 5.1 (released 2026-09-01; rows added 2026-09-08)**: `claude-fable-5-1` / `anthropic.claude-fable-5-1` normalize to `fable` / `1M` / `extended_any` / `compaction_capable` — the same fingerprint as Fable 5, so a Fable 5 → Fable 5.1 upgrade is *not* reported as drift (the advisory compares fingerprints, not IDs). Longest-match routes `claude-fable-5-1` to its own row rather than the shorter `claude-fable-5*` wildcard. Google Cloud, Microsoft Foundry, and Claude Platform on AWS all expose the bare first-party ID `claude-fable-5-1`, so those are matched by the Anthropic-direct row. Fable 5.1 and Mythos 5.1 are the same model under different safeguards; Mythos IDs are limited-availability and intentionally unregistered (fail-safe `null`). Evidence: Anthropic model catalog (Fable 5.1 "1M context window, 128K max output"; adaptive thinking always on), Bedrock and Google Cloud docs context-window statements (both name Claude Fable 5.1), Claude Code model-config docs (`fable` alias resolves to Fable 5.1 from v2.1.255).
- **Sonnet 4.6 Bedrock upgraded to `1M` (as of 2026-08-10 verification)**: prior table revisions modeled `anthropic.claude-sonnet-4-6*` as `200k`; Anthropic's Bedrock docs now list Sonnet 4.6 among the 1M-context models on Bedrock (same upgrade pattern as Opus 4.6 Bedrock, note below). Evidence: Anthropic Bedrock docs context-window statement.
- **Opus 4.8 (released 2026-05-28; provider set re-verified 2026-08-10)**: both rows normalize to `1M` context, and the fingerprint holds on all three providers. Bedrock ID is `anthropic.claude-opus-4-8` (no ARN version suffix, per the AWS model card). On Google Cloud (current docs brand the offering "Agent Platform", formerly Vertex AI), Opus 4.8 is exposed with the **bare first-party ID** `claude-opus-4-8` — no `@YYYYMMDD` form ever shipped for it — so Google Cloud usage is matched by the Anthropic-direct pattern exactly as with the Claude 5 family; a former `@*` parity row was removed as an ID shape that never existed (the Opus 4.7, Opus 4.6, and Sonnet 4.6 `@*` rows followed on 2026-09-08 for the same reason). Newer models on Google Cloud are served via global and multi-region endpoints only. Evidence: Anthropic Claude-on-Google-Cloud model-ID table and context-window statement, AWS Claude Opus 4.8 model card (Bedrock).
- **Lifecycle relabels (2026-08-10)**: Anthropic's model catalog now lists Opus 4.8, Opus 4.7, Opus 4.6, and Sonnet 4.6 in its **Legacy models** table ("still available … consider migrating" — distinct from retired). The corresponding rows are relabeled `legacy`; per the Lifecycle Status Labels contract this changes advisory wording only — recognition and normalization output are unchanged. Fable 5 followed on 2026-09-08 (see the Fable 5 note above).
- Both `claude-opus-4-6` variants (Anthropic direct — which also covers the bare Google Cloud ID — and Bedrock) normalize to `1M` context as of 2026-04-20. Prior table revisions modeled Bedrock as `200k`; Bedrock has since upgraded Opus 4.6 to 1M per the AWS model card, and the table is aligned to current provider reality.
- **Sonnet 4.5 post-retirement (as of 2026-04-30; Google Cloud re-verified 2026-09-08)**: Anthropic-direct (`claude-sonnet-4-5*`) is `200k` — the `context-1m-2025-08-07` beta retired on April 30, 2026 per Anthropic release notes; requests exceeding 200k now return an error. Bedrock (`anthropic.claude-sonnet-4-5*`) was `200k` from launch. Google Cloud (`claude-sonnet-4-5@*`) stays `1M observed`: Google's Sonnet 4.5 model card still lists "Maximum input tokens: 1M (Preview), 200,000 (GA)", and this table counts a provider preview until the provider retires it (the same rule that kept Anthropic-direct at `1M` until 2026-04-30). Anthropic's own Google Cloud page lists Sonnet 4.5 among the 200k-context models on Agent Platform — that statement describes the GA limit; if Google retires the Preview, flip this row to `200k` and update the t3 fixture. For 1M context without a preview, migrate to a current model — Sonnet 5, Opus 5, or Fable 5.1 (all 1M by default, no beta header). Evidence: AWS Claude Sonnet 4.5 model card (Bedrock), Google Cloud Claude Sonnet 4.5 model card (1M Preview / 200k GA, read 2026-09-08), Anthropic Claude-on-Google-Cloud context-window statement, Anthropic release notes 2026-04-30 (1M beta retirement).

## Evidence Status Labels

### observed

Directly verified against Anthropic, Bedrock, or Vertex public documentation or official model capability announcements. **Active by default in v2.12.0** — these rows drive normalization output.

### hypothesized

Inferred from pattern-matching adjacent observed entries; flagged for future verification against primary sources. **NOT active** per the evidence-hygiene requirement. Rows with this status are excluded from normalization output until promoted to `observed`.

### extrapolated

Extended from adjacent observed patterns with lowest confidence; requires independent primary-source verification before activation. **NOT active**. Subject to removal if primary sources contradict the extrapolation.

## Lifecycle Status Labels

The `lifecycle` column is orthogonal to evidence status: evidence status says how well-sourced a row is; lifecycle says where the model stands in the vendor lineup. Both `current` and `legacy` rows are **active recognition entries** — a legacy row still normalizes, because the table's function is to recognize model IDs that exist in real user configs, not to endorse them.

### current

The vendor's model catalog lists the model in its **current** (recommended) section. Multiple generations can be current at once — the label follows the vendor's own catalog placement, not release recency. No advisory beyond normal drift handling.

### legacy

The vendor's model catalog lists the model outside its current section (legacy, deprecated, or retiring). The model is still served and the row still normalizes; when `/audit` surfaces a legacy-model configuration, its advice SHOULD note that a current-generation model is available and recommend evaluating a migration. Legacy rows are never deleted while the ID remains recognizable in the wild — deleting them would silently disable recognition for exactly the configurations that most need the migration advice.

## Non-Covered Providers

### Microsoft Foundry

Microsoft Foundry was evaluated for inclusion in the normalization provider set and dropped during design closure (2026-04-18): what a Foundry request sends is an operator-chosen deployment name, not a provider-stable model ID, so Foundry has no pattern family of its own. Revisited 2026-09-08: Foundry deployments now *default* to the first-party model ID as the deployment name (e.g. `claude-fable-5-1`, `claude-opus-5`, `claude-opus-4-6` — per Anthropic's model catalog), and such a name is matched by the Anthropic-direct rows like any other bare ID. Only a deployment name that does not carry the model ID returns `null` from the fail-safe semantics; for those the `/audit` drift advisory is suppressed via the `normalization_null` silence condition.

**Future Foundry patch**: if Foundry ever exposes a stable, ID-bearing convention for renamed deployments (enabling model-ID inference from the name), a future patch release may add Foundry to the provider set. Such an extension would shift previously-`null` Foundry names to `match`/`drift` state — a contract-significant change requiring contract-extension review.

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
