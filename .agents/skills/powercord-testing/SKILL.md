---
name: powercord-testing
description: >-
  Testing and QA skill for the Powercord ecosystem. Use when writing, running, or debugging
  tests for the server, client, or extensions, or when evaluating code quality before a commit.
---

# Powercord Testing & Quality Assurance

Standards for running test suites, mocking external APIs, and preventing deadlocks.

---

## 1. Quick Recipes

* **Run Upstream Test Suite**:
  ```bash
  cd powercord && poetry run pytest
  ```
* **Run with Coverage**:
  ```bash
  cd powercord && poetry run pytest --cov=app
  ```
* **Kill Orphaned Pytest Processes**:
  ```bash
  python3 .agents/skills/powercord-testing/scripts/kill_stale_tests.py
  ```
* **Lint & Format**:
  ```bash
  poetry run ruff check --fix . && poetry run ruff format .
  ```

---

## 2. Deep References

* [Mocking Guidelines](references/mocking-guidelines.md) — Hermetic mocking, local import patch paths, and schema matching.
* [CI/CD & Cloud Build](references/ci-cd-cloudbuild.md) — Cloud Build sidecar database configuration.
* [Database Testing Rules](../../rules/database-testing.md) — `NullPool` fixture teardowns and port management.
