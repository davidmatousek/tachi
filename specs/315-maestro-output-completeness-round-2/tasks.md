---
description: "Task list for F-315 MAESTRO Output Completeness (Round 2)"
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-03
    status: APPROVED_WITH_CONCERNS
    notes: "FR 10/10 + SC 7/7 mapped to tasks, no orphans; no scope creep; zero #311/Model-B re-entry; MVP (US1) independently shippable; delivery gate (Closes #312 #313 + merge #314 + deliver-release) captured in T020; [US1]/[US2]→#312/#313 traceability clear. 0 BLOCKING / 0 HIGH / 0 MEDIUM / 2 LOW (both optional: FR-010 verified via SC-006/T019 with no dedicated affirmative task; T008 either/or → default documentation branch). Full review .aod/results/product-manager.md."
  architect_signoff:
    agent: architect
    date: 2026-06-03
    status: APPROVED_WITH_CONCERNS
    notes: "All 5 plan-review concerns confirmed actionable as tasks (MEDIUM-2→T003+T004, MEDIUM-1 drift-drop→T013, MEDIUM-1 CI paths→T010, LOW-4 backfill-locality→T005, LOW-5→T014, +LOW-8→T008). Every path/line-num verified vs live repo; T002 baseline confirmed green. 0 BLOCKING / 0 HIGH / 1 MEDIUM / 4 LOW. MEDIUM-1 (T008 `[P]` was a hidden same-file conflict with T005 — both edit the same maestro-stack template_data block) FOLDED: removed `[P]`, T008 emit-branch now depends on T005. Dependency graph otherwise correct. Full review .aod/results/architect.md."
  techlead_signoff:
    agent: team-lead
    date: 2026-06-03
    status: APPROVED
    notes: "Critical path T013(drift-audit)→T014(PDF regen, Typst+mmdc-gated)→T016(gated byte-check); US1 chain T003→T004→T005→T006→T009 correct & minimal — both verified. CALENDAR PASS (no concrete dates, no weekend-placement defect, none asserted by review). Granularity right-sized (T013/T014 correctly NOT split); US1∥US2 one-wave realistic (disjoint files verified); capacity clear (only release PR #314 + draft #316 open); mmdc+typst present locally; zero plan carry-forwards dropped. 0 BLOCKING / 0 HIGH / 0 MEDIUM / 3 LOW / 4 NITS. LOW (T001 Python-3.11-vs-local-3.9 wording) FOLDED — clarified local 3.9+ for tests, CI pins 3.11. Full review .aod/results/team-lead.md."
---

# Tasks: MAESTRO Output Completeness (Round 2) — Infographic + CI Durability

