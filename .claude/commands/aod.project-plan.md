---
description: Create implementation plan with dual sign-off (PM + Architect) - Streamlined v2
---

## User Input

```text
$ARGUMENTS
```

Consider user input before proceeding (if not empty).

## Step 0: Parse --autonomous

1. If `$ARGUMENTS` contains `--autonomous`:
   - Set `autonomous = true`
   - Strip `--autonomous` from `$ARGUMENTS` (trim extra whitespace)
2. Default: `autonomous = false`

## Step 0y: Parse --revision

1. If `$ARGUMENTS` contains `--revision`:
   - Set `revision_mode = true`
   - Strip `--revision` from `$ARGUMENTS` (trim extra whitespace)
   - Read `.aod/revision-context.md` for reviewer feedback (contains reviewer name, attempt number, artifact path, and full feedback text)
   - Store feedback as `revision_feedback`
2. Default: `revision_mode = false`

## Overview

Self-contained implementation planning command with automatic PM + Architect dual sign-off.

**Flow**: Validate spec → Setup & load context → Generate plan (phases 0-1) → Dual review (parallel) → Handle blockers → Inject frontmatter

## Step 1: Validate Prerequisites

1. Get branch: `git branch --show-current` → must match `NNN-*` pattern
2. Find spec: `specs/{NNN}-*/spec.md` → must exist
3. Parse frontmatter: Verify `triad.pm_signoff.status` is APPROVED (or APPROVED_WITH_CONCERNS/BLOCKED_OVERRIDDEN)
4. If validation fails: Show error with required workflow order and exit

## Step 2: Generate Plan

**If `revision_mode == true`** (re-invocation after governance rejection):
1. Read the existing plan at `specs/{NNN}-*/plan.md` (do not start from scratch)
2. Read `revision_feedback` from `.aod/revision-context.md`
3. Apply targeted changes to address the specific issues raised by the reviewer
4. Preserve sections the reviewer did not flag — only regenerate flagged sections
5. Skip Phase 0 research (already completed) — jump directly to updating the flagged sections
6. Proceed directly to Step 3 (Dual Sign-off) after updating the plan

### 2a: Setup

1. Run `.aod/scripts/bash/setup-plan.sh --json` from repo root and parse JSON for FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

### 2b: Load Context

1. Read FEATURE_SPEC and `.aod/memory/constitution.md`
2. Load IMPL_PLAN template (already copied by setup script)

### 2c: Execute Plan Workflow

Follow the structure in IMPL_PLAN template to:
- Fill Technical Context (mark unknowns as "NEEDS CLARIFICATION")
- Fill Constitution Check section from constitution
- Evaluate gates (ERROR if violations unjustified)
- Phase 0: Generate research.md (resolve all NEEDS CLARIFICATION)
- Phase 1: Generate data-model.md, contracts/, quickstart.md
- Phase 1: Update agent context by running the agent script
- Re-evaluate Constitution Check post-design

### Phase 0: Outline & Research

1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

### Phase 1: Design & Contracts

**Prerequisites:** `research.md` complete

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Agent context update**:
   - Run `.aod/scripts/bash/update-agent-context.sh claude`
   - These scripts detect which AI agent is in use
   - Update the appropriate agent-specific context file
   - Add only new technology from current plan
   - Preserve manual additions between markers

**Output**: data-model.md, /contracts/*, quickstart.md, agent-specific file

### 2d: Verify Plan Created

1. Verify `plan.md` was created at `specs/{NNN}-*/plan.md`
2. If not created: Error and exit

## Step 3: Dual Sign-off (Parallel)

Launch **two Task agents in parallel** (single message, two Task tool calls):

| Agent | subagent_type | Focus | Key Criteria |
|-------|---------------|-------|--------------|
| PM | product-manager | Product alignment | Spec requirements covered, user stories, acceptance criteria, no scope creep |
| Architect | architect | Technical | Architecture sound, technology appropriate, security addressed, scalable |

**Prompt template for each** (customize focus area):
```
Review plan.md at {plan_path} for {FOCUS AREA}.

Read the file, then provide sign-off:

STATUS: [APPROVED | APPROVED_WITH_CONCERNS | CHANGES_REQUESTED | BLOCKED]
NOTES: [Your detailed feedback]
```

**Parse responses**: Extract STATUS and NOTES from each agent's output.

## Step 4: Handle Review Results

**All APPROVED/APPROVED_WITH_CONCERNS**: → Proceed to Step 5

**Any CHANGES_REQUESTED**:
1. Display feedback from reviewers who requested changes
2. Use architect agent to update plan addressing the feedback
3. Re-run reviews only for reviewers who requested changes
4. Loop until all approved or user aborts

**Any BLOCKED**:
1. Display blocker with veto domain (PM=product scope, Architect=technical)
2. **If `autonomous == true`**: **HALT** — save state and stop. Display: `"BLOCKED in autonomous mode — halting. Manual intervention required."`. Do NOT auto-override BLOCKED status.
3. Use AskUserQuestion with options:
   - **Resolve**: Address issues and re-submit to blocked reviewer
   - **Override**: Provide justification (min 20 chars), mark as BLOCKED_OVERRIDDEN
   - **Abort**: Cancel plan creation

## Step 5: Inject Frontmatter

Add YAML frontmatter to plan.md (prepend to existing content):

```yaml
---
triad:
  pm_signoff:
    agent: product-manager
    date: {YYYY-MM-DD}
    status: {pm_status}
    notes: "{pm_notes}"
  architect_signoff:
    agent: architect
    date: {YYYY-MM-DD}
    status: {architect_status}
    notes: "{architect_notes}"
  techlead_signoff: null  # Added by /aod.tasks
