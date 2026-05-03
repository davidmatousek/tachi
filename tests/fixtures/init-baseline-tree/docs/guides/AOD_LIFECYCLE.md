# AOD Lifecycle Reference

**Version**: 1.0.0
**Status**: Active
**Spec Reference**: `specs/010-aod-lifecycle-formalization/spec.md` (FR-011)

---

## The AOD Lifecycle

The AOD Lifecycle is a single, linear sequence of **6 stages** organized into **3 phases**. All work passes through these stages from idea to delivered, documented feature.

```
         DISCOVERY                    DELIVERY                                     QUALITY
.-----------------------. .----------------------------------------------. .---------------.
|                       | |                                              | |               |
| [1. Discover]-->[2. Define]-->[3. Plan]-->[4. Build]-->[5. Deliver]----->[ 6. Document] |
|                       | |                                              | |               |
'-----------------------' '----------------------------------------------' '---------------'
                                                                |
                                                         Feedback Loop
                                                                |
                                                    New ideas --> Discover
```

Stages 1-5 are orchestrated by `/aod.run`. Stage 6 (Document) is a separate human-driven command (`/aod.document`) for post-delivery quality review.

### Lifecycle with Governance Gates

Governance gates are Triad approval checkpoints that operate **between stages**, not as stages themselves. Gates determine who approves before work advances.

```
  DISCOVERY PHASE                          DELIVERY PHASE                               QUALITY PHASE
  ================                         ======================================       ==============

  +------------+       +----------+        +---------+       +---------+       +---------+       +----------+
  |            |       |          |        |         |       |         |       |         |       |          |
  | 1.Discover |       | 2.Define |        | 3. Plan |       | 4.Build |       |5.Deliver|       |6.Document|
  |            |       |          |        |         |       |         |       |         |       |          |
  | Capture    |       | Create   |        | Spec    |       | Execute |       | Close   |       | Simplify |
  | ideas +    |       | PRD with |        | + Arch  |       | tasks   |       | feature |       | docstrings|
  | ICE score  |       | Triad    |        | plan +  |       | with    |       | + retro |       | CHANGELOG|
  |            |       | review   |        | tasks   |       | reviews |       |         |       | API docs |
  +-----+------+       +----+-----+        +----+----+       +----+----+       +----+----+       +----+-----+
        |                    |                   |                 |                 |                 |
        v                    v                   v                 v                 v                 v
   +---------+         +---------+     +------------------+  +---------+       +---------+       +---------+
   |  GATE   |         |  GATE   |     |      GATES       |  |  GATE   |       |  GATE   |       |  GATE   |
   | PM val. |         | PRD     |     | PM spec sign-off |  | Arch    |       | DoD     |       | Human   |
   | (tier-  |         | review  |     | PM+Arch plan     |  | check-  |       | check   |       | approval|
   | depend.)|         | (tier-  |     | Triple sign-off  |  | points  |       |         |       | per step|
   +---------+         | depend.)|     +------------------+  +---------+       +---------+       +---------+
                       +---------+
```

---

## Pre-Lifecycle: Foundation Workshop

Before entering the lifecycle, new projects should run `/aod.foundation` to establish product vision and design identity. This is a one-time setup that populates `product-vision.md` and creates brand files (`brand.md`, `tokens.css`, `anti-patterns.md`) from one of 6 design archetypes.

**Command**: `/aod.foundation` (also supports `--vision` and `--design` flags for partial execution)

---

## Stage Definitions

### 1. Discover (Discovery Phase)

**Purpose**: Capture new feature ideas, score them with ICE, and gather evidence of the problem being solved.

| | |
|---|---|
| **Primary Command** | `/aod.discover` |
| **Key Output** | Scored idea with evidence, GitHub Issue (`stage:discover`) |
| **Governance Gate** | PM validation (tier-dependent) |

### 2. Define (Discovery Phase)

**Purpose**: Create a Product Requirements Document (PRD) through structured Triad review, establishing the "what" and "why" for a feature.

| | |
|---|---|
| **Primary Command** | `/aod.define` |
| **Key Output** | Approved PRD in `docs/product/02_PRD/` |
| **Governance Gate** | Triad PRD review (tier-dependent) |

### 3. Plan (Delivery Phase)

**Purpose**: Produce the specification, architecture plan, and task breakdown. This is the most complex stage, with 3 sequential sub-steps managed by a single router command.

| | |
|---|---|
| **Primary Command** | `/aod.plan` (router -- auto-delegates to sub-steps) |
| **Key Output** | `spec.md`, `plan.md`, `tasks.md` in `.aod/` |
| **Governance Gates** | PM spec sign-off, PM+Architect plan sign-off, Triple sign-off on tasks |

