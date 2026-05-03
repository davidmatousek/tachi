---
description: "Task list for Feature 189 — F-A2 Source Attribution Schema Extension"
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-17
    status: APPROVED_WITH_CONCERNS
    notes: "Strong coverage: US1/US2/US3 complete independent test slices. FR mapping solid — FR-001→T004, FR-002/003/004/005→T004, FR-006→T010+T016, FR-007→T010+T011, FR-008→T027, FR-009→T026, FR-010 surface-neutral, FR-011→T008/T009/T021/T022/T024, FR-012→T017, FR-013→T025, FR-014→T001/T031, FR-015→T032, FR-016→T032. SC mapping: SC-001→T032, SC-002→T017, SC-003→T008/T009/T014, SC-004→T021/T022/T024, SC-005→T001/T031/T036, SC-006/007→T032. T032 grep audit enumerates all 22 paths. MVP independence preserved. 3 LOW concerns (non-blocking): T005 [P] same-file-as-T004 is honestly flagged; no explicit SC-gate task for validate_source_attribution wiring; Checkpoint 4 'stakeholder demo' phrasing slightly aggressive — none blocking."
  architect_signoff:
    agent: architect
    date: 2026-04-17
    status: APPROVED
    notes: "Critical path T001→T004→T010→T017→T031 correct and explicit. T001 gates T004; T004 gates all US work. Q1/Q2 surface/phase neutrality fully preserved: T006, T010, T011 describe both Q1-E and Q1-B branches without prejudging; T011 is shape-only. ADR-028 dual-commit governance mirrors F-A1/ADR-027 exactly: T001 Proposed at Day 1 Wave 1.1 with all 6 FR-014 body items enumerated; T031 Accepted at Day 3 Wave 6.1; T036 post-merge SHA fill. T032 SC-007 grep covers correct 22 files. T028 determinism check explicit (no HTTP, no env, no timestamps, no module-level state). Test-first ordering clean. [P] markers correctly exclude same-file conflicts. Six checkpoints represent resumable states. T005 [P] with T004 is honestly flagged as same-file authoring-prep only."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-17
    status: APPROVED_WITH_CONCERNS
    notes: "Timeline envelope fits 2026-04-20 → 2026-04-22. Critical path realistic with Wave 3.1/4.1/5.1 fixture parallelism. Task atomicity good (1-3h except T001/T010/T027 which are 3-4h). Q1-E→Q1-B fallback is surface-neutral, so mid-Day 2 pivot does not require task rewrite. T017 SC-2 regression positioned early Day 2 PM, leaving Day 3 AM as diagnostic buffer. T036 scoped out-of-PR correctly. 4 concerns addressable in agent-assignments.md: (1) T017 needs tester primary / senior-backend-engineer secondary encoded per PRD Milestones table; (2) T001 architect assignment explicit in agent-assignments; (3) Wave 3.1/4.1/5.1 fixture tasks ~10 in one half-day tight for single-developer — agent-assignments notes this as contingency lever; (4) T034 full pytest placement Day 3 PM should add earlier gate post-T028 to catch regressions before ADR Accepted flip."
---

# Tasks: Source Attribution Schema Extension (F-A2, Feature 189)

**Input**: Design documents from `/specs/189-source-attribution-schema-extension/`
**Prerequisites**: plan.md (approved PM + Architect), spec.md (approved PM), research.md, data-model.md, contracts/

**Tests**: Included. Testing Excellence is Constitution Principle VI; spec FR-011, FR-012, FR-013 require unit, integration, and referential-integrity coverage.

**Organization**: Tasks are grouped by user story (US1, US2, US3), each at P1 priority and independently testable per spec. MVP = US1 (schema shape). Incremental delivery adds US2 (round-trip) and US3 (validation).

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: US1 (Multi-Framework Citation), US2 (Parser Round-Trip), US3 (Closed-Enum + Referential Integrity)
- File paths are absolute relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Decision prerequisites — Q1, Q2, Q3 resolution landing in ADR-028 Proposed commit.

**Wave 1.1 (Day 1 AM, 2026-04-20)**

