---
name: powercord-testing
description: >
  Testing and QA skill for the Powercord ecosystem. Use when writing, running,
  or debugging tests for the server, client, or extensions, or when evaluating
  code quality before a commit.
---

# Powercord Testing & QA

## Overview

This skill covers the full testing and quality-assurance workflow for the
Powercord server, client, and extension projects. It describes the test
taxonomy, database isolation strategy, extension standalone testing, mocking
requirements, performance testing guidelines, coverage targets, and common
anti-patterns to avoid.

## When to Use

- Writing or modifying any test (unit, integration, extension).
- Running the QA pipeline (`just qa`) or individual quality commands.
- Debugging test failures related to database state or mocking.
- Evaluating coverage or preparing a commit for review.
- Setting up extension standalone test harnesses.

## QA Pipeline

| Command | What it does |
|---|---|
| `just qa` | lint → format → type-check → test (full gate) |
| `just test` | Unit tests only (default) |
| `just test --type all` | Unit + integration tests |
| `just test --type integration` | Integration tests only |
| `just coverage` | Run tests with coverage report |
| `just verify-dashboard` | Dashboard-specific integration tests |
| `just lint [--fix]` | `ruff check` (pass `--fix` to auto-fix) |
| `just format [--fix]` | `ruff format` (pass `--fix` to auto-fix) |
| `just check` | `mypy` type checking |

### Pre-Commit Requirement

Before presenting any changes for review, **always** run:

```bash
poetry run ruff check --fix . && poetry run ruff format .
```

## Test Taxonomy

### Unit Tests — `tests/unit/`

- Marker: `@pytest.mark.unit`
- Fast, no external services, all I/O mocked.

### Integration Tests — `tests/integration/`

- Marker: `@pytest.mark.integration`
- Hit a real test database (`powercord_test`) and may exercise HTTP endpoints.
- Require Docker PostgreSQL (see Database Test Isolation).

### Extension Tests — `tests/extensions/`

- Validate extension behaviour against the core server API.
- May also live inside individual extension repos (see Extension Standalone Testing).

### Client Tests

In the **powercord-client** repo, `just test` runs `pytest tests src/extensions`.

## Database Test Isolation

- **Test DB**: `powercord_test` — auto-provisioned by `_ensure-db`, which is a
  dependency of `just test`. A Docker PostgreSQL 15 container runs on **port 5433**.
- Tables are **dropped and recreated per session**.
- Use `NullPool` and **explicit engine disposal** in fixtures.
- **SAVEPOINT rollbacks do not work** — some application code creates its own
  sessions directly from the engine, bypassing the test transaction.
- **Hermetic fixtures**: always clean up inserted rows in teardown.
- **Docker networking fallback**: if IPv4 forwarding is disabled, use
  `--network host` and connect via `localhost:5432` instead.

## Extension Standalone Testing

Extensions can run tests independently of the main server checkout:

1. Set `POWERCORD_PATH` env var **or** place the extension two directories below
   the server root so `../../powercord` resolves.
2. The extension `conftest.py` loads credentials from the core `.env`.
   Fallback defaults: `user=powercord`, `password=test_pass`.
3. Recipe resolution uses `devkit.just` from the core repo.

## Writing Tests

### Unit Tests

- Mock all external I/O (DB, HTTP, filesystem).
- Keep each test focused on a single behaviour.

### Integration Tests

- Depend on `_ensure-db` (handled automatically via `just test`).
- Use `NullPool` + dispose engines in fixture teardown.
- Assert on DB state, not just return values.

### Extension Tests

- Mirror the extension's public API surface.
- Use the standalone testing setup described above when working outside the
  monorepo.

## Mocking Requirements

- **All loopback HTTP requests must be fully mocked** — this includes bot API
  calls and sprocket API calls. Never let a test make a real network request.
- Prefer `unittest.mock.patch` or `pytest-mock` fixtures scoped to the test.

## Performance Testing

- Use **comparative bounds**, not strict timing assertions (e.g., "≤ 2× baseline"
  rather than "< 50 ms").
- Strict max-execution-time assertions are fragile in CI and are an anti-pattern.

## Coverage

- **Target**: ≥ 80 % overall.
- **Documented exclusions**:
  - `db_tools.py` — ~23 % coverage (heavy CLI/interactive code).
  - `extension_manager.py` — ~56 % coverage (dynamic plugin loading).

## Cache Testing

Use **DB state checksums** as `TTLCache` keys so cache invalidation is
deterministic and testable without sleeps or time manipulation.

## Common Anti-Patterns

| Anti-pattern | Why it's bad | Fix |
|---|---|---|
| Naming the FastAPI instance `test_app` | Pytest tries to collect it as a test | Use `app` or `application` |
| Strict max execution time assertions | Flaky in CI under load | Use comparative bounds |
| Missing DB teardown in fixtures | Leaks state between tests | Always clean up rows + dispose engine |
| Skipping `NullPool` | Connections leak across tests | Always set `poolclass=NullPool` |
| Un-mocked HTTP to bot/sprocket API | Tests break without network, or hit prod | Fully mock all loopback HTTP |
