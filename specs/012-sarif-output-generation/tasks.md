---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-22
    status: APPROVED
    notes: "All 4 user stories covered with [US*] traceability. All 12 spec FRs traced. No scope creep. MVP clearly identified at Phase 3 with STOP and VALIDATE gate."
  architect_signoff:
    agent: architect
    date: 2026-03-22
    status: APPROVED_WITH_CONCERNS
    notes: "1 medium: T014 trust_zone cross-reference needs explicit Phase 1 Trust Zones table lookup. 3 low: line number fragility, [P] marking, insertion point estimate. All addressable during implementation."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-22
    status: APPROVED_WITH_CONCERNS
    notes: "20 tasks across 7 phases appropriate. Critical path correct. 100% FR coverage. 1 medium: T002 [P] targets same file as T001 — execute sequentially. Maximize Wave 5 parallelism for US2-4."
---

# Tasks: SARIF Output Generation

**Input**: Design documents from `/specs/012-sarif-output-generation/`
**Prerequisites**: plan.md (required), spec.md (required), research.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. All deliverables are markdown/YAML/JSON prompt files — no application code.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Prepare orchestrator for SARIF generation extension

- [X] T001 Add SARIF output reference to orchestrator frontmatter `references` block in `agents/orchestrator.md` — add `sarif_template: templates/threats.sarif` and update `description` to mention both threats.md and threats.sarif output
- [X] T002 [P] Update the Output Format Specification preamble in `agents/orchestrator.md` (line 73 area) to state that every invocation produces both `threats.md` AND `threats.sarif` in the same output directory

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Schema fix and reference template that all user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 [P] Update SARIF Severity Mapping comment block in `schemas/output.yaml` (lines 156-164) — change Note row from `none | 0.0` to `note | 0.1` per spec FR-005 Note-level fix. Update ONLY the Note row — do not change CVSS ranges for other levels (per Architect review M-02)
- [X] T004 [P] Create SARIF 2.1.0 reference template at `templates/threats.sarif` with complete JSON structure including: `$schema`, `version: "2.1.0"`, `runs[]` with `tool.driver` (name: "Tachi", semanticVersion, informationUri, rules[]), example `result` objects showing all mapped fields from FR-003, example `relatedLocations` for correlated findings, example `partialFingerprints` with `primaryLocationLineHash`, `findingId/v1`, and `correlationGroup`, and dual-location example (physicalLocation + logicalLocations). Include inline comments explaining each placeholder value.

**Checkpoint**: Schema fixed, reference template created — orchestrator extension can begin

---

## Phase 3: User Story 1 — Export Threat Findings as SARIF 2.1.0 (Priority: P0) MVP

**Goal**: Orchestrator produces a valid `threats.sarif` file alongside `threats.md` with all findings mapped to SARIF results

**Independent Test**: Run orchestrator against `examples/mermaid-agentic-app/input.md` and verify `threats.sarif` is produced with results matching findings in `threats.md`

### Implementation for User Story 1

- [X] T005 [US1] Add new "SARIF Output Generation" section header to `agents/orchestrator.md` Phase 4, positioned after the existing "Output Structural Validation" section (after line ~1050). Include introductory paragraph explaining that Phase 4 now produces both `threats.md` and `threats.sarif` using the same finding data collected in Phase 3.

- [X] T006 [US1] Add Category → Rule ID Mapping Table to the SARIF section in `agents/orchestrator.md` — embed the canonical mapping from spec FR-004 with all 8 rows: `spoofing`→`tachi/stride/spoofing`, `tampering`→`tachi/stride/tampering`, `repudiation`→`tachi/stride/repudiation`, `info-disclosure`→`tachi/stride/information-disclosure`, `denial-of-service`→`tachi/stride/denial-of-service`, `privilege-escalation`→`tachi/stride/elevation-of-privilege`, `agentic`→`tachi/ai/agentic-threats`, `llm`→`tachi/ai/llm-threats`. Include note about the `info-disclosure`→`information-disclosure` and `privilege-escalation`→`elevation-of-privilege` naming normalization.

