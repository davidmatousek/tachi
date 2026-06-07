---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-07
    status: APPROVED
    notes: "0 blocking, 2 minor non-blocking. All US1/US2/US3 + FR-001..FR-009 mapped to tasks; US1 (10 edges) is the independently-shippable MVP gated only on T002 (never the T005 disposition); no scope creep (#184/#185 + 2 CWE-blocked + ~72 out-of-scope removals all excluded); empty-add-set degenerate case handled (T006/T007 skip cleanly, T008 has a non-vacuous empty-set branch). All 3 plan-stage PM carry-forwards satisfied. Minor: (1) priority-label cosmetic drift immaterial at tasks stage; (2) T013 correctly deliver-time. Details: .aod/results/product-manager.md"
  architect_signoff:
    agent: architect
    date: 2026-06-07
    status: APPROVED
    notes: "0 blocking, 3 minor advisory (no conditions). Dependency order exactly right — T002 extract-to-checked-in-artifact is the blocking Foundational gate before every edit (de-risks the unreachable/unpushed dangling SHAs); US1 ⟂ US2 correctly modeled (10 resolvable edges have zero dependency on the 6 missing IDs); US3 verification last. Byte-exact recovery + annotation-key-stripping proven test-safe. FR-006 drift-guard (T009) is discrete + blocking, targets empirically-real failure modes (2 CWE-blocked + exact 72 non-gap removals). Full FR→task traceability. No new test needed (existing 5-fn suite is the oracle). PoC re-reproduced at tasks stage: insert 10 → 536 → 5 passed in 0.97s, tree clean. Minor advisories (all optional, suite already covers): contract '1 vs 3 attack→cwe' wording; optional key-set==5 assertion in T004/T008; optional T003 self-dedupe. Details: .aod/results/architect.md"
  techlead_signoff:
    agent: team-lead
    date: 2026-06-07
    status: APPROVED
    notes: "0 blocking, 0 concerns (the 3 PRD-stage concerns C1/C2/C3 resolved upstream in spec/plan). 13-task granularity right-sized for the 0.4-0.75 day envelope; critical path T001→T002→{US1 ∥ US2}→US3→Polish correct; the US1∥US2 parallelization is real (disjoint surfaces) and worth modeling; the [MANUAL-ONLY] architect gate (T005) is correctly isolated so it never blocks the US1 MVP; extract-first (T002) + conditional T006/T007 sequencing sound. agent-assignments.md WRITTEN (W0 architect → W1 senior-backend-engineer → W2 tester+code-reviewer; registry names only). Details: .aod/results/team-lead.md"
---

# Tasks: MITRE ATT&CK + ATLAS Catalog Expansion — Residual Drift-Edge Restoration (F-A1.3)

