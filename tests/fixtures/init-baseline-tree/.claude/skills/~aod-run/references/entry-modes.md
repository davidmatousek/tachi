# Entry Modes Reference (v030)
<!-- Loaded via Read tool — do not inline into core SKILL.md -->

This reference contains all entry mode handlers for the AOD lifecycle orchestrator: New Idea, Issue, Resume, and Status modes, plus their sub-sections (Artifact Discovery, State File Detection, GitHub Graceful Degradation, Artifact Consistency Validation, Stale State Detection, GitHub Label Validation, Status Fallback).

## New Idea Entry

When mode is `idea`, the orchestrator creates a fresh orchestration from a raw idea description.

**Algorithm**:

1. **Check for existing state file**: Use Bash to run `bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_exists && echo "exists" || echo "none"'`
   - If state file exists: Display warning: `"A state file already exists for a previous orchestration. Use --resume to continue it, or delete .aod/run-state.json to start fresh."` Then STOP (do not overwrite).

2. **Read governance tier**: Read `.aod/memory/constitution.md`, extract `governance:` → `tier:` value. Default to `standard` if not found.

3. **Generate feature metadata**:
   - `feature_name`: Convert idea text to kebab-case (lowercase, spaces to hyphens, strip non-alphanumeric except hyphens, truncate to 50 chars)
   - `feature_id`: Will be assigned after Discover stage creates a GitHub Issue (set to `"000"` initially)
   - `branch`: Will be set after Discover stage determines the branch name (set to `"pending"` initially)
   - `github_issue`: null initially (assigned by Discover stage)
   - `idea`: The full idea text as provided by the user

4. **Create initial state JSON**: Build the state object following Entity 1 schema:

```json
{
  "version": "1.0",
  "feature_id": "000",
  "feature_name": "{kebab-case-idea}",
  "github_issue": null,
  "idea": "{full idea text}",
  "branch": "pending",
  "started_at": "{current ISO 8601 timestamp}",
  "updated_at": "{current ISO 8601 timestamp}",
  "governance_tier": "{tier from constitution}",
  "current_stage": "discover",
  "current_substage": null,
  "session_count": 1,
  "intervention_count": 0,
  "stages": {
    "discover": { "status": "pending", "started_at": null, "completed_at": null, "artifacts": [], "governance": null, "substages": null, "error": null },
    "define": { "status": "pending", "started_at": null, "completed_at": null, "artifacts": [], "governance": null, "substages": null, "error": null },
    "plan": { "status": "pending", "started_at": null, "completed_at": null, "artifacts": [], "governance": null, "substages": { "spec": { "status": "pending", "artifacts": [] }, "project_plan": { "status": "pending", "artifacts": [] }, "tasks": { "status": "pending", "artifacts": [] } }, "error": null },
    "build": { "status": "pending", "started_at": null, "completed_at": null, "artifacts": [], "governance": null, "substages": null, "error": null },
    "deliver": { "status": "pending", "started_at": null, "completed_at": null, "artifacts": [], "governance": null, "substages": null, "error": null },
    "document": { "status": "pending", "started_at": null, "completed_at": null, "artifacts": [], "governance": null, "substages": null, "error": null }
  },
  "session_strategy": null,
  "estimated_sessions": null,
  "build_progress": null,
  "autonomous_decisions": [],
  "error_log": [],
  "gate_rejections": []
}
```

5. **Write state to disk**: Use Bash to create the state file via `bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_create '"'"'{json}'"'"''` (using the constructed JSON).

6. **Display initial status**:
```
AOD ORCHESTRATOR — New Lifecycle
================================
Idea: {idea text}
Governance Tier: {tier}
Starting Stage: Discover

Stage Map:
  [>] Discover  [ ] Define  [ ] Plan  [ ] Build  [ ] Deliver  [ ] Document
```

7. **Proceed to Core Loop**: Fall through to Step 2 (Core State Machine Loop) to begin executing the Discover stage.

## Issue Entry

When mode is `issue`, the orchestrator reads an existing GitHub Issue to determine the current lifecycle stage and creates (or loads) state accordingly.

**Algorithm**:

1. **Parse issue number**: Extract the numeric issue number from the input (strip `#` prefix if present).

