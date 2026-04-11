# Session Continuation: Feature 130 — Fix Attack Path Mermaid Rendering When mmdc Is Not Installed

**Generated**: 2026-04-11
**Branch**: `130-prd-130-fix`
**Last Commit**: b46e931 docs(130): declare mmdc as hard prerequisite across README, install.sh, Tech Stack, spec 112

## Completed This Session

Waves 1-5 of `/aod.build 130` complete. **17/32 tasks (53%)**. P1 checkpoint **APPROVED**.

**Session commits** (newest first):

- `b46e931` docs(130): declare mmdc as hard prerequisite across README, install.sh, Tech Stack, spec 112 — **Wave 5 US3**
- `732fd49` fix(130): abort on mid-render failure with per-finding error list — **Wave 4 US2**
- `db0073c` fix(130): add mmdc preflight gate with defense-in-depth — **Wave 3 US1** (T004-T008, committed this session after prior session left it uncommitted)
- `528204f` docs(130): scaffold feature workspace with PRD, spec, plan, ADR-022 — **Waves 1-2**

**Per-wave summary**:

- **Wave 1 (Setup) — T001**: Context loaded.
- **Wave 2 (Foundational) — T002, T003**: Baseline pretest captured; ADR-022 authored.
- **Wave 3 (US1 Preflight Gate) — T004-T008**: Shell + Python preflight gates, text-fallback branch deleted, 4 preflight tests pass. Committed this session as `db0073c`.
- **Wave 4 (US2 Mid-Render Aggregator) — T009-T012**: `_render_single` promoted to module level, R6 error message format emitted, 9/9 preflight tests pass. R6 (highest-priority architect refinement) delivered exactly per spec.
- **Wave 5 (US3 Docs Sync) — T013-T017**: README Prerequisites section, install.sh mmdc warning, Tech Stack update with ADR-022 cross-link, spec 112 SC-004 inversion with audit comment, research.md pymmdc factual correction and Durable Decision Rationale block.

**Verification state (all green)**:

- `test_mmdc_preflight.py`: **9/9** passed (4 preflight + 5 mid-render aggregator)
- `test_backward_compatibility.py`: **5/5** baselines byte-identical under `SOURCE_DATE_EPOCH=1700000000`
- Full pytest suite: **48/48** passed (per P1 checkpoint run)
- Canonical install command grep: **6/7** locations placed (7th coming in Wave 6 T018)

## P1 Checkpoint Review (APPROVED)

Architect review at `.aod/results/architect-130-p1-checkpoint.md`:

- **STATUS**: APPROVED
- All in-scope FRs satisfied (FR-130.1 through FR-130.6; FR-130.7 is Wave 6)
- All in-scope architect refinements satisfied (R1, R2, R5, R6, R7, R9)
- Happy-path byte identity preserved

**Non-blocking concerns** (document for Wave 6/7 address):

1. **Stale docstring** at `templates/tachi/security-report/attack-path.typ:39` — still lists `mermaid-text` as a parameter key even though the field and fallback branch were removed in T007. Optional cleanup for Wave 7 polish.
2. **Module-level globals** `_render_attack_trees_dir` / `_render_rel_target` in `scripts/extract-report-data.py:721-722` — trade-off documented inline (lines 712-720) to preserve 2-arg `_render_single` test-mock signature. Accepted as-is; optional hardening would be an `assert _render_attack_trees_dir is None` guard before publishing to catch hypothetical future re-entrant callers.
3. **Canonical install command locations**: 6/7 placed; the 7th (`.github/workflows/tachi-mmdc-preflight.yml`) arrives with T018. T023 grep check will formally verify all 7.

## Current State

- **Phase**: implement (Wave 6 of 7)
- **Uncommitted**:
  - `docs/product/_backlog/BACKLOG.md` — timestamp bump only (GitHub stage label update failed on Step 1 of /aod.build; content unchanged). Can be discarded or committed separately.
  - `specs/086-automated-release-tagging/run-state.json` — pre-session, unrelated to Feature 130, leave untouched.
- **Tasks**: 17/32 complete — T001-T017 marked `[X]`; T018-T032 pending

## Next Actions

