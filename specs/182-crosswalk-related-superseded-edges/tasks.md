---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-07
    status: APPROVED
    notes: "0 blocking, 4 non-blocking (notation/doc-hygiene). FR coverage 15/15 discharged; self-declared FR→task map verified line-by-line; all 7 SCs tied to verification tasks; [MANUAL-ONLY] tags (T002 harvest, T005 audit) exactly match spec FR-002/FR-014. US1 (≥80 related floor) correctly modeled as MVP shippable independent of US2/US3; empty-superseded degenerate case handled by three guards (T008 'may be 0' + deferral-MUST-exist, T009 'does NOT fail on empty', Independent Test 'passes even if empty'). No scope creep: all six Out-of-Scope lines held (no catalog expansion, no #183, no schema/test/ADR-027 change via T003+T013 belt-and-suspenders, superseded remainder DEFERRED not dropped, disjoint write-set). Anti-drift enforced at every gate — no low-padding pathway anywhere (T002 tripwire → T003 documented-floor → T004 0-OWASP-LLM→CWE → T005 downgrade audit). Live-state re-verified: 542/0/0, 5 test fns, enums + PRIMARY_EDGE_FLOOR=500, cwe 53/atlas 36/attack 701/owasp 60. Details: .aod/results/product-manager.md"
  architect_signoff:
    agent: architect
    date: 2026-06-07
    status: APPROVED
    notes: "0 blocking, 4 non-blocking. Live-state re-verified (542/0/0, 5 integrity fns, catalogs 53/36/701/60, 5 passed, clean tree, ADR-027 present). All 6 review questions resolved: T002 Foundational gate + T003 floor-authorization sound; US1⟂US2 same-file serialization (T008 after T004) correctly captured and not falsely parallelized; annotation-key-stripping structurally backstopped by test_crosswalk_loads extras-forbidden; T005 content audit correctly distinct from shape-only test_citation_shape; existing 5-fn suite is the complete oracle (no new test); FR-006 View-ID + T013 diff-guard are real failure modes correctly guarded. No residual technical gap before /aod.build. Details: .aod/results/architect.md"
  techlead_signoff:
    agent: team-lead
    date: 2026-06-07
    status: APPROVED_WITH_CONCERNS
    notes: "0 blocking, 3 non-blocking. Live-verified every T001 claim (542/0/0, catalogs 53/36/701/60, 5 fns, suite green 1.01s). Granularity right-sized (15 tasks on the F-186 6-phase skeleton +2 harvest/survey split); T004 correctly the heavy per-edge authoring task (~5-min/edge); floor 80 → ~2.0d realistic. Critical path T001→T002→T003 gate→{US1∥US2-survey}→US3→Polish correct; US1 MVP (T001-T006) isolated to ship even if superseded thin. T007 [P] ∥ US1 real (disjoint surfaces); T008 correctly serializes after T004. [MANUAL-ONLY] = right time-variable pair (T002/T005); yield-tripwire (T003) caps the floor from becoming an open-ended sink. All 4 PRD concerns honored: C1 1.5-2.5d, C2 quota'd floor+tripwire, C3 #185 sequencing/snapshot, C4 hard 150 ceiling. Non-blocking: TL-1 strict-serial ceiling math ~3.0d but C4 quota bounds it (expected ~65-80 core); TL-2 Polish order (provenance before diff-guard); TL-3 deferred-superseded.md must ship even if empty. agent-assignments.md WRITTEN (registry names only). POST-REVIEW REFINEMENT applied (resolves TL-2): Polish renumbered so T012 provenance/CHANGELOG → T013 diff-guard run sequentially, and the diff-guard allowed-file set now includes CHANGELOG.md; agent-assignments.md reconciled to match. Details: .aod/results/team-lead.md"
---

# Tasks: Crosswalk `related` + `superseded` Edge Expansion — First Tranche (F-182)

