# Agent Assignments — Feature 185: CWE Catalog Expansion (F-A1.2)

**Author**: team-lead | **Date**: 2026-06-11
**Feasibility**: APPROVED (tasks.md triple-signed 2026-06-11; team-lead review: `.aod/results/team-lead.md`)
**Source**: `specs/185-cwe-catalog-expansion/tasks.md` (20 tasks, T001–T020)
**Agent registry**: `.claude/agents/_README.md` — all `subagent_type` values below are exact registry names
**Effort pin of record**: O/R/P = **0.75 / 1.0 / 1.5 days** (team-lead revision; supersedes PRD v1.1 0.5/0.75/1.0)
**Delivery**: Single PR (#328); fits the /aod.build 3-wave ceiling in one session (W0 → W1 → W2)

---

## 1. Agent Assignment Matrix

| Task | Agent (`subagent_type`) | Rationale |
|------|------------------------|-----------|
| T001 | senior-backend-engineer | Git plumbing + pytest pre-state evidence; record EXPECTED-RED backward-compat state with literal totals (no fixes) |
| T002 | senior-backend-engineer | Scripted corpus download + SHA-256 pin; mechanical, no judgment — launches the pacing lane |
| T003 | senior-backend-engineer | Extraction script over two git blobs per `contracts/restored-edges.schema.md` |
| T004 | senior-backend-engineer | XML harvest script (cwec_v4.20 → 40-row table); moved from architect per tasks review — architect stays judgment-only and consumes `harvest-40.md` |
| T005 | senior-backend-engineer | Run extraction, verify 67-edge counts/splits/exclusions, insurance commit (closes Risk 185.1) |
| T006 | **architect** | The feature's only judgment task: 40-ID add/reject/defer disposition, Category/Pillar fidelity-first rationale, 8 sentinel spot-checks, Issue #185 posting |
| T007 | senior-backend-engineer | Scripted lexicographic merge of add-set records into `cwe.yaml` (Python string-sort positions) |
| T008 | senior-backend-engineer | F-A1.2 provenance header block in `cwe.yaml` |
| T009 | senior-backend-engineer | README §3.5 composition/count refresh (may run ∥ T008 — different files, ~15 min upside, optional) |
| T010 | senior-backend-engineer | US1 commit gate: integrity 5/5 + record count; gate stays with the data author — independence is reserved for T020 |
| T011 | senior-backend-engineer | Byte-exact edge insertion from committed artifact + BLOCKING exact-tuple/near-key dedupe re-check (0 collisions) |
| T012 | senior-backend-engineer | Crosswalk header "Edit lineage" line (+67 or actual, blob e58f247, Issue #185) |
| T013 | senior-backend-engineer | US2 commit gate: YAML-parse edge counts + byte-exactness diff vs e58f247 + #186-deferred pair check |
| T014 | senior-backend-engineer | 6-baseline sequential regen per `contracts/baseline-regen.contract.md` (shared `report-data.typ` forbids parallel regen); HALT on any non-CA page delta (R6) |
| T015 | senior-backend-engineer | US3 baseline gate: backward-compat 6/6 red→green flip vs T001 pre-state; commit ~14 MB regenerated PDFs |
| T016 | **tester** | Independent QA verification: all-add-set name-diff vs harvest, 0 mismatches (R7 gate; CWE-1039 rename sentinel) — verification kept out of the data author's hands |
| T017 | **code-reviewer** | Read-only review sweep: no-excluded-edge-returns + stale-count grep; C4 — defer count-fixes on T018-owned files (CHANGELOG/ADR-037-adjacent) to T018 |
| T018 | senior-backend-engineer | Docs closure single commit: dual-attribution CHANGELOG, ADR-037 D-7 annotation (read architect C3 restatement first), NEXT-SESSION residual |
| T019 | senior-backend-engineer | Governance trail: PRD v1.2 errata (MUST carry revised O/R/P 0.75/1.0/1.5d), KB process-lesson, Issue #185 40/40 disposition-line verification |
| T020 | **tester** | Final gate (team-lead C2): full pytest + `/aod.analyze` + quickstart walkthrough run independently of the data author; push + PR #328 description update included |

**Workload**: senior-backend-engineer 16/20 (heavy but inherent to a strictly-sequenced data feature — tasks are short, sequential, never parallel-overloaded); architect 1; tester 2; code-reviewer 1. Max concurrent agents: 3 (Wave 2 launch).

---

## 2. Parallel Execution Waves

### Wave 0 — Setup + Foundational + Disposition (two parallel lanes)

**Pacing rule (team-lead C3)**: Lane A is the timing-dominant entry leg into T007 (~2–3h vs Lane B's ~1.5–2h). Launch T002 → T004 → T006 FIRST; T006, not T005, is the start-side pacing item.

| Lane | Sequence | Agents |
|------|----------|--------|
| A (pacing — launch first) | T002 → T004 → T006 | senior-backend-engineer → senior-backend-engineer → architect |
| B (insurance) | T001 → T003 → T005 | senior-backend-engineer |

T001 ∥ T002 at session start; T003 ∥ T004 after setup; T005 ∥ T006 (extraction vs disposition — plan D5 twin tracks).

**Exit criteria**: T005 artifact committed (Gate G0a) AND T006 disposition published (Gate G0b). Both block T007.

### Wave 1 — Sequential Data Spine (single agent: senior-backend-engineer)

```
T007 → (T008 ∥ T009) → T010 [US1 gate] → T011 → T012 → T013 [US2 gate]
```

Records before edges is FR-030-mandated — no cross-agent parallelism exists here. T007 requires T006 (disposition gates inserts) + T002 (corpus) + T005 (no production edit before the insurance commit). US1 checkpoint after T010 is the independently-verifiable MVP branch state.

**Exit criteria**: T013 gate green and committed.

### Wave 2 — Verification Fan-out + Closure (three parallel tracks, then final gate)

Launch together immediately after T013 (matches tasks.md "Parallel Example: User Story 3"):

| Track | Sequence | Agent |
|-------|----------|-------|
| 1 (critical path) | T014 → T015 [baseline gate] → T018 → T019 | senior-backend-engineer |
| 2 | T016 (needs only T007+T004 — ready at wave start) | tester |
| 3 | T017 (needs T013 — ready at wave start) | code-reviewer |

Then: **T020** (tester) after ALL of T014–T019.

File-disjointness verified for the fan-out (baselines vs name-diff script vs read-only sweep). Tracks 2–3 finish before T018 starts in practice, which makes the C4 deferral rule workable. Sequential regen inside T014 is contract-mandated, not a missed parallel opportunity.

**Exit criteria**: T020 final gate green; branch pushed; PR #328 description updated.

---

## 3. Quality Gates

| Gate | Task | Position | Owner | Must show | Blocks |
|------|------|----------|-------|-----------|--------|
| G0a — Insurance artifact | T005 | W0 → W1 | senior-backend-engineer | `restored-edges.yaml` COMMITTED; 67 = 65 owasp→cwe + 2 mitre-attack→cwe; 40 distinct `_blocked_on`; 34 high / 32 medium / 1 low, all primary; exclusions absent (1 other-drift + 20 non-CWE + 25 dedupe). Closes Risk 185.1 | ALL production-data edits (T007+) |
| G0b — Disposition | T006 | W0 → W1 | architect | 40/40 add/reject/defer lines on Issue #185 with Category/Pillar rationale; verdict summary in `test-results/disposition.md`; deprecated → never "add" | T007 (insert scope) |
| G1 — US1 records | T010 | Inside W1 (MVP checkpoint) | senior-backend-engineer | Integrity suite 5/5; record count 53 → 53+\|add-set\| (93 add-all); records + header + README committed | T011 (FR-030: records before edges) |
| G2 — US2 edges | T013 | W1 → W2 | senior-backend-engineer | Integrity 5/5; YAML-parse counts 578→645 total / 541→608 primary (add-all; NOT grep — over-counts +1); byte-exactness diff vs e58f247; #186 pair present (`T1070.006→CWE-1269`, `T1562→CWE-693`); committed | T014, T017 |
| G3 — US3 baselines | T015 | Inside W2 | senior-backend-engineer | `test_backward_compatibility.py` 6/6 — red→green flip vs T001 recorded pre-state; 6 regenerated baselines committed; T014 diffs were CA-only with BOTH attributions (cwe 53→93 + inherited mitre-atlas 30→36) | T018 (CHANGELOG references the flip) |
| G4 — Final | T020 | End | tester | Full `pytest tests/ -q` green; `/aod.analyze` clean (SC-006); quickstart §0–§6 re-run clean; branch pushed; PR #328 counts + evidence links | Delivery (`/aod.deliver`) |

Commit discipline: commit after each gate task (T005, T010, T013, T015) plus the T018 docs commit — every commit keeps `test_crosswalk_referential_integrity` green (FR-030). HALT escalation: any non-CA baseline delta at T014 stops Track 1 and escalates (R6 typst-drift investigation) — do not proceed to T015.

---

## 4. Time Estimates per Wave

Consistent with the revised pin O/R/P = 0.75 / 1.0 / 1.5 days (8h day → 6h / 8h / 12h). Wave wall-clock = longest lane/track (lanes run concurrently).

| Wave | Optimistic | Realistic | Pessimistic | Drivers |
|------|-----------|-----------|-------------|---------|
| W0 | 2.0h | 2.5h | 3.5h | Lane A dominates (download+pin, harvest, 40-ID disposition + 8 spot-checks + Issue posting); P: slow cwe.mitre.org fetches, disposition deliberation |
| W1 | 1.75h | 2.5h | 3.5h | Scripted merges + two gate runs; P: dedupe collision investigation at T011, sort-position fixes |
| W2 | 2.25h | 3.0h | 5.0h | Track 1 critical path (T014 regen ~1.5–1.75h R → T015 → T018/T019) + T020; T016/T017 absorbed off-path; P: R6 halt path (+2–3h) and name-diff remediation tail |
| **Total** | **6.0h (0.75d)** | **8.0h (1.0d)** | **12.0h (1.5d)** | |

**Floor conditions** (0.75d holds only if): (a) scripted harvest at T004, and (b) first-pass-clean CA-only page diffs at T014 (no R6 halt). Note the regen cycle runs three times end-to-end (T014 regen, T015 suite byte-compare, T020 full pytest) — absorbed in the figures above. Typst 0.14.2 verified installed (R6 → LOW); byte-identity suite is local-only (no CI dependency — T020 is the enforcement point). Confidence: HIGH (mechanism proven by #186).

---

## 5. Orchestrator Handoff Notes

1. **Launch order**: Start Lane A (T002) and Lane B (T001) simultaneously at session start; treat T006 as the start-side pacing item (C3).
2. **Hard ordering**: T005 commit before ANY production-data edit; T006 before T007; T010 before T011; T013 before T014; T015 before T018; T020 last.
3. **Scope elasticity**: any add-set ⊂ 40 from T006 shrinks T007/T011 without rework — counts scale; rejected-ID edges stay in the artifact with rationale on Issue #185.
4. **C4 rule for T017**: defer stale-count fixes on T018-owned files (CHANGELOG, ADR-037-adjacent) to T018's commit.
5. **Never commit**: cwec zip/xml, extracted tmp PDFs. Committed evidence lives in `specs/185-cwe-catalog-expansion/test-results/`.
6. **No test edits**: existing suites are the acceptance gates; gate tasks run them.
7. **Completion report**: return per-gate results, literal pytest totals (pre-state vs final), final record/edge counts, and any HALT events to team-lead for phase sign-off. Issue #185 closure happens at `/aod.deliver`, not here.

---

**Team-lead sign-off**: Assignments APPROVED for orchestrator handoff — registry-valid, dependency-correct, workload-balanced within the inherent sequential constraint, and consistent with the revised effort pin.
