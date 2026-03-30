---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-30
    status: APPROVED
    notes: "5/5 user stories covered in dedicated phases. 49/49 FRs traced to tasks. 8/8 success criteria with test tasks. No scope creep. MVP-first strategy with baseball card as Phase 3."
  architect_signoff:
    agent: architect
    date: 2026-03-30
    status: APPROVED_WITH_CONCERNS
    notes: "Dependencies correctly ordered. Parallel opportunities accurate. T007 refactoring gate well-positioned. 2 concerns: (1) T008 should mention exit code 1 detection for FR-047; (2) FR-048 malformed row inherited from shared parsers — awareness note only."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-30
    status: APPROVED
    notes: "Feasible at 85% confidence. 46 tasks for ~850-1100 lines. Critical path correct. 30% test-to-implementation ratio healthy. 1-2 build sessions realistic. senior-backend-engineer as primary implementer."
---

# Tasks: Deterministic Infographic Extraction

**Input**: Design documents from `specs/071-deterministic-infographic-extraction/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Create shared parser module by extracting generic parsers from existing script. Zero-behavior-change refactor.

- [X] T001 Create `scripts/tachi_parsers.py` — extract shared constants (`SEVERITY_ORDER`, `STRIDE_PREFIXES`, `EXIT_SUCCESS/MISSING_ARTIFACT/VALIDATION_FAILURE`) and utility functions (`escape_typst_string`, `strip_bold`, `_parse_int`) from `scripts/extract-report-data.py`
- [X] T002 Move generic table parsers to `scripts/tachi_parsers.py` — extract `parse_markdown_table()`, `_find_table_with_column()` from `scripts/extract-report-data.py`
- [X] T003 Move frontmatter and metadata parsers to `scripts/tachi_parsers.py` — extract `parse_frontmatter()`, `parse_project_name()`, `detect_artifacts()`, `determine_tier()` from `scripts/extract-report-data.py`
- [X] T004 Move severity parsers to `scripts/tachi_parsers.py` — extract `parse_threats_severity()`, `parse_risk_scores_severity()`, `_empty_severity()`, `_accumulate_severity_rows()` from `scripts/extract-report-data.py`
- [X] T005 Move findings and scope parsers to `scripts/tachi_parsers.py` — extract `parse_threats_findings()`, `parse_risk_scores_findings()`, `parse_component_distribution()`, `parse_scope_data()`, `parse_compensating_controls_md()` from `scripts/extract-report-data.py`
- [X] T006 Update `scripts/extract-report-data.py` — replace extracted functions with `from tachi_parsers import ...` statements, preserve all report-specific functions in place
- [X] T007 Verify refactoring: run `python scripts/extract-report-data.py --target-dir examples/agentic-app/sample-report --output /tmp/refactor-test.typ --template-dir templates/tachi/security-report` and diff against pre-refactor output — must be byte-identical

**Checkpoint**: Shared parser module exists. `extract-report-data.py` produces identical output. No behavior change.

---

## Phase 2: Foundational (Core Script Infrastructure)

**Purpose**: Create the infographic extraction script skeleton with CLI, shared imports, and foundational computations that all templates need.

**CRITICAL**: No template-specific work can begin until this phase is complete.

- [X] T008 Create `scripts/extract-infographic-data.py` — script skeleton with argparse CLI (`--target-dir`, `--template`, `--output`), shared parser imports from `tachi_parsers`, and `main()` entry point
- [X] T009 Implement `largest_remainder(values, target)` in `scripts/extract-infographic-data.py` — Largest Remainder Method for percentage rounding with deterministic tie-breaking (fractional part desc, label asc)
- [X] T010 Implement severity extraction pipeline in `scripts/extract-infographic-data.py` — tier detection, severity parsing per tier (Tier 1: compensating-controls, Tier 2: risk-scores, Tier 3: Section 7 findings array per architect C-3 decision), Note severity separation
- [X] T011 Implement `compute_severity_percentages()` in `scripts/extract-infographic-data.py` — severity percentages using `largest_remainder()`, exclude Note, add color codes per data-model.md palette
- [X] T012 Implement `compute_heat_map()` in `scripts/extract-infographic-data.py` — component x severity cross-tabulation, zero-fill from scope components, sort by total desc then name asc, max 8 rows with "Other" aggregation
- [X] T013 Implement `select_top_findings()` in `scripts/extract-infographic-data.py` — top 5 selection with deterministic ranking (score desc, threat ID asc), tier-appropriate score source
- [X] T014 Implement `compute_component_risk_weights()` in `scripts/extract-infographic-data.py` — weighted score (C=4, H=3, M=2, L=1), classify as high/medium/low
- [X] T015 Implement `deduplicate_findings()` in `scripts/extract-infographic-data.py` — union of threat IDs from Section 3 agent tables and Section 4a correlation groups, handle missing Section 4a gracefully
- [X] T016 Implement metadata computation in `scripts/extract-infographic-data.py` — `scan_date` from frontmatter, `agent_count` from `## 3.X` section count, `risk_posture` from deterministic template string
- [X] T017 Implement `validate_infographic()` in `scripts/extract-infographic-data.py` — severity sum check, top 5 ID existence check, heat map row consistency check; exit code 2 on failure
- [X] T018 Implement `build_json_output()` in `scripts/extract-infographic-data.py` — assemble JSON structure per data-model.md, `json.dumps(sort_keys=True, indent=2)` for deterministic output

