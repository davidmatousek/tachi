---
name: aod-orchestrate
description: >-
  Multi-feature orchestration skill that bridges /aod.blueprint output to
  parallel wave execution. Groups synced GitHub Issues by ICE priority tier
  (P0/P1/P2) into sequential waves, creates Task records, spawns batch
  sessions via the orchestrator API, monitors completion, and reports results.
  Supports --issues (selective), --dry-run (preview), and --yes (skip confirm).
  Use when a developer invokes /aod.orchestrate to execute multiple features
  from a blueprint in priority-ordered waves.
---

# /aod.orchestrate Skill

## Purpose

Orchestrate multiple features from `/aod.blueprint` output as priority-ordered parallel waves. The skill auto-detects the project, fetches actionable issues, groups them by ICE priority tier, and executes waves sequentially via the batch spawn API with governance checkpoints at tier boundaries.

**Flow**: Parse flags --> Auto-detect project --> Check idempotency --> Fetch issues --> Plan waves --> Confirm --> Execute waves --> Report completion

---

## Step 0: Capture Start Time

Record the orchestration start time for duration calculation in the completion report.

Run the following command via Bash tool and store the result:

```bash
date +%s
```

Store this value as `start_time` for use in Step 8 (Completion Reporter).

---

## Step 1: Parse Arguments

Parse user arguments from the skill invocation.

### User Input

```text
$ARGUMENTS
```

### 1.1: Parse --issues flag

Check if `$ARGUMENTS` contains `--issues`:

1. If `$ARGUMENTS` contains `--issues N,N,N` (comma-separated issue numbers):
   - Extract the comma-separated list of issue numbers
   - Set `selected_issues` to the parsed list of integers
   - Strip `--issues N,N,N` from `$ARGUMENTS` (trim extra whitespace)
2. If `$ARGUMENTS` does NOT contain `--issues`:
   - Set `selected_issues` to empty (all issues)

### 1.2: Parse --dry-run flag

Check if `$ARGUMENTS` contains `--dry-run`:

1. If present:
   - Set `dry_run = true`
   - Strip `--dry-run` from `$ARGUMENTS`
2. If not present:
   - Set `dry_run = false`

### 1.3: Parse --yes flag

Check if `$ARGUMENTS` contains `--yes`:

1. If present:
   - Set `auto_confirm = true`
   - Strip `--yes` from `$ARGUMENTS`
2. If not present:
   - Set `auto_confirm = false`

---

## Step 2: Project Auto-Detection

Resolve the active orchestrator project from local context. Detection follows a priority order with fallback.

### 2.1: Read config file

Run the following command via Bash tool:

```bash
cat .aod/config.json 2>/dev/null
```

If the file exists and contains a `project_id` field, extract the value and proceed to Step 2.2 for validation.

If the file does not exist or does not contain `project_id`, skip to Step 2.3 (git remote fallback).

### 2.2: Validate cached project ID

Run the following command via Bash tool (replace `{project_id}` with the extracted value):

```bash
curl -sf "${AOD_API_URL:-http://localhost:8000}/api/v1/projects/{project_id}" -H "X-AOD-Source: skill"
```

- If the command succeeds (exit code 0 and valid JSON response): the project is valid. Store `project_id` and proceed to Step 3.
- If the command fails (404 or network error): the cached config is stale. Proceed to Step 2.3 (git remote fallback). Do NOT display an error yet.

### 2.3: Git remote fallback

Extract the GitHub owner and repo from the git remote:

```bash
git remote get-url origin 2>/dev/null | sed -E 's|.*github\.com[:/]([^/]+)/([^/.]+)(\.git)?$|\1/\2|'
```

Parse the output to extract `github_owner` and `github_repo` (split on `/`).

If git remote extraction fails (no remote or not a GitHub URL), display the following error and STOP:

```
ERROR: No project registered. Run /aod.blueprint first to set up your project.
```

### 2.4: Query API by GitHub owner/repo

Run the following command via Bash tool:

```bash
curl -sf "${AOD_API_URL:-http://localhost:8000}/api/v1/projects" -H "X-AOD-Source: skill"
```

Parse the JSON response and find a project where `github_owner` matches and `github_repo` matches the values extracted in Step 2.3.

- If a match is found: store `project_id` from the matching project. Proceed to Step 2.5 to cache the result.
- If no match is found: display the following error and STOP:

```
ERROR: No project registered. Run /aod.blueprint first to set up your project.
```

### 2.5: Write config cache

Write the discovered project ID to `.aod/config.json` for faster detection on subsequent runs:

```bash
mkdir -p .aod && echo '{"project_id": "{project_id}"}' > .aod/config.json
```

If the write fails, continue without caching (non-fatal).

Proceed to Step 3 with the resolved `project_id`.

---

## Step 3: Idempotent Launch Check

Check for active orchestrations to prevent duplicate launches.

### 3.1: Query orchestration status

Run the following command via Bash tool:

```bash
curl -sf "${AOD_API_URL:-http://localhost:8000}/api/v1/projects/{project_id}/orchestrations/status" \
  -H "X-AOD-Source: skill"
```

