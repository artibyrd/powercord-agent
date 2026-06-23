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

### 2. Verify Downstream Cleanliness

Ensure the downstream deployment server and all extension repos have a clean working tree with no uncommitted changes:

```bash
cd "../powercord-downstream-server"

echo "=== Checking powercord-downstream-server/ ==="
git status
# Expected: nothing to commit, working tree clean

echo ""
echo "=== Checking extensions ==="
for ext_dir in ../powercord-extensions/*/; do
    if [ -d "$ext_dir/.git" ]; then
        ext_name=$(basename "$ext_dir")
        echo "→ $ext_name:"
        git -C "$ext_dir" status --short
    fi
done
```

Expected: All repos report a clean working tree. If any repo has uncommitted
changes, commit or stash them before proceeding.

### 3. Run Full QA Suite

Run the complete QA suite in the downstream repository to catch lint errors, formatting issues, type-check failures, and test regressions:

```bash
cd "../powercord-downstream-server"
just qa
```

Expected: All checks pass — linting, formatting, mypy type checking, and the
full test suite complete without errors.

**If any check fails, STOP. Fix the issue before deploying.**

### 4. Verify Extension Commits

Ensure all extension repositories have their latest changes committed and
pushed to their respective remotes:

```bash
for ext_dir in ../powercord-extensions/*/; do
    if [ -d "$ext_dir/.git" ]; then
        ext_name=$(basename "$ext_dir")
        echo "→ $ext_name:"
        echo "  Latest commit:"
        git -C "$ext_dir" log --oneline -1
        echo "  Remote sync:"
        git -C "$ext_dir" status -sb
        echo ""
    fi
done
```

Expected: Each extension shows a recent commit and is in sync with its remote
(no `ahead` or `behind` indicators).

### 5. Trigger Cloud Build

> **⚠️ FINAL SAFETY CHECK: Confirm that Step 1 consent was explicitly received.**
> **Do NOT execute `just gcp-build` without prior user confirmation.**

Deploy to production via GCP Cloud Build:

```bash
cd "../powercord-downstream-server"
just gcp-build
```

This command submits a Cloud Build that:
1. Builds the production Docker image
2. Pushes it to the Artifact Registry
3. Automatically deploys the new image to the production Compute Engine VM (`powercord-instance`) via Terraform and resets the instance.

The build typically takes 3–5 minutes.

### 6. Monitor Build Progress

Monitor the Cloud Build logs to track deployment progress:

```bash
cd "../powercord-downstream-server"

# Check the latest Cloud Build status
gcloud builds list --limit=1 --format="table(id,status,startTime,duration)"

# Stream logs from the latest build (if still running)
gcloud builds log $(gcloud builds list --limit=1 --format="value(id)") --stream
```

Expected: Build status progresses through `QUEUED` → `WORKING` → `SUCCESS`.
If the build fails, inspect the logs for errors before re-attempting.

### 7. Post-Deployment Verification

Verify the production container is running with the new image on the Compute Engine instance:

```bash
# Check the VM instance status
gcloud compute instances describe powercord-instance --zone us-central1-a --format="value(status)"

# SSH into the instance and list running containers
gcloud compute ssh powercord-instance --zone us-central1-a --command "docker ps"

# Stream docker logs from the powercord container to verify successful startup
gcloud compute ssh powercord-instance --zone us-central1-a --command "docker logs --tail 50 \$(docker ps -q -f name=klt-powercord)"
```

Expected: The VM status is `RUNNING`, the Docker container is active, and logs contain `Database initialized.` and supervisord starting all services without crash traces.

### 8. Smoke Test

Verify the deployed application is responding correctly (replace `<external-ip-or-domain>` with the actual IP/domain of the VM):

```bash
PROD_URL="http://<external-ip-or-domain>"

# Health check endpoint
echo "→ Health check:"
curl -s -o /dev/null -w "HTTP %{http_code}\n" "$PROD_URL/api/health"

# API root endpoint
echo "→ API root:"
curl -s -o /dev/null -w "HTTP %{http_code}\n" "$PROD_URL/api"

# Dashboard load check
echo "→ Dashboard:"
curl -s -o /dev/null -w "HTTP %{http_code}\n" "$PROD_URL/"
echo ""
```

Expected: All endpoints return `HTTP 200`. If any endpoint returns an error,
check the application logs immediately.

---

> **⚠️ Reminder:** If any step fails after deployment, coordinate with the user
> on whether to roll back. A rollback can be performed by re-deploying the
> previous known-good image from the container registry.