- [X] T001 Draft architect memo resolving Open Questions Q1 (serialization surface: Q1-E primary / Q1-B fallback), Q2 (referential-integrity phase: Q2-B preferred), Q3 (ADR number: ADR-028 unless another ADR lands first). Memo lives inline in the ADR-028 Proposed body — no sidecar file. Save draft at `docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md` with `Status: Proposed`. Include all 6 required body items per spec FR-014 — additive-optional-field decision + Complex-Shape Addition Clarifier lineage under ADR-026; serialization surface choice; 5-value taxonomy enum scope + rationale; relationship enum + default-to-primary; referential-integrity contract; 22-file zero-edit invariant per ADR-023.
- [X] T002 [P] Create fixture directory `tests/scripts/fixtures/source_attribution/` with `.gitkeep` placeholder. Q1-independent.
- [X] T003 [P] Verify baseline state: run `git diff main -- schemas/ scripts/ tests/ docs/architecture/ README.md` and confirm no uncommitted drift that would pollute the F-A2 diff. Output to terminal; no file written.

**Checkpoint 1**: ADR-028 Proposed commit lands with Q1+Q2 resolutions. Schema YAML authoring (Phase 2) can begin.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Schema lock — `schemas/finding.yaml` 1.4 → 1.5 with `source_attribution` field declared. No user-story implementation can begin until this phase is complete because every downstream task reads the schema shape.

**CRITICAL**: No user story work can begin until this phase is complete.

**Wave 2.1 (Day 1 PM, 2026-04-20)**

- [X] T004 Modify `schemas/finding.yaml` — bump `schema_version: "1.4"` → `"1.5"` at line 13. Append new optional `source_attribution` field as the last field under top-level `finding:` mapping (after `baseline_run_id` at line 208). Field shape per data-model.md: `type: list[record]`, record shape `{taxonomy: string (5-value enum), id: string, relationship: string (3-value enum, default primary)}`. Include inline comments matching the `agentic_pattern` (Feature 142) and `delta_status` (Feature 104) style, noting ADR-028 as the authoritative decision record. Preserve all 14 existing fields byte-identically.
- [X] T005 [P] Author `schemas/finding.yaml` comment block referencing the Feature 189 schema evolution (matching the "v1.2 MAESTRO Layer Classification" and "v1.4 Agentic Pattern Classification" section-header style at lines 122 and 147).

**Checkpoint 2**: Schema file carries `schema_version: "1.5"` + new `source_attribution` field declaration. Parser and validator implementation can begin. Test fixture authoring can begin.

---

## Phase 3: User Story 1 — Multi-Framework Citation on a Single Finding (Priority: P1) MVP

**Goal**: Prove a finding can carry 3 `source_attribution` records spanning 3 distinct taxonomies (OWASP LLM05, CWE-1426, MITRE ATLAS AML.T0051) end-to-end — from YAML fixture through `parse_threats_findings` to returned dict preserving input order verbatim.

**Independent Test**: Hand-author `valid_multi_record.md` fixture; run `parse_threats_findings`; assert the returned finding dict has `source_attribution` key with 3 records in input order with all `{taxonomy, id, relationship}` fields intact.

### Tests for User Story 1

**NOTE**: Write these tests FIRST; ensure they FAIL before implementation (per Constitution Principle VI test-first convention).

- [X] T006 [P] [US1] Author fixture `tests/scripts/fixtures/source_attribution/valid_multi_record.md` — one threats.md-shaped document containing one finding with `source_attribution` array of 3 records spanning owasp/LLM05, cwe/CWE-1426, mitre-atlas/AML.T0051 (all `relationship: primary`). Embed the attribution via the Q1-resolved serialization surface — Q1-E conditional Section 9 YAML block keyed by finding ID, OR Q1-B co-located `valid_multi_record-attribution.yaml` sidecar file if Q1-B is selected. Fixture file names mirror Feature 142's fixture naming convention.
- [X] T007 [P] [US1] Author fixture `tests/scripts/fixtures/source_attribution/valid_single_record.md` — one finding with one attribution record carrying `taxonomy: owasp, id: A01` (no explicit relationship, to exercise the default-injection path).
- [X] T008 [US1] Add test function `test_round_trip_multi_record` to `tests/scripts/test_source_attribution.py` (new file) — loads `valid_multi_record.md`, invokes `parse_threats_findings`, asserts returned finding dict has `source_attribution` key with exactly 3 records in input order; every record has all 3 keys populated; values match input verbatim.
- [X] T009 [US1] Add test function `test_round_trip_single_record` to `tests/scripts/test_source_attribution.py` — loads `valid_single_record.md`, asserts single-record round-trip with `relationship` defaulted to `"primary"` by the parser.