**Input**: Design documents from `specs/315-maestro-output-completeness-round-2/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓
**Tests**: INCLUDED — this feature is test-centric (US1 locks new payload keys via fixtures; US2 *is* CI gating + byte-gate verification).
**Stories**: US1 = maestro-stack infographic completeness (PRD US-2 / **#312**, P1); US2 = CI durability + non-gated PDF refresh (PRD US-3 / **#313**, P2). PRD/GitHub **US-1 Model B (#311) is carved out** — not here.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: can run in parallel (different files, no incomplete-task dependency)
- **[USx]**: maps to the spec user story
- **[MANUAL-ONLY]**: cannot be automated (reason inline)

---

## Phase 1: Setup (Shared)

**Purpose**: confirm toolchain + starting state before edits.

- [ ] T001 Verify the build/test toolchain is available: a local Python (3.9+) with `pytest`/`pytest-timeout` for running tests (the new CI job pins **Python 3.11** to match repo CI), and Typst + `mmdc` for PDF regeneration in US2. If `mmdc`/Typst are absent, note it in `specs/315-maestro-output-completeness-round-2/quickstart.md` (PDF regen tasks T014–T016 require them; the rest do not).
- [ ] T002 [P] Record the starting baseline: run `python -m pytest tests/scripts/test_maestro_coverage_invariant.py -v` (expect green — all examples 7-row) and `python -m pytest tests/scripts/test_backward_compatibility.py -v` (expect green — 6 gated baselines byte-identical). Capture output as the pre-change reference.

---

## Phase 2: Foundational (Blocking Prerequisites)

**None.** US1 and US2 are independent (disjoint file sets) and form one parallel wave. No foundational work blocks either story — proceed directly to Phase 3 / Phase 4 (which may run concurrently).

**Checkpoint**: both stories may begin immediately.

---

## Phase 3: User Story 1 — maestro-stack infographic completeness (#312) (Priority: P1) MVP

**Goal**: the `maestro-stack` infographic spec data presents all 7 MAESTRO layers (zero-finding muted) with deterministic, code-computed `empty_layers`/`layers_with_findings`/`layer_count`.

**Independent Test**: generate maestro-stack spec data for a fixture with ≥1 empty layer → all 7 layers present, correct counts, byte-identical on repeat; `maestro-heatmap` golden unchanged.

### Tests for User Story 1 (write FIRST — must FAIL before T006)

- [ ] T003 [P] [US1] Author a NEW partial-MAESTRO fixture at `tests/scripts/fixtures/exec_arch/maestro_partial/` (architecture input + a `threats.md` whose "Risk by MAESTRO Layer" table has findings in ~3 of 7 layers) — needed because the existing `agentic_app` golden source is table-less (all-empty only). [Architect MEDIUM-2]
- [ ] T004 [US1] Extend `tests/scripts/test_extract_infographic_data.py`: assert the `maestro-stack` `template_data` contains `empty_layers`, `layers_with_findings`, `layer_count`; assert `layers_with_findings + empty_layers == layer_count == 7`; assert the **mixed** counts (`layers_with_findings=3, empty_layers=4`) against the T003 partial fixture AND the all-empty case against the existing golden; assert byte-identity across two runs. Confirm these FAIL pre-implementation. (depends on T003)

### Implementation for User Story 1

- [ ] T005 [US1] In `scripts/extract-infographic-data.py`, the `maestro-stack` `template_data` block (≈L1937–1965): backfill the distribution to all 7 `MAESTRO_LAYERS` (missing → `finding_count: 0`) and add `layers_with_findings = count(>0)`, `empty_layers = 7 − that`, `layer_count = 7`. **Local to the maestro-stack block ONLY — do NOT touch shared `extract_maestro_data`** (protects the heatmap payload / FR-004). [Architect LOW-4] (depends on T004)
- [ ] T006 [US1] Regenerate the golden fixture `tests/scripts/fixtures/golden/maestro-stack.json` (now carries the 3 keys; all-empty case). Confirm `tests/scripts/fixtures/golden/maestro-heatmap.json` is UNCHANGED. (depends on T005)
- [ ] T007 [P] [US1] Add a one-line directive in `.claude/agents/tachi/threat-infographic.md`: the maestro-stack `{empty_layers}`/`{layers_with_findings}`/`{layer_count}` placeholders MUST be taken from the emitted JSON, not recomputed.
- [ ] T008 [US1] (Optional, Architect LOW-8) Either emit `most_exposed_count` in the same `template_data` block for full sidebar determinism — **depends on T005 (same block; NOT parallel with it)** — OR add a code comment that `{most_exposed_count}` is intentionally left agent-rendered and outside FR-002's enumerated set (this branch is independent). Default to the documentation branch if undecided.
- [ ] T009 [US1] Run `python -m pytest tests/scripts/test_extract_infographic_data.py -v` → green; verify determinism (extract twice → byte-identical JSON) and that the `maestro-heatmap` golden/output is unchanged (FR-004). (depends on T005, T006)

**Checkpoint**: US1 fully functional and independently testable.

---

## Phase 4: User Story 2 — CI durability + non-gated PDF refresh (#313) (Priority: P2)

**Goal**: a dedicated CI job fails (naming the missing layer) on any <7-row MAESTRO matrix regression; drifted non-gated example PDFs refreshed deterministically; 6 gated baselines byte-identical.

**Independent Test**: force a <7-row matrix → dedicated job fails naming the layer; regenerate non-gated PDFs → only MAESTRO churn; gated baselines stay byte-identical.

### CI gate sub-stream

- [ ] T010 [P] [US2] Create `.github/workflows/tachi-maestro-coverage.yml` — a dedicated `ubuntu-latest` / Python 3.11 job (`pip install pytest pytest-timeout`; `python -m pytest tests/scripts/test_maestro_coverage_invariant.py -v`), modeled on `tachi-mmdc-preflight.yml`. `on.pull_request.paths` per `contracts/tachi-maestro-coverage-ci.contract.md`: regression-necessary tier (`test_maestro_coverage_invariant.py`, `examples/**/threats.md`, `scripts/tachi_parsers.py`, `scripts/populate-maestro-coverage.py`, the workflow file) + optional defense-in-depth tier. Do NOT touch `tachi-pytest.yml`. Keep `paths:` ⇄ invocation in lock-step.
- [ ] T011 [P] [US2] Remove the "intentionally NOT wired into CI" docstring note (≈L25–27) from `tests/scripts/test_maestro_coverage_invariant.py`.
- [ ] T012 [US2] Verify: invariant test green locally; negative test — in a scratch copy of an example `threats.md`, delete one canonical layer row → re-run → fails naming the missing layer ID; discard scratch. Confirm an unrelated-file change does not trigger the job and leaves `tachi-pytest.yml` untouched. (depends on T010, T011)

### Non-gated PDF refresh sub-stream

- [ ] T013 [US2] Drift audit: for each non-gated example PDF (`agentic-app/sample-report`, `consumer-agent-app/sample-report`, `predictive-ml-app/sample-report`, `mobile-banking-app/sample-report`, `maestro-reference` loose `.pdf`), `cmp`/`git` compare PDF vs its `.baseline`/prior content and classify drift (MAESTRO row/order vs none vs table-less). Finalize the **confirmed-drift** refresh set; DROP no-drift targets (`mobile-banking-app` is byte-identical today — verify) and the two table-less reports. Record findings in the PR. [Architect MEDIUM-1]
- [ ] T014 [US2] For each confirmed-drift target only: run `python scripts/populate-maestro-coverage.py <target>/sample-report/threats.md` (idempotent normalize — for agentic-app use the **sample-report** `threats.md`, not the top-level file [LOW-5]), then regenerate the PDF under `SOURCE_DATE_EPOCH=1700000000`. Leave the gated `maestro-reference/.baseline` untouched (refresh only its loose `.pdf`). (depends on T013)
- [ ] T015 [US2] [MANUAL-ONLY: non-gated PDFs have no automated byte-gate] Diff each regenerated PDF/baseline vs prior — confirm ONLY MAESTRO row/order churn, no unrelated binary drift. (depends on T014)
- [ ] T016 [US2] Verify the 6 byte-gated baselines remain byte-identical: `python -m pytest tests/scripts/test_backward_compatibility.py -v` → green; confirm the gated set in `BASELINE_EXAMPLES` is unchanged (not expanded — Q-D1). (depends on T014)

**Checkpoint**: US1 and US2 both independently functional.

---

## Phase 5: Polish & Cross-Cutting

- [ ] T017 [P] Add a `CHANGELOG.md` `feat(315)` entry (US-2 maestro-stack all-7 + deterministic counts; US-3 dedicated MAESTRO CI gate + non-gated PDF refresh; note US-1 Model B carved to #311).
- [ ] T018 Run `/aod.analyze` cross-artifact consistency check (spec ↔ plan ↔ tasks); resolve any drift.
- [ ] T019 Run `specs/315-maestro-output-completeness-round-2/quickstart.md` end-to-end validation (both stories' verification steps; SC-001…SC-007).
- [ ] T020 DoD checklist + **delivery gate note for `/aod.deliver`**: the delivering PR MUST `Closes #312 #313` (umbrella #315 closes when both land); **merge release PR #314 (v4.39.0) before/alongside**; verify the F-315 squash-merge (`feat(315):`) yields a release-please PR (deliver-release gate). [PM LOW-2]

