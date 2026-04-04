# Scenario Matrix

## Coverage Rationale

This matrix covers **7 languages with their most popular frameworks**, across 2 project states (new, existing) for high-priority stacks. The goal is to test `/generate` and `/audit` skill quality across the most common real-world project types.

**Language selection criteria:** Stack Overflow Developer Survey and GitHub usage — C/C++, Python, Rust, Java, JavaScript/TypeScript, Go represent the majority of active development.

**State definitions:**
- **new** — Empty or scaffold-only project. No CLAUDE.md, no `.claude/` directory.
- **existing** — Has source code and dependencies but no Claude Code configuration.

---

## Phase 1: Initial Coverage (16 Scenarios)

| # | ID | Language | Framework | State | Priority | Fixture |
|---|----|----------|-----------|-------|----------|---------|
| 1 | python-fastapi-new | Python | FastAPI | new | High | python-fastapi |
| 2 | python-fastapi-existing | Python | FastAPI | existing | High | python-fastapi |
| 3 | python-django-new | Python | Django | new | Medium | python-django |
| 4 | javascript-nextjs-new | JS/TS | Next.js | new | High | javascript-nextjs |
| 5 | javascript-nextjs-existing | JS/TS | Next.js | existing | High | javascript-nextjs |
| 6 | javascript-express-new | JS | Express | new | Medium | javascript-express |
| 7 | rust-cli-new | Rust | CLI (clap) | new | High | rust-cli |
| 8 | rust-cli-existing | Rust | CLI (clap) | existing | Medium | rust-cli |
| 9 | java-springboot-new | Java | Spring Boot | new | High | java-springboot |
| 10 | java-springboot-existing | Java | Spring Boot | existing | Medium | java-springboot |
| 11 | c-cmake-new | C | CMake | new | High | c-cmake |
| 12 | c-cmake-existing | C | CMake | existing | Medium | c-cmake |
| 13 | cpp-cmake-new | C++ | CMake | new | High | cpp-cmake |
| 14 | go-web-new | Go | net/http | new | High | go-web |
| 15 | go-cli-new | Go | Cobra | new | Medium | go-cli |
| 16 | monorepo-new | Multi | Next.js + Express | new | Medium | monorepo |

### Priority Guide

- **High**: Most popular framework per language + new state. These represent the majority of first-time `/generate` usage.
- **Medium**: Secondary frameworks or existing-state variants. Important but lower frequency.

### Fixture Sharing

Multiple scenarios can share the same fixture. The difference between `new` and `existing` states is handled by `setup-scenario.sh`:
- **new**: Copies fixture as-is (no Claude Code config)
- **existing**: Copies fixture + adds pre-existing source files with more realistic project complexity

---

## Phase 2: Extended Coverage (Planned)

### Additional Frameworks

| Language | Framework | Rationale |
|----------|-----------|-----------|
| Python | CLI (Click/Typer) | Different project structure from web |
| Python | ML (numpy/pandas/jupyter) | Unique dependency and workflow patterns |
| JS/TS | React SPA (Vite) | Frontend-only, no server |
| Rust | Web (Axum) | Different from CLI projects |
| Rust | Library crate | No binary, different build/test patterns |
| Java | Gradle project | Alternative build tool to Maven |
| Kotlin | Spring Boot (Gradle) | Kotlin 2.3.x + Spring Boot 4.x, different build conventions from Java/Maven |
| C | Makefile | Traditional C build system (no CMake) |
| C++ | Conan + CMake | Package manager adds complexity |
| Go | Web (Gin/Echo) | Framework-based vs stdlib |

### Adversarial Scenarios

| ID | Description | Tests |
|----|-------------|-------|
| adversarial-no-package | No package manager, pure shell scripts | Graceful handling when no build tool detected |
| adversarial-bad-config | Pre-existing broken CLAUDE.md | `/generate` merge behavior with invalid config |
| adversarial-secrets | .env and credentials committed | `/audit` security detection, `/generate` protection rules |
| adversarial-multi-lang | 3+ languages in one repo (no monorepo tool) | Language detection priority and config scope |

### Monorepo Variants

| ID | Description |
|----|-------------|
| monorepo-turborepo | Turborepo with multiple packages |
| monorepo-nx | Nx workspace |
| monorepo-pnpm-workspace | pnpm workspaces |

---

## Coverage Tracking

Update this section after each eval cycle:

| Scenario | Last Tested | Avg Score | Verdict | Notes |
|----------|-------------|-----------|---------|-------|
| (filled after first eval cycle) | | | | |
