---
title: "Project Learning System"
description: "Spec for persistent project profiling, decision journaling, and context-driven learning across plugin skills"
version: 1.0.0
status: draft
date: 2026-04-08
---

# Project Learning System

## 1. Motivation

### Problem

The plugin's current skills (`/create`, `/audit`, `/secure`, `/optimize`) operate as one-time setup tools. Once a project is configured, users have no reason to return. Each skill invocation starts from scratch — scanning the project, asking questions, and generating recommendations without awareness of what happened in previous sessions.

This causes:

- **Redundant work**: Every skill re-discovers the tech stack by reading manifests from scratch.
- **Inconsistent recommendations**: Different sessions may detect the project differently and suggest conflicting approaches (e.g., recommending `npm` in one session after `pnpm` was established in another).
- **No continuity**: Recommendations made in a previous `/audit` are forgotten. Declined features are re-suggested. Adopted changes are not acknowledged.
- **One-time engagement**: Users install the plugin, run `/create`, maybe `/audit`, then never return.

### Goal

Transform the plugin from a one-time setup tool into a **continuous configuration companion** that:

1. Remembers the project's detected environment across sessions.
2. Tracks configuration decisions (applied, pending, declined) over time.
3. Uses accumulated context to deliver increasingly relevant recommendations.
4. Provides ongoing value through drift detection, recommendation follow-up, and configuration health monitoring.

### Design Principles

- **Score is a snapshot, not learning data.** Audit scores are shown to users as a point-in-time quality indicator. They are NOT recorded in learning storage because scoring criteria change across audit versions, making cross-version comparison misleading. Learning is based on actions, decisions, and detected changes — not scores.
- **Markdown-only.** No compiled binaries, no JSONL, no shell scripts for data processing. All storage is plain Markdown that LLMs read natively. This aligns with the plugin's pure-Markdown philosophy and is more token-efficient than structured formats like JSONL.
- **Bounded growth.** All files have explicit line budgets enforced by compaction. Token cost remains predictable regardless of how long the plugin has been in use.
- **Minimal file footprint.** Maximum 7 files in the local directory at any time. No timestamp-based file accumulation.

---

## 2. Directory Structure

### Layout

```markdown
.claude/.plugin-cache/guardians-of-the-claude/
├── .gitignore                       ← "* !remote/"
└── local/
    ├── project-profile.md           ← Auto-detected project state (~30 lines)
    ├── config-changelog.md          ← Decision journal (200 lines max)
    ├── latest-audit.md              ← Last /audit result (includes score)
    ├── latest-create.md             ← Last /create result
    ├── latest-secure.md             ← Last /secure result
    └── latest-optimize.md           ← Last /optimize result
```

### Constraints

| Constraint | Value |
| ------------ | ------- |
| Max files in `local/` | 7 (fixed: profile + changelog + 4 latest + future reserve) |
| `project-profile.md` budget | ~30 lines (~300 tokens) |
| `config-changelog.md` budget | 200 lines (~1,600 tokens) |
| `latest-*.md` | 1 per skill, overwritten each run |
| Timestamp-based files | None. Previous `{timestamp}-{skill}.md` pattern is replaced |

### .gitignore

The parent directory `.claude/.plugin-cache/` already has a `.gitignore` with `*` that blocks all contents from git tracking. For Phase 1, no additional `.gitignore` changes are needed — the `local/` directory is automatically excluded by the parent rule.

For Phase 2 (remote/), the `.gitignore` at the `guardians-of-the-claude/` level would need to be created with `* !remote/`, and the parent `.gitignore` would need a `!guardians-of-the-claude/` exception. This is deferred.

### Legacy File Paths

Before the learning system, skills stored results as timestamped files directly in `.claude/.plugin-cache/guardians-of-the-claude/`:

```
.claude/.plugin-cache/guardians-of-the-claude/
├── 20260408-143022-create.md    ← legacy (no local/ subdirectory)
├── 20260410-091500-audit.md     ← legacy
└── ...
```

The new system stores files in the `local/` subdirectory. Migration logic in Phase 0 Step 2 checks the parent directory for legacy files when no `local/latest-*.md` is found.

---

## 3. Project Profile (`project-profile.md`)

### Purpose

