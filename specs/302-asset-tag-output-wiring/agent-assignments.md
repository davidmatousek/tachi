# Agent Assignments: Asset-Tag Output Wiring (F-260b)

**Feature**: 302-asset-tag-output-wiring
**Branch**: `302-asset-tag-output-wiring` | **Date**: 2026-05-30
**Tasks**: [tasks.md](tasks.md) (T001-T022, 8 phases) — triple-signed-off (PM APPROVED / Architect APPROVED / Team-Lead APPROVED_WITH_CONCERNS, both MEDIUMs folded)
**Plan**: [plan.md](plan.md) (AD-1 Design A production-tier; critical path)
**Feasibility**: APPROVED — ~3-4 working days realistic; build window 2026-06-01 (Mon) → 2026-06-11 (Thu) ceiling = ~9 working days → ~5 working-days residual slack. Design B fallback NOT triggered.

**Agent names**: validated against `.claude/agents/_README.md` (13-agent registry). Only canonical `subagent_type` values used.

---

## 1. Agent Assignment Matrix

This is an instrumentation-harness project: Python scripts (stdlib-only, PAT-014) + YAML schemas + markdown references/templates + LLM agent-prose authoring contracts. Per registry fallbacks, markdown/YAML/Python authoring → **senior-backend-engineer**; test design + acceptance/live verification → **tester**; the governance ADR → **architect** (system-design decision record).

| Task | Phase | [P] | Story | Agent | Rationale |
|------|-------|-----|-------|-------|-----------|
| T001 | 1 Setup | — | — | **tester** | Capture pre-change SC-002 byte-identity "before" snapshot under `SOURCE_DATE_EPOCH`; verification-baseline action, not feature code. |
| T002 | 2 Foundational | [P] | — | **senior-backend-engineer** | YAML schema edit: `affected_assets` enum-array field + `schema_version` 1.8→1.9 + governance comment in `schemas/finding.yaml`. |
| T003 | 2 Foundational | [P] | — | **architect** | ADR-046 records the LLM-vs-Python tier-boundary + production-tier election + test-checked NFR-3 — an architecture decision record (HOW). |
| T004 | 2 Foundational | [P] | — | **senior-backend-engineer** | Define the always-present `affected_assets` block contract in `finding-format-shared.md` + `threats.md` template (the contract all downstream code implements). |
| T005 | 3 US-2 | — | US2 | **senior-backend-engineer** | Implement the deterministic populator (Python, value authority) joining `parse_component_asset_map` → findings, writing the `threats.md` block. |
| T006 | 3 US-2 | — | US2 | **senior-backend-engineer** | Wire the populator into the production pipeline (sequencing step) in `tachi.threat-model.md` + `tachi.risk-score.md` command flows (AD-1 M-2). |
| T007 | 3 US-2 | [P]* | US2 | **tester** | Populator unit tests (SC-003/SC-005 + fuzzy match + Q4 semantic + sorted/dedup + UNCHANGED/RESOLVED) in `test_affected_assets_wiring.py`. |
| T008 | 4 US-1 | — | US1 | **senior-backend-engineer** | Shared `parse_affected_assets()` extractor in `sarif_common.py` (single source for the verification tier; mirrors `parse_component_metadata`). |
| T009 | 4 US-1 | [P] | US1 | **senior-backend-engineer** | Add snake_case `result.properties.affected_assets` to `generate-threats-sarif.py`, sourced from the extractor (FR-004 verification). |
| T010 | 4 US-1 | [P] | US1 | **senior-backend-engineer** | Add snake_case `result.properties.affected_assets` to `generate-risk-scores-sarif.py`, sourced from the extractor (FR-004 verification). |
| T011 | 4 US-1 | — | US1 | **senior-backend-engineer** | Update production LLM authoring contract in `sarif-specification.md` (orchestrator → `threats.sarif`, snake_case copy-verbatim). Authoring-text edit. |
| T012 | 4 US-1 | — | US1 | **senior-backend-engineer** | Update production LLM authoring contract in `risk-scorer.md` SARIF section (risk-scorer → `risk-scores.sarif`); §3.5 + 9.2 ceiling UNCHANGED. Authoring-text edit. |
| T013 | 4 US-1 | —* | US1 | **tester** | Cross-format consistency test (SC-006): per-finding equality table across `threats.md` block + both SARIF generators in `test_affected_assets_wiring.py`. |
| T014 | 5 US-4 | [P] | US4 | **senior-backend-engineer** | Extend `asset-modifiers.md` with an Output Contract section + correct the stale "9.5"→"9.2" in the T-2 example (must NOT touch `risk-scoring.yaml`). |
| T015 | 5 US-4 | [P] | US4 | **senior-backend-engineer** | Add the `affected_assets` contract pointer to `schemas/README.md` (FR-007). |
| T016 | 5 US-4 | — | US4 | **tester** | Regenerate no-tag baselines under `SOURCE_DATE_EPOCH`; verify `git diff` is additive-only, all existing rows byte-identical (SC-002 / AD-2). |
| T017 | 5 US-4 | —* | US4 | **tester** | Schema-doc accuracy (SC-007) + ceiling-preservation (SC-004) tests in `test_affected_assets_wiring.py`. Serializes on shared test file. |
| T018 | 5 US-4 | — | US4 | **tester** | `[MANUAL-ONLY]` live-pipeline verification (R9): real `tachi.threat-model` run confirming `affected_assets` in `threats.md` + both `.sarif` — acceptance gate. |
| T019 | 6 US-3 | — | US3 | **senior-backend-engineer** | Add `CHANGELOG.md` `feat(302):` entry + @north-echo prototype-author attribution (NEVER "surfaced by") + Discussion #246 ref + `Co-Authored-By` trailer. |
| T020 | 8 Polish | [P] | — | **senior-backend-engineer** | CI wiring: add both test files to `paths:` + `pytest` invocation in `.github/workflows/tachi-pytest.yml` (lock-step, F-256 lesson). |
| T021 | 8 Polish | — | — | **tester** | Frozen-constraint gate (SC-011): assert `git diff main` shows NO change to `VALID_ASSET_TAGS`, `modifier_ceiling: 9.2`, ordering, or `risk-scoring.yaml` version. |
| T022 | 8 Polish | — | — | **tester** | Run full `quickstart.md` validation (SC-001…SC-012); confirm 26-case suite + new suite green in CI; NFR-2 score-equivalence holds. |

