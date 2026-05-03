# ADR-005: Sequential Triad Review Execution Trade-off

**Status**: Accepted
**Date**: 2026-02-13
**Decision Maker**: Architect
**Feature**: 047-optimize-define-plan-stages
**Implementation**: Core Loop step 9 (serialized review execution)

## Context

The current Triad review workflow executes reviewer agents (PM, Architect, Team-Lead) in parallel using context forking. While parallelization reduces wall-clock time, it creates significant context window pressure:

- **Parallel review context cost**: ~18K tokens loaded simultaneously (3 reviewer contexts at ~6K each)
- **Context window constraint**: With parallel execution, the orchestrator must maintain multiple concurrent contexts, consuming a substantial portion of the available context window
- **Single-session priority**: Per the PRD priority stack (Quality > Few Pauses > Speed), users prioritize completing features in a single session over minimizing wall-clock time

**The Trade-off**: Parallel reviews optimize for wall-clock speed but consume more concurrent context. Sequential reviews optimize for context efficiency but increase elapsed time.

## Decision

**Execute Triad reviews sequentially instead of in parallel.**

### Implementation Approach

1. **Sequential review order**: PM -> Architect -> Team-Lead (for tasks.md triple review)
2. **Context savings**: Sequential execution saves ~6K tokens per review cycle by not loading all reviewer contexts simultaneously
3. **Reviewer context isolation**: Each reviewer loads, executes, and unloads before the next reviewer starts

### Trade-off Analysis

| Dimension | Parallel | Sequential |
|-----------|----------|------------|
| Concurrent context | ~18K tokens | ~6K tokens |
| Context savings | Baseline | 60% reduction |
| Wall-clock time | Baseline | +15-20 seconds per cycle |
| Single-session viability | Lower | Higher |

## Alternatives Considered

### Alternative 1: Keep Parallel Reviews (Status Quo)

**Description**: Maintain current parallel review execution with context forking.

**Pros**:
- Faster wall-clock time
- Reviews complete simultaneously
- Optimizes for speed

**Cons**:
- High concurrent context consumption (~18K tokens)
- Increases session break probability
- Conflicts with PRD priority stack (Quality > Few Pauses > Speed)

**Why Not Chosen**: The 15-20 second time savings is not worth the 60% higher context consumption when users prioritize single-session completion.

### Alternative 2: Hybrid Approach (Parallel PM+Architect, Then Team-Lead)

**Description**: Run PM and Architect reviews in parallel, then Team-Lead sequentially.

**Pros**:
- Partial time savings
- Moderate context reduction

**Cons**:
- Complexity of mixed execution modes
- Still consumes ~12K concurrent for PM+Architect
- Marginal benefit over full sequential

**Why Not Chosen**: Hybrid complexity is not justified by the marginal improvement. Full sequential provides cleaner implementation and maximum context savings.

### Alternative 3: On-Demand Context Loading

**Description**: Load reviewer context only when needed, unload immediately after.

**Pros**:
- Maximum context efficiency
- Dynamic resource management

**Cons**:
- Requires agent lifecycle management infrastructure
- Not supported by current Claude Code architecture
- Implementation complexity exceeds benefit

**Why Not Chosen**: Current agent architecture does not support dynamic context loading/unloading. Sequential execution achieves similar benefits with existing capabilities.

## Consequences

### Positive

1. **60% concurrent context reduction**: From ~18K to ~6K tokens during reviews
2. **Enables single-session lifecycle**: Lower concurrent context increases probability of completing define/plan stages without session breaks
3. **Aligns with PRD priority stack**: Optimizes for "Few Pauses" over "Speed" per user preferences
4. **Simpler error handling**: Sequential execution provides clearer failure points
5. **Predictable resource consumption**: Easier to estimate context requirements per stage

### Negative

1. **15-20 seconds longer per review cycle**: Triple review (tasks.md) adds ~45-60 seconds total
2. **No parallel efficiency**: Cannot leverage context forking benefits when available
3. **Blocking failure mode**: If PM review fails, Architect review cannot proceed (unlike parallel where all reviews attempt)

### Mitigation

- 15-20 second delay is acceptable per PRD priority analysis (users prefer completion over speed)
- Context forking remains available for other use cases (e.g., parallel file reads)
- Sequential failure mode actually improves efficiency by stopping early on first rejection

## Implementation Details

### Location

Core Loop step 9 in `.claude/skills/~aod-run/SKILL.md`

### Serialization Algorithm

1. **Sequential execution order**: PM -> Architect -> Team-Lead
2. **Context clearing between reviewers**: Re-read `references/governance.md` after each reviewer output (per KB Entry 9 pattern)
3. **Cache each verdict**: Call `aod_state_cache_governance` after each individual reviewer completes
4. **Early termination**: Stop on first CHANGES_REQUESTED or BLOCKED; do not invoke remaining reviewers
5. **Same criteria**: Identical reviewers, checklists, and approval criteria as parallel execution

### Wall-Clock Time Measurement

| Artifact | Reviewers | Parallel Time | Sequential Time | Delta |
|----------|-----------|---------------|-----------------|-------|
| spec.md | PM only | ~5s | ~5s | +0s |
| plan.md | PM + Architect | ~8s | ~15s | +7s |
| tasks.md | PM + Architect + Team-Lead | ~10s | ~25s | +15s |
| **Total per lifecycle** | -- | ~23s | ~45s | **+22s** |

### Re-Grounding Pattern

After each reviewer's output is processed, the orchestrator re-reads `references/governance.md` before invoking the next reviewer. This prevents template drift from variable-length reviewer feedback (KB Entry 9 pattern).

## References

- PRD: `docs/product/02_PRD/047-optimize-define-plan-stages-2026-02-13.md`
- Spec: `specs/047-optimize-define-plan-stages/spec.md`
- Plan: `specs/047-optimize-define-plan-stages/plan.md`
- Governance Rules: `.claude/rules/governance.md`
