---
title: "Markdown Lint Review Log"
description: "Summary of markdownlint issues reviewed and remediated in this repository"
date: 2026-03-19
---

# Markdown Lint Review Log

This document records the markdownlint issues reviewed in this repository so far, the root cause identified for each rule, the remediation applied, and the verification method used.

## Reviewed Rules

| Rule | Status | Root cause | Remediation |
| ----- | ------ | ---------- | ----------- |
| `MD060/table-column-style` | Reviewed and remediated | Table separator rows used compact style such as `|-----|-----|` instead of spaced compact columns | Normalized separator rows to spaced style across affected docs |
| `MD040/fenced-code-language` | Reviewed and remediated | Several fenced blocks omitted info strings; the planning doc also had outer `markdown` fences that were too short to safely contain inner fenced examples | Added explicit fence languages such as `text`, `markdown`, and `gitignore`; upgraded affected outer fences in the planning doc from triple to quadruple backticks |

## Files Reviewed for `MD060`

- `docs/claude-md-guide.md`
- `docs/directory-structure-guide.md`
- `docs/effective-usage-guide.md`
- `docs/rules-guide.md`
- `docs/settings-guide.md`
- `docs/superpowers/plans/2026-03-18-claude-code-templates.md`
- `docs/superpowers/specs/2026-03-18-claude-code-templates-design.md`

## Files Reviewed for `MD040`

- `docs/claude-md-guide.md`
- `docs/directory-structure-guide.md`
- `docs/effective-usage-guide.md`
- `docs/getting-started.md`
- `docs/rules-guide.md`
- `docs/superpowers/plans/2026-03-18-claude-code-templates.md`
- `docs/superpowers/specs/2026-03-18-claude-code-templates-design.md`

## Review Notes

- Short command transcripts such as `claude` followed by `/init` were labeled `text` because they are illustrative terminal transcripts rather than runnable shell snippets.
- Repository trees and directory listings were labeled `text`.
- `.gitignore` examples were labeled `gitignore`.
- Markdown examples that embed inner fenced blocks now use outer quadruple backticks so the embedded fences remain literal content instead of terminating the example early.

## Verification Performed

- Searched all `*.md` files for compact table separator rows to confirm the `MD060` pattern was removed.
- Parsed markdown files to identify fenced code openings without an info string and corrected the remaining real offenders.
- Re-scanned the repository after edits to confirm the reviewed `MD040` and `MD060` patterns no longer appear in the previously affected files.

## Limitations

- `markdownlint` is not installed in this workspace, so verification was performed with repository scans and structural inspection instead of the linter binary itself.
