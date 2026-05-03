---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-08
    status: APPROVED
    notes: "4/4 user stories covered, 15/15 FRs addressed, 0 scope creep, MVP strategy (US4+US1 first) aligns with product priorities."
  architect_signoff:
    agent: architect
    date: 2026-04-08
    status: APPROVED_WITH_CONCERNS
    notes: "Dependencies correctly ordered, parallel opportunities valid, 10/10 components mapped. Medium concern: baseline_run_id source path inconsistency between data-model and tasks — resolve during T004/T006 implementation (non-blocking)."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-08
    status: APPROVED
    notes: "18 tasks across 7 phases, critical path correctly identified, parallel execution maximized (3 user stories concurrent after foundational). Same-file contention on tachi_parsers.py mitigated by sequencing T004/T005 before T006."
---

# Tasks: Downstream Baseline Propagation

**Input**: Design documents from `/specs/104-downstream-baseline-propagation/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md

**Tests**: Not explicitly requested — test tasks omitted. Validation covered in Phase 6.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Foundational — Schema Templates (Blocking Prerequisites)

**Purpose**: Update output schema templates that define the contract all downstream consumers follow. These MUST be completed before parser or agent changes, because the schemas define what columns and sections exist.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T001 [P] Add Status column to Section 7 Recommended Actions table in `templates/tachi/output-schemas/threats.md` — update column definition from `Finding ID | Component | Threat | Risk Level | Mitigation` to `Finding ID | Status | Component | Threat | Risk Level | Mitigation`, update examples to include Status values (NEW, UNCHANGED, UPDATED), update column count references
- [X] T002 [P] Add Section 8 Delta Summary structure to `templates/tachi/output-schemas/threats.md` — add after Section 7 with Finding Lifecycle table (Status/Count/Description rows for NEW, UNCHANGED, UPDATED, RESOLVED, Total), Baseline Reference table (Source, Date, Baseline Findings, Run ID), and conditional presence note (omit on first run)
- [X] T003 [P] Update `templates/tachi/output-schemas/threat-report.md` — add baseline_source, baseline_date, delta_counts to frontmatter field table; add Section 8 Delta Summary (lifecycle breakdown, remediation progress narrative, baseline reference); add baseline handling guidance to Section 5 Attack Trees; bump schema_version from "1.0" to "1.1"

**Checkpoint**: Schema templates define the delta contract. Parser and agent updates can now reference these structures.

---

## Phase 2: Foundational — Shared Parser (Blocking Prerequisites)

**Purpose**: Add delta-aware parsing functions to the shared parser module that both extraction scripts depend on. Component 1 from the plan.

**CRITICAL**: Extraction script changes (US2, US3) cannot begin until this phase is complete.

- [X] T004 [P] Add `parse_baseline_frontmatter()` function to `scripts/tachi_parsers.py` — new function (NOT extending existing parse_frontmatter()) that parses nested `baseline:` block from YAML frontmatter, returns dict with keys source/date/finding_count/run_id (all None when no baseline)
- [X] T005 [P] Add `parse_resolved_findings()` function to `scripts/tachi_parsers.py` — new function that parses Section 4b Resolved Findings table with columns ID/Component/Threat/Last Risk Level/Resolution Reason, returns list of finding dicts with delta_status="RESOLVED" injected, returns empty list when Section 4b absent
- [X] T006 Update `parse_threats_findings()` in `scripts/tachi_parsers.py` — add delta_status extraction from "Status" column in Section 7 row dict, include only when present and non-empty (backward compatible), preserve existing field set (id, component, threat, likelihood, impact, risk_level, mitigation)

**Checkpoint**: Shared parser exposes delta fields. Extraction scripts can now consume them.

---

## Phase 3: User Story 4 — Shared Parser and Schema Delta Support (Priority: P0) MVP

**Goal**: Verify the foundational parser and schema changes work correctly as a unit before proceeding to downstream consumers.

**Independent Test**: Call `parse_threats_findings()` on a baseline-aware threats.md — verify delta_status present. Call on pre-074 threats.md — verify identical output. Call `parse_resolved_findings()` — verify Section 4b parsing. Call `parse_baseline_frontmatter()` — verify nested baseline fields.

- [X] T007 [US4] Validate shared parser changes by running `parse_threats_findings()`, `parse_resolved_findings()`, and `parse_baseline_frontmatter()` against example output in `examples/` directory — verify delta fields present when Status column exists, verify backward compatibility when Status column absent, verify Section 4b parsing, verify baseline frontmatter extraction

**Checkpoint**: Foundational parser and schema changes verified. User story implementation can now begin in parallel.

---

## Phase 4: User Story 1 — Delta-Aware Threat Report (Priority: P0)

**Goal**: Threat-report agent produces delta-aware narrative output with executive summary delta counts, lifecycle-grouped threat analysis, attack tree carry-forward for UNCHANGED findings, and Section 8 Delta Summary.

**Independent Test**: Run threat-report agent on a baseline-compared threats.md. Verify delta counts in executive summary, lifecycle annotations in Section 3, UNCHANGED carry-forward in Section 5, and Section 8 Delta Summary present.

- [X] T008 [P] [US1] Update threat-report agent input contract in `agents/threat-report.md` — add delta_status and baseline_run_id to Finding IR Fields Consumed table, add Section 4b Resolved Findings to Required Input Sections table, add baseline frontmatter fields to input contract
- [X] T009 [US1] Update threat-report agent output instructions in `agents/threat-report.md` — add delta counts to Executive Summary (Section 1) generation, add delta status annotations to Threat Analysis (Section 3) narrative, add delta branching to Attack Trees (Section 5): NEW/UPDATED generate fresh, UNCHANGED notes "carried forward from baseline", RESOLVED excluded; add Section 8 Delta Summary generation with lifecycle breakdown table, remediation progress narrative, baseline reference; add no-baseline guard (omit Section 8, generate all trees fresh, no annotations)

**Checkpoint**: Threat report agent produces delta-aware output with all four user story acceptance scenarios met.

---

## Phase 5: User Story 2 — Delta-Aware Infographics (Priority: P0)

**Goal**: Infographic pipeline excludes RESOLVED findings from severity distribution, includes delta breakdown fields, and passes delta context to Gemini prompts.

**Independent Test**: Run extract-infographic-data.py on a threats.md with RESOLVED findings. Verify severity distribution excludes RESOLVED, delta_counts present in JSON output, and delta_status per finding in top findings list.

- [X] T010 [P] [US2] Update `scripts/extract-infographic-data.py` — import parse_baseline_frontmatter and parse_resolved_findings from tachi_parsers; call parse_baseline_frontmatter() for baseline detection; compute active-only severity counts (exclude RESOLVED); call parse_resolved_findings() for resolved count; add delta_counts object to JSON output; include delta_status per finding in top findings; guard all delta logic behind baseline presence check
- [X] T011 [P] [US2] Update threat-infographic agent instructions in `agents/threat-infographic.md` — add delta_status to input contract consumed fields; note RESOLVED findings excluded from severity distribution; add delta emphasis directives for visual design when delta data present
- [X] T012 [US2] Update infographic command in `.claude/commands/infographic.md` — detect baseline presence in source threats.md; pass delta context to agent noting delta_counts available; include delta emphasis directives in Gemini prompt construction

**Checkpoint**: Infographic pipeline produces accurate, delta-aware severity counts and visual emphasis on new findings.

---

## Phase 6: User Story 3 — Delta-Aware PDF Security Report (Priority: P1)

**Goal**: PDF security assessment separates RESOLVED findings into a dedicated section, annotates NEW findings, and includes delta counts in the executive summary.

**Independent Test**: Run extract-report-data.py on a delta-annotated threats.md. Verify report-data.typ includes delta_status per finding, resolved_findings list, and baseline metadata variables.

- [X] T013 [P] [US3] Update `scripts/extract-report-data.py` — import parse_baseline_frontmatter and parse_resolved_findings from tachi_parsers; call parse_baseline_frontmatter() and write baseline Typst variables; include delta_status per active finding in Typst data; call parse_resolved_findings() and write resolved_findings list; compute active vs total severity counts; guard all delta logic behind baseline presence check
- [X] T014 [P] [US3] Update report-assembler agent instructions in `.claude/agents/tachi/report-assembler.md` — separate findings into active and resolved lists when delta data present; annotate NEW findings with visual indicator in active table; render RESOLVED findings in separate section; include delta counts in executive summary; guard with no-baseline check
- [X] T015 [US3] Update security-report command in `.claude/commands/security-report.md` — detect baseline presence in source threats.md; pass delta context to report-assembler agent; include delta counts in artifact detection summary

**Checkpoint**: PDF pipeline renders delta-aware reports with separate resolved section and NEW finding annotations.

---

## Phase 7: Validation & Polish

**Purpose**: End-to-end validation across all output formats and backward compatibility regression.

- [X] T016 Run primary validation: execute baseline-compared threat model on second-brain-mcp (April 8 vs March 31 runs) — verify RESOLVED findings excluded from active counts in threat-report, infographic, and PDF; verify NEW findings highlighted; verify Section 8 Delta Summary present; verify delta counts in executive summaries
- [X] T017 Run regression validation: execute threat model without baseline (first run on fresh architecture) — verify output identical to pre-Feature-104 behavior; verify no Section 8, no delta annotations, no resolved sections; verify severity counts include all findings
- [X] T018 Update example outputs in `examples/` directory — regenerate all 6 example outputs with delta-aware pipeline to reflect new Section 7 Status column, Section 8 Delta Summary, and updated threat-report.md schema v1.1

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Schema Templates)**: No dependencies — can start immediately. All 3 tasks are parallel.
- **Phase 2 (Shared Parser)**: T004 and T005 have no cross-dependencies (parallel). T006 conceptually depends on T001 (Status column in Section 7 schema).
- **Phase 3 (US4 Validation)**: Depends on Phases 1 + 2 completion.
- **Phase 4 (US1 — Threat Report)**: Depends on Phase 1 (schema templates). Does NOT depend on Phase 2 (agent reads threats.md directly, not through shared parser).
- **Phase 5 (US2 — Infographics)**: Depends on Phase 2 (extraction script uses shared parser).
- **Phase 6 (US3 — PDF Report)**: Depends on Phase 2 (extraction script uses shared parser).
- **Phase 7 (Validation)**: Depends on all user stories completing.

### User Story Dependencies

- **US4 (Parser/Schema)**: Foundational — blocks US2 and US3 (extraction script dependency)
- **US1 (Threat Report)**: Independent of US2, US3 — reads threats.md directly, not through parser
- **US2 (Infographics)**: Independent of US1, US3 — but depends on shared parser (US4)
- **US3 (PDF Report)**: Independent of US1, US2 — but depends on shared parser (US4)

### Parallel Opportunities

- **Phase 1**: All 3 tasks (T001, T002, T003) run in parallel — different files
- **Phase 2**: T004 and T005 run in parallel — different functions in same file, non-overlapping
- **After Phase 1**: US1 (Phase 4) can start immediately — does not need shared parser
- **After Phase 2**: US2 (Phase 5) and US3 (Phase 6) can start in parallel
- **Maximum parallelism**: After foundational phases, US1 + US2 + US3 can all proceed simultaneously

---

## Implementation Strategy

### MVP First (US4 + US1)

1. Complete Phase 1: Schema Templates (3 parallel tasks)
2. Complete Phase 2: Shared Parser (3 tasks, 2 parallel)
3. Complete Phase 3: US4 Validation
4. Complete Phase 4: US1 Threat Report (2 tasks)
5. **STOP and VALIDATE**: Run threat-report agent on baseline-compared input
6. Deploy/demo threat report with delta awareness

### Incremental Delivery

1. Schema + Parser → Foundation ready
2. Add US1 (Threat Report) → Test independently → Primary output delta-aware
3. Add US2 (Infographics) → Test independently → Visual outputs delta-aware
4. Add US3 (PDF Report) → Test independently → All output formats delta-aware
5. Run validation → Confirm end-to-end correctness

### Parallel Team Strategy

After foundational phases complete:
- Agent A: US1 (Threat Report — agents/threat-report.md)
- Agent B: US2 (Infographics — extraction script + agent + command)
- Agent C: US3 (PDF Report — extraction script + agent + command)

All three complete independently and validate against the same test case.

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- All delta logic MUST be guarded behind baseline presence checks for backward compatibility
- Follow the delta-driven branching pattern from Feature 074 (risk-scorer, control-analyzer) for consistency
- 18 total tasks across 7 phases (3 foundational schema, 3 foundational parser, 1 validation, 2 US1, 3 US2, 3 US3, 3 validation/polish)
