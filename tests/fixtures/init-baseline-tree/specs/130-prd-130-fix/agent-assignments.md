# Agent Assignments — Feature 130: Fix Attack Path Mermaid Rendering When mmdc Is Not Installed

**Feature ID**: 130-prd-130-fix
**Generated**: 2026-04-11
**Team Lead**: team-lead agent
**Source**: `specs/130-prd-130-fix/tasks.md` (32 tasks)
**Plan Reference**: `specs/130-prd-130-fix/plan.md` (7 phases)
**PR Target Branch**: `main` (feature branch `130-prd-130-fix`)
**Prior Reviews**:
- PM APPROVED (`.aod/results/product-manager-tasks.md`)
- Architect APPROVED (`.aod/results/architect-tasks.md`)
- Team-Lead APPROVED_WITH_CONCERNS (`.aod/results/team-lead-tasks.md`) — 7 non-blocking refinements carried forward into Section 6 below

---

## 1. Overview

| Field | Value |
|---|---|
| Total tasks | **32** (T001-T032) |
| Total estimate | **4.35d PRD + 0.65d buffer = 5.0d target** (honest range: 4.8-5.4d, solo-dev serial) |
| Execution waves | **7 waves** (1 per tasks.md phase, with US3 optionally overlapping US1/US2 if parallel capacity exists) |
| Critical path length | **~5.0 days** (solo-dev serial: Setup → Foundational → US1 → US2 → Cross-Cutting/CI → Polish; US3 interleaved but does not shorten the chain) |
| PR target branch | `main` |
| Feature branch | `130-prd-130-fix` |
| Priority | **P0 bug fix** — 5-day target is functionally unbuffered |

**Workload Distribution**:

| Agent | Share | Scope |
|---|---:|---|
| `senior-backend-engineer` | **~62%** | All Python/shell/Typst code edits (T005-T007, T010-T011), all markdown authoring (T013-T017, T025-T026, T032), grep verification (T019, T023-T024) |
| `tester` | **~22%** | All pytest authoring (T004, T009), baseline pre/post capture (T002, T022), manual E2E validation (T027-T029), full-suite run (T030) |
| `architect` | **~6%** | ADR-022 authoring (T003) — first-of-its-kind CLI-prerequisite governance artifact |
| `devops` | **~6%** | CI workflow authoring (T018), example baseline regeneration (T020-T021) |
| `code-reviewer` | **~2%** | Negative-task verification (T019 cross-check), constitutional walk-through (T031) |
| `orchestrator` | **~2%** | Phase 1 setup/context load (T001) |

**Load balance**: `senior-backend-engineer` is the anchor agent because Feature 130 is fundamentally a per-file surgical fix with ~17 files touched across Python, Typst, shell, markdown, and YAML. No single agent exceeds ~65% loading. Solo-dev critical path is the 5-day anchor; multi-agent parallelism is an optimization layer on top.

---

## 2. Agent Assignment Matrix (T001-T032)

All agent names below are **exact matches** from `.claude/agents/_README.md`. No invented labels.

### Phase 1 — Setup

| Task | Agent | Description | Estimate | Parallel? |
|---|---|---|---|---|
| T001 | `orchestrator` | Read plan.md, research.md, spec.md, constitution.md; confirm feature branch `130-prd-130-fix`; confirm `.aod/results/` exists | 0.05d (10 min) | Sequential (entry point) |

### Phase 2 — Foundational (Blocking Prerequisites)

| Task | Agent | Description | Estimate | Parallel? |
|---|---|---|---|---|
| T002 | `tester` | Run `SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py` and capture baseline pretest state to `.aod/results/130-baseline-pretest.md` (R9 High-priority) | 0.1d (30 min) | [P] with T003 |
| T003 | `architect` | Author `docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md` — first-of-its-kind CLI-prerequisite governance ADR; cross-refs ADR-014 and ADR-021; includes Future Work clause (R1, R2) | 0.25d PRD / **0.4d realistic** (see Section 6 T1) | [P] with T002 |

**Checkpoint**: Baseline captured, ADR-022 in place. Phase 3+ unblocked.

### Phase 3 — User Story 1 (MVP: Preflight Gate)