### Implementation for User Story 1

- [X] T010 [US1] Extend `scripts/tachi_parsers.py::parse_threats_findings` (line 621) — add a new helper function `_extract_source_attribution(document_or_row, finding_id) -> list[dict] | None` that reads from the Q1-resolved serialization surface. For Q1-E: search for `## 9. Source Attribution` section header in content; parse the YAML code fence inside; return the list keyed by `finding_id`, or None if the section is absent or the finding ID is not keyed. For Q1-B: try-read a co-located `threats-attribution.yaml` file; return the list keyed by `finding_id`, or None if the file or key is absent. Inject `relationship: "primary"` default on records missing the key. After existing field extraction (line 671), invoke the helper and conditionally inject: `if attribution is not None: finding["source_attribution"] = attribution`. Preserve the absent-key semantic exactly per the `delta_status` precedent at lines 672-676.
- [X] T011 [US1] Add parser-tier shape validation inside `_extract_source_attribution` — assert every record is a dict with exactly the key set `{taxonomy, id}` or `{taxonomy, id, relationship}`. Extra keys raise `ValueError(f"Finding {finding_id}: unexpected key(s) in source_attribution record: {extra_keys}")` per data-model V5.

**Checkpoint 3**: US1 tests (T008, T009) pass. Multi-framework citation round-trip is fully functional and testable independently.

---

## Phase 4: User Story 2 — Parser Round-Trip Preserves Backward Compatibility (Priority: P1)

