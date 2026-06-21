---
name: powercord-database-operations
description: >
  Use when creating, modifying, or debugging PostgreSQL database schemas,
  Alembic migrations, SQLModel models, trigram search, connection pooling,
  backup/restore, test-database isolation, or running DB admin commands
  (add-admin, api-key management) in the Powercord ecosystem.
---

# Powercord Database Operations

## Overview

Powercord uses **PostgreSQL 15** with the **SQLModel** ORM (SQLAlchemy + Pydantic),
**Alembic** for migrations, and **pg_trgm** for fuzzy search. Connection pooling is
configured in `app/common/alchemy.py`. Extensions maintain their own independent
Alembic migration branches under `app/extensions/<name>/alembic/versions/`.

## When to Use

Activate this skill when the task involves:

- Creating or modifying database models (`SQLModel` classes)
- Generating or editing Alembic migrations (core or extension)
- Adjusting connection pool settings
- Running database admin commands (`just add-admin`, `just add-api-key`, etc.)
- Export, import, or backup operations
- Writing or debugging tests that touch the database
- Trigram / fuzzy-search queries or GIN indexes
- GCP production database maintenance

## Justfile Quick Reference

| Command | Description |
|---|---|
| `just db-upgrade` | `alembic upgrade heads` — upgrades **all** branches (core + extensions) |
| `just db-revision "msg"` | `alembic revision --autogenerate -m "msg"` |
| `just db-export` | Export DB to SQL; flags: `--file "name.sql"`, `--migration` |
| `just db-import <file>` | Import a SQL dump |
| `just db-backup` | Manual backup (pg_dump → `.sql.gz`) |
| `just add-admin` | Create an admin user |
| `just remove-admin` | Remove an admin user |
| `just reset-admins` | Reset all admin accounts |
| `just add-api-key` | Generate a new API key |
| `just revoke-api-key` | Revoke an existing API key |
| `just list-api-keys` | List all active API keys |

The devkit provides `_ensure-db` — spins up a Docker PostgreSQL 15 instance on **port 5433**.

## Core vs Extension Migrations

Powercord uses a **fully decoupled multibase** layout:

- **Core** migrations live in `alembic/versions/` at the repo root.
- **Extension** migrations live in `app/extensions/<name>/alembic/versions/`.
- `just db-upgrade` runs `alembic upgrade heads` (plural) so every branch advances.
- Each extension manages its own Alembic `env.py` and version history — no cross-branch dependencies.

## Creating Migrations

1. Make your SQLModel changes in the relevant module.
2. Run `just db-revision "describe the change"`.
3. **Review the generated file** — autogenerate is not perfect:
   - Verify column types match the SQLModel field types exactly (see *Type Conformance* below).
   - Remove any no-op or duplicate operations.
4. Run `just db-upgrade` to apply.

### Type Conformance

SQLModel column types **must** match Alembic migration types exactly. A mismatch
(e.g., `sa.String` vs `sqlmodel.AutoString`) causes autogenerate to emit spurious
`alter_column` ops on every subsequent revision. Always check that the migration
uses the same type class the model declares.

## Applying Migrations

```bash
# Apply all pending migrations (core + extensions)
just db-upgrade

# Target a specific revision
alembic upgrade <revision_id>

# Downgrade one step
alembic downgrade -1
```

## Export / Import / Backup

### Manual Operations

```bash
just db-export                        # default export
just db-export --file "snapshot.sql"   # named export
just db-export --migration             # migration-compatible export
just db-import snapshot.sql            # import a dump
just db-backup                        # pg_dump → .sql.gz
```

### Automated Backups (BackupService)

- **Schedule**: APScheduler cron trigger at **03:00 UTC** daily.
- **Format**: `pg_dump` → `.sql.gz` (gzip-compressed).
- **Retention**: 7 days local.
- **GCS sync**: systemd timer at **04:00 UTC** pushes to Cloud Storage.

## Trigram Search

Fuzzy search uses `pg_trgm` with GIN indexes.

- **Builder**: `build_trigram_query()` in `app/db/search.py`.
- Always create a **GIN index** on columns used for trigram matching to avoid sequential scans.
- Example migration snippet:
  ```python
  op.create_index(
      "ix_my_table_name_trgm",
      "my_table",
      ["name"],
      postgresql_using="gin",
      postgresql_ops={"name": "gin_trgm_ops"},
  )
  ```

## Test Database Isolation

Tests run against a dedicated **`powercord_test`** database, fully isolated from development data.

### Key Mechanisms

- `conftest.py` forces `POWERCORD_POSTGRES_DB=powercord_test` via `os.environ`.
- `ensure_test_database()` in `app/common/testing.py` auto-provisions the DB if missing.
- Default test credentials: `user=powercord`, `password=test_pass` (set via `os.environ.setdefault`).
- Engine uses **`NullPool`** — no connection pooling in tests.
- Explicit engine disposal in teardown prevents PostgreSQL deadlocks.
- Tables are **dropped and recreated** at session start (not SAVEPOINT rollback) because
  some application code creates its own sessions outside the test transaction.

### Extension Standalone Testing

Extensions that run tests independently load credentials from the **core `.env` file**
and fall back to the defaults above if unavailable.

## Connection Pooling

Configured in `app/common/alchemy.py` with environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `POWERCORD_DB_POOL_SIZE` | 20 | Base number of persistent connections |
| `POWERCORD_DB_MAX_OVERFLOW` | 10 | Extra connections allowed above pool size |
| `POWERCORD_DB_POOL_TIMEOUT` | 30 | Seconds to wait for a connection before error |
| `POWERCORD_DB_POOL_RECYCLE` | 1800 | Seconds before a connection is recycled (30 min) |

### Cache Invalidation

When caching query results (e.g., `TTLCache`), hash **DB state** into cache keys — not
just `guild_id` or similar identifiers. This prevents serving stale data after writes.

## GCP Production Operations

On the deployed GCP instance, run DB commands inside the container:

```bash
docker exec <CONTAINER_ID> /app/.venv/bin/python -m <module> [args]
```

Override the DB host when connecting from within the container:

```bash
POWERCORD_DB_HOST=localhost:5432
```

Use `just` admin recipes (`add-admin`, `add-api-key`, etc.) locally only.
In production, invoke the equivalent Python modules directly via `docker exec`.

## Common Failure Patterns

| Symptom | Likely Cause | Fix |
|---|---|---|
| Autogenerate emits no-op `alter_column` | Type mismatch between SQLModel and migration | Align column type classes exactly |
| `TimeoutError` on DB access | Pool exhausted (`POOL_SIZE + MAX_OVERFLOW` reached) | Increase pool settings or audit connection leaks |
| Tests hang or deadlock | Pooled connections not released | Ensure `NullPool` and explicit `engine.dispose()` in teardown |
| `alembic upgrade` skips extension branch | Using `head` (singular) instead of `heads` | Use `just db-upgrade` which runs `alembic upgrade heads` |
| Stale cache after DB write | Cache key doesn't include DB state hash | Hash DB state into `TTLCache` keys |
| Extension tests fail with auth errors | Missing `.env` or wrong defaults | Ensure core `.env` is accessible; check `os.environ.setdefault` values |
| Migration drift after model rename | Alembic sees drop + create instead of rename | Manually edit migration to use `op.rename_table` / `op.alter_column` |
