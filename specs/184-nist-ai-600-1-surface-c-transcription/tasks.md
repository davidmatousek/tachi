---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-10
    status: APPROVED
    notes: "0 blocking, 3 advisory. All 8 spec FRs traced across T001–T015 (FR-001→T003, FR-002→T004, FR-003→T007, FR-004→T006, FR-005→T011, FR-006→T008/T012/T014, FR-007→T013+deliver, FR-008→gates); US-1/2/3 phases match spec priorities with MVP = US-1+US-2 at the T009 increment; deliver-time items and the #325 control→rmf extras correctly fenced out of build scope; #185 serialize directive carried; 541/578 forward-guard honored everywhere; the 27→31 spec baseline correction (architect plan-review F1) ACCEPTED. Advisory: F-184 agent-assignments must supersede the stale F-224 .aod copy (done by team-lead). Details: .aod/results/product-manager.md"
  architect_signoff:
    agent: architect
    date: 2026-06-10
    status: APPROVED
    notes: "APPROVED_WITH_CONCERNS instrument (.aod/results/architect.md) recorded as APPROVED per its sign-off position. Plan-stage binding conditions F1 (31-pin on all six surfaces + Issue #325) and F2 (AST byte-untouched check, executed green) re-verified APPLIED and CLOSED. tasks.md contract-exact at every task (C1–C6 1:1, all line anchors re-verified live at 02b63da); dependency order enforces FR-008 at every commit boundary; W2 change-set atomic; commit/[P]/prefix patterns correct. Finding 3 (minor-binding, APPLIED in-line before W4): sweep gate expects TWO historical 542 survivors (crosswalk L14 lineage + README ~L193 F-182 narrative), not one — T014 + quickstart §6 + plan W4 corrected, T012 names README L243 as the composition line and fences L193. Finding 4 nit residuals (spec FR-006 anchors, plan W4 row) also fixed. Details: .aod/results/architect.md"
  techlead_signoff:
    agent: team-lead
    date: 2026-06-10
    status: APPROVED
    notes: "Feasibility APPROVED, no timeline/capacity veto. 15 tasks justified (FR-7 delta over my 12–14 expectation; matches the #182=15 anchor); single-executor serialization honored with [P] only on the three disjoint W4 doc files (isolation, not speedup); critical path T001→T002→W1→W2→T010→W4→T015 sound. W0 pins re-verified live: suite 5/5 via /usr/bin/python3, 542/37/0=579, drift class=16, control→rmf=31, 0 new-class edges. My C2 (#185 serialize), C3 (quoting), C4 (separate sort key), C5 (interpreter pin) all carried as binding directives; 541/578 fully landed (my stale Q3 557/594 correctly superseded). Same-day expectation holds at 0.75–1.0 d realistic / 1.25 d ceiling. F-184 agent-assignments.md authored, superseding stale F-224 copy — ready for /aod.build. Details: .aod/results/team-lead.md"
---

# Tasks: NIST AI 600-1 GAI Risk Taxonomy — Surface C Transcription (F-184)

**Input**: Design documents from `specs/184-nist-ai-600-1-surface-c-transcription/`
**Prerequisites**: plan.md (PM + Architect APPROVED), spec.md (PM APPROVED), research.md, data-model.md, contracts/surface-c-transcription.contract.md (BINDING), quickstart.md

**Tests**: No new test tasks — the existing 5-function integrity suite is the acceptance oracle (spec FR-008; F-182 precedent). Verification tasks run the suite + quickstart checks at every gate.

**Organization**: Tasks grouped by user story; phases map to the plan's W0–W4 waves. Single senior-backend-engineer executor + checkpoint gates (Team-Lead Q3). **All wave gates use 541/578** (the 557/594 figures in `.aod/results/team-lead.md` Q3 predate FR-7 and are superseded).

**Binding references**: contract C1 (12 catalog records) · C2 (15-edge add list) · C3 (16-edge remove list + 31-edge control→rmf no-touch pin) · C4 (8-site test-surgery inventory, `_sort_key_nist` byte-untouched) · C5 (doc surfaces + exemptions) · C6 (oracle). Interpreter pin: `/usr/bin/python3`.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup (W0 — baseline STOP-gate)

**Purpose**: Pin the verified baseline before any edit. STOP if red or drifted.