Replace `{project_id}` with the resolved project ID from Step 2.

### 3.2: Handle response

**If the command fails with a 404 or network error**: No active orchestration exists. Proceed to Step 4.

**If the command succeeds**: Parse the JSON response and check the `status` field.

- If `status` is `"completed"` or `"aborted"`: No active orchestration. Proceed to Step 4.

- If `status` is `"running"` or `"paused"`:
  1. Extract `id` (orchestration ID) and `current_wave` and `total_waves` from the response
  2. Display:
     ```
     Active orchestration found (ID: {id}, Wave {current_wave}/{total_waves}). Showing status.
     ```
  3. Prompt with: `[Show status / Start new anyway / Abort]`

  Wait for user response:

  - **Show status**: Display the full orchestration details from the response (ID, status, current wave, total waves, started_at, and any session summary available). Then STOP. Do not proceed to wave execution.
  - **Start new anyway**: Display `"Starting new orchestration (existing ID: {id} will continue independently)."` and proceed to Step 4.
  - **Abort**: Display `"Orchestration aborted."` and STOP.

---

## Step 4: Issue Retrieval and Filtering

Fetch actionable issues from the orchestrator API and filter to unstarted items.

### 4.1: Fetch issues

Run the following command via Bash tool:

```bash
curl -sf "${AOD_API_URL:-http://localhost:8000}/api/v1/projects/{project_id}/issues?state=open&sort=ice_desc" -H "X-AOD-Source: skill"
```

Replace `{project_id}` with the resolved project ID from Step 2.

If the API call fails, display:

```
ERROR: Failed to fetch issues for project {project_id}. Verify the API is running at ${AOD_API_URL:-http://localhost:8000}.
```

And STOP.

### 4.2: Filter to actionable issues

From the API response, include only issues where:
- `current_stage` is `null` (unstarted), OR
- `current_stage` is `"discover"`, OR
- `current_stage` is `"define"`

Exclude issues where:
- `current_stage` is `"plan"`, `"build"`, `"deliver"`, or `"done"`
- `is_done` is `true`
- `state` is `"closed"`

### 4.3: Apply --issues filter

If `selected_issues` is not empty (from Step 1.1):
1. Filter the actionable issues to include only those whose `issue_number` is in `selected_issues`
2. For each number in `selected_issues` that was NOT found in the actionable issues, display:
   ```
   Warning: Issue #{N} not found or not in an actionable stage.
   ```
3. If no valid issues remain after filtering, display "No actionable issues found for the specified issue numbers." and STOP.

### 4.4: Extract dependencies

For each actionable issue, extract `depends-on` relationships:

**From issue body** -- scan for pattern (case-insensitive): `depends-on:\s*#(\d+)`
Extract all matching issue numbers.

**From issue labels** -- scan for pattern: `depends-on:(\d+)`
Extract all matching issue numbers.

Combine both sources (deduplicate) into a `depends_on` list per issue.

### 4.5: Check for empty results

If no actionable issues remain after filtering, display:

```
No unstarted issues found. All issues are already in progress or completed.
```

And STOP.

### 4.6: Build issue list

For each actionable issue, compute:
- `ice_avg = ice_total / 3` (rounded to 1 decimal place)

Build a sorted list (by `ice_total` descending) of:
```
{issue_number, title, ice_total, ice_avg, depends_on[]}
```

Display the count of actionable issues found:
```
Found {N} actionable issue(s) for project {project_id}.
```

### 4.7: Resolve per-feature `deliver_flags` from blueprint

Some features require per-invocation flags for the downstream `/aod.deliver` step (e.g., autonomous `--no-tests=<reason>` opt-outs for features with non-automatable ACs). These flags are declared in the blueprint YAML generated by `/aod.blueprint` as a per-feature `deliver_flags` array (resolves spec FR-005 [NEEDS CLARIFICATION]; see plan Research R-1 and `specs/139-delivery-verified-not-documented/spec.md` US-3).

**Blueprint YAML shape** (canonical, per-feature):

```yaml
features:
  - number: 139
    name: delivery-verified-not-documented
    deliver_flags: ["--no-tests=exempt_while_e2e_infra_unstable"]
  - number: 140
    name: next-feature
    deliver_flags: []
```

**Resolution algorithm**:

1. Locate the blueprint file: `.aod/blueprint.yaml` or `.aod/blueprint.yml` (first match wins). If neither exists, skip flag resolution — all features default to `deliver_flags = []`.
2. For each actionable issue in the list (built in Step 4.6), look up the blueprint entry whose `number` matches the issue's `issue_number`. If no entry is found, default to `deliver_flags = []`.
3. Parse the entry's `deliver_flags` field:
   - If the field is absent or `null`: default to `[]` (no additional flags).
   - If the field is an array of strings: adopt as-is. Each string is passed verbatim as a single literal argument to `/aod.deliver` — no shell splitting, no substitution.
   - If the field exists but is not an array of strings: display a warning `"Warning: blueprint deliver_flags for #{issue_number} is malformed (expected array of strings); defaulting to []"` and continue with `[]`.
