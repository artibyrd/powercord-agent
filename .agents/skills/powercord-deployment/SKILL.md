---
name: powercord-deployment
description: >-
  Deployment and CI/CD skill for the Powercord ecosystem. Use when building, deploying,
  or managing infrastructure for the Powercord production server. NEVER run `just gcp-build` without direct explicit user consent.
---

# Powercord Deployment & CI/CD

Deployment, Cloud Build pipelines, Terraform infrastructure, and release verification.

---

## 1. Safety Invariants

> [!CAUTION]
> **Zero AI Self-Merges (`inv-branch-pr-review-gate`)**:
> Agents must **NEVER** run `gh pr merge`. When upstream fixes are required during pre-flight or deployment:
> 1. Create a branch (`git checkout -b fix/<topic>`).
> 2. Verify locally (`just check`).
> 3. Open PR (`gh pr create`).
> 4. **STOP and request Human Mk1 review and merge**. Never self-merge PRs.

> [!CAUTION]
> **`just gcp-build` deploys to LIVE PRODUCTION.**
> Agents must **NEVER** run `just gcp-build` without explicit user permission. Always use `/deploy-production` workflow.

> [!NOTE]
> **Cold Boot Timing & Container Isolation**:
> - Production cold boot (VM reset + Docker pull + Alembic migrations) requires 90–120s. Gate 5 polls for 180s.
> - Cloud Build containers mount isolated repositories at `/workspace`. Tests must never assume `REPO_ROOT.parent` exists without skip guards.

---

## 2. Quick Recipes

### 2.1 Production Management (Downstream `powercord-downstream-server/`)
* **Inspect Live Production State**:
  ```bash
  cd powercord-downstream-server && just prod-status
  ```
  Inspects VM status, currently deployed container image, latest GCS backups, and pings live endpoints.
* **Stream Live Production Container Logs**:
  ```bash
  cd powercord-downstream-server && just prod-logs 100
  ```
* **Mandatory Pre-Deploy Backup**:
  ```bash
  cd powercord-downstream-server && just prod-backup pre-deploy
  ```
  Dumps container database, syncs to GCS, saves local `.sql.gz` copy to `./backups/`, and writes `backups/last_known_good.json`.
* **Safe Production Deployment (Gated)**:
  ```bash
  cd powercord-downstream-server && just prod-deploy
  ```
  *Requires explicit human approval.* Automatically executes: 1) working tree clean check, 2) `just check`, 3) `just prod-backup`, 4) Cloud Build & VM reset, 5) 90-second health poll.
* **Push-Button Rollback**:
  ```bash
  cd powercord-downstream-server && just prod-rollback
  # Or roll back to specific image:
  cd powercord-downstream-server && just prod-rollback image=<image_uri>
  ```
  Rolls back to image in `backups/last_known_good.json` via Terraform and resets VM.
* **Database Disaster Recovery / Restore**:
  ```bash
  cd powercord-downstream-server && just prod-db-restore backups/<backup_file>.sql.gz
  ```

### 2.2 Infrastructure & Release
* **Plan Infrastructure Changes**:
  ```bash
  cd powercord && just tf-plan
  ```
* **Apply Infrastructure Changes (Post-Approval)**:
  ```bash
  cd powercord && just tf-apply --yes
  ```
* **Release & Manifest Parity Lifecycle**:
  1. Bump version in `powercord/pyproject.toml` and align `tests/governance/test_version_and_manifest_parity.py`.
  2. Run pre-release validation: `just check && just test-gov`.
  3. Execute release: `just release <version> "<message>"` (stages `Justfile`, `pyproject.toml`, and governance parity tests).
  4. Reconcile downstream testbed:
     ```bash
     cd powercord-downstream-server && git pull origin main && just rebuild-target
     ```
  5. Verify live container health on `http://localhost:5001/`.

### 2.1 Docker Hygiene & Build Cache Management

Frequent container builds can quickly accumulate 50GB+ of dangling layers and builder cache:
* **Standard Cleanup (Safe Daily)**:
  ```bash
  just docker-clean
  ```
  Prunes dangling images and builder cache older than 24 hours.
* **Deep Clean (Reclaim Full Disk Space)**:
  ```bash
  just docker-clean all=true
  ```
  Prunes all dangling images and completely purges the Docker build cache.
* **Operational Gates**:
  - Run `just docker-clean` after rebuilding downstream test containers and before submitting production Cloud Builds.

---

## 3. Deep References

* [Cloud Build Pipeline](references/cloudbuild-pipeline.md) — 5-stage pipeline, sidecar DB, and Docker artifact registry.
* [Terraform Infrastructure](references/terraform-infra.md) — Compute, IAM, VPC, and storage topology.
* [Production Workflow](../../workflows/deploy-production.md) — Step-by-step production deployment procedure.