**Checkpoint**: Core script runs, produces JSON for any template (template_data placeholder). All shared computations working.

---

## Phase 3: User Story 1 — Deterministic Baseball Card Specification (Priority: P1) MVP

**Goal**: Baseball card template produces byte-identical JSON on repeated runs with correct severity, heat map, top findings, and risk weights.

**Independent Test**: Run script twice on `examples/agentic-app/sample-report/` with `--template baseball-card`, diff outputs.

### Implementation

- [X] T019 [US1] Implement baseball card `template_data` in `scripts/extract-infographic-data.py` — populate `risk_weights` array from `compute_component_risk_weights()` per data-model.md schema
- [X] T020 [US1] Wire baseball card end-to-end in `scripts/extract-infographic-data.py` — connect `main()` pipeline for `--template baseball-card`: parse → compute → validate → write JSON
- [X] T021 [US1] Test baseball card Tier 1: run on `examples/agentic-app/sample-report/` (all artifacts present), verify JSON output structure matches data-model.md, verify severity counts match `extract-report-data.py`
- [X] T022 [US1] Test baseball card Tier 3: run on `examples/mermaid-agentic-app/` (threats.md only), verify graceful handling and correct output
- [X] T023 [US1] Test baseball card determinism: run twice on same input, diff outputs — zero differences

**Checkpoint**: Baseball card template fully functional. Deterministic. Cross-output consistent.

---

## Phase 4: User Story 2 — Deterministic System Architecture Specification (Priority: P1)

**Goal**: System architecture template produces byte-identical JSON with trust zones, data flows, and severity coloring.

**Independent Test**: Run script twice on `examples/agentic-app/sample-report/` with `--template system-architecture`, diff outputs.

### Implementation

- [X] T024 [US2] Implement `compute_architecture_overlay()` in `scripts/extract-infographic-data.py` — trust zone groupings (ordered by trust level desc, component name asc), data flow severity coloring (highest severity of destination component), boundary crossing annotations
- [X] T025 [US2] Implement trust zone absence fallback in `scripts/extract-infographic-data.py` — set `trust_zones` to `null` in JSON when scope data has no trust zones, log note to stderr
- [X] T026 [US2] Wire system-architecture template in `scripts/extract-infographic-data.py` — connect pipeline for `--template system-architecture`: shared data + architecture overlay → JSON
- [X] T027 [US2] Test system-architecture Tier 1: run on `examples/agentic-app/sample-report/`, verify trust zones, data flows, and boundary crossings populated
- [X] T028 [US2] Test system-architecture determinism: run twice on same input, diff outputs — zero differences

