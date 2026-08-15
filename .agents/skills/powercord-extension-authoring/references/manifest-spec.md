# Extension Manifest Specification (`extension.json`)

Every Powercord extension declares its metadata, gadgets, and requirements via `extension.json`.

---

## 1. Schema Example

```json
{
  "name": "midi_library",
  "display_name": "MIDI Library",
  "version": "1.0.0",
  "description": "Catalog and browse MIDI files for Discord servers.",
  "author": "Powercord Team",
  "cogs": ["cog.py"],
  "sprockets": ["sprocket.py"],
  "widgets": ["widget.py"],
  "routes": ["routes.py"],
  "blueprints": ["blueprint.py"],
  "dependencies": {
    "pretty-midi": "^0.2.10"
  },
  "default_widgets": [
    {
      "name": "guild_admin_midi_library_overview_widget",
      "title": "MIDI Library Overview",
      "display_order": 1,
      "col_span": 6
    }
  ]
}
```

---

## 2. Field Definitions

* **`name`**: Unique snake_case extension identifier.
* **`cogs`**: Nextcord Discord bot command cogs.
* **`sprockets`**: FastAPI JSON API routers.
* **`widgets`**: FastHTML dashboard widgets (must follow `admin_` or `guild_admin_` prefix rules).
* **`routes`**: Full-page FastHTML routes.
* **`blueprints`**: Shared models, utilities, or database schemas.
* **`dependencies`**: Python dependencies specific to this extension.
* **`default_widgets`**: Initial grid layout configuration (column spans and display order).
