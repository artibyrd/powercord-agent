---
name: powercord-security-auditor
description: >-
  Use when creating, modifying, debugging, or testing Security Auditor features — rule engine logic,
  permission bitmask checks, audit scoring, REST API endpoints, or dashboard widgets in the utilities extension.
---

# Powercord Security Auditor System

Architectural specifications and testing practices for Discord RBAC audits and security rules.

---

## 1. Quick Invariants

* **Permission Gating**: Always gate channel-scoped checks on View Channel (`1 << 10`).
* **Category Overwrites**: Always use `get_effective_channel_permissions()` with `parent_overwrites`.
* **State Checksums**: Always key evaluation caches on a hash/checksum of Discord role and channel table states.

---

## 2. Deep References

* [Rule Engine Specification](references/rule-engine-specs.md) — Evaluation flow, alert hashes, and health scoring.
* [Security & Permissions Rules](../../rules/security-permissions.md) — Bitmask precedence, lowest admin boundary, and default-deny invariants.
* [Database Testing Rules](../../rules/database-testing.md) — Mock schemas, table teardown, and session rollback handling.
