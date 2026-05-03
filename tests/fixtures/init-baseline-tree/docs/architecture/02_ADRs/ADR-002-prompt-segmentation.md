# ADR-002: Prompt Segmentation for Context Efficiency

**Status**: Accepted
**Date**: 2026-02-11
**Deciders**: Architect
**Feature**: 030 (Context Efficiency of /aod.run)

---

## Context

The `/aod.run` orchestrator skill (Feature 022) was implemented as a single monolithic SKILL.md file of 1,884 lines (~25,800 tokens). This entire file is loaded into the agent's context window at skill invocation, consuming approximately 13% of a 200K-token context budget before any work begins.

The orchestrator's content falls into two categories:

1. **Always-needed**: Core routing, state machine loop, stage mapping, display templates (~400 lines)
2. **Conditionally-needed**: Governance gate rules (only at stage boundaries), entry mode handlers (only one per invocation), dry-run logic (only with `--dry-run` flag), error recovery (only on corruption or lifecycle completion)

Loading conditionally-needed content upfront wastes context tokens that could otherwise be used for implementation work during the Build stage -- the longest and most context-intensive phase.

**Constraints**:
- The Claude Code Skill tool loads the SKILL.md file into context at invocation time
- The Read tool can load additional files on demand, and their content is evictable by the model
- Reference files must be co-located with the skill for discoverability
- All orchestrator behavior must be preserved exactly (no functional regression)
- Existing state files (pre-030) must remain compatible

---

## Decision

We will **segment the monolithic SKILL.md into a core file plus 4 on-demand reference files**, loaded via the Read tool only when their content is needed during orchestration.

The structure:

```
.claude/skills/~aod-run/
  SKILL.md                    (~405 lines, always loaded)
  references/
    governance.md             (~367 lines, loaded at governance gates)
    entry-modes.md            (~577 lines, loaded once per entry mode)
    dry-run.md                (~384 lines, loaded only with --dry-run)
    error-recovery.md         (~143 lines, loaded on error/completion)
```

The core SKILL.md contains a Navigation table mapping each section to its reference file, and MANDATORY Read instructions at each branch point where a reference file is needed.

---

## Rationale

**Reasons**:
1. **78% persistent context reduction**: Core SKILL.md drops from ~25,800 tokens to ~5,690 tokens, freeing ~20,110 tokens for Build stage work
2. **On-demand loading**: Reference files are loaded only when needed and are evictable from context after use, unlike the persistent SKILL.md
3. **Natural segmentation boundaries**: The content divides cleanly along functional lines (governance, entry modes, dry-run, error recovery) with minimal cross-references
4. **Zero functional regression**: All orchestrator behavior is preserved; content is relocated, not removed
5. **Re-grounding pattern**: MANDATORY Read instructions before each reference file use prevent template drift after variable-length governance output (KB Entry 9)
6. **Backward compatible**: No state file schema changes required; governance caching is additive

---

## Alternatives Considered

### Alternative 1: Keep Monolithic SKILL.md with Trimmed Content
**Pros**:
- Simplest approach (just remove verbose examples)
- No reference file management

**Cons**:
- Limited reduction potential; most content is procedural instructions, not examples
- Estimated savings: ~3,000-5,000 tokens (vs. ~20,110 with segmentation)
- Still loads all governance/dry-run/error content even when unused

**Why Not Chosen**: Insufficient savings. The problem is structural (always-loaded vs. conditionally-needed), not verbosity.

### Alternative 2: Multiple Separate Skills
**Pros**:
- Complete isolation of each concern
- Each skill has its own SKILL.md

**Cons**:
- Breaks the single-command orchestration model (`/aod.run` becomes multiple commands)
- State passing between skills adds complexity
- User experience degradation (must invoke separate skills for governance, recovery)
- Skill-to-skill invocation overhead

**Why Not Chosen**: Violates the core design principle of `/aod.run` as a single-command lifecycle orchestrator.

### Alternative 3: Parameterized Skill Loading (Framework Change)
**Pros**:
- Framework-level support for conditional SKILL.md sections
- No manual Read tool calls needed

**Cons**:
- Requires changes to the Claude Code Skill tool framework (not under our control)
- Non-standard; would break portability to other agent frameworks
- Speculative timeline for framework support

**Why Not Chosen**: Depends on external framework changes. The Read tool approach works today with existing capabilities.

---

## Consequences

### Positive
- ~20,110 tokens freed for Build stage implementation work
- Reference files can be independently maintained and versioned
- Re-grounding pattern prevents template drift after long governance output
- Governance caching further reduces reference file loads (cache hits skip reading governance.md)

### Negative
- Orchestrator logic is now spread across 5 files instead of 1
- MANDATORY Read instructions add procedural overhead to the SKILL.md
- Developers editing orchestrator behavior must identify the correct reference file
- Read tool invocations add minor latency (~100ms each)

### Mitigation
- Navigation table in SKILL.md maps every section to its reference file location
- MANDATORY annotations prevent skipping Read steps, ensuring correctness
- Reference files are named descriptively (governance.md, entry-modes.md, dry-run.md, error-recovery.md)
- Governance result caching reduces the frequency of governance.md reads

---

## Related Decisions

- ADR-001: Atomic State Persistence (state file format extended with `governance_cache`)
- ADR-019: Shared Cross-Agent Definitions and Model Field Governance (extends this pattern to cross-agent shared content and model assignment, Feature 078)
- Bash 3.2 compatibility constraint (compound helpers in run-state.sh, see KB Entry 6)

---

## References

- `.claude/skills/~aod-run/SKILL.md` -- Core orchestrator skill (post-segmentation)
- `.claude/skills/~aod-run/references/` -- On-demand reference files
- `.aod/scripts/bash/run-state.sh` -- Extended with compound helpers and governance cache functions
- `specs/030-prd-030-context/final-measurements.md` -- Token reduction measurements
