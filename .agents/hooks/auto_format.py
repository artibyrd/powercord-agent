#!/usr/bin/env python3
"""PostToolUse lifecycle hook to automatically format modified Python files using ruff."""
import json
import os
import subprocess
import sys

def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        print(json.dumps({}))
        return

    tool_call = payload.get("toolCall", {})
    args = tool_call.get("args", {})
    target_file = args.get("TargetFile", "")

    if target_file and target_file.endswith(".py") and os.path.exists(target_file):
        try:
            # Run ruff format and ruff check --fix
            file_dir = os.path.dirname(target_file)
            subprocess.run(
                ["ruff", "format", target_file],
                capture_output=True,
                timeout=10,
                check=False
            )
            subprocess.run(
                ["ruff", "check", "--fix", target_file],
                capture_output=True,
                timeout=10,
                check=False
            )
        except Exception:
            pass

    print(json.dumps({}))

if __name__ == "__main__":
    main()