`*` = the tasks.md `[P]` marker is constrained by shared-file serialization — see Wave notes and §2.

**Distribution**: senior-backend-engineer 13 (T002, T004, T005, T006, T008, T009, T010, T011, T012, T014, T015, T019, T020) · tester 8 (T001, T007, T013, T016, T017, T018, T021, T022) · architect 1 (T003). No agent exceeds the 80% single-wave load ceiling (max concurrent per wave is 2× senior-backend-engineer; serialized where files collide).

---

## 2. Parallel Execution Waves

Waves honor the AD-1 dependency chain and the **shared-test-file serialize-on-write rule** (team-lead M-2 / architect LOW-2): T007, T013, T017 all append to `tests/scripts/test_affected_assets_wiring.py` and MUST NOT run concurrently with each other — they land in *different waves* by their natural phase ordering, which resolves the collision cleanly.

### Wave 0 — Setup (blocking snapshot)
- **T001** (tester) — pre-change byte-identity baseline snapshot.
- *No parallelism (single task).* Must complete before baselines are touched (gives SC-002 its "before").

### Wave 1 — Foundational (all parallel, different files)
- **T002** (senior-backend-engineer) ∥ **T003** (architect) ∥ **T004** (senior-backend-engineer)
- True 3-way parallel — schema field, ADR-046, block contract are independent files. **Blocks Phases 3-8.**

### Wave 2 — US-2 populator core (serial pair)
- **T005** (senior-backend-engineer) → **T006** (senior-backend-engineer)
- T005 (populator) needs T002+T004; T006 (pipeline sequencing) needs T005. Serial — same author, dependent steps.

### Wave 3 — US-2 validation + US-1 extractor (parallel)
- **T007** (tester) ∥ **T008** (senior-backend-engineer)
- T007 (populator unit tests) needs T005; T008 (shared extractor) needs T004. Different files (test file vs `sarif_common.py`) → parallel. **First write to `test_affected_assets_wiring.py`.**

