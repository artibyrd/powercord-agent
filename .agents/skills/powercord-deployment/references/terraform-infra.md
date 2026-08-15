# Terraform Infrastructure Reference

Overview of production infrastructure configuration under `powercord/terraform/`.

---

## 1. Module Overview

| File | Resource |
| :--- | :--- |
| `compute.tf` | Container-Optimized OS VM running containerized Powercord stack |
| `iam.tf` | Service accounts and IAM role bindings |
| `network.tf` | VPC network and firewall rules |
| `storage.tf` | GCS state and media buckets |
| `secrets.tf` | Secret Manager references |
| `monitoring.tf` | Uptime checks and alert policies |

---

## 2. Terraform Recipes

```bash
just tf-init                     # Initialize working directory
just tf-plan                     # Preview diff
just tf-apply --yes              # Apply infrastructure changes (after user review)
just tf-destroy                  # Tear down infrastructure (requires explicit confirmation)
```