4. Attach the resolved `deliver_flags` to each issue record:

```
{issue_number, title, ice_total, ice_avg, depends_on[], deliver_flags[]}
```

**Validation boundary**: `/aod.orchestrate` does NOT validate flag contents. Invalid flag strings (e.g., reason below minimum length for `--no-tests`) are rejected downstream by `/aod.deliver`'s own flag parser (spec FR-001..FR-004). The orchestrator's role is pass-through only.

**Pass-through mechanism**: The resolved `deliver_flags` for each issue flow through to `/aod.deliver` via the Task record's `description` field (see Step 7.1.1 step 3 below). The Task record persists the `/aod.run` invocation with flags appended, and `/aod.run` forwards them to its Deliver stage (Stage 5) when invoking the `aod.deliver` skill.

---

## Step 5: Wave Planning Engine

Group actionable issues into sequential waves by ICE priority tier with dependency and concurrency constraints.

### 5.1: Assign priority tiers

For each issue, assign a priority tier based on `ice_avg`:
- **P0**: `ice_avg >= 7`
- **P1**: `4 <= ice_avg < 7`
- **P2**: `ice_avg < 4`

### 5.2: Group into waves by tier

Initial wave assignment:
- All P0 issues --> Wave 1
- All P1 issues --> Wave 2
- All P2 issues --> Wave 3

If a tier has no issues, skip that wave number (e.g., if no P0 issues, P1 starts at Wave 1).

### 5.3: Enforce dependency ordering

For each issue with `depends_on` entries:
1. Find the wave of each dependency
2. If the issue is in the same wave or an earlier wave than any dependency, bump it to the wave AFTER the dependency's wave
3. Repeat until no more bumps are needed (handle transitive dependencies)

### 5.4: Split oversized waves

For each wave that exceeds `max_concurrent_sessions` (default: 3):
1. Split into sub-waves: Wave 1a, Wave 1b, etc.
2. Each sub-wave contains at most `max_concurrent_sessions` issues
3. Preserve ICE score ordering within sub-waves (highest first)
4. Re-number waves sequentially (1a-->1, 1b-->2, etc.) after all splitting

### 5.5: Insert checkpoint markers

Insert checkpoint markers at tier boundaries:
- Between the last P0 wave and the first P1 wave: `"Checkpoint: P0 to P1 boundary"`
- Between the last P1 wave and the first P2 wave: `"Checkpoint: P1 to P2 boundary"`

If only one tier exists, no checkpoints are inserted.

### 5.6: Display formatted wave plan

Display the wave plan to the user:

```
Wave Plan:
  Wave 1 (P0): #{N} {title} (ICE {avg}), #{N} {title} (ICE {avg})
  -- Checkpoint: P0 to P1 boundary --
  Wave 2 (P1): #{N} {title} (ICE {avg}), #{N} {title} (ICE {avg})
  -- Checkpoint: P1 to P2 boundary --
  Wave 3 (P2): #{N} {title} (ICE {avg})

Total sessions: {count} across {wave_count} waves
```

---

## Step 6: Wave Plan Confirmation

After displaying the wave plan, prompt the user for confirmation.

### 6.1: Check skip conditions

- If `dry_run == true`: Display `"Dry run complete. No sessions spawned."` and STOP. Do NOT create Task records, spawn sessions, or write `.aod/wave-plan.md`.
- If `auto_confirm == true` (`--yes` flag): Display `"Auto-confirmed (--yes). Proceeding with execution."` and skip to Step 6.3.

### 6.2: Prompt for confirmation

Display:

```
Proceed? [Yes / Edit waves / Abort]
```

Wait for user response:

- **Yes** (or "y", "yes", "proceed", "continue"): Proceed to Step 6.3 (write audit file), then Step 7.
- **Edit waves**: Display: `"Manual wave editing is not yet supported. Please re-run with --issues to select specific issues, or confirm the current plan."` Then re-display the prompt.
- **Abort** (or "no", "n", "abort", "cancel"): Display `"Orchestration aborted."` and STOP.

### 6.3: Write wave plan audit file

After confirmation (or auto-confirm), write the wave plan to `.aod/wave-plan.md` for audit purposes. This write is non-fatal -- it must not block execution:

```bash
cat > .aod/wave-plan.md << 'WAVE_PLAN_EOF'
# Wave Plan

Generated: {current_date_time}
Project: {project_id}
Total issues: {count}

## Waves

### Wave {N} ({tier})
- #{issue_number} {title} (ICE {ice_total}, avg {ice_avg})
- ...

{checkpoint marker if applicable}

### Wave {N+1} ({tier})
- ...

## Summary
Total sessions: {count} across {wave_count} waves
Checkpoints: {checkpoint_count}
WAVE_PLAN_EOF
```

If the write fails, log a warning (`"Warning: Could not write .aod/wave-plan.md"`) but continue execution.

Proceed to Step 7.

---

