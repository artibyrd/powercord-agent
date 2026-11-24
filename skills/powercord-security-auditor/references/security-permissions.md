# Security, Auth & Discord Permission Rules

These rules govern authentication flows, authorization checks, security auditor logic, and Discord permission resolution.

---

## 1. Discord Permission Precedence & Bitmasks

* **View Channel Gating (`1 << 10`)**: When authoring or modifying security audit rules that check channel-scoped permissions (Send Messages, Mention Everyone, etc.), **always gate on View Channel (`1 << 10`) first**. If a role cannot see a channel, all other channel permissions are inert.
* **Category Overwrite Inheritance**: Channel permission checks must account for parent category overwrite inheritance. Use `get_effective_channel_permissions()` with `parent_overwrites` rather than custom inline resolution logic.

---

## 2. Authentication & Authorization Invariants

* **Single Source of Truth (`get_admin_guilds()`)**: Both the Discord OAuth login callback and the post-login `auth_before` middleware must delegate to `get_admin_guilds()` (`helpers.py`) to verify dashboard access.
* **Default-Deny Invariant**: All authorization functions must return `False` (deny) when encountering missing, null, or malformed input (sessions, auth dicts, tokens). Never default to `True` on error paths.
* **Scope-Based API Gating**: FastAPI sprocket endpoints use `api_scope_required(extension, level)` to check scopes hierarchically (`global.admin` > `core.admin` > `{guild_id}.{ext}.admin`).
* **Signature Preservation on Decorators**: Route decorators applied to FastHTML handlers (below `@rt(...)`) must preserve `__signature__` using `inspect.signature(f)` to prevent FastHTML parameter injection failures.

---

## 3. Caching & Mocking Guidelines

* **Database-Backed Checksum Cache**: Security audit evaluations and database queries must not be cached purely on static identifiers (e.g. `guild_id`). Always incorporate a hash/checksum of the underlying state (roles, channels, config records) into the cache key to auto-invalidate on state changes.
* **Mock Schema Conformance**: When mocking security rules or alert outputs in API tests, include core schema keys (`alert_hash`, `parent_hash`, `parent_rule`, `category`, `severity`) to avoid UI crashes.
* **Local Import Mock Paths**: When patching functions imported locally inside function bodies (`from x.y import z`), `@patch` must target the source module (`x.y.z`), not the calling module.
