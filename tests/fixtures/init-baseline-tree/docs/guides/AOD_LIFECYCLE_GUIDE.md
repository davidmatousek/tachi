# AOD Complete Lifecycle Guide

**Version**: 2.0.0
**Read Time**: ~8 minutes

**Related**:
- [AOD Quickstart](AOD_QUICKSTART.md) -- Quick onboarding guide
- AOD Infographic -- (Infographic coming soon)
- [SDLC Triad Reference](../AOD_TRIAD.md) -- Governance layer documentation
- [AOD Lifecycle Reference](AOD_LIFECYCLE.md) -- Stage definitions and governance tiers

This guide covers the complete product lifecycle from raw idea to shipped feature using the AOD (Agentic Oriented Development) Lifecycle.

---

## Visual Flow

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

---

## Complete Lifecycle Overview

```
Discovery                       Delivery                                        Quality
─────────────────────         ──────────────────────────────────              ──────────

Stage 1      Stage 2      Stage 3        Stage 4      Stage 5      Stage 6
Discover  →  Define    →  Plan        →  Build     →  Deliver   →  Document
    │            │            │              │            │              │
    ▼            ▼            ▼              ▼            ▼              ▼
GitHub       PRD doc     spec.md +      Implemented  Closed feature  Simplified code +
Issue +                  plan.md +      feature      + retrospective docstrings +
evidence                 tasks.md                    + KB entry      CHANGELOG +
                                                                     API docs
```

---

## Stage 1: Discover

**Command**: `/aod.discover "your idea"` (full flow with PM validation) or `/aod.discover` with capture-only mode

**What happens**:
1. A GitHub Issue is created with a descriptive title and `type:idea` label
2. The idea description is recorded
3. ICE scoring (Impact, Confidence, Effort) is applied
4. Evidence prompt: "Who has this problem, and how do you know?"
5. PM validation gate (tier-dependent)
6. If approved: user story generated, `stage:discover` label applied to the GitHub Issue

**Output**: GitHub Issue with `stage:discover` label, scored idea with evidence.

**ICE Quick Reference**:
- P0 (25-30): Critical — fast-track
- P1 (18-24): High — next sprint
- P2 (12-17): Medium — when capacity allows
- Deferred (< 12): Auto-deferred — PM override via `/aod.validate`

---

## Stage 2: Define

**Command**: `/aod.define <topic>`

**What happens**:
1. PRD creation flow begins with Triad review
2. If a backlog item is selected, PRD frontmatter includes source traceability:
   ```yaml
   source:
     github_issue: 21
     story_id: US-001
   ```
3. PM drafts, Architect + Team-Lead review, PM finalizes

**Output**: PRD in `docs/product/02_PRD/{NNN}-{topic}-{date}.md`

**Governance Gate**: Triad PRD review (tier-dependent)

---

## Stage 3: Plan

**Command**: `/aod.plan`

`/aod.plan` auto-advances through 3 sequential sub-steps (spec → project-plan → tasks). Run it up to 3 times — each invocation advances to the next sub-step on approval.

| Sub-step | Direct Command | Output | Sign-off |
|----------|---------------|--------|----------|
| Specification | `/aod.spec` | spec.md | PM |
| Architecture Plan | `/aod.project-plan` | plan.md | PM + Architect |
| Task Breakdown | `/aod.tasks` | tasks.md + agent-assignments.md | PM + Architect + Team-Lead |

> These sub-commands are invoked automatically by `/aod.plan`. Run them individually only if you need manual control over a specific sub-step.

**Router logic**:
1. No spec.md → delegates to `/aod.spec`
2. Spec approved, no plan.md → delegates to `/aod.project-plan`
3. Plan approved, no tasks.md → delegates to `/aod.tasks`
4. All approved → "Plan stage complete"

### Specification (Sub-step 1)

**What happens**:
1. Research phase: KB query, codebase exploration, architecture docs, web search
2. Spec generation with functional requirements, user scenarios, acceptance criteria
3. PM review and sign-off

### Architecture Plan (Sub-step 2)

**What happens**:
1. Architecture decisions, API contracts, data models
2. PM + Architect dual sign-off

### Task Breakdown (Sub-step 3)

**What happens**:
1. Tasks decomposed from plan with agent assignments
2. Parallel execution waves defined
3. PM + Architect + Team-Lead triple sign-off

---

## Stage 4: Build

**Command**: `/aod.build` (flags: `--no-security`, `--no-design-check`)

