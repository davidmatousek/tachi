---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-11
    status: APPROVED_WITH_CONCERNS
    notes: "All 3 user stories covered with independent commit-gated tests; FR-001..FR-008 fully traced; zero scope creep beyond PRD v1.1 + accepted FR-006. All 5 PM plan-stage conditions landed verbatim (T001 red pre-state guard, T018 dual-attribution + stale-by-design disclosure, T019 PRD errata + KB lesson, amended regen contract wired into T014). Disposition gate correctly blocks catalog edits while extraction parallels (D5); US1 MVP slice viable as branch checkpoint. 2 LOW folded at tasks stage (T020 /aod.analyze, MVP phrasing) + 1 INFO. Details: .aod/results/product-manager.md"
  architect_signoff:
    agent: architect
    date: 2026-06-11
    status: APPROVED_WITH_CONCERNS
    notes: "FR-030 ordering correct (T005 blocks production edits; T011 after T010; T014 after T013); all deferred folds landed in T014/T001/T015/T018; [P] write sets verified pairwise-disjoint; gates keep every commit green. New erratum folded: edge counts via YAML parse (naive grep over-counts +1) — T001/T013/quickstart amended; literal pytest totals to be recorded in evidence; C3 D-7 trigger-taxonomy clause restated in results for T018 executor. 6 items (4 LOW + 1 INFO + cosmetics), none structural. Details: .aod/results/architect.md"
  techlead_signoff:
    agent: team-lead
    date: 2026-06-11
    status: APPROVED_WITH_CONCERNS
    notes: "Granularity PASS (20 single-sitting tasks); critical path topologically correct; timing-dominant entry leg is T002→T004→T006 — pace disposition first. REVISED O/R/P: 0.75/1.0/1.5 days (supersedes PRD 0.5/0.75/1.0; +FR-006 regen ~2.25h R + red-main trail ripple; floor requires first-pass-clean CA-only diffs) — folded into tasks.md Estimated Effort + T019 errata. Typst 0.14.2 verified installed (R6→LOW); byte-identity suite local-only. Agent map registry-valid; T020→tester. 1 MED (effort line — folded) + 4 LOW. Details: .aod/results/team-lead.md"
---

# Tasks: CWE Catalog Expansion — T029 Drift-Edge Restoration (F-A1.2)

**Input**: Design documents from `/specs/185-cwe-catalog-expansion/`
**Prerequisites**: plan.md ✓ (dual-signed), spec.md ✓ (PM-signed), research.md ✓ (D1–D6), data-model.md ✓, contracts/ ✓ (restored-edges + baseline-regen), quickstart.md ✓

**Tests**: No new test files — the existing suites are the acceptance gates (`tests/schemas/test_taxonomy_integrity.py` 5/5 at every data commit; `tests/scripts/test_backward_compatibility.py` red→green at W1-3). Gate tasks below run them; no test is edited.

**Organization**: Tasks grouped by user story. US1 = records (MVP), US2 = edges, US3 = baselines + verification + trail.

## Format: `[ID] [P?] [Story] Description`

## Path Conventions
Single-project data feature: `schemas/taxonomy/`, `examples/`, `specs/185-cwe-catalog-expansion/` at repo root. No `src/` changes.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Pin recovery sources and record the verified pre-state (including the known-red byte-identity suite).

- [X] T001 Verify recovery objects and record pre-state evidence in specs/185-cwe-catalog-expansion/test-results/pre-state.md: `git cat-file -t e58f247` and `991e1ee` both → `commit`; blob edge counts 551/438 via YAML parse (NOT `grep -c "edge_type:"` — over-counts +1 on a commented header line); integrity suite 5/5 green (~1s); run `tests/scripts/test_backward_compatibility.py` and record the EXPECTED RED pre-state with LITERAL pytest totals (parametrized failures attributed to the ATLAS CA section per plan review — do NOT "fix" anything here)
- [X] T002 [P] Download `https://cwe.mitre.org/data/xml/cwec_v4.20.xml.zip`, unzip locally (NOT committed), record corpus pin (version 4.20, release 2026-04-30, file SHA-256, retrieval date) in specs/185-cwe-catalog-expansion/test-results/corpus-pin.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Close the dangling-object window (Risk 185.1) and produce the harvest table — the two inputs every story consumes.

