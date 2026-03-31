# Session Continuation: Tachi Agent Best Practices

**Generated**: 2026-03-31 (session 1)
**Branch**: 075-tachi-agent-best
**Last Commit**: a330a6b fix(071): enforce score-derived severity bands and remove Gemini fallback

## Completed This Session

### Wave 1: Baseline Capture (T001-T002)
- Recorded baseline line counts for all 18 tachi agents
- Captured pre-extraction pipeline output checksums to `specs/075-tachi-agent-best/baseline-output/`

### Wave 2: Skill Extraction + Leaf/Report Tone Audit (T003-T006, T008-T011, T013-T016, T019-T021)
- Created 3 skill packages with SKILL.md + 3 reference files each:
  - `.claude/skills/tachi-orchestration/` (sarif-specification 498L, dispatch-rules 244L, output-schemas 498L)
  - `.claude/skills/tachi-risk-scoring/` (scoring-dimensions 256L, cvss-vectors 74L, severity-bands 195L)
  - `.claude/skills/tachi-control-analysis/` (control-categories 249L, evidence-criteria 117L, residual-risk 171L)
- Tone-audited 6 STRIDE leaf agents (no tone changes needed, added `tools:` frontmatter)
- Tone-audited 5 AI leaf agents (softened 1 MUST each, added `tools:`, improved descriptions)
- Tone-audited 2 report agents (softened 4 instances in threat-infographic, added `tools:`)

### P0 Checkpoint: APPROVED_WITH_CONCERNS
- C1 (fixed): Normalized `extracted_from` frontmatter paths to full relative paths
- C2 (noted): Two reference files at 498/500 lines -- do not add content

### Wave 3: Agent Refactoring + Threat-Report Trim (T007, T012, T017, T024)
- Refactored orchestrator.md: 2,000 -> 769 lines (removed extracted domain knowledge, added Skill References section)
- Refactored risk-scorer.md: 1,419 -> 994 lines (removed extracted content + Metadata block, added Skill References)
- Refactored control-analyzer.md: 1,367 -> 935 lines (removed extracted content, added Skill References)
- Trimmed threat-report.md: 801 -> 800 lines (removed 1 non-functional blank line)

## Current State

- **Phase**: implement
- **Uncommitted**: 28 items (17 modified agent files, 3 new skill directories, spec/plan/task artifacts, best practices doc)
- **Tasks**: 21/29 complete
- **Post-refactor line counts**:
  - orchestrator.md: 769 (cap: 1,000)
  - risk-scorer.md: 994 (cap: 1,000)
  - control-analyzer.md: 935 (cap: 1,000)
  - threat-report.md: 800 (cap: 800)

## Next Actions

### Wave 4: Post-Extraction Verification + Methodology Tone Audit (4 tasks)
1. **T018** [tester]: Verify all 3 methodology agents <=1,000 lines and no content duplication between agents and skill reference files
2. **T022** [senior-backend-engineer]: Tone audit 3 methodology agents (post-extraction) -- review emphasis patterns, verify data-top ordering
3. **T023** [senior-backend-engineer]: Tone audit threat-report agent -- soften emphasis, add tool restrictions, verify data-top ordering
4. **T025** [tester]: Verify threat-report.md <=800 lines

### Wave 5: Validation + Compliance (4 tasks)
5. **T026** [tester]: Run full pipeline on example architecture and compare against baseline checksums
6. **T027** [tester]: Verify all 18 agents within tier caps (batch wc -l)
7. **T028** [code-reviewer]: Verify all 18 agents pass 8-criterion quality checklist
8. **T029** [senior-backend-engineer]: Update compliance table in `_TACHI_AGENT_BEST_PRACTICES.md`

### After Wave 5
- P1 Checkpoint: Architect review (blocking)
- Final Validation (Step 5): Architect + Code Review + Security
- Security Scan (Step 6)
- Completion Report (Step 7)
- `/aod.deliver` then `/aod.document`

## Key Context

- All changes are uncommitted -- commit before resuming to create a save point
- `extracted_from` paths in all 9 reference files have been normalized to full relative paths (C1 fix)
- Two reference files (sarif-specification.md, output-schemas.md) are at 498/500 lines -- do not add content (C2)
- risk-scorer.md Metadata block was removed to bring it under 1,000 cap (was at 1,014 after extraction)
- Stack pack `knowledge-system` is active (`.aod/stack-active.json`)
- Feature type: docs-only (markdown/YAML editing, zero application code)

## Context Files

- `specs/075-tachi-agent-best/tasks.md` -- task list with progress markers
- `specs/075-tachi-agent-best/agent-assignments.md` -- agent-to-task mapping and wave definitions
- `specs/075-tachi-agent-best/plan.md` -- implementation plan
- `specs/075-tachi-agent-best/spec.md` -- feature specification
- `specs/075-tachi-agent-best/baseline-output/` -- pre-extraction checksums and line counts
- `.aod/results/architect-p0-checkpoint.md` -- P0 review details
- `.claude/agents/tachi/_TACHI_AGENT_BEST_PRACTICES.md` -- best practices doc (compliance table needs updating in T029)

## Resume Command

```bash
claude "Resume Feature 075 Tachi Agent Best Practices (branch: 075-tachi-agent-best). Waves 1-3 complete (21/29 tasks). Run /aod.build to continue with Wave 4."
```
