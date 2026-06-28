---
description: Reconcile the downstream server deployment after upstream commits by discarding local drift, pulling changes, and re-syncing extensions to restore a clean git status.
---

# Reconcile Downstream Server

This workflow reconciles `powercord-downstream-server/` after changes have been
committed in the upstream `powercord/` repository. It restores a clean `git status`
without requiring a full teardown and re-clone.

**When to use:** After one or more agent sessions that edited files in `powercord/`
(upstream) and/or `powercord-extensions/`, when the downstream repo shows modified
or untracked files from framework drift.

> **Important:** This workflow intentionally discards all local modifications in the
> downstream repo. The downstream is a deployment target — source changes must never
> originate here. If an agent accidentally committed source edits in the downstream,
> those changes will be lost. This is by design per the ecosystem's source isolation
> model.

---

## Steps

### 1. Pre-flight Safety Checks

Verify we are working with the correct downstream deployment and that the
upstream remote is properly configured:

```bash
cd "../powercord-downstream-server"

# Confirm 'origin' points at the local upstream repo
git remote get-url origin
# Expected: /home/pendragon/Projects/powercord-ecosystem/powercord/.
#       or: /home/pendragon/Projects/powercord-ecosystem/powercord

# Confirm push is disabled (safety net against accidental pushes)
git remote get-url --push origin
# Expected: DISABLED
```

If the remote is not configured correctly, abort and run
`/fresh-install-downstream-server` instead.

### 2. Discard Local Framework Modifications

Discard all unstaged modifications and remove untracked files. Gitignored paths
(including externally installed extensions like `app/extensions/honeypot/` and
`app/extensions/midi_library/`) are preserved by `git clean`.

```bash
cd "../powercord-downstream-server"

# Discard all modified tracked files
git checkout -- .

# Remove untracked files and directories (respects .gitignore)
git clean -fd
```

### 3. Pull Upstream Changes

Fast-forward to the latest upstream commits:

```bash
cd "../powercord-downstream-server"
git pull origin main
```

If the pull reports merge conflicts, this indicates structural divergence that
cannot be auto-reconciled. In that case, abort and run
`/fresh-install-downstream-server` instead.

### 4. Re-install Extensions (Dynamic Discovery)

Dynamically discover and re-install all server extensions from the
`powercord-extensions/` directory. This ensures extensions stay in sync with
their source repos, including any new dependency or migration changes.

```bash
cd "../powercord-downstream-server"

# Dynamically discover and install each extension
for ext_dir in ../powercord-extensions/*/; do
    if [ -d "$ext_dir" ] && [ -f "$ext_dir/pyproject.toml" ]; then
        ext_name=$(basename "$ext_dir")
        echo "→ Re-installing extension: $ext_name"
        just ext-install "$ext_dir"
    fi
done
```

### 5. Verify Clean Status

Confirm the working tree is clean and extensions are properly installed:

```bash
cd "../powercord-downstream-server"

# Git status should show a clean working tree
git status

# List installed extensions to confirm they loaded
just ext-list
```

Expected: `git status` reports `nothing to commit, working tree clean` (gitignored extension directories will not appear). `ext-list` shows all expected extensions.

### 5b. Verify Migration Graph & Dependencies

Verify that all extension dependencies were successfully installed and that the Alembic migration config is fully updated:

```bash
cd "../powercord-downstream-server"

# Run database migrations to auto-generate/verify the config (override password if using standard dev db container)
POWERCORD_POSTGRES_PASSWORD=test_pass just db-upgrade

# Print migration heads to confirm extension paths are registered
poetry run alembic heads
```

Expected:
- `poetry.lock` and `pyproject.toml` should show modified status in `git status` if any dependencies had been lost and restored.
- `alembic heads` lists all three migration heads: `0caed23d30a5 (head)`, `honey0001 (head)`, and `midi0002 (head)`.

### 6. Rebuild Containers (If Running)

If Docker containers are running, rebuild them to pick up the changes:

```bash
cd "../powercord-downstream-server"

# Check if containers are running
if docker compose ps --quiet 2>/dev/null | grep -q .; then
    echo "Containers are running — rebuilding..."
    just rebuild-target
    just _wait-for-compose-db
else
    echo "No containers running — skipping rebuild."
    echo "Run 'just rebuild-target' when ready to start the containerized environment."
fi
```

### 7. Summary

Report what was reconciled:

```bash
cd "../powercord-downstream-server"

echo ""
echo "=== Reconciliation Complete ==="
echo ""
echo "Branch:"
git branch -v
echo ""
echo "Latest commits:"
git log --oneline -5
echo ""
echo "Installed extensions:"
just ext-list
echo ""
echo "Container status:"
docker compose ps 2>/dev/null || echo "(not running)"
```
