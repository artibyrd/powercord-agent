# Hermetic Mocking Guidelines Reference

---

## 1. Mocking Invariants

* **Hermetic Network Isolation**: Any test invoking Discord APIs, external REST endpoints, or internal loopback requests must be fully mocked to prevent hangs, rate limits, or staging server dependency.
* **Local Import Mocking**: When patching functions imported inside function bodies (e.g. `from app.ui.helpers import get_admin_guilds` within a handler), `@patch` must target the source module (`app.ui.helpers.get_admin_guilds`), not the caller module.
* **Security Schema Keys in Mocks**: When mocking security rules or alert payloads, always populate `alert_hash`, `parent_hash`, `parent_rule`, `category`, and `severity` to avoid UI template `KeyError` crashes.
