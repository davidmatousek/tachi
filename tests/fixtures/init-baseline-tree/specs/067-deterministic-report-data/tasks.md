---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-30
    status: APPROVED
    notes: "All 6 user stories covered. All 27 FRs addressed. No scope creep. MVP strategy aligns with P1 priorities."
  architect_signoff:
    agent: architect
    date: 2026-03-30
    status: APPROVED_WITH_CONCERNS
    notes: "2 minor concerns: (1) T013 generate_report_data_typ is dense — may benefit from helper functions during implementation. (2) T017 scope parsing breadth — 4 table types in one task. Both acceptable for single-file script. 27/27 FRs covered."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-30
    status: APPROVED
    notes: "Feasible. 32 tasks across 5 execution waves. ~4h estimated. MVP (Phases 1-3) meaningful and verifiable. Critical path correctly identified. Single-file constraint honestly limits parallelism."
---

# Tasks: Deterministic Report Data Extraction

**Input**: Design documents from `/specs/067-deterministic-report-data/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: No test framework requested. Determinism and correctness are validated by running the script against example datasets and using `diff`.

**Organization**: Tasks are grouped by implementation phase, with user story traceability via [US] labels.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Create the script skeleton with CLI argument parsing and artifact detection.

- [X] T001 Create `scripts/extract-report-data.py` with argparse CLI: `--target-dir`, `--output`, `--template-dir`, `--title` arguments, and exit code constants (0, 1, 2)
- [X] T002 Implement artifact detection function in `scripts/extract-report-data.py`: scan target directory for threats.md (required), risk-scores.md, compensating-controls.md, threat-report.md, infographic JPEGs, brand assets; exit code 1 if threats.md missing
- [X] T003 Implement tier selection logic in `scripts/extract-report-data.py`: Tier 1 if compensating-controls.md exists, Tier 2 if risk-scores.md exists, Tier 3 otherwise

**Checkpoint**: Script runs, detects artifacts, selects tier, exits cleanly.

---

## Phase 2: Core Parsing (Foundational)

**Purpose**: Implement the parsers that all tiers depend on — frontmatter, section anchoring, table parsing, and string escaping utilities.

- [X] T004 [P] Implement `parse_frontmatter()` in `scripts/extract-report-data.py`: regex-based extraction of `date`, `classification`, `schema_version` from YAML frontmatter between `---` delimiters; handle nested keys by extracting only top-level values needed
- [X] T005 [P] Implement `parse_markdown_table()` utility in `scripts/extract-report-data.py`: find table by section header anchor, parse header row for column names, skip separator row, extract data rows with `|`-splitting and stripping; skip malformed rows with warning to stderr
- [X] T006 [P] Implement `strip_bold()` and `escape_typst_string()` utilities in `scripts/extract-report-data.py`: strip `**` markers from cell values; escape `"` to `\"`, `\` to `\\`, newlines to `\n` for Typst strings
- [X] T007 Implement `parse_project_name()` in `scripts/extract-report-data.py`: extract name from `# Threat Model: {name}` heading, with `--title` override taking precedence

**Checkpoint**: Utility functions complete. Individual parsers can now be built on top.

---

## Phase 3: User Story 1 — Reproducible Report Generation (Priority: P1) MVP

**Goal**: Parse threats.md and risk-scores.md to produce a deterministic Tier 2 `report-data.typ` from the agentic-app example dataset.

**Independent Test**: Run script twice on `examples/agentic-app/sample-report/`, diff the two outputs — zero differences.

### Implementation for User Story 1

- [X] T008 [US1] Implement `parse_threats_severity()` in `scripts/extract-report-data.py`: parse Section 6 Risk Summary table from threats.md; extract Critical, High, Medium, Low, Note counts; handle Total row "N (M raw)" format using regex; strip bold markers
- [X] T009 [US1] Implement `parse_threats_findings()` in `scripts/extract-report-data.py`: parse Section 7 Recommended Actions table for Tier 3 findings (id, component, threat, risk_level, mitigation); set likelihood and impact to em dash
- [X] T010 [US1] Implement `parse_risk_scores_severity()` in `scripts/extract-report-data.py`: parse risk-scores.md Section 1 severity distribution table; prefer these counts over threats.md when Tier 2
- [X] T011 [US1] Implement `parse_risk_scores_findings()` in `scripts/extract-report-data.py`: parse risk-scores.md Section 2 Scored Threat Table for Tier 2 findings (id, component, threat, composite_score, severity, cvss, exploitability)
- [X] T012 [US1] Implement `parse_component_distribution()` in `scripts/extract-report-data.py`: count findings per component from the active findings table, sort by count descending
- [X] T013 [US1] Implement `generate_report_data_typ()` in `scripts/extract-report-data.py`: format all extracted data as Typst `#let` variable bindings following the exact variable names and types from the report-assembler agent Steps 3a-3q; output complete file with header comment, metadata, severity counts, page flags, tier, image paths, findings array, scope data, brand assets, page visibility
- [X] T014 [US1] Wire `main()` in `scripts/extract-report-data.py`: connect CLI args → artifact detection → tier selection → parsers → Typst generation → file write; verify determinism by running twice on `examples/agentic-app/sample-report/` and diffing output

