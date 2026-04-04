---
date: 2026-04-05
scenario: java-springboot-existing
template_version: v2.3.0
skill: generate
run_count: 1
scores:
  accuracy: [5]
  customization: [5]
  completeness: [5]
  conciseness: [5]
  best_practices: [5]
average: 5.0
verdict: excellent
---

# java-springboot-existing -- /generate Evaluation (2026-04-05)

## Summary

1 run completed for an EXISTING Java/Spring Boot 4.0.5 project (has controller layer, service layer stub, pom.xml, .gitignore -- but no Claude Code config or Maven wrapper). Average 5.0 (excellent). All five dimensions score 5/5. The Phase 2.5S scan is the key differentiator: reading pom.xml prevented phantom `./mvnw` commands, reading source files grounded references in actual classes and endpoints, and reading .gitignore enabled correct append behavior.

## Run Details

### Run 1

**Scores:** Accuracy 5 | Customization 5 | Completeness 5 | Conciseness 5 | BP 5

**Observations:**
- All commands use `mvn` (not `./mvnw`) -- correct since no Maven wrapper exists in the project; the starter template default of `./mvnw compile` was correctly overridden
- Spring Boot version 4.0.5 and GAV coordinates `com.example:myapp:0.1.0` both referenced from actual pom.xml
- `AppService` (`com.example.service.AppService`) explicitly called out as a business logic stub -- references the actual existing class
- `HelloController` endpoint `GET /hello` returning `"Hello, World!"` matches the source exactly
- Testing section correctly notes `spring-boot-starter-test` is absent from pom.xml rather than assuming `mvn test` works -- documents what IS, not what should be
- No linter/formatter assumed -- absence noted factually without prescriptive "consider adding" language
- Package structure `com.example.controller`, `com.example.service` referenced -- both confirmed to exist in the source tree
- settings.json allow list includes `mvn compile`, `mvn spring-boot:run`, `mvn package` -- all valid Maven goals; no test command included since no test framework exists
- .gitignore correctly appended `.claude/settings.local.json` to the existing `target/` entry -- merge, not overwrite
- CLAUDE.md is 35 lines -- well within the 200-line limit and tightly focused
- All 6 required starter sections present: Project Overview, Build & Run, Testing, Code Style & Conventions, Development Approach, Important Context

## Cross-Run Patterns

- Single run; no cross-run variance to analyze
- The "existing project" scenario with a service layer stub is a good test of whether generation references actual classes vs. generic framework boilerplate -- this run correctly referenced `AppService` by fully qualified name
- The absence of `mvnw` is the critical "existing project" trap: the starter template defaults to `./mvnw` for Java/Spring, and the scan must override this based on what actually exists in the filesystem

## Improvements Identified

- [ ] settings.json allow list could include `Bash(mvn test)` proactively -- even though no test framework exists yet, users will likely add `spring-boot-starter-test` and then wonder why `mvn test` is not permitted. Counter-argument: allowing a command that currently has no effect could be confusing
- [ ] The Testing section's "Add it before running `mvn test`" phrasing is borderline prescriptive -- could be reworded to "Currently no tests exist to run" for a purely factual tone
- [ ] No Project Structure section was generated -- for an existing project with real directories (`controller/`, `service/`), a brief structure section would add value. The starter template spec does not include it, but the advanced template does

## LLM Context Note

> For existing Java/Spring Boot projects, the Phase 2.5S scan must check for Maven wrapper presence (`mvnw`/`mvnw.cmd`) before defaulting to `./mvnw` commands -- use `mvn` when no wrapper exists. Reading pom.xml is critical: verify `spring-boot-starter-test` before suggesting `mvn test`, and note the exact Spring Boot parent version. Reference actual classes by fully qualified name (e.g., `com.example.service.AppService`) to demonstrate the output is grounded in the real codebase. For .gitignore, always append rather than overwrite -- existing entries like `target/` must be preserved.

## Comparison with Previous Eval

Previous eval (java-springboot-new, 2026-04-04) was for a NEW project scenario. This "existing" scenario differs in having real source files to reference (`AppService`, `HelloController`), producing stronger customization grounding. The key additional challenge is the absent Maven wrapper, which must override the template default. Both scenarios should score similarly on completeness and best practices, but the existing scenario has a higher bar for accuracy (must not hallucinate about the service layer's capabilities) and customization (must reference actual code, not just framework conventions).