---
```

## Step 6: System Design Generation

After frontmatter injection, auto-scaffold system design documentation from the approved plan.

1. Read the just-approved `plan.md` at `specs/{NNN}-*/plan.md`
2. Search for canonical section headings: `## Components`, `## Data Flow`, `## Tech Stack`
3. **If at least one canonical section is found**:
   a. Extract the content of each found section (including any Mermaid diagram blocks — preserve verbatim)
   b. If `docs/architecture/01_system_design/` directory does not exist, create it
   c. If `docs/architecture/01_system_design/README.md` already exists, read its current content
   d. Append extracted content under a feature-specific heading: `### Feature {NNN}: {feature-name}`
   e. If the feature heading already exists in the file, skip to prevent duplication
   f. Write/update `docs/architecture/01_system_design/README.md`
   g. Display: "System design generated: docs/architecture/01_system_design/README.md"
4. **If no canonical sections are found** (none of `## Components`, `## Data Flow`, `## Tech Stack` exist):
   - Display: "System design generation skipped: no canonical sections found in plan.md"
   - Skip gracefully — this step is non-blocking

**Non-blocking**: Failure in this step does not prevent plan completion. If any error occurs during file I/O, log the error and continue.

## Step 7: GitHub Lifecycle Update

After plan creation, regenerate BACKLOG.md to reflect current state:

1. Run `.aod/scripts/bash/backlog-regenerate.sh` to refresh BACKLOG.md
2. If `gh` is unavailable, skip silently (graceful degradation)

## Step 8: Report Completion

Display summary including branch, IMPL_PLAN path, and generated artifacts:
```
IMPLEMENTATION PLAN COMPLETE

Feature: {feature_number}
Spec: {spec_path}
Plan: {plan_path}
Artifacts: research.md, data-model.md, contracts/, quickstart.md
System Design: {generated | skipped}

Dual Sign-offs:
- PM: {pm_status}
- Architect: {architect_status}

Next: /aod.plan
```

**Important**: The `Next:` line MUST always be `/aod.plan` (no arguments). The router will re-evaluate artifact states and route to the correct next sub-step (typically `/aod.tasks`). Do not substitute reviewer recommendations or add arguments to this line.

## Key Rules

- Use absolute paths
- ERROR on gate failures or unresolved clarifications
- Command ends after Phase 1 planning and dual sign-off

## Quality Checklist

- [ ] Spec has approved PM sign-off
- [ ] plan.md created with full plan generation workflow
- [ ] Phase 0 research.md generated
- [ ] Phase 1 design artifacts generated
- [ ] Agent context updated
- [ ] Dual review executed in parallel
- [ ] Blockers handled (resolved, overridden, or aborted)
- [ ] Frontmatter injected with PM + Architect sign-offs
- [ ] Completion summary displayed

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I'll run `/aod.project-plan` before the spec's PM sign-off lands — save a step" | Step 1 ("Validate Prerequisites") parses spec frontmatter and requires `triad.pm_signoff.status` ∈ {APPROVED, APPROVED_WITH_CONCERNS, BLOCKED_OVERRIDDEN}. Without PM sign-off, Step 1 errors and exits. |
| "Architect BLOCKED the plan — I'll re-run with `--autonomous` to push past it" | Step 4 with `autonomous == true` HALTS (line 155) — does NOT auto-override. Override requires interactive justification ≥20 chars. Run interactively or address the veto. |
| "I'll regenerate the plan from scratch after CHANGES_REQUESTED instead of using `--revision`" | Step 0y `--revision` reads `.aod/revision-context.md` and applies targeted edits to flagged sections only. Regenerating discards reviewer feedback and reruns Phase 0. |
| "I'll edit the `Next:` line in Step 8 to point at `/aod.tasks`" | Step 8 (line 228) binds `Next:` to `/aod.plan`. The router re-evaluates artifact states and routes to the correct sub-step. Substituting breaks resume-from-rejection. |

## Red Flags

- Agent invokes `/aod.project-plan` while `spec.md` has no `triad.pm_signoff` frontmatter or status is null.
- Agent overrides a BLOCKED architect verdict while `autonomous == true` instead of halting per Step 4.
- Agent's Step 8 completion summary shows `Next: /aod.tasks` (or any other command) instead of `Next: /aod.plan`.
- Agent dispatches Phase 1 design (data-model.md, contracts/) while `research.md` still contains unresolved `NEEDS CLARIFICATION` markers.
- Agent runs PM and Architect reviews sequentially (two separate messages with one Task each) instead of one message with two parallel Task calls per Step 3.
- Agent regenerates `plan.md` from scratch after a CHANGES_REQUESTED stop without invoking `/aod.project-plan --revision`.
