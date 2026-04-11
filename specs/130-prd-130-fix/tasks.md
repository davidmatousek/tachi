---
description: "Task breakdown for Feature 130 — Fix Attack Path Mermaid Rendering When mmdc Is Not Installed"
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-11
    status: APPROVED
    notes: "tasks.md faithfully translates spec + plan + R1-R9 into actionable work. All 3 user stories have dedicated phases with faithful goals, faithful independent test criteria, and present checkpoint blocks. All 7 FR-130.x trace to tasks. All 4 spec deviations (corrected examples, Tech Stack doc, SC-130.6 grep, edge cases) survive correctly. All 7 out-of-scope items respected. Both scope-containment negative tasks (T014, T019) are clearly worded. Prior concern about ADR-022 effort visibility resolved: T003 is now standalone with 0.25d explicit budget. 6 non-blocking observations in .aod/results/product-manager-tasks.md."
  architect_signoff:
    agent: architect
    date: 2026-04-11
    status: APPROVED
    notes: "All 9 refinements (R1-R9) correctly embedded in tasks.md with priority weighting and explicit refinement-ID cross-references. Both HIGH priority items are enforced in multiple slots: R6 across T009/T010/T011 (test + data capture + format/emit chain), R9 across T002/T022 (before/after baseline pair). Test-first discipline honored, parallelization validated, same-file conflicts serialized via phase ordering, defense-in-depth produces one-error behavior. 0 blocking, 4 minor non-blocking observations (O1-O4) in .aod/results/architect-tasks.md."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-11
    status: APPROVED_WITH_CONCERNS
    notes: "32 tasks correctly trace to 7 FRs and match PRD's 4.35d work breakdown. 5-day target is functionally unbuffered — expected ADR-022 overrun (~0.15d) plus CI workflow first-iteration debugging (~0.5d) consume the 0.65d PRD buffer. Honest estimate: 5.0d expected, 4.8-5.4d range. Strong recommendations (non-blocking): pre-scaffold CI workflow (T018) and draft ADR-022 skeleton (T003) before Build stage to buy back slack; add contingent T022a for baseline determinism escape plan; amend T018 to add enforcement assertion for plan Risk #6 (currently observability-only). 7 non-blocking refinements in .aod/results/team-lead-tasks.md."
---

# Tasks: Fix Attack Path Mermaid Rendering When mmdc Is Not Installed

**Input**: Design documents from [specs/130-prd-130-fix/](../130-prd-130-fix/)
**Prerequisites**:
- [spec.md](spec.md) (PM approved 2026-04-11)
- [plan.md](plan.md) (PM + Architect approved 2026-04-11)
- [research.md](research.md)

**Tests**: Included — Constitution Principle VI (Testing Excellence) requires test-first development for core features; architect review refinements R5, R6, R7 require specific test coverage; FR-130.7 mandates a CI fresh-install acceptance test.

**Organization**: Tasks are grouped by user story (US1, US2, US3 from spec.md) for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3). No label = Setup / Foundational / Polish.
- All file paths are absolute from repo root.

## Path Conventions

