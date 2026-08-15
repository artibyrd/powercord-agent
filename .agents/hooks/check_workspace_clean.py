#!/usr/bin/env python3
"""Stop lifecycle hook to verify no temporary scratch scripts remain in the root directory."""
import json
import os
import sys

SCRATCH_PATTERNS = [
    "check_tables.py",
    "kill_stale_tests.py",
    "clear_pg_locks.py",
    "scratch_",
    "test_fail.log",
    "test_output.log"
]

def main():
    try:
        payload = json.load(sys.stdin)
        workspace_paths = payload.get("workspacePaths", [])
    except Exception:
        workspace_paths = ["."]

    found_scratch = []
    for root_dir in workspace_paths:
        if not os.path.isdir(root_dir):
            continue
        for fname in os.listdir(root_dir):
            if any(pattern in fname for pattern in SCRATCH_PATTERNS):
                found_scratch.append(os.path.join(root_dir, fname))

    if found_scratch:
        output = {
            "decision": "continue",
            "reason": f"Scratch files detected in workspace root: {', '.join(found_scratch)}. Please remove them before completing."
        }
        print(json.dumps(output))
    else:
        print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    main()
