# Agent Assignments: F-292 Post-Merge Verification Runs (T017 + T026)

**Feature**: #295 | **Draft PR**: #353 | **Branch**: `295-f292-verification-runs`
**Source**: `specs/295-f292-verification-runs/tasks.md` (triple-signed 2026-07-03)
**Feasibility**: APPROVED_WITH_CONCERNS (Team-Lead, 0H/0M/4L) — see `feasibility-check.md`
**Estimate**: 0.5 (floor) / 1.0 (central) / 2.0 (ceiling) eng-days
**Wave plan**: 1 serial wave, roster of 2 (security-analyst LEAD, tester) — FR-021 forbids concurrent tachi pipeline runs

> **Agent-name provenance**: every `subagent_type` below is an exact entry from `.claude/agents/_README.md` Agent Roster. No generic labels.

---

## 1. Agent Assignment Matrix

| Task | Story | Agent (`subagent_type`) | [P] | Notes |
|------|-------|-------------------------|-----|-------|
| T001 | Setup | `security-analyst` | | Precondition sanity (jq/pytest, branch-current, 4-findingId anchor) |
| T002 | Foundational | `security-analyst` | | D-E pre-state suite → `test-results/pre-state.md` (FR-019, blocks all commits) |
| T003 | US1 | `security-analyst` | | Anchor OI subset extraction — **fail-closed gate** (exactly 4, else ERROR-stop) |
| T004 | US1 | `security-analyst` | | Fresh `tachi-output-integrity` run — **M-1 escape hatch** (2 attempts) |
| T005 | US1 | `security-analyst` | **[P]** | Author `assemble_oi_sarif.py` — schema-shape only, overlaps T004 wall-clock |
| T006 | US1 | `security-analyst` | | Assemble `fresh-oi.sarif` + subset — **fail-closed gate** (non-empty, else ERROR-stop) |
| T007 | US1 | `security-analyst` | | D-1 hard gate: count + findingId set + sink/flow identity + attribution — **fail-closed** |
| T008 | US1 | `security-analyst` | | Commit `sc-003-verification-record.md`; check #295 T017 box |
| T009 | US1 | `security-analyst` | | File contract-§3 dual-defect Issue (ALWAYS) + conditional FR-007 defect |
| T010 | US2 | `security-analyst` | | FR-014 URI enabler in `generate-threats-sarif.py:481` + L-a before/after cmp proof |
| T011 | US2 | `security-analyst` | | Same commit as T010: covering assertion + CI hardening-paths anchor |
| T012 | US2 | `security-analyst` | | Full pipeline run on multi-tenant-rag-app — **M-1 escape hatch** (2 attempts, staged fallback) |
| T013 | US2 | `security-analyst` | | Cat 6 gate: ≥1 `OI-*` CWE-943 — **fail-closed** (zero ⇒ defect Issue, STOP Phase 4) |
| T014 | US2 | `security-analyst` | | Copy 4 artifacts + regen `threats.sarif` — **fail-closed** (regen MISMATCH ⇒ defect, STOP) |
| T015 | US2 | `security-analyst` | | README row + count-pin co-update (L-3); commit 5 artifacts + `sc-015-verification-record.md` |
| T016 | US2 | `security-analyst` | **[P]** | File `generate-risk-scores-sarif.py` enhancement Issue — overlaps T014/T015 |
| T017 | US3 | `tester` (alt: `senior-backend-engineer`) | | Author `test_sarif_regen_identity.py` — fail-closed, local green |
| T018 | US3 | `tester` (alt: `senior-backend-engineer`) | | Same commit as T017: `.github/workflows/tachi-sarif-regen.yml` (6-path anchor) |
| T019 | US3 | `tester` | **[P]** | Update PR #353 body with FR-017 coverage-boundary — overlaps T017/T018 |
| T020 | Polish | `security-analyst` (LEAD) | | Closure cross-check: CI green, post-state flips attributed, FR-020 fence audit |

**Workload**: security-analyst = 17 tasks (T001–T016, T020); tester = 3 tasks (T017–T019).

**Concentration rationale (>80%-on-one-agent metric deliberately superseded)**: FR-021 *mandates* serialization (shared `tachi` orchestrator context — no concurrent pipeline runs), so multi-agent parallelism is architecturally forbidden, not merely unused. The verification-run body (T003–T016) also requires single-context continuity for the live `tachi-output-integrity` / `/tachi.threat-model` dispatches. Concentrating the LEAD role on `security-analyst` is a constraint-driven decision consistent with "do not over-staff a 1.0d feature," not a capacity oversight. The Team-Lead veto was **not** exercised.

**Alternate-agent trigger (T017/T018)**: reassign the Python/workflow authoring to `senior-backend-engineer` if `tester`'s BDD/Gherkin default is unsuited to the importlib-load + `read_bytes()` equality module and raw GitHub Actions YAML. T019 (PR-body prose) stays with `tester` regardless.

---

## 2. Parallel Execution Waves

**One serial wave** (FR-021: no concurrent tachi pipeline runs). Story order is fixed: **US1 → US2 → US3 → closure**. The template's parallel-team strategy does **not** apply.

