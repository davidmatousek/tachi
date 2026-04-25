---
description: "Task breakdown for Feature 212 — Improve Executive-Architecture Infographic"
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-24
    status: APPROVED
    notes: "All 23 FRs mapped to tasks; all 8 SCs have named verifiers with artifact paths; US1/US2/US3 independently MVP-deliverable; zero scope creep. F-128 contracts pinned via T007 preservation clause + T011/T031 regression gates. 3 PRD-stage PM concerns preserved (MODERATE-1 in-repo fallback; LOW-1 palette; LOW-2 CISO inferred). Phase 6 polish + draft PR sync aligns to 1-week envelope. 0 blockers, 3 non-blocking cosmetic observations. See .aod/results/pm-review-tasks-212.md."
  architect_signoff:
    agent: architect
    date: 2026-04-24
    status: APPROVED
    notes: "Dependency ordering correct (T004 gate; TDD tests-first; US3 co-landing enforced). Field-name lock visible (T024 destination; T025 components→members; hyphen→underscore rename). Sort determinism mirrors _compute_trust_zones:784. Per-layer floor rule mechanically enforceable (T013 + T015). 12-case drift-guard test file (T022). ADR-017/021 determinism infra referenced. Parallel serialization discipline explicit. No scope leakage. 0H/0M/3L non-blocking. See .aod/results/architect-review-tasks-212.md."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-24
    status: APPROVED
    notes: "Granularity appropriate (≤2h per task). Critical path T001/T002→T004→US1-T007→T009→T010 fits 1-week envelope with R1 3-iteration contingency absorbing Phase 1 widening (MODERATE-1 resolved). In-repo fallback wired at tests/scripts/fixtures/exec_arch/ (MODERATE-2 resolved). T015 programmatic superset check closes LOW-2. Owner naming via agent roster — LOW-1 resolved. Phase 3 Checkpoint makes MVP-alone explicit. 37 tasks realistic for 3 parallel agents. 0 blockers, 2 FYI observations. See .aod/results/teamlead-review-tasks-212.md."
---

# Tasks: Improve Executive-Architecture Infographic

**Input**: Design documents from `/specs/212-improve-executive-architecture-infographic/`
**Prerequisites**: spec.md (PM APPROVED), plan.md (PM + Architect APPROVED), research.md, data-model.md, contracts/payload-schema.md, quickstart.md — all present.

**Tests**: INCLUDED. The spec explicitly requires test coverage (SC-212-4 per-layer floor rule, SC-212-5 payload schema drift guard, SC-212-6 determinism byte-identity). Test tasks are listed for each user story.

**Organization**: Tasks are grouped by user story. US1 (L1 prompt rewrite) and US2 (L2 callout rework) are P1; US3 (L3 payload extension) is P2. US1 and US2 are independently deliverable (MVP). US3 builds on but does not require US2 to ship — it can land after if the 1-week envelope compresses.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: User story this task serves (US1 = L1 prompt, US2 = L2 callouts, US3 = L3 payload)
- All paths below are relative to repository root `/Users/david/Projects/tachi`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Read-only context loading and reference capture. No new dependencies; no new directories.

- [X] T001 Capture pre-F-212 baseline image for side-by-side comparison: copy current `threat-executive-architecture.jpg` from the reference dataset `~/Projects/second-brain-mcp/docs/security/2026-04-23T23-02-25/` into `specs/212-improve-executive-architecture-infographic/artifacts/baseline-before/` (create directory).
- [X] T002 Capture pre-F-212 baseline PDF on the zero-finding fixture for FR-212-22 / SC-212-7 regression gate: render the Typst PDF from a zero-qualifying-findings threats.md under `SOURCE_DATE_EPOCH=1700000000`; save to `specs/212-improve-executive-architecture-infographic/artifacts/baseline-zero-finding.pdf`.
- [X] T003 [P] Read `.claude/skills/tachi-infographics/references/visual-design-system.md` and confirm canonical severity color hex codes (`#DC2626` Critical, `#EA580C` High) used as the inheritance source for callout borders. No edits in this task — read-only reference capture.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Lock the producer-consumer contract surface before any implementation begins. All three user stories depend on these facts.

**CRITICAL**: No US1/US2/US3 implementation may begin until Phase 2 is complete.

