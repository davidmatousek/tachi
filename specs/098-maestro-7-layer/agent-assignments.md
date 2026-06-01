# Agent Assignments: Feature 098 — MAESTRO Coverage Matrix (Always Render All 7 Layers)

**Feature**: Issue #98 · BLP-04 Wave 4 · `feat(098)`
**Tasks source**: `specs/098-maestro-7-layer/tasks.md` (17 tasks, triple-approved 2026-06-01)
**Team-Lead**: David Matousek · **Generated**: 2026-06-01
**Feasibility**: APPROVED (1.0–1.5 days) — see `tasks.md` triad block + `.aod/results/team-lead.md`

---

## 1. Execution Model

This is a **tightly-coupled, single-developer rendering fix** — not parallel-team work. One contract (T001) is consumed by one production directive, one populator, one filter change, one Typst literal, and a regression suite. The `[P]` markers below are **batching hints** (independent files that may be edited back-to-back in one sitting), not multi-developer concurrency.

The dependency spine is non-negotiable:

```
T001 → T002 → T005 → T006 → T011 → T012 → T014 → T017
```

The Architect's **HIGH CONCERN-1** (h3→h4 heading normalization, T006) is a hard gate **before** any PDF baseline regeneration (T011). Without it the agentic-app PDF renders 0 MAESTRO layers and the invariant test (T010) false-greens.

---

## 2. Agent Assignment Matrix

Agent names are exact entries from `.claude/agents/_README.md`. Per CLAUDE.md fallback mappings: markdown/spec/doc + non-code file editing → **senior-backend-engineer**; validation/acceptance verification → **tester**. Deterministic PDF pipeline regeneration → **devops**. PR diff-scope judgment → **code-reviewer**.

| Task | Agent | Rationale (one line) | Est. |
|------|-------|----------------------|------|
| **T001** | senior-backend-engineer | Spec/markdown contract edit in `output-schemas.md` (Omission→all-7, Ordering→L1→L7, zero-finding cell schema) — doc-editing fallback. | 30m |
| **T002** | senior-backend-engineer | Rewrite the MAESTRO directive in `orchestrator.md` (markdown agent-prompt, FR-001/004/005/006) — doc-editing fallback. | 30m |
| **T003** [P] | senior-backend-engineer | Python filter removal at `extract-report-data.py:407` (FR-003, no canonical seeding) — backend script change. | 20m |
| **T004** [P] | senior-backend-engineer | Typst literal swap at `maestro-findings.typ:154` (FR-004, U+2014) — scoped non-code template edit. | 20m |
| **T005** | senior-backend-engineer | New stdlib populator `populate-maestro-coverage.py` (FR-007, heading-agnostic discovery + normalize-on-write + `--check`) — core Python authoring. | 2.5h |
| **T006** [US1] | senior-backend-engineer | Run populator over 9 in-scope files + normalize 3 h3→h4 headings (Architect HIGH gate) — script execution + content regeneration. | 45m |
| **T007** [US1] | tester | Acceptance verification: 7 canonical rows in L1→L7, L4 present, heading now `#### `, spot-check 2 examples — QA validation. | 30m |
| **T008** [US2] | tester | Cross-format parity check: markdown cell phrase == PDF prose phrase (assert phrase, NOT punctuation; PM OBS-2) — QA validation. | 30m |
| **T009** [P] [US3] | senior-backend-engineer | Author pytest unit in `test_extract_report_data.py` (FR-009a, len==7 + empty-findings group) — test authoring (Python). | 30m |
| **T010** [P] [US3] | senior-backend-engineer | Author new invariant test `test_maestro_coverage_invariant.py` (FR-009b, heading-agnostic, test-output excluded) — test authoring (Python). | 45m |
| **T011** [US3] | devops | Regenerate 6 gated PDF baselines via exact `extract-report-data.py` + `typst compile` pipeline under `SOURCE_DATE_EPOCH=1700000000` — deterministic build-artifact pipeline. | 45m |
| **T012** [US3] | tester | Run backward-compat (6 baselines byte-identical) + the two new test files; confirm all green — QA gate. | 20m |
| **T013** [P] | tester | Verify no SARIF/schema change via `git diff --stat` (FR-010) — negative-coverage validation. | 10m |
| **T014** | tester | Run `/aod.analyze`; confirm no cross-artifact inconsistencies (SC-005) — consistency validation. | 15m |
| **T015** [P] | senior-backend-engineer | Add CHANGELOG.md `feat(098)` entry — doc-editing fallback. | 10m |
| **T016** [P] | senior-backend-engineer | Create 2 follow-up GitHub issues (FR-011 Model B; FR-012 maestro-stack infographic) via `gh` — non-code tracked-work creation. | 20m |
| **T017** | code-reviewer | Assemble PR description; verify ONLY matrix rows/order changed in agentic-app diff (Risk 98.3, PM OBS-1) + note F-302 remedy — diff-scope review judgment. | 30m |

