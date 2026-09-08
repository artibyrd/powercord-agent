---
description: Deploy the Powercord server to the live GCP production environment via Cloud Build. Includes mandatory safety gates requiring explicit user consent before any deployment action.
---

# Deploy to Production

> **⚠️ CRITICAL: This workflow deploys to the LIVE PRODUCTION server.**
> **`just gcp-build` triggers a Cloud Build that replaces the running production container.**
> **This action MUST NEVER be executed without DIRECT EXPLICIT user consent.**

This workflow guides the full production deployment process from pre-flight
checks through post-deployment verification.

> **Safety Model:** The deployment command (`just gcp-build`) is gated behind
> an explicit consent step. Agents MUST stop and confirm with the user before
> executing Step 5. Skipping the consent gate is a critical violation.

---

## Steps

### 1. Pre-Deployment Safety Gate

> **⚠️ STOP — Do not proceed past this step without explicit user consent.**
>
> This workflow will deploy code to the **live production server**. The
> deployment command (`just gcp-build`) will:
> - Build a new Docker image via GCP Cloud Build
> - Push the image to the production container registry
> - Replace the running production container with the new image
>
> **Any bugs or regressions will immediately affect live users.**

**Action required:** Explicitly confirm with the user that they want to deploy
to production. Do not accept implied consent — the user must directly state
their intent to deploy.

```
Agent: "This will deploy to the LIVE production server. Do you want to proceed with the production deployment?"
User:  (must explicitly confirm)
```

**If the user does not confirm, STOP HERE. Do not continue.**

### 1.1 Verify Local Human ("Mk1 Eyeball") Approval
Ensure the human developer has completed local interactive verification:
- Web UI is responsive at `http://localhost:5001/`
- Admin dashboards and security widgets render without 500 errors
- Discord bot slash commands are registered and responding

### 1.2 Inspect Live Production State
Inspect the live VM, running container image, and existing backup archives:

```bash
cd powercord-downstream-server
just prod-status
```

Expected: VM status is `RUNNING`, container image tag is shown, recent `.sql.gz` archives exist in GCS, and health endpoints respond.

### 2. Verify Downstream Cleanliness & Governance
Before deploying, ensure working trees are clean and hermetic pre-commit checks pass:

```bash
cd powercord-downstream-server
just check
```

Expected: All shift-left governance tests, linting, and formatting checks pass (<3s).

### 3. Create Verified Pre-Deploy Production Backup
Before altering any production code or running migrations, take an immediate, verified snapshot of the live production database:

```bash
cd powercord-downstream-server
just prod-backup pre-deploy
```

This recipe:
1. Executes `BackupService.create_daily_backup()` inside the running production container.
2. Captures the currently running image tag into `backups/last_known_good.json`.
3. Downloads a local copy of the new `.sql.gz` backup archive into `backups/`.
4. Confirms GCS sync.

### 4. Trigger Production Deployment (Automated 5-Gate Pipeline)

> **⚠️ FINAL SAFETY CHECK: Confirm that Step 1 consent was explicitly received.**
> **Do NOT execute `just prod-deploy` without prior user confirmation.**

Execute the safe deployment pipeline:

```bash
cd powercord-downstream-server
just prod-deploy
```

`prod-deploy` automatically runs the 5 safety gates:
1. **Gate 1**: Verifies working tree cleanliness across downstream and all extensions.
2. **Gate 2**: Runs hermetic QA checks (`just check`).
3. **Gate 3**: Performs a mandatory pre-deploy database backup (`just prod-backup pre-deploy`).
4. **Gate 4**: Submits Cloud Build with `--project={{gcp_project}}` and resets `powercord-instance`.
5. **Gate 5**: Polls the live health endpoint `http://<vm_ip>/api/health` every 3s for up to 90s.

### 5. Post-Deployment Verification & Live Logs

If needed, stream container logs or verify services:

```bash
cd powercord-downstream-server

# Stream live container logs
just prod-logs 100

# Inspect overall production status
just prod-status
```

### 6. Rollback Procedures (If Needed)

If an issue occurs after deployment:

#### A. Container / Image Rollback
Roll back to the previous known-good image captured in `backups/last_known_good.json`:

```bash
cd powercord-downstream-server
just prod-rollback
```

To roll back to a specific historical image:
```bash
just prod-rollback image=us-central1-docker.pkg.dev/bards-guild-midi-project/powercord/powercord-app:<TAG>
```

#### B. Database Rollback / Disaster Recovery
If schema migrations broke backwards compatibility or corrupted data, restore the pre-deploy database snapshot:

```bash
cd powercord-downstream-server
just prod-db-restore backups/<backup_name>.sql.gz
```