**Sub-steps** (auto-detected by `/aod.plan`):

| Sub-step | Command | Sign-off |
|----------|---------|----------|
| Specification | `/aod.spec` | PM sign-off |
| Architecture Plan | `/aod.project-plan` | PM + Architect sign-off |
| Task Breakdown | `/aod.tasks` | PM + Architect + Team-Lead sign-off |

### 4. Build (Delivery Phase)

**Purpose**: Execute tasks from the approved task breakdown with architect checkpoints during implementation.

| | |
|---|---|
| **Primary Command** | `/aod.build` |
| **Key Output** | Implemented feature on feature branch |
| **Governance Gate** | Architect checkpoints during execution |

### 5. Deliver (Delivery Phase)

**Purpose**: Close the feature with Definition of Done validation and a structured retrospective that feeds learnings back into discovery.

| | |
|---|---|
| **Primary Command** | `/aod.deliver` |
| **Key Output** | Closed feature, retrospective, KB entry, new ideas (feedback loop) |
| **Governance Gate** | DoD check (all tiers) |

### 6. Document (Quality Phase)

**Purpose**: Human-driven post-delivery quality review. Each step presents findings interactively and commits only what the human approves. This is the one stage designed for human judgment rather than agent automation.

| | |
|---|---|
| **Primary Command** | `/aod.document` |
| **Key Output** | Simplified code, docstrings, CHANGELOG entries, API doc sync, KB review |
| **Governance Gate** | Human approval per step (accept/reject/skip) |

**Steps** (each requires human approval):

| Step | What It Does |
|------|-------------|
| Code Simplification | Runs `/simplify` on changed files, presents diff for review |
| Docs-Lint | Flags complex undocumented functions, suggests docstrings |
| CHANGELOG | Generates entries from commits, categorized by conventional commit type |
| API Sync | Compares code endpoints against OpenAPI spec, flags mismatches |
| KB Review | Reviews institutional knowledge entries captured during Build/Deliver |

**Note**: Stage 6 is NOT part of the `/aod.run` orchestrator. It runs separately after Deliver because it requires sustained human interaction and judgment.

---

## Governance Tiers

Governance gates are a **separate, configurable layer** on top of the lifecycle. Choose a tier that matches your project's risk level. The lifecycle stages are the same regardless of tier -- only the gates change.

### Tier Overview

| Tier | Gate Count | When to Use |
|------|-----------|-------------|
| **Light** | 2 | Solo developers, prototypes, internal tools, hackathons |
| **Standard** (default) | 6 | Team projects, production features, most work |
| **Full** | all | Regulated industries, critical systems, high-stakes launches |

### Tier Descriptions

**Light (2 gates)**: Minimal ceremony. Triple sign-off at Plan stage and DoD at Deliver. Discover and Define gates are optional or skipped. For work where speed matters more than risk mitigation.

**Standard (6 gates, default)**: Balanced governance. PM validation at Discover, PRD review at Define, PM+Architect sign-off plus Triple sign-off at Plan, Architect checkpoints at Build, DoD at Deliver. Appropriate for most production work.

**Full (all gates)**: Maximum rigor. Everything in Standard plus a separate PM spec sign-off before the architecture plan. For environments where audit trails and formal approval at every boundary are required.

### Configuration

Set the governance tier in `.aod/memory/constitution.md`:

```yaml
governance:
  tier: standard  # light | standard | full
```

### Rules

- Triple sign-off (PM + Architect + Team-Lead on tasks) is the **minimum governance floor** for all tiers
- DoD check and Architect build checkpoints apply to **all tiers**
- Document stage (human approval per step) applies to **all tiers**
- Tier affects only Discover, Define, and Plan stage gates
- Tier is configured per project, not per feature

---

## Governance Gate Matrix

Which gates activate at each stage, per tier.

| Tier | Discover | Define | Plan | Build | Deliver | Document |
|------|----------|--------|------|-------|---------|----------|
| **Light** | Optional | Skip | Triple sign-off only | Architect checkpoints | DoD | Human approval |
| **Standard** | PM validation | PRD review | PM+Arch + Triple | Architect checkpoints | DoD | Human approval |
| **Full** | PM validation | PRD review | PM spec + PM+Arch plan + Triple | Architect checkpoints | DoD | Human approval |

**Reading the matrix**: "PM+Arch + Triple" means PM and Architect sign-off on the architecture plan, followed by PM + Architect + Team-Lead sign-off on the task breakdown. "PM spec" means a separate PM sign-off on the specification before the architecture plan proceeds.

