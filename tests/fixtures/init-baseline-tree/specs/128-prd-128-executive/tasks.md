---
plan_reference: specs/128-prd-128-executive/plan.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-09
    status: APPROVED
    notes: "All US-1 to US-4 covered. P1 stories ordered before P2. MVP scope clear (US-1 + US-2). Backward compat hard gate clear in T024 + T034. T033 example regeneration captured. 0 concerns. Full review at .aod/results/product-manager-tasks.md."
  architect_signoff:
    agent: architect
    date: 2026-04-09
    status: APPROVED
    notes: "F-091 + F-112 patterns followed. T020 reuses infographic-page() (no new Typst function). Schema-first ordering correct (T004 before any user story). Architect L-1 (component normalization) addressed in T005/T006/T009; L-2 (baseline storage) addressed in T002/T024. 2 informational non-blocking observations. Full review at .aod/results/architect-tasks.md."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-09
    status: APPROVED_WITH_CONCERNS
    notes: "Initial review returned CHANGES_REQUESTED with 2 blockers (B-1 phantom pytest infra, B-2 dependency inversion) and 8 non-blocking concerns. Re-review after rewrite: all 10 prior concerns cleanly resolved. 0 blocking. 3 minor new (A-1 exec_module mention - fixed inline; A-2 T006 duration tradeoff - accepted; A-3 plan techlead_signoff coordination - non-blocking). 2 deferred deliverables (M-1 agent-assignments.md to be generated as Step 6; M-2 plan techlead_signoff null - this signoff is on tasks.md not plan.md). 51 tasks across 8 phases, ~745 lines, ~5-6 sessions. Full review at .aod/results/team-lead-tasks-rev2.md (rev2); rev1 at .aod/results/team-lead-tasks.md."
---

# Tasks: Executive Threat Architecture Infographic

**Input**: Design documents from `/specs/128-prd-128-executive/`
**Prerequisites**: plan.md (PM + Architect approved), spec.md (PM approved), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are MANDATORY for tachi per Constitution Principle VI (Testing Excellence). Phase 0 bootstraps the missing pytest harness; subsequent phases include test tasks targeting ≥80% coverage of new code.

