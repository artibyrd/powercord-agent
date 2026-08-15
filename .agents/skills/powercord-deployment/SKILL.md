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

---

## 3. Deep References

* [Cloud Build Pipeline](references/cloudbuild-pipeline.md) — 5-stage pipeline, sidecar DB, and Docker artifact registry.
* [Terraform Infrastructure](references/terraform-infra.md) — Compute, IAM, VPC, and storage topology.
* [Production Workflow](../../workflows/deploy-production.md) — Step-by-step production deployment procedure.
