---
title: "Project Learning System — Remaining Work"
description: "Implementation plan for completing Phase 3 (Validation) and Phase 4 (Documentation) of the learning system"
version: 1.0.0
date: 2026-04-09
parent_spec: docs/plans/project-learning-system.md
---

# Project Learning System — Remaining Work

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the learning system by fixing remaining documentation issues, committing cosmetic changes, and updating the spec checklist to reflect actual completion state.

**Architecture:** No structural changes. This is cleanup work: one hooks.json description fix, cosmetic commits, and spec checklist updates.

**Tech Stack:** Markdown, JSON, Git

---

## Pre-Flight: What's Already Done

Phase 1 (Storage & Hook) and Phase 2 (Skill Integration) are **fully committed** in 7 commits on `feat/project-learning-system`. The following Phase 4 items are already done:

- ✅ CHANGELOG.md updated (commit `bb2a172`)
- ✅ CLAUDE.md updated (commit `bb2a172`)
- ✅ plugin.json version — already `2.9.0` on both main and branch (no bump needed)
- ✅ i18n guide sync — not needed (no English guide files were modified)

## What's Actually Remaining

After analysis, the remaining work reduces to:

1. **hooks.json description update** — description is stale
2. **Cosmetic changes commit** — uncommitted formatting/asset changes need a separate commit
3. **Spec checklist update** — mark completed items and annotate Phase 3 validation status
4. **Phase 3 validation** — manual E2E testing (cannot be automated in this repo)

---

### Task 1: Update hooks.json Description

**Files:**
- Modify: `plugin/hooks/hooks.json`

The hook now performs 3-case detection (no config, no profile, stale profile) but the description still says the old single-case behavior.

- [ ] **Step 1: Update description field**

In `plugin/hooks/hooks.json`, change line 2:

```json
"description": "Checks project state on session start — suggests /create if no config, /audit if no profile, or re-audit if profile is stale"
```

The full file should read:

```json
{
  "description": "Checks project state on session start — suggests /create if no config, /audit if no profile, or re-audit if profile is stale",
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/session-start.sh\"",
            "statusMessage": "Checking for Claude Code configuration"
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add plugin/hooks/hooks.json
git commit -m "docs(hooks): update hooks.json description for 3-case detection"
```

---

### Task 2: Commit Cosmetic Changes

**Files (all uncommitted in working tree):**
- `README.md` — bold marker removal
- `docs/i18n/ja-JP/README.md` — bold marker removal (mirror)
- `docs/i18n/ko-KR/README.md` — bold marker removal (mirror)
- `plugin/references/security-patterns.md` — table alignment
- `plugin/skills/audit/references/checks/lav.md` — heading bold removal
- `plugin/skills/audit/references/checks/t1-foundation.md` — table alignment
- `plugin/skills/audit/references/checks/t2-protection.md` — table alignment
- `plugin/skills/audit/references/checks/t3-optimization.md` — table alignment
- `plugin/skills/audit/references/scoring-model.md` — table alignment, code fence tags
- `plugin/skills/create/templates/advanced.md` — bold marker removal

Asset changes (separate commit):
- `assets/banner.svg` — deleted
- `assets/claudecode-color.svg` — added
- `assets/old/` — created (contains old banner.svg)

- [ ] **Step 1: Commit formatting changes**

```bash
git add README.md \
  docs/i18n/ja-JP/README.md \
  docs/i18n/ko-KR/README.md \
  plugin/references/security-patterns.md \
  plugin/skills/audit/references/checks/lav.md \
  plugin/skills/audit/references/checks/t1-foundation.md \
  plugin/skills/audit/references/checks/t2-protection.md \
  plugin/skills/audit/references/checks/t3-optimization.md \
  plugin/skills/audit/references/scoring-model.md \
  plugin/skills/create/templates/advanced.md
git commit -m "style: normalize Markdown formatting (table alignment, bold markers)"
```

- [ ] **Step 2: Commit asset changes**

```bash
git add assets/
git rm assets/banner.svg
git commit -m "chore(assets): replace banner.svg with claudecode-color.svg"
```

Note: Verify `assets/old/banner.svg` exists (the old file moved there) before deleting `assets/banner.svg` from git tracking.

---

### Task 3: Update Spec Checklist

**Files:**
- Modify: `docs/plans/project-learning-system.md` (Section 14, lines 878-919)

Update the implementation checklist to reflect actual completion state.

- [ ] **Step 1: Mark completed Phase 1 items**

Replace Phase 1 section with:

```markdown
### Phase 1: Storage & Hook (foundation)

- [x] Create `local/` directory structure in `.plugin-cache/guardians-of-the-claude/` — created at runtime by Final Phase Step 1
- [N/A] Update `.gitignore` to `* !remote/` — deferred to Phase 2 (remote/); parent `.plugin-cache/.gitignore` already blocks local/
- [x] Define `project-profile.md` template with frontmatter — in `references/learning-system.md`
- [x] Define `config-changelog.md` template with frontmatter — in `references/learning-system.md`
- [x] Rewrite `hooks/session-start.sh` with 3-case detection — commit `3640c59`
- [x] Update `hooks/hooks.json` if needed — description updated for 3-case detection
```