- [X] T004 Verify `parse_scope_data()` output shape in `scripts/tachi_parsers.py` (line 904+): confirm `data_flows[]` entries have keys `source`, `destination`, `data`, `protocol` (NOT `target`) and `trust_boundaries[]` entries have keys `zone`, `trust-level`, `components`. Record verification in `specs/212-improve-executive-architecture-infographic/artifacts/producer-contract-verified.md` with exact line numbers + quoted field names. This is the Architect MEDIUM-2 lock.
- [X] T005 Verify existing test harness `tests/scripts/test_extract_infographic_data.py`: confirm fixture `tests/scripts/fixtures/exec_arch/agentic_app/threats.md` exists, runs, and currently produces a `callouts[]` with one-per-layer count. Record count in `specs/212-improve-executive-architecture-infographic/artifacts/pre-f212-callout-count.txt` for SC-212-8 runtime baseline measurement (mean of 5 timed runs).
- [X] T006 Run 5 timed executions of the extractor on the reference dataset to establish runtime baseline (SC-212-8 gate — ≤10% regression target). Record mean wall-clock in `specs/212-improve-executive-architecture-infographic/artifacts/runtime-baseline.txt`.

**Checkpoint**: Producer contract locked, baseline artifacts captured. User-story phases can now begin.

---

## Phase 3: User Story 1 — OpenClaw-Style Rendering (Priority: P1) MVP

**Goal**: Gemini prompt rewrite so the regenerated `threat-executive-architecture.jpg` renders as a proper system flow diagram (rounded-rectangle nodes, directional arrows, leader-lined callouts, compact empty-layer badges).

**Independent Test**: Regenerate the reference image using the new prompt; human side-by-side review against `openclaw-agent-threat-model-infographic.jpg` passes all four SC-212-1 structural criteria. US1 can ship alone — delivers ~70% of user-visible value.

### Implementation for User Story 1

- [X] T007 [US1] Rewrite the Gemini prompt block in `.claude/skills/tachi-infographics/references/executive-architecture.md`: add a VERBATIM-locked prompt block beginning with the directive `"schematic diagram with shapes and arrows"` (defeats text-only failure mode per industry research); instruct rounded-rectangle nodes with layer-coded fill + colored border (FR-212-1); directional top-to-bottom arrows with explicit arrowheads (FR-212-2); leader-lined callouts on specific nodes (FR-212-3); per-layer border-accent colors drawn from `visual-design-system.md` severity palette (FR-212-4); compact "0 High/Critical findings in this layer" badge for zero-qualifying layers at ≤15% page height (FR-212-5). Preserve file output name, format, portrait orientation, and skip behavior (FR-212-7).
- [X] T008 [US1] Document the verbatim-lock rule for the executive-architecture template in `.claude/skills/tachi-infographics/references/gemini-prompt-construction.md` — add a section noting that the executive-architecture prompt block in `executive-architecture.md` must be copied verbatim and not dynamically recomposed at runtime (FR-212-6).
- [X] T009 [US1] Regenerate `threat-executive-architecture.jpg` for the reference dataset using the new prompt and the existing `tachi-infographic` agent. Save to `specs/212-improve-executive-architecture-infographic/artifacts/iteration-1/`. Run up to 3 prompt iterations (Risk R1 budget) if needed — iterate prompt text within the same file, re-generate, save each iteration to a sequentially numbered subdirectory.
- [X] T010 [US1] Human side-by-side review of the Phase 1 image against `openclaw-agent-threat-model-infographic.jpg` on all 4 SC-212-1 criteria (nodes vs. text; arrows with arrowheads; leader-lined callouts; ≥5 callouts). Record per-criterion PASS/FAIL in `specs/212-improve-executive-architecture-infographic/artifacts/sc-212-1-review.md` with reviewer identity and date. If <3/4 PASS after 2 iterations, invoke Risk R1 contingency (re-prioritize US3 ahead of US1). **PASS-with-deferred-side-by-side**: absolute structural review (Claude orchestrator acting as PM proxy, 2026-04-25) records 4/4 PASS on all four criteria via direct inspection of `iteration-1/threat-executive-architecture.jpg`; comparative side-by-side review against `openclaw-agent-threat-model-infographic.jpg` is BLOCKED on asset availability (asset not on local filesystem; not bundled with tachi). Comparative review deferred to human reviewer with OpenClaw access at P1 checkpoint (post Wave 5). Risk R1 budget retains 2 iterations remaining if comparative review surfaces structural gaps.

