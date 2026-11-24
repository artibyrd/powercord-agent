# Powercord Agent Guidelines & Sovereign Invariants

> **Heuristics**:
> 1. *Check `powercord/Justfile` (`powercord/just/`) first.*
> 2. *Zero untracked task runners; scripts reside inside git repos.*
> 3. *Keep scratch files outside git repos (session scratch dir or `/tmp/`); zero inline shell blobs.*
> 4. *Run Python tools via `poetry run <cmd>`.*
> 5. *Log completed work in `CHANGELOG.md`; keep `ROADMAP.md` forward-looking.*
> 6. *Preserve the active master plan document; draft separate proposals in `<topic>.md`.*

**Skill Overlays:** Check `.agents/overrides/<skill>.md` before applying generalized workflow skills.

## 1. Tier 0: Universal Core Invariants

### Class α: Sovereign Safety & Custody (P0)
- **`inv-branch-pr-review-gate`**: Zero direct `main` pushes; gate via `just check`. PRs require human Mk1 review; zero AI self-merges.
- **`inv-single-vm-cost-ceiling`**: Single fixed-cost GCE VM (`powercord-instance`); zero autoscaling.
- **`inv-no-unauthorized-gcp-deploy`**: `just gcp-build` and `just prod-deploy` require explicit human confirmation.
- **`inv-mk1-downstream-walkthrough-verification`**: Verify live flows on local downstream (`:5001`) before PRs.
- **`inv-pre-deploy-qa-and-backup-gate`**: Pre-deploy requires UI sign-off, `just prod-backup` GCS check, and `just qa`.
- **`inv-default-deny-auth`**: `auth_before` and `api_scope_required` return `False` on missing or invalid input.
- **`inv-view-channel-gating`**: Gate channel permission checks on View Channel (`1 << 10`) first.
- **`inv-tri-sink-error-logging`**: Persist data-health errors to rotating file (`logs/<ext>_data_health.log`), DB, and Cloud Logging.

### Class β: Topology, Lifecycle & Boundaries (P1)
- **`inv-cart-before-horse`**: Tooling and shared contracts precede refactors; use vertical-slice TDD inside features.
- **`inv-downstream-integration-testbed`**: `powercord-downstream-server/` is the pre-PR sandbox; rebuild and verify on `:5001`.
- **`inv-source-isolation-no-ad-hoc-cp`**: Zero ad-hoc `cp`; sync via rebase and `just ext-install`. External extensions live in `powercord-extensions/`.
- **`inv-changelog-session-parity`**: Update `CHANGELOG.md` each session; keep `ROADMAP.md` forward-looking.
- **`inv-manifest-version-parity`**: Manifests (`extension.json` / `[tool.powercord]`) match `pyproject.toml`; decouple pre-`1.0.0` packages.
- **`inv-repo-bound-task-runners`**: Task runners live in versioned repos; multi-repo orchestration lives in `powercord/Justfile`.
- **`inv-alembic-lineage-isolation`**: Extensions keep isolated `down_revision` branches in `alembic/versions/`.
- **`inv-downstream-deploy-origin`**: Submit production Cloud Builds solely from `powercord-downstream-server/`.
- **`inv-split-stack-isolation`**: FastHTML returns FT components; FastAPI sprockets return JSON/Pydantic schemas.
- **`inv-guild-data-lifecycle`**: Guild-scoped extensions implement `delete_guild_data` on guild leave.
- **`inv-hermetic-db-testing-nullpool`**: Test engines use `NullPool` and dispose connections on teardown.
- **`inv-client-server-decoupling`**: Client never imports `app.*`, `nextcord`, or `fasthtml`; HTTP/WS only.
- **`inv-4tier-knowledge`**: Tier 0 `AGENTS.md` (<800 tokens), Tier 1 skills/overlays, Tier 2 `tests/governance/`, Tier 3 `docs/`.

### Class γ: Interface Symmetry & Governance (P2)
- **`inv-500-loc-ceiling`**: Deep Modules (~500 LOC soft split trigger); 1,000-LOC hard safety rail.
- **`inv-compute-ontology`**: Pure math/bitmask helpers use `compute_*`.
- **`inv-widget-scope-namespaces`**: Widgets use `admin_`, `guild_admin_`, or public prefixes.
- **`inv-fasthtml-card-signature`**: Call `Card(title, content, **kwargs)`; decorators preserve `__signature__`.
- **`inv-no-raw-snowflakes`**: Resolve Snowflake IDs to cached names with fallback indicators.
- **`inv-omission-over-fallback-galleries`**: Omit malformed gallery records; oversample queries.
- **`inv-state-checksum-caching`**: Cache keys incorporate underlying state checksums.
- **`inv-flet-async-routing`**: Desktop views use async routing with `httpx.AsyncClient`.
- **`inv-living-canon`**: Reference invariants by semantic slug without hardcoded counts.

## 2. Progressive Domain Skills (`powercord-agent/skills/`)
- [`powercord-ecosystem`](powercord-agent/skills/powercord-ecosystem/SKILL.md), [`powercord-database-operations`](powercord-agent/skills/powercord-database-operations/SKILL.md), [`powercord-testing`](powercord-agent/skills/powercord-testing/SKILL.md), [`powercord-extension-authoring`](powercord-agent/skills/powercord-extension-authoring/SKILL.md)
- [`powercord-security-auditor`](powercord-agent/skills/powercord-security-auditor/SKILL.md), [`powercord-client-development`](powercord-agent/skills/powercord-client-development/SKILL.md), [`powercord-deployment`](powercord-agent/skills/powercord-deployment/SKILL.md), [`powercord-gcp-operations`](powercord-agent/skills/powercord-gcp-operations/SKILL.md)

## 3. Shift-Left Gates & Commands (`powercord/`)
- **Gates (`tests/governance/`)**: `test_architecture_governance.py`, `test_version_and_manifest_parity.py`, `test_split_stack_isolation.py`, `test_docs_integrity.py`, `test_validate_pr.py`.
- **Commands (`Justfile`)**: `just check`, `just typecheck`, `just agent-check`, `just sync-overlays`, `just branch`/`commit`/`pr-create`, `just status-all`, `just docker-clean`, `just ignite`, `just release`.
