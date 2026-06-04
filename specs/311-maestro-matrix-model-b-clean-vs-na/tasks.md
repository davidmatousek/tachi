---
description: "Task list for F-311 MAESTRO Matrix Model B (clean vs n/a)"
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-03
    status: APPROVED_WITH_CONCERNS
    notes: "14/14 FR + 5/5 SC map to tasks (no orphans, no scope creep); US1/US2/US3 covered with sound [USx] tags (4/4/2); all 7 Out-of-Scope boundaries held; MVP (Phase A+B) a coherent shippable slice; deliver-gate + both LOW spec advisories (US P1 label, two-token doc T007) captured. 0 BLOCKING / 0 CHANGES_REQUESTED / 1 MEDIUM (T008 populator fork — by-design open decision; PM endorses option a) / 2 LOW. No veto. Full: .aod/results/product-manager.md"
  architect_signoff:
    agent: architect
    date: 2026-06-03
    status: APPROVED
    notes: "All 5 plan-review carry-forwards verified landed + correctly targeted vs live code: HIGH-A→T009 (maestro_findings_by_layer group records L366-370+L383-388), MEDIUM-B→T008 (forces option-a present-row re-decision, D3-fenced, sound+budgeted), MEDIUM-A→T015 (regen-at-test-time via parse_maestro_data), LOW-A→T016 (5 paths reclassified, F-250 lock-step), LOW-B→T014 ({layer_bands_text} builder-keyed). Dependency ordering correct; ZERO same-file [P] collisions (315 lesson, programmatically verified); D3/D4/D5 guards + test-first classifier + determinism chain present; no task unimplementable. 0 BLOCKING / 2 LOW. No veto. Full: .aod/results/architect.md"
  techlead_signoff:
    agent: team-lead
    date: 2026-06-03
    status: APPROVED_WITH_CONCERNS
    notes: "Critical path realistic (~10-node S-sized spine T003→T004→[T009∥T012]→[T011,T014]→T015→T016→T017→T018→T020, one MEDIUM-contained T008 fork); split confirmed wrong (T015 needs all 4 surface tasks at once); PDF ∥ infographic one-wave verified disjoint (6 files pairwise non-overlapping, all [P] collision-free); T008 correctly un-split, option-(a) effort realistic; CALENDAR clean (no dates asserted); mmdc+Typst present; v4.40.0 tag-local gap captured at T001+T023; all 13 plan Carry-Forwards landed. 0 BLOCKING / 1 MEDIUM / 3 LOW. Full: .aod/results/team-lead.md"
---

# Tasks: MAESTRO Matrix Model B — Clean vs. N/A

