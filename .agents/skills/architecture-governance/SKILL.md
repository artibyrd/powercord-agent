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