**Scope correction**: This document was revised on 2026-04-09 after team-lead review surfaced two blocking issues: (B-1) tachi has no pytest infrastructure — added Phase 0 bootstrap; (B-2) baseline PDF generation needs explicit git-worktree mechanics — split T003 into a–e. Eight non-blocking concerns also resolved: agent assignments split into a separate `agent-assignments.md` file (per /aod.tasks Step 6); timeline revised from 1–2 sessions to 5–6 sessions; over-granular test tasks consolidated; code-reviewer + architect checkpoints added; T005 fixture list clarified; T046 deleted; T053 downgraded to non-blocking with 5-business-day SLA; T051/T052 overlap resolved (T052 merged into T051).

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story?] Description`
- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4) — only on user-story phase tasks
- File paths are absolute or repo-root-relative

---

## Phase 0: Test Infrastructure Bootstrap

**Purpose**: Create the pytest harness that tachi has never had. Constitution Principle VI requires test coverage; tachi's existing convention does not provide a runnable harness. This phase establishes one for F-128 and every future feature.

**Deliverables**: A working `pytest tests/scripts/` invocation that imports hyphenated-name Python scripts via importlib and runs at least one smoke test.

- [X] T0a Create directory structure: `tests/`, `tests/__init__.py`, `tests/scripts/`, `tests/scripts/__init__.py`, `tests/scripts/fixtures/`. Empty `__init__.py` files mark them as packages.
- [X] T0b Create `tests/conftest.py` with a hyphenated-script import shim. The shim defines a fixture `extract_infographic_data` and `extract_report_data` that use `importlib.util.spec_from_file_location()`, `importlib.util.module_from_spec()`, and `spec.loader.exec_module(module)` (all three steps required) to load `scripts/extract-infographic-data.py` and `scripts/extract-report-data.py` respectively, exposing their public functions to tests. Document the technique with a one-paragraph comment so future contributors understand why imports are non-standard.
- [X] T0c Add `[tool.pytest.ini_options]` section to `pyproject.toml` (creating the file if absent). Set `testpaths = ["tests"]`, `python_files = ["test_*.py"]`, `python_functions = ["test_*"]`, and `addopts = "-ra --strict-markers"`. If a `pyproject.toml` already exists at repo root, edit it; otherwise create a minimal one.
- [X] T0d Create `requirements-dev.txt` at repo root listing test dependencies: `pytest>=8.0`, `pytest-cov>=4.1`. Document install command (`pip install -r requirements-dev.txt`) in the file's header comment.
- [X] T0e Add a `test:` target to `Makefile` (creating the file if absent) that runs `pytest tests/scripts/ --cov=scripts --cov-report=term-missing`. If a `Makefile` already exists, append the target.
- [X] T0f Create `tests/scripts/test_smoke.py` with one test function `test_extract_infographic_data_module_loads` that uses the conftest shim to load `extract-infographic-data.py` and asserts the module exposes at least one expected function (e.g., `parse_threats_findings` if re-exported, or just verifies the module object is non-None).
- [X] T0g Run `make test` (or `pytest tests/scripts/`) and verify the smoke test passes. If it fails, fix the conftest shim or pyproject configuration before proceeding. This is the gate that proves Phase 0 is complete.
- [X] T0h Update repo `README.md` (or create `CONTRIBUTING.md` if a separate file is preferred) with a "Running Tests" section explaining `pip install -r requirements-dev.txt` and `make test`. Brief — 5–10 lines.

**Checkpoint**: Phase 0 complete when `make test` exits 0 and prints the smoke test passing. Subsequent phases can now author real tests against the harness.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Pre-implementation verification and baseline preparation.

- [X] T001 Verify `examples/agentic-app/sample-report/threats.md` has at least one Critical or High severity finding (5-minute manual check; addresses architect L-1 observation). If absent, either update the example or choose a different example for regeneration. Record the chosen example in `specs/128-prd-128-executive/decisions.md` (file created by T002).
- [X] T002 Create `specs/128-prd-128-executive/decisions.md` documenting the baseline PDF storage approach (architect L-2 observation). Decide and record: (a) commit `security-report.pdf.baseline` files alongside each example in `examples/{name}/sample-report/`, (b) generate baselines on CI from parent revision, or (c) `git stash`/`git worktree` comparison. **Recommended**: option (a) for repeatability. Also record T001's outcome (the chosen example) in this file. **No forward dependency on test files** — `decisions.md` is created here in Phase 1, not in a later phase.
- [X] T003a Create a clean git worktree at `/tmp/tachi-pre-f128` checked out to `main` (or to the parent commit of the F-128 branch): `git worktree add /tmp/tachi-pre-f128 main`. This isolates baseline generation from the working branch without `git stash`.
- [X] T003b In the worktree at `/tmp/tachi-pre-f128`, run `/tachi.security-report --target-dir examples/{name}/sample-report/` for each of the 5 unmodified examples (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice). This produces 5 pre-F-128 PDF outputs.
- [X] T003c Verify deterministic baseline generation: run T003b a second time and `cmp` each output against the first run. All 5 must be byte-identical. If not, the existing pipeline has a non-determinism bug that must be fixed (or accommodated in the comparison strategy) before baselines are trusted.
- [X] T003d Copy each of the 5 deterministic baseline PDFs from the worktree into the working tree at the location chosen in T002 — recommended path: `examples/{name}/sample-report/security-report.pdf.baseline`.
- [X] T003e Remove the worktree: `git worktree remove /tmp/tachi-pre-f128`. The working branch is unchanged; baselines are now committed to the feature branch.

**Checkpoint**: Baselines established and verified deterministic. Code work can begin.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Schema-first per ADR-019. The schema enumeration must exist before extraction code references the new template name.

**CRITICAL**: No user story implementation can begin until this phase is complete.

- [X] T004 Add `executive-architecture` template enumeration to `schemas/infographic.yaml`. Use `specs/128-prd-128-executive/contracts/infographic-schema-additions.yaml` as the contract reference. Include: template name, alias (`exec`), six required spec sections (Metadata, Architecture Layers, Threat Callouts, Severity Distribution, Visual Layout Directives, Gemini Prompt Construction Notes), visual directives (portrait orientation, pastel layer fills, red dashed-border callouts, color palette, typography). Additive enumeration; no schema version bump required.

**Checkpoint**: Schema ready. User story implementation can now begin.

---

## Phase 3: User Story 1 - Generate executive-architecture infographic from threat model output (Priority: P1) MVP

**Goal**: A consultant can run `/tachi.infographic --template executive-architecture` against a threat model output folder and receive both a markdown spec file and a JPEG image showing the layered architecture with Critical/High threat callouts.

**Independent Test**: Run `/tachi.infographic --template executive-architecture --target-dir examples/agentic-app/sample-report/` and verify that `threat-executive-architecture-spec.md` is created with all 6 sections, and `threat-executive-architecture.jpg` is created (or absent only if Gemini API fails, in which case the spec is still present).

### Tests for User Story 1 (write FIRST, ensure they FAIL before implementation)

- [X] T005 [US1] Create unit test fixtures for executive-architecture extraction in `tests/scripts/fixtures/exec_arch/`: (1) `agentic_app/threats.md`, `agentic_app/risk-scores.md`, `agentic_app/compensating-controls.md` — copies of the corresponding files from `examples/agentic-app/sample-report/`; (2) `no_critical_high/threats.md` — synthetic threat model with only Medium/Low/Note severity findings; (3) `no_trust_zones/threats.md` — synthetic threat model with Section 1 components but empty Section 2; (4) `no_scope_data/threats.md` — synthetic threat model with empty Section 1 AND Section 2; (5) `mixed_case_components/threats.md` — synthetic threat model with case-inconsistent component names between trust zone definitions and finding `affected_component` fields; (6) `orphaned_finding/threats.md` — synthetic threat model with one Critical finding referencing a component not in any trust zone; (7) `multiple_per_layer/threats.md` — synthetic threat model where one trust zone has 5 Critical findings to verify per-layer dedup tie-break.
- [X] T006 [US1] Author all US-1 unit tests in a single file `tests/scripts/test_extract_infographic_data.py`. Tests included (each as a separate `test_*` function in the file):
  - `test_executive_architecture_happy_path` — agentic-app fixture; assert exit 0, ≥1 layer, ≥1 callout, `metadata.skip_image == False`, all callouts have severity in `{"Critical", "High"}`
  - `test_executive_architecture_with_risk_scores_tier` — agentic-app fixture with `risk-scores.md` present; assert `metadata.tier_source == "risk-scores"`, callouts have non-null `composite_score`
  - `test_executive_architecture_with_compensating_controls_tier` — agentic-app fixture with `compensating-controls.md` present; assert `metadata.tier_source == "compensating-controls"`
  - `test_executive_architecture_no_critical_high_skip_image` — `no_critical_high` fixture; assert exit 0, `metadata.skip_image == True`, `callouts == []`, `severity_distribution.critical_count == 0`, `high_count == 0`
  - `test_executive_architecture_no_threats_md` — empty folder; assert exit 1, stderr contains `threats.md missing`
  - `test_executive_architecture_no_scope_data` — `no_scope_data` fixture; assert exit 2, stderr contains `no parseable scope data`
  - `test_executive_architecture_trust_zone_fallback_to_dfd` — `no_trust_zones` fixture; assert exit 0, `metadata.fallback_used == True`, `layers[].source_kind == "dfd_type"`
  - `test_executive_architecture_one_callout_per_layer` — `multiple_per_layer` fixture; assert exactly 1 callout for the layer, selected by tie-break (severity desc → composite score desc → finding ID asc)
  - `test_executive_architecture_deterministic_output` — same input twice with `--frozen-time`; assert byte-identical JSON
  - `test_executive_architecture_orphaned_finding_dropped` — `orphaned_finding` fixture; assert the finding is filtered out of callouts (architect L-1 observation)
  - `test_executive_architecture_component_name_normalization` — `mixed_case_components` fixture; assert finding matches layer after normalization (architect L-1 observation)
  - `test_existing_templates_unchanged` — parametrized over the 5 existing templates (baseball-card, system-architecture, risk-funnel, maestro-stack, maestro-heatmap); for each, assert output is byte-identical to a checked-in golden JSON file under `tests/scripts/fixtures/golden/`
- [X] T007 [US1] Run `make test` (or `pytest tests/scripts/test_extract_infographic_data.py -v`). Confirm all 12 US-1 tests FAIL (the implementation does not exist yet). This is the test-first gate before any implementation begins.

### Implementation for User Story 1

- [X] T008 [US1] Add `executive-architecture` to the argparse `--template` choices list in `scripts/extract-infographic-data.py` (around line 1195). One-line change but enables the new dispatch path for all subsequent steps.
- [X] T009 [US1] Add three new helper functions to `scripts/extract-infographic-data.py`, in this order to avoid forward references:
  - `_compute_dfd_type_layers(scope_data)` — returns a list of `ArchitecturalLayer` dicts grouped by DFD `type` field from Section 1 components, sorted alphabetically by type name. Used as the fallback when trust zones are absent. Conform to the entity definition in `specs/128-prd-128-executive/data-model.md`.
  - `_normalize_component_name(name)` — returns the lowercased, trimmed, punctuation-stripped form of a component name. Used by the layer-finding matcher to address architect observation L-1.
  - `_select_critical_high_callouts(findings, layers)` — filters findings to Critical/High severity, matches each finding to its layer via normalized `affected_component`, applies the per-layer dedup with the tie-break rule (severity desc → composite score desc → finding ID asc) from data-model.md, drops orphaned findings (whose component matches no layer), and returns a list of `ThreatCallout` dicts.
- [X] T010 [US1] Add `_build_executive_architecture_payload(threats_content, tier_data, scope_data, source_file)` to `scripts/extract-infographic-data.py`. Combines `_compute_trust_zones()` (existing) or `_compute_dfd_type_layers()` (T009) for layers, calls `_select_critical_high_callouts()` (T009) for callouts, builds the `severity_distribution` (Critical/High counts only), builds the `metadata` block per the schema in `specs/128-prd-128-executive/data-model.md`, sets `skip_image = (total_filtered_count == 0)`, sets `fallback_used` based on which layer source was used, and returns the complete `ExecutiveArchitecturePayload` dict.
- [X] T011 [US1] Add the `executive-architecture` dispatch branch to the template selection logic in `scripts/extract-infographic-data.py` (around lines 1274-1277 where existing template branches live). When `args.template == "executive-architecture"`, call `_build_executive_architecture_payload()` from T010 and emit the JSON to stdout. Handle exit codes 0/1/2 per the contract in `specs/128-prd-128-executive/contracts/extraction-cli-contract.md`.
- [X] T012 [US1] Run `make test` and confirm all 12 US-1 tests now PASS. Iterate on T008-T011 until coverage of the new code in extract-infographic-data.py reaches ≥80% (verified via `pytest --cov`).
- [X] T013 [US1] Add the `executive-architecture` template description and six-section spec structure to `.claude/agents/tachi/threat-infographic.md` (around lines 64-75 where the existing template list lives). Each section must match the schema enumeration from T004. Document that the spec is rendered from the JSON payload emitted by T011.
- [X] T014 [US1] Add the Gemini prompt construction guidance to `.claude/agents/tachi/threat-infographic.md` for the executive-architecture template. The prompt MUST instruct Gemini to: render in portrait orientation; arrange architectural layers as horizontal bands with pastel fills (cycle from the palette in the schema); place red dashed-border callout boxes with warning icons connected to each layer's most exposed component; rewrite each callout's `raw_description` to ≤25 words in plain English with no technical jargon; use large readable typography. Reference the `visual_directives` block from `contracts/infographic-schema-additions.yaml`.
- [X] T015 [US1] Add the graceful skip-image branch to `.claude/agents/tachi/threat-infographic.md`: when `metadata.skip_image == True` in the payload, the agent MUST render the spec file with an explanatory note in the Threat Callouts section and MUST NOT invoke Gemini. One-paragraph "Skip Image Edge Case" subsection in the agent doc.

**Checkpoint**: User Story 1 fully functional. A consultant can now generate the spec and image standalone. Run quickstart Step 2 against agentic-app to validate.

---

## Phase 4: User Story 2 - Executive architecture page appears immediately after Executive Summary in PDF report (Priority: P1)

**Goal**: When the executive-architecture image exists in an output folder, compiling the PDF security report places it on the page immediately after the Executive Summary, before any other infographic pages or attack path analysis.

**Independent Test**: After completing US-1 against agentic-app, run `/tachi.security-report --target-dir examples/agentic-app/sample-report/` and open the resulting PDF. Verify the executive architecture page is immediately after Executive Summary, before Attack Path Analysis.

### Tests for User Story 2

- [X] T016 [US2] Author all US-2 unit tests in a single file `tests/scripts/test_extract_report_data.py`. Tests included:
  - `test_has_executive_architecture_true_when_image_present` — fixture folder with non-zero `threat-executive-architecture.jpg`; assert `report-data.typ` contains `#let has-executive-architecture = true`
  - `test_has_executive_architecture_false_when_image_absent` — fixture folder without the image; assert `#let has-executive-architecture = false`
  - `test_has_executive_architecture_false_when_image_zero_size` — fixture with empty (zero-byte) JPEG; assert false
  - `test_executive_architecture_image_path_relative_to_template_dir` — assert path written to `report-data.typ` is correctly relative
  - `test_existing_image_flags_unchanged` — assert funnel/baseball/architecture/maestro image flag values are byte-identical to a checked-in golden file
