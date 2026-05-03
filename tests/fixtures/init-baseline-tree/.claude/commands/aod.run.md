---
description: Run the full AOD lifecycle orchestrator — chains all 6 stages (Discover → Define → Plan → Build → Deliver → Document) with session-resilient state and governance gates at every boundary.
---

## User Input

```text
$ARGUMENTS
```

## Overview

Single-command lifecycle orchestrator. Accepts 4 input modes and 1 combinable flag (`--dry-run`), and delegates to the `~aod-run` skill.

**Usage**: `/aod.run <idea | #NNN | --resume | --status | --dry-run>`

**Entry Points**:

| Command | Mode | What It Does |
|---------|------|-------------|
| `/aod.run "Add dark mode toggle"` | New idea | Starts full lifecycle at Discover stage |
| `/aod.run #22` or `/aod.run 22` | Issue | Reads GitHub Issue, resumes from current stage |
| `/aod.run --resume` | Resume | Continues from last state checkpoint on disk |
| `/aod.run --status` | Status | Read-only display of current orchestration state |
| `/aod.run --status #22` | Status | Inferred status for a specific issue (no state file needed) |
| `/aod.run --dry-run "Add dark mode"` | Dry-run | Preview full lifecycle without executing |
| `/aod.run --dry-run #22` | Dry-run | Preview from issue without executing |
| `/aod.run --dry-run --resume` | Dry-run | Preview resume without executing |

**State File**: `.aod/run-state.json` — persisted after every stage transition for session resilience.

**Skill Reference**: `.claude/skills/~aod-run/SKILL.md` — full orchestration logic.

## Step 0: Parse Flags

Parse optional flags from `$ARGUMENTS`. Flags must appear at the start of arguments.

**Step 0a: Parse --dry-run**

Check if `$ARGUMENTS` starts with `--dry-run`:

1. If `$ARGUMENTS` starts with `--dry-run`:
   - Set `dry_run = true`
   - Strip `--dry-run` from the beginning of `$ARGUMENTS` (trim leading whitespace from remainder)
   - Continue to Step 1 with the remaining arguments

2. If `$ARGUMENTS` does NOT start with `--dry-run`:
   - Set `dry_run = false`
   - Continue to Step 1 with `$ARGUMENTS` unchanged

## Step 1: Parse Input Mode

Read the (possibly stripped) arguments and determine the entry mode:

1. **Status mode**: Arguments start with `--status`
   - If followed by `#NNN` or `NNN`: set mode = `status`, issue = NNN
   - If no number: set mode = `status`, issue = null

2. **Resume mode**: Arguments equal `--resume`
   - Set mode = `resume`

3. **Issue mode**: Arguments match `#NNN` or are a bare number `NNN` (1-4 digits)
   - Set mode = `issue`, issue = NNN (strip `#` prefix if present)

4. **New idea mode**: Arguments are a quoted or unquoted text string (anything else)
   - Set mode = `idea`, idea = the full argument text (strip surrounding quotes if present)

5. **No arguments**: Display usage help and exit:
   ```
   Usage: /aod.run <idea | #NNN | --resume | --status | --dry-run>

   Examples:
     /aod.run "Add dark mode toggle"    Start new lifecycle from idea
     /aod.run #22                        Resume from GitHub Issue #22
     /aod.run --resume                   Continue from last checkpoint
     /aod.run --status                   View current orchestration state
     /aod.run --status #22               View status for issue #22
     /aod.run --dry-run "Add feature"   Preview lifecycle without executing
     /aod.run --dry-run #22             Preview from issue without executing
     /aod.run --dry-run --resume        Preview resume without executing

   Lifecycle stages: Discover → Define → Plan (spec → plan → tasks) → Build → Deliver → Document
   All 6 stages are orchestrated by aod.run. Document runs automatically as Stage 6.
   Governance gates pause at each stage boundary for Triad sign-offs.
   State is persisted to .aod/run-state.json for session resilience.

   Flags:
     --dry-run         Read-only preview mode, no modifications
   ```

## Step 2: Invoke Orchestrator Skill

Use the Skill tool to invoke `~aod-run` with the parsed mode and arguments:

- Pass the determined mode (`idea`, `issue`, `resume`, `status`) and relevant data (idea text, issue number) as context in the skill invocation
- The skill handles all orchestration logic, state management, and stage delegation

Format the invocation as:
```
Mode: {mode}
Issue: {issue_number or "none"}
Idea: {idea_text or "none"}
DryRun: {true or false}
```

The `~aod-run` skill will take over from here.

## Expected Behavior by Mode

### New Idea (`"text"`)
1. Creates initial state file with `current_stage: "discover"`
2. Chains through: Discover → Define → Plan → Build → Deliver
3. Pauses at governance gates for Triad sign-offs
4. On session overflow: state is on disk, resume with `--resume`

### Issue (`#NNN`)
1. Reads GitHub Issue labels to detect current stage
2. Scans disk for existing artifacts (PRD, spec, plan, tasks)
3. Creates state file with completed stages pre-filled
4. Resumes from the first incomplete stage

### Resume (`--resume`)
1. Reads `.aod/run-state.json` and validates schema
2. Checks artifact consistency (warns if files are missing)
3. Detects stale state (>7 days) and asks for confirmation
4. Continues from the last completed stage boundary

### Status (`--status`)
1. Read-only display — never modifies state or artifacts
2. Shows stage map, feature name, governance gate results
3. With `#NNN`: infers status from GitHub label + disk artifacts if no state file

### Dry-Run (`--dry-run`)
1. Read-only preview — never modifies state, git, or GitHub
2. Shows planned stages (EXECUTE/SKIP), governance gates, and expected artifacts
3. Combinable with idea, issue, or resume modes (flag must appear first)
4. Exits immediately after preview display
5. If combined with `--status`: the `--dry-run` flag is ignored (status is already read-only)
