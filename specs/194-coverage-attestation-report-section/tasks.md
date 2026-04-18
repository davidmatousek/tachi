---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-18
    status: APPROVED
    notes: "Faithful, scope-disciplined 46-task breakdown of PRD v1.1 + spec.md. All 3 P1 user stories have dedicated phases with MVP (US3-only) as viable partial merge. All 19 FRs have task-level ownership; all 12 SCs have verifying tasks in an accurate traceability matrix. PRD-resolved questions (Q1-A, Q2-A, Q4, Q6-D) preserved verbatim. No drift into out-of-scope territory (crosswalk JOIN, 4th classification, SARIF, schema changes). BLOCKER invariants (SC-002/SC-009/FR-015/FR-017) all have dedicated audit tasks."
  architect_signoff:
    agent: architect
    date: 2026-04-18
    status: APPROVED
    notes: "Architecturally sound. All 6 plan-phase findings carried forward correctly: M-1 (T014 post-findings-detail ~:393 insertion point), M-2 (T039 explicit F-A3 coordination), M-3 (T005 synthetic fixture with NO schemas/taxonomy modification), L-1 (T012 single atomic 3-guard block), L-2 (T030 matrix split + T035 per-finding merge with prefix), L-3 (T002 ADR-029 cites Features 128 + 141). TDD ordering strict across all 3 user stories. Dependency graph sound; T006 stub template blocks T013/T014; aggregator before Typst rendering. 3 non-blocking observations (commit grouping T012-T014 discretion, T030/T017 minor overlap, T038 fixture generator addition) — none block approval."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-18
    status: APPROVED_WITH_CONCERNS
    notes: "Timeline feasible: critical path ~18-22h sequential within 4-day (32h) envelope. 46 task IDs (44 in-window, 1 verification, 1 post-merge). Day 2 load peak ~22 tasks absorbable via 14 pytest-safe [P]-parallel test-authoring. Critical path validated: T002→T024-T027→T012-T014→T015→T043→T046. F-A3 coordination (T039) gives ~48h escalation runway. 0 BLOCKING / 2 MEDIUM / 2 LOW. M1 (same-file aggregator discipline) acceptable. M2 (senior-backend-engineer Day 3 ~90-110% load) absorbed inline via T038 slip-to-Day-4 pre-approval. L1 (ux-ui-designer Q5 memo fallback covered by T003). L2 (T012 line-range 89-107 defensive re-validate recommended — noted for implementation). Agent assignments valid against .claude/agents/_README.md. Calendar verified (2026-04-20 Mon → 2026-04-23 Thu)."
---

# Tasks: Coverage Attestation Report Section

**Input**: Design documents from `/specs/194-coverage-attestation-report-section/`
**Prerequisites**: plan.md ✓, spec.md ✓ (PM APPROVED), research.md ✓, data-model.md ✓, contracts/typst-data-contract.md ✓, quickstart.md ✓
**Feature**: 194 — F-B Coverage Attestation Report Section (BLP-01 Coverage Attestation Reporting tier)
**Timeline**: 4 days realistic (2026-04-20 Mon → 2026-04-23 Thu); 3 days aspirational on Q1-A + Q2-A + Q6-D + Q5 Day 2 AM happy path

**Tests**: REQUIRED for this feature (PRD FR-6, SC-011, Constitution VI Testing Excellence). TDD order: tests before implementation.

**Organization**: Tasks grouped by user story (US1/US2/US3) for independent testability. Day labels map to PRD Timeline & Milestones section.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: US1 (Per-Finding Table) / US2 (Per-Framework Matrix) / US3 (Backward Compat Gate)
- All task file paths are absolute from repo root

## Path Conventions
- Scripts: `scripts/extract-report-data.py`, `scripts/tachi_parsers.py` (existing)
- Typst: `templates/tachi/security-report/*.typ`
- Schemas: `schemas/taxonomy/*.yaml` (read-only), `schemas/finding.yaml` (UNCHANGED — FR-015)
- Tests: `tests/scripts/`, `tests/scripts/fixtures/coverage_attestation/`
- ADR: `docs/architecture/02_ADRs/ADR-029-coverage-attestation-report-section.md`
- Examples: `examples/` (5 non-agentic baselines, SC-002 gate)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Feature-branch scaffolding. Minimal since the tachi repo already carries all runtime tooling (Python 3.11, Typst, pytest, pyyaml).