- [X] T007 [US1] Add Severity Mapping Table to the SARIF section in `agents/orchestrator.md` — embed the CVSS alignment table from spec FR-005: Critical→error/"9.0", High→error/"8.0", Medium→warning/"5.0", Low→note/"2.0", Note→note/"0.1". Include explicit note that `security-severity` MUST be a numeric string and that Note maps to 0.1 (not 0.0).

- [X] T008 [US1] Add SARIF Tool Metadata instructions to `agents/orchestrator.md` — per spec FR-006, instruct the LLM to populate `tool.driver` with `name: "Tachi"`, `semanticVersion` from output.yaml `schema_version` field, `informationUri` from repository URL, and `rules[]` array containing only `reportingDescriptor` objects for categories that produced findings in the current run.

- [X] T009 [US1] Add Rule Definition Templates to `agents/orchestrator.md` — for each of the 8 threat categories, provide a `reportingDescriptor` template structure including `id` (rule ID from mapping table), `shortDescription.text` (max 255 chars), `fullDescription.text` (max 1024 chars), `help.text` (plain text detection guidance), `help.markdown` (markdown with OWASP/CWE/MITRE framework references from the finding IR `references` field), and `properties.tags` array (max 20 tags, e.g., `["security", "stride", "spoofing"]`). Include concrete examples for at least spoofing, info-disclosure, and agentic-threats.

- [X] T010 [US1] Add Finding IR → SARIF Result Mapping Instructions to `agents/orchestrator.md` — embed the complete field-by-field mapping from spec FR-003 as a step-by-step instruction set. For each finding collected in Phase 3, instruct the LLM to: create a `result` object, set `ruleId` from category mapping table, set `message.text` from `threat` field, set `message.markdown` from `mitigation` field, set `level` from severity mapping table, compute `properties.security-severity` as numeric string from severity table. Use probabilistic language guidance ("may", "could" not "can", "will") for threat descriptions.

- [X] T011 [US1] Add SARIF Schema Compliance Structure to `agents/orchestrator.md` — per spec FR-009, provide the exact top-level JSON structure the LLM must produce: `$schema` URI, `version: "2.1.0"`, single `runs[]` entry with `tool.driver` and `results[]`. Include the complete schema URI: `https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json`

- [X] T012 [US1] Add JSON Structural Self-Check to `agents/orchestrator.md` — per spec FR-010, add a validation checklist the LLM must run before outputting the SARIF file: (1) all required properties present, (2) every result has ruleId/message.text/level/locations/partialFingerprints, (3) every ruleId has corresponding entry in rules[], (4) security-severity is numeric string matching severity table, (5) result count matches expected finding count. Include "if any check fails, correct before proceeding" instruction.

**Checkpoint**: At this point, the orchestrator can produce a basic SARIF file with all findings mapped. US1 is independently testable.

---

## Phase 4: User Story 2 — Correlated Findings in SARIF (Priority: P1)

**Goal**: Correlation groups from F-010 are represented in SARIF via `relatedLocations` and `partialFingerprints.correlationGroup`

**Independent Test**: Run orchestrator against an input producing correlated findings and verify primary findings have `relatedLocations[]` with peer IDs and `correlationGroup` in fingerprints

### Implementation for User Story 2

- [X] T013 [US2] Add Correlated Finding Mapping Instructions to `agents/orchestrator.md` SARIF section — per spec FR-007, instruct the LLM: (1) for each correlation group from Section 4a, identify the primary finding (first listed), (2) create a full SARIF `result` for the primary finding, (3) add correlated peers to `relatedLocations[]` with their finding IDs and component names as `logicalLocations`, (4) store the correlation group ID in `partialFingerprints["correlationGroup"]` (e.g., "CG-1"), (5) do NOT create separate top-level results for correlated peers. Include handling for zero-correlation case (skip relatedLocations, no correlationGroup key).

