# Alembic Migrations Reference

Guidance on managing multi-branch Alembic migration histories across the core server and independent extensions.

---

## 1. Migration Structure & CLI Bootstrapping

* **Multi-Branch Design**: Core server migrations reside in `powercord/alembic/versions/`. Each server extension maintains an independent version branch under `app/extensions/<name>/alembic/versions/`.
* **Dynamic `version_locations`**:
  * `app/common/alembic_config.py` provides `_update_alembic_ini()` to register all extension migration paths in `alembic.ini`.
  * `just db-upgrade` and `start.sh` execute this automatically before invoking Alembic CLI commands.

---

## 2. Generating & Running Migrations

* **Generate Revision (Core)**:
  ```bash
  poetry run alembic revision --autogenerate -m "add_table_name"
  ```
* **Generate Revision (Extension)**:
  ```bash
  poetry run alembic revision --autogenerate --version-path=app/extensions/<name>/alembic/versions/ --branch-label=<ext_name> -m "add_table"
  ```
* **Apply Migrations**:
  ```bash
  just db-upgrade
  ```
* **Inspect Heads**:
  ```bash
  poetry run alembic heads
  ```