- [X] T001 Feature branch `194-coverage-attestation-report-section` verified on `origin` and tracking upstream; GitHub Issue #194 moved to `stage:build` (verification checkpoint, no work)

---

## Phase 2: Foundational (Blocking Prerequisites — Day 1)

**Purpose**: Wave 1.0 architect critical path + Wave 1.1 parallel Q-independent scaffolding. No user-story work begins until this phase completes.

**CRITICAL**: All user story phases depend on this phase.

### Wave 1.0 — Day 1 AM (architect critical path, sequential)

- [X] T002 Author ADR-029 Proposed commit at `docs/architecture/02_ADRs/ADR-029-coverage-attestation-report-section.md` with Status: Proposed. Body must enumerate all 7 decision surfaces per FR-013: (a) Typst template + aggregator + `has-source-attribution` boolean pattern cross-referencing Feature 141 precedent, (b) Q1-A 3-value classification rule (Partial = `related`/`derived`-only, zero `primary`), (c) Q2-A denominator authority (`len(yaml.safe_load(schemas/taxonomy/{framework}.yaml))`), (d) zero-crosswalk-JOIN scope line, (e) Q6-D Out-of-Scope deferral, (f) 22-file zero-edit invariant preservation with ADR-023 + ADR-028 cross-references, (g) R9/MED-3 Partial disclosure rule. Cross-reference Features 128 and 141 precedents (architect L-3). Commit directly to feature branch.

- [X] T003 [P] Q5 ux-ui-designer memo handoff — architect writes a short Q5 specification note (color + icon recommendation: Covered = green check, Partial = yellow half-circle, Gap = red X with red fill; WCAG AA color-blind accessible) at `specs/194-coverage-attestation-report-section/q5-visual-treatment-architect-fallback.md` as pre-approved fallback if ux-ui-designer memo slips.

### Wave 1.1 — Day 1 (parallel scaffolding, Q-independent)

- [X] T004 [P] Author 3 test fixtures under `tests/scripts/fixtures/coverage_attestation/` — `empty_attribution.yaml` (0 findings with `source_attribution`), `one_primary_attribution.yaml` (1 finding with 1 `primary` citation), `multi_mixed_attribution.yaml` (≥3 findings with mixed `primary`/`related`/`derived` across ≥2 frameworks). Fixtures adhere to `schemas/finding.yaml` v1.5 shape per F-A2.

- [X] T005 [P] Author zero-denominator synthetic fixture `tests/scripts/fixtures/coverage_attestation/zero_denominator_framework.yaml` (synthetic empty-list framework YAML) — **MUST NOT modify any file under `schemas/taxonomy/`** (architect M-3). Fixture feeds the zero-item-YAML edge test.

- [X] T006 [P] Create Typst template skeleton `templates/tachi/security-report/coverage-attestation.typ` — header, footer, exported function signature `coverage-attestation-page(per-finding-rows, per-framework-aggregates)`, empty body that compiles without error. Final rendering implementation comes in Phase 4 + Phase 5.

- [X] T007 [P] Scaffold `has-source-attribution` boolean emission placeholder in `scripts/extract-report-data.py` — stub function `compute_has_source_attribution(findings)` returning `False` (final implementation in T011). Placeholder enables main.typ integration tests in Phase 3 to compile against the data contract.

**Checkpoint**: Foundation ready. User story phases can proceed in parallel (subject to aggregator dependency ordering US3 → US2 → US1 per Phase 3/4/5 structure below).

---

## Phase 3: User Story 3 — Conditional Inclusion Preserves Backward Compatibility (Priority: P1 MVP)

**Goal**: Ship the `has-source-attribution` gate end-to-end. When no finding carries `source_attribution`, the PDF is byte-identical to the pre-F-B baseline. This is the BLOCKER-level story: SC-002 + SC-009 merge gates.

**Independent Test**: Run the pipeline on any of the 5 non-agentic baselines (`web-app`, `microservices`, `ascii-web-api`, `free-text-microservice`, `maestro-reference`) under `SOURCE_DATE_EPOCH=1700000000`; regenerated PDF is byte-identical to `.pdf.baseline`. Gate is live; the template is a no-op stub.

### Tests for User Story 3 (TDD — write first, assert failure before implementation)

- [X] T008 [P] [US3] Author `tests/scripts/test_coverage_attestation.py::test_has_source_attribution_false_on_empty_fixture` — asserts `compute_has_source_attribution` returns `False` on `empty_attribution.yaml`.

