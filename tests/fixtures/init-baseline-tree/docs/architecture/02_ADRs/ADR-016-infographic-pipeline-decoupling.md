# ADR-016: Infographic Pipeline Decoupling

**Status**: Accepted
**Date**: 2026-03-28
**Deciders**: Architect
**Feature**: 039 (Standalone Infographic Command)

---

## Context

Since Feature 018, infographic generation ran as Phase 6 of the orchestrator pipeline, dispatched automatically after Phase 5 (Report). This created three architectural problems:

1. **Tight coupling**: The orchestrator was the sole entry point for infographic generation. Users who wanted an infographic from an existing threat model had to re-run the full pipeline or manually invoke the agent -- there was no first-class standalone path.

2. **Stale data source**: Feature 035 introduced quantitative risk scoring (`risk-scores.md`), providing richer data than the qualitative `threats.md` that Phase 6 consumed. The pipeline-coupled infographic had no mechanism to prefer the scored data when available.

3. **Pipeline complexity**: The orchestrator carried Phase 6 dispatch logic, three opt-out mechanisms (`--skip-infographic`, `TACHI_SKIP_INFOGRAPHIC`, `infographic: false`), and Gemini API error handling -- all for a presentation enhancement orthogonal to the core threat analysis workflow.

Features 035 (risk scoring) and 036 (compensating controls) had already established the pattern of standalone post-pipeline commands (`/risk-score`, `/compensating-controls`) that operate on pipeline output independently.

---

## Decision

Extract infographic generation from the orchestrator pipeline into a standalone `/infographic` command. The orchestrator pipeline becomes a 5-phase pipeline (Phases 1-5). The `/infographic` command auto-detects the richest available data source (`risk-scores.md` preferred over `threats.md`), supports explicit file override, and template selection.

Key design choices:

1. **Standalone command pattern**: The `/infographic` command follows the same structure as `/risk-score` and `/compensating-controls` -- parse flags, detect input, invoke agent in fresh context, report results.

2. **Dual-path data extraction**: When `risk-scores.md` is available, the infographic agent reads quantitative composite scores from it and structural/spatial data from co-located `threats.md`. When only `threats.md` is available, the agent falls back to qualitative extraction (original Feature 018 behavior).

3. **Pipeline simplification**: The orchestrator removes Phase 6 dispatch, all infographic-related flags (`--skip-infographic`, `--infographic-template`), and the `TACHI_SKIP_INFOGRAPHIC` environment variable. A post-pipeline hint directs users to `/infographic`.

4. **Gemini API integration preserved**: The spec-first architecture and graceful degradation from ADR-014 remain unchanged. Only the invocation path changed (command instead of pipeline phase).

---

## Rationale

### Why decouple (not keep in pipeline)?

1. **Consistency**: `/risk-score` and `/compensating-controls` already established that post-analysis enhancements are standalone commands. Infographic generation is the same category -- a presentation enhancement consuming pipeline output. Keeping it as Phase 6 was an inconsistency.

2. **Richer data access**: The standalone command can auto-detect `risk-scores.md` and prefer it over `threats.md`. The pipeline-coupled Phase 6 could only receive `threats.md` because risk scoring runs after the pipeline completes.

3. **Reduced orchestrator complexity**: Removing Phase 6 dispatch, three opt-out mechanisms, and Gemini API error handling from the orchestrator reduces its surface area. The orchestrator focuses on its core mission: threat identification and assessment.

4. **Independent re-execution**: Users can re-generate infographics after updating risk scores or compensating controls without re-running the full threat analysis pipeline.

### Why auto-detect data source (not require explicit input)?

1. **Progressive enhancement**: Users who run `/infographic` after `/risk-score` automatically get the richer quantitative visualization. No additional flags or configuration needed.

2. **Backward compatibility**: Users who run `/infographic` directly after `/threat-model` (without risk scoring) get the original qualitative visualization. The command works at every point in the analysis workflow.

---

## Alternatives Considered

### Alternative 1: Keep Phase 6, Add Standalone Command as Duplicate Path

**Pros**:
- Backward compatible -- existing pipeline users unaffected
- Two entry points for maximum flexibility

**Cons**:
- Two code paths to maintain for the same functionality
- Phase 6 still limited to `threats.md` input (cannot access `risk-scores.md`)
- Opt-out flags remain in the orchestrator, adding complexity

**Why Not Chosen**: Maintaining dual invocation paths creates maintenance burden and user confusion without solving the stale data source problem.

### Alternative 2: Move to Phase 7, After Risk Scoring

**Pros**:
- Infographic would have access to `risk-scores.md` within the pipeline
- Single linear pipeline preserved

**Cons**:
- Requires risk scoring to be part of the pipeline (currently standalone)
- Would need to make Phase 6 = risk scoring, Phase 7 = infographic, creating a longer mandatory pipeline
- Violates the established pattern that post-analysis enhancements are standalone

**Why Not Chosen**: Would require restructuring the entire post-pipeline command architecture. The standalone pattern is already proven and preferred by users.

---

## Consequences

### Positive
- Orchestrator pipeline simplified to 5 phases focused on core threat analysis
- Infographic generation can leverage the richest available data source automatically
- Consistent command architecture: all post-analysis enhancements are standalone commands
- Independent re-execution without full pipeline re-runs
- Reduced orchestrator prompt size (removed Phase 6 dispatch and opt-out logic)

### Negative
- Users accustomed to automatic infographic generation after `/threat-model` must now run `/infographic` separately
- Post-pipeline hint in `/threat-model` output is advisory, not enforced

### Mitigation
- Clear post-pipeline hint in `/threat-model` output directs users to `/infographic`
- `/infographic` auto-detects data sources, requiring no additional configuration for basic usage

---

## Related Decisions

- [ADR-014: Gemini API Optional Image Generation](ADR-014-gemini-api-optional-image-generation.md) -- spec-first architecture and graceful degradation decisions remain in effect; Phase 6 dispatch and opt-out mechanisms superseded by this ADR
- [ADR-008: Opt-out Flag for Default-On Quality Gate Steps](ADR-008-opt-out-flag-for-default-quality-gates.md) -- `--skip-infographic` flag removed from orchestrator; no longer applicable to standalone command
- [ADR-011: Multi-Flag Opt-Out Pattern](ADR-011-multi-flag-opt-out-and-step-insertion-pattern.md) -- infographic opt-out removed from the multi-flag set

---

## References

- Feature 039 spec: `specs/039-standalone-infographic-command/spec.md`
- Feature 039 plan: `specs/039-standalone-infographic-command/plan.md`
- Standalone command: `.claude/commands/infographic.md`
- Infographic agent: `.claude/agents/tachi/threat-infographic.md`
- Infographic schema: `schemas/infographic.yaml` (unchanged)