**Checkpoint**: System architecture template fully functional. Deterministic. Trust zone fallback works.

---

## Phase 5: User Story 3 — Deterministic Risk Funnel Specification (Priority: P1)

**Goal**: Risk funnel template produces byte-identical JSON with 4-tier counts and reduction percentages.

**Independent Test**: Run script twice on `examples/agentic-app/sample-report/` with `--template risk-funnel`, diff outputs.

### Implementation

- [X] T029 [US3] Implement `compute_risk_funnel()` in `scripts/extract-infographic-data.py` — 4-tier computation: Tier 0 (threats.md Section 6 total), Tier 1 (risk-scores.md count), Tier 2 (compensating-controls.md count), Tier 3 (residual severity counts); null for absent artifacts
- [X] T030 [US3] Implement funnel reduction percentages in `scripts/extract-infographic-data.py` — compute `((prev - curr) / prev) * 100` between adjacent non-null tiers, use Largest Remainder Method for the set
- [X] T031 [US3] Implement `missing_enrichments` array in `scripts/extract-infographic-data.py` — populate with `/risk-score` and/or `/compensating-controls` commands when intermediate artifacts absent
- [X] T032 [US3] Wire risk-funnel template in `scripts/extract-infographic-data.py` — connect pipeline for `--template risk-funnel`: shared data + funnel tiers → JSON
- [X] T033 [US3] Test risk-funnel Tier 1 (full pipeline): run on `examples/agentic-app/sample-report/`, verify all 4 tiers populated with reduction percentages
- [X] T034 [US3] Test risk-funnel Tier 3 (threats.md only): run on `examples/mermaid-agentic-app/`, verify Tier 0 populated, Tiers 1-3 null, `missing_enrichments` contains `["/risk-score", "/compensating-controls"]`
- [X] T035 [US3] Test risk-funnel determinism: run twice on same input, diff outputs — zero differences

**Checkpoint**: Risk funnel template fully functional. Partial funnels handled. Deterministic.

---

## Phase 6: User Story 4 — Cross-Output Consistency (Priority: P1)

**Goal**: Severity counts in infographic JSON match `extract-report-data.py` severity counts for same input and tier.

**Independent Test**: Run both scripts on same directory, compare severity counts programmatically.

### Implementation

- [X] T036 [US4] Cross-output consistency test Tier 1: run both `extract-report-data.py` and `extract-infographic-data.py` on `examples/agentic-app/sample-report/`, compare severity counts — must match exactly
- [X] T037 [US4] Cross-output consistency test Tier 3: run both scripts on `examples/mermaid-agentic-app/`, compare severity counts — must match exactly
- [X] T038 [US4] Verify percentage sums: for each template, check that `severity_distribution` percentages sum to exactly 100 (or 0 when total is 0)

**Checkpoint**: Cross-output consistency verified across tiers. Percentage invariant holds.

---

## Phase 7: User Story 5 — Agent Prompt Update (Priority: P2)

**Goal**: Infographic agent invokes deterministic script instead of LLM-based parsing.

**Independent Test**: Run `/infographic` end-to-end on example datasets, verify generated spec files contain data matching script JSON output.

### Implementation

- [X] T039 [US5] Update `.claude/agents/tachi/threat-infographic.md` — replace Steps 1-2 (LLM-based extraction) with script invocation: `python scripts/extract-infographic-data.py --target-dir {dir} --template {template} --output /tmp/infographic-data.json`
- [X] T040 [US5] Add JSON consumption step in `.claude/agents/tachi/threat-infographic.md` — new step reads `/tmp/infographic-data.json` and maps structured data to Sections 1-5 of the spec markdown
- [X] T041 [US5] Add error handling in `.claude/agents/tachi/threat-infographic.md` — check script exit code: 0 proceed, 1 display missing artifact error and halt, 2 display validation failure and halt
- [X] T042 [US5] End-to-end test: run `/infographic --template baseball-card` on `examples/agentic-app/sample-report/`, verify generated spec file severity counts match script JSON output