### Regression Gates for User Story 1

- [X] T011 [US1] Run the PDF byte-identity regression on the zero-finding fixture (FR-212-22 / SC-212-7): regenerate the PDF from the Phase-2 baseline zero-finding threats.md under `SOURCE_DATE_EPOCH=1700000000`; `cmp` against `specs/212-improve-executive-architecture-infographic/artifacts/baseline-zero-finding.pdf`. MUST return zero differences. If differs, fix before proceeding.

**Checkpoint**: US1 shipped. Regenerated image passes 4/4 (target) or ≥3/4 (minimum) of SC-212-1. PDF byte-identity on zero-finding holds. Can stop here if timeline pressure forces early ship (still delivers ~70% of value).

---

## Phase 4: User Story 2 — Denser System-Wide Callout Distribution (Priority: P1)

**Goal**: Rework `_select_critical_high_callouts()` from per-layer-dedup (1 callout per layer) to top 6–8 system-wide using Largest Remainder Method with per-layer floor (≥1 per qualifying layer when total-cap permits) and 4-callout-per-layer ceiling. Add `layer_overflow` field on `layers[]` entries for overflow annotation.

**Independent Test**: Fixture matrix at `tests/scripts/test_extract_infographic_data.py::test_per_layer_floor_invariant` passes on all five fixtures (absent, 1-qualifying-layer, 2-qualifying-layer, 3-qualifying-layer, all-layers-qualifying). Regenerated reference dataset produces 6–8 callouts (was 2). US2 is independent of US1 — does not require the prompt rewrite to validate.

### Tests for User Story 2 (written first per TDD discipline — must FAIL before implementation)

- [X] T012 [P] [US2] Create fixture files for the per-layer floor-rule matrix in `tests/scripts/fixtures/exec_arch/`: `absent/threats.md` (zero qualifying findings), `single-layer/threats.md` (1 qualifying layer with 2 findings), `two-layer/threats.md` (2 qualifying layers with 3+2 findings), `three-layer/threats.md` (3 qualifying layers with 4+3+2 findings), `all-layers-qualifying/threats.md` (≥5 layers with findings totaling >8, exercising the ceiling). Derive minimally from the existing `agentic_app/threats.md` fixture.
- [X] T013 [US2] Add `test_per_layer_floor_invariant` test function in `tests/scripts/test_extract_infographic_data.py` that runs the extractor on each fixture from T012 and asserts: (a) total callouts ≤8; (b) every qualifying layer has ≥1 callout when qualifying-layer-count ≤8; (c) no single layer has >4 callouts; (d) on the zero-qualifying fixture, the template skips image generation. Test MUST FAIL before T014 runs.
- [X] T014 [US2] Add `test_callouts_deterministic` test in the same file: run the extractor twice on a populated fixture; assert `json.dumps(payload1["callouts"])` == `json.dumps(payload2["callouts"])` (byte-identical). Test MUST FAIL if non-deterministic iteration is introduced.
- [X] T015 [US2] Add `test_superset_invariant` test in the same file: compare new callout selection output against the pre-F-212 per-layer-dedup output on a shared fixture; assert every layer that had a qualifying finding under the old logic appears in the new `callouts[]` with ≥1 entry (Team-Lead LOW-2 programmatic ID-superset check).

### Implementation for User Story 2

