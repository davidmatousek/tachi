---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-07-01
    status: APPROVED
    notes: "3/3 stories correct priority + MVP; 9/9 FRs, 11/11 ACs + deletion-failure mapped (T003/T009–T012/T013–T014); all 6 PRD Out items respected, T014 guards OQ-1; SC-001/002/003 traceable. No scope creep. Details: .aod/results/product-manager.md"
  architect_signoff:
    agent: architect
    date: 2026-07-01
    status: APPROVED_WITH_CONCERNS
    notes: "Ordering sound, line-anchors verified live; MED-1→T004+T015, MED-2→T003 carried; T005/T006 both-moments split has no gap. 2 items folded post-review: MED-3 fault-injection cases must run in-process via _load_extract_module (subprocess can't be monkeypatched) — folded into T003; NIT-1 commit verb — folded into T014. Details: .aod/results/architect.md"
  techlead_signoff:
    agent: team-lead
    date: 2026-07-01
    status: APPROVED_WITH_CONCERNS
    notes: "All 4 feasibility criteria PASS; 17 tasks = safety-verification cadence, not over-slicing; critical path T001→T008; estimate reconciles to 0.5/1.0/2.0; T010 gate downside-only. Carry-forwards: branch checked out before commits; T010 defer = human call; T014 optional; agent fit binding (SBE code+pytest, code-reviewer T015). agent-assignments.md written. Details: .aod/results/team-lead.md"
---

# Tasks: Detect-Images Duplicate Cleanup — Opt-In Mislabeled-Image Removal

**Input**: Design documents from `/specs/217-detect-images-duplicate-cleanup/`
**Prerequisites**: plan.md (PM + Architect approved), spec.md (PM approved), research.md, data-model.md, contracts/cli-contract.md, quickstart.md

**Tests**: REQUIRED — spec FR-007 mandates dedicated automated cases for AC-1a–AC-1h plus the deletion-failure branch (Architect MED-2); plan is test-first (Constitution VI).

**Organization**: Tasks grouped by user story. Single build wave (team-lead feasibility: multi-wave rejected for <100 net lines) — US1 first, then US2 ∥ US3, then polish.

> **Definition of Done** (canonical bar = constitution VII):
> 1. ✅ Pushed to Production — feature deployed and operational.
> 2. ✅ Tested — all automated tests pass (unit, integration, E2E, performance)
> 3. ✅ User Validated — real-world usage confirmed by actual users/stakeholders.

<!-- DOD-ACK -->

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

## Path Conventions
Single project at repo root: production code in `scripts/`, tests in `tests/scripts/`, doc surface in `.claude/skills/tachi-report-assembly/references/`, dogfood target in `examples/agentic-app/test-output/2026-04-19T03-20-30/`.

---

## Phase 1: Setup (Pre-State & Harness)

**Purpose**: Freeze the pre-change baseline and prepare the test harness. KB Entry 15: record LITERAL pre-state totals before touching baseline-coupled files.

- [ ] T001 Record LITERAL pre-state pytest totals: run `python3 -m pytest tests/scripts/test_extract_report_data.py tests/scripts/test_extractor_contract_fixes.py -q` and save exact pass/fail/total counts + command output to specs/217-detect-images-duplicate-cleanup/pre-state.md (KB Entry 15 discipline)
- [ ] T002 Extend `run_extract` in tests/scripts/test_extract_report_data.py with optional `extra_args=None` parameter appended to the subprocess argv (contracts/cli-contract.md §4); all existing call sites unchanged; re-run the module to confirm totals still match T001

---

## Phase 2: Foundational (Blocking Prerequisites)

**No foundational tasks** — User Story 1 itself is the foundation: US2 (dogfood) and US3 (docs) both consume the flag US1 ships. Phase 1 is the only cross-story prerequisite.

**Checkpoint**: After T002 — user story implementation can begin.

---

## Phase 3: User Story 1 — Opt-in cleanup of mislabeled duplicate images (Priority: P1) 🎯 MVP

**Goal**: `--cleanup-mislabeled-images` flag with double-gated (flag AND byte-identity), direction-agnostic deletion wired into BOTH moments; no-flag behavior byte-identical; best-effort error handling.

**Independent Test**: Run the extractor with/without the flag against seeded fixture directories (mislabeled/corrected pairs); assert deletions, emitted paths, stderr records, exit codes (spec US-1 Independent Test).

### Tests for User Story 1 (write FIRST — new-behavior cases MUST FAIL before implementation)

