---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-09-27
    status: APPROVED_WITH_CONCERNS
    notes: "tasks.md matches the spec and plan. No scope creep; FR coverage 44/44, all nine story slices, NFR-1..NFR-8 and SC-1..SC-8 mapped. The RC-P1..RC-P8 plan fold verified PASS (8/8). 5 required changes (MEDIUM RC-T1: a complete TW-7 early-PR path with its own notices, the P-10.4 render set and the A-2 dependency; LOW RC-T2..RC-T5) FOLDED in the team-lead's rev. 1 (T040, T030, T015, T009/T011/T038, T002/T005). New binding rulings: P-11.1 (installer scope wording: broken, looping or wrong-type links, nested links, destinations inside the tachi source clone), P-11.2 (notices when TW-7 splits the release), P-11.3 (T039's W1-exit TW-0..TW-2 re-check ACCEPTED). Details: .aod/results/product-manager-373-tasks.md"
  architect_signoff:
    agent: architect
    date: 2026-09-27
    status: APPROVED_WITH_CONCERNS
    notes: "Iteration 3. The first review was CHANGES_REQUESTED (MEDIUM F1 K12 helper placement, F2 inherent-join call-site wiring, F3 tier-2/3 recommendation blanking, F4 no post-landing carve mechanics; conditions C-1..C-3; L1-L18), all folded in team-lead rev. 1. The fresh re-review was CHANGES_REQUESTED (new MEDIUM NM-1: K12 must count the normalized Section 7 map per FR-K12.1/K12.2, 4/0/82 on agentic-app/sample-report; NM-2: T039's carve paths could not execute; required LOW-1: agent-assignments.md must exist), folded in rev. 2. The delta check verified 3/3: 13/13 plan conditions encoded; ordering, the W1 launch rule and one writer per wave hold; agent-assignments.md matches all 40 tasks with registry names only; the tester->senior-backend-engineer reassignment for pytest and the W3 writer is confirmed (F-362 precedent). 5 LOW build-time notes remain. Details: .aod/results/architect-373-tasks.md, .aod/results/architect-373-tasks-rereview.md"
  techlead_signoff:
    agent: team-lead
    date: 2026-09-27
    status: APPROVED_WITH_CONCERNS
    notes: "Bottom-up re-cost: effort 8.31 d; duration 3.5 / 5.2 / 7.7 d (floor/central/ceiling). TW-0 NOT fired: 5.21 d against 5.5 d (margin 0.29 d; the producer's 4.4 d projection was superseded); T039 re-checks it at W1 exit with actuals (P-11.3). TW-1 (K11 1.14 d against 1.2), TW-2 (0.50 against 0.6), TW-3 and TW-4 NOT fired; OQ-5 closed (the #370 test uses the real MITRE catalog; T031 retargeted after 3d67ca7 moved the guard). R-1..R-8 folded: the W1 launch rule, the corrected TW-0 record, the T039 checkpoint, an agent per task, a single W3 writer, T031 retargeted, the five goldens named, the N4 re-run. 40 tasks, acceptable because they are split by lane and carve unit; peak agent load 70% (no instance over 80%). Milestones: M4 target Fri 10-02 (about 0.3 d slack), realistic Mon 10-05; ceiling Wed 10-07 for the full bundle, with TW-7 landing K1-K3 by about 10-05. agent-assignments.md generated. Details: .aod/results/team-lead-373-tasks.md, -revision.md, -revision-2.md"
---

# Tasks: Adopter Install + Output Fidelity Fixes

**Input**: Design documents from `/specs/373-adopter-install-output-fidelity/`
**Prerequisites**:
- `plan.md`: PM and Architect both APPROVED_WITH_CONCERNS; architect iteration 2; rev. 2 folds in the re-review.
- `spec.md`: PM APPROVED_WITH_CONCERNS; the spec touches T1–T31 and PM rulings P-9.x and P-10.1–P-10.4 are applied.
- `research.md`: PD-1..PD-20.
- `data-model.md`.
- `contracts/`: installer-cli, manifest-completeness, extraction-data-contract, gemini-request-and-scaffold.
- `quickstart.md`.

**Revision 1 (2026-09-27)** folds in the three `/aod.tasks` reviews:
- the architect's, CHANGES_REQUESTED (`.aod/results/architect-373-tasks.md`): F1–F4, the condition gaps C-1..C-3, and L1–L18;
- the PM's, APPROVED_WITH_CONCERNS (`.aod/results/product-manager-373-tasks.md`): RC-T1..RC-T5, R-T1..R-T4, and the binding rulings P-11.1 and P-11.2 (§ PM rulings from the tasks review);
- the team-lead's, APPROVED_WITH_CONCERNS (`.aod/results/team-lead-373-tasks.md`): R-1..R-8, including the TW-0 re-cost and ruling.

**Revision 2 (2026-09-27)** folds in the architect's delta re-review (`.aod/results/architect-373-tasks-rereview.md`): NM-1, NM-2, LOW-1 and LOW-2..LOW-9. LOW-10 goes to the PM.
- It adds `agent-assignments.md`, which `/aod.build` reads.
- It corrects two assignments: the `senior-backend-engineer` now writes the pytest modules, and a `senior-backend-engineer` is the W3 writer (§ Standing rules, "Agent types").

Task IDs T001–T040 are unchanged. The item-by-item maps are in `.aod/results/team-lead-373-tasks-revision.md` and `.aod/results/team-lead-373-tasks-revision-2.md`.

**Tests**: Included. The spec mandates them:
- NFR-1: synthetic-fixture regression tests for every deterministic fix;
- FR-K2.3–K2.5: the manifest completeness test;
- FR-K3.6: the installer tests, with the safety negatives written first;
- FR-K14.2: the static contract test;
- NFR-7: CI gating in lock-step.