**Agent load summary** (no agent exceeds the 80% ceiling for this short cycle):
- **senior-backend-engineer**: T001, T002, T003, T004, T005, T006, T009, T010, T015, T016 (10 tasks — the implementation core; sequenced, never concurrent).
- **tester**: T007, T008, T012, T013, T014 (5 tasks — all verification/acceptance gates).
- **devops**: T011 (1 task — the deterministic baseline-regen pipeline).
- **code-reviewer**: T017 (1 task — PR diff-scope judgment).

---

## 3. Parallel Execution Waves

Waves are **sequential**; `[P]` tasks inside a wave are independent-file batches for one developer.

### Wave 0 — Setup / Shared Contract
**Tasks**: T001
**Agent**: senior-backend-engineer
**Why first**: Freezes the single format contract (all-7, L1→L7, zero-finding cell, `#### ` heading) that the directive, populator, and tests all reference. Nothing downstream is sound until this is pinned.
**Est.**: ~0.5h

### Wave 1 — Foundational (Production Render Path + Populator) — BLOCKS all user stories
**Tasks**: T002 → T005 (spine) · T003 [P] · T004 [P]
**Agent**: senior-backend-engineer
**Batching**: T003 + T004 are independent-file edits (Python filter / Typst literal) and may be done back-to-back; T002 (directive) and T005 (populator) author/consume the contract and carry the critical path.
**Gate before exit**: T005 populator must run clean in `--check` form and the 4 production-surface edits (T002–T004) must be in place.
**Est.**: ~3.5h (T005 dominates at ~2.5h)

### Wave 2 — US-1 Regeneration (Architect Sees Full Scan Span)
**Tasks**: T006 → T007
**Agents**: senior-backend-engineer (T006 run + normalize) → tester (T007 accept)
**Critical gate**: T006 performs the **h3→h4 normalization on the 3 named files** (agentic-app, agentic-app/sample-report, mobile-banking-app/sample-report) — Architect HIGH CONCERN-1. This MUST complete before Wave 4 (T011) baseline regen, or the agentic-app PDF renders 0 layers.
**Est.**: ~1.25h

### Wave 3 — US-2 Annotation Parity (Self-Documenting Zero Rows)
**Tasks**: T008
**Agent**: tester
**Depends on**: T006 (rows regenerated) + T004 (Typst literal). Asserts the cross-format **phrase** parity (sanctioned trailing-period difference in PDF prose).
**Close-gate**: US-1 + US-2 together are the **Issue #98 close-gate (Model A)**.
**Est.**: ~0.5h

### Wave 4 — US-3 Regression + Deterministic Baselines
**Tasks**: T009 [P] + T010 [P] (test authoring) → T011 (baseline regen) → T012 (gate)
**Agents**: senior-backend-engineer (T009, T010) · devops (T011) · tester (T012)
**Sequencing note**: Tests T009/T010 are *authored* against the target state (test-first per plan); they may be written any time after Wave 1, but they only go green after Wave 2 regeneration. **T011 is gated behind T006's heading normalization** (see Wave 2). T012 verifies all 6 baselines byte-identical + both new test files green.
**Est.**: ~2.25h

### Wave 5 — Polish, Gates & PR
**Tasks**: T013 [P] + T015 [P] + T016 [P] (independent polish) · T014 (analyze) · T017 (PR — last)
**Agents**: tester (T013, T014) · senior-backend-engineer (T015, T016) · code-reviewer (T017)
**Batching**: T013 (no-SARIF check), T015 (CHANGELOG), T016 (follow-up issues) are mutually independent. T014 (`/aod.analyze`) and T017 (PR) close the wave; T017 is strictly last.
**Est.**: ~1.5h

---

## 4. Quality Gates Between Waves

