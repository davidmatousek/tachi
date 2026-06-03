# Agent Assignments: F-315 — MAESTRO Output Completeness (Round 2)

**Feature**: Infographic completeness (US1 / #312) + CI durability & non-gated PDF refresh (US2 / #313)
**Tasks source**: `specs/315-maestro-output-completeness-round-2/tasks.md` (T001–T020, 5 phases)
**Feasibility**: APPROVED (triple sign-off complete — PM APPROVED_WITH_CONCERNS, Architect APPROVED_WITH_CONCERNS, Team-Lead APPROVED)
**Carve-out**: PRD/GitHub US-1 (Model B, #311) is NOT in scope — do not re-enter.
**Agent names**: every `subagent_type` below is an exact entry from `.claude/agents/_README.md` Agent Roster. No generic labels used.

---

## 1. Agent Assignment Matrix

Every task T001–T020 mapped to exactly one execution agent (valid registry name).

| Task | Story | Description (abbrev) | Agent (`subagent_type`) | Rationale |
|------|-------|----------------------|-------------------------|-----------|
| T001 | Setup | Verify toolchain (Python/pytest + Typst/mmdc); note absences in quickstart | `devops` | Environment/toolchain readiness is infra-engineer scope |
| T002 | Setup | Record green baseline (invariant + backward-compat pytest runs) | `tester` | Pre-change quality baseline / test execution |
| T003 | US1 | Author NEW partial-MAESTRO fixture (`maestro_partial/`: arch input + 3-of-7 table) | `senior-backend-engineer` | Fixture is structured test data tightly coupled to extractor payload shape |
| T004 | US1 | Extend `test_extract_infographic_data.py` — assert 3 keys, sum==7, mixed + all-empty, byte-identity; confirm FAIL | `senior-backend-engineer` | Authoring extractor assertions against internal payload; same engineer as T003/T005 minimizes context handoff |
| T005 | US1 | Edit `scripts/extract-infographic-data.py` maestro-stack block — backfill 7 layers + 3 counts (local block ONLY) | `senior-backend-engineer` | Python implementation, source-of-truth extractor logic |
| T006 | US1 | Regenerate golden `maestro-stack.json`; confirm `maestro-heatmap.json` UNCHANGED | `senior-backend-engineer` | Golden regen via the extractor; FR-004 heatmap-protection check |
| T007 | US1 | Add directive line in `.claude/agents/tachi/threat-infographic.md` (placeholders from JSON) | `senior-backend-engineer` | Agent-directive markdown authoring; pairs with extractor contract |
| T008 | US1 | EITHER emit `most_exposed_count` (same block, depends T005) OR add code comment (independent). Default: documentation branch | `senior-backend-engineer` | Same `template_data` block as T005; emit branch is a same-file edit — must be same engineer |
| T009 | US1 | Run `test_extract_infographic_data.py` → green; determinism + heatmap-unchanged verification | `tester` | Independent verification / acceptance run after implementation |
| T010 | US2 | Create `.github/workflows/tachi-maestro-coverage.yml` (Python 3.11 job; `paths:` per contract); do NOT touch `tachi-pytest.yml` | `devops` | CI workflow YAML authoring is infra-engineer scope |
| T011 | US2 | Remove "intentionally NOT wired into CI" docstring note from invariant test | `senior-backend-engineer` | Source-file docstring edit on the test module |
| T012 | US2 | Verify: invariant green; negative test (delete one layer row → fails naming layer); unrelated change does not trigger job | `tester` | Negative-test + CI-trigger verification |
| T013 | US2 | Drift audit of 5 non-gated example PDFs; classify drift; finalize confirmed-drift set; record in PR | `devops` | Toolchain-heavy binary/PDF drift audit (cmp/git compare); infra scope |
| T014 | US2 | Regenerate confirmed-drift PDFs (populate-maestro-coverage + `SOURCE_DATE_EPOCH`); leave gated `.baseline` untouched | `devops` | Deterministic PDF regen (Typst+mmdc toolchain); infra scope |
| T015 | US2 | [MANUAL-ONLY] Diff each regenerated PDF/baseline — confirm ONLY MAESTRO churn, no unrelated drift | `tester` | Manual-diff verification of regen output |
| T016 | US2 | Verify 6 byte-gated baselines unchanged (`test_backward_compatibility.py` green); `BASELINE_EXAMPLES` not expanded | `tester` | Gated byte-check / quality validation |
| T017 | Polish | Add `CHANGELOG.md` `feat(315)` entry (US-2 + US-3; note US-1 Model B → #311) | `senior-backend-engineer` | Repo-doc authoring grouped with the implementation work |
| T018 | Polish | Run `/aod.analyze` cross-artifact consistency (spec ↔ plan ↔ tasks); resolve drift | `tester` | Cross-artifact consistency validation |
| T019 | Polish | Run `quickstart.md` end-to-end validation (both stories; SC-001…SC-007) | `tester` | Acceptance / end-to-end verification |
| T020 | Polish | DoD checklist + delivery gate (`Closes #312 #313`; merge #314; verify release-please PR) | `product-manager` | Delivery-gate / scope-closure governance is PM authority |

**Agents used (6 distinct)**: `senior-backend-engineer`, `tester`, `devops`, `product-manager`.
*(4 distinct named — listed as 6 references collapse to 4 unique agents. Workload spans 4 of the 13 registry agents; no agent overloaded.)*

---

## 2. Parallel Execution Waves

Honors: **US1 ∥ US2 as one wave**; within-US1 chain `T003→T004→T005→T006→T009`; within-US2 chains `T010∥T011→T012` and `T013→T014→T015∥T016`. T008 emit-branch folded to depend on T005 (Architect MEDIUM-1) — scheduled on the same engineer track as T005/T006, never parallel with T005.

### Wave 0 — Setup (Shared)
Confirm toolchain + capture starting baseline before any edits.

| Task | Agent | Parallel? |
|------|-------|-----------|
| T001 | `devops` | runs first (toolchain gate) |
| T002 | `tester` | `[P]` — independent baseline capture |

> T001 and T002 are independent (T002 is marked `[P]`); they may run concurrently. T002's green result is the reference for later byte/determinism checks.

### Wave 1 — US1 ∥ US2 (the single combined parallel wave; disjoint file sets)

This is the one parallel wave the tasks file mandates. Within it, three independent tracks run concurrently; each track is internally sequential per its dependency chain.

**Track A — US1 infographic completeness (#312), `senior-backend-engineer`** *(sequential chain)*
```
T003 (fixture)
  → T004 (failing tests, depends T003)
    → T005 (extractor edit, depends T004)
      → T006 (regen maestro-stack golden; heatmap unchanged, depends T005)
      → T008 emit-branch (same block, depends T005)   [or documentation branch — independent]
        → T009 (tester verify: green + determinism + heatmap intact, depends T005,T006)
T007 (threat-infographic.md directive)  — [P], independent; any point in Track A
```

**Track B — US2 CI gate (#313), `devops` + `senior-backend-engineer`**
```
T010 (devops: tachi-maestro-coverage.yml)   ∥   T011 (s-b-e: drop "not wired" docstring)
  → T012 (tester: invariant green + negative test + non-trigger check; depends T010,T011)
```

**Track C — US2 non-gated PDF refresh (#313), `devops` + `tester`** *(sequential chain)*
```
T013 (devops: drift audit, finalize confirmed-drift set)
  → T014 (devops: regen confirmed-drift PDFs; gated .baseline untouched; depends T013)
    → T015 (tester: MANUAL-ONLY diff — only MAESTRO churn; depends T014)
    ∥ T016 (tester: 6 gated baselines byte-identical; BASELINE_EXAMPLES not expanded; depends T014)
```

> Tracks A, B, C touch disjoint files and run fully concurrently. T009 (tester) gates Track A close; T012 gates Track B close; T015∥T016 gate Track C close.

### Wave 2 — Polish & Cross-Cutting (after BOTH stories complete)

| Task | Agent | Parallel? | Depends on |
|------|-------|-----------|------------|
| T017 | `senior-backend-engineer` | `[P]` — CHANGELOG | Wave 1 complete |
| T018 | `tester` | sequential — `/aod.analyze` then resolve drift | Wave 1 complete |
| T019 | `tester` | after T017/T018 settle (full e2e) | Wave 1 complete; T017,T018 |
| T020 | `product-manager` | last — DoD + delivery/release gate | T019 green |

> T017 (`[P]`) may run alongside T018. T019 (full quickstart e2e) should follow once CHANGELOG + analyze drift are settled. T020 is the terminal delivery-gate sign-off.

---

## 3. Quality Gates

Between-wave gates the orchestrator must enforce before advancing.

| Gate | After | Pass condition | Owner | Action on fail |
|------|-------|----------------|-------|----------------|
| **G0 — Baseline green** | Wave 0 | T002: invariant test green (all examples 7-row) AND backward-compat green (6 gated baselines byte-identical). Toolchain status recorded (mmdc/Typst presence noted for T014–T016). | `tester` | STOP — do not edit until baseline is green and toolchain documented |
| **G1a — US1 closed** | Wave 1 Track A | T004 failed pre-impl then passes post-impl; T009 green; extract-twice byte-identical; `maestro-heatmap` golden/output UNCHANGED (FR-004). | `tester` | Return to `senior-backend-engineer`; do not mark US1 done |
| **G1b — US2 CI gate closed** | Wave 1 Track B | T012: invariant green locally; negative test fails naming the missing layer ID; unrelated-file change does NOT trigger job; `tachi-pytest.yml` untouched. | `tester` | Return to `devops`/`s-b-e`; fix `paths:` ⇄ invocation lock-step |
| **G1c — US2 PDF refresh closed** | Wave 1 Track C | T015: only MAESTRO row/order churn, no unrelated binary drift; T016: 6 byte-gated baselines byte-identical, `BASELINE_EXAMPLES` not expanded (Q-D1); gated `maestro-reference/.baseline` untouched. | `tester` | Return to `devops`; re-run regen under `SOURCE_DATE_EPOCH=1700000000` |
| **G1 — Both stories done** | Wave 1 | G1a AND G1b AND G1c all pass; no `.aod/` modifications. | `team-lead` | Block Wave 2 |
| **G2 — Delivery ready** | Wave 2 | T018 `/aod.analyze` clean (no spec↔plan↔tasks drift); T019 quickstart e2e passes SC-001…SC-007; T017 CHANGELOG present; T020 DoD checklist satisfied; delivery PR will `Closes #312 #313`, release PR #314 merged/aligned, release-please PR verified. | `product-manager` | Resolve drift / fix DoD gaps before `/aod.deliver` |

**Hard invariants (enforced at every gate)**
- Never modify shared `extract_maestro_data` (FR-004 / heatmap payload) — T005 is block-local only.
- Never expand `BASELINE_EXAMPLES`; never touch `maestro-reference/.baseline`.
- Never touch `tachi-pytest.yml`.
- Zero #311 / Model-B re-entry.
- No `.aod/` modifications during execution.

---

## 4. Time Estimates (effort-based — NO calendar dates)

Calendar dates are deferred per Team-Lead sign-off (CALENDAR PASS — no concrete dates asserted). Estimates are relative effort and wave wall-clock under parallel execution.

| Wave | Tasks | Critical path (longest track) | Relative effort | Wall-clock (parallel) |
|------|-------|-------------------------------|-----------------|------------------------|
| **Wave 0 — Setup** | T001, T002 | T001 toolchain check ∥ T002 baseline run | XS | ~1 unit (concurrent) |
| **Wave 1 — US1 ∥ US2** | T003–T009, T010–T016 | **Track C** `T013→T014→T015/T016` (PDF regen, Typst+mmdc-gated) ≈ Track A `T003→T004→T005→T006→T009` | L (dominant wave) | ~3 units (longest of A/B/C; B is shortest) |
| **Wave 2 — Polish** | T017–T020 | `T018→T019→T020` (T017 `[P]` overlaps) | M | ~1.5 units |

**Effort legend**: XS < S < M < L (relative t-shirt sizing, not hours/days).

**Critical-path notes**
- The feature's critical path runs through **Wave 1 Track C** (drift audit → PDF regen → manual+gated verification): toolchain-gated and inherently sequential. Track A (US1) is comparable in length; Track B (CI gate) is the shortest and will idle first.
- If `mmdc`/Typst are absent (flagged at T001/G0), Track C (T014–T016) is **blocked**; US1 (Track A) + US2 CI gate (Track B) still ship independently — MVP (US1 / #312) remains independently shippable per PM sign-off.
- Capacity: only release PR #314 and draft #316 are open; no contention. Workload spans 4 of 13 registry agents — no single agent exceeds the 80% load ceiling.

---

## 5. Handoff to Orchestrator

- **Feasibility**: APPROVED (triple sign-off recorded in `tasks.md` front-matter).
- **Wave strategy**: Wave 0 (setup) → Wave 1 (US1 ∥ US2, three concurrent tracks) → Wave 2 (polish). One mandated parallel wave (US1 ∥ US2).
- **Assignments**: per the Matrix (Section 1) — use exact `subagent_type` values.
- **Gates**: enforce G0 → G1a/G1b/G1c → G1 → G2 (Section 3) before advancing each boundary.
- **Return expectation**: completion report with per-task status, gate results, and ready-for-`/aod.deliver` confirmation (all tasks `[X]`, no `.aod/` edits, invariants held).

---

**End of Agent Assignments — F-315**