### Wave 4 — US-1 SARIF emitters + production authoring (parallel)
- **T009** (senior-backend-engineer) ∥ **T010** (senior-backend-engineer) ∥ **T011** (senior-backend-engineer) ∥ **T012** (senior-backend-engineer)
- All four need only T008/T004 and touch distinct files (`generate-threats-sarif.py`, `generate-risk-scores-sarif.py`, `sarif-specification.md`, `risk-scorer.md`). T011/T012 are authoring-text edits (runtime verified later by T016/T018). Strong parallel batch.

### Wave 5 — US-1 cross-format gate + US-4 docs (parallel)
- **T013** (tester) ∥ **T014** (senior-backend-engineer) ∥ **T015** (senior-backend-engineer)
- T013 (SC-006 cross-format) needs T009+T010; docs T014/T015 need only T004. Distinct files. **Second write to `test_affected_assets_wiring.py`** — safe because Wave 3's T007 has fully completed.

### Wave 6 — US-4 baseline regen + schema-doc/ceiling tests (parallel)
- **T016** (tester) ∥ **T017** (tester)
- T016 (baseline regen, SC-002) needs T005/T006/T011/T012; T017 (SC-007 + SC-004) needs T014. Distinct files (example baselines vs the test file). **Third write to `test_affected_assets_wiring.py`** — safe because Wave 5's T013 has completed. T016 regenerates `examples/agentic-app` baselines, no collision.

### Wave 7 — US-4 live verification (manual gate)
- **T018** (tester) — `[MANUAL-ONLY]` live `tachi.threat-model` run.
- Needs T006/T011/T012 (all complete by Wave 5). Isolated because it is a human/agent LLM-pipeline invocation, not a unit test — R9 "shipped, adopters see nothing" gate.

### Wave 8 — US-3 CHANGELOG + Polish (parallel where independent)
- **T019** (senior-backend-engineer, CHANGELOG) ∥ **T020** (senior-backend-engineer, CI wiring)
- T019 needs wiring done (any time after); T020 needs the test files to exist (T007/T013/T017 done). Distinct files (`CHANGELOG.md` vs the workflow YAML) → parallel.

### Wave 9 — Final gates (serial)
- **T021** (tester) → **T022** (tester)
- T021 (frozen-constraint binary diff, SC-011) then T022 (full `quickstart.md` validation, SC-001…SC-012 + CI green + NFR-2). T022 is the closing acceptance gate — it depends on everything, including T020's CI wiring.

**Delivery-time tails (NOT feature-branch waves)**: per tasks.md Phase 6/7, FR-011c Discussion #246 ack comment + offered `Co-Authored-By`, FR-012 issue closes (#302/#260 completing #246→#262→#260→#302), and FR-010/SC-009 release-please verify all execute at `/aod.deliver`, not in these build waves.

---

## 3. Quality Gates Between Waves

| Gate | After Wave | Criterion | Owner |
|------|-----------|-----------|-------|
| **G0 — Snapshot recorded** | 0 | Pre-change `threats.md`/`threats.sarif`/`risk-scores.sarif` captured under `SOURCE_DATE_EPOCH=1700000000`; 4 tagged components confirmed (SC-002 "before"). | tester |
| **G1 — Contract frozen** | 1 | Schema 1.9 field present; ADR-046 committed; `affected_assets` block contract defined. Populator + SARIF work unblocked. | architect / senior-backend-engineer |
| **G2 — US-2 independently testable** | 3 | `threats.md` carries deterministic `affected_assets` (populated where tagged, `[]` otherwise); populator unit tests green (SC-003/SC-005). | tester |
| **G3 — SC-006 cross-format equality** | 5 | Per-finding values byte-identical across `threats.md` block + both SARIF generators, incl. untagged `[]`; identical `affected_assets` key string. | tester |
| **G4 — SC-002 byte-identity** | 6 | `git diff` on regenerated no-tag baselines shows ONLY the additive `affected_assets` block/property; all existing table rows byte-identical (AD-2). | tester |
| **G5 — R9 live propagation** | 7 | Real `tachi.threat-model` on the tagged worked example shows `affected_assets` in `threats.md` AND `threats.sarif` AND `risk-scores.sarif` (not just regeneration scripts). | tester |
| **G6 — SC-011 frozen-constraint** | 9 (T021) | `git diff main` shows NO change to `VALID_ASSET_TAGS`, `modifier_ceiling: 9.2`, modifier-after-clamp ordering, or `risk-scoring.yaml` `schema_version` (stays 1.1). | tester |
| **G7 — Full acceptance** | 9 (T022) | `quickstart.md` SC-001…SC-012 pass; 26-case suite + `test_affected_assets_wiring.py` green in CI; NFR-2 score-equivalence vs v4.31.0 worked example holds. | tester |