1. **Resume `/aod.build 130`** for Wave 6 (Cross-Cutting & CI). The skill detects `[X]` marks in tasks.md and resumes at Wave 6.
2. **Wave 6 highlights (T018-T029)** — this is the biggest wave and the most risk-laden:
   - **T018** (devops): Author `.github/workflows/tachi-mmdc-preflight.yml` — **0.5d PRD / 1.0d realistic** for first-iteration GitHub Actions debugging. Must assert non-zero exit + canonical three tokens (`@mermaid-js/mermaid-cli`, `npm install -g @mermaid-js/mermaid-cli`, `Attack path rendering`). Architect R3 requires a diagnostic echo (`which mmdc || echo "expected absence..."`). Team-Lead T4 refinement requires an **enforcement assertion** (not just diagnostic) that mmdc is absent.
   - **T019** (code-reviewer): explicit negative — verify `BASELINE_EXAMPLES` in `test_backward_compatibility.py` does NOT include `examples/agentic-app/sample-report/`. R8 refinement prevents scope creep.
   - **T020** (devops): Regenerate `examples/mermaid-agentic-app/security-report.pdf.baseline` under `SOURCE_DATE_EPOCH=1700000000`.
   - **T021** (devops): Regenerate `examples/agentic-app/sample-report/security-report.pdf` (non-baseline, 47 attack trees).
   - **T022** (tester): Run full backward-compat suite; compare against T002 snapshot for byte-identity (R9 post-flight snapshot). **High-priority**.
   - **T023** (senior-backend-engineer): Canonical install command grep check across **7 locations** — formally verifies all 7 after T018 adds the CI workflow. Currently 6/7.
   - **T024** (code-reviewer): SC-130.6 dead code grep — `else if mermaid-text` and silent-fallback `has_image=False` patterns must return zero.
   - **T025** (senior-backend-engineer): Update `CLAUDE.md` Recent Changes via `.aod/scripts/bash/update-agent-context.sh claude`.
   - **T026** (senior-backend-engineer): Write `specs/130-prd-130-fix/quickstart.md` per plan outline.
   - **T027/T028/T029** (tester): Manual E2E validations — **require user interaction** (visual PDF inspection, shell PATH manipulation). Best done with you present.
3. **Wave 7 (Polish) — T030-T032**:
   - T030: Full pytest suite.
   - T031: Constitutional walk-through.
   - T032: PR description assembly.

**Strongly recommend**: Resume Wave 6 in a fresh session with your oversight. Wave 6 CI workflow debugging benefits from iteration cycles (commit → push → watch GitHub Actions → fix → repeat), and the manual E2E validations (T027-T029) require your visual inspection.

## Context Files

Essential for next session:

- `specs/130-prd-130-fix/tasks.md` — 32-task breakdown with `[X]`/`[ ]` marks; Wave 6 tasks at T018-T029, Wave 7 at T030-T032
- `specs/130-prd-130-fix/agent-assignments.md` — Phase 6 agent matrix (devops for T018/T020/T021, tester for T022/T027-T029, senior-backend-engineer for T023/T025/T026, code-reviewer for T019/T024)
- `specs/130-prd-130-fix/plan.md` — search for "R3" (CI diagnostic), "R4" (7-location grep), "R6" (error format already satisfied), "R8" (negative), "R9" (baseline guardrails)
- `.aod/results/130-baseline-pretest.md` — pre-flight baseline snapshot for T022 post-flight comparison
- `.aod/results/architect-130-p1-checkpoint.md` — P1 checkpoint review with the 3 non-blocking concerns above
- `.aod/results/senior-backend-engineer-130-t010-t011.md` — Wave 4 T010/T011 implementation details
- `.aod/results/senior-backend-engineer-130-wave5.md` — Wave 5 docs sync details
- `docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md` — the governance anchor Wave 6 T023 grep must count

## Resume Command

```bash
claude "Resume Feature 130 mmdc preflight fix (branch: 130-prd-130-fix). Waves 1-5 complete (T001-T017, 17/32 tasks, 53%). P1 checkpoint APPROVED. All 14 preflight+baseline tests green; full suite 48/48 green. Run /aod.build 130 to continue with Wave 6 (Cross-Cutting & CI, T018-T029). T018 CI workflow is the biggest risk item (0.5d PRD / 1.0d realistic). Manual E2E validations T027-T029 require user interaction."
```
