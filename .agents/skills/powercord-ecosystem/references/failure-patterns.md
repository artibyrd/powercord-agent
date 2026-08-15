# Common Ecosystem Failure Patterns & Mitigations

---

## 1. Discord Client Slash Command Caching (Phantom Bugs)

* **Symptom**: Newly registered or updated slash commands do not appear in the Discord client UI after restarting the bot.
* **Root Cause**: The Discord client application caches guild and global commands aggressively.
* **Mitigation**: Advise the user to force-refresh their Discord client (`Ctrl+R` on desktop or reload app on mobile) before debugging command registration logic.

---

## 2. Alembic CLI Bootstrapping Conflicts

* **Symptom**: `alembic upgrade head` fails with `Can't locate revision`.
* **Root Cause**: The Alembic CLI resolves migration targets from `alembic.ini` on disk *before* executing `env.py`. Dynamically updating `version_locations` inside `env.py` is too late for the CLI runner.
* **Mitigation**: Always ensure `_update_alembic_ini()` is executed first (via `just db-upgrade` or in `start.sh`) so that `alembic.ini` contains all extension migration paths.

---

## 3. Downstream Extension Dependency Resets

* **Symptom**: Downstream tests fail with `ModuleNotFoundError` for an extension package after a git clean.
* **Root Cause**: Reconciling the downstream repository with `git checkout -- .` discards additions in `pyproject.toml` and `poetry.lock`.
* **Mitigation**: Rerun extension installation (`just ext-install ../path`) during the reconciliation workflow (`/reconcile-downstream-server`) to re-register missing dependencies.

---

## 4. Missing `devkit.just` DB Warnings

* **Symptom**: `just test` outputs `[devkit] powercord/devkit.just not found` and tests crash on DB connection.
* **Root Cause**: Running an extension outside the standard sibling directory layout.
* **Mitigation**: Export `POWERCORD_PATH=/path/to/powercord` so the extension resolves `devkit.just`.
