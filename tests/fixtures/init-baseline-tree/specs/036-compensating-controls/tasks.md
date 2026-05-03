---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-27
    status: APPROVED_WITH_CONCERNS
    notes: "All 5 P0 user stories covered, all 20 FRs addressable, P1 correctly excluded, MVP strategy sound. 3 low concerns: SC-003 actionability validation, story numbering traceability, quickstart syntax verification."
  architect_signoff:
    agent: architect
    date: 2026-03-27
    status: APPROVED_WITH_CONCERNS
    notes: "7 findings (0 blocking, 2 medium, 5 low). Medium: T002/T003 should depend on T001 schema, relatedLocations merging strategy undefined. All resolvable during implementation."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-27
    status: APPROVED_WITH_CONCERNS
    notes: "21 tasks across 7 phases, 6 execution waves. Effort validated at 9.5-13.0h (slightly wider than claimed 9.0-11.5h). 3 medium concerns: T008 oversized, T016 could start earlier, SARIF reference existence check. Critical path bottleneck at T008 (3-4h)."
---

# Tasks: Compensating Controls Analysis

**Input**: Design documents from `/specs/036-compensating-controls/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: Not explicitly requested in spec — test tasks omitted. Validation against `examples/agentic-app/` is included as implementation tasks.

**Organization**: Tasks grouped by user story. All deliverables are markdown, YAML, and JSON files (knowledge system pattern — no compiled code).

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Create foundational schema and reference files that all subsequent work depends on.

- [X] T001 Create controlled finding schema at `schemas/compensating-controls.yaml` extending `schemas/risk-scoring.yaml` with fields: control_status, control_evidence, control_category, control_effectiveness, reduction_factor, residual_score, residual_severity_band, recommendation, effort_estimate — per `specs/036-compensating-controls/data-model.md`
- [X] T002 [P] Create markdown output template at `templates/compensating-controls.md` with sections: frontmatter (schema_version, date, source_file, target_path, classification), Executive Summary, Coverage Matrix, Control Details, Recommendations, Residual Risk Summary — following structure of `templates/risk-scores.md`
- [X] T003 [P] Create SARIF output template at `templates/compensating-controls.sarif` with tool driver `tachi-control-analyzer` v1.0, rules for 8 STRIDE + 2 AI categories, per-result property bag fields (control-status, control-evidence, control-effectiveness, inherent-risk, residual-risk, recommendation, effort-estimate), and relatedLocations for control evidence — following structure of `templates/risk-scores.sarif`

**Checkpoint**: Schema and templates ready — agent and command work can begin.

---

## Phase 2: Foundational (Agent Core Structure)

**Purpose**: Create the control-analyzer agent with its overall structure, input parsing (Phase 1), and codebase discovery (Phase 2). These capabilities are prerequisites for all user stories.

**CRITICAL**: All user story tasks depend on this phase completing.

- [X] T004 Create control-analyzer agent at `.claude/agents/tachi/control-analyzer.md` with: YAML frontmatter (agent_name, category, output_schema reference), Purpose section, 6-phase pipeline overview, input sanitization boundary declaration, and reference file loading instructions (load `schemas/compensating-controls.yaml` and `adapters/claude-code/agents/references/sarif-generation.md` on demand)
- [X] T005 Write agent Phase 1 (Parse Input) in `.claude/agents/tachi/control-analyzer.md`: read risk-scores.md (canonical) or risk-scores.sarif (fallback), extract per-threat fields (ID, category, component, description, composite_score, severity_band, dimensional scores, governance fields, fingerprints), validate at least 1 scored threat exists, handle malformed input with descriptive errors
- [X] T006 Write agent Phase 2 (Discover Codebase) in `.claude/agents/tachi/control-analyzer.md`: architecture-guided discovery (extract component-to-directory mapping from architecture.md), heuristic fallback (prioritize directories: middleware/, auth/, security/, validators/, guards/, interceptors/, filters/, policies/, config/), 200-file read budget enforcement, large file truncation (>5K tokens to imports + security-relevant sections), component → file list mapping output
- [X] T007 Embed STRIDE-to-control-category mapping table in `.claude/agents/tachi/control-analyzer.md`: Spoofing→Authentication+Access Control, Tampering→Input Validation, Repudiation→Logging/Audit, Info Disclosure→Encryption, DoS→Rate Limiting, Privilege Escalation→Access Control, Agentic→All 8, LLM→Input Validation+Logging/Audit — per data-model.md

**Checkpoint**: Agent can parse risk-score input and discover codebase files. Ready for control detection.

---

## Phase 3: User Story 1 — Codebase Control Detection (Priority: P0) MVP

**Goal**: Scan target codebase for existing security controls in 8 categories, classify each threat as Control Found / Partial Control / No Control Found, and provide file:line evidence.

**Independent Test**: Run agent against `examples/agentic-app/` with risk-scores.md input. Verify every threat gets exactly one classification with evidence for detected controls.

### Implementation for User Story 1

- [X] T008 [US1] Write agent Phase 3 (Detect Controls) in `.claude/agents/tachi/control-analyzer.md`: for each component batch — read component files, scan for 8 control categories using two-phase detection (pattern scan then LLM semantic analysis), record evidence per detection (file path, line number, code snippet up to 5 lines, confidence level), describe detection patterns for each of the 8 categories: Authentication (auth middleware, JWT verification, OAuth, session management), Input Validation (schema validation, sanitization, parameterized queries, type checking), Rate Limiting (rate limiter middleware, throttling, circuit breakers), Encryption (TLS/SSL, encryption functions, key management, hashing), Logging/Audit (structured logging, audit trail, event tracking), CSRF Protection (CSRF tokens, SameSite cookies, origin validation), CSP/Security Headers (CSP, X-Frame-Options, HSTS), Access Control (RBAC/ABAC, permission checks, role guards)
- [X] T009 [US1] Write agent Phase 4 (Map & Classify) in `.claude/agents/tachi/control-analyzer.md`: for each scored threat — use STRIDE-to-control mapping to identify which control categories to check, classify as Control Found (matching control with evidence), Partial Control (control exists but incomplete coverage), or No Control Found (no matching control), handle multiple controls per threat (use highest effectiveness), handle cross-component controls (global middleware applies to all components)
- [X] T010 [US1] Add component-based batching instructions to `.claude/agents/tachi/control-analyzer.md`: group threats by component, analyze all threats for a component simultaneously, context window budget allocation (~50K tokens for codebase content per batch), sub-batch splitting when component exceeds limits (halve threat count), partial result emission with warnings for failed batches

**Checkpoint**: Agent can detect controls and classify all threats. Core P0 value delivered.

---

## Phase 4: User Story 2 — Compensating Control Recommendations (Priority: P0)

**Goal**: Generate actionable recommendations for unmitigated/partial threats, sorted by composite risk score, with effort estimates.

**Independent Test**: Given classified threats with "No Control Found" and "Partial Control" statuses, verify recommendations include what/where/patterns/effort for every gap, sorted by score descending.

### Implementation for User Story 2

- [X] T011 [US2] Write agent Phase 5 recommendation logic in `.claude/agents/tachi/control-analyzer.md`: for each threat classified as "No Control Found" — generate recommendation with: specific control to implement, suggested implementation location (file/module), reference patterns or libraries, effort estimate (Low=config change, Medium=new middleware/function, High=architectural change). For "Partial Control" — focus recommendation on hardening existing control (what's missing, how to extend). Sort all recommendations by composite_score descending.

**Checkpoint**: Agent generates prioritized remediation roadmap for all gaps.

---

## Phase 5: User Story 3 — Residual Risk Calculation (Priority: P0)

**Goal**: Calculate residual risk per threat using binary reduction factors and generate summary statistics.

**Independent Test**: Given threats with known classifications, verify residual scores are arithmetically correct (Found: score*0.50, Partial: score*0.75, Missing: unchanged) and summary totals are accurate.

### Implementation for User Story 3

- [X] T012 [US3] Write agent Phase 5 residual risk calculation in `.claude/agents/tachi/control-analyzer.md`: apply P0 binary reduction factors (Found=0.50, Partial=0.25, Missing=0.00), calculate per-threat residual_score = composite_score * (1 - reduction_factor), clamp to [0.0, 10.0], map to residual_severity_band using same thresholds as inherent (Critical>=9.0, High 7.0-8.9, Medium 4.0-6.9, Low <4.0), compute summary: total inherent risk, total residual risk, delta, overall reduction percentage

**Checkpoint**: Agent calculates accurate residual risk for all threats.

---

## Phase 6: User Story 4 + User Story 5 — Coverage Matrix & Dual-Format Output (Priority: P0)

**Goal**: Generate coverage matrix with summary statistics (US4) and produce both compensating-controls.md and compensating-controls.sarif output files (US5).

**Independent Test**: Run full analysis and verify both output files are generated — MD contains all 5 sections with correct matrix and statistics, SARIF validates against 2.1.0 schema with preserved fingerprints.

### Implementation for User Story 4 (Coverage Matrix)

- [X] T013 [US4] Write agent Phase 6 coverage matrix generation in `.claude/agents/tachi/control-analyzer.md`: generate table with columns Threat ID, Component, Threat, Inherent Score, Inherent Severity, Control Status, Residual Score, Residual Severity — one row per threat, grouped by residual severity. Calculate summary statistics: count and percentage for each status (X% Found, Y% Partial, Z% Missing).

### Implementation for User Story 5 (Dual-Format Output)

- [X] T014 [US5] Write agent Phase 6 markdown output generation in `.claude/agents/tachi/control-analyzer.md`: produce compensating-controls.md following `templates/compensating-controls.md` structure — frontmatter, Executive Summary (total threats, coverage stats, overall risk reduction, highest-risk unmitigated finding), Coverage Matrix (from T013), Control Details (per-control evidence with file:line and effectiveness), Recommendations (from Phase 5), Residual Risk Summary (inherent vs residual totals with delta)
- [X] T015 [US5] Write agent Phase 6 SARIF output generation in `.claude/agents/tachi/control-analyzer.md`: produce compensating-controls.sarif following `templates/compensating-controls.sarif` structure — tool.driver.name "tachi-control-analyzer", preserve findingId/v1 fingerprints from input risk-scores.sarif, set security-severity to residual score (string), populate per-result properties (control-status, control-evidence, control-effectiveness, inherent-risk, residual-risk, recommendation, effort-estimate), map control evidence to relatedLocations with physicalLocation for each evidence file:line, sort results by residual risk descending
- [X] T016 [US5] Create command orchestrator at `.claude/commands/compensating-controls.md`: parse flags (--target, --output-dir), validate risk-score input exists (risk-scores.md or risk-scores.sarif with md canonical), detect optional architecture.md, determine output directory, invoke tachi-control-analyzer agent with input content + target path + architecture (if available), display completion summary with severity distribution and coverage statistics — following pattern of `.claude/commands/risk-score.md`

**Checkpoint**: Full pipeline operational — command invokes agent, agent produces dual-format output.

---

## Phase 7: Validation & Polish

**Purpose**: Validate against example codebase, generate example outputs, ensure SARIF compliance.

- [X] T017 [P] Run `/compensating-controls` against `examples/agentic-app/sample-report/` with `--target examples/agentic-app/` and write example output to `examples/agentic-app/sample-report/compensating-controls.md`
- [X] T018 [P] Validate `examples/agentic-app/sample-report/compensating-controls.sarif` against SARIF 2.1.0 schema — verify tool metadata, fingerprint preservation from risk-scores.sarif, property bag completeness, relatedLocations for control evidence
- [X] T019 Verify SARIF supersession chain: confirm compensating-controls.sarif findingId/v1 fingerprints match risk-scores.sarif fingerprints for every corresponding finding
- [X] T020 Review example output against spec acceptance criteria: every threat classified (SC-001), file:line evidence present for detected controls (FR-005), recommendations sorted by score (FR-010), residual risk calculations correct (FR-011/FR-012), coverage statistics accurate (SC-007)
- [X] T021 Run quickstart.md validation: execute each usage example from `specs/036-compensating-controls/quickstart.md` and verify expected behavior

**Checkpoint**: All P0 user stories validated. Feature ready for delivery.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on T001 (schema) — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 completion (agent core + discovery)
- **US2 (Phase 4)**: Depends on Phase 3 (needs control classifications to recommend)
- **US3 (Phase 5)**: Depends on Phase 3 (needs control classifications to calculate residual risk). Can run in parallel with US2.
- **US4+US5 (Phase 6)**: Depends on Phase 4 + Phase 5 (needs all analysis results for output)
- **Validation (Phase 7)**: Depends on Phase 6 (needs complete pipeline)

### Critical Path

```
T001 → T004 → T005 → T006 → T007 → T008 → T009 → T010 → T011 → T013 → T014 → T016 → T017
```

T008 (Phase 3 control detection) is the critical path bottleneck (~3-4 hours per Team-Lead estimate).

### Parallel Opportunities

- T002 + T003 can run in parallel with each other (different files)
- T002 + T003 can run in parallel with T001 (T001 blocks Phase 2, not T002/T003)
- T011 (US2 recommendations) and T012 (US3 residual risk) can run in parallel
- T013 (US4 coverage matrix) and T014/T015 (US5 output) are sequential within Phase 6
- T017 + T018 can run in parallel (different validation targets)

### User Story Dependencies

- **US1 (P0)**: Independent after Foundational — no dependencies on other stories
- **US2 (P0)**: Depends on US1 classifications — needs control status per threat
- **US3 (P0)**: Depends on US1 classifications — can parallelize with US2
- **US4 (P0)**: Depends on US1+US3 — needs classifications + residual scores
- **US5 (P0)**: Depends on US1+US2+US3+US4 — needs all data for output
- **US6 (P1)**: Not included in P0 tasks — deferred to future iteration

---

## Parallel Example: Phase 1

```
# Wave 1a: All three setup tasks in parallel
Task T001: Create schema at schemas/compensating-controls.yaml
Task T002: Create MD template at templates/compensating-controls.md
Task T003: Create SARIF template at templates/compensating-controls.sarif
```

## Parallel Example: Phase 4+5

```
# Wave 4: US2 and US3 in parallel (different agent sections, no dependency)
Task T011: Write recommendation logic (US2)
Task T012: Write residual risk calculation (US3)
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup (schema + templates)
2. Complete Phase 2: Foundational (agent core + discovery)
3. Complete Phase 3: US1 (control detection + classification)
4. **STOP and VALIDATE**: Agent can detect controls and classify threats
5. Value: "What controls do I already have?" answered

