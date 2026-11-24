#!/usr/bin/env python3
"""PreToolUse lifecycle hook gating irreversible GCP and Terraform production commands.

Strictly gates irreversible Powercord production operations with decision="ask"
(inv-no-unauthorized-gcp-deploy) without interfering with normal git workflows
(git safety is delegated to git-guardrails).
"""

from __future__ import annotations

import json
import re
import sys

# Intentionally unanchored so env-var prefixes, wrappers (sudo/env/time/nohup/exec/
# xargs/watch/poetry run), subshells, braces, backticks, bash -c / sh -c, and
# absolute/tilde paths cannot bypass the safety prompt. A false-positive "ask" is
# strictly safer than a silent bypass.
_JUST_PROD_RE = re.compile(
    r"\bjust\b[^;&|\n]*\b(gcp-build|prod-deploy|prod-rollback|prod-db-restore|tf-apply|tf-destroy)\b"
)

_TERRAFORM_MUTATE_RE = re.compile(r"\bterraform\b[^;&|\n]*\b(apply|destroy)\b")

_GCLOUD_BUILDS_SUBMIT_RE = re.compile(r"\bgcloud\b[^;&|\n]*\bbuilds\b[^;&|\n]*\bsubmit\b")


def evaluate_command(command_line: str) -> dict[str, str]:
    """Evaluate a shell command line and return a PreToolUse decision payload."""
    if not command_line:
        return {"decision": "allow"}

    just_match = _JUST_PROD_RE.search(command_line)
    if just_match:
        recipe = just_match.group(1)
        return {
            "decision": "ask",
            "reason": (
                f"Irreversible production operation detected ('just {recipe}'). "
                "Per inv-no-unauthorized-gcp-deploy, explicit human confirmation is required."
            ),
        }

    tf_match = _TERRAFORM_MUTATE_RE.search(command_line)
    if tf_match:
        action = tf_match.group(1)
        return {
            "decision": "ask",
            "reason": (
                f"Production infrastructure mutation detected ('terraform {action}'). "
                "Verify the plan diff and obtain explicit human confirmation before proceeding."
            ),
        }

    if _GCLOUD_BUILDS_SUBMIT_RE.search(command_line):
        return {
            "decision": "ask",
            "reason": (
                "GCP Cloud Build submission detected ('gcloud builds submit'). "
                "Per inv-no-unauthorized-gcp-deploy, explicit human confirmation is required."
            ),
        }

    return {"decision": "allow"}


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        print(json.dumps({"decision": "allow"}))
        return

    tool_call = payload.get("toolCall", {}) if isinstance(payload, dict) else {}
    args = tool_call.get("args", {}) if isinstance(tool_call, dict) else {}
    command_line = ""
    if isinstance(args, dict):
        command_line = str(
            args.get("CommandLine") or args.get("commandLine") or args.get("command") or ""
        )

    print(json.dumps(evaluate_command(command_line)))


if __name__ == "__main__":
    main()
