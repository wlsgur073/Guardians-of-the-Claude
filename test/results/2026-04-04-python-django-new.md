---
date: 2026-04-04
scenario: python-django-new
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

# python-django-new -- /generate Evaluation (2026-04-04)

## Summary

1 run completed using Phase 2.5S pre-generation scan + Phase 3S generation with best-practices.md rules. Average 5.0 (excellent). All five dimensions score 5/5. The output is grounded entirely in the actual project state -- no phantom directories, no uninstalled package commands, and concrete references to real configuration details.

## Run Details

### Run 1

**Scores:** Accuracy 5 | Customization 5 | Completeness 5 | Conciseness 5 | BP 5

**Observations:**
- All commands use `python manage.py` as the entry point (`runserver`, `migrate`, `test`, `createsuperuser`, `startapp`) -- correct for Django projects, not generic Python commands
- `requirements.txt` was read and confirmed only `django>=5.2.0` and `djangorestframework>=3.15.0` are installed; no phantom packages referenced (no `pytest`, `ruff`, `coverage` commands suggested as defaults)
- Phase 2.5S scan confirmed no app directories exist beyond `myproject/` config package; CLAUDE.md explicitly states "no Django apps exist yet; create them with `python manage.py startapp <name>`" instead of referencing phantom app directories
- Concrete details from actual source code referenced: `SECRET_KEY` insecure fixture value noted, `rest_framework` in `INSTALLED_APPS` confirmed, `/admin/` URL pattern from `myproject/urls.py`, SQLite database (`db.sqlite3`), `DJANGO_SETTINGS_MODULE` set to `myproject.settings`
- Security concern addressed: `SECRET_KEY` flagged as insecure fixture value needing replacement before deployment; `.env` and `.env.*` denied in settings.json
- All 6 required starter sections present: Project Overview, Build & Run, Testing, Code Style & Conventions, Development Approach, Important Context
- 41 lines total -- well within the 200-line limit with no filler content
- settings.json includes `$schema`, allow list (`manage.py test`, `manage.py test *`, `manage.py migrate`, `manage.py runserver`), and deny list (`.env`, `.env.*`)
- `.gitignore` created with `.claude/settings.local.json`
- Code Style section is Django/DRF-specific: recommends `path()` over `re_path`, class-based views with DRF `APIView`/`ViewSet`, PEP 8 naming conventions

## Cross-Run Patterns

- Single run; no cross-run variance to report
- The Phase 2.5S scan was decisive: reading `requirements.txt`, `settings.py`, and `urls.py` before generation prevented all common hallucination patterns (phantom test tools, nonexistent app directories, generic framework boilerplate)

## Improvements Identified

- [ ] Consider noting that `python manage.py test` uses Django's built-in test runner (unittest-based), and if the user later adds `pytest-django`, the test command section should be updated
- [ ] The allow list could include `Bash(python manage.py startapp *)` since app creation is the obvious next step for a new project
- [ ] A note about `DEBUG = True` being set could be added alongside the `SECRET_KEY` warning for deployment awareness

## LLM Context Note

> For Django new-project scenarios, the Phase 2.5S scan of `requirements.txt`, `settings.py`, and `urls.py` provides sufficient grounding to avoid all common hallucination patterns. Key checks: (1) verify no app directories exist beyond the config package before referencing any, (2) use `python manage.py` commands not generic Python commands, (3) confirm DRF is in `INSTALLED_APPS` before suggesting DRF patterns, (4) flag `SECRET_KEY` insecure fixture value. Django projects have a distinctive command interface (`manage.py`) that must be reflected throughout -- generic Python commands like `pytest` or `uvicorn` are incorrect unless explicitly present in the dependency manifest.
