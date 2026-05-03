# Migrating to Claude Code v2.1.16+ Features

This guide helps you upgrade Agentic Oriented Development Kit to leverage Claude Code v2.1.16 features for improved Triad governance workflows.

## Overview

Claude Code v2.1.16 introduces powerful new capabilities that Triad can leverage:

- **Parallel Execution**: Run PM and Architect reviews simultaneously
- **Context Forking**: Isolate agent contexts to prevent pollution
- **Memory Leak Fixes**: Stable long-running parallel workflows

**Impact**: ~50% faster Triad review cycles with improved reliability.

---

## Prerequisites

- Existing Agentic Oriented Development Kit installation
- Access to upgrade Claude Code

---

## Quick Start (5 minutes)

### Step 1: Check Current Version

```bash
claude --version
```

If you see `v2.1.16` or higher, you already have full features! Skip to [Verify Features](#step-4-verify-features).

### Step 2: Upgrade Claude Code

```bash
claude upgrade
```

### Step 3: Restart Terminal

Close and reopen your terminal to ensure environment variables are refreshed.

### Step 4: Verify Features

Run the Triad feature check:

```bash
source .claude/lib/version/detect.sh
source .claude/lib/version/feature-flags.sh

echo "Version: $AOD_CLAUDE_VERSION"
echo "Full Features: $AOD_FULL_FEATURES"
echo "Parallel Execution: $AOD_FEATURE_PARALLEL_EXECUTION"
echo "Context Forking: $AOD_FEATURE_CONTEXT_FORKING"
```

Expected output for v2.1.16+:
```
Version: 2.1.16
Full Features: true
Parallel Execution: true
Context Forking: true
```

---

## Feature Availability Matrix

| Feature | v2.1.15 (Limited) | v2.1.16+ (Full) |
|---------|-------------------|-----------------|
| Context Forking | ❌ Shared context | ✅ Isolated forks |
| Parallel Reviews | ❌ Sequential | ✅ Parallel |
| Memory Leak Fixes | ❌ Known issues | ✅ Fixed |
| Task Dependencies | ❌ Manual | ✅ Automated |
| Triad Cycle Time | 5-7 min | 3-4 min |

---

## What Changes After Upgrade

### Before (v2.1.15)

```
/aod.project-plan
  └─► PM Review (2-3 min)
       └─► Architect Review (2-3 min)
            └─► Complete (5-7 min total)
```

PM and Architect reviews run sequentially. Context is shared between agents.

### After (v2.1.16+)

```
/aod.project-plan
  ├─► PM Review (2-3 min)     ─┬─► Merge Results
  └─► Architect Review (2-3 min)  │
                                   └─► Complete (3-4 min total)
```

PM and Architect reviews run in parallel with isolated contexts. Results merge automatically.

---

## Backward Compatibility

Triad maintains full backward compatibility with v2.1.15:

- **All workflows continue to work**: `/aod.spec`, `/aod.project-plan`, `/aod.tasks`, `/aod.build`
- **Automatic detection**: Triad detects your Claude Code version at runtime
- **Graceful degradation**: Unavailable features fall back to sequential execution
- **Clear messaging**: Users see informative messages about limited functionality

### Degradation Behavior

| If Missing | Fallback Behavior |
|------------|-------------------|
| Parallel Execution | Sequential reviews (PM → Architect → Tech-Lead) |
| Context Forking | Shared context (risk of pollution) |
| Task Dependencies | Manual coordination required |

---

## Troubleshooting

### Version Not Detected

**Symptom**: `AOD_CLAUDE_VERSION=unknown`

**Cause**: CLAUDECODE environment variable not set.

**Solution**:
1. Ensure you're running inside Claude Code
2. Check: `echo $CLAUDECODE`
3. If empty, restart Claude Code

### Features Still Disabled After Upgrade

**Symptom**: `AOD_FULL_FEATURES=false` after upgrading

**Solutions**:
1. Restart your terminal
2. Verify version: `claude --version` shows 2.1.16+
3. Re-source the detection scripts
4. Check for environment overrides: `env | grep AOD`

### Parallel Reviews Not Running

**Symptom**: Reviews still run sequentially

**Cause**: Feature flag disabled or version detection failed.

**Solution**:
1. Verify: `echo $AOD_FEATURE_PARALLEL_EXECUTION`
2. If `false`, check version detection
3. Manual override (testing only): `export AOD_FEATURE_PARALLEL_EXECUTION=true`

### Memory Issues During Long Workflows

**Symptom**: Claude Code slows down or crashes during >30 min workflows

**Cause**: Memory leak in v2.1.15

**Solution**: Upgrade to v2.1.16+ which includes memory leak fixes

---

## Rollback Instructions

If you need to revert to v2.1.15 behavior:

### Option 1: Disable Features (Keep v2.1.16)

```bash
# Add to your shell profile or .env
export AOD_FEATURE_PARALLEL_EXECUTION=false
export AOD_FEATURE_CONTEXT_FORKING=false
```

### Option 2: Downgrade Claude Code

```bash
# Not recommended - loses bug fixes
# Contact Anthropic support if truly necessary
```

**Recommendation**: Use Option 1 to disable specific features while keeping v2.1.16 bug fixes.

---

## Technical Details

### Version Detection Method

Triad detects Claude Code version using:

1. **CLAUDECODE env var**: Presence indicates running in Claude Code
2. **CLI parsing**: `claude --version` output is parsed
3. **Fallback**: If detection fails, assumes v2.1.15 (conservative)

### Feature Flags

Feature flags are computed at script load time:

```bash
# .claude/lib/version/feature-flags.sh
AOD_FEATURE_CONTEXT_FORKING=true   # v2.1.0+
AOD_FEATURE_PARALLEL_EXECUTION=true # v2.1.16+
AOD_FEATURE_TASK_DEPENDENCIES=true  # v2.1.16+
AOD_FEATURE_GRACEFUL_DEGRADATION=true # Always
```

### Skill Context Configuration

Forked context skills use this frontmatter:

```yaml
---
context: fork
agent: Explore
---
```

- `context: fork` - Creates isolated execution context
- `agent: Explore` - Uses fast, read-only agent for reviews

---

## FAQ

**Q: Do I need to change my workflow commands?**

A: No. All `/aod.*` commands work identically. Triad automatically uses the best available features.

**Q: Will old specs/plans/tasks still work?**

A: Yes. All existing artifacts are fully compatible.

**Q: Can I use v2.1.16 features in CI/CD?**

A: Yes, as long as Claude Code v2.1.16+ is installed in your CI environment.

**Q: What if team members have different versions?**

A: Each user's Triad instance detects their local version. Artifacts are version-agnostic.

---

## Related Documentation

- [Feature Flags Configuration](.claude/config/feature-flags.json)
- [Version Detection Scripts](.claude/lib/version/)
- [Triad Governance Rules](.claude/rules/governance.md)
- [AOD Kit Quick Reference](docs/AOD_TRIAD.md)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-24 | Initial migration guide for v2.1.16 features |
