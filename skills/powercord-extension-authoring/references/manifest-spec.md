# Extension Manifest Specification (`pyproject.toml` & `extension.json`)

Powercord extensions declare metadata, Discord permissions, migration heads, and default dashboard widgets using one of two manifest formats depending on extension type:

1. **External Server Extensions (`powercord-extensions/*`)**: Declare metadata inside `[tool.powercord]` and `[[tool.powercord.default_widgets]]` in `pyproject.toml` (no separate `extension.json`).
2. **Internal Server Extensions (`powercord/app/extensions/*`) & Companion Client Extensions (`powercord-client-extensions/*`)**: Declare metadata in `extension.json`.

Both formats are validated by `powercord/tests/governance/test_version_and_manifest_parity.py`.

---

## 1. External Server Extensions (`[tool.powercord]` in `pyproject.toml`)

External server extensions (such as `honeypot` and `midi_library`) consolidate package and Powercord metadata into `pyproject.toml`:

```toml
[tool.poetry]
name = "honeypot"
version = "1.1.1"
description = "Automatic spammer-banning via monitored honeypot channels."

[tool.powercord]
discord_permissions = ["ban_members", "manage_channels"]
has_migrations = true
latest_migration_version = "honey0001"
internal = false

[[tool.powercord.default_widgets]]
widget_name = "guild_admin_honeypot_reports"
display_order = 8
column_span = 6

[[tool.powercord.default_widgets]]
widget_name = "guild_admin_honeypot_config"
display_order = 9
column_span = 6
```

### `[tool.powercord]` Field Definitions

* **`discord_permissions`**: List of Discord permission slugs required by the extension's cogs.
* **`has_migrations`**: Boolean indicating whether the extension ships an isolated Alembic migration head under `alembic/versions/`.
* **`latest_migration_version`**: Head revision ID for the extension's isolated Alembic lineage (e.g., `"honey0001"`, `"midi0004"`).
* **`internal`**: Must be `false` for external server extensions.
* **`[[tool.powercord.default_widgets]]`**: Array of default dashboard widget placements:
  * **`widget_name`**: Must match a widget function in `widget.py` and adhere to scope prefixes (`admin_`, `guild_admin_`, or public without `admin` in the name — `inv-widget-scope-namespaces`).
  * **`display_order`**: Integer sort order on first-load dashboard provisioning.
  * **`column_span`**: Integer between `1` and `12` (12-column responsive grid).
  * **`position_config`** *(optional)*: Placement hint for sidebar or floating widgets (e.g., `"left"`, `"bottom-right"`).

---

## 2. Internal Server & Client Extensions (`extension.json`)

Internal built-in server extensions (`custom_content`, `example`, `utilities`) and companion client extensions (`midi_library_client`) use `extension.json`:

### Internal Server Example (`powercord/app/extensions/utilities/extension.json`)

```json
{
  "name": "utilities",
  "version": "1.1.0",
  "description": "Administrative tools for server analytics and security auditing.",
  "python_dependencies": [],
  "discord_permissions": ["manage_roles", "manage_channels"],
  "has_migrations": true,
  "internal": true,
  "default_widgets": [
    {
      "widget_name": "guild_admin_security_overview_widget",
      "display_order": 1,
      "column_span": 4
    }
  ]
}
```

### Companion Client Example (`powercord-client-extensions/midi_library_client/extension.json`)

```json
{
  "name": "midi_library_client",
  "version": "1.0.1",
  "description": "Scans local files and bulk-uploads MIDI archives to the server.",
  "python_dependencies": ["py7zr", "rarfile"]
}
```

### Parity Rules

* If an extension provides **both** `extension.json` and `pyproject.toml`, their `version` fields MUST match (`inv-manifest-version-parity`).
* Every `default_widgets` entry (in either `extension.json` or `[[tool.powercord.default_widgets]]`) MUST have `1 <= column_span <= 12` and obey widget scope prefix rules (`admin_`, `guild_admin_`, or non-admin public names).