**Goal**: Prove the 5 non-agentic example PDF baselines regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000` with schema 1.5 in place. Plus prove the absent-vs-present-but-empty conditional-key distinction round-trips correctly.

**Independent Test**: Run `pytest tests/scripts/test_backward_compatibility.py` (existing harness, unmodified) under `SOURCE_DATE_EPOCH=1700000000`; all 5 baselines must match byte-for-byte. Separately, assert fixture `valid_absent.md` round-trips without `source_attribution` key on returned findings, and `valid_empty_array.md` round-trips WITH `source_attribution: []` preserved.

### Tests for User Story 2

- [X] T012 [P] [US2] Author fixture `tests/scripts/fixtures/source_attribution/valid_absent.md` — threats.md-shaped document with 2-3 findings in the Section 7 table, NONE carrying any attribution data, NO Section 9 block (Q1-E) or NO companion sidecar (Q1-B). Exercises the absent-key round-trip.
- [X] T013 [P] [US2] Author fixture `tests/scripts/fixtures/source_attribution/valid_empty_array.md` — threats.md with one finding carrying `source_attribution: []` explicitly. Exercises the present-but-empty semantic per data-model V6.
- [X] T014 [US2] Add test function `test_absent_omits_key` to `tests/scripts/test_source_attribution.py` — loads `valid_absent.md`, asserts every returned finding dict has NO `source_attribution` key (checked via `"source_attribution" not in finding`).
- [X] T015 [US2] Add test function `test_empty_array_preserved` to `tests/scripts/test_source_attribution.py` — loads `valid_empty_array.md`, asserts the affected finding's `source_attribution` value is an empty list (checked via `finding["source_attribution"] == []`).

### Implementation for User Story 2

- [X] T016 [US2] Refine `_extract_source_attribution` to distinguish absent-from-input (return None) vs present-but-empty-on-input (return []) — this is the data-model V6 invariant. Confirm via T014 + T015 dual-path assertion.
- [X] T017 [US2] Run existing backward-compatibility harness: `pytest tests/scripts/test_backward_compatibility.py -v` with `SOURCE_DATE_EPOCH=1700000000`. Assert 5/5 baselines byte-identical against `examples/{web-app,microservices,ascii-web-api,mermaid-agentic-app,free-text-microservice}/security-report.pdf.baseline`. If any baseline diffs, halt and diagnose; per spec constraint C1, regression is a BLOCKER.

**Checkpoint 4**: SC-002 byte-identity gate green. US2 tests (T014, T015) pass. Backward-compat invariant proven. MVP slice (US1 + US2) ready for stakeholder demo.

---

## Phase 5: User Story 3 — Closed-Enum `relationship` with Referential Integrity (Priority: P1)

**Goal**: Prove the two-tier validation works: parser-tier catches enum violations inline; `validate_source_attribution` catches referential-integrity violations in a separate phase invoked by the orchestrator Phase 4 (per Q2-B architect preference).

**Independent Test**: Hand-author 3 invalid fixtures (bad taxonomy, bad relationship, bad id). Parser-tier fixtures raise `ValueError` with finding ID + bad value + closed-domain. Referential-integrity fixture produces structured `ValidationError` with finding ID + bad id + target YAML path.

### Tests for User Story 3

- [X] T018 [P] [US3] Author fixture `tests/scripts/fixtures/source_attribution/invalid_taxonomy.md` — one finding with `source_attribution: [{taxonomy: not-a-real-taxonomy, id: X, relationship: primary}]`. Exercises V1 (parser-tier taxonomy enum validation).
- [X] T019 [P] [US3] Author fixture `tests/scripts/fixtures/source_attribution/invalid_relationship.md` — one finding with `source_attribution: [{taxonomy: owasp, id: LLM05, relationship: fabricated_value}]`. Exercises V2 (parser-tier relationship enum validation).
- [X] T020 [P] [US3] Author fixture `tests/scripts/fixtures/source_attribution/invalid_id.md` — one finding with `source_attribution: [{taxonomy: owasp, id: NOT-A-REAL-OWASP-ID, relationship: primary}]`. Exercises V4 (validator-tier referential integrity).
- [X] T021 [US3] Add test function `test_invalid_taxonomy_rejected` to `tests/scripts/test_source_attribution.py` — loads `invalid_taxonomy.md`, asserts `parse_threats_findings` raises `ValueError` whose message contains the finding ID, the bad value `not-a-real-taxonomy`, and the closed domain `{owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe}`.
- [X] T022 [US3] Add test function `test_invalid_relationship_rejected` to `tests/scripts/test_source_attribution.py` — loads `invalid_relationship.md`, asserts `parse_threats_findings` raises `ValueError` whose message contains the finding ID, the bad value `fabricated_value`, and the closed domain `{primary, related, derived}`.
- [X] T023 [US3] Add test function `test_relationship_defaults_to_primary` to `tests/scripts/test_source_attribution.py` — uses `valid_single_record.md` (from T007); asserts parser injects `relationship: "primary"` on the record that omitted the field in input.
- [X] T024 [US3] Add test function `test_invalid_id_detected` to `tests/scripts/test_source_attribution.py` — loads `invalid_id.md`; calls `parse_threats_findings` (passes parser-tier enum checks); then calls `validate_source_attribution`; asserts returned error list contains exactly one `ValidationError` with `finding_id`, `record.id == "NOT-A-REAL-OWASP-ID"`, and `target_yaml_path == "schemas/taxonomy/owasp.yaml"`.
- [X] T025 [US3] Add test function `test_fixtures_self_consistent` to `tests/scripts/test_source_attribution.py` — loads all valid fixtures (`valid_single_record.md`, `valid_multi_record.md`, `valid_absent.md`, `valid_empty_array.md`), calls `validate_source_attribution` on the parsed findings, asserts returned error list is empty (valid fixtures' taxonomy/id/relationship values all resolve per FR-013).

### Implementation for User Story 3

- [X] T026 [US3] Add parser-tier enum validation inside `_extract_source_attribution` — on each record read, assert `record["taxonomy"] in {"owasp", "mitre-attack", "mitre-atlas", "nist-ai-rmf", "cwe"}` (V1) and `record.get("relationship", "primary") in {"primary", "related", "derived"}` (V2). Raise `ValueError` per FR-009 error-shape: include finding ID, bad value, closed-domain list. Also assert `record["id"]` is non-empty string (V3).
- [X] T027 [US3] Implement new helper `validate_source_attribution(findings: list[dict], taxonomy_dir: pathlib.Path = Path("schemas/taxonomy")) -> list[ValidationError]` in `scripts/tachi_parsers.py`. For each finding with `source_attribution`, for each record, load `taxonomy_dir / f"{record['taxonomy']}.yaml"` (cached per-invocation in local dict). Assert `record["id"]` matches a top-level `id:` key in the catalog's list of records. Return `ValidationError` entries for unresolved IDs; return empty list on full success. `ValidationError` is a new `@dataclass` with fields `finding_id: str`, `record: dict`, `target_yaml_path: str`, `reason: str`.
- [X] T028 [US3] Verify `validate_source_attribution` respects ADR-021 determinism — no HTTP fetches, no env reads, no timestamp logic. Per-invocation cache is scoped to the local dict; no module-level state.

**Checkpoint 5**: US3 tests pass. All three acceptance scenarios (AC-1 through AC-4) for US-189-3 proven. Two-tier validation is functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: ADR transition, cross-reference docs, SC audit, PR preparation.

**Wave 6.1 (Day 3 PM, 2026-04-22)**

- [X] T029 [P] Update `README.md` (top-level) — add one line under Recent Changes naming Feature 189 and linking to `docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md`. Follow the F-A1 precedent; preserve existing structure byte-identically apart from the one added line.
- [X] T030 [P] Update `docs/architecture/00_Tech_Stack/README.md` Standards section — add an entry under the finding-schema evolution timeline naming `schema_version 1.5` and linking to ADR-028. Follow the F-A1 2-link-edit precedent per spec FR-038.
- [X] T031 Transition ADR-028 `Status: Proposed` → `Status: Accepted` with `Accepted-date: 2026-04-17` (provisional; will auto-correct post-merge) and `Accepted-commit-SHA: <pending-post-merge-fill>` placeholder. Mirrors ADR-027 / F-A1 precedent exactly.
- [X] T032 Run the SC audit grep checks — output saved to `.aod/results/sc-audit.md`:
  - SC-001: schema_version 1.5 verified at `schemas/finding.yaml:13`.
  - SC-006: empty diff on pyproject.toml / requirements*.txt / package.json.
  - SC-007: empty diff on 22 detection-tier files (flat `.claude/agents/tachi/<name>.md` layout + 11 skill-refs). ADR-028 Decision 6 paths also corrected to reflect flat layout.
- [X] T033 [P] Run quickstart validation — walked 5 steps end-to-end against live pipeline. All passed. One correction: `CWE-1426` → `CWE-116` in the round-trip test example (CWE-1426 not in catalog). Outcome saved to `.aod/results/quickstart-validation.md`.
- [X] T034 Full pytest suite: run `pytest tests/scripts/ -v` from repo root. Assert all pre-existing tests pass + new T008/T009/T014/T015/T021/T022/T023/T024/T025 tests pass. Zero new failures. Attach output to PR description. Result: 284 passed, 1 skipped (pre-existing SC-003 narrowing).
- [X] T035 Submit PR — title "feat(189): F-A2 source attribution schema extension (#189)". Body references spec, plan, research, ADR-028, quickstart. Includes SC audit output summary, pytest output summary, test-coverage numbers, 22-file zero-edit confirmation. **PR URL**: https://github.com/davidmatousek/tachi/pull/190

**Post-merge**:
- [X] T036 Post-merge hook — update ADR-028 `Accepted-commit-SHA` placeholder with actual squash-merge SHA. Single-line commit: `docs(adr): ADR-028 post-merge SHA fill`. Mirrors F-A1 Wave 5.2 post-merge fill precedent.

**Checkpoint 6**: All 7 SC gates green. PR merged. Follow-on F-A3 Issue filed with F-A2 contract as dependency satisfied.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies. T001 is the critical-path Day 1 AM task. T002, T003 can run in parallel with T001.
- **Phase 2 (Foundational)**: Depends on Phase 1 T001 completion (schema lock requires Q1+Q2 resolved). BLOCKS all user-story work.
- **Phase 3 (US1)**: Depends on Phase 2 completion. Fixtures (T006, T007) can begin as soon as Q1 resolves (after T001); implementation (T010, T011) requires T004.
- **Phase 4 (US2)**: Depends on Phase 3 US1 completion — T010's `_extract_source_attribution` is the substrate for T016's absent-vs-empty refinement. T017 backward-compat run depends on T010 being in place (the parser must at minimum not regress the existing baselines).
- **Phase 5 (US3)**: Depends on Phase 3 US1 completion — T026's enum validation extends the helper introduced in T010. T027's validator is file-independent and can author in parallel with T010 after T001's Q2 resolution.
- **Phase 6 (Polish)**: Depends on Phases 1-5 completion. T031 (ADR Accepted transition) depends on all prior tasks being green.

### User Story Dependencies

- **US1** (Phase 3): Foundational — MVP delivery boundary. No dependency on other stories.
- **US2** (Phase 4): Depends on US1 (shared parser helper). Parallelizable with US3 once T010 lands.
- **US3** (Phase 5): Depends on US1 (shared parser helper) for T026; T027 validator is US1-independent and can author from T001 onward.

### Within Each User Story

- Tests (T006-T007, T012-T013, T018-T020) MUST be authored and FAIL before implementation (Constitution Principle VI test-first).
- Models → services → integration: F-A2 has no service layer; the progression is fixture → parser extension → validator extension.
- Commit after each task or logical group per Constitution Principle IX.

### Parallel Opportunities

- **Wave 1.1 (Day 1 AM)**: T002 + T003 parallel with T001 (memo authoring).
- **Wave 2.1 (Day 1 PM)**: T004 + T005 parallel (same file — serialized by git, but authoring can prepare diffs in parallel).
- **Wave 3.1 (Day 2 AM)**: T006 + T007 parallel (different fixture files).
- **Wave 4.1 (Day 2 AM)**: T012 + T013 parallel (different fixture files).
- **Wave 5.1 (Day 2 AM)**: T018 + T019 + T020 parallel (different fixture files).
- **Wave 6.1 (Day 3 PM)**: T029 + T030 parallel (different files); T033 parallel with T032.

Critical path: T001 → T004 → T010 → T017 → T031. Approx 2-3 working days with partial parallelism.

---

## Parallel Example: User Story 1 (Wave 3.1 — Day 2 AM)

```bash
# Launch test fixture authoring together:
Task: "Author valid_multi_record.md fixture at tests/scripts/fixtures/source_attribution/"
Task: "Author valid_single_record.md fixture at tests/scripts/fixtures/source_attribution/"