**Input**: Design documents from `specs/311-maestro-matrix-model-b-clean-vs-na/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓, ADR-047 ✓
**Tests**: INCLUDED — this feature is consistency-test-centric (the cross-surface fixture is the regression anchor; test-first on the classifier).
**Stories**: US1 = tell clean from n/a on all 3 surfaces (PRD US-311.1, **#311**, P1); US2 = machine-discernible `coverage_state` (PRD US-311.2, P1); US3 = structural cross-surface consistency (PRD US-311.3, P2). Single feature — do not split (Team-Lead).

## Format: `[ID] [P?] [Story] Description`
- **[P]**: can run in parallel (different files, no incomplete-task dependency)
- **[USx]**: maps to the spec user story
- **[MANUAL-ONLY]**: cannot be automated (reason inline)

> **Build order (plan §Risks & Sequencing)**: Phase A (source contract) is a **hard prerequisite** for Phase B; within Phase B the PDF track ∥ the infographic track (disjoint files); Phase C after both render; Phase D (baseline regen) last.

---

## Phase 1: Setup (Shared)

**Purpose**: confirm toolchain + capture the pre-change baseline.

- [X] T001 Verify the build/test toolchain: a local Python (3.9+) with `pytest`/`pytest-timeout` (the CI job pins **Python 3.11**), and Typst + `mmdc` for PDF regeneration in Phase D. If `mmdc`/Typst are absent, note it in `specs/311-maestro-matrix-model-b-clean-vs-na/quickstart.md` (only T018–T020 need them). Confirm `git tag v4.40.0` presence; if absent, record the deliver-time fetch check (Team-Lead).
- [X] T002 [P] Record the starting baseline: run `python -m pytest tests/scripts/test_maestro_coverage_invariant.py -v` (expect green — all examples 7-row) and `python -m pytest tests/scripts/test_backward_compatibility.py -v` (expect green — 6 gated baselines byte-identical). Capture as the pre-change reference in `specs/311-maestro-matrix-model-b-clean-vs-na/test-results/`.

---

## Phase 2: Foundational (Blocking Prerequisites) — Plan Phase A (source contract)

**Purpose**: author the clean-vs-n/a token at the source and the shared classifier both extractors inherit. **Everything in Phase B depends on T004 (the classifier) and the authored-token contract.**

### Tests for the classifier (write FIRST — must FAIL before T004)

- [X] T003 [P] Author classifier tests in `tests/scripts/test_tachi_parsers.py` (create if absent) per `contracts/coverage-state-classifier.contract.md`: `(8,"Critical")→"findings"`; `(0,"Analyzed — no findings this scan")→"clean"`; `(0,"Not applicable — no components map to this layer")→"not_applicable"`; `(0,"")→"clean"` (backfill default); en-dash (U+2013) tolerance → `"not_applicable"`; and INV-3 ordinal-0: `SEVERITY_ORDINAL.get("<n/a token>",0)==0` and `...get("<clean token>",0)==0`. Confirm they FAIL pre-implementation.

### Implementation (source contract)

- [X] T004 Implement `classify_maestro_coverage_state(finding_count, highest_severity) -> "findings"|"clean"|"not_applicable"` in `scripts/tachi_parsers.py` — pure, side-effect-free, reads ONLY the two args; MUST NOT import/call `parse_component_layer_mapping` or read the Section-1 table (ADR-047 D2/D3; contract INV-1 + anti-requirements). (depends on T003)
- [X] T005 In `.claude/agents/tachi/orchestrator.md` (Section-6 directive ~L718), author the zero-finding cell from the component→layer set: ≥1 component maps → clean token `Analyzed — no findings this scan`; 0 components map → n/a token `Not applicable — no components map to this layer` (em-dash U+2014, no trailing period). Section-6 carried token is the **sole** applicability authority (FR-002 / ADR-047 D1).
- [X] T006 [P] Document the three-state Section-6 contract + the new n/a token in `.claude/skills/tachi-orchestration/references/output-schemas.md` §6 (~L229–242) (FR-001/FR-007).
- [X] T007 [P] Document the two MAESTRO zero-finding tokens (clean / n/a) as a MAESTRO-layer-view note in `.claude/skills/tachi-orchestration/references/coverage-matrix-model.md`, mapping them to the `---`/`n/a` STRIDE semantics (NFR Consumability; PM LOW advisory — named doc task).
- [X] T008 **[MEDIUM-B DECISION + impl]** `scripts/populate-maestro-coverage.py` is Section-6-only today (no Section-1 read; present rows kept verbatim; `tachi_parsers.py` has no shared component→layer parser). **DECISION (recommended → option a, ratify at review): add an examples-local Section-1 component→layer read + present-row re-decision** so unmapped zero-finding rows author the n/a token on regen — required for deterministic Phase-D example regen and idempotent `--check`. The Section-1 read MUST stay **examples-regeneration-only** and MUST NOT become a second *production* authority (production authoring is the orchestrator, T005 — respect ADR-047 D3). Reuse `classify_maestro_coverage_state` for the token decision. *(Fallback option b — descope populator to clean-only and author n/a example tables via the orchestrator/manual path — only if (a) proves out of budget; record which was chosen in the PR.)* (uses T004)

**Checkpoint**: classifier green; the Section-6 token contract is authored + documented; both extractors now have a stable token to inherit.

---

## Phase 3: User Stories 1 + 2 (the three rendering surfaces) — Plan Phase B (PDF ∥ infographic)

**Goal**: clean and n/a render as visibly + machine-discernibly distinct states on the PDF and the infographic, inheriting the Section-6 token (US1 = visible; US2 = `coverage_state` field). **Two disjoint tracks — run in parallel.**

**Independent Test**: regenerate `examples/microservices` outputs → L7=clean, L1/L3/L5/L6=n/a, L2/L4=findings on each surface, visibly distinct, with a `coverage_state` field in `report-data.typ` and `maestro-stack.json`.

### PDF surface track

- [X] T009 [P] [US1] [US2] In `scripts/extract-report-data.py`, call `classify_maestro_coverage_state` and thread `coverage_state` onto the **`maestro_findings_by_layer` GROUP records** (Architect HIGH-A: the only structure `main.typ` passes to the MAESTRO page — set it at the group pre-build ≈L366–370 + the fallback ≈L383–388 from the matching `parsed_layers` row's classified token); also add `coverage_state` to `maestro_layer_distribution`. Preserve the ordinal-0 tie-break (FR-012). (depends on T004)
- [X] T010 [US2] Extend `tests/scripts/test_extract_report_data.py` (`test_maestro_zero_finding_layer_is_retained_not_dropped`, ≈L384–409): on `examples/microservices`, assert the group record carries `coverage_state="clean"` for L7 and `"not_applicable"` for L1/L3/L5/L6; assert `compute_most_exposed_layer` never returns a zero-finding layer (FR-012). (depends on T009)
- [X] T011 [US1] In `templates/tachi/security-report/maestro-findings.typ` (~L147–155), branch the zero-finding row on `layer-group.at("coverage-state", default: "clean")`: clean → `Analyzed — no findings this scan.` (unchanged `brand-muted` italic); n/a → `Not applicable — no components map to this layer.` with a visually separable muted treatment (distinct fill/weight or an `(out of scope)` qualifier). (depends on T009)

### Infographic surface track (parallel with the PDF track)

- [X] T012 [P] [US1] [US2] In `scripts/extract-infographic-data.py`: call `classify_maestro_coverage_state` and emit `coverage_state` into `per_layer_summaries` (≈L1988–1996); ensure the backfill (≈L1958–1971) defaults absent (table-less) layers to `clean` AND preserves a **present** `not_applicable` token verbatim through the merge (Architect MEDIUM-3 / D4); **FENCE** `parse_component_layer_mapping()` to heatmap-only — it MUST NOT drive the `maestro-stack` state (ADR-047 D3); preserve ordinal-0 (FR-012). (depends on T004)
- [X] T013 [US2] Extend `tests/scripts/test_extract_infographic_data.py`: on `examples/microservices`, assert per-layer `coverage_state` (L7=clean; L1/L3/L5/L6=not_applicable; L2/L4=findings); assert backfill-survival (a present n/a token is not overwritten to empty/clean); regenerate the golden `tests/scripts/fixtures/golden/maestro-stack.json` (now carries `coverage_state`) and confirm `maestro-heatmap.json` is UNCHANGED. (depends on T012)
- [X] T014 [US1] In `templates/tachi/infographics/infographic-maestro-stack.md`, add the documented **third band state in the `{layer_bands_text}` builder keyed on `coverage_state`** (Architect LOW-B — not only static prose): clean = muted band + dash (—) (unchanged); n/a = distinct muted treatment + **"N/A"** text label. Update the Empty-Layers prose (~L124–130), the Gemini prompt (~L186–198), and extend the Accessibility section (~L216–223) to name the n/a label alongside the clean dash. (depends on T012)

**Checkpoint**: all three surfaces emit + render clean/n/a/findings for `microservices`.

---

## Phase 4: User Story 3 (structural cross-surface consistency) — Plan Phase C (fixture + CI)

**Goal**: the three surfaces provably agree on every layer's state, gated in CI; divergence fails naming the layer.

**Independent Test**: run the consistency test on `microservices` → green; force one surface to disagree → fails naming L7.

- [X] T015 [US3] Add the cross-surface consistency test (new `tests/scripts/test_maestro_cross_surface_consistency.py` or a case in `test_maestro_coverage_invariant.py`): for `examples/microservices`, assert `state(threats.md Section-6, via classify_maestro_coverage_state)` == `state(report-data.typ coverage_state)` == `state(maestro-stack.json coverage_state)` for all 7 layers, expected L7=clean / L1·L3·L5·L6=not_applicable / L2·L4=findings. **The PDF state is obtained by invoking `extract-report-data.py` / `parse_maestro_data` on the example at test time** (render IR is not committed — Architect MEDIUM-A; mirror the infographic's `_maestro_stack_template_data` harness). Add a negative test: force one surface's L7 to `not_applicable` (or re-route the stack to `component_layer_map`) → assert failure names `L7`. (depends on T009, T011, T012, T014)
- [X] T016 [US3] Wire T015 into `.github/workflows/tachi-maestro-coverage.yml` in **F-250 lock-step** (update `on.pull_request.paths` AND the pytest invocation in the SAME commit): add the consistency module to the invocation; **reclassify `scripts/extract-report-data.py`, `scripts/extract-infographic-data.py`, `templates/tachi/security-report/maestro-findings.typ`, `templates/tachi/infographics/infographic-maestro-stack.md`, `.claude/agents/tachi/orchestrator.md` as regression-necessary** (Architect LOW-A — the consistency test re-extracts render IR, so these can change a test outcome; remove the stale "cannot change a committed example" rationale). Do NOT touch `tachi-pytest.yml`. (depends on T015)

**Checkpoint**: cross-surface consistency gated; SC-001/SC-002 satisfied on the committed fixture.

---

## Phase 5: Polish & Cross-Cutting — Plan Phase D (baseline regen) + delivery

- [ ] T017 Drift audit (Decision F): for each candidate example with ≥1 genuine n/a layer — gated `microservices`, `web-app`, `free-text-microservice`, `mermaid-agentic-app`, `ascii-web-api`, `maestro-reference`; non-gated `mobile-banking-app/sample-report`, `agentic-app` — `git`/`cmp` compare current committed `threats.md`/PDF vs what the new pipeline produces; classify real clean-vs-n/a churn vs no-drift; **DROP no-drift targets**; enumerate the final churn set in the PR body.
- [ ] T018 Baseline regen (confirmed-churn targets only): run `python scripts/populate-maestro-coverage.py <target>/threats.md` (heading-normalize FIRST — Architect LOW-2 — so no n/a-bearing example parses to zero layers), then regenerate `report-data.typ` + the PDF under `SOURCE_DATE_EPOCH=1700000000`. Re-freeze the affected gated `.pdf.baseline` files deliberately. (depends on T015, T017)
- [ ] T019 [MANUAL-ONLY: clean-vs-n/a is a deliberate render change with no pre-existing baseline] Diff each regenerated `threats.md`/PDF vs prior — confirm the change is **only** the clean→n/a annotation split (+ any pagination reflow), no unrelated/non-MAESTRO or scoring drift; flag (don't silently absorb) anything else. (depends on T018)
- [ ] T020 Verify the 6 byte-gated baselines are byte-identical AFTER intentional re-freeze: `python -m pytest tests/scripts/test_backward_compatibility.py -v` → green; confirm `BASELINE_EXAMPLES` is the same set (not expanded). (depends on T018)
- [ ] T021 [P] Add a `CHANGELOG.md` `feat(311)` entry: MAESTRO Model B clean-vs-n/a across all three surfaces (threats.md token, PDF n/a state, infographic n/a band) + cross-surface CI gate + ADR-047.
- [ ] T022 SC-003 no-schema-drift: `git diff --stat -- '**/*.sarif' schemas/` shows zero changes; run `/aod.analyze` (spec ↔ plan ↔ tasks) → 0 inconsistencies; resolve any drift.
- [ ] T023 Run `specs/311-maestro-matrix-model-b-clean-vs-na/quickstart.md` end-to-end (SC-001…SC-005); DoD checklist + **deliver-gate note for `/aod.deliver`**: PR squash title MUST be `feat(311):` (release-please); confirm `git tag v4.40.0` present locally before deliver; verify the squash-merge yields a release-please PR (deliver-release gate).

---

## Dependencies & Execution Order

### Phase dependencies
- **Setup (P1)**: no dependencies.
- **Foundational (P2 / Plan Phase A)**: T003 → T004; T005/T006/T007 independent `[P]`; T008 uses T004. **T004 blocks all of Phase B.**
- **US1+US2 (P3 / Plan Phase B)**: PDF track (T009 → T010, T011) ∥ infographic track (T012 → T013, T014) — disjoint files; both depend on T004.
- **US3 (P4 / Plan Phase C)**: T015 (needs all four surface tasks) → T016.
- **Polish (P5 / Plan Phase D)**: T017 → T018 → (T019 ∥ T020); T021/T022/T023 after.

### Within Phase B
- PDF: T009 → T010 (test) ∥ T011 (Typst). Infographic: T012 → T013 (test) ∥ T014 (template).
- PDF track ∥ infographic track (different files; the architect's 315 same-file `[P]` lesson honored — T009 and T012 touch different scripts).

### Parallel opportunities
- Foundational: T003 ∥ T005 ∥ T006 ∥ T007 (different files); T004 then T008.
- Phase B: PDF track ∥ infographic track (whole tracks); T009 ∥ T012.
- Setup: T002 `[P]`.

---

## Parallel Example: Phase B one-wave execution

```bash
# After Phase A (T004 landed). Wave B — both surface tracks at once (disjoint files):
# PDF track:
Task: "T009 extract-report-data.py: coverage_state onto maestro_findings_by_layer groups (HIGH-A)"
Task: "T011 maestro-findings.typ: branch zero-finding row on coverage-state (after T009)"
# Infographic track:
Task: "T012 extract-infographic-data.py: coverage_state + backfill-survival + D3 fence"
Task: "T014 infographic-maestro-stack.md: third band state in {layer_bands_text} (after T012)"
```

---

## Implementation Strategy

### MVP First (US1 + US2 via the three surfaces)
1. Setup (T001–T002) → Foundational source contract (T003–T008) → Phase B both tracks (T009–T014) → STOP & VALIDATE: all three surfaces show L7=clean, L1/L3/L5/L6=n/a for `microservices`. This is the user-visible + machine-discernible win.

### Incremental
2. Add US3 (T015–T016): the cross-surface consistency gate — the durability guarantee.
3. Polish (T017–T023): drift-audit → deterministic baseline regen → byte-gate → CHANGELOG → analyze → deliver-gate.

### Notes
- `[P]` = different files, no incomplete-task dependency. Commit after each task or logical group.
- Test-first: T003 (classifier) FAILS before T004; T010/T013 assert before/with the extractor edits; T015 is the cross-surface regression anchor.
- ADR-047 D3 (single authority / heatmap fence) is the load-bearing invariant — T012 must not route `component_layer_map` into the stack; T015 negative test guards it.
- Toolchain: T018–T020 (PDF regen) need Typst + mmdc; all other tasks do not.
- The MEDIUM-B populator decision (T008) is the one real scope fork — ratify option (a) vs (b) at triple-review before build.