## Step 6.5: State Persistence (Crash Recovery)

Persist orchestration state to `.aod/orchestrate-state.json` so the skill can resume after a crash or context overflow. This file is written after Task creation (Step 7.1.1) and updated after each wave completes.

### 6.5.1: Check for existing state

Run the following command via Bash tool:

```bash
cat .aod/orchestrate-state.json 2>/dev/null
```

If the file exists and contains valid JSON:
1. Parse the state: `project_id`, `issue_to_task`, `task_to_issue`, `wave_plan`, `current_wave_index`, `succeeded`, `failed`, `skipped`, `skipped_issues`, `batch_ids`, `start_time`
2. Display:
   ```
   Resuming orchestration from Wave {current_wave_index + 1} (project {project_id}).
   Previously: {succeeded} succeeded, {failed} failed, {skipped} skipped.
   ```
3. Prompt: `[Resume / Start fresh / Abort]`
   - **Resume**: Restore all state variables and skip to Step 7.1 at `current_wave_index`. Skip Steps 7.1.1 (task creation) for already-created waves.
   - **Start fresh**: Delete the state file and proceed normally from Step 7.
   - **Abort**: STOP.

If the file does not exist: proceed normally to Step 7.

### 6.5.2: State file format

The state file has this structure (written via Bash `cat > .aod/orchestrate-state.json`):

```json
{
  "project_id": 1,
  "start_time": 1711100000,
  "issue_to_task": {"1": 10, "2": 11},
  "task_to_issue": {"10": 1, "11": 2},
  "wave_plan": [{"wave_number": 1, "issues": [1, 2], "tier": "P0"}],
  "current_wave_index": 0,
  "succeeded": 0,
  "failed": 0,
  "skipped": 0,
  "skipped_issues": [],
  "batch_ids": []
}
```

### 6.5.3: Write state

After each state-changing operation (Task creation, batch spawn, wave completion), write the current state to `.aod/orchestrate-state.json` via Bash tool. Use a single `cat > .aod/orchestrate-state.json << 'EOF'` command with the full JSON. This write is non-fatal — if it fails, log a warning and continue.

### 6.5.4: Clean up state on completion

After Step 8 (Completion Reporter) finishes successfully, delete the state file:

```bash
rm -f .aod/orchestrate-state.json
```

---

## Step 7: Wave Execution

Execute waves sequentially. For each wave: create Task records, spawn a batch, and poll until completion.

Initialize an empty mapping: `issue_to_task = {}` (maps issue_number to task_id)
Initialize an empty mapping: `task_to_issue = {}` (maps task_id to issue_number)
Initialize an empty list: `all_batch_results = []`
Initialize counters: `succeeded = 0`, `failed = 0`, `skipped = 0`
Initialize an empty set: `skipped_issues = set()` (tracks skipped issue numbers for dependency propagation)

**After initializing these variables**, write the initial state file per Step 6.5.3.

### 7.1: Execute each wave

For each wave in the wave plan (in order):

#### 7.1.0: Pre-wave dependency check