| Task | Agent | Description | Estimate | Parallel? |
|---|---|---|---|---|
| T004 | `tester` | Create `tests/scripts/test_mmdc_preflight.py` with 4 failing preflight pytest cases (R5, R7) | 0.1d (45 min) | Sequential (blocks T005-T007) |
| T005 | `senior-backend-engineer` | Modify `.claude/commands/tachi.security-report.md` Step 1: add shell-level preflight mmdc check | 0.05d (20 min) | [P] with T007 |
| T006 | `senior-backend-engineer` | Modify `scripts/extract-report-data.py` lines 721-730: replace silent fallback with `raise RuntimeError(...)` — **serializes on the shared extract-report-data.py file with T010/T011** | 0.1d (30 min) | Sequential (blocks T008, T010) |
| T007 | `senior-backend-engineer` | Delete lines 78-86 in `templates/tachi/security-report/attack-path.typ` (text-fallback branch) | 0.02d (5 min) | [P] with T005 |
| T008 | `tester` | Run `pytest tests/scripts/test_mmdc_preflight.py -k preflight -v`; confirm all 4 T004 tests pass; atomic commit T004-T008 | 0.05d (10 min) | Sequential (US1 gate) |

**Checkpoint**: US1 shippable as MVP — preflight gate fires loudly on shell without mmdc.

### Phase 4 — User Story 2 (Mid-Render Loud Failure)

| Task | Agent | Description | Estimate | Parallel? |
|---|---|---|---|---|
| T009 | `tester` | Extend `tests/scripts/test_mmdc_preflight.py` with 5 failing mid-render aggregator tests (R5, **R6 High priority**, R7) | 0.15d (60 min) | Sequential (blocks T010) |
| T010 | `senior-backend-engineer` | Modify `_render_single` in `scripts/extract-report-data.py` to return structured failure record (dict with id/file_path/failure_class/stderr_excerpt) | 0.15d (45 min) | Sequential (blocks T011; same file as T006) |
| T011 | `senior-backend-engineer` | Modify `as_completed` loop in `render_mermaid_to_png()`: collect failures, format per R6 spec, `raise RuntimeError(message)` — **R6 is the single highest-priority architect refinement** | 0.15d (45 min) | Sequential (after T010) |
| T012 | `tester` | Run `pytest tests/scripts/test_mmdc_preflight.py -v`; confirm all 9 tests (T004 + T009) pass; atomic commit T009-T012 | 0.05d (10 min) | Sequential (US2 gate) |

**Checkpoint**: US2 shippable — mid-render failures abort with per-finding error list.

### Phase 5 — User Story 3 (Documented Dependency Posture)

| Task | Agent | Description | Estimate | Parallel? |
|---|---|---|---|---|
| T013 | `senior-backend-engineer` | Author `## Prerequisites` section in `README.md` (macOS/Linux/WSL install commands) | 0.15d (45 min) | [P] all US3 tasks |
| T014 | `senior-backend-engineer` | Add mmdc presence check to `scripts/install.sh` (courtesy warning; explicit negative: do NOT add Typst check) | 0.05d (20 min) | [P] all US3 tasks |
| T015 | `senior-backend-engineer` | Update `docs/architecture/00_Tech_Stack/README.md` line 279: describe mmdc as hard prerequisite; cross-link to ADR-022 | 0.1d (30 min) | [P] all US3 tasks (**depends on T003 ADR existing**) |
| T016 | `senior-backend-engineer` | Modify `specs/112-attack-path-pages/spec.md`: invert SC-004, delete line 135, add audit-trail comment | 0.1d (30 min) | [P] all US3 tasks |
| T017 | `senior-backend-engineer` | Modify `specs/112-attack-path-pages/research.md` line 80: correct pymmdc factual error; add Durable Decision Rationale block at lines 91-93 | 0.15d (45 min) | [P] all US3 tasks |

**Checkpoint**: US3 complete — all documentation consistently describes mmdc as a hard prerequisite; spec 112 factual errors corrected. **US3 is fully parallelizable with US1/US2 if a second contributor is available** (per tasks.md Implementation Strategy).

### Phase 6 — Cross-Cutting & CI

