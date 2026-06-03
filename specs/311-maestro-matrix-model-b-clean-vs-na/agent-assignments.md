---
description: "Agent assignments for F-311 MAESTRO Matrix Model B (clean vs n/a)"
feature: "311-maestro-matrix-model-b-clean-vs-na"
tasks_signoff: APPROVED_WITH_CONCERNS  # PM + Architect + Team-Lead (2026-06-03)
generated_by: team-lead
date: 2026-06-03
agent_registry: .claude/agents/_README.md  # all subagent_type values validated against this
waves: 5
---

# Agent Assignments: MAESTRO Matrix Model B — Clean vs. N/A

**Input**: `tasks.md` (T001–T023, 5 phases) · `plan.md` (build order: Phase A source-contract → B PDF ∥ infographic → C fixture+CI → D baseline regen)
**Feasibility**: **APPROVED_WITH_CONCERNS** (tasks triple-signed 2026-06-03). 0 BLOCKING / 1 MEDIUM (T008 populator fork — option (a) endorsed) / multiple LOW. Critical path is a ~10-node S-sized spine `T003→T004→[T009∥T012]→[T011,T014]→T015→T016→T017→T018→T020`.

**Agent registry**: every `subagent_type` below is an exact name from `.claude/agents/_README.md`. Five agents are used: `senior-backend-engineer`, `tester`, `devops`, `code-reviewer`, `security-analyst`. No invented labels.

**Assignment rules applied** (from the registry + fallbacks):
- Python extractors / classifier / populator / pytest tests, Typst template, Gemini-prompt + reference markdown, orchestrator directive → `senior-backend-engineer` (markdown/docs/non-code edits also fall here per fallback).
- CI workflow YAML → `devops`.
- Cross-surface consistency proof + quickstart end-to-end + DoD/acceptance gates → `tester`.
- HIGH-A render-IR wiring review + D3-fence diff review + MANUAL-ONLY annotation-only diff → `code-reviewer` (advisory, runs alongside the implementing agent, not in place of it).
- D3 single-authority fence is a security-relevant structural invariant → `security-analyst` advisory check at the Wave-2 gate.

---

## 1. Agent Assignment Matrix

