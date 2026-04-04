---
date: 2026-04-04
scenario: python-fastapi-existing
template_version: v2.3.0
skill: generate
run_count: 1
scores:
  accuracy: [5]
  customization: [5]
  completeness: [5]
  conciseness: [4]
  best_practices: [5]
average: 4.8
verdict: excellent
---

# python-fastapi-existing -- /generate Evaluation (2026-04-04)

## Summary

1 run completed for an EXISTING Python/FastAPI project (has app/models/, app/routes/, tests/, .gitignore, requirements.txt -- but no Claude Code config). Average 4.8 (excellent). Accuracy, Customization, Completeness, and Best Practices all score 5/5. Conciseness docked to 4/5 for a minor advisory addition.

## Run Details

### Run 1

**Scores:** Accuracy 5 | Customization 5 | Completeness 5 | Conciseness 4 | BP 5

**Observations:**
- All commands are copy-paste correct: `pip install -r requirements.txt`, `uvicorn app.main:app --reload`, `pytest` -- none reference packages not in requirements.txt
- `pytest --cov` correctly omitted since pytest-cov is not in requirements.txt; instead a note says "No coverage tool is currently installed -- add pytest-cov to requirements.txt if needed"
- All referenced directories (`app/models/`, `app/routes/`, `tests/`) confirmed to exist in the project -- no phantom paths
- `GET /health` endpoint mentioned by name with its exact return value `{"status": "ok"}`
- App title "MyApp" referenced from the actual `FastAPI(title="MyApp")` constructor in app/main.py
- TestClient + httpx test pattern specifically called out (grounded in actual tests/test_main.py)
- Ruff/linter correctly noted as "not configured yet" rather than assumed present
- "Project Structure" section added beyond the 6 starter sections -- justified for an existing project with real directories, but is a deviation from the strict starter template spec
- The "consider adding ruff" advisory in Important Context is mildly prescriptive -- could be omitted to stay purely descriptive
- settings.json has correct `$schema`, allow list (pytest, pip install, uvicorn), and deny list (.env, .env.*)
- .gitignore correctly appended `.claude/settings.local.json` without overwriting the existing `.env` entry
- CLAUDE.md is 45 lines -- well within 200-line limit

## Cross-Run Patterns

- Single run; no cross-run variance to analyze
- The "existing project" scenario is inherently stronger on Customization because real directories and endpoints exist to reference
- Phase 2.5S scan is the critical differentiator -- reading actual source files prevents the phantom path/command issues seen in naive generation

## Improvements Identified

- [ ] Conciseness: The "consider adding ruff" note in Important Context is advisory rather than factual -- consider moving such suggestions to a separate "Next Steps" callout or omitting from CLAUDE.md entirely (CLAUDE.md should describe what IS, not what SHOULD BE)
- [ ] Template alignment: The "Project Structure" section is not part of the 6-section starter spec but IS part of the advanced spec -- the starter template in `plugin/skills/generate/templates/starter.md` could be updated to include Project Structure as an optional 7th section when source directories exist
- [ ] settings.json allow list could include `Bash(pytest -v)` and `Bash(pytest tests/*)` as common test invocation variants

## LLM Context Note

> For existing Python/FastAPI projects, the Phase 2.5S scan is essential: reading requirements.txt prevents phantom tool commands (pytest-cov, ruff), and reading the file tree prevents phantom directory references. The key "existing vs new" difference is that real directories (app/models/, app/routes/) and real endpoints (GET /health) exist to reference, producing higher Customization scores. One area for improvement: CLAUDE.md should describe the project as-is without advisory "consider adding X" suggestions -- those belong in a /generate wrap-up message, not in the persistent config file.

## Comparison with Previous Eval

Previous eval (python-fastapi-new, same date) scored 5.0 average. The "existing" scenario scores 4.8, docked only for a minor conciseness issue (advisory content in Important Context). The existing scenario naturally produces stronger customization grounding since real code structures exist to reference.
