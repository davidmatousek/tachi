# Governance

<!-- Rule file for tachi -->
<!-- This file is referenced from CLAUDE.md using @-syntax -->

## Overview

This file defines mandatory governance workflows for tachi. All agents must follow these sign-off requirements when creating specs, plans, and tasks.

**CRITICAL**: After creating specs/plans/tasks, you MUST auto-trigger reviews. Do not wait for user request.

---

## Sign-off Requirements

| Artifact | Required Sign-offs | Agents to Invoke |
|----------|-------------------|------------------|
| spec.md | PM | product-manager |
| plan.md | PM + Architect | product-manager, architect |
| tasks.md | PM + Architect + Team-Lead | product-manager, architect, team-lead |

### Before `/aod.spec` (Research Phase):

A **mandatory research phase** runs before spec generation:

1. **Knowledge Base**: Query for similar patterns, lessons learned, past bug fixes
2. **Codebase**: Explore existing implementations, naming conventions, reusable utilities
3. **Architecture**: Read relevant architecture docs, constraints, dependencies
4. **Web Research**: Search for industry best practices, common patterns, existing solutions

**Output**: `specs/{NNN}-*/research.md` summarizing findings to inform spec creation.

**Purpose**: Ground specifications in codebase reality and industry best practices, avoiding reinvention and ensuring alignment with existing patterns.

### After `/aod.spec` Completes:
1. **Automatically** invoke product-manager agent for PM review using Task tool
2. Present review results (APPROVED or CHANGES REQUESTED)
3. If CHANGES REQUESTED: Address issues, re-submit for review
4. Do NOT declare "ready for planning" until PM sign-off: APPROVED

### After `/aod.project-plan` Completes:
1. Invoke product-manager for PM review
2. Invoke architect for technical review
3. Require **both approvals** before declaring ready

**Parallel Review (Claude Code v2.1.16+)**: If context forking is available, PM and Architect reviews run simultaneously in isolated contexts. Use a single message with two Task calls for parallel execution.

### After `/aod.tasks` Completes:
1. Invoke product-manager, architect, and team-lead
2. Team-lead generates `agent-assignments.md` with parallel execution waves
3. Require **all three approvals** before implementation

**Triple Parallel Review (v2.1.16+)**: All three reviews can run in parallel with context forking. Results merge automatically using severity ranking.

### Review Outcomes:
- **APPROVED**: Proceed to next phase, document sign-off
- **CHANGES REQUESTED**: Address issues, re-submit (repeat until approved)
- **BLOCKED**: Critical issues, escalate to user

### Thinking Lenses During Review (Optional Escalation)

Reviewers may apply structured thinking lenses when encountering complexity, risk, or ambiguity. This is **optional** - standard reviews use role-specific checklists. Escalate to a lens when deeper analysis is warranted.

| Reviewer | Recommended Lens | When to Apply |
|----------|------------------|---------------|
| PM | Pre-Mortem | Requirements seem risky or unclear |
| PM | First Principles | Inherited assumptions need challenging |
| Architect | Pre-Mortem | Technical risks could derail implementation |
| Architect | Systems Thinking | Complex component interactions need mapping |
| Team-Lead | Constraint Analysis | Hidden dependencies or blockers suspected |
| Team-Lead | Systems Thinking | Task dependencies need validation |

**How to Apply**: Reference `docs/core_principles/README.md` for lens selection and methodology details. Document lens findings in review comments when used.

---

## Triad Roles

The SDLC Triad ensures Product-Architecture-Engineering alignment:
- **product-manager (PM)**: Defines **What** & **Why** (user value, business goals)
- **architect**: Defines **How** (technical approach, infrastructure baseline)
- **team-lead**: Defines **When** & **Who** (timeline, agent assignments)

### Infrastructure PRD Workflow (sequential):
1. PM analyzes need → architect provides baseline → PM drafts PRD
2. Tech-lead feasibility → architect review → PM finalizes

### Feature PRD Workflow (parallel):
1. PM drafts PRD → architect + tech-lead review in parallel → PM finalizes