| Task | Agent | Description | Estimate | Parallel? |
|---|---|---|---|---|
| T018 | `devops` | Author `.github/workflows/tachi-mmdc-preflight.yml` new CI workflow: Ubuntu-latest, Typst installed, mmdc NOT installed, diagnostic echo + **enforcement assertion** (see Section 6 T4), run pipeline, assert non-zero exit + canonical tokens grep (R3) | 0.5d PRD / **1.0d realistic** (see Section 6 T2) | Sequential within Phase 6 (strongly recommended: pre-scaffold before Build stage — Section 6 T2) |
| T019 | `code-reviewer` | **Explicit negative task**: verify `BASELINE_EXAMPLES` in `tests/scripts/test_backward_compatibility.py` does NOT include `examples/agentic-app/sample-report/`; confirm no regeneration (R8) | 0.01d (2 min) | [P] with T018 |
| T020 | `devops` | Regenerate `.baseline` PDF for `examples/mermaid-agentic-app/` under `SOURCE_DATE_EPOCH=1700000000`; commit updated `.baseline` | 0.2d (1h) | Sequential (blocks T022) |
| T021 | `devops` | Regenerate `examples/agentic-app/sample-report/security-report.pdf` (non-baseline, 47 attack trees); commit regenerated PDF | 0.05d (15 min) | [P] with T020 (different working dir) |
| T022 | `tester` | Run `SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py`; compare against T002 snapshot; confirm byte-identity (R9 High priority) | 0.05d (20 min) | Sequential (after T020) |
| T023 | `senior-backend-engineer` | Canonical error message grep-consistency check across **7 locations** (extract-report-data.py, tachi.security-report.md, install.sh, README.md, test_mmdc_preflight.py, tachi-mmdc-preflight.yml, ADR-022) (R4) | 0.05d (10 min) | Sequential |
| T024 | `code-reviewer` | SC-130.6 dead code grep verification: `else if mermaid-text` and silent-fallback `has_image=False` patterns; zero results required | 0.05d (10 min) | Sequential |
| T025 | `senior-backend-engineer` | Update `CLAUDE.md` "Recent Changes" via `.aod/scripts/bash/update-agent-context.sh claude`; add Feature 130 entry | 0.05d (15 min) | [P] with T026 |
| T026 | `senior-backend-engineer` | Write `specs/130-prd-130-fix/quickstart.md`: bug reproduction, fix validation, happy path, regeneration instructions | 0.1d (30 min) | [P] with T025 |
| T027 | `tester` | Manual E2E validation with mmdc present: run `/tachi.security-report examples/mermaid-agentic-app/`; verify PDF attack path pages contain rendered images; document in PR | 0.1d (20 min) | Sequential (local validation) |
| T028 | `tester` | Manual E2E validation with mmdc removed from PATH: run `/tachi.security-report examples/mermaid-agentic-app/`; verify non-zero exit + canonical error; document in PR | 0.1d (20 min) | [P] with T027 (different shell) |
| T029 | `tester` | Manual PDF inspection of `examples/agentic-app/sample-report/security-report.pdf` (47 attack trees); verify visually; document in PR — **candidate cut** (see Section 6 T7) | 0.05d (10 min) | [P] with T027/T028 |

### Phase 7 — Polish

| Task | Agent | Description | Estimate | Parallel? |
|---|---|---|---|---|
| T030 | `tester` | Run full test suite: `pytest tests/`; confirm 100% pass; no undocumented skips | 0.05d (15 min) | Sequential (blocks T031) |
| T031 | `code-reviewer` | Pre-merge constitutional checklist walk-through: no runtime Python deps added, stdlib-only constraint holds, feature branch workflow intact, conventional commits | 0.1d (20 min) | Sequential (after T030) |
| T032 | `senior-backend-engineer` | PR description assembly: summarize 7 FR-130.x deliverables, link manual validations (T027/T028/T029), link ADR-022, Before/After CHANGELOG narrative | 0.15d (30 min) | Sequential (final task) |

---

## 3. Parallel Execution Waves

Waves map directly to the 7 tasks.md phases. Solo-dev serial execution is the authoritative critical path; parallel-group notes are optimizations if a second contributor is available.

