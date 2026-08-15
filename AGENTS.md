# Powercord Ecosystem Universal Developer Invariants

These invariant rules define mandatory guidelines and constraints for AI agents operating within the Powercord Ecosystem across all repositories.

---

## 1. Agent Behavior & Communication Invariants

* **No Assumptions / Clarify First**: Do not make assumptions regarding project structure, script placement, environment settings, or execution workflows. Ask for clarification before proceeding with file creations or major architectural alterations.
* **No Apologies / Immediate Guardrail Refinement**: Do not generate conversational apologies when a mistake occurs. State the correction factually, identify the root cause, and immediately refine or propose guardrail rules to prevent repetition.
* **File Location Verification**: Before creating any new configuration files, script assets, or automation runners, present target directory options and obtain explicit confirmation before writing files.
* **Critical Design Evaluation**: Provide a rigorous, critical evaluation of design decisions. If a proposal introduces architectural risks or violates separation of concerns, flag why it is suboptimal before solutioning.
* **Grounded in Best Practices**: Prefer native tool capabilities (e.g. poetry, standard Justfiles, Alembic, Docker, Antigravity standard discovery) over ad-hoc workarounds or custom wrappers.
* **Human Code Review Mandatory**: Agents and subagents must **NEVER** execute `git commit` in any repository. Git commits are strictly reserved for the human reviewer. Present changes in a structured format (similar to a pull request description) for human review.
* **Pre-Commit Formatting & Linting**: Always run `poetry run ruff check --fix . && poetry run ruff format .` within the relevant repository prior to presenting changes for human review.
* **Leverage Visualizations**: Proactively include Mermaid diagrams (flowcharts, sequence diagrams, architecture hierarchies) in plans, walkthroughs, and documentation to clarify complex logic.
* **Documentation Impact Assessment**: When modifying authentication, authorization, access control, or user-facing behavior, audit `docs/*.md`, inline docstrings, and `README.md` for stale references and update them.

---

## 2. Workspace & Environment Isolation Invariants

* **Scratch Script Isolation**: Never leave temporary test or debugging scripts (e.g., `check_tables.py`, `kill_stale_tests.py`) in repository roots. Store temporary scripts in the conversation artifacts scratch directory (`<appDataDir>/brain/<conversation-id>/scratch/`) and clean them up before turn completion.
* **No Configuration Pollution for Scratch Files**: Never modify `pyproject.toml`, `.gitignore`, or `tsconfig.json` to ignore or accommodate temporary debugging scripts.
* **Strict Poetry Execution**: Always execute python, pytest, or database commands using `poetry run` (e.g., `poetry run pytest`, `poetry run python ...`) to guarantee virtual environment alignment.
* **Bash Shell Enforcement**: All automation scripts and Just recipes must run in a Bash/POSIX-compliant shell. Never use shell-specific or Windows-specific syntax in automation files.
* **Source Isolation**: Never instantiate `.env` files or build local databases directly within upstream source repositories (`powercord/`, `powercord-client/`). Staging tests and local runs must occur in designated downstream testbeds.
* **No Downstream Sync During Active Development**: Do not sync core changes to downstream repositories during active development. Downstream reconciliation occurs only after human approval and commit of upstream changes via official workflows (`/reconcile-downstream-server`).

---

## 3. Modular Domain Rules Reference

Specific domain guidelines are modularized under `.agents/rules/`:
* [Git & Workspace Workflow](.agents/rules/git-workflow.md)
* [Split-Stack Architecture](.agents/rules/split-stack-architecture.md)
* [Database Testing & Isolation](.agents/rules/database-testing.md)
* [Security & Permissions](.agents/rules/security-permissions.md)
* [FastHTML & DaisyUI](.agents/rules/fasthtml-daisyui.md)
* [Flet Client Guidelines](.agents/rules/flet-client.md)