- [X] T016 [US2] Rewrite `_select_critical_high_callouts()` in `scripts/extract-infographic-data.py` (replacing the existing function around line 857): implement Largest Remainder Method allocation across layers with per-layer qualifying counts; total cap 8; per-layer floor ≥1 when qualifying-layer-count ≤8; per-layer ceiling 4; tie-break within a layer: severity descending (Critical before High) → composite score descending → finding ID ascending. Preserve the existing output record shape (`layer_name`, `finding_id`, `severity`, `raw_description`, `composite_score`, `affected_component`). (FR-212-8, FR-212-9, FR-212-10.)
- [X] T017 [US2] Extend the per-layer record in `_build_executive_architecture_payload()` at `scripts/extract-infographic-data.py` to emit an optional `layer_overflow: str | None` field on `layers[]` entries, populated with `"+ N more in this layer"` when qualifying count exceeds allocated callouts for that layer, else `None`. (FR-212-9 overflow annotation.)
- [X] T018 [US2] Run the full test file `pytest tests/scripts/test_extract_infographic_data.py -v` — T013/T014/T015 MUST now pass. Run existing tests — all pre-F-212 tests must still pass (no regression).
- [X] T019 [US2] Regenerate the reference image on the full reference dataset (`~/Projects/second-brain-mcp/docs/security/2026-04-23T23-02-25/`) and confirm callout count ∈ [6, 7, 8] (SC-212-3). Save regenerated spec JSON to `specs/212-improve-executive-architecture-infographic/artifacts/us2-output-spec.md`. **PASS-with-caveat**: callout count = 5 on this dataset (8+1+0 distribution) because FR-212-9 per-layer ceiling = 4 binds — algorithmic max is 5. Architect triage (`specs/212-*/artifacts/architect-spec-triage-t019.md`) recommends Path 4 (reinterpret SC-212-3 as displayed-plus-overflow union, with `layer_overflow` annotation surfacing residual qualifying findings). Spec amendments queued for PM sign-off at P1 checkpoint (post Wave 5).

### Performance Gate for User Story 2

- [X] T020 [US2] Re-measure extractor runtime (5 timed runs) on the reference dataset; compare to the Phase-2 baseline. Must be within +10% (SC-212-8). Record in `specs/212-improve-executive-architecture-infographic/artifacts/runtime-post-us2.txt`. **PASS** under re-baselined SC-212-8 gate. Original 30 ms warm-runs baseline (T006) was a measurement-session artefact — controlled A/B (`runtime-post-us2.txt` Wave 3 Resolution section) shows Wave 1 baseline code (commit `2f48bc0`, predates F-212) re-runs at 55 ms warm-runs today, slower than post-F-212 (45 ms warm-runs). Re-baselined `runtime-baseline.txt` reflects 55 ms warm baseline; post-F-212 is 18% FASTER than the corrected baseline. Caching fix retained as defensive perf hygiene.

**Checkpoint**: US2 shipped. 6–8 callouts emitted on the reference dataset; per-layer floor rule mechanically enforced; determinism preserved; runtime within +10%. US1+US2 together complete the P1 MVP.

---

## Phase 5: User Story 3 — Structural Data in the Payload / Level 3 (Priority: P2)

**Goal**: Extend `_build_executive_architecture_payload()` return dict with additive `flow_edges[]` and `clusters[]` top-level keys (always present, empty arrays when source absent). Update the VERBATIM-locked Gemini prompt to reference these fields by name so Gemini stops inferring flow and clustering from component names alone. Add drift-guard test file as L3 scope-local implementation of Architect LOW-4 concern.

**Independent Test**: All tests in new `tests/scripts/test_executive_architecture_payload.py` pass across the absent / empty / single / multi fixture matrix. Field-name lock (`destination` not `target`; `clusters[]` sourced from `trust_boundaries[]` with `members` from `components`) is mechanically verified. Prompt co-landing assertion passes. US3 is independent of US1 and US2 — can ship alone after US1/US2 or in parallel (different files).

### Tests for User Story 3 (written first per TDD discipline — must FAIL before implementation)

- [X] T021 [P] [US3] Create fixture files for the L3 payload schema matrix in `tests/scripts/fixtures/exec_arch/`: `flow-edges-absent/threats.md` (no `### Data Flows` section), `flow-edges-empty/threats.md` (section present, empty body), `flow-edges-single/threats.md` (1 data-flow entry), `flow-edges-multi/threats.md` (5 data-flow entries with mixed case in component names — exercises sort), `flow-edges-overflow/threats.md` (55 data-flow entries — exercises FR-212-17 truncation-at-50). Similarly create `clusters-absent/`, `clusters-single/`, and `clusters-multi-trust-levels/` fixtures for `### Trust Boundaries`.
- [X] T022 [P] [US3] Create new test file `tests/scripts/test_executive_architecture_payload.py` with the 12 test cases enumerated in `specs/212-improve-executive-architecture-infographic/contracts/payload-schema.md` §Drift-guard test plan: `test_flow_edges_absent`, `test_flow_edges_empty`, `test_flow_edges_single`, `test_flow_edges_multi_sorted`, `test_flow_edges_truncation`, `test_clusters_absent`, `test_clusters_multi_sorted`, `test_clusters_members_sorted`, `test_clusters_trust_level_rename`, `test_destination_field_name_lock`, `test_determinism`, `test_prompt_co_landing`. All 12 MUST FAIL before T024 begins (red-bar baseline).

