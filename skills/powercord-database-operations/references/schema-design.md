# Database Schema Design Reference

Guidelines for SQLModel models, column constraints, and PostgreSQL extensions in Powercord.

---

## 1. SQLModel & PostgreSQL Conformance

* **Type Matching**: Ensure SQLModel model field definitions align with PostgreSQL column types:
  * String fields with length constraints map to `VARCHAR(N)` or `Text`.
  * JSON fields map to `JSONB` or `JSON` with appropriate serialization defaults.
* **Trigram Search Support**: For full-text search (e.g. MIDI library searches), ensure `pg_trgm` extension is enabled in migration initialization.
* **Connection Pooling**: Use `NullPool` in test harnesses (`conftest.py`) to prevent persistent connection leaks and pool exhaustion during automated test runs.
