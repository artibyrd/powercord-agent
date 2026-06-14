#!/usr/bin/env bash
# powercord-agent/setup.sh
# Automates linking the agent rules and agent workflow files to the workspace root and sub-repositories.

set -euo pipefail

# Find the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== Powercord Agent Setup ==="
echo "Workspace root detected at: $WORKSPACE_ROOT"

# Function to print usage
usage() {
    echo "Usage: $0 [workspace|repos|all]"
    echo "  workspace : Links .cursorrules and .agent to the workspace root (recommended for full-workspace opening)."
    echo "  repos     : Links .cursorrules and .agent to all individual Git repositories."
    echo "  all       : Links to both the workspace root and all sub-repositories."
    exit 1
}

if [ $# -lt 1 ]; then
    usage
fi

link_workspace() {
    echo "--> Symlinking to workspace root..."
    # Remove existing files/folders to avoid nested link creation
    rm -rf "$WORKSPACE_ROOT/.cursorrules"
    rm -rf "$WORKSPACE_ROOT/.agent"
    
    ln -s "powercord-agent/.cursorrules" "$WORKSPACE_ROOT/.cursorrules"
    ln -s "powercord-agent/.agent" "$WORKSPACE_ROOT/.agent"
    echo "Workspace root links created successfully."
}

link_repos() {
    echo "--> Symlinking to sub-repositories..."
    REPOS=(
        "powercord"
        "powercord-client"
        "powercord-client-extensions/midi_library_client"
        "powercord-extensions/honeypot"
        "powercord-extensions/midi_library"
        "powercord-downstream-server"
    )
    for repo in "${REPOS[@]}"; do
        REPO_PATH="$WORKSPACE_ROOT/$repo"
        if [ -d "$REPO_PATH" ]; then
            echo "    Linking agent knowledge to $repo..."
            
            # Remove existing links to avoid nested link creation
            rm -rf "$REPO_PATH/.cursorrules"
            rm -rf "$REPO_PATH/.agent"
            
            # Resolve correct relative symlink path based on repository nesting depth
            if [[ "$repo" == *"/"* ]]; then
                REL_TARGET="../../powercord-agent"
            else
                REL_TARGET="../powercord-agent"
            fi
            
            ln -s "$REL_TARGET/.cursorrules" "$REPO_PATH/.cursorrules"
            ln -s "$REL_TARGET/.agent" "$REPO_PATH/.agent"
        else
            echo "    [Warning] Repository directory not found: $repo. Skipping."
        fi
    done
    echo "Sub-repository links created successfully."
}

case "$1" in
    workspace)
        link_workspace
        ;;
    repos)
        link_repos
        ;;
    all)
        link_workspace
        link_repos
        ;;
    *)
        usage
        ;;
esac

echo "=== Setup Completed Successfully ==="
