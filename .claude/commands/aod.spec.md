---
description: Create feature specification with automatic PM sign-off - Streamlined v2
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

Creates a feature specification with automatic PM sign-off (Constitution Principle VIII: Product-Spec Alignment). Generates spec.md inline with research grounding and governance review.

**Flow**: Validate PRD → **Research** → Generate spec (inline) → PM review → Handle blockers → Inject frontmatter

## Step 1: Validate Prerequisites

1. Get branch: `git branch --show-current` → must match `NNN-*` pattern
2. Find PRD: `docs/product/02_PRD/{NNN}-*.md` → must exist
3. Parse frontmatter: Verify all Triad sign-offs are APPROVED (or APPROVED_WITH_CONCERNS/BLOCKED_OVERRIDDEN)
4. If validation fails: Show error with required workflow order and exit
5. **GitHub Lifecycle Update (early)**: Move the feature's GitHub Issue to `stage:plan` at the *start* of specification work. The issue number is the NNN prefix extracted from the branch in step 1 (e.g., branch `086-my-feature` → issue `86`). Run:
   ```bash
   bash -c 'source .aod/scripts/bash/github-lifecycle.sh && aod_gh_update_stage NNN plan'
   ```
   Then regenerate BACKLOG.md:
   ```bash
   bash .aod/scripts/bash/backlog-regenerate.sh
   ```
   If `gh` is unavailable or the issue does not exist, skip silently (graceful degradation).

## Step 2: Research Phase

Before generating the specification, conduct research to ground the spec in reality. Run these **in parallel** using Task agents:

| Research Area | Agent/Tool | What to Find | Output |
|---------------|------------|--------------|--------|
| Knowledge Base | kb-query skill | Similar patterns, lessons learned, past bug fixes | Relevant KB entries |
| Codebase | Explore agent | Existing implementations, naming conventions, utilities | Similar features, patterns |
| Architecture | Read tool | Relevant architecture docs, constraints, dependencies | Technical constraints |
| Web Research | WebSearch tool | Industry best practices, existing solutions, common patterns | External references |

**Parallel Execution**: Launch all four research tasks simultaneously to minimize time.

**Research Prompt Template** (for Explore agent):
```
Research the codebase for the feature: {prd_title}

Find:
1. Similar features already implemented (patterns to follow)
2. Relevant utilities, helpers, or shared components
3. Naming conventions used for similar functionality
4. Any existing code that this feature might extend or integrate with

PRD context: {prd_path}
```

**Web Research Queries** (derive from PRD):
- "{feature_type} best practices {year}"
- "{feature_type} implementation patterns"
- "common {feature_type} user experience patterns"

**Output**: Create `specs/{NNN}-*/research.md` with findings:

```markdown
# Research Summary: {feature_name}

## Knowledge Base Findings
- [List relevant KB entries with links]
- Key lessons: ...

## Codebase Analysis
- Similar features: [list with file paths]
- Patterns to follow: ...
- Utilities to reuse: ...

## Architecture Constraints
- Relevant docs: [list with links]
- Key constraints: ...
- Dependencies: ...

## Industry Research
- Best practices: ...
- Common patterns: ...
- References: [links]

## Recommendations for Spec
- [Bullet points of what to include/avoid based on research]
```

**Pass research.md to Step 3** for use as context during spec generation.

## Step 3: Generate Specification (Inline)

**If `revision_mode == true`** (re-invocation after governance rejection):
1. Read the existing spec at `specs/{NNN}-*/spec.md` (do not start from scratch)
2. Read `revision_feedback` from `.aod/revision-context.md`
3. Apply targeted changes to address the specific issues raised by the reviewer
4. Preserve sections the reviewer did not flag — only regenerate flagged sections
5. Skip research phase (Step 2) — research from the original run is still valid
6. Proceed directly to Step 3.4 (Quality Validation) after updating the spec

The text the user typed after the command **is** the feature description. Do not ask the user to repeat it unless they provided an empty command.

### 3.1 Setup

1. **Check for Approved PRD** (PRD → Spec Traceability):
   - Search `docs/product/02_PRD/` for a PRD matching the feature description
   - Look for status "Approved" or "In Progress" in the PRD registry (INDEX.md)
   - If found, extract the PRD number (e.g., `006` from `006-phase-production-launch`)
   - **Use `--number N` flag** with the PRD number:
     ```bash
     .aod/scripts/bash/create-new-feature.sh --json --number N "$ARGUMENTS"
     ```
   - If no PRD found, warn user:
     ```
     ⚠️ Warning: No approved PRD found for this feature.
     Per Constitution v1.4.0: "No spec.md without an approved PRD"
     Recommended: Create PRD first with /aod.define <topic>
     Continue without PRD? (y/n)
     ```

