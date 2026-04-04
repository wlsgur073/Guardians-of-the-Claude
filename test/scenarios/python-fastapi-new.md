---
id: python-fastapi-new
language: Python
framework: FastAPI
state: new
phase: 1
priority: high
fixture: python-fastapi
---

# Python FastAPI — New Project

## Project Description
A new FastAPI REST API project with minimal scaffolding, including only a basic main.py entry point and requirements.txt.

## Fixture Contents
- main.py
- requirements.txt

## /generate Evaluation Focus
- uvicorn run command (e.g., `uvicorn app.main:app --reload`)
- pytest command for test execution
- FastAPI-specific security guidance (CORS configuration, input validation with Pydantic)
- Recommended app/ directory structure (routers, models, schemas)

## /audit Evaluation Focus
- Test command detection (pytest)
- Web framework security suggestions (CORS, authentication, input validation)
- Correct identification of FastAPI as the web framework