| Task | Story | [P] | Primary agent (`subagent_type`) | Supporting | One-line rationale |
|------|-------|-----|-------------------------------|------------|--------------------|
| **T001** | — | | `tester` | — | Toolchain/`mmdc`/Typst + `git tag v4.40.0` presence is a verification/acceptance check, not CI authoring; records gaps in quickstart. |
| **T002** | — | [P] | `tester` | — | Capture pre-change baseline (`pytest` invariant + backward-compat green) as the regression reference — pure validation. |
| **T003** | US1/US2 | [P] | `senior-backend-engineer` | — | Author the test-first classifier pytest cases (`test_tachi_parsers.py`) per contract; must FAIL pre-impl. |
| **T004** | US1/US2 | | `senior-backend-engineer` | `code-reviewer` | Implement the pure `classify_maestro_coverage_state` helper (no Section-1 read) — the source contract; reviewer confirms INV-1 anti-requirement (no `parse_component_layer_mapping` import). |
| **T005** | US2 | [P] | `senior-backend-engineer` | — | Author the Section-6 clean/n/a token directive in the orchestrator agent markdown (sole applicability authority, ADR-047 D1). |
| **T006** | — | [P] | `senior-backend-engineer` | — | Document the three-state Section-6 contract + n/a token in `output-schemas.md` reference (markdown). |
| **T007** | — | [P] | `senior-backend-engineer` | — | Document the two zero-finding tokens in `coverage-matrix-model.md` (PM LOW advisory — named doc task; markdown). |
| **T008** | — | | `senior-backend-engineer` | `code-reviewer` | MEDIUM-B fork: implement option (a) examples-local Section-1 read + present-row re-decision in `populate-maestro-coverage.py`; reviewer guards the D3 "examples-regeneration-only, not a 2nd production authority" boundary. |
| **T009** | US1/US2 | [P] | `senior-backend-engineer` | `code-reviewer` | **HIGH-A wiring**: thread `coverage_state` onto the `maestro_findings_by_layer` GROUP records (≈L366–370 + fallback L383–388) — the only structure `main.typ` passes; reviewer verifies it rides the group, not `maestro_layer_distribution` alone. |
| **T010** | US2 | | `senior-backend-engineer` | — | Extend `test_extract_report_data.py` — assert group-record `coverage_state` + `compute_most_exposed_layer` never returns a zero-finding layer (FR-012). |
| **T011** | US1 | | `senior-backend-engineer` | — | Branch the zero-finding row in `maestro-findings.typ` on `coverage-state` (clean vs n/a visual treatment) — Typst template. |
| **T012** | US1/US2 | [P] | `senior-backend-engineer` | `code-reviewer` | **D3-fence edit**: emit `coverage_state` in `extract-infographic-data.py`, preserve present n/a through backfill (D4), FENCE `parse_component_layer_mapping()` to heatmap-only; reviewer diff-checks the fence (component_layer_map must NOT drive the stack). |
| **T013** | US2 | | `senior-backend-engineer` | — | Extend `test_extract_infographic_data.py` + regenerate golden `maestro-stack.json`; assert backfill-survival and `maestro-heatmap.json` UNCHANGED. |
| **T014** | US1 | | `senior-backend-engineer` | — | Add the third band state in the `{layer_bands_text}` builder keyed on `coverage_state` (LOW-B) + Gemini prompt + Accessibility — infographic template markdown. |
| **T015** | US3 | | `tester` | `senior-backend-engineer` | Cross-surface consistency test (the regression anchor): asserts the three surfaces agree on all 7 layers, PDF state regenerated at test time (MEDIUM-A) + negative test names L7; SBE supports the `parse_maestro_data` harness wiring. |
| **T016** | US3 | | `devops` | — | Wire T015 into `.github/workflows/tachi-maestro-coverage.yml` in F-250 lock-step (`paths:` + invocation, same commit) + reclassify 5 regression-necessary paths — CI/CD authority. |
| **T017** | — | | `senior-backend-engineer` | — | Drift audit (Decision F): `git`/`cmp` each candidate example, classify real churn vs no-drift, DROP no-drift, enumerate the final set in the PR body. |
| **T018** | — | | `senior-backend-engineer` | `devops` | Deterministic baseline regen on confirmed-churn targets (`populate-...py` heading-normalize first, then `report-data.typ` + PDF under `SOURCE_DATE_EPOCH`); devops advises on Typst/`mmdc` toolchain reproducibility. |
| **T019** | — | | `code-reviewer` | — | **[MANUAL-ONLY]** diff each regenerated `threats.md`/PDF — confirm ONLY the clean→n/a annotation split (+ pagination), flag any unrelated/scoring drift. Diff-review is exactly code-reviewer's lane. |
| **T020** | — | | `tester` | — | Byte-gate: `test_backward_compatibility.py` green after intentional re-freeze; confirm `BASELINE_EXAMPLES` set unchanged — acceptance gate. |
| **T021** | — | [P] | `senior-backend-engineer` | — | Add the `CHANGELOG.md` `feat(311)` entry (markdown). |
| **T022** | — | | `tester` | — | SC-003 no-schema-drift: `git diff --stat` on `*.sarif`/`schemas/` shows zero; run `/aod.analyze` → 0 inconsistencies — cross-artifact validation. |
| **T023** | — | | `tester` | — | Run `quickstart.md` end-to-end (SC-001…SC-005) + DoD checklist + deliver-gate note (`feat(311):` squash, `v4.40.0` tag, release-please verify). |

**Agent load summary**: `senior-backend-engineer` 14 primary (T003, T004, T005, T006, T007, T008, T009, T010, T011, T012, T013, T014, T017, T018, T021) — heavily front-loaded into Phases A/B but spread across waves so no single wave exceeds ~4 concurrent SBE tasks; `tester` 6 (T001, T002, T015, T020, T022, T023); `devops` 1 primary (T016) + 1 support (T018); `code-reviewer` 1 primary (T019) + 4 advisory; `security-analyst` advisory only (Wave-2 fence gate). No agent is >80% loaded within any single wave (the spine serializes SBE work; [P] siblings are disjoint-file).

---

## 2. Parallel Execution Waves

Honors the dependency graph in `tasks.md` §Dependencies and the **hard A→B barrier** (T004 blocks all of Phase B) and the **disjoint-file ∥ within Phase B** (PDF track files never overlap infographic track files — 315 same-file `[P]` lesson programmatically verified clean).

### Wave 0 — Setup (T001–T002) · size **S**
| Task | Agent | Parallel? |
|------|-------|-----------|
| T001 toolchain + `v4.40.0` tag check | `tester` | T002 [P] |
| T002 capture pre-change baseline | `tester` | [P] with T001 |

No dependencies. Both run together (same agent, two independent verification streams).

