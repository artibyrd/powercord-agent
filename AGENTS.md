# Agent Guidelines & Sovereign Invariant Architecture for Powercord

Welcome to the **Powercord Ecosystem** (`/home/pendragon/Projects/powercord-ecosystem`).

> **Operational Heuristics**:
> 1. *When in doubt, check the Justfile (`just --list` or `just -g status`).*
> 2. *ONLY scratch directory is `<appDataDir>/brain/<conversation-id>/scratch/` (zero in-repo scripts).*
> 3. *Strict Poetry execution: Always run commands via `poetry run <cmd>`.*

---

## 1. Tier 0: Universal Core Invariants

### Class α: Sovereign Safety, Custody & Human Authority (P0)
- **`inv-branch-pr-review-gate`**: Zero direct commits or pushes to `main`. Incremental commits on local `feat/*` branches gated by `just check`. Verify downstream (`http://localhost:5001/`) before opening PRs (`gh pr create`). Merges and tags require human Mk1 review.
- **`inv-single-vm-cost-ceiling`**: Single fixed-cost GCE VM (`powercord-instance`). Zero Cloud Run or serverless autoscaling.
- **`inv-no-unauthorized-gcp-deploy`**: GCP deploys (`just gcp-build`) require explicit human confirmation.
- **`inv-mk1-downstream-walkthrough-verification`**: Walkthroughs must provide interactive testing steps on downstream (`http://localhost:5001/`).
- **`inv-pre-deploy-qa-and-backup-gate`**: Pre-flight requires local UI sign-off, GCS backup check, and passing downstream `just qa`.
- **`inv-default-deny-auth`**: Auth middleware (`auth_before`) and guards (`api_scope_required`) deny (`False`) on invalid input.
- **`inv-view-channel-gating`**: Permission checks gate on View Channel (`1 << 10`) first.
- **`inv-tri-sink-error-logging`**: Persist data errors across rotating file (`logs/<ext>_data_health.log`), DB, and Cloud Logging.

### Class β: Execution Topology, Lifecycle & Release Architecture (P1)
- **`inv-cart-before-horse`**: Tooling and test runners precede downstream refactoring and testing.
- **`inv-downstream-integration-testbed`**: Downstream (`powercord-downstream-server/`) is the pre-commit integration sandbox for migrations and containers.
- **`inv-source-isolation-no-ad-hoc-cp`**: Zero ad-hoc `cp` to downstream; sync strictly via `just ext-install` and `/reconcile-downstream-server`.
- **`inv-manifest-version-parity`**: Extension `extension.json` version must match `pyproject.toml`.
- **`inv-alembic-lineage-isolation`**: Extensions maintain isolated `down_revision` branches in `alembic/versions/`.
- **`inv-downstream-deploy-origin`**: Production Cloud Builds submitted exclusively from locked downstream assembly.
- **`inv-split-stack-isolation`**: FastHTML views return FT components; FastAPI sprockets return JSON/Pydantic schemas.
- **`inv-guild-data-lifecycle`**: Extensions implement `delete_guild_data` hook on guild leave.
- **`inv-hermetic-db-testing-nullpool`**: Test engines use `NullPool` and dispose connections on fixture teardown.
- **`inv-client-server-decoupling`**: Companion desktop client never imports backend modules (`app.*`, `nextcord`, `fasthtml`). HTTP/WS only.
- **`inv-4tier-knowledge`**: 4-Tier taxonomy: Tier 0 `AGENTS.md` (<800 tokens), Tier 1 skills (`.agents/skills/`), Tier 2 tests (`tests/governance/`), Tier 3 blueprints (`ROADMAP.md`).

### Class γ: Interface Symmetry, Epistemic Parity & Governance (P2)
- **`inv-500-loc-ceiling`**: 500 LOC ceiling with ratchet. Monoliths frozen in `governance_ratchet.json` and decrease monotonically.
- **`inv-compute-ontology`**: Pure mathematical and bitmask functions use `compute_*` prefix.
- **`inv-widget-scope-namespaces`**: Dashboard widgets adhere to scope prefixes: `admin_`, `guild_admin_`, or public.
- **`inv-fasthtml-card-signature`**: `Card(title, content, **kwargs)`. Custom route decorators preserve `__signature__`.
- **`inv-no-raw-snowflakes`**: Resolve Snowflake IDs to cached names in UI with fallback indicators.
- **`inv-omission-over-fallback-galleries`**: Omit malformed records rather than placeholders; oversample queries.
- **`inv-state-checksum-caching`**: Caches incorporate state record checksums.
- **`inv-flet-async-routing`**: Desktop views use non-blocking async routing with `httpx.AsyncClient`.
- **`inv-living-canon`**: Reference system invariants via semantic slugs without hardcoded rule counts.

---

## 2. Progressive Skills (`.agents/skills/`)
- 🏛️ [`architecture-governance`](.agents/skills/architecture-governance/SKILL.md): 500 LOC ceiling, ratchet, split-stack.
- 🧠 [`knowledge-governance`](.agents/skills/knowledge-governance/SKILL.md): 4-tier taxonomy, context economy (<800 tokens).
- 🛡️ [`bootstrap-approvals`](.agents/skills/bootstrap-approvals/SKILL.md): Prime IDE command permissions.
- 📦 [`powercord-ecosystem`](.agents/skills/powercord-ecosystem/SKILL.md): Multi-repo isolation workflows.
- 🗄️ [`powercord-database-operations`](.agents/skills/powercord-database-operations/SKILL.md): Port 5433, multi-head migrations.
- 🧩 [`powercord-extension-authoring`](.agents/skills/powercord-extension-authoring/SKILL.md): Gadget architecture.
- 🛡️ [`powercord-security-auditor`](.agents/skills/powercord-security-auditor/SKILL.md): Bitmask rules and widgets.
- 🖥️ [`powercord-client-development`](.agents/skills/powercord-client-development/SKILL.md): Flet companion desktop client.
- 🚀 [`powercord-deployment`](.agents/skills/powercord-deployment/SKILL.md) & ☁️ [`powercord-gcp-operations`](.agents/skills/powercord-gcp-operations/SKILL.md): Single VM GCE operations.

---

## 3. Shift-Left Test Gates (`tests/governance/`)
- `test_architecture_governance.py`: 500 LOC ratchet, pure `compute_*`, client isolation (<3s).
- `test_version_and_manifest_parity.py`: Manifest parity, SemVer, Alembic lineage isolation.
- `test_split_stack_isolation.py`: FastHTML vs FastAPI sprocket boundaries.
- `test_docs_integrity.py`: Context economy (<800 tokens) and Living Canon dynamic naming.

---

## 4. Standard Commands (`powercord/Justfile` & Workspace)
- `just check`: Parallel, hermetic pre-commit gate (<3s, zero Docker required): `lint` + `format` + `test-gov`.
- `just typecheck`: Run Mypy static type checking.
- `just branch <name>` / `just commit <msg>` / `just pr-create`: Feature branch and PR lifecycle.
- `just bootstrap-approvals`: Prime IDE command permissions.
- `just ignite`: Single-command environment setup, preflight, and health check.
- `just release <version> <msg>`: Atomic version bump, manifest sync, and release tagging.
- `just -g status`: Workspace-wide multi-repository git status inspection.
