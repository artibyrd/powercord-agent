---
name: powercord-client-development
description: >-
  Use when creating, modifying, debugging, or testing the Powercord Client desktop application —
  Flet views, async routing, API client, client extensions, or build/distribution pipelines.
---

# Powercord Client Development

Guidelines for developing and testing the cross-platform Flet companion application.

---

## 1. Quick Recipes

* **Run Dev Client with Hot Reload**:
  ```bash
  cd powercord-client && just run
  ```
* **Run Tests**:
  ```bash
  cd powercord-client && just test
  ```
* **Install Client Extension**:
  ```bash
  cd powercord-client && just ext-install ../powercord-client-extensions/<name>
  ```
* **Code Formatting**:
  ```bash
  cd powercord-client && just format
  ```

---

## 2. Deep References

* [Flet Routing & Authentication](references/flet-routing-auth.md) — Async navigation, auth guards, and `PowercordApiClient`.
* [Client Extension System](references/client-extensions.md) — Manifest structure and extension base classes.
* [Flet Client Rules](../../rules/flet-client.md) — View structures and HTTP client standards.
