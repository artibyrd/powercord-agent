---
name: powercord-gcp-operations
description: >-
  Use this skill when the user wants to interact with the deployed Powercord production server on GCP,
  including tasks like database maintenance, rescoring MIDI files, managing API keys, or running internal modules in Docker.
---

# Powercord GCP Operations

Run operational tasks directly against the production Container-Optimized OS container on GCP.

---

## 1. Quick Recipes

* **SSH into Production VM**:
  ```bash
  gcloud compute ssh powercord-instance --zone us-central1-a
  ```
* **Locate Container**:
  ```bash
  docker ps
  ```

---

## 2. Deep References

* [Container Operations](references/container-operations.md) — `/app/.venv/bin/python` execution, API key management, and DB restore.
* [Deployment Skill](../powercord-deployment/SKILL.md) — Terraform and Cloud Build release pipelines.
