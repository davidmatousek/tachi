# Triad Feature Availability Matrix

This document details which Triad features are available based on Claude Code version.

## Quick Reference

| Feature | v2.1.15 | v2.1.16+ | Notes |
|---------|---------|----------|-------|
| Basic Triad Governance | ✅ | ✅ | Core workflow always works |
| Sequential Reviews | ✅ | ✅ | Default fallback |
| Parallel Reviews | ❌ | ✅ | ~50% faster cycles |
| Context Forking | ❌ | ✅ | Isolated agent contexts |
| Task Dependencies | ❌ | ✅ | Automatic blocking |
| Memory Leak Fixes | ❌ | ✅ | Stable long workflows |
| Graceful Degradation | ✅ | ✅ | Clear user messaging |
| `/aod.build` Design Quality Gate | ✅ | ✅ | Step 6 in build; skip with `--no-design-check` (Feature 097, 2026-03-27) |
| `/aod.build` Pre-Flight Validation | ✅ | ✅ | Step 0g in build; validates uncommitted changes + NEXT-SESSION.md (Feature 100, 2026-03-28) |
| `/aod.build` Test Execution Gate | ✅ | ✅ | Step 4.5 in build; per-wave test discovery, execution, and regression gating. Skip with `--no-tests`, elevate to hard gate with `--require-tests` (Feature 109, 2026-03-28) |
| `/aod.foundation` Workshop | ✅ | ✅ | Post-init vision + design identity workshop (Feature 100, 2026-03-28) |

---

## Detailed Feature Breakdown

### Context Forking (v2.1.0+)

**What it does**: Creates isolated execution contexts for each agent during parallel reviews.

**Minimum Version**: v2.1.0

**Flag**: `SPECKIT_FEATURE_CONTEXT_FORKING`

**Benefits**:
- PM cannot see Architect's intermediate state
- Architect cannot see Tech-Lead's calculations
- No context pollution between reviews
- Clean result merging

**Without this feature**:
- Agents share global context
- Risk of cross-agent interference
- Reviews execute sequentially to mitigate

### Parallel Execution (v2.1.16+)

**What it does**: Allows multiple Task calls in a single message to execute simultaneously.

**Minimum Version**: v2.1.16

**Flag**: `SPECKIT_FEATURE_PARALLEL_EXECUTION`

**Benefits**:
- PM + Architect reviews run concurrently
- Total time = max(PM, Architect) instead of sum
- ~50% reduction in Triad cycle time

**Without this feature**:
- Reviews execute one after another
- Longer overall workflow time
- All functionality still works correctly

### Task Dependencies (v2.1.16+)

**What it does**: Enables automatic prerequisite enforcement for tasks.

**Minimum Version**: v2.1.16

**Flag**: `SPECKIT_FEATURE_TASK_DEPENDENCIES`

**Benefits**:
- Tasks auto-block until dependencies complete
- Circular dependency detection
- Ready/blocked status visibility
- TodoWrite integration

**Without this feature**:
- Manual dependency coordination
- No automatic blocking
- Custom wrapper provides basic support

### Memory Leak Fixes (v2.1.16+)

**What it does**: Resolves memory issues in long-running parallel workflows.

**Minimum Version**: v2.1.16

**No flag** (automatic with version)

**Benefits**:
- Stable 30+ minute workflows
- Proper cleanup on interruption
- No orphaned tool results

**Without this feature**:
- Memory degrades over time
- Possible incomplete results
- Recommended to limit session length

---

## Version Detection Flow

```
┌─────────────────┐
│ Check CLAUDECODE│
│ env var         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Parse claude    │
│ --version       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Compare against │
│ thresholds      │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
v2.1.16+   < v2.1.16
    │         │
    ▼         ▼
┌─────────┐ ┌─────────┐
│ FULL    │ │ LIMITED │
│ FEATURES│ │ FEATURES│
└─────────┘ └─────────┘
```

---

## Feature Flag Configuration

Configuration file: `.claude/config/feature-flags.json`

```json
{
  "features": {
    "context_forking": {
      "minimum_version": "2.1.0",
      "default": false
    },
    "parallel_execution": {
      "minimum_version": "2.1.16",
      "default": false
    },
    "task_dependencies": {
      "minimum_version": "2.1.16",
      "default": false
    },
    "graceful_degradation": {
      "minimum_version": "2.1.15",
      "default": true
    }
  }
}
```

---

## Environment Variable Overrides

For testing or special cases, features can be manually controlled:

```bash
# Force enable (testing only)
export SPECKIT_FEATURE_PARALLEL_EXECUTION=true

# Force disable (troubleshooting)
export SPECKIT_FEATURE_CONTEXT_FORKING=false
```

**Warning**: Manual overrides may cause unexpected behavior if the underlying Claude Code version doesn't support the feature.

---

## Checking Your Feature Status

Run this to see your current feature availability:

```bash
source .claude/lib/version/feature-gate.sh
generate_feature_status
```

Output example:
```
## Triad Feature Status

**Claude Code Version**: 2.1.16
**Detection Method**: cli
**Full Features**: true

### Feature Flags

| Feature | Status | Required Version |
|---------|--------|------------------|
| Context Forking | true | v2.1.0+ |
| Parallel Execution | true | v2.1.16+ |
| Task Dependencies | true | v2.1.16+ |
| Graceful Degradation | true | v2.1.15+ |

### Execution Mode

**Recommended Mode**: parallel
```

---

## Upgrade Path

| Current Version | Target | Action |
|-----------------|--------|--------|
| < v2.1.15 | v2.1.16 | `claude upgrade` (recommended) |
| v2.1.15 | v2.1.16 | `claude upgrade` |
| v2.1.16+ | - | Already at recommended version |

---

## Related Documentation

- [Migration Guide](MIGRATION.md)
- [Version Detection Scripts](../../.claude/lib/version/)
- [Feature Flags Config](../../.claude/config/feature-flags.json)
