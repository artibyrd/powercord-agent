# Security Rule Engine Specification

Specifications for the Security Auditor rule engine, alert deduplication, and score calculation.

---

## 1. Rule Evaluation Flow

1. **Role & Channel Extraction**: Load `DiscordRole`, `DiscordChannel`, and `DiscordAuditorConfig` from the database.
2. **Effective Permission Computation**:
   - Compute effective channel permissions using `get_effective_channel_permissions(role, channel)` with category overwrite inheritance.
   - **View Channel Gating**: Channel-scoped checks must verify View Channel (`1 << 10`) first. If denied, channel permissions are inert.
   - **Administrator Bypass**: Roles with Administrator (`1 << 3`) bypass channel restrictions.
3. **Alert Deduplication & Hashes**:
   - Each alert generates an `alert_hash` and `parent_hash` for stable grouping and active-hash filtering.
4. **Health Score Arc**:
   - Scores range from 0 to 100 based on active alert severities (Critical, High, Medium, Low).
