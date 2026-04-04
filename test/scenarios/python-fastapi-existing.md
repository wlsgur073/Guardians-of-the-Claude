---
id: python-fastapi-existing
language: Python
framework: FastAPI
state: existing
phase: 1
priority: high
fixture: python-fastapi
---

# Python FastAPI — Existing Project

## Project Description
An existing FastAPI REST API project with established source structure including models, routes, and configuration files.

## Fixture Contents
- main.py
- requirements.txt
- .gitignore
- app/models/
- app/routes/
- app/schemas/

## /generate Evaluation Focus
- Should detect existing patterns and not overwrite them
- Merge approach for configuration (append, not replace)
- Recognize existing directory structure depth (models/, routes/, schemas/)
- Preserve existing coding conventions

## /audit Evaluation Focus
- Recognize existing structure depth and project maturity
- Test command (pytest) detection even without existing tests/ directory
- Security suggestions appropriate for an established codebase