Live renders are `[MANUAL-ONLY]` (US-4a #5, US-4b #4).

**Organization**: Tasks are grouped by user story, in priority order, and bucket-scoped rather than file-scoped. Each task names:
- its **lane** (plan § Structure decision: lanes follow files, one writer per wave);
- its **wave** (W0–W4; `/aod.build` waves 1–5);
- its **agent**, by exact registry name (`.claude/agents/_README.md`);
- its central effort as `~X d` (attention-days; the team-lead's re-cost).

§ Trip-Wire Evaluation holds the TW-0..TW-4 rulings and the per-wave agent load. `agent-assignments.md` carries the assignment matrix, the `/aod.build` wave map, the checkpoints and the quality gates (LOW-1).

> **Definition of Done** (canonical bar = constitution VII; PRD-373 §8 applies in full, refined in spec SC-6/SC-7/SC-8, NFR-7, NFR-8, FR-K3.4 and FR-K14.3):
> 1. ✅ Pushed to Production — feature deployed and operational.
> 2. ✅ Tested — all automated tests pass (unit, integration, E2E, performance)
> 3. ✅ User Validated — real-world usage confirmed by actual users/stakeholders.

<!-- DOD-ACK -->

## Format: `[ID] [P?] [Story] Description`

- **[P]**: the task can start at its wave's start without waiting on another task of the same wave. A lane's own tasks still run in sequence under that lane's agent, so schedule from the lane table, not from the markers.
- **[Story]**: US1, US2, US3a, US3b, US3c, US4a, US4b, US5, US6, matching the spec's story IDs.
- **Agent**: named in each task's parenthesis. When a task names several agents, they split it by file. The team-lead is the assigner, never an assignee: its trip-wire rulings are checkpoints that the `orchestrator` invokes.
- Paths are repo-relative. Pointers follow the contracts and are verified at `v4.48.0` (`63438d7`).

## Standing rules for every task (NFR-8, KB)

- **Never run the extraction modules, the extractors or `install.sh` in the main working tree.** Use a scratch clone (`quickstart.md` §1). They re-render tracked `examples/**` PNGs (#365).
- **Commit before running a gated suite.** The harness clones the committed HEAD.
- **Verify your own commit, not the shared tree (R-1).**
  - Lanes share one working tree, so a lane runs its checks in a scratch clone of its own local commit. Another lane's uncommitted edits then never reach its run.
  - This matters in W1: the completeness module's end-to-end case and import walk read `scripts/install.sh` and `scripts/*.py`, which A′ and B1 are editing at the time.
- **Carvable and early-ship K-items get their own commits (F4, NM-2).**
  - K11, K13-posture and K15 commits, and C1's K14 commits, never share a commit with other work. Each names its K-item in the subject, for example `fix(373): K15 allow-list emission`.
  - A later carve, or T040's K14 ride, is then a `git revert` or a cherry-pick of named commits, followed by T032 for the surviving goldens.
  - Non-carvable work may share commits: A-1 (K1/K2), and T016's K9, K10 and K12.
- **`/aod.build`'s post-wave tests run the gated set in a scratch clone (LOW-2).**
  - After each wave, run the fast-workflow modules plus `tachi-pytest.yml`'s gated subset, in a scratch clone of the wave commit.
  - Never run the full `pytest` in the main tree. It re-renders tracked PNGs and hits about 19 pre-existing reds outside the gate.
  - Skip sub-step 4.6's test generation (NFR-7: every module must be gated), or pass `--no-tests` with the reason recorded. `agent-assignments.md` § 4 has the exact commands.
- **Stage explicit paths only.** Never `git add -A`. Before each commit, run `git status --short` and restore only the `examples/**/*.png` changes this session produced.
- **New tests never write into `examples/`.** No real-world content goes anywhere (NFR-6).
- **Agent types.**
  - `senior-backend-engineer` instances write every pytest module, fixture and golden, as well as the product files. That includes the test lane (the plan's "tester" rows) and the single W3 writer.
  - This repo's `tester` agent is a BDD/Gherkin specialist, and its registry boundary is "writes tests only, does not implement application features or fix bugs". It runs validation scenarios (the live render sessions and the N4 re-runs), records them, and edits no product file. This follows the F-362 T017 precedent.
- **Reviewer prompts carry these rules.**
  - Every reviewer and verification agent is told: no pytest and no extractors in the main tree; scratch clone only; run `git status --short` after it returns.
  - The reviews in T011 and T036 are scoped explicitly to executable code (bash, Python, Typst), checked against the contracts. The knowledge-system stack supplements say there is no application code to review, which is not true of this bundle.

## PM rulings from the tasks review (2026-09-27; binding for the build)

- **P-11.1: installer scope wording.**
  - The help text (both surfaces), the README K3 section and the D-1 release note name the always-refused set as "broken, looping or wrong-type links, links nested inside an installed folder, and destinations inside the tachi source clone".
  - Wrong-type links are named, not folded into "broken". This settles the architect's re-review item T27.
  - "Destinations inside" replaces "links into", because containment works on physical destinations (M1, AR-1).
  - The refusal messages are unchanged. `contracts/installer-cli.md` `:17` and `:243` now carry the new phrase.
  - Realized in T009, T011 and T038.
- **P-11.2: notices when TW-7 splits the release.**
  - The early release carries:
    - notice 1: update the clone first, then re-run `install.sh`; it names the three skills and the populator;
    - notice 2 if K3 rides, otherwise notice 7;
    - notice 6 if K14 rides with a model recorded as statically verified only.

    The PM writes these when TW-7 fires, and PD-7's mechanism applies to that release.
  - The main release carries notices 3 to 6 as applicable, plus notice 2 if K3 did not ride early. It opens with one line: "Update your tachi clone and re-run `install.sh` to pick up these fixes."
  - SC-6 is verified per release with `gh release view`.
  - Realized in T040 and T038.
- **P-11.3: the W1-exit trip-wire re-check (T039) is accepted** (the PM, after the architect re-review's LOW-10).
  - It re-evaluates TW-0..TW-2 once at W1 exit, on actuals, with the PRD §10 thresholds and the fixed carve order K15 → K11 → K13-posture.
  - It preserves P-9.5 and P-10.2.
  - It is recorded in the spec's split-valve "During the build" list.
  - Realized in T039.

---

## Phase 1: Setup (W0: pre-state and de-risking)

**Purpose**: record the literal pre-state, snapshot the data layer, retire model-access risk, and build the synthetic fixtures every story consumes. It writes no product code.

- [X] T001 [P] Pre-state and oracle pre-snapshot, in a **clean scratch clone** at the W0 commit (`senior-backend-engineer`; ~0.15 d).
  - **Pre-state.** Record literal pass, fail, skip and error totals in `specs/373-adopter-install-output-fidelity/test-results-prestate.md` for:
    - the four modules the fast workflow will gate (`tests/scripts/test_tachi_parsers.py`, `test_extract_infographic_data.py`, `test_extract_report_data.py`, `test_extractor_contract_fixes.py`);
    - `tests/scripts/test_executive_architecture_payload.py` (N4);
    - `tachi-pytest.yml`'s current 16-module invocation;
    - the roughly 20 ungated parser- and extractor-consuming modules (N4; for example `test_source_attribution.py`, `test_finding_pattern_parser.py`, `test_project_name_parser.py`, `test_attack_chain_extraction.py`).
  - **Oracle pre-snapshot** (`quickstart.md` §3): both extractors × the 12 **tracked** example directories that have a `threats.md` × the 6 templates, plus `report-data.typ`.
    - Normalize run-specific fields.
    - Capture each run's stderr with it, so T035 can attribute new warning classes and N7's warning (L8).
    - Snapshots stay in the scratchpad; only the run list is recorded.
- [X] T002 [P] W0 smoke render (P-10.3, PD-3, PM R-b; `senior-backend-engineer`; ~0.05 d), recorded in `specs/373-adopter-install-output-fidelity/test-results/w0-smoke.md` (`quickstart.md` §4).
  - **Calls**: eight `generateContent` calls: `gemini-3-pro-image` and `gemini-3.1-flash-image` × {16:9, 3:4} × {default size, `imageSize: "2K"`}. The key is loaded per NFR-5 (only in the process environment; sent only as a header read from stdin; never `-v`).
  - **Record per call**: HTTP status, whether an image came back, pixel dimensions, response time, and response-part key casing.
  - **Decide `IMAGE_SIZE_RESTORED`**: true only if all four 2K calls return an image whose long edge exceeds the default variant's.
  - **3:4 at default size must succeed on both models.** This is blocking only for T013's executive-architecture configuration.
    - AR-2 scoped this decision to that configuration. The wording "before K14 commits" at `quickstart.md:115`, `contracts/gemini-request-and-scaffold.md:187` and `research.md:174` is superseded (LOW-5).
  - **Any other refusal status** (not 404 or 403) is recorded for the architect under AR-2. It is non-blocking: W1 is never held.
  - **A blocked model** follows P-10.1: diagnose and retry within TW-6's budget.
  - **Order**: T002 precedes both T012 and T013. T012's reference and adapter bodies carry `imageSize` only if `IMAGE_SIZE_RESTORED`, and its provenance dates come from this record (L1).
- [X] T003 [P] Synthetic fixtures and symlink sandbox builders (the test lane; `senior-backend-engineer`; ~0.20 d).
  - **Fixtures**, under `tests/scripts/fixtures/fidelity_373/`, in the templates' real section order:
    - short-form controls headers with an empty Critical band;
    - an empty last band directly before `### Summary Statistics`;
    - a `###` MAESTRO heading;
    - a `## 4c.` baseline with known NEW, UPDATED, UNCHANGED and resolved counts plus one placeholder row, and a legacy `## 4b.` twin;
    - bracketed statuses: `[NEW]`, `**[NEW]**` and `` `[NEW]` `` (N6);
    - a baseline run whose Section 7 status map and tier finding IDs differ (F1);
    - a Status-less Section 7 on a non-baseline run;
    - a controls Section 4 that covers only some findings, and a drifted Section 4;
    - K11 funnels: STEP-bound, strong-reduction, 3-tier, threats-only and volumes-unavailable;
    - an Inherent-less controls table with a matching `risk-scores.md`, for the K11 join path (F2);
    - statuses `Missing`, empty, unrecognized, `Partially Found` and `None found`;
    - unparseable scores (`—`, `8.5 (High)`, `NaN`);
    - residual above inherent;
    - a Section 1 comparand mismatch;
    - a controls/risk-scores row-count mismatch.
  - **Sandbox builders** go in `tests/scripts/install_sh_helpers.py` (the test lane in W0; Lane A′ owns it from W1). They build symlinks at test time only, never committed.
    - **Commit the builders on their own** (LOW-3). `install_sh_helpers.py` does not exist on `main`, so T040's K3 cherry-pick set needs that commit.

**Checkpoint**: pre-state, smoke and fixtures recorded. `IMAGE_SIZE_RESTORED` is decided before T012 and T013.

---

## Phase 2: User Stories 1 + 5: Every skill and script ships, and CI catches drift (P1). 🎯 MVP / the cut line

**Goal**: K1/K2 plus its guard land in one green commit, **A-1**, before any other lane's commit (PM ruling P-9.1: never bent).
- The other lanes develop from the start of W1, but none of them commits before A-1 is green (§ Dependencies, the W1 launch rule).
- From that commit on, the bundle can be cut at any wave boundary without holding K1/K2 back.

**Independent Test**:
- a fresh install into an empty project yields 21 skill dirs, 21 agent definitions and 4 scripts;
- the completeness test is green on the fixed manifest and red on every negative case;
- the `manifest-completeness` job runs on PR #375.

- [X] T004 [US1] Manifest and manual-install surfaces (Lane A, W1; `senior-backend-engineer`; ~0.20 d).
  - `INSTALL_MANIFEST.md`:
    - the block gains `tachi-output-integrity/`, `tachi-misinformation/`, `tachi-human-trust-exploitation/` and `scripts/populate-affected-assets.py`;
    - the prose counts become 21/21, and the agent table gains three rows;
    - both script notes and the script table cover 4 scripts;
    - the dependency note becomes "stdlib-only at import; PyYAML lazily for the PDF coverage-attestation page";
    - `:73` becomes the "every other file in `scripts/` is tachi-internal" rule;
    - `:71` gets the R-P7 wording;
    - the `:140` checklist item is reworded.
  - `README.md` "Manual install (alternative)" and both blocks in `docs/guides/DEVELOPER_GUIDE_TACHI.md` (split the combined fence at `:1011-1032`):
    - the comment-free loop between the `<!-- BEGIN MANUAL INSTALL LOOP -->` and `<!-- END MANUAL INSTALL LOOP -->` markers (`contracts/manifest-completeness.md`). T005 byte-compares the three blocks between exactly these markers (L15);
    - the D-1 sentence ("does not check for symlinked destinations");
    - stale verify counts replaced by a manifest comparison;
    - `--version v4.0.0` becomes `vX.Y.Z`.
- [X] T005 [US5] Completeness test and the cut-line commit **A-1** (Lane A, W1; `senior-backend-engineer` writes the module; `devops` writes the workflow and runs the #375 check; ~0.40 d).
  - Create `tests/scripts/test_install_manifest_completeness.py` per `contracts/manifest-completeness.md`:
    - a reader that mirrors `parse_manifest`, with markers exactly once and entry hygiene (no whitespace, `..`, `/` or `~`, no entry prefixing another);
    - required sets (a)–(d), with the `(?:\./)?` regex over the pinned distributed globs;
    - a fail-closed commented exclusion list, and cardinality floors;
    - S-13's stdlib-only import assertion (skipped below Python 3.10);
    - the negative matrix, with failure messages naming `INSTALL_MANIFEST.md` and the path;
    - the manifest-driven, `.git`-less e2e install;
    - `test_manual_install_loop`: the three blocks byte-identical, the static no-comment check, run under bash and under `zsh -f -i` when present, idempotent on a second run.

    The module must not import `install_sh_helpers.py`.
  - Create `.github/workflows/tachi-install-fidelity.yml` with **only** the `manifest-completeness` job (PD-9, RC-P1):
    - its `paths:` are:
      - `INSTALL_MANIFEST.md`;
      - `.claude/skills/**`, `.claude/commands/tachi.*.md`, `.claude/agents/tachi/**` and `templates/tachi/**`;
      - `scripts/*.py`, for the import closure and S-13 (RC-T5 (b), L15);
      - `scripts/install.sh`;
      - `README.md` and `docs/guides/DEVELOPER_GUIDE_TACHI.md`;
      - the module, both conftests, `pyproject.toml` and the workflow;
    - `pull_request` plus `push: [main]` through one anchor;
    - `contents: read`; pytest, pytest-timeout and PyYAML.
  - Commit **A-1** locally, run the module in a scratch clone of that commit, push, and confirm that the job ran and is green on #375.
  - Record the one-time `/bin/bash` 3.2 and zsh manual-loop run in `specs/373-adopter-install-output-fidelity/test-results/`.

**Checkpoint (cut line)**: A-1 is green on #375. US-1 and US-5 are independently shippable: TW-7 can ship from here, through T040.

---

## Phase 3: Foundational (W1, after A-1): the Group B safety net and the scaffold guard

**Purpose**: two prerequisites.
- The pre-existing extraction modules get gated **before any parser change** (the R-3 net).
- The prompt splitter gets hardened **before any prompt-text edit** (M3).

**⚠️ Ordering**:
- T006 lands immediately after A-1 and before any Lane B1 commit.
- B1 develops from the start of W1, in its own worktree (T016).
  - Its first commit may be a marker-only commit in `test_tachi_parsers.py`, made after A-2 is committed and before A-2's job is green (LOW-6).
  - Its other commits wait until A-2's job is green.
- T007 lands before any prompt-text edit (T022, T026, T028).
- T013 edits only the configuration fences, which sit after the prompt fence, so it may land before T007 when T007 is held only by A-2's triage.

- [X] T006 Wiring commit **A-2**: gate the pre-existing extraction modules (Lane A, W1; `devops` for the job, the triage and the quarantine markers; `senior-backend-engineer` for the fixture edit; ~0.10 d).
  - In the `agentic_app_report_typst` fixture of `tests/scripts/test_extract_report_data.py` (PD-8):
    - skip when `shutil.which("mmdc")` is None, before the extractor call;
    - move the fixture to a `tmp_path_factory` copy of the whole `examples/agentic-app/sample-report`.
  - Add the `extraction-fidelity` job to `.github/workflows/tachi-install-fidelity.yml`. It invokes `test_tachi_parsers.py`, `test_extract_infographic_data.py`, `test_extract_report_data.py`, `test_extractor_contract_fixes.py` and `test_executive_architecture_payload.py` (N4).
  - Its `paths:` gain:
    - `examples/**`, `tests/scripts/fixtures/exec_arch/**` and `tests/scripts/fixtures/golden/**` (N3);
    - `tests/scripts/fixtures/report_data/**`, which `test_extract_report_data.py:24` reads (C-1);
    - `tests/scripts/fixtures/fidelity_373/**`, whose first reader is B1's W1 test-first work in `test_tachi_parsers.py` (C-1);
    - `schemas/taxonomy/*.yaml` (OQ-5). The gated report module loads the catalogs whenever an input carries source attribution (`extract-report-data.py:2328-2331`), and T031's second case reads them too;
    - the extractors, `tachi_parsers.py` and the modules.
  - **Triage owner (N9, C-3): `devops`.**
    - It attributes any pre-existing red on bare ubuntu within 0.15 d, then escalates to `debugger`.
    - It may add per-test skip or xfail markers that cite a follow-up issue. It adds them to the modules that have no other W1 writer (`test_extract_infographic_data.py`, `test_extractor_contract_fixes.py`, `test_executive_architecture_payload.py`) and to `test_extract_report_data.py`.
    - A red in `test_tachi_parsers.py` gets its marker from B1, that file's W1 writer. It lands as B1's marker-only first commit (LOW-6).
    - Once the markers land, the job is green and the R-3 net is live.
  - Commit A-2 locally, verify it in a scratch clone of that commit, and push.
- [X] T007 PD-6 splitter hardening in `scripts/extract-infographic-data.py` (Lane B1, W1; `senior-backend-engineer`; ~0.05 d).
  - Anchor the primary marker to line start (`^DATA CONTENT \(render this`).
  - Search for `\nFOOTER` only after the marker line.
  - Drop the no-newline `find("FOOTER")` fallback.
  - **Keep the bare `^DATA CONTENT` fallback** (N8, decided per L14; NFR-4; it is unreachable while the primary marker exists). Pin that in a code comment and in the contract's scaffold note.
  - Scaffold output must be byte-identical on today's five templates, so the goldens stay unchanged. The golden test proves it.

**Checkpoint**: the safety net is active, and the scaffold is hardened. Lanes A′, B1 and C1 proceed in parallel.

---

## Phase 4: User Story 2: The installer never writes or deletes through a symlink without consent (P1)

**Goal**: D-1 in full.
- Deny by default.
- `--follow-symlinks` for links at or above each entry.
- Four classes always refused, flag or not: unresolvable links, nested links, destinations in the source tree (by identity), and cleanup through a link.
- A restore that is never silent.

K3 is not a split candidate, and it ships with K1.

**Independent Test**: sandboxed synthetic projects cover every US-2 scenario on the `tachi-pytest.yml` 2-OS matrix: bash 3.2 with BSD tools, and bash 5 with GNU tools.

- [X] T008 [P] [US2] K3 test harness, safety negatives first (Lane A′, W1; `senior-backend-engineer`, the test-lane instance; ~0.45 d). Write `tests/scripts/test_install_sh_symlink_preflight.py` and `tests/scripts/test_install_sh_ref_restore.py` on `tests/scripts/install_sh_helpers.py`, per `contracts/installer-cli.md` § Test harness contract.
  - **Harness**:
    - `/bin/bash` pinned (N12), with `LC_ALL=C`; ANSI codes stripped; only installer-authored text asserted;
    - a working-tree `install.sh` copied into synthetic sources;
    - `--version` throwaway repos with isolated git config and an identical `install.sh` at the tag and at HEAD;
    - the `/bin/sh` git shim for the forced restore failure;
    - before-and-after tree snapshots of the target and of each link's target;
    - non-vacuous "reached through a link" and "above the root" cases.
  - **Written first**: the cleanup safety negatives (refused without the flag; skipped with it; the shared file survives).
    - The evidence is a recorded local red run against today's installer, in `specs/373-adopter-install-output-fidelity/test-results/k3-test-first.md`, not a red commit (L16).
  - **Cases**:
    - every US-2 scenario (#1–#12);
    - the rev. 1 cases: containment through the clone's parent, a vendored clone, a wrong-type link, a dangling deprecated-command link, and a no-link install on bash 3.2;
    - the rev. 2 cases (AR-1): a case-variant link into the clone, and a project reached through a case-variant path. These run on macOS only and skip on case-sensitive volumes;
    - N11 (decided per L14): a tachi clone that sits at a subtree path of a directory entry is refused.
  - The modules land in T010's single lock-step commit.
- [X] T009 [US2] K3 implementation in `scripts/install.sh` (Lane A′, W1; `devops`; ~0.62 d).
  - **Containment**: project-root containment with the `under` identity walk at the `:95` site, before the version block.
  - **Pre-flight**: after the `--version` checkout, before the cleanup. It covers:
    - origin sets; `resolve` (40 hops) and `phys_dest`;
    - per-entry destination containment by identity (AR-1), plus the same check for every cleanup file that is not itself a link (L5);
    - N11: for each directory entry, refuse when `under "$SRC_P" "$dest"`. The always-refused remedy already covers moving the clone;
    - classification; refusal and opt-in reports (RC-P4 texts); the cleanup skip.
  - **Flag**: `--follow-symlinks` parsing (long form, boolean, no alias).
  - **Trap**: records rc, `if ! git … checkout`, warns, exits with rc; fix the `:111` comment.
  - **Help**: both help surfaces (the header comment and `usage()`) get the RC-P4 help text, as amended by **P-11.1**.
    - The always-refused set reads "broken, looping or wrong-type links, links nested inside an installed folder, and destinations inside the tachi source clone".
    - `contracts/installer-cli.md:17` carries the amended phrase. The refusal messages are unchanged.
  - **The M8 bash 3.2 rules**: helpers only in conditionals; `local`; `unset CDPATH`; newline strings instead of empty arrays; `< <(…)` loops.
  - **Keep** every `x-release-please-version` marker (`:13,19,43`).
  - **Iterate** locally on `/bin/bash` 3.2.57 until T008 is green.
- [X] T010 [US2] K3 CI lock-step and convergence (Lane A′ in W1, then Lane A in W2; `devops`; ~0.25 d).
  - **One commit (F-250, L16)**, pushed after A-1 is green. It holds:
    - T008's modules, `install_sh_helpers.py` and T009's `install.sh`;
    - the `.github/workflows/tachi-pytest.yml` wiring: the installer paths go into `&hardening_paths` with `# F-373` markers, the modules into the invocation, and a line into the header log.

    Before pushing, run the completeness module's end-to-end case in a scratch clone of this commit. `manifest-completeness` triggers on `scripts/install.sh`, so an installer regression would redden the cut-line job.
  - **Converge** both OS legs on #375 (Lane A, W2).
    - The ubuntu leg is the first GNU `cp` evidence.
    - Batch fix-forwards, so each ~25-min cycle counts.
  - T010 completes in W2, once both legs are green. `agent-assignments.md` counts it in build wave 3.
- [ ] T011 [US2] K3 docs and security review (Lane A, W2; `senior-backend-engineer` for the README; `security-analyst` for the review; ~0.15 d).
  - In `README.md`'s install section, document `--follow-symlinks` by reusing the help text's scope sentence (P-9.3), in P-11.1's wording. Keep the markers at `:120` and `:471`.
  - `security-analyst` gives an advisory review of the pre-flight, scoped to the bash code (standing rules):
    - deny-by-default;
    - no delete before the check;
    - identity containment;
    - the refusal classes.

    Findings go to `.aod/results/security-analyst-373-k3.md`.

**Checkpoint**: US-2 is green on both legs, with every refusal class and restore path proven.

---

## Phase 5: User Story 4a: The stock infographic agent renders every template (P1)

**Goal**: a schema-conformant `generateContent` body, created per template through a key-to-field mapping.
- The chain is the GA pair `gemini-3-pro-image` → `gemini-3.1-flash-image`, walked on 404/403.
- A 400 is loud but non-blocking.
- K14 is must-ship and never bends the cut line (P-9.1).

**Independent Test**:
- the static contract test (A1–A8) is green;
- K14's render set succeeds through the agent: each template once, each chain model at least once, and executive-architecture on one portrait PDF page (FR-K14.3, P-10.2).

- [X] T012 [P] [US4a] K14 reference, agent and adapter copy (Lane C1, W1; `senior-backend-engineer`; ~0.30 d; after T002).
  - `.claude/skills/tachi-infographics/references/gemini-prompt-construction.md`:
    - the known-good body;
    - the key→field table;
    - chain and walk set per PD-14, with `default_model` equal to chain[0];
    - camelCase `inlineData`/`mimeType` (SDK spelling accepted);
    - error guidance;
    - the corrected executive-architecture routing (`:31-39`);
    - provenance: endpoint, models, ratios, dates, and the single `Retired models:` line;
    - `resolution` removed.
  - `.claude/agents/tachi/threat-infographic.md`:
    - the skill-reference pointer to `executive-architecture.md`;
    - the "read the active template's configuration and map it" instruction;
    - error-table rows: 400 (not walked, Error, summary), 404/403 (walked), exhausted chain (Error, models named), catch-all (5xx, 2xx without image), and the 429 hint to reorder models.
  - `adapters/claude-code/agents/references/infographic-gemini-api.md` (FR-K14.6): the same body, chain and response keys.
- [X] T013 [P] [US4a] K14 template and executive-architecture configuration (Lane C1, W1; `senior-backend-engineer`; ~0.10 d; after T002).
  - The five `## Gemini API Configuration` blocks in `templates/tachi/infographics/infographic-{baseball-card,maestro-heatmap,maestro-stack,risk-funnel,system-architecture}.md`: chain models, `aspect_ratio: "16:9"`, `image_size` per `IMAGE_SIZE_RESTORED`.
  - Executive-architecture's `## Gemini API Configuration` section in `.claude/skills/tachi-infographics/references/executive-architecture.md`, **outside** the lock markers (PD-1): `aspect_ratio: "3:4"`.
  - Reword `templates/tachi/infographics/INFOGRAPHIC_TEMPLATES.md:127-134` ("validated by the static contract test").
  - **Constraint**: no fence under a prompt heading (FR-K15.3).
  - **If AR-2's decision 2 holds** executive-architecture's configuration (3:4 failed at W0), C1 commits the five blocks now. A-3 then lands without A3, and A3 joins with the configuration once the architect clears it (L1).
- [X] T014 [US4a] K14 static contract test and wiring commit **A-3** (W1; Lane C1's `senior-backend-engineer` writes the module; `devops` wires it for Lane A; ~0.20 d).
  - Create `tests/scripts/test_gemini_request_contract.py` with A1–A8 per `contracts/gemini-request-and-scaffold.md`:
    - `IMAGE_SIZE_RESTORED` pinned from T002;
    - chain order;
    - A3's line index after the END marker;
    - A6's retired-ID scan, with the `Retired models:` exception;
    - the strengthened A8 scaffold boundaries, plus N8's assertion (decided per L14): exactly one line-start `FOOTER` after the marker line. It holds on all five templates today.
  - A-3 adds the module to the `extraction-fidelity` job, with `adapters/claude-code/**` in `paths:`.
- [ ] T015 [US4a] K14 live render set (W3; `tester` runs the render session and records it, with the maintainer's visual check; the W3 writer, a `senior-backend-engineer`, makes any 2K-drop commit; ~0.20 d). `[MANUAL-ONLY] needs a live key, network, and a human visual check`
  - Run through the agent end to end, in a scratch clone of the W3 commit (T034), on a scratch copy of the MAESTRO reference example (`quickstart.md` §4).
  - **T015 and T030 are one sequential render session**, in this order:
    1. T030's first iteration (the six templates);
    2. T015's fallback-model render and one-page PDF check;
    3. any further T030 iteration.
  - **Render set, under P-10.2**:
    - if K15 ships, its first-iteration renders double as K14's per-template renders;
    - if K15 is carved, render each of the six templates once, with no leakage check;
    - either way, at least one render uses the fallback model;
    - executive-architecture (3:4) must land on one portrait page of a scratch PDF.
  - **2K latency**: if 2K was restored and any real 2K render exceeds ~45 s, drop 2K (RC-T3 (a), L6).
    - The W3 writer makes the drop as **one commit** that flips the six configuration blocks, the reference, the adapter copy and `IMAGE_SIZE_RESTORED` (PD-3). A1 and A4 go red on a partial drop.
    - Record the reason in the PR and in the reference provenance.
    - Re-push through T034 before T036 (LOW-4).
  - **A blocked model** (RC-T3 (b)):
    - it is recorded as statically verified only in the reference provenance, the PR record and the release notes (notice 6), with a follow-up issue;
    - both GA models stay in the chain (P-10.1, P-9.2).
  - **Record in the PR**: status, time, dimensions, visual check, endpoint, model, date, extension vs bytes, key casing. No images are committed.

**Checkpoint**: US-4a is statically green in W1 and live-verified in W3.

---

## Phase 6: User Story 3a: The report shows the same numbers as its source artifacts (P2)

**Goal**: K9, K10, K12 and K13 (recommendations, MAESTRO, placeholder rows). This is the deterministic core of G3, with every fix in the shared parser module and sibling parity across both surfaces.

**Independent Test**: T003's fixtures produce the exact expected values in both the infographic JSON and `report-data.typ`. The sibling-parity module is green.

- [X] T016 [P] [US3a] Lane B1 parser work, test-first in `tests/scripts/test_tachi_parsers.py` (W1; `senior-backend-engineer`; ~0.57 d; commits after T006).
  - **While the commit gate is closed (NM-2).** B1 develops in an isolated worktree (the Agent tool's `isolation: "worktree"`) or a scratch clone, making local commits there.
    - T020 (K11) and T024 (K13-posture) each get their own commits.
    - Once A-2's job is green, B1 replays the commits onto the branch in order. Its files have no other W1 writer, so the cherry-picks apply cleanly.
    - Fallback: start T020 only after T016's commits land. B1's float against A′ (about 0.2 d) covers the wait.
  - All in `scripts/tachi_parsers.py`, in sequence. K9, K10 and K12 are non-carvable and may share commits.
    - **K9**:
      - `normalize_header` plus `HEADER_ALIASES`;
      - the level-aware stop rule in `parse_markdown_table` (non-heading matches keep today's rule);
      - `is_placeholder_id`;
      - `parse_score`: it catches `InvalidOperation`/`ValueError`/`TypeError` and rejects non-finite values. It **returns None, and the caller counts it toward the aggregated class** (L4). `_score_to_band` uses it.
    - **K12: the full parser-side surface, so W2 only wires it (AR-3, F1, NM-1).**
      - `normalize_delta_status(s)` (N6, spelled out per L4): strip a surrounding run of backticks, `*`, `_` and whitespace; then one `[…]` pair; then the run again; then upper-case.
      - `delta_status_by_id(threats_md) -> (status_by_id, has_status_column, row_count)`: the normalized map (placeholder IDs excluded), whether Section 7 has a Status column, and its row count (F1).
      - **`compute_delta_counts(status_by_id, resolved)`**: counts NEW, UPDATED and UNCHANGED **over the normalized Section 7 map**, plus the resolved rows (FR-K12.1/K12.2; data-model §6; NM-1).
        - The same K12 commit updates both extractors' existing call sites to pass the map. B1 owns both extractors in W1, so the gated modules stay green between waves.
      - `apply_delta_status(findings, status_by_id)`: writes the normalized statuses onto a tier's findings in place (tiers 1 and 2), **only** for the per-finding badges and `top_findings[].delta_status`. It plays no part in the counts (NM-1). In W2, `_merge_delta_status` delegates to it.
      - `warn_delta_scope(has_baseline, has_status_column, status_by_id, row_count, tier_ids)`: emits PD-16's four warnings (unknown statuses; an empty map; an ID-set mismatch; a baseline run without a Status column), aggregated per class, on baseline runs only.
        - The unknown-status stem prints the normalized value, which is what the map holds (LOW-5).
      - Tier-3 `parse_threats_findings` normalizes its Status at parse.
      - `parse_resolved_findings` accepts 4b|4c through `match_heading`, skips placeholder rows, and has its docstring swept (FR-K12.5).
    - **`match_heading`**, with `start_line`.
    - **Parse-time warning aggregation per class** (R-P6).
  - Then K10 in both `scripts/extract-infographic-data.py` and `scripts/extract-report-data.py`, through `match_heading` (`^#{3,4}\s+Risk by MAESTRO Layer`).
  - **Pins** are regression tests in `test_tachi_parsers.py` (L4) for:
    - the three substring callers;
    - one `##` caller;
    - `scripts/generate-risk-scores-sarif.py`.
- [ ] T017 [US3a] Lane B2 wiring for K12 and K13.1, plus the FR-K12.5 sweep (B2a and B2b, W2; `senior-backend-engineer` in each lane; ~0.35 d).
  - **K12: both extractors make the same calls (F1, NM-1).** Each extractor:
    1. calls `delta_status_by_id`;
    2. at tiers 1 and 2, calls `apply_delta_status`, for the badges (report) and `top_findings[].delta_status` (infographic) only;
    3. calls `warn_delta_scope`, with the tier's finding IDs;
    4. on baseline runs, counts over the normalized map (FR-K12.1/K12.2), identically on both surfaces. This step has been in place since T016's K12 commit.

    Per extractor:
    - `scripts/extract-infographic-data.py` (B2a) gains the tier-1/2 merge it lacks today, so `top_findings[].delta_status` appears at tier 1.
    - `scripts/extract-report-data.py` (B2b): `_merge_delta_status` stays importable with its `(findings, threats_md)` signature, which `test_extractor_contract_fixes.py:242` calls. It delegates to `delta_status_by_id` and `apply_delta_status` (FR-K12.2). The badges use the normalized status.
  - **K13.1 (B2b), per data-model §7's per-tier table (F3, PD-19):**

    | Data tier | Finding field (cards, `findings-detail.typ:95`) | Roadmap action text | Attack-path remediation |
    |---|---|---|---|
    | 1 | `recommendation`: the analyzer recommendation, else `REC_FALLBACK_PREFIX` + the Section 7 mitigation, else `REC_PLACEHOLDER` | the finding's `recommendation` | `_get_finding_mitigation` → `recommendation` |
    | 2 | none: the card keeps its `—` default (unchanged) | today's threat text; `REC_PLACEHOLDER` only when that is empty | unchanged (`_build_remediation("")`'s generic step) |
    | 3 | `mitigation` (the only field `:2105` emits), or `REC_PLACEHOLDER` when empty | the finding's `mitigation` (`:213`), so the placeholder when empty | `_get_finding_mitigation` → `mitigation`, so the placeholder when empty |

    - The prefix fallback stays tier-1 only. Tier 2 gains no `recommendation` field.
    - The Section 4 drift warning (tier 1).
  - **The sweep** (B2b) of the remaining 4b→4c sites:
    - `.claude/skills/tachi-orchestration/references/output-schemas.md:173,275`;
    - `.claude/agents/tachi/report-assembler.md:242`;
    - `templates/tachi/output-schemas/threat-report.md:57,207,298,303,314`;
    - `scripts/extract-report-data.py:2202`;
    - `docs/architecture/01_system_design/README.md:2077`;
    - `docs/architecture/00_Tech_Stack/README.md:130,200,234`.

    Record per-occurrence dispositions in `specs/373-adopter-install-output-fidelity/sweep-4b-ledger.md`.
- [ ] T018 [P] [US3a] FR-K9.3: `.claude/commands/tachi.infographic.md` explicit-path detection accepts `Residual Score` or `Residual` (Lane C2, W2; `senior-backend-engineer`; ~0.02 d).
- [ ] T019 [US3a] US-3a regression tests and sibling parity (the test lane, W2; `senior-backend-engineer`; ~0.34 d).
  - In `tests/scripts/test_extract_infographic_data.py`, `test_extract_report_data.py` and `test_extractor_contract_fixes.py`:
    - **K9**: short-form headers with an empty Critical band; an empty last band before Summary Statistics yields 0 phantom rows;
    - **K10**: `###` equals `####` on both extractors;
    - **K12**:
      - exact `4c` baseline counts; `4b` legacy;
      - bracketed statuses (`[NEW]`, `**[NEW]**`, `` `[NEW]` ``);
      - a Status-less non-baseline run with no warning; the ID-set warning's scope;
      - the map/tier ID-mismatch fixture (F1, NM-1): both surfaces report the **Section 7 tallies** as absolute values (the counts of the normalized map, not of the tier's findings), and each emits one ID-set warning;
    - **K13.1, per data tier (F3)**:
      - tier 1: a partial Section 4 gives prefix and placeholder text identical across the three consumers; a drifted Section 4 warns;
      - tier 2: the card and the attack path are unchanged, and the placeholder appears only for an empty roadmap text;
      - tier 3: an empty `mitigation` becomes the placeholder on the card, the roadmap and the attack path.
  - Create `tests/scripts/test_extraction_sibling_parity.py`. It compares:
    - posture;
    - severity counts;
    - delta counts, including the bracketed and ID-mismatch baselines;
    - MAESTRO;
    - the K11 join path: on the Inherent-less controls fixture with a `risk-scores.md`, the clamp, the residual bands, the severity counts and the posture agree on both surfaces (F2). This case belongs to K11's carve unit and lands in its own K11 commit.
  - Lane A's W2 wiring commit adds the parity module to `extraction-fidelity`. Its fixture trees are already in `paths:` since A-2 (C-1).
  - A11 (the FR-K9.3 detection text) goes in `tests/scripts/test_gemini_request_contract.py`.

**Checkpoint**: US-3a is green in the fast workflow. SC-4's K9, K10, K12 and K13.1 clauses hold.

---

## Phase 7: User Story 3b: The risk funnel narrows by risk volume (P3, split-valve candidate; TW-0 second, TW-1)

**Goal**: D-2 over one row set, with:
- deterministic widths (STEP = 10, FLOOR = 30);
- volume reductions;
- row-derived totals on the funnel **and** the baseball card (S-9);
- null semantics.

**K11 carve unit** (plan, extended by this revision):
- T020–T023, including T020's join wiring at both tier-1 call sites (F2);
- K11's text and caption, including T022's S-9 null sites (L11);
- the join-path parity case in T019;
- notice 4;
- K11's golden commit in T032 (the funnel and baseball-card goldens).

If K11 is carved, the parser keeps today's unclamped residuals and substring idiom, while `parse_score` still serves K9. At T039, the carve is a revert of T020's own commits, which B1 makes.

**Independent Test**: the STEP-bound and strong-reduction fixtures produce hand-computed volumes, mixes, widths and reductions. The 3-tier, threats-only and volumes-unavailable shapes match `contracts/extraction-data-contract.md`.

- [X] T020 [US3b] K11 parser and join wiring, Lane B1 step 3 (W1, after T016; `senior-backend-engineer`; ~0.30 d). In `scripts/tachi_parsers.py`, with unit tests in `tests/scripts/test_tachi_parsers.py`, per data-model §3 (L18):
  - **The inherent read** (`Inherent Score`/`Inherent`), filled by ID join to the risk-scores composites through a new input, `parse_compensating_controls_md(content, composites_by_id=None)`. The composites come from `parse_risk_scores_findings` (`composite_score` through `parse_score`) (F2).
  - **Both tier-1 call sites, wired in W1** (B1 owns both extractors in W1):
    - `extract_severity` in `scripts/extract-infographic-data.py` (`:266`) passes composites from the `rs_content` it already reads;
    - `scripts/extract-report-data.py` (`:2229`) reads `risk-scores.md` at tier 1 when it is present, and passes them. Today it reads that file only at tier 2 (`:2236`).
  - **`classify_control_status`**:
    - whole tokens, `partial` as a prefix, the negation tokens `no`/`not`/`none`/`nothing`, and the recognized no-control set;
    - it classifies each row once, and replaces both row idioms (`:1202-1208`, `:1253-1260`);
    - the Section 1 summary reader keeps its own matching.
  - **The residual**:
    - clamped to at most inherent, once, at parse, with an aggregated warning;
    - a missing residual with an inherent present means residual = inherent (no credit), with a warning;
    - the band fallbacks follow data-model §3.
  - **T020's commits stand alone**: no other K-item shares them, so T039 can revert them (NM-2).
- [ ] T021 [US3b] K11 funnel and S-9 in `scripts/extract-infographic-data.py` (Lane B2a, W2; `senior-backend-engineer`; ~0.45 d). Per data-model §4.1–§4.4 (L18):
  - `compute_risk_funnel`:
    - four tier objects with `ghost`;
    - Decimal volumes (1 dp, half-up) and integer severity mixes;
    - widths per FR-K11.5 (Decimal clamp bounds, then round half-up);
    - three reductions derived from the emitted volumes;
    - `risk_reduction` computed once.
  - Volumes are unavailable when no row carries an inherent score, or when V2 = 0. The funnel and the baseball card then both get nulls, and the one volumes-unavailable warning is emitted.
  - Reductions:
    - (0→1) is `0.0` when JSON tier 1 is real, and `null` under a ghost;
    - a zero denominator with volumes available gives `0.0`;
    - 3-tier mode labels JSON tier 2 "Unmitigated Risk".
  - Warnings: the Section 1 comparand (> 0.1) and the row count.
  - The baseball card's `risk_reduction`, `inherent_score` and `residual_score` take the row-derived values.
  - Align the funnel `source` strings with the one-row-set wording (N13).
- [ ] T022 [P] [US3b] K11 text (Lane C2 in W2, plus the caption from Lane B2b; `senior-backend-engineer` in each lane; ~0.14 d).
  - `templates/tachi/infographics/infographic-risk-funnel.md`:
    - tier blocks and the width rule keyed on `ghost`;
    - the Tier 2 one-row-set line;
    - the "0% risk reduction" note keyed on a numeric 0.0;
    - the nominal ~75/50/30% headings removed;
    - the sidebar's Risk Reduction line (`:157`) renders a `null` as "not available" (L11).
  - `.claude/skills/tachi-infographics/references/template-specific-formats.md:64-69,124,128`, plus (L11):
    - `:23`: the baseball card's Risk Reduction is row-derived under S-9, not "from the Executive Summary", and a `null` renders "not available";
    - `:79` and `:95`: the funnel table's Risk Reduction row and its definition. It is the row-derived Tier 2→4 volume reduction, "not available" when `null`.
  - B2b edits `templates/tachi/security-report/main.typ:292`: the caption, with the R-P5 clause.
- [ ] T023 [US3b] K11 tests (the test lane, W2; `senior-backend-engineer`; ~0.20 d). In `tests/scripts/test_extract_infographic_data.py`:
  - STEP-bound (100/90/80/70) and strong-reduction (FLOOR-bound) widths;
  - the 3-tier, threats-only and volumes-unavailable shapes;
  - statuses `Missing` (silent), empty or unrecognized (warns), `Partially Found` (partial), `None found` (none);
  - the clamp, Section 1 and row-count warnings;
  - the Inherent-less join-path fixture: its volumes come from the joined composites;
  - baseball-card and funnel parity on `risk_reduction` and the totals;
  - reductions that are never negative.

**Checkpoint**: US-3b is green. SC-4's funnel clause holds.

---

## Phase 8: User Story 3c: One posture label on every surface (P3, split-valve candidate; TW-0 third, TW-2)

**Goal**: D-3's single rubric (the highest band present).
- It is emitted as a level and a label into both surfaces.
- It is rendered verbatim, with color taken from the level.
- It fails loudly on stale data.

**K13-posture carve unit**: T024–T026, the `report-posture` job wiring, K13's golden commit in T032, and notice 5. Each of these lands in K13-posture-only commits.

**Independent Test**: the same run directory gives identical posture fields in the JSON and `report-data.typ`. A stale `report-data.typ` panics with the regenerate message in CI.

- [X] T024 [US3c] Posture function, Lane B1 step 4 (W1, after T020 or T016; `senior-backend-engineer`; ~0.05 d): `compute_risk_posture(counts) -> (level, label)` in `scripts/tachi_parsers.py`, with unit tests, in its own commit.
  - Zero findings give `low`/`LOW RISK`.
  - It runs on post-clamp counts when K11 ships, and on today's counts if K11 is carved.
- [ ] T025 [US3c] Posture emission, Typst and the stale-data gate (Lane B2a and B2b in W2, with Lane A wiring; `senior-backend-engineer` in B2a and in B2b; `devops` for the job; ~0.32 d).
  - **Emission**:
    - `metadata.risk_posture_{level,label}` in every infographic JSON, including executive-architecture through its early-exit builder in `scripts/extract-infographic-data.py`;
    - `#let risk-posture-level` and `#let risk-posture-label` after the severity counts in `scripts/extract-report-data.py`.
  - **Typst**:
    - `templates/tachi/security-report/cover.typ` takes the label and level from data, with color from the level, and its own derivation removed;
    - the `main.typ` guard between `:117` and `:147` (the panic message from the contract);
    - `.claude/skills/tachi-report-assembly/references/typst-template-contract.md` gets the REQUIRED/no-default note scoped to the posture variables;
    - `.claude/agents/tachi/report-assembler.md:184` gets the deprecation-note line.
  - **The stale-data gate** (L12): B2b creates `tests/scripts/test_report_posture_contract.py`. The stale file panics, and the positive control has no panic text.
    - It generates the fresh `report-data.typ` from an mmdc-free T003 fixture, never from `examples/`. If it needs a dedicated fixture, B2b owns the `tests/scripts/fixtures/fidelity_373/posture/` subdirectory in W2 (LOW-9).
    - It compiles against a `tmp_path` copy of `templates/tachi/security-report/`.
    - Do not reuse the existing stale-data harness's in-tree steps. That harness runs the extractor on `examples/web-app` and swaps `report-data.typ` inside the template directory.
  - Lane A's W2 wiring adds the `report-posture` job (`typst-community/setup-typst@v5`, `TACHI_REQUIRE_TYPST=1`), in its own K13-posture commit. It is **never in W1**, and it isn't added at all if K13-posture is carved.
- [ ] T026 [P] [US3c] Posture text (Lane C2, W2; `senior-backend-engineer`; ~0.10 d).
  - `templates/tachi/infographics/infographic-baseball-card.md`: the badge shows the label alone; the prompt; the ">20% of findings" rubric deleted.
  - `.claude/skills/tachi-infographics/references/gemini-prompt-construction.md:296`.
  - `templates/tachi/infographics/INFOGRAPHIC_TEMPLATES.md:108-109` placeholders.
  - `.claude/skills/tachi-infographics/references/infographic-specifications.md:53,171`.
  - `.claude/agents/tachi/threat-infographic.md:206`, the JSON contract.
  - `schemas/infographic.yaml:51`: the posture fields.

**Checkpoint**: US-3c is green, including the `report-posture` job.

---

## Phase 9: User Story 4b: Rendered images carry no leaked prompt text or wrong IDs (P3, split-valve candidate; TW-0 first, TW-3, TW-5, TW-6)

**Goal**: the layout-label and allow-list instructions in every prompt, inside the scaffold contract. The extractor emits the allow-list, and executive-architecture gets the PD-2 amendment.

**K15 carve unit**:
- T027–T030;
- A9 and A10 (T029). A10 is meaningful only after T028;
- K15's golden commit in T032;
- SC-5's leakage and allow-list clauses.

When it can be carved:
- at T039, at no cost, because no K15 work has landed yet;
- in W3, only through TW-6, using T030's late-carve procedure.

**Independent Test**:
- A9–A11 are green;
- one live render per template shows no layout-label text and no ID outside its allow-list, within two iterations.

- [ ] T027 [US4b] Allow-list emission in `scripts/extract-infographic-data.py` (Lane B2a, W2; `senior-backend-engineer`; ~0.15 d).
  - `compute_allow_list`, per PD-17 and data-model §8:
    - per-template `finding_ids`: the full set for baseball-card and system-architecture, per-layer IDs for maestro-stack, none for the funnel and heatmap, and callouts for executive-architecture;
    - one common `component_names`;
    - sorted and unique.
  - Emitted as the top-level `allow_list`, including executive-architecture through its early-exit builder.
  - Keep the `allow_list` lines apart from T025's posture lines in `_build_executive_architecture_payload` and `build_json_output`: separate commits, and non-adjacent lines where possible. A TW-6 revert of T027 then applies cleanly; otherwise the W3 writer resolves it by hand (LOW-4).
  - AR-3 supersedes the extraction contract's listing of `compute_allow_list` under `tachi_parsers.py`. It lives in `extract-infographic-data.py` (L3).
- [ ] T028 [US4b] K15 prompt hardening (Lane C2, W2; `senior-backend-engineer`; ~0.25 d).
  - **The five scaffolded templates' preambles and the reference prompt**: the final layout-label sentence and the allow-list rule (PD-17 wording).
    - They go between `IMPORTANT:` and `STYLING DIRECTIVES`, within the scaffold rules: no preamble line starting `FOOTER`, no early marker text, no extra fence.
    - Keep each K15 sentence on one unwrapped line, so no wrapped line starts with `FOOTER` (L14).
  - **The agent's `ALLOWED IDS AND NAMES` line**: only for the five scaffolded templates and the reference path (N10).
  - **Executive-architecture** (`.claude/skills/tachi-infographics/references/executive-architecture.md`): the one-paragraph PD-2 amendment inside the lock, after IMPORTANT. It meets all nine conditions, including: markers unchanged, no fence or slot, the region variant, generic labels.
  - **The lock rule** in `gemini-prompt-construction.md` gets the dated "Amended by F-373 K15" note, which reconciles the header list (FLOW EDGES, CLUSTERS) and the slot list (7).
  - **The agent's executive-architecture section** (`.claude/agents/tachi/threat-infographic.md:260-272`) defers to the verbatim block and drops its contradicting lines.
- [ ] T029 [US4b] K15 static assertions (the test lane, W2; `senior-backend-engineer`; ~0.10 d). Add A9 and A10 to `tests/scripts/test_gemini_request_contract.py`:
  - **A9**:
    - the K15 text sits between IMPORTANT and STYLING DIRECTIVES in each scaffolded preamble, the reference and the executive-architecture block;
    - executive-architecture carries its region variant;
    - the agent text instructs writing the `ALLOWED IDS AND NAMES` line from `allow_list`, for the five scaffolded templates and the reference path;
    - an N10 negative: the agent's executive-architecture section does not instruct that line (L13).
  - **A10**: the lock markers are byte-identical, `flow_edges` and `clusters` are present, and the amendment note exists.
    - The strip rule is applied **verbatim**: split on blank lines between the markers, drop the paragraph after `IMPORTANT:`, and assert that the SHA-256 of the rest equals the pinned pre-change value.
    - The pin is the SHA-256 of the block at `63438d7`, from the character after the BEGIN line's newline to the END marker, split and re-joined on `"\n\n"` (L13).
- [ ] T030 [US4b] K15 live renders (W3; `tester` renders, judges and records, with the maintainer's visual check; the W3 writer, a `senior-backend-engineer`, makes the text iterations and any TW-6 revert; ~0.35 d). `[MANUAL-ONLY] non-deterministic image output needs a live key and a human visual check`
  - Render once per template (all six, executive-architecture in portrait) through the agent. This runs in a scratch clone of the W3 commit, on a scratch copy of `examples/maestro-reference/` (`quickstart.md` §4), as part of T015's render session.
  - Record results in the PR body and in `specs/373-adopter-install-output-fidelity/test-results/k15-renders.md`.
  - Check for layout-label text, and for IDs outside `allow_list` and the legend. Watch the length of the allow-list line on large lists (N10).
  - At most two prompt iterations (TW-5). Residual leakage goes to a pre-decided follow-up issue (export `AOD_REPO` before filing).
  - **If an iteration changes prompt text**, the W3 writer edits it, re-runs T032 for the scaffolded goldens, and re-pushes through T034 (L7).
  - **Late carve (TW-6: renders blocked for more than half a day).** No unverified K15 text ships (RC-T2, F4). The W3 writer:
    1. reverts K15's named commits: T027, T028, T029, and any T030 iteration commits (LOW-4). At the decision, the architect says whether T028's agent-section deferral stays as a routing fix; by default it is reverted with the rest;
    2. re-runs T032 for the surviving K-items. K15's golden authorization lapses (SC-8);
    3. hands back to the `tester`: T015 renders all six templates under P-10.2 (b) once renders resume, or records K14 under P-9.2 and P-10.1;
    4. moves SC-5's leakage and allow-list clauses to K15's follow-up issue (spec R-c; export `AOD_REPO`);
    5. re-pushes through T034.

**Checkpoint**: US-4b is statically green in W2 and live-verified in W3, or carved per the trip-wires.

---

## Phase 10: User Story 6: The FR-012b form-drift guard is test-covered (P3, drop-able; TW-4)

**Goal**: #370's recipe, retargeted to today's code, with no behavior change.
- Commit `3d67ca7` moved the FR-012b guard out of `classify_framework_items`.
- It is now `_warn_unmatched_attribution_refs(findings, framework_name, catalog_ids)` (`extract-report-data.py:1174`), called from `build_per_framework_aggregates` (`:1287`).

**Independent Test**: both cases pass on the current guard and fail if its warning or its "never misreported" promise regresses.

- [ ] T031 [US6] #370 (the test lane and Lane B2b, W2; `senior-backend-engineer` in each; ~0.15 d).
  - **Tests**, in `tests/scripts/test_extract_report_data.py`:
    - **Case 1**: `_warn_unmatched_attribution_refs`, given a stale-form attribution ID (`{taxonomy: owasp, id: "LLM05:2025"}`), warns on stderr (`capsys`).
      - `classify_framework_items` returns identical items with and without that reference.
      - The guard leaves `findings` deep-equal before and after the call (LOW-7).
    - **Case 2**: through `build_per_framework_aggregates` with the **real** catalogs (OQ-5, closed by the team-lead), a finding citing `{taxonomy: mitre-attack, id: "T1070.001"}` is not reported as unmatched.
      - `T1070.001` is `out_of_scope: true` at `schemas/taxonomy/mitre-attack.yaml:982-988`.
      - The promise now belongs to the caller, which passes the full-catalog ID set, so only an end-to-end call pins it.
      - `schemas/taxonomy/*.yaml` is in `paths:` since A-2 (T006).
  - **Docstring** (B2b), on `_warn_unmatched_attribution_refs` in `scripts/extract-report-data.py`: document that the caller skips the guard for a framework whose in-scope count is 0 (`:1310-1311`).
    - Do not soften "never raises". Since `3d67ca7` the guard does no catalog I/O, so the claim is true.
  - The recipe is now 2 tests and 1 note. Drop the item entirely if it outgrows that (TW-4).

---

## Phase 11: Polish & Cross-Cutting Concerns (end of W2, W3, W4)

- [ ] T032 Golden regeneration, the test lane's wave-final W2 commits (`senior-backend-engineer`; ~0.14 d). In W3, the W3 writer re-runs it.
  - The five goldens in `tests/scripts/fixtures/golden/`, authorized by name (SC-8, R-7):
    - `risk-funnel.json` and `baseball-card.json`: K11's funnel and S-9 fields (the baseball card only while K11 ships, P-9.5);
    - `baseball-card.json`, `maestro-heatmap.json`, `maestro-stack.json`, `risk-funnel.json` and `system-architecture.json`: K13's posture fields, which every JSON gains;
    - the same five: K15's `prompt_scaffold` text and `allow_list`.
  - **One commit per K-item**, split by field class (K11, then K13, then K15), so a later carve can revert one. After any carve, re-run this task for the surviving K-items rather than relying on a clean revert (F4).
  - Regenerate in a scratch clone with the fixture command in `quickstart.md` §5. Copy back only the authorized files, and run `git status --short` afterward (L10). Attribute each hunk to one K-item.
- [ ] T033 Architect P0 checkpoint, N4 re-run, TW-7 ruling and session handoff, at the end of W2 (`architect` for the checkpoint; `tester` for the re-run; the `orchestrator` invokes the team-lead's TW-7 ruling; ~0.13 d).
  - **The architect** reviews:
    - the parser semantics, the goldens by file name, and the oracle attribution rules;
    - the W0 "other status" record (AR-2), amending the walk set if needed.
  - **N4 re-run (C-2, R-8)**: the tester re-runs the roughly 20 ungated parser- and extractor-consuming modules in the scratch clone, and the architect attributes any delta against T001. B1's stop-rule change landed in W1, and this is the last gate before the session break.
  - **TW-7**, with the actuals: Group A ships early through T040 if either of these holds:
    - the remaining projected work exceeds 2.0 d;
    - any lane is more than 50% over its budget (§ Trip-Wire Evaluation).

    TW-7 carves nothing. From T033 on, K15 is carved only through TW-6, and TW-5 caps its iterations (F4 (e), LOW-10).
  - Write `specs/373-adopter-install-output-fidelity/NEXT-SESSION.md`.
- [ ] T034 W3 integration (Lane A; `devops`; ~0.20 d).
  - Commit and push. The render session (T030 → T015) starts from this commit in a scratch clone while CI runs (L7).
  - Before T036's architect checkpoint, these must be **visibly** green on #375:
    - every fast-workflow job (`manifest-completeness`, `extraction-fidelity`, and `report-posture` if K13-posture ships);
    - both `tachi-pytest.yml` legs.
  - The co-fired gates `tachi-mmdc-preflight`, `tachi-catalog-drift` and `tachi-maestro-coverage` must be green.
  - Re-run the N4 ungated modules in a scratch clone and attribute any delta against T001.
- [ ] T035 Oracle post-snapshot and attribution (W3, after the render session's last text change and any T032 re-run; `senior-backend-engineer`; ~0.20 d).
  - Repeat T001's snapshot, stderr included, then diff.
  - Write `specs/373-adopter-install-output-fidelity/oracle-diff.md`, grouped **by field class × K-item with per-example counts** (not one row per field).
  - The expected movers (L8):
    - K10: none among the tracked examples;
    - the M5 fallback examples (K13.1);
    - **K12** (NM-1; figures from the architect's re-review §3):
      - `agentic-app/sample-report` (tier 1) goes to **4 NEW / 0 UPDATED / 82 UNCHANGED**, with one ID-set warning (`T-1` is in Section 7 but not in the controls report);
      - `agentic-app` (tier 3) goes to **12 NEW / 69 UNCHANGED**;
      - the badges change;
      - the infographic's `top_findings[].delta_status` is normalized at tier 3 and newly present at tier 1;
    - K11's funnel fields and S-9's baseball-card fields;
    - the posture fields and `allow_list` everywhere, and the `prompt_scaffold` text (K11, K13, K15);
    - warnings: the new aggregated classes, and `has_baseline`'s stateless false positive (N7), attributed from stderr.
  - 100% attributed. No PDF baseline or tracked PNG changes.
- [ ] T036 Code review and the W3 architect checkpoint (`code-reviewer`, then `architect`; ~0.15 d).
  - `code-reviewer` reviews the full diff against the contracts, NFR-2, NFR-3, NFR-5 and NFR-8, scoped to executable code (standing rules). The result goes in `.aod/results/code-reviewer-373.md`.
    - It may start at the W3 commit, and it ends with a delta look at any iteration diff.
  - **Any Python or Typst fix** that T035's attribution or this review requires is made by the W3 writer (a `senior-backend-engineer`), after the render session. Re-run T032 or T035 if an output changes (LOW-8).
  - Then the architect's W3 checkpoint, after T035. It confirms that N8 (T014) and N11 (T009) landed as decided in W1.
- [ ] T037 W4 close-out docs (Lane A and Lane B docs; `senior-backend-engineer`, with `architect` for the ADR-014 note; ~0.15 d).
  - Add the dated F-373 note to `docs/architecture/02_ADRs/ADR-014-gemini-api-optional-image-generation.md`: the GA chain, the 404/403 walk, the loud non-blocking 400 (PD-15). The architect writes it.
  - Docs sweep of the README and developer-guide install sections.
  - `CHANGELOG.md` `Unreleased` prose carrying PD-7's applicable notices.
  - **The PR body** (R-T1):
    - the changed examples (from T035);
    - the 4b ledger;
    - the live-render records (T015, T030) and the W0 smoke record;
    - the golden authorization list;
    - the trip-wire outcomes (TW-0 to TW-7), with each carved item's follow-up issue and the SC clauses that moved with it;
    - PD-8 described as #365-adjacent;
    - "Closes #373", and "Closes #370" when #370 is folded in;
    - confirmation that the title is `fix(373): …`.
  - **Draft the #364 handoff comment** (R-T2): the example data surfaces that changed, from `oracle-diff.md`. Those are:
    - the K13.1 fallback examples;
    - `agentic-app`'s K12 delta counts and badges;
    - the posture and `allow_list` fields;
    - the funnel fields.

    K10 moves no tracked example. Keep it generic per NFR-6.
- [ ] T038 Release-notes text (W4; `product-manager`; ~0.05 d).
  - Write `specs/373-adopter-install-output-fidelity/release-notes-upgrading.md` with PD-7's seven conditional notices, generic per NFR-6:
    - the update-and-re-run notice, naming the three skills and the populator;
    - the D-1 note, in P-11.1's wording: "broken, looping or wrong-type links, links nested inside an installed folder, and destinations inside the tachi source clone";
    - M5;
    - K11 (conditional);
    - K13-posture stale data (conditional);
    - statically verified only (conditional);
    - replace the link (conditional).
  - **If TW-7 fired (T040)**, this file covers the main release only (P-11.2).
    - It carries notices 3 to 6 as applicable, plus notice 2 if K3 did not ride early.
    - It opens with the line "Update your tachi clone and re-run `install.sh` to pick up these fixes."
  - It is used at deliver, in this order:
    1. any polish run;
    2. an edit of the release-please PR body before merge;
    3. the post-publish `gh release edit` backstop;
    4. a `gh release view` check.

---

## Phase 12: Trip-wire checkpoint and the conditional TW-7 path

T039 runs at W1 exit. T040 runs at the end of Session 1, and only if TW-7 fires. They are listed last so that the reviewed task IDs T001–T038 stay stable.

- [X] T039 W1-exit trip-wire checkpoint and snapshot (W1 exit, before any W2 task starts; the `orchestrator` invokes the team-lead's ruling; `senior-backend-engineer` (B1) makes any revert it orders; ~0.03 d).
  - **Re-run TW-0** with the actual durations of W0 and W1, and W2–W4 as planned (§ Trip-Wire Evaluation).
    - It fires if W0 and W1 together took more than about 2.0 working days (planned: 1.75).
    - For a build that starts Monday 09-28, that means W1 is still open at the start of Wednesday 09-30.
  - **Re-run TW-1 and TW-2** with the actuals of T020 and T024:
    - K11 fires if T020 took more than about 0.36 d;
    - K13-posture fires if T024 took more than about 0.15 d.
  - **Carve in the fixed order** (K15 → K11 → K13-posture) until TW-0 fits:
    - **K15** costs nothing here, because none of its work has landed. T015 then renders all six templates (P-10.2 (b)), and A9/A10 are not written.
    - **K11** costs a revert of T020's own commits (the parser step and the join wiring). T024 then runs on today's counts.
    - **K13-posture** costs a revert of T024's commit.
  - **Reverts (NM-2).** B1 makes them, as the W1 writer of `tachi_parsers.py` and both extractors. It verifies each in a scratch clone of the revert commit before any W2 lane edits those files, so AR-3 holds.
  - **W2 launches only after this ruling and any revert it orders.** T039 gates every W2 task (NM-2).
  - The rule, threshold and order are PRD §10's. This task only adds a second evaluation point, with actuals (team-lead R-3; architect F4 (b)). The PM's acceptance of that placement is recorded separately (LOW-10).
  - Record the ruling in `specs/373-adopter-install-output-fidelity/test-results/w1-exit-checkpoint.md`. Write a NEXT-SESSION snapshot, so Session 1 can break here at no cost if the orchestrator's context runs short.
- [ ] T040 Early Group A PR and release, **conditional: only if TW-7 fires at T033** (end of Session 1; `devops` for the branch, CI and merge; `tester` for the render set if K14 rides; `product-manager` for the notices; ~0.25 d, plus ~0.25 d if K14 rides; outside the central estimate).
  - If TW-7 does not fire, mark this task `[X]` with the note "not triggered (TW-7 did not fire at T033)".
  - **Work in its own worktree** (LOW-3). KB Entry 18's `git checkout -B main origin/main` would otherwise switch the shared tree off the feature branch.
  - **Composition (RC-T1 (a); C-3):** a branch from `main` with these commits cherry-picked:
    - A-1 (T004–T005);
    - K3's commits, only if K3 is green on both legs:
      - T003's sandbox-builder commit, because `install_sh_helpers.py` does not exist on `main` (LOW-3);
      - T010's lock-step commit and its convergence fixes (T008–T011);
    - A-2 (T006): required if K14 rides (N9); otherwise optional, once its pre-existing-red triage is closed;
    - A-3 (T014) with C1's commits (T012–T013), only if K14 rides. A-3 never goes without C1.
  - **K14 rides only under P-9.1's three conditions (RC-T1 (b)):**
    1. its static test is green;
    2. P-10.4's full render set is made from this branch's own code: each template once, each chain model at least once, and executive-architecture on one portrait PDF page. The tester runs it per `quickstart.md` §4;
    3. its commits separate cleanly from the K13 and K15 edits, which the own-commit rule for carvable and early-ship items ensures.

    If both models are blocked, K14 does not ride.
  - **Deliver it with its own notices (RC-T1 (c), P-11.2):**
    - The PM writes notice 1, notice 2 if K3 rides (otherwise notice 7), and notice 6 if K14 rides with a model recorded as statically verified only.
    - PD-7's mechanism applies:
      - the release-PR body edit, as the last action before the merge;
      - the post-publish `gh release edit` backstop;
      - any polish run first;
      - a `gh release view` check.
    - Before merging, apply KB Entry 18: the branch is current, and local `main` equals `origin/main`.
    - Squash-merge as `fix(373): …`. Then verify that the release-please patch PR opens within about 30 s, or push a `fix(373):` marker commit.
  - **Afterwards**, bring #375 up to date with `main`: merge `main` into the branch; the final squash flattens it.
    - Expect conflicts where release-please bumped the version at `install.sh:13,19,43` (in the header that T009 rewrites) and at README `:120`/`:471`. Keep K3's text with the new version (LOW-3).
    - T038 then covers the main release.

---

## Dependencies & Execution Order

### Phase dependencies

- **Setup (T001–T003)** has no dependencies.
  - T002 must finish before T012 and T013 (`IMAGE_SIZE_RESTORED`, the provenance dates, the 3:4 check).
  - T003 must finish before the story tests.
- **The W1 launch rule (R-1).** All four W1 lanes (A, A′, B1, C1) launch at the start of W1. Only their commits are gated:
  - **Nothing else commits before A-1 (T004 → T005) is green.**
  - A′ and C1 commit after A-1 is green.
  - B1 commits after A-2 (T006) is committed and its job is green. The one exception is B1's marker-only first commit (LOW-6).
  - While its gate is closed, B1 keeps T020 and T024 separable, following T016's worktree rule (NM-2).
  - A-3 (the T014 wiring) lands last in W1.
  - Each lane verifies its commits in a scratch clone of its local commit (standing rules).
- **Foundational**:
  - T006 (A-2) lands immediately after A-1 and before any Lane B1 commit.
  - T007 lands before any prompt-text edit (T022, T026, T028).
  - T013 edits only the configuration fences after the prompt fence, so it may land before T007 when T007 is held only by A-2's triage.
- **US-2** (T008 → T009 → T010 → T011) depends only on A-1.
  - T008 to T010 land as one lock-step commit (L16).
  - It is Lane A′ in W1 and Lane A in W2.
- **US-4a**:
  - T012 ∥ T013 → T014 (A-3), in W1.
  - T015 in W3, in the render session that starts from T034's commit. Under a K15 carve, it renders all six templates.
- **US-3a**: T016 (W1, after T006) → T039 → T017 and T019 (W2). T018 is independent (C2, W2).
- **US-3b**: T020 (W1, after T016) → T039 → T021, T022 and T023 (W2).
- **US-3c**: T024 (W1, after T020, or after T016 if K11 is carved) → T039 → T025 and T026 (W2).
- **US-4b**: T039 → T027 and T028 (W2; T028 also after T007) → T029 (W2) → T030 (W3).
- **US-6**: T039 → T031 (W2).
- **Checkpoints**:
  - T039 runs when W1's last lane closes, and **it gates every W2 task**. W2 launches after its ruling and any revert B1 makes (NM-2).
  - T033 ends W2 and Session 1.
  - T040 runs only if T033 fires TW-7.
- **Polish**:
  - T032 is wave-final in W2, after every W2 lane; then T033.
  - W3: T034 → the render session (T030 → T015, then T032 again if text changed) → T035 → T036. T036's code review may start from T034's commit.
  - W4: T037 ∥ T038.

### Lane / file ownership per wave

Plan § "Lane and file ownership per wave" is normative. In summary:
- Lane A owns every fast-workflow edit (A-1, A-2, A-3 and the W2 wiring commits).
- Lane A′ owns `scripts/install.sh`, the installer tests, the helper and `tachi-pytest.yml` in W1.
- Lane B1 is the **only** writer of `tachi_parsers.py` (W1; it has no W2 writer, AR-3), and the only writer of both extractors in W1. It also makes any revert T039 orders, at W1 exit (NM-2).
- In W2, B2a owns `extract-infographic-data.py`. B2b owns `extract-report-data.py`, the Typst templates, the Typst contract, the report-assembler text and the sweep. If T025 needs its own fixture, B2b owns the `fidelity_373/posture/` subdirectory (LOW-9).
- Lane C (C1 in W1, C2 in W2) owns every infographic text surface, the infographic agent and command, `schemas/infographic.yaml` and the adapter copy.
- **The test lane** (the plan's "tester" rows) owns the extraction regression modules, the fixtures and the goldens from W2. A `senior-backend-engineer` instance writes it (§ Standing rules, "Agent types").
- **In W3, one `senior-backend-engineer` instance, the W3 writer, is the single writer of** (R-5, L9, LOW-8):
  - the infographic text and the adapter copy;
  - `test_gemini_request_contract.py`;
  - the goldens;
  - any Python or Typst fix.

  That covers the 2K flip (T015), the K15 iterations and a TW-6 revert (T030), the T032 re-runs, and the fixes that T035 or T036 require.
  - The `tester` renders, judges and records, and edits no product file.
  - Lane A (`devops`) writes only CI and convergence files.
  - T035 writes only `oracle-diff.md`.
- A W1 triage quarantine marker follows T006:
  - `devops` places it in the modules with no other W1 writer, and in `test_extract_report_data.py`;
  - B1 places it in `test_tachi_parsers.py`, as its marker-only first commit.

### Critical path

1. W0 (T003).
2. The A-1 gate.
3. Lane A′, the W1 pacer: T008 → T009 → T010's lock-step commit.
4. T039, plus any revert.
5. W2: B2a (T021, T025 emission, T027) and the test lane's tests (T019, T023, T029, T031).
6. The goldens (T032), then T033.
7. The session break.
8. T034, then the render session (T030 → T015), then T032 if text changed.
9. T035, then T036.
10. Close-out (T037, T038), then `/aod.deliver`.

- **Near-critical**: B1 (T007 → T016 → T020 → T024), about 0.2 d behind A′.
  - K3's ~25-min macOS CI cycles run in W2 (convergence) with about 0.5 d of float to T034. They consume it only at the ceiling (4+ cycles plus a GNU rework), and K3 then becomes critical (feasibility C-1).
- **T039 synchronizes the W1→W2 boundary**, so the dependency graph and the hard-wave TW-0 model coincide there.

### Parallel opportunities

- **W0**: T001 ∥ T002 ∥ T003.
- **W1**, from the start of the wave, with commits gated as above:
  - Lane A: T004 → T005 → T006, then A-3;
  - Lane A′: T008 test-first, then T009, then T010's commit;
  - Lane B1, in its own worktree: T007, T016 → T020 → T024;
  - Lane C1: T012 ∥ T013 → T014.
- **W1 exit**: T039, plus any revert B1 makes.
- **W2**, after T039:
  - Lane A: T010 convergence, T011 and the wiring commits;
  - B2a: T017's part, T025's emission, T021 and T027;
  - B2b: T017, T025's Typst part, T031's docstring and the T022 caption;
  - C2: T018, T026, T022 and T028;
  - the test lane: T019, T023, T029 and T031's tests.

  That is four heavy lanes plus Lane A in the background, the solo-curator cap. Then T032 and T033.
- **W3**: T034 → the render session (T030 → T015), with T036's code review alongside → T032 if text changed → T035 → T036's architect checkpoint.
- **W4**: T037 ∥ T038.

## Parallel Example: W1 from the start of the wave

```bash
# Launch all four W1 lanes together. Only commits are gated (A-1 green → A-2 → the rest → A-3).
Task: "T004 → T005 (A-1: commit, verify in a scratch clone, push, green on #375) → T006 (A-2)"                  # Lane A (senior-backend-engineer + devops)
Task: "T008 test-first (record the local red run) → T009 → T010 one lock-step commit, pushed after A-1 is green"   # Lane A′ (senior-backend-engineer + devops)
Task: "own worktree: T007, T016, then T020 and T024 as stand-alone commits; replay after A-2 is green"           # Lane B1 (senior-backend-engineer)
Task: "T012 ∥ T013 → T014's module; commits after A-1 is green"                                                # Lane C1 (senior-backend-engineer)
```

## Trip-Wire Evaluation (the team-lead rules at sign-off)

**Source**: `.aod/results/team-lead-373-tasks.md` (the sign-off review), updated for revisions 1 and 2.

### Re-cost (attention-days)

- **Effort**: the per-task figures above sum to **≈ 8.3 d** (floor 6.5, ceiling 12.9).
  - The comparable define-stage base is **5.6 d**: the feasibility check's 6.0, minus the 0.40 d plan stage, which is already spent.
  - Growth is about +2.7 d (+48%). About 77% of it is on items the valve can't carve.

| Group | Tasks | Central | Carvable |
|---|---|---|---|
| Setup (W0) | T001–T003 | 0.40 | no |
| K1 + K2 (cut line) | T004–T005 | 0.60 | no |
| A-2 + PD-6 | T006–T007 | 0.15 | no |
| K3 | T008–T011 | 1.47 | no |
| K14 | T012–T015 | 0.80 | no |
| US-3a (K9, K10, K12, K13.1) | T016–T019 | 1.28 | no |
| K11 | T020–T023 | 1.09 | 2nd |
| K13-posture | T024–T026 | 0.47 | 3rd |
| K15 | T027–T030 | 0.85 | 1st |
| #370 | T031 | 0.15 | drop-able |
| Polish | T032–T038 | 1.02 | no |
| Checkpoint | T039 | 0.03 | no |
| **Total** | | **8.31** | |

T040 (≈ 0.25–0.50 d) runs only if TW-7 fires, and is outside the estimate.

- **Duration, branch → merge** (the TW-0 formula; floor / central / ceiling): **3.5 / 5.2 / 7.7 d**.
  - The sign-off review gave 3.5 / 5.05 / 7.6 d, before the revisions' folds.
  - The folds that added time: F1's parser surface, F2's join wiring, L11, L12, N11, the per-K-item golden commits, T039, B1's worktree replay, and T039 gating every W2 task.

### TW-0 (aggregate): NOT FIRED

The pacing lane is each wave's longest dependency chain, including the serial gates this file declares inside the wave:

| Wave | Pacing chain | Days |
|---|---|---|
| W0 | T003 | 0.20 |
| W1 | Lane A′: T008 → T009 → T010's lock-step commit (1.17) → T039 (0.03), which W2 waits for | 1.20 |
| W2 | the test lane's T019, T023, T029 and T031 tests (0.77) → T032 (0.14) → T033 (0.13) | 1.04 |
| W3 | T034's commit (0.05) → the render session T030 → T015 (0.43) → a T032 re-run (0.05) → T035 (0.20) → T036's checkpoint (0.05) | 0.78 |
| W4 | T037 | 0.15 |
| **Σ** | | **3.37** |

- **Projected duration** = 3.37 × 1.25 + 1.0 = **5.21 d**, against 5.5 d: **not fired, with a margin of 0.29 d**.
  - Nothing is carved at `/aod.tasks`. The carve order stays K15 → K11 → K13-posture.
- **The ruling depends on the W1 launch rule.** Before revision 1, the text launched Lanes A′, B1 and C1 only after A-1 was green and A-2 committed. On that schedule, the same formula computed 5.8–5.9 d and would have carved K15, and K11 as well on the re-cost.
- **The earlier ≈ 4.4 d projection is superseded.** It counted only the longest parallel lane in each wave, and dropped the declared gates T032 → T033 and T034 → T036.
- **Cross-check** (effort × 0.71–0.75, the define-stage compression ratio): 5.4–5.7 d on the original task figures, 6.0–6.4 d on the re-cost. This is the pessimistic read.
  - F-362, the one multi-lane precedent, supports the formula to within about ±10% (5.4 d projected against 5–6 d actual).
  - F-362 did not compress to 0.71–0.75.
- **The margin sits inside that error band.** So T039 re-checks TW-0 with actuals at W1 exit, the last point where a K15 carve costs nothing.

### TW-1 to TW-4

| Trip-wire | Evidence | Sum | Limit | Ruling |
|---|---|---|---|---|
| TW-1 (K11) | STEP 10, FLOOR 30 (PD-4), the numeric semantics (PD-5) and the Tier-3 formula (data-model §3) are all pinned | **1.14 d**: T020–T023 with F2's join wiring and L11's text, K11's parity case, and its golden share | 1.2 | **Not fired**, margin 0.06. T039 re-evaluates it with T020's actual |
| TW-2 (K13-posture) | OQ-3 is closed (D-3; PD-13); Typst runs in its own W2 job (PD-8) | **0.50 d**: T024–T026 and its golden share | 0.6 | **Not fired**, margin 0.10 |
| TW-3 (K15) | OQ-4 is closed (PD-17); P-2 is ratified with nine conditions (PD-2) | — | — | **Not fired**. No partial carve |
| TW-4 (#370) | The recipe fits, and shrinks to 2 tests + 1 note (T031). **OQ-5 is closed**: case 2 uses the real catalog, and `schemas/taxonomy/*.yaml` joins `paths:` in A-2 | 0.15 d | recipe | **Not fired** |

### TW-5 to TW-7 (during the build)

- **TW-5** (T030): at most two prompt iterations. Residual leakage goes to a follow-up issue.
- **TW-6** (T030): if renders are blocked for more than half a day, K15 is carved through T030's late-carve procedure. K14 keeps T015 (P-10.2).
- **TW-7** (T033): Group A ships early through T040 if, with the actuals, either of these holds:
  - the remaining projected work exceeds 2.0 d;
  - any lane is more than 50% over its budget.

  TW-7 carves nothing. At central, the remaining work at T033 is about 1.7 d.

The lane budgets TW-7 measures against, from the per-task figures:

| Lane | Budget |
|---|---|
| A′ (W1) | 1.17 d, plus 0.15 d of W2 convergence |
| A (W1) | 0.72 d |
| B1 | 0.97 d |
| C1 | 0.58 d, T014's module included |
| B2a | 0.72 d |
| B2b | 0.55 d |
| C2 | 0.50 d |
| Test lane (W2) | 0.77 d, plus T032 |

### Agent load per wave

Window = the pacing chain × 1.25. Load = an instance's effort in the wave ÷ the window. No instance exceeds 80%. `agent-assignments.md` carries the same assignments as the `/aod.build` matrix.

The instances:
- **SBE**: a `senior-backend-engineer` instance.
- **SBE-T**: the test-lane instance.
- **The W3 writer**: one SBE.

T039 and T033's TW-7 ruling are team-lead checkpoints that the orchestrator invokes, so they carry no assignee load.

| Wave (window) | Agent instances and loads |
|---|---|
| W0 (0.25 d) | SBE T001 60%; SBE T002 20%; SBE-T T003 80% (the pacing lane, by construction) |
| W1 (1.50 d) | SBE Lane A 37%; `devops` Lane A 11%; SBE-T (T008) 30%; `devops` A′ 48%; SBE B1 65%; SBE C1 (with T014's module) 39% |
| W2 (1.30 d) | SBE B2a 55%, B2b 42%, C2 38%; SBE-T (with T032) 70%; `devops` Lane A 18%; SBE Lane A (T011) 4%; `security-analyst` 8%; `architect` 5%; `tester` (N4 re-run) 2% |
| W3 (0.98 d) | `devops` (T034) 21%; `tester` (the render session) 44%; the W3 writer 15%; SBE (T035) 21%; `code-reviewer` 10%; `architect` 5% |
| W4 (0.19 d) | SBE (T037) 64%; `architect` (the ADR-014 note) 16%; `product-manager` (T038) 27% |

### Milestones against PRD §11

Working days count from Monday 09-28. The plan stage closed on Sunday 09-27, a day ahead of M1.

| Milestone | PRD central / ceiling | Projected |
|---|---|---|
| M2 (end of Session 1) | 09-30 / 10-01 | Wed 09-30 at the edge; otherwise Thu 10-01 morning |
| M3 (end of Session 2) | 10-01 / 10-05 | Fri 10-02 |
| M4 | 10-02 / 10-06 | Fri 10-02, with about 0.3 d of slack; realistically Mon 10-05 |

In the ceiling case, the full bundle lands on Wed 10-07, and TW-7 lands K1–K3 by about 10-05.

## Implementation Strategy

### MVP first (the cut line)

Setup, then A-1 (US-1 and US-5). A-1 is shippable alone and closes the third K1 recurrence. A-2 (the Group B safety net) follows immediately.

### Incremental delivery

- **W1**: US-2 (K3) and US-4a (K14) are statically green, and the Group B parser foundations land.
- **W1 exit**: T039 re-checks the trip-wires with actuals, before W2 starts.
- **W2**: the consumers and text for US-3a, 3b, 3c and 4b, plus #370, then the goldens.
- **End of Session 1, only if TW-7 fires**: Group A ships early through T040, with P-11.2's notices.
- **W3**: live verification (the US-4a render set and the US-4b renders), the oracle, CI convergence and review.
- **W4**: close-out.

The split valve can cut at any wave boundary after A-1. K3 ships with K1. K14 never bends the cut line; its early-ship conditions are P-9.1 and P-10.4 (T040).

### Session strategy (clean-session phasing)

- The plan stage runs in this session.
- **`/aod.build` reads `agent-assignments.md`.** Build waves 1–5 are W0–W4. Run it with `--no-tests`, with the reason recorded, and run the gated set as each wave's gate (standing rules; LOW-2).
- **Build Session 1**: W0–W2 (build waves 1–3, the `/aod.build` standalone ceiling).
  - It ends at T033, with `NEXT-SESSION.md` and the TW-7 check (T040 if it fires).
  - T039's snapshot at W1 exit is the fallback break point if the orchestrator's context runs short.
- **Build Session 2**: W3–W4 (build waves 4–5).
- Then `/aod.deliver`.
- **Maintainer availability** (PM §9 item 7):
  - about 1 hour on the afternoon of Thursday 10-01, for W3's visual checks (T030/T015: six images plus the executive-architecture PDF page);
  - about 30 minutes on the morning of Friday 10-02, held in reserve for a TW-5 iteration.

  T002's W0 smoke needs no visual check.

### Deliver-stage reminders (not tasks; `/aod.deliver` checklist inputs)

- Before any merge or push, verify that the branch is current and that local `main` equals `origin/main` (KB Entry 18). `git reset --hard` is blocked in this environment; use `git checkout -B main origin/main`.
- Confirm every wave commit is on `origin/373-adopter-install-output-fidelity`.
- Squash-merge #375 as `fix(373): …`, then verify that the release-please **patch** PR opens within about 30 s. If it doesn't, push a `fix(373):` marker commit.
- Apply `release-notes-upgrading.md` per PD-7, and verify it with `gh release view`.
  - If the release PR merges after deliver, this is the follow-through item.
  - If TW-7 fired, SC-6 is verified per release (P-11.2).
- Post the #364 handoff comment. Close #370 if it was folded in.
- File follow-up issues, after `export AOD_REPO=davidmatousek/tachi`, for:
  - TW-5 residual leakage;
  - a blocked model (P-10.1);
  - each carved K-item (TW-0 to TW-6), carrying its tasks, SC clauses and goldens (R-T4);
  - N7: a free-text `baseline.source` on a stateless run triggers PD-16's "baseline run but no Status column" warning (R-T3).
- SC-7 is tracked outside this feature: live confirmation on the next large real-world run, with the stock `install.sh --version <released tag>`, and with `--follow-symlinks` where a destination is symlinked by design.

## Notes

- Tasks in one lane run in sequence under that lane's agent. [P] marks tasks that can start at their wave's start.
- Every test module lands in lock-step with its workflow entries (NFR-7, PD-20). That happens through Lane A's wiring commits, or, for the installer, in T010's single commit.
- The trip-wires are evaluated mechanically.
  - Carving a K-item moves its tasks, its SC clauses (spec R-c) and its goldens to its follow-up issue. Its render proof is kept per P-10.2.
  - Because each carvable K-item has its own commits, a carve after work has landed is a `git revert` of named commits, followed by T032 for the survivors (T030's late-carve procedure; T039's reverts).
