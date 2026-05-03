# Governance Gate Reference (v047)
<!-- Loaded via Read tool — do not inline into core SKILL.md -->

This reference contains the complete governance flow for the AOD lifecycle orchestrator: gate detection, tier rules, rejection handling, retry tracking, circuit breaker, and blocked handling. Loading this single file provides everything needed for any governance path.

## Governance Gate Detection

After each stage skill returns, detect the governance gate result by reading the produced artifact's YAML frontmatter. The orchestrator does NOT re-implement governance — it reads the results that stage skills already produced.

**Detection algorithm**:

1. **Identify the artifact to check** based on the completed stage:

   | Stage | Artifact Path | Required Sign-offs |
   |-------|--------------|-------------------|
   | Discover | (no artifact — Discover approval is implicit in ICE score + PM validation) | None (approval is part of the discover flow) |
   | Define | `docs/product/02_PRD/{NNN}-*.md` | PM + Architect + Team-Lead (Triad review) |
   | Plan: spec | `specs/{NNN}-*/spec.md` | PM (`triad.pm_signoff.status`) |
   | Plan: project_plan | `specs/{NNN}-*/plan.md` | PM + Architect (`triad.pm_signoff.status`, `triad.architect_signoff.status`) |
   | Plan: tasks | `specs/{NNN}-*/tasks.md` | PM + Architect + Team-Lead (all three `triad.*.status` fields) |
   | Build | (no single artifact — Build approval via Architect checkpoints within `aod.build`) | None (checkpoints handled internally) |
   | Deliver | (no artifact — Deliver approval via DoD validation within `aod.deliver`) | None (DoD handled internally) |

2. **Check governance verdict cache BEFORE reading artifact** (FR-009 through FR-012):

   Before reading the artifact file, check if a cached verdict exists for each required reviewer:

   a. **For each required reviewer**, call the cache retrieval function:
      ```bash
      bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_get_governance_cache "{artifact_key}" "{reviewer}"'
      ```
      Where `{artifact_key}` is one of: `prd`, `spec`, `plan`, `tasks` (derived from artifact path).
      Where `{reviewer}` is one of: `pm`, `architect`, `techlead`.

   b. **Parse cache result**: The function returns `"status|timestamp|summary"` or `"null"` if not cached.
      - If result is `"null"`: Cache miss — proceed to step 3 (read artifact frontmatter)
      - If result contains a value: Cache hit — proceed to cache validation (step 2c)

   c. **Validate cache freshness via mtime check** (cache invalidation):
      Get the artifact file's modification timestamp:
      ```bash
      # macOS:
      stat -f %m "{artifact_path}"
      # Linux:
      stat -c %Y "{artifact_path}"
      ```
      Compare artifact mtime (Unix epoch) against cache timestamp (ISO 8601 → epoch conversion):
      - If artifact mtime > cache timestamp: Cache is stale — invalidate by proceeding to step 3
      - If artifact mtime ≤ cache timestamp: Cache is valid — use cached verdict (skip to step 4)

   d. **Use cached verdict**: If cache is valid, extract status from cached result (first pipe-delimited field).
      This avoids reading the full artifact frontmatter, saving 4-7K tokens per check.

3. **Read the artifact file** (only if cache miss or stale cache) using the Read tool. Extract the YAML frontmatter between `---` delimiters.

4. **Parse sign-off statuses**: For each required sign-off field, extract the `status` value from the `triad:` block.

5. **Evaluate gate result**:

   - **All required sign-offs are APPROVED or APPROVED_WITH_CONCERNS**: Gate PASSED
   - **Any sign-off is BLOCKED_OVERRIDDEN**: Gate PASSED (override was user-authorized)
   - **Any sign-off is CHANGES_REQUESTED**: Gate REJECTED — record which reviewer requested changes and their notes
   - **Any sign-off is BLOCKED**: Gate BLOCKED — record which reviewer blocked and their notes
   - **Sign-off field is null or missing**: Stage skill did not complete governance — treat as still in progress

