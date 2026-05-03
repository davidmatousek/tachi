---
description: Capture a new feature idea with ICE scoring into the Ideas Backlog
---

## User Input

```text
$ARGUMENTS
```

Consider user input before proceeding (if not empty).

## Overview

Captures a raw feature idea, scores it with ICE (Impact, Confidence, Effort), and creates a GitHub Issue for lifecycle tracking.

**Source of truth**: GitHub Issues with `stage:*` labels. BACKLOG.md is auto-generated.

**Flow**: Parse idea → Generate ID from GitHub Issues → Capture source → ICE scoring → Evidence → Auto-defer gate → Create GitHub Issue → Regenerate BACKLOG.md → Report result

### Flags

- **`--seed`**: Fast-track mode for pre-vetted ideas. Skips ICE prompts, evidence, source, and PM validation. Auto-assigns P1 defaults (I:8 C:7 E:7 = 22). Usage: `/aod.discover --seed My feature idea`
- **`--autonomous`**: Auto-select defaults for all interactive prompts (used by `aod.run` orchestrator). See Step 0.

## Step 0: Parse --autonomous

1. If `$ARGUMENTS` contains `--autonomous`:
   - Set `autonomous = true`
   - Strip `--autonomous` from `$ARGUMENTS` (trim extra whitespace)
2. Default: `autonomous = false`

## Step 1: Validate Input

1. Parse idea description from `$ARGUMENTS`
2. If empty: Ask the user to describe their idea before proceeding

## Step 2: Execute Idea Capture

Follow the workflow defined in the ~aod-discover skill (`.claude/skills/~aod-discover/SKILL.md`):

1. Create GitHub Issue and use the auto-assigned Issue number as the canonical ID
2. Capture source via AskUserQuestion (Brainstorm / Customer Feedback / Team Idea / User Request)
   - **If `autonomous == true`**: Auto-select `"Team Idea"`. Display: `"Auto-selected: Team Idea (autonomous mode)"`
3. ICE scoring via AskUserQuestion (Impact, Confidence, Effort — each H9/M6/L3 or custom 1-10)
   - **If `autonomous == true`**: Auto-assign medium defaults: Impact=6, Confidence=6, Effort=6 (total=18). Display: `"Auto-selected: ICE 6/6/6 = 18 (autonomous mode)"`
4. Evidence prompt via AskUserQuestion
   - **If `autonomous == true`**: Auto-provide `"Automated discovery via aod.run"`. Display: `"Auto-selected: automated evidence (autonomous mode)"`
5. Compute ICE total, apply auto-defer gate (< 12 = Deferred, >= 12 = Scoring)
6. Create GitHub Issue with structured body and `stage:discover` label
7. Regenerate BACKLOG.md via `.aod/scripts/bash/backlog-regenerate.sh`
8. Report result with ID, ICE breakdown, priority tier, and next step guidance

## Quality Checklist

- [ ] Idea description captured from user
- [ ] GitHub Issue created and Issue number used as canonical ID
- [ ] Source captured from user selection
- [ ] Evidence captured from user
- [ ] ICE score computed and auto-defer gate applied
- [ ] GitHub Issue created with structured body and `stage:discover` label
- [ ] BACKLOG.md regenerated
- [ ] Result reported with next step guidance

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I'll use `--seed` to skip ICE scoring — it's faster" | `--seed` auto-assigns I:8 C:7 E:7 = 22 (P1) and skips PM validation. Step 2 auto-defer gate cannot triage unvetted ideas. Use only for pre-vetted items. |
| "I'll run `/aod.discover` with no arguments and describe the idea later" | Step 1 aborts on empty `$ARGUMENTS` and asks the user to describe the idea. Pass the idea as an argument; do not run blind. |
| "I'll pass `--autonomous` so I don't have to answer the prompts" | `--autonomous` is for `aod.run` orchestrator use. Outside that context, it fills source/ICE/evidence with synthetic defaults and runs the auto-defer gate on fake data. |
| "ICE total came back Deferred — I'll re-invoke with bigger numbers" | The auto-defer gate (< 12) is the triage signal. Inflated re-runs bypass it. Use `/aod.score` to re-score with new evidence; do not re-discover. |

## Red Flags

- Agent invokes `/aod.discover --seed` for a fresh unvetted idea instead of a pre-vetted seed item.
- Agent runs `/aod.discover` with empty `$ARGUMENTS` and accepts the Step 1 abort without re-prompting the user.
- Agent re-invokes `/aod.discover` with higher ICE inputs after a Deferred result on the same idea.
- Agent uses `--autonomous` outside an `aod.run` orchestrator context.
- Agent advances a Deferred-tier idea to `/aod.define` without re-scoring via `/aod.score`.

