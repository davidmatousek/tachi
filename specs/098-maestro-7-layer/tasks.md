---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-01
    status: APPROVED
    notes: "All 12 FRs + US-1/US-2/US-3 covered; close-gate (T001-T008) unambiguous; deferrals (T016 → FR-011/FR-012 follow-ups) correct; no scope creep (T005 examples-only, 2 table-less sample-reports excluded, 9 in-scope files). OBS-1 (T017 expects agentic-app diff churn) + OBS-2 (T008 asserts annotation phrase not trailing period) honored; CHANGELOG feat(098) (T015) + agentic-app PR diff (T017) present. 5 non-blocking obs. Details: .aod/results/product-manager.md"
  architect_signoff:
    agent: architect
    date: 2026-06-01
    status: APPROVED
    notes: "CONCERN-1 (HIGH) fully pinned + source-accurate: T005 heading-agnostic discovery + normalize-on-write; T006 names exactly the 3 h3 files (agentic-app, agentic-app/sample-report, mobile-banking-app/sample-report) for h3→h4; T010 heading-agnostic, NOT `####`-anchored. CONCERN-3 (U+2014 verified by codepoint) + populator-not-production-path boundary pinned. Critical path T001→T002→T005→T006→T011→T012 correct; test-first honored; T003 no-canonical-seeding preserved; [P] markers genuine; all line anchors exact. 12/12 FRs; data-model/contracts correctly absent. 2 LOW (FR-005/006 tag labels [now added]; T004 Edit scoping [now noted]). Details: .aod/results/architect.md"
  techlead_signoff:
    agent: team-lead
    date: 2026-06-01
    status: APPROVED_WITH_CONCERNS
    notes: "Feasible at 1.0-1.5 days. Critical path correct; regen tail (Risk 98.1) isolated/sequenced/gated; Architect HIGH h3→h4 norm gated before baseline regen; F-302 remedy noted (T017). All load-bearing claims codebase-verified (h3/h4 split, row counts, line cites, 6 baselines, typst, F-302 script). MED-1 (baseline-regen command was a placeholder) RESOLVED — T011 + quickstart now pin the exact extract-report-data.py + typst compile invocation from test_backward_compatibility.py:88-120. 3 Low non-blocking. Details: .aod/results/team-lead.md"
---

# Tasks: MAESTRO Coverage Matrix — Always Render All 7 Layers

**Input**: Design documents from `specs/098-maestro-7-layer/` (plan.md, spec.md, research.md, quickstart.md)
**Feature**: Issue #98 · BLP-04 Wave 4 · `feat(098)`
**Tests**: REQUESTED — FR-009 mandates a regression test (the durability story US-3). Test tasks are included.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no incomplete-task dependency)
- **[Story]**: US1 / US2 / US3 (maps to spec.md user stories); Setup/Foundational/Polish carry no story label
- Exact file paths included in every task.

## Canonical constants (used by multiple tasks — never re-derive)
- **Canonical layers**: import `MAESTRO_LAYERS` from `scripts/tachi_parsers.py` (`["L1".."L7"]`). No second hard-coded list.
- **Zero-finding annotation (Decision A)**: `Analyzed — no findings this scan` — em dash is **U+2014**. Markdown table cell has **no** trailing period; the Typst prose literal adds a trailing `.` (the only sanctioned cross-format difference).
- **Determinism (ADR-021)**: `SOURCE_DATE_EPOCH=1700000000` for every PDF (re)generation + the backward-compat test.
- **Canonical heading level**: `#### Risk by MAESTRO Layer` (h4) per `output-schemas.md:229`.
- **In-scope tables (9)**: see Foundational/US1 list (plan.md Decision E). Exclude 2 table-less sample-reports + all `test-output/` snapshots (by path pattern; never hardcode a count).

---

## Phase 1: Setup (Shared Contract)

**Purpose**: Pin the single format contract that the LLM directive, the populator, and the tests all honor.

- [X] T001 Update the "Risk by MAESTRO Layer" spec in `.claude/skills/tachi-orchestration/references/output-schemas.md` (~lines 229–240, FR-002): replace the **Omission** bullet (L238) with "always include all 7 canonical layers (L1–L7)"; change the **Ordering** bullet (L237) from severity-descending to **canonical L1→L7, then conditional Unclassified last**; add the zero-finding cell schema — Finding Count `0`, Highest Severity = `Analyzed — no findings this scan` (U+2014); keep the canonical heading at `#### `; preserve the existing "Unclassified row — do not omit it" rule.

