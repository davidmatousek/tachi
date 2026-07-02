# Agent Assignments — F-217 Detect-Images Duplicate Cleanup

**Feature**: 217 · Opt-In Mislabeled-Image Removal
**Owner**: team-lead | **Date**: 2026-07-01
**Feasibility**: [feasibility-check.md](feasibility-check.md) — APPROVED_WITH_CONCERNS · 0.5 / **1.0** / 2.0 eng-days
**Tasks**: [tasks.md](tasks.md) (T001–T017) · **Single build wave**, internal sequencing US1 → US2 ∥ US3 → Polish

Agent names below are exact registry entries from `.claude/agents/_README.md`. No invented labels.

---

## Agent Selection Rationale

| Agent | Tier | Why |
|-------|------|-----|
| **senior-backend-engineer** | sonnet | Authors ALL production code (`extract-report-data.py`) AND the co-located **white-box pytest** cases (subprocess CLI harness). Also owns verification/dogfood/docs tasks. |
| **code-reviewer** | opus (verdict gate) | Owns the T015 safety-invariant review — renders binding APPROVED / CHANGES_REQUESTED on the deletion primitive (SC-003 / INV-1 / INV-2 / MED-1). |

**Deliberately NOT assigned**:
- `tester` — BDD/Gherkin specialist; a poor fit for a white-box pytest module. Test authoring stays with senior-backend-engineer (per feasibility decision).
- `devops` — no deployment task; PR squash-merge is "production" for this template repo (plan Constitution VII).
- `security-analyst` — no assignable task (stdlib-only, no new deps, no network, local file deletes). The `/aod.build` Security Scan (Step 7) auto-runs the `security` skill over the branch diff — pipeline gate, not a task here.
- `frontend-developer` / `ux-ui-designer` — no UI surface (Design Quality Gate N/A).

---

## Agent Assignment Matrix (T001–T017)

| Task | Description (abbrev.) | Agent | Segment |
|------|-----------------------|-------|---------|
| T001 | Record LITERAL pre-state pytest totals → pre-state.md | senior-backend-engineer | S1 Setup |
| T002 | Extend `run_extract` with `extra_args` param | senior-backend-engineer | S1 Setup |
| T003 | Write 9 US1 pytest cases (AC-1a–1h + FR-005) — must FAIL first | senior-backend-engineer | S2 US1 |
| T004 | `filecmp` import + `_maybe_delete_mislabeled` helper | senior-backend-engineer | S2 US1 |
| T005 | Wire Moment A (pre-existing pairs branch) | senior-backend-engineer | S2 US1 |
| T006 | Wire Moment B (recovery write, `pre_existed` guard) | senior-backend-engineer | S2 US1 |
| T007 | Add `--cleanup-mislabeled-images` to parser + thread in main | senior-backend-engineer | S2 US1 |
| T008 | Verify US1 green + commit (MVP checkpoint) | senior-backend-engineer | S2 US1 |
| T009 | US2 pre-cleanup baseline → before.typ | senior-backend-engineer | S3a US2 |
| T010 | **AC-2b gate check** — repo-search for snapshot consumers | senior-backend-engineer *(defer decision = [MANUAL-ONLY] human)* | S3a US2 |
| T011 | Run flag against snapshot dir (6 deletions) | senior-backend-engineer | S3a US2 |
| T012 | Path-invariance proof + commit (SC-001: 6→0) | senior-backend-engineer | S3a US2 |
| T013 | [P] Docs note in typst-artifacts.md (AC-3a) | senior-backend-engineer | S3b US3 |
| T014 | Optional cross-ref + OQ-1 guard verify | senior-backend-engineer | S3b US3 |
| T015 | **Safety-invariant code review** → .aod/results/code-reviewer.md | **code-reviewer** | S4 Polish |
| T016 | Commit-first → gated 15-module pytest + catalog-drift green | senior-backend-engineer | S4 Polish |
| T017 | Quickstart end-to-end validation (SC-001/002/003) + post-state | senior-backend-engineer | S4 Polish |

---

## Single Build Wave — Internal Segments

The feasibility decision is **one build wave** (multi-wave rejected: coordination overhead disproportionate to <100 net lines). The wave sequences into four internal segments; only S3a ∥ S3b parallelize.

```
S1 Setup ──▶ S2 US1 (critical path, MVP) ──▶ ┌─ S3a US2 (gated) ─┐ ──▶ S4 Polish
                                             └─ S3b US3 [P] ─────┘
```

