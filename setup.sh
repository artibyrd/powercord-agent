#!/usr/bin/env bash
# powercord-agent/setup.sh
# Verifies Antigravity 2.0 workspace health, skills, rules, and hooks configuration.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== Powercord Antigravity Workspace Verification ==="
echo "Workspace root: $WORKSPACE_ROOT"

# Verify .agents directory structure
if [ -d "$SCRIPT_DIR/.agents/skills" ] && [ -d "$SCRIPT_DIR/.agents/rules" ] && [ -d "$SCRIPT_DIR/.agents/workflows" ]; then
    echo "✅ Native .agents structure verified in powercord-agent."
else
    echo "❌ Missing core .agents subdirectories in powercord-agent."
    exit 1
fi

# Verify hooks configuration
if [ -f "$SCRIPT_DIR/.agents/hooks.json" ]; then
    echo "✅ Lifecycle hooks (hooks.json) configured."
else
    echo "❌ Missing hooks.json."
    exit 1
fi

# Verify root AGENTS.md
if [ -f "$WORKSPACE_ROOT/AGENTS.md" ]; then
    echo "✅ Universal workspace AGENTS.md present."
else
    echo "❌ Missing workspace AGENTS.md."
    exit 1
fi

# Verify sub-repository AGENTS.md files
REPOS=(
    "powercord"
    "powercord-client"
    "powercord-downstream-server"
    "powercord-extensions"
    "powercord-client-extensions"
)
for repo in "${REPOS[@]}"; do
    if [ -f "$WORKSPACE_ROOT/$repo/AGENTS.md" ]; then
        echo "✅ $repo/AGENTS.md verified."
    else
        echo "⚠️ $repo/AGENTS.md not found."
    fi
done

echo ""
echo "=== All Antigravity Workspace Checks Passed ==="