**Checkpoint**: Correlated findings correctly represented. US2 independently testable.

---

## Phase 5: User Story 3 — Architecture Component Navigation (Priority: P1)

**Goal**: Every SARIF result includes both physical and logical location information for component-level navigation

**Independent Test**: Generate SARIF from a multi-component input and verify each result has physicalLocation (input file, startLine: 1) and logicalLocations (component name, trust zone, DFD kind)

### Implementation for User Story 3

- [X] T014 [US3] Add Dual-Location Instructions to `agents/orchestrator.md` SARIF section — per spec FR-011, instruct the LLM to add both location types to every result: (1) `physicalLocation.artifactLocation.uri` set to the input architecture file path, `region.startLine` set to 1 (architecture-level analysis has no line granularity), (2) `logicalLocations[]` array with one entry per finding: `name` = component name from finding IR, `fullyQualifiedName` = "{trust_zone}/{component_name}" (cross-reference trust zone from Phase 1 Trust Boundaries data — Architect concern M-01), `kind` = DFD element type mapped to lowercase-hyphenated custom values (`External Entity`→`external-entity`, `Process`→`process`, `Data Store`→`data-store`, `Data Flow`→`data-flow`). Include note that `logicalLocations` is not displayed by GitHub Code Scanning but benefits VS Code SARIF Viewer and Azure DevOps.

**Checkpoint**: Dual locations present on all results. US3 independently testable.

---

## Phase 6: User Story 4 — Stable Finding Tracking (Priority: P1)

**Goal**: SARIF results include deterministic `partialFingerprints` enabling GitHub Code Scanning to track findings across runs

**Independent Test**: Run orchestrator twice against same input, verify `primaryLocationLineHash` values are identical for same category+component combinations

### Implementation for User Story 4

- [X] T015 [US4] Add Fingerprint Computation Instructions to `agents/orchestrator.md` SARIF section — per spec FR-008, instruct the LLM to compute `partialFingerprints` for every result: (1) `primaryLocationLineHash` = deterministic hash of `ruleId` + `component_name`, formatted as SHA-256 truncated to 16 hex characters (instruct LLM to produce a consistent hash by concatenating ruleId and component name with a separator, e.g., `"tachi/stride/spoofing|API Gateway"` → compute hash), (2) `findingId/v1` = the finding IR `id` value (e.g., `"S-1"`, `"AG-2"`) for cross-reference to threats.md. Include note that `primaryLocationLineHash` is the key GitHub uses for alert dedup — it must be deterministic and stable.

**Checkpoint**: Fingerprints present and deterministic. US4 independently testable.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validation, P1 enhancement, and cross-cutting updates

- [X] T016 [P] Validate SARIF output by running orchestrator against `examples/mermaid-agentic-app/input.md` — verify threats.sarif is produced alongside threats.md, contains results for both STRIDE and AI categories, severity levels match threats.md, all results have dual locations and fingerprints
- [X] T017 [P] Validate SARIF output by running orchestrator against `examples/ascii-web-api/input.md` — verify threats.sarif contains STRIDE-only findings (no AI rules in tool.driver.rules[])
- [X] T018 Validate SARIF schema compliance — verify the generated JSON structure matches SARIF 2.1.0 schema requirements: required properties present, security-severity is numeric string, rule descriptions within GitHub limits (255 char name, 1024 char descriptions, 20 tags)
- [X] T019 [P] Add SARIF taxonomies support (P1/Should Have) to `agents/orchestrator.md` — per spec FR-012, add optional instructions for `run.taxonomies[]` array declaring OWASP and CWE frameworks as `toolComponent` entries, `tool.driver.supportedTaxonomies[]` references, and `rule.relationships[]` mapping rules to taxonomy entries via `target.id` and `target.toolComponent.name`. Mark as optional ("if taxonomies are requested" or enable by default as P1 enhancement).
- [X] T020 Update orchestrator output self-check section in `agents/orchestrator.md` to verify both `threats.md` AND `threats.sarif` are produced — extend the existing structural validation checklist to include SARIF file existence and basic structure check

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: No hard dependency on Phase 1, but logically follows — BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Phase 2 completion (severity table and template must exist before orchestrator references them)
  - US1 (Phase 3) delivers core MVP — must complete first
  - US2, US3, US4 (Phases 4-6) can proceed in parallel after US1 or sequentially
