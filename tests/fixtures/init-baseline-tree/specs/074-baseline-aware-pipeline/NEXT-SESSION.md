# Session Continuation: Baseline-Aware Pipeline

**Generated**: 2026-04-01 (session 2)
**Branch**: 074-baseline-aware-pipeline
**Last Commit**: b9a7bba docs(075): update CHANGELOG (#77)

## Completed This Session

### Wave 3: Story Entry Points (T013, T016, T031)
- T013: Enhanced RESOLVED detection in orchestrator.md Phase 1a (component removal, rename, partial fix)
- T016: Isolated discovery context in orchestrator.md Phase 2 (anchoring bias prevention)
- T031: Governance field carry-forward in risk-scorer.md Section 8 (SLA recalculation triggers)

### Wave 4: Story Completion (T014-T020, T032)
- T014: RESOLVED findings section (4b) in threats.md template
- T015: Delta summary output in orchestrator.md Phase 5
- T017: Phase 3a merge/dedup algorithm in orchestrator.md (Levenshtein similarity, >80% threshold)
- T018: Bounded scoring for NEW findings in risk-scorer.md Section 3
- T019: Score bounding specification in tachi-risk-scoring SKILL.md
- T020: Deterministic similarity algorithm in tachi-orchestration SKILL.md
- T032: Governance persistence rules in tachi-risk-scoring SKILL.md

### P1 Checkpoint: APPROVED_WITH_CONCERNS (resolved)
- C-1 Fixed: Aligned similarity formula between orchestrator.md and SKILL.md (character-level Levenshtein)
- C-2 Fixed: Aligned bounded scoring table to 8 canonical categories matching risk-scoring.yaml

### Wave 5: Delta Annotations + SARIF (T021-T026, T035)
- T021: Status column in all STRIDE and AI threat tables in threats.md
- T022: Score source column + baseline frontmatter in risk-scores.md
- T023: Carry-forward indicator + rescan_scope in compensating-controls.md
- T024: baselineState + baselineRunId in threats.sarif
- T025: score-source + baseline-state in risk-scores.sarif
- T026: control-carry-forward in compensating-controls.sarif
- T035: baselineState documentation in SARIF specification reference

## Current State

- **Phase**: implement
- **Uncommitted**: 22 files (18 modified + 4 new — all work from Waves 0-5)
- **Tasks**: 29/36 complete (81%)
- **Waves Complete**: 0-5 (of 0-8)
- **Checkpoints**: P0 APPROVED, P1 APPROVED_WITH_CONCERNS (concerns resolved)

## Remaining Tasks (7)

### Wave 6: Coverage Gate Core (US5) — Sequential
- T027: Coverage gate in orchestrator.md Phase 4
- T028: Targeted re-analysis dispatch in orchestrator.md

### Wave 7: Coverage Gate Templates (US5) — Parallel
- T029: Coverage gate results section in threats.md template
- T030: Coverage gate orchestration rules in SKILL.md

### Wave 8: Validation — Sequential then Parallel
- T033: Validate against second-brain-mcp (zero drift + delta annotations)
- T034: Validate against agentic-app (coverage gate for LLM/MCP)
- T036: Run quickstart.md validation scenarios (7 test scenarios)

## Next Actions

1. **Commit current work** — 22 files uncommitted from Waves 0-5
2. **Wave 6** (T027-T028): Coverage gate implementation in orchestrator.md
3. **Wave 7** (T029-T030): Coverage gate templates and skill rules
4. **P2 Checkpoint** after Wave 7 (non-blocking)
5. **Wave 8** (T033-T036): End-to-end validation
6. Final validation (Step 5), security scan (Step 6), `/aod.deliver`

## Key Decisions Made

Sessions 1+2 combined:
- `findingId/v1` is PRIMARY correlation key; `primaryLocationLineHash` is validation signal only
- Schema versions bumped 1.0->1.1
- Similarity: normalized Levenshtein on sorted, preprocessed tokens (character-level on joined strings)
- Bounded scoring uses 8 canonical categories (S/T/R/I/D/E/AG/LLM) not 11 sub-categories
- SARIF `baselineState` maps RESOLVED -> `absent` per SARIF 2.1.0 convention
- risk_owner is NEVER auto-overwritten (human-assigned field)
- SLA recalculation triggers only on severity band change

## Context Files

- `specs/074-baseline-aware-pipeline/tasks.md` — task list with progress
- `specs/074-baseline-aware-pipeline/agent-assignments.md` — wave definitions
- `specs/074-baseline-aware-pipeline/plan.md` — technical design
- `specs/074-baseline-aware-pipeline/spec.md` — requirements
- `specs/074-baseline-aware-pipeline/data-model.md` — schema extensions
- `specs/074-baseline-aware-pipeline/checkpoint-p1.md` — P1 architect review

## Resume Command

```bash
claude "Resume Baseline-Aware Pipeline (branch: 074-baseline-aware-pipeline). Waves 0-5 complete (29/36 tasks). P1 checkpoint APPROVED. Run /aod.build to continue with Wave 6."
```
