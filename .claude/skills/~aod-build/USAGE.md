# Implementation Checkpoint Skill - Usage Guide

## TL;DR

```bash
cd .claude/skills/~aod-build

python scripts/generate_checkpoint.py \
  --tasks-file ../../specs/001-tachi/tasks.md \
  --output-dir ../../specs/001-tachi \
  --description "Phase1-2-Complete"
```

Follow the prompts. Done in <2 minutes.

---

## Detailed Workflow

### Step 1: Decide When to Checkpoint

Create a checkpoint when you've reached a strategic milestone:
- ✅ Complete phase finished
- ✅ User story fully implemented
- ✅ Critical feature ready (MVP core)
- ✅ Before pausing for review/testing
- ✅ After architect approval

### Step 2: Navigate to Skill Directory

```bash
cd .claude/skills/~aod-build
```

### Step 3: Run Generate Script

```bash
python scripts/generate_checkpoint.py \
  --tasks-file ../../specs/{feature-id}/tasks.md \
  --output-dir ../../specs/{feature-id} \
  --description "{Milestone-Description}"
```

**Parameters**:
- `--tasks-file`: Path to your tasks.md file
- `--output-dir`: Where to save the checkpoint report
- `--description`: Short milestone name (e.g., "Phase1-2-Complete", "US1-Complete")

### Step 4: Answer Prompts

The script will analyze your tasks and prompt you for:

#### 4a. Executive Summary
```
Executive Summary (2-3 sentences about what was completed):
>
```

**Example**:
```
> Implementation paused after completing the foundation and MVP core functionality. The atomic locking mechanism is complete and production-ready.
```

#### 4b. Key Achievements
```
Key achievements (3-5 bullet points, one per line):
Enter each achievement on a new line. Press Enter twice when done.
>
```

**Example**:
```
> Database schema with 6 entities, 19 indexes
> Architect review APPROVED
> MVP core: Atomic locking with row-level locks
> Complete audit trail with JSONB snapshots
> Backend server running successfully
> [press Enter twice]
```

#### 4c. Files Summary
```
Files created/modified summary (brief overview):
>
```

**Example**:
```
> 65+ files including backend services, routes, configuration, tests, and documentation
```

#### 4d. Knowledge Base Entries
```
Number of knowledge base entries captured (enter number or '0'):
>
```

**If 0**: Skip to next step
**If >0**: You'll be prompted for each entry:

```
--- Knowledge Base Entry 1/5 ---
Title:
> PostgreSQL Row-Level Locking with NOWAIT

Problem (1-2 sentences):
> Standard UPDATE has race conditions for concurrent claims

Solution (2-3 sentences):
> SELECT ... FOR UPDATE NOWAIT with error code 55P03 handling prevents races

Time saved (e.g., '30 minutes', '2 hours'):
> 2 hours
```

**Repeat for all entries**.

### Step 5: Review Generated Files

The script will output:
```
✓ Generated: CHECKPOINT-01_Phase1-2-Complete_T001-T030.md
✓ Location: specs/001-tachi/CHECKPOINT-01_Phase1-2-Complete_T001-T030.md
✓ Updated: CHECKPOINTS_README.md

Next: Resume with /aod.build --resume
```

### Step 6: Fill in TODO Sections

Open the generated checkpoint file and replace `_TODO:` placeholders with actual content:

**Required sections to complete**:
- `{WHAT_WAS_IMPLEMENTED}` - Detail by phase/user story
- `{SERVER_STATUS}` - Server and database status
- `{QUALITY_METRICS}` - Code quality, tests, performance
- `{REMAINING_WORK}` - Next waves and estimates
- `{PAUSE_RATIONALE}` - Why pausing here
- `{TESTING_INSTRUCTIONS}` - How to test
- `{DEPENDENCIES}` - Runtime versions
- `{RISK_ASSESSMENT}` - Completed/remaining risks
- `{RECOMMENDATIONS}` - Guidance for next session
- `{SUCCESS_CRITERIA}` - Status from spec

**Tip**: Look at existing [CHECKPOINT-01](../../../specs/001-tachi/CHECKPOINT-01_Phase1-2-Complete_T001-T030.md) for reference.

### Step 7: Commit Checkpoint

```bash
git add specs/{feature-id}/CHECKPOINT-*.md
git add specs/{feature-id}/CHECKPOINTS_README.md
git commit -m "docs: Add checkpoint {NN} - {Description}"
```

---

## Advanced Usage

### Override Checkpoint Number

By default, the script auto-detects the next checkpoint number. To override:

```bash
python scripts/generate_checkpoint.py \
  --tasks-file ../../specs/001-tachi/tasks.md \
  --output-dir ../../specs/001-tachi \
  --description "Phase1-2-Complete" \
  --checkpoint-num 05
```

### Analyze Tasks Only

To see metrics without generating a checkpoint:

```bash
python scripts/analyze_tasks.py ../../specs/001-tachi/tasks.md
```

