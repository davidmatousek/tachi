---
description: Generate tasks with triple sign-off (PM + Architect + Team-Lead) - Streamlined v2
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

Generate an actionable, dependency-ordered tasks.md with automatic Triad triple sign-off governance.

**Flow**: Validate plan → Generate tasks → Triple review (parallel) → Handle blockers → Inject frontmatter → Generate assignments

## Step 1: Validate Prerequisites

1. Get branch: `git branch --show-current` → must match `NNN-*` pattern
2. Find plan: `specs/{NNN}-*/plan.md` → must exist
3. Parse frontmatter: Verify `triad.pm_signoff.status` and `triad.architect_signoff.status` are APPROVED (or APPROVED_WITH_CONCERNS/BLOCKED_OVERRIDDEN)
4. If validation fails: Show error with required workflow order and exit

## Step 2: Generate Tasks

**If `revision_mode == true`** (re-invocation after governance rejection):
1. Read the existing tasks at `specs/{NNN}-*/tasks.md` (do not start from scratch)
2. Read `revision_feedback` from `.aod/revision-context.md`
3. Apply targeted changes to address the specific issues raised by the reviewer
4. Preserve sections the reviewer did not flag — only regenerate flagged sections
5. Skip prerequisite loading (already in context) — jump directly to updating the flagged sections
6. Proceed directly to Step 3 (Triple Sign-off) after updating the tasks

### 2a. Setup

1. Run `.aod/scripts/bash/check-prerequisites.sh --json` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

### 2b. Load Design Documents

Read from FEATURE_DIR:
- **Required**: plan.md (tech stack, libraries, structure), spec.md (user stories with priorities)
- **Optional**: data-model.md (entities), contracts/ (API endpoints), research.md (decisions), quickstart.md (test scenarios)
- Note: Not all projects have all documents. Generate tasks based on what's available.

### 2c. Execute Task Generation Workflow

1. Load plan.md and extract tech stack, libraries, project structure
2. Load spec.md and extract user stories with their priorities (P1, P2, P3, etc.)
3. If data-model.md exists: Extract entities and map to user stories
4. If contracts/ exists: Map endpoints to user stories
5. If research.md exists: Extract decisions for setup tasks
6. Generate tasks organized by user story (see Task Generation Rules below)
7. Generate dependency graph showing user story completion order
8. Create parallel execution examples per user story
9. Validate task completeness (each user story has all needed tasks, independently testable)

### 2d. Generate tasks.md

Use `.aod/templates/tasks-template.md` as structure, fill with:
- Correct feature name from plan.md
- Phase 1: Setup tasks (project initialization)
- Phase 2: Foundational tasks (blocking prerequisites for all user stories)
- Phase 3+: One phase per user story (in priority order from spec.md)
- Each phase includes: story goal, independent test criteria, tests (if requested), implementation tasks
- Final Phase: Polish & cross-cutting concerns
- All tasks must follow the strict checklist format (see Task Generation Rules below)
- Clear file paths for each task
- Dependencies section showing story completion order
- Parallel execution examples per story
- Implementation strategy section (MVP first, incremental delivery)

### 2e. Verify Output

1. Verify `tasks.md` was created at `specs/{NNN}-*/tasks.md`
2. If not created: Error and exit
3. Output summary: total task count, task count per user story, parallel opportunities, independent test criteria, suggested MVP scope
4. Format validation: Confirm ALL tasks follow the checklist format (checkbox, ID, labels, file paths)

The tasks.md should be immediately executable - each task must be specific enough that an LLM can complete it without additional context.

Context for task generation: $ARGUMENTS

## Task Generation Rules

**CRITICAL**: Tasks MUST be organized by user story to enable independent implementation and testing.

**Tests are OPTIONAL**: Only generate test tasks if explicitly requested in the feature specification or if user requests TDD approach.

### Checklist Format (REQUIRED)

Every task MUST strictly follow this format:

```text
- [ ] [TaskID] [P?] [Story?] Description with file path
```

**Format Components**:

1. **Checkbox**: ALWAYS start with `- [ ]` (markdown checkbox)
2. **Task ID**: Sequential number (T001, T002, T003...) in execution order
3. **[P] marker**: Include ONLY if task is parallelizable (different files, no dependencies on incomplete tasks)
4. **[Story] label**: REQUIRED for user story phase tasks only
   - Format: [US1], [US2], [US3], etc. (maps to user stories from spec.md)
   - Setup phase: NO story label
   - Foundational phase: NO story label
   - User Story phases: MUST have story label
   - Polish phase: NO story label