**Checkpoint**: The shared format contract is frozen — all downstream authoring (directive, populator) and verification (tests) reference it.

---

## Phase 2: Foundational (Production Render Path + Populator) — BLOCKS all user stories

**Purpose**: The four production-surface edits + the regeneration tool. Serves US-1 and US-2 jointly; must exist before any example/baseline regeneration.

- [X] T002 Rewrite the MAESTRO directive in `.claude/agents/tachi/orchestrator.md:~718` (FR-001 + FR-004 + FR-005 + FR-006): replace "Omit layers with zero findings. Order rows by highest severity descending, then finding count descending." with "Always emit all 7 canonical layers (L1–L7) in canonical L1→L7 order. Zero-finding layers show Finding Count `0` and Highest Severity `Analyzed — no findings this scan` (U+2014 em dash). The Unclassified row remains conditional, placed after L7." (FR-006 canonical order + FR-005 conditional-Unclassified-after-L7 are both encoded here.) Point to `output-schemas.md` for the format.
- [X] T003 [P] Remove the zero-finding filter at `scripts/extract-report-data.py:407` (FR-003): change `findings_by_layer = [layer_groups[lid] for lid in sorted_layer_ids if layer_groups[lid]["findings"]]` to `findings_by_layer = [layer_groups[lid] for lid in sorted_layer_ids]`. Do NOT add canonical seeding — `layer_groups` stays seeded from `parsed_layers` so the PDF can never show more layers than the markdown authored (single source of truth; SC-003). The existing `layer_sort_key` (L1→L7 then Unclassified) is unchanged.
- [X] T004 [P] Replace the dead empty-layer literal at `templates/tachi/security-report/maestro-findings.typ:154` (FR-004): change exactly the bracketed literal `[No findings mapped to this layer.]` (scope the Edit to the full `text(...)[...]` line to avoid matching the heading) to `[Analyzed — no findings this scan.]` (U+2014 em dash; trailing period is correct here — Typst prose). Leave the `else`-branch structure and the `(#count finding…)` heading at :149 unchanged (verify it renders `(0 findings)` grammatically).
- [X] T005 Create `scripts/populate-maestro-coverage.py` (FR-007 — stdlib-only, modeled on `scripts/populate-affected-assets.py` for **transform mechanics only**; **examples-regeneration tool — MUST NOT be wired into any command or orchestrator phase**): import `MAESTRO_LAYERS` from `tachi_parsers.py`; **discover the table heading-level-agnostically** (`^#{3,4}\s+Risk by MAESTRO Layer`) and **normalize the heading to `#### ` on write** (Architect CONCERN-1); parse present rows → `{layer_id: (count, severity)}`; emit all 7 canonical layers in L1→L7 order (present rows keep `(count, severity)`; absent rows → `0` + the annotation, U+2014); move/keep a conditional `Unclassified` row last; idempotent regex upsert of the table block; `--check` mode exits non-zero on drift.

**Checkpoint**: Foundation ready — production renders all 7 layers on new runs; the populator can regenerate committed examples.

---

## Phase 3: User Story 1 — Architect Sees the Full Scan Span (Priority: P1) MVP

**Goal**: Every shipped MAESTRO coverage view lists all 7 canonical layers (L1–L7) in canonical order.

**Independent Test**: Open any regenerated example's threats.md "Risk by MAESTRO Layer" table (and its PDF page) — all 7 canonical layers appear as rows in L1→L7 order, regardless of finding count.

- [X] T006 [US1] Run `scripts/populate-maestro-coverage.py` over the **9 in-scope files** and normalize the 3 h3 headings to `#### `:
  `examples/agentic-app/threats.md` (h3→h4; **PR-diff target**), `examples/agentic-app/sample-report/threats.md` (h3→h4), `examples/mobile-banking-app/sample-report/threats.md` (h3→h4), `examples/web-app/threats.md`, `examples/microservices/threats.md`, `examples/ascii-web-api/threats.md`, `examples/mermaid-agentic-app/threats.md`, `examples/free-text-microservice/threats.md`, `examples/maestro-reference/threats.md` (re-order only). **Do NOT touch** `examples/predictive-ml-app/sample-report/threats.md` or `examples/consumer-agent-app/sample-report/threats.md` (no MAESTRO table — must not force-fit) or any `examples/**/test-output/**`.