Before processing this wave, check if any issues in the wave have been added to `skipped_issues` (from dependency propagation in a previous wave's failure handler, Step E):

- Remove any issues whose `issue_number` is in `skipped_issues` from this wave
- If all issues in the wave were removed, display: `"Wave {wave_number}: All issues skipped (dependency propagation). Advancing to next wave."` and skip to the next wave.

#### 7.1.1: Create Task records (Task Record Creator)

For each issue in the current wave:

1. Compute the task title:
   - Base: `/aod.run #{issue_number} -- {issue_title}`
   - If the total length exceeds 200 characters, truncate `issue_title`:
     ```
     prefix = "/aod.run #{issue_number} -- "
     max_title_chars = 200 - len(prefix)
     truncated_title = issue_title[:max_title_chars - 3] + "..."
     title = prefix + truncated_title
     ```
   - Otherwise: `title = prefix + issue_title`

2. Build the `depends_on` list: for each issue number in the issue's `depends_on`, look up the corresponding `task_id` from `issue_to_task`. If a dependency was not yet created (should not happen with wave ordering), omit it.

2.5. **Compose invocation with `deliver_flags` pass-through** (FR-005 resolution):

- Start with the base invocation: `invocation = "/aod.run #{issue_number}"`
- If the issue's `deliver_flags` array (resolved in Step 4.7) is non-empty, append `--deliver-flags` followed by each flag as a separate literal argument:
  ```
  invocation = "/aod.run #{issue_number} --deliver-flags {flag_1} {flag_2} ..."
  ```
- If `deliver_flags` is empty or absent, leave `invocation = "/aod.run #{issue_number}"` unchanged.
- Flags are passed verbatim — no shell-splitting, substitution, or quoting changes. Blueprint authors are responsible for supplying shell-metacharacter-free flag values (single-line, quoted at the source). `/aod.run` forwards the captured flags to `/aod.deliver` when invoking the Deliver-stage skill.

3. Create the Task record via API (note: `description` carries the composed invocation from step 2.5):

```bash
curl -sf -X POST "${AOD_API_URL:-http://localhost:8000}/api/v1/tasks" \
  -H "Content-Type: application/json" \
  -H "X-AOD-Source: skill" \
  -d '{
    "project_id": {project_id},
    "title": "{title}",
    "priority": "{P0|P1|P2}",
    "wave_number": {wave_number},
    "description": "{invocation}",
    "depends_on": [{task_ids}]
  }'
```

4. Parse the response to extract the `id` (task_id).
5. Store mapping: `issue_to_task[issue_number] = task_id`
6. Store reverse mapping: `task_to_issue[task_id] = issue_number`

Display: `"Created {N} task(s) for Wave {wave_number}."`

Write updated state per Step 6.5.3 (captures `issue_to_task` and `task_to_issue` mappings).

#### 7.1.2: Spawn batch

Construct the batch spawn request with one assignment per task in this wave:

```bash
curl -sf -X POST "${AOD_API_URL:-http://localhost:8000}/api/v1/projects/{project_id}/batches" \
  -H "Content-Type: application/json" \
  -H "X-AOD-Source: skill" \
  -d '{
    "assignments": [
      {"task_id": {task_id_1}, "agent_type": "claude"},
      {"task_id": {task_id_2}, "agent_type": "claude"}
    ]
  }'
```

Parse the response to extract:
- `batch.id` as `batch_id`
- `sessions[]` array -- store the `session_id` to `task_id` mapping from each entry

**Important (Architect warning)**: The `BatchDetailResponse` from the poll endpoint may lack `task_id` per session. Use the `session_id` to `task_id` mapping captured HERE from the spawn response for all subsequent status correlation.

Display: `"Wave {wave_number}: Spawned batch {batch_id} with {N} session(s)."`

If the batch spawn fails, display the error and STOP:
```
ERROR: Failed to spawn batch for Wave {wave_number}. API response: {error}
```

#### 7.1.3: Poll batch status

**IMPORTANT**: Do NOT poll with individual `sleep` + `curl` tool calls — this burns through context with dozens of identical tool calls. Instead, run a **single Bash command** that loops internally and only returns when a terminal status is reached or the timeout expires.

Run the following as a **single Bash tool call** with `timeout: 600000` (10 minutes). Replace `{project_id}` and `{batch_id}` with actual values:

```bash
API="${AOD_API_URL:-http://localhost:8000}"
BATCH_URL="${API}/api/v1/projects/{project_id}/batches/{batch_id}"
TIMEOUT=1800  # 30 minute max
INTERVAL=30   # poll every 30 seconds
ELAPSED=0

while [ $ELAPSED -lt $TIMEOUT ]; do
  RESP=$(curl -sf "$BATCH_URL" -H "X-AOD-Source: skill" 2>/dev/null)
  STATUS=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))" 2>/dev/null)

  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "partial_failure" ] || [ "$STATUS" = "failed" ]; then
    echo "$RESP"
    exit 0
  fi

  # Progress line (shown in tool output)
  PROGRESS=$(echo "$RESP" | python3 -c "
import sys,json
d=json.load(sys.stdin).get('progress',{})
print(f\"{d.get('completed',0)}/{d.get('total','?')} complete, {d.get('running',0)} running ({int($ELAPSED/60)}m elapsed)\")
" 2>/dev/null)
  echo "Wave {wave_number}: $PROGRESS"

  sleep $INTERVAL
  ELAPSED=$((ELAPSED + INTERVAL))
done

echo '{"status":"timeout","error":"Polling timed out after 30 minutes"}'
exit 1
```

After the command returns:
1. Parse the final JSON response
2. If `status` is `"timeout"`: Display `"Wave {wave_number}: Polling timed out after 30 minutes. Check the dashboard or run /aod.orchestrate to resume."` and STOP.
3. Otherwise, proceed to Step 7.1.4 with the terminal status.

#### 7.1.4: Handle terminal status

**On "completed"**:
- Increment `succeeded` by the number of sessions in this wave
- Store batch result in `all_batch_results`
- **Run Step G (halt-record inspection) below** — even fully-completed batches may contain Deliver-stage halts (sessions that exited 10 at the Deliver stage without causing batch-level partial failure)
- Increment `current_wave_index` and write updated state per Step 6.5.3
- Display: `"Wave {wave_number} completed successfully."`
- If a checkpoint marker follows this wave, proceed to checkpoint handling (see 7.2)
- Otherwise, proceed to the next wave

**On "partial_failure"**:

Handle partial failures with circuit breaker, per-issue retry/skip/abort, and dependency propagation.

**Step A: Identify failed sessions**

From the batch detail response (the final poll result), examine the `sessions[]` array. For each session:
1. Use the `session_id` to look up the `task_id` from the mapping captured during batch spawn (Step 7.1.2)
2. Use `task_to_issue[task_id]` to resolve back to the `issue_number`
3. Classify each session as succeeded or failed based on its `status` field
4. For failed sessions, extract `current_stage` and `output_summary` (or `error`) from the session object

Build two lists:
- `wave_succeeded`: list of issue numbers whose sessions completed successfully
- `wave_failed`: list of `{issue_number, title, current_stage, output_summary}` for failed sessions

Increment `succeeded` by the count of `wave_succeeded`.

**Step B: Circuit breaker check**

Before prompting for per-issue actions, check if the failure rate exceeds 50%:

1. Compute `failure_rate = len(wave_failed) / (len(wave_succeeded) + len(wave_failed))`
2. If `failure_rate > 0.5` (more than 50% failed):

   Display:
   ```
   CIRCUIT BREAKER: >50% of Wave {wave_number} sessions failed ({len(wave_failed)}/{len(wave_succeeded) + len(wave_failed)}).
   Pausing orchestration.

   Failed issues:
   - #{issue_number} {title}: {current_stage}
   - #{issue_number} {title}: {current_stage}
   ...

   [Continue anyway / Abort]
   ```

   Wait for user response:
   - **Continue anyway**: Proceed to Step C (per-issue failure prompts)
   - **Abort**: Increment `failed` by the count of `wave_failed`. Display partial completion summary (use Step 8 completion reporter) and STOP.

3. If `failure_rate <= 0.5`: Proceed directly to Step C.

**Step C: Per-issue failure prompts**

For each failed issue in `wave_failed`, display the failure details and prompt:

```
Issue #{issue_number} ({title}) failed at stage {current_stage}: {output_summary}

[Retry / Skip / Abort all]
```

Wait for user response:

- **Retry**: Execute the retry flow (Step D)
- **Skip**: Execute the skip flow (Step E)
- **Abort all**: Increment `failed` by the count of remaining unhandled failures. Display partial completion summary (use Step 8 completion reporter) and STOP.

**Step D: Retry logic**

When the user chooses "Retry" for a failed issue:

1. Create a new Task record for the failed issue:

```bash
curl -sf -X POST "${AOD_API_URL:-http://localhost:8000}/api/v1/tasks" \
  -H "Content-Type: application/json" \
  -H "X-AOD-Source: skill" \
  -d '{
    "project_id": {project_id},
    "title": "/aod.run #{issue_number} -- {title} (retry)",
    "priority": "{priority}",
    "wave_number": {wave_number},
    "description": "/aod.run #{issue_number}",
    "depends_on": []
  }'
```

2. Extract the new `task_id` from the response. Update mappings:
   - `issue_to_task[issue_number] = new_task_id`
   - `task_to_issue[new_task_id] = issue_number`

3. Spawn a single-session batch:

```bash
curl -sf -X POST "${AOD_API_URL:-http://localhost:8000}/api/v1/projects/{project_id}/batches" \
  -H "Content-Type: application/json" \
  -H "X-AOD-Source: skill" \
  -d '{
    "assignments": [
      {"task_id": {new_task_id}, "agent_type": "claude"}
    ]
  }'
```

4. Store the `session_id` to `task_id` mapping from the spawn response.

5. Poll the batch status using the same single-Bash-loop approach from Step 7.1.3 until terminal.

6. Evaluate result:
   - If `completed`: Increment `succeeded` by 1. Display `"Issue #{issue_number} retry succeeded."`. Continue to next failed issue.
   - If `failed` or `partial_failure`: Display `"Issue #{issue_number} retry also failed."` Re-prompt with `[Retry again / Skip / Abort all]`.

**Step E: Skip and dependency propagation**

When the user chooses "Skip" for a failed issue:

1. Increment `skipped` by 1.
2. Display: `"Skipped Issue #{issue_number} ({title})."`
3. Store the skipped issue number in a `skipped_issues` set.

4. **Dependency propagation**: Scan ALL remaining waves (waves not yet executed) for issues whose `depends_on` list contains the skipped issue number:
   - For each dependent issue found:
     a. Remove the issue from its wave
     b. Increment `skipped` by 1
     c. Display: `"Skipped: Issue #{dependent_number} ({dependent_title}) depends on #{issue_number} which was skipped"`
     d. Add the dependent issue number to `skipped_issues`
   - Repeat propagation: check if any other issues depend on newly skipped issues (transitive propagation)
   - Independent issues in later waves are unaffected and proceed normally

5. Continue to next failed issue (or next wave if all failures handled).

**Step F: Wave completion after failure handling**

After all failed issues in the wave have been handled (retried, skipped, or aborted):
- Store batch result in `all_batch_results`
- Proceed to Step G (halt-record inspection) before wave completion
- If a checkpoint marker follows this wave, proceed to checkpoint handling (Step 7.2)
- Otherwise, proceed to the next wave

**Step G: Deliver-stage halt record inspection (FR-024, FR-025)**

After terminal status handling, inspect each completed session for a `/aod.deliver` halt record. The Deliver stage of `/aod.run` invokes `/aod.deliver`, which writes a structured halt record to `.aod/state/deliver-{NNN}.halt.json` when it halts for review (exit code 10 per the three-channel halt protocol). The halt-record schema and exit-code taxonomy are documented in [`specs/139-delivery-verified-not-documented/contracts/halt-record.md`](../../../specs/139-delivery-verified-not-documented/contracts/halt-record.md).

**Exit-code taxonomy** (from halt-record contract §Channel 3):

| Code | Meaning | Orchestrator policy |
|------|---------|--------------------|
| 0 | Success | Proceed to next feature |
| 10 | Halted for review (E2E fail, AC-coverage fail, or abandoned heal) | Halt wave; route feature to review queue (add `requires-review` label); other wave features may still succeed |
| 11 | Lockfile conflict (concurrent `/aod.deliver` live) | Retry with exponential backoff (max 3 retries: 30s, 90s, 270s); if still conflicting, skip feature with warning and mark as `skipped` |
| 12 | Abandoned heal sentinel (crash-recovery) | Halt wave for this feature; do NOT proceed with automatic retry; add `requires-review` label and emit manual-cleanup prompt |
| 1-9 | Pre-existing delivery errors | Handle per existing Step C-E partial-failure logic (Retry/Skip/Abort) |

**Inspection algorithm** — for each issue in the current wave (succeeded and failed):

1. Derive the halt-record path from the issue number: `halt_record_path = ".aod/state/deliver-{NNN}.halt.json"` where `NNN` is the 3-digit zero-padded `issue_number`.
2. Check file existence via Bash: `test -f "$halt_record_path" && echo EXISTS`
3. If the halt-record file exists, parse it via `jq`:

   ```bash
   jq -r '[.reason, .recovery_status, (.heal_pr_url // "null"), (.failing_scenarios | tostring)] | @tsv' "$halt_record_path"
   ```

4. Extract fields: `reason`, `recovery_status`, `heal_pr_url`, `failing_scenarios`.
5. Log a structured summary to the skill's output:

   ```
   Halt detected: #{issue_number} — reason={reason}, recovery_status={recovery_status}
     Heal-PR: {heal_pr_url or "unavailable"}
     Failing scenarios: {failing_scenarios list}
   ```

6. **Route to review queue**: Add the `requires-review` GitHub label to the feature's issue:

   ```bash
   gh issue edit {issue_number} --add-label requires-review
   ```

   If `gh` is unavailable, log a warning and continue — the halt record is still persisted on disk for downstream tooling.

7. **Capture halt in wave-results**: Extend the per-session result in `all_batch_results` with a `halt_record` object containing `{reason, recovery_status, heal_pr_url, failing_scenarios}`. Increment a `halted` counter distinct from `failed`.

8. **Exit-code policy enforcement**:

   - **Code 10 (halt)**: The current wave completes for the non-halted features (do not interrupt other running sessions), but the halted feature is NOT retried. Dependents of the halted feature are added to `skipped_issues` for propagation via Step E.
   - **Code 11 (lockfile conflict)**: If the Deliver-stage session surfaces exit 11, attempt up to 3 retries with exponential backoff (30s, 90s, 270s). If all retries conflict, mark the feature as `skipped` with a warning and propagate to dependents.
   - **Code 12 (abandoned heal)**: Halt the feature's lifecycle; do NOT auto-retry. Add `requires-review` label and emit a manual-cleanup prompt identical to the halt-record's message. Propagate to dependents.

9. Other features in the wave that succeeded cleanly (no halt record present) continue to completion normally. Only the halted features are routed to the review queue.

After all halt records are processed, continue to checkpoint handling (Step 7.2) or the next wave.

**On "failed"**:
- Increment `failed` by the number of sessions in this wave
- Display:
  ```
  Wave {wave_number}: All sessions failed.
  ```
- Display: `"Retry with: /aod.orchestrate --issues {issue_numbers_in_wave}"`
- STOP execution (do not proceed to next waves)

### 7.2: Governance Checkpoints

When a checkpoint marker is reached between waves (at P0 to P1 or P1 to P2 tier boundaries):

**Step A: Collect wave results**

For each batch that ran in the waves of the tier that just completed, query the batch detail to get per-session results:

```bash
curl -sf "${AOD_API_URL:-http://localhost:8000}/api/v1/projects/{project_id}/batches/{batch_id}" \
  -H "X-AOD-Source: skill"
```

For each session in the batch response:
1. Use the `session_id` to look up the `task_id` from the spawn mapping (Step 7.1.2)
2. Use `task_to_issue[task_id]` to resolve the `issue_number`
3. Extract `status` (succeeded/failed), `current_stage`, and `pr_url` from the session

**Step B: Display structured checkpoint summary**

Display a structured checkpoint summary table:

```
-- Checkpoint: {tier_a} to {tier_b} boundary --

Wave {N} Results:
| Issue | Status | Stage | PR |
|-------|--------|-------|----|
| #{issue_number} {title} | Succeeded | deliver | #{pr_number} |
| #{issue_number} {title} | Failed | build | -- |
...

{If multiple waves in the tier, repeat the table per wave}

Sessions: {total_succeeded}/{total_sessions} succeeded
```

Where:
- `Status` is "Succeeded" or "Failed"
- `Stage` is the `current_stage` value from the session
- `PR` is the PR number extracted from `pr_url` (e.g., `#51`), or `--` if no PR was created

**Step C: Prompt for action**

Display:

```
[Continue / Review on dashboard / Abort]
```

Wait for user response:

- **Continue** (or "c", "continue", "yes", "proceed"): Proceed to the next wave.
- **Review on dashboard**: Display the dashboard URL: `"${AOD_API_URL:-http://localhost:8000}/dashboard/projects/{project_id}"`. Then re-display the prompt: `[Continue / Review on dashboard / Abort]`.
- **Abort** (or "abort", "stop", "cancel"): Display partial completion summary showing what completed so far (invoke Step 8 completion reporter with current counters) and STOP.

**Note**: Single-tier orchestrations have no checkpoint markers inserted (per Step 5.5), so this section is automatically skipped.

---

## Step 8: Completion Reporter

Display the final orchestration summary after all waves complete (or execution stops).

### 8.1: Calculate duration

Run the following command via Bash tool:

```bash
date +%s
```

Compute `duration = end_time - start_time` (from Step 0).

Format duration as:
- If < 60 seconds: `"{N}s"`
- If < 3600 seconds: `"{M}m {S}s"`
- If >= 3600 seconds: `"{H}h {M}m"`

### 8.2: Collect PR links

From the batch detail responses stored in `all_batch_results`, extract `pr_url` fields from each session. Collect all non-null PR URLs.

To get session details with PR URLs, query each batch:

```bash
curl -sf "${AOD_API_URL:-http://localhost:8000}/api/v1/projects/{project_id}/batches/{batch_id}" \
  -H "X-AOD-Source: skill"
```

Parse `sessions[]` and collect any `pr_url` values.

### 8.3: Display completion summary

```
Orchestration Complete

Total: {total_issues} features
Succeeded: {succeeded}
Failed: {failed}
Skipped: {skipped}
Duration: {formatted_duration}

{if PR links exist:}
PRs created: {comma-separated PR URLs or numbers}

{if failed > 0:}
Failed issues: {list of failed issue numbers with titles}
Retry failed: /aod.orchestrate --issues {failed_issue_numbers}

{if skipped > 0:}
Skipped issues: {list of skipped issue numbers with reasons}
```

---

## Quality Checklist

- [ ] All API calls use `${AOD_API_URL:-http://localhost:8000}` base URL
- [ ] All curl calls include `-H "X-AOD-Source: skill"` header
- [ ] All curl calls use `-sf` flags (silent + fail on HTTP errors)
- [ ] Project auto-detection handles stale config (404 --> git remote fallback)
- [ ] Issue filtering excludes in-progress and completed issues
- [ ] Wave planning respects dependency ordering
- [ ] Wave splitting enforces max_concurrent_sessions limit
- [ ] Task titles truncated to 200 characters
- [ ] Task creation in wave order for depends_on ID resolution
- [ ] Batch spawn response session_id mapping stored for status correlation
- [ ] Polling uses a single Bash loop (NOT individual sleep+curl tool calls) with 30s interval and 30m timeout
- [ ] --dry-run exits after wave plan display without side effects (no wave-plan.md written)
- [ ] --yes skips confirmation prompt
- [ ] --issues filters to specified issue numbers
- [ ] Duration calculated from start_time captured in Step 0
- [ ] Wave plan audit file written to .aod/wave-plan.md AFTER dry-run check (Step 6.3)
- [ ] Idempotent launch check queries orchestration status before issue retrieval (Step 3)
- [ ] Governance checkpoints display structured summary tables at tier boundaries (Step 7.2)
- [ ] Circuit breaker triggers when >50% of wave sessions fail (Step 7.1.4 partial_failure Step B)
- [ ] Per-issue failure prompts offer Retry / Skip / Abort all (Step 7.1.4 partial_failure Step C)
- [ ] Retry creates new Task record and spawns single-session batch (Step 7.1.4 partial_failure Step D)
- [ ] Skip propagates to dependent issues in later waves (Step 7.1.4 partial_failure Step E)
- [ ] Pre-wave dependency check removes skipped issues before execution (Step 7.1.0)
- [ ] State file `.aod/orchestrate-state.json` written after task creation and each wave completion (Step 6.5.3)
- [ ] State file checked on startup for crash recovery (Step 6.5.1)
- [ ] State file deleted on successful completion (Step 6.5.4)
- [ ] Per-feature `deliver_flags` resolved from blueprint YAML (Step 4.7) and passed verbatim into Task record `description` via `/aod.run ... --deliver-flags ...` (Step 7.1.1 step 2.5) — resolves spec FR-005
- [ ] Deliver-stage halt records inspected after every wave (Step G, both completed and partial_failure paths): exit 10 routes to review queue with `requires-review` label, exit 11 retries with backoff, exit 12 halts with manual-cleanup prompt (see `contracts/halt-record.md`)
- [ ] Halt-record failing features do NOT block other features in the wave; dependents propagate via `skipped_issues` like skip semantics