5. **Description**: Clear action with exact file path

**Examples**:

- CORRECT: `- [ ] T001 Create project structure per implementation plan`
- CORRECT: `- [ ] T005 [P] Implement authentication middleware in src/middleware/auth.py`
- CORRECT: `- [ ] T012 [P] [US1] Create User model in src/models/user.py`
- CORRECT: `- [ ] T014 [US1] Implement UserService in src/services/user_service.py`
- WRONG: `- [ ] Create User model` (missing ID and Story label)
- WRONG: `T001 [US1] Create model` (missing checkbox)
- WRONG: `- [ ] [US1] Create User model` (missing Task ID)
- WRONG: `- [ ] T001 [US1] Create model` (missing file path)

### Task Organization

1. **From User Stories (spec.md)** - PRIMARY ORGANIZATION:
   - Each user story (P1, P2, P3...) gets its own phase
   - Map all related components to their story:
     - Models needed for that story
     - Services needed for that story
     - Endpoints/UI needed for that story
     - If tests requested: Tests specific to that story
   - Mark story dependencies (most stories should be independent)

2. **From Contracts**:
   - Map each contract/endpoint to the user story it serves
   - If tests requested: Each contract gets a contract test task [P] before implementation in that story's phase

3. **From Data Model**:
   - Map each entity to the user story(ies) that need it
   - If entity serves multiple stories: Put in earliest story or Setup phase
   - Relationships map to service layer tasks in appropriate story phase

4. **From Setup/Infrastructure**:
   - Shared infrastructure goes in Setup phase (Phase 1)
   - Foundational/blocking tasks go in Foundational phase (Phase 2)
   - Story-specific setup goes within that story's phase

### Phase Structure

- **Phase 1**: Setup (project initialization)
- **Phase 2**: Foundational (blocking prerequisites - MUST complete before user stories)
- **Phase 3+**: User Stories in priority order (P1, P2, P3...)
  - Within each story: Tests (if requested) → Models → Services → Endpoints → Integration
  - Each phase should be a complete, independently testable increment
- **Final Phase**: Polish & Cross-Cutting Concerns

## Step 3: Triple Sign-off (Parallel)

Launch **three Task agents in parallel** (single message, three Task tool calls):

| Agent | subagent_type | Focus | Key Criteria |
|-------|---------------|-------|--------------|
| PM | product-manager | Product scope | User stories covered, no scope creep, FRs addressed |
| Architect | architect | Technical | Dependencies ordered, parallel opportunities, patterns maintained |
| Team-Lead | team-lead | Timeline | Granularity appropriate, critical path identified, parallelization maximized |

**Prompt template for each** (customize focus area):
```
Review tasks.md at {tasks_path} for {FOCUS AREA}.

Read the file, then provide sign-off:

STATUS: [APPROVED | APPROVED_WITH_CONCERNS | CHANGES_REQUESTED | BLOCKED]
NOTES: [Your detailed feedback]
```

**Parse responses**: Extract STATUS and NOTES from each agent's output.

## Step 4: Handle Review Results

**All APPROVED/APPROVED_WITH_CONCERNS**: Proceed to Step 5

**Any CHANGES_REQUESTED**:
1. Display feedback from reviewers who requested changes
2. Use architect agent to update tasks addressing the feedback
3. Re-run reviews only for reviewers who requested changes
4. Loop until all approved or user aborts

**Any BLOCKED**:
1. Display blocker with veto domain (PM=scope, Architect=technical, Team-Lead=timeline)
2. **If `autonomous == true`**: **HALT** — save state and stop. Display: `"BLOCKED in autonomous mode — halting. Manual intervention required."`. Do NOT auto-override BLOCKED status.
3. Use AskUserQuestion with options:
   - **Resolve**: Address issues and re-submit to blocked reviewer
   - **Override**: Provide justification, mark as BLOCKED_OVERRIDDEN
   - **Abort**: Cancel task generation

**Multiple BLOCKED (cross-domain conflict)**:
1. Display all blockers with their domains
2. **If `autonomous == true`**: **HALT** — same as single BLOCKED above.
3. Use AskUserQuestion for executive decision:
   - **Product priority**: Override non-PM blocks
   - **Technical priority**: Override non-Architect blocks
   - **Schedule priority**: Override non-Team-Lead blocks
   - **Revise all**: Return to planning phase
   - **Abort**: Cancel

## Step 5: Inject Frontmatter

Add YAML frontmatter to tasks.md (prepend to existing content):

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
  techlead_signoff:
    agent: team-lead
    date: {YYYY-MM-DD}
    status: {techlead_status}
    notes: "{techlead_notes}"
