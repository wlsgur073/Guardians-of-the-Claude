# STARTER PATH

For new or empty projects. Generates a minimal 5-section CLAUDE.md and basic settings.

## Phase 1S: Skip Analysis

There are no files to scan. Skip project analysis entirely. Use the language/framework defaults from the user's answers as your baseline.

## Phase 2S: Ask Questions

Ask the following questions **one at a time**.

1. **Project type and language** — Ask what kind of project and what language/framework:
   > "What are you building, and with what language/framework?"
   >
   > Project type: (a) Web API / backend (b) Frontend web app (c) CLI tool (d) Library / package (e) Other
   >
   > Then ask which language/framework. Offer common choices based on their answer:
   > - Web API: Node.js/Express, Python/FastAPI, Go, Java/Spring, etc.
   > - Frontend: React, Vue, Next.js, Svelte, etc.
   > - CLI: Node.js, Python/Click, Go/Cobra, Rust/Clap, etc.
   > - Library: Node.js, Python, Go, Rust, etc.

2. **Project description** — Ask for a 1-2 sentence description of what the project does. This becomes the `# Project Overview` content.

3. **Build, run, and test commands** — Suggest sensible defaults based on Question 1, then ask the user to confirm or customize:

   | Language | build | dev | test | lint |
   |----------|-------|-----|------|------|
   | Node.js | `npm install` | `npm run dev` | `npm test` | `npm run lint` |
   | Python | `pip install -e .` | `uvicorn main:app --reload` | `pytest` | `ruff check .` |
   | Go | `go build ./...` | `go run .` | `go test ./...` | `golangci-lint run` |
   | Rust | `cargo build` | `cargo run` | `cargo test` | `cargo clippy` |
   | Java/Spring | `./mvnw compile` | `./mvnw spring-boot:run` | `./mvnw test` | — |

   > "Here are the standard commands for [chosen framework]. Are these correct, or would you like to customize them?"

4. **Code style** — Suggest the standard conventions for the chosen language, then ask:
   > "Should I use the standard [language] conventions, or do you have specific preferences? (indentation, naming, formatting)"

## Phase 3S: Generate Files

Create files based on user answers. Follow the generation rules in `references/best-practices.md`.

### Generate:

**`CLAUDE.md`** with 6 sections:

```
# Project Overview        ← user's description + language/framework from Q1-Q2
## Build & Run            ← exact commands from Q3
## Testing                ← test commands from Q3
## Code Style & Conventions ← from Q4, only rules that differ from language defaults
## Development Approach    ← iterative self-refinement rules (see below)
## Important Context      ← note that this is a new project; any architectural decisions mentioned
```

The **Development Approach** section must include these rules:

```
## Development Approach
- When a request is vague or ambiguous, do not start implementing immediately
- First, critically analyze the request: identify assumptions, missing context, and possible interpretations
- Present your analysis and ask targeted clarifying questions before writing code
- After clarifying, outline your approach briefly and get confirmation before proceeding
```

**`.claude/settings.json`**:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [],
    "deny": []
  }
}
```

- `allow`: add test, lint, and build commands from Q3 (e.g., `"Bash(npm test)"`, `"Bash(npm run lint)"`)
- `deny`: add `"Read(.env)"`, `"Read(.env.*)"` as sensible defaults

**`.gitignore`** — append this line if not already present:

```
.claude/settings.local.json
```

Do NOT generate `.claude/rules/`, hooks, agents, or skills on the starter path.