**CRITICAL**: T005's commit is the feature's insurance policy; it lands before ANY production-data edit.

- [X] T003 [P] Write specs/185-cwe-catalog-expansion/scripts/extract_restore_set.py — removed-set from `git show e58f247:schemas/taxonomy/crosswalk.yaml` vs `991e1ee`, filter `target.taxonomy == cwe AND target.id ∉ frozen-53`, emit restored-edges.yaml with header provenance + per-edge `_blocked_on` (per contracts/restored-edges.schema.md)
- [X] T004 [P] Write specs/185-cwe-catalog-expansion/scripts/harvest_cwe_names.py — parse cwec_v4.20.xml (Weakness/Category/View elements), emit the 40-row table (id, verbatim name, type Weakness|Category|Pillar, status incl. deprecated flag) to specs/185-cwe-catalog-expansion/test-results/harvest-40.md
- [X] T005 Run extraction → specs/185-cwe-catalog-expansion/restored-edges.yaml; verify counts (67 = 65 owasp→cwe + 2 mitre-attack→cwe; 40 distinct `_blocked_on` IDs; 34 high / 32 medium / 1 low; all primary; exclusions absent: 1 other-drift + 20 non-CWE + 25 dedupe); COMMIT the artifact immediately (closes Risk 185.1)

**Checkpoint**: Restore-set artifact committed; harvest table ready — user stories can begin.

---

## Phase 3: User Story 1 — The Catalog Gains the Missing CWE Records (Priority: P1) 🎯 MVP

**Goal**: All 40 missing IDs dispositioned; add-set records land in `cwe.yaml` with verbatim v4.20 names — catalog becomes a complete citation-resolution layer (AI CWEs citable).

**Independent Test**: Records alone (no edge changes): integrity suite 5/5 green; catalog 53 → 53+|add-set|; every new ID resolves at its canonical URL; name-diff clean.

- [X] T006 [US1] Architect disposition (gate before catalog edits): verify each of the 40 IDs against harvest-40.md + 8-sentinel live-page spot-checks (CWE-16/255/937/1035/693 + 1426/1427/1039); publish one add/reject/defer line per ID on GitHub Issue #185 with Category/Pillar fidelity-first rationale (lead posture: add-all-40; deprecated → never "add"; note CWE-693 rejection would re-strand a #186-deferred edge); record verdict summary in specs/185-cwe-catalog-expansion/test-results/disposition.md
- [X] T007 [US1] Insert add-set records into schemas/taxonomy/cwe.yaml via scripted lexicographic merge from harvest-40.md — shape `{id, full_id, name, url}`, NO `cwe_refs`/`out_of_scope` keys, URL `https://cwe.mitre.org/data/definitions/<N>.html`, Python string-sort position (`CWE-1035 < CWE-1039 < … < CWE-16 < CWE-201`)
- [X] T008 [US1] Extend schemas/taxonomy/cwe.yaml header comment with the F-A1.2 provenance block (mirroring the 41+11+1 composition note): source = T029 drift-edge targets, Issue #185, cwec v4.20 + retrieval date, Category/Pillar status annotations for CWE-16/255/937/1035 (Categories) + CWE-693 (Pillar)
- [X] T009 [US1] Update schemas/taxonomy/README.md §3.5 — composition, record count 53 → 53+|add-set| (93 add-all), retrieval date, Category/Pillar note
- [X] T010 [US1] US1 gate: `/usr/bin/python3 -m pytest tests/schemas/test_taxonomy_integrity.py -q` → 5/5; record count check (`grep -c "^- id: " schemas/taxonomy/cwe.yaml`); commit records + header + README

**Checkpoint**: Catalog complete — independently verifiable branch checkpoint (MVP increment; single-PR delivery means no partial merge to main) — edges not yet restored.

---

## Phase 4: User Story 2 — The 67 CWE-Blocked Edges Return (Priority: P2)

**Goal**: Every add-set-targeted edge restored byte-exact from the committed artifact; #186's 2-edge deferral closed.

**Independent Test**: With US1 records in place: integrity suite 5/5; crosswalk 578 → 578+|restored| (645/608-primary add-all); field-level diff vs `e58f247` blob shows byte-identity; dedupe checks 0.