### Wave 1 — Foundational source contract (Plan Phase A) · size **S→M**
**Sub-wave 1a** (test-first + the doc/directive fan-out, all disjoint files, [P]):
| Task | Agent | Note |
|------|-------|------|
| T003 classifier tests (FAIL first) | `senior-backend-engineer` | blocks T004 |
| T005 orchestrator Section-6 directive | `senior-backend-engineer` | [P] — different file |
| T006 `output-schemas.md` §6 doc | `senior-backend-engineer` | [P] — different file |
| T007 `coverage-matrix-model.md` doc | `senior-backend-engineer` | [P] — different file |

**Sub-wave 1b** (after T003 red, then T004 green):
| Task | Agent | Note |
|------|-------|------|
| T004 implement `classify_maestro_coverage_state` | `senior-backend-engineer` (+ `code-reviewer`) | **A→B barrier — blocks ALL of Phase B** |
| T008 populator option-(a) impl | `senior-backend-engineer` (+ `code-reviewer`) | uses T004; runs after T004, parallel-safe vs nothing else in B yet |

> **Hard barrier**: Phase B may NOT start until T004 lands green. T008 also depends on T004 but is examples-regen scope; it can overlap the start of Wave 2 (different file: `populate-maestro-coverage.py`).

### Wave 2 — The two surface tracks IN PARALLEL (Plan Phase B) · size **M**
Two disjoint tracks; whole tracks run simultaneously (no cross-track file overlap).

| PDF track (`senior-backend-engineer`) | Infographic track (`senior-backend-engineer`) |
|---|---|
| **T009** `extract-report-data.py` — `coverage_state` on group records (+ `code-reviewer` HIGH-A) | **T012** `extract-infographic-data.py` — `coverage_state` + D3 fence + D4 survival (+ `code-reviewer` fence) |
| then **T010** test (∥ T011) | then **T013** test (∥ T014) |
| then **T011** `maestro-findings.typ` branch (∥ T010) | then **T014** `infographic-maestro-stack.md` band (∥ T013) |

Intra-track: T009 → {T010 ∥ T011}; T012 → {T013 ∥ T014}. Cross-track: T009 ∥ T012 (different scripts). Up to 4 disjoint-file tasks concurrent at peak.

### Wave 3 — Cross-surface consistency (Plan Phase C) · size **S→M**
| Task | Agent | Note |
|------|-------|------|
| T015 cross-surface consistency test (PDF state regen at test time, MEDIUM-A) | `tester` (+ `senior-backend-engineer`) | depends on **all four** surface tasks T009/T011/T012/T014 |
| → T016 wire into `tachi-maestro-coverage.yml` (F-250 lock-step) | `devops` | depends on T015 |

T015 is the sequencing pinch-point — it needs every Phase-B surface complete (split confirmed wrong by Team-Lead).

### Wave 4 — Polish / baseline regen + delivery (Plan Phase D) · size **M**
| Task | Agent | Order |
|------|-------|-------|
| T017 drift audit (DROP no-drift) | `senior-backend-engineer` | first |
| → T018 deterministic baseline regen | `senior-backend-engineer` (+ `devops`) | after T017 (needs Typst+`mmdc`) |
| → T019 [MANUAL-ONLY] annotation-only diff | `code-reviewer` | after T018, **∥ T020** |
| → T020 byte-gate `test_backward_compatibility.py` | `tester` | after T018, **∥ T019** |
| T021 `CHANGELOG.md` feat(311) | `senior-backend-engineer` | [P] — independent |
| T022 SC-003 no-drift + `/aod.analyze` | `tester` | after regen settles |
| T023 quickstart end-to-end + deliver-gate | `tester` | last (DoD) |

Within Wave 4: T017 → T018 → (T019 ∥ T020); T021 may run [P] any time; T022 then T023 close out.

---

## 3. Quality Gates (between waves)

