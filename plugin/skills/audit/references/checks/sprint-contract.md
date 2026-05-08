---
title: "sprint-contract.md parser (audit-only consumer)"
description: "Optional, read-only post-freeze parse of sprint-contract.md for qa-report Sprint Contract Coverage section"
version: "1.0.0"
applies_to: audit-score-v4.1.0
---

# Sprint Contract Parser

Read `<project-root>/sprint-contract.md` AFTER audit-fact freeze (LAV scores committed, DS/SB/cap/Final computed, bucket classified). Read is optional, read-only, non-fatal on any failure.

**Forbidden**: do NOT read `sprint-contract.md` before LAV scoring; do NOT pass its content into LAV prompts (preserves I5 freeze ordering and prevents sprint scope from biasing LAV evaluation).

## Branch Order

Evaluate state in this exact order:

1. **Existence** — file at `<project-root>/sprint-contract.md`?
2. **Readability** — file readable as UTF-8?
3. **Frontmatter** — YAML frontmatter parses cleanly? (advisory only)
4. **Heading-extraction** — `## In Scope` H2 present + ≥1 extractable bullet?

| State | Conditions | Section render | Terminal warning |
|---|---|---|---|
| **B1 absent** | Existence fails | OMITTED | None |
| **B2 frontmatter advisory** | Existence ✓, readability ✓, frontmatter fails, heading-extraction succeeds | RENDERED (treat as B4) | `sprint-contract.md frontmatter malformed; using heading-based extraction` |
| **B3 missing or empty** | Existence ✓, readability ✓; no `## In Scope` OR header present but heading-extraction yields zero items | OMITTED | `sprint-contract.md missing '## In Scope' section or no extractable items; skipping coverage` |
| **B4 valid** | All four checks succeed | RENDERED with mapping table | None |
| **B5 unreadable** | Existence ✓, readability ✗ | OMITTED | `sprint-contract.md unreadable; skipping coverage` |

## Heading-Based Extraction (5 ordered steps)

1. **Locate header** — first H2 matching `## In Scope` (case-sensitive, exact). No `## in-scope` / `## In-Scope` / `## InScope` aliases. If multiple `## In Scope` headers exist, only the first is processed. Trim trailing whitespace before comparison (so '## In Scope' and '## In Scope ' both match).
2. **Capture region** — bullets `- ` or `* ` directly under the header until next H2 (`##`) or end-of-file (blank lines between header and bullets, or between adjacent bullets, do not terminate capture; capture terminates only at next H2 or end-of-file). Numbered lists (`1. `, `2. `) NOT extracted. H3+ subheadings ignored — only direct bullets count.
3. **Extract label and body** — for each bullet:
   - Preferred: `- **Label** — body` or `- **Label**: body`. Strip markdown emphasis (`**`, `__`).
   - Fallback (no leading bold): take content up to first em dash (`—`), colon (`:`), or sentence-terminator (`. ` or end of line).
   - Delimiter protection: do NOT split on em dash / colon / period inside inline code spans (`` ` ` ``) or bracketed file paths (`<path>`).
   - Body = remainder + continuation lines.
   - Both label and body retained; label rendered, both used for alignment matching.
4. **Zero-items handling** — extraction yields zero items → B3 with warning.
5. **Multi-line bullets** — continuation lines indented by ≥2 spaces under a bullet are appended to that bullet's body. Continuation ends at the next bullet or section boundary.

## In Scope ↔ LAV Mapping (B4 or B2 only)

Render in qa-report Sprint Contract Coverage section:

```markdown
| In Scope item | LAV items aligned | Coverage |
|---|---|---|
| <label> | L_X, L_Y (or "—") | <alignment summary> |
```

**Alignment rule**: LAV item Lk aligns with In Scope item if Lk's "Evidence cited" content (qa-report Section 2 column) names a file/directory/command/concept appearing in the item's label OR body (markdown-stripped, case-insensitive substring match).

**Footer denominator**: `(X/6 LAV items aligned)` where X = count of distinct LAV items with ≥1 alignment, deduplicated.

**Rendered label**: only markdown-stripped label appears in column 1; body used for matching but not displayed.

This is intentionally low-precision in this release — exact semantic matching deferred. Future versions may tighten via anchor syntax.

## Boundary

Parser output affects ONLY qa-report Sprint Contract Coverage section. MUST NOT influence: LAV scoring, DS/SB/cap, bucket classification, recommendations.json content.

Zero-alignment fallback (B4 with all `—`): render table + footer *"No LAV items currently aligned with active sprint scope."* (informative, not a recommendation per I3).