Standard `/aod.build` post-wave checkpoints (Design Quality Gate Step 6 is **N/A** — no UI; Security Scan Step 7 applies to the new Python populator/extractor) run per the command pipeline.

---

## 4. Time Estimates Per Wave

Build window: 2026-06-01 (Mon) → 2026-06-11 (Thu) ceiling = ~9 working days. Team-lead-validated effort **~3-4 working days**. Estimates below are conservative working-hours (8h/day) and sum within that envelope.

| Wave | Tasks | Est. (hrs) | Cumulative | Notes |
|------|-------|-----------|-----------|-------|
| 0 | T001 | 1.5 | 0.2 d | Snapshot + tag confirmation. |
| 1 | T002, T003, T004 | 4.0 (parallel; ~2.5h longest path) | 0.5 d | 3-way parallel; ADR-046 (T003) is the longest single item. |
| 2 | T005, T006 | 7.0 | 1.4 d | Populator (T005) is the net-new core — the heaviest single item (~5h); pipeline sequencing (T006) ~2h. |
| 3 | T007, T008 | 4.0 (parallel; ~2.5h longest path) | 1.7 d | Unit tests ∥ extractor. |
| 4 | T009, T010, T011, T012 | 5.0 (parallel; ~2h longest path) | 1.9 d | Four-way parallel; emitters + two authoring-text edits. |
| 5 | T013, T014, T015 | 4.0 (parallel; ~3h longest path) | 2.3 d | SC-006 cross-format test is the longest path. |
| 6 | T016, T017 | 4.0 (parallel; ~3h longest path) | 2.6 d | Baseline regen + diff inspection ∥ schema-doc/ceiling tests. |
| 7 | T018 | 2.0 | 2.9 d | `[MANUAL-ONLY]` live LLM-pipeline run + 3-surface confirmation. |
| 8 | T019, T020 | 3.0 (parallel; ~2h longest path) | 3.1 d | CHANGELOG ∥ CI wiring. |
| 9 | T021, T022 | 4.0 | 3.6 d | Frozen-diff gate → full quickstart acceptance (depends on all). |

**Total: ~3.6 working days** (serialized critical path; parallelism within waves keeps wall-clock under the ~3-4 day estimate). Against the ceiling: ~3.6 days effort vs ~9 working-days window → **~5 working-days residual slack**. Comfortably within 2026-06-11; Design B fallback not required.

**Critical path** (plan §Critical Path): T002/T004 → T005 → T006 → T011/T012 → T016 + T018 → T022. T013 is the SC-006 correctness gate; T021 is the SC-011 frozen-constraint gate.

---

## 5. Handoff to Orchestrator

- **Feasibility**: APPROVED (~3-4 working days within the 2026-06-11 ceiling; ~5 days slack).
- **tasks.md**: `specs/302-asset-tag-output-wiring/tasks.md` — triple-signed-off, T001-T022.
- **Wave strategy**: 10 waves (Wave 0-9) above; honor the dependency chain and the shared-test-file serialize-on-write rule.
- **Critical serialization rule**: T007 (Wave 3) → T013 (Wave 5) → T017 (Wave 6) MUST land in their separate waves — all three append to `tests/scripts/test_affected_assets_wiring.py`; never run them concurrently.
- **Frozen constraints**: `scripts/tachi_parsers.py` and `schemas/risk-scoring.yaml` are READ-ONLY (SC-011 gate, T021). Populator records provenance only — never re-scores; 9.2 ceiling untouched.
- **Delivery-time exclusions**: do NOT execute the Discussion #246 ack, issue closes (#302/#260), or release-please verify in build — they belong to `/aod.deliver`.
