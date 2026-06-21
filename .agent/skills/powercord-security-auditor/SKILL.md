---
name: powercord-security-auditor
description: >
  Use when creating, modifying, debugging, or testing Security Auditor
  features — rule engine logic, permission bitmask checks, audit scoring,
  REST API endpoints, or dashboard widgets in the utilities extension.
---

# Security Auditor Skill

## Overview

The Security Auditor is a subsystem of the **utilities** extension that
continuously evaluates a Discord guild's role and channel configuration
against eight security rules, producing a 0–100 score and categorised alerts.

## When to Use

- Adding or modifying a `SecurityRule`
- Changing permission bitmask logic or effective-permission computation
- Updating audit REST endpoints or dashboard widgets
- Debugging false-positive / false-negative alerts
- Writing or fixing tests for the rule engine

## Architecture

```
DB Models (app/db/models.py)
  ├─ DiscordAuditorConfig   → staff_separator_role_id, staff_channel_ids[], announcement_channel_ids[]
  ├─ DiscordRole            → name, position, managed, mentionable, permissions (bitmask)
  └─ DiscordChannel         → name, type, category_parent_id, permission_overwrites[]
        │
        ▼
Rule Engine (app/extensions/utilities/widget.py)
  └─ executes SecurityRule checks against cached DB data
        │
        ▼
REST API (app/extensions/utilities/routes.py)
  └─ /api/guild/{guild_id}/audit/*
```

## Permission Bitmask Reference

| Permission       | Bit        | Decimal     |
|------------------|------------|-------------|
| Kick Members     | `1 << 1`   | 2           |
| Ban Members      | `1 << 2`   | 4           |
| Administrator    | `1 << 3`   | 8           |
| Manage Channels  | `1 << 4`   | 16          |
| Manage Server    | `1 << 5`   | 32          |
| View Channel     | `1 << 10`  | 1024        |
| Send Messages    | `1 << 11`  | 2048        |
| Mention Everyone | `1 << 17`  | 131072      |
| Manage Roles     | `1 << 28`  | 268435456   |

> **View Channel gate:** ALWAYS check `1 << 10` first. If denied, every
> other channel-scoped permission is **inert** and the leak must be
> downgraded to **Low** with an `[INERT]` annotation.

## The 8 Security Rules

### 1. Category Permission Baseline
- **Category:** exposure | **Severity:** Medium (High if View Channel exposed; Low if inert)
- **Condition:** A category grants permissions to non-staff roles beyond the server default.
- **Remediation:** Remove unnecessary category-level overwrites; prefer per-channel grants.

### 2. Public Announcement Protection
- **Category:** pings | **Severity:** High
- **Condition:** A non-staff role has Send Messages, Mention Everyone, or `@everyone` in announcement channels.
- **Remediation:** Deny Send Messages and Mention Everyone for all non-staff roles in announcement channels.

### 3. Exposed Staff Channels
- **Category:** exposure | **Severity:** High
- **Condition:** A non-staff role has View Channel allowed in a channel listed in `staff_channel_ids`.
- **Remediation:** Explicitly deny View Channel for every non-staff role on staff channels.

### 4. Unauthorized Chat Pings in Non-Text Locations
- **Category:** pings | **Severity:** Medium
- **Condition:** A non-staff role has Send Messages in voice, stage, thread, or forum channels.
- **Remediation:** Deny Send Messages for non-staff roles on non-text channel types.

### 5. Low-Tier Role Privileges
- **Category:** roles | **Severity:** High
- **Condition:** A role **below** the staff separator has any of: Administrator, Manage Server, Manage Roles, Manage Channels, Kick Members, Ban Members, Mention Everyone.
- **Remediation:** Remove dangerous permissions from roles below the separator or move the role above it.

### 6. General Role Mentionability
- **Category:** pings | **Severity:** Low
- **Condition:** A non-staff, unmanaged role has `mentionable = true`.
- **Remediation:** Disable mentionability or restrict via channel overwrites.

### 7. Suggestive Honeypot Integration
- **Category:** integrations | **Severity:** Medium (Low if discovery channels are protected)
- **Condition:** Guild has public discovery channels but the Honeypot extension is not enabled.
- **Remediation:** Enable the Honeypot extension or remove public discovery channels.

### 8. Over-privileged Bot Integrations
- **Category:** integrations | **Severity:** Medium
- **Condition:** A managed (bot) role has Administrator, Manage Server, Manage Roles, or Manage Channels.
- **Remediation:** Reduce bot role permissions to the minimum required scope.

## Scoring Mechanism

```
Score = max(0, 100 - (15 × N_high + 10 × N_medium + 5 × N_low))
```

- Each **distinct alert** (not each affected entity) counts once per severity.
- A score of 100 means zero alerts.

## REST API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/guild/{guild_id}/audit/score` | Current score + alert counts |
| GET | `/api/guild/{guild_id}/audit/alerts?category=` | Filtered alert list (category: exposure, pings, roles, integrations) |
| GET | `/api/guild/{guild_id}/audit/config` | Current `DiscordAuditorConfig` |
| POST | `/api/guild/{guild_id}/audit/config` | Update config (separator, staff/announcement channel IDs) |

## Effective Permission Computation

1. Start with the role's server-wide `permissions` bitmask.
2. If Administrator bit is set → grant all; stop.
3. Apply **category** overwrites (allow/deny) for the role.
4. Apply **channel** overwrites (allow/deny) for the role — these override category.
5. Use `get_effective_channel_permissions(role, channel)` which handles parent inheritance.

## Staff Separator Concept

A designated role (`staff_separator_role_id`) divides the role hierarchy:
- Roles **at or above** the separator's `position` → staff.
- Roles **below** → non-staff (community / public).

Rules 1–6 use this boundary to decide which roles to scrutinise.

## Testing Security Rules

- Unit tests live alongside the extension; mock `DiscordRole` / `DiscordChannel` objects.
- For each rule, test: true-positive, true-negative, inert-leak downgrade, edge cases (no overwrites, Administrator bypass).
- Integration tests hit the REST API with a seeded test database.
- Use `.cursorrules §5` as the canonical reference for Discord permission precedence.

## Common Pitfalls

1. **Forgetting the View Channel gate** — every channel-scoped check must test `1 << 10` first.
2. **Ignoring category inheritance** — a channel with no overwrites inherits its category's overwrites.
3. **Double-counting alerts** — one rule instance = one alert, even if multiple roles are affected.
4. **Administrator bypass** — `1 << 3` grants all permissions; don't flag channel-level leaks for admin roles.
5. **Managed vs. unmanaged** — Rule 6 only applies to unmanaged roles; Rule 8 only applies to managed (bot) roles.
6. **Separator edge** — a role at exactly the separator position is **staff**, not non-staff.
