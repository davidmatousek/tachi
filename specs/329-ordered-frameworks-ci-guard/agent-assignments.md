# Agent Assignments: ORDERED_FRAMEWORKS Catalog-Drift CI Guard (#329)

**Branch**: `329-ordered-frameworks-ci-guard` · **Date**: 2026-06-30 · **Estimate**: floor 1.0 / plan 1.5 / ceiling 3.0 eng-days
**Source**: derived from [feasibility-check.md](./feasibility-check.md) (Team-Lead capacity model — one engineer, senior-backend profile, **no cross-agent wave fan-out**) + [tasks.md](./tasks.md) (triple-approved).

> Single-engineer feature. The "waves" below are **execution checkpoints for one implementer**, not concurrent agent lanes. `[P]` inside a wave = disjoint-file parallelism the one engineer may interleave (or thin Track A∥B per plan M1∥M2); it does NOT imply multiple agents.

## Agent Assignment Matrix

| Task | Description (short) | Agent (`subagent_type`) |
|------|---------------------|-------------------------|
| T001 | Confirm preconditions (branch, live loader refs, no sidecar) | `senior-backend-engineer` |
| T002 | Verify deps (pytest/pyyaml; typst 0.14.2) | `senior-backend-engineer` |
| T003 | Pre-state go/no-go gate (run byte-identity suite) [MANUAL-ONLY] | `senior-backend-engineer` |
| T004 | Fingerprint core (`check-catalog-drift.py`, C-2 isinstance guard) | `senior-backend-engineer` |
| T005 | `--check` mode (find_drift, fail-closed, message) | `senior-backend-engineer` |
| T006 | Regen script + `--emit` (formalize recipe, sidecar byproduct) | `senior-backend-engineer` |
| T007 | Real local regen/byte-compare cycle [MANUAL-ONLY] | `senior-backend-engineer` |
| T008 | Test module: live gate + catch cases (cache_clear) | `senior-backend-engineer` |
| T009 | Test: ignore cases (#333 / non-member / clean) | `senior-backend-engineer` |
| T010 | CI workflow `tachi-catalog-drift.yml` (dual-trigger) | `senior-backend-engineer` |
| T011 | Test: dynamic future-member case | `senior-backend-engineer` |
| T012 | ADR-037 amendment (new D-14, C-1) | `senior-backend-engineer` |
| T013 | Docs note + CHANGELOG | `senior-backend-engineer` |
| T014 | File OQ-6 re-tag follow-up issue | `senior-backend-engineer` |
| T015 | Integration + quickstart negative checks [MANUAL-ONLY] | `tester` |
| T016 | Deliver gate (main==origin/main, merge via devops, release-please) | `devops` |

**Utilization**: `senior-backend-engineer` 14 tasks (build/test/docs) · `tester` 1 (acceptance) · `devops` 1 (deliver). Architect/PM/Team-Lead discharged at plan/tasks sign-off; the Architect re-engages only at the `/aod.build` checkpoints.

## Parallel Execution Waves (single-engineer checkpoints)

| Wave | Tasks | Intra-wave [P] | Gate to exit | Est. |
|------|-------|----------------|--------------|------|
| **W1 — Setup + Foundational** | T001, T002, T003, T004 | T001∥T002; T003∥T004 | T003 verdict recorded (KB-15 totals); fingerprint core importable | ~0.3d |
| **W2 — US1 guard core (load-bearing)** | T005, T006, T007, T008 | Track A (T005→T006→T007) ∥ Track B (T008, stub sidecar) | Guard catches drift; sidecar committed; live-tree case green on clean tree **(MVP)** | ~0.6d |
| **W3 — US2/US3/US4 + docs** | T009, T010, T011, T012, T013, T014 | T009→T011 sequential (same test file); T012∥T013∥T014 (disjoint docs) | All 4 stories proven; workflow live on PR+push:[main]; ADR/docs/CHANGELOG done | ~0.4d |
| **W4 — Acceptance + Deliver** | T015 (`tester`), T016 (`devops`) | — | Quickstart negatives pass; `main`==`origin/main` verified; merged `feat(329:)`; release-please opens | ~0.2d |

## Quality Gates Between Waves

- **W1→W2**: T003 go/no-go is the schedule-defining gate. If RED, the W2 T007 regen cycle also refreshes the 6 baselines (bounded remediation, ceiling-day driver C-B) before the guard goes green.
- **W2→W3**: MVP gate — the guard must catch a probed drift AND pass on the clean tree (sidecar committed) before broadening to US2/US3/US4.
- **W3→W4**: full green — all 6 synthetic cases + the live-tree case pass; the dual-trigger workflow is live.
- **W4 exit (DoD)**: constitution VII — pushed (post-green, via devops), tested (both triggers), validated (quickstart negatives + sidecar-by-regen). KB-18 deliver gate: verify branch-current + `main`==`origin/main` (full-tree diff) before any merge/push.

## Capacity Analysis

- **Bottleneck**: none — single engineer, linear critical path (T004→T005→T006→T007→T008→T010→T015→T016).
- **Variance driver (watch)**: the FR-2 regen lane (T006/T007) — the one novel surface (no `regenerate-ca-baselines.sh` exists yet); Team-Lead C-B. Pushes toward the ceiling day if T003 is RED.
- **Critical path**: W1(T004) → W2(T005→T006→T007→T008) → W3(T010) → W4(T015→T016). [MANUAL-ONLY] Typst-rendering points (T003, T007, T015) are the only non-automatable steps.
- **Slack**: floor 1.0 / plan 1.5 / ceiling 3.0 — ~1.5d of slack to the ceiling absorbs the T003-red remediation tail.