- [X] T009 [P] [US3] Author `tests/scripts/test_coverage_attestation.py::test_has_source_attribution_true_on_one_primary_fixture` — asserts returns `True` on `one_primary_attribution.yaml`.

- [X] T010 [P] [US3] Author `tests/scripts/test_coverage_attestation.py::test_default_value_guard_stale_report_data` — loads a synthetic stale `report-data.typ` snippet missing `has-source-attribution`, `per-finding-rows`, and `per-framework-aggregates` declarations; verifies `main.typ` compiles without "variable not found" error (subprocess call to `typst compile`).

### Implementation for User Story 3 (Day 2-3)

- [X] T011 [US3] Implement `compute_has_source_attribution(findings) -> bool` in `scripts/extract-report-data.py`. Returns `True` iff any finding has `source_attribution` that is not `None` and has `len() > 0`. Emits `#let has-source-attribution = true|false` to the Typst data contract via `_typst_bool()` (existing helper from Feature 141 at line 1426 precedent).

- [X] T012 [US3] Add 3 default-value guards to `templates/tachi/security-report/main.typ` §2b defaults block (around lines 89-107) as a **single atomic edit block** (architect L-1). **Implementation deviation from architect's prescribed `if X != none { X } else { default }` idiom**: discovered during T016 that the prescribed pattern only handles present-but-`none` vars (because `#import "report-data.typ": *` doesn't bind absent names). The data-contract.md §Backward Compatibility explicitly requires handling the absent-from-data-file case. Switched to `dictionary(report-data-module).at("name", default: ...)` after binding `#import "report-data.typ" as report-data-module`. T010 stale-data test green; T015 baselines byte-identical. ADR-029 may need a "guard-pattern selection" addendum in T043.

- [X] T013 [US3] Add `#import "coverage-attestation.typ": coverage-attestation-page` to `templates/tachi/security-report/main.typ` in the existing imports block (around lines 43-47). Unconditional import; byte-identity is preserved because the function is not invoked when the gate predicate is false.

- [X] T014 [US3] Add conditional inclusion block to `templates/tachi/security-report/main.typ` AFTER the always-rendered findings-detail-page (~line 393) and BEFORE the compensating-controls block (line 398) — architect M-1 refined insertion point, NOT between MAESTRO-findings (:348) and compensating-controls (:398). Block:
    ```typst
    #if has-source-attribution and per-finding-rows.len() > 0 {
      coverage-attestation-page(per-finding-rows: per-finding-rows, per-framework-aggregates: per-framework-aggregates)
    }
    ```
    Mirrors the Feature 141 pattern at `main.typ:246`.

- [X] T015 [US3] SC-002 byte-identity regression — run `SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py` and verify all 5 non-agentic baselines regenerate byte-identical to committed `.pdf.baseline` files. **BLOCKER** gate: if any baseline regresses, fix before proceeding. **Outcome (Wave 4.1)**: 13 passed, 1 skipped — all 5 non-agentic baselines (web-app, microservices, ascii-web-api, free-text-microservice, maestro-reference) + mermaid-agentic-app byte-identical to committed `.pdf.baseline` under `SOURCE_DATE_EPOCH=1700000000`. The 1 skip is the pre-existing Feature 142 T033-documented known-limitation on mermaid-agentic-app pattern classification (unrelated to F-B).

- [X] T016 [US3] Day 3 `#import` byte-identity smoke (architect MED-5) — verified that adding the `#import` in T013 + T012 guards (without T014 conditional block) produces byte-identical PDFs on the 6 baselines (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice, maestro-reference). Run via `SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py -k byte_identical` — 6/6 green.

**Checkpoint**: US3 complete. The gate is live. Coverage attestation section is omitted on all 5 baselines. PDFs byte-identical to pre-F-B state.

---

## Phase 4: User Story 2 — Aggregate Per-Framework Coverage Matrix (Priority: P1)

**Goal**: Render 5 per-framework matrix pages (OWASP, MITRE ATT&CK, MITRE ATLAS, NIST AI RMF, CWE) when `has-source-attribution: true`. Each page classifies every framework item as Covered / Partial / Gap, displays coverage percentage, and renders the Partial count alongside (R9 / MED-3 disclosure).

**Independent Test**: Run the pipeline on the `multi_mixed_attribution.yaml` fixture; generated PDF contains 5 per-framework pages with correct Covered/Partial/Gap classifications matching hand-computed expected values.

### Tests for User Story 2 (TDD — write first, assert failure before implementation)