### Incremental Delivery

1. Setup + Foundational → Schema and agent skeleton ready
2. Add US1 → Control detection working → Validate against example
3. Add US2 + US3 (parallel) → Recommendations + residual risk
4. Add US4 + US5 → Full output pipeline → Command operational
5. Validation → Example output + SARIF compliance → Feature complete

### Effort Estimate (from Team-Lead PRD review)

Total: 9.0 - 11.5 hours across 7 waves (60% confidence)
- Phase 1 (Setup): ~1.0h
- Phase 2 (Foundational): ~1.5h
- Phase 3 (US1 - Detection): ~3.0-4.0h (critical path)
- Phase 4+5 (US2+US3): ~1.5h (parallelizable)
- Phase 6 (US4+US5 - Output): ~1.5-2.0h
- Phase 7 (Validation): ~0.5-1.0h

---

## Notes

- All deliverables are markdown, YAML, and JSON files (knowledge system pattern)
- Agent file (`.claude/agents/tachi/control-analyzer.md`) is the primary deliverable (~60-80KB expected)
- Command file (`.claude/commands/compensating-controls.md`) is secondary (~150-200 lines expected)
- Schema + templates are small foundational files
- US6 (P1 effectiveness assessment) deliberately excluded from P0 task breakdown
- Commit after each phase completion for incremental progress
