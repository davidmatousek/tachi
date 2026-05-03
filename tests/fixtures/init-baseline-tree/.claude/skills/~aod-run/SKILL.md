---
name: ~aod-run
description: Full lifecycle orchestrator that chains all 6 AOD stages (Discover, Define, Plan, Build, Deliver, Document) with disk-persisted state for session resilience and governance gates at every boundary. Use this skill when you need to run the full lifecycle, orchestrate stages, resume orchestration, or check orchestration status.
---

# Full Lifecycle Orchestrator Skill

## Purpose

Single-command lifecycle orchestrator that chains all 6 AOD stages autonomously, pausing at governance gates for Triad sign-offs and persisting state to disk for session resilience. After Deliver completes, Document runs automatically as Stage 6.

**Entry Points**:
- Raw idea: `"description"` → start at Discover
- Issue number: `#NNN` or `NNN` → resume from issue's current stage
- Resume: `--resume` → continue from last state checkpoint
- Status: `--status` / `--status #NNN` → read-only display

**State File**: `.aod/run-state.json` (atomic write-then-rename via `run-state.sh`)

## Navigation

| Section | Purpose | Location |
|---------|---------|----------|
| [Step 1: Route by Mode](#step-1-route-by-mode) | Entry point routing | This file |
| [Step 2: Core State Machine Loop](#step-2-core-state-machine-loop) | Central orchestration logic | This file |
| [Plan Substage Tracking](#plan-substage-tracking) | Spec → project_plan → tasks | This file |
| [Stage Skill Mapping](#stage-skill-mapping) | Stage-to-skill invocation table | This file |
| [Post-Stage Context Extraction](#post-stage-context-extraction) | Artifact discovery after each stage | This file |
| [Stage Map Display](#stage-map-display) | Visual progress indicators | This file |
| [Transition Messages](#transition-messages) | Stage transition headers | This file |
| [GitHub Integration](#github-integration) | Label updates after stage completion | This file |
| [Error Logging](#error-logging) | Error/event capture in state file | This file |
| Governance Gate Detection | Reading approval/rejection from frontmatter | `references/governance.md` |
| Governance Tier | Light/Standard/Full gate rules | `references/governance.md` |
| Rejection / Retry / Circuit Breaker / Blocked | Governance result handling | `references/governance.md` |
| New Idea / Issue / Resume / Status Entry | Mode-specific handlers | `references/entry-modes.md` |
| Dry-Run Entry | `--dry-run` preview handler (read-only) | `references/dry-run.md` |
| Corrupted State / Lifecycle Complete | Error and completion handlers | `references/error-recovery.md` |

## Execution

When this skill is invoked, the command file passes a parsed mode and arguments:

```
Mode: {idea | issue | resume | status}
Issue: {number or "none"}
Idea: {text or "none"}
DryRun: {true or false}
```

### Step 1: Route by Mode

Read the mode and DryRun flag from the invocation context. Route to the appropriate handler:

**DryRun + Status check (first)**: If `DryRun == true` AND `Mode == status`, display `"Note: --status is already read-only. --dry-run flag ignored."` and route to Status Entry as normal.

**DryRun check (second)**: If `DryRun == true` (and Mode is NOT `status`):

**MANDATORY**: You MUST use the Read tool to load `references/dry-run.md` before proceeding with dry-run handling. Do NOT rely on memory of prior dry-run content. If the file cannot be read, display an error and STOP.

Follow the Dry-Run Entry instructions from that file. The Dry-Run Entry handler will perform read-only detection and display a preview, then exit without entering the Core Loop.

**Mode routing (if DryRun is false)**:

**MANDATORY**: You MUST use the Read tool to load `references/entry-modes.md` before proceeding with any entry mode handler. Do NOT rely on memory of prior entry mode content. If the file cannot be read, display an error and STOP.

| Mode | Handler | Description |
|------|---------|-------------|
| `idea` | New Idea Entry (in entry-modes.md) | Create initial state, start at Discover |
| `issue` | Issue Entry (in entry-modes.md) | Read GitHub Issue, create/load state, resume |
| `resume` | Resume Entry (in entry-modes.md) | Load state file, validate, continue |
| `status` | Status Entry (in entry-modes.md) | Read-only display, then exit |

After the entry handler sets up state, all modes (except `status`) converge to the **Consent Prompt**, then the **Core Loop**.

### Step 1b: Autonomous Mode Consent

Before entering the Core Loop, display the autonomous mode consent prompt and capture the user's choice. This is the **only** human interaction point in the entire autonomous run.

**Display**:

```
AOD ORCHESTRATOR — Autonomous Mode
====================================
This will run the full lifecycle autonomously:

  Discover → Define → Plan → Build → Deliver → Document

Autonomous mode will:
  - Auto-select defaults for all interactive prompts
  - Auto-retry governance rejections (up to 3 attempts)
  - Halt on circuit breaker or BLOCKED (requires manual fix + resume)
  - Split across sessions if the feature is too large

All decisions are logged to run-state.json for post-run review.

Proceed? (Y/n)
```

**Handle response**:
- **Yes (or empty/default)**: Set `autonomous_mode = true`. All stage skill invocations will include `--autonomous` in args. Continue to Core Loop.
- **No**: Set `autonomous_mode = false`. Skills are invoked without `--autonomous` (interactive mode). Continue to Core Loop.

**On resume** (`--resume`): If the state file contains `"autonomous_mode": true`, skip the consent prompt and continue in autonomous mode. Do not re-ask.

### Step 2: Core State Machine Loop

This is the central orchestration logic. It runs after any entry handler has established or loaded state.

**Loop algorithm**:

1. **Read loop context**: Use Bash to read loop context via `bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_get_loop_context'` — returns `{stage}|{substage}|{stage_status}` (e.g., `plan|spec|in_progress`). Parse the pipe-delimited result. **Do NOT use `aod_state_read` here** — the compound helper extracts only the 3 fields needed for routing.
2. **Check completion**: If stage_status from step 1 indicates all stages may be complete, verify by checking all 6 stage statuses via `bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_get_multi ".stages.discover.status" ".stages.define.status" ".stages.plan.status" ".stages.build.status" ".stages.deliver.status" ".stages.document.status"'`. If all show `completed`, **MANDATORY**: You MUST use the Read tool to load `references/error-recovery.md`, then follow the Lifecycle Complete instructions. Do NOT rely on memory of prior error-recovery content. If the file cannot be read, display an error and STOP. **Note**: If `.stages.document.status` returns null (legacy 5-stage state file), treat as `pending`.
3. **Determine next stage**: Use the `current_stage` and `stage_status` from step 1. If status is `"completed"`, advance to the next stage in sequence: `discover` → `define` → `plan` → `build` → `deliver` → `document`
4. **Handle Plan substages**: If `current_stage` is `plan`, use the `substage` from step 1 and cycle through `spec` → `project_plan` → `tasks`. Only advance past Plan when all 3 substages complete. **When advancing between substages, apply context boundary** (see Plan Substage Tracking step 3a) to clear previous substage content and retain only approval metadata.
5. **Write pre-stage checkpoint**: Update state with `current_stage` status = `"in_progress"` and current timestamp. Write atomically via `bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_write '"'"'<json>'"'"''`.
6. **Display stage map**: Show current progress (see [Stage Map Display](#stage-map-display))
7. **Display transition message**: Show formatted header for the stage about to execute (see [Transition Messages](#transition-messages))
7a. **Aggressive pre-Build boundary**: If the stage about to execute is `build`, apply an extra-aggressive context boundary before invocation:
    1. Summarize all prior stages into a compact metadata block (~500 tokens max):
       - Feature: `{feature_id}` - `{feature_name}`
       - Branch: `{branch}`
       - Spec: `{path}` (APPROVED by PM)
       - Plan: `{path}` (APPROVED by PM + Architect)
       - Tasks: `{path}` (APPROVED by PM + Architect + Team-Lead)
       - Wave count: `{N}`
    2. Clear ALL prior stage content from working context
    3. Build skill reads its own context (tasks.md, plan.md, assignments) fresh
    4. Display: `"[Pre-Build boundary] Prior stages summarized (~500 tokens). Build reads context fresh."`
8. **Invoke stage skill**: Use the Skill tool to invoke the appropriate stage skill (see [Stage Skill Mapping](#stage-skill-mapping)). Pass required context (idea text, issue number, artifact paths from prior stages).
9. **Detect governance result**: After the skill returns, first check the governance cache via `bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_get_governance_cache "{artifact}" "{reviewer}"'`. If the cache returns a verdict (not `"null"`), use the cached result. If the cache returns `"null"`, **MANDATORY**: You MUST use the Read tool to load `references/governance.md` before proceeding with governance gate detection. Do NOT rely on memory of prior governance content. If the file cannot be read, display an error and STOP. Follow the Governance Gate Detection and Governance Tier instructions from that file. Apply tier-specific rules.

   **Parallel Triad Reviews**: When a governance gate requires multiple reviewers (e.g., plan.md requires PM + Architect, tasks.md requires PM + Architect + Team-Lead), execute reviews **in parallel** using multiple Agent tool calls in a single message:

   1. **Parallel execution**: Launch all required reviewers simultaneously via Agent tool calls in one message. Each reviewer runs in its own agent context, preventing cross-contamination.
   2. **Cache all verdicts**: After all reviewers return, cache each verdict via `aod_state_cache_governance` before evaluating the aggregate result.
   3. **Aggregate evaluation**: After all reviewers complete, evaluate the combined result. If **any** reviewer returned CHANGES_REQUESTED or BLOCKED, handle per step 10 (use the most severe status).
   4. **Same checklists and criteria**: Parallel execution uses the same reviewers, review prompts, and approval criteria as sequential — only the execution model changes.

   **Context note**: Parallel reviews are safe with 1M context. Each reviewer runs in an isolated agent context, so there is no cross-reviewer drift. Re-grounding (see below) applies **once after all reviewers return**, not between each reviewer.
10. **Handle result**:
    - **APPROVED / APPROVED_WITH_CONCERNS**: Mark stage completed in state, record artifacts, write checkpoint, continue loop
    - **CHANGES_REQUESTED**: Follow the Rejection Handling instructions in `references/governance.md` (re-read if not already loaded). This includes Retry Tracking and Max-Retry Circuit Breaker checks.
    - **BLOCKED**: Follow the Blocked Handling instructions in `references/governance.md` (re-read if not already loaded).
    - **No governance gate for this stage/tier**: Mark completed, continue
11. **Write post-stage checkpoint**: Update state with completion status, artifacts, governance results, timestamp. Write atomically via `bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_write '"'"'<json>'"'"''`.
11a. **Apply context boundary** (all stage transitions): When advancing from one stage to the next:
    1. Display: `"[Context boundary] Clearing {completed_stage} context"`
    2. Retain ONLY from the completed stage:
       - `status` (APPROVED / completed)
       - `artifact_paths` (list of file paths)
       - `feature_id`, `github_issue`, `branch`
       - governance verdict summary (one line per reviewer)
    3. The next stage skill will re-read any artifacts it needs via Read tool
    4. Skill file content from the completed stage is NOT carried forward
12. **Update GitHub Issue label**: If `gh` available, update stage label (see [GitHub Integration](#github-integration))
13. **Loop**: Return to step 1

**Re-grounding policy** (context-thrifty): Re-read reference files only when variable-length output has been injected into context since the last read. This prevents template drift without wasting context on redundant reads.

- **After governance reviews**: If reviewer feedback, rejection details, or override justifications produced significant output (>50 lines), re-read `references/governance.md` before continuing the loop. With parallel reviews, this applies **once after all reviewers return**, since each reviewer runs in an isolated agent context.
- **After rejection/blocked handling**: Re-read `references/governance.md` before re-entering the loop, since user interaction and error display inject variable-length content.
- **After lifecycle complete display**: Re-read `references/error-recovery.md` to ensure the completion template is followed exactly.
- **Skip re-grounding** when: the previous step produced minimal output (stage map display, short status messages, cache hits). Unnecessary re-reads waste ~4-7K tokens each.

**Stage sequence**: `discover` → `define` → `plan` (spec → project_plan → tasks) → `build` → `deliver` → `document`

**Exit conditions**:
- All stages completed → display lifecycle summary (6/6)
- BLOCKED with no resolution → save state, exit
- User chooses to pause → save state, exit
- Session ends → user resumes with `--resume` in new session

### Plan Substage Tracking

The Plan stage contains 3 substages executed in strict sequence. The orchestrator tracks each substage independently and only advances past Plan when all 3 are complete.

**Substage sequence**: `spec` → `project_plan` → `tasks`

**Algorithm** (detailed expansion of Core Loop step 4):

1. **When entering Plan stage**: If `current_substage` is null, set it to `spec` (first substage). Update state: `stages.plan.status = "in_progress"`, `stages.plan.started_at = {now}`, `current_substage = "spec"`.

2. **Determine active substage**: Read `current_substage` from state. Check the substage's status in `stages.plan.substages.{substage}.status`:
   - If `"completed"`: Advance to next substage in sequence
   - If `"pending"` or `"in_progress"`: This is the active substage to execute

3. **Substage advancement logic**:
   - `spec` completed → set `current_substage = "project_plan"`, set `stages.plan.substages.project_plan.status = "in_progress"`. **Apply context boundary** (see step 3a).
   - `project_plan` completed → set `current_substage = "tasks"`, set `stages.plan.substages.tasks.status = "in_progress"`. **Apply context boundary** (see step 3a).
   - `tasks` completed → set `current_substage = null`, mark overall Plan stage as `"completed"`, set `stages.plan.completed_at = {now}`

3a. **Context boundary at substage transitions** (FR-013, FR-014, FR-015, FR-016) — *retained for context thrift; prevents accumulation even with 1M window*:

   When advancing from one substage to the next (spec → project_plan, or project_plan → tasks), apply a context boundary to prevent context accumulation:

   **Step 1 - Display boundary message**:
   ```
   [Context boundary] Clearing {previous_substage} context
   ```
   Where `{previous_substage}` is `spec` or `project_plan`.

   **Step 2 - Extract and retain only approval metadata**:
   From the completed substage, retain only:
   - `status`: The approval status (e.g., "APPROVED")
   - `artifact_path`: Path to the artifact (e.g., `specs/{NNN}-*/spec.md`)
   - `feature_id`: The 3-digit feature ID (e.g., "047")

   These values are already persisted in `run-state.json` under `stages.plan.substages.{substage}` and do not require re-extraction.

   **Step 3 - Clear previous substage full content**:
   The previous substage's artifact content (spec.md or plan.md full text) is NOT carried forward. The next substage skill will read its own required context fresh.

   **Step 4 - On-demand re-read available**:
   If the next substage explicitly needs details from a prior artifact, it can re-read the artifact using the path stored in metadata. This is NOT automatic — the substage skill must explicitly invoke the Read tool with the artifact path from `stages.plan.substages.{prior_substage}.artifacts`.

   **Example boundary output**:
   ```
   [Context boundary] Clearing spec context
   Retained metadata: {status: "APPROVED", artifact_path: "specs/047-*/spec.md", feature_id: "047"}
   ```

4. **Write substage checkpoint**: After each substage transition, write state atomically. This ensures that if the session dies between substages, the orchestrator can resume at the correct substage.

5. **Skill invocation per substage**:
   - `spec` substage → invoke `aod.spec` skill
   - `project_plan` substage → invoke `aod.project-plan` skill
   - `tasks` substage → invoke `aod.tasks` skill

6. **Governance per substage**: Each substage has its own governance gate. First check the governance cache via `aod_state_get_governance_cache` (see Core Loop step 9). If the cache returns `"null"`, fall back to reading the substage's artifact frontmatter (load `references/governance.md` for the detection algorithm):
   - `spec`: Check `specs/{NNN}-*/spec.md` for PM sign-off
   - `project_plan`: Check `specs/{NNN}-*/plan.md` for PM + Architect sign-off
   - `tasks`: Check `specs/{NNN}-*/tasks.md` for PM + Architect + Team-Lead sign-off

7. **Display**: When displaying the stage map during Plan, show the active substage:
   ```
   [>] Plan (spec)       — spec substage in progress
   [>] Plan (plan)       — project_plan substage in progress
   [>] Plan (tasks)      — tasks substage in progress
   ```

### Stage Skill Mapping

Each lifecycle stage maps to an existing AOD skill invoked via the Skill tool. The orchestrator delegates all stage work — it never re-implements stage logic.

| Stage | Substage | Skill to Invoke | Skill Tool Name | Arguments to Pass |
|-------|----------|----------------|-----------------|-------------------|
| Discover | — | Discovery flow | `aod.discover` | `--autonomous "{idea_text}"` (if autonomous_mode) or idea text only |
| Define | — | PRD creation | `aod.define` | `--autonomous "{feature_title}"` (if autonomous_mode) or feature title only |
| Plan | spec | Specification | `aod.spec` | `--autonomous` (if autonomous_mode) or no args |
| Plan | project_plan | Architecture plan | `aod.project-plan` | `--autonomous` (if autonomous_mode) or no args |
| Plan | tasks | Task breakdown | `aod.tasks` | `--autonomous` (if autonomous_mode) or no args |
| Build | — | Implementation | `aod.build` | `--orchestrated --autonomous` (if autonomous_mode) or `--orchestrated` only |
| Deliver | — | Delivery retrospective | `aod.deliver` | `--autonomous "FEATURE: {NNN} - {name}" {deliver_flags...}` (if autonomous_mode) or `"FEATURE: {NNN} - {name}" {deliver_flags...}` (interactive). `{deliver_flags...}` expands the per-feature flags forwarded from `/aod.orchestrate` via the Task description (e.g. `--no-tests="<reason>"`). When `/aod.run` is invoked standalone (not via `/aod.orchestrate`), `{deliver_flags...}` is empty. See aod-orchestrate SKILL.md Step 4.7 and Step 7.1.1 step 2.5 for the upstream contract. |
| Document | — | Documentation review | `aod.document` | `--autonomous` (if autonomous_mode) or no args |

**Invocation pattern**: Use the Skill tool with `skill: "{skill_name}"` and pass arguments as `args: "{arguments}"`.

**Context passing between stages** (FR-012):
- After **Discover** completes: extract GitHub Issue number from discovery output; store in state as `github_issue`
- After **Define** completes: PRD path is at `docs/product/02_PRD/{NNN}-*.md`; store in state artifacts
- After **Plan:spec** completes: spec path is at `specs/{NNN}-*/spec.md`; store in state artifacts
- After **Plan:project_plan** completes: plan path is at `specs/{NNN}-*/plan.md`; store in state artifacts
- After **Plan:tasks** completes: tasks path is at `specs/{NNN}-*/tasks.md`; store in state artifacts
- After **Build** completes: implementation files tracked via tasks.md `[X]` markers
- After **Deliver** completes: delivery summary and metrics captured

**Argument formatting per stage**:

When `autonomous_mode == true`, prepend `--autonomous` to all skill args:

- **Discover**: `args: "--autonomous {idea_text}"` — pass flag + raw idea description
- **Define**: `args: "--autonomous {feature_title}"` — pass flag + feature title/topic
- **Plan stages**: `args: "--autonomous"` — flag only; skills read context from branch
- **Build**: `args: "--orchestrated --autonomous"` — both flags enable orchestrated + autonomous modes
- **Deliver**: `args: "--autonomous FEATURE: {NNN} - {feature_name} {deliver_flags...}"` — flag + feature info + optional per-feature deliver flags forwarded from `/aod.orchestrate` (e.g. `--no-tests="<reason>"`). When `/aod.run` is invoked standalone (not via orchestrator), `{deliver_flags...}` is empty. See `aod-orchestrate` SKILL.md Step 4.7 + 7.1.1 step 2.5 for the upstream contract.
- **Document**: `args: "--autonomous"` — flag only; skill reads context from branch

When `autonomous_mode == false` (interactive), omit `--autonomous`:

- **Discover**: `args: "{idea_text}"`
- **Define**: `args: "{feature_title}"`
- **Plan stages**: no args
- **Build**: `args: "--orchestrated"`
- **Deliver**: `args: "FEATURE: {NNN} - {feature_name} {deliver_flags...}"` — `{deliver_flags...}` expansion is empty unless forwarded from `/aod.orchestrate` (see Stage Skill Mapping table note)
- **Document**: no args

### Post-Stage Context Extraction

After each stage skill returns, the orchestrator extracts context from the produced artifacts and updates the state file. This ensures subsequent stages receive the correct inputs.

**After Discover completes**:

1. The Discover skill creates a GitHub Issue and outputs the issue number. Read the orchestration output to find the issue number.
2. Use Bash to scan for new GitHub Issues: `gh issue list --label "stage:discover" --json number,title --limit 5` (if `gh` available)
3. Update state fields:
   - `github_issue`: Set to the issue number
   - `feature_id`: Zero-pad the issue number to 3 digits (e.g., `22` → `"022"`)
   - `branch`: Set to `{feature_id}-{feature_name}` (e.g., `"022-add-dark-mode-toggle"`)
4. Create the feature branch if not already on it: `git checkout -b {branch}` (or confirm current branch matches)
5. Record artifacts: Add the GitHub Issue URL to `stages.discover.artifacts`
6. Write updated state atomically

**After Define completes**:

1. Use Glob to find the PRD: `docs/product/02_PRD/{NNN}-*.md` where NNN is `feature_id`
2. Record artifacts: Add the PRD path to `stages.define.artifacts`
3. Write updated state atomically

**After Plan:spec completes**:

1. Use Glob to find the spec: `specs/{NNN}-*/spec.md`
2. Record artifacts: Add the spec path to `stages.plan.substages.spec.artifacts`
3. Write updated state atomically

**After Plan:project_plan completes**:

1. Use Glob to find the plan: `specs/{NNN}-*/plan.md`
2. Record artifacts: Add the plan path to `stages.plan.substages.project_plan.artifacts`
3. Write updated state atomically

**After Plan:tasks completes**:

1. Use Glob to find tasks and assignments: `specs/{NNN}-*/tasks.md`, `specs/{NNN}-*/agent-assignments.md`
2. Record artifacts: Add paths to `stages.plan.substages.tasks.artifacts`
3. Mark overall Plan stage as completed
4. Write updated state atomically

**After Plan:tasks completes (continued) — Size Estimation Display**:

After recording Plan:tasks artifacts and before the Core Loop advances to Build, perform a size estimation:

1. Read `agent-assignments.md` from `specs/{NNN}-*/agent-assignments.md`
2. Count the number of waves (sections labeled "Wave 1", "Wave 2", etc.)
3. Apply the heuristic:
   - `wave_count <= 3` → `session_strategy = "one-shot"`, `estimated_sessions = 1`
   - `wave_count <= 6` → `session_strategy = "cautious"`, `estimated_sessions = 2`
   - `wave_count > 6` → `session_strategy = "multi-session"`, `estimated_sessions = ceil(wave_count / 3)`
4. Update state with the estimation:
   ```
   bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_write '"'"'{"session_strategy":"{strategy}","estimated_sessions":{N},"build_progress":{"total_waves":{wave_count},"completed_waves":0,"session_breaks":[]}}'"'"''
   ```
5. Display the build estimate:

   ```
   --- BUILD ESTIMATE ---
   Waves: {wave_count}
   Estimated sessions: {estimated_sessions}

   {If wave_count <= 3: "Expected to complete in this session."}
   {If wave_count > 3: "May require ~{estimated_sessions} sessions. The orchestrator will auto-break and resume if needed."}
   ```

**After Build completes**:

1. Read tasks.md from `specs/{NNN}-*/tasks.md`
2. Count total tasks (lines matching `- [ ]` or `- [X]`)
3. Count completed tasks (lines matching `- [X]`)
4. Determine the last completed wave by reading `agent-assignments.md` and cross-referencing completed tasks
5. **If completed < total (session break protocol)**:
   - Parse the `AOD_BUILD_RESULT` comment from build output
   - Log in error_log with type `"build_incomplete"` and message including wave progress
   - Update `build_progress` in state:
     ```
     bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_write '"'"'{"build_progress":{"total_waves":{total},"completed_waves":{N},"session_breaks":[{"session":{session_count},"waves_completed":"{range}","timestamp":"{now}"}]}}'"'"''
     ```
   - Log the session break decision to `autonomous_decisions`:
     ```
     bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_append ".autonomous_decisions" '"'"'{"decision":"session_break","reason":"Build incomplete: {completed}/{total} tasks after wave {N}","timestamp":"{now}"}'"'"''
     ```
   - Display the session break message:
     ```
     AOD ORCHESTRATOR — Session Break
     ==================================
     Feature: {feature_name} (#{github_issue})
     Build: Wave {N}/{total_waves} complete ({completed_tasks}/{total_tasks} tasks)

     The remaining waves require a new conversation.

     To continue:
       /aod.run --resume

     The orchestrator will pick up from Wave {N+1} automatically.

     Resume prompt (copy-paste):
       claude "Resume aod.run for #{github_issue} — {feature_name}. Run /aod.run --resume"
     ```
   - **STOP** — Do NOT continue to Deliver. Exit the Core Loop.
6. **If completed == total**: Mark Build as completed, continue to Deliver
7. Record artifacts: Add `"tasks.md (all tasks completed)"` to `stages.build.artifacts`
8. Write updated state atomically

**After Deliver completes**:

1. The deliver stage produces a delivery summary
2. **Check for halt record** (FR-024, FR-025) — before marking Deliver as completed, inspect `.aod/state/deliver-{NNN}.halt.json` (where `NNN` is the zero-padded `feature_id` from state). The `/aod.deliver` skill writes this file when it halts for review per the three-channel halt protocol. Schema and exit-code taxonomy are documented in [`specs/139-delivery-verified-not-documented/contracts/halt-record.md`](../../../specs/139-delivery-verified-not-documented/contracts/halt-record.md).

   **Exit-code taxonomy** (from halt-record contract §Channel 3):

   | Code | Meaning | `/aod.run` policy |
   |------|---------|-------------------|
   | 0 | Success | Proceed to Document stage |
   | 10 | Halted for review (E2E fail, AC-coverage fail, or abandoned heal) | Halt lifecycle; emit halt record to operator; do NOT advance to Document |
   | 11 | Lockfile conflict (concurrent `/aod.deliver` live) | Halt lifecycle; log holding PID from lockfile; operator resolves |
   | 12 | Abandoned heal sentinel (crash-recovery) | Halt lifecycle; emit manual-cleanup prompt; do NOT auto-retry |
   | 1-9 | Pre-existing delivery errors | Handle per existing stage_error logic (log, surface to operator) |

   **Inspection algorithm**:

   1. Derive the halt-record path: `halt_record_path = ".aod/state/deliver-{NNN}.halt.json"`
   2. Check existence via Bash: `test -f "$halt_record_path" && echo EXISTS`
   3. If the file does NOT exist: assume Deliver succeeded; proceed to step 3 below (record artifacts, continue to Document).
   4. If the file exists, parse it via `jq`:

      ```bash
      jq -r '[.reason, .recovery_status, (.heal_pr_url // "null"), (.heal_pr_number // "null"), (.failing_scenarios | tostring), .timestamp] | @tsv' "$halt_record_path"
      ```

   5. Extract fields: `reason`, `recovery_status`, `heal_pr_url`, `heal_pr_number`, `failing_scenarios`, `timestamp`.

   6. **Emit human-readable halt summary to the operator** (surfaced in stdout via the skill's output):

      ```
      =====================================================
      LIFECYCLE HALT — Deliver stage halted for review
      =====================================================
      Feature: {feature_id} — {feature_name}
      Reason: {reason}
      Recovery Status: {recovery_status}
      Heal-PR: {heal_pr_url} (#{heal_pr_number})
      Failing Scenarios:
        - {scenario_1}
        - {scenario_2}
        ...
      Halted At: {timestamp}
      =====================================================

      Next steps:
      - Review the heal-PR for failure context and attempted fixes
      - Fix the underlying failure and merge the heal-PR (requires human approval — no auto-merge per FR-023)
      - Re-run /aod.run --resume to retry Deliver after the fix is merged
      ```

   7. **Mark Deliver as halted** in state:

      ```
      bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_write '"'"'{"stages":{"deliver":{"status":"failed","halt_record":{"reason":"{reason}","recovery_status":"{recovery_status}","heal_pr_url":"{heal_pr_url}","heal_pr_number":{heal_pr_number},"failing_scenarios":{failing_scenarios_json},"timestamp":"{timestamp}"}}}}'"'"''
      ```

   8. **Append to error_log** (per Error Logging contract) with `type: "stage_error"` and a summary message.

   9. **Autonomous mode policy**: If `autonomous_mode == true`, the halt is non-recoverable within the current run — the lifecycle stops here. Do NOT advance to Document. The operator resolves via manual heal-PR review, then re-runs `/aod.run --resume` to re-invoke the Deliver stage. Emit an additional line:

      ```
      Autonomous mode: lifecycle halted. Manual intervention required before --resume.
      ```

   10. **Interactive mode policy**: If `autonomous_mode == false`, display the halt summary and prompt:

       ```
       Deliver stage halted for review. Options:
         [Pause / Abort]
       ```

       - **Pause**: Save state, exit cleanly. Operator resumes after fix via `/aod.run --resume`.
       - **Abort**: Save state with `aborted` status, exit.

   11. **Exit the Core Loop** — do NOT advance to Document. The halt is terminal for the current session.

3. Record artifacts: Add `"delivery complete"` to `stages.deliver.artifacts` (only when no halt record is present)
4. Write updated state atomically

**After Document completes**:

1. The document stage produces documentation review artifacts (CHANGELOG updates, docstrings, API docs, code simplification commits)
2. Record artifacts: Add PR URL and commit SHAs from the document branch merge to `stages.document.artifacts`
3. Write updated state atomically
4. **MANDATORY**: You MUST use the Read tool to load `references/error-recovery.md`, then follow the Lifecycle Complete instructions. If the file cannot be read, display an error and STOP.

### Stage Map Display

Display the stage map after each stage transition to show progress. This is referenced by Core Loop step 6.

**Algorithm**:

1. Read state from `.aod/run-state.json`
2. For each stage in sequence (`discover`, `define`, `plan`, `build`, `deliver`, `document`), determine its display marker:
   - `status == "completed"` → `[x]`
   - `status == "in_progress"` → `[>]`
   - `status == "pending"` → `[ ]`
   - `status == "failed"` → `[!]`
3. For the Plan stage, append the active substage in parentheses if in progress:
   - If `current_substage == "spec"` → `Plan (spec)`
   - If `current_substage == "project_plan"` → `Plan (plan)`
   - If `current_substage == "tasks"` → `Plan (tasks)`
   - If Plan is completed → `Plan`
4. Display the formatted stage map:

```
Stage Map:
  {marker} Discover  {marker} Define  {marker} Plan{substage}  {marker} Build  {marker} Deliver  {marker} Document
```

**Examples**:

Starting a new lifecycle:
```
Stage Map:
  [>] Discover  [ ] Define  [ ] Plan  [ ] Build  [ ] Deliver  [ ] Document
```

After Discover and Define complete, Plan:spec in progress:
```
Stage Map:
  [x] Discover  [x] Define  [>] Plan (spec)  [ ] Build  [ ] Deliver  [ ] Document
```

Mid-lifecycle with Build in progress:
```
Stage Map:
  [x] Discover  [x] Define  [x] Plan  [>] Build  [ ] Deliver  [ ] Document
```

All stages complete:
```
Stage Map:
  [x] Discover  [x] Define  [x] Plan  [x] Build  [x] Deliver  [x] Document
```

### Transition Messages

Display a formatted transition header before each stage begins executing. This is referenced by Core Loop step 7.

**Algorithm** (called by Core Loop step 7, before each stage skill invocation):

1. **Read current state**: Get `current_stage` and `current_substage` from state.

2. **Map stage to number and detail**: Use the lookup table below:

   | `current_stage` | `current_substage` | N | STAGE_NAME | Substage Detail |
   |-----------------|-------------------|---|------------|----------------|
   | `discover` | null | 1 | DISCOVER | — |
   | `define` | null | 2 | DEFINE | — |
   | `plan` | `spec` | 3 | PLAN | sub-stage 1/3: Feature Specification |
   | `plan` | `project_plan` | 3 | PLAN | sub-stage 2/3: Architecture Plan |
   | `plan` | `tasks` | 3 | PLAN | sub-stage 3/3: Task Breakdown |
   | `build` | null | 4 | BUILD | — |
   | `deliver` | null | 5 | DELIVER | — |
   | `document` | null | 6 | DOCUMENT | — |

3. **Format and display**:

   For non-Plan stages:
   ```
   --- STAGE {N}: {STAGE_NAME} ---
   ```

   For Plan substages:
   ```
   --- STAGE 3: PLAN ({substage detail}) ---
   ```

**Examples**:
```
--- STAGE 1: DISCOVER ---
--- STAGE 3: PLAN (sub-stage 1/3: Feature Specification) ---
--- STAGE 4: BUILD ---
```

### GitHub Integration

After each stage completes successfully (governance gate passed), update the GitHub Issue's `stage:*` label to reflect the new current stage. This keeps the GitHub Issue board in sync with the orchestration state (FR-023).

**Algorithm** (called by Core Loop step 12, after post-stage checkpoint):

1. **Check prerequisites**:
   - Read `github_issue` from state. If null (no GitHub Issue for this feature), skip entirely.
   - Check if `gh` CLI is available: `command -v gh >/dev/null 2>&1`. If not, skip silently.
   - Check if `gh` is authenticated: `gh auth status >/dev/null 2>&1`. If not, skip silently.

2. **Determine the new stage label**: Map the newly-completed stage to the next stage in the sequence:

   | Completed Stage | Completed Substage | New Label |
   |-----------------|-------------------|-----------|
   | discover | — | `stage:define` |
   | define | — | `stage:plan` |
   | plan | spec | `stage:plan` (still in Plan) |
   | plan | project_plan | `stage:plan` (still in Plan) |
   | plan | tasks | `stage:build` |
   | build | — | `stage:deliver` |
   | deliver | — | `stage:document` |
   | document | — | `stage:done` |

   **Note**: Plan substage completions (spec, project_plan) do not change the label — the issue stays at `stage:plan` until all 3 substages complete.

3. **Update the label**: Use the `github-lifecycle.sh` function:
   ```
   bash -c 'source .aod/scripts/bash/github-lifecycle.sh && aod_gh_update_stage {github_issue} {new_stage}'
   ```

4. **Handle failures gracefully**: If the label update fails, log a warning but do NOT halt orchestration.
   - Display: `"Note: GitHub label update skipped ({reason}). Orchestration continues."`

5. **Backlog refresh**: After updating the label:
   ```
   bash .aod/scripts/bash/backlog-regenerate.sh 2>/dev/null || true
   ```
   This is fire-and-forget — failure does not affect orchestration.

### Error Logging

Capture stage errors and significant events in the state file's `error_log` array for debugging and auditability. Error entries follow Entity 4 schema.

**Algorithm** (called whenever an error or significant event occurs during orchestration):

1. **Build error entry**:

```json
{
  "timestamp": "{current ISO 8601 timestamp}",
  "stage": "{current_stage}",
  "type": "{error_type}",
  "message": "{descriptive error message}",
  "recoverable": true
}
```

2. **Error types** (standardized values for `type` field):

   | Type | When Used | Recoverable |
   |------|-----------|-------------|
   | `stage_error` | A stage skill invocation fails or returns an error | true |
   | `governance_rejection` | A governance gate returns CHANGES_REQUESTED | true |
   | `governance_blocked` | A governance gate returns BLOCKED | true |
   | `circuit_breaker` | Max retries (3) reached on a governance gate | true |
   | `user_abort` | User chose to abort orchestration | true |
   | `artifact_missing` | Artifact recorded in state not found on disk | true |
   | `state_corruption` | State file failed validation | true |
   | `github_error` | GitHub CLI operation failed | true |
   | `skill_invocation_error` | Skill tool invocation returned unexpected result | true |

3. **Append to state**: Use the `aod_state_append` function:
   ```
   bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_append ".error_log" '"'"'{"timestamp":"...","stage":"...","type":"...","message":"...","recoverable":true}'"'"''
   ```

4. **When to log errors**:
   - **Stage skill failure**: When a Skill tool invocation produces an error or unexpected output
   - **Governance gate rejection**: Also tracked in `gate_rejections`, log summary in `error_log`
   - **Circuit breaker activation**: When max retries are reached
   - **User abort**: When the user chooses to abort
   - **Artifact inconsistency**: When resume validation detects missing artifacts
   - **State corruption**: When the state file fails validation
   - **GitHub errors**: When `gh` CLI operations fail

5. **Error entries are append-only**: Never remove or modify existing error log entries. The log provides a chronological audit trail.

   | Type | When Used | Recoverable |
   |------|-----------|-------------|
   | `build_incomplete` | Post-build verification finds incomplete tasks | true |

### Adaptive Session Management

The orchestrator adapts its session strategy based on feature size. Small features complete in one session; large features automatically split across sessions when context runs out.

**Size Estimation Heuristic** (executed after Plan:tasks completes, before Build):

```
wave_count = count of waves in agent-assignments.md

if wave_count <= 3:
  session_strategy = "one-shot"
  estimated_sessions = 1
elif wave_count <= 6:
  session_strategy = "cautious"
  estimated_sessions = 2
else:
  session_strategy = "multi-session"
  estimated_sessions = ceil(wave_count / 3)
```

**Session breaks are reactive, not predictive**: Token heuristics don't work — Claude Code doesn't expose token usage to skills. Instead, `aod.build` runs waves until either all complete (`AOD_BUILD_RESULT:COMPLETE`) or context degrades (`AOD_BUILD_RESULT:PARTIAL`). Post-build verification in the orchestrator then triggers a session break if tasks remain incomplete.

**State fields for session management**:

| Field | Type | Description |
|-------|------|-------------|
| `session_strategy` | string | `"one-shot"`, `"cautious"`, or `"multi-session"` — set after Plan:tasks |
| `estimated_sessions` | number | Estimated session count from heuristic |
| `build_progress` | object | `{total_waves, completed_waves, session_breaks[]}` — updated after each build run |
| `autonomous_decisions` | array | Log of automated decisions (session breaks, auto-retries) for post-run review |

**Resume-after-break flow**: When `aod.run --resume` loads a state where Build is `in_progress`, it re-invokes `aod.build --orchestrated --autonomous`. Build's Step 1.6 detects completed waves via `[X]` markers and continues from the next incomplete wave. This repeats (recursive session breaks) until all waves complete, then the orchestrator advances to Deliver.
