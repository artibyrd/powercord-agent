---
name: bootstrap-approvals
description: Bootstrap Antigravity IDE agent command approvals in fresh workspaces. Sequentially invokes individual run_command tool calls across core Powercord command shapes so the operator can click "Always Allow" for autonomous workflows.
---

# Bootstrap Approvals Skill (`bootstrap-approvals`)

Use this skill when starting work in a fresh or unprimed Powercord workspace to prime the Antigravity IDE command approval cache.

---

## 1. Prime Command Approval Shapes

Run the following discrete commands in order so the operator can click "Always Allow" once:

```bash
# 1. Workspace status
just -g status

# 2. Pre-commit check (in powercord/)
just check

# 3. Type checking
just typecheck

# 4. Git status check
git status -s

# 5. Poetry package check
poetry run ruff check .
```

---

## 2. Universal Recipe

You can also run `just bootstrap-approvals` directly from `powercord/Justfile`.
