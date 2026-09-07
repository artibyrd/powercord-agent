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

## 2. Core Development & PR Lifecycle

Development adheres to `inv-branch-pr-review-gate` and `inv-mk1-downstream-walkthrough-verification`:
1. **Feature Branch Isolation**: Never develop directly on `main`. Create a feature branch in affected source repos: `just branch feat/<name>`.
2. **Incremental Local Commits**: Commit incrementally on the feature branch: `just commit <msg>` (gated by `just check`).
3. **Downstream Integration Verification**: Sync changes downstream (`just ext-install`), rebuild Docker target (`just rebuild-target`), and verify live functionality locally on `http://localhost:5001/`.
4. **Push Branch & Open PR**: Push the feature branch and open a pull request via GitHub CLI: `just pr-create "<title>"`.
5. **Human Mk1 Review Gate**: Human reviewer inspects side-by-side diffs, runs interactive checks on the running local container, and approves/merges the PR on GitHub.
6. **Release Tagging on `main`**: Following PR merge, pull `main` and execute the release sequence: `just release <version> "<message>"`.

---

## 3. Deep References

For in-depth architectural specifications, see the references:
* [Auth Architecture](references/auth-architecture.md) — Dual-layer auth, beforeware, and `get_admin_guilds()`.
* [Devkit Recipes](references/devkit-just.md) — `devkit.just` database auto-provisioning and port 5433 handling.
* [Dependency Matrix](references/dependency-matrix.md) — Exact dependency bounds across server and client.
* [Failure Patterns](references/failure-patterns.md) — Troubleshooting client caching, Alembic drift, and port locks.
