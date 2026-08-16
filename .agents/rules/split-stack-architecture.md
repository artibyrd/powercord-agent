# Split-Stack Architecture & Extension Rules

These rules govern the architectural boundary between FastHTML UI rendering, FastAPI REST endpoints, and extension packaging.

---

## 1. Split-Stack Separation

* **FastHTML Routes vs FastAPI Sprockets**:
  * FastHTML routes (`routes.py` / `widget.py`) return HTML fragments for server-rendered UI and HTMX swapping.
  * FastAPI sprockets (`sprocket.py`) return structured JSON payloads for companion client applications and API consumers.
  * Keep logic clearly separated; do not return HTML from sprocket endpoints or JSON from FastHTML views unless explicitly designed as an API proxy.
* **Decoupled Database Schemas**: Extensions must manage their own tables via independent, isolated Alembic version histories inside their extension directory. Never alter core migrations for extension tables.
* **Lifecycle Hooks & Data Purging**:
  * Extensions managing guild-scoped data must register a `delete_guild_data` hook in their `__init__.py`.
  * Global catalogs (e.g., `midi_library`) must be explicitly excluded from guild-level data deletion to preserve catalog integrity.
* **Downstream Target Isolation**:
  * Never perform ad-hoc file copies (`cp`) between `powercord/` and `powercord-downstream-server/`.
  * Downstream testing environments must only be updated using standard skill recipes (`just rebuild-target`, `just ext-install`, `just db-import`).

---

## 2. Sprocket & Widget Conventions

* **Sprocket Partial Updates**: When implementing sprocket `PATCH` or `POST` config routes, handle partial payloads by checking `payload.model_fields_set` or `exclude_unset=True` rather than blindly overwriting database fields with `None` or default values.
* **Widget Naming & Scope Filtering**: Adhere strictly to prefix-based namespace conventions for FastHTML dashboard widgets:
  * `admin_` prefix: Global admin controls (rendered on `/admin`).
  * `guild_admin_` prefix: Guild-specific admin configurations (rendered on `/dashboard/{guild_id}`).
  * All other prefixes/names: Public or visitor widgets.
  * Pages rendering widgets must validate and filter widgets based on their scope prefixes to prevent missing argument `TypeError` exceptions.
* **Dynamic Extension Discovery**: Never hardcode extension names in workflows or automation. Iteratively discover extensions by scanning `powercord-extensions/*/` (server) or `powercord-client-extensions/*/` (client), using the presence of `pyproject.toml` as the sentinel for a valid extension.
* **Discord Entity Resolution & DB Fallbacks**:
  * Dashboard views displaying Discord entities (e.g. roles, channels) must never display raw numerical Snowflake IDs.
  * If the live Bot Internal API is unreachable, always fall back to querying cached database models (`DiscordRole`, `DiscordChannel`) and display a subtle cache indicator (e.g., `(Loaded from DB cache)`).