A single document capturing the auto-detected current state of the project. All skills read this file in Phase 0 to immediately understand the project context without re-scanning manifests.

### Format

```markdown
---
title: Project Profile
description: Auto-detected project environment for consistent Claude Code recommendations
generated_by: guardians-of-the-claude
last_updated: 2026-04-08
source_files_checked:
  - package.json
  - tsconfig.json
---

## Runtime & Language
- Runtime: Node.js 22.x
- Language: TypeScript 5.7
- Module system: ESM

## Framework & Libraries
- Framework: Next.js 15 (App Router)
- UI: React 19
- Styling: Tailwind CSS v4

## Package Management
- Manager: pnpm
- Lock file: pnpm-lock.yaml

## Testing
- Unit: Vitest
- E2E: Playwright

## Build & Dev
- Bundler: Turbopack (via Next.js)
- Linter: ESLint 9 (flat config)
- Formatter: Prettier

## Project Structure
- Type: Single project (not monorepo)
- Source convention: src/
- Key directories: src/app/, src/components/, src/lib/

## Claude Code Configuration State
- CLAUDE.md: exists (12 sections)
- settings.json: exists (permissions configured)
- Rules: 3 files
- Agents: 1 file
- Hooks: 2 configured
- MCP: 2 servers
```

### Generation

- **First created by:** The first skill that runs (`/create`, `/audit`, `/secure`, or `/optimize`).
- **Updated by:** Any skill that detects changes during Phase 0 spot-check, or `/audit` which always performs a full refresh.
- **Sections are project-dependent:** If a project has no testing framework, the Testing section reads "Not detected". If it's a Python project, sections reflect Python tooling.

### Relationship to CLAUDE.md

| | CLAUDE.md | project-profile.md |
| --- | --- | --- |
| Author | User (with LLM assistance) | LLM (auto-detected) |
| Content | Instructions ("use vitest") | Facts ("vitest 2.3.1 detected") |
| Location | Project root | `.plugin-cache/local/` |
| Git tracked | Yes | No |

These are complementary, not overlapping. CLAUDE.md prescribes behavior; the profile describes reality.

---

## 4. Config Changelog (`config-changelog.md`)

### Purpose

A decision journal tracking what actions were taken, what was recommended, and what the user decided — across all skill invocations over time. This is the primary data source for the learning system.

**Critical principle:** This file does NOT contain audit scores. Scores are version-dependent snapshots shown to users in `latest-audit.md`, not learning data.

### Format

```markdown
---
title: Configuration Changelog
description: Decision journal for Claude Code configuration changes
version: 1.0.0
compacted_at: 2026-07-01
entry_count: 23
---

## Compacted History

- **2026** (full year): 8 audits, 3 secure, 2 optimize, 2 create runs.
  Applied: deny patterns, file protection hooks, MCP integration, rules split.
  Declined: custom agents (user preference). Detected: pnpm migration, Playwright added.

- **2027-Q1**: 3 audits, 1 optimize.
  Applied: custom agent (api-reviewer), E2E test hooks.
  Open: workspace-level rules (2x pending). No new declines.

- **2027-Q2**: 2 audits, 1 secure.
  Applied: updated deny patterns for new API endpoints.
  Resolved: workspace-level rules. No open items.

## Recent Activity

### 2027-07-15 — /audit
- Detected: Tailwind v4 migration complete (v3 references removed)
- Profile updated: Framework & Libraries section
- Applied: (none)
- Recommendations:
  - Add browser automation to settings.json allow — PENDING

### 2027-07-08 — /optimize
- Applied: Added custom agent api-reviewer.md
- Applied: Split testing rules from code-style rules
- Profile updated: Configuration State (Agents 1→2, Rules 3→4)
- Resolved: "custom agent" from 2027-Q1

### 2027-07-01 — /audit
- Detected: typescript upgraded 5.7→5.8
- Profile updated: Runtime & Language section
- Applied: (none)
- Recommendations:
  - Add browser automation to settings.json allow — PENDING
  - Upgrade ESLint flat config rules — PENDING
```

### Entry Format

Each entry follows this structure:

```markdown
### {YYYY-MM-DD} — /{skill-name}
- Detected: {project changes found, if any}
- Profile updated: {sections changed, if any}
- Applied: {configuration changes made by this skill}
- Resolved: {previously PENDING recommendations now addressed}
- Recommendations:
  - {recommendation description} — {PENDING | DECLINED by user}
```