- [X] T007 [US1] Verify US-1 acceptance: in `examples/agentic-app/threats.md` confirm all 7 canonical rows present in L1→L7 order with L4 (Deployment Infrastructure) now shown; confirm the markdown table heading is now `#### `; spot-check 2 other regenerated examples for 7 canonical rows + canonical order.

**Checkpoint**: US-1 complete — the full 7-layer span is visible in every regenerated example's table.

---

## Phase 4: User Story 2 — Self-Documenting Zero-Finding Rows (Priority: P1)

**Goal**: Zero-finding rows are explicitly annotated so a reviewer reads them as "covered, clean," cross-format identical.

**Independent Test**: For a zero-finding layer (e.g., agentic-app L4), the markdown row shows `0` + `Analyzed — no findings this scan`, and the regenerated PDF page shows the same annotation phrase.

- [ ] T008 [US2] Verify US-2 cross-format annotation parity: confirm each zero-finding row in the regenerated `examples/agentic-app/threats.md` carries `0` + `Analyzed — no findings this scan` (U+2014, no trailing period in the cell); regenerate the agentic-app PDF and confirm the "MAESTRO Layer Analysis" page renders the same **phrase** `Analyzed — no findings this scan` (trailing period in PDF prose is the sanctioned difference — assert on the phrase, NOT the punctuation; PM OBS-2). Confirm the annotation reads as coverage metadata, not a severity, and does not contradict the STRIDE `---`/`n/a` vocabulary.

**Checkpoint**: US-1 + US-2 both complete — this is the Issue #98 close-gate (Model A).

---

## Phase 5: User Story 3 — Regression-Proofed Completeness (Priority: P2)

**Goal**: An automated test fails if any MAESTRO coverage view drops below 7 canonical layers; the 6 PDF baselines stay byte-deterministic.

**Independent Test**: Introduce a renderer change that omits a layer → the new test fails identifying the missing layer(s); the backward-compat test matches all 6 regenerated baselines byte-for-byte.

> **Test-first note**: T009 and T010 are AUTHORED against the target state immediately after Phase 2 (per plan sequencing). T009 goes green once T003 lands; T010 is red until T006 regeneration, then green. They are grouped here under US-3 for story coherence.

- [ ] T009 [P] [US3] Add a unit assertion to `tests/scripts/test_extract_report_data.py` (FR-009a): given a synthetic `parsed_layers` containing all 7 canonical layers with some zero-finding, assert `maestro_findings_by_layer` has length 7 (filter removed) and that a zero-finding layer's group has an empty `findings` list (so the Typst `else`-branch fires). Follow the existing subprocess+emitted-Typst harness pattern (or add a direct-import unit — the module imports cleanly).
- [ ] T010 [P] [US3] Create `tests/scripts/test_maestro_coverage_invariant.py` (FR-009b): for every `examples/**/threats.md` **excluding any path containing `test-output/`**, **if** the file contains a "Risk by MAESTRO Layer" table (discover **heading-level-agnostically** — `^#{3,4}\s+Risk by MAESTRO Layer` or a bare `Risk by MAESTRO Layer` substring, NOT anchored on `#### `, per Architect CONCERN-1) **then** assert all 7 canonical L-IDs from `MAESTRO_LAYERS` are present. Files without the table are skipped (this naturally excludes the 2 table-less sample-reports). Do NOT hardcode any snapshot count.
- [ ] T011 [US3] Regenerate the **6 gated PDF baselines** under `SOURCE_DATE_EPOCH=1700000000` (FR-008). For each example in {web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice, maestro-reference}, run the exact two-step pipeline the backward-compat test uses (`tests/scripts/test_backward_compatibility.py:88-120`), writing the typst output directly to the `.baseline` path:
  ```bash
  SOURCE_DATE_EPOCH=1700000000 python3 scripts/extract-report-data.py \
    --target-dir examples/<ex> \
    --output templates/tachi/security-report/report-data.typ \
    --template-dir templates/tachi/security-report
  SOURCE_DATE_EPOCH=1700000000 typst compile \
    templates/tachi/security-report/main.typ \
    examples/<ex>/security-report.pdf.baseline --root .
  rm -f templates/tachi/security-report/report-data.typ   # keep template dir clean
  ```
  (maestro-reference changes by re-order only.) Also regenerate the agentic-app PDF artifacts for the US-2/PR diff, though agentic-app is not in the 6-baseline gate.
