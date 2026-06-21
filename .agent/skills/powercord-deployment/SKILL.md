---
name: powercord-deployment
description: >
  Deployment and CI/CD skill for the Powercord ecosystem. Use when building,
  deploying, or managing infrastructure for the Powercord production server.
  NEVER run `just gcp-build` without direct explicit user consent.
---

# Powercord Deployment & CI/CD

## Overview

This skill covers the full deployment lifecycle for the Powercord server:
Cloud Build CI/CD pipeline, Terraform infrastructure management, Docker image
builds, production verification, and rollback procedures.

## When to Use

- Reviewing or modifying CI/CD configuration (`cloudbuild.yaml`).
- Running Terraform plan/apply against GCP infrastructure.
- Investigating deployment failures or Cloud Build logs.
- Performing post-deployment verification.
- Understanding production infrastructure topology.

## ⚠️ SAFETY

> [!CAUTION]
> **`just gcp-build` deploys to PRODUCTION.** This command submits a Cloud Build
> job and resets the production VM. It **MUST NEVER** be run without **DIRECT,
> EXPLICIT user consent**. There is no staging environment — this rolls over the
> live server immediately.

> [!CAUTION]
> **`just tf-apply` modifies live infrastructure.** Always run `just tf-plan`
> first and present the diff to the user. Use `--yes` only after the user has
> reviewed and approved the plan.

**Mandatory safety rules for agents:**

1. **NEVER** execute `just gcp-build` autonomously. Always ask the user first.
2. **NEVER** execute `just tf-apply` without showing the plan output to the user.
3. **NEVER** execute `just tf-destroy` without explicit user confirmation.
4. Treat any command behind a `_require-gcp` guard as production-affecting.

## Pre-Deployment Checklist

1. All tests pass: `just qa` (or at minimum `just test --type all`).
2. Pre-commit linting: `poetry run ruff check --fix . && poetry run ruff format .`
3. `POWERCORD_GCP_PROJECT` is set (loaded from `.env` via `dotenv-load`).
4. Review Terraform plan if infra changes are involved: `just tf-plan`.
5. **Obtain explicit user consent before running `just gcp-build`.**

## CI/CD Pipeline Overview

Cloud Build (`cloudbuild.yaml`) executes five stages:

| Stage | Description |
|---|---|
| 1. Postgres sidecar | Starts a PostgreSQL container for QA tests |
| 2. QA gate | `poetry install` → wait for DB → `ruff check` → `ruff format --check` → `mypy` → `pytest` (unit) |
| 3. Docker build | Builds image with two tags: `BUILD_ID` and `latest` |
| 4. Push to registry | Pushes to `us-central1-docker.pkg.dev/$PROJECT_ID/powercord/powercord-app` |
| 5. Terraform deploy | `terraform init` + `terraform apply -auto-approve` |

## Deployment Commands

| Command | Effect | Safety |
|---|---|---|
| **`just gcp-build`** | **Submits Cloud Build + resets production VM** | **🔴 REQUIRES EXPLICIT USER CONSENT** |
| `just tf-init` | Initialize Terraform working directory | Safe |
| `just tf-plan [--docker-image]` | Preview infrastructure changes | Safe |
| `just tf-apply [--docker-image]` | Apply infrastructure changes (has `[confirm]` prompt; use `--yes` for agent after user approval) | ⚠️ Needs user review |
| `just tf-destroy` | Tear down all infrastructure (has `[confirm]` prompt) | 🔴 Destructive |

> [!CAUTION]
> **Reminder: `just gcp-build` rolls over the production server.** Do NOT run it
> unless the user has explicitly told you to deploy.

### Environment

- `POWERCORD_GCP_PROJECT` — required; set in `.env`, guarded by `_require-gcp`.
- Docker image: `us-central1-docker.pkg.dev/$PROJECT_ID/powercord/powercord-app:latest`
- Terraform state bucket: `${PROJECT_ID}-tf-state` (GCS).

## Terraform Operations

Terraform files live in `terraform/`:

| File | Purpose |
|---|---|
| `compute.tf` | Container-Optimized OS VM |
| `iam.tf` | Service accounts and IAM bindings |
| `network.tf` | VPC, firewall rules |
| `storage.tf` | GCS buckets |
| `secrets.tf` | Secret Manager references |
| `monitoring.tf` | Uptime checks, alerting |
| `main.tf` | Root module |
| `providers.tf` | Provider configuration |
| `variables.tf` / `locals.tf` | Input variables and locals |
| `outputs.tf` | Output values |

Workflow: `just tf-init` → `just tf-plan` → review → `just tf-apply --yes`
(only after user approval).

## Infrastructure Components

- **VM**: Container-Optimized OS running a single Docker container.
- **Process manager**: `supervisord` runs four services: bot, api, ui, postgres.
- **Reverse proxy**: nginx in front of the API and UI.
- **Python runtime**: `/app/.venv/bin/python` — production does **not** use
  `just` or `poetry`.
- **Automated backups**: systemd timer syncs data to GCS at 04:00 UTC daily.

## Rollback Procedures

1. Identify the last known-good `BUILD_ID` tag in Artifact Registry.
2. Run `just tf-plan --docker-image <registry>/<image>:<good-tag>` and review.
3. With user approval, apply: `just tf-apply --docker-image <registry>/<image>:<good-tag> --yes`.
4. Verify with post-deployment checks below.

## Post-Deployment Verification

1. SSH into the VM and confirm all supervisord services are `RUNNING`.
2. Curl the health endpoint: `curl https://<domain>/api/health`.
3. Verify bot connectivity (check logs for successful Discord gateway connect).
4. Run `just verify-dashboard` against production URL if applicable.

## Common Failures

| Symptom | Likely cause | Fix |
|---|---|---|
| Cloud Build fails at QA stage | Lint or test failure | Fix locally, re-run `just qa` |
| Terraform state lock | Previous apply interrupted | `terraform force-unlock <LOCK_ID>` |
| VM not pulling latest image | Stale instance metadata | Reset VM: `gcloud compute instances reset` |
| `_require-gcp` error | `POWERCORD_GCP_PROJECT` not set | Add to `.env` or export in shell |
| supervisord service not starting | Config or dependency error | SSH in, check `/var/log/supervisor/` |
