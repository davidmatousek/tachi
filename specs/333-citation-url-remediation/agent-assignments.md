---
artifact: agent-assignments
feature_id: "333"
owner: team-lead
date: 2026-06-29
status: approved
source_tasks: specs/333-citation-url-remediation/tasks.md
estimate:
  planning_days: 3.0
  floor_days: 1.5
  ceiling_days: 5.0
agents_used:
  - web-researcher
  - architect
  - senior-backend-engineer
  - tester
  - code-reviewer
---

# Agent Assignments — F-333 Citation-URL Remediation (BLP-06 Wave 1)

**Input**: `specs/333-citation-url-remediation/tasks.md` (T001–T020, triple-signed 2026-06-29)
**Feasibility**: FEASIBLE WITH MODIFICATIONS — 3.0 eng-day central (floor 1.5 / ceiling 5.0)
**Governance**: PM APPROVED · Architect APPROVED_WITH_CONCERNS · Team-Lead APPROVED_WITH_CONCERNS — all triple-review concerns folded into the FINAL tasks.md; 0 blocking.

> All agent names below are exact entries from the Agent Registry (`.claude/agents/_README.md`). Five agents are engaged: `web-researcher` (W0 retrieval), `architect` (W0→W1 fork gate), `senior-backend-engineer` (apply edits), `tester` (test authoring + validation + acceptance), `code-reviewer` (binding W3 gate). No invented labels.

---

## 1. Agent Assignment Matrix

Every task maps to **exactly one** agent. The rationale column ties the choice to the registry role and the task's nature.

| Task | [P] | Story | Agent | Rationale (registry role) |
|------|-----|-------|-------|---------------------------|
| **T001** | | Setup | `senior-backend-engineer` | Source-mapping the 41-finding list across 3 catalog files → worklist (data/repo navigation, no edits). |
| **T002** | [P] | Setup | `senior-backend-engineer` | Author the #325 deferral doc (`deferred-325.md`) — structured artifact authoring. |
| **T003** | [P] | W0 | `web-researcher` | ATLAS adjudication: verify 36 IDs in MITRE `atlas-data`, dual-UA + runner-egress probe → `research-atlas.md`. Pure external retrieval/investigation. |
| **T004** | [P] | W0 | `web-researcher` | NIST AI 100-1 canonical lookup (disambiguate from AI 600-1), 2xx verification → `research-nist.md`. |
| **T005** | [P] | W0 | `web-researcher` | OWASP dead-set adjudication across `owasp.yaml` + `crosswalk.yaml`, `llm0X`/`llm0X2025` twin disambiguation → `research-owasp.md`. |
| **T006** | | W0 GATE | `architect` | **Fork sign-off** — re-classify vs re-point is a HOW decision (plan.md APPROVE authority; opus-tier verdict gate). Host-keyed override scope note (Concern 3). |
| **T007** | [P] | US1 | `tester` | Author the offline synthetic-404 verdict unit test (extend `test_citation_linkrot_parity.py`); confirm FAILS pre-impl. Test authoring = QA scope; invariant: tester never haiku. |
| **T008** | | US1 | `senior-backend-engineer` | Add `_HOST_STATUS_OVERRIDES` + guard in `_verdict_for_status(...)` (`scripts/check-citation-urls.py`). Server-side logic edit. |
| **T009** | | US1 | `senior-backend-engineer` | Update `mitre-atlas.yaml` R7/FR-033 header comment to cross-ref the code override (Architect OBS-1). Data-file edit. |
| **T010** | | US1 | `tester` | Run T007 → green; confirm ATLAS reclassified, no other-host 404 behavior changed. Test execution + verdict. |
| **T011** | | US2 | `senior-backend-engineer` | Replace dead NIST DOI in `nist-ai-rmf.yaml` (cascades to 73 records). Data-file edit. |
| **T012** | | US3 | `senior-backend-engineer` | Re-point dead OWASP citations in **both** `owasp.yaml` + `crosswalk.yaml`, resolve twin, keep `llm01` byte-unchanged (Team-Lead Concern 1). Data-file edits. |
| **T013** | | US4 | `senior-backend-engineer` | Add `no_cache` `workflow_dispatch` input to `tachi-citation-linkrot.yml` (wires existing `--no-cache`). Workflow/config edit. |
| **T014** | [P] | US4 | `tester` | FR-007 rendering-exposure grep over byte-baselined render artifacts → `fr7-exposure.md`; expect zero hits. Validation/quality check. |
| **T015** | | US4 | `tester` | Run full offline suite (`test_citation_shape()` + synthetic-404) → green; verify the new test is **collected/executed** (anti silent-green, Concern 2). |
| **T016** | | US4 GATE | `code-reviewer` | **Binding code review** (NFR-005): host-scoped, documented, reversible; frozensets + `llm01` untouched; no network on PR/push. Opus-tier verdict gate. |
| **T017** | | US4 GATE | `tester` | `[MANUAL-ONLY]` Live monitor dispatch + await **#332 self-close** (FR-006 real DoD). Validation gate + fallback-to-T006 judgment. Deliver-adjacent. |
| **T018** | | US4 | `tester` | `[MANUAL-ONLY]` Landing-content spot-check: 1 NIST + 1 OWASP URL in browser (PM-M3). Human quality validation. Deliver-adjacent. |
| **T019** | [P] | Polish | `senior-backend-engineer` | Record fork-resolution evidence in `delivery.md` (SC-004). Artifact authoring (created at deliver). |
| **T020** | [P] | Polish | `senior-backend-engineer` | Confirm + link the #325 deferral doc for FR-005 AC-1. Artifact verification (created at deliver). |

