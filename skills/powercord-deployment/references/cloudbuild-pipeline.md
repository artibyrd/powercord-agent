# Cloud Build & CI/CD Pipeline Reference

---

## 1. Cloud Build Stages (`cloudbuild.yaml`)

| Stage | Action |
| :--- | :--- |
| **1. Postgres Sidecar** | Spawns a PostgreSQL container for integration testing. |
| **2. QA Gate** | `poetry install` → wait for DB → `ruff check` → `ruff format --check` → `mypy` → `pytest`. |
| **3. Docker Build** | Builds image with `BUILD_ID` and `latest` tags. |
| **4. Push to Registry** | Pushes to Artifact Registry (`us-central1-docker.pkg.dev/$PROJECT_ID/powercord/powercord-app`). |
| **5. Terraform Deploy** | Runs `terraform init` and `terraform apply -auto-approve`. |

---

## 2. Mandatory Production Gating

> [!CAUTION]
> **`just gcp-build` deploys directly to the live GCP Production VM.**
> Agents must **NEVER** execute `just gcp-build` without direct, explicit user confirmation.