- [X] T017 [US2] Run `make test`. Confirm all 5 US-2 unit tests FAIL (implementation does not exist). Test-first gate.

### Implementation for User Story 2

- [X] T018 [US2] Add the `threat-executive-architecture.jpg` entry to the `detect_images()` function in `scripts/extract-report-data.py` (around lines 797-830). Follow the existing pattern: file exists check + size > 0 check.
- [X] T019 [US2] Add the `has-executive-architecture` boolean writer line and `executive-architecture-image-path` string writer line to the section that emits image-related Typst variables in `scripts/extract-report-data.py` (around line 940). Use `_typst_bool()` and `escape_typst_string()` per the existing convention. Reference `specs/128-prd-128-executive/contracts/report-data-typst-contract.md` for exact field names.
- [X] T020 [US2] Add the conditional page block to `templates/tachi/security-report/main.typ` immediately after the Executive Summary block (current line 191) and immediately before the Attack Path Analysis conditional block (current line 197). The block calls `infographic-page()` with `image-path: executive-architecture-image-path`, `section-name: "Executive Threat Architecture"`, `classification: classification-label`, and a brief descriptive caption explaining the visualization. **Reuse** the existing `infographic-page()` function from `templates/tachi/security-report/full-bleed.typ:40-86` (already portrait — no new template function required).
- [X] T021 [US2] Update the artifact detection table in `.claude/agents/tachi/report-assembler.md` to add a new row for `threat-executive-architecture.jpg` with the corresponding `has-executive-architecture` flag. Document the page positioning in the assembler agent's narrative.
- [X] T022 [US2] Run `make test`. Confirm all 5 US-2 unit tests now PASS. Iterate on T018-T019 until coverage reaches ≥80% on the new lines.
- [X] T023 [US2] Manual end-to-end verification: regenerate the agentic-app example. Run `/tachi.infographic --template executive-architecture --target-dir examples/agentic-app/sample-report/`, then `/tachi.security-report --target-dir examples/agentic-app/sample-report/`. Open the resulting PDF. Confirm the executive architecture page is immediately after Executive Summary, immediately before Attack Path Analysis. Document the verification (page count, TOC entries, page number) in `specs/128-prd-128-executive/manual-verification.md`.
- [X] T024 [US2] Create `tests/scripts/test_backward_compatibility.py` with `test_unmodified_examples_byte_identical_pdfs` — iterates over the 5 unmodified examples, runs `/tachi.security-report` for each, and `cmp`s the result against the baseline PDFs from T003d. Asserts all 5 are byte-identical. The baseline storage path comes from `decisions.md` (T002).
- [X] T025 [US2] Create `tests/scripts/test_pdf_page_positioning.py` with `test_executive_architecture_page_position` — runs the full pipeline on agentic-app, opens the resulting PDF (via `pypdf` if available, or `subprocess` calling `pdftotext`), asserts: (a) PDF has expected page count, (b) TOC contains "Executive Threat Architecture" entry, (c) the new page is at the position immediately after Executive Summary. Addresses plan Open Question #2.