### Per-Agent Load Summary

| Agent | Tasks | Count | Tier (FR-004) |
|-------|-------|-------|---------------|
| `web-researcher` | T003, T004, T005 | 3 | haiku (retrieval, no verdict) |
| `architect` | T006 | 1 | opus (fork verdict gate) |
| `senior-backend-engineer` | T001, T002, T008, T009, T011, T012, T013, T019, T020 | 9 | sonnet (implementation) |
| `tester` | T007, T010, T014, T015, T017, T018 | 6 | sonnet (gate-grade validation; never haiku) |
| `code-reviewer` | T016 | 1 | opus (binding review gate) |

**Balance check**: `senior-backend-engineer` (9) and `tester` (6) carry the bulk, but the 9 backend tasks are **never all concurrent** — they spread across Wave 0 (T001/T002), Wave 2 apply (T008/T009/T011/T012), Wave 3 (T013), and Polish (T019/T020). Peak concurrent backend load is the three file-disjoint apply streams in Wave 2 (US1 T008/T009 ∥ US2 T011 ∥ US3 T012). No agent exceeds the 80%-loaded ceiling at any single wave. Verdict-gate agents (`architect`, `code-reviewer`) each hold one focused decision — correct for a small remediation feature.

---

## 2. Parallel Execution Waves

Five waves plus a hard intra-W0 barrier. `[MANUAL-ONLY]` marks deliver-time tasks gated out of CI by the ADR-021 determinism boundary (live network / `gh` lifecycle / human judgment) — they run during `/aod.deliver`, not in the build.

### Wave 0 — Setup + Research (Foundational)

> Setup runs immediately; the research fan-out is the W0 gate input. **No catalog edit may begin here.**

| Sub-step | Tasks | Agent(s) | Parallelism |
|----------|-------|----------|-------------|
| 0a Setup | T001, **T002 [P]** | `senior-backend-engineer` | T002 ∥ T001 (disjoint docs) |
| 0b Research (∥ fan-out) | **T003 [P] · T004 [P] · T005 [P]** | `web-researcher` | All three classes in one `web-researcher` fan-out |

**Wave 0 exit condition**: `research-atlas.md`, `research-nist.md`, `research-owasp.md` all written with cited evidence → feeds T006.

### Wave 0-Gate — Architect Fork Sign-off (BARRIER)

| Task | Agent | Type |
|------|-------|------|
| **T006** | `architect` | **Hard barrier** — blocks ALL of Wave 2+. See Quality Gate 1. |

> **CRITICAL**: no apply task (T008/T009/T011/T012/T013) may start until T006 is green. This is the structural enforcement of NFR-001 ("no citation edited on a hunch"). Architect-confirmed dependency ordering; load-bearing W0→W1 gate (Architect OBS-2).

