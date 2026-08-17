---
name: powercord-extension-authoring
description: >-
  Author new Powercord server and client extensions from scratch. Use when creating, scaffolding,
  or modifying extension gadgets (cogs, sprockets, widgets, routes, blueprints), writing extension.json
  manifests, setting up Alembic migrations, or registering lifecycle hooks.
---

# Powercord Extension Authoring

Guidelines for creating, structuring, and registering server and companion client extensions.

---

## 1. Extension Directory Layout

```text
powercord-extensions/<extension_name>/
├── extension.json        # Extension manifest
├── pyproject.toml        # Extension package metadata
├── __init__.py           # Hook registrations (on_install, delete_guild_data)
├── cog.py                # Nextcord Discord bot commands
├── sprocket.py           # FastAPI REST endpoints
├── widget.py             # FastHTML dashboard widgets
├── routes.py             # Full-page FastHTML routes
├── actions.py            # Scheduled background jobs (interval / cron)
├── blueprint.py          # Database models & business logic
└── alembic/              # Decoupled migration history
```

---

## 2. Deep References

* [Extension Manifest Spec](references/manifest-spec.md) — `extension.json` format and widget placement.
* [Gadgets Spec](references/gadget-specs.md) — Cogs, sprockets, widgets, and route signatures.
* [Split-Stack Rules](../../rules/split-stack-architecture.md) — Route separation, widget namespaces, and lifecycle hooks.
* [FastHTML DaisyUI Rules](../../rules/fasthtml-daisyui.md) — Card arguments, modals, and signature preservation (`inspect.signature`).
