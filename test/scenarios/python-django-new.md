---
id: python-django-new
language: Python
framework: Django
state: new
phase: 1
priority: medium
fixture: python-django
---

# Python Django — New Project

## Project Description
A new Django project with Django REST Framework for building a web API, created via django-admin startproject.

## Fixture Contents
- manage.py
- requirements.txt
- myproject/settings.py
- myproject/urls.py
- myproject/wsgi.py

## /generate Evaluation Focus
- manage.py commands (runserver, migrate, createsuperuser, collectstatic)
- Django-specific security guidance (CSRF protection, SECRET_KEY handling, DEBUG=False for production)
- Migration commands (makemigrations, migrate)
- Django app structure awareness

## /audit Evaluation Focus
- Django management commands detection (manage.py test, manage.py runserver)
- Middleware security suggestions (SecurityMiddleware, CSRF, session)
- Correct identification of Django + DRF as the framework stack
