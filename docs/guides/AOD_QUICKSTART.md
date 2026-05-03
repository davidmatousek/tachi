# AOD Quickstart

**Version**: 2.0.0
**Read Time**: ~5 minutes

**Related**:
- [AOD Lifecycle Reference](AOD_LIFECYCLE.md) -- Full stage reference, governance tiers, end-to-end example
- [AOD Infographic](AOD_INFOGRAPHIC.md) -- Visual at-a-glance lifecycle diagram
- [SDLC Triad Reference](../AOD_TRIAD.md) -- Governance layer documentation

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AOD LIFECYCLE                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  Discovery                       Delivery                                Quality
  ─────────                       ────────                                ───────

  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │1.Discover│─▶│ 2.Define │─▶│ 3. Plan  │─▶│ 4.Build  │─▶│5.Deliver │─▶│6.Document│
  │          │  │          │  │          │  │          │  │          │  │          │
  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
       │                                                        │
       └──────────────────── Feedback Loop ◀────────────────────┘
```

---

## What is AOD?

AOD is **Agentic Oriented Development** -- a unified lifecycle with 6 stages across 3 phases that takes work from raw idea to delivered, documented feature. Governance gates (Triad sign-offs) operate as a **separate, configurable layer** between stages. AOD answers three questions: **"Should we build this?"** (Discovery), **"How do we build this right?"** (Delivery), and **"Is the quality where it needs to be?"** (Quality).

---

## Quick Start

The fastest path from idea to implementation:

```bash
# Optional: Establish product vision and design identity after make init
/aod.foundation                           # Guided workshop (vision + brand)

# Full flow: 6 commands covering 6 stages
/aod.discover "Add dark mode support"     # Stage 1: Capture idea + ICE score + PM validation
/aod.define dark-mode-support             # Stage 2: Create PRD with Triad review
/aod.plan                                 # Stage 3: Spec → project-plan → tasks (auto-advances)
/aod.build                                # Stage 4: Execute tasks with Architect checkpoints
/aod.deliver                              # Stage 5: Close feature with retrospective
/aod.document                             # Stage 6: Quality review (simplify, docs, CHANGELOG)
```

`/aod.plan` auto-advances through 3 sequential sub-steps (spec → project-plan → tasks). Run it up to 3 times — each invocation advances to the next sub-step on approval. `/aod.document` runs separately after delivery (see [AOD_LIFECYCLE.md](AOD_LIFECYCLE.md) for details).

---

## Command Reference

### Primary Lifecycle Commands (1 per stage)

| Command | Stage | What It Does |
|---------|-------|-------------|
| `/aod.discover` | 1. Discover | Capture idea, ICE score, evidence prompt, PM validation |
| `/aod.define` | 2. Define | Create PRD with Triad review |
| `/aod.plan` | 3. Plan | Router: auto-delegates to `/aod.spec`, `/aod.project-plan`, `/aod.tasks` |
| `/aod.build` | 4. Build | Execute tasks with architect checkpoints |
| `/aod.deliver` | 5. Deliver | Close feature with DoD check and retrospective |
| `/aod.document` | 6. Document | Human-driven code simplification, docstrings, CHANGELOG, API sync |

### Utility Commands

| Command | Purpose |
|---------|---------|
| `/aod.foundation` | Guided post-init workshop (vision + design identity) |
| `/aod.score` | Re-score an existing idea |
| `/aod.status` | Regenerate BACKLOG.md, show stage summary |
| `/aod.analyze` | Cross-artifact consistency check |
| `/aod.clarify` | Resolve spec ambiguities |
| `/aod.checklist` | Generate quality checklist (Definition of Done) |
| `/aod.constitution` | View or update governance constitution |
| `/aod.kickstart` | POC kickstart — generate consumer guide with seed features |
| `/aod.blueprint` | Multi-feature story generation from consumer guide |
| `/aod.orchestrate` | Multi-feature parallel wave execution from `/aod.blueprint` output |
| `/aod.roadmap` | Scaffold quarterly roadmap from completed PRDs |
| `/aod.okrs` | Scaffold OKR document with standard template |
| `/aod.stack` | Manage stack packs (activate, remove, list, scaffold) |
| `/aod.run` | Full lifecycle orchestrator — chains stages 1-5 |

### Template Maintenance Commands

| Command | Purpose |
|---------|---------|
| `/aod.update` | Apply upstream template updates to this project. F129, shipped 2026-04-19. See [DOWNSTREAM_UPDATE.md](DOWNSTREAM_UPDATE.md) and [`aod.update.md`](../../.claude/commands/aod.update.md). |

### Choosing Your Entry Point

| Scenario | Start With |
|----------|-----------|
| Raw idea, need validation | `/aod.discover` |
| Requirements already clear | `/aod.define` |
| Want full automation (stages 1-5) | `/aod.run` |
| Multiple features from a blueprint | `/aod.orchestrate` |

---

## ICE Scoring Quick Reference

ICE stands for **Impact**, **Confidence**, and **Effort** (ease of implementation). Each dimension is scored 1-10, with a total range of 3-30.

### Quick-Assessment Anchors

| Dimension | High (9) | Medium (6) | Low (3) |
|-----------|----------|------------|---------|
| **Impact** | Transformative | Solid improvement | Minor enhancement |
| **Confidence** | Proven pattern | Some unknowns | Speculative |
| **Effort (Ease)** | Days of work | Weeks of work | Months of work |

### Priority Tiers

| Score Range | Priority | Action |
|-------------|----------|--------|
| 25-30 | P0 (Critical) | Fast-track to development |
| 18-24 | P1 (High) | Queue for next sprint |
| 12-17 | P2 (Medium) | Consider when capacity allows |
| < 12 | Deferred | Auto-defer; requires PM override via `/aod.validate` |

### Auto-Defer Gate

Ideas scoring below 12 are automatically deferred (labeled `type:idea` on GitHub). The PM can override this gate using `/aod.validate NNN` where NNN is the GitHub Issue number.

---

## Governance Tiers

Governance gates are a configurable layer. Choose a tier that matches your risk level.

| Tier | Gate Count | When to Use |
|------|-----------|-------------|
| **Light** | 2 | Solo developers, prototypes, internal tools |
| **Standard** (default) | 6 | Team projects, production features |
| **Full** | all | Regulated industries, critical systems |

Configure in `.aod/memory/constitution.md`:
```yaml
governance:
  tier: standard  # light | standard | full