**Checkpoint**: User Story 2 fully functional. PDF positioning correct. Backward compatibility confirmed for 5 unmodified examples.

---

## Phase 5: User Story 3 - The `all` shorthand includes the executive-architecture template (Priority: P2)

**Goal**: Running `/tachi.infographic --template all` produces 6 spec files instead of the previous 5, including the new executive-architecture template. The `exec` alias also works as a shortcut for direct invocation.

**Independent Test**: Run `/tachi.infographic --template all --target-dir examples/agentic-app/sample-report/` and verify 6 spec files exist (including `threat-executive-architecture-spec.md`). Run `/tachi.infographic --template exec --target-dir examples/agentic-app/sample-report/` and verify it dispatches to executive-architecture.

### Tests for User Story 3

- [X] T026 [US3] Author both US-3 dispatch tests in `tests/scripts/test_command_dispatch.py` (new file):
  - `test_all_shorthand_includes_executive_architecture` — verifies `all` expansion in `.claude/commands/tachi.infographic.md` includes `executive-architecture`
  - `test_exec_alias_dispatches_to_executive_architecture` — verifies `exec` alias maps to `executive-architecture` (single template, not a compound)

  Since these test command file content (not Python code), use file-content assertions: open `.claude/commands/tachi.infographic.md` and assert specific strings are present.

