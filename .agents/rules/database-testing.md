# Database Testing & Schema Isolation Rules

These rules define database management, port conflict resolution, and hermetic testing standards for PostgreSQL and Alembic in the Powercord Ecosystem.

---

## 1. Database Provisioning & Port Management

* **Dev Database Port (`5433`)**: The local PostgreSQL dev container (`powercord-pg-dev`) runs on port `5433`.
* **Port Conflict Prevention**:
  * Before executing upstream test suites on the host, stop running downstream containers (e.g., `docker compose down` in downstream repo) to release port `5433`.
  * Before restarting downstream containerized stacks (`just rebuild-target`), teardown any standalone upstream dev container (`just _teardown-dev-db` in `powercord/`).
* **Docker Networking Fallback**: If `powercord-pg-dev` is unreachable via `localhost:5433` due to disabled IPv4 forwarding (`WARNING: IPv4 forwarding is disabled`), recreate the container in `--network host` mode connecting via `localhost:5432` with `POWERCORD_DB_HOST=localhost:5432`.
* **Credential Alignment**: Default dev credentials are user `powercord` / password `test_pass`. Export `POWERCORD_POSTGRES_USER=powercord` and `POWERCORD_POSTGRES_PASSWORD=test_pass` when provisioning manually.
* **Volume Password Cache**: If credentials change, remove the volume (`docker volume rm powercord_pg_dev_data`) and rebuild to force PostgreSQL re-initialization.

---

## 2. Testing Isolation & Alembic Conformance

* **Test Teardown & Row Cleanups**: Every test inserting database records must clean up rows during fixture teardown to prevent state leakage.
* **Alembic Column Type Conformance**: Ensure SQLModel column types match Alembic migrations exactly (e.g. matching String/Text lengths with VARCHAR/Text columns) to avoid autogenerate drift.
* **Hermetic Connection Pooling (`NullPool`)**: Pytest `conftest.py` engines must use `NullPool` (disabling pooling) and explicitly dispose engines/connections inside fixture teardowns to prevent PostgreSQL deadlocks.
* **Pytest Concurrency & Deadlocks**: Never run multiple `pytest` sessions concurrently. Run `python -m app.common...` or the encapsulated `kill_stale_tests.py` script if test processes hang.
* **Extension Table Teardown Isolation**: When executing cleanup on optional extension tables (e.g. `honeypot_channels`), verify table existence via `inspect(bind).has_table(...)` and ensure `session.rollback()` is called in exception blocks to avoid transaction abort crashes (`InterfaceError: in failed transaction block`).
* **First-Load Testing**: When testing fresh initialization or onboarding logic, drop the database volume (`docker compose down -v`) and rebuild (`just rebuild-target`) to ensure pre-existing rows do not bypass first-load paths.
