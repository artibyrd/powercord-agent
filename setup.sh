#!/usr/bin/env bash
# powercord-agent/setup.sh
# Verifies native Antigravity v2.34 plugin layout, skill overlays, hooks, and workspace parity.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== Powercord Developer Kit Verification ==="
echo "Plugin root:    $SCRIPT_DIR"
echo "Workspace root: $WORKSPACE_ROOT"

# 1. Run pure-stdlib plugin & overlay linter
python3 "$SCRIPT_DIR/scripts/lint_skills.py"

# 2. Run hook unit tests
python3 -m unittest discover -s "$SCRIPT_DIR/tests" -v

# 3. Run strict Antigravity plugin validator when agy CLI is installed
if command -v agy >/dev/null 2>&1; then
    echo "Running agy plugin validate --strict..."
    agy plugin validate --strict "$SCRIPT_DIR"
else
    echo "Note: 'agy' CLI not found on PATH; skipping optional native plugin validator."
fi

# 4. Verify umbrella workspace parity when running inside multi-repo ecosystem
if [ -f "$WORKSPACE_ROOT/AGENTS.md" ]; then
    if cmp -s "$WORKSPACE_ROOT/AGENTS.md" "$SCRIPT_DIR/rules/AGENTS.md"; then
        echo "OK: Umbrella AGENTS.md matches powercord-agent/rules/AGENTS.md."
    else
        echo "ERROR: Umbrella AGENTS.md has drifted from powercord-agent/rules/AGENTS.md."
        exit 1
    fi
fi

if [ -d "$WORKSPACE_ROOT/.agents" ]; then
    if [ -e "$WORKSPACE_ROOT/.agents/overrides" ] && [ -f "$WORKSPACE_ROOT/.agents/plugins.json" ]; then
        echo "OK: Umbrella .agents/overrides and .agents/plugins.json verified."
    else
        echo "WARNING: Umbrella .agents/ is missing overrides symlink or plugins.json."
    fi
    if [ -f "$WORKSPACE_ROOT/.agents/skills.json" ]; then
        echo "ERROR: Umbrella .agents/skills.json duplicates plugin skill discovery; remove it and rely on .agents/plugins.json."
        exit 1
    fi
fi

echo "=== All Powercord Developer Kit Checks Passed ==="
