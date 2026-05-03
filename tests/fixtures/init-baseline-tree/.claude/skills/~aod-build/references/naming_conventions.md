# Checkpoint Naming Conventions

## Format

`CHECKPOINT-{NN}_{Phase-Description}_{TaskRange}.md`

## Components

### `{NN}`: Sequential checkpoint number
- Zero-padded two digits (01, 02, 03...)
- Auto-incremented from existing checkpoints
- Starts at 01 for first checkpoint
- Never skip numbers (no gaps in sequence)

**Examples**:
- `01` - First checkpoint
- `02` - Second checkpoint
- `15` - Fifteenth checkpoint

### `{Phase-Description}`: Human-readable milestone
- CamelCase or hyphen-separated
- Concise description of what was completed (2-4 words max)
- Focus on functional milestone, not task numbers
- Common patterns:
  - `Phase1-2-Complete` - Multiple phases completed
  - `US1-Complete` - User Story 1 complete
  - `MVP-Ready` - MVP functionality ready
  - `FoundationComplete` - Foundation phase done
  - `ProductionReady` - Production deployment ready

**Examples**:
- ✅ `Phase1-2-Complete` (clear, concise)
- ✅ `US1-Complete` (standard pattern)
- ✅ `MVP-Ready` (milestone-focused)
- ❌ `phase_1_and_2` (wrong case, uses underscores)
- ❌ `CompletedAllTheSetupTasksAndSomeFoundationalTasks` (too verbose)
- ❌ `T001-T030` (don't repeat task range here)

### `{TaskRange}`: Start and end task IDs
- Format: `T###-T###`
- Zero-padded three digits
- Represents cumulative task range from project start
- Example: `T001-T030` means tasks 1 through 30 completed

**Examples**:
- `T001-T030` - First 30 tasks
- `T001-T039` - First 39 tasks (note: always starts at T001)
- `T001-T120` - All 120 tasks

**Important**: Task range is always cumulative from T001, not just the tasks in this checkpoint.

## Complete Examples

### ✅ Good Examples

```
CHECKPOINT-01_Phase1-2-Complete_T001-T030.md
CHECKPOINT-02_US1-Complete_T001-T039.md
CHECKPOINT-03_US2-Complete_T001-T055.md
CHECKPOINT-04_MVP-Ready_T001-T101.md
CHECKPOINT-05_ProductionReady_T001-T120.md
```

### ❌ Bad Examples

```
checkpoint_01.md
  ❌ Lowercase, no description, no task range

CHECKPOINT-1_Phase1.md
  ❌ Single digit number, no task range

progress-report-phase-1-and-2.md
  ❌ Non-standard format

CHECKPOINT-02_CompletedUserStoryOneWithAllEndpoints_T031-T039.md
  ❌ Description too verbose, task range not cumulative

CHECKPOINT-03_T040-T055.md
  ❌ No description, only task range

checkpoint-04_us2-complete_t001-t055.md
  ❌ All lowercase
```

## Naming Best Practices

1. **Be consistent** - Follow the format exactly for all checkpoints
2. **Be descriptive** - Description should instantly convey what milestone was reached
3. **Be concise** - Keep description short (2-4 words)
4. **Use standard patterns** - Prefer established patterns like "US{N}-Complete", "Phase{N}-Complete"
5. **Think cumulative** - Task range always starts at T001, even if this checkpoint only added tasks T031-T039

## Pattern Library

Common checkpoint description patterns:

| Pattern | When to Use | Example |
|---------|-------------|---------|
| `Phase{N}-Complete` | Single phase done | `Phase1-Complete` |
| `Phase{N}-{M}-Complete` | Multiple phases done | `Phase1-2-Complete` |
| `US{N}-Complete` | User story complete | `US1-Complete` |
| `US{N}-{M}-Complete` | Multiple stories | `US1-3-Complete` |
| `MVP-Ready` | Core MVP functionality ready | `MVP-Ready` |
| `{Feature}-Ready` | Specific feature ready | `API-Ready`, `WebUI-Ready` |
| `ProductionReady` | Deployment ready | `ProductionReady` |
| `{Milestone}` | Custom milestone | `DatabaseMigration`, `SecurityAudit` |

## Auto-Detection Logic

The `generate_checkpoint.py` script auto-detects the next checkpoint number by:

1. Scanning output directory for files matching `CHECKPOINT-*.md`
2. Extracting all checkpoint numbers
3. Taking max(numbers) + 1
4. Formatting as zero-padded 2-digit string

**Example**:
```
Existing files:
- CHECKPOINT-01_Phase1-2-Complete_T001-T030.md
- CHECKPOINT-02_US1-Complete_T001-T039.md

Next checkpoint: 03
```

## Validation Rules

The naming convention is validated by checking:

1. ✅ Starts with `CHECKPOINT-`
2. ✅ Has 2-digit zero-padded number
3. ✅ Followed by underscore
4. ✅ Has non-empty description
5. ✅ Followed by underscore
6. ✅ Has task range in format `T\d{3}-T\d{3}`
7. ✅ Ends with `.md`

**Regex pattern**:
```regex
^CHECKPOINT-\d{2}_[A-Za-z0-9-]+_T\d{3}-T\d{3}\.md$
```

## Migration from Old Formats

If you have checkpoints using old naming formats, rename them to follow this convention:

**Before**:
```
checkpoint-phase-1-complete.md
progress_report_2025-11-20.md
```

**After**:
```
CHECKPOINT-01_Phase1-Complete_T001-T009.md
CHECKPOINT-02_Phase1-2-Complete_T001-T030.md
```

---

**Version**: 1.0.0
**Last Updated**: 2025-11-20
