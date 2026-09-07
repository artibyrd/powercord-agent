# Agent Guidelines & Sovereign Invariant Architecture for Powercord

Welcome to the **Powercord Ecosystem** (`/home/pendragon/Projects/powercord-ecosystem`).

> **Operational Heuristics**:
> 1. *When in doubt, check repo Justfile (primary: `powercord/Justfile`).*
> 2. *Zero untracked task runners: scripts reside strictly inside git repos.*
> 3. *ONLY scratch: `<appDataDir>/brain/<conversation-id>/scratch/`.*
> 4. *Strict Poetry: Always run commands via `poetry run <cmd>`.*
> 5. *Session changelog parity: Record completed changes in `CHANGELOG.md` every session; keep `ROADMAP.md` forward-looking.*

---

## 1. Tier 0: Universal Core Invariants

### Class α: Sovereign Safety, Custody & Human Authority (P0)
- **`inv-branch-pr-review-gate`**: Zero direct pushes to `main`. Semantic branches (`feat/<topic>`) gated by `just check`. Verify downstream (port 5001) before PRs (`gh pr create`). Human Mk1 review.
- **`inv-single-vm-cost-ceiling`**: Single fixed-cost GCE VM (`powercord-instance`). Zero autoscaling.
- **`inv-no-unauthorized-gcp-deploy`**: GCP deploys (`just gcp-build`) require explicit human confirmation.
- **`inv-mk1-downstream-walkthrough-verification`**: Walkthroughs require interactive testing on local downstream container (port 5001) before PRs.
- **`inv-pre-deploy-qa-and-backup-gate`**: Pre-flight requires local UI sign-off, GCS backup check, and downstream `just qa`.
- **`inv-default-deny-auth`**: Auth middleware (`auth_before`) and guards (`api_scope_required`) deny (`False`) on invalid input.
- **`inv-view-channel-gating`**: Permission checks gate on View Channel (`1 << 10`) first.
- **`inv-tri-sink-error-logging`**: Persist errors across rotating file (`logs/<ext>_data_health.log`), DB, and Cloud Logging.

### Class β: Execution Topology, Lifecycle & Release Architecture (P1)
- **`inv-cart-before-horse`**: Tooling and test runners precede downstream refactoring.
- **`inv-downstream-integration-testbed`**: Downstream (`powercord-downstream-server/`) is pre-commit sandbox. Rebuild container; verify on port 5001 before PRs.
- **`inv-source-isolation-no-ad-hoc-cp`**: Zero ad-hoc `cp` to downstream; sync via git rebase and `just ext-install`. External extensions live in `powercord-extensions/`, never core.
- **`inv-changelog-session-parity`**: Record completed changes in `CHANGELOG.md` every session; keep `ROADMAP.md` strictly forward-looking.
- **`inv-manifest-version-parity`**: Extension `extension.json` matches `pyproject.toml`. Pre-release packages decoupled until `1.0.0`.
- **`inv-repo-bound-task-runners`**: Task runners reside inside versioned repos; multi-repo orchestration lives in `powercord/Justfile` (`just status-all`).
- **`inv-alembic-lineage-isolation`**: Extensions maintain isolated `down_revision` branches in `alembic/versions/`.
- **`inv-downstream-deploy-origin`**: Production Cloud Builds submitted exclusively from locked downstream assembly.
- **`inv-split-stack-isolation`**: FastHTML views return FT components; FastAPI sprockets return JSON/Pydantic schemas.
- **`inv-guild-data-lifecycle`**: Extensions implement `delete_guild_data` hook on guild leave.
- **`inv-hermetic-db-testing-nullpool`**: Test engines use `NullPool` and dispose connections on fixture teardown.
- **`inv-client-server-decoupling`**: Companion desktop client never imports backend modules (`app.*`, `nextcord`, `fasthtml`). HTTP/WS only.
- **`inv-4tier-knowledge`**: 4 tiers: Tier 0 `AGENTS.md` (<800 tokens), Tier 1 skills (`.agents/skills/`), Tier 2 tests (`tests/governance/`), Tier 3 blueprints (`ROADMAP.md`).

### Class γ: Interface Symmetry, Epistemic Parity & Governance (P2)
- **`inv-500-loc-ceiling`**: 500 LOC ceiling with monotonic ratchet decrease in `governance_ratchet.json`.
- **`inv-compute-ontology`**: Pure math and bitmask functions use `compute_*` prefix.
- **`inv-widget-scope-namespaces`**: Dashboard widgets adhere to scope prefixes: `admin_`, `guild_admin_`, or public.
- **`inv-fasthtml-card-signature`**: `Card(title, content, **kwargs)`; route decorators preserve `__signature__`.
- **`inv-no-raw-snowflakes`**: Resolve Snowflake IDs to cached names in UI with fallback indicators.
- **`inv-omission-over-fallback-galleries`**: Omit malformed records rather than placeholders; oversample queries.
- **`inv-state-checksum-caching`**: Caches incorporate state record checksums.
- **`inv-flet-async-routing`**: Desktop views use non-blocking async routing with `httpx.AsyncClient`.
- **`inv-living-canon`**: Reference system invariants via semantic slugs without hardcoded rule counts.

---

## 2. Progressive Skills (`.agents/skills/`)
- 🏛️ [`architecture-governance`](.agents/skills/architecture-governance/SKILL.md) · 🧠 [`knowledge-governance`](.agents/skills/knowledge-governance/SKILL.md) · 🛡️ [`bootstrap-approvals`](.agents/skills/bootstrap-approvals/SKILL.md)
- 📦 [`powercord-ecosystem`](.agents/skills/powercord-ecosystem/SKILL.md) · 🗄️ [`powercord-database-operations`](.agents/skills/powercord-database-operations/SKILL.md) · 🧩 [`powercord-extension-authoring`](.agents/skills/powercord-extension-authoring/SKILL.md)
- 🛡️ [`powercord-security-auditor`](.agents/skills/powercord-security-auditor/SKILL.md) · 🖥️ [`powercord-client-development`](.agents/skills/powercord-client-development/SKILL.md) · 🚀 [`powercord-deployment`](.agents/skills/powercord-deployment/SKILL.md) · ☁️ [`powercord-gcp-operations`](.agents/skills/powercord-gcp-operations/SKILL.md)

---

## 3. Shift-Left Test Gates (`tests/governance/`)
- `test_architecture_governance.py`: 500 LOC ratchet, pure `compute_*`, client isolation (<3s).
- `test_version_and_manifest_parity.py`: Manifest parity, SemVer, Alembic isolation.
- `test_split_stack_isolation.py`: FastHTML vs FastAPI sprocket boundaries.
- `test_docs_integrity.py`: Context economy (<800 tokens), root cleanliness, Living Canon.

---

## 4. Standard Commands (`powercord/Justfile`)
- `just check`: Hermetic pre-commit gate (<3s): `lint` + `format` + `test-gov`.
- `just typecheck`: Mypy static type checking.
- `just branch <name>` / `just commit <msg>` / `just pr-create`: Branch & PR lifecycle.
- `just status-all`: Multi-repo git status inspection across ecosystem.
- `just docker-clean`: Prune dangling Docker images and build cache (`all=true` for full purge).
- `just bootstrap-approvals`: Prime IDE command permissions.
- `just ignite`: Environment setup and health check.
- `just release <version> <msg>`: Version bump, manifest sync, and release tagging.
