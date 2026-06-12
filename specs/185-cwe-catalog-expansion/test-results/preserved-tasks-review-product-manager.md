# PM Review — tasks.md (Feature 185: CWE Catalog Expansion, F-A1.2)

**Date**: 2026-06-11
**Artifact**: `specs/185-cwe-catalog-expansion/tasks.md` (20 tasks, 6 phases)
**Context chain**: PRD v1.1 (Triad-approved) → spec.md (PM APPROVED_WITH_CONCERNS, FR-006 accepted) → plan.md (PM + Architect APPROVED_WITH_CONCERNS, D2/D3 ratified, red-main discovery folded) → tasks.md
**Verdict**: **APPROVED_WITH_CONCERNS** — 0 blocking. 2 LOW + 1 INFO. No re-review needed; fold LOW-1 at build (one-line T020 edit) or honor at execution.

---

## 1. User Story Coverage — PASS (3/3, each with independent gate)

| Story | Tasks | Independent test criteria | Verdict |
|---|---|---|---|
| US1 records (P1, MVP) | T006–T010 | T010 gate: integrity 5/5 + count check + commit; disposition gate T006 precedes all catalog edits | COVERED |
| US2 edges (P2) | T011–T013 | T013 gate: integrity 5/5, counts 578→645/541→608, field-level byte-exactness diff vs `e58f247`, #186 deferral pair present | COVERED |
| US3 baselines+verification+trail (P3) | T014–T019 | T015 gate: backward-compat 6/6 red→green flip vs T001 pre-state; T016 name-diff 0 mismatches; T017 sweep; T018/T019 trail | COVERED |

Each story closes with its own commit-gated checkpoint; `test_crosswalk_referential_integrity` green at every intermediate commit (FR-030) is restated in Notes and Incremental Delivery. Story independence is real: US1 ships value alone (AI CWEs citable), US2 depends only on US1, US3 wraps both.

## 2. FR Traceability — PASS (8/8)

