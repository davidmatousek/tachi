# Error Recovery Reference (v030)
<!-- Loaded via Read tool — do not inline into core SKILL.md -->

This reference contains error and completion handlers for the AOD lifecycle orchestrator: corrupted state file handling, lifecycle complete detection, and lifecycle complete summary/archival.

## Corrupted State File Handling

When the state file fails validation (JSON parse error, missing required fields, or unrecognized schema version), the orchestrator archives the corrupt file and offers recovery options.

**Algorithm** (called by Resume Entry step 2 when `aod_state_validate` returns non-zero):

1. **Archive the corrupt file**: Generate a timestamped backup name and copy the corrupt file:
   ```
   bash -c 'cp .aod/run-state.json ".aod/run-state.json.corrupt.$(date +%Y%m%d%H%M%S)"'
   ```

2. **Display corruption details**:

   ```
   ERROR: Corrupted state file detected
   ======================================
   File: .aod/run-state.json
   Archive: .aod/run-state.json.corrupt.{timestamp}

   Validation errors:
     {error details from aod_state_validate stderr}

   The corrupted file has been archived for inspection.
   ```

3. **Attempt artifact-based recovery**: Scan disk for existing artifacts to determine what stage the feature was in:
   - Use the Artifact Discovery algorithm (see `references/entry-modes.md`) to find PRD, spec, plan, tasks
   - Infer the current lifecycle stage from found artifacts (same logic as GitHub Graceful Degradation Level 1/2 artifact inference in `references/entry-modes.md`)

4. **Offer recovery options**: Use AskUserQuestion:
   - Question: "State file is corrupted. How would you like to recover?"
   - Options:
     - "Start fresh from artifacts" — Create a new state file based on discovered artifacts (infer completed stages from what exists on disk). Delete the corrupt `.aod/run-state.json` and create a fresh one. Then proceed to the Core Loop from the inferred stage.
     - "Start completely fresh" — Delete the corrupt state file entirely. Display guidance: `"Run /aod.run 'idea' or /aod.run #NNN to begin a new orchestration."` Then STOP.

5. **Handle "Start fresh from artifacts"**:
   1. Determine feature ID from the current branch name (extract NNN from `NNN-feature-name` pattern)
   2. If branch doesn't match the pattern, ask user for the feature number
   3. Run Artifact Discovery with that feature ID
   4. Infer completed stages from found artifacts
   5. Build a new state file (same as Issue Entry step 9 logic in `references/entry-modes.md`) with discovered artifacts
   6. Read governance tier from constitution
   7. Write the new state file atomically
   8. Display: `"Recovery complete. New state created from {N} artifacts found on disk."`
   9. Proceed to the Core Loop

6. **Handle "Start completely fresh"**:
   1. Delete `.aod/run-state.json`
   2. Display guidance for starting a new orchestration
   3. STOP

## Lifecycle Already Complete Detection

Guard clause that prevents restarting an already-completed lifecycle. This is checked at:
- Resume Entry step 6 (before artifact validation and other resume checks)
- Core Loop step 2 (as part of the main loop)
- Issue Entry step 4 (when `stage:done` label is detected)

**Algorithm**:

1. **Read stage statuses**: Check the `status` field for all 6 stages (`discover`, `define`, `plan`, `build`, `deliver`, `document`) in the state file.

2. **Check if all completed**: If all 6 stages have `status: "completed"`:

   - Display the lifecycle completion summary (same as [Lifecycle Complete](#lifecycle-complete)), then STOP. Do NOT proceed to the Core Loop, restart any stages, or invoke any skills.

   ```
   AOD ORCHESTRATOR — Lifecycle Already Complete
   ===============================================
   Feature: {feature_name} (#{github_issue})
   Branch: {branch}

   All 6 lifecycle stages have already been completed.

   Stage Map:
     [x] Discover  [x] Define  [x] Plan  [x] Build  [x] Deliver  [x] Document

   To start a new feature:
     /aod.run "your new idea"
     /aod.run #NNN

   To view the delivery summary:
     /aod.run --status
   ```

   Then STOP immediately.

3. **If not all completed**: Continue with the normal flow (resume validation, core loop, etc.).

## Lifecycle Complete

When all 6 stages show `status: "completed"` (checked at Core Loop step 2), display the lifecycle completion summary and archive the state file.

**Algorithm**:

1. **Read final state**: Read `.aod/run-state.json` for all completion data.

2. **Calculate metrics**:
   - `session_count`: Read directly from state
   - `governance_gates_passed`: Count stages where `governance` object is non-null and contains at least one sign-off with APPROVED or APPROVED_WITH_CONCERNS status. Include Plan substages individually.
   - `total_governance_gates`: Count stages that had governance checks (based on tier rules)
   - `total_rejections`: Length of `gate_rejections` array
   - `intervention_count`: Read directly from state
   - `duration`: Calculate from `started_at` to `updated_at` (display as "X days" or "X hours")
   - `artifacts`: Collect all non-empty `artifacts` arrays from each stage and Plan substages

3. **Display completion summary**:

```
AOD ORCHESTRATOR — Lifecycle Complete
=====================================
Feature: {feature_name} (#{github_issue})
Branch: {branch}
Duration: {session_count} session(s), {duration}
Stages: 6/6 complete
Governance Gates: {governance_gates_passed}/{total_governance_gates} passed
Rejections: {total_rejections} total ({intervention_count} manual interventions)

Stage Map:
  [x] Discover  [x] Define  [x] Plan  [x] Build  [x] Deliver  [x] Document

Artifacts:
  - {artifact_path_1}
  - {artifact_path_2}
  - ...
```

4. **Archive state file**: Copy the state file to the specs directory for permanent record:
   ```
   bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_archive "specs/{NNN}-{feature_name}/run-state.json"'
   ```
   Where `{NNN}` is the `feature_id` and `{feature_name}` is from state.

5. **Do NOT delete the active state file**: Keep `.aod/run-state.json` in place so `--status` can still read it and the lifecycle-already-complete detection works on subsequent invocations.

6. **Exit**: The orchestrator's work is complete (6/6 stages). The user can review the archived state.
