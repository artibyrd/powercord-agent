---
name: powercord-ecosystem
description: >-
  Use when making architectural changes to the Powercord server, client, or extensions,
  or when testing code in a locally installed project directory without contaminating source repositories.
---

# Powercord Ecosystem Architecture & Workflow

Powercord consists of a centralized backend server framework, a Flet-based UI companion client, and a decoupled extension ecosystem. Development adheres to strict source-to-downstream isolation.

---

## 1. Repository Structure

1. **`powercord`** (Server Source): Core framework, FastAPI routes, FastHTML dashboard views, Nextcord Discord bot, and Alembic migrations.
2. **`powercord-client`** (Client Source): Companion desktop UI built with Flet and HTTPX.
3. **`powercord-extensions/*`** (Server Extensions): Standalone server-side packages (e.g. `honeypot`, `midi_library`).
4. **`powercord-client-extensions/*`** (Client Extensions): Standalone UI companion extensions (e.g. `midi_library_client`).
5. **`powercord-downstream-server`** (Staging Testbed): Containerized integration target for testing.

---

## 2. Core Development Workflow

1. **Edit Source Repositories**: Author and verify changes inside upstream source repos (`powercord/`, `powercord-client/`, `powercord-extensions/`).
2. **Verify Upstream**: Run tests locally in the source repo using `just test` or `poetry run pytest`.
3. **Submit for Human Review**: Present changes for human code review and commit.
4. **Reconcile Downstream**: Once committed upstream, sync the downstream deployment via `/reconcile-downstream-server`.

---

## 3. Deep References

For in-depth architectural specifications, see the references:
* [Auth Architecture](references/auth-architecture.md) — Dual-layer auth, beforeware, and `get_admin_guilds()`.
* [Devkit Recipes](references/devkit-just.md) — `devkit.just` database auto-provisioning and port 5433 handling.
* [Dependency Matrix](references/dependency-matrix.md) — Exact dependency bounds across server and client.
* [Failure Patterns](references/failure-patterns.md) — Troubleshooting client caching, Alembic drift, and port locks.