| FR | Task(s) | Notes |
|---|---|---|
| FR-001 disposition gate | T006 (+T019 verifies 40/40 lines on Issue #185) | Lead posture add-all-40, deprecated-never-add, CWE-693 re-strand consequence — all carried verbatim |
| FR-002 records | T002 (corpus pin), T004 (harvest), T007 (insert, shape, sort semantics incl. `CWE-1035 < CWE-16` example) | Exact |
| FR-003 restore-set first, ∥ disposition | T003 + T005; Phase 2 CRITICAL note: commit before ANY production-data edit; T005 ∥ T006 per plan D5 | Risk 185.1 insurance correctly sequenced |
| FR-004 byte-exact edges, records-first, dedupe re-check | T011 (BLOCKING pre-insertion 0-collision check; `low` edge preserved) + T013; T011 gated on T010 | Exact |
| FR-005 integrity suite every commit, no test edits | Header note "no test is edited"; gates T010/T013; Notes commit discipline | Exact |
| FR-006 baseline regen (accepted consequence-scope) | T014 (6 baselines per amended contract, CA-only deltas, HALT on non-CA/R6) + T015 (red→green flip) | Exact — see §4 |
| FR-007 trail (a–g) | (a) T018 (b) T008 (c) T009+T017 grep sweep (d) T012 (e) T018 ADR-037 D-7 (f) T018 NEXT-SESSION (g) T019 disposition verification; closure deferred to `/aod.deliver` per Notes — consistent with spec [MANUAL-ONLY] | All 7 surfaces traceable |
| FR-008 scripted all-40 name-diff + sentinel spot-checks | T016 (R7 gate, CWE-1039 sentinel) + T006 (8-sentinel live-page checks) | See INFO-1 |

## 3. Scope Check — PASS (no creep)

Write-set: specs/185 scripts/artifacts/evidence, `cwe.yaml`, `crosswalk.yaml`, README §3.5, 6 gated baselines, ADR-037 annotation (docs-only), F-180 NEXT-SESSION, CHANGELOG, PRD errata, KB entry, Issue #185, PR #328 description. Everything maps to PRD v1.1 + accepted FR-006 + PM plan-stage conditions. Out-of-scope fences honored: no net-new edges, no schema/ADR change, no test edits, excluded T029 edges policed by T017's no-return check, the 2 sample-report baselines untouched per ratified D2 (stale-by-design disclosed in T018). T020 polish is workflow hygiene, not scope.

## 4. Plan-Stage PM Conditions — ALL LANDED

| Condition (plan sign-off) | Landing | Verdict |
|---|---|---|
| Red pre-state recorded before any change | T001: run backward-compat suite, record EXPECTED RED 6/6 FAIL with ATLAS attribution, explicit "do NOT fix anything here" guard | LANDED verbatim |
| Dual-attribution CHANGELOG (F-185 CWE + absorbed #186 ATLAS) | T018, including stale-by-design note for the 2 sample-report baselines (D2 disclosure condition) | LANDED |
| PRD v1.2 errata | T019: FR-006 consequence-scope addition + red-main discovery, "per PM condition" | LANDED (both errata elements) |
| KB process lesson | T019: check `ORDERED_FRAMEWORKS` membership for ANY catalog-growth feature at definition time | LANDED (exact framing) |
| Regen-contract expected-deltas amendment | Verified in `contracts/baseline-regen.contract.md`: dual deltas (cwe 53→93 + mitre-atlas 30→36), green-restored invariant, 0.00%-percentage caveat; T014 references the contract and inlines both attributions | LANDED |

Team-lead O/R/P re-validation (the third spec-stage condition) is the team-lead's call at this gate; tasks.md restates 0.5/0.75/1.0d and correctly flags T004 (scripted harvest) as the 0.5-floor path.

## 5. MVP Slicing & Disposition Gate

- **Disposition gate**: T006 hard-gates T007 ("disposition gates inserts"); extraction (T005) runs parallel per D5 — governance gate intact while the insurance commit is not delayed. Add-set ⊆ 40 shrink path handled without rework (Notes). CORRECT.
- **MVP (US1-only)**: viable as a branch-internal checkpoint — integrity 5/5, complete citation catalog, AI CWEs citable. Two precision points below (LOW-2). Single-PR delivery (contract invariant 4) is the actual shipping plan, so partial-merge risk is foreclosed.

## 6. Concerns

**LOW-1 — `/aod.analyze` (SC-006) not explicit in T020.** Spec US3-AC4/SC-006 require an `/aod.analyze` clean pass; T020 lists full pytest + quickstart + PR update but omits it. The Notes section explicitly defers Issue closure to `/aod.deliver` but is silent on `/aod.analyze`. The workflow-level rule (CLAUDE.md: "Run /aod.analyze before PRs") means the gate exists regardless — this is a traceability gap, not a missing gate. **Fold**: add "/aod.analyze clean" to T020, or add a Notes line deferring it to deliver alongside Issue closure.

**LOW-2 — MVP phrasing precision (no task change required).** (a) "Independently shippable" for US1 is checkpoint-shippable, not merge-shippable: a hypothetical US1-only merge would deepen the red byte-identity suite (CA pages render the 53→93 count), so T014/T015 would have to travel with any partial ship — invariant 4 already binds single-PR delivery, so risk is nil. (b) The MVP Validate step says "name spot-checks" while US1's Independent Test says "name-diff clean"; T016's deps (T007+T004 only) make it pull-forwardable into an MVP slice — worth knowing if the slice is ever exercised.

**INFO-1 — Sentinel spot-checks moved earlier (improvement, no action).** Plan W2-a placed the 8-sentinel live-page checks in the verification wave (tester); tasks.md folds them into T006 (architect, disposition). The verification chain stays complete — inserted-records→harvest all-40 at T016, harvest→live-pages 8-sentinel at T006 — and catches harvest errors before insertion rather than after. Accepted as written.

## 7. Success Criteria Traceability

SC-001 → T006/T019; SC-002 → T007/T010/T016; SC-003 → T011/T013/T017; SC-004 → T010/T013 + commit discipline; SC-005 → T014/T015; SC-006 → T018/T019 + deliver-stage closure (see LOW-1 for the `/aod.analyze` line item).

## 8. Sign-off

**PM verdict: APPROVED_WITH_CONCERNS** — all 8 FRs and 3 user stories covered with independent gates, zero scope creep, all five PM plan-stage conditions landed verbatim, disposition gate and MVP sequencing sound. Concerns are non-blocking documentation-precision items; LOW-1 is a one-line fold at build. Proceed to architect + team-lead review; on triple sign-off, build may start.