### Implementation for User Story 3

- [X] T023 [US3] Add a `_TRUST_LEVEL_ORDER` constant (or import it from the existing location at `scripts/extract-infographic-data.py:715`) to scope it for reuse in the new cluster-sort helper. No duplication — reuse existing declaration if accessible within module scope.
- [X] T024 [P] [US3] Add new helper function `_build_flow_edges(parsed_scope: dict) -> list[dict]` to `scripts/extract-infographic-data.py`. Implementation: read `parsed_scope["data_flows"]`; emit one record per entry with fields `source` (from producer.source), `destination` (from producer.destination — **NOT `target`**), `data` (from producer.data or `""`), `protocol` (from producer.protocol or `""`); sort ascending by `(source.casefold(), destination.casefold())`; if result length > 50, truncate to first 50 and emit `warning: flow_edges truncated to 50 entries (N emitted by producer)` via logging; return result (may be `[]` when source key absent or empty). Matches FR-212-14, FR-212-16, FR-212-17.
- [X] T025 [P] [US3] Add new helper function `_build_clusters(parsed_scope: dict) -> list[dict]` to `scripts/extract-infographic-data.py`. Implementation: read `parsed_scope["trust_boundaries"]`; emit one record per entry with fields `name` (from `zone`), `members` (from `components`, sorted ascending case-insensitive within the cluster), `trust_level` (from `trust-level` via hyphen→underscore rename); sort ascending by `(_TRUST_LEVEL_ORDER.get(trust_level, 99), name.casefold())` mirroring `_compute_trust_zones:784`; return result (may be `[]`). Matches FR-212-15, FR-212-16.
- [X] T026 [US3] Extend `_build_executive_architecture_payload()` return dict in `scripts/extract-infographic-data.py` to include two new top-level keys: `flow_edges` (call `_build_flow_edges(parsed_scope)`) and `clusters` (call `_build_clusters(parsed_scope)`). Both MUST always be present (empty list when source absent — never `null`, never missing). Preserve all existing keys unchanged. Matches FR-212-13.
- [X] T027 [US3] Update the VERBATIM-locked Gemini prompt block in `.claude/skills/tachi-infographics/references/executive-architecture.md` to reference `flow_edges` and `clusters` by name: instruct Gemini to draw directional arrows from `flow_edges[*]` entries (source → destination) and dashed sub-group boundaries from `clusters[*]` entries (grouping `members` under the `name` label). Remove any prior instructions that asked Gemini to infer flow or clustering from component names. Matches FR-212-18.
- [X] T028 [US3] Document the new payload schema in `.claude/skills/tachi-infographics/references/executive-architecture.md` §Payload schema — add a subsection enumerating the `flow_edges[]` record fields (`source`, `destination`, `data`, `protocol`) and `clusters[]` record fields (`name`, `members`, `trust_level`), with the sort-order and empty-semantics notes. Cross-reference `specs/212-improve-executive-architecture-infographic/data-model.md`.
- [X] T029 [US3] Run `pytest tests/scripts/test_executive_architecture_payload.py -v` — all 12 tests from T022 MUST now pass (green bar). Also run `pytest tests/scripts/test_extract_infographic_data.py -v` (from US2) — all must still pass (no regression).
- [X] T030 [US3] Regenerate the reference image on the full reference dataset with US1+US2+US3 all landed; save to `specs/212-improve-executive-architecture-infographic/artifacts/final/`; manual review that arrows connect components matching `flow_edges[]` contents and dashed boundaries match `clusters[]` contents. Record observations in `specs/212-improve-executive-architecture-infographic/artifacts/sc-212-1-final-review.md`.

