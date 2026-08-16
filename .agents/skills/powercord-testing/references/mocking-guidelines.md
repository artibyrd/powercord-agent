# Hermetic Mocking Guidelines Reference

---

## 1. Mocking Invariants

* **Hermetic Network Isolation**: Any test invoking Discord APIs, external REST endpoints, or internal loopback requests must be fully mocked to prevent hangs, rate limits, or staging server dependency.
* **Local Import Mocking**: When patching functions imported inside function bodies (e.g. `from app.ui.helpers import get_admin_guilds` within a handler), `@patch` must target the source module (`app.ui.helpers.get_admin_guilds`), not the caller module.
* **Security Schema Keys in Mocks**: When mocking security rules or alert payloads, always populate `alert_hash`, `parent_hash`, `parent_rule`, `category`, and `severity` to avoid UI template `KeyError` crashes.

---

## 2. Session Dict Mocking

When mocking FastHTML user sessions, include all required session keys:
```python
mock_session = {
    "user_id": 123456789,
    "username": "TestAdmin",
    "avatar": "test_avatar",
    "is_admin": True,
}
```

---

## 3. Database Test Isolation & `@require_admin` Defense-in-Depth

1. **Autouse Test Engine Provisioning**: The `fixture_engine` in `tests/conftest.py` must use `autouse=True` so `powercord_test` and SQLModel metadata tables are provisioned even when running isolated test subsets (e.g. `just verify-dashboard`).
2. **Admin Route Mocking**: When testing routes decorated with `@require_admin`, patch `app.ui.helpers.is_dashboard_admin` to return `True` in addition to providing `is_admin: True` in the session:
```python
@patch("app.ui.helpers.is_dashboard_admin", return_value=True)
def test_admin_route_action(mock_admin, client):
    ...
```