- [X] T011 [US2] Insert add-set-targeted edges from specs/185-cwe-catalog-expansion/restored-edges.yaml into schemas/taxonomy/crosswalk.yaml — strip `_blocked_on` working annotations; preserve `edge_type`/`confidence`/`citation` byte-exact (the single `confidence: low` edge `T1070.006 → CWE-1269` stays `low`); BLOCKING pre-insertion re-check: exact-tuple + near-key dedupe vs live crosswalk → 0 collisions (record result in specs/185-cwe-catalog-expansion/test-results/dedupe-check.md)
- [X] T012 [US2] Append the F-185 restoration line to the schemas/taxonomy/crosswalk.yaml header "Edit lineage" block (mirroring the T029/F-186/F-184 entries): +67 edges (or actual), source blob e58f247, Issue #185
- [X] T013 [US2] US2 gate: integrity suite 5/5; edge counts via YAML parse (578→645 total / 541→608 primary, add-all); field-level byte-exactness diff of restored edges vs `git show e58f247:schemas/taxonomy/crosswalk.yaml`; #186-deferred pair present (`T1070.006 → CWE-1269`, `T1562 → CWE-693`); commit edges + lineage

**Checkpoint**: Crosswalk restored — US1 and US2 independently verified.

---

## Phase 5: User Story 3 — Integrity, Report Baselines, and the Decision Trail (Priority: P3)