### Wave 1 — Setup (T001)
- **Entry criteria**: Feature branch `130-prd-130-fix` exists; `.aod/results/` directory ready
- **Execution**: Sequential — `orchestrator` loads context
- **Duration**: ~10 minutes
- **Exit criteria**: Full context loaded; next phase unblocked

### Wave 2 — Foundational (T002, T003)
- **Entry criteria**: Wave 1 complete
- **Execution**: T002 and T003 run in parallel — `tester` captures baseline while `architect` authors ADR-022
- **Duration**: ~0.4-0.5d (bounded by T003 ADR authoring)
- **Exit criteria**: Baseline pretest snapshot committed at `.aod/results/130-baseline-pretest.md`; ADR-022 exists in `docs/architecture/02_ADRs/`
- **Critical**: **T003 must complete before T015** (Tech Stack doc cross-links ADR-022)

### Wave 3 — US1 Preflight Gate (T004-T008)
- **Entry criteria**: Wave 2 exit gate passed
- **Execution**: T004 (tests-first) sequential → T005/T007 parallel + T006 sequential on extract-report-data.py → T008 verification
- **Duration**: ~0.5d
- **Exit criteria**: All 4 T004 preflight tests pass; atomic US1 commit landed
- **Critical**: **T006 serializes on scripts/extract-report-data.py** — no parallelism with T010/T011

### Wave 4 — US2 Mid-Render Aggregator (T009-T012)
- **Entry criteria**: Wave 3 exit gate passed (US1 `render_mermaid_to_png()` refactor is the substrate for US2)
- **Execution**: T009 (tests-first) → T010 → T011 → T012 — strictly sequential due to shared file
- **Duration**: ~0.35-0.4d
- **Exit criteria**: All 9 tests (T004 + T009) pass; atomic US2 commit landed
- **Critical**: **R6 error message format in T011 is the single highest-priority architect refinement** — the vague error message is the failure mode Feature 130 is fixing

### Wave 5 — US3 Documentation Sync (T013-T017) — PARALLEL WITH WAVES 3-4 IF STAFFING ALLOWS
- **Entry criteria**: Wave 2 exit gate passed (ADR-022 exists, prerequisite for T015)
- **Execution**: All 5 tasks parallel-safe (different files, no shared state)
  - **Solo-dev**: serial ~0.55d between Wave 4 and Wave 6
  - **Multi-dev**: interleaves against Wave 3/4 for zero wall-clock added
- **Duration**: ~0.55d serial / 0d parallel (if dedicated contributor)
- **Exit criteria**: README Prerequisites section committed; install.sh mmdc check committed; Tech Stack doc updated; spec 112 SC-004 inverted; research.md factual error corrected
- **Note**: The Parallel Team Strategy in tasks.md:258-266 names Developers A/B/C — **this is aspirational for the current solo-author codebase**. Treat multi-dev parallelism as a ceiling, not a baseline.

### Wave 6 — Cross-Cutting & CI (T018-T029)
- **Entry criteria**: Waves 3, 4, 5 all complete
- **Execution**: T018 CI workflow (long task, serial); T019 negative verification parallel with T018; T020/T021 regeneration parallel; T022 baseline verify sequential on T020; T023/T024 grep checks sequential; T025/T026 CLAUDE.md and quickstart parallel; T027/T028/T029 manual validations parallel
- **Duration**: ~1.5-2.0d (bounded by T018 CI debug time)
- **Exit criteria**: CI workflow green; both examples regenerated; baseline byte-identity confirmed; all grep consistency checks pass; manual validations documented
- **Critical**: **T018 is underestimated at 0.5d** — realistic 1.0d for first-iteration CI debugging (see Section 6 T2)

### Wave 7 — Polish (T030-T032)
- **Entry criteria**: Wave 6 exit gate passed
- **Execution**: Sequential — T030 full test suite → T031 constitutional walk-through → T032 PR description
- **Duration**: ~0.3d
- **Exit criteria**: Full pytest suite green; constitutional checklist signed off; PR ready for Triad sign-off and merge

---

## 4. Quality Gates Between Waves