---

## Command Reference

### Primary Lifecycle Commands (1 per stage)

| Command | Stage | Phase | What It Does |
|---------|-------|-------|-------------|
| `/aod.discover` | Discover | Discovery | Capture idea, ICE score, evidence prompt, PM validation |
| `/aod.define` | Define | Discovery | Create PRD with Triad review |
| `/aod.plan` | Plan | Delivery | Router: auto-delegates to `/aod.spec`, `/aod.project-plan`, `/aod.tasks` |
| `/aod.build` | Build | Delivery | Execute tasks with architect checkpoints |
| `/aod.deliver` | Deliver | Delivery | Close feature with DoD check and retrospective |
| `/aod.document` | Document | Quality | Human-driven code simplification, docstrings, CHANGELOG, API sync |

### Plan Sub-Commands (invoked by `/aod.plan` router)

| Command | Plan Sub-Step | Output |
|---------|--------------|--------|
| `/aod.spec` | Specification | `spec.md` with PM sign-off |
| `/aod.project-plan` | Architecture Plan | `plan.md` with PM + Architect sign-off |
| `/aod.tasks` | Task Breakdown | `tasks.md` with Triple sign-off |

### Utility Commands (no governance gates)

| Command | Purpose |
|---------|---------|
| `/aod.score` | Re-score an existing idea (stays in Discover stage). See [`aod.score.md`](../../.claude/commands/aod.score.md). |
| `/aod.status` | Regenerate BACKLOG.md on demand, show stage summary. See [`aod.status.md`](../../.claude/commands/aod.status.md). |
| `/aod.analyze` | Cross-artifact consistency check. See [`aod.analyze.md`](../../.claude/commands/aod.analyze.md). |
| `/aod.clarify` | Resolve spec ambiguities. See [`aod.clarify.md`](../../.claude/commands/aod.clarify.md). |
| `/aod.checklist` | Generate quality checklist (Definition of Done). See [`aod.checklist.md`](../../.claude/commands/aod.checklist.md). |
| `/aod.constitution` | View or update governance constitution. See [`aod.constitution.md`](../../.claude/commands/aod.constitution.md). |

### Bootstrap & Orchestration Commands

| Command | Purpose |
|---------|---------|
| `/aod.run` | Full lifecycle orchestrator — chains stages 1-5 with session-resilient state and governance gates at every boundary. See [`aod.run.md`](../../.claude/commands/aod.run.md). |
| `/aod.orchestrate` | Multi-feature parallel wave execution from `/aod.blueprint` output; groups GitHub Issues into P0/P1/P2 waves and spawns batch sessions. |
| `/aod.kickstart` | POC kickstart — transforms a raw project idea into a sequenced consumer guide with 6-10 seed features. See [`aod.kickstart.md`](../../.claude/commands/aod.kickstart.md). |
| `/aod.blueprint` | Generate ICE-scored, dependency-ordered GitHub Issues from a consumer guide; feeds `/aod.orchestrate`. See [`aod.blueprint.md`](../../.claude/commands/aod.blueprint.md). |

### Scaffolding Commands

| Command | Purpose |
|---------|---------|
| `/aod.roadmap` | Scaffold a quarterly roadmap document from completed PRDs with PM sign-off. See [`aod.roadmap.md`](../../.claude/commands/aod.roadmap.md). |
| `/aod.okrs` | Scaffold an OKR document with standard template and PM sign-off. See [`aod.okrs.md`](../../.claude/commands/aod.okrs.md). |

### Template Maintenance Commands

| Command | Purpose |
|---------|---------|
| `/aod.update` | Apply upstream template updates to this project (F129, shipped 2026-04-19). See [DOWNSTREAM_UPDATE.md](DOWNSTREAM_UPDATE.md) and [`aod.update.md`](../../.claude/commands/aod.update.md). |

### Minimum Feature Sequence

```
/aod.discover --> /aod.define --> /aod.plan --> /aod.build --> /aod.deliver --> /aod.document
```

Six commands. `/aod.plan` auto-advances through 3 sequential sub-steps (spec → project-plan → tasks). Run it up to 3 times — each invocation advances to the next sub-step on approval. `/aod.document` runs separately after delivery for human-driven quality review.

---

## Where Do I Find Things?

Artifacts are organized into 3 zones. Each zone has a distinct purpose.

### `.aod/` Zone -- Active Feature State

The source of truth for the current feature being worked on.

