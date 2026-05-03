# Dry-Run Entry Reference (v030)
<!-- Loaded via Read tool — do not inline into core SKILL.md -->

This reference contains the complete dry-run entry handler for the AOD lifecycle orchestrator. When `DryRun == true` is received from the command file, this handler performs **read-only detection and planning**, then displays a preview of what the orchestrator would do — without executing any stages, writing state, creating branches, or updating GitHub labels.

## Dry-Run Entry

**Algorithm overview**:
1. Parse the DryRun context (extract sub-mode) — step (a)
2. Run detection phase for the sub-mode (read-only) — step (b)
3. Build planned execution sequence — step (c)
4. Build governance gate predictions — step (d)
5. Build artifact predictions — step (e)
6. Handle edge cases (inline in step b, see reference) — step (f)
7. Display preview output — step (g)
8. Exit immediately — step (h)

**Sub-mode dispatch**: The original `Mode` value determines which detection logic to run:

| Sub-mode | Detection Logic | Reference |
|----------|----------------|-----------|
| `issue` | Issue Entry steps 1, 3-8 (read-only, skipping step 2 and 9+) | See `references/entry-modes.md` Issue Entry |
| `idea` | New Idea Entry steps 2-3 (read-only) | See `references/entry-modes.md` New Idea Entry |
| `resume` | Resume Entry steps 1-3 (read-only) | See `references/entry-modes.md` Resume Entry |

---

### Step (a): Parse DryRun Context

Extract from the invocation context:
- `DryRun`: Confirm `true`
- `Mode`: The underlying mode — `idea`, `issue`, or `resume`
- `Issue`: The issue number (if mode is `issue`)
- `Idea`: The idea text (if mode is `idea`)

Store these as the working variables for subsequent steps.

---

### Step (b): Run Detection Phase (Issue Sub-mode)

When sub-mode is `issue`, run the **same detection logic as Issue Entry steps 1, 3-8** (read-only, skipping step 2 and steps 9+) but suppress all write operations. Specifically:

1. **Parse issue number**: Extract the numeric issue number from `Issue` (strip `#` prefix if present).