### Wave 1 Exit Gate
- [ ] Context loaded: plan.md, research.md, spec.md, constitution.md
- [ ] `git branch --show-current` returns `130-prd-130-fix`
- [ ] `.aod/results/` directory exists

### Wave 2 Exit Gate (Foundational Complete)
- [ ] `SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py` **passes** before any code changes (T002); result captured to `.aod/results/130-baseline-pretest.md`
- [ ] `docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md` exists with: context, decision, consequences, cross-refs to ADR-014 and ADR-021, Future Work clause per R1
- [ ] ADR-022 is grep-discoverable for the canonical install command `npm install -g @mermaid-js/mermaid-cli` (R4)

### Wave 3 Exit Gate (US1 MVP)
- [ ] `tests/scripts/test_mmdc_preflight.py` exists with 4 preflight tests (T004)
- [ ] All 4 preflight tests **failing** before T006 implementation (test-first verification)
- [ ] All 4 preflight tests **passing** after T006 implementation (T008)
- [ ] Manual check: on a shell without `mmdc`, `/tachi.security-report examples/mermaid-agentic-app/` aborts with canonical three-line error
- [ ] Manual check: on same shell, a project WITHOUT attack trees (e.g., `examples/web-app/`) runs to completion
- [ ] Text-fallback branch in `templates/tachi/security-report/attack-path.typ` (lines 78-86) is **deleted**, not commented
- [ ] Atomic commit: `fix(130): add mmdc preflight gate with defense-in-depth`

### Wave 4 Exit Gate (US2 Loud Failure)
- [ ] `tests/scripts/test_mmdc_preflight.py` contains all 9 tests (T004 + T009)
- [ ] All 9 tests passing after T011 implementation (T012)
- [ ] R6 error message format verified: summary line `Attack path rendering failed for N findings:` + per-finding block with id/file_path/failure_class/stderr_excerpt
- [ ] R7 distinction verified: preflight and mid-render RuntimeError messages are distinguishable
- [ ] Happy path test verifies byte-identity (no regression when all renders succeed)
- [ ] Atomic commit: `fix(130): abort on mid-render failure with per-finding error list`

### Wave 5 Exit Gate (US3 Docs Sync)
- [ ] `README.md` Prerequisites section names `typst` and `@mermaid-js/mermaid-cli` with macOS/Linux/WSL install commands
- [ ] `scripts/install.sh` prints mmdc warning if not present (courtesy only)
- [ ] `docs/architecture/00_Tech_Stack/README.md` line 279 describes mmdc as hard prerequisite and cross-links ADR-022
- [ ] `specs/112-attack-path-pages/spec.md` SC-004 inverted with audit-trail comment
- [ ] `specs/112-attack-path-pages/research.md` line 80 corrected (pymmdc is GPL-3.0 Node.js wrapper, not pure Python); Durable Decision Rationale block at lines 91-93
- [ ] No Typst check added to install.sh (explicit negative — plan S2 decision)

### Wave 6 Exit Gate (Cross-Cutting & CI)
- [ ] `.github/workflows/tachi-mmdc-preflight.yml` exists and passes on a PR touching trigger paths
- [ ] CI workflow asserts non-zero exit + canonical three tokens (`@mermaid-js/mermaid-cli`, `npm install -g @mermaid-js/mermaid-cli`, `Attack path rendering`)
- [ ] CI workflow contains **enforcement** (not just diagnostic) assertion that mmdc is absent — Section 6 T4
- [ ] `BASELINE_EXAMPLES` confirmed to NOT include `examples/agentic-app/sample-report/` (T019, R8)
- [ ] `examples/mermaid-agentic-app/security-report.pdf.baseline` regenerated under `SOURCE_DATE_EPOCH=1700000000`
- [ ] `examples/agentic-app/sample-report/security-report.pdf` regenerated (non-baseline)
- [ ] `SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py` **passes** after regeneration (T022); compared against T002 snapshot with zero divergence (R9)
- [ ] Canonical install command `npm install -g @mermaid-js/mermaid-cli` appears in exactly **7 locations** (T023, R4)
- [ ] Dead code greps return zero results (T024): no `else if mermaid-text` in attack-path.typ, no silent-fallback `has_image=False` in extract-report-data.py shutil.which context
- [ ] `CLAUDE.md` Recent Changes section contains Feature 130 entry
- [ ] `specs/130-prd-130-fix/quickstart.md` authored
- [ ] Manual validations T027, T028, T029 documented in PR

