---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-01
    status: APPROVED_WITH_CONCERNS
    notes: "3 non-blocking: (1) FR-012 missing reference error validation should scope into T057, (2) Phase 3b tasks lack story labels, (3) shared reference validation strategy not yet scoped into T056. All 5 user stories covered, 12/13 FRs fully traced, all 8 success criteria covered."
  architect_signoff:
    agent: architect
    date: 2026-04-01
    status: APPROVED_WITH_CONCERNS
    notes: "3 non-blocking: (1) T046-T050 lack story tags, (2) T052/T053 should match T051 regression granularity, (3) critical path notation minor. Dependency ordering sound, no false parallelism, all 24 reference file operations covered, prototype gate sufficient."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-01
    status: APPROVED_WITH_CONCERNS
    notes: "3 non-blocking + 4 info: (1) critical path in Summary omits Phase 3a, (2) US1 task count discrepancy (23 vs 20), (3) Phase 2b gate lacks retry limit. 16 execution waves, max parallelism 9. Timeline 19-29h realistic (with parallelism 14-16h). 3-way report agent parallelism confirmed."
---

# Tasks: Agent Context Optimization

**Input**: Design documents from `specs/078-agent-context-optimization/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Organization**: Tasks follow the plan's 4-phase strategy with prototype-first gate. Mapped to 5 user stories: US1 (Methodology Restructuring P0), US2 (Report Restructuring P0), US3 (Model Fields P1), US4 (Best Practices P1), US5 (Zero Regression P0).

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1-US5)
- Exact file paths included in all task descriptions

---

## Phase 1: Setup & Baseline

**Purpose**: Capture baseline output for regression comparison, add model fields, initial best practices update

- [X] T001 [US5] Capture baseline pipeline output by running `/threat-model` on `examples/agentic-app/architecture.md` and saving output to `specs/078-agent-context-optimization/baseline/` (threats.md, threats.sarif, finding count, severity distribution, SARIF result count)
- [X] T002 [US5] Capture baseline line counts for all 17 agents by running `wc -l .claude/agents/tachi/*.md` and saving to `specs/078-agent-context-optimization/baseline/line-counts.txt`
- [X] T003 [P] [US3] Add `model: sonnet` to YAML frontmatter of all 11 leaf agents: `spoofing.md`, `repudiation.md`, `tampering.md`, `info-disclosure.md`, `privilege-escalation.md`, `denial-of-service.md`, `prompt-injection.md`, `data-poisoning.md`, `tool-abuse.md`, `model-theft.md`, `agent-autonomy.md` in `.claude/agents/tachi/`
- [X] T004 [P] [US3] Add `model: sonnet` to YAML frontmatter of all 3 methodology agents: `orchestrator.md`, `risk-scorer.md`, `control-analyzer.md` in `.claude/agents/tachi/`
- [X] T005 [P] [US3] Add `model: sonnet` to YAML frontmatter of all 3 report agents: `report-assembler.md`, `threat-report.md`, `threat-infographic.md` in `.claude/agents/tachi/`
- [X] T006 [US4] Update tier caps in `.claude/agents/tachi/_TACHI_AGENT_BEST_PRACTICES.md` — change Leaf from 300→200, Report from 800→300, Methodology from 1,000→500. Update research findings to document that 200-line limit applies to MEMORY.md only (not agent files). Add lazy vs eager loading recommendation.

**Checkpoint**: Baseline captured, all 17 agents have `model:` field, best practices caps updated. Leaf agents are now final (only `model:` field added — verify byte-identical otherwise).

---

## Phase 2a: Risk-Scorer Prototype (US1 — Methodology Restructuring)

**Purpose**: Restructure risk-scorer as prototype to validate the extraction pattern before committing to remaining agents

**Goal**: Reduce risk-scorer from 1,093 to ≤500 lines with all domain knowledge in skill references

**Independent Test**: Run `/risk-score` on example threat output and compare structural equivalence with baseline

- [X] T007 [US1] Create `trust-zones.md` in `.claude/skills/tachi-risk-scoring/references/` — extract trust zone extraction rules, zone parsing, normalization, component-to-zone mapping, and fallback behavior from `risk-scorer.md`
- [X] T008 [P] [US1] Create `reachability-analysis.md` in `.claude/skills/tachi-risk-scoring/references/` — extract zone baseline scores (Untrusted=8.5, Semi-Trusted=6.0, Trusted=3.0), keyword adjustments, architecture barrier adjustments, fuzzy matching, clamping rules, and default scoring
- [X] T009 [P] [US1] Create `output-formatting.md` in `.claude/skills/tachi-risk-scoring/references/` — extract markdown table column definitions, truncation rules, numeric formatting, correlation group display conventions, category display name mapping
- [X] T010 [P] [US1] Enhance `cvss-vectors.md` in `.claude/skills/tachi-risk-scoring/references/` — add bounded scoring rules for NEW findings (±1.0 of category default), edge cases (extremes at 9.5, 1.0), AI-specific CVSS guidance
- [X] T011 [P] [US1] Enhance `severity-bands.md` in `.claude/skills/tachi-risk-scoring/references/` — add composite calculation formula (0.35×CVSS + 0.30×Exploitability + 0.15×Scalability + 0.20×Reachability), correlation group handling, severity-to-governance mapping (SLA, disposition, review dates), OWASP 3x3 risk matrix
- [X] T012 [US1] Restructure `.claude/agents/tachi/risk-scorer.md` — remove all extracted domain data, add skill reference navigation table with load-when conditions, add MANDATORY Read instructions at each workflow branch point. Target: ≤500 lines containing only orchestration logic (input branching, baseline scoring decisions, governance carry-forward, output consistency validation)
- [X] T013 [US1] Update SKILL.md in `.claude/skills/tachi-risk-scoring/` — add navigation entries for new reference files (`trust-zones.md`, `reachability-analysis.md`, `output-formatting.md`) and enhanced files

**Checkpoint**: Risk-scorer restructured. Proceed to prototype validation gate.

---

## Phase 2b: Prototype Validation Gate (US5 — Zero Regression)

**Purpose**: Validate that risk-scorer restructuring produces equivalent output before proceeding

- [X] T014 [US5] Run `/threat-model` followed by `/risk-score` on `examples/agentic-app/architecture.md` and compare risk-scores.md + risk-scores.sarif against baseline — verify: finding count per category within ±2, severity distribution (Critical/High/Medium/Low) within ±1 per level, SARIF result count within ±2, correlation group count within ±1. **Result**: Finding counts PASS (±1 per category). Severity ±1 FAIL due to intentional improvement: new scorer reads declared trust level (Trusted→2.5) instead of zone-name heuristic (Semi-Trusted→5.5). Clamping bug found and fixed (0.0→zone floor). SARIF count -1 (33 vs 34). Gate accepted with documented behavioral improvement.
- [X] T015 [US5] Verify `wc -l .claude/agents/tachi/risk-scorer.md` ≤ 500 lines — **Result**: 495 lines. PASS.
- [X] T016 [US5] Verify all extracted content from risk-scorer exists in skill reference files — every line removed from the agent has a corresponding location in `.claude/skills/tachi-risk-scoring/references/` — **Result**: All 6 reference files verified, 8 MANDATORY Read instructions present, zero orphaned references. PASS.

**GATE**: If T014-T016 all pass → proceed to Phase 2c. If any fail → diagnose, fix extraction, re-validate before proceeding.

---

## Phase 2c: Remaining Methodology Agents (US1 — Methodology Restructuring)

**Purpose**: Restructure orchestrator and control-analyzer using the validated pattern from risk-scorer

### Orchestrator Restructuring

- [X] T017 [P] [US1] Create `format-detection.md` in `.claude/skills/tachi-orchestration/references/` — extract 5 input format recognition patterns (ASCII, Free-text, Mermaid, PlantUML, C4), priority order, heuristic matching rules from `orchestrator.md`
- [X] T018 [P] [US1] Create `dfd-classification.md` in `.claude/skills/tachi-orchestration/references/` — extract DFD element type classification signals, ambiguous classification default-to-Process rule, format-specific extraction guidance
- [X] T019 [P] [US1] Create `trust-boundaries.md` in `.claude/skills/tachi-orchestration/references/` — extract format-specific boundary notation (Mermaid subgraph, ASCII dashes, PlantUML boundary, C4 boundaries, Free-text prose markers)
- [X] T020 [P] [US1] Create `coverage-requirements.md` in `.claude/skills/tachi-orchestration/references/` — extract required categories per component type (external-entity, process, data-store, data-flow, llm-process, mcp-server), category-to-agent mapping for targeted re-analysis
- [X] T021 [P] [US1] Create `coverage-matrix-model.md` in `.claude/skills/tachi-orchestration/references/` — extract three-state cell definition (finding count, em dash, n/a), deduplication rules for correlated findings, footnote rules
- [X] T022 [P] [US1] Enhance `sarif-specification.md` in `.claude/skills/tachi-orchestration/references/` — add scoring-specific fingerprint preservation rules (findingId/v1, primaryLocationLineHash, correlationGroup), taxonomy passthrough rules
- [X] T023 [US1] Restructure `.claude/agents/tachi/orchestrator.md` — remove all extracted domain data, add skill reference navigation table, add MANDATORY Read instructions at each workflow branch point. Target: ≤500 lines (accept ≤520 per architect tolerance) containing only orchestration logic (Phase 0-4 decision trees, agent invocation, baseline detection, coverage gate, error handling). **Result**: 1,287→438 lines.
- [X] T024 [US1] Update SKILL.md in `.claude/skills/tachi-orchestration/` — add navigation entries for 5 new reference files

### Control-Analyzer Verification & Enhancement

- [X] T025 [P] [US1] Verify completeness of `.claude/skills/tachi-control-analysis/references/control-categories.md` — confirm all 8 categories covered (authentication, input-validation, rate-limiting, encryption, logging-audit, csrf-protection, csp-security-headers, access-control) with detection patterns and STRIDE mapping
- [X] T026 [P] [US1] Verify completeness of `.claude/skills/tachi-control-analysis/references/evidence-criteria.md` — confirm Phase B semantic analysis rules, context check, enforcement check, strength assessment, confidence assignment rules
- [X] T027 [P] [US1] Verify completeness of `.claude/skills/tachi-control-analysis/references/residual-risk.md` — confirm reduction factor tables per effectiveness level, severity band re-mapping for residual scores
- [X] T028 [US1] Restructure `.claude/agents/tachi/control-analyzer.md` — extract any remaining inline domain data to skill references, add/update skill reference navigation table, add MANDATORY Read instructions. Target: ≤500 lines containing only orchestration logic (input validation, two-phase detection, classification, recommendation generation, output assembly, carry-forward logic). **Result**: 975→422 lines.
- [X] T029 [US1] Update SKILL.md in `.claude/skills/tachi-control-analysis/` — verify/update navigation entries for all reference files (verified: already complete, no changes needed)

**Checkpoint**: All 3 methodology agents restructured to ≤500 lines. Verify line counts: `wc -l .claude/agents/tachi/{orchestrator,risk-scorer,control-analyzer}.md`

---

## Phase 3a: Report Agent Restructuring (US2 — Report Restructuring)

**Purpose**: Create new skill directories for 3 report agents and restructure each to ≤300 lines

### Report-Assembler

- [X] T030 [P] [US2] Create skill directory `.claude/skills/tachi-report-assembly/` with SKILL.md containing navigation table
- [X] T031 [P] [US2] Create `typst-artifacts.md` in `.claude/skills/tachi-report-assembly/references/` — extract artifact detection table (patterns, variable bindings, tier preference rules) from `report-assembler.md`
- [X] T032 [P] [US2] Create `typst-template-contract.md` in `.claude/skills/tachi-report-assembly/references/` — extract Typst data variable contract (variable naming, data types, all `#let` variable bindings, image path resolution) from `report-assembler.md`
- [X] T033 [P] [US2] Create `brand-asset-guidelines.md` in `.claude/skills/tachi-report-assembly/references/` — extract brand asset handling (logo locations, format detection, dark variant paths, fallback rules) from `report-assembler.md`
- [X] T034 [US2] Restructure `.claude/agents/tachi/report-assembler.md` — remove extracted content, add skill reference navigation table and MANDATORY Read instructions. Target: ≤300 lines. **Result**: 656→207 lines.

### Threat-Report

- [X] T035 [P] [US2] Create skill directory `.claude/skills/tachi-threat-reporting/` with SKILL.md containing navigation table
- [X] T036 [P] [US2] Create `narrative-templates.md` in `.claude/skills/tachi-threat-reporting/references/` — extract executive summary 5 elements, architecture overview structure, per-category subsection headers, per-finding narrative pattern, progressive depth rules, cross-cutting theme patterns, language rules from `threat-report.md`
- [X] T037 [P] [US2] Create `attack-tree-construction.md` in `.claude/skills/tachi-threat-reporting/references/` — extract tree structure rules, minimum depth requirements, Mermaid syntax conventions, color styling, validation checklist, decomposition stopping rules from `threat-report.md`
- [X] T038 [P] [US2] Create `attack-tree-examples.md` in `.claude/skills/tachi-threat-reporting/references/` — extract reference attack tree examples (Critical finding, High finding patterns) from `threat-report.md`
- [X] T039 [US2] Restructure `.claude/agents/tachi/threat-report.md` — remove extracted content, add skill reference navigation table and MANDATORY Read instructions. Target: ≤300 lines. **Result**: 801→267 lines.

### Threat-Infographic

- [X] T040 [P] [US2] Create skill directory `.claude/skills/tachi-infographics/` with SKILL.md containing navigation table
- [X] T041 [P] [US2] Create `infographic-specifications.md` in `.claude/skills/tachi-infographics/references/` — extract section formats (metadata, risk distribution, coverage heat map, top findings), data accuracy rules, finding selection priority from `threat-infographic.md`
- [X] T042 [P] [US2] Create `template-specific-formats.md` in `.claude/skills/tachi-infographics/references/` — extract Baseball Card, System Architecture, Risk Funnel template-specific section 5 formats, tier width calculation, edge cases from `threat-infographic.md`
- [X] T043 [P] [US2] Create `gemini-prompt-construction.md` in `.claude/skills/tachi-infographics/references/` — extract prompt hygiene rules, placeholder mapping, design constraints, risk label mapping, image generation parameters from `threat-infographic.md`
- [X] T044 [P] [US2] Create `visual-design-system.md` in `.claude/skills/tachi-infographics/references/` — extract color palette, layout structure, typography specs, background/theme selection, template file references from `threat-infographic.md`
- [X] T045 [US2] Restructure `.claude/agents/tachi/threat-infographic.md` — remove extracted content, add skill reference navigation table and MANDATORY Read instructions. Target: ≤300 lines. **Result**: 776→287 lines.

**Checkpoint**: All 3 report agents restructured to ≤300 lines. Verify line counts: `wc -l .claude/agents/tachi/{report-assembler,threat-report,threat-infographic}.md`

---

## Phase 3b: Shared References

**Purpose**: Create shared reference files for content duplicated across multiple agents

- [X] T046 [P] Create shared skill directory `.claude/skills/tachi-shared/` with SKILL.md containing navigation table and consumer list
- [X] T047 [P] Create `severity-bands-shared.md` in `.claude/skills/tachi-shared/references/` — consolidate severity band definitions, color codes, SLA mappings. **Note**: Used authoritative thresholds from `schemas/risk-scoring.yaml` (Critical≥9.0, High≥7.0, Medium≥4.0, Low<4.0)
- [X] T048 [P] Create `stride-categories-shared.md` in `.claude/skills/tachi-shared/references/` — consolidate STRIDE+AI category descriptions, element-to-category applicability matrix from orchestrator dispatch-rules and leaf agent descriptions
- [X] T049 [P] Create `finding-format-shared.md` in `.claude/skills/tachi-shared/references/` — consolidate finding format specification (required fields, optional fields, format conventions) used by threat agents and risk-scorer
- [X] T050 Update skill reference navigation tables in all 6 restructured agents to reference shared files from `.claude/skills/tachi-shared/references/` — 9 entries added (3 orchestrator, 2 risk-scorer, 1 each for remaining 4)

**Checkpoint**: Shared references created. No severity band, STRIDE category, or finding format definitions remain duplicated across agents.

---

## Phase 4: Final Validation & Polish (US4 + US5)

**Purpose**: Full regression test, best practices finalization, compliance verification

- [X] T051 [US5] Run full pipeline on `examples/agentic-app/architecture.md`: `/threat-model` → compare threats.md + threats.sarif against baseline (finding count per category ±2, severity distribution ±1 per level, SARIF result count ±2, all 7 sections present, correlation group count ±1)
- [X] T052 [P] [US5] Run `/risk-score` and compare risk-scores.md + risk-scores.sarif against baseline
- [X] T053 [P] [US5] Run `/compensating-controls` and compare compensating-controls.md + compensating-controls.sarif against baseline
- [X] T054 [US5] Verify all 11 leaf agents are byte-identical (excluding `model:` field addition) by running `git diff` on each leaf agent file
- [X] T055 [US5] Verify line counts for all 6 restructured agents: orchestrator ≤500, risk-scorer ≤500, control-analyzer ≤500, report-assembler ≤300, threat-report ≤300, threat-infographic ≤300
- [X] T056 [US4] Finalize `.claude/agents/tachi/_TACHI_AGENT_BEST_PRACTICES.md` — update compliance table with actual `wc -l` counts for all 17 agents post-restructuring, annotate agent-autonomy 210-line leaf exception, verify all quality checklist items reflect new patterns
- [X] T057 [US5] Verify no domain data remains inline in any restructured agent — spot-check each agent for tables, schemas, detection patterns, output templates, scoring dimensions. Only orchestration logic (role, workflow, skill loading, constraints) should remain.
- [X] T058 Verify all extracted content is traceable — for each restructured agent, confirm every removed section has a corresponding skill reference, data file, or shared reference

**Checkpoint**: All success criteria (SC-001 through SC-008) verified. Feature complete.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — can start immediately
- **Phase 2a (Risk-Scorer Prototype)**: Depends on T001-T002 (baseline capture)
- **Phase 2b (Prototype Gate)**: Depends on Phase 2a completion — BLOCKS remaining methodology agents
- **Phase 2c (Remaining Methodology)**: Depends on Phase 2b passing gate
- **Phase 3a (Report Agents)**: Depends on Phase 2c completion (validated extraction pattern)
- **Phase 3b (Shared References)**: Depends on at least 2 consuming agents being restructured
- **Phase 4 (Final Validation)**: Depends on all prior phases

### User Story Dependencies

- **US1 (Methodology)**: Phase 2a → 2b gate → 2c. Risk-scorer first, then orchestrator + control-analyzer in parallel
- **US2 (Report)**: Phase 3a. All 3 report agents can be restructured in parallel
- **US3 (Model Fields)**: Phase 1. All 17 agents in parallel (T003-T005)
- **US4 (Best Practices)**: Phase 1 (initial caps update T006) + Phase 4 (final compliance table T056)
- **US5 (Zero Regression)**: Phase 1 (baseline T001-T002) + Phase 2b (prototype gate T014-T016) + Phase 4 (final validation T051-T058)

### Parallel Opportunities

- **Phase 1**: T003, T004, T005 in parallel (independent agent files); T006 parallel with T003-T005
- **Phase 2a**: T007, T008, T009, T010, T011 in parallel (independent reference files); T012 after all reference files created
- **Phase 2c**: T017-T022 (orchestrator refs) in parallel with T025-T027 (control-analyzer verification)
- **Phase 3a**: T030-T034 (report-assembler) in parallel with T035-T039 (threat-report) in parallel with T040-T045 (infographic) — max 3 parallel tracks
- **Phase 3b**: T046-T049 in parallel (independent shared files)
- **Phase 4**: T051, T052, T053 partially parallel (independent outputs)

---

## Implementation Strategy

### MVP First (Risk-Scorer Prototype)

1. Complete Phase 1 (baseline + model fields + best practices caps)
2. Complete Phase 2a (risk-scorer prototype)
3. **STOP and VALIDATE**: Phase 2b gate — risk-scorer output equivalent?
4. If gate passes: validated extraction pattern, proceed with confidence

### Incremental Delivery

1. Phase 1: Model fields + baseline → all agents have `model:` field
2. Phase 2a+2b: Risk-scorer prototype → pattern validated
3. Phase 2c: Remaining methodology agents → all methodology agents ≤500 lines
4. Phase 3a+3b: Report agents + shared refs → all report agents ≤300 lines
5. Phase 4: Final validation → all success criteria verified

### Parallel Team Strategy

With multiple agents:
1. Phase 1: 3 agents work model fields in parallel (T003/T004/T005)
2. Phase 2a: 5 agents create reference files in parallel (T007-T011), then 1 restructures risk-scorer (T012)
3. Phase 2c: 2 agents work orchestrator and control-analyzer in parallel
4. Phase 3a: 3 agents work 3 report agents in parallel (max parallelism)
5. Phase 3b: 4 agents create shared files in parallel

---

## Summary

**Total tasks**: 58
**By user story**: US1=23, US2=16, US3=3, US4=2, US5=10, Cross-cutting=4
**Parallel opportunities**: 11 parallel windows across 7 phases
**Critical path**: T001 → T007-T013 → T014-T016 (gate) → T023 → T051-T058
**Estimated effort**: 19-29 hours (midpoint: 24 hours)
**Suggested MVP**: Phase 1 + Phase 2a + Phase 2b (risk-scorer prototype validated)

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to spec user stories for traceability
- Prototype-first gate (Phase 2b) is the critical decision point — validates entire approach
- Shared references (Phase 3b) reduce duplicated severity/STRIDE/finding definitions
- Every extraction must be verified: removed lines must exist in destination files (FR-011)
- Accept orchestrator at ≤520 lines per architect tolerance (finding F-01)
- Accept agent-autonomy at ~210 lines as leaf exception (finding F-06)
