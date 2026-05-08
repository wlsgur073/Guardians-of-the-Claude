---
title: Distributed-Config Bucket Rubric
description: Bucket rubric for distributed-config monorepos — required conditions (with_claude_md >= 2 + monorepo type), 4 supporting signals (>=2 of {ratio, root compactness, subpackage actionability, verbose-prose-sparse-config exclusion}), exclusion conditions (excessive root, low-quality distribution), and advisory numeric guardrails. Classifies monorepos that distribute Claude Code configuration across sub-package CLAUDE.md files rather than centralizing in root.
version: 1.0.0
applies_to: audit-score-v4.1.0
---

# Distributed-Config Bucket Rubric

Distributed-config bucket captures monorepos where Claude Code configuration is split across multiple sub-package CLAUDE.md files rather than centralized in a single root CLAUDE.md. This pattern is common in mature monorepos with package-local engineering teams maintaining their own context.

## §0. Scope

Bucket name: `distributed_config` (added to bucket enum at `audit-score-v4.1.0`).

**Evaluation order** in `ci/scripts/check-audit-goldens.py` `classify_bucket_full()`:

1. Outlier short-circuits: `claude_md_lines > 250` OR `has_meta_marketplace=true`
2. Verbose-prose-sparse-config Outlier: `lines >= 200 AND rules+hooks+agents+mcp == 0`
3. **`distributed_config` (this document)** — applied here
4. Advanced / Intermediate / Starter / UNMATCHED (existing rubric branches)

Outlier paths take precedence. A profile classifying as Outlier never reaches the `distributed_config` check.

## §1. Required Conditions (ALL must hold)

For a profile to be considered for `distributed_config` classification:

1. `subpackage_coverage.with_claude_md >= 2` — at least 2 sub-packages have CLAUDE.md
2. `project_structure.type == "monorepo"` AND `monorepo_detection.detected == true`

If any required condition fails, the profile cannot classify as `distributed_config` and falls through to existing Advanced/Intermediate/Starter rubric branches.

## §2. Supporting Signals (>=2 of 4 must hold)

When required conditions hold, count supporting signals satisfied:

### §2.1 Distributed config ratio
`with_claude_md / package_roots_total >= 0.5`

Captures monorepos where at least half of declared sub-packages have CLAUDE.md, indicating intentional per-package documentation rather than incidental coverage.

### §2.2 Root CLAUDE.md compactness
`profile.claude_md_lines <= 150`

A compact root CLAUDE.md (<= 150 lines) suggests the project relies on sub-package CLAUDE.md for detailed context, rather than concentrating all guidance at root.

### §2.3 Subpackage-local actionability
`mean(subpackages[].lav_breakdown.L6) >= 0.5` over scored subpackages.

L6 (concrete commands per `lav.md`) measures whether sub-package CLAUDE.md files include concrete commands or paths. Average L6 ratio across scored subpackages reaching 0.5 indicates per-package actionability is the documentation pattern, not narrative-only prose.

### §2.4 Verbose-prose-sparse-config exclusion
`NOT (profile.claude_md_lines > 250 AND mechanical_config < 4)`

where `mechanical_config = rules_count + hooks_count + agents_count + mcp_count`.

This signal excludes profiles that consolidate all guidance into long root CLAUDE.md prose with minimal mechanical config — those match the verbose-prose-sparse-config Outlier rubric and should not also classify as distributed_config. Note: profiles satisfying the Outlier verbose-prose-sparse-config rubric never reach this signal because evaluation order short-circuits at step 2 above; this signal is a defense-in-depth check.

### Threshold
`signal_count >= 2` (out of 4 supporting signals).

## §3. Exclusion Conditions (ANY triggers fall-through)

Even when required conditions and >=2 supporting signals hold, the following exclusions force fall-through to existing rubric (most likely Advanced or Intermediate):

1. `profile.claude_md_lines > 1000` — excessive root CLAUDE.md indicates over-documentation, not distributed config
2. All scored subpackages have `final_score < 30` — low-quality distribution indicates configuration exists but is unhelpful

## §4. Numeric Guardrails (advisory, not absolute)

Typical distributed_config profiles:
- `with_claude_md ∈ [3, 20]` — too few suggests incidental coverage; too many suggests org-scale workspace beyond bucket scope
- `distributed_config_ratio ∈ [0.5, 1.0]` — below 0.5 fails the supporting signal; above 1.0 impossible by definition

Edge cases (e.g., ratio exactly 0.5, root claude_md_lines exactly 150) are within bucket scope. Document edge-case rationale in fixture `bucket_rationale` for review.

## §5. Validation Reference

Implemented in `ci/scripts/check-audit-goldens.py`:
- `classify_bucket_distributed(data: dict) -> bool` — applies §1 + §2 + §3 rubric, returns True iff profile matches
- `classify_bucket_full(data: dict) -> str` — orchestrator combining existing `classify_bucket(profile)` (Outlier short-circuits) with `classify_bucket_distributed(data)` per evaluation order in §0

Test fixtures classifying as `distributed_config` set `expected_bucket: "distributed_config"` and provide `bucket_rationale` text explaining required conditions met, supporting signal count, and any borderline values relative to §4 guardrails.