Fields with no data use `(none)` rather than being omitted, for consistency.

### Same-Day Duplicate Handling

If the same skill runs multiple times on the same day, the changelog does NOT create separate entries. Instead, the existing entry for that day+skill is **updated in place**:

```markdown
### 2026-04-08 — /audit (3 runs)
- Detected: playwright added (run 1), typescript 5.7→5.8 (run 3)
- Profile updated: Testing, Runtime sections
- Applied: (none)
- Recommendations:
  - browser automation allow — PENDING
```

Rules:
- The `(N runs)` count is appended to the header.
- New detections are appended to the Detected line with the run number.
- Recommendations reflect the final state (if a recommendation was PENDING in run 1 and RESOLVED in run 2, it shows as RESOLVED).
- This prevents one day of heavy usage from consuming disproportionate changelog budget.

### Recommendation Statuses

| Status | Meaning |
| -------- | --------- |
| PENDING | Recommended but not yet addressed |
| PENDING (Nx) | Recommended N times across multiple runs |
| RESOLVED | Previously PENDING, now addressed |
| DECLINED | User explicitly chose not to adopt |
| STALE | PENDING 3+ times with no user response; auto-archived |

### Budget & Compaction

Total budget: 200 lines.

| Section | Budget | Typical content |
| --------- | -------- | ----------------- |
| Frontmatter | 7 lines | Fixed metadata |
| Compacted History | ~90 lines | Multi-year summaries at 3-tier resolution |
| Recent Activity | ~70 lines (10 entries × 7 lines) | Detailed recent entries |
| Buffer | ~33 lines | Headroom for variation |

---

## 5. Compaction Algorithm

### Trigger

Compaction runs during any skill's final phase (when writing to the changelog). It triggers when the **Recent Activity section exceeds 10 entries**.

### Process

```
1. Count entries in Recent Activity
2. If count > 10:
   a. Select entries strictly older than 30 days (entry date < today - 30; entries exactly 30 days old stay in Recent Activity)
   b. Group by quarter (YYYY-QN)
   c. For each quarter group, produce a compacted summary
   d. Append summaries to Compacted History
   e. Remove original entries from Recent Activity
3. If Compacted History has entries from 2+ years ago:
   a. Group old quarterly summaries by year
   b. Produce yearly summaries
   c. Replace quarterly entries with yearly summary
4. Update frontmatter: compacted_at, entry_count
```

### Three-Tier Resolution

```
Year-level   — entries older than 2 years
Quarter-level — entries older than current quarter
Entry-level  — recent entries (full detail)
```

This ensures the file stays within 200 lines regardless of how long the plugin has been in use.

### Lossless Anchors vs. Lossy Narrative

During compaction, data is classified into two categories:

Lossless Anchors (MUST be preserved):

- Date range (period covered)
- Skill names and execution counts
- Applied changes (what was actually done)
- Recommendation statuses: PENDING (with count), RESOLVED, DECLINED, STALE
- Declined features list
- Detected project changes (tech stack, structural)

Lossy Narrative (MAY be summarized):

- Detailed descriptions of individual changes
- Specific file names created/modified
- Verbose detection details
- Resolved recommendations (compress to count)

### Compaction Example

**Before** (3 entries, ~21 lines):

```markdown
### 2026-04-15 — /audit
- Detected: Next.js 15, pnpm, Vitest (first scan)
- Profile: generated
- Applied: (none)
- Recommendations:
  - /secure (deny patterns missing) — PENDING
  - rules/ split (CLAUDE.md >150 lines) — PENDING

### 2026-04-22 — /secure
- Applied: 8 deny patterns, 2 file protection hooks
- Profile updated: Configuration State (Hooks 0→2)
- Resolved: "/secure (deny patterns)" from 2026-04-15

### 2026-04-30 — /audit
- Detected: playwright added (devDependencies)
- Profile updated: Testing section (E2E: Playwright)
- Applied: (none)
- Recommendations:
  - rules/ split — PENDING (2x)
  - custom agent — DECLINED by user
```

**After** (~4 lines):