- [X] T017 [P] [US2] Author `tests/scripts/test_coverage_attestation.py::test_per_framework_aggregates_emits_exactly_5_records` — asserts exactly-5-frameworks invariant when `has-source-attribution: true`.

- [X] T018 [P] [US2] Author `tests/scripts/test_coverage_attestation.py::test_partition_invariant` — asserts `covered_count + partial_count + gap_count == yaml_record_count` for every framework aggregate across all 3 fixtures.

- [X] T019 [P] [US2] Author `tests/scripts/test_coverage_attestation.py::test_classification_rules_q1_a` — asserts Covered requires ≥1 `primary`; Partial requires zero `primary` AND ≥1 `related`/`derived`; Gap requires zero attributions. Uses hand-constructed fixture records.

- [X] T020 [P] [US2] Author `tests/scripts/test_coverage_attestation.py::test_coverage_percentage_arithmetic` — hand-computes expected percentages for `multi_mixed_attribution.yaml` and asserts aggregator output matches.

- [X] T021 [P] [US2] Author `tests/scripts/test_coverage_attestation.py::test_coverage_percentage_na_on_zero_denominator` — uses `zero_denominator_framework.yaml` fixture; asserts `coverage_percentage == "N/A"`.

- [X] T022 [P] [US2] Author `tests/scripts/test_coverage_attestation.py::test_coverage_percentage_0pct_on_zero_numerator` — asserts empty fixture with non-empty YAML produces `"0.00%"`.

- [X] T023 [P] [US2] Author `tests/scripts/test_coverage_attestation.py::test_aggregator_fails_loud_on_malformed_yaml` — mocks a malformed YAML load and asserts `yaml.YAMLError` propagates up with clear framework-identifying message (per ADR-022 fail-loud).

### Implementation for User Story 2 (Day 2 aggregator + Day 3 Typst)

- [X] T024 [US2] Implement `load_framework_yaml_record_counts() -> dict[str, int]` in `scripts/extract-report-data.py` — loads 5 external-framework YAMLs (`owasp`, `mitre-attack`, `mitre-atlas`, `nist-ai-rmf`, `cwe`) from `schemas/taxonomy/*.yaml` via `yaml.safe_load`. Returns a dict `{framework_name: yaml_record_count}`. Cached per-invocation (local function dict, no module-level mutable state — per F-A2 convention). Malformed YAML raises `yaml.YAMLError` with framework-identifying wrapper.

- [X] T025 [US2] Implement `classify_framework_items(findings, framework_name, framework_yaml_records) -> list[dict]` in `scripts/extract-report-data.py` — for each top-level record in the framework YAML, applies Q1-A classification: Covered if ≥1 finding has `source_attribution[i].taxonomy == framework_name` and `.id == record.id` and `.relationship == "primary"`; Partial if zero primary AND ≥1 related/derived; Gap otherwise. Returns list of `{id, classification}` preserving YAML iteration order.

- [X] T026 [US2] Implement `build_per_framework_aggregate(framework_name, findings, yaml_record_count, items) -> dict` in `scripts/extract-report-data.py` — computes `covered_count` / `partial_count` / `gap_count` from classified items; computes `coverage_percentage` as `"X.XX%"` or `"N/A"` when `yaml_record_count == 0` or `"0.00%"` when `covered_count == 0`. Returns the Per-Framework Aggregate Record shape per data-model.md. Partition invariant asserted (T018 covers).

- [X] T027 [US2] Wire aggregator invocation in `scripts/extract-report-data.py`'s main extraction pathway — after findings are parsed, compute `has_source_attribution`, then if True compute per-framework aggregates for all 5 frameworks and emit them alongside `has-source-attribution` and (empty for now) `per-finding-rows` to the Typst data contract. Emits `#let per-framework-aggregates = (...)`.

- [X] T028 [US2] Render per-framework matrix page body in `templates/tachi/security-report/coverage-attestation.typ` — iterate over `per-framework-aggregates`; render one page per framework (5 pages, always rendered when gate is true per Q4 resolution); title, 3-group item visualizations (Covered / Partial / Gap), summary line `"Covered: K/N = X.XX% · Partial: P · Gap: G"` with equal visual weight (FR-008).

- [X] T029 [US2] Render Gap item highlighting in `coverage-attestation.typ` — color + icon combination (WCAG AA color-blind accessible per FR-010). Default to architect fallback (Covered = green check, Partial = yellow half-circle, Gap = red X with red fill) if Q5 ux-ui-designer memo has not landed.