6. **Record governance result and cache verdicts** (FR-009, FR-010):

   a. Update the stage's `governance` object with each reviewer's status and date.

   b. Add entries to `gate_rejections` array if rejected.

   c. **Cache each reviewer's verdict** for subsequent gate checks within the same stage:
      For each reviewer that completed their review (status is not null), call:
      ```bash
      bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_cache_governance "{artifact_key}" "{reviewer}" "{status}" "{summary}"'
      ```
      Where:
      - `{artifact_key}`: `prd`, `spec`, `plan`, or `tasks` (matches step 2a)
      - `{reviewer}`: `pm`, `architect`, or `techlead`
      - `{status}`: The sign-off status (APPROVED, CHANGES_REQUESTED, BLOCKED, etc.)
      - `{summary}`: Brief summary of reviewer notes (truncate to 100 chars if needed)

      **Example** (after reading spec.md frontmatter with PM approval):
      ```bash
      bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_cache_governance "spec" "pm" "APPROVED" "Spec meets all requirements"'
      ```

   This enables subsequent governance checks (e.g., when Plan stage verifies spec approval) to use the cache instead of re-reading artifact frontmatter, saving 4-7K tokens per check.

**Recognized approval statuses**: `APPROVED`, `APPROVED_WITH_CONCERNS`, `BLOCKED_OVERRIDDEN`
**Recognized rejection statuses**: `CHANGES_REQUESTED`
**Recognized blocker statuses**: `BLOCKED`

**Re-grounding** (context-thrifty): After governance reviews that produce significant variable-length output (>50 lines of reviewer feedback, rejection details, override justifications), re-read this file (`references/governance.md`) before continuing the loop to prevent template drift (per KB Entry 9). Skip re-grounding when output is minimal (cache hits, short approvals). With parallel Triad reviews, re-ground **once after all reviewers return** — agent isolation prevents cross-reviewer drift.

## Governance Tier

The orchestrator reads the governance tier from the project constitution to determine which gates are active. This follows the same pattern as `~aod-plan`.

**How to read the tier**:

1. Read `.aod/memory/constitution.md`
2. Look for the `## Governance Tiers` section, then find the YAML configuration block:
   ```yaml
   governance:
     tier: standard
   ```
3. Extract the `tier:` value. Valid values: `light`, `standard`, `full`
4. If the section is not found, the `governance:` key is missing, or the value is not recognized: **default to `standard`**

**Tier-specific gate rules**:

| Tier | Discover Gate | Define Gate | Plan: spec Gate | Plan: project_plan Gate | Plan: tasks Gate | Build Gate | Deliver Gate |
|------|---------------|-------------|-----------------|------------------------|-----------------|------------|--------------|
| **Light** | SKIP | SKIP | SKIP (PM sign-off not required) | Check dual sign-off | Check triple sign-off | Internal (aod.build) | Internal (aod.deliver) |
| **Standard** | Check (implicit in discover flow) | Check Triad review | Check PM sign-off | Check dual sign-off | Check triple sign-off | Internal (aod.build) | Internal (aod.deliver) |
| **Full** | Check | Check | Check PM sign-off (separate) | Check dual sign-off | Check triple sign-off | Internal (aod.build) | Internal (aod.deliver) |

**Gate skip behavior** (Light tier):
- When a gate is marked SKIP, the orchestrator marks the stage as completed without checking frontmatter sign-offs
- The stage skill is still invoked (stages are never skipped — only gates are)
- Display: `"Note: Light governance tier — {gate_name} gate skipped."`

**Governance floor (FR-026)**: Triple sign-off on `tasks.md` MUST be enforced regardless of tier. This is the non-negotiable governance floor. Even in Light tier, the orchestrator checks that `tasks.md` has PM + Architect + Team-Lead sign-offs before allowing Build to proceed.

**When to read the tier**:
- At orchestration startup (initial or resume)
- Store in state as `governance_tier`
- On resume, re-read from constitution (tier may have changed mid-orchestration — apply new tier going forward, do not re-evaluate already-completed gates)

**Mid-orchestration tier change handling**:

When the governance tier changes between sessions (detected at Resume Entry step 10), the orchestrator applies these rules:

1. **Read new tier**: Extract `tier:` from constitution on every resume
2. **Compare with stored tier**: Check `governance_tier` in state file against the newly-read value
3. **If changed**:
   - Update `governance_tier` in state to the new value
   - Display: `"Note: Governance tier changed from {old_tier} to {new_tier}. New tier applied going forward."`
   - **Do NOT re-evaluate already-completed gates**: Stages that already passed governance review keep their status. The new tier only affects gates for stages that have not yet been evaluated.
   - **Example**: If Discover and Define passed under `standard` tier, then the user switches to `light` tier mid-orchestration — Discover and Define keep their approval status. The Light tier's gate-skip rules only apply to pending stages (Plan:spec gate would now be skipped instead of requiring PM sign-off).