```markdown
- **2026-Q2 (Apr)**: 2 audits, 1 secure.
  Applied: deny patterns + file protection hooks.
  Open: rules/ split (2x pending). Declined: custom agent.
  Detected changes: playwright added.
```

Lossless Anchor verification:

- Period: 2026-Q2 (Apr) ✓
- Skills: 2 audits, 1 secure ✓
- Applied: deny patterns + hooks ✓
- PENDING: rules/ split (2x) ✓
- DECLINED: custom agent ✓
- Detected: playwright ✓

---

## 6. Latest Result Files (`latest-*.md`)

### Purpose

Each skill overwrites its `latest-{skill}.md` with the most recent execution result. This replaces the previous timestamp-based file accumulation pattern (`{timestamp}-{skill}.md`).

### Behavior

```
Skill completes →
  1. Overwrite latest-{skill}.md with current result
  2. Append summary to config-changelog.md
  3. Update project-profile.md (if changes detected)
```

### Content

Each `latest-*.md` preserves the format currently used by each skill's Phase 5, with one distinction:

- `latest-audit.md` — **includes score** (user-facing snapshot)
- All other `latest-*.md` — result summary, files created/modified, features declined

### Same-Day Multiple Runs

If a skill runs multiple times in one day, `latest-{skill}.md` is overwritten each time. Only the most recent result survives. This is intentional — the file's purpose is providing context for the NEXT session's Phase 0, not preserving intra-day history. The changelog's same-day merge captures any incremental detections.

### Migration from Timestamp Files

When a skill's Phase 0 runs:

```
1. Check for local/latest-{skill}.md → if exists, read it
2. If not found, check parent directory for legacy *-{skill}.md files
   → if found, read the most recent one
   → migrate its content to local/latest-{skill}.md
   → delete legacy timestamp files for this skill
3. If nothing found, proceed without previous context (cold start)
```

This migration happens automatically and only once per skill.

---

## 7. SessionStart Hook Enhancement

### Current Behavior

```bash
# Only checks if CLAUDE.md and settings.json exist
if [ ! -f "CLAUDE.md" ] && [ ! -f ".claude/settings.json" ]; then
  # Suggest /create
fi
```

### Enhanced Behavior (3-case detection)

```bash
#!/usr/bin/env bash
PROFILE=".claude/.plugin-cache/guardians-of-the-claude/local/project-profile.md"

# Case 1: No Claude Code configuration at all
if [ ! -f "CLAUDE.md" ] && [ ! -f ".claude/settings.json" ]; then
  cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "This project has no Claude Code configuration yet. The guardians-of-the-claude plugin is installed — suggest the user run /guardians-of-the-claude:create to set up CLAUDE.md and .claude/ configuration through a guided interview."
  }
}
EOF
  exit 0
fi

# Case 2: Configuration exists but no profile yet
if [ ! -f "$PROFILE" ]; then
  cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Claude Code configuration exists but no project profile has been generated yet. Running /guardians-of-the-claude:audit will generate a project profile for more accurate recommendations across all skills."
  }
}
EOF
  exit 0
fi

# Case 3: Profile exists — check for staleness
STALE="false"
for f in package.json tsconfig.json pyproject.toml go.mod Cargo.toml \
         pom.xml Gemfile requirements.txt .claude/settings.json; do
  if [ -f "$f" ] && [ "$f" -nt "$PROFILE" ]; then
    STALE="true"
    STALE_FILE="$f"
    break
  fi
done

if [ "$STALE" = "true" ]; then
  cat << EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Project profile may be outdated — $STALE_FILE was modified since the last profile update. Running /guardians-of-the-claude:audit will refresh the profile and check for new recommendations."
  }
}
EOF
  exit 0
fi

# Case 4: Everything is fresh — no additional context needed
exit 0
```

### Design Notes

- All cases use `additionalContext` only — Claude decides whether to mention it based on relevance to the user's current task.
- The hook does NOT force any action. It provides context for Claude to make informed suggestions.
- File modification time comparison (`-nt`) is the only check performed. No content parsing in the hook.

---

## 8. Stale Prevention (3-Layer Defense)

### Layer 1: SessionStart Hook

Compares file modification times of key manifests against the profile's modification time. Cheap (~0 tokens, runs in bash before the session). Catches dependency changes, settings modifications.

