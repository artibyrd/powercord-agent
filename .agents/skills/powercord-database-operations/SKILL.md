---
name: powercord-database-operations
description: >-
  Use when creating, modifying, or debugging PostgreSQL database schemas, Alembic migrations,
  SQLModel models, connection pooling, backup/restore, or running DB administration tasks.
---

# Powercord Database Operations

Guidance on administering PostgreSQL, authoring SQLModel schemas, and running Alembic migrations.

---

## 1. Quick Recipes

* **Start Local Dev Database**:
  ```bash
  just _ensure-db
  ```
* **Run Database Migrations**:
  ```bash
  just db-upgrade
  ```
* **Inspect Migration Heads**:
  ```bash
  poetry run alembic heads
  ```
* **Check Tables & Row Counts**:
  ```bash
  python3 .agents/skills/powercord-database-operations/scripts/check_tables.py
  ```
* **Clear Stale Locks**:
  ```bash
  python3 .agents/skills/powercord-database-operations/scripts/clear_pg_locks.py
  ```

---

## 2. Deep References

* [Alembic Migrations](references/alembic-migrations.md) — Multi-branch migration design and CLI revision commands.
* [Schema Design & SQLModel](references/schema-design.md) — Column type conformance, JSON fields, and connection pooling.
* [Database Testing Rules](../../rules/database-testing.md) — Port 5433 conflict management and teardown isolation.