### Wave 7 Exit Gate (PR Ready)
- [ ] `pytest tests/` returns green across full suite
- [ ] No skipped tests without documented justification
- [ ] Constitutional checklist walk-through completed: no runtime Python deps, stdlib-only constraint intact, feature branch workflow, conventional commits
- [ ] PR description summarizes all 7 FR-130.x deliverables with commit references, manual validation links, ADR-022 link, Before/After CHANGELOG narrative
- [ ] Triad sign-off completed on tasks.md (PM + Architect + Team-Lead already APPROVED as of 2026-04-11)

---

## 5. Critical Path

**The critical path is the US1 → US2 chain that serializes on `scripts/extract-report-data.py`**, extended by Phases 1, 2, 6, 7.

**Longest serial chain (solo developer)**:

```
T001 (setup 10 min)
  → T002 (baseline pretest 30 min) || T003 (ADR-022 3-4h)                  [bounded by T003]
  → T004 (preflight tests 45 min)
  → T006 (extract-report-data.py preflight raise 30 min)                   [SHARED FILE]
    (T005, T007 run in parallel but do not extend critical path)
  → T008 (verify US1 10 min)
  → T009 (mid-render tests 60 min)
  → T010 (extract-report-data.py _render_single refactor 45 min)           [SAME SHARED FILE]
  → T011 (render_mermaid_to_png loop with R6 format 45 min)                [SAME SHARED FILE]
  → T012 (verify US2 10 min)
  → T013-T017 US3 docs sync (~0.55d serial; 0d if parallel with US1/US2)
  → T018 (CI workflow, 0.5d PRD / 1.0d realistic)                          [CRITICAL OVERRUN RISK]
    (T019, T021 parallel-safe)
  → T020 (baseline regen 1h)
  → T022 (baseline verify 20 min)                                          [DETERMINISM RISK]
  → T023-T024 (grep checks 20 min)
  → T027/T028/T029 (manual E2E 50 min; parallelizable)
  → T030 (full pytest 15 min)
  → T031 (constitutional walk-through 20 min)
  → T032 (PR description 30 min)
```

**Critical path length (honest estimate)**:

| Segment | PRD budget | Realistic | Notes |
|---|---:|---:|---|
| Wave 1 setup | 0d | 0.05d | T001 |
| Wave 2 foundational | 0d | 0.5d | T002 || T003 (ADR-022 +0.15d over-budget) |
| Wave 3 US1 | 0.5d | 0.5d | T004-T008 |
| Wave 4 US2 | 0.25d | 0.4d | T009-T012 (includes R6 format care) |
| Wave 5 US3 (if serial) | 0.75d | 0.55d | T013-T017 (0d if multi-dev parallel) |
| Wave 6 Cross-Cutting | 1.0d | **1.5d** | T018 CI workflow +0.5d realistic; T020-T022 baseline |
| Wave 7 Polish | 0.25d | 0.3d | T030-T032 |
| **Critical path total** | **2.75d** | **5.0d** (solo-dev) | Multi-dev parallel (Wave 5 overlap): **4.45d** |

**Expected wall-clock delivery**: **5.0 days** (solo-dev honest estimate, with ADR-022 and CI workflow overruns consuming the PRD buffer).

**Best case**: 4.8 days (ADR-022 lands in 0.3d, CI workflow lands in 0.75d, baseline byte-identical first try).

**Pessimistic case**: 5.4 days (ADR-022 = 0.5d, CI = 1.5d, baseline determinism surprise invokes T022a escape plan).

**The critical path has ZERO slack.** Any rework, Triad re-review, or unknown-unknown push the delivery past the 5-day target.

---

## 6. Risk Mitigation Actions (Carried Forward from Team-Lead Tasks Review)

The team-lead review at `.aod/results/team-lead-tasks.md` identified **7 non-blocking refinements** (T1-T7). These are surfaced here for the Build stage orchestrator to action. None require Triad re-review.

### T1 — ADR-022 Budget Under-Estimation (Medium Priority)