### Layer 2: Skill Phase 0 Spot-Check

When any skill reads `project-profile.md`, it also reads the project's primary manifest (e.g., `package.json`) and cross-checks **two high-impact items**:

1. **Lock file type** — Does the lock file match the profile's Package Management section? (Detects package manager switches: npm→pnpm, yarn→bun, etc.)
2. **Framework major version** — Does the primary framework version match the profile? (Detects framework upgrades: Next.js 14→15, which changes recommendations significantly.)

If either mismatches, the skill updates that section of the profile immediately before proceeding with its main work.

**Cost:** One manifest file read (~200 tokens). Applied to every skill invocation.

### Layer 3: Full Refresh via `/audit`

`/audit` always regenerates the entire profile from scratch, regardless of staleness signals. This is the authoritative reset that catches any drift not covered by Layers 1-2.

### Coverage Analysis

| Change type | Layer 1 | Layer 2 | Layer 3 |
| ------------- | --------- | --------- | --------- |
| Dependency added/removed | ✓ (file time) | — | ✓ |
| Package manager switched | ✓ (file time) | ✓ (lock file) | ✓ |
| Framework major upgrade | ✓ (file time) | ✓ (version check) | ✓ |
| Monorepo transition | ✓ (workspace file) | — | ✓ |
| Directory restructuring | — | — | ✓ |
| Claude Code config changes | ✓ (settings.json time) | — | ✓ |

Layer 3 (`/audit`) covers all cases. Layers 1-2 provide early detection for the most impactful changes.

---

## 9. Learning System

### What "Learning" Means

The plugin's skills are static Markdown — they do not change. "Learning" means the **data** that skills read (profile + changelog + latest) grows richer over time, causing the LLM to produce increasingly relevant recommendations.

This is **context-driven adaptation**, not machine learning.

### How Learning Is Encoded

Each skill's Phase 0 includes a `Learning Rules` section that instructs the LLM how to interpret accumulated data:

```markdown
## Phase 0: Load Context & Learn

1. Read `local/project-profile.md` (if exists)
   → Parse current tech stack, project structure, configuration state
   → If not found, this skill will generate it upon completion

2. Read `local/latest-{current-skill}.md` (if exists)
   → Parse previous execution result for comparison

3. Read `local/config-changelog.md` — Recent Activity section only (if exists)
   → Apply Learning Rules below

### Learning Rules

Apply these rules based on changelog data. Each rule follows the
CSA (Context-Signal-Action) pattern.

**Rule 1 — Recommendation Follow-up**
- Context: PENDING recommendations in changelog + latest-*.md existence
- Signal: A recommendation is PENDING and the corresponding skill's
  latest file shows it was not addressed
- Action: Re-state the recommendation with "(Nx pending)" count.
  Explain what remains unaddressed and why it matters.

**Rule 2 — Preference Respect**
- Context: DECLINED items in changelog + project-profile.md
- Signal: A feature was previously DECLINED by the user
- Action: Do NOT re-suggest unless the project's scale or structure
  has changed significantly since the decline (e.g., dependency count
  doubled, monorepo transition). If re-suggesting, explicitly
  acknowledge the previous decline and explain what changed.

**Rule 3 — Stagnation Detection**
- Context: Last 3+ entries in changelog (any skill, not audit-only)
- Signal: The same PENDING recommendation appears in 3+ entries consecutively
  (non-audit entries that don't mention the item do not break the chain),
  OR "Applied: (none)" appears 3 consecutive times
- Action: Change approach. Ask the user: "This recommendation has been
  pending for 3 sessions. Would you like to: (a) Apply it now,
  (b) Mark it as declined, (c) Defer to next audit?"
  If no response after this prompt, mark as STALE on next compaction.

**Rule 4 — Profile Drift Response**
- Context: project-profile.md vs current manifest files
- Signal: Phase 0 spot-check detects a mismatch between profile and
  actual project state
- Action: Update the mismatched profile section immediately.
  Re-evaluate any recommendations that depended on the changed data.
  Note the drift in the changelog entry.
```

### STALE Handling

PENDING recommendations that trigger Rule 3 and receive no user response are marked STALE during the next compaction cycle:

```
PENDING (3x) → Rule 3 asks user → no response → STALE
STALE items are mentioned once more in the next audit entry,
then archived in Compacted History as "(no response, archived)".
```

**"No response" detection:** Since conversations are stateless, there is no way to record that a Rule 3 prompt was issued. Instead, use the PENDING count as evidence: if an item is PENDING (N≥3) at compaction time and no apply/decline/defer action was recorded in any entry since the count reached 3, mark it STALE. The (Nx) count itself is sufficient evidence — no intermediate `PROMPTED` status is needed.

This prevents infinite PENDING accumulation.

### Learning Effectiveness by Run Count

| Run # | Available context | Active rules | Learning effect |
| ------- | ------------------- | -------------- | ----------------- |
| 1st | None (cold start) | None | Identical to current behavior. Generates profile + first changelog entry |
| 2nd | Profile + 1 entry | Rule 4 (drift) | Tech stack known instantly. No redundant scanning questions |
| 3rd+ | Profile + 2+ entries | All 4 rules | Recommendation tracking, preference respect, stagnation detection |

---

## 10. Skill Integration

### Common Phase 0 (all skills)

Every skill's Phase 0 gains this block before its existing logic:

```markdown
## Phase 0: Load Context & Learn

### Step 0 — Directory Check
1. Check if `.claude/.plugin-cache/guardians-of-the-claude/local/` directory exists
2. If the directory does not exist: this is a cold start.
   Skip Steps 1-3 entirely and proceed to this skill's existing Phase 0 logic.
   The Final Phase will create the directory and all initial files.

### Step 1 — Load Profile
1. Read `local/project-profile.md`
2. If found: use as project context for all subsequent phases
3. If not found: note that profile will be generated in the final phase

### Step 2 — Load Previous Results
1. Read `local/latest-{this-skill}.md` for this skill's previous result
2. Read additional latest files as needed by this skill:
   - `/secure`: also read `local/latest-audit.md` (for T2 issue references)
   - `/optimize`: also read `local/latest-audit.md` and `local/latest-secure.md`
   - `/create`: also read `local/latest-secure.md` and `local/latest-optimize.md` (to avoid overwriting other skills' changes)
   - `/audit`: no additional files needed
3. If no latest file found: check parent directory
   (`.claude/.plugin-cache/guardians-of-the-claude/`) for legacy
   `*-{skill}.md` files. If found, read the most recent one.

### Step 3 — Load Changelog & Apply Learning Rules
1. Read `local/config-changelog.md`
   - `/audit`: read the full file (Compacted History + Recent Activity)
   - All other skills: read the Recent Activity section only
2. If found: apply Learning Rules (see Section 9)
3. If not found: skip (first or second run)

Then proceed to this skill's existing Phase 0 logic.
```

### Common Final Phase (all skills)

Every skill's final phase gains this block after its existing logic:

```markdown
## Final Phase: Persist Results

### Step 1 — Write Latest Result
1. Create `.claude/.plugin-cache/guardians-of-the-claude/local/` if it does not exist
2. Write `latest-{this-skill}.md` with current execution results
   (overwrite if exists)

### Step 2 — Update Profile
1. If project-profile.md does not exist: generate it from detected project state
2. If it exists and this skill detected changes: update relevant sections only
3. Update `last_updated` in frontmatter

### Step 3 — Append to Changelog
1. If config-changelog.md does not exist: create it with frontmatter + first entry
2. Before appending, run the Same-Day Duplicate Check (Step 3a)
3. Run compaction check (if Recent Activity > 10 entries, compact)

### Step 3a — Same-Day Duplicate Check

Before appending a new entry to Recent Activity:

1. Find the last `### ` line in the Recent Activity section
2. Extract the date: the `YYYY-MM-DD` portion immediately after `### `
3. Extract the skill name: the text after ` — /`
4. Compare with today's date and the current skill name

**If both match** → update the existing entry in place:
- Increment the run count in the header: `(2 runs)` → `(3 runs)`
- Append new detections with the run number: `typescript 5.7→5.8 (run 3)`
- Merge recommendations to reflect final state
  (if PENDING in run 1 and RESOLVED in run 2, show RESOLVED)
- Do NOT duplicate unchanged fields

**If either differs** → append a new entry as normal.