- [ ] T012 [US3] Run `pytest tests/scripts/test_backward_compatibility.py` and confirm all 6 baselines are byte-identical; run `pytest tests/scripts/test_extract_report_data.py tests/scripts/test_maestro_coverage_invariant.py` and confirm green.

**Checkpoint**: US-3 complete — the 7-row invariant is regression-proofed and baselines are deterministic.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T013 [P] Verify **no SARIF / schema change** (FR-010): `git diff --stat` shows no changes under SARIF emitters or `schemas/`; confirm no `.sarif`/schema files in the diff.
- [ ] T014 Run `/aod.analyze` and confirm no cross-artifact inconsistencies (SC-005).
- [ ] T015 [P] Add a CHANGELOG.md entry: `feat(098): MAESTRO coverage matrix always shows all 7 layers (Issue #98)`.
- [ ] T016 [P] Create two tracked follow-up GitHub issues: (a) FR-011 Model B — clean-vs-`n/a` two-state annotation (adopt `coverage-matrix-model.md` `---`/`n/a` vocabulary; needs `component_layer_map` from `extract-infographic-data.py`); (b) FR-012 `maestro-stack` infographic completeness. Both are P1 follow-ups, NOT close-gates for #98.
- [ ] T017 Assemble the PR description: show the `examples/agentic-app/` diff; spot-check that ONLY matrix rows/order changed (Risk 98.3) — expect the added L4 row **+** the Unclassified row relocating to the bottom **+** non-empty rows re-sorting to canonical order (PM OBS-1, expected churn, not content drift). Note the F-302 remedy in the PR: if `init-baseline-tree` fails on unrelated doc-drift, run `tests/fixtures/regenerate-baseline.sh` after verifying substitution semantics (separate fixture from the PDF `.baseline` gate).

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (T001)**: no dependencies — defines the shared contract.
- **Foundational (T002–T005)**: depends on T001; **BLOCKS all user stories**. T003 and T004 are `[P]` (different files); T002 and T005 author/consume the contract.
- **US-1 (T006–T007)**: depends on T005 (populator must exist).
- **US-2 (T008)**: depends on T006 (rows regenerated) + T004 (Typst literal).
- **US-3 (T009–T012)**: T009 depends on T003; T010 authored after Phase 2 (green after T006); T011 depends on T006 (markdown regenerated); T012 depends on T010 + T011.
- **Polish (T013–T017)**: depends on all prior phases; T017 (PR) is last.

### Critical Path
`T001 → T002 → T005 → T006 → T011 → T012 → T014 → T017`
(T003/T004 parallel to T002/T005; T009/T010 parallel after their deps; T013/T015/T016 parallel in Polish.)

### Cross-story note (inherent, accepted)
US-3 verifies US-1/US-2 outputs, so it depends on US-1 regeneration — this is intrinsic to a regression/durability story and does not break US-1/US-2 independent testability (US-1 and US-2 are demonstrable from the regenerated examples before US-3 runs).

### Parallel Opportunities
- T003 + T004 (different files, after T001).
- T009 + T010 (different test files).
- T013 + T015 + T016 (independent polish tasks).

---

## Implementation Strategy

### MVP (closes Issue #98)
1. T001 (contract) → 2. T002–T005 (Foundational) → 3. T006–T007 (US-1) → 4. T008 (US-2). **STOP & VALIDATE**: both coverage views show all 7 layers with annotated zero rows. US-1 + US-2 are the close-gate.

### Incremental
5. US-3 (T009–T012) regression-proofs + regenerates baselines → 6. Polish (T013–T017) gates + CHANGELOG + follow-ups + PR.

### Single-developer reality
This is a tightly-coupled rendering fix (not parallel team work). Execute along the critical path; use `[P]` markers to batch the independent edits/tests. Est. 1.0–1.5 days (Team-Lead).

---

## Notes
- Commit after each logical group (e.g., Foundational edits together; regeneration together).
- Freeze the annotation string + canonical order is already done (plan Decision A) — do not re-litigate mid-build.
- The single largest risk is byte-determinism on the 6 baselines (Risk 98.1/98.3); the populator (T005) + heading normalization (T006) + `SOURCE_DATE_EPOCH` (T011) + backward-compat gate (T012) collectively contain it.
- Heading normalization (h3→h4) is load-bearing: without it, the agentic-app PDF renders 0 MAESTRO layers and T010 would false-green (Architect CONCERN-1, HIGH).
