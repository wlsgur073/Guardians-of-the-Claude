---
title: Schema Evolution Policy & Recommendation Registry
description: SemVer + base+versioned-wrapper schema evolution; recommendation ID registry; legacy MD project profile format (pre-v2.11.0).
version: 1.0.0
---

## Legacy Project Profile Format (pre-v2.11.0)

> **Note**: Current canonical format is `profile.json` — see `plugin/references/schemas/profile.schema.base.json` (shape) and `profile.schema.v1.0.0.json` / `profile.schema.v1.1.0.json` / `profile.schema.v1.2.0.json` (versioned validators). This legacy MD format is still parsed by Phase 0.5 migration (Task 3) to convert existing installations.

Frontmatter:

```yaml
---
title: Project Profile
description: Auto-detected project environment for consistent Claude Code recommendations
generated_by: guardians-of-the-claude
last_updated: {YYYY-MM-DD}
source_files_checked:
  - {manifest files checked}
---
```

Sections use `- Key: Value` format. Use "Not detected" when absent:

```markdown
## Runtime & Language
- Runtime: {e.g. Node.js 22.x}
- Language: {e.g. TypeScript 5.7}
- Module system: {e.g. ESM}

## Framework & Libraries
- Framework: {e.g. Next.js 15 (App Router)}
- UI: {e.g. React 19}
- Styling: {e.g. Tailwind CSS v4}

## Package Management
- Manager: {e.g. pnpm}
- Lock file: {e.g. pnpm-lock.yaml}

## Testing
- Unit: {e.g. Vitest}
- E2E: {e.g. Playwright}

## Build & Dev
- Bundler: {e.g. Turbopack}
- Linter: {e.g. ESLint 9 (flat config)}
- Formatter: {e.g. Prettier}

## Project Structure
- Type: {e.g. Single project (not monorepo)}
- Source convention: {e.g. src/}
- Key directories: {e.g. src/app/, src/components/, src/lib/}

## Claude Code Configuration State
- CLAUDE.md: {exists/missing (section count)}
- settings.json: {exists/missing (permissions note)}
- Rules: {count} files
- Agents: {count} files
- Hooks: {count} configured
- MCP: {count} servers
```

---

## Schema Evolution Policy

Profile and recommendation schemas follow SemVer:

- **Patch (z)**: clarifications, docs, no structural change.
- **Minor (y)**: add optional fields. The parser/validator accepts N-1 minor — each per-version schema file is a single-version validator (pinned by `"schema_version": { "const": "x.y.z" }`).
- **Major (x)**: remove or rename a field, or change its type.

Migration parser MUST support the current minor AND the previous minor (N-1). A major bump triggers a one-time migration rewrite. The `schema_version` field in the JSON payload tracks payload version, independent from `plugin.json` version.

**Base + versioned-wrapper architecture (profile schema)**: `profile.schema.base.json` holds the shared property shape via `$defs` without closing the schema. Versioned wrappers (`profile.schema.v1.0.0.json`, `profile.schema.v1.1.0.json`, etc.) compose the base via `$ref` and close with `unevaluatedProperties: false` at every scope the wrapper extends.

**Why `unevaluatedProperties` not `additionalProperties`**: `additionalProperties: false` placed in a base schema evaluates within the base's own scope — it rejects fields added by versioned wrappers (those fields look "additional" to the base). `unevaluatedProperties: false` at wrapper scope counts all declarations reached through `allOf`/`$ref` composition as "evaluated," so wrapper-added fields pass while truly unknown fields are rejected. This keyword requires JSON Schema draft 2019-09 or later; wrappers declare `"$schema": "https://json-schema.org/draft/2020-12/schema"` explicitly. Pre-2019-09 validators silently ignore `unevaluatedProperties`, leaving the schema appearing strict but not enforcing — the T0 preflight probe (`ci/scripts/preflight-schema.py`) verifies draft 2020-12 enforcement before T1 schema commits.

**Versioned dispatch**: the parser/validator reads each instance's `schema_version` literal, selects the matching `profile.schema.v<version>.json` wrapper, and validates. Unknown versions fail with a diagnostic naming the literal and the candidate path tried. Schema-level `oneOf` aggregation is not the canonical mechanism.

**Aliases enable id renames across schema versions**: see `recommendation-registry.json` (`aliases[]` field) — a recommendation key can be renamed in a later schema version while the old key continues to resolve transparently to the new entry. ID stability is **not** assumed; aliases are the migration mechanism.

**All timestamps MUST be ISO-8601 UTC** across `profile.json`, `recommendations.json`, `recommendation-registry.json`, and `state-summary.md` (header `Generated at`).

---

## Recommendation ID Registry

The canonical registry is **`plugin/references/recommendation-registry.json`** — machine-readable, schema-validated, the single source of truth for recommendation identities, allowed issuers/resolvers, and aliases. See Task 2.5 for its schema and initial data.

**Identity model**: each recommendation has a stable `key` (lowercase kebab-case, e.g., `deny-env`) — independent of which skill issues or resolves it. The registry stores allowed `issuers[]` and `resolvers[]` per key; CI lints enforce that skill code emits only registered keys (or aliases) and only claims to issue/resolve where the registry authorizes.

**Aliases**: a key can be renamed across schema versions via the `aliases[]` field — backward references continue to resolve transparently. ID stability is not assumed; aliases are the migration mechanism.

**Generated table** (optional): a human-readable summary of the registry may be embedded inline below this section, generated by tooling from `recommendation-registry.json`. Do not maintain such a table by hand — it will drift.

---