2. Run the script `.aod/scripts/bash/create-new-feature.sh --json [--number N] "$ARGUMENTS"` from repo root and parse its JSON output for BRANCH_NAME and SPEC_FILE. All file paths must be absolute.
   **IMPORTANT** You must only ever run this script once. The JSON is provided in the terminal as output - always refer to it to get the actual content you're looking for. For single quotes in args, use: `"I'm Groot"`.

3. Load `.aod/templates/spec-template.md` to understand required sections.

### 3.2 Execution Flow

1. Parse user description from Input
   If empty: ERROR "No feature description provided"
2. Extract key concepts from description
   Identify: actors, actions, data, constraints
3. For unclear aspects:
   - Make informed guesses based on context, industry standards, and research.md findings
   - Only mark with [NEEDS CLARIFICATION: specific question] if:
     - The choice significantly impacts feature scope or user experience
     - Multiple reasonable interpretations exist with different implications
     - No reasonable default exists
   - **LIMIT: Maximum 3 [NEEDS CLARIFICATION] markers total**
   - Prioritize clarifications by impact: scope > security/privacy > user experience > technical details
4. Fill User Scenarios & Testing section
   If no clear user flow: ERROR "Cannot determine user scenarios"
5. Generate Functional Requirements
   Each requirement must be testable
   Use reasonable defaults for unspecified details (document assumptions in Assumptions section)
6. Define Success Criteria
   Create measurable, technology-agnostic outcomes
   Include both quantitative metrics and qualitative measures
   Each criterion must be verifiable without implementation details
7. Identify Key Entities (if data involved)
8. Return: SUCCESS (spec ready for review)

### 3.3 Write Specification

Write the specification to SPEC_FILE using the template structure, replacing placeholders with concrete details derived from the feature description (arguments) while preserving section order and headings.

### 3.4 Quality Validation

After writing the initial spec, validate against quality criteria:

a. **Create Spec Quality Checklist**: Generate a checklist file at `FEATURE_DIR/checklists/requirements.md`:

   ```markdown
   # Specification Quality Checklist: [FEATURE NAME]

   **Purpose**: Validate specification completeness and quality
   **Created**: [DATE]
   **Feature**: [Link to spec.md]

   ## Content Quality
   - [ ] No implementation details (languages, frameworks, APIs)
   - [ ] Focused on user value and business needs
   - [ ] Written for non-technical stakeholders
   - [ ] All mandatory sections completed

   ## Requirement Completeness
   - [ ] No [NEEDS CLARIFICATION] markers remain
   - [ ] Requirements are testable and unambiguous
   - [ ] Success criteria are measurable
   - [ ] Success criteria are technology-agnostic
   - [ ] All acceptance scenarios are defined
   - [ ] Edge cases are identified
   - [ ] Scope is clearly bounded
   - [ ] Dependencies and assumptions identified

   ## Feature Readiness
   - [ ] All functional requirements have clear acceptance criteria
   - [ ] User scenarios cover primary flows
   - [ ] Feature meets measurable outcomes defined in Success Criteria
   - [ ] No implementation details leak into specification

   ## Notes
   - Items marked incomplete require spec updates before `/aod.clarify` or `/aod.project-plan`
   ```

b. **Run Validation Check**: Review the spec against each checklist item

c. **Handle Validation Results**:
   - **If all items pass**: Mark checklist complete and proceed
   - **If items fail**: List failing items, update spec, re-validate (max 3 iterations)
   - **If [NEEDS CLARIFICATION] markers remain**:
     - **If `autonomous == true`**: Auto-resolve all markers with best inference from PRD context. Display: `"Auto-resolved: {count} NEEDS CLARIFICATION markers from PRD context (autonomous mode)"`. Do not prompt.
     - Else: Present up to 3 clarification questions in table format, wait for user response, update spec

d. **Update Checklist** with current pass/fail status

### 3.5 Verify and Report

1. Verify `spec.md` was created at `specs/{NNN}-*/spec.md`
2. If not created: Error and exit

**Guidelines**:
- Focus on **WHAT** users need and **WHY**
- Avoid HOW to implement (no tech stack, APIs, code structure)
- Written for business stakeholders, not developers
- DO NOT create any checklists embedded in the spec
- Make informed guesses using context and industry standards
- Document assumptions in the Assumptions section
- Think like a tester: every requirement should be testable and unambiguous

**NOTE:** The script creates and checks out the new branch and initializes the spec file before writing.