2. **Read GitHub Issue** (read-only): Use Bash to fetch issue data:
   ```
   gh issue view {NNN} --json number,title,labels
   ```
   - Extract `number`, `title`, and `labels` array
   - If `gh` is unavailable: display `"GitHub CLI unavailable. Stage detection based on artifact scan only."` and fall back to artifact-only detection — skip steps 3-4 (label/stage inference), proceed directly to step 5 (artifact scan) to classify stages from disk. Set `feature_name` to `"unknown"`. See [Edge Case: gh CLI Unavailable](#edge-case-gh-cli-unavailable-issue-sub-mode) for full procedure.
   - If issue not found (gh returns error): display `"Issue #{NNN} not found on GitHub."` and **EXIT immediately** (do not proceed to steps c-h, do not create state). See [Edge Case: GitHub Issue Not Found](#edge-case-github-issue-not-found-issue-sub-mode).

3. **Extract stage label**: Search the labels array for `stage:*`:
   - Map to current stage using the same table as Issue Entry step 4
   - `stage:done` → display "Lifecycle already complete" and EXIT
   - No `stage:*` label → default to `discover`

4. **Infer completed stages**: Using the same table as Issue Entry step 5, mark prior stages as completed based on the detected label.

5. **Discover existing artifacts**: Scan disk using the Artifact Discovery algorithm (Glob only — read-only). See `references/entry-modes.md` for the Artifact Discovery section.

6. **Read governance tier**: Read `.aod/memory/constitution.md`, extract `governance:` → `tier:` value. Default to `standard` if not found.

7. **Generate feature metadata** (in-memory only — NOT written to disk):
   - `feature_id`: Zero-pad issue number to 3 digits
   - `feature_name`: Convert issue title to kebab-case
   - `branch`: `{feature_id}-{feature_name}`
   - `github_issue`: The issue number

**What is NOT done** (mutations suppressed):
- Do NOT create or write `.aod/run-state.json`
- Do NOT create or switch git branches
- Do NOT update GitHub Issue labels
- Do NOT run `backlog-regenerate.sh`
- Do NOT invoke any stage skills

---

### Step (b): Run Detection Phase (Idea Sub-mode)

When sub-mode is `idea`, run the **same detection logic as New Idea Entry steps 2-3** but suppress all write operations. Since an idea starts from scratch, all stages will execute.

1. **Read governance tier**: Read `.aod/memory/constitution.md`, extract `governance:` → `tier:` value. Default to `standard` if not found.

2. **Generate feature metadata** (in-memory only — NOT written to disk):
   - `feature_name`: Convert idea text to kebab-case (lowercase, spaces to hyphens, strip non-alphanumeric except hyphens, truncate to 50 chars)
   - `feature_id`: `"000"` (not yet assigned — would be assigned after Discover creates a GitHub Issue)
   - `branch`: `"pending"` (not yet assigned)
   - `github_issue`: null
   - `idea`: The full idea text as provided

3. **Mark all stages as pending**: No stages are completed, no artifacts exist. All 7 stage/substage entries will be classified as `EXECUTE` in step (c).

**What is NOT done** (mutations suppressed):
- Do NOT check for existing state file (irrelevant for preview)
- Do NOT create `.aod/run-state.json`
- Do NOT create git branches
- Do NOT invoke any stage skills

---

### Step (b): Run Detection Phase (Resume Sub-mode)

When sub-mode is `resume`, run the **same detection logic as Resume Entry steps 1-3** but suppress all write operations. Read state to determine remaining stages.

1. **Check for state file**: Use Bash to run `bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_exists && echo "exists" || echo "none"'`
   - If state file does NOT exist: display error and exit (see [No State File Error](#no-state-file-error) below)

2. **Validate state file**: Use Bash to run `bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_validate'`
   - If validation fails: display `"State file corrupted. In a real run, recovery would be offered."` along with the validation error output, then **EXIT immediately** (do not perform recovery — that would be a mutation). See [Edge Case: Corrupted State File](#edge-case-corrupted-state-file-resume-sub-mode).

3. **Read full state** (read-only): Use Bash to run `bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_read'`. Parse the JSON to extract:
   - `feature_id`, `feature_name`, `github_issue`, `branch`
   - `current_stage`, `current_substage`
   - `session_count`, `updated_at`
   - All stage statuses from `stages` map

4. **Read governance tier**: Read `.aod/memory/constitution.md`, extract `governance:` → `tier:` value. Default to `standard` if not found.

5. **Classify stages from state**: For each stage in the `stages` map:
   - If `status == "completed"` → mark as `SKIP (already completed)` for step (c)
   - If `status == "in_progress"` → mark as `EXECUTE` (will re-execute from beginning)
   - If `status == "pending"` → mark as `EXECUTE`
   - For Plan substages: check each substage's status individually

6. **Check staleness** (read-only): Use Bash to run `bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_is_stale && echo "STALE" || echo "FRESH"'`
   - If `STALE`: Read `updated_at` from state, calculate age in days. Store staleness warning for display in step (g):
     ```
     WARNING: Orchestration state is {N} days old (last updated: {updated_at}).
     In a real resume, you would be prompted to confirm or start fresh.
     ```
   - If `FRESH`: No staleness warning needed.

**What is NOT done** (mutations suppressed):
- Do NOT increment `session_count`
- Do NOT update `governance_tier` in the state file
- Do NOT validate artifact consistency (would trigger user prompts)
- Do NOT validate GitHub label (would trigger user prompts)
- Do NOT ensure correct branch
- Do NOT modify `.aod/run-state.json` in any way
- Do NOT invoke any stage skills

---

#### No State File Error

If the state file does not exist when sub-mode is `resume`:

Display:
```
No active orchestration found.

No state file exists at .aod/run-state.json.
There is nothing to resume.

To start a new orchestration:
  /aod.run "your feature idea"
  /aod.run #NNN  (from existing GitHub Issue)
```

Then **EXIT immediately**. Do NOT create a state file.

---

### Step (c): Build Planned Execution Sequence

For each stage in the lifecycle sequence, classify its predicted action:

| Stage | Substage | Classification Logic |
|-------|----------|---------------------|
| Discover | — | If inferred completed → `SKIP (already completed)`. Else → `EXECUTE` |
| Define | — | If inferred completed → `SKIP (already completed)`. Else if PRD artifact found → `SKIP (artifact found)`. Else → `EXECUTE` |
| Plan | spec | If inferred completed → `SKIP (already completed)`. Else if spec.md found → `SKIP (artifact found)`. Else → `EXECUTE` |
| Plan | project_plan | If inferred completed → `SKIP (already completed)`. Else if plan.md found → `SKIP (artifact found)`. Else → `EXECUTE` |
| Plan | tasks | If inferred completed → `SKIP (already completed)`. Else if tasks.md found → `SKIP (artifact found)`. Else → `EXECUTE` |
| Build | — | If inferred completed → `SKIP (already completed)`. Else → `EXECUTE` |
| Deliver | — | If inferred completed → `SKIP (already completed)`. Else → `EXECUTE` |

**Priority**: Stage label inference takes precedence over artifact scan. If the GitHub label says `stage:build` (meaning discover, define, plan are complete), those stages are `SKIP (already completed)` even if some artifacts are missing.

Store the classification for each stage/substage as a list for display in step (g).

---

### Step (d): Build Governance Gate Predictions

For each stage classified as `EXECUTE` in step (c), determine its governance gate based on the tier read in step (b):

**Use the Governance Tier table** from `references/governance.md`:

| Stage | Light Tier | Standard Tier | Full Tier |
|-------|-----------|---------------|-----------|
| Discover | SKIP | Implicit (discover flow) | Check |
| Define | SKIP | Check Triad review | Check |
| Plan: spec | SKIP (PM not required) | PM sign-off | PM sign-off (separate) |
| Plan: project_plan | Dual sign-off (PM + Architect) | Dual sign-off (PM + Architect) | Dual sign-off (PM + Architect) |
| Plan: tasks | Triple sign-off (PM + Architect + Team-Lead) | Triple sign-off (PM + Architect + Team-Lead) | Triple sign-off (PM + Architect + Team-Lead) |
| Build | Internal (aod.build checkpoints) | Internal (aod.build checkpoints) | Internal (aod.build checkpoints) |
| Deliver | Internal (aod.deliver DoD) | Internal (aod.deliver DoD) | Internal (aod.deliver DoD) |

For stages classified as `SKIP`, the gate is not applicable — display `—` (dash).

Store the gate prediction for each stage for display in step (g).

---

### Step (e): Build Artifact Predictions

For each stage classified as `EXECUTE` in step (c), list the expected artifact paths based on the patterns from Post-Stage Context Extraction (in core SKILL.md):

| Stage | Substage | Expected Artifact Pattern |
|-------|----------|--------------------------|
| Discover | — | GitHub Issue (URL) |
| Define | — | `docs/product/02_PRD/{NNN}-*.md` |
| Plan | spec | `specs/{NNN}-*/spec.md` |
| Plan | project_plan | `specs/{NNN}-*/plan.md` |
| Plan | tasks | `specs/{NNN}-*/tasks.md`, `specs/{NNN}-*/agent-assignments.md` |
| Build | — | Implementation files (tracked via tasks.md) |
| Deliver | — | Delivery summary, archived state |

Replace `{NNN}` with the actual `feature_id` from step (b).

For stages classified as `SKIP`, show the found artifact path (if any) instead of the expected pattern.

Store the artifact predictions for display in step (g).

---

### Step (f): Edge Case Handling

Edge cases are handled inline during the detection phase (step b) for each sub-mode. See [Dry-Run Edge Cases](#dry-run-edge-cases) for the consolidated reference.

---

### Step (g): Display Preview Output

Format and display the complete dry-run preview using the template below. All data comes from steps (a) through (e).

```
AOD ORCHESTRATOR — Dry-Run Preview
====================================
Mode: {issue | idea | resume}
{Mode-specific context — see below}

Governance Tier: {light | standard | full}
Source: {.aod/memory/constitution.md | default}

--- Entry Detection ---
{Entry detection details — see below}

--- Artifact Scan ---
{Found artifacts from disk scan, or "No artifacts scanned (idea mode)"}

--- Planned Execution ---

  Stage 1: Discover         {EXECUTE | SKIP (reason)}
    Gate: {gate description | — (skipped)}
    Artifacts: {expected paths | found paths}

  Stage 2: Define           {EXECUTE | SKIP (reason)}
    Gate: {gate description | — (skipped)}
    Artifacts: {expected paths | found paths}

  Stage 3a: Plan (spec)     {EXECUTE | SKIP (reason)}
    Gate: {gate description | — (skipped)}
    Artifacts: {expected paths | found paths}

  Stage 3b: Plan (plan)     {EXECUTE | SKIP (reason)}
    Gate: {gate description | — (skipped)}
    Artifacts: {expected paths | found paths}

  Stage 3c: Plan (tasks)    {EXECUTE | SKIP (reason)}
    Gate: {gate description | — (skipped)}
    Artifacts: {expected paths | found paths}

  Stage 4: Build            {EXECUTE | SKIP (reason)}
    Gate: {gate description | — (skipped)}
    Artifacts: {expected paths | found paths}

  Stage 5: Deliver          {EXECUTE | SKIP (reason)}
    Gate: {gate description | — (skipped)}
    Artifacts: {expected paths | found paths}

  Stage 6: Document         {EXECUTE | SKIP (reason)}
    Gate: {gate description | — (skipped)}
    Artifacts: {expected paths | found paths}

--- Summary ---
  Stages to execute: {N of 7}
  Stages to skip: {N of 7}
  Governance gates: {N active}
  Expected artifacts: {N}

NOTE: This is a preview only. No files were created or modified.
To execute: /aod.run {original args without --dry-run}
```

**Mode-specific context** (varies by sub-mode):

- **Issue mode**:
  ```
  Issue: #{NNN} — {title}
  Branch: {feature_id}-{feature_name}
  Detected Label: stage:{label} (or "none")
  Starting Stage: {inferred starting stage}
  ```

- **Idea mode**:
  ```
  Idea: "{idea text}"
  Branch: pending (assigned after Discover)
  Starting Stage: Discover (all stages will execute)
  ```

- **Resume mode**:
  ```
  Feature: {feature_name} (#{github_issue})
  Branch: {branch}
  Session: {session_count} (would become {session_count + 1})
  Current Stage: {current_stage}
  Last Updated: {updated_at}
  ```

**Entry detection details** (varies by sub-mode):

- **Issue mode**: Show the GitHub Issue labels, the inferred stage, and the completed stages list
- **Idea mode**: Show `"New idea — no prior state. Full lifecycle will execute."`
- **Resume mode**: Show the state file summary (stages completed, current stage, session count)

---

### Step (h): Exit Immediately

After displaying the preview output in step (g):

**STOP.** Do NOT:
- Enter the Core State Machine Loop
- Write `.aod/run-state.json`
- Create or switch git branches
- Update GitHub Issue labels
- Invoke any stage skills (no Skill tool calls)
- Run `backlog-regenerate.sh`
- Modify any files on disk

The dry-run is complete. The user now has the information needed to decide whether to run the full orchestration.

---

### Dry-Run Edge Cases

These edge cases are handled inline during the detection phase (step b) but are documented here as a consolidated reference.

#### Edge Case: `gh` CLI Unavailable (Issue Sub-mode)

When `gh` is not installed or not authenticated during `--dry-run #NNN`:

1. Display: `"GitHub CLI unavailable. Stage detection based on artifact scan only."`
2. Skip GitHub Issue reading entirely (no labels, no title)
3. Fall back to **artifact-only detection**:
   - Run the Artifact Discovery algorithm via Glob (see `references/entry-modes.md`)
   - Infer stage from found artifacts (e.g., if spec.md exists, Plan:spec is complete)
   - Set `feature_id` from the issue number, `feature_name` to `"unknown"`, `github_issue` to the provided number
4. Continue to steps (c) through (h) normally with the artifact-based classifications
5. In the preview output, show `"Detected Label: unavailable (gh CLI not found)"` in the mode-specific context

This is handled inline in Step (b): Issue Sub-mode item 2.

#### Edge Case: GitHub Issue Not Found (Issue Sub-mode)

When `gh issue view {NNN}` returns a "not found" error during `--dry-run #NNN`:

1. Display: `"Issue #{NNN} not found on GitHub."`
2. **EXIT immediately** — do not proceed to steps (c) through (h)
3. Do NOT create any state file or branch

This is handled inline in Step (b): Issue Sub-mode item 2.

#### Edge Case: Corrupted State File (Resume Sub-mode)

When `aod_state_validate` fails during `--dry-run --resume`:

1. Display: `"State file corrupted. In a real run, recovery would be offered."`
2. Optionally display the validation error details from `aod_state_validate` output
3. **EXIT immediately** — do not proceed to steps (c) through (h)
4. Do NOT perform recovery, delete the state file, or create a new one

This is handled inline in Step (b): Resume Sub-mode item 2.
