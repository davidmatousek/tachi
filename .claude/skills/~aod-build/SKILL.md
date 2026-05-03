---
name: ~aod-build
description: Generate standardized checkpoint reports for multi-phase implementation projects. Use this skill when pausing implementation at strategic milestones (phase completion, user story completion, critical features) to create comprehensive progress reports with task breakdowns, metrics, knowledge base entries, and resume instructions.
---

# Implementation Checkpoint Skill

## Purpose

Automatically generate standardized checkpoint reports that document implementation progress at strategic milestones. Each report includes completed tasks, remaining work, technical achievements, knowledge base entries, quality metrics, and resume instructions.

## When to Use

Create a checkpoint at:

1. **Complete phase finish** - All tasks in a phase marked complete
2. **User story completion** - Entire user story implemented and tested
3. **Critical milestone** - Core functionality ready (e.g., MVP core)
4. **Before pausing** - Stopping for review, testing, or user feedback
5. **After architect review** - Major approval/sign-off received

## How to Use

### Quick Usage

```bash
# Navigate to skill directory
cd .claude/skills/~aod-build

# Generate checkpoint (interactive prompts will follow)
python scripts/generate_checkpoint.py \
  --tasks-file ../../specs/{feature-id}/tasks.md \
  --output-dir ../../specs/{feature-id} \
  --description "{Phase-Description}"
```

### Step-by-Step Process

1. **Analyze completion status**
   ```bash
   # Script automatically:
   # - Reads tasks.md
   # - Counts [X] completed vs [ ] pending
   # - Calculates progress percentage
   # - Identifies completed phases
   # - Determines task range
   ```

2. **Provide context when prompted**
   ```
   Key achievements (3-5 bullet points):
   > - Achievement 1
   > - Achievement 2
   > - Achievement 3

   Knowledge base entries captured (count or 'none'):
   > 2

   [For each KB entry, provide: Title, Problem, Solution]
   ```

3. **Review generated report**
   ```bash
   # Output: CHECKPOINT-{NN}_{Description}_{TaskRange}.md
   # Location: specs/{feature-id}/
   ```

4. **Verify index updated**
   ```bash
   # Check: CHECKPOINTS_README.md includes new checkpoint
   ```

### Checkpoint Naming Convention

**Format**: `CHECKPOINT-{NN}_{Phase-Description}_{TaskRange}.md`

**Components**:
- `{NN}`: Sequential checkpoint number (01, 02, 03...) - auto-detected
- `{Phase-Description}`: Milestone name (e.g., "Phase1-2-Complete", "US1-Complete")
- `{TaskRange}`: Task IDs covered (e.g., "T001-T030")

**Examples**:
```
✓ CHECKPOINT-01_Phase1-2-Complete_T001-T030.md
✓ CHECKPOINT-02_US1-Complete_T001-T039.md
✓ CHECKPOINT-03_MVP-Ready_T001-T101.md
✓ CHECKPOINT-04_ProductionReady_T001-T120.md
```

See `references/naming_conventions.md` for detailed rules.

### Required Sections

Every checkpoint report includes:

1. **Executive Summary** - What was completed, what's next
2. **Completion Status** - Progress table with percentages
3. **What Was Implemented** - Detailed task breakdown by phase
4. **Key Technical Achievements** - Highlights and innovations
5. **Files Created/Modified** - Complete file inventory with counts
6. **Knowledge Base Captured** - Critical learnings documented
7. **Server/Database Status** - Current state of running services
8. **Quality Metrics** - Code quality, reviews, test coverage
9. **Remaining Work** - What's left and estimated time
10. **Resume Instructions** - How to continue implementation

### Metrics Calculated Automatically

- **Progress percentage**: `(completed / total) * 100`
- **Phase completion**: Per-phase progress tracking
- **Task range**: Start and end task IDs
- **Next task**: First pending task to work on

See `references/metrics_formulas.md` for formulas and examples.

### Knowledge Base Integration

When prompted for knowledge base entries, provide learnings that:

✅ **DO include**:
- Solved problems that took >30 minutes
- Non-obvious gotchas or edge cases
- Architectural decisions with trade-offs
- Patterns that should be reused
- Issues that could happen again

❌ **DON'T include**:
- Obvious facts ("we use PostgreSQL")
- Generic statements ("testing is important")
- Implementation progress ("completed task T026")
- Temporary workarounds

### Output Files

The skill generates/updates:

1. **Checkpoint Report**: `CHECKPOINT-{NN}_{Description}_{TaskRange}.md`
   - Location: `specs/{feature-id}/`
   - Size: ~15-20 KB
   - Format: Markdown with tables and code blocks

2. **Checkpoints Index**: `CHECKPOINTS_README.md` (updated)
   - Location: `specs/{feature-id}/`
   - Adds new checkpoint entry
   - Updates progress tracking table

### Resume Commands Generated

The checkpoint report includes auto-generated resume commands:

```bash
# For team-lead orchestration
/aod.build --resume

# For direct continuation
# Continue from task {NEXT_TASK}
```

## Scripts Reference

### analyze_tasks.py

Parse tasks.md and extract metrics.

**Input**: Path to tasks.md file
**Output**: JSON with completion metrics

**Usage**:
```bash
python scripts/analyze_tasks.py specs/001-{{PROJECT_NAME}}/tasks.md
```

**Output Format**:
```json
{
  "total_tasks": 120,
  "completed_tasks": 32,
  "progress_percentage": 26.67,
  "phases": [...],
  "task_range": "T001-T030",
  "next_task": "T031"
}
```

### generate_checkpoint.py

