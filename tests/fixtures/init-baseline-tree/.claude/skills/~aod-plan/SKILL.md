---
name: ~aod-plan
description: "Plan stage orchestrator that runs all three Plan sub-steps (spec → project-plan → tasks) in sequence with governance gates. Stops on rejection, continues through approvals. Use this skill when you need to run the full Plan stage, navigate planning sub-steps, or resume after a rejection."
---

# Plan Stage Orchestrator Skill

## Purpose

Orchestrates the full Plan stage by running spec → project-plan → tasks in sequence. After each sub-step completes and its governance review passes (APPROVED), the orchestrator automatically advances to the next sub-step. If any review returns CHANGES_REQUESTED or BLOCKED, the orchestrator stops and reports the rejection so the user can fix and re-run `/aod.plan` to resume.

With 1M context, all three artifacts and their reviews fit comfortably in a single session.

## How It Works

### Step 1: Determine Feature Context

1. Get branch: `git branch --show-current` → extract NNN prefix
2. If on `main` and a PRD exists (e.g., `docs/product/02_PRD/{NNN}-*.md`), **automatically create the feature branch** (`git checkout -b {NNN}-{kebab-name}`) per git workflow rules. Do NOT ask the user — feature branches are mandatory, not optional.
3. **Open Draft PR**: After creating the branch, push it and open a draft PR so work is visible early:
   ```bash
   git commit --allow-empty -m "chore({NNN}): open feature branch"
   git push -u origin {NNN}-{kebab-name}
   gh pr create --draft \
     --title "{NNN}: {Feature Name}" \
     --body "Draft PR for feature {NNN}. Opened automatically at plan stage."
   ```
   If `gh` is unavailable, skip silently (graceful degradation). Store the PR number for later use.
4. Derive specs directory: `specs/{NNN}-*/`
5. If no specs directory found, check `.aod/spec.md` as fallback
6. If no feature context found: warn and suggest `/aod.define` first

### Step 2: Read Artifact States

For each artifact (spec.md, plan.md, tasks.md), determine its approval status:

1. **Check file existence** — if file cannot be read (missing, permissions, encoding), treat as "does not exist"
2. **Parse YAML frontmatter** — extract the `triad:` block between `---` delimiters
3. **Extract sign-off status** — read `triad.{role}_signoff.status` for the required reviewers

### Step 3: Evaluate Frontmatter (with error handling)

For each artifact file, apply these rules in order:

1. **File does not exist** → status = `missing`
2. **File exists but has no `---` frontmatter delimiters** → status = `not_approved`, emit: "Note: {file} has no frontmatter. Running {sub-step} for review."
3. **File has frontmatter but no `triad:` key** → status = `not_approved`, emit: "Note: {file} frontmatter missing triad block. Running {sub-step} for review."
4. **`triad:` exists but required sign-off field is null or missing** → status = `not_approved`
5. **Sign-off status is not a recognized value** → status = `not_approved`, emit: "Warning: Unexpected status '{value}' in {file}. Re-running {sub-step}."
6. **YAML parse error** → status = `not_approved`, emit: "Warning: Could not parse frontmatter in {file}. Re-running {sub-step}."

**Recognized approved statuses**: `APPROVED`, `APPROVED_WITH_CONCERNS`, `BLOCKED_OVERRIDDEN`

### Step 3b: Read Governance Tier

Read `.aod/memory/constitution.md` and extract the governance tier:

1. Look for the `## Governance Tiers` section
2. Find the configuration block: `governance:` → `tier:` value
3. Valid values: `light`, `standard`, `full`
4. If not found or invalid: default to `standard`

**Tier affects Step 4 decision table** — specifically the spec PM sign-off check.

### Step 4: Apply Decision Table

**Standard and Full tiers** (default behavior):

| spec.md exists? | spec PM approved? | plan.md exists? | plan dual-approved? | tasks.md exists? | tasks triple-approved? | Action |
|-----------------|-------------------|-----------------|---------------------|------------------|------------------------|--------|
| No | — | — | — | — | — | Invoke `/aod.spec` |
| Yes | No | — | — | — | — | Invoke `/aod.spec` (needs PM sign-off) |
| Yes | Yes | No | — | — | — | Invoke `/aod.project-plan` |
| Yes | Yes | Yes | No | — | — | Invoke `/aod.project-plan` (needs dual sign-off) |
| Yes | Yes | Yes | Yes | No | — | Invoke `/aod.tasks` |
| Yes | Yes | Yes | Yes | Yes | No | Invoke `/aod.tasks` (needs triple sign-off) |
| Yes | Yes | Yes | Yes | Yes | Yes | Report "Plan stage complete" |

**Light tier** (reduced gates):

| spec.md exists? | plan.md exists? | plan dual-approved? | tasks.md exists? | tasks triple-approved? | Action |
|-----------------|-----------------|---------------------|------------------|------------------------|--------|
| No | — | — | — | — | Invoke `/aod.spec` |
| Yes | No | — | — | — | Invoke `/aod.project-plan` (skip PM spec sign-off) |
| Yes | Yes | No | — | — | Invoke `/aod.project-plan` (needs dual sign-off) |
| Yes | Yes | Yes | No | — | Invoke `/aod.tasks` |
| Yes | Yes | Yes | Yes | No | Invoke `/aod.tasks` (needs triple sign-off) |
| Yes | Yes | Yes | Yes | Yes | Report "Plan stage complete" |