**Example — merging a second run into an existing entry:**

Before (10:30:00 run):

```markdown
### 2026-04-08 — /audit
- Detected: playwright added
- Profile updated: Testing section
- Applied: (none)
- Recommendations:
  - browser automation allow — PENDING
```

After (14:15:00 run merged):

```markdown
### 2026-04-08 — /audit (2 runs)
- Detected: playwright added (run 1), typescript 5.7→5.8 (run 2)
- Profile updated: Testing section (run 1), Runtime section (run 2)
- Applied: (none)
- Recommendations:
  - browser automation allow — PENDING
```

### Step 4 — Legacy Cleanup
1. Glob for legacy `*-{this-skill}.md` files in parent directory
2. If found: delete them (data is now in latest + changelog)
```

### Skill-Specific Differences

| Skill | Phase 0 special | Final phase special |
| ------- | ----------------- | --------------------- |
| `/audit` | Reads **full** changelog (not just Recent) for trend analysis. Always performs full profile regeneration in final phase | `latest-audit.md` includes score (user-facing snapshot) |
| `/create` | Checks profile to **skip** the "existing vs new project" question if profile exists | Records declined features explicitly in changelog entry |
| `/secure` | Reads profile's Configuration State to identify security gaps | Updates profile's Hooks/Rules counts; marks addressed audit recommendations as RESOLVED |
| `/optimize` | Reads profile + changelog to avoid re-suggesting previously DECLINED items | Updates profile's Configuration State; marks addressed audit recommendations as RESOLVED |

---

## 11. Token Budget Analysis

### Per-Skill Cost

| Data read | Tokens | Which skills |
| ----------- | -------- | ------------- |
| project-profile.md | ~300 | All 4 skills |
| latest-{skill}.md | ~200 | All 4 skills |
| config-changelog.md (Recent only) | ~550 | /create, /secure, /optimize |
| config-changelog.md (full) | ~1,300 | /audit only |

Typical cost per skill invocation:

- `/create`, `/secure`, `/optimize`: ~1,050 tokens (profile + latest + recent changelog)
- `/audit`: ~1,800 tokens (profile + latest + full changelog)

Comparison — learning vs no learning:

| Approach | Tokens per invocation |
| ---------- | ---------------------- |
| With learning (`/create`, `/secure`, `/optimize`) | ~1,050 |
| With learning (`/audit`) | ~1,800 |
| Without learning (re-scan manifests every time) | ~2,000+ |

The learning system reduces per-invocation cost by avoiding redundant manifest scanning, while providing richer context for recommendations.

---

## 12. Phase 2: Remote (Deferred)

> **Status: Design only. Not implemented until user demand is established.**

### Concept

For team projects, a `remote/` directory within `.plugin-cache/guardians-of-the-claude/` could hold git-tracked, team-shared data:

```
.claude/.plugin-cache/guardians-of-the-claude/
├── .gitignore          ← "* !remote/"
├── local/              ← Per-developer (current implementation)
└── remote/             ← Team-shared (Phase 2)
    ├── project-profile.md    ← Team-agreed project facts
    └── team-decisions.md     ← Team-level adopted/declined decisions