| Gate | After | Owner | Pass condition | On fail |
|------|-------|-------|----------------|---------|
| **G0 — Toolchain/Baseline gate** | Wave 0 | `tester` | Python+pytest present; `mmdc`/Typst presence recorded (only T018–T020 need them); pre-change `pytest` invariant + backward-compat both GREEN; `v4.40.0` tag noted | Record toolchain gap in quickstart; if baseline is red, stop — the repo is not at a clean start. |
| **G1 — Classifier-green gate** | Wave 1 | `senior-backend-engineer` + `code-reviewer` | T003 went RED→GREEN on T004; `classify_maestro_coverage_state` is pure (no `parse_component_layer_mapping`, no Section-1 read — INV-1); Section-6 token authored + documented (T005–T007) | Do NOT enter Phase B. The barrier holds: both extractors must have a stable token to inherit. |
| **G2 — Surface-render gate + D3 fence** | Wave 2 | `code-reviewer` + `security-analyst` (advisory) | All three surfaces emit + render clean/n/a/findings for `microservices`; `coverage_state` present on PDF group records (HIGH-A) and infographic `per_layer_summaries`; **D3 fence verified** — `component_layer_map` does NOT drive `maestro-stack`; `maestro-heatmap.json` UNCHANGED; ordinal-0 preserved | Block Wave 3 — the consistency test will false-pass or the single-authority invariant is broken. security-analyst advisory: confirm no second applicability authority leaked into production. |
| **G3 — Cross-surface-consistency gate** | Wave 3 | `tester` + `devops` | T015 GREEN on `microservices` (7/7 layers agree: L7=clean, L1·L3·L5·L6=n/a, L2·L4=findings); negative test FAILS naming L7; CI job updated in F-250 lock-step (`paths:` ⇄ invocation same commit); `tachi-pytest.yml` untouched | Block Wave 4 — durability guarantee (SC-001/SC-002) not yet proven; baseline regen on an unproven contract risks masking drift. |
| **G4 — Byte-gate** | Wave 4 | `tester` | T019 confirms diff is ONLY the clean→n/a annotation split (+ pagination); `test_backward_compatibility.py` GREEN after intentional re-freeze; `BASELINE_EXAMPLES` set NOT expanded; SC-003 `git diff --stat` on `*.sarif`/`schemas/` = 0; `/aod.analyze` = 0 inconsistencies; quickstart SC-001…SC-005 pass | Block delivery. Any non-annotation/non-MAESTRO/scoring drift is flagged (not absorbed); resolve before `/aod.deliver`. Deliver-gate: `feat(311):` squash title + release-please PR verified. |

---

## 4. Time Estimates (relative S/M sizing — no calendar dates)

| Wave | Phase | Size | Driver |
|------|-------|------|--------|
| **Wave 0** | Setup | **S** | Two independent verification streams, no build. |
| **Wave 1** | A — source contract | **S→M** | S for the [P] doc/directive fan-out (T005–T007) + test authoring; the M edge is the T003→T004 test-first round-trip + the T008 MEDIUM-B option-(a) populator (the one real scope fork). |
| **Wave 2** | B — PDF ∥ infographic | **M** | Two surface tracks run concurrently (so wall-time ≈ one track, not two), but each track is the most code-dense work — extractor wiring (HIGH-A / D3 fence) + template branch + tests. |
| **Wave 3** | C — fixture + CI | **S→M** | S for T015 if the Phase-B harness is clean; the M edge is the at-test-time PDF-state regen wiring (MEDIUM-A) + the F-250 lock-step CI edit + negative-test calibration. |
| **Wave 4** | D — baseline regen + delivery | **M** | Drift audit + deterministic regen across the confirmed-churn set + manual annotation-only diff review are inherently serial and toolchain-bound (Typst+`mmdc`); the byte-gate + analyze + quickstart close-out add overhead. |

**Critical path** (longest serial chain, Team-Lead-confirmed ~10-node S-sized spine):
`T003 → T004 → [T009 ∥ T012] → [T011, T014] → T015 → T016 → T017 → T018 → T020`
with the one MEDIUM-contained fork at T008 (option (a), examples-regen scope, budgeted). The PDF ∥ infographic parallelism collapses Phase B to roughly a single-track duration; the pinch-points are the **A→B barrier (T004)** and the **all-four-surfaces convergence at T015**.

---

## Handoff to Orchestrator

**Feasibility**: APPROVED_WITH_CONCERNS (proceed; the 1 MEDIUM is the by-design T008 fork — orchestrator ratifies option (a) at build start per Team-Lead/PM/Architect endorsement, records the chosen option in the PR body).
**tasks.md**: `specs/311-maestro-matrix-model-b-clean-vs-na/tasks.md`
**Wave strategy**: 5 waves (0–4) above; honor the hard A→B barrier and the disjoint-file Phase-B parallelism; do NOT split the feature (single source cell shared by three surfaces).
**Expect back**: completion report with all tasks `[X]`, no `.aod/` modifications, the T017 final churn set + T008 chosen option enumerated in the PR body, and ready-for-`/aod.deliver` confirmation (`feat(311):` squash, release-please PR verified).
