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
  cd powercord && just test --type unit
  # Or when invoking pytest directly against the dev container:
  POWERCORD_POSTGRES_PASSWORD=$(grep POWERCORD_POSTGRES_PASSWORD .env | cut -d= -f2) poetry run pytest tests/unit/<test_file>.py
  ```
* **Run with Coverage**:
  ```bash
  cd powercord && poetry run pytest --cov=app
  ```
* **Kill Orphaned Pytest Processes**:
  ```bash
  python3 powercord-agent/skills/powercord-testing/scripts/kill_stale_tests.py
  ```
* **Upstream Verification Before Downstream Reconciliation**:
  Verify all backend modifications by running `poetry run pytest` directly in upstream `powercord/` before reconciling changes into `powercord-downstream-server/`.
* **Lint & Format (Pre-Commit Across Modified Repos)**:
  Run across all modified repositories (`powercord/`, `powercord-client/`, `powercord-extensions/*/`, `powercord-client-extensions/*/`):
  ```bash
  poetry run ruff check --fix . && poetry run ruff format .
  ```

---

## 2. Deep References

* [Mocking Guidelines](references/mocking-guidelines.md) — Hermetic mocking, local import patch paths, and schema matching.
* [CI/CD & Cloud Build](references/ci-cd-cloudbuild.md) — Cloud Build sidecar database configuration.
* [Database Testing Rules](../powercord-database-operations/references/database-testing.md) — `NullPool` fixture teardowns and port management.