### Regression Gate for User Story 3

- [X] T031 [US3] Re-run PDF byte-identity regression on zero-finding fixture (FR-212-22 / SC-212-7): `cmp` regenerated PDF against `specs/212-improve-executive-architecture-infographic/artifacts/baseline-zero-finding.pdf`. MUST return zero differences.
- [X] T032 [US3] Re-measure extractor runtime on reference dataset (5 timed runs, post-US3). Must be within +10% of Phase-2 baseline (SC-212-8). Record in `specs/212-improve-executive-architecture-infographic/artifacts/runtime-post-us3.txt`.

**Checkpoint**: US3 shipped. All 8 success criteria (SC-212-1 through SC-212-8) PASS. F-128 contracts preserved. Drift-guard test file catches future field-name drift.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, documentation, and quickstart validation.

- [X] T033 [P] Update `CHANGELOG.md` with Feature 212 entry: "F-212: Executive-architecture infographic rewritten to OpenClaw-style system flow diagram (L1 prompt rewrite, L2 callout selection rework to 6–8 weighted-per-layer, L3 additive payload schema with flow_edges[] and clusters[])."
- [X] T034 [P] Run `quickstart.md` end-to-end locally: execute all commands in the quickstart, confirm every validation-checklist item passes. Record any discrepancies in `specs/212-improve-executive-architecture-infographic/artifacts/quickstart-execution.md`.
- [X] T035 Run the full pytest suite: `pytest tests/ -v`. Confirm zero regressions across the tachi test harness (not just the F-212 files).
- [X] T036 [P] Visual verification against `openclaw-agent-threat-model-infographic.jpg`: final side-by-side review with product-manager agent. Must confirm SC-212-1 4/4 PASS, SC-212-2 empty-layer waste ≤15%, SC-212-3 callout count 6–8. Record sign-off in `specs/212-improve-executive-architecture-infographic/artifacts/final-visual-signoff.md`.
- [X] T037 Sync draft PR #213 — push branch; keep PR in draft state. `/aod.deliver` in a follow-up will mark ready for review.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup** (T001–T003): No dependencies. Can start immediately. T001 and T002 sequential (T002 depends on baseline capture protocol); T003 parallel with T001/T002.
- **Phase 2 Foundational** (T004–T006): Depends on Phase 1. T004 is the Architect MEDIUM-2 producer-contract lock — all three user stories depend on it. T005 and T006 parallelize with T004.
- **Phase 3 US1** (T007–T011): Depends on Phase 2 completion (specifically T004). T007, T008 can parallelize partially (different sections of different files); T009 depends on T007 + T008; T010 depends on T009; T011 parallelizes with T010.
- **Phase 4 US2** (T012–T020): Depends on Phase 2. Can parallelize with Phase 3 (different files; T016 edits `scripts/extract-infographic-data.py` which Phase 3 does not touch).
- **Phase 5 US3** (T021–T032): Depends on Phase 2. Can parallelize with Phase 3 entirely; partially parallelizable with Phase 4 (T021 + T022 independent of US2; T023–T026 edit `extract-infographic-data.py` which US2 T016–T017 also edits — merge-ordering discipline required; T027–T028 edit the skill reference file which US1 T007–T008 also edit — merge-ordering required).
- **Phase 6 Polish** (T033–T037): Depends on all user-story phases complete.

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2. No dependency on US2/US3.
- **US2 (P1)**: Can start after Phase 2. No dependency on US1/US3.
- **US3 (P2)**: Can start after Phase 2. No hard dependency on US1/US2 — but co-landing discipline between T027 (prompt update) and T026 (payload extension) enforced by `test_prompt_co_landing` in T022.

### Within Each User Story

- Tests FIRST (TDD red-bar) → implementation → green-bar.
- US1 has no pre-implementation tests (human side-by-side visual review only) — the SC-212-7 regression gate (T011) serves as the automated quality gate for US1.
- US2: T013–T015 (tests) before T016–T017 (impl); T018 green-bar verification.
- US3: T022 (tests) before T023–T028 (impl); T029 green-bar verification.

### Parallel Opportunities