---
```

## Step 6: Generate Agent Assignments

Invoke team-lead agent to create `agent-assignments.md`.

**REQUIRED**: Team-lead MUST read `.claude/agents/_README.md` before assigning tasks and use ONLY exact agent names from the Agent Registry. Do NOT invent generic labels like `file-agent`, `doc-agent`, or `qa-agent` — these are not valid subagent types.

**Agent Roster** (valid `subagent_type` values for the Agent tool):

| Agent name | Use for |
|---|---|
| `senior-backend-engineer` | Backend code, APIs, config files, SKILL.md authoring, markdown file creation/editing |
| `frontend-developer` | UI components, client-side code |
| `tester` | Validation scenarios, acceptance testing, QA |
| `security-analyst` | Security reviews, vulnerability assessment |
| `devops` | Deployment, CI/CD, infrastructure |
| `code-reviewer` | Code quality review |
| `web-researcher` | External research, documentation lookup |
| `debugger` | Bug investigation, root cause analysis |
| `architect` | System design, architecture decisions |
| `product-manager` | Product requirements, scope decisions |
| `ux-ui-designer` | UI/UX design, wireframes |
| `orchestrator` | Multi-agent coordination, wave execution |

**Common fallback mappings** (when no specialist fits):
- Markdown/documentation writing → `senior-backend-engineer`
- File creation or editing (non-code) → `senior-backend-engineer`
- Validation/acceptance scenario execution → `tester`
- Research and external docs → `web-researcher`

**Output includes**:
- Agent Assignment Matrix (task to agent mapping using exact names above)
- Parallel Execution Waves (grouped by dependencies)
- Quality Gates between waves
- Time estimates per wave

Save to `specs/{NNN}-*/agent-assignments.md`

## Step 7: Report Completion

**Re-ground before output**: Re-read the template below exactly. The `Next:` line must always be a copyable command the user can paste directly — `/aod.build {feature_number}`.

Display summary:
```
TASK BREAKDOWN COMPLETE

Feature: {feature_number} - {feature_name}
Tasks: {tasks_path}
Assignments: {assignments_path}

Triple Sign-offs:
- PM: {pm_status}
- Architect: {architect_status}
- Team-Lead: {techlead_status}

Next: /aod.build {feature_number}
```

## Quality Checklist

- [ ] Plan has dual sign-offs (PM + Architect)
- [ ] tasks.md generated with full task generation workflow
- [ ] Triple review executed in parallel
- [ ] Blockers handled (resolved, overridden, or aborted)
- [ ] Frontmatter injected with all three sign-offs
- [ ] agent-assignments.md generated
- [ ] Completion summary displayed

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I'll run `/aod.tasks` before the architect signs off the plan" | Step 1 ("Validate Prerequisites") requires `triad.architect_signoff.status` ∈ {APPROVED, APPROVED_WITH_CONCERNS, BLOCKED_OVERRIDDEN} (line 39). Without architect sign-off, Step 1 errors and exits. |
| "Team-Lead BLOCKED on timeline grounds — I'll override since I think we can hit it" | Step 4 binds Team-Lead to timeline (line 206). In `autonomous == true`, Step 4 HALTS (line 207). Compress scope or timeline. |
| "I'll let team-lead invent agent names like `file-agent` for clarity" | Step 6 (line 252) requires exact names from the 12-agent Agent Roster. Invented names break `/aod.build`'s `subagent_type` lookup; the wave never runs. |
| "I'll edit Step 7's `Next:` line to `/aod.deliver` since the user knows what to run" | Step 7 Re-ground rule (line 287) binds `Next:` to `/aod.build {feature_number}`. The build orchestrator depends on this resume contract. |

## Red Flags

- Agent invokes `/aod.tasks` while `plan.md` has only PM sign-off (architect_signoff null or CHANGES_REQUESTED).
- Agent's `agent-assignments.md` uses agent names not in the Step 6 Agent Roster (e.g., `file-agent`, `doc-agent`, `qa-agent`).
- Agent's Step 7 completion summary shows `Next: /aod.deliver` or any non-`/aod.build` command.
- Agent runs the three Triad reviews sequentially (three messages with one Task each) instead of one message with three parallel Task calls per Step 3.
- Agent overrides a Multiple-BLOCKED cross-domain conflict while `autonomous == true` instead of halting per Step 4 line 215.
- Agent regenerates `tasks.md` from scratch after CHANGES_REQUESTED instead of running `/aod.tasks --revision` (Step 0y).
