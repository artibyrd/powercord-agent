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
> **`just gcp-build` deploys to LIVE PRODUCTION.**
> Agents must **NEVER** run `just gcp-build` without explicit user permission. Always use `/deploy-production` workflow.

---

## 2. Quick Recipes

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