- [ ] T003 [US1] Write 9 test cases in the Issue-#215 section of tests/scripts/test_extract_report_data.py per the plan.md Test Plan table: AC-1a delete+emit+one-record, AC-1b no-flag byte-identical (regression pin — passes pre-implementation), AC-1c recovery write-verify-delete, AC-1d non-identical untouched, AC-1e all-correct no-op, AC-1f truncated copy no-delete (short `copyfile` fault injection), AC-1g cross-swap no-delete, AC-1h legitimate mixed pair untouched, FR-005 deletion-failure best-effort (`os.remove`/`Path.unlink` raising `OSError` → file persists, one failure stderr line, extraction completes, output unchanged — Architect MED-2). 7 cases go through the CLI path `run_extract(extra_args=["--cleanup-mislabeled-images"])` with `_write_minimal_png/_jpeg` fixtures; the 2 fault-injection cases (AC-1f, FR-005) MUST run in-process via the existing `_load_extract_module()` helper calling `detect_images(..., cleanup=True)` with monkeypatch — `run_extract` is a subprocess and monkeypatch cannot cross the process boundary (Architect MED-3); assert no-exception + preservation + stderr record as the exit-0 equivalent. Verify the 8 new-behavior cases FAIL (flag/kwarg unrecognized) and AC-1b passes

### Implementation for User Story 1 (all in scripts/extract-report-data.py — sequential, same file)

- [ ] T004 [US1] Add stdlib `filecmp` import and `_maybe_delete_mislabeled(mislabeled_fp, counterpart_fp)` helper (~12 lines) in scripts/extract-report-data.py: gate-2 check (counterpart exists, non-zero, `filecmp.cmp(..., shallow=False)`) then delete + one stderr record; ENTIRE attempt (probe + compare + delete) wrapped in `try/except OSError` logging failure to stderr, never raising (FR-005/INV-3, Architect MED-1); returns whether deletion happened
- [ ] T005 [US1] Thread `cleanup=False` defaulted kwarg into `detect_images` (FR-006; two-positional callers unchanged) with `filecmp.clear_cache()` at entry when cleanup is on, and wire Moment A in the self-consistent branch (~L1506–1510): when cleanup, probe the other candidates of the stem; for each mislabeled one resolve its correctly-labeled counterpart (stem + canonical ext for its content format) and call the helper (AC-1a/1d/1e/1h; chosen is structurally undeletable — INV-2)
- [ ] T006 [US1] Wire Moment B in the recovery branch (~L1512–1525): record `pre_existed = target_path.exists()` BEFORE `shutil.copyfile`; after the write, when cleanup AND NOT `pre_existed`, call the helper on (original, written sibling) — byte-identity doubles as copy-success verification (AC-1c/1f/1g)
- [ ] T007 [US1] Add `--cleanup-mislabeled-images` (`action="store_true"`, help per contracts/cli-contract.md §1) to `build_parser()` (~L2020) and thread `cleanup=args.cleanup_mislabeled_images` at the single `detect_images` call site in `main()` (~L2164)
- [ ] T008 [US1] Verify US1 green: run both extractor suites — all 9 T003 cases pass, existing #215 tests (:242/:284/:316) pass, tests/scripts/test_extractor_contract_fixes.py UNMODIFIED and green (FR-006 compat oracle), totals reconcile against T001 pre-state.md; commit US1 work

**Checkpoint**: US1 fully functional and independently testable — MVP complete.

---

## Phase 4: User Story 2 — In-repo dogfood cleanup of the legacy snapshot (Priority: P2, gated)

**Goal**: Remove the 6 mislabeled `.jpg` files (~6.75 MB) from `examples/agentic-app/test-output/2026-04-19T03-20-30/` via the new flag with path-invariance proof (AC-2a); defer with documented rationale if a consumer surfaces (AC-2b).

**Independent Test**: Flag run against the snapshot dir → 6 deletions; `report-data.typ` byte-identical pre/post; extractor module green (spec US-2 Independent Test).

- [ ] T009 [US2] Pre-cleanup baseline: generate `report-data.typ` for examples/agentic-app/test-output/2026-04-19T03-20-30/ into scratch as before.typ (quickstart.md path-invariance procedure); confirm the dir holds exactly the 6 known mislabeled-`.jpg` + byte-identical `.png` pairs
- [ ] T010 [US2] AC-2b gate check: search the repo for any consumer of the 6 snapshot `.jpg` paths (tests, scripts, docs, workflows); expected result NONE (OQ-2 = CLEAN, triple-verified in research.md). If a real consumer surfaces: STOP — defer US-2 with a documented rationale comment on Issue #217 and skip T011–T012 `[MANUAL-ONLY] defer decision is a human judgment call on consumer significance`
- [ ] T011 [US2] Run the flag against the snapshot dir: `python3 scripts/extract-report-data.py --target-dir examples/agentic-app/test-output/2026-04-19T03-20-30 --template-dir <per quickstart> --output <scratch>/after.typ --cleanup-mislabeled-images`; verify exactly 6 deletion stderr records and the 6 `.jpg` files removed, all 6 `.png` survivors intact
- [ ] T012 [US2] Path-invariance proof + commit: byte-compare before.typ vs after.typ (MUST be identical — AC-2a); run both extractor suites green; verify `git status` shows exactly 6 deletions under the snapshot dir; commit the deletions (SC-001: 6 → 0)

**Checkpoint**: US1 and US2 both complete; repo no longer carries duplicate pairs.

---

## Phase 5: User Story 3 — Documented duplicate-pair expectation and cleanup path (Priority: P3)