- [X] T001 Verify baseline integrity suite green: `/usr/bin/python3 -m pytest tests/schemas/test_taxonomy_integrity.py -v` → 5/5 (~1s). Record output in `specs/184-nist-ai-600-1-surface-c-transcription/test-results/w0-baseline.txt`. **STOP-gate**: abort and escalate if not 5/5.
- [X] T002 Pin count baseline per quickstart §2–§3 against `schemas/taxonomy/crosswalk.yaml`: 542 primary / 37 related / 0 superseded = 579 total; drift class `tachi-stride-ai-category → nist-ai-rmf` = exactly 16 matching contract C3 1:1; `tachi-control-category → nist-ai-rmf` = 31 (**do NOT touch — 4 non-table extras are Issue #325's scope**); `→ nist-ai-600-1` = 0. Append to `specs/184-nist-ai-600-1-surface-c-transcription/test-results/w0-baseline.txt`. **STOP-gate**: abort if any count drifts from this PRD/plan-verified state.

**Checkpoint**: Baseline pinned — W1 may begin.

---

## Phase 2: Foundational

**No separate foundational tasks** — User Story 1 (catalog + enum) IS the foundational increment for this feature; the FR-008 ordering invariant (catalog + test surgery land before/with the edge change-set) is enforced by the phase order below. No user story work before Phase 1 completes.

---

## Phase 3: User Story 1 — The Crosswalk Gains the NIST AI 600-1 Catalog (Priority: P1) — MVP foundation (W1)

**Goal**: 8th catalog resolvable + 8-value enum enforced — `nist-ai-600-1` endpoints become formable under referential integrity.

**Independent Test**: Suite 5/5 with 8 catalogs loaded and 0 new edges (valid intermediate state); quickstart §4 catalog checks pass; `_sort_key_nist` byte-identical to main.

### Implementation for User Story 1

- [X] T003 [US1] Author `schemas/taxonomy/nist-ai-600-1.yaml` per contract C1: exactly 12 records §§2.1–2.12 in publication order, shape `{id, full_id, name, url, cwe_refs: []}`, **ids as YAML-quoted strings** `"2.1"`…`"2.12"`, `full_id` form `NIST AI 600-1 §2.X`, all `url: https://doi.org/10.6028/NIST.AI.600-1`, names verbatim from C1 table (incl. §2.6 "Harmful Bias or Homogenization" — or/and divergence documented, routes to OQ-4 delivery note). House-style header comment (model `nist-ai-rmf.yaml`): source + retrieval date 2026-06-10, record shape, **quoted-id rule**, publication-order sort convention, cwe_refs rationale, FR-024 pointer.
- [X] T004 [US1] Execute the full C4 test-surgery inventory in `tests/schemas/test_taxonomy_integrity.py` — all 7 edit sites, nothing else: (1) `CATALOG_FILENAMES` += `"nist-ai-600-1.yaml"`; (2) `TAXONOMY_ENUM` += `"nist-ai-600-1"`; (3) author NEW `_sort_key_section` (`"2.10"` → `(2, 10)`) with docstring; (4) NEW `elif filename == "nist-ai-600-1.yaml"` branch in `test_records_sorted` using `_sort_key_section`; (5) fixture docstring L82 → 8-catalog/count-agnostic; (6) `test_records_sorted` docstring L289 → names the new branch; (7) assert strings L241/L245 → 8-value/count-agnostic. **Site 8 invariant: `_sort_key_nist` code AND docstring BYTE-UNTOUCHED.** No new test functions; `edge_type`/`confidence` enums + `PRIMARY_EDGE_FLOOR` unchanged.
- [X] T005 [US1] W1 gate + single commit: suite 5/5 via `/usr/bin/python3` (8 catalogs, 0 new edges — floor 542≥500 holds); quickstart §4 catalog checks (12 records, string ids, publication order, DOI, empty cwe_refs); quickstart §5 AST extraction check → `_sort_key_nist` byte-identical to main. Record in `test-results/w1-gate.txt`. Commit T003+T004 together as one commit (`feat(184): add nist-ai-600-1 catalog + 8-value enum (W1)`), push.

**Checkpoint**: US-1 independently shippable — 8-catalog world live, no edge changes yet.

---

## Phase 4: User Story 2 — Surface C Becomes 15 Correct Edges, the 16 Wrong Ones Go (Priority: P1) — MVP completion (W2 + W3)

**Goal**: The paired correction as ONE coherent change-set — add the 15 contract edges, empty the 16-edge drift class, keep every other class byte-untouched.

**Independent Test**: quickstart §2 filters → 15 / 0 / 31; §3 arithmetic → (541, 37, 0, 578); suite 5/5; W3 fidelity + diff drift-guard clean.

### Implementation for User Story 2

- [ ] T006 [US2] Remove the 16 drift edges from `schemas/taxonomy/crosswalk.yaml` by **class filter** (`source.taxonomy == tachi-stride-ai-category AND target.taxonomy == nist-ai-rmf`), never line ranges: verify pre-count == 16 and pair-list matches contract C3 1:1 before deleting; verify post-filter empty. The `tachi-control-category → nist-ai-rmf` class (31) and all other classes untouched.
- [ ] T007 [US2] Append the 15 Surface C edges to `schemas/taxonomy/crosswalk.yaml` exactly per contract C2: direction `tachi-stride-ai-category → nist-ai-600-1`, `edge_type: primary`, `confidence: high`, `citation: .claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`, **target ids quoted** (`"2.4"`/`"2.9"`/`"2.10"`/`"2.12"`), edge template shape (no extra keys — suite forbids extras). Under a section comment identifying the F-184 Surface C transcription.
- [ ] T008 [US2] Update `schemas/taxonomy/crosswalk.yaml` header + prose: header taxonomy enum line (L6 `taxonomy (7):` → 8 values incl. `nist-ai-600-1`); edit-lineage counts → 541 primary / 37 related / 0 superseded; retire the mid-file "Surface C DEFERRED" NOTE unit (~L2002–2007 incl. the T028/T029 reconciliation sentence) — replace with a one-line F-184 transcription pointer.
- [ ] T009 [US2] W2 gate + single commit: suite 5/5; quickstart §2 (Surface C = 15 exact contract pairs, drift class = 0, control→rmf = 31); quickstart §3 hard assert (541, 37, 0, 578); no duplicate triples; all 30 new endpoints resolve. Record in `test-results/w2-gate.txt`. Commit T006+T007+T008 as ONE coherent change-set (`feat(184): transcribe 15 Surface C edges, remove 16 drift edges (W2)`), push. **Shippable MVP increment.**
- [ ] T010 [US2] W3 transcription-fidelity + drift-guard review (code-reviewer): (a) all 15 added edges verbatim vs the Surface C table (pair, direction, confidence, citation, quoted ids) and 1:1 vs contract C2; (b) all 16 removals 1:1 vs contract C3 — nothing else removed; (c) **diff drift-guard**: `git diff main -- schemas/taxonomy/crosswalk.yaml` contains ONLY the intended additions/removals/header/NOTE changes; (d) exempt surfaces zero-diff (quickstart §5 block 2); (e) baseline-fixture test green (`tests/scripts/test_init_sh_substitution.py`). Write findings to `test-results/w3-fidelity.md`. **Gate**: any unintended diff line → fix before Phase 5.

**Checkpoint**: US-1 + US-2 complete — the data contract is correct and shippable; only governance docs remain.

---

## Phase 5: User Story 3 — The Schema Change Carries Its Governance Trail (Priority: P2) (W4)

**Goal**: Activation + cleanup auditable in one hop: ADR-027 instrument, README provenance, CHANGELOG disclosure.

**Independent Test**: spec US-3 acceptance scenarios — ADR entry/annotation/blurb in one commit with ratified text byte-unchanged; README §3.8 + 8-stem snippet + 541/37/0; quickstart §6 sweep clean (one expected F-186 lineage survivor).

### Implementation for User Story 3

- [ ] T011 [P] [US3] ADR-027 governance instrument in ONE commit (binding OQ-3 conditions): (a) dated Revision History entry in `docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md` self-describing as the Decision 3 extension-governance instrument, citing PRD-184, Issue #184, the Architect sign-off, 8-value activation, 12-record catalog, 15-edge transcription, FR-022 direction correction, AND the FR-7 16-edge removal disposition (T027 → T029 Option (d) MIX survivors → removed here); (b) one-line additive annotation under the Decision 3 heading ("Amended at F-184: enum extended to 8 values — see Revision History") — ratified text above it byte-unchanged; (c) `docs/architecture/README.md` ~L54 ADR-027 blurb gains "extended to 8 values at F-184, see Revision History". Architect reviews entry text at the build checkpoint.
- [ ] T012 [P] [US3] `schemas/taxonomy/README.md` per contract C5: NEW §3.8 provenance (DOI source, 12-record composition, retrieval date 2026-06-10, cwe_refs rationale, quoted-id + sort convention, Gap-row omission note incl. §2.9×Spoofing no-first-`low` rationale); §1 snippet tuple → 8 stems; §2 bullet 3 amendment note (Surface C deferred at F-180 → transcribed at F-184 as 15 edges direction-corrected, 16 legacy drift edges removed; corrects the stale "(14) … 41 edges" text); edge-type composition statement at **L243** ("…still governs the 542 `primary` edges") → 541/37/0; L13 "seven taxonomies" → eight; L20 "9 files" → 10. **Do NOT edit L193** ("the 542-edge primary graph") — F-182 yield-tripwire historical narrative, a true statement about F-182's build-start state.
- [ ] T013 [P] [US3] `CHANGELOG.md` hand-curated Unreleased section: `feat(184)` entry naming BOTH the additions (8th catalog `nist-ai-600-1.yaml`, 12 GAI Risk records; 15 Surface C primary edges, direction-corrected per FR-022) AND the removal (16 legacy `tachi-stride-ai-category → nist-ai-rmf` drift edges — T027 directive completed; 542→541 primary / 579→578 total). Do NOT touch release-please sections or lingering Unreleased entries (dual-CHANGELOG model).
- [ ] T014 [US3] W4 sweep gate: quickstart §6 grep over the inventory surfaces (`7-value|7 catalog|seven taxonom|taxonomy (7)|542|(14)`) → **exactly TWO expected historical survivors** remain: the crosswalk-header F-186 lineage line `(526 -> 542)` (L14) and the README §4.1 yield-tripwire narrative "the 542-edge primary graph" (~L193, F-182 build-start state) — any other hit is a sweep failure; exempt surfaces zero-diff (`docs/architecture/01_system_design/README.md`, `specs/180-*`, ADR-025/028 bodies, historical PRDs); suite still 5/5. Record in `test-results/w4-sweep.txt`. Commit T011–T013 (T011 as its own commit per the one-commit OQ-3 condition; T012+T013 may share a commit), push.

**Checkpoint**: All three user stories complete.

---

## Phase 6: Polish & Pre-PR Gate

- [ ] T015 Full pre-PR verification: `/usr/bin/python3 -m pytest tests/schemas/ tests/scripts/test_init_sh_substitution.py -q` all green; run `/aod.analyze` (cross-artifact consistency — spec/plan/tasks); verify draft PR #324 title still conventional (`feat(184): …`); push all commits; update PR body checklist with completed scope. Record in `test-results/final-gate.txt`. **Deliver-time items are NOT tasks here**: Issue #184 `stage:done` closure + OQ-4 ADR-025 one-line amendment note (incl. §2.6 or/and observation) + PR ready/squash-merge happen at `/aod.deliver`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (W0)**: No dependencies — start immediately. STOP-gates protect everything downstream.
- **Phase 3 / US-1 (W1)**: Requires Phase 1. **Blocks US-2** (referential integrity: edges need the catalog + enum).
- **Phase 4 / US-2 (W2+W3)**: Requires US-1 complete (FR-008 ordering invariant).
- **Phase 5 / US-3 (W4)**: Requires US-2 complete (governance docs cite the shipped 541/37/0 state).
- **Phase 6**: Requires all stories complete.

### Task Dependencies

```
T001 → T002 → [T003 → T004 → T005] → [T006 → T007 → T008 → T009 → T010] → [T011 ∥ T012 ∥ T013 → T014] → T015
        W0            W1 (one commit)            W2 (one commit)  W3              W4 [P]                    gate
```

T003/T004 are sequential-by-convention (same logical change, one commit at T005); T006–T008 are one coherent change-set (single file, one commit at T009). T011/T012/T013 are genuinely parallel `[P]` (three disjoint files) but serialize on the single executor — parallelism is isolation, not speedup (Team-Lead Q3 / #186 lesson).

### Parallel Opportunities

- T011 ∥ T012 ∥ T013 (different files: ADR-027+arch README / taxonomy README / CHANGELOG).
- Everything else is intentionally serialized: one executor, one shared file pair (`crosswalk.yaml` + test), checkpoint gates between waves.

---

## Implementation Strategy

**MVP = US-1 + US-2** (Phases 1–4): the data contract is correct, integrity-green, and shippable at the T009 commit; T010 hardens it. US-3 (Phase 5) is required before the PR is marked ready (the enum change is invalid without its ADR-027 instrument — spec FR-005) but is not needed to validate the data increment.

**Incremental checkpoints**: every wave gate (T001/T002, T005, T009, T010, T014, T015) is a STOP-and-validate point; suite must be 5/5 at every commit boundary (FR-008).

**Scheduling directives (binding)**:
- **Serialize #185** (Team-Lead C2): do not start #185's build mid-#184 — `crosswalk.yaml`, `schemas/taxonomy/README.md`, `CHANGELOG.md` are shared surfaces.
- **Do NOT touch** the 4 control→rmf non-table extras (Issue #325) or any exempt surface (contract C5).
- Effort envelope 0.75–1.25 d; realistic 0.75–1.0 d; expect same-day (Team-Lead calibration).

---

## Notes

- Single executor: senior-backend-engineer for T001–T009, T011–T013, T015; code-reviewer for T010; tester validates gates T009/T014 outputs (see agent-assignments.md).
- Commit after each wave gate (not each task): W1 = 1 commit, W2 = 1 commit, W4 = 2 commits (T011 alone; T012+T013), plus T010/T015 result files with the nearest commit.
- All commits `feat(184): …` or `docs(184): …` per conventional-commit standards; PR #324 title stays `feat(184): …`.
- Avoid: editing `_sort_key_nist`, touching exempt surfaces, removing the 4 #325 edges, splitting the W2 change-set, folding deliver-time actions into build.
