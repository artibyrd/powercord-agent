---
description: Reconcile the downstream client deployment after upstream commits by discarding local drift, pulling changes, and re-syncing extensions to restore a clean git status.
---

# Reconcile Downstream Client

This workflow reconciles `powercord-downstream-client/` after changes have been
committed in the upstream `powercord-client/` repository. It restores a clean
`git status` without requiring a full teardown and re-clone.

**When to use:** After one or more agent sessions that edited files in
`powercord-client/` (upstream) and/or `powercord-client-extensions/`, when the
downstream repo shows modified or untracked files from framework drift.

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
cd "../powercord-downstream-client"

# Confirm 'origin' points at the local upstream client repo
git remote get-url origin
# Expected: /home/pendragon/Projects/powercord-ecosystem/powercord-client/.
#       or: /home/pendragon/Projects/powercord-ecosystem/powercord-client

# Confirm push is disabled (safety net against accidental pushes)
git remote get-url --push origin
# Expected: DISABLED
```

If the remote is not configured correctly, abort and run
`/fresh-install-downstream-client` instead.

### 2. Discard Local Client Modifications

Discard all unstaged modifications and remove untracked files. Gitignored paths
(including externally installed extensions) are preserved by `git clean`.

```bash
cd "../powercord-downstream-client"

# Discard all modified tracked files
git checkout -- .

# Remove untracked files and directories (respects .gitignore)
git clean -fd
```

### 3. Pull Upstream Changes

Fast-forward to the latest upstream commits:

```bash
cd "../powercord-downstream-client"
git pull origin main
```

If the pull reports merge conflicts, this indicates structural divergence that
cannot be auto-reconciled. In that case, abort and run
`/fresh-install-downstream-client` instead.

### 4. Re-install Client Extensions (Dynamic Discovery)

Dynamically discover and re-install all client extensions from the
`powercord-client-extensions/` directory. This ensures extensions stay in sync
with their source repos, including any new dependency or configuration changes.

```bash
cd "../powercord-downstream-client"

# Dynamically discover and install each client extension
for ext_dir in ../powercord-client-extensions/*/; do
    if [ -d "$ext_dir" ] && [ -f "$ext_dir/pyproject.toml" ]; then
        ext_name=$(basename "$ext_dir")
        echo "→ Re-installing client extension: $ext_name"
        just ext-install "$ext_dir"
    fi
done
```

### 5. Verify Clean Status

Confirm the working tree is clean and extensions are properly installed:

```bash
cd "../powercord-downstream-client"

# Git status should show a clean working tree
git status

# List installed extensions to confirm they loaded
just ext-list
```

Expected: `git status` reports `nothing to commit, working tree clean` (gitignored
extension directories will not appear). `ext-list` shows all expected client
extensions.

### 6. Summary

Report what was reconciled:

```bash
cd "../powercord-downstream-client"

echo ""
echo "=== Client Reconciliation Complete ==="
echo ""
echo "Branch:"
git branch -v
echo ""
echo "Latest commits:"
git log --oneline -5
echo ""
echo "Installed extensions:"
just ext-list
```
