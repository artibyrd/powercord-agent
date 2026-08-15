# Flet Client Development Rules

These rules govern the development, styling, and testing of the companion desktop application (`powercord-client`) and client-side extensions (`powercord-client-extensions/*`).

---

## 1. Flet v0.82+ Async Routing Patterns

* **Async Routing Architecture**: Meticulously adhere to Flet v0.82+ async routing conventions:
  * Page views and routes must handle navigation state asynchronously.
  * Avoid synchronous blocking calls in view initialization routines; use `asyncio.create_task()` or background helpers for long-running network operations.
* **HTTP Client Encapsulation**: Use `httpx.AsyncClient` with proper lifecycle management for all API interactions with the Powercord backend server.

---

## 2. Companion Extension Client Rules

* **Companion Client Extensions**: Client extensions under `powercord-client-extensions/<name>/` mirror server extension features:
  * Must contain an `extension.json` manifest defining view routes, titles, icons, and requirements.
  * Views should return structured Flet controls (`ft.View`, `ft.Container`, `ft.ResponsiveRow`).
  * Never import backend server modules (`app.*`, `nextcord`, `fasthtml`) directly into client code. Client code communicates exclusively via HTTP REST endpoints or WebSockets.
