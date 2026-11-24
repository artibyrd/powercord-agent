# Powercord Auth Architecture Reference

Powercord employs a dual-layer authentication and authorization system separating the FastHTML UI server from the FastAPI REST API server.

---

## 1. UI Server Authentication (FastHTML)

* **Beforeware (`auth_before` in `app/ui/auth.py`)**:
  * Global session-based auth gate applied to all FastHTML routes except those in `Beforeware.skip` (e.g. `/login`, `/logout`, `/dev/login`, plus extension `PUBLIC_PATHS`).
* **Login Flow**:
  1. User initiates Discord OAuth login.
  2. Handled by `discord_callback`.
  3. Invokes `get_admin_guilds()` to verify dashboard access permissions.
  4. Session is populated with user profile and authorized guild list.
  5. Redirects to `/profile`.
* **`get_admin_guilds()` (`app/ui/helpers.py`)**:
  * The **single source of truth** for authorization.
  * Checks Discord Administrator permission (`1 << 3`), `DashboardAccessRole`, and `ApiUserRole`.
  * Used by both the login callback and the post-login `auth_before` middleware.
* **`@require_admin` (`app/ui/main_ui.py`)**:
  * Defense-in-depth decorator on `/admin/*` route handlers.
  * Calls `is_dashboard_admin()` to verify the session user is a global admin.
  * Preserves `__signature__` for FastHTML parameter injection compatibility (`inspect.signature(f)`).
* **Navigation Visibility**:
  * `_check_admin_for_nav()` in `app/ui/page.py` performs a live database lookup via `is_dashboard_admin()` rather than relying on stale cached session data.

---

## 2. API Server Authentication (FastAPI)

* **Token-Based Authentication**:
  * `get_current_api_user` dependency resolves Bearer tokens via SHA-256 hashed DB lookup.
* **Scope-Based Gating**:
  * `api_scope_required(extension, level)` dependency generator checks scopes hierarchically:
    `global.admin` > `core.admin` > `{guild_id}.{ext}.admin`, etc.
* **Internal System Key**:
  * Bot-to-API key (`system_internal`) uses a plaintext fast-path comparison, mapped to `global.admin` permissions.

---

## 3. Invariants

* **Default-Deny Invariant**: Login gates and post-login authorization checks **must** use the same access criteria — both delegate to `get_admin_guilds()`. Missing or invalid tokens/sessions must always deny access.
