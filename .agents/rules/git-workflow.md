# Git & Workspace Workflow Rules

These rules govern Git operations, workspace normalization, and downstream reconciliation within the Powercord Ecosystem.

---

## 1. Workspace Inspection & Normalization

* **User Justfile Commands**: To inspect or normalize repositories across the workspace, execute global user-level Just recipes:
  * Check branch status and functional modifications (ignoring CRLF differences):
    ```bash
    just -g status
    ```
  * Perform safe line-ending normalization across all clean sub-repositories:
    ```bash
    just -g normalize-all
    ```
* **No Unstaged Hard Resets**: Never execute `git reset --hard` to resolve carriage return (CRLF) noise when the workspace contains uncommitted changes.
* **Line Ending Config**: Ensure `core.autocrlf` is configured to `input` locally in every repository to maintain LF line endings and preserve executable permissions.

---

## 2. Commit & Reconciliation Workflow

* **Strict Commit Prohibition for Agents**: Agents and subagents must **NEVER** execute `git commit`. All commits are reserved for the human developer following review.
* **Upstream Verification Before Downstream Reconciliation**: Verify all backend modifications by running the unit/integration test suite directly within the upstream repository (`powercord/`) using `poetry run pytest`.
* **Downstream Workflow Selection**:
  * **`/reconcile-downstream-server`** / **`/reconcile-downstream-client`**: Lightweight, non-destructive sync used after upstream commits have been approved.
  * **`/fresh-install-downstream-server`** / **`/fresh-install-downstream-client`**: Use when downstream is structurally broken, has merge conflicts, or requires volume reset.
  * **`/audit-workflow-downstream-server`** / **`/audit-workflow-downstream-client`**: Run to verify workspace health, QA pipelines, and recipe validation.
  * **`/deploy-production`**: Live production deployment to GCP. **Requires explicit user confirmation.**
* **Amended Upstream History**: If upstream history is amended or force-pushed, cleanly reset the downstream target:
  ```bash
  git fetch origin
  git reset --hard origin/main
  git clean -fd
  ```
* **Pre-Commit Code Quality**: Prior to human review, run `poetry run ruff check --fix . && poetry run ruff format .` across modified repositories (`powercord/`, `powercord-client/`, `powercord-extensions/*/`, `powercord-client-extensions/*/`).
