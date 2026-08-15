# Client Extension Architecture Reference

---

## 1. Directory Structure

```text
src/extensions/<ext_name>/
├── extension.json      # Manifest: name, version, python_dependencies
└── client_ext.py       # Exports ClientExtension subclass
```

---

## 2. Base Class Interface

`ClientExtension` subclasses implement:
* `get_routes() -> list[tuple[str, Callable]]`: Returns route tuples.
* `get_nav_items() -> list[ft.NavigationRailDestination]`: Returns sidebar items.

---

## 3. Manager Commands

```bash
just ext-install <path>   # Install client extension
just ext-uninstall <name> # Uninstall client extension
just ext-list             # List installed extensions
```
