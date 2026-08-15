#!/usr/bin/env python3
"""PreToolUse lifecycle hook to enforce safety gates on shell command execution."""
import json
import re
import sys

def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        # If payload parsing fails, do not block
        print(json.dumps({"decision": "allow"}))
        return

    tool_call = payload.get("toolCall", {})
    tool_name = tool_call.get("name", "")
    args = tool_call.get("args", {})
    command_line = args.get("CommandLine", "")

    # Rule 1: Prohibit automated git commits
    if re.search(r"\bgit\s+commit\b", command_line):
        output = {
            "decision": "deny",
            "reason": "AGENTS ARE STRICTLY PROHIBITED FROM RUNNING 'git commit'. Git commits are reserved for the human code reviewer."
        }
        print(json.dumps(output))
        return

    # Rule 2: Intercept unconfirmed GCP deployment
    if re.search(r"\bjust\s+gcp-build\b", command_line):
        output = {
            "decision": "ask",
            "reason": "WARNING: 'just gcp-build' rolls over the live production GCP server. Explicit user confirmation is mandatory."
        }
        print(json.dumps(output))
        return

    # Rule 3: Intercept unconfirmed Terraform apply/destroy
    if re.search(r"\b(terraform|just\s+tf-)(apply|destroy)\b", command_line) and "--yes" not in command_line:
        output = {
            "decision": "ask",
            "reason": "Production infrastructure modification detected. Please verify Terraform diff and obtain user approval."
        }
        print(json.dumps(output))
        return

    # Allow command
    print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    main()
