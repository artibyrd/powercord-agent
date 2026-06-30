---
name: powercord-extension-authoring
description: >
  Author new Powercord server and client extensions from scratch. Use when
  creating, scaffolding, or modifying extension gadgets (cogs, sprockets,
  widgets, routes, blueprints), writing extension.json manifests, setting up
  Alembic migrations, registering lifecycle hooks, or structuring standalone
  extension repositories and their client-side companions.
---

# Powercord Extension Authoring

## Overview

A Powercord **extension** is a self-contained feature module that lives in
`app/extensions/<name>/`. Each extension is composed of **gadgets** — Python
files that the `GadgetInspector` (`app/common/extension_loader.py`) discovers
at startup via AST analysis. No manual registration is needed; drop the file in
and it is auto-wired.

## When to Use

Activate this skill when the user wants to:

- Scaffold a new extension or add gadgets to an existing one
- Write or edit `extension.json` manifests
- Create cogs (Discord slash commands), sprockets (REST API), widgets (dashboard UI), or routes (full pages)
- Set up Alembic migrations for an extension
- Build a standalone extension repo or client-side companion
- Register lifecycle hooks (`on_install`, `on_uninstall`, `delete_guild_data`)

---

## Extension Folder Structure

```
app/extensions/<name>/
├── __init__.py            # Lifecycle hooks via register_hook()
├── extension.json         # Manifest (required)
├── cog.py                 # Discord commands (Nextcord cog)
├── sprocket.py            # REST API routes (FastAPI router)
├── widget.py              # Dashboard widgets (FastHTML renderables)
├── routes.py              # Full-page routes (FastHTML)
├── blueprint.py           # Shared helpers / models
├── extension.just         # Optional extension-specific just recipes
└── alembic/
    ├── env.py
    └── versions/          # Decoupled multibase migrations
```

All gadget files are **optional** — include only what the extension needs.

---

## extension.json Manifest

```json
{
  "name": "my_extension",
  "version": "1.0.0",
  "description": "Short description of the extension.",
  "python_dependencies": [],
  "discord_permissions": [],
  "has_migrations": false,
  "latest_migration_version": null,
  "internal": false,
  "global_only": false,
  "widget_settings": {
    "display_order": 50
  }
}
```

| Field | Type | Notes |
|---|---|---|
| `name` | `str` | Snake_case, must match directory name |
| `version` | `str` | SemVer string |
| `python_dependencies` | `list[str]` | pip-style specifiers; installed at extension install time |
| `discord_permissions` | `list[str]` | Nextcord permission names the cog requires |
| `has_migrations` | `bool` | Set `true` if `alembic/` directory exists |
| `latest_migration_version` | `str\|null` | Alembic revision ID of the newest migration |
| `internal` | `bool` | Hide from public extension catalogue |
| `global_only` | `bool` | Extension cannot be toggled per-guild |
| `widget_settings.display_order` | `int` | Position in 12-column widget grid (lower = earlier) |

---

## Gadget Templates

### Cog (`cog.py`)

Cogs provide Discord slash commands. Inherit from `GuildAwareCog` and use
Nextcord 3.x decorators. The `GadgetInspector` detects any class inheriting
`commands.Cog`; `CogContexts` (method prefix `cc_`) and `CogPersists`
(persistent Views/Modals) are also discovered via AST.

```python
import nextcord
from nextcord.ext import commands
from app.common.guild_cog import GuildAwareCog

class MyCog(GuildAwareCog):
    """Short description shown in help."""

    def __init__(self, bot: commands.Bot):
        super().__init__(bot)

    @nextcord.slash_command(description="Say hello")
    async def hello(self, interaction: nextcord.Interaction):
        await interaction.response.send_message("Hello from my_extension!")

def setup(bot: commands.Bot):
    bot.add_cog(MyCog(bot))
```

### Sprocket (`sprocket.py`)

Sprockets are FastAPI `APIRouter` instances. The inspector looks for
`APIRouter()` calls. Routes are auto-mounted at `/api/<extension_name>/...`
but sprocket authors MUST explicitly apply `Depends(api_scope_required(extension_name, level))`
to each endpoint to secure it, as the auto-applied middleware has been removed from `load_sprockets()`.

```python
from fastapi import APIRouter, Depends
from app.common.auth import api_scope_required

router = APIRouter()

@router.get("/status", dependencies=[Depends(api_scope_required("my_extension", level="user"))])
async def get_status():
    """GET /api/my_extension/status"""
    return {"ok": True}
```

### Widget (`widget.py`)

Widgets are FastHTML renderable functions. Scope is determined by name prefix:

| Prefix | Scope |
|---|---|
| `admin_` | Global admin dashboard |
| `guild_admin_` | Guild-specific admin panel |
| *(none)* | Public dashboard |

```python
from fasthtml.common import *
from fasthtml.svg import *

def guild_admin_overview(guild_id: int):
    """Widget shown on the guild admin panel."""
    return Card(
        "Overview",                          # title (first positional arg)
        P("Extension stats go here."),       # content (second positional arg)
        cls="shadow-md",
    )
```

> **⚠️ Card()**: Always pass `title` as the first arg and `content` as the
> second. Never pass content as the first positional argument.

> **DaisyUI tooltips**: Use `cls='tooltip tooltip-<position>'` with
> `data_tip='Tooltip text'` — not `title` attribute.

`WidgetSettings` respects `display_order` from `extension.json` for
positioning within the 12-column grid.

### Routes (`routes.py`)

