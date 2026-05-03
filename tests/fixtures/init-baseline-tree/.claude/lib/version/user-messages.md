# User Notification Messages for Unavailable Features

This file contains user-friendly messages displayed when AOD Kit features are unavailable due to Claude Code version constraints.

## Version Banner Messages

### Full Features (v2.1.16+)

```
✅ Claude Code v{VERSION} - Full Features Enabled
   • Context forking: Enabled (parallel reviews isolated)
   • Parallel execution: Enabled (faster Triad cycles)
   • Task dependencies: Enabled (automatic blocking)
```

### Limited Features (v2.1.15)

```
⚠️ Claude Code v{VERSION} - Limited Features

Some AOD Kit optimizations are unavailable:
   • Parallel execution: Disabled (reviews run sequentially)
   • Context forking: Disabled (shared context mode)

All workflows function correctly, just slower.
Run 'claude upgrade' for full features.
```

### Unknown Version

```
❓ Claude Code Version Unknown

Feature detection could not determine your Claude Code version.
Running in conservative mode with limited optimizations.

If you believe this is an error:
1. Check CLAUDECODE environment variable is set
2. Verify 'claude --version' works
3. Report issue at github.com/anthropics/claude-code/issues
```

## Feature-Specific Messages

### Context Forking Unavailable

```
⚠️ Context Forking Unavailable

Feature: Isolated context forks for parallel agent reviews
Required: Claude Code v2.1.0 or higher
Current: v{VERSION}

What this means:
- PM and Architect reviews share context
- Potential for context pollution between reviews
- Reviews still work, but isolation is not guaranteed

Fallback: Reviews will execute sequentially to avoid pollution.

To enable: Upgrade Claude Code with 'claude upgrade'
Docs: See docs/devops/MIGRATION.md for upgrade instructions
```

### Parallel Execution Unavailable

```
⚠️ Parallel Execution Limited

Feature: Parallel Task calls with memory leak fixes
Required: Claude Code v2.1.16 or higher
Current: v{VERSION}

What this means:
- PM and Architect reviews run sequentially (one after another)
- Triad review cycles take longer (5-7 min vs 3-4 min parallel)
- All functionality works, just slower

Impact: ~50% longer review cycles

To enable: Upgrade Claude Code with 'claude upgrade'
Docs: See docs/devops/MIGRATION.md for upgrade instructions
```

### Task Dependencies Unavailable

```
⚠️ Task Dependency Tracking Unavailable

Feature: Native task dependency enforcement
Required: Claude Code v2.1.16 or higher
Current: v{VERSION}

What this means:
- Task prerequisites not automatically enforced
- Manual coordination required for task ordering
- Risk of starting tasks before dependencies complete

Fallback: Use manual checklist verification before starting tasks.

To enable: Upgrade Claude Code with 'claude upgrade'
Docs: See docs/devops/MIGRATION.md for upgrade instructions
```

## Upgrade Recommendation

```
🔄 Upgrade Recommended

Current Claude Code: v{CURRENT_VERSION}
Recommended: v2.1.16+

Upgrade Benefits:
  ✅ Parallel Triad reviews (3-4 min vs 5-7 min)
  ✅ Context isolation (no cross-agent pollution)
  ✅ Memory leak fixes for long workflows
  ✅ Native task dependency support

How to upgrade:
  claude upgrade

After upgrade:
  1. Restart your terminal
  2. Run 'claude --version' to verify
  3. AOD Kit will auto-detect new features
```

## Session Start Banner

Display at the start of Triad commands:

```
╔══════════════════════════════════════════════════════════════╗
║                  SDLC Triad Governance                   ║
╠══════════════════════════════════════════════════════════════╣
║  Claude Code: v{VERSION}                                     ║
║  Features: {FEATURE_LIST}                                    ║
║  Execution: {PARALLEL|SEQUENTIAL}                            ║
╚══════════════════════════════════════════════════════════════╝
```

Example (full features):
```
╔══════════════════════════════════════════════════════════════╗
║                  SDLC Triad Governance                   ║
╠══════════════════════════════════════════════════════════════╣
║  Claude Code: v2.1.16                                        ║
║  Features: context_forking, parallel_execution, dependencies ║
║  Execution: PARALLEL                                         ║
╚══════════════════════════════════════════════════════════════╝
```

Example (limited):
```
╔══════════════════════════════════════════════════════════════╗
║                  SDLC Triad Governance                   ║
╠══════════════════════════════════════════════════════════════╣
║  Claude Code: v2.1.15                                        ║
║  Features: graceful_degradation (LIMITED MODE)               ║
║  Execution: SEQUENTIAL                                       ║
║                                                              ║
║  ⚠️ Run 'claude upgrade' for parallel execution              ║
╚══════════════════════════════════════════════════════════════╝
```
