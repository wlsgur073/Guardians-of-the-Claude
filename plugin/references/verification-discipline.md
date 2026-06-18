---
title: Verification Discipline
description: Operational verification — read-back-after-edit, tool-success vs task-correct, scope-checked reporting. Complementary to critical-thinking.md.
version: 1.1.0
---

# Verification Discipline

Operational verification covers the gap between *the tool returned success* and *the task is actually correct*. This file documents the runtime checks Claude should perform after every non-trivial action; pair it with [`critical-thinking.md`](critical-thinking.md) for reasoning-time discipline. The two together close the loop: critical-thinking guards inputs and conclusions; verification-discipline guards outputs and effects.

## Vocabulary

Three named concepts shape verification practice.

**Read-back-after-edit.** After modifying a file, re-read the relevant section to confirm the edit landed as intended. This catches anchor-matched-wrong-place, partial replacement, and silent failures that tool-level success codes don't surface. Cost: one read per edit. Benefit: catches a class of "tool reports success but content is wrong" bugs.

**Tool-success ≠ task-correct.** A tool call's exit code only tells you *the tool finished*. It does not tell you the task was semantically correct. Example: `git commit -m "fix bug"` exits 0 whether or not the commit actually fixed the bug. Treat every tool-success report as evidence that *something* happened, not as evidence the *right* thing happened.

**Scope-checked reporting.** When summarizing work, describe what you *actually* checked, not what you generically *might* have checked. "Verified the deny pattern in `settings.json:42`" beats "Verified the configuration"; "Updated the cross-link and confirmed the slug resolves" beats "Updated cross-links."

## Read-Back-After-Edit

After any Edit that lands a regex-anchored change, re-read the surrounding lines. Tool-level "Edit succeeded" means the regex matched and a replacement happened — not that the right region was matched.

**Example.** Adding a deny pattern to `templates/advanced/.claude/settings.json`:

1. Edit lands: `"deny": ["Read(./.env)"]` becomes `"deny": ["Read(./.env)", "Bash(rm -rf *)"]`.
2. Read back lines 8-15 of `settings.json`. Confirm the new pattern appears AND the JSON is still valid (closing bracket, no trailing comma where there shouldn't be one).
3. If the regex matched something unexpected (e.g., a `"deny"` key in an unrelated nested object), the read-back surfaces it; the Edit exit code does not.

Skip read-back only for truly trivial changes (typos, whitespace) where the failure mode is visible at the same level the edit happened.

## Tool-Success ≠ Task-Correct

A successful tool call proves something executed; it does not prove the task was semantically right.

**Example.** Bumping a guide's frontmatter `version` field from `1.3.2` to `1.4.0`:

1. `Edit` returns success.
2. The version field in the frontmatter now says `1.4.0`.
3. BUT — was the bump semantically appropriate? If the change was a typo fix (patch-level), the bump should have been `1.3.3`, not `1.4.0`. The Edit tool reports success either way; only a semantic check (does this content addition match minor-version criteria?) tells you the bump was correct.

The discipline: after every tool-success, ask "did this advance the *task*, or just the *operation*?" before reporting completion.

## Report-What-You-Actually-Checked

When summarizing work to the user, name the specific verifications performed — not a generic class of verification.

**Bad reporting:**
> "Verified the changes and everything looks good."

**Good reporting:**
> "Verified: ran `wc -l` on `claude-md-guide.md` (141 lines, within ~165 budget); checked the Identity-DNA section renders with `## Identity-DNA` heading; confirmed cross-link from `getting-started.md` Step 3 points to `#identity-dna` slug. NOT verified: end-to-end link resolution in the rendered file (would require a browser render or `lychee` run)."

The good version (a) lets the user trust what *was* checked, (b) makes explicit what *wasn't* checked, and (c) gives the user a basis to ask follow-up questions.

## Reusable Definition-of-Done Checklist

Use this template at the end of any Job that ships content into the repo. Items map to project-level discipline (envelopes, evidence labels, anti-goals) and operational verification (read-back, scope-checked reporting).

```markdown
**Job DoD checklist:**

- [ ] Anchor used as declared in the project's Edit Envelopes (for OWN'd files, anchor verified against current file structure)
- [ ] Line-budget respected (post-edit line count within declared cap for the OWN'd file)
- [ ] Cross-references resolve (target files exist; anchor slugs match GitHub-flavored markdown slugification)
- [ ] Evidence label assigned (one of: public-doc-backed, repo-derived, generalized-pattern, speculative); any within-Job claim of different evidence class locally marked
- [ ] No anti-goal violation (per the project's anti-goal list: no direct third-party quotes, no vendor-does-X claims, no speculative date commitments, no external-source branding in filenames/titles)
- [ ] Read-back performed on every regex-anchored Edit
- [ ] Tool-success ≠ task-correct check performed
- [ ] Original requirement re-confirmed against the FINAL artifact — not just per-edit: a later edit in the same Job did not silently regress what an earlier edit established (the original goal still holds end-to-end)
- [ ] Scope-checked report drafted (what was checked, what wasn't)
```

Copy this into the Phase plan's DoD section and tailor only the file/anchor-specific items.

## Self-Policing Meta-Loop

This file's DoD checklist applies to its own creation. The two items below specifically catch the "agent forgot to verify its own discipline" failure mode — meta-items that close the loop:

- [ ] Cumulative line-budget ledger maintained for shared files (declared budget per file; current line count tracked; growth verified within budget)
- [ ] Every behavioral claim has an evidence label (one of: public-doc-backed, repo-derived, generalized-pattern, speculative)

Without these, the verification discipline becomes self-exempt: the agent verifies *other things* but not the verification process itself.

## See Also

- [`critical-thinking.md`](critical-thinking.md) — Socratic verification at reasoning time. Use alongside operational verification: critical-thinking guards inputs and conclusions; verification-discipline guards outputs and effects.
