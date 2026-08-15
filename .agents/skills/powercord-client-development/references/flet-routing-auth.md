# Flet Routing & Authentication Reference

Architecture for async routing, auth guarding, and API client singleton in `powercord-client`.

---

## 1. Async Route Handling

`src/app.py` registers an asynchronous `route_change` handler on `page.on_route_change`:
* **Exact Matching**: `/login`, `/dashboard`, `/admin`, `/settings`.
* **Pattern Matching**: `/server/{guild_id}` (extracts target guild ID).
* **Fallback**: Auto-redirects to `/dashboard`.

---

## 2. Auth Guard

Every route (except `/login`) verifies a saved `api_key` in Flet client storage:

```python
api_key = await page.client_storage.get_async("api_key")
if not api_key:
    await page.go_async("/login")
    return
```

---

## 3. PowercordApiClient Singleton

Wraps `httpx.AsyncClient`:
* Base URL resolved from preferences or environment.
* Bearer token set from stored `api_key`.
* All methods are async (`await client.get(...)`, `await client.post(...)`).