| File | Purpose |
|------|---------|
| `spec.md` | Feature specification (Plan stage output) |
| `plan.md` | Architecture plan (Plan stage output) |
| `tasks.md` | Task breakdown (Plan stage output) |
| `memory/constitution.md` | Governance principles + tier configuration |

### `specs/NNN-*/` Zone -- Feature Archives

Per-feature directory for research, design artifacts, and review records.

| File | Purpose |
|------|---------|
| `research.md` | Pre-specification research findings |
| `data-model.md` | Entity model and state machine design |
| `checklists/` | Quality checklists for the feature |
| `agent-assignments.md` | Task-to-agent mapping (Team-Lead output) |
| `spec.md` | Archived spec (copied from `.aod/`) |
| `plan.md` | Archived plan (copied from `.aod/`) |
| `tasks.md` | Archived tasks (copied from `.aod/`) |

### `docs/product/` Zone -- Product Documentation

Long-lived product artifacts that span features.

| File/Directory | Purpose |
|----------------|---------|
| `02_PRD/` | Product Requirements Documents (Define stage output) |
| `02_PRD/INDEX.md` | PRD index with status tracking |
| `_backlog/BACKLOG.md` | Auto-generated backlog grouped by lifecycle stage |
| `_backlog/archive/` | Archived legacy backlog files |
| `01_Product_Vision/` | Product vision and strategy |
| `03_Product_Roadmap/` | Roadmap and timeline |
| `05_User_Stories/` | User story library |
| `06_OKRs/` | Objectives and Key Results |

---

## Traceability Model

The complete chain from idea to delivery:

```
GitHub Issue #21 (type:idea label, stage:discover)
  └── US-001 (User Story)
        └── PRD 005 (docs/product/02_PRD/005-*.md)
              └── spec.md (specs/005-*/spec.md)
                    └── plan.md (specs/005-*/plan.md)
                          └── tasks.md (specs/005-*/tasks.md)
                                └── Implementation files
```

Each artifact references its source:

- User Story -> links to GitHub Issue #NNN via Source column
- PRD -> links to GitHub Issue #NNN and US-NNN via `source` frontmatter
- Spec -> links to PRD via `prd_reference` frontmatter
- Plan -> links to Spec via `spec_reference`
- Tasks -> links to Plan via `plan_reference`

---

## Status Flow Diagram

### Idea Status (GitHub Issues)

```
[Capture] -> stage:discover (>= 12) -> stage:define (PRD started)
                |
                +-> Deferred (< 12) -> Re-scored (>= 12) -> stage:define
                |
                +-> Rejected (PM rejected)
```

### Feature Lifecycle (GitHub Issue labels)

```
stage:discover -> stage:define -> stage:plan -> stage:build -> stage:deliver -> stage:document
```

---

## End-to-End Example

A dark-mode feature walked through all 6 stages.

### Step 1: Discover

```bash
/aod.discover "Add dark mode support for the dashboard"
```

- GitHub Issue **#21** created with `type:idea` and `stage:discover` labels
- ICE Score: 24 (I:9 C:9 E:6) -- P1 (High)
- Evidence: "Customer feedback -- 12 requests in last quarter"
- PM agent reviews: APPROVED

### Step 2: Define

```bash
/aod.define dark-mode-support
```

- PRD created with `source.github_issue: 21`
- GitHub Issue label updated to `stage:define`

### Step 3: Plan (3 sub-steps)

```bash
/aod.plan    # Invocation 1: generates spec.md (PM sign-off)
/aod.plan    # Invocation 2: generates plan.md (PM + Architect sign-off)
/aod.plan    # Invocation 3: generates tasks.md (Triple sign-off)
```

- GitHub Issue label updated to `stage:plan`

### Step 4: Build

```bash
/aod.build
```

- Tasks executed with Architect checkpoints
- GitHub Issue label updated to `stage:build`

### Step 5: Deliver

```bash
/aod.deliver
```

- DoD validated, retrospective captured, KB entry created
- GitHub Issue label updated to `stage:deliver`
- New ideas from retrospective -> new GitHub Issues with `stage:discover`

### Step 6: Document

```bash
/aod.document
```

- Code simplification reviewed and approved
- Docstrings added to complex undocumented functions
- CHANGELOG updated with feature entries
- API docs synced (if OpenAPI spec exists)
- KB entries validated

Feature delivered and documented with full traceability from original idea to shipped code.

---

**Last Updated**: 2026-04-20
**Maintained By**: Product Manager (lifecycle governance)
**Source**: Feature 010 -- AOD Lifecycle Formalization (consolidated with former AOD_LIFECYCLE_GUIDE.md on 2026-04-20)