- [X] T030 [US2] Verify MITRE per-framework split is preserved in matrix pages — `mitre-attack` and `mitre-atlas` render as 2 SEPARATE per-framework pages, NOT merged (architect L-2). The MITRE merge is per-finding-column only (see Phase 5 US1).

**Checkpoint**: US2 complete. Running on `multi_mixed_attribution.yaml` produces a PDF with 5 per-framework matrix pages showing correct Covered/Partial/Gap classifications. Per-finding table still empty (pending US1).

---

## Phase 5: User Story 1 — Per-Finding Attribution Table (Priority: P1)

**Goal**: Render the per-finding attribution table — one row per finding, 7 columns, `primary` citations bold, `related`/`derived` plain, MITRE column merges ATT&CK and ATLAS with per-ref prefix.

**Independent Test**: Run the pipeline on the `multi_mixed_attribution.yaml` fixture; per-finding table has one row per finding, 7 columns with correct citation formatting and bold/plain weight differentiation.

### Tests for User Story 1 (TDD — write first, assert failure before implementation)

- [X] T031 [P] [US1] Author `tests/scripts/test_coverage_attestation.py::test_per_finding_row_count_matches_finding_count` — every finding in input produces exactly one row; findings with empty `source_attribution` still produce a row with empty ref arrays.

- [X] T032 [P] [US1] Author `tests/scripts/test_coverage_attestation.py::test_per_finding_row_mitre_merge_with_prefix` — row with `mitre-attack: T1070.001 primary` and `mitre-atlas: AML.T0051 primary` emits `mitre_refs = [{id: "ATT&CK:T1070.001", relationship: "primary"}, {id: "ATLAS:AML.T0051", relationship: "primary"}]`.

- [X] T033 [P] [US1] Author `tests/scripts/test_coverage_attestation.py::test_per_finding_row_grouping_by_taxonomy` — row with `owasp: LLM05 primary`, `cwe: CWE-1426 related` emits `owasp_refs = [{id: "LLM05", relationship: "primary"}]`, `cwe_refs = [{id: "CWE-1426", relationship: "related"}]`, `mitre_refs = []`, `nist_refs = []`.

- [X] T034 [P] [US1] Author `tests/scripts/test_coverage_attestation.py::test_per_finding_row_preserves_input_order` — asserts emission order matches input finding-list order (no re-sort).

### Implementation for User Story 1 (Day 2-3)

- [X] T035 [US1] Implement `build_per_finding_rows(findings) -> list[dict]` in `scripts/extract-report-data.py` — for each finding, emit `{id, title, severity, owasp_refs, mitre_refs, nist_refs, cwe_refs}` per data-model.md. Groups `source_attribution` records by taxonomy; merges `mitre-attack` and `mitre-atlas` into the `mitre_refs` column with per-ref prefix `"ATT&CK:"` / `"ATLAS:"` respectively (FR-005, architect L-2 per-finding-only). Findings with empty or absent `source_attribution` produce a row with 4 empty ref arrays.

- [X] T036 [US1] Wire per-finding row emission into `scripts/extract-report-data.py`'s Typst data-contract output — emits `#let per-finding-rows = (...)` alongside the existing `has-source-attribution` and `per-framework-aggregates` declarations.

- [X] T037 [US1] Render per-finding attribution table in `templates/tachi/security-report/coverage-attestation.typ` — section header + single paginated table (Typst native row-break) with 7 columns: `Finding ID | Title | Severity | OWASP refs | MITRE refs | NIST refs | CWE refs`. Each row iterates the 4 `*_refs` arrays; applies bold styling when `relationship == "primary"`, plain otherwise. Empty ref arrays render as blank cells (row still visible per FR-006).

- [X] T038 [US1] Day 3 pagination smoke fixture + smoke test — author `tests/scripts/generate_pagination_fixture.py` script generating a synthetic 100-finding × 5-framework × 5-attribution fixture, then compile `coverage-attestation.typ` against it and visually inspect pagination quality. If portrait is unacceptable, activate landscape-orientation fallback or per-severity split per FR-012. Document outcome in PR. **Slip-to-Day-4 pre-approved** (team-lead M2): if Day 3 senior-backend-engineer load exceeds capacity, T038 may slip to Day 4 AM without impacting SC-002 regression (T015) or ADR Accepted (T043). Pagination smoke is independent of the SC-002 gate. **Outcome**: Portrait US Letter pagination validated — at 100-finding × 5-framework scale the per-finding table spans ~5 pages with `table.header(repeat: true)` keeping column headers visible on every continuation page; total section adds 10 pages over baseline (5 framework + 5 per-finding table). No landscape fallback needed for MVP.