### Implementation for User Story 3

- [X] T027 [US3] Add `executive-architecture` to the valid template list in `.claude/commands/tachi.infographic.md` (around line 17). Add `exec` as an alias (around line 19 where existing aliases live). Update the `all` shorthand expansion (around lines 162-164) to include `executive-architecture` alongside the base templates, before the conditional MAESTRO additions.
- [X] T028 [US3] Run `make test` and confirm both T026 tests now PASS.

**Checkpoint**: User Story 3 fully functional.

---

## Phase 6: User Story 4 - Template gracefully handles threat models with no qualifying findings (Priority: P2)

**Goal**: Running the executive-architecture template against a threat model with no Critical or High findings produces a clean spec file (with skip_image flag set) and no JPEG, and the downstream PDF compilation omits the page entirely.

**Independent Test**: Run extraction against the `no_critical_high` fixture from T005. Verify exit code 0, spec file produced with `skip_image: true`, no JPEG generated, and PDF omits the page.

### Tests for User Story 4

- [X] T029 [US4] Author US-4 PDF skip test in `tests/scripts/test_pdf_page_positioning.py` (file created in T025): `test_executive_architecture_skip_image_pdf_omits_page` — runs the full pipeline on a fixture folder where extraction produces `skip_image: true`; asserts the resulting PDF does NOT contain the executive architecture page (page count matches the no-image baseline). The corresponding extraction-side test (`test_executive_architecture_no_critical_high_skip_image`) is already in T006's bundle.

