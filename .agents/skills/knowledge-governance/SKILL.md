---
name: knowledge-governance
description: Manage the 4-tier knowledge placement taxonomy, audit AGENTS.md context economy (<800 tokens), and route new learnings into progressive skills vs universal invariants.
---

# Knowledge Governance & Context Economy Skill (`knowledge-governance`)

Use this skill when modifying `AGENTS.md`, creating new skills, running `/remember`, or documenting new invariants across the Powercord ecosystem.

---

## 1. 4-Tier Knowledge Taxonomy

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      4-TIER KNOWLEDGE TAXONOMY                         │
├────────────────────────────────────────────────────────────────────────┤
│ Tier 0: Universal Invariants     → AGENTS.md (<800 tokens)             │
│ Tier 1: Progressive Skills       → .agents/skills/<skill>/SKILL.md     │
│ Tier 2: Shift-Left Test Gates    → tests/governance/test_*.py          │
│ Tier 3: Blueprints & Specs       → docs/blueprints/ & ROADMAP.md       │
└────────────────────────────────────────────────────────────────────────┘
```

### Tier 0: Universal Core Invariants (`AGENTS.md`)
* High-signal, non-negotiable rules organized into Class $\alpha$ (Safety & Authority), Class $\beta$ (Lifecycle & Boundaries), and Class $\gamma$ (Architecture & Interface).
* **Strict Context Budget**: Must remain **< 800 tokens** at all times.
* Zero multi-line procedure scripts or tool installation guides; route procedural details to Tier 1 skills.

### Tier 1: Progressive Subsystem Skills (`.agents/skills/`)
* Modular, on-demand reference guides activated when performing specific subsystem tasks (database migrations, deployment, extension authoring, Flet client).

### Tier 2: Shift-Left Automated Integrity Tests (`tests/governance/`)
* Automated in-memory Pytest gates running in `<3s` asserting 500 LOC compliance, manifest parity, migration consistency, and split-stack isolation.

### Tier 3: Blueprints, Specs & Roadmap (`docs/`, `ROADMAP.md`)
* Deep architectural rationale, sequence diagrams, and phased release milestones.

---

## 2. Knowledge Routing Rules (`/remember`)

When the user gives feedback or a new lesson is learned:
1. **Never dump inline blobs into `AGENTS.md`**.
2. If it is a domain-specific procedure (e.g. Docker flags, Alembic recipes), place it in the corresponding Tier 1 skill under `.agents/skills/`.
3. If it is an architectural invariant that must never regress, add an automated assertion to `tests/governance/`.
4. Only elevate to Tier 0 `AGENTS.md` if it represents a fundamental system-wide invariant that all agents must know upfront.