**Checkpoint**: US1 complete. Full feature end-to-end: per-finding table + 5 per-framework matrix pages render correctly on populated fixtures.

---

## Phase 6: Polish & Cross-Cutting Concerns (Day 3-4)

**Purpose**: ADR transition, documentation cross-linking, final validation, PR preparation.

- [X] T039 Team-lead Day 2 EOD F-A3 merge-order coordination check (per architect M-2 / team-lead M-2). Query GitHub Issues for any F-A3 / populator / "threat-agent source_attribution" Issue filed during Days 1-2. If filed, escalate to serialization decision: hold F-B PR for F-A3 merge, OR advance F-B and accept F-A3 re-baseline cost (~0.5-1d). Document decision in PR description. **Outcome 2026-04-18**: No F-A3 Issue filed; F-B advances independently. Decision recorded at `specs/194-coverage-attestation-report-section/fa3-coordination-decision.md` for T046 PR-prep consumption.

- [X] T040 Zero-edit invariant grep audit per SC-009 — run:
    ```bash
    git diff --name-only main...HEAD | \
      grep -E '^\.claude/(agents/tachi/(stride|ai)/.*\.md|skills/tachi-.*/references/detection-patterns\.md)$'
    ```
    Expected output: empty (no matches). Any match is a BLOCKER regression. Documented in PR.

- [X] T041 Zero-dependency diff audit per SC-008 — run:
    ```bash
    git diff main...HEAD -- pyproject.toml requirements.txt requirements-dev.txt package.json
    ```
    Expected output: empty diff (no changes to runtime deps; dev-only `pytest`+`pytest-cov` already declared per Feature 128). Any non-empty diff is a BLOCKER regression.

- [X] T042 Run `quickstart.md` validation walkthrough (all 9 steps) — verifies end-to-end feature correctness: aggregator unit tests (Step 1), SC-002 byte-identity (Step 2), Typst compile smoke (Step 3), pagination smoke (Step 4), default-value guard (Step 5), zero-edit audit (Step 6), zero-dep audit (Step 7), ADR governance (Step 8), end-to-end sanity on a baseline (Step 9). All steps green. **Outcome (Wave 4.1)**: 9/9 steps GREEN. Step 1: 16/16 aggregator tests pass. Step 2: shared with T015 (13 pass, 1 pre-existing skip). Step 3: Typst compile on web-app baseline exits 0, produces 1190293-byte PDF. Step 4: 5/5 pagination tests pass. Step 5: stale-data typst compile exits 0 (default-value guard intact — no "variable not found"). Step 6: zero-edit grep audit PASS (0 of 22 files modified). Step 7: dependency diff empty (0 lines). Step 8: ADR-029 Proposed status verified at `docs/architecture/02_ADRs/ADR-029-coverage-attestation-report-section.md`. Step 9: regenerated web-app PDF byte-identical to `.pdf.baseline`. T040 covers Step 6 detail; T041 covers Step 7 detail.

- [X] T043 Transition ADR-029 Proposed → Accepted on Day 4 at PR pre-merge — architect updates `docs/architecture/02_ADRs/ADR-029-coverage-attestation-report-section.md` Status: line to `Status: Accepted` with provisional merge-date `2026-04-23` and placeholder `<pending-post-merge-fill>` preserved on `Accepted-commit-SHA` (T044 post-merge fills actual SHA). Revision History entry added dated 2026-04-23 recording the transition plus a T012 guard-pattern selection note (Typst `at(..., default: ...)` idiom preferred over `!= none` for absent-name handling). No Decision text amended. Commit on feature branch.

- [ ] T044 Post-merge SHA fill on ADR-029 — after PR squash-merges to main, amend the ADR's `merge-sha:` placeholder with the actual squash commit SHA; commit directly to main (per Feature 180/189 post-merge SHA fill precedent). Tracked as a separate commit, not amended into the PR.

- [X] T045 [P] Update `docs/architecture/01_system_design/README.md` with a new `### Feature 194: coverage-attestation-report-section` subsection referencing plan.md's System Design block (Components, Data Flow, Tech Stack). Mirrors Feature 143 / 144 architecture documentation precedent.

