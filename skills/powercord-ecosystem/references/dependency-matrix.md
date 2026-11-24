# Tech Stack & Dependency Matrix Reference

Explicit dependency boundaries across the Powercord Ecosystem framework.

---

## 1. Powercord Server (Backend)

| Component | Minimum Version | Description |
| :--- | :--- | :--- |
| **Python** | `>=3.12, <3.13` | Backend runtime environment |
| **FastAPI** | `^0.116.1` | REST API web framework |
| **Nextcord** | `^3.1.0` | Discord API wrapper (with voice extras) |
| **SQLModel** | `^0.0.33` | Database ORM layer (Pydantic & SQLAlchemy) |
| **python-fasthtml** | `^0.12.21` | UI rendering utilities for server endpoints |
| **Pytest** | `^9.0.2` | Test execution runner |

---

## 2. Powercord Client (UI / Frontend)

| Component | Minimum Version | Description |
| :--- | :--- | :--- |
| **Python** | `>=3.11` | Client runtime environment |
| **Flet** | `>=0.82.0, <0.83.0` | UI framework (v0.82+ async routing) |
| **HTTPX** | `>=0.28.1, <0.29.0` | Async HTTP client for server communication |
| **Pydantic** | `>=2.12.5, <3.0.0` | Data validation and model serialization |