```

### Merge Strategy (preliminary)

When both `local/` and `remote/` exist:

- **Project facts** (tech stack, structure): `remote` takes precedence
- **Personal configuration state** (individual hooks, agents): `local` takes precedence
- **Team DECLINED decisions**: Override individual suggestions (if the team declined agents, don't suggest agents to individuals)

### Why Deferred

1. Most plugin users are solo developers.
2. The local learning system must be stable before adding team complexity.
3. The `local/` path structure is already future-proof — adding `remote/` requires no migration.

---

## 13. Critical Thinking & Insight Delivery

### Philosophy

LLM models (Claude, Codex, Gemini) have a natural tendency toward sycophancy — agreeing with the user, following instructions without questioning, and avoiding pushback. This leaves users vulnerable to blind spots: assumptions they never examined, edge cases they did not consider, simpler alternatives they did not explore.

Our skills take a different approach. Inspired by the Socratic method, every skill should **think critically about its own output AND the user's situation**, surfacing questions and insights that lead to better outcomes through dialogue — not just task completion.

The goal is not to be contrarian. It is to be a **thinking partner** that earns the user's trust by catching what they missed.

### The Anti-Sycophancy Principle

When a skill generates a recommendation or completes a task, it must resist the default LLM behavior of presenting results as final and correct. Instead:

| Sycophantic (avoid) | Critical (prefer) |
| --- | --- |
| "Done. I added 3 deny patterns." | "I added 3 deny patterns. However, your project also has a `/api` route that handles file uploads — this endpoint may need an additional allow rule for multipart processing, or requests will be silently blocked." |
| "Your configuration looks good." | "Your configuration covers the common cases. One thing I notice: you have MCP servers configured but no deny pattern for MCP tool names — if a server exposes a destructive tool, there is no guardrail." |
| "I recommend adding agents." | "Agents could help here, but I should note — your project has only 2 rule files and a straightforward structure. Agents add value when there are multiple distinct review concerns. At your current scale, a well-written rule file might achieve the same result with less complexity." |

### How to Think Critically (Socratic Verification)

After completing its main work, every skill should ask itself these questions — not as a mechanical checklist, but as genuine critical examination:

Challenge the recommendation:
- "If I were a skeptical senior engineer reviewing this recommendation, what would I question?"
- "Is there a simpler way to achieve the same outcome that I did not consider?"
- "Am I recommending this because it is genuinely the best option, or because it is the most common pattern?"

Challenge the assumptions:
- "What am I assuming about this project that I have not verified?"
- "Does the profile say one thing while the actual project state says another?"
- "Did the user ask for X, but would they actually be better served by Y?"

Find the blind spots:
- "What could go wrong with what I just did that the user would not notice until later?"
- "Is there a dependency or interaction between my changes and existing configuration that I have not addressed?"
- "What question should the user be asking that they are not asking?"

### When to Share Insights

Not every self-verification finding deserves to be shared. Apply this filter:

```
Is it specific to THIS project?     → No → discard
Is it actionable or educational?    → No → discard
Would a senior engineer mention it? → No → discard
                                    → Yes → share as insight
```

### Insight Quality Standards

Good insights are:
- Specific to the project ("your `/api` route handles file uploads")
- Non-obvious (something the user likely did not think about)
- Concise (2-3 sentences, one topic per insight)
- Honest about trade-offs ("this adds safety but also adds complexity")

Bad insights are:
- Generic advice that applies to any project ("use TypeScript for type safety")
- Restating what the skill just did ("I added 3 deny patterns")
- Praising the user's choices ("great decision to use pnpm!")
- Hedging without substance ("you might want to consider...")

### Encouraging Dialogue, Not Monologue

The critical thinking process should naturally create opportunities for the user to engage. When a skill surfaces a genuine insight or question, it invites the user to think, respond, and refine — leading to better outcomes through iteration.

This is the difference between:
- **Monologue:** "Here are your results. Done." → User accepts, moves on, misses issues
- **Dialogue:** "Here are your results. I noticed X — does that match your intent?" → User reconsiders, we iterate, outcome improves

Skills should not force dialogue on every run. But when self-verification reveals something genuinely worth discussing, the skill should present it as a question or observation that invites the user's judgment — not as a directive.

---

## 14. Implementation Checklist

### Phase 1: Storage & Hook (foundation)

- [x] Create `local/` directory structure in `.plugin-cache/guardians-of-the-claude/` — created at runtime by Final Phase Step 1
- [N/A] Update `.gitignore` to `* !remote/` — deferred to Phase 2 (remote/); parent `.plugin-cache/.gitignore` already blocks local/
- [x] Define `project-profile.md` template with frontmatter — in `references/learning-system.md`
- [x] Define `config-changelog.md` template with frontmatter — in `references/learning-system.md`
- [x] Rewrite `hooks/session-start.sh` with 3-case detection — commit `3640c59`
- [x] Update `hooks/hooks.json` if needed — description updated for 3-case detection

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

### Phase 4: Documentation

- [x] Update plugin CHANGELOG.md — commit `bb2a172`
- [x] Bump plugin version in plugin.json — already 2.9.0 (matches CHANGELOG)
- [x] Update CLAUDE.md if repository structure description changes — commit `bb2a172`
- [N/A] Sync i18n files (ko-KR, ja-JP) if guides are affected — no English guides modified