### Implementation for User Story 4

- [X] T030 [US4] No new implementation required — the skip-image behavior was implemented in T010 (extraction sets `skip_image`) and T015 (agent honors the flag). T029 verifies the existing implementation works end-to-end. If T029 fails, fix T010 or T015. This task is satisfied by T029 passing.

**Checkpoint**: User Story 4 fully functional.

---

## Phase 7: Documentation, Polish & Example Regeneration

**Purpose**: Documentation parity with existing templates, example regeneration, gate checkpoints, final cross-cutting validation.

- [X] T031 [P] Add a new reference doc `executive-architecture.md` in `.claude/skills/tachi-infographics/references/` describing the template (purpose, output artifacts, parameters, PDF positioning). Follow the format of existing reference docs in that folder for parity. Implements FR-036.
- [X] T032 [P] Update `.claude/skills/tachi-infographics/SKILL.md` (or equivalent index file) to list the new `executive-architecture` template alongside the existing 5.
- [X] T033 Regenerate the `examples/agentic-app/sample-report/` example. Run `/tachi.infographic --template executive-architecture --target-dir examples/agentic-app/sample-report/` and `/tachi.security-report --target-dir examples/agentic-app/sample-report/`. Stage the new files: `threat-executive-architecture-spec.md`, `threat-executive-architecture.jpg`, and the updated `security-report.pdf`. Implements FR-034.
- [X] T034 Run the full test suite via `make test`. All tests must pass: smoke test (T0f), 12 US-1 tests (T006), 5 US-2 tests (T016), 2 US-3 tests (T026), 1 US-4 PDF test (T029), backward compat test (T024), page positioning test (T025), AND all pre-existing tests if any are added later. Backward compatibility coverage from T024 is included in this run, so T051/T052 from the prior tasks.md are now consolidated into this single command.
- [X] T035 [code-reviewer] Code-review the full F-128 diff against the constitution and F-091/F-112 pattern parity. Reviewer should verify: backward compatibility (Principle III), test coverage ≥80% (Principle VI), conventional commits (Principle IX), reuse of `infographic-page()` (no new Typst function), proper schema-first ordering. Document review outcome in `specs/128-prd-128-executive/code-review.md`. Resolves architect's Phase 7 checkpoint gap.
- [X] T036 [architect] Architect sign-off checkpoint on implementation. Architect should verify: `main.typ` insertion point is at the documented line range, the conditional block correctly reuses `infographic-page()`, the new code paths in `extract-infographic-data.py` follow F-091 pattern, the backward compatibility test from T024 passes, the data model in code matches `data-model.md`. Document in `specs/128-prd-128-executive/architect-checkpoint.md`. Resolves architect's Phase 7 checkpoint gap.
- [X] T037 [security-analyst] Security review: confirm no new secrets, PII, or credentials introduced via the example regeneration (T033). The agentic-app threats.md is a sanitized fixture; the new image is generated by Gemini from that fixture and should also be sanitized. Document in `specs/128-prd-128-executive/security-review.md`. If the team prefers `--no-security` justification on `/aod.build` instead, document the rationale here and skip this task. Either path satisfies the security gate.
- [X] T038 [P] Usability check (per spec SC-004): show pages 1–7 of the regenerated agentic-app PDF to one non-technical reviewer. Ask "what is the most exposed architectural layer in this system?" Record whether they answer correctly within 30 seconds. Document the result in `specs/128-prd-128-executive/manual-verification.md`. **Non-blocking with 5-business-day SLA**: if a reviewer is not available before T039 (PR open), open the PR anyway and complete this check post-merge within 5 business days. Reviewer name and date should be pre-arranged during T001 if possible to remove friction. **DEFERRED**: non-blocking per SLA; T039 proceeds without T038.
- [X] T039 Open a pull request per the Git Workflow constitution principle. PR title format: `feat(128): add executive threat architecture infographic with early-page PDF positioning`. PR body must reference: spec.md, plan.md, tasks.md, the architect/PM/team-lead sign-off statuses, the agentic-app regeneration, the backward compatibility test results from T024/T034, and the code-review (T035), architect-checkpoint (T036), and security-review (T037) artifacts. Include `[ ]` checkboxes for any deferred items (e.g., T038 if completed post-merge). **PR #131 created: https://github.com/davidmatousek/tachi/pull/131** (commit 01d3e85)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 0 (Test Infrastructure Bootstrap)**: T0a → T0b → T0c → T0d → T0e → T0f → T0g → T0h. Mostly sequential because each builds on the previous (directory before files, files before config, config before smoke test). T0g is the gate.
- **Phase 1 (Setup)**: T001 + T002 in parallel after Phase 0; T003a → T003b → T003c → T003d → T003e sequential after T002.
- **Phase 2 (Foundational)**: T004 depends on Phase 1 complete.
- **Phase 3 (US-1)**: T005 → T006 → T007 → T008 → T009 → T010 → T011 → T012 → T013 → T014 → T015. T013, T014, T015 can run after T012 in any order.
- **Phase 4 (US-2)**: All US-2 tasks depend on US-1 implementation being complete (T011 minimum). T016 → T017 → T018 → T019 → T020 → T021 → T022 → T023 → T024 → T025.
- **Phase 5 (US-3)**: T026 → T027 → T028. Depends on T008 (`executive-architecture` exists in argparse).
- **Phase 6 (US-4)**: T029 → T030. Depends on T010 + T015 + T020 (full pipeline available).
- **Phase 7 (Polish)**: T031, T032 are documentation tasks and can run in parallel with anything from Phase 3 onward. T033 depends on Phase 6 complete. T034 depends on T033. T035, T036, T037 depend on T034. T038 can run in parallel with T035/T036/T037 if a reviewer is available (otherwise downgraded post-merge). T039 depends on T034 + T035 + T036 + T037.

