# Shared Development Recipes (`devkit.just`) Reference

The `powercord/devkit.just` module centralizes reusable Just recipes that extensions and the framework depend on during local development.

---

## 1. Provided Recipes

| Recipe | Purpose |
| :--- | :--- |
| `_ensure-db` | Starts a local PostgreSQL 15 Docker container (`powercord-pg-dev`) on port `5433` if one isn't already running. Uses `ss` for port detection and `pg_isready` for readiness polling. |
| `_teardown-dev-db` | Stops and removes the `powercord-pg-dev` container. |

---

## 2. Dynamic Resolution in Extensions

Extensions include a self-resolving `_ensure-db` recipe that discovers and delegates to `devkit.just` at runtime:

```just
[private]
_ensure-db:
    #!/usr/bin/env bash
    pc_path="${POWERCORD_PATH:-../../powercord}"
    devkit="$pc_path/devkit.just"
    if [ -f "$devkit" ]; then
      just --justfile "$devkit" _ensure-db
    else
      echo "[devkit] powercord/devkit.just not found - skipping DB provisioning"
    fi
```

### Resolution Order:
1. `POWERCORD_PATH` environment variable (explicit override — same variable used by `conftest.py`).
2. `../../powercord` relative path (standard sibling layout).
3. Warning message if neither resolves (e.g. CI pipelines managing external DB services).

---

## 3. Resolution Context Matrix

| Context | `_ensure-db` Resolution |
| :--- | :--- |
| Extension cloned next to `powercord/` | ✅ Devkit found via relative path — Docker DB auto-provisioned. |
| Extension in non-standard location | ✅ Set `POWERCORD_PATH` to resolve. |
| Downstream project (`powercord-downstream-server`) | ✅ Project-level Justfile has its own `_ensure-db` via `import 'powercord/devkit.just'`. |
| CI pipelines | ⚠️ Warning printed — CI manages its own DB services. |