**Checkpoint**: Tier 2 works end-to-end. Running twice produces byte-identical output. MVP complete.

---

## Phase 4: User Story 2 — Validated Severity Counts (Priority: P1)

**Goal**: Add internal consistency validation so severity count mismatches are caught before PDF generation.

**Independent Test**: Run script on valid data (exit 0), then inject a count mismatch and verify exit code 2 with descriptive error.

### Implementation for User Story 2

- [X] T015 [US2] Implement `validate()` in `scripts/extract-report-data.py`: check (a) critical + high + medium + low == total - note_count, (b) all finding IDs unique; return list of error messages; exit code 2 with stderr description if any check fails
- [X] T016 [US2] Add Note severity handling in `scripts/extract-report-data.py`: parse Note row from Risk Summary, expose as `note-count` Typst variable, exclude from four-level validation sum

**Checkpoint**: Validation catches severity sum mismatches and duplicate IDs.

---

## Phase 5: User Story 3 — Deterministic Scope Data Extraction (Priority: P1)

**Goal**: Extract scope data (components, data flows, trust boundaries, boundary crossings) deterministically from threats.md Sections 1-2.

**Independent Test**: Run script on agentic-app dataset and verify scope counts in output match source table row counts.

### Implementation for User Story 3

- [X] T017 [US3] Implement `parse_scope_data()` in `scripts/extract-report-data.py`: parse threats.md Section 1 for components table (name, type, description) and data flows table (source, destination, data, protocol); parse Section 2 for trust zones table (zone, trust-level, components) and boundary crossings table (crossing, from-zone, to-zone, components, controls); compute counts for each category
- [X] T018 [US3] Add scope validation to `validate()` in `scripts/extract-report-data.py`: verify len(scope_components) == scope_component_count and len(scope_data_flows) == scope_data_flow_count; gracefully handle missing sections (empty arrays, zero counts, warning)

**Checkpoint**: Scope data is extracted deterministically with count validation.

---

## Phase 6: User Story 4 — Agent Prompt Update (Priority: P1)

**Goal**: Update the report-assembler agent to invoke the Python script instead of LLM-based parsing.

**Independent Test**: Run `/security-report` on agentic-app dataset and verify it invokes the script, generates PDF, and exits successfully.

### Implementation for User Story 4

- [X] T019 [US4] Update `.claude/agents/tachi/report-assembler.md`: replace Steps 2-3 (Data Extraction + Typst Data Generation) with a single Step 2 that invokes `python3 scripts/extract-report-data.py --target-dir {target_dir} --output templates/tachi/security-report/report-data.typ --template-dir templates/tachi/security-report/ [--title "{title_override}"]`; add exit code handling (0=proceed to Step 3 compilation, 1=abort with error, 2=abort with validation details); renumber remaining steps; preserve Step 1 (Artifact Detection) and current Step 4 (Compilation) unchanged
- [X] T020 [US4] Update Step 2j (report-config.typ copy) in `.claude/agents/tachi/report-assembler.md`: ensure report-config.typ copy behavior remains in the agent orchestration (before script invocation), not in the script, per architect's concern

**Checkpoint**: Agent invokes script. Full `/security-report` pipeline works end-to-end.

---

## Phase 7: User Story 5 — Consistent Recommendation Formatting (Priority: P2)

**Goal**: Extract recommendations verbatim with proper Typst escaping.

**Independent Test**: Run script twice, compare recommendation text in output — character-identical.

### Implementation for User Story 5

- [X] T021 [US5] Implement `parse_threat_report_md()` in `scripts/extract-report-data.py`: extract executive narrative from Section 1 (Risk Posture + Top 5 Threats + Key Recommendations), truncate to 2000 chars if needed; extract remediation actions from Remediation Timeline section
- [X] T022 [US5] Implement `parse_compensating_controls_md()` in `scripts/extract-report-data.py`: parse Section 2 Coverage Matrix for Tier 1 findings (id, component, threat, residual_score, residual_severity, control_status, recommendation); parse STRIDE coverage matrix (per-category found/partial/missing); parse Section 3 detailed controls (component, category, status, evidence, effectiveness); compute coverage summary (total-found, total-partial, total-missing)
- [X] T023 [US5] Implement remediation source priority in `scripts/extract-report-data.py`: use compensating-controls.md Section 3 recommendations if available, else threat-report.md Remediation Timeline, else `none`; derive SLA from severity (Critical=7d, High=14d, Medium=30d, Low=90d)

**Checkpoint**: Tier 1 parsing complete. All three tiers functional. Recommendations extracted verbatim.

---

