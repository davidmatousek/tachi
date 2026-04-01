---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-31
    status: APPROVED
    notes: "All 6 user stories covered (6/6). All 20 FRs traceable (20/20). Zero scope creep. MVP strategy correctly targets P0 priorities. Phase checkpoints independently testable. Architect concerns and prior PM spec concern resolved in task descriptions."
  architect_signoff:
    agent: architect
    date: 2026-03-31
    status: APPROVED_WITH_CONCERNS
    notes: "Dependencies correctly ordered, parallel waves valid. Plan review concerns C-3 and C-5 addressed. 3 medium items for task execution: (1) T024 baselineState placement per SARIF 2.1.0, (2) T017 needs exact-match-first and tie-breaking, (3) T002-T004 need schema_version bump to 1.1."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-31
    status: APPROVED_WITH_CONCERNS
    notes: "36 tasks across 9 waves, max parallelism 7. MVP path (15 tasks, Phases 1-4) sound. 1 medium concern: orchestrator.md concentration (8/36 tasks) — mitigate with holistic validation at wave checkpoints. T035 moved to Wave 5 for SARIF co-location."
---

# Tasks: Baseline-Aware Pipeline

**Input**: Design documents from `specs/074-baseline-aware-pipeline/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Organization**: Tasks grouped by user story. Each story can be validated independently after its phase completes.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Schema Extensions)

**Purpose**: Extend existing schemas and create new coverage checklist schema. These are additive-only changes — no breaking modifications.

- [X] T001 [P] Create coverage checklists schema at schemas/coverage-checklists.yaml with component type to required threat categories mapping per data-model.md (External Entity, Process, Data Store, Data Flow, LLM Process, MCP Server)
- [X] T002 [P] Extend schemas/finding.yaml with delta_status (enum: NEW, UNCHANGED, UPDATED, RESOLVED) and baseline_run_id (string, nullable) fields per data-model.md
- [X] T003 [P] Extend schemas/risk-scoring.yaml with score_source (enum: inherited, fresh) and score_bounds (object with min/max) fields per data-model.md
- [X] T004 [P] Extend schemas/compensating-controls.yaml with control_carry_forward (boolean) and rescan_scope (enum: full, incremental) fields per data-model.md

**Checkpoint**: All schemas updated. Validation: each schema file parses as valid YAML with new fields documented.

---

## Phase 2: Foundational (Baseline Infrastructure)

**Purpose**: Core baseline detection and loading infrastructure in the orchestrator. MUST complete before any user story implementation.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T005 Add baseline detection and loading logic to .claude/agents/tachi/orchestrator.md — detect previous threats.md in output directory or via --baseline flag, parse finding registry (IDs, categories, components, fingerprints), extract baseline metadata (date, count, run_id)
- [X] T006 [P] Add baseline parsing and correlation domain knowledge to .claude/skills/tachi-orchestration/SKILL.md — baseline file detection rules, finding registry extraction format, fingerprint correlation algorithm using partialFingerprints.findingId/v1 as primary key and primaryLocationLineHash as validation signal (not discriminator, per architect review)
- [X] T007 [P] Add baseline frontmatter block to templates/tachi/output-schemas/threats.md — baseline source, date, finding_count, run_id fields (null when no baseline)

**Checkpoint**: Orchestrator can detect and parse baseline files. Output template has baseline frontmatter. Validation: run /threat-model without baseline — output identical to current behavior.

---

## Phase 3: User Story 1 — Stable Re-Scan (Priority: P0) MVP

**Goal**: Re-running the pipeline on unchanged code produces identical finding IDs and scores.

**Independent Test**: Run pipeline twice on same architecture — compare output files for 100% ID match, zero score drift, identical counts.

### Implementation for User Story 1

- [X] T008 [US1] Implement carry-forward logic in .claude/agents/tachi/orchestrator.md Phase 1 — for each baseline finding, verify against current architecture, classify as UNCHANGED (identical assessment), UPDATED (description/context changed), or RESOLVED (no longer applicable), inherit original ID and score for UNCHANGED
- [X] T009 [US1] Implement score inheritance in .claude/agents/tachi/risk-scorer.md — for UNCHANGED findings, copy all scoring fields verbatim (cvss_base, cvss_vector, exploitability, scalability, reachability, composite_score, severity_band), set score_source to "inherited"
- [X] T010 [P] [US1] Implement control status carry-forward in .claude/agents/tachi/control-analyzer.md — for UNCHANGED findings, copy control_status, control_evidence, reduction_factor, residual_score from baseline, set control_carry_forward to true, set rescan_scope to "incremental"
- [X] T011 [P] [US1] Add score inheritance rules to .claude/skills/tachi-risk-scoring/SKILL.md — inherited vs fresh scoring logic, when to copy vs recompute, score_source field semantics
- [X] T012 [P] [US1] Add control carry-forward rules to .claude/skills/tachi-control-analysis/SKILL.md — carry-forward conditions, incremental re-scan scope determination, evidence preservation semantics

**Checkpoint**: Pipeline re-run on unchanged code produces identical output. SC-001 (100% ID stability), SC-002 (zero drift), SC-003 (zero count drift) validated.

---

## Phase 4: User Story 2 — Remediation Verification (Priority: P0)

**Goal**: Fixed vulnerabilities are marked [RESOLVED] with original ID preserved for audit traceability.

**Independent Test**: Remove a component's attack surface from architecture, re-run pipeline — verify targeted finding marked [RESOLVED] with original ID.

**Dependencies**: Requires Phase 3 (carry-forward logic must exist to detect resolved findings)

### Implementation for User Story 2

- [X] T013 [US2] Enhance RESOLVED detection in .claude/agents/tachi/orchestrator.md carry-forward logic — when a baseline finding's component or threat is no longer present in current architecture, classify as RESOLVED, retain original ID/description/last-known score in output
- [X] T014 [P] [US2] Add RESOLVED findings section to templates/tachi/output-schemas/threats.md — resolved findings table after main findings tables, preserving ID, description, last-known risk level, and resolution annotation
- [X] T015 [US2] Add delta summary format to .claude/agents/tachi/orchestrator.md report phase — generate finding-level delta summary lines (e.g., "T-2: Tampering — RESOLVED") for developer-facing confirmation

**Checkpoint**: Removing a threat from architecture marks it [RESOLVED]. Partial fix marks as [UPDATED]. SC-006 validated.

---

## Phase 5: User Story 3 — New Threat Discovery (Priority: P0)

**Goal**: New threats discovered alongside carried-forward findings without anchoring bias or duplication.

**Independent Test**: Add new component to architecture, re-run — verify new findings with [NEW] annotation, sequential IDs, no duplicates of existing findings.

**Dependencies**: Requires Phase 3 (carry-forward provides the baseline finding set for dedup)

### Implementation for User Story 3

- [X] T016 [US3] Implement isolated discovery context in .claude/agents/tachi/orchestrator.md Phase 2 — spawn discovery with architecture description + coverage summary only (component names + covered threat categories), explicitly exclude full finding text to prevent anchoring bias
- [X] T017 [US3] Implement merge and deduplication in .claude/agents/tachi/orchestrator.md Phase 3 — match Phase 2 findings against baseline by (component, threat_category, primaryLocationLineHash), use deterministic string similarity (normalized Levenshtein or Jaccard on tokenized descriptions) with >80% threshold for duplicate detection (baseline version wins), assign new sequential IDs after highest existing per category
- [X] T018 [US3] Add bounded scoring rules to .claude/agents/tachi/risk-scorer.md — for NEW findings from Phase 2, enforce CVSS base score within ±1.0 of category default from schemas/risk-scoring.yaml category_defaults section, clamp to [0.0, 10.0] range
- [X] T019 [P] [US3] Add score bounding specification to .claude/skills/tachi-risk-scoring/SKILL.md — bounded scoring formula, category default reference, clamping rules at extremes (9.5 default → 8.5–10.0, 1.0 default → 0.0–2.0)
- [X] T020 [P] [US3] Document deterministic similarity algorithm in .claude/skills/tachi-orchestration/SKILL.md — specify the concrete algorithm (normalized Levenshtein on lowercased, stopword-removed description tokens), threshold rationale, and baseline-wins policy per architect review item C-5

**Checkpoint**: New findings discovered with [NEW] and sequential IDs. No duplicates of baseline findings. Scores bounded within ±1.0. SC-004 validated.

---

## Phase 6: User Story 4 — Delta Annotations (Priority: P1)

**Goal**: Every finding annotated with lifecycle status for trend reporting and audit trails.

**Independent Test**: Run pipeline with baseline, make changes, re-run — verify every finding carries exactly one delta annotation.

**Dependencies**: Requires Phases 3-5 (all delta statuses must be producible)

### Implementation for User Story 4

- [X] T021 [P] [US4] Add delta annotation column to threat tables in templates/tachi/output-schemas/threats.md — add Status column showing [NEW], [UNCHANGED], [UPDATED], or [RESOLVED] for every finding in STRIDE and AI threat tables
- [X] T022 [P] [US4] Add score_source column to templates/tachi/output-schemas/risk-scores.md — show "inherited" or "fresh" per finding, add baseline reference in frontmatter
- [X] T023 [P] [US4] Add control_carry_forward indicator to templates/tachi/output-schemas/compensating-controls.md — show carry-forward status per finding, add rescan_scope in frontmatter
- [X] T024 [P] [US4] Add baselineState property to templates/tachi/output-schemas/threats.sarif — add baselineState (new/unchanged/updated/absent) to result properties object, add baselineRunId to partialFingerprints
- [X] T025 [P] [US4] Add score_source property to templates/tachi/output-schemas/risk-scores.sarif — add score_source to result properties
- [X] T026 [P] [US4] Add carry_forward property to templates/tachi/output-schemas/compensating-controls.sarif — add control_carry_forward to result properties

**Checkpoint**: All output files include delta annotations. Every finding has exactly one status. SARIF files include baselineState. Output parseable by downstream tools.

---

## Phase 7: User Story 5 — Coverage Assurance (Priority: P1)

**Goal**: Coverage gate verifies minimum threat categories evaluated per component type.

**Independent Test**: Run pipeline on architecture with LLM Process — verify coverage gate checks for prompt injection, data poisoning, model theft.

**Dependencies**: Requires Phase 5 (merged finding set needed for coverage evaluation)

### Implementation for User Story 5

- [X] T027 [US5] Implement coverage gate in .claude/agents/tachi/orchestrator.md Phase 4 — load schemas/coverage-checklists.yaml, for each component determine its type (DFD element type + AI subtype detection via keyword matching), check merged findings against required categories, flag uncovered component-category pairs
- [X] T028 [US5] Implement targeted re-analysis dispatch in .claude/agents/tachi/orchestrator.md — for each coverage gap, dispatch the specific threat agent for the missing category targeting only the uncovered component, merge results into finding set, run once per gap (no retry loop)
- [X] T029 [P] [US5] Add coverage gate results section to templates/tachi/output-schemas/threats.md — coverage gate pass/fail status in frontmatter, coverage matrix showing required vs evaluated categories per component, gap list with re-analysis results
- [X] T030 [P] [US5] Add coverage gate orchestration rules to .claude/skills/tachi-orchestration/SKILL.md — component type detection rules, checklist lookup logic, gap flagging format, targeted re-analysis dispatch rules, non-blocking warning semantics

**Checkpoint**: Coverage gate detects missing categories and triggers targeted re-analysis. Passes silently when all covered. SC-005 validated.

---

## Phase 8: User Story 6 — Remediation SLA Tracking (Priority: P1)

**Goal**: Governance fields persist across runs for compliance reporting.

**Independent Test**: Run pipeline across 3 cycles — verify governance fields (risk_owner, remediation_sla) preserved for persisting findings.

**Dependencies**: Requires Phase 3 (carry-forward logic provides persistence mechanism)

### Implementation for User Story 6

- [X] T031 [US6] Add governance field carry-forward to .claude/agents/tachi/risk-scorer.md — for UNCHANGED and UPDATED findings, preserve risk_owner, remediation_sla, risk_disposition, review_date from baseline, only overwrite if score changes severity band (triggering SLA recalculation)
- [X] T032 [P] [US6] Add governance persistence rules to .claude/skills/tachi-risk-scoring/SKILL.md — field preservation semantics, SLA recalculation triggers (severity band change only), review_date update policy

**Checkpoint**: Governance fields persist across runs. SLA recalculated only on severity band change. Lifecycle traceable: [NEW] → [UNCHANGED] → [UPDATED] → [RESOLVED].

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Validation against real architectures and documentation updates.

- [X] T033 Validate baseline-aware pipeline against examples/second-brain-mcp architecture — run twice on unchanged code, verify zero drift (SC-001, SC-002, SC-003), modify architecture, verify delta annotations and RESOLVED findings
- [X] T034 [P] Validate baseline-aware pipeline against examples/ agentic-app architecture (if available) — run with baseline, verify coverage gate activates for LLM/MCP components
- [X] T035 [P] Update SARIF specification reference at .claude/skills/tachi-orchestration/references/sarif-specification.md — document baselineState property, baselineRunId fingerprint field, delta annotation mapping to SARIF conventions
- [X] T036 Run quickstart.md validation scenarios from specs/074-baseline-aware-pipeline/quickstart.md — execute all 7 test scenarios, document results

**Checkpoint**: Real-world validation passes. All success criteria verified. Feature ready for delivery.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately. All 4 tasks parallelizable.
- **Foundational (Phase 2)**: Depends on Phase 1 (schemas must exist). T005 is sequential; T006, T007 parallelizable.
- **US1 — Stable Re-Scan (Phase 3)**: Depends on Phase 2 (baseline loading must exist). T008 sequential; T009-T012 parallelizable after T008.
- **US2 — Remediation Verification (Phase 4)**: Depends on Phase 3 (carry-forward logic).
- **US3 — New Threat Discovery (Phase 5)**: Depends on Phase 3 (baseline finding set for dedup). Independent of US2.
- **US4 — Delta Annotations (Phase 6)**: Depends on Phases 3-5 (all statuses must be producible). All 6 tasks parallelizable.
- **US5 — Coverage Assurance (Phase 7)**: Depends on Phase 5 (merged finding set). Independent of US4.
- **US6 — SLA Tracking (Phase 8)**: Depends on Phase 3 (carry-forward). Independent of US4, US5.
- **Polish (Phase 9)**: Depends on all story phases completing.

### User Story Dependencies

- **US1 (P0)**: Foundational — all other stories depend on carry-forward
- **US2 (P0)**: Depends on US1 only
- **US3 (P0)**: Depends on US1 only (independent of US2)
- **US4 (P1)**: Depends on US1 + US2 + US3 (needs all statuses)
- **US5 (P1)**: Depends on US3 only (needs merged finding set)
- **US6 (P1)**: Depends on US1 only (needs carry-forward)

### Parallel Opportunities

```
Wave 0: T001, T002, T003, T004 (all parallel — different schema files)
Wave 1: T005 (sequential), T006, T007 (parallel with each other, after T005)
Wave 2: T008 (sequential), then T009, T010, T011, T012 (parallel after T008)
Wave 3: T013, T016 (parallel — US2 and US3 independent), T031 (US6 independent)
Wave 4: T014, T015, T017, T018, T019, T020, T032 (parallel — different files)
Wave 5: T021-T026 (all parallel — US4, all different template files)
Wave 6: T027, T028 (sequential — US5 coverage gate)
Wave 7: T029, T030 (parallel — US5 templates)
Wave 8: T033, T034, T035, T036 (validation — T033 sequential, rest parallel)
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (4 schema tasks)
2. Complete Phase 2: Foundational (baseline infrastructure)
3. Complete Phase 3: US1 — Stable Re-Scan
4. Complete Phase 4: US2 — Remediation Verification
5. **STOP and VALIDATE**: Zero drift on unchanged code, RESOLVED detection works
6. This alone solves the core problem (23% drift, ID remapping)

### Full Delivery

7. Add Phase 5: US3 — Fresh discovery alongside stability
8. Add Phase 6: US4 — Delta annotations on all outputs
9. Add Phase 7: US5 — Coverage gate for reliability
10. Add Phase 8: US6 — Governance field persistence
11. Complete Phase 9: Polish and real-world validation

### Incremental Value

Each phase adds testable value:
- After Phase 3: Pipeline stops drifting (core value)
- After Phase 4: Fixes are verifiable (developer value)
- After Phase 5: New threats still discoverable (analysis quality)
- After Phase 6: All outputs annotated (reporting value)
- After Phase 7: Coverage guaranteed (reliability value)
- After Phase 8: SLA tracking enabled (compliance value)

---

## Notes

- All tasks modify agent/skill/schema/template files — no application code
- [P] tasks target different files with no cross-dependencies
- Architect concerns (C-3 primaryLocationLineHash role, C-5 deterministic similarity) addressed in T017 and T020
- Score bounding applies only to Phase 2 NEW findings (not inherited scores)
- Coverage gate is non-blocking — warnings, not errors
- Backward compatibility: no baseline = identical to current behavior