4. **Governance floor preserved**: The triple sign-off on `tasks.md` is always enforced regardless of tier change (FR-026). Changing from `standard` to `light` cannot bypass the tasks.md triple sign-off.

## Rejection Handling

When a governance gate returns CHANGES_REQUESTED, the orchestrator displays the rejection details and offers the user options to address or pause.

**Algorithm** (called by Core Loop step 10 when result is CHANGES_REQUESTED):

1. **Extract rejection details**: From the artifact's YAML frontmatter, identify which reviewer(s) returned CHANGES_REQUESTED. Collect:
   - `reviewer`: The reviewer agent name (e.g., `product-manager`, `architect`, `team-lead`)
   - `status`: `CHANGES_REQUESTED`
   - `notes`: The reviewer's feedback/required changes
   - `stage`: The current stage name
   - `substage`: The current substage (for Plan stages) or null

2. **Display rejection information**:

```
GOVERNANCE GATE — CHANGES REQUESTED
====================================
Stage: {stage}{substage_detail}
Reviewer: {reviewer}
Attempt: {attempt_number} of 3

Feedback:
  {reviewer notes/required changes}

The reviewer has requested changes before this stage can be approved.
```

3. **Offer options**:

   **If `autonomous_mode == true`**: Auto-select `"Address now"`. Display: `"Auto-selected: Address now (autonomous mode)"`. Skip to step 4 "Address now" handling. Do NOT prompt the user.

   Use AskUserQuestion to present choices:
   - Question: "How would you like to proceed?"
   - Options:
     - "Address now" — Continue in this session. The orchestrator will re-invoke the stage skill to address the changes, then re-submit for governance review.
     - "Pause orchestration" — Save current state (including the rejection) and exit gracefully. The user can resume later with `--resume`.

