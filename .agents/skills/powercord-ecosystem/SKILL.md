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

Development adheres to `inv-branch-pr-review-gate`, `inv-downstream-integration-testbed`, and `inv-mk1-downstream-walkthrough-verification`:
1. **Feature Branch Isolation & Semantic Naming**: Never develop directly on `main`. Create a feature branch in affected source repos: `just branch feat/<topic>`.
   - **Semantic Topic Names Only**: Branch names must describe the semantic feature or refactor (e.g., `feat/decompose-cog-views`, `feat/governance-ratchet`, `feat/align-baseline-manifest`).
   - **Zero Cross-Repo Version Coupling**: Never name a branch after the version number of a *different* repository (e.g., do not name an extension or client branch after core server's `v2.0.0`).
2. **Incremental Local Commits**: Commit incrementally on the feature branch: `just commit <msg>` (gated by `just check`).
3. **Downstream Integration Verification (Powercord vs. Credence)**:
   - Unlike Credence (which deploys dev previews to Cloud Run via GitHub Actions), Powercord runs on a single VM (`inv-single-vm-cost-ceiling`) with zero cloud preview URLs.
   - The downstream server (`powercord-downstream-server`) is the mandatory local integration sandbox.
   - Sync modified extensions downstream (`just ext-install`), rebuild the Docker container target (`docker compose up --build -d`), apply multi-head Alembic migrations, and verify live functionality locally on `http://localhost:5001/` before opening PRs.
4. **Push Branch & Open PR**: Push the feature branch and open a pull request via GitHub CLI: `just pr-create "<title>"`.
5. **Human Mk1 Review Gate**: Human reviewer inspects side-by-side diffs on GitHub, tests the locally running container, and approves/merges the PR.
6. **Release Tagging on `main`**: Following PR merge, pull `main` and execute the release sequence: `just release <version> "<message>"`. Releases are tagged using that specific repository's own SemVer.
7. **Post-Release `/learn` & Lean Patch Release**: Post-release retrospectives triggered by `/learn` synthesize lessons into rules/skills, bump the core/downstream patch version (`vX.Y.1`), and deploy an immediate lean patch release.

---

## 3. Multi-Repo Boundaries & Task Runners

To ensure strict portability, reproducibility, and git custody (`inv-repo-bound-task-runners`):
1. **Zero Unversioned Root Files**: The workspace root (`/home/pendragon/Projects/powercord-ecosystem/`) is an unversioned container directory for standalone Git repositories. It must never contain unversioned `Justfile`s, scripts, or tooling.
2. **Zero External Dotfile Dependencies**: Tasks must NEVER rely on user-level `~/.config/just/justfile` or `just -g`. Untracked external config breaks CI/CD and teammate reproducibility.
3. **Primary Framework Justfile**: The primary framework repository (`powercord/Justfile`) is the canonical, version-controlled entry point for multi-repo orchestration:
   - Multi-repo inspection: `cd powercord && just status-all` inspects git status across all sub-repos.
4. **Repository-Scoped Task Runners**: Sibling repos (`powercord-client`, `powercord-downstream-server`) maintain their own version-controlled `Justfile`s for local development.

---

## 4. Deep References

For in-depth architectural specifications, see the references:
* [Auth Architecture](references/auth-architecture.md) — Dual-layer auth, beforeware, and `get_admin_guilds()`.
* [Devkit Recipes](references/devkit-just.md) — `devkit.just` database auto-provisioning and port 5433 handling.
* [Dependency Matrix](references/dependency-matrix.md) — Exact dependency bounds across server and client.
* [Failure Patterns](references/failure-patterns.md) — Troubleshooting client caching, Alembic drift, and port locks.