### Segment S1 — Setup (T001 → T002) · sequential
- senior-backend-engineer. T001 before T002 (record totals before touching the harness file — KB Entry 15).
- **Effort: 0.05d**

### Segment S2 — US1 MVP (T003 → T004 → T005 → T006 → T007 → T008) · sequential
- senior-backend-engineer. **Structurally serial**: T004–T007 all edit `extract-report-data.py` — no [P] possible. T003 tests authored FIRST and proven FAILING before T004.
- Critical path of the whole feature. T005/T006 (double-gate in both moments) is the one spot needing genuine care.
- **Effort: 0.5d** (dominant segment)

### Segment S3a — US2 dogfood, gated (T009 → T010 → T011 → T012) · sequential
- senior-backend-engineer. **Depends on S2/T008** (exercises the shipped flag). T010 gate precedes the destructive T011.
- **Effort: 0.20d** (near-zero if T010 defers)

### Segment S3b — US3 docs (T013 [P] → T014) · sequential, ∥ with S3a
- senior-backend-engineer (docs). **Depends on S2/T008** (accurate flag semantics); independent of S3a (different file tree). May run as a second senior-backend-engineer instance concurrent with S3a.
- **Effort: 0.15d**

### Segment S4 — Polish (T015 → T016 → T017) · sequential
- **T015 code-reviewer** (binding safety gate) → then senior-backend-engineer for T016 (commit-first gated suite) → T017 (quickstart validation).
- **Effort: 0.10d**

**Effort total: 0.05 + 0.5 + 0.20 + 0.15 + 0.10 = 1.0 eng-day** (central). Wall-clock compresses S3a∥S3b (~0.20d) if two SBE instances run; floor 0.5d if T010 defers US2 and US3 stays terse.

---

## Quality Gates Between Segments

| Gate | Position | Pass Criteria | Owner |
|------|----------|---------------|-------|
| **G0** | Before S1 | On `217-detect-images-duplicate-cleanup` branch (NOT main); `main == origin/main` (KB18) | senior-backend-engineer |
| **G1** | After S1 (T002) | Harness extended; T001 totals still reconcile (no regression from `extra_args`) | senior-backend-engineer |
| **G2** | After S2 (T008) — **MVP gate** | 9 T003 cases green; `test_extractor_contract_fixes.py` UNMODIFIED + green (FR-006 oracle); no-flag byte-identical (SC-002); **committed** | senior-backend-engineer |
| **G3** | At T010 — **AC-2b decision gate** | CLEAN → proceed T011–T012. CONSUMER surfaces → **escalate (human judgment)**, defer US2, skip to S4 `[MANUAL-ONLY]` | senior-backend-engineer → human |
| **G4** | After S3 (T012 + T014) | before.typ == after.typ (AC-2a path-invariance); exactly 6 `.jpg` deleted + 6 `.png` survive; US3 docs present; OQ-1 guard verified; **committed** | senior-backend-engineer |
| **G5** | S4 — **binding safety gate** | **T015 code-reviewer APPROVED**: no deletion path without BOTH gates (INV-1), INV-2 structural guarantee holds, MED-1 try/except wraps whole attempt, stderr matches cli-contract §3 → then T016 gated 15-module subset + catalog-drift green on committed HEAD → T017 SC-001/002/003 validated | code-reviewer → senior-backend-engineer |
| **G6** | Build pipeline | `/aod.build` Security Scan (Step 7) + Economy Gate (Step 8) clean over branch diff (Design Quality Gate N/A — no UI) | pipeline |

**Blocking gates**: G2 (MVP), G5/T015 (code-reviewer binding verdict). A CHANGES_REQUESTED at G5 loops back to senior-backend-engineer before feature-complete.

---

## Carry-Forward Concerns (from feasibility + tasks review)

1. **Branch hygiene** — enforce G0 before any T004 edit / T008 commit (session started on `main`).
2. **T010 defer = human call** — build agent escalates on any consumer hit; does not auto-decide.
3. **T014 stays optional** — force only the OQ-1 guard half; the cross-reference is discretionary.
4. **F-248/F-256 harness** — T016 clones committed HEAD; commit before the gated subset (already sequenced).

---

*Team-lead sign-off: APPROVED_WITH_CONCERNS. Ready for orchestrator hand-off (single wave, senior-backend-engineer primary, code-reviewer safety gate at G5).*