- [ ] **Step 2: Mark completed Phase 2 items**

Replace Phase 2 section with:

```markdown
### Phase 2: Skill Integration

- [x] Add Common Phase 0 (Load Context & Learn) to all 4 skills — commit `5bd6b1a`
- [x] Add Common Final Phase (Persist Results) to all 4 skills — commit `5bd6b1a`
- [x] Add Learning Rules section to each skill's Phase 0 — via `references/learning-system.md`
- [x] Add Self-Verification checklist to each skill's final phase — via Critical Thinking reference
- [x] Add Insight delivery guidance to each skill — via Critical Thinking reference
- [x] Add skill-specific variations (audit reads full changelog, create records declines, etc.) — commit `5bd6b1a`
- [x] Add compaction logic to the Final Phase — in `references/learning-system.md`
- [x] Add same-day duplicate handling logic to changelog append step — in `references/learning-system.md`
- [x] Add legacy migration logic to Phase 0 — in each skill's Phase 0 override
```

- [ ] **Step 3: Annotate Phase 3 as manual testing**

Replace Phase 3 section with:

```markdown
### Phase 3: Validation

> Manual E2E testing — requires running skills against a real project with the plugin installed.
> Initial testing completed (commit `7a277c2` fixed spec ambiguities found during E2E).
> Full validation deferred to post-merge acceptance testing.

- [ ] Test cold start (no existing files)
- [ ] Test second run (profile exists, one changelog entry)
- [ ] Test stale detection (modify package.json, verify hook triggers)
- [ ] Test compaction (create 11+ entries, verify compaction runs)
- [ ] Test STALE handling (3+ PENDING, verify prompt)
- [ ] Test migration (old timestamp files → latest format)
- [ ] Test profile spot-check (change lock file, verify Phase 0 catches it)
- [ ] Test same-day duplicate (run /audit twice, verify single merged entry)
- [ ] Test self-verification (verify insight is project-specific, not generic)
```

- [ ] **Step 4: Mark completed Phase 4 items**

Replace Phase 4 section with:

```markdown
### Phase 4: Documentation

- [x] Update plugin CHANGELOG.md — commit `bb2a172`
- [x] Bump plugin version in plugin.json — already 2.9.0 (matches CHANGELOG)
- [x] Update CLAUDE.md if repository structure description changes — commit `bb2a172`
- [N/A] Sync i18n files (ko-KR, ja-JP) if guides are affected — no English guides modified
```

- [ ] **Step 5: Commit**

```bash
git add docs/plans/project-learning-system.md
git commit -m "docs(plans): update learning system checklist with completion status"
```

---

### Task 4: Phase 3 Validation (Manual E2E)

This task cannot be executed in this repository. It requires a separate test project with the plugin installed. Listed here as a reference checklist for post-merge testing.

**Test environment setup:**
1. Create or use an existing project with source code (e.g., a Node.js/TypeScript project)
2. Install the plugin: ensure `.claude/plugins/` points to this branch's version
3. Clear any existing `.claude/.plugin-cache/guardians-of-the-claude/` directory

**Scenario scripts:**

- [ ] **4.1: Cold start** — Run `/audit` on a project with no `.plugin-cache/local/` directory. Verify: `local/` created, `project-profile.md` generated, `config-changelog.md` created with first entry, `latest-audit.md` written.

- [ ] **4.2: Second run** — Run `/audit` again on the same project. Verify: profile read (not re-scanned from scratch), changelog has 2 entries, previous audit compared.

- [ ] **4.3: Stale detection** — Modify `package.json` (e.g., add a dependency). Start new session. Verify: SessionStart hook outputs "profile may be outdated" message.

- [ ] **4.4: Compaction** — Manually create `config-changelog.md` with 12+ entries in Recent Activity. Run `/audit`. Verify: entries older than 30 days are compacted into quarterly summaries.

- [ ] **4.5: STALE handling** — Create changelog with a recommendation at `PENDING (3x)`. Run `/audit`. Verify: skill asks user to apply/decline/defer rather than silently incrementing.

- [ ] **4.6: Migration** — Create legacy `20260408-143022-audit.md` in parent directory (not `local/`). Run `/audit`. Verify: legacy file read, content migrated to `local/latest-audit.md`, legacy file deleted.

- [ ] **4.7: Profile spot-check** — Change lock file (e.g., rename `package-lock.json` to `pnpm-lock.yaml`). Run `/create`. Verify: Phase 0 spot-check detects mismatch, updates profile's Package Management section before proceeding.

- [ ] **4.8: Same-day duplicate** — Run `/audit` twice on the same day. Verify: `config-changelog.md` has one merged entry with "(2 runs)" in header, not two separate entries.

- [ ] **4.9: Self-verification** — Run `/audit` on a project with real configuration. Verify: insights are project-specific (mention actual tech stack, real file paths), not generic advice.
