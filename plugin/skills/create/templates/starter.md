# STARTER PATH

For new or empty projects. Generates a minimal 5-section CLAUDE.md and basic settings.

## Phase 1S: Quick Check Before Skipping Analysis

Before skipping analysis, do a quick search for dependency manifests (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `Gemfile`) and source code files (`*.ts`, `*.js`, `*.py`, `*.go`, `*.rs`, `*.java`).

**Safety check (MANDATORY):** If dependency manifests OR source code files are found, you MUST tell the user:

> "I noticed this project already has source code and/or dependencies (e.g., [detected files]). The Advanced path can auto-detect your setup and generate more complete configuration (rules, hooks, agents, skills). Would you like to switch to the Advanced path, or continue with Starter?"

If the user switches, follow the ADVANCED PATH (read `templates/advanced.md`). If they continue, proceed with Phase 2S below using the language/framework defaults from the user's answers as your baseline.

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
   | ---------- | ------- | ----- | ------ | ------ |
   | Node.js | `npm install` | `npm run dev` | `npm test` | `npm run lint` |
   | Python | `pip install -r requirements.txt` | `uvicorn main:app --reload` | `pytest` | `ruff check .` |
   | Go | `go build ./...` | `go run .` | `go test ./...` | `go vet ./...` |
   | Rust | `cargo build` | `cargo run` | `cargo test` | `cargo clippy` |
   | Java/Maven | `mvn compile` | `mvn spring-boot:run` | `mvn test` | — |
   | C/CMake | `cmake -B build && cmake --build build` | `./build/<binary>` | `ctest --test-dir build` | — |
   | C++/CMake | `cmake -B build && cmake --build build` | `./build/<binary>` | `ctest --test-dir build` | — |

   **Note:** If a Maven/Gradle wrapper exists (`mvnw`, `gradlew`), use the wrapper (`./mvnw`, `./gradlew`) instead of the bare command. Verify wrapper existence during Phase 2.5S scan before suggesting.

   > "Here are the standard commands for [chosen framework]. Are these correct, or would you like to customize them?"

4. **Code style** — Suggest the standard conventions for the chosen language, then ask:
   > "Should I use the standard [language] conventions, or do you have specific preferences? (indentation, naming, formatting)"

## Phase 2.5S: Pre-Generation Scan

Before writing any files, silently scan the project to ground your output in reality:

1. List all files and directories in the project (use `find . -maxdepth 3 -not -path './.git/*'` or equivalent)
2. Read the dependency manifest (requirements.txt, package.json, Cargo.toml, go.mod, pom.xml) to know exactly what packages are available
3. Skim the main source file(s) to note actual endpoints, routes, commands, or entry points

Use these findings in Phase 3S — reference only directories that exist, suggest only commands for installed packages, and mention at least one concrete detail from the actual code.

**Dependency check:** If any command confirmed in Q3 references a tool not found in the dependency manifest (e.g., `ruff` not in `requirements.txt`, `eslint` not in `package.json`), tell the user before generating: "`[tool]` is not listed in your dependencies — include it anyway, or skip?" Adjust the commands based on their answer.

## Phase 3S: Generate Files

Create files based on user answers AND the scan results from Phase 2.5S. Follow the generation rules in `references/best-practices.md`.

### Generate

**`CLAUDE.md`** with 6 sections:

```markdown
# Project Overview        ← user's description + language/framework from Q1-Q2
## Build & Run            ← exact commands from Q3
## Testing                ← test commands from Q3
## Code Style & Conventions ← from Q4, only rules that differ from language defaults
## Development Approach    ← iterative self-refinement rules (see below)
## Important Context      ← note that this is a new project; any architectural decisions mentioned
```

The **Development Approach** section must include these rules:

```markdown
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
- `deny`: add Essential deny patterns as sensible defaults: `"Read(./.env)"`, `"Read(./.env.*)"`, `"Edit(./.env)"`, `"Edit(./.env.*)"`, `"Write(./.env)"`, `"Write(./.env.*)"`, `"Read(./secrets/)"`, `"Edit(./secrets/)"`, `"Write(./secrets/)"`

**`.gitignore`** — if `.gitignore` exists, append this line if not already present. If `.gitignore` does not exist, create it with this line:

```gitignore
.claude/settings.local.json
```

Do NOT generate `.claude/rules/`, hooks, agents, or skills on the starter path.
