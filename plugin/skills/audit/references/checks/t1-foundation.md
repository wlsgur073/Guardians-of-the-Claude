# T1 — Foundation Checks

These checks form the **Foundation Gate** — they determine what percentage of the Detail Score (Protection + Optimization) applies to the final score. A missing foundation item suppresses the entire score.

## Weights

| Item | Weight | Rationale |
| ------ | -------- | ----------- |
| T1.1 CLAUDE.md existence | 0.25 | Prerequisite for all configuration |
| T1.2 Test command | 0.35 | Highest-leverage single item |
| T1.3 Build command | 0.20 | Compile-time error checking |
| T1.4 Project overview | 0.20 | Context for Claude's understanding |

## T1.1 CLAUDE.md Existence

Check if `CLAUDE.md` exists at the project root or `.claude/CLAUDE.md`.

- Found → **PASS**
- Neither exists → **FAIL** — stop and recommend running `/guardians-of-the-claude:create` first. Do NOT proceed to T1.2 or any subsequent phase. Use the Early Halt output format (see output-format.md)

## T1.2 Test Command

Search CLAUDE.md for a test command (e.g., `npm test`, `pytest`, `go test`, `cargo test`, `dotnet test`, `mvn test`). This is the single highest-leverage item in any CLAUDE.md.

- Found and runnable → **PASS**
- Found but command may not work (e.g., references a tool not in dependencies) → **PARTIAL**
- Not found → **FAIL** — "Add a test command so Claude can verify its work"
- No application code in the project (documentation-only, template, or config-only repositories) → **SKIP**

## T1.3 Build Command

Search CLAUDE.md for a build/compile command (e.g., `npm run build`, `tsc`, `go build`, `cargo build`, `mvn package`).

- Found and runnable → **PASS**
- Found but manifest or tool not available (e.g., references `cargo build` but no `Cargo.toml`) → **PARTIAL**
- Interpreted language with no build step needed (Python, Ruby) → **SKIP**
- No application code in the project (documentation-only, template, or config-only repositories) → **SKIP**
- Not found for a compiled language → **FAIL** — "Add a build command for compile-time error checking"

## T1.4 Project Overview

Check if CLAUDE.md has a project description in the first 20 lines (a heading followed by text explaining what the project is/does).

- Clear description with language/framework mentioned → **PASS**
- Heading exists with some descriptive text but vague or too brief (under 10 words) → **PARTIAL**
- Heading exists but no descriptive text follows (title only), or only commands with no context → **FAIL** — "Add a brief project overview so Claude understands context"