## Phase 8: User Story 6 — Testing Against Both Example Datasets (Priority: P2)

**Goal**: Validate correctness across example datasets and all three tier configurations.

**Independent Test**: Run script on each dataset, verify output against expected values, confirm determinism.

### Implementation for User Story 6

- [X] T024 [P] [US6] Implement `detect_images()` and `detect_brand_assets()` in `scripts/extract-report-data.py`: check image file existence and non-zero size for infographic JPEGs and brand logos; compute relative paths from template directory using `../../{target_dir}/` pattern; set page inclusion flags
- [X] T025 [US6] Implement schema v1.0 compatibility in `scripts/extract-report-data.py`: check `schema_version` from frontmatter, skip Section 4a parsing for v1.0, log info message
- [X] T026 [US6] Verify script against `examples/agentic-app/sample-report/` (Tier 2): run twice, diff outputs, verify severity counts match source, verify scope data counts match source
- [X] T027 [US6] Create Tier 1 test fixture at `examples/agentic-app/sample-report/compensating-controls.md` per the compensating-controls.yaml schema: include Section 2 Coverage Matrix with residual severity counts and Section 3 detailed controls for at least 5 findings
- [X] T028 [US6] Verify script against Tier 1 fixture: run with compensating-controls.md present, verify Tier 1 output with residual severity counts, coverage matrix, and detailed controls
- [X] T029 [US6] Verify script against Tier 3 scenario: run on agentic-app dataset with risk-scores.md temporarily excluded, verify Tier 3 output with Section 7 findings and Section 6 severity counts

**Checkpoint**: All three tiers verified. Determinism confirmed on both datasets.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, end-to-end PDF verification, and cleanup.

- [X] T030 Run full `/security-report` end-to-end on agentic-app dataset: verify PDF generated, severity counts on cover match source, scope page data correct
- [X] T031 Run full `/security-report` twice on same dataset and verify byte-identical PDF output
- [X] T032 Verify error handling: run with missing threats.md (expect exit 1), run with injected severity mismatch (expect exit 2)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Core Parsing)**: Depends on Phase 1 — utility functions block all parsers
- **Phase 3 (US1)**: Depends on Phase 2 — MVP tier 2 parsing
- **Phase 4 (US2)**: Depends on Phase 3 — validation uses parsed data
- **Phase 5 (US3)**: Depends on Phase 2 — scope parsing uses table utility; can parallel with Phase 3-4
- **Phase 6 (US4)**: Depends on Phase 3 — agent needs working script
- **Phase 7 (US5)**: Depends on Phase 2 — Tier 1 parsing; can parallel with Phases 3-5
- **Phase 8 (US6)**: Depends on Phases 3-7 — all parsers must be complete for tier testing
- **Phase 9 (Polish)**: Depends on all phases

### User Story Dependencies

- **US1 (Reproducible)**: Core — all other stories depend on this
- **US2 (Validation)**: Depends on US1 (needs parsed data to validate)
- **US3 (Scope)**: Independent of US1/US2 after Phase 2 utilities
- **US4 (Agent Update)**: Depends on US1 (needs working script)
- **US5 (Recommendations)**: Independent after Phase 2 utilities (adds Tier 1 + threat-report parsers)
- **US6 (Testing)**: Depends on all stories (integration testing)

### Parallel Opportunities

- **Phase 2**: T004, T005, T006 can all run in parallel (independent utility functions)
- **Phase 5 + Phase 3-4**: Scope parsing (T017-T018) can run in parallel with US1 severity/findings work
- **Phase 7 + Phase 3-5**: Tier 1 parsing (T022-T023) can run in parallel with Tier 2/3 work
- **Phase 8**: T024 (image detection) can run in parallel with other US6 tasks

---

## Implementation Strategy

### MVP First (Phase 1-3: Tier 2 Determinism)

1. Complete Phase 1: Setup (script skeleton)
2. Complete Phase 2: Core Parsing (utilities)
3. Complete Phase 3: US1 (Tier 2 end-to-end)
4. **STOP and VALIDATE**: Run twice on agentic-app, diff outputs — zero differences
5. This is the MVP — deterministic Tier 2 report generation

### Incremental Delivery

1. MVP (Phases 1-3) → Tier 2 determinism verified
2. Add US2 (Phase 4) → Validation catches data errors
3. Add US3 (Phase 5) → Scope data deterministic
4. Add US4 (Phase 6) → Agent integrated, `/security-report` works
5. Add US5 (Phase 7) → All three tiers, recommendations, narratives
6. Add US6 (Phase 8) → Full test coverage across datasets
7. Polish (Phase 9) → End-to-end PDF verification

---

## Notes

- [P] tasks = different files or independent functions, no dependencies
- [Story] label maps task to specific user story for traceability
- All implementation is in a single file: `scripts/extract-report-data.py`
- Agent update is a separate file: `.claude/agents/tachi/report-assembler.md`
- Determinism is verified at each phase by running twice and diffing