### Critical Path

T0a → T0b → T0c → T0d → T0e → T0f → T0g → T0h → T001 → T002 → T003a → T003b → T003c → T003d → T003e → T004 → T005 → T006 → T007 → T008 → T009 → T010 → T011 → T012 → T013 → T014 → T015 → T016 → T017 → T018 → T019 → T020 → T021 → T022 → T023 → T024 → T025 → T026 → T027 → T028 → T029 → T030 → T033 → T034 → T035 → T036 → T037 → T039

(T031, T032, T038 are off the critical path.)

### Parallel Opportunities

- T031 + T032 (skill reference docs) can run in parallel with all of Phases 3–7
- T013 + T014 + T015 (agent doc updates) can run after T012 in any order
- T018 + T019 (extract-report-data edits) are sequential (same file)
- T035 + T036 + T037 (gates) can run in parallel after T034
- T038 (usability) can run in parallel with T035-T037 if reviewer is available
- Across stories: once US-1 is complete, US-2 and US-3 can be authored in parallel by different agents (US-2 touches Python+Typst+report-assembler.md; US-3 touches the command file)

### Estimation by Phase (~5–6 sessions, ~745 lines of code+docs)

| Phase | Tasks | Lines | Hours | Sessions |
|-------|-------|-------|-------|----------|
| Phase 0 | T0a–T0h (8) | ~60 | 2.0 | 0.5–1 |
| Phase 1 | T001, T002, T003a–e (7) | n/a | 1.5 | 0.5 |
| Phase 2 | T004 (1) | ~25 | 0.5 | 0.1 |
| Phase 3 | T005–T015 (11) | ~290 (fixtures + tests + impl + agent doc) | 7.0 | 2 |
| Phase 4 | T016–T025 (10) | ~200 (tests + impl + integration tests + verification) | 5.0 | 1.5 |
| Phase 5 | T026–T028 (3) | ~30 | 0.5 | 0.2 |
| Phase 6 | T029–T030 (2) | ~30 | 0.3 | 0.1 |
| Phase 7 | T031–T039 (9) | ~110 (docs + checkpoints + PR) | 3.0 | 1 |
| **Total** | **51 tasks** | **~745** | **~19.5 hours** | **~5–6 sessions** |

