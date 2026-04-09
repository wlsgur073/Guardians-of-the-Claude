# T3 — Optimization Checks

These checks verify that the configuration is well-organized and maintainable. (40% of Detail Score weight)

## Weights

| Item | Weight | Rationale |
| ------ | -------- | ----------- |
| T3.1 Directory references | 0.20 | Configuration accuracy |
| T3.2 CLAUDE.md length | 0.10 | Maintainability signal |
| T3.3 Command availability | 0.20 | Tool chain integrity |
| T3.4 Rules path validation | 0.10 | Rule targeting accuracy |
| T3.5 Agent configuration quality | 0.15 | Agent effectiveness |
| T3.6 MCP configuration | 0.15 | External tool integration |
| T3.7 Environment variable documentation | 0.10 | Setup completeness |

## T3.1 Directory References

Extract directory paths mentioned in CLAUDE.md using three sources:

1. **Slash-terminated paths** in text (e.g., `src/api/`, `tests/`, `db/migrations/`)
2. **Tree diagram characters** (`├──`, `└──`, `│`) — parse tree structure to construct nested paths
3. **Inline comments** listing subdirectories (e.g., `# hub/, motion/`) — combine with parent path from the tree line

For tree diagram parsing, example:
```
├── components/   # hub/, motion/, solutions/
```
This produces three paths to validate: `components/hub/`, `components/motion/`, `components/solutions/`.

For each extracted path, check if the directory actually exists in the project.

- No directory paths mentioned in CLAUDE.md → **SKIP**
- All mentioned directories exist → **PASS**
- Most exist, 1–2 missing → **PARTIAL** — list the specific missing paths
- Many missing → **FAIL** — list the directories mentioned but not found

## T3.2 CLAUDE.md Length

Count the lines in CLAUDE.md.

- Under 200 lines → **PASS**
- 200–300 lines → **PARTIAL** — "Consider splitting into `.claude/rules/` files"
- Over 300 lines → **MINIMAL** — "Strongly recommend splitting — long CLAUDE.md reduces effectiveness"

### Conditional Suggestion

If CLAUDE.md is over 150 lines and no `.claude/rules/` directory exists → suggest: "Consider extracting domain-specific rules into `.claude/rules/` files for better organization."

## T3.3 Command Availability

Check documented commands in CLAUDE.md against the project in two stages:

**Stage 1 — Manifest existence** (existing check):
- `npm`/`pnpm`/`yarn` commands → `package.json` exists
- `cargo` commands → `Cargo.toml` exists
- `go` commands → `go.mod` exists
- `python`/`pip` commands → `requirements.txt` or `pyproject.toml` exists

**Stage 2 — Tool config verification** (new):
If CLAUDE.md documents specific tool commands, check that the tool's config file exists:

| Documented command | Config file check |
| --- | --- |
| `lint` / `eslint` | `eslint.config.*` or `.eslintrc.*` exists |
| `test` / `vitest` / `jest` | `vitest` or `jest` in devDependencies |
| `build` / `next build` | `next.config.*` or build tool config exists |
| `typecheck` / `tsc` | `tsconfig.json` exists |

Scoring:
- No tool-specific commands referenced in CLAUDE.md → **SKIP**
- All referenced tool manifests and configs found → **PASS**
- Manifest exists but tool config missing → **PARTIAL** — "CLAUDE.md references `{command}` but `{config}` not found"
- Manifest missing → **FAIL** — "CLAUDE.md references `{tool}` but `{manifest}` not found"

## T3.4 Rules Path Validation

If `.claude/rules/` directory exists, read each rule file. If a rule has a `paths:` field in its frontmatter, check that at least one matching file exists using Glob.

- All paths match → **PASS**
- No rules directory → **SKIP**
- Some paths have no matches → **PARTIAL** — list the rules with unmatched paths

## T3.5 Agent Configuration Quality

If `.claude/agents/` directory exists with agent files:

1. Check that each agent has a `model:` field in its YAML frontmatter
2. Check that each agent has at least a Scope section defining its boundaries
3. Check if all agents use the same model (no diversity)

Scoring:
- All agents have model + scope, and model diversity present → **PASS**
- Some agents lack model or scope → **PARTIAL** — list which agents need improvement
- All agents use the same model → **PARTIAL** — "All agents use `[model]`. Consider `haiku` for exploration, `opus` for review tasks"
- No agents directory → **SKIP**

### Conditional Suggestions

- If more than 3 distinct top-level source directories → suggest: "Consider creating specialized agents for different areas."
- If all agents use the same model → suggest: "Consider differentiating models — `haiku` for exploration, `opus` for review tasks."

## T3.6 MCP Configuration

Check if `.mcp.json` exists at the project root.

If the project uses databases (check for `pg`, `prisma`, `knex`, `sequelize`, `mongoose` in dependencies) or external APIs:
- `.mcp.json` exists with relevant servers → **PASS**
- `.mcp.json` exists but doesn't cover detected tools → **PARTIAL**
- No `.mcp.json` but database/API dependencies detected → **MINIMAL** — "Consider adding a `.mcp.json` with a matching MCP server"
- No `.mcp.json` and no database/API dependencies → **SKIP**

## T3.7 Environment Variable Documentation

Scan these files for environment variable references (`${VAR}` or `$VAR` patterns):
- `.npmrc`
- `.env.example`, `.env.local.example`
- `docker-compose.yml`, `docker-compose.yaml`
- `Dockerfile`

Source code scanning (`process.env.X`, `os.environ`) is intentionally excluded — too broad and would significantly increase audit time. CI config files (`.github/workflows/`) are also excluded as their env vars are typically CI-scoped, not local development prerequisites.

If environment variable references are found, check if CLAUDE.md documents setup instructions for those variables.

- No scan target files or no env var references → **SKIP**
- Env vars found and documented in CLAUDE.md → **PASS**
- Env vars found, partially documented → **PARTIAL** — list undocumented variables
- Env vars found, not documented at all → **FAIL** — "Environment variables found in `{file}` but not documented in CLAUDE.md"