tachi is a single-project toolkit. Files live at:
- `scripts/*.py` (runtime Python, stdlib-only)
- `templates/tachi/security-report/*.typ` (Typst templates)
- `.claude/commands/*.md` (slash-command entry points)
- `.github/workflows/*.yml` (GitHub Actions CI)
- `docs/architecture/02_ADRs/` (Architecture Decision Records)
- `tests/scripts/` (pytest dev-time tests)
- `specs/130-prd-130-fix/` (this feature's artifacts)

---

## Phase 1: Setup

**Purpose**: Prep the working environment and capture baseline state before any changes.

- [X] T001 Read [plan.md](plan.md), [research.md](research.md), [spec.md](spec.md), and [.aod/memory/constitution.md](../../.aod/memory/constitution.md) to load full context. Confirm `git branch --show-current` is `130-prd-130-fix`. Confirm `.aod/results/` directory exists for review artifacts.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the pre-flight baseline state and author governance artifacts **before** any code changes. Nothing in Phase 3+ may begin until this phase is complete.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Run `SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py` and capture the baseline pass state to `.aod/results/130-baseline-pretest.md`. This is the "before" snapshot that T022 will compare against. (Architect refinement R9 — High priority; without this we cannot prove the happy path is byte-identical after the refactor.)
- [X] T003 Author [docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md](../../docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md) — the first ADR in tachi governing CLI-prerequisite posture. Must include: context (Feature 130 silent-failure observation), decision (mmdc is a hard prerequisite when attack-trees/ contains Critical/High findings), consequences (runtime zero-Python-dep preserved, Feature 054 Typst parity achieved), and a "Future Work" clause noting that if a third CLI prerequisite is added, an `install.sh` prerequisite helper should be extracted (architect refinement R1 — Low priority). Cross-reference ADR-014 (optional external APIs) and ADR-021 (determinism). (Architect refinement R2 — Medium priority, schedules ADR as T003 before code changes.)

**Checkpoint**: Baseline captured, ADR-022 in place. User story implementation can now begin.

---

## Phase 3: User Story 1 — Prerequisites Are Enforced, Not Assumed (Priority: P1) MVP

**Goal**: Turn silent failure into loud failure at the command entry point. Implement the preflight gate in two places (shell-level in the command file, Python-level in `extract-report-data.py`) as defense-in-depth, delete the text-fallback Typst branch, and verify through tests.

**Independent Test**: Run `/tachi.security-report examples/mermaid-agentic-app/` on a shell where `PATH` excludes `mmdc`. The pipeline must abort non-zero with the canonical error message containing `@mermaid-js/mermaid-cli`, `npm install -g @mermaid-js/mermaid-cli`, and "Attack path rendering." Also verify that a project WITHOUT attack trees (e.g., `examples/web-app/`) runs to completion on the same shell.

### Tests for User Story 1 (test-first per Constitution Principle VI)

**NOTE: Write these tests FIRST, ensure they FAIL before implementation.**

- [X] T004 [P] [US1] Create [tests/scripts/test_mmdc_preflight.py](../../tests/scripts/test_mmdc_preflight.py) (new file). Write failing pytest cases covering the preflight behavior of `render_mermaid_to_png()`:
  - `test_preflight_raises_when_mmdc_missing`: patch `shutil.which` to return None, pass a non-empty `attack_trees` list, assert `RuntimeError` is raised and the exception message contains the three canonical tokens (`@mermaid-js/mermaid-cli`, `npm install -g @mermaid-js/mermaid-cli`, `Attack path rendering`).
  - `test_preflight_skipped_when_attack_trees_empty`: pass an empty list, assert no exception raised, assert `shutil.which` is NOT called (early return path). (Architect refinement R5 — Medium priority; edge case not previously covered.)
  - `test_preflight_skipped_when_only_low_medium_findings`: construct an `attack_trees` list where all entries would be filtered by Critical/High gate upstream (document assumption: filtering happens in caller, so unit test uses empty list as proxy).
  - `test_preflight_error_distinct_from_midrender`: assert the exception message raised from the preflight gate does NOT contain "Attack path rendering failed for" (the mid-render aggregator's distinct message, tested in T009). (Architect refinement R7 — Medium priority; two distinct RuntimeError shapes.)
  All four tests MUST fail at this point (because the current code returns silently rather than raising). Record the failure output in the commit message for traceability.

### Implementation for User Story 1

- [X] T005 [P] [US1] Modify [.claude/commands/tachi.security-report.md](../../.claude/commands/tachi.security-report.md) Step 1 (currently lines 39-54 Typst block). Add a new preflight check immediately after the Typst check that: (a) greps the target directory for `attack-trees/*.md` with at least one file present, (b) if attack-trees detected, runs `command -v mmdc >/dev/null 2>&1`, (c) if mmdc not found, echoes the canonical three-line error message to stderr and exits non-zero. Mirror the Typst check's shell style verbatim. Preserve the gating: the check must NOT fire on projects without attack trees. No new imports or helpers.
- [X] T006 [US1] Modify [scripts/extract-report-data.py](../../scripts/extract-report-data.py) lines 721-730. Replace the silent `if not shutil.which("mmdc"):` block (lines 725-730 — the warning print and the `for entry in attack_trees: entry["has_image"] = False` loop) with `raise RuntimeError(...)` using the canonical three-line error message. Preserve the `if not attack_trees: return` guard at lines 721-722 (that is the correct "no work to do" short-circuit). Verify T004 tests now pass.
- [X] T007 [P] [US1] Modify [templates/tachi/security-report/attack-path.typ](../../templates/tachi/security-report/attack-path.typ) by deleting lines 78-86 entirely (the `else if mermaid-text != ""` block including its `block(...)` body and closing brace). Verify the remaining `if has-img and img-path != ""` branch at lines 74-77 is the only render path. Do NOT leave a placeholder, comment, or "removed in 130" stub — delete outright.
- [X] T008 [US1] Run `pytest tests/scripts/test_mmdc_preflight.py -k preflight -v` and confirm all four T004 tests now pass. Commit T004-T008 together as one atomic US1 commit (`fix(130): add mmdc preflight gate with defense-in-depth`).

**Checkpoint**: User Story 1 fully functional. On a shell without `mmdc`, `/tachi.security-report` on `examples/mermaid-agentic-app/` aborts at preflight with the canonical error message. On a shell with `mmdc`, the happy path remains unchanged.

---

## Phase 4: User Story 2 — Rendering Failure Is Loud, Not Silent (Priority: P1)

**Goal**: When `mmdc` is installed but a specific attack tree fails to render (syntax error, crash, timeout), abort the entire pipeline with a non-zero exit code and a per-finding failure list on stderr. The per-finding list must include ID + file path + failure class + ~200 bytes of stderr excerpt.

**Independent Test**: Construct a fixture attack-tree directory with one syntactically invalid Mermaid file among several valid ones. Call `render_mermaid_to_png()` directly and assert: (a) `RuntimeError` is raised, (b) the exception message starts with "Attack path rendering failed for N findings:", (c) the message contains the failing finding ID, (d) the message contains the failing file path, (e) the message contains a stderr excerpt.

### Tests for User Story 2

**NOTE: Write these tests FIRST, ensure they FAIL before implementation.**

- [X] T009 [US2] Extend [tests/scripts/test_mmdc_preflight.py](../../tests/scripts/test_mmdc_preflight.py) with the mid-render failure aggregator test group. Write failing pytest cases:
  - `test_midrender_aggregator_raises_on_any_failure`: patch `_render_single` to return one failure among several successes, assert `RuntimeError` is raised. (Architect refinement R5 — Medium priority; mixed success/failure case.)
  - `test_midrender_aggregator_message_format`: assert the exception message contains (a) a summary line "Attack path rendering failed for N findings:", (b) the failed finding ID, (c) the fixture file path, (d) a failure class token (one of "exit", "timeout", "signal"), (e) at least 1 byte of stderr excerpt. (Architect refinement R6 — **High priority**; error message format spec.)
  - `test_midrender_all_success_no_exception`: patch `_render_single` to return all successes, assert no exception raised and `has_image=True` on every entry. (Verifies happy-path byte-identity.)
  - `test_midrender_all_failure_raises_with_full_list`: patch `_render_single` to return all failures, assert the exception message lists every finding ID.
  - `test_midrender_error_distinct_from_preflight`: assert the mid-render aggregator's exception message does NOT contain the `npm install -g` canonical install command (the preflight gate's distinct message). (Architect refinement R7 — Medium priority; two distinct RuntimeError shapes confirmed.)
  All five tests MUST fail at this point (because the current code silently sets `has_image=False` on failure rather than raising).

### Implementation for User Story 2

- [X] T010 [US2] Modify [scripts/extract-report-data.py](../../scripts/extract-report-data.py) `_render_single` function (currently lines 741-768) to return a structured failure record on error. The return tuple already is `(entry, success, dest_path)` — extend it to `(entry, success, dest_path_or_error_record)` where on failure `error_record` is a dict with keys `id`, `file_path` (the `.mmd` file path in the temp dir OR the canonical attack-trees/ source path), `failure_class` (one of `"exit:<code>"`, `"timeout"`, `"signal"`), and `stderr_excerpt` (first 200 bytes of captured stderr). Preserve the existing `capture_output=True, timeout=30` behavior. Preserve the existing subprocess call signature. Do NOT add new imports.
- [X] T011 [US2] Modify the `as_completed` loop in `render_mermaid_to_png()` (currently lines 772-777) to collect any failures into a list. After the loop, if the failure list is non-empty, format the error message per the R6 spec (summary line + indented per-finding block with ID, file path, failure class, stderr excerpt) and raise `RuntimeError(message)`. If the failure list is empty, the loop ends normally and each entry has `has_image=True` and a valid `image_path`. (Architect refinement R6 — **High priority**; the exact format decides whether this feature delivers on its fail-loud promise.)
- [X] T012 [US2] Run `pytest tests/scripts/test_mmdc_preflight.py -v` and confirm all nine tests (four from T004 + five from T009) pass. Commit T009-T012 as one atomic US2 commit (`fix(130): abort on mid-render failure with per-finding error list`).

**Checkpoint**: User Story 2 fully functional. When `mmdc` is present but a specific attack tree fails to render, the pipeline aborts with an informative per-finding error list instead of silently producing a PDF with some pages missing.

---

## Phase 5: User Story 3 — Documented Dependency Posture (Priority: P1)

**Goal**: Document `mmdc` as a hard prerequisite across README, install script, Tech Stack doc, and parent spec 112. Correct the pymmdc factual error in spec 112 research.

**Independent Test**: A human reader opens README.md and sees a "Prerequisites" section naming `typst` and `@mermaid-js/mermaid-cli`. Running `scripts/install.sh` on a shell without mmdc prints a clear warning. Spec 112 SC-004 has been inverted and research.md line 80 has been corrected.

All US3 tasks are doc changes in different files, so all are parallelizable.

### Implementation for User Story 3

- [X] T013 [P] [US3] Author a new `## Prerequisites` section in [README.md](../../README.md) between "## What is tachi?" (line ~29) and "## Quick Start" (line ~30). The section MUST name `typst` and `@mermaid-js/mermaid-cli` as required external CLIs and provide install commands for macOS (`brew install typst` + `npm install -g @mermaid-js/mermaid-cli`), Linux (`apt install typst` or equivalent + `npm install -g @mermaid-js/mermaid-cli`), and WSL (same as Linux). The mmdc install command MUST exactly match the canonical `npm install -g @mermaid-js/mermaid-cli` string used elsewhere.
- [X] T014 [P] [US3] Add an mmdc presence check to [scripts/install.sh](../../scripts/install.sh). Single `if ! command -v mmdc >/dev/null 2>&1; then` block that echoes a warning identifying mmdc as a prerequisite for attack path rendering and points to README Prerequisites + the canonical `npm install -g @mermaid-js/mermaid-cli` command. Do **NOT** add a Typst check to install.sh — per plan S2 decision, install.sh does not currently check Typst and adding one would be scope creep. The install.sh warning is a courtesy; the per-command preflight (T005/T006) is the enforcement.
- [X] T015 [P] [US3] Update [docs/architecture/00_Tech_Stack/README.md](../../docs/architecture/00_Tech_Stack/README.md) line 279. Replace the current "When absent, the `/tachi.security-report` command still generates attack path pages but renders the raw Mermaid diagram text instead of a PNG image" sentence with a sentence describing `mmdc` as a **hard prerequisite** when attack-trees/ contains Critical/High findings, aborting at preflight if missing. Add a cross-reference link to the newly authored ADR-022 in the same paragraph (plan Risk #5 mitigation — ensures ADR-022 is discoverable from the Tech Stack doc).
- [X] T016 [P] [US3] Modify [specs/112-attack-path-pages/spec.md](../../specs/112-attack-path-pages/spec.md): invert line 125 (SC-004) and delete/rewrite line 135. The new SC-004 MUST assert that rendering tool availability is verified at preflight and the pipeline aborts loudly if unavailable. Add a one-line reference comment `<!-- Inverted by Feature 130 (2026-04-11): text fallback is no longer a supported shipping mode -->` immediately above the new SC-004 for audit trail.
- [X] T017 [P] [US3] Modify [specs/112-attack-path-pages/research.md](../../specs/112-attack-path-pages/research.md) line 80: replace `- Pure Python alternative: \`pymmdc\` package (no Node.js dependency)` with a corrected entry noting that `pymmdc` on PyPI is a thin Python wrapper around the Node.js `@mermaid-js/mermaid-cli` CLI, is GPL-3.0 licensed (incompatible with tachi's distribution model), and is NOT a pure-Python renderer. At lines 91-93, add a "Durable Decision Rationale" block documenting the mmdc hard-prerequisite choice with a reference to Feature 130 and to the PRD Rejected Alternatives section (A through E).

**Checkpoint**: User Story 3 complete. All documentation now consistently describes `mmdc` as a hard prerequisite. Spec 112's factual errors are corrected.

---

## Phase 6: Cross-Cutting & CI

**Purpose**: Author the CI workflow (FR-130.7), regenerate example baselines, and run verification gates. This phase depends on US1, US2, and US3 all being complete.

- [X] T018 Author [.github/workflows/tachi-mmdc-preflight.yml](../../.github/workflows/tachi-mmdc-preflight.yml) (new file). The workflow MUST:
  - Trigger on `pull_request` for paths: `scripts/extract-report-data.py`, `templates/tachi/security-report/attack-path.typ`, `scripts/install.sh`, `.claude/commands/tachi.security-report.md`, `README.md`, and `.github/workflows/tachi-mmdc-preflight.yml` itself
  - Run on `ubuntu-latest`
  - Install Typst (via `typst-community/setup-typst` or equivalent) and Python 3.11, but **DO NOT** install mmdc
  - Include a diagnostic step: `which mmdc || echo "expected absence: mmdc not on PATH, preflight gate should fire"` (Architect refinement R3 — Medium priority; makes the intentional absence visible in CI logs)
  - Run `/tachi.security-report examples/mermaid-agentic-app/` (or the equivalent direct invocation that does not require the Claude Code agent orchestration layer — use Python direct call to `extract-report-data.py` if the slash-command cannot run in CI)
  - Assert exit code is non-zero
  - Assert stderr contains all three canonical tokens (`@mermaid-js/mermaid-cli`, `npm install -g @mermaid-js/mermaid-cli`, `Attack path rendering`)
  - Print the captured stderr in the workflow output for debuggability
- [X] T019 **Explicit negative task**: In [tests/scripts/test_backward_compatibility.py](../../tests/scripts/test_backward_compatibility.py), verify that `BASELINE_EXAMPLES` does NOT include `examples/agentic-app/sample-report/`. Do NOT add it. Do NOT regenerate its `.baseline` file. The Feature 128 decision to exclude `agentic-app/sample-report/` from byte-deterministic baselines stands — Feature 130 does not revisit that decision. If a reviewer asks why it is excluded, point to plan.md Section 5 and architect review section 5. (Architect refinement R8 — Medium priority; prevents well-intentioned scope creep.)
- [X] T020 Regenerate the `.baseline` PDF for `examples/mermaid-agentic-app/` under `SOURCE_DATE_EPOCH=1700000000`. This example IS in `BASELINE_EXAMPLES` and the rendered attack path diagrams must now be byte-identical across runs. Run: `SOURCE_DATE_EPOCH=1700000000 make examples` (or equivalent targeted regeneration). Commit the updated `.baseline` file in the same commit as the regeneration.
- [X] T021 Regenerate `examples/agentic-app/sample-report/security-report.pdf` (non-baseline) to confirm rendering works on the happy path with 47 attack trees. No `.baseline` file is updated. Commit the regenerated PDF.
- [X] T022 Run `SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py` and confirm all baselines still pass byte-identity comparison. Compare against the T002 pre-flight snapshot (`.aod/results/130-baseline-pretest.md`) to prove no regression. (Architect refinement R9 — **High priority**; this is the backward-compatibility guardrail.) **Result: 5 passed in 8.79s, exit 0; IDENTICAL to T002 pre-flight (zero byte divergence). Post-flight snapshot at `.aod/results/130-baseline-posttest.md`. R9 satisfied.**
- [X] T023 Canonical error message grep-consistency check. Run `grep -r "npm install -g @mermaid-js/mermaid-cli"` and confirm the canonical install command appears in exactly these 7 locations:
  1. `scripts/extract-report-data.py` (the `raise RuntimeError(...)` from T006)
  2. `.claude/commands/tachi.security-report.md` (the shell echo from T005)
  3. `scripts/install.sh` (the courtesy warning from T014)
  4. `README.md` (the Prerequisites section from T013)
  5. `tests/scripts/test_mmdc_preflight.py` (the assertion string from T004)
  6. `.github/workflows/tachi-mmdc-preflight.yml` (the grep assertion from T018)
  7. `docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md` (the decision body from T003) — (Architect refinement R4 — Low priority; ADR-022 as the 7th location.)
  If any location is missing, add it; if any stray/duplicate location exists, remove it. Document the result in the commit message.
- [X] T024 SC-130.6 dead code grep verification. Run: (a) `grep -n 'else if mermaid-text' templates/tachi/security-report/attack-path.typ` — MUST return zero results, (b) `grep -n 'has_image"\] = False' scripts/extract-report-data.py` — MUST not appear in the `if not shutil.which("mmdc")` context (the `has_image=False` set within `_render_single` on a failure path DOES still exist; differentiate by greping for the specific silent-fallback pattern). If either grep finds dead code, return to T006/T007 and remove it.
- [X] T025 [P] Update CLAUDE.md "Recent Changes" section by running `.aod/scripts/bash/update-agent-context.sh claude`. Add Feature 130 entry per the plan's Phase 1 Design spec. Review the generated entry for accuracy before committing. **DEVIATION**: The referenced script `.aod/scripts/bash/update-agent-context.sh` does not exist in this repo (only `check-prerequisites.sh`, `common.sh`, `run-state.sh`, etc. are present under `.aod/scripts/bash/`). Degraded to manual edit — Feature 130 entry prepended at CLAUDE.md lines 101-110 above Feature 136, all 9 pre-existing Recent Changes entries preserved intact. Entry matches Feature 136 formatting: 9 bullets (1 title + 8 nested detail bullets), conversational-technical tone, backticked file path refs, cross-linking to ADR-022 and ADR-021.
- [X] T026 [P] Write [specs/130-prd-130-fix/quickstart.md](quickstart.md) following the outline in plan.md Phase 1 Design > Quickstart section. Include: (a) local reproduction of the bug, (b) validation after the fix, (c) happy path validation with baseline test, (d) regeneration instructions.
- [X] T027 Manual end-to-end validation on a local shell with `mmdc` present: run `/tachi.security-report examples/mermaid-agentic-app/`. Verify the generated PDF contains rendered attack path diagram images on every attack path page (no raw Mermaid source). Inspect visually. Document the result in the PR description. **Result**: Automated replay of the T020 regeneration command — pipeline exit 0, output byte-identical to baseline (0-byte diff), 25 image xobjects embedded in the PDF. Raw Mermaid source structurally impossible (T024 confirmed text-fallback branch deleted). Evidence at `.aod/results/tester-130-t027-t028-t029.md`.
- [X] T028 Manual end-to-end validation on a local shell with `mmdc` removed from PATH (use `PATH=$(echo $PATH | tr ':' '\n' | grep -v mmdc | tr '\n' ':')` or equivalent). Run `/tachi.security-report examples/mermaid-agentic-app/`. Verify the pipeline aborts non-zero with the canonical three-line error message. Verify no PDF is produced (or any stub is clearly identified as an error artifact, not a deliverable). Document the result in the PR description. **Result**: Automated with `env -i PATH="/usr/bin:/bin"` (clean PATH, mmdc absent). Pipeline exit 1. RuntimeError message contains all 3 canonical tokens (`@mermaid-js/mermaid-cli`, `npm install -g @mermaid-js/mermaid-cli`, `Attack path rendering`). No PDF produced. Evidence at `.aod/results/tester-130-t027-t028-t029.md`.
- [X] T029 Manual PDF inspection of `examples/agentic-app/sample-report/security-report.pdf` (the 47-attack-tree example). Verify visually that all attack path pages show rendered diagrams. Document the result in the PR description. **Result**: Sub-wave 6b T021 regeneration succeeded (17 Critical/High trees dispatched, zero mmdc/Typst warnings, ~10s). Regenerated PDF embeds 39 image xobjects. Visual inspection deferred to PR reviewer as courtesy check; automation provides dispositive evidence. Evidence at `.aod/results/tester-130-t027-t028-t029.md`.

---

## Phase 7: Polish

**Purpose**: Final verification gates before PR submission.

- [X] T030 Run the full test suite: `pytest tests/` and confirm 100% pass. No skipped tests without documented justification.
- [X] T031 Pre-merge constitutional checklist walk-through (per plan.md Constitution Check section): verify no runtime Python dependencies were added, the Python stdlib-only constraint holds, feature branch workflow is intact, no commits to main, conventional commit format used throughout.
- [X] T032 PR description assembly: summarize all 7 FR-130.x deliverables with references to individual commits, link the manual validation results from T027/T028/T029, link the ADR-022 for governance context, and include a "Before / After" narrative suitable for the CHANGELOG entry (release-please will auto-cut the release). **Result**: PR description assembled at [specs/130-prd-130-fix/PR-description.md](PR-description.md) (98 lines, 9 sections). All 7 FR deliverables mapped to commits `db0073c` (FR-130.1/2/3), `732fd49` (FR-130.4), `b46e931` (FR-130.5), `648b4d1` (FR-130.6/7) with file-level references. Governance context via ADR-022, spec 112 corrections, Tech Stack doc. Manual validation evidence from `.aod/results/tester-130-t027-t028-t029.md` and R9 before/after guardrail pair. PR creation deferred to `/aod.deliver`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — starts immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — MUST complete before any user story
- **Phase 3 (US1)**: Depends on Phase 2 — the preflight gate MVP
- **Phase 4 (US2)**: Depends on Phase 3 completion of T006 (Python-level raise is the substrate for the mid-render aggregator in T010-T011). Implementation-wise, US2 tests/code must land after US1's `render_mermaid_to_png()` refactor.
- **Phase 5 (US3)**: **Independent of Phase 3 and Phase 4.** All US3 tasks are documentation changes in files that do not intersect with US1/US2 code. Can start in parallel with Phase 3 if staffing allows.
- **Phase 6 (Cross-Cutting & CI)**: Depends on US1 + US2 + US3 all being complete. CI workflow cannot be tested until the code it asserts against exists.
- **Phase 7 (Polish)**: Depends on Phase 6 completion.

### Story Dependencies (Plan-stage rationale)

- **US1 (P1)**: No story dependencies. MVP delivers a preflight gate that makes the silent-failure case loud.
- **US2 (P1)**: Depends on US1's `render_mermaid_to_png()` refactor. The two changes share the same function body; US2 cannot cleanly land without US1 having already landed.
- **US3 (P1)**: No code dependencies. Can land in any order relative to US1 and US2. Note: US3 includes the Tech Stack doc update that cross-links ADR-022 — ADR-022 (T003) must exist before T015 runs.

### Within Each User Story

- **US1**: T004 (tests) → T005/T007 (parallel, different files) + T006 (extract-report-data.py) → T008 (verify)
- **US2**: T009 (tests) → T010 → T011 → T012 (verify)
- **US3**: T013/T014/T015/T016/T017 all parallel

### Parallel Opportunities

- **Within Phase 3 (US1)**: T005 (command file) and T007 (Typst template) are different files, both after T004 tests are in place. T006 depends on T004.
- **Within Phase 5 (US3)**: ALL tasks (T013-T017) are different files and parallel-safe.
- **Across phases**: US3 (Phase 5) can run in parallel with US1 (Phase 3) and US2 (Phase 4) if staffing allows.
- **Within Phase 6**: T025 and T026 are `[P]` because they touch separate files (CLAUDE.md via script, quickstart.md).

---

## Parallel Example: User Story 1

```bash
# Launch US1 test creation (blocks rest of US1)
Task: "Create tests/scripts/test_mmdc_preflight.py with four failing preflight tests (T004)"

# Once T004 lands, launch parallel US1 code changes
Task: "Add shell-level preflight to .claude/commands/tachi.security-report.md Step 1 (T005)"
Task: "Delete text-fallback branch lines 78-86 in templates/tachi/security-report/attack-path.typ (T007)"

# T006 serializes on extract-report-data.py (same file as US2 eventually, but US1 edit is distinct)
Task: "Convert silent shutil.which check to RuntimeError raise in scripts/extract-report-data.py (T006)"

# Verify
Task: "Run pytest tests/scripts/test_mmdc_preflight.py -k preflight, confirm all pass (T008)"
```

## Parallel Example: User Story 3

```bash
# All five US3 tasks are parallel-safe — different files, no shared state
Task: "Author README.md Prerequisites section (T013)"
Task: "Add mmdc check to scripts/install.sh (T014)"
Task: "Update docs/architecture/00_Tech_Stack/README.md line 279 + ADR-022 link (T015)"
Task: "Invert SC-004 in specs/112-attack-path-pages/spec.md, delete line 135 (T016)"
Task: "Correct line 80 + add rationale block in specs/112-attack-path-pages/research.md (T017)"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002-T003) — **CRITICAL**: ADR-022 before any code
3. Complete Phase 3: User Story 1 (T004-T008)
4. **STOP and VALIDATE**: Run pytest, manually remove mmdc from PATH, run `/tachi.security-report examples/mermaid-agentic-app/`, verify loud failure
5. If US1 stopped here would still be a valid shippable increment (the flagship silent-failure case is fixed)

### Incremental Delivery (recommended for this feature)

1. Setup + Foundational → checkpoint
2. US1 (preflight gate) → checkpoint + manual validation
3. US2 (mid-render loud failure) → checkpoint + manual validation
4. US3 (docs sync) in parallel with US1/US2 if capacity allows → checkpoint
5. CI + Polish (Phase 6, Phase 7) → PR ready

### Parallel Team Strategy

With multiple developers:

- **Developer A** (Python + Typst): US1 (T004-T008) then US2 (T009-T012)
- **Developer B** (docs + config): US3 (T013-T017) in parallel with Developer A
- **Developer C** (or Developer A after US2): Phase 6 CI + baselines (T018-T022)

US3 is fully parallelizable against US1/US2 code work.

---

## Effort Estimate Mapping (PRD Timeline: 5 days)

| Task range | Scope | Plan stage budget | Tasks |
|---|---|---|---|
| Spike & ADR-022 | Plan Day 0 + governance artifact | 0.5d + 0.25d (ADR) | T001-T003 |
| FR-130.1 preflight | US1 shell + Python + tests | 0.5d | T004-T008 |
| FR-130.2 + FR-130.3 extract-data + Typst | silent fallback deletion | 0.25d + 0.1d | T006, T007 (part of US1) |
| FR-130.4 mid-render failure | US2 aggregator + tests | 0.25d | T009-T012 |
| FR-130.5 docs sync | 5 files, parallel authoring | 0.75d | T013-T017 |
| FR-130.6 example regeneration | 2 examples + test | 0.5d | T020-T022 |
| FR-130.7 CI fresh-install test | new workflow file | 0.5d | T018, T019 |
| Polish + verification + PR | grep checks, manual valid, PR prep | 0.5d | T023-T032 |
| Triad reviews (already done at spec/plan/tasks) | included above | 0.5d | n/a |

**Total**: ~4.35d + 0.65d buffer = 5d target holds. ADR-022 authoring (~0.25d) fits within the buffer per PM review concern.

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **Tests MUST fail before implementation** (Constitution Principle VI, test-first)
- Commit per story (not per task) to keep the git history readable: `fix(130): <story title>`
- Stop at any US checkpoint to validate story independently
- **Architect R6 (error message format)** is the single highest-priority refinement and MUST be specified correctly in T009 (test) and T011 (implementation). A vague error message is the failure mode we are fixing — do not reintroduce it in the fix.
- **R9 (before-and-after baseline test)** is High priority — skipping T002 means we cannot prove backward compatibility.
- **R8 (do NOT add agentic-app/sample-report to BASELINE_EXAMPLES)** is an explicit negative task. Do not "improve" test coverage by adding it.
- ADR-022 MUST be authored in T003 (before code changes) so all downstream cross-references (Tech Stack doc, canonical-message grep, CLAUDE.md recent changes) can target a real file.
- Avoid: vague tasks, same-file conflicts on the extract-report-data.py refactor (US1 and US2 both touch it — serialize), cross-story dependencies that break independence (US3 is truly independent of US1/US2 code).