---

## Dependencies & Execution Order

### Phase dependencies
- **Setup (P1)**: no dependencies.
- **Foundational (P2)**: none — both stories unblocked immediately.
- **US1 (P3)** and **US2 (P4)**: independent — **one parallel wave** (disjoint files; neither depends on the other nor on #311).
- **Polish (P5)**: after both stories complete.

### Within US1
- T003 → T004 (test needs fixture) → T005 (impl after failing test) → T006 (regen golden) → T009 (verify). T007 is independent `[P]`. T008's *emit* branch depends on T005 (same `template_data` block — not parallel with T005); its *documentation* branch is independent.

### Within US2
- CI sub-stream: T010 ∥ T011 → T012 (verify).
- PDF sub-stream: T013 (audit) → T014 (regen) → T015 (manual diff) ∥ T016 (gated byte-check).
- CI sub-stream ∥ PDF sub-stream (different files).

### Parallel opportunities
- **US1 ∥ US2** (whole stories).
- US1: T003 ∥ T007 (T008 only if its documentation branch); US2: T010 ∥ T011 ∥ T013.
- Setup: T002 `[P]`.

---

## Parallel Example: one-wave execution

```bash
# Wave A — both stories at once (disjoint files):
# US1 track:
Task: "T003 author partial-MAESTRO fixture"
Task: "T007 add threat-infographic.md directive"
# US2 track:
Task: "T010 create tachi-maestro-coverage.yml dedicated CI job"
Task: "T011 remove 'not wired' docstring from invariant test"
Task: "T013 drift-audit non-gated example PDFs"
```

---

## Implementation Strategy

### MVP First (US1 only)
1. Setup (T001–T002) → US1 (T003–T009) → STOP & VALIDATE (all-7 infographic with correct deterministic counts; heatmap unchanged). The visible output-fidelity win ships independently.

### Incremental
2. Add US2 (T010–T016): CI gate (T010–T012) + PDF refresh (T013–T016) — independently testable, no US1 coupling.
3. Polish (T017–T020) → `/aod.deliver`.

### Notes
- `[P]` = different files, no incomplete-task dependency. Commit after each task or logical group.
- US1/US2 are independently completable and testable — neither requires the other nor US-1/#311.
- Tests (T003–T004, T012, T016) gate the implementation; verify failing-before-passing where applicable.
- Toolchain: T014–T016 (PDF regen) need Typst + mmdc; all other tasks do not.