2. **Check for existing state file**: Use Bash to run `bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_exists && echo "exists" || echo "none"'`
   - If state file exists: Check if it matches this issue number (see [State File Detection for Existing Features](#state-file-detection-for-existing-features))
   - If state file does not exist: Continue to step 3

3. **Read GitHub Issue**: Use Bash to fetch issue data:
   ```
   gh issue view {NNN} --json number,title,labels
   ```
   - Extract `number`, `title`, and `labels` array
   - If `gh` is unavailable or fails: fall back to [GitHub Graceful Degradation](#github-graceful-degradation)

4. **Extract stage label**: Search the labels array for a label matching `stage:*`:
   - `stage:discover` → current stage is `define` (see note below)
   - `stage:define` → current stage is `define`
   - `stage:plan` → current stage is `plan`
   - `stage:build` → current stage is `build`
   - `stage:deliver` → current stage is `deliver`
   - `stage:done` → lifecycle already complete (display summary and exit)
   - No `stage:*` label found → default to `define` (see note below)

   **IMPORTANT**: When entering via Issue Entry (`/aod.run #NNN`), the Discover stage is **always complete by definition**. The output of Discover IS the GitHub Issue itself. If the issue exists, discover already happened. Therefore:
   - The minimum starting stage for Issue Entry is `define`
   - `stage:discover` label on an existing issue means "discover just completed" → start from `define`
   - No label on an existing issue → assume discover completed → start from `define`

5. **Infer completed stages**: Based on the detected stage label, mark all prior stages as `completed`:

   | Detected Label | Completed Stages | Starting Stage |
   |---------------|-----------------|----------------|
   | `stage:discover` | discover | define |
   | `stage:define` | discover | define |
   | `stage:plan` | discover, define | plan |
   | `stage:build` | discover, define, plan | build |
   | `stage:deliver` | discover, define, plan, build | deliver |
   | `stage:document` | discover, define, plan, build, deliver | document |
   | `stage:done` | all | (lifecycle complete) |
   | (no label) | discover | define |

6. **Discover existing artifacts**: Scan disk for artifacts from completed stages (see [Artifact Discovery](#artifact-discovery)).

7. **Read governance tier**: Read `.aod/memory/constitution.md`, extract `governance:` → `tier:` value. Default to `standard` if not found.

8. **Generate feature metadata**:
   - `feature_id`: Zero-pad the issue number to 3 digits (e.g., `42` → `"042"`)
   - `feature_name`: Convert issue title to kebab-case (lowercase, spaces to hyphens, strip non-alphanumeric except hyphens, truncate to 50 chars)
   - `branch`: `{feature_id}-{feature_name}` (e.g., `"042-add-dark-mode-toggle"`)
   - `github_issue`: The issue number
   - `idea`: The issue title

9. **Create initial state JSON**: Build the state object following Entity 1 schema, with completed stages pre-filled:

```json
{
  "version": "1.0",
  "feature_id": "{NNN}",
  "feature_name": "{kebab-case-title}",
  "github_issue": {issue_number},
  "idea": "{issue title}",
  "branch": "{feature_id}-{feature_name}",
  "started_at": "{current ISO 8601 timestamp}",
  "updated_at": "{current ISO 8601 timestamp}",
  "governance_tier": "{tier}",
  "current_stage": "{detected starting stage}",
  "current_substage": null,
  "session_count": 1,
  "intervention_count": 0,
  "stages": {
    "discover": { "status": "{completed or pending}", "started_at": null, "completed_at": "{if completed: now, else: null}", "artifacts": ["{discovered artifacts}"], "governance": null, "substages": null, "error": null },
    "define": { "status": "{completed or pending}", ... },
    "plan": { "status": "{completed or pending}", ..., "substages": { "spec": {...}, "project_plan": {...}, "tasks": {...} } },
    "build": { "status": "pending", ... },
    "deliver": { "status": "pending", ... },
    "document": { "status": "pending", "started_at": null, "completed_at": null, "artifacts": [], "governance": null, "substages": null, "error": null }
  },
  "session_strategy": null,
  "estimated_sessions": null,
  "build_progress": null,
  "autonomous_decisions": [],
  "error_log": [],
  "gate_rejections": []
}
```

   For completed stages: set `status: "completed"`, populate `artifacts` from disk scan, set timestamps to current time (exact original times are not available).

   For the Plan stage when it's marked completed: also mark all 3 substages (`spec`, `project_plan`, `tasks`) as `completed` with their discovered artifacts.

10. **Write state to disk**: Use Bash to create the state file via `bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_create '"'"'{json}'"'"''`

11. **Ensure correct branch**: Check current git branch. If not on the expected feature branch, switch to it:
    - If branch exists: `git checkout {branch}`
    - If branch does not exist: `git checkout -b {branch}`

12. **Display initial status**:
```
AOD ORCHESTRATOR — Resume from Issue #{NNN}
=============================================
Feature: {feature_name} (#{github_issue})
Branch: {branch}
Governance Tier: {tier}
Detected Stage: {stage label}
Starting Stage: {starting_stage}

Completed: {list of completed stage names}
Artifacts Found: {count}

Stage Map:
  {markers per stage}
```

13. **Proceed to Core Loop**: Fall through to Step 2 (Core State Machine Loop) to begin executing the starting stage.

## Artifact Discovery

When resuming from a GitHub Issue, the orchestrator scans the disk for existing artifacts to populate the state file. This ensures context from prior stages is available to subsequent stages.

**Scan algorithm**:

1. **Determine feature ID**: Zero-pad the issue number to 3 digits (e.g., `42` → `"042"`).

2. **Scan for each artifact type**:

   | Artifact | Glob Pattern | Stage |
   |----------|-------------|-------|
   | PRD | `docs/product/02_PRD/{NNN}-*.md` | define |
   | Spec | `specs/{NNN}-*/spec.md` | plan (spec substage) |
   | Plan | `specs/{NNN}-*/plan.md` | plan (project_plan substage) |
   | Tasks | `specs/{NNN}-*/tasks.md` | plan (tasks substage) |
   | Agent Assignments | `specs/{NNN}-*/agent-assignments.md` | plan (tasks substage) |
   | Research | `specs/{NNN}-*/research.md` | plan (pre-spec research) |

3. **Use Glob tool** for each pattern. Record found paths in the corresponding stage's `artifacts` array.

4. **Cross-validate**: If a stage is inferred as completed (from the GitHub label) but its expected artifact is not found on disk, log a warning:
   ```
   WARNING: Stage {stage} inferred as complete from GitHub label, but artifact not found: {expected pattern}
   ```
   Still mark the stage as completed (trust the GitHub label as authoritative), but note the missing artifact.

5. **Plan substage inference**: If Plan stage is marked completed, check which Plan artifacts exist:
   - spec.md found → mark `spec` substage as completed
   - plan.md found → mark `project_plan` substage as completed
   - tasks.md found → mark `tasks` substage as completed
   - If some Plan substage artifacts are missing but the overall Plan stage label says complete, warn but trust the label.

## State File Detection for Existing Features

When an issue number is provided and a state file already exists, the orchestrator checks whether the existing state file belongs to this feature.

**Algorithm**:

1. **Read existing state file**: Use Bash to run `bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_get .github_issue'`

2. **Compare issue numbers**:
   - If the state file's `github_issue` matches the provided issue number: offer to resume from the state file instead of re-inferring from GitHub label
     - Use AskUserQuestion: "A state file already exists for Issue #{NNN}. Resume from state file (recommended) or re-infer from GitHub Issue label?"
     - Options: "Resume from state file" (recommended), "Re-infer from GitHub"
     - If user chooses resume: switch to `--resume` flow (see [Resume Entry](#resume-entry))
     - If user chooses re-infer: delete existing state file, continue with issue entry flow from step 3
   - If the state file's `github_issue` does NOT match: warn about conflict
     - Use AskUserQuestion: "A state file exists for a different feature (Issue #{existing}). What would you like to do?"
     - Options: "Switch to Issue #{NNN} (archive current state)", "Cancel"
     - If switch: archive current state to `specs/{existing_NNN}-*/run-state.json`, then continue with issue entry
     - If cancel: exit

## GitHub Graceful Degradation

When the `gh` CLI is unavailable or fails, the orchestrator falls back to artifact-only detection.

**Degradation levels**:

| Level | Condition | Detection Method | Behavior |
|-------|-----------|-----------------|----------|
| 1 | `gh` not installed | `command -v gh` fails | Fall back to artifact-only scan |
| 2 | `gh` not authenticated | `gh auth status` fails | Fall back to artifact-only scan |
| 3 | Issue not found | `gh issue view` returns error | Warn user, offer to create issue or proceed without |

**Artifact-only fallback** (Levels 1 and 2):

1. Display warning: `"GitHub CLI unavailable. Falling back to artifact-only detection."`
2. Skip the `gh issue view` call
3. Use the provided issue number to construct the feature ID (zero-pad to 3 digits)
4. Scan disk for artifacts using the [Artifact Discovery](#artifact-discovery) algorithm
5. Infer the current stage from the highest-level artifact found:
   - tasks.md found → infer `build` (Plan complete)
   - plan.md found → infer `plan` (project_plan substage complete, check for tasks)
   - spec.md found → infer `plan` (spec substage complete, check for plan)
   - PRD found → infer `plan` (Define complete, start at Plan:spec)
   - No artifacts → infer `define` (issue exists = discover complete, start from Define)
6. Ask user to confirm the inferred stage: "Based on artifacts found, the current stage appears to be {stage}. Is this correct?"
   - Options: "Yes, continue from {stage}", "No, let me specify"
   - If user specifies: accept their input as the starting stage

**Level 3 fallback** (Issue not found):

1. Display warning: `"GitHub Issue #{NNN} not found."`
2. Use AskUserQuestion: "Issue #{NNN} was not found on GitHub. What would you like to do?"
   - Options: "Scan artifacts and proceed without issue", "Cancel"
   - If proceed: use artifact-only fallback (same as Level 1/2)
   - If cancel: exit

## Resume Entry

When mode is `resume`, the orchestrator reads the persisted state file from disk, validates it, and continues from the last completed stage boundary.

**Algorithm**:

1. **Check for state file**: Use Bash to run `bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_exists && echo "exists" || echo "none"'`
   - If state file does NOT exist: Display error and guidance:
     ```
     ERROR: No orchestration state file found at .aod/run-state.json

     To start a new orchestration:
       /aod.run "your feature idea"
       /aod.run #NNN  (from existing GitHub Issue)

     A state file is created automatically when you start orchestration.
     ```
     Then STOP (exit without proceeding).

2. **Read and validate state file**: Use Bash to run `bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_validate'`
   - If validation fails (non-zero exit): the state file is corrupt or has an unrecognized schema. Route to Corrupted State File Handling (see `references/error-recovery.md`) — archive the corrupt file and offer recovery options.

3. **Read full state**: Use Bash to run `bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_read'`. Parse the JSON to extract:
   - `feature_id`, `feature_name`, `github_issue`, `branch`
   - `current_stage`, `current_substage`
   - `session_count`
   - `started_at`, `updated_at`
   - All stage statuses from `stages` map

4. **Increment session count**: Calculate `new_session_count = session_count + 1`. Update state:
   ```
   bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_set ".session_count" "{new_session_count}"'
   ```

5. **Validate schema version**: Check that `version` is `"1.0"`. If not recognized, warn but attempt to continue (forward-compatible).

6. **Check lifecycle-already-complete**: Check if all 6 stages show `status: "completed"` (see `references/error-recovery.md` for Lifecycle Already Complete Detection). If complete, display summary and STOP — do NOT proceed to the Core Loop or restart any stages.

7. **Run artifact consistency validation**: For each stage marked as `completed` in the state, verify its recorded artifacts exist on disk (see [Artifact Consistency Validation](#artifact-consistency-validation)).

8. **Run stale state detection**: Check if the state file is stale (see [Stale State Detection](#stale-state-detection)). If stale, ask user confirmation before proceeding.

9. **Run GitHub label validation**: If `gh` is available, verify the GitHub Issue's `stage:*` label matches `current_stage` in the state file (see [GitHub Label Validation on Resume](#github-label-validation-on-resume)).

10. **Re-read governance tier**: Read `.aod/memory/constitution.md`, extract `governance:` → `tier:` value. Default to `standard` if not found. Update state if tier has changed:
    ```
    bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_set ".governance_tier" "{tier}"'
    ```
    If tier changed from previous value, display: `"Note: Governance tier changed from {old} to {new}. New tier applied going forward."`

11. **Ensure correct branch**: Check current git branch. If not on the expected feature branch:
    - If branch exists: `git checkout {branch}`
    - If branch does not exist: warn user: `"Expected branch {branch} not found. Currently on {current_branch}."`
    - Use AskUserQuestion: "Feature branch {branch} not found. Continue on current branch or create it?"
      - Options: "Continue on {current_branch}", "Create {branch}"

12. **Display resume status**:

```
AOD ORCHESTRATOR — Resuming
============================
Feature: {feature_name} (#{github_issue})
Branch: {branch}
Session: {new_session_count} (previous: {old_session_count})
Governance Tier: {tier}
Current Stage: {current_stage}{substage_detail}
Last Updated: {updated_at}

Completed Stages: {list of completed stage names}
Pending Stages: {list of pending stage names}

Stage Map:
  {markers per stage}
```

   **Resume-after-break enhancement**: If `current_stage` is `build` and `build_progress` exists in state (indicating a prior session break), display additional build progress context:

   ```
   Build Progress: Wave {completed_waves}/{total_waves} ({session_breaks count} prior session break(s))
   Resuming from Wave {completed_waves + 1}...
   ```

   When `autonomous_mode == true` in the state file, skip any confirmation prompts and auto-continue directly to the Core Loop. The brief status summary above is sufficient — no user interaction needed.

13. **Proceed to Core Loop**: Fall through to Step 2 (Core State Machine Loop). The current stage from the state file determines where execution resumes.

   - If a stage is `in_progress`, re-execute it from its beginning (idempotent restart). If a stage is `completed`, advance to the next pending stage.
   - **Build resume-after-break**: When Build is `in_progress`, `aod.build --orchestrated --autonomous` is re-invoked. Build's existing Step 1.6 detects completed waves via `[X]` markers in tasks.md and continues from the next incomplete wave. Post-Build verification (see SKILL.md "After Build completes") then checks task completion:
     - If still incomplete → another session break (recursive until done)
     - If all complete → advance to Deliver

## Artifact Consistency Validation

When resuming, verify that artifacts recorded in the state file for completed stages actually exist on disk. This catches cases where artifacts were manually deleted or moved between sessions.

**Algorithm** (called by Resume Entry step 7):

1. **Iterate completed stages**: For each stage in the `stages` map where `status == "completed"`:

2. **Check recorded artifacts**: Read the `artifacts` array for that stage. For each artifact path in the array:
   - Use Glob to check if the file exists at that path
   - If the path contains a wildcard (e.g., `specs/022-*/spec.md`), use Glob to resolve it
   - Record whether each artifact was found or missing

3. **Check Plan substage artifacts**: If the Plan stage is completed, also check each substage (`spec`, `project_plan`, `tasks`) and their `artifacts` arrays using the same logic.

4. **Build inconsistency report**: Collect all missing artifacts into a list:

   ```
   Artifact Consistency Check:
     [OK] specs/022-full-lifecycle-orchestrator/spec.md
     [OK] specs/022-full-lifecycle-orchestrator/plan.md
     [MISSING] specs/022-full-lifecycle-orchestrator/tasks.md
   ```

5. **Handle results**:

   - **All artifacts found**: Display `"Artifact consistency check: PASSED ({count} artifacts verified)"` and continue.

   - **Some artifacts missing**: Display the inconsistency report and use AskUserQuestion:
     - Question: "Some artifacts for completed stages are missing from disk. How would you like to proceed?"
     - Options:
       - "Accept current state (skip missing artifacts)" — Continue with resume, trusting the state file. Missing artifacts may cause issues in subsequent stages.
       - "Re-run affected stages" — For each stage with missing artifacts, reset its status to `"pending"` in the state file. The orchestrator will re-execute those stages.
     - If user chooses to accept: log a warning in state `error_log` and continue
     - If user chooses to re-run: update state for affected stages, write atomically, then continue to Core Loop (which will re-execute from the earliest incomplete stage)

6. **Write any state changes**: If stages were reset, write the updated state atomically via `run-state.sh`.

## Stale State Detection

Detect when the state file has not been updated for more than 7 days. This catches situations where a developer started an orchestration, left it for a while, and is now resuming with potentially outdated context.

**Algorithm** (called by Resume Entry step 8):

1. **Check staleness**: Use Bash to run `bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_is_stale && echo "STALE" || echo "FRESH"'`
   - The `aod_state_is_stale` function compares `updated_at` against current time with a 7-day (604800 second) threshold
   - Exit code 0 = stale, exit code 1 = fresh, exit code 2 = error (no timestamp)

2. **Handle results**:

   - **FRESH**: No action needed. Continue with resume flow.

   - **STALE**: Read the `updated_at` timestamp from state. Calculate the age in days. Display a staleness warning:
     ```
     WARNING: Orchestration state is {N} days old (last updated: {updated_at}).

     This may indicate:
       - The feature was paused and context has changed
       - Artifacts may have been modified outside the orchestrator
       - GitHub Issue labels may be out of sync

     Current stage: {current_stage}
     Feature: {feature_name} (#{github_issue})
     ```

     Use AskUserQuestion:
     - Question: "The orchestration state is {N} days old. Do you want to continue from where you left off?"
     - Options:
       - "Yes, resume from {current_stage}" — Continue with resume flow as normal
       - "No, start fresh" — Archive the current state file to `specs/{NNN}-*/run-state.json`, delete `.aod/run-state.json`, and display guidance for starting a new orchestration. Then STOP.

   - **ERROR**: Display `"WARNING: Could not determine state file age (missing updated_at timestamp). Proceeding with caution."` Continue with resume flow.

3. **No state modification**: This check is read-only. It does not modify the state file. The session count increment has already been written by the Resume Entry step 4.

## GitHub Label Validation on Resume

When resuming with a GitHub Issue number in state, verify that the issue's `stage:*` label matches the `current_stage` recorded in the state file. This catches cases where someone manually moved the issue label or another process updated it.

**Algorithm** (called by Resume Entry step 8):

1. **Check prerequisites**:
   - Read `github_issue` from state. If null, skip this check entirely (no GitHub Issue to validate against).
   - Check if `gh` CLI is available: `command -v gh >/dev/null 2>&1`. If not available, skip with message: `"GitHub CLI unavailable. Skipping label validation."` and continue.
   - Check if `gh` is authenticated: `gh auth status >/dev/null 2>&1`. If not authenticated, skip with message: `"GitHub CLI not authenticated. Skipping label validation."` and continue.

2. **Read GitHub Issue label**: Use Bash to fetch the issue's labels:
   ```
   gh issue view {github_issue} --json labels --jq '.labels[].name' 2>/dev/null
   ```
   - Search the output for a line matching `stage:*`
   - Extract the stage name (e.g., `stage:build` → `build`)
   - If no `stage:*` label found: skip validation with message: `"No stage label found on Issue #{github_issue}. Skipping label validation."`

3. **Compare with state file**: Compare the GitHub label's stage with `current_stage` from the state file.

4. **Handle results**:

   - **Match**: Display `"GitHub label validation: PASSED (Issue #{github_issue} label matches state: stage:{current_stage})"` and continue.

   - **Mismatch**: Display the discrepancy:
     ```
     WARNING: GitHub Issue label does not match orchestration state.

       State file: current_stage = {current_stage}
       GitHub Issue #{github_issue}: label = stage:{github_label_stage}

     This may indicate:
       - Someone manually updated the issue label
       - Another process advanced the lifecycle
       - The state file is from a different session
     ```

     Use AskUserQuestion:
     - Question: "The state file says '{current_stage}' but GitHub says 'stage:{github_label_stage}'. Which source of truth should we use?"
     - Options:
       - "Use state file ({current_stage})" — Trust the local state file. Update the GitHub label to match: `bash -c 'source .aod/scripts/bash/github-lifecycle.sh && aod_gh_update_stage {github_issue} {current_stage}'`
       - "Use GitHub label ({github_label_stage})" — Trust GitHub. Update the state file: reset stages as needed (mark stages before the GitHub label as completed, reset the current and later stages). This is similar to the Issue Entry flow's stage inference logic. Write updated state atomically.

   - **Error reading GitHub**: If `gh issue view` fails for any reason, skip with message: `"Could not read Issue #{github_issue}. Skipping label validation."` and continue.

5. **Write any state changes**: If the user chose to trust GitHub, write the updated state atomically via `run-state.sh`. If a GitHub label was updated, the `github-lifecycle.sh` function handles that.

## Status Entry

When mode is `status`, the orchestrator displays the current orchestration state in read-only mode, then exits. It MUST NOT modify the state file or any artifacts.

**Algorithm**:

1. **Parse optional issue number**: Check if an issue number was provided along with `--status` (e.g., `--status #NNN`). If yes, store it as `status_issue_number`.

2. **Check for state file**: Use Bash to run `bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_exists && echo "exists" || echo "none"'`

   - If state file exists: proceed to step 3 (display from state file)
   - If state file does NOT exist AND `status_issue_number` is set: proceed to [Status Fallback (No State File)](#status-fallback-no-state-file)
   - If state file does NOT exist AND no issue number: display message and exit:
     ```
     No active orchestration found.

     To check status of a specific issue:
       /aod.run --status #NNN

     To start a new orchestration:
       /aod.run "your feature idea"
       /aod.run #NNN
     ```
     Then STOP (exit without proceeding).

3. **Read state file** (read-only): Use Bash to run `bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_read'`. Parse the JSON to extract all fields.

4. **Build stage map**: For each stage, determine its display marker using the same logic as Stage Map Display (in core SKILL.md):
   - `completed` → `[x]`, `in_progress` → `[>]`, `pending` → `[ ]`, `failed` → `[!]`
   - For Plan stage: append substage in parentheses if in progress

5. **Determine next action**: Based on `current_stage` and its status:
   - If `in_progress`: "Continue {stage_name}" (or "Continue Plan: {substage}" for Plan)
   - If `completed` and next stage exists: "Start {next_stage_name}"
   - If all completed: "Lifecycle complete (6/6)"
   - If `failed`: "Retry {stage_name} (resolve blocker first)"

6. **Display status report**:

```
AOD ORCHESTRATOR — Status
==========================
Feature: {feature_name} (#{github_issue})
Branch: {branch}
Governance Tier: {governance_tier}
Session Count: {session_count}
Last Updated: {updated_at}

Stage Map:
  {stage markers}

Current Stage: {current_stage}{substage_detail}
Status: {current_stage_status}
Next Action: {next_action}

Completed: {list of completed stage names, or "none"}
Pending: {list of pending stage names, or "none"}

Governance Gates:
  {for each stage with governance: stage — reviewer: status}

Rejections: {gate_rejections count} total ({intervention_count} interventions)
```

7. **Exit**: STOP immediately after display. Do NOT modify state, invoke any skills, or enter the Core Loop.

## Status Fallback (No State File)

When `--status` is invoked with an issue number but no state file exists, infer status from GitHub Issue labels and on-disk artifacts.

**Algorithm**:

1. **Check GitHub CLI availability**: Run `command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1`
   - If `gh` is available and authenticated: proceed to step 2
   - If `gh` is unavailable or not authenticated:
     - Display: `"GitHub CLI unavailable. Falling back to artifact-only detection."`
     - Skip to step 3 (artifact-only scan)

2. **Read GitHub Issue**: Use Bash to fetch issue data:
   ```
   gh issue view {NNN} --json number,title,labels
   ```
   - Extract `number`, `title`, and `labels` array
   - Search labels for `stage:*` to determine current stage
   - If issue not found: display `"Issue #{NNN} not found on GitHub."` and STOP

3. **Scan on-disk artifacts**: Use the same Artifact Discovery logic (zero-pad issue number, scan for PRD/spec/plan/tasks using Glob).

4. **Infer stage from artifacts** (if GitHub label not available):
   - tasks.md found → infer `build` (Plan complete)
   - plan.md found → infer `plan` (project_plan substage)
   - spec.md found → infer `plan` (spec substage)
   - PRD found → infer `plan` (Define complete)
   - No artifacts → infer `define` (issue exists = discover complete)

5. **Display inferred status**:

```
AOD ORCHESTRATOR — Inferred Status (no state file)
====================================================
Issue: #{NNN} — {title or "unknown"}
Detected Stage: {stage from label or artifact inference}
Source: {GitHub label | artifact scan}

Artifacts Found:
  {list of found artifact paths, or "none"}

Note: No state file exists for this feature.
      This status is inferred from {source}. To start orchestration:
        /aod.run #{NNN}
```

6. **Exit**: STOP immediately. Do NOT create a state file or modify anything.