# Parser extension sequences after fixtures exist:
Task: "Extend parse_threats_findings with _extract_source_attribution helper"
Task: "Add parser-tier shape validation for source_attribution records"
```

---

## Implementation Strategy

### MVP First (US1 Only — End of Day 2 AM)

1. Phase 1 Setup — ADR-028 Proposed commit (T001) unblocks everything.
2. Phase 2 Foundational — Schema bump (T004-T005).
3. Phase 3 US1 — Multi-framework citation round-trip (T006-T011).
4. **STOP and VALIDATE** — Run T008 + T009. Multi-record round-trip is the MVP primitive.

### Incremental Delivery (Day 2 PM → Day 3)

1. MVP (US1) — Day 2 AM.
2. US2 (backward-compat) — Day 2 PM. **SC-002 gate** greens here.
3. US3 (enum + referential integrity) — Day 2 PM / Day 3 AM.
4. Phase 6 (Polish + PR) — Day 3 PM.

### Parallel Team Strategy

With one developer (expected): serial with partial wave parallelism (fixtures authored in parallel, implementation serial). With two developers: US2 and US3 parallelize at Wave 4.1 / 5.1 once T010 is in place.

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Every US1/US2/US3 task is independently completable and testable per spec User Story Independent Test descriptors
- Verify tests fail before implementing (red → green → refactor)
- Commit after each task or logical group per Constitution Principle IX
- Stop at Checkpoint 4 (SC-002 green) to validate backward-compat independently
- Avoid: vague tasks, same-file conflicts, cross-story dependencies that break MVP independence
- Q1 (serialization surface) and Q2 (referential-integrity phase) resolutions live in ADR-028 Proposed commit (T001). All T006+ tasks read the Q1/Q2 resolution from the ADR; they do NOT prejudge.