4. **Handle user choice**:

   - **"Address now"**:
     1. Increment `intervention_count` in state (user is manually intervening)
     2. **Clear governance cache** for the artifact being re-invoked: `bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_clear_governance_cache "{artifact}"'`. This ensures fresh reviews are required after changes.
     3. Write updated state atomically
     4. **Write revision context** to `.aod/revision-context.md` before re-invocation:
        ```markdown
        ---
        reviewer: {reviewer agent name}
        attempt: {attempt_number}
        artifact: {original artifact path}
        stage: {current stage}
        substage: {current substage or null}
        ---

        ## Reviewer Feedback

        {full text of reviewer notes/required changes}
        ```
     5. Re-invoke the stage skill via Skill tool with `--revision` flag appended to the original arguments (e.g., `skill="aod.spec", args="--revision --autonomous"`)
     6. After skill returns, re-check governance gate result (return to Core Loop step 9)
     7. If approved: continue with normal completion flow. Clean up `.aod/revision-context.md` (delete it).
     8. If rejected again: return to this Rejection Handling flow (loop) — the next iteration will overwrite `.aod/revision-context.md` with fresh feedback

   - **"Pause orchestration"**:
     1. Record the rejection in state (see [Retry Tracking](#retry-tracking))
     2. Write state with the current stage still `in_progress` and the rejection recorded
     3. Display pause message:
        ```
        Orchestration paused. State saved to .aod/run-state.json

        To resume later:
          /aod.run --resume

        The orchestrator will continue from the {stage} stage.
        ```
     4. STOP (exit without continuing the loop)

## Retry Tracking

Every governance gate rejection is recorded in the state's `gate_rejections` array for auditability and circuit breaker logic.

**Algorithm** (called whenever a governance gate returns CHANGES_REQUESTED or BLOCKED):

1. **Build rejection entry** following Entity 5 schema:

```json
{
  "timestamp": "{current ISO 8601 timestamp}",
  "stage": "{current_stage}",
  "substage": "{current_substage or null}",
  "reviewer": "{reviewer agent name}",
  "status": "{CHANGES_REQUESTED or BLOCKED}",
  "attempt": {attempt_number},
  "feedback": "{reviewer notes/feedback}"
}
```

2. **Calculate attempt number**: Count existing entries in `gate_rejections` that match the same `stage` + `substage` + `reviewer` combination, then add 1. This gives the sequential attempt number for this specific gate.

3. **Append to state**: Add the rejection entry to the `gate_rejections` array:
   ```
   bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_append ".gate_rejections" '"'"'{rejection_json}'"'"''
   ```

4. **Update intervention count**: When the user chooses "Address now" in the Rejection Handling flow, increment `intervention_count`:
   ```
   bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_set ".intervention_count" "{new_count}"'
   ```
   This tracks how many times the user manually intervened at governance gates (for SC-003 metric: "80% of orchestrations complete without manual intervention beyond governance gate decisions").

5. **Update stage governance record**: Also update the stage's `governance` object in state to reflect the latest reviewer status:
   ```
   bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_set ".stages.{stage}.governance.{reviewer_field}" '"'"'{"status":"{status}","date":"{date}","notes":"{notes}"}'"'"''
   ```
   Where `{reviewer_field}` maps:
   - `product-manager` → `pm_signoff`
   - `architect` → `architect_signoff`
   - `team-lead` → `techlead_signoff`

6. **Write state atomically**: All state updates are written atomically via `run-state.sh` helpers.

**Retry flow**: After recording the rejection, if the user chose "Address now", the Rejection Handling flow re-invokes the stage skill. After the skill completes, governance is re-checked. If approved, the rejection history remains in `gate_rejections` as an audit trail. If rejected again, a new entry is appended and the attempt number increments.

## Max-Retry Circuit Breaker

After 3 consecutive rejections on the same governance gate, the orchestrator stops automatic retries and asks the user to intervene manually. This prevents infinite rejection loops where the AI agent cannot satisfy a reviewer's requirements.

**Algorithm** (called by Rejection Handling before offering "Address now"):

1. **Count consecutive rejections**: Query the `gate_rejections` array for entries matching the current `stage` + `substage` + `reviewer` combination. Count how many consecutive entries exist (i.e., entries with sequential `attempt` numbers without an intervening approval).

2. **Check threshold**: If the count is >= 3:

   - **If `autonomous_mode == true`**: **HALT** — do NOT auto-override. 3 consecutive rejections means the issue is genuinely broken and requires human intervention. Auto-select `"Pause and fix manually"`. Display: `"CIRCUIT BREAKER in autonomous mode — halting. 3 consecutive rejections require manual fix. Resume with --resume."`. Save state and STOP.

   - **Do NOT offer "Address now"**. Instead, display the circuit breaker message:

   ```
   CIRCUIT BREAKER — Max retries reached
   ======================================
   Stage: {stage}{substage_detail}
   Reviewer: {reviewer}
   Consecutive Rejections: {count}

   The same governance gate has been rejected {count} times.
   Automatic retries are paused to prevent an infinite loop.

   Rejection history:
     Attempt 1: {feedback_summary}
     Attempt 2: {feedback_summary}
     Attempt 3: {feedback_summary}

   Please review the feedback above and make manual changes
   before resuming orchestration.
   ```

   - Use AskUserQuestion:
     - Question: "Max retries reached on this governance gate. How would you like to proceed?"
     - Options:
       - "Pause and fix manually" — Save state with the stage marked as `failed`, exit. User fixes the artifact offline and resumes with `--resume`.
       - "Override and continue" — User takes responsibility. Mark the gate as `BLOCKED_OVERRIDDEN` in state, record the override in `gate_rejections` with a note that the user overrode after max retries, and advance to the next stage.

   - **Handle "Pause and fix manually"**:
     1. Update stage status to `"failed"` in state
     2. Record an error in `error_log`:
        ```json
        {
          "timestamp": "{now}",
          "stage": "{stage}",
          "type": "circuit_breaker",
          "message": "Max retries (3) reached on {reviewer} review for {stage}. Manual intervention required.",
          "recoverable": true
        }
        ```
     3. Write state atomically
     4. Display resume guidance and STOP

   - **Handle "Override and continue"**:
     1. Increment `intervention_count`
     2. Update the stage's governance record to show `BLOCKED_OVERRIDDEN` for the reviewer
     3. Append an override entry to `gate_rejections`:
        ```json
        {
          "timestamp": "{now}",
          "stage": "{stage}",
          "substage": "{substage or null}",
          "reviewer": "{reviewer}",
          "status": "BLOCKED_OVERRIDDEN",
          "attempt": {count + 1},
          "feedback": "User override after {count} consecutive rejections."
        }
        ```
     4. Write state atomically
     5. Mark stage as completed and continue the Core Loop

3. **If count < 3**: The circuit breaker does not fire. Return to Rejection Handling, which offers the normal "Address now" / "Pause orchestration" options.

## Blocked Handling

When a governance gate returns BLOCKED, it represents a critical blocker that a reviewer has identified. The orchestrator displays the blocker details and offers the user three options: resolve, override, or abort.

**Algorithm** (called by Core Loop step 10 when result is BLOCKED):

1. **Extract blocker details**: From the artifact's YAML frontmatter, identify which reviewer(s) returned BLOCKED. Collect:
   - `reviewer`: The reviewer agent name
   - `status`: `BLOCKED`
   - `notes`: The reviewer's blocker description and veto reason
   - `stage`: The current stage name
   - `substage`: The current substage or null

2. **Record the rejection**: Use [Retry Tracking](#retry-tracking) to record this BLOCKED result in `gate_rejections`.

3. **Display blocker information**:

```
GOVERNANCE GATE — BLOCKED
==========================
Stage: {stage}{substage_detail}
Reviewer: {reviewer}

Blocker:
  {reviewer notes/blocker description}

A reviewer has identified a critical issue that prevents this stage
from being approved. This is a hard block, not a request for changes.
```

4. **Offer options**:

   **If `autonomous_mode == true`**: **HALT** — BLOCKED is a hard veto; autonomous mode cannot override reviewer judgment. Save state with stage marked as `failed`, log error, and STOP. Display: `"BLOCKED in autonomous mode — halting. A reviewer has issued a hard block. Manual intervention required. Resume with --resume."`. Do NOT auto-override.

   Use AskUserQuestion to present choices:
   - Question: "A governance gate has been blocked. How would you like to proceed?"
   - Options:
     - "Resolve and re-submit" — Address the blocker in this session. The orchestrator will re-invoke the stage skill, then re-submit for governance review.
     - "Override with justification" — Provide a written justification for overriding the blocker. The gate will be marked `BLOCKED_OVERRIDDEN` and orchestration will continue. Use this only when the blocker is understood and accepted.
     - "Abort orchestration" — Cancel the orchestration entirely. State is saved but the stage is marked as `failed`.

5. **Handle user choice**:

   - **"Resolve and re-submit"**:
     1. Increment `intervention_count`
     2. Write updated state
     3. **Write revision context** to `.aod/revision-context.md` (same format as Rejection Handling step 4 — reviewer, attempt, artifact, stage, substage, and full blocker feedback)
     4. Re-invoke the stage skill via Skill tool with `--revision` flag appended to the original arguments
     5. After skill returns, re-check governance gate (return to Core Loop step 9)
     6. If now approved: continue normally. Clean up `.aod/revision-context.md`.
     7. If blocked again: return to this Blocked Handling flow
     8. **Note**: The max-retry circuit breaker also applies to BLOCKED results. After 3 consecutive BLOCKED results on the same gate, the circuit breaker fires.

   - **"Override with justification"**:
     1. The user's justification is captured from the AskUserQuestion response (they provide it via the "Other" free-text option or it's implied by selecting Override)
     2. Increment `intervention_count`
     3. Update the stage's governance record to show `BLOCKED_OVERRIDDEN`:
        ```json
        {
          "status": "BLOCKED_OVERRIDDEN",
          "date": "{today}",
          "notes": "User override: {justification}"
        }
        ```
     4. Append override entry to `gate_rejections`:
        ```json
        {
          "timestamp": "{now}",
          "stage": "{stage}",
          "substage": "{substage or null}",
          "reviewer": "{reviewer}",
          "status": "BLOCKED_OVERRIDDEN",
          "attempt": {attempt_number},
          "feedback": "User override: {justification}"
        }
        ```
     5. Write state atomically
     6. Mark stage governance as passed and continue the Core Loop

   - **"Abort orchestration"**:
     1. Update stage status to `"failed"` in state
     2. Record an error in `error_log`:
        ```json
        {
          "timestamp": "{now}",
          "stage": "{stage}",
          "type": "user_abort",
          "message": "User aborted orchestration due to BLOCKED governance gate ({reviewer}).",
          "recoverable": true
        }
        ```
     3. Write state atomically
     4. Display abort message:
        ```
        Orchestration aborted. State saved to .aod/run-state.json

        The {stage} stage is marked as failed.

        To restart this stage later:
          /aod.run --resume

        The orchestrator will retry the {stage} stage from the beginning.
        ```
     5. STOP (exit without continuing)
