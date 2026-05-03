---
description: Run the full Plan stage — spec → project-plan → tasks — advancing automatically on approval, stopping on rejection
---

## User Input

```text
$ARGUMENTS
```

Consider user input before proceeding (if not empty).

## Overview

Orchestrates all three Plan sub-steps in sequence. Advances automatically when governance reviews pass (APPROVED). Stops if any review returns CHANGES_REQUESTED or BLOCKED, so the user can fix and re-run `/aod.plan` to resume from where it stopped.

**Flow**: Detect branch → Read artifact states → Run sub-steps in sequence (spec → project-plan → tasks) → Stop on rejection or report completion

## Execution

Invoke the `~aod-plan` skill to perform orchestration. Pass any user arguments through to the sub-commands.

The skill will:
1. Determine the current feature from the git branch
2. Check spec.md, plan.md, and tasks.md for existence and approval status
3. Start from the first sub-step that needs work (skips already-approved artifacts)
4. After each sub-step is approved, automatically advance to the next
5. Stop on CHANGES_REQUESTED or BLOCKED — report what needs fixing
6. Report "Plan stage complete" when all three artifacts are approved

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I'll bypass `/aod.plan` and run the sub-commands myself" | `/aod.plan` resumes from the first unfinished sub-step (Step 3 of this file) and skips already-approved artifacts. Running sub-commands manually loses auto-advance and the artifact-state check. |
| "The spec was rejected — I'll re-run `/aod.plan` to skip past it" | Step 5 stops on CHANGES_REQUESTED by design and re-enters at the rejected sub-step. Address review notes; the orchestrator does not bypass rejections. |
| "I'll run `/aod.plan` from main — it will figure out the branch" | Step 1 derives the feature from `git branch --show-current`. From main, no NNN-* feature is detected and the orchestrator aborts. Create the feature branch first. |

## Red Flags

- Agent runs `/aod.spec`, `/aod.project-plan`, and `/aod.tasks` separately without invoking `/aod.plan` once.
- Agent re-invokes `/aod.plan` immediately after a CHANGES_REQUESTED stop without editing the rejected artifact.
- Agent invokes `/aod.plan` from the `main` branch instead of a `NNN-*` feature branch.
- Agent reports "Plan stage complete" without the Step 6 confirmation message from the orchestrator.