**Goal**: Byte-identity suite red→green via intentional 6-baseline regen (absorbing inherited #186 ATLAS delta); name correctness proven; every trail surface closed.

**Independent Test**: Full verification set green (integrity 5/5, backward-compat 6/6, name-diff 0 mismatches); trail surfaces inspectable (Issue #185, headers, lineage, README, ADR-037, NEXT-SESSION, CHANGELOG).

- [ ] T014 [US3] Regenerate the 6 gated baselines sequentially per contracts/baseline-regen.contract.md (`SOURCE_DATE_EPOCH=1700000000`; extract → typst compile per example); per-page text diff old-vs-new → deltas confined to CA pages with BOTH expected attributions (cwe 53→93 + inherited mitre-atlas 30→36; percentages may stay 0.00% — denominators/Gap rows are the visible delta); restore templates/tachi/security-report/report-data.typ after final run; evidence in specs/185-cwe-catalog-expansion/test-results/baseline-diff.md; HALT on any non-CA delta (typst drift, Risk R6)
- [ ] T015 [US3] US3 baseline gate: `/usr/bin/python3 -m pytest tests/scripts/test_backward_compatibility.py -q` → 6/6 green (red→green flip vs T001 pre-state); commit the 6 regenerated baselines
- [X] T016 [P] [US3] Write + run specs/185-cwe-catalog-expansion/scripts/name_diff.py — all-(40 or add-set) name comparison of inserted cwe.yaml records vs cwec_v4.20.xml harvest → 0 mismatches (R7 gate; CWE-1039's v4.17 rename is the sentinel case); evidence in specs/185-cwe-catalog-expansion/test-results/name-diff.md
- [X] T017 [P] [US3] Review sweep (code-reviewer): no-excluded-edge-returns check (the 1 other-drift + 20 non-CWE + 25 dedupe edges remain absent from crosswalk.yaml); stale-count grep sweep (`53 record|53-record|578` in docs/ + schemas/ outside specs/, update any found); evidence in specs/185-cwe-catalog-expansion/test-results/review-sweep.md
- [ ] T018 [US3] Docs closure (single commit): CHANGELOG.md `feat(185)` entry (dual-attributing baseline regen: F-185 CWE growth + absorbed #186 ATLAS delta; noting the 2 sample-report baselines stale-by-design); docs/architecture/02_ADRs/ADR-037-…md D-7 annotation (blockquote + Revision History row, prospective-only wording incl. the trigger-taxonomy clause — read architect C3 restatement in .aod/results/architect.md before writing; 5/8 substitution CWEs now cataloged: 307/311/319/326/732); specs/180-taxonomy-crosswalk-collection/NEXT-SESSION.md T029 CWE-blocked residual → resolved by F-A1.2 (alongside the F-A1.3 entry)
- [ ] T019 [US3] Governance trail: PRD v1.2 errata in docs/product/02_PRD/185-cwe-catalog-expansion-2026-06-11.md (FR-006 consequence-scope addition + red-main discovery + revised O/R/P 0.75/1.0/1.5d, per PM + team-lead conditions); KB process-lesson entry via the project's KB pattern (check `ORDERED_FRAMEWORKS` membership for ANY catalog-growth feature at definition time); verify Issue #185 carries 40/40 disposition lines (cross-link T006)

**Checkpoint**: All three stories independently verified; trail complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T020 Final gate: full `/usr/bin/python3 -m pytest tests/ -q` green; `/aod.analyze` clean (SC-006); quickstart.md §0–§6 walkthrough re-run clean; push branch; update draft PR #328 description with counts (records 53→N, edges 578→M, baselines 6, suite red→green) and evidence links

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: none — start immediately; T001 ∥ T002
- **Phase 2 (Foundational)**: T003 ∥ T004 after Setup; T005 after T003 — **T005 commit blocks all production-data edits**
- **Phase 3 (US1)**: T006 after T004 (needs harvest) — runs ∥ T005 (disposition is extraction-independent, plan D5); T007 after T006 (disposition gates inserts) + T002; T008/T009 after T007; T010 gate last
- **Phase 4 (US2)**: T011 after T010 (records before edges — FR-030) + T005 (artifact); T012 after T011; T013 gate last
- **Phase 5 (US3)**: T014 after T013 (baselines capture final data); T015 after T014; T016 ∥ T014 (different files; needs only T007+T004); T017 ∥ T014 (read-only sweep; needs T013); T018 after T015 (CHANGELOG references the flip); T019 after T018
- **Phase 6**: T020 after all

### Critical Path

T001 → T003 → T005 → (T006) → T007 → T010 → T011 → T013 → T014 → T015 → T018 → T019 → T020
(T006 enters the path only until T007; T002/T004 feed it early)

### Parallel Opportunities

- T001 ∥ T002 (setup)
- T003 ∥ T004 (different scripts)
- T005 ∥ T006 (extraction vs disposition — plan D5 twin tracks)
- T016 ∥ T017 ∥ (T014→T015) (name-diff and review-sweep don't touch baseline files)

---

## Parallel Example: User Story 3

```bash
# After T013, launch together:
Task: "T014 regenerate 6 gated baselines per contract"        # senior-backend-engineer
Task: "T016 name_diff.py all-40 vs harvest"                   # tester
Task: "T017 no-excluded-edge-returns + stale-count sweep"     # code-reviewer
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 → Phase 2 (artifact committed = insurance in place)
2. Phase 3 (US1): disposition → records → gate — **catalog is independently shippable** (AI CWEs citable)
3. Validate: integrity 5/5, count check, name spot-checks

### Incremental Delivery

- US1 (records) → US2 (edges) → US3 (baselines + verification + trail) — each gated by its suite run; every intermediate commit keeps `test_crosswalk_referential_integrity` green (FR-030)
- Single-PR delivery (PR #328): catalog growth and baseline regen merge together (contract invariant 4)

### Estimated Effort

O/R/P = **0.75 / 1.0 / 1.5 days** (team-lead revision at tasks review, 2026-06-11 — supersedes the PRD 0.5/0.75/1.0 pin: +FR-006 regen lane ~2.25h realistic, +red-main trail ripple; the floor now also requires first-pass-clean CA-only diffs). Pacing: the timing-dominant entry leg is T002→T004→T006 (corpus → harvest → disposition), not the extraction leg — start T002/T004 first. Typst 0.14.2 verified installed (R6 → LOW); byte-identity suite is local-only (no CI dependency). Task count: 20 (2 setup + 3 foundational + 5 US1 + 3 US2 + 6 US3 + 1 polish).

---

## Notes

- Commit after each gate task (T005, T010, T013, T015, T018) — every commit keeps the integrity suite green
- Any add-set ⊂ 40 from T006 shrinks T007/T011 scope without rework (counts scale; rejected-ID edges stay in the artifact with rationale on Issue #185)
- The cwec zip/xml and extracted PDFs in tmp paths are never committed; committed evidence lives in specs/185-cwe-catalog-expansion/test-results/
- Issue #185 closure itself happens at `/aod.deliver`, not here