Output:
```json
{
  "total_tasks": 120,
  "completed_tasks": 31,
  "progress_percentage": 25.83,
  "phases": [...],
  "task_range": "T001-T036"
}
```

### Update Index Manually

If you need to update CHECKPOINTS_README.md separately:

```bash
python scripts/update_index.py \
  --checkpoints-readme ../../specs/001-tachi/CHECKPOINTS_README.md \
  --checkpoint-file CHECKPOINT-02_US1-Complete_T001-T039.md \
  --checkpoint-num 02 \
  --progress 33
```

---

## Common Scenarios

### Scenario 1: First Checkpoint in New Feature

```bash
# 1. Create CHECKPOINTS_README.md from template
cp assets/CHECKPOINTS_README_template.md ../../specs/002-new-feature/CHECKPOINTS_README.md

# 2. Edit template variables
# Replace {FEATURE_ID}, {FEATURE_NAME}, {TOTAL_TASKS}, etc.

# 3. Generate first checkpoint
python scripts/generate_checkpoint.py \
  --tasks-file ../../specs/002-new-feature/tasks.md \
  --output-dir ../../specs/002-new-feature \
  --description "FoundationComplete"
```

### Scenario 2: Mid-Implementation Checkpoint

```bash
# Standard workflow
python scripts/generate_checkpoint.py \
  --tasks-file ../../specs/001-tachi/tasks.md \
  --output-dir ../../specs/001-tachi \
  --description "US2-Complete"

# Answer prompts, review output, fill TODOs, commit
```

### Scenario 3: Final Checkpoint (Production Ready)

```bash
python scripts/generate_checkpoint.py \
  --tasks-file ../../specs/001-tachi/tasks.md \
  --output-dir ../../specs/001-tachi \
  --description "ProductionReady"

# This should show 100% progress if all tasks complete
```

---

## Troubleshooting

### Error: "Tasks file not found"

**Cause**: Wrong path to tasks.md

**Solution**: Use absolute path or correct relative path from skill directory

```bash
# From skill directory
python scripts/generate_checkpoint.py \
  --tasks-file /Users/david/Documents/GitHub/tachi/specs/001-tachi/tasks.md \
  --output-dir /Users/david/Documents/GitHub/tachi/specs/001-tachi \
  --description "Phase1-2-Complete"
```

### Error: "Output directory not found"

**Cause**: Output directory doesn't exist

**Solution**: Create directory first

```bash
mkdir -p specs/002-new-feature
```

### Error: "Template not found"

**Cause**: checkpoint_template.md missing

**Solution**: Verify skill installation

```bash
ls .claude/skills/~aod-build/references/checkpoint_template.md
```

### Checkpoint number wrong

**Cause**: Naming conflict or detection error

**Solution**: Override with `--checkpoint-num`

```bash
python scripts/generate_checkpoint.py \
  --checkpoint-num 03 \
  ...
```

### CHECKPOINTS_README.md not updating

**Cause**: File doesn't exist in output directory

**Solution**: Create from template first

```bash
cp assets/CHECKPOINTS_README_template.md ../../specs/001-tachi/CHECKPOINTS_README.md
```

---

## Tips for Quality Checkpoints

### Executive Summary
✅ **Good**: "Implementation paused after completing the foundation and MVP core functionality."
❌ **Bad**: "We did some work and made progress."

### Key Achievements
✅ **Good**: "Database schema with 6 entities, 19 indexes"
❌ **Bad**: "Database stuff"

### Knowledge Base Entries
✅ **Include**: Problems that took >30 min, non-obvious solutions, patterns to reuse
❌ **Skip**: Obvious facts, generic statements, temporary workarounds

### Description Naming
✅ **Good**: "Phase1-2-Complete", "US1-Complete", "MVP-Ready"
❌ **Bad**: "checkpoint-2", "progress", "T001-T030"

---

## Integration with Workflow

### Standard Implementation Flow

1. **Start implementation**: `/aod.build`
2. **Complete milestone**: Mark tasks [X] in tasks.md
3. **Create checkpoint**: Run this skill
4. **Review**: Architect/PM review checkpoint
5. **Resume**: `/aod.build --resume`

### Checkpoint Frequency

**Recommended**: 1 checkpoint per 20-30 tasks or major milestone

**Example schedule**:
- Checkpoint 01: After Phase 1-2 (T001-T030)
- Checkpoint 02: After User Story 1 (T031-T039)
- Checkpoint 03: After User Story 2 (T040-T055)
- Checkpoint 04: After User Story 3 (T056-T069)
- Checkpoint 05: MVP Feature Complete (T070-T101)
- Checkpoint 06: Production Ready (T102-T120)

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python scripts/analyze_tasks.py {path}` | View metrics only |
| `python scripts/generate_checkpoint.py ...` | Generate full checkpoint |
| `python scripts/update_index.py ...` | Update index manually |
| `--checkpoint-num {NN}` | Override auto-detection |
| `--help` | Show command help |

---

**Need help?** See [SKILL.md](SKILL.md) for full documentation or [README.md](README.md) for overview.