In Light tier, when spec.md exists but has no PM sign-off, the router **skips** the PM spec sign-off check and proceeds directly to `/aod.project-plan`. Emit: "Note: Light governance tier — PM spec sign-off skipped."

**Full tier** uses the same table as Standard. The difference between Standard and Full is that Full requires a **separate** PM spec sign-off step (the PM reviews spec.md independently before plan creation). This distinction is enforced within `/aod.spec` itself, not in the router.

**Approval checks per artifact**:
- **spec.md** (Standard/Full): `triad.pm_signoff.status` is approved
- **spec.md** (Light): existence is sufficient — PM sign-off not required
- **plan.md**: `triad.pm_signoff.status` AND `triad.architect_signoff.status` are both approved
- **tasks.md**: `triad.pm_signoff.status` AND `triad.architect_signoff.status` AND `triad.techlead_signoff.status` are all approved

**Invariant**: Triple sign-off on tasks.md is the governance floor for ALL tiers, including Light.

### Step 5: Execute Orchestration Loop

Based on the decision table, determine the **starting sub-step** (the first one that needs work). Then run sub-steps in sequence, advancing automatically on approval.

**Loop logic**:

1. **Invoke the current sub-step** using the Skill tool (`aod.spec`, `aod.project-plan`, or `aod.tasks`)
2. **After the sub-step completes**, check the governance outcome:
   - **APPROVED** (or APPROVED_WITH_CONCERNS): Display a brief progress line, then **re-read artifact states** (Step 2) and **re-apply the decision table** (Step 4) to determine the next sub-step. Continue the loop.
   - **CHANGES_REQUESTED or BLOCKED**: **Stop the loop.** Display the rejection details and instruct the user to fix the issues, then re-run `/aod.plan` to resume.
3. **If the decision table returns "Plan stage complete"**: Exit the loop and display:

```
PLAN STAGE COMPLETE

All artifacts approved:
- spec.md: PM sign-off ✓
- plan.md: PM + Architect sign-off ✓
- tasks.md: PM + Architect + Team-Lead sign-off ✓

Next: Run /aod.build to start implementation.
```

**Progress display between sub-steps**:

After each approved sub-step, display a brief status line before advancing:

```
✓ spec.md — PM approved. Advancing to project-plan...
```
```
✓ plan.md — PM + Architect approved. Advancing to tasks...
```

**Important**: Re-read artifact states after each sub-step. Do NOT assume the next sub-step — the decision table handles edge cases (e.g., plan.md exists but lost dual approval).

## Edge Cases

### No PRD exists
If the user runs `/aod.plan` but there is no approved PRD for the current feature (no `docs/product/02_PRD/{NNN}-*.md`), warn:
```
No approved PRD found for this feature.

The Plan stage requires a PRD as input. Run /aod.define first to create one,
then return to /aod.plan.
```

### Direct sub-command invocation
The orchestrator does NOT block direct invocation of `/aod.spec`, `/aod.project-plan`, or `/aod.tasks`. Those commands work independently — the orchestrator is a convenience layer, not a gatekeeper.

### Re-run after rejection
If a governance gate rejects (e.g., PM requests changes to spec.md), the user fixes issues and re-runs `/aod.plan`. The orchestrator detects the missing/rejected sign-off and re-invokes the correct sub-step, then continues the loop from there.

### Mid-stage resume
If the user previously completed spec.md and plan.md (both approved) and runs `/aod.plan`, the orchestrator skips directly to `/aod.tasks` — it only runs what's needed.

## Integration

### Reads
- `specs/{NNN}-*/spec.md` — check existence and PM sign-off
- `specs/{NNN}-*/plan.md` — check existence and dual sign-off
- `specs/{NNN}-*/tasks.md` — check existence and triple sign-off
- `docs/product/02_PRD/{NNN}-*.md` — check PRD existence (edge case)

### Invokes (in sequence, advancing on approval)
- `/aod.spec` — when spec needs creation or PM approval
- `/aod.project-plan` — when plan needs creation or dual approval
- `/aod.tasks` — when tasks need creation or triple approval

### Updates
- None (orchestrator reads artifact state, sub-commands write artifacts)

---

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I know what's done, I'll skip re-reading state between sub-steps" | Step 5 Loop point 3 mandates re-read after each sub-step — assumed-state advancement misses lost approvals. |
| "This branch is small, I'll commit straight to main" | Step 1 point 2 auto-creates the feature branch on main — bypassing it skips the draft PR opened in point 3. |
| "spec.md exists, the gate must already be green" | Step 4 decision table requires `pm_signoff.status` approved per Step 2 — existence alone routes back to `/aod.spec`. |
| "Light tier means skip triple sign-off on tasks too" | Step 4 invariant (line 100) keeps tasks.md triple sign-off as the floor for ALL tiers, including Light. |
| "Approved with concerns is close enough — I'll fix later" | Step 4 recognized list (line 52) treats it as approved, but the concerns must still be addressed before delivery. |

## Red Flags

- Agent advances past an approved sub-step without re-running Step 4's decision table.
- Agent invokes `/aod.tasks` directly when plan.md lacks dual sign-off per the Step 4 plan row.
- Agent skips the draft PR open in Step 1 point 3 because `gh` "felt slow."
- Agent treats a missing `triad:` block as approved instead of `not_approved` per Step 3 rule 3.
- Agent reports "Plan stage complete" without all three artifacts hitting the Step 4 final row.
- Agent ignores the Light-tier note in Step 4 and re-runs `/aod.spec` for a PM sign-off the tier doesn't require.