**Checkpoint**: Agent fully updated. End-to-end `/infographic` works with deterministic extraction.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final verification across all templates and documentation.

- [X] T043 [P] Run all three templates on `examples/agentic-app/sample-report/` — verify all produce valid JSON, all deterministic (run twice, diff)
- [X] T044 [P] Run all three templates on `examples/mermaid-agentic-app/` — verify Tier 3 handling for all templates
- [X] T045 Verify `scripts/extract-report-data.py` still produces byte-identical output after shared module refactor — final regression check
- [X] T046 [P] Validate JSON output against data-model.md schema for all templates and tiers — spot-check key invariants (severity sum, percentage sum, heat map totals)

**Checkpoint**: All templates, all tiers verified. Refactoring regression passed. Feature complete.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — shared module must exist before new script
- **Phases 3-5 (US1-US3)**: All depend on Phase 2 — can run in parallel after Phase 2
- **Phase 6 (US4)**: Depends on Phase 2 — can run in parallel with Phases 3-5
- **Phase 7 (US5)**: Depends on Phases 3-5 — needs all templates working before agent update
- **Phase 8 (Polish)**: Depends on all previous phases

### User Story Dependencies

- **US1 (Baseball Card)**: After Phase 2 — independent of other stories
- **US2 (System Architecture)**: After Phase 2 — independent of other stories
- **US3 (Risk Funnel)**: After Phase 2 — independent of other stories
- **US4 (Cross-Output)**: After Phase 2 — can run in parallel with US1-US3
- **US5 (Agent Update)**: After US1+US2+US3 — needs all templates completed

### Within Each User Story

- Template-specific implementation → wiring → testing (sequential)

### Parallel Opportunities

- T001-T005 can be grouped (all extract to same file, but sequential within the file)
- T019-T020, T024-T026, T029-T032 can run in parallel (different template code paths)
- T021-T023, T027-T028, T033-T035 (tests per template) can run in parallel
- T043-T046 (polish) can run in parallel

---

## Parallel Example: Template Implementation Wave

```
# After Phase 2 complete, launch all three templates in parallel:
Wave A: T019-T023 (Baseball Card — US1)
Wave B: T024-T028 (System Architecture — US2)
Wave C: T029-T035 (Risk Funnel — US3)
Wave D: T036-T038 (Cross-Output — US4, can overlap with A-C)
```

---

## Implementation Strategy

### MVP First (Baseball Card Only)

1. Complete Phase 1: Setup (shared module extraction)
2. Complete Phase 2: Foundational (core script)
3. Complete Phase 3: Baseball Card (US1)
4. **STOP and VALIDATE**: Test determinism + cross-output consistency
5. Proceed to remaining templates

### Incremental Delivery

1. Setup + Foundational → Core infrastructure ready
2. Baseball Card → Deterministic, cross-output consistent (MVP!)
3. System Architecture → Trust zones, data flows added
4. Risk Funnel → 4-tier pipeline visualization
5. Agent Update → End-to-end integration
6. Polish → Full verification

---

## Summary

| Metric | Count |
|--------|-------|
| Total Tasks | 46 |
| Phase 1 (Setup) | 7 |
| Phase 2 (Foundational) | 11 |
| Phase 3 (US1 Baseball Card) | 5 |
| Phase 4 (US2 System Architecture) | 5 |
| Phase 5 (US3 Risk Funnel) | 7 |
| Phase 6 (US4 Cross-Output) | 3 |
| Phase 7 (US5 Agent Update) | 4 |
| Phase 8 (Polish) | 4 |
| Parallel Opportunities | 3 template waves after Phase 2 |
| Suggested MVP Scope | Phases 1-3 (Baseball Card) |
