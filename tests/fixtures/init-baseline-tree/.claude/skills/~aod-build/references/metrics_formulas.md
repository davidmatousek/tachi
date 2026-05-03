# Checkpoint Metrics Formulas

This document defines the formulas used to calculate progress metrics in checkpoint reports.

---

## Progress Metrics

### Progress Percentage

**Formula**:
```
progress_percentage = (completed_tasks / total_tasks) * 100
```

**Example**:
```
Total tasks: 120
Completed tasks: 32
Progress: (32 / 120) * 100 = 26.67%
```

**Rounding**: Round to 2 decimal places for display, or 0 decimal places for summary views.

**Edge Cases**:
- If `total_tasks = 0`, return `0.0%` (avoid division by zero)
- If `completed_tasks > total_tasks`, cap at `100%` (data error)

---

### Phase Completion Percentage

**Formula**:
```
phase_completion = (completed_tasks_in_phase / total_tasks_in_phase) * 100
```

**Example**:
```
Phase 1: Setup
Total tasks in phase: 9
Completed tasks in phase: 9
Phase completion: (9 / 9) * 100 = 100%
```

**Status Determination**:
- `complete`: phase_completion = 100%
- `partial`: 0% < phase_completion < 100%
- `pending`: phase_completion = 0%
- `empty`: total_tasks_in_phase = 0

---

### Task Range Calculation

**Formula**:
```
task_range = "{first_completed_task}-{last_completed_task}"
```

**Example**:
```
Completed tasks: T001, T002, ..., T029, T030
Task range: "T001-T030"
```

**Edge Cases**:
- If no tasks completed: `"T000-T000"`
- Always cumulative from project start (T001)

---

## Efficiency Metrics

### Parallel Efficiency (when applicable)

**Formula**:
```
parallel_efficiency = 1 - (actual_time / sequential_time)
```

**Example**:
```
Sequential time (if done linearly): 203 hours
Actual time (with parallelization): 95 hours
Parallel efficiency: 1 - (95 / 203) = 1 - 0.468 = 0.532 = 53.2%
```

**Interpretation**:
- 0% = No parallelization benefit (sequential execution)
- 50% = Half the time saved through parallelization
- 100% = Instant completion (theoretical maximum)

**Note**: Only calculate if both actual_time and sequential_time are tracked.

---

### Time Savings

**Formula**:
```
time_saved = sequential_time - actual_time
```

**Example**:
```
Sequential time: 203 hours
Actual time: 95 hours
Time saved: 203 - 95 = 108 hours
```

**Units**: Express in hours for consistency.

**Display Format**: Convert to human-readable (e.g., "108 hours" or "4.5 days")

---

### Velocity (tasks per day)

**Formula**:
```
velocity = completed_tasks / days_elapsed
```

**Example**:
```
Completed tasks: 32
Days elapsed: 2.5
Velocity: 32 / 2.5 = 12.8 tasks/day
```

**Use Case**: Estimate remaining time based on current velocity.

**Estimated Completion**:
```
remaining_days = remaining_tasks / velocity
```

Example:
```
Remaining tasks: 88
Current velocity: 12.8 tasks/day
Estimated days: 88 / 12.8 = 6.875 ≈ 7 days
```

---

## Quality Metrics

### Test Coverage (when tests exist)

**Formula**:
```
test_coverage = (lines_covered / total_lines) * 100
```

**Example**:
```
Total lines: 8500
Lines covered by tests: 6800
Coverage: (6800 / 8500) * 100 = 80%
```

**Threshold**: Most projects target 80% coverage.

---

### Code Quality Score (composite)

**Formula**:
```
quality_score = (
    linting_pass_rate * 0.3 +
    type_safety_score * 0.3 +
    test_coverage * 0.2 +
    review_approval_rate * 0.2
)
```

**Example**:
```
Linting: 100% pass
Type safety: 100% (zero errors)
Test coverage: 80%
Review approval: 100%

Quality: (1.0*0.3) + (1.0*0.3) + (0.8*0.2) + (1.0*0.2)
       = 0.3 + 0.3 + 0.16 + 0.2
       = 0.96 = 96%
```