### Wave 2 — Apply (US1 ∥ US2 ∥ US3, file-disjoint)

> Three classes proceed in parallel after the T006 gate. File-disjoint per tasks.md §Parallel Opportunities: US1 → `check-citation-urls.py` + `mitre-atlas.yaml` (comment only); US2 → `nist-ai-rmf.yaml`; US3 → `owasp.yaml` + `crosswalk.yaml`. No write collision (US1's re-classify path edits no ATLAS data, so US3 owns `crosswalk.yaml` uncontested).

| Stream | Tasks (serial within stream) | Agent(s) |
|--------|------------------------------|----------|
| **US1 (ATLAS)** | T007 (FAIL-first) → T008 → T009 → T010 (green) | `tester` (T007/T010) → `senior-backend-engineer` (T008/T009) |
| **US2 (NIST)** | T011 | `senior-backend-engineer` |
| **US3 (OWASP)** | T012 | `senior-backend-engineer` |

> Intra-US1 the T007→T008→T010 FAIL-checkpoint sequence is serial even under US1∥US2∥US3 (Team-Lead Concern 6, INFO) — the test must be authored and observed RED before T008 implements.

### Wave 3 — US4 Validate → Live Gate

| Sub-step | Tasks | Agent(s) | Notes |
|----------|-------|----------|-------|
| 3a Setup + grep (∥) | T013 · **T014 [P]** | `senior-backend-engineer` (T013) · `tester` (T014) | Workflow input ∥ exposure grep |
| 3b Offline green | T015 | `tester` | Verify new test COLLECTED/EXECUTED (Concern 2) |
| 3c Binding review | **T016** | `code-reviewer` | **GATE** — see Quality Gate 2 |
| 3d Live self-close | **T017** `[MANUAL-ONLY]` | `tester` | **GATE** — #332 self-close; deliver-adjacent. See Quality Gate 3 |
| 3e Landing spot-check | **T018** `[MANUAL-ONLY]` | `tester` | 1 NIST + 1 OWASP browser check; deliver-adjacent |

> US4 depends on **US1 + US2 + US3 all complete** — it validates the aggregate. T017 is strictly last/async (Architect + Team-Lead confirmed). T017/T018 run at `/aod.deliver` (F-183 KB Entry 17 pattern).

### Wave 4 — Polish & Cross-Cutting

| Tasks | Agent | Parallelism |
|-------|-------|-------------|
| **T019 [P] · T020 [P]** | `senior-backend-engineer` | Both ∥; both created at deliver (`delivery.md` + #325 link) |

---

## 3. Quality Gates Between Waves

Three hard gates govern wave transitions. Each is a STOP point — downstream work does not proceed until the gate clears.

### Gate 1 — T006 Architect Fork Sign-off (W0 → W2)

- **Owner**: `architect` (opus-tier verdict authority).
- **Blocks**: every apply task in Wave 2 (T008/T009/T011/T012) and downstream Wave 3.
- **Pass criteria**: T003–T005 evidence reviewed; ATLAS path confirmed as host-scoped re-classify (or a per-ID re-point / the split-valve explicitly authorized); the fork-resolution record notes the host-keyed override also suppresses the **~96 `atlas.mitre.org` refs in `crosswalk.yaml`** (Concern 3) so coverage is proven, not assumed.
- **Split-valve trigger (Team-Lead C2 / D2)**: if T008 reveals host-scoping needs a `classify_one()` control-flow refactor (it should not — `_verdict_for_status` already receives `url`, confirmed in-tree at :447), split the classifier work to a BLP-06 Wave 2 sibling and ship F-333 with NIST + OWASP data fixes. Record the trigger at T006/T008.
- **Fail action**: re-adjudicate in W0; do not edit any catalog.

### Gate 2 — T016 Binding Code Review (W3)

- **Owner**: `code-reviewer` (opus-tier; renders **binding** APPROVED / CHANGES_REQUESTED).
- **Blocks**: the live self-close gate (T017) and delivery.
- **Pass criteria (NFR-005)**: `_HOST_STATUS_OVERRIDES` change is host-scoped, documented, and reversible; global `_HARD_ROT_STATUSES`/`_NEEDS_REVIEW_STATUSES` frozensets untouched; `llm01-prompt-injection/` untouched; **no network added to any PR/push path** (ADR-021 boundary intact).
- **Fail action**: CHANGES_REQUESTED → return to the relevant apply stream (US1/US3), re-run T015, re-review.

### Gate 3 — T017 #332 Self-Close (Real DoD Gate)

- **Owner**: `tester` · `[MANUAL-ONLY]` · deliver-adjacent.
- **Blocks**: feature closure (this IS Definition-of-Done step 3, FR-006).
- **Pass criteria**: a `--no-cache` full-sweep dispatch (`gh workflow run tachi-citation-linkrot.yml -f no_cache=true`) finds **zero in-scope confirmed rot** and **#332 auto-closes** with its recovery comment; T018 landing spot-check (1 NIST + 1 OWASP) confirms each URL renders the specific cited item.
- **Fail action (PM-M4 / spec R1)**: if #332 does NOT self-close, the fork was resolved wrong → **loop back to T006/W0 re-adjudication**. This is the closed-loop correctness check on Gate 1.

---

## 4. Time Estimates Per Wave

Anchored to the feasibility-check **3.0 eng-day central** (floor 1.5 / ceiling 5.0), single engineer, wall-clock. The re-classify code-path is priced into Wave 2 per C1.

| Wave | Scope | Central (d) | Floor (d) | Ceiling (d) | Drivers |
|------|-------|-------------|-----------|-------------|---------|
| **W0** Setup + Research | T001–T002 + T003–T005 ∥ | **0.75** | 0.5 | 1.25 | 3-class research fan-out (dual-UA + runner-egress); OWASP set messier than "4" (C5). |
| **W0-Gate** Fork sign-off | T006 | **0.25** | 0.1 | 0.5 | Architect adjudication; +buffer if ATLAS resolves mixed (per-ID). |
| **W2** Apply (US1∥US2∥US3) | T007–T012 | **1.25** | 0.5 | 2.5 | US1 re-classify path (host-override + offline test) ~0.75–1.25d; NIST/OWASP cascading edits cheap; ceiling if `classify_one()` refactor (→ split-valve). |
| **W3** US4 Validate + Live | T013–T018 | **0.5** | 0.25 | 0.5 | Offline green + binding review fast; FR-006 dispatch-then-await ~0.5d wall-clock; +2nd dispatch at ceiling. |
| **W4** Polish | T019–T020 ∥ | **0.25** | 0.15 | 0.25 | Deliver-time doc authoring/linking. |
| **Total** | T001–T020 | **3.0** | **1.5** | **5.0** | Matches feasibility-check; carry 5.0 as risk-buffered ceiling. |

**Ceiling triggers (any two+ → 5.0d)**: ATLAS resolves mixed (per-ID handling); host-scoping needs a `classify_one()` refactor; FR-007 finds rendering exposure → ADR-037 D-9 CA-baseline regen; FR-006 needs a 2nd dispatch; #325 folds (it should not — C3).

**Deliver-adjacent note**: W3's T017/T018 wall-clock lands at `/aod.deliver`, not in the build pipeline. The build-pipeline critical path is **W0 → T006 → US1 → T015 → T016** (~2.5d); the remaining ~0.5d is the deliver-time live gate.

---

## Handoff to Orchestrator

- **Feasibility**: APPROVED (3.0 eng-day central; no blockers).
- **tasks.md**: `specs/333-citation-url-remediation/tasks.md` (triple-signed, FINAL).
- **Wave strategy**: W0 (setup+research ∥) → **T006 architect barrier** → W2 (US1∥US2∥US3 apply, file-disjoint) → W3 (validate → binding review → `[MANUAL-ONLY]` live #332 self-close) → W4 (polish ∥).
- **Critical path (build pipeline)**: T001 → T003/T004/T005 → **T006** → US1(T007→T008→T010) → T015 → **T016**. US2/US3 fold in parallel; T017/T018 are deliver-time.
- **Gates**: Gate 1 (T006, architect) and Gate 2 (T016, code-reviewer) are STOP points; Gate 3 (T017) is the deliver-time real-DoD self-close with the loop-back-to-T006 fallback.

---

**End of Agent Assignments — F-333**
