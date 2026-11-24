"""Unit tests for hooks/guard_prod_ops.py PreToolUse safety hook."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
HOOK_SCRIPT = PLUGIN_ROOT / "hooks" / "guard_prod_ops.py"

sys.path.insert(0, str(PLUGIN_ROOT / "hooks"))
import guard_prod_ops  # noqa: E402


class GuardProdOpsUnitTests(unittest.TestCase):
    """Verify irreversible prod ops prompt with decision='ask' and normal ops pass."""

    def test_gates_irreversible_just_prod_recipes(self) -> None:
        gated_commands = [
            "just gcp-build",
            "cd powercord-downstream-server && just prod-deploy",
            "just prod-rollback",
            "just prod-rollback image=us-central1-docker.pkg.dev/proj/powercord/app:v2.5.0",
            "just prod-db-restore backups/pre-deploy.sql.gz",
            "just tf-apply",
            "just tf-apply --yes",
            "cd powercord && just tf-destroy",
            "just -d powercord-downstream-server prod-deploy",
            "just --justfile powercord/Justfile prod-deploy",
            "just check; just gcp-build",
        ]
        for cmd in gated_commands:
            with self.subTest(cmd=cmd):
                result = guard_prod_ops.evaluate_command(cmd)
                self.assertEqual(result["decision"], "ask")
                self.assertIn("reason", result)

    def test_gates_wrapper_env_and_subshell_bypasses(self) -> None:
        bypass_commands = [
            "FOO=1 just prod-deploy",
            "cd x && FOO=bar just gcp-build",
            "TF_LOG=1 terraform apply",
            "sudo just prod-deploy",
            "env just prod-deploy",
            "time just prod-deploy",
            "nohup just prod-deploy",
            "exec just prod-deploy",
            "xargs just prod-deploy",
            "watch just prod-deploy",
            "! just prod-deploy",
            "poetry run just prod-deploy",
            "bash -c 'just prod-deploy'",
            'sh -c "just gcp-build"',
            "(just prod-deploy)",
            "{ just prod-deploy; }",
            "`just prod-deploy`",
            "~/bin/just prod-deploy",
        ]
        for cmd in bypass_commands:
            with self.subTest(cmd=cmd):
                result = guard_prod_ops.evaluate_command(cmd)
                self.assertEqual(result["decision"], "ask")
                self.assertIn("reason", result)

    def test_gates_direct_terraform_and_gcloud_builds_submit(self) -> None:
        gated_commands = [
            "terraform apply",
            "terraform apply -auto-approve",
            "terraform destroy",
            "cd infra && terraform -chdir=gcp apply",
            "terraform plan && terraform apply",
            "gcloud builds submit",
            "gcloud builds submit --config=cloudbuild.yaml --project=powercord",
            "cd powercord-downstream-server && gcloud --project=proj builds submit",
        ]
        for cmd in gated_commands:
            with self.subTest(cmd=cmd):
                result = guard_prod_ops.evaluate_command(cmd)
                self.assertEqual(result["decision"], "ask")
                self.assertIn("reason", result)

    def test_allows_normal_git_and_read_only_commands(self) -> None:
        allowed_commands = [
            "git commit -m 'feat: add v2.5.0 overlays'",
            "just commit 'feat: add v2.5.0 overlays'",
            "just check",
            "just typecheck",
            "just prod-status",
            "just prod-logs 100",
            "just prod-backup pre-deploy",
            "just tf-init",
            "just tf-plan",
            "terraform init",
            "terraform plan",
            "terraform validate",
            "gcloud builds list --limit=5",
            "gcloud compute instances list",
            "",
        ]
        for cmd in allowed_commands:
            with self.subTest(cmd=cmd):
                result = guard_prod_ops.evaluate_command(cmd)
                self.assertEqual(result["decision"], "allow")

    def test_cli_json_roundtrip_ask_and_allow(self) -> None:
        ask_payload = {
            "hookEventName": "PreToolUse",
            "toolCall": {
                "id": "toolu_01",
                "name": "run_command",
                "args": {"CommandLine": "cd powercord-downstream-server && just prod-deploy"},
            },
        }
        proc = subprocess.run(
            [sys.executable, str(HOOK_SCRIPT)],
            input=json.dumps(ask_payload),
            text=True,
            capture_output=True,
            check=True,
        )
        out = json.loads(proc.stdout)
        self.assertEqual(out["decision"], "ask")
        self.assertIn("prod-deploy", out["reason"])

        allow_payload = {
            "hookEventName": "PreToolUse",
            "toolCall": {
                "id": "toolu_02",
                "name": "run_command",
                "args": {"CommandLine": "git commit -m 'chore: sync overlays'"},
            },
        }
        proc_allow = subprocess.run(
            [sys.executable, str(HOOK_SCRIPT)],
            input=json.dumps(allow_payload),
            text=True,
            capture_output=True,
            check=True,
        )
        out_allow = json.loads(proc_allow.stdout)
        self.assertEqual(out_allow["decision"], "allow")

    def test_cli_handles_malformed_stdin_gracefully(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(HOOK_SCRIPT)],
            input="{not valid json",
            text=True,
            capture_output=True,
            check=True,
        )
        out = json.loads(proc.stdout)
        self.assertEqual(out["decision"], "allow")


if __name__ == "__main__":
    unittest.main()
