---
description: Systematically audit the Powercord downstream client installation and all local development recipes to verify workspace health.
---

# Powercord Downstream Client Audit Workflow

This workflow guides human developers and Antigravity agents in verifying the
health of the Powercord client downstream workspace and local developer recipes.

## Pre-requisites
1. Poetry and Python 3.12 installed on the host.
2. No stale client processes running from previous sessions.

## Timing Instrumentation Guidance
For performance tracking and auditing, you can measure the execution time of any `just` recipe. Wrap the audit command steps with the `just _timed` wrapper recipe as follows:
```bash
just _timed <recipe-name> [arguments]
```
For example, to run and time the QA check or lint recipes:
```bash
just _timed lint
just _timed check
just _timed test
```
This wrapper will execute the command and output the elapsed time upon completion.

---

## Steps

### 0. Pre-flight QA Check

Before proceeding with the downstream audit, perform a pre-flight QA check on
the upstream codebase to ensure a stable base. Run linting and type checking in
the upstream client directory:

```bash
cd "../powercord-client"
just lint
just check
```

If these checks fail, fix the failures in the upstream repository first.

### 1. Perform Downstream Installation

Run the downstream client installation workflow to establish a fresh environment:

```bash
# Call the downstream client setup workflow
/fresh-install-downstream-client
```

Verify that the client application directory is created and dependencies are
installed without errors.

### 2. Run QA Recipe Checks

Execute the code standards and testing commands to verify the code:

```bash
cd "../powercord-downstream-client"

# Run linting
just lint

# Run formatting checks
just format

# Run mypy type checking
just check

# Run the test suite
just test
```

Expected outcome: All lints pass, mypy prints `Success: no issues found`, and
the test suite executes successfully.

### 3. Verify Extension Management

Confirm that all expected client extensions are installed and visible:

```bash
cd "../powercord-downstream-client"

# List installed extensions
just ext-list
```

Expected: All extensions from `powercord-client-extensions/` should appear in
the list. Verify each expected extension is present by name.

### 4. Verify Application Boot

Launch the Flet desktop application and confirm it starts without errors:

```bash
cd "../powercord-downstream-client"

# Start the client application
just run
```

Expected: The application window opens and renders without exceptions in the
console. Manually verify the UI is responsive, then terminate with `Ctrl+C`.

### 5. Summary

Report the audit results:

```bash
cd "../powercord-downstream-client"

echo ""
echo "=== Client Audit Complete ==="
echo ""
echo "Branch:"
git branch -v
echo ""
echo "Latest commits:"
git log --oneline -5
echo ""
echo "Installed extensions:"
just ext-list
echo ""
echo "QA status: All checks passed"
```