**Interpretation**:
- 90-100%: Excellent
- 80-89%: Good
- 70-79%: Acceptable
- <70%: Needs improvement

---

## Checkpoint-Specific Metrics

### Tasks Per Checkpoint

**Formula**:
```
tasks_per_checkpoint = total_completed_tasks / checkpoint_number
```

**Example**:
```
Checkpoint: 01
Total completed: 32
Average: 32 / 1 = 32 tasks/checkpoint
```

**Use Case**: Estimate tasks for future checkpoints.

---

### Checkpoint Frequency

**Formula**:
```
checkpoint_frequency = days_elapsed / checkpoint_number
```

**Example**:
```
Days elapsed: 2.5
Checkpoint: 01
Frequency: 2.5 / 1 = 2.5 days/checkpoint
```

**Use Case**: Estimate when next checkpoint should occur.

---

## Display Formats

### Percentage

**Format**: `XX.XX%` or `XX%` (depending on context)

**Examples**:
- `26.67%` (detailed)
- `27%` (summary)

---

### Time Duration

**Format**: Human-readable with appropriate units

**Examples**:
- `< 1 hour` → "45 minutes"
- `1-8 hours` → "X hours"
- `> 8 hours` → "X hours" or "X days"
- `> 24 hours` → "X days"

**Conversion**:
```
hours_to_days = hours / 8  (assuming 8-hour work day)
```

---

### Task IDs

**Format**: Zero-padded 3 digits with `T` prefix

**Examples**:
- `T001` (not `T1`)
- `T030` (not `T30`)
- `T120` (not `T120`)

---

### Progress Bar (ASCII)

**Format**: Visual progress indicator

**Formula**:
```
filled_blocks = floor((progress_percentage / 100) * total_blocks)
empty_blocks = total_blocks - filled_blocks
progress_bar = "█" * filled_blocks + "░" * empty_blocks
```

**Example** (20 blocks):
```
Progress: 27%
Blocks filled: floor(0.27 * 20) = 5
Bar: "█████░░░░░░░░░░░░░░░" 27%
```

---

## Calculation Examples

### Example 1: Checkpoint 01 (Foundational Phase)

**Input**:
```
Total tasks: 120
Completed tasks: 32
Days elapsed: 2.5
Sequential estimate: 203 hours
Actual time: 95 hours
```

**Calculations**:
```
Progress: (32 / 120) * 100 = 26.67%
Velocity: 32 / 2.5 = 12.8 tasks/day
Time saved: 203 - 95 = 108 hours
Parallel efficiency: 1 - (95/203) = 53.2%
Remaining days: (120-32) / 12.8 = 6.875 days ≈ 7 days
```

---

### Example 2: Checkpoint 02 (User Story 1 Complete)

**Input**:
```
Total tasks: 120
Completed tasks: 39
Phases complete: Phase 1 (9/9), Phase 2 (16/16), Phase 3 (14/14)
Days elapsed: 3.0
```

**Calculations**:
```
Progress: (39 / 120) * 100 = 32.5% ≈ 33%
Task range: T001-T039
Velocity: 39 / 3.0 = 13 tasks/day
Phase 1 completion: (9/9) * 100 = 100%
Phase 2 completion: (16/16) * 100 = 100%
Phase 3 completion: (14/14) * 100 = 100%
```

---

## Edge Cases and Error Handling

### Division by Zero

**Scenario**: `total_tasks = 0`

**Solution**: Return `0%` or `N/A`

---

### Invalid Data

**Scenario**: `completed_tasks > total_tasks`

**Solution**: Cap at 100%, log warning

---

### Missing Time Data

**Scenario**: No `actual_time` or `sequential_time` tracked

**Solution**: Skip efficiency calculations, mark as "Not tracked"

---

### Negative Time

**Scenario**: `actual_time > sequential_time` (better than estimate)

**Solution**: Report negative efficiency or "Exceeded expectations"

---

## Automation

All formulas in this document are implemented in:
- `scripts/analyze_tasks.py` - Progress and phase metrics
- `scripts/generate_checkpoint.py` - Checkpoint-specific metrics

**Testing**: Validate calculations against manual examples above.

---

**Version**: 1.0.0
**Last Updated**: 2025-11-20
**Maintainer**: Team Lead Agent
