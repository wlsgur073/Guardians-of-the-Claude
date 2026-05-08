---
title: "Sprint Contract"
description: "Scope contract for the current work cycle"
version: "1.0.0"
---

# Sprint Contract

This file defines the current scope boundary. Work not listed under In Scope
is outside this contract unless the user explicitly updates this file.

## In Scope

- **Task CRUD endpoints** — REST endpoints for create, read, update, and delete
  operations on Task entities, scoped to the authenticated user.
- **User authentication baseline** — Email/password signup and login, JWT access
  tokens with refresh-token rotation.
- **Task ownership rules** — Task records scoped to the authenticated user;
  cross-user access blocked at the repository layer.
- **Verification path** — Jest test coverage for endpoints, services, and
  ownership rules; minimum 80% line coverage in `src/services/`.

## Deferred

- **Comment entity** — Reason: requires nested resource design; deferred until
  Task CRUD is stable.
- **OAuth providers** — Reason: requires provider selection, callback security
  design, and separate secrets handling.
- **Email notifications** — Reason: depends on SMTP/provider setup and
  message-template decisions.
- **Real-time updates (WebSocket)** — Reason: belongs after core REST API
  ships; requires session affinity design.