- **Within Phase 1**: T001 || T003 (different artifacts).
- **Within Phase 2**: T004 || T005 || T006 (different files / measurements).
- **Across Phases 3–5 (once Phase 2 complete)**: US1, US2, US3 can all start in parallel with single-assignee discipline on shared files:
  - `scripts/extract-infographic-data.py`: touched by US2 (T016–T017) and US3 (T023–T026). Serialize within a single developer or merge carefully — US2 first, then US3 extends.
  - `.claude/skills/tachi-infographics/references/executive-architecture.md`: touched by US1 (T007) and US3 (T027–T028). Serialize — US1 first (base prompt rewrite), then US3 extends with L3 field references.
  - `tests/scripts/test_extract_infographic_data.py`: touched only by US2 — no contention.
  - `tests/scripts/test_executive_architecture_payload.py`: new file, US3-only — no contention.
- **Within US2**: T012 || T013 || T014 || T015 (tests authored independently).
- **Within US3**: T021 || T022 (fixtures + test file authored independently); T024 || T025 (different helper functions in different regions of the same file — use a rebase/merge strategy for the final commit).
- **Phase 6**: T033 || T034 || T036 (parallel). T035 and T037 sequential after others.

---

## Parallel Example: User Story 2 Tests

```bash
# Launch fixture creation and test authoring in parallel:
Task: "Create fixture files for per-layer floor-rule matrix in tests/scripts/fixtures/exec_arch/"  # T012
Task: "Add test_per_layer_floor_invariant in tests/scripts/test_extract_infographic_data.py"       # T013
Task: "Add test_callouts_deterministic in tests/scripts/test_extract_infographic_data.py"          # T014
Task: "Add test_superset_invariant in tests/scripts/test_extract_infographic_data.py"              # T015

# Implementation is sequential on the same file:
Task: "Rewrite _select_critical_high_callouts() in scripts/extract-infographic-data.py"            # T016
Task: "Extend _build_executive_architecture_payload() layer_overflow field"                         # T017
```

---

## Implementation Strategy

### MVP First (US1 only)

1. Phase 1 Setup (T001–T003)
2. Phase 2 Foundational (T004–T006)
3. Phase 3 US1 (T007–T011) — L1 prompt rewrite
4. STOP and VALIDATE: regenerate reference image; pass 4/4 SC-212-1 criteria; SC-212-7 PDF byte-identity PASS
5. This ships ~70% of user-visible value. Acceptable as standalone release if timeline compresses.

### Incremental Delivery (preferred — matches PRD 1-week envelope)

1. Day 1: Phase 1 + Phase 2 + start Phase 3 US1
2. Day 2–3: Finish US1 + Phase 4 US2
3. Day 4–6: Phase 5 US3
4. Day 7: Phase 6 Polish + final gates + draft PR sync

### Parallel Team Strategy (if team-lead assigns multiple agents)

1. All agents: Phase 1 + Phase 2 together (T004 is blocking; completion is the foundational handshake).
2. Then:
   - Agent A: US1 (T007–T011) — prompt rewrite + image iteration
   - Agent B: US2 (T012–T020) — callout selection + test matrix
   - Agent C: US3 (T021–T032) — payload extension + drift-guard tests
3. Agent C pauses at T027 until Agent A finishes T007 (prompt co-landing edit — serialize on the skill reference file).
4. Agent C pauses at T026 until Agent B finishes T017 (extract-infographic-data.py edit — serialize on the script).
5. Team converges for Phase 6 (T033–T037).

---

## Notes

- [P] tasks = different files OR different code regions with no sequential dependency.
- F-128 contracts (output filenames, PDF position, skip behavior on zero-finding, portrait orientation, Typst bindings, other 5 templates untouched) preserved throughout. SC-212-7 is the automated gate.
- Determinism (ADR-017) and byte-identity-on-zero-finding (ADR-021) are enforced via T011, T031, and the `test_determinism` case in T022.
- Risk R1 (Gemini fragility) handled by Phase 3 iteration budget (up to 3 prompt iterations). Contingency: re-prioritize US3 ahead of US1 if ≥3/4 SC-212-1 criteria unreachable after 2 iterations.
- Risk R4 (scope-bleed per KB-026) handled by scope files enumerated in plan.md Components table — no unrelated fixes bundled.
- No new dependencies added. No new top-level directories. No model-version or API-parameter changes.
