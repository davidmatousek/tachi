# Context Loading

<!-- Rule file for tachi -->
<!-- This file is referenced from CLAUDE.md using @-syntax -->

## Overview

Load governance context by domain using the guides below. This ensures agents have the right context for each task type.

---

## Session Start

Read these first when starting a new session:
```bash
cat docs/AOD_TRIAD.md                          # SDLC Triad quick reference
cat .aod/memory/constitution.md               # Governance principles
```

---

## By Domain

Load context based on the task type:

| Domain | Read This | When Needed |
|--------|-----------|-------------|
| **Triad Workflow** | `docs/standards/TRIAD_COLLABORATION.md` | Creating specs, plans, tasks |
| **Product/PRDs** | `docs/product/02_PRD/INDEX.md` | PRD work, product decisions |
| **Architecture** | `docs/architecture/README.md` | Technical design, system decisions |
| **DevOps/Deploy** | `docs/devops/README.md` | Any deployment task |
| **Agents/Skills** | `.claude/README.md` | Using agents or skills |
| **Standards** | `docs/standards/DEFINITION_OF_DONE.md` | DoD, naming, git workflow |
| **Thinking Lenses** | `docs/core_principles/README.md` | 5 Whys, Pre-Mortem, etc. |
| **KB/Memory** | `docs/INSTITUTIONAL_KNOWLEDGE.md` | Project history, lessons learned |

---

## Feature Context

Load current feature context when working on active features:
```bash
cat .aod/spec.md      # Requirements
cat .aod/plan.md      # Technical design
cat .aod/tasks.md     # Work items
```