- **Polish (Phase 7)**: Depends on all user story phases being complete

### User Story Dependencies

- **US1 (P0)**: Can start after Phase 2 — no dependencies on other stories. Delivers independently testable MVP.
- **US2 (P1)**: Depends on US1 (needs basic SARIF result structure to add relatedLocations). Can start after Phase 3 checkpoint.
- **US3 (P1)**: Depends on US1 (needs basic SARIF result structure to add locations). Can start after Phase 3 checkpoint. Can run in parallel with US2.
- **US4 (P1)**: Depends on US1 (needs basic SARIF result structure to add fingerprints). Can start after Phase 3 checkpoint. Can run in parallel with US2 and US3.

### Parallel Opportunities

- T003 and T004 can run in parallel (different files)
- T016 and T017 can run in parallel (different example inputs)
- US2, US3, and US4 can all run in parallel after US1 completes (all modify different sections of the orchestrator SARIF block)
- T019 can run in parallel with T016-T018 (additive P1 enhancement)

---

## Parallel Example: Phase 2 (Foundational)

```bash
# Wave 1 — both tasks target different files:
Task: "T003 Update SARIF Severity Mapping in schemas/output.yaml"
Task: "T004 Create SARIF reference template at templates/threats.sarif"
```

## Parallel Example: Phase 4-6 (P1 Stories after US1 MVP)

```bash
# Wave 2 — all tasks add different sub-sections to orchestrator.md SARIF block:
Task: "T013 [US2] Correlated Finding Mapping in agents/orchestrator.md"
Task: "T014 [US3] Dual-Location Instructions in agents/orchestrator.md"
Task: "T015 [US4] Fingerprint Computation in agents/orchestrator.md"
```

**Note**: While US2-4 all modify `agents/orchestrator.md`, they add separate sub-sections with no overlap. Sequential execution is safer for a single agent; parallel is viable if each agent appends to a designated section.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 2: Foundational (T003-T004)
3. Complete Phase 3: User Story 1 (T005-T012)
4. **STOP and VALIDATE**: Run against mermaid example, verify SARIF output
5. Deploy/demo if ready — MVP delivers core SARIF export value

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 (core SARIF export) → Test → Validate (MVP!)
3. US2 (correlated findings) → Test → Validate
4. US3 (component navigation) → Test → Validate
5. US4 (stable tracking) → Test → Validate
6. Polish (validation + taxonomies) → Final validation

### Total: 20 tasks across 7 phases

| Phase | Tasks | Parallel | Description |
|-------|-------|----------|-------------|
| 1: Setup | 2 | 1 | Orchestrator prep |
| 2: Foundational | 2 | 2 | Schema fix + template |
| 3: US1 (P0) | 8 | 0 | Core SARIF mapping (MVP) |
| 4: US2 (P1) | 1 | 0 | Correlated findings |
| 5: US3 (P1) | 1 | 0 | Dual locations |
| 6: US4 (P1) | 1 | 0 | Fingerprints |
| 7: Polish | 5 | 3 | Validation + taxonomies |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- All tasks produce markdown, YAML, or JSON — no application code
- Commit after each phase completion
- Stop at any checkpoint to validate independently
- Architect concern M-01 (trust_zone cross-reference) addressed in T014 task description
- Architect concern M-02 (output.yaml update scope) addressed in T003 task description
