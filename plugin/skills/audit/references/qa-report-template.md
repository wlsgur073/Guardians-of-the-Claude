---
title: "qa-report.md template"
description: "Section list + render rules for the post-audit qa-report.md artifact (self-versioned, sibling to canonical state files)"
version: "1.0.0"
---

# qa-report.md Render Template

`qa-report.md` is a post-audit transparency artifact written to `local/qa-report.md`. Sections 1-4 always render; Section 5 conditional per sprint-contract parser branches.

## Section List Invariance

`qa-report.md` section *content* adapts to audit data per the per-section rules below, but the section list itself is fixed in order. Forbidden by spec:

- Omitting any of sections 1-4.
- Reordering any section.
- Adding new top-level sections by audit input.

The only allowed section-list variation is Section 5: Sprint Contract Coverage, which renders if and only if the sprint-contract parser reaches B4 (valid) or B2 (frontmatter advisory). Otherwise omitted.

## Frontmatter (always emitted at top)

```yaml
---
title: "qa-report"
description: "Post-audit transparency artifact for <project> at <ISO-8601 timestamp>"
version: "1.0.0"
---
```

The version field is the qa-report artifact semver (independent from plugin version). Bump the artifact version when the section list or render contract changes — not on every audit.

## Section 1 — Score Summary (always)

Single-row table. Columns: Final, Bucket, DS, SB, LAV_nonL5, cap.

```markdown
## Score Summary

| Final | Bucket | DS | SB | LAV_nonL5 | cap |
|---|---|---|---|---|---|
| <Final> | <Bucket> | <DS> | <SB> | <LAV_nonL5> | <cap> |
```

## Section 2 — LAV Item Rationale (always)

6-row table, one row per L1-L6. Columns: Item, Score, Evidence cited, Counterfactual to next band.

```markdown
## LAV Item Rationale

| Item | Score | Evidence cited | Counterfactual to next band |
|---|---|---|---|
| L1 | <score> | <evidence> | <counterfactual or "—"> |
| L2 | ... |
| L3 | ... |
| L4 | ... |
| L5 | ... |
| L6 | ... |
```

**Counterfactual cell rules (S2 + I3 enforcement):**

- "Material" = next-band reach achievable by ONE piece of evidence (one of: H2/H3 ≤10 lines project-specific; named command + flags + path; correctly-named directory or file path; deduplicated bullet list or removed redundant section).
- "Immaterial" = next-band reach requires 2+ pieces. Render as `—` (em dash, no text).
- All-immaterial fallback: render single line under table — *"No material counterfactual deltas at this audit."* (table still rendered).
- Wording rule: hypothetical observation only. Use *"Score would reach +X if CLAUDE.md cited [evidence type]"*. NEVER *"Add X"* or *"Document Y"*.

## Section 3 — Bucket Rationale (always)

1-3 sentences citing the bucket-rubric path that produced the live classification. Reference the live classifier (`Final` and `Bucket` from Section 1), not fixture vocabulary.

## Section 4 — Recommendations Linkage (always, 3-state branch)

Branches by `local/recommendations.json` state. MUST NOT enumerate or paraphrase recommendation content (per I3); MAY reference IDs by stable kebab-case key.

| State | Detection | Rendered text |
|---|---|---|
| Valid with entries | exists + parses + ≥1 entry | "- See `local/recommendations.json` for active recommendations." |
| Valid empty | exists + parses + `recommendations: []` | "No active recommendations." |
| Absent / unreadable / stateless | missing OR parse fail OR stateless mode | "Recommendation state unavailable for this report." |

## Section 5 — Sprint Contract Coverage (CONDITIONAL — B4 or B2 only)

Render if and only if sprint-contract parser reaches B4 (valid) or B2 (frontmatter advisory). Section is OMITTED entirely on B1 (absent), B3 (no In Scope / empty), or B5 (unreadable). See `references/checks/sprint-contract.md` for parser spec.

When rendered:

```markdown
## Sprint Contract Coverage

| In Scope item | LAV items aligned | Coverage |
|---|---|---|
| <label> | L_X, L_Y (or "—") | <alignment summary> |

(X/6 LAV items aligned)
```

Zero-alignment fallback: render table with all `—` entries plus footer line *"No LAV items currently aligned with active sprint scope."*

## Negative-Transparency Filter (S5)

Apply to GENERATOR-AUTHORED regions only (template prose, render templates). DO NOT apply to user-quoted content.

**Verbatim-preserved content categories (MUST NOT be filtered):**

- (a) CLAUDE.md evidence quoted in Section 2 "Evidence cited" column.
- (b) Sprint contract item labels and bodies quoted in Section 5 mapping table.
- (c) File paths, command strings, AND identifiers extracted from the audited project (all three; do not narrow to file paths only).

Forbidden tokens in generator-authored regions:

- Internal release identifiers (any release-cycle vocabulary).
- Internal task / decision / round identifiers.
- Any reference to gitignored paths.

Implementation: filter at template-rendering time on generator-authored regions; quoted user content passes through verbatim.