Generate checkpoint report from template.

**Usage**:
```bash
python scripts/generate_checkpoint.py \
  --tasks-file specs/{feature-id}/tasks.md \
  --output-dir specs/{feature-id} \
  --description "{Phase-Description}"
```

**Interactive Prompts**:
- Key achievements summary
- Knowledge base entries (optional)
- Per-entry: title, problem, solution

**Output**: Complete checkpoint report file

### update_index.py

Update CHECKPOINTS_README.md with new checkpoint.

**Usage**:
```bash
python scripts/update_index.py \
  --checkpoints-readme specs/{feature-id}/CHECKPOINTS_README.md \
  --checkpoint-file CHECKPOINT-{NN}_{Description}_{TaskRange}.md \
  --checkpoint-num {NN}
```

**Changes Made**:
- Adds checkpoint to "Active Checkpoints" section
- Updates progress tracking table
- Updates "Next Checkpoint Planned" footer

## Templates Reference

### checkpoint_template.md

Complete Markdown template for checkpoint reports. Contains all required sections with template variables for substitution.

**Location**: `references/checkpoint_template.md`

**Key Variables**:
- `{CHECKPOINT_NUM}`, `{PHASE_DESCRIPTION}`, `{TASK_RANGE}`
- `{DATE}`, `{FEATURE_ID}`, `{TOTAL_TASKS}`, `{COMPLETED_TASKS}`
- `{PROGRESS_PERCENTAGE}`, `{PHASES_TABLE}`, `{KEY_ACHIEVEMENTS}`
- `{KB_ENTRIES}`, `{NEXT_TASK}`, `{RESUME_COMMAND}`

### CHECKPOINTS_README_template.md

Template for creating the checkpoints index file (first-time use).

**Location**: `assets/CHECKPOINTS_README_template.md`

**Usage**: Copy to `specs/{feature-id}/CHECKPOINTS_README.md` when creating first checkpoint.

## Examples

### Example 1: After Completing Phase 1-2

```bash
$ python scripts/generate_checkpoint.py \
    --tasks-file specs/001-{{PROJECT_NAME}}/tasks.md \
    --output-dir specs/001-{{PROJECT_NAME}} \
    --description "Phase1-2-Complete"

Analyzing tasks.md...
✓ Found 120 total tasks
✓ Found 32 completed tasks (27%)
✓ Task range: T001-T030
✓ Checkpoint #01 (auto-detected)

Key achievements (3-5 bullet points):
> - Database schema with 6 entities, 19 indexes
> - Architect review APPROVED
> - MVP core: Atomic locking with row-level locks

Knowledge base entries: 5

[... interactive prompts for KB entries ...]

✓ Generated: CHECKPOINT-01_Phase1-2-Complete_T001-T030.md
✓ Updated: CHECKPOINTS_README.md

Next: Resume with /aod.build --resume
```

### Example 2: After Completing User Story 1

```bash
$ python scripts/generate_checkpoint.py \
    --tasks-file specs/001-{{PROJECT_NAME}}/tasks.md \
    --output-dir specs/001-{{PROJECT_NAME}} \
    --description "US1-Complete"

✓ Checkpoint #02: US1-Complete (T001-T039)
✓ Progress: 33% (39/120 tasks)

[... prompts and generation ...]

✓ Generated: CHECKPOINT-02_US1-Complete_T001-T039.md
```

## Troubleshooting

**Q: Script can't find tasks.md**
A: Provide absolute path or verify relative path from skill directory

**Q: Checkpoint number is wrong**
A: Manually specify with `--checkpoint-num NN` flag

**Q: Template variables not substituted**
A: Check template file exists in `references/checkpoint_template.md`

**Q: Index file not updating**
A: Verify CHECKPOINTS_README.md exists in output directory

## Best Practices

1. **Create checkpoints proactively** - Don't wait until pausing
2. **Capture knowledge fresh** - Document learnings immediately
3. **Be specific in achievements** - "Implemented X" not "Made progress"
4. **Validate metrics** - Review auto-calculated percentages
5. **Test resume commands** - Verify they work before distributing

---

**Skill Version**: 1.0.0
**Last Updated**: 2025-11-20
**Maintainer**: Team Lead Agent

---

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I'll skip the checkpoint — I'm only mid-phase" | Step 1 (line 17) lists critical milestones too; mid-phase pause without report leaves no resume artifact. |
| "KB entries can wait until after delivery" | Line 307 directs capturing knowledge fresh; deferred entries miss the gotchas described in lines 121-126. |
| "Achievements like 'made progress' are fine" | Line 308 requires specific achievements; vague entries violate the KB DON'T list (line 130). |
| "I can hand-write achievements without the script" | Quick Usage (line 27) requires `generate_checkpoint.py` — manual reports skip the auto progress percentage from line 109. |
| "Resume commands are documentation, not testing" | Line 311 requires testing resume commands before distributing; untested commands break next session. |

## Red Flags

- Agent creates a checkpoint without running `analyze_tasks.py` per the metrics block (lines 162-183).
- Agent's KB entries match the DON'T list (line 128): "obvious facts," "generic statements," "implementation progress."
- Agent skips line 310 (validate metrics): publishes auto-calculated percentages without sanity-checking them.
- Agent omits the Required Sections list (line 96) — Quality Metrics, Resume Instructions, or Files Created.
- Agent uses arbitrary checkpoint numbering instead of the auto-detected `{NN}` from the script (line 78).
- Agent's report contains template variables like `{NEXT_TASK}` unsubstituted — Troubleshooting Q3 (line 298) flags this.