Full-page routes use FastHTML. You **must** define a `register_routes(rt)`
callback. Declare `PUBLIC_PATHS` for unauthenticated access.

```python
from fasthtml.common import *

PUBLIC_PATHS = ["/my_extension/public"]

def register_routes(rt):
    @rt("/my_extension/dashboard")
    def dashboard(request):
        return Titled("Dashboard", P("Authenticated page."))

    @rt("/my_extension/public")
    def public_page(request):
        return Titled("Public", P("No login required."))
```

#### Route Authentication & Authorization

Extension routes registered via `register_routes(rt)` are automatically
protected by the core `Beforeware` (session-based auth). However:

- **Public routes** that should be accessible without login must declare
  a `PUBLIC_PATHS` constant at module level (see `discovery.md`). The
  core framework dynamically extends the `Beforeware.skip` list from
  these declarations at startup.
- **Admin-only mutation routes** in the core framework use the
  `@require_admin` decorator (defined in `main_ui.py`) for
  defense-in-depth. Extensions with admin routes in `routes.py` should
  implement similar guards using `is_dashboard_admin()` from
  `app.ui.helpers`.
- **Guild-level access** is checked via `_check_guild_admin()` in
  `dashboard.py`, which verifies the user has admin permissions on the
  specific guild via Discord Admin perms, `DashboardAccessRole`, or
  `ApiUserRole`.
- **FastHTML decorators** must preserve `__signature__` using
  `inspect.signature(f)` — see `.cursorrules` Section 5 for the
  pattern. Without this, FastHTML's parameter injector silently stops
  resolving `req`, `sess`, and path parameters.

### Blueprint (`blueprint.py`)

Blueprints hold shared SQLAlchemy models, helpers, or constants used across
other gadgets in the same extension. No special discovery — just import from
sibling modules.

```python
from sqlalchemy import Column, Integer, String
from app.common.database import Base

class MyModel(Base):
    __tablename__ = "my_extension_data"
    id = Column(Integer, primary_key=True)
    value = Column(String, nullable=False)
```

---

## Lifecycle Hooks

Register hooks in `__init__.py` using `register_hook(name, event, callback)`.
Supported events: `on_install`, `on_uninstall`, `delete_guild_data`.

```python
from app.common.extension_loader import register_hook

async def _on_install(guild_id: int): pass
async def _on_uninstall(guild_id: int): pass
async def _delete_guild_data(guild_id: int): pass

register_hook("my_extension", "on_install", _on_install)
register_hook("my_extension", "on_uninstall", _on_uninstall)
register_hook("my_extension", "delete_guild_data", _delete_guild_data)
```

---

## Alembic Migration Setup

Extensions use **decoupled multibase** migrations — each extension owns its own
Alembic environment in `<ext>/alembic/`.

1. Create `alembic/` directory with `env.py` pointing at the extension's models.
2. Generate a migration: `alembic revision --autogenerate -m "add my_table"`
3. Set `has_migrations: true` and `latest_migration_version` in `extension.json`.

Migrations run automatically during extension install/upgrade.

---

## Standalone Repo Structure

External extensions live in separate repos under `powercord-extensions/<name>/`:

```
powercord-extensions/my_extension/
├── app/extensions/my_extension/   # Symlinked into server at install
│   ├── __init__.py
│   ├── extension.json
│   ├── cog.py
│   └── ...
├── tests/
│   └── conftest.py               # Wired to devkit.just DB provisioning
├── pyproject.toml
├── poetry.lock
├── Justfile                       # Must include ext-install / ext-uninstall
└── README.md
```

Install/uninstall via just recipes:
```bash
just ext-install /path/to/powercord-extensions/my_extension
just ext-uninstall my_extension
just ext-list
```

---

## Client Extension Structure

Client-side companions live in `powercord-client-extensions/<name>/`:

```
powercord-client-extensions/my_extension/
├── client_ext.py                  # ClientExtension subclass
├── pyproject.toml
└── ...
```

```python
from powercord_client.base import ClientExtension

class MyClientExtension(ClientExtension):
    name = "my_extension"

    async def on_ready(self):
        pass
```

---

## Testing

Tests live in `tests/` with `conftest.py` wired to `devkit.just` DB provisioning.
Set `POWERCORD_PATH` to the local server checkout. Run via `Justfile` recipes.

```python
import pytest

@pytest.mark.asyncio
async def test_cog_hello(bot, guild):
    cog = bot.get_cog("MyCog")
    assert cog is not None
```

---

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| `Card(content, title)` arg order | `Card(title, content, **kwargs)` — title is always first |
| DaisyUI tooltip via `title=` attr | Use `cls='tooltip tooltip-top'` + `data_tip='...'` |
| Sprocket missing auth middleware | Sprocket authors MUST explicitly apply `Depends(api_scope_required(extension_name, level))` to secure each endpoint |
| Forgetting `register_routes(rt)` | Routes file is silently ignored without this callback |
| `PUBLIC_PATHS` not a module-level list | Must be a top-level `list[str]` in `routes.py` |
| Migration not detected | Ensure `has_migrations: true` and `latest_migration_version` are set |
| Extension name ≠ directory name | `extension.json` `name` must match the folder name exactly |
| SVG imports from wrong module | Use `from fasthtml.svg import *`, not custom SVG strings |
| Missing `setup()` in cog | Nextcord requires the module-level `setup(bot)` function |
| Lifecycle hook not firing | Verify `register_hook` is called at module level in `__init__.py` |
