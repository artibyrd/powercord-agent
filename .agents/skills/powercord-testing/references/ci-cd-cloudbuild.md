# Cloud Build & CI/CD Testing Reference

---

## 1. Cloud Build Containerized Tests

* **Sidecar Database Requirements**: When Cloud Build runs integration tests requiring a database:
  1. A sidecar PostgreSQL container matching the target version is launched on the shared network (`cloudbuild`).
  2. The pipeline waits for readiness (`pg_isready`) before invoking pytest.
* **Indentation Preservation**: In `cloudbuild.yaml` inline scripts, use `textwrap.dedent` or block scalars (`|`) to prevent Python indentation syntax errors.
