---
name: powercord-client-development
description: >
  Use when creating, modifying, debugging, or testing the Powercord Client
  desktop application — Flet views, async routing, API client, client
  extensions, or build/distribution pipelines.
---

# Powercord Client Development Skill

## Overview

The Powercord Client is a cross-platform desktop application built with
**Flet** that communicates with the Powercord server API over HTTPX.
It has no local database — all persistent data lives on the server.

## When to Use

- Adding or modifying Flet views, routes, or navigation
- Working with the `PowercordApiClient` (HTTPX)
- Creating, installing, or debugging client extensions
- Running, testing, linting, or building the client
- Deploying a downstream client via the `/fresh-install-downstream-client` workflow

## Tech Stack & Version Constraints

| Dependency | Constraint | Notes |
|------------|-----------|-------|
| Python     | `>= 3.11` | Required for `tomllib`, `TaskGroup` |
| Flet       | `>= 0.82.0, < 0.83.0` | **CRITICAL — async routing API changed in 0.82** |
| HTTPX      | `>= 0.28.1, < 0.29.0` | Async HTTP client |
| Pydantic   | `>= 2.12.5, < 3.0.0` | Request/response models |

> [!CAUTION]
> Flet v0.82+ introduced breaking changes to routing. All route handlers
> must be **async**. Do NOT use pre-0.82 synchronous patterns or the
> deprecated `TemplateRoute` class.

## Application Architecture

```
src/
├── app.py                  # Entry point: ft.run(main), route handling, auth guard
├── api_client.py           # PowercordApiClient singleton (httpx.AsyncClient, Bearer auth)
├── views/
│   ├── login.py            # Login view — saves api_key to shared preferences
│   ├── dashboard.py        # Main dashboard after auth
│   ├── server.py           # Per-server view (/server/{guild_id})
│   ├── admin.py            # Admin panel
│   └── settings.py         # User settings
└── extensions/
    ├── base.py             # ClientExtension abstract base class
    └── manager.py          # ClientExtensionManager — discovery, install, uninstall
```

## Routing & Auth

### Route Handling

`app.py` registers an async `route_change` handler on `page.on_route_change`:

1. **Exact match** — `/login`, `/dashboard`, `/admin`, `/settings`
2. **Pattern match** — `/server/{guild_id}` (extract guild ID from path)
3. **Fallback** — redirect to `/dashboard`

### Auth Guard

Every route (except `/login`) checks for a saved `api_key` in Flet
shared preferences. If missing → redirect to `/login`.

```python
api_key = await page.client_storage.get_async("api_key")
if not api_key:
    await page.go_async("/login")
    return
```

## API Client

`PowercordApiClient` is a singleton wrapping `httpx.AsyncClient`:

- Base URL configured at init (server address from preferences or env)
- Bearer token set from stored `api_key`
- All methods are **async** — `await client.get(...)`, `await client.post(...)`
- No local database; every data operation is an API call

## Views

Each view is an **async function** returning a `ft.View`:

```python
async def dashboard_view(page: ft.Page) -> ft.View:
    # fetch data via PowercordApiClient
    # build and return ft.View(route="/dashboard", controls=[...])
```

- Views must not block the event loop — use `await` for all I/O.
- Navigation: `await page.go_async("/route")`.

## Client Extension System

### Extension Structure

```
src/extensions/<ext_name>/
├── extension.json      # Manifest: name, version, description, python_dependencies
└── client_ext.py       # Must export a ClientExtension subclass
```

### Base Class

`ClientExtension` (in `src/extensions/base.py`) requires subclasses to implement:

- `get_routes() -> list[tuple[str, Callable]]` — additional routes
- `get_nav_items() -> list[ft.NavigationRailDestination]` — sidebar entries

### Manager CLI

```bash
python -m src.extensions.manager install <path>   # Copy extension into src/extensions/
python -m src.extensions.manager uninstall <name>  # Remove extension directory
python -m src.extensions.manager list              # List installed extensions
```

`ClientExtensionManager` scans `src/extensions/` for subdirectories containing
`client_ext.py` with a valid `ClientExtension` subclass.

### Example: midi_library_client

Demonstrates: file picker, local directory scanning, archive extraction,
MD5 deduplication, HTTP upload to server API, and progress bar updates.

## Justfile Commands

| Command | Description |
|---------|-------------|
| `just run` | `flet run -d` with hot-reload |
| `just ext-install <path>` | Install a client extension from path |
| `just ext-uninstall <name>` | Uninstall a client extension by name |
| `just ext-list` | List installed client extensions |
| `just build windows` | Production build for Windows |
| `just qa` | Run all quality checks |
| `just lint` | Ruff linting |
| `just format` | Ruff formatting |
| `just check` | Type checking |
| `just test` | `pytest tests src/extensions` |

> `PYTHONPATH=.` is set in the Justfile — imports use `src.` prefix.

## Testing

- Run: `just test` or `pytest tests src/extensions`
- Mock `PowercordApiClient` responses — never hit a live server in tests.
- Test views by asserting the returned `ft.View` has expected controls.
- Extension tests live inside the extension directory and are auto-discovered.

## Building for Distribution

```bash
just build windows      # Produces a standalone .exe via Flet packaging
```

- Ensure all `python_dependencies` from installed extensions are in the
  build environment.
- The downstream client deployment workflow (`/fresh-install-downstream-client`)
  handles cloning, dependency installation, and extension configuration.

## Common Pitfalls

1. **Using sync Flet APIs** — All route/navigation calls must be async (`go_async`, `update_async`). Sync variants will deadlock.
2. **Flet version drift** — Pinned to `>= 0.82.0, < 0.83.0`. Do not upgrade without verifying routing API compatibility.
3. **Blocking the event loop** — Never use `time.sleep()` or synchronous HTTP calls; use `asyncio.sleep()` and HTTPX async methods.
4. **Missing PYTHONPATH** — Imports assume `PYTHONPATH=.`; running outside the Justfile requires setting it manually.
5. **Forgetting auth guard** — Every new view must check `api_key` in shared preferences before rendering.
6. **Extension manifest omissions** — `extension.json` must list all `python_dependencies` or the build will fail.
7. **Hardcoded server URLs** — Always read the base URL from preferences or environment, never hardcode.