## Step 4: PM Sign-off

Launch **one Task agent** for PM review:

| Agent | subagent_type | Focus | Key Criteria |
|-------|---------------|-------|--------------|
| PM | product-manager | Product alignment | PRD requirements covered, user stories, success criteria, no scope creep |

**Prompt template**:
```
Review spec.md at {spec_path} against PRD at {prd_path}.

Evaluate:
- Alignment with PRD requirements and scope
- Completeness (all PRD requirements addressed)
- User story coverage
- Success criteria clarity

Provide sign-off:
STATUS: [APPROVED | APPROVED_WITH_CONCERNS | CHANGES_REQUESTED | BLOCKED]
NOTES: [Your detailed feedback]
```

**Parse response**: Extract STATUS and NOTES from agent output.

## Step 5: Handle Review Results

**APPROVED/APPROVED_WITH_CONCERNS**: → Proceed to Step 6

**CHANGES_REQUESTED**:
1. Display PM feedback
2. Notify: "Update spec.md and re-run /aod.spec"
3. Still inject frontmatter with CHANGES_REQUESTED status

**BLOCKED**:
1. Display blocker with veto domain (PM=product scope)
2. **If `autonomous == true`**: **HALT** — save state and stop. Display: `"BLOCKED in autonomous mode — halting. Manual intervention required."`. Do NOT auto-override BLOCKED status.
3. Use AskUserQuestion with options:
   - **Resolve**: Address issues and re-run /aod.spec
   - **Override**: Provide justification (min 20 chars), mark as BLOCKED_OVERRIDDEN
   - **Abort**: Exit workflow

## Step 6: Inject Frontmatter

Add YAML frontmatter to spec.md (prepend to existing content):

```yaml
---
prd_reference: {prd_path}
triad:
  pm_signoff:
    agent: product-manager
    date: {YYYY-MM-DD}
    status: {pm_status}
    notes: "{pm_notes}"
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---
```

## Step 7: Report Completion

**Re-ground before output**: Re-read the template below exactly. Do not paraphrase or substitute reviewer recommendations for the `Next:` line — it must always be `/aod.plan SPEC: {feature_number} - {feature_name}`.

Display summary:
```
SPECIFICATION CREATION COMPLETE

Feature: {feature_number}
PRD: {prd_path}
Spec: {spec_path}

PM Sign-off: {pm_status}

Next: /aod.plan SPEC: {feature_number} - {feature_name}
```

## Quality Checklist

- [ ] Branch matches NNN-* pattern
- [ ] PRD exists with approved Triad sign-offs
- [ ] Research phase completed (KB, codebase, architecture, web)
- [ ] research.md created with findings
- [ ] spec.md created with inline generation (informed by research)
- [ ] Spec quality validation passed
- [ ] PM review completed
- [ ] Blockers handled (resolved, overridden, or aborted)
- [ ] Frontmatter injected with PM sign-off
- [ ] Completion summary displayed

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I already know what to build, the spec is just paperwork" | The spec is the artifact PM signs off on. Without it, the gate has nothing to gate. |
| "I'll fill in the [NEEDS CLARIFICATION] markers later" | Markers fail validation at /aod.spec Step 3.4 Quality Validation (.claude/commands/aod.spec.md:177); spec is not ready if any remain. Resolve now or run /aod.clarify. |
| "I'll skip Step 2 research — I know enough about this feature already" | Step 2 grounds the spec in current code (Explore agent), KB lessons, architecture, and external research. Skipping risks invented gates and pattern drift. |
| "I'll regenerate `spec.md` from scratch after CHANGES_REQUESTED instead of using `--revision`" | Step 0y `--revision` applies targeted edits to flagged sections only and reuses prior research. Regenerating discards PM feedback context and reruns Step 2. |

## Red Flags

- Agent accepts a spec with more than 3 `[NEEDS CLARIFICATION]` markers (Step 3.2 line 159 caps at 3).
- Agent runs the four Step 2 research areas sequentially instead of one message with four parallel Task calls (line 62: "Launch all four research tasks simultaneously").
- Agent's Step 7 completion summary shows `Next: /aod.project-plan` (or any other command) instead of `Next: /aod.plan SPEC: {feature_number} - {feature_name}` (line 305 / 317).
- Agent regenerates `spec.md` from scratch after CHANGES_REQUESTED instead of running `/aod.spec --revision`.
- Agent overrides a BLOCKED PM verdict while `autonomous == true` instead of halting per Step 5 line 279.
- Agent skips the Step 1 GitHub Issue stage update (lines 41-49) when `gh` CLI is available.