| Gate | After Wave | Pass Condition | Owner | On Fail |
|------|-----------|----------------|-------|---------|
| **G0 — Contract frozen** | Wave 0 | `output-schemas.md` carries all-7 + L1→L7 ordering + zero-finding cell schema + `#### ` heading preserved. | senior-backend-engineer | Re-edit T001; do not start Wave 1. |
| **G1 — Foundation ready** | Wave 1 | 4 production edits (T002–T004) landed; `populate-maestro-coverage.py --check` runs clean; no canonical seeding added (single source of truth, SC-003). | senior-backend-engineer | Fix populator/edit; block all user stories. |
| **G2 — Heading normalization done** | Wave 2 | The 3 named h3 files now `#### `; agentic-app shows 7 canonical rows incl. L4 in L1→L7 order; 2 examples spot-checked. **This gate explicitly precedes any baseline regen.** | tester (T007) | Re-run T006; never proceed to T011. |
| **G3 — #98 close-gate (Model A)** | Wave 3 | US-1 (all 7 layers visible) **and** US-2 (zero-finding phrase parity md↔PDF) both demonstrably pass on regenerated examples. | tester (T008) | Address render defect; this is the issue-close bar. |
| **G4 — Baselines byte-pass + tests green** | Wave 4 | `test_backward_compatibility.py`: 6 baselines byte-identical; `test_extract_report_data.py` + `test_maestro_coverage_invariant.py` green. | tester (T012) | Re-regen under `SOURCE_DATE_EPOCH=1700000000`; do not open PR. |
| **G5 — Pre-PR clean** | Wave 5 | No SARIF/schema diff (T013); `/aod.analyze` clean (T014); CHANGELOG `feat(098)` present; 2 follow-ups filed; agentic-app diff shows ONLY matrix row/order churn. | code-reviewer (T017) | Resolve before `gh pr ready`; PR title MUST be `feat(098): …`. |

---

## 5. Time Estimate Per Wave

| Wave | Scope | Est. | Cumulative |
|------|-------|------|-----------|
| Wave 0 | Setup / contract (T001) | 0.5h | 0.5h |
| Wave 1 | Foundational + populator (T002–T005) | 3.5h | 4.0h |
| Wave 2 | US-1 regen + accept (T006–T007) | 1.25h | 5.25h |
| Wave 3 | US-2 parity (T008) | 0.5h | 5.75h |
| Wave 4 | US-3 tests + baselines (T009–T012) | 2.25h | 8.0h |
| Wave 5 | Polish + gates + PR (T013–T017) | 1.5h | 9.5h |

**Total**: ~9.5h focused work ≈ **1.0–1.5 working days** — within the approved envelope. Realistic (with commit/verify overhead between logical groups) lands near the **1.25-day** midpoint; pessimistic (a baseline byte-determinism retry on Risk 98.1/98.3) stays under 1.5 days because the regen tail (T011) is isolated and re-runnable.

---

## 6. Handoff to Orchestrator

**Feasibility**: APPROVED. **Strategy**: 6 sequential waves along the critical path `T001→T002→T005→T006→T011→T012→T014→T017`, with `[P]` batching inside Waves 1/4/5.

**Hard constraints for the executor**:
1. **Gate G2 before T011** — the h3→h4 normalization (T006, Architect HIGH CONCERN-1) MUST complete before baseline regeneration, else agentic-app PDF renders 0 layers and T010 false-greens.
2. **No canonical seeding in T003** — `layer_groups` stays seeded from `parsed_layers` (PDF can never show more layers than the markdown authored; SC-003).
3. **Determinism** — every PDF (re)gen + the backward-compat test runs under `SOURCE_DATE_EPOCH=1700000000` (ADR-021).
4. **Annotation parity asserts the phrase, not the punctuation** — markdown cell has no trailing period; Typst prose adds one (sole sanctioned cross-format difference; PM OBS-2).
5. **PR title** must be `feat(098): …` (release-please gate).

**Excluded files (never force-fit a MAESTRO table)**: `examples/predictive-ml-app/sample-report/threats.md`, `examples/consumer-agent-app/sample-report/threats.md`, and all `examples/**/test-output/**`.

**Receive-back for sign-off**: completion report with all 17 tasks marked `[X]`, G3 (close-gate) + G4 (baselines byte-pass) evidence, no `.aod/` modifications, blockers resolved.

---

**End of Agent Assignments — Feature 098**
