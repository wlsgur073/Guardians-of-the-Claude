# Generation Best Practices

Follow these rules when generating configuration files.

- **Be specific and verifiable** — "Use 2-space indentation" not "Format code properly"
- **Omit obvious information** — don't state what Claude can infer from reading the code
- **All commands must be copy-pasteable** — use actual project commands, not placeholders
- **Use actual directory names** — reference the project's real structure, not generic examples
- **Verify paths exist before referencing** — before mentioning any file or directory in CLAUDE.md (e.g., `app/models/`, `src/lib/`), confirm it exists with a file listing. Do not assume standard framework directories exist just because they are conventional
- **Verify command dependencies** — before suggesting a command that requires a non-core package (e.g., `pytest --cov`, `eslint`), check the dependency manifest (requirements.txt, package.json, Cargo.toml, etc.) to confirm the package is installed. If it is not listed, either omit the command or explicitly note it requires additional installation
- **Include project-specific details** — reference at least one concrete detail from the actual source code (e.g., a specific endpoint, model, or entry point) to demonstrate the output is tailored to this project, not a generic template for the framework
- **Document what IS, not what SHOULD be** — CLAUDE.md describes the project's current state. Do not add prescriptive suggestions like "consider adding ruff" or "you should set up ESLint". Tool recommendations belong in `/audit` suggestions, not in generated configuration
- **Note absent standard tools** — if a standard tool is absent for the project type (test runner, linter, formatter), note it in Important Context so Claude does not assume it exists (e.g., "No test runner configured" for a C project without CTest)
- **CLAUDE.md must stay under 200 lines** — be concise
- **Merge, don't overwrite** — if a config file already exists, merge new content in
- **Skills should use `$ARGUMENTS`** — if the skill accepts parameters, parse them from `$ARGUMENTS` in Step 1 instead of asking the user
- **Skills should bundle reference files** — when a skill needs project context (conventions, examples), put them in a `references/` directory alongside SKILL.md
- **Hooks should use `statusMessage`** — every hook entry must include a `statusMessage` so the user sees feedback while it runs
- **Security rules should reference detected patterns** — don't generate generic "never do X" rules; reference the actual auth middleware, validation library, or secrets management the project uses
- **Agent model comments must explain the choice** — every agent's `model:` field should have a YAML comment explaining why that model was selected (e.g., `# opus: security review requires deep analysis`)
- **Advanced features use multi-select** — let the user pick multiple options at once for independent features; don't force one-at-a-time selection