**Finding**: T003 is budgeted at 0.25d but realistic estimate is **0.4d** (3.2h). ADR-022 is the first-of-its-kind CLI-prerequisite ADR in tachi and scope-equivalent to ADR-014 (~190 lines), not ADR-020/021 (~130 lines). First-of-kind ADRs take 3-4 hours because there is no template to copy.

**Action**: **Strongly recommend pre-drafting ADR-022 skeleton before Build stage starts**. One-hour sketch (one paragraph per section, no prose polish) front-loads the thinking outside the 5-day window. During formal T003, promote the skeleton to full draft. Recovers ~0.15d of slack.

**Owner**: `architect` (during Plan-stage downtime or Build-stage warm-up)

### T2 — CI Workflow Budget Under-Estimation (**High** Priority)

**Finding**: T018 is budgeted at 0.5d but realistic estimate is **1.0d** (range 1.0-1.5d for first-iteration debugging). The tachi `.github/workflows/` directory has exactly 1 existing workflow (`release-please.yml`); there is no internal template. T018 requires selecting and verifying `typst-community/setup-typst` action, ensuring the pipeline runs without the Claude Code orchestration layer (direct Python invocation of `extract-report-data.py`), asserting exit code, and grep-asserting stderr tokens. First-iteration debugging typically hits action-name typos, `fetch-depth` surprises, package-version drift, and PATH differences.

**Action** (pick one):
1. **Pre-scaffold T018 NOW, before Build stage starts** (recommended). Push a minimal workflow with just `which mmdc || echo ...` step, confirm it triggers and Typst installs. Front-loads the CI infrastructure risk outside the 5-day window. Returns a clean 0.5d T018 line-item later.
2. **Timebox T018 at 0.75d**. If debugging exceeds budget, land the workflow as a **follow-up PR** (scope cut on FR-130.7 but preserves P0 shipping date).
3. **Accept the slip** to 5.5d target.

**Owner**: `devops` (pre-scaffold) or Build-stage `orchestrator` (timebox enforcement)

### T3 — Baseline Determinism Escape Plan (Medium Priority)

**Finding**: T022 validates byte-identity of regenerated `mermaid-agentic-app` baseline, but there is **no escape plan** if the byte-identity check fails through no fault of Feature 130 (e.g., mmdc/Puppeteer PNG metadata drift, Chromium version change, tEXt chunk non-determinism). The Feature 128 decision to exclude `agentic-app/sample-report/` from `BASELINE_EXAMPLES` was for exactly this category of latent non-determinism.

**Action**: Add contingent **T022a** task to the Build-stage checklist:
> "If T022 byte-identity check FAILS and no Feature 130 code change plausibly caused the divergence, document the determinism regression in `.aod/results/130-determinism-escape.md`, escalate to `architect` for a same-day call between options (a) debug determinism as blocker, (b) update baseline and document divergence, or (c) de-list `mermaid-agentic-app` from `BASELINE_EXAMPLES` (requires amending R8 hard negative). Budget: 0.3d if invoked, 0d if T022 passes first attempt."

**Owner**: `architect` (escalation point) + `devops` (investigation)

### T4 — T018 Enforcement Assertion (Medium Priority)

**Finding**: T018 currently specifies a **diagnostic** step (`which mmdc || echo "expected absence: ..."`) that covers the observability half of plan Risk #6 (CI accidentally installs mmdc via a transitive dep) but NOT the **enforcement** half. If mmdc unexpectedly IS on PATH (e.g., `typst-community/setup-typst` pulls it transitively), the diagnostic prints but the workflow continues, potentially running the pipeline successfully and masking the regression.

**Action**: Amend T018 to add an explicit negative assertion immediately after the diagnostic echo:

```yaml
- name: Enforce mmdc absence (plan Risk #6)
  run: |
    if command -v mmdc >/dev/null 2>&1; then
      echo "FATAL: mmdc unexpectedly present on PATH. S3 spike assumption broken."
      exit 1
    fi
```

Cost: +5 lines in the workflow file, zero schedule impact.

**Owner**: `devops` (as part of T018 authoring)

### T5 — T009 Test Count Optimization (Low Priority, OPTIONAL)