```
WAVE 1 (serial) — security-analyst LEAD, tester on US3
│
├─ Phase 1  T001                          [security-analyst]
├─ Phase 2  T002  ── pre-state commit ──  [security-analyst]   (blocks all later commits)
│
├─ Phase 3 (US1)  T003 → T004 → T006 → T007 → T008 → T009   [security-analyst]
│                        └─ T005 [P] overlaps T004 wall-clock ─┘
│
├─ Phase 4 (US2)  T010+T011 (one commit) → T012 → T013 → T014 → T015   [security-analyst]
│                        └─ T016 [P] anytime after T013 ──────────────┘
│
├─ Phase 5 (US3)  T017+T018 (one commit)                    [tester / alt senior-backend-engineer]
│                        └─ T019 [P] overlaps T017/T018 ──── [tester]
│
└─ Phase 6  T020  closure cross-check                        [security-analyst LEAD]
```

**The 3 [P] annotations are intra-agent wall-clock overlaps, not concurrent pipeline runs**:
- **T005 [P]** — author the assembler tool while T004's live OI run executes (depends on SARIF schema shape only, not T004 output).
- **T016 [P]** — file the enhancement Issue during the T014/T015 copy-and-verify work (independent file, no dependency).
- **T019 [P]** — update the PR body while T017/T018 author the module + workflow (independent surface).

Each [P] is executed by the phase's owning agent; none introduces a second live `tachi` run.

---

## 3. Quality Gates Between Phases

| Boundary | Gate | Type | Failure disposition |
|----------|------|------|---------------------|
| Enter Phase 3 | T002 pre-state committed | Blocking prerequisite | Commit before any artifact commit (FR-019) |
| Within Phase 3 | **T003** anchor subset = exactly 4 findingIds | **Fail-closed ERROR-stop** | Empty/wrong cardinality ⇒ stop, never pass |
| Within Phase 3 | **T004** fresh OI run | **M-1 escape hatch** (2 live attempts) | After 2 ⇒ file tooling defect, close on staged-partial record |
| Within Phase 3 | **T006** fresh-oi subset non-empty | **Fail-closed ERROR-stop** | Empty extraction ⇒ stop |
| Within Phase 3 | **T007** D-1 hard gate (count + findingId set + identity + attribution) | **Fail-closed** | Unattributable delta ⇒ gate FAIL (honest FAIL still completes; T009 files FR-007 Issue) |
| Phase 3 → 4 | US1 checkpoint: SC-003 closed on evidence (PASS or honest FAIL) | Checkpoint | US2 starts only after Phase 3 concludes (FR-021) |
| Within Phase 4 | **T012** full pipeline run | **M-1 escape hatch** (2 attempts + staged per-skill fallback) | Overflow ⇒ staged fallback; after 2 ⇒ defect + partial record |
| Within Phase 4 | **T013** Cat 6 ≥1 `OI-*` CWE-943 | **Fail-closed ERROR-stop** | Zero ⇒ file defect Issue, STOP Phase 4 (no baseline commit), mark US3 deferred (FR-018) |
| Within Phase 4 | **T014** regen byte-identity (`cmp`) | **Fail-closed ERROR-stop** | MISMATCH ⇒ file FR-007 defect, STOP (no baseline commit; US3 defers) — Architect L-1 explicit disposition |
| Phase 4 → 5 | **FR-018 STRUCTURAL GATE** | Structural precondition | Proceed to Phase 5 ONLY if T014 regen passed; on T013/T014 failure US3 defers to defect Issue **without** counting as a US3 failure |
| Phase 5 → 6 | US3 checkpoint: module green locally + in workflow | Checkpoint | — |
| Phase 6 | **T020** closure cross-check | Final gate | CI green (tachi-pytest, maestro-coverage, gitleaks, +tachi-sarif-regen if US3 landed); every post-state flip attributed; both #295 boxes checked; all pre-decided Issues filed; **FR-020 fence audit** (`git diff main --stat` + content-review of `generate-threats-sarif.py` per Architect L-2) |

---

## 4. Time Estimates Per Phase

Bounds fit the feasibility floor 0.5 / central 1.0 / ceiling 2.0 eng-days. Per Team-Lead L-1, the central→ceiling glide is **steep** — bounded adds (URI enabler, count-pin co-update, identity table) consume the snag buffer, so slippage lands near the ceiling rather than mid-band.

| Phase | Tasks | Owner | Floor | Central | Ceiling |
|-------|-------|-------|-------|---------|---------|
| 1 — Setup | T001 | security-analyst | 0.25h | 0.5h | 0.5h |
| 2 — Foundational | T002 | security-analyst | 0.25h | 0.75h | 1.0h |
| 3 — US1 (SC-003) | T003–T009 | security-analyst | 1.25h | 3.0h | 6.0h |
| 4 — US2 (SC-015) | T010–T016 | security-analyst | 1.5h | 3.0h | 6.5h |
| 5 — US3 (regen CI) | T017–T019 | tester (alt SBE) | 0.5h | 0.5h | 1.5h |
| 6 — Polish | T020 | security-analyst | 0.25h | 0.25h | 0.5h |
| **Total** | **20 tasks** | | **~4.0h (0.5d)** | **~8.0h (1.0d)** | **~16.0h (2.0d)** |

**Ceiling drivers**: T003–T004 (2 live OI attempts + tooling-defect fallback) and T012–T014 (2 pipeline attempts + staged per-skill fallback on orchestrator overflow, per the known Phase-5-skip context limit). The deliverable is the verification record — an honest FAIL with committed evidence still completes the feature (KB Entry 17).

---

## 5. Sign-off

**Team-Lead**: APPROVED_WITH_CONCERNS — task graph realizes the 1-serial-wave plan; 20 tasks right-sized; roster of 2 honored; all 3 [P] annotations are wall-clock overlaps, not concurrent pipeline runs; estimate holds. Veto not exercised. Hand off to `orchestrator` for serial execution.
