---
name: architecture-governance
description: Enforces the 500 LOC Ceiling Law with Ratchet, compute_* calculation naming ontology, split-stack FastHTML vs FastAPI isolation, Card signature preservation, and client-server decoupling in Powercord.
---

# Architecture Governance & Modularity Skill (`architecture-governance`)

Use this skill when refactoring, modularizing, or auditing Python source files, extensions, and task runners across the Powercord ecosystem.

---

## 1. Core Modularity & Architecture Laws

### 1. 500 LOC Ceiling Law with Ratchet
* **Strict Limit for New Code**: No new Python file or Justfile shall exceed **500 Lines of Code (LOC)**.
* **Architectural Debt Ratchet (`governance_ratchet.json`)**: Legacy files exceeding 500 LOC are frozen in `powercord/tests/governance/governance_ratchet.json`.
  * Their line counts must decrease monotonically upon modification.
  * When decomposed to $\le 500$ LOC, they are graduated from probation.
  * Milestone targets are formally tracked in `powercord/ROADMAP.md`.

### 2. `compute_*` Pure Function Ontology
* **Naming Standard**: All mathematical, statistical, bitmask, and permission calculation functions must strictly use the `compute_*` prefix.
* **Banned Prefixes**: Functions starting with `calc_*` or `calculate_*` are disallowed.
* **Purity**: Functions prefixed with `compute_*` must be pure with zero database or network side effects.

### 3. Split-Stack FastHTML vs FastAPI REST Isolation
* **FastHTML Routes (`routes.py`, `widget.py`)**: Return HTML elements / FT components for HTMX swapping.
* **FastAPI Sprockets (`sprocket.py`)**: Return structured Pydantic schemas / JSON payloads. Never return HTML strings from sprockets.

### 4. FastHTML Card Integrity & Decorator Signature Preservation
* **Card Invocation**: Always invoke `Card` components as `Card(title, content, **kwargs)`.
* **Decorator Signature**: Custom decorators placed below `@rt(...)` must preserve `__signature__ = inspect.signature(f)` to prevent FastHTML parameter injection failures.

### 5. Client-Server Runtime Isolation
* Companion desktop code (`powercord-client`) must never import backend modules (`app.*`, `nextcord`, `fasthtml`).
* Communication is strictly over asynchronous HTTP REST (`httpx.AsyncClient`) or WebSockets.

### 6. FastHTML Route Typing Convention
* **Dynamic Element Tags**: FastHTML generates HTML tags (`Div`, `Td`, `Form`, `Table`, etc.) dynamically at runtime, causing extensive `[name-defined]` false positives in static typecheckers.
* **Header Convention**: FastHTML route and UI component modules assembling visual trees should place `# mypy: ignore-errors` on line 1.
* **Strict Typing for Domain & Logic**: Pure domain models, API sprockets (`sprocket.py`), database queries, and `compute_*` pure functions must NEVER disable Mypy and must maintain strict static typing.

### 7. Facade-Preserving Monolith Deconstruction
* **Monolith Replacement**: When graduating a file from `governance_ratchet.json`, replace the legacy monolith with an assembler/facade module ($\le 500$ LOC) that re-exports all public symbols (`__all__`).
* **Gadget Loader Scope Preservation**: Define thin pass-through wrapper functions (e.g. `def guild_admin_*_widget(...)`) in the facade module so `extension_loader.py` gadget inspection (`getattr(obj, "__module__", None) == module.__name__`) discovers them.
* **Dynamic Mock Propagation**: In child subpackages querying the database, resolve `Session` and `engine` dynamically from the facade inside handler functions:
  ```python
  import app.extensions.<ext>.widget as facade
  session_cls = getattr(facade, "Session", Session)
  current_engine = getattr(facade, "engine", engine)
  with session_cls(current_engine) as session:
      ...
  ```
  This guarantees that unit tests patching `app.extensions.<ext>.widget.Session` or `engine` continue to inject their mocks into submodules without circular import penalties.

### 8. Container Filesystem Isolation & Path Invariants
* Governance tests and build scripts running in isolated container environments (e.g. Cloud Build `/workspace`) mount only a single repository.
* Tests must never assume sibling repositories (`REPO_ROOT.parent / ...`) exist without graceful skip guards (`if not ROOT.exists(): pytest.skip(...)`).
* Guard all workspace-level file inspections to ensure isolated container builds never crash on absent multi-repo sibling paths.