**What happens**:
1. Pre-flight validation (session resumption safety)
2. Execute tasks from approved task breakdown
3. Architect checkpoints at wave boundaries
4. Design quality gate (validates UI code against brand identity and design rules)
5. Security scan (OWASP Top 10 + CVE analysis)
6. Code simplification review

**Output**: Implemented feature on feature branch

**Governance Gate**: Architect checkpoints, design quality gate, security gate

---

## Stage 5: Deliver

**Command**: `/aod.deliver`

**What happens**:
1. Definition of Done validation
2. Structured retrospective:
   - Estimated vs. actual duration
   - "What surprised us" (lessons learned)
   - "What should we do next" (new ideas)
3. KB entry from lessons learned
4. New ideas fed back to Discover as GitHub Issues with `stage:discover` label

**Output**: Closed feature, retrospective, KB entry, feedback loop to Discover

**Governance Gate**: DoD check (all tiers)

---

## Stage 6: Document

**Command**: `/aod.document`

**What happens**:
1. Code Simplification — runs `/simplify` on changed files, presents diff for human review
2. Docs-Lint — flags complex undocumented functions, suggests docstrings
3. CHANGELOG — generates entries from commits, categorized by conventional commit type
4. API Sync — compares code endpoints against OpenAPI spec, flags mismatches
5. KB Review — validates institutional knowledge entries captured during Build/Deliver

Each step presents findings interactively — the human accepts, rejects, or skips each one. This is the one stage designed for human judgment rather than agent automation.

**Output**: Simplified code, docstrings, CHANGELOG entries, API doc sync, KB review

**Governance Gate**: Human approval per step (all tiers)

**Note**: Stage 6 runs separately after delivery -- see [AOD_LIFECYCLE.md](AOD_LIFECYCLE.md) for details.

---

## Commands by Stage

| Stage | Command | Output |
|-------|---------|--------|
| — | `/aod.foundation` | Product vision + design identity (recommended post-init) |
| 1. Discover | `/aod.discover <idea>` | GitHub Issue + scored idea |
| 2. Define | `/aod.define <topic>` | PRD |
| 3. Plan | `/aod.plan` (router) | spec.md, plan.md, tasks.md |
| 4. Build | `/aod.build` | Implemented feature (includes design quality gate) |
| 5. Deliver | `/aod.deliver` | Closed feature + retrospective |
| 6. Document | `/aod.document` | Simplified code, docstrings, CHANGELOG, API docs |

**Post-init**: `/aod.foundation` is not a lifecycle stage — it's a one-time setup that establishes product vision and design identity before entering the lifecycle.

**Full flow shortcut**: `/aod.discover <idea>` covers the entire Discover stage in one command.

---

## Traceability Model

The complete traceability chain from idea to delivery:

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
- User Story → links to GitHub Issue #NNN via Source column
- PRD → links to GitHub Issue #NNN and US-NNN via `source` frontmatter
- Spec → links to PRD via `prd_reference` frontmatter
- Plan → links to Spec via `spec_reference`
- Tasks → links to Plan via `plan_reference`

---

## Status Flow Diagram

### Idea Status (GitHub Issues)

```
[Capture] → stage:discover (>= 12) → stage:define (PRD started)
                │
                └→ Deferred (< 12) → Re-scored (>= 12) → stage:define
                │
                └→ Rejected (PM rejected)
```

### Feature Lifecycle (GitHub Issue labels)

```
stage:discover → stage:define → stage:plan → stage:build → stage:deliver → stage:document
```

---

## End-to-End Example

### Step 1: Discover

```bash
/aod.discover "Add dark mode support for the dashboard"
```

- GitHub Issue **#21** created with `type:idea` and `stage:discover` labels
- ICE Score: 24 (I:9 C:9 E:6) — P1 (High)
- Evidence: "Customer feedback — 12 requests in last quarter"
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
- New ideas from retrospective → new GitHub Issues with `stage:discover`

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

## Summary

| Stage | Command | Output | Governance |
|-------|---------|--------|-----------|
| 1. Discover | `/aod.discover` | Scored idea + evidence | PM validation (tier-dependent) |
| 2. Define | `/aod.define` | PRD | Triad PRD review |
| 3. Plan | `/aod.plan` (3 sub-steps) | spec + plan + tasks | PM, PM+Arch, Triple sign-off |
| 4. Build | `/aod.build` | Implementation | Architect checkpoints |
| 5. Deliver | `/aod.deliver` | Closed feature + retro | DoD check |
| 6. Document | `/aod.document` | Simplified code + docs | Human approval per step |