- [X] T046 PR preparation — open PR against `main` with description citing: (a) spec.md, plan.md, tasks.md paths, (b) triple sign-off status, (c) ADR-029 Accepted with pending SHA, (d) SC-002 regression results, (e) SC-009 zero-edit audit results, (f) SC-008 zero-dep audit results, (g) T039 F-A3 coordination outcome. **Outcome (Wave 4.2)**: PR #195 opened 2026-04-18 — `https://github.com/davidmatousek/tachi/pull/195`. Triple sign-off confirmed (PM APPROVED + Architect APPROVED + Team-Lead APPROVED_WITH_CONCERNS, all 2026-04-18). ADR-029 Accepted with placeholder `merge-sha: <pending-post-merge-fill>` for T044. SC-002 (13 pass / 1 pre-existing skip), SC-008 (empty dep diff), SC-009 (22-file zero-edit audit) all green. Test suite: 305 pass, 1 skip. Quickstart 9/9 green. 3 user stories delivered (US3 gate MVP, US2 per-framework matrix, US1 per-finding table).

**Checkpoint**: All 12 SCs green. PR ready for external review and squash-merge.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies (already complete — feature branch exists).
- **Phase 2 Foundational (Wave 1.0 + 1.1)**: No dependencies beyond Setup. BLOCKS all user story phases.
- **Phase 3 US3 (Gate MVP)**: Depends on Phase 2 complete. Independent of US1 and US2 content.
- **Phase 4 US2 (Per-Framework Matrix)**: Depends on Phase 2 complete. Can run in parallel with Phase 3 on different files (aggregator code vs. main.typ integration). MUST land before the full rendered output is visible.
- **Phase 5 US1 (Per-Finding Table)**: Depends on Phase 2 complete. Can run in parallel with Phase 3 + Phase 4. Same co-located aggregator code as US2; requires coordination if Phase 4 and Phase 5 concurrently edit `scripts/extract-report-data.py`.
- **Phase 6 Polish**: Depends on Phase 3 + 4 + 5 all complete.

### User Story Dependencies

- **US3 (Backward Compat Gate)**: MVP story. Independent of US1 and US2 content. SC-002 can be verified with stub template.
- **US2 (Per-Framework Matrix)**: Independent of US1 in principle, but shares the aggregator file with US1. Coordination required to avoid same-file conflicts. Aggregator structure allows for independent functions (`build_per_framework_aggregate` vs. `build_per_finding_rows`).
- **US1 (Per-Finding Table)**: Independent of US2 in principle. Same aggregator-file coordination constraint.

### Within Each User Story (TDD Ordering)

- Tests (T008-T010 US3, T017-T023 US2, T031-T034 US1) MUST be written and FAIL before implementation tasks.
- Aggregator functions before Typst rendering (data before presentation).
- Unit tests green before integration tests.

### Parallel Opportunities

- **Wave 1.1 (Day 1)**: T003, T004, T005, T006, T007 all parallel (different files, Q-independent).
- **Phase 3 US3 tests (Day 2 AM)**: T008, T009, T010 parallel.
- **Phase 4 US2 tests (Day 2 AM)**: T017, T018, T019, T020, T021, T022, T023 parallel (same file but different test functions; pytest handles concurrency).
- **Phase 5 US1 tests (Day 2 AM)**: T031, T032, T033, T034 parallel (same file, different tests).
- **Phase 3 + Phase 4 + Phase 5 main.typ vs. aggregator**: T012/T013/T014 (main.typ edits, US3) can run in parallel with T024-T027 (aggregator US2) and T035-T036 (aggregator US1) — different files.
- **Phase 6 audit tasks**: T040, T041, T045 parallel (different files / different git commands).

---

## Parallel Example: Wave 1.1 Day 1 Morning

```bash
# Launch all 5 Wave 1.1 scaffolding tasks together (senior-backend-engineer and tester):
Task: "T004 [P] Author 3 test fixtures in tests/scripts/fixtures/coverage_attestation/"
Task: "T005 [P] Author zero-denominator synthetic fixture"
Task: "T006 [P] Create Typst template skeleton in templates/tachi/security-report/coverage-attestation.typ"
Task: "T007 [P] Scaffold has-source-attribution boolean placeholder in scripts/extract-report-data.py"
# T003 runs in parallel on architect's side.
```

## Parallel Example: Day 2 Morning TDD