**Input**: Design documents from `specs/182-crosswalk-related-superseded-edges/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

**Tests**: No NEW test tasks. Per spec/plan, the **existing** `tests/schemas/test_taxonomy_integrity.py` (5 functions) is the structural acceptance oracle — any dangling endpoint, broken enum, duplicate 5-tuple, bad citation shape, or unsorted catalog fails it. No new code or schema → no new test required (verification tasks RUN the existing suite). The **anti-drift citation audit** (FR-014) is a manual content gate the shape-only suite cannot enforce.

**Organization**: By user story. US1 (≥80 `related` floor) is the MVP, shippable independent of US2 (`superseded`, may be empty) and US3 (README rubric). All authoring is blocked on the Foundational survey/harvest gate.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files/surfaces, no dependency on an incomplete task)
- **[Story]**: US1 / US2 / US3
- Exact file paths included.

---

## Phase 1: Setup

**Purpose**: Confirm the clean baseline before any edit.

- [x] T001 Confirm baseline: `pytest tests/schemas/test_taxonomy_integrity.py` reports `5 passed`; `crosswalk.yaml` edge_type counts are `{primary: 542, related: 0, superseded: 0}`; catalog counts are cwe 53 / mitre-atlas 36 / mitre-attack 701 / owasp 60; working tree has no uncommitted changes to `schemas/taxonomy/*.yaml` or `tests/schemas/test_taxonomy_integrity.py`. If counts differ, STOP and reconcile before authoring.

---

## Phase 2: Foundational (Blocking Prerequisite)

**Purpose**: Survey the achievable yield and capture the durable harvest artifact. **CRITICAL**: blocks all `related` authoring; the survey result governs the floor (FR-002 yield-tripwire).

- [x] T002 Build-start survey + harvest (FR-002, FR-012): harvest candidate `related` relations from the four audited source classes — CWE↔CWE (cwe.mitre.org Relationships/views, both ends in the 53-record `cwe.yaml`, recording Nature + View ID), OWASP-Web→CWE (owasp.org/Top10 counted lists, target in `cwe.yaml`), ATLAS→ATT&CK (atlas-data `ATT&CK-reference`, ATLAS in `mitre-atlas.yaml` + ATT&CK in `mitre-attack.yaml`), OWASP-LLM→ATLAS (genai.owasp.org Reference Links, ATLAS in `mitre-atlas.yaml`). Capture every candidate with `source_class`, `confidence`, `citation`, `disposition` to `specs/182-crosswalk-related-superseded-edges/reference-edges.yaml` per [contracts/reference-edges.schema.md](contracts/reference-edges.schema.md). Compute `high_medium_core_total`; set `tripwire_fired: true` if core < 80. `[MANUAL-ONLY]` external-source harvest + curator confidence judgment.
- [x] T003 No-migration gate + floor authorization (architect): re-confirm the additive-only posture (no `schema_version` bump, no change to `tests/schemas/test_taxonomy_integrity.py`, no new ADR, no ADR-027 change) and review the T002 survey yield — if `high_medium_core_total ≥ 80`, authorize the ≥80 floor; if `< 80`, authorize the **documented achievable floor** (yield-tripwire) and require the rationale be recorded in `reference-edges.yaml` (**no `low`-padding to reach 80**). Gate (FR-002, FR-011).

**Checkpoint**: harvest captured + floor authorized — US1 and US2 can now proceed (US2 survey ∥ US1 authoring).

---

## Phase 3: User Story 1 — Traverse "what else relates to this?" (Priority: P1) MVP

**Goal**: Author the committed floor of `high`/`medium` `related` edges, turning the primary-only graph into a traversable one.

**Independent Test**: Filter `crosswalk.yaml` to `edge_type == 'related'` → non-empty resolved set (≥80 or documented floor), every endpoint resolves, every high/medium edge cites a supporting source. Ships independent of US2/US3.

- [x] T004 [US1] Author the `related` edges (FR-001/003/004/005/006): promote the `disposition: authored` candidates from `reference-edges.yaml` into `schemas/taxonomy/crosswalk.yaml` — **strip annotation keys** (`source_class`, `disposition`) so each record carries only `{source, target, edge_type: related, confidence, citation}`. Constrain to the four audited source classes; assign `confidence` per the anti-drift rule; CWE↔CWE citations record Nature + View ID; assign **0** `high`/`medium` to OWASP-LLM→CWE edges (FR-004). Dedupe-guard against the existing 542 edges and the 5-tuple uniqueness key. Stay within the 80–150 band (never exceed 150; surplus → headroom note, not authored).
- [x] T005 [US1] Anti-drift citation audit (FR-014, code-reviewer): for every `high`/`medium` `related` edge just authored, open its `citation` and confirm the source supports the assigned label; downgrade any unsupported edge to the weaker label. Confirm **0** `high`/`medium` edges originate from OWASP-LLM→CWE (SC-002, SC-003). `[MANUAL-ONLY]` requires reading each cited source.
- [x] T006 [US1] Verify US1 in `tests/schemas/test_taxonomy_integrity.py`: run the suite → `5 passed`; confirm `related` count ∈ [80,150] (or the documented achievable floor), `primary` count unchanged at 542, **0** duplicate 5-tuples, all new endpoints resolve in their catalogs (FR-010, FR-013; SC-001, SC-007).

**Checkpoint**: MVP complete — the `related` floor authored, audited, integrity green. Shippable on its own.

---

## Phase 4: User Story 2 — Answer "what superseded what?" (Priority: P2)

**Goal**: Author the catalog-authorable `superseded` set and record the deferred remainder. Independent of US1 after T002.

**Independent Test**: Filter `crosswalk.yaml` to `edge_type == 'superseded'` → every edge's endpoints resolve; `deferred-superseded.md` exists with a per-class disposition. Passes even if the authored set is empty.

- [x] T007 [P] [US2] Survey authorable `superseded` pairs (FR-007 prep): scan the catalogs for deprecation/replacement pairs whose **both** endpoints already resolve under current catalogs (e.g., a deprecated CWE + its replacement both in `cwe.yaml`; an ATT&CK deprecation pair both in `mitre-attack.yaml`); record candidates + citations to `reference-edges.yaml`. `[P]` — research surface, runs parallel with the US1 authoring lane.
- [x] T008 [US2] Author `superseded` + record deferral (FR-007/008): insert the authorable `superseded` edges (annotation keys stripped) into `schemas/taxonomy/crosswalk.yaml` (may be 0); write `specs/182-crosswalk-related-superseded-edges/deferred-superseded.md` with a one-line rationale per catalog-gated deferred class → follow-on. The deferral file MUST exist even if the authored set is empty.
- [x] T009 [US2] Verify US2 in `tests/schemas/test_taxonomy_integrity.py`: run the suite → `5 passed`; confirm every authored `superseded` edge resolves + is unique, and `deferred-superseded.md` is present with dispositions (SC-004). If the authored set is empty, confirm the empty outcome is documented as acceptable.

**Checkpoint**: superseded lineage authored where authorable; deferred remainder honestly recorded.

---

## Phase 5: User Story 3 — Inherit a settled edge-authoring methodology (Priority: P3)

**Goal**: Extend the README rubric so future authors inherit a drift-resistant methodology.

**Independent Test**: A new author can classify a candidate edge's confidence using only `schemas/taxonomy/README.md` — including the View-ID rule and the OWASP-LLM→CWE caution.

- [X] T010 [US3] Extend `schemas/taxonomy/README.md` (FR-009): add a `related`/`superseded` calibration section with a worked example per audited source class, the CWE View-ID rule (parents are view-dependent), an explicit "OWASP-LLM→CWE is prose-only on official pages → `low`/inferred" caution, and the authoritative-source list. Keep the existing primary-edge rubric + anti-drift rule intact.
- [X] T011 [US3] Verify US3 (code-reviewer): confirm the README rubric extension is self-sufficient (a new author can calibrate confidence from the README alone) and that its calibration examples match the confidence assignments actually used in the authored edges (SC-006).

**Checkpoint**: edge-authoring methodology settled and documented.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: No-migration verification, documentation, and closure (FR-011, FR-015).

- [X] T012 Provenance + CHANGELOG (FR-015): add an F-182 header provenance note to `schemas/taxonomy/crosswalk.yaml` (mirroring the F-186 convention) and a `feat(182)` entry to `CHANGELOG.md` (BLP-05 F-3 sibling-h3 cluster placement) summarizing the `related` floor authored + `superseded` outcome.
- [X] T013 No-migration diff guard (FR-011, code-reviewer) — runs AFTER T012 so it sees the final diff: confirm the feature diff touches ONLY `schemas/taxonomy/crosswalk.yaml`, `schemas/taxonomy/README.md`, `CHANGELOG.md`, and `specs/182-*` artifacts — **0** changes to any catalog YAML, `tests/schemas/test_taxonomy_integrity.py`, `schema_version`, or any ADR (incl. ADR-027); `primary` count == 542 (SC-005).
- [X] T014 Final integrity gate: `pytest tests/schemas/test_taxonomy_integrity.py` → `5 passed`; run `/aod.analyze` → no inconsistency (FR-013; SC-005).
- [x] T015 Close GitHub Issue #182 `stage:done` with the deliverable summary (`related` count, `superseded` count, deferred-set reference) — deliver-time, via `/aod.deliver` (FR-015). **Done 2026-06-07**: 37 related / 0 superseded (4 deferred classes → `deferred-superseded.md`); see [delivery.md](delivery.md).

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (T001)**: no deps — start immediately.
- **Foundational (T002→T003)**: after T001 — **BLOCKS** all authoring. T003 gate authorizes the floor.
- **US1 (T004→T005→T006)** and **US2 (T007→T008→T009)**: both start after T003. US2's survey (T007) runs ∥ US1 authoring; US2 authoring (T008) on `crosswalk.yaml` serializes after US1 authoring (same file). US1 does NOT depend on US2.
- **US3 (T010→T011)**: after US1/US2 patterns settle (the rubric examples reflect the authored edges).
- **Polish (T012–T015)**: after US3. T015 is deliver-time.

### Within-Story Order
- US1: T004 → T005 (audit) → T006 (verify).
- US2: T007 (survey, [P]) → T008 (author + defer) → T009 (verify).
- US3: T010 (extend) → T011 (verify).

### Parallel Opportunities
- **T007 [P]** (superseded survey) ∥ US1 lane (T004/T005) — different research surface.
- Polish is sequential: T012 (provenance/CHANGELOG) → T013 (diff guard, must see the final diff) → T014 (final gate).

---

## Implementation Strategy

### MVP First (US1)
1. T001 Setup → T002/T003 Foundational (survey, harvest, floor gate) → T004/T005/T006 US1.
2. **STOP and VALIDATE**: `related` floor authored, anti-drift audit clean, `5 passed`, primary still 542. Complete, shippable increment even if `superseded` ends up empty.

### Incremental
1. Setup + Foundational → harvest ready, floor authorized.
2. US1 → the `related` floor (MVP). ∥ US2 survey → superseded disposition.
3. US2 author + defer → US3 README rubric.
4. Polish → diff guard + docs + final gate + close.

---

## Notes
- Total: **15 tasks** (Setup 1, Foundational 2, US1 3, US2 3, US3 2, Polish 4).
- Per story: US1 = 3, US2 = 3, US3 = 2.
- Parallel: T007 ∥ US1 lane (Polish is sequential: T012 provenance → T013 diff-guard → T014 gate).
- Independent test criteria: US1 = related ∈ [80,150] + 5/5 + audit clean; US2 = superseded resolve + deferred doc present (empty OK); US3 = README self-sufficient.
- Suggested MVP scope: **T001–T006** (the `related` floor).
- `[MANUAL-ONLY]`: T002 (external-source harvest), T005 (anti-drift citation audit).
- FR coverage: FR-001(T004), FR-002(T002/T003), FR-003(T004/T005), FR-004(T004/T005), FR-005(T004), FR-006(T004), FR-007(T007/T008), FR-008(T008), FR-009(T010/T011), FR-010(T006/T009), FR-011(T003/T013), FR-012(T002), FR-013(T006/T014), FR-014(T005), FR-015(T012/T015).
- Commit after each task or logical group. Harvest-don't-invent — never author an edge without a citation.