---

## Implementation Strategy

### MVP (Phases 0 + 1 + 2 + 3 + 4 → US-1 and US-2)

Both US-1 and US-2 are P1, and the feature delivers no executive value without both.

1. Bootstrap test infrastructure (Phase 0)
2. Establish baselines (Phase 1)
3. Schema first (Phase 2)
4. US-1 extraction + agent (Phase 3)
5. US-2 PDF integration (Phase 4)
6. **STOP and VALIDATE**: Run quickstart Steps 1-4 against agentic-app

### Incremental Delivery

7. Add US-3 + US-4 (Phases 5-6) for discoverability and edge cases
8. Phase 7 polish + gates + PR

### Parallel Team Strategy

With multiple agents:
- Agent A (orchestrator + senior-backend-engineer): Phase 0 → Phase 1 → Phase 2 → Phase 3
- Agent B (senior-backend-engineer + tester): joins at Phase 4 (US-2)
- Agent C (senior-backend-engineer): joins at Phase 5 + Phase 6 (US-3 + US-4)
- Phase 7 gates run sequentially after all code phases complete

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks within the same file
- [Story] label maps task to specific user story for traceability
- Tests are constitutionally required (Principle VI ≥80% coverage); verify tests fail before implementation
- Commit after each task or logical group; conventional commit format: `feat(128): <task description>`
- Architect observations L-1 and L-2 are addressed by tasks T001, T002, T005 (mixed_case + orphaned fixtures), T009 (normalize helper), T024 (backward compat test)
- Plan Open Question #2 (PDF page-count assertion test) is addressed by T025
- Agent assignments are documented in `specs/128-prd-128-executive/agent-assignments.md` (separate file generated by team-lead per /aod.tasks Step 6)
- Avoid: vague tasks, same-file conflicts within parallel groups, cross-story dependencies that break independent testability