**Input**: Design documents from `specs/186-mitre-catalog-expansion/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

**Tests**: No NEW test tasks. Per spec, the **existing** `tests/schemas/test_taxonomy_integrity.py` (5 functions) is the acceptance oracle — any dangling edge or shape/sort violation fails it. No new code or schema → no new test required (verification tasks RUN the existing suite).

**Organization**: By user story. US1 (restore 10 edges) is the MVP and is **independent of** US2 (the disposition gate) — both start after the Foundational extract.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: US1 / US2 / US3
- Exact file paths included.

---

## Phase 1: Setup

**Purpose**: Confirm the recovery prerequisites and the clean baseline before any edit.

- [X] T001 Confirm recovery prerequisites: `git cat-file -t e58f247` and `git cat-file -t 991e1ee` both return `commit`, and `pytest tests/schemas/test_taxonomy_integrity.py` reports `5 passed` (baseline 526 primary edges). If the dangling commits are absent (fresh clone / post-`git gc`), STOP and escalate — recovery source is gone.

---

## Phase 2: Foundational (Blocking Prerequisite)

**Purpose**: Extract the durable restore-set. **CRITICAL**: blocks all edge restoration (US1 + US2 edges); de-risks dangling-object loss.

- [X] T002 Extract the 16 MITRE-gap-scoped removed edges from commit `e58f247` (`git show e58f247:schemas/taxonomy/crosswalk.yaml`, filter to edges referencing the 16 gap IDs) into `specs/186-mitre-catalog-expansion/restored-edges.yaml`, annotated `_resolvable: true|false` + `_blocked_on:` per the contract (FR-002). Confirm: 16 edges total, 10 `_resolvable: true`, 6 `_resolvable: false`, each `edge_type`/`confidence`/`citation` byte-exact to `e58f247`.

**Checkpoint**: restore-set captured and checked in — US1 and US2 can now proceed in parallel.

---

## Phase 3: User Story 1 — Restore the 10 Now-Resolvable MITRE Edges (Priority: P1) MVP

**Goal**: Restore the 10 edges whose endpoints already resolve, growing the crosswalk 526 → 536 with integrity intact.

**Independent Test**: Insert the 10 edges, run the integrity suite → `5 passed`, crosswalk = 536 primary edges, no dangling endpoint. Ships independently of the US2 disposition.

- [ ] T003 [US1] Insert the 10 resolvable edges (the `_resolvable: true` set, **annotation keys `_resolvable`/`_blocked_on` stripped**) from `specs/186-mitre-catalog-expansion/restored-edges.yaml` into `schemas/taxonomy/crosswalk.yaml` (FR-001). Dedupe-guard against the existing 526 (architect confirmed 0 collisions).
- [ ] T004 [US1] Verify US1 in `tests/schemas/test_taxonomy_integrity.py`: run the suite → `5 passed`; confirm 536 primary edges, all 10 endpoints resolve, no duplicate, ≥500 floor (SC-001, SC-002).

**Checkpoint**: MVP complete — the 10 MITRE edges restored, integrity green. Shippable on its own.

---

## Phase 4: User Story 2 — Disposition the 6 Missing ATLAS IDs (Priority: P2)

**Goal**: Settle the 6-ID question with a source-verified add/reject/defer decision; add any approved records and restore their edges. Independent of US1 after T002.

**Independent Test**: 6/6 IDs carry a documented disposition on Issue #186; any "add" record passes shape + sort tests; any unblocked edge restores with integrity intact.

- [ ] T005 [P] [US2] Architect: verify each of the 6 missing ATLAS IDs (`AML.T0001/T0005/T0025/T0037/T0043/T0048`) against `mitre-atlas/atlas-data` `techniques.yaml`; publish an `add`/`reject`/`defer` decision + one-line rationale as a comment on GitHub Issue #186 (decision trail), informing the `schemas/taxonomy/mitre-atlas.yaml` adds (FR-003). `[MANUAL-ONLY]` external-source verification + architect judgment. If `atlas-data` is unreachable, record the obstruction (blocks only US2, not US1).
- [ ] T006 [US2] For each `add`-disposition ID, insert a record into `schemas/taxonomy/mitre-atlas.yaml` (shape `{id, full_id: ATLAS-AML.TXXXX, name (byte-exact from atlas-data), url, cwe_refs: []}`, correct lexicographic position) and append the F-A1.3 provenance note to the file header (FR-004, FR-009). Conditional — skip if the add-set is empty.
- [ ] T007 [US2] For each `add`-disposition ID, restore its blocked edge (the matching `_resolvable: false` entry, annotations stripped) from `restored-edges.yaml` into `schemas/taxonomy/crosswalk.yaml` (FR-005). Conditional — skip if the add-set is empty.
- [ ] T008 [US2] Verify US2 in `tests/schemas/test_taxonomy_integrity.py`: run the suite → `5 passed`; confirm any new records are shape-valid + lexicographically sorted, and any restored edges resolve (SC-003). If add-set empty: confirm 6/6 reject/defer dispositions are recorded on Issue #186.

**Checkpoint**: 6-ID decision trail closed; catalog/crosswalk reflect the approved adds.

---

## Phase 5: User Story 3 — No Drift Re-Introduced, Integrity Green (Priority: P3)

**Goal**: Prove only the intended edges were added and the structural gate holds.

**Independent Test**: Diff the crosswalk against pre-change; confirm only the 10 (+k) intended edges were added and the integrity suite is 5/5.

- [ ] T009 [US3] Drift guard on `schemas/taxonomy/crosswalk.yaml`: diff vs the pre-change crosswalk; confirm ONLY the 10 (+k FR-005) intended edges were added — 0 of the ~72 non-gap T029 removals (semantic-drift/dedupe/owasp→cwe/control→nist) and 0 of the 2 CWE-blocked edges (`T1070.006→CWE-1269`, `T1562→CWE-693`) reappear (FR-006, SC-004).
- [ ] T010 [US3] Final integrity gate: `pytest tests/schemas/test_taxonomy_integrity.py` → `5 passed`; run `/aod.analyze` → no inconsistency; confirm `schemas/taxonomy/mitre-attack.yaml` unchanged at 701 records and no `schema_version` change anywhere (SC-005, SC-006).

**Checkpoint**: All stories verified; crosswalk is correct and integrity-gated.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and closure (FR-009).

- [ ] T011 [P] Add a `feat(186)` entry to `CHANGELOG.md` summarizing the 10 edges restored + the 6-ID disposition outcome.
- [ ] T012 [P] Update `specs/180-taxonomy-crosswalk-collection/NEXT-SESSION.md` decision trail to point at the #186 resolution; note the 2 CWE-blocked edges as #185 scope.
- [ ] T013 Close GitHub Issue #186 `stage:done` with the disposition summary + deliverable references (deliver-time, via `/aod.deliver`).

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (T001)**: no deps — start immediately.
- **Foundational (T002)**: after T001 — **BLOCKS** all edge work.
- **US1 (T003→T004)** and **US2 (T005→T006→T007→T008)**: both start after T002, **in parallel** (disjoint concerns; US1 touches only crosswalk edges, US2 the disposition + conditional records). US1 does NOT depend on US2.
- **US3 (T009→T010)**: after US1 (and US2 if it restored edges) — final verification.
- **Polish (T011-T013)**: after US3. T013 is deliver-time.

### Within-Story Order
- US1: T003 → T004.
- US2: T005 (gate) → T006 (records) → T007 (edges) → T008 (verify). T006/T007 conditional on "add" dispositions.

### Parallel Opportunities
- **T005 [P]** (disposition) runs in parallel with the entire US1 lane (T003/T004) — different surfaces.
- **T011 [P]** ∥ **T012 [P]** (CHANGELOG vs NEXT-SESSION — different files).

---

## Implementation Strategy

### MVP First (US1)
1. T001 Setup → T002 Foundational (extract restore-set) → T003/T004 US1.
2. **STOP and VALIDATE**: 10 edges restored, `5 passed`, 536 edges. This is a complete, shippable increment even if all 6 IDs end up reject/defer.

### Incremental
1. Setup + Foundational → restore-set ready.
2. US1 → the 10 edges (MVP). ∥ US2 → 6-ID disposition (+ any adds).
3. US3 → drift guard + final integrity gate.
4. Polish → docs + close.

---

## Notes
- Total: **13 tasks** (Setup 1, Foundational 1, US1 2, US2 4, US3 2, Polish 3).
- Per story: US1 = 2, US2 = 4, US3 = 2.
- Parallel: T005 ∥ US1 lane; T011 ∥ T012.
- Independent test criteria: US1 = integrity 5/5 + 536 edges; US2 = 6/6 dispositions + sorted records; US3 = drift-free diff + 5/5.
- Suggested MVP scope: **T001–T004** (the 10-edge restore).
- `[MANUAL-ONLY]`: T005 (architect external-source verification).
- Commit after each task or logical group. Byte-exact recovery — never re-author edges.
