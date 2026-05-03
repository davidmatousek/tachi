---
name: ~aod-status
description: "On-demand backlog snapshot and lifecycle stage summary. Regenerates BACKLOG.md from GitHub Issues and displays item counts per stage. Use this skill when you need to check backlog status, view stage counts, regenerate BACKLOG.md, or get a lifecycle overview."
---

# AOD Status Skill

## Purpose

Utility skill for the AOD Lifecycle. Provides an on-demand snapshot of the project backlog by regenerating BACKLOG.md from GitHub Issues and displaying a summary of items per lifecycle stage.

No governance gates — this is a read-only utility command.

## How It Works

### Step 1: Reconcile Board

Run board reconciliation to fix any label↔board column drift before generating the snapshot:

```bash
source .aod/scripts/bash/github-lifecycle.sh && aod_gh_reconcile_board
```

This compares each open issue's `stage:*` label to its board column and fixes mismatches. If the board or `gh` is unavailable, it skips silently.

### Step 2: Regenerate BACKLOG.md

Run the backlog regeneration script with JSON output mode:

```bash
bash .aod/scripts/bash/backlog-regenerate.sh --json
```

**Parse the JSON output** to extract:
- `file`: path to regenerated BACKLOG.md
- `total`: total number of GitHub Issues
- `stages`: object with counts per stage (`discover`, `define`, `plan`, `build`, `deliver`, `untracked`)

**If the script fails or `gh` is unavailable**: Display a warning and attempt to read the existing BACKLOG.md file instead. If no BACKLOG.md exists either, report that no backlog data is available.

### Step 3: Display Stage Summary

Present a formatted summary table:

```
AOD LIFECYCLE STATUS

| Stage    | Count |
|----------|-------|
| Discover | {n}   |
| Define   | {n}   |
| Plan     | {n}   |
| Build    | {n}   |
| Deliver  | {n}   |
| Untracked| {n}   |
|----------|-------|
| Total    | {n}   |

BACKLOG.md regenerated at {file_path}.
```

### Step 4: Show Active Feature Context (Optional)

If the current git branch matches a feature pattern (`NNN-*`), display the active feature context:

1. Get branch: `git branch --show-current`
2. Extract NNN prefix
3. Check for `specs/{NNN}-*/` directory
4. If found, read spec.md/plan.md/tasks.md frontmatter to show approval status:

```
Active Feature: {NNN}-{name}
  spec.md:  {PM approved / not approved / missing}
  plan.md:  {dual approved / not approved / missing}
  tasks.md: {triple approved / not approved / missing}
```

If not on a feature branch, skip this section.

## Edge Cases

- **`gh` CLI unavailable**: Warn and fall back to reading existing BACKLOG.md (may be stale)
- **No GitHub remote**: Same as above — graceful degradation
- **Empty backlog**: Display the table with all zeros
- **Script not found**: Warn: "backlog-regenerate.sh not found at expected path"
- **Not on a feature branch**: Skip active feature context section

## Integration

### Reads
- `.aod/scripts/bash/github-lifecycle.sh` — reconciliation functions
- `.aod/scripts/bash/backlog-regenerate.sh` — regeneration script (JSON mode)
- `docs/product/_backlog/BACKLOG.md` — fallback if script fails
- `specs/{NNN}-*/spec.md`, `plan.md`, `tasks.md` — active feature context

### Invokes
- `aod_gh_reconcile_board` — fixes label↔board drift before snapshot

### Updates
- `docs/product/_backlog/BACKLOG.md` — regenerated from GitHub Issues
- GitHub Projects board — reconciles mismatched columns