**Goal**: Report-assembly reference surface documents the duplicate-pair origin, sanctioned flag invocation, and double-gate semantics (AC-3a).

**Independent Test**: Inspect `.claude/skills/tachi-report-assembly/references/` for origin + flag + double-gate coverage with no `find … rm` recommendation (spec US-3 Independent Test).

- [ ] T013 [P] [US3] Add "Legacy duplicate pairs & sanctioned cleanup" note to .claude/skills/tachi-report-assembly/references/typst-artifacts.md near Image File Validation / legacy extraction reference (L30–36/L112–114): duplicate-pair origin (gemini-2.5-flash-image fallback era), flag invocation, double-gate safety semantics, explicit "do NOT use raw find … rm" (AC-3a)
- [ ] T014 [US3] Add a one-line cross-reference from .claude/skills/tachi-report-assembly/references/typst-template-contract.md Image Paths section (L92–103) to the typst-artifacts.md note ONLY if it reads naturally (plan US-3: optional); verify .claude/agents/tachi/report-assembler.md is NOT modified to pass the flag (OQ-1: human opt-in only); commit US3 work

**Checkpoint**: All three user stories independently complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Safety-invariant review, gated-suite verification, final validation.

- [ ] T015 Safety-invariant code review (code-reviewer): verify no deletion path exists without BOTH gates (SC-003/INV-1 — `_maybe_delete_mislabeled` is the sole deletion primitive in the module), INV-2 structural guarantee holds, best-effort try/except covers the whole attempt (MED-1), stderr records match contracts/cli-contract.md §3; findings to .aod/results/code-reviewer.md
- [ ] T016 Commit all work FIRST, then run the gated 15-module pytest subset locally (F-248/F-256 harness clones committed HEAD — never run before committing) and confirm `tachi-catalog-drift.yml` checks stay green after the US2 deletions (KB Entry 19; extractor is not render-coupled — expected green)
- [ ] T017 Run quickstart.md validation end-to-end: no-flag run byte-identical on a scratch fixture (SC-002), flag run deletes only under the double gate (SC-003), record post-state pytest totals against T001 pre-state.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 → T002 (totals must be recorded before the harness file changes)
- **Foundational (Phase 2)**: none — Phase 1 completion unblocks US1
- **US1 (Phase 3)**: depends on Phase 1. Internal: T003 (tests, FAIL) → T004 → T005 → T006 → T007 (same file, sequential) → T008 (verify+commit)
- **US2 (Phase 4)**: depends on US1 complete (T008) — exercises the shipped flag. Internal: T009 → T010 (gate) → T011 → T012
- **US3 (Phase 5)**: depends on US1 complete (T008) for accurate flag semantics; independent of US2 — **runs in parallel with Phase 4**
- **Polish (Phase 6)**: T015 after all code final; T016 after all commits; T017 last

### User Story Dependencies

- **US1 (P1)**: independent — MVP
- **US2 (P2)**: consumes US1's flag; gated by T010 (AC-2b defer path)
- **US3 (P3)**: documents US1's flag; parallel with US2 (different files)

### Parallel Opportunities

- T013 [P] (skill doc) runs parallel with all of Phase 4 (examples/ + scratch)
- Everything else is effectively sequential: one production file (T004–T007), one test file (T002/T003), and verification tasks that depend on committed state

---

## Parallel Example: after US1 checkpoint (T008)

```bash
# US2 and US3 proceed concurrently:
Task: "T009–T012 dogfood cleanup in examples/agentic-app/test-output/2026-04-19T03-20-30/"   # senior-backend-engineer
Task: "T013 docs note in .claude/skills/tachi-report-assembly/references/typst-artifacts.md" # senior-backend-engineer (docs)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 (T001–T002) → Phase 3 (T003–T008)
2. **STOP and VALIDATE**: 9 new tests green, contract-fixes module untouched-green, no-flag byte-identical
3. US1 alone is a shippable MVP (the sanctioned cleanup path exists for adopters)

### Incremental Delivery

1. US1 → validate → commit (MVP)
2. US2 (gated) ∥ US3 → validate each independently → commit
3. Polish (T015–T017) → feature complete at the 1.0 eng-day central estimate (floor 0.5 if T010 defers US2 and US3 goes terse)

### Estimate Reconciliation (feasibility-check.md)

- US1 code+tests ≈ 0.5d (T001–T008) · US2 ≈ 0.25d (T009–T012, near-zero if deferred) · US3 ≈ 0.25d (T013–T014) · Polish inside AOD overhead — matches the 0.5 / 1.0 / 2.0 envelope, no re-estimate needed

---

## Notes

- Single production file means US1 implementation tasks are deliberately sequential — no same-file [P] conflicts
- Verify T003's new-behavior tests FAIL before T004 begins (test-first)
- Commit after each checkpoint (T008, T012, T014) — T016's gated harness clones committed HEAD
- Agent fit per feasibility: senior-backend-engineer authors code AND pytest cases (tester agent is BDD/Gherkin — poor fit for white-box pytest); code-reviewer owns the T015 safety gate