```bash
# Launch all Phase 3/4/5 test authoring in parallel (tester + senior-backend-engineer):
Task: "T008 [P] [US3] test_has_source_attribution_false_on_empty_fixture"
Task: "T009 [P] [US3] test_has_source_attribution_true_on_one_primary_fixture"
Task: "T010 [P] [US3] test_default_value_guard_stale_report_data"
Task: "T017 [P] [US2] test_per_framework_aggregates_emits_exactly_5_records"
Task: "T018 [P] [US2] test_partition_invariant"
Task: "T019 [P] [US2] test_classification_rules_q1_a"
Task: "T031 [P] [US1] test_per_finding_row_count_matches_finding_count"
Task: "T032 [P] [US1] test_per_finding_row_mitre_merge_with_prefix"
```

---

## Implementation Strategy

### MVP First (US3 Only)

1. Complete Phase 1 + Phase 2 (Day 1).
2. Complete Phase 3 US3 end-to-end with stub template (Day 2-3).
3. Verify SC-002 byte-identity passes — MVP shipped. Feature is live as a no-op gate.

### Incremental Delivery

1. Phase 2 Foundational complete → baseline infrastructure ready.
2. Phase 3 US3 complete + SC-002 green → gate MVP, backward-compat guaranteed.
3. Phase 4 US2 complete → per-framework matrix pages render.
4. Phase 5 US1 complete → per-finding table renders; full feature end-to-end.
5. Phase 6 Polish complete → PR merges.

### Parallel Team Strategy (if staffed)

Day 2:
- Developer A: US3 Phase 3 (gate + main.typ integration)
- Developer B: US2 Phase 4 aggregator + tests
- Developer C: US1 Phase 5 aggregator + tests
(Same-file coordination via lint-free modular function structure.)

Day 3:
- Developer A: SC-002 regression (US3)
- Developer B: US2 Typst matrix rendering
- Developer C: US1 Typst per-finding rendering

Day 4: Polish phase collaborative (ADR, audits, PR prep).

---

## Traceability Matrix

| Task | Spec FR | Spec SC | PRD Day |
|------|---------|---------|---------|
| T002 ADR-029 Proposed | FR-013 | SC-007 | Day 1 |
| T004/T005 Fixtures | FR-006 | SC-011 | Day 1 |
| T006 Typst skeleton | FR-001 | SC-001 | Day 1 |
| T007 Boolean scaffold | FR-002 | SC-003 | Day 1 |
| T011 Boolean emission | FR-002 | SC-003 | Day 2 |
| T012 Default-value guards | FR-004 | SC-004a | Day 3 |
| T013 Import | — | — | Day 3 |
| T014 Conditional block | FR-003 | SC-004b | Day 3 |
| T015 SC-002 regression | FR-003 | SC-002 | Day 4 |
| T016 #import byte-identity smoke | — | SC-002 | Day 3 |
| T024-T026 Aggregator per-framework | FR-007, FR-008, FR-009, FR-011 | SC-005 | Day 2 |
| T028-T029 Matrix Typst render | FR-001, FR-008, FR-010 | SC-006 | Day 3 |
| T035-T036 Per-finding aggregator | FR-005, FR-006 | — | Day 2-3 |
| T037 Per-finding table Typst | FR-005, FR-006 | SC-001 | Day 3 |
| T038 Pagination smoke | FR-012 | SC-010, SC-012 | Day 3 |
| T039 F-A3 coordination | — | — | Day 2 EOD |
| T040 Zero-edit audit | FR-014 | SC-009 | Day 4 |
| T041 Zero-dep audit | FR-016 | SC-008 | Day 4 |
| T042 Quickstart validation | all | all | Day 4 |
| T043 ADR-029 Accepted | FR-013 | SC-007 | Day 4 |
| T044 Post-merge SHA fill | FR-013 | SC-007 | Post-merge |
| T045 System design doc | — | — | Day 4 |

---

## Notes

- [P] tasks touch different files OR same-file-different-test-functions (pytest-safe concurrency).
- [Story] label enables story-level partial delivery (US3 alone is a valid merge).
- Same-file coordination within Phase 4 + Phase 5 (aggregator in `scripts/extract-report-data.py`) requires developer discipline: use distinct function boundaries and small PR scope per task.
- Commit after each task or logical group.
- Stop at Phase 3 US3 + T015 green to have a valid MVP merge if the team hits a blocker in Phase 4 or 5.
- Zero-tolerance policy: SC-002 + SC-009 + FR-015 + FR-017 are BLOCKER-level gates — any violation halts the PR.