**Finding**: T009 specifies 5 mid-render tests. Two of them (`test_midrender_all_success_no_exception` and `test_midrender_all_failure_raises_with_full_list`) are arguably covered by other tests (happy-path baseline and per-finding aggregator unit test respectively). Dropping these two recovers ~30 minutes.

**Action**: **Optional** — only apply if Wave 6 schedule pressure forces a cut. The full 5-test coverage is the preferred shape.

**Owner**: `tester` (judgment call at T009 authoring time)

### T6 — Parallel Team Strategy Clarification (Low Priority)

**Finding**: The `tasks.md:258-266` "Parallel Team Strategy" section names Developers A/B/C. This is aspirational for the current solo-author codebase (recent commits on `main` are all single-author). The 5-day target rests on a solo-developer serial critical path, not wave-based parallelism.

**Action**: Add a clarifying comment to the orchestrator's Wave 5 handoff: "US3 parallelism is a multi-dev optimization; solo-dev execution extends Wave 5 serially by ~0.55d. Critical path is the 5-day anchor regardless."

**Owner**: Build-stage `orchestrator` (setting developer expectations)

### T7 — T029 47-Tree Manual Inspection Cut (Low Priority, OPTIONAL)

**Finding**: T029 requires manual visual inspection of `examples/agentic-app/sample-report/security-report.pdf` (47 attack trees). This overlaps with T027's 24-tree validation on `mermaid-agentic-app`. Cutting T029 recovers ~0.1d.

**Action**: **Optional** — only apply if Wave 6 schedule pressure forces a cut. T027 + T028 provide sufficient happy-path and loud-failure validation; T029 is a belt-and-suspenders check that may not be worth its schedule cost.

**Owner**: `tester` (judgment call when approaching PR submission)

---

## 7. Sign-off Authority

| Artifact | Approver | Status |
|---|---|---|
| Feasibility | `team-lead` | APPROVED (this document and `.aod/results/team-lead-tasks.md`) |
| Agent Assignments | `team-lead` | APPROVED (this document) |
| tasks.md (prior review) | PM + Architect + Team-Lead | Triple sign-off APPROVED/APPROVED/APPROVED_WITH_CONCERNS |
| Final phase sign-off | `team-lead` | Deferred to Wave 7 exit validation |
| Phase gate sign-offs (Waves 2-7 exits) | `team-lead` | Sequential — each gate validated before next wave launches |

---

## 8. Recommended Build-Stage Sequence

For the Build-stage orchestrator, the prescriptive execution order is:

1. **Pre-Build warm-up (outside 5-day window)**:
   - `architect` pre-drafts ADR-022 skeleton (T1 refinement)
   - `devops` pre-scaffolds CI workflow minimal version (T2 refinement option 1)
2. **Wave 1**: `orchestrator` runs T001 (10 min)
3. **Wave 2**: `tester` runs T002 + `architect` runs T003 in parallel (~0.4-0.5d)
4. **Wave 3**: `tester` runs T004 → `senior-backend-engineer` runs T005+T007 in parallel with T006 → `tester` runs T008 (~0.5d)
5. **Wave 4**: `tester` runs T009 → `senior-backend-engineer` runs T010 → T011 → `tester` runs T012 (~0.4d)
6. **Wave 5**: `senior-backend-engineer` runs T013-T017 in parallel OR serially (~0-0.55d depending on staffing)
7. **Wave 6**: `devops` runs T018 (with T4 enforcement assertion) in parallel with `code-reviewer` T019, then T020-T021 parallel, then T022 sequential, then T023-T026 as described, then T027-T029 parallel manual validations (~1.5-2.0d)
8. **Wave 7**: `tester` T030 → `code-reviewer` T031 → `senior-backend-engineer` T032 (~0.3d)

**If T22a is invoked (determinism escape)**: `architect` escalation call, then `devops` implementation of chosen option. Adds up to 0.3d.

---

**Agent Registry**: All agents referenced above (`senior-backend-engineer`, `tester`, `architect`, `devops`, `code-reviewer`, `orchestrator`) are valid entries in `.claude/agents/_README.md`. No invented labels used.

**End of Agent Assignments**
