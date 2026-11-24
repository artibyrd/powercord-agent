# Powercord Developer Kit (`powercord-agent`)

Centralized domain skills, universal invariants, self-contained workflow overlays, PostgreSQL MCP configuration, and production-safety hooks for the **Powercord Ecosystem** (`powercord`, `powercord-client`, `powercord-extensions/*`, `powercord-client-extensions/*`, and `powercord-downstream-server`).

Designed for **native Antigravity v2.34 plugin discovery** while remaining **100% platform-agnostic** (zero lock-in): every invariant is backed by harness-agnostic Tier 2 tests in `powercord/tests/governance/`, open-standard `AGENTS.md`, Open Agent Skills (`SKILL.md`), and self-contained Markdown overlays readable by Antigravity, Claude Code, Cursor, Codex, or OpenHands.

---

## 1. Native Plugin Layout

```text
powercord-agent/
├── plugin.json                # Native plugin manifest (v2.5.0)
├── assets/logo.svg            # Square plugin icon
├── rules/
│   └── AGENTS.md              # Canonical Tier 0 invariants (<800 tokens)
├── skills/                    # 8 progressive Powercord domain skills
│   ├── powercord-ecosystem/
│   ├── powercord-database-operations/
│   ├── powercord-testing/
│   ├── powercord-extension-authoring/
│   ├── powercord-security-auditor/
│   ├── powercord-client-development/
│   ├── powercord-deployment/
│   └── powercord-gcp-operations/
├── overrides/                 # 6 self-contained 3-section workflow overlays
│   ├── architecture-review.md
│   ├── bootstrap-approvals.md
│   ├── domain-modeling.md
│   ├── knowledge-governance.md
│   ├── pr-brief.md
│   └── release-lifecycle.md
├── hooks.json                 # PreToolUse production safety hook manifest
├── hooks/
│   └── guard_prod_ops.py      # Prompts on irreversible GCP/Terraform prod ops
├── mcp_config.json            # Local PostgreSQL MCP server (:5433)
├── scripts/
│   └── lint_skills.py         # Pure-stdlib plugin, link, overlay & path linter
├── tests/
│   └── test_guard_prod_ops.py # Unit tests for guard_prod_ops.py
├── setup.sh                   # Local verification entrypoint
└── .github/workflows/ci.yml   # Hermetic GitHub Actions CI
```

---

## 2. Zero-Lock-In Overlay Architecture

Generalized engineering skills (code review, architecture review, knowledge governance, git guardrails, workspace hygiene, command approval bootstrapping, PR briefs, and release lifecycle) can be paired with this kit via **`antigravity-customizations`** — without duplicating or shadowing them.

Instead of shipping colliding copies of generalized skills, `powercord-agent/overrides/` defines six self-contained Markdown policies following the 3-section delta contract (`Overrides`, `Extensions`, `Disabled / Not Applicable`):

* [`overrides/architecture-review.md`](overrides/architecture-review.md) — Deep Modules + 1,000-LOC safety rail, `compute_*` purity, split-stack FastHTML/FastAPI isolation, `Card`/decorator signature preservation, client decoupling, facade deconstruction, and container path guards.
* [`overrides/knowledge-governance.md`](overrides/knowledge-governance.md) — 4-tier taxonomy, `<800`-token `AGENTS.md` parity, `CHANGELOG.md`/`ROADMAP.md` symmetry, Living Canon slugs, and plain-English prose readability.
* [`overrides/release-lifecycle.md`](overrides/release-lifecycle.md) — Local downstream `:5001` Mk1 verification, `validate_pr.py`, GCS pre-deploy backup + `just qa`, and topological multi-repo merge ordering.
* [`overrides/pr-brief.md`](overrides/pr-brief.md) — `[vX.Y.Z]` PR title parity, multi-repo topology callouts, and local `:5001` verification evidence.
* [`overrides/bootstrap-approvals.md`](overrides/bootstrap-approvals.md) — Safe read-only `Justfile` approval set with strict no-spicy-prefixes enforcement.
* [`overrides/domain-modeling.md`](overrides/domain-modeling.md) — Canonical Powercord domain vocabulary (`cog`, `sprocket`, `widget`, `blueprint`, `downstream`, `MCI`) and lazy ADR guidance.

At the umbrella workspace root, `.agents/overrides` symlinks to `../powercord-agent/overrides` and `.agents/plugins.json` registers `powercord-agent` as a native plugin (loading its 8 skills, `rules/AGENTS.md`, `hooks.json`, and `mcp_config.json` without duplicating skills). Core `powercord/.agents/overrides/` stays mirrored via `just sync-overlays` so standalone clones work out of the box.

---

## 3. Production Safety Hook (`hooks.json`)

`hooks.json` registers a single focused `PreToolUse` hook (`hooks/guard_prod_ops.py`) on `run_command`:

* Returns `decision: "ask"` on irreversible production and infrastructure mutations (including env-var prefixes, wrappers, subshells, and `bash -c` invocations): `just gcp-build`, `just prod-deploy`, `just prod-rollback`, `just prod-db-restore`, `just tf-apply`, `just tf-destroy`, `terraform apply`, `terraform destroy`, and `gcloud builds submit`.
* Allows normal local feature-branch `git commit` / `just commit` workflows and read-only inspection commands (`just prod-status`, `just prod-logs`, `just tf-plan`, `just check`).

---

## 4. Verification

```bash
# Pure-stdlib linter + unit tests + optional agy plugin validate --strict
./powercord-agent/setup.sh

# Or invoke individual checks directly
python3 powercord-agent/scripts/lint_skills.py
python3 -m unittest discover -s powercord-agent/tests -v
agy plugin validate --strict powercord-agent/
```