```

---

## Triad Roles Summary

| Role | Defines | Authority | Key Question |
|------|---------|-----------|--------------|
| **PM** | What & Why | Scope & requirements | Does this solve the right problem? |
| **Architect** | How | Technical decisions | Is this technically sound? |
| **Team-Lead** | When & Who | Timeline & resources | Can we deliver this effectively? |

---

## Sign-off Requirements

| Stage | Required Sign-offs | Command |
|-------|-------------------|---------|
| Define | PM + Architect + Team-Lead | `/aod.define` |
| Plan: Spec | PM | `/aod.spec` (via `/aod.plan`) |
| Plan: Architecture | PM + Architect | `/aod.project-plan` (via `/aod.plan`) |
| Plan: Tasks | PM + Architect + Team-Lead | `/aod.tasks` (via `/aod.plan`) |
| Build | Architect checkpoints | `/aod.build` |
| Deliver | DoD check | `/aod.deliver` |
| Document | Human approval per step | `/aod.document` |

Each step auto-validates before proceeding. If a reviewer returns **CHANGES REQUESTED**, the phase repeats until all required sign-offs are **APPROVED**.

---

## File Locations

```
Active Feature:
  .aod/                          # Source of truth
  ├── spec.md                    # Feature specification
  ├── plan.md                    # Implementation plan
  └── tasks.md                   # Task breakdown

Feature Archives:
  specs/{NNN}-{feature}/         # Per-feature archives

Product Artifacts:
  docs/product/02_PRD/           # PRD documents
  docs/product/_backlog/         # BACKLOG.md (auto-generated)
```

---

## Troubleshooting

**"Idea auto-deferred but I want to build it"**
Use `/aod.validate NNN` (where NNN is the GitHub Issue number) to submit the idea for PM review. The PM can override the auto-defer gate with documented rationale.

**"Is Discovery mandatory?"**
No. You can start directly at `/aod.define` without any Discovery artifacts.

**"Spec has no PM sign-off"**
Use `/aod.plan` (which invokes `/aod.spec`) instead of creating spec.md manually. The command automatically invokes PM review.

**"Plan blocked after multiple iterations"**
Split the feature into smaller, independently deliverable pieces, or escalate to the user for scope clarification.

**"Command not found"**
All lifecycle commands use the `/aod.*` prefix. Run `/help` to see all available commands. Old `/pdl.*` and `/triad.*` namespaces were removed in Feb 2026 — see [archive/AOD_MIGRATION.md](archive/AOD_MIGRATION.md) if you need the historical mapping.
