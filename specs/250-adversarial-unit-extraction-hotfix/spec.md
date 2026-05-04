---
prd_reference: docs/product/02_PRD/250-adversarial-unit-extraction-hotfix-2026-05-04.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-04
    status: APPROVED
    notes: "PRD G-1..G-6 each map to at least one FR (FR-009..FR-010, FR-012..FR-016) and one SC (SC-001..SC-006); AC-1..AC-8 all reflected with architect-broadened scope preserved; NG-1..NG-3 verbatim. US-1 and US-2 both P1 with Given/When/Then scenarios. TC-4 MUST NOTs encoded as FR-019..FR-022. OQ-1 clean-delete and OQ-2 fix(250) resolved with PM stance. TC-1..TC-4 flagged forward to tasks.md. Edge Cases surface R-1..R-5. Zero [NEEDS CLARIFICATION]. Detailed audit at .aod/results/pm-spec-review-250.md."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Adversarial Unit Extraction Hot-Fix

**Feature Branch**: `250-adversarial-unit-extraction-hotfix`
**Created**: 2026-05-04
**Status**: Draft
**Input**: User description: "PRD: 250 - adversarial-unit-extraction-hotfix"
**PRD Reference**: `docs/product/02_PRD/250-adversarial-unit-extraction-hotfix-2026-05-04.md`
**Research**: `specs/250-adversarial-unit-extraction-hotfix/research.md`

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Adopter ships a feature without CI runner-roulette (Priority: P1)

An adopter who forks tachi and pushes a feature branch needs the init.sh test suite to complete inside the standard CI window without flaking on `macos-latest`, so their PRs land cleanly without admin-override merges or runner retries.

**Why this priority**: This is the hot-fix's primary outcome. The cold-cache 300-second timeout class on `macos-latest` directly blocked F-248's closing CI run (`25314246672`) and required an admin-override squash-merge. Until the timeout class is eliminated, every adopter merge to `main` carries the same risk.

**Independent Test**: Push a feature branch to a tachi fork after the hot-fix lands. Confirm both CI matrix legs (`macos-latest`, `ubuntu-latest`) are green within the standard CI window with no manual intervention. Five consecutive runs without flake confirm the timeout class is removed.

**Acceptance Scenarios**:

1. **Given** an adopter has pushed a tachi feature branch with the post-hot-fix init.sh test suite in place, **When** the GitHub Actions CI workflow runs, **Then** both `macos-latest` and `ubuntu-latest` matrix legs MUST report green inside the standard CI window without per-test timeout failures.
2. **Given** the post-hot-fix CI workflow has run on at least five consecutive merges, **When** the run history is inspected, **Then** the `macos-latest` matrix leg MUST show a 5/5 green-rate (vs. the 1/5 historical baseline).
3. **Given** the post-hot-fix init.sh test suite is executing on `macos-latest`, **When** the suite duration is measured by the GitHub Actions step timer, **Then** total wall time MUST be at most 15 minutes (down from the 30–40 minute pre-hot-fix band).

---

### User Story 2 — Maintainer triages a substitution-helper regression with a precise stack trace (Priority: P1)

A tachi maintainer who is triaging a substitution-semantics regression needs the test that fails to point directly at the helper function under test, so they can locate the root cause without parsing eight megabytes of init.sh integration stderr.

**Why this priority**: A second-order goal of the hot-fix is improving regression-detection signal-to-noise. Today, a substitution regression triggers a full init.sh run that emits unrelated context; the maintainer must mentally subtract that noise before naming the helper at fault. The unit-level extraction makes the helper the named subject of the test, so the failing test ID *is* the diagnosis.

**Independent Test**: Deliberately introduce a known-bad regression in `aod_template_substitute_placeholders` (e.g., remove the `shopt -u patsub_replacement` shim on a bash 5.x dev workstation). Run the full test suite. Confirm the failing test name and its stderr blob both unambiguously identify `aod_template_substitute_placeholders` as the helper at fault.

**Acceptance Scenarios**:

1. **Given** a deliberate regression in `aod_template_substitute_placeholders` is introduced on a bash 5.x runtime, **When** `pytest tests/scripts/` runs, **Then** at least one of `test_template_substitute_unit.py::case_1_ampersand`, `case_3_backref`, or `case_6_multibyte` MUST fail with stderr that names the corrupted byte sequence; no other unrelated test failures should be triggered by the same regression.
2. **Given** a deliberate regression in `aod_init_read_validated` is introduced (e.g., the input-rejection path is broken), **When** `pytest tests/scripts/` runs, **Then** the failing test ID MUST be in `test_init_input_unit.py` and its stderr MUST name the input-rejection class (empty / multiline / disallowed-character) rather than a generic init.sh failure.

---

### Edge Cases

- **Pipe-subshell silent false-pass (R-1, HIGH)**: The `aod_init_read_validated` helper writes to caller scope via `printf -v`. When invoked through a shell pipe, the rightmost element runs in a subshell and the assignment is silently lost — the function returns RC=0 but `result=""`. A unit test that uses the wrong invocation pattern would pass while validating nothing. The spec MUST require process-substitution invocation as the only sanctioned pattern, and a positive-path canary test must guard the pattern at module-load.
- **Locale drift on multibyte UTF-8 (R-4)**: Case 6 (`Ⅷ-Ⅸ` U+2160 range) could mask a regression if the unit-test environment locale differs from the runner default. The spec MUST require `LC_ALL=C` to be pinned in every per-case subprocess invocation (matches the F-248 baseline at `init_sh_helpers.run_init_in_clone:135`).
- **Future helper-invocation drift (R-5)**: A future refactor could change *how* `init.sh` invokes the helpers (e.g., adding a pre-validation layer) such that the unit-tested helper diverges from production behavior. The spec MUST keep case 13 (trailing-newline byte-identity) and `test_no_residual_placeholders_after_init` exercising the full init.sh path, plus `test_init_sh_substitution.py` (Test-1) on every CI run, so any drift surfaces in the integration backstop.
- **Atomic-PR ordering (TC-3)**: A partial merge of the three steps (substitute-unit module → input-unit module → delete-block from adversarial.py) leaves both old and new tests in-tree, doubling CI cost on intermediate commits. The spec MUST require the three steps merge as a single PR.
- **Test-1 long pole (R-3)**: If `test_init_sh_substitution.py` becomes the dominant remaining CI cost, the ≥25-minute savings target may be tight. The 12-case extraction alone removes ~36–50 minutes of subprocess time per the architect baseline §6 calculation, but a one-shot post-merge CI timing measurement is required to confirm.

---

## Requirements *(mandatory)*

### Functional Requirements

> **Acceptance Criteria Rule**: Each AC begins with **Given** and follows Given/When/Then structure. ACs that cannot be fully automated are marked `[MANUAL-ONLY]` with a reason.

#### Test architecture

- **FR-001**: The system MUST host adversarial substitution-semantics cases 1–8 (the 6 sed-metacharacter cases and the 2 quoting cases) in a new pytest module at `tests/scripts/test_template_substitute_unit.py` that exercises `aod_template_substitute_placeholders` directly without invoking `scripts/init.sh`.
- **FR-002**: The system MUST host adversarial input-rejection cases 9–12 (empty, multiline, disallowed-character classes) in a new pytest module at `tests/scripts/test_init_input_unit.py` that exercises `aod_init_read_validated` directly without invoking `scripts/init.sh`.
- **FR-003**: The new test modules MUST NOT import from `tests/scripts/init_sh_helpers.py` and MUST contain zero references to `run_init_in_clone`, `clone_into_tmpdir`, `init_sh_helpers`, or `scripts/init.sh`.
- **FR-004**: The system MUST retain the case 13 trailing-newline byte-identity integration test and the `test_no_residual_placeholders_after_init` integration test in `tests/scripts/test_init_sh_adversarial.py` byte-unchanged from their pre-hot-fix form, including the existing `from init_sh_helpers import ...` block needed by case 13.
- **FR-005**: The system MUST leave `tests/scripts/init_sh_helpers.py` and `.aod/scripts/bash/template-substitute.sh` and `.aod/scripts/bash/init-input.sh` byte-unchanged. The hot-fix is test-tree-only.

#### Invocation pattern

- **FR-006**: Tests in `test_init_input_unit.py` MUST invoke `aod_init_read_validated` via process substitution (`< <(printf '%s\n' "$INPUT")`) and MUST NOT invoke it through a shell pipe. Pipe invocation silently loses the `printf -v` caller-scope assignment and produces a false-pass.
- **FR-007**: The first test collected from `test_init_input_unit.py` MUST be a positive-path canary: a known-good input passed through `aod_init_read_validated` MUST round-trip and produce a non-empty result. This canary fails fast if the invocation pattern is broken.
- **FR-008**: Every per-case subprocess invocation in both new modules MUST pin `LC_ALL=C` and the minimum `PATH` needed to execute bash, matching the F-248 baseline at `init_sh_helpers.run_init_in_clone:135`. This prevents locale-dependent drift on multibyte UTF-8 case 6.

#### Regression coverage preservation

- **FR-009**: The 6 sed-metacharacter cases (1: ampersand `AT&T`, 2: pipe `foo|bar`, 3: backref `\1\2`, 4: single-quoted, 5: double-quoted, 6: multibyte `Ⅷ-Ⅸ`) extracted to `test_template_substitute_unit.py` MUST detect the same regression class the pre-hot-fix integration suite detected — namely, the `AT&T → AT{{PROJECT_NAME}}T` corruption that F-248 closed.
- **FR-010**: Removing the `shopt -u patsub_replacement 2>/dev/null || true` shim from `.aod/scripts/bash/template-substitute.sh` on a bash 5.x runtime MUST cause at least cases 1, 3, and 6 of `test_template_substitute_unit.py` to fail with non-zero exit and stderr identifying the corrupted byte sequence. Cases 2, 4, and 5 MUST pass under the same fault state, confirming they exercise pure parameter expansion independent of the shim. `[MANUAL-ONLY] one-shot deliberate-fault check is run locally on bash 5.x; not a permanent CI step`
- **FR-011**: The 4 input-rejection cases (empty, multiline, disallowed-character classes) extracted to `test_init_input_unit.py` MUST detect the same rejection-path regressions the pre-hot-fix integration suite detected — including the 3-strike exit path (3 copies of bad input followed by exit 1 with a named reason class on stderr).

#### CI behaviour

- **FR-012**: Every test in `test_template_substitute_unit.py` and `test_init_input_unit.py` MUST complete in at most 2 seconds wall time on `macos-latest`, as observed in the pytest `--durations=0` summary on the post-merge CI run.
- **FR-013**: Both new modules MUST be invoked under `pytest --timeout=15` so any wall-time regression that pushes a single case past 5 seconds fails fast.
- **FR-014**: After the hot-fix lands, the count of `scripts/init.sh` subprocess invocations across `tests/scripts/` MUST drop from 17 (pre-hot-fix) to 5 (post-hot-fix). The 5 remaining invocations are: case 13 in `test_init_sh_adversarial.py`, `test_no_residual_placeholders_after_init`, `test_init_sh_constitution.py`, `test_init_sh_self_delete.py`, and `test_init_sh_substitution.py`.
- **FR-015**: The post-merge CI run MUST be green on both `macos-latest` and `ubuntu-latest` without any admin-override merge.
- **FR-016**: Total wall time of the init.sh test suite on `macos-latest` MUST be at most 15 minutes on the post-merge CI run, measured by the GitHub Actions step duration. The delta from CI run `25314246672` MUST be at least 25 minutes.

#### Release plumbing

- **FR-017**: The hot-fix MUST ship as a single PR with the title `fix(250): extract adversarial unit tests — eliminate cold-cache CI flake` (Conventional Commits format). Atomic-PR ordering (substitute-unit then input-unit then delete-block from adversarial.py) is required to avoid an intermediate doubled-CI state.
- **FR-018**: After squash-merge to `main`, a release-please PR MUST appear within ~30 seconds. If it does not, an empty `fix(250):` release-marker commit MUST be pushed per the post-merge belt-and-suspenders rule in `.claude/rules/git-workflow.md`.

#### Scope fences (MUST NOT)

- **FR-019**: The hot-fix MUST NOT modify any bash helper in `.aod/scripts/bash/`. Helper-extraction shape changes are out of scope.
- **FR-020**: The hot-fix MUST NOT introduce any new adversarial cases beyond the 12 extracted from the existing table. Adding novel cases is a separate PRD's scope.
- **FR-021**: The hot-fix MUST NOT modify `tests/scripts/init_sh_helpers.py`. Any helper-shape evolution is deferred to the Path C scope refactor.
- **FR-022**: The hot-fix MUST NOT touch case 13 (trailing-newline byte-identity) or `test_no_residual_placeholders_after_init`. Those tests remain byte-unchanged as the integration backstop.

### Key Entities

- **`test_template_substitute_unit.py`**: New pytest module covering substitution-semantics cases 1–8. Sources `template-substitute.sh`, sets the 12 `AOD_PERSONALIZATION_*` env vars, writes a 1-line src file containing `{{PROJECT_NAME}}`, invokes `aod_template_substitute_placeholders src dest`, then byte-verifies the dest contents. Function-scoped `tmp_path` fixture only.
- **`test_init_input_unit.py`**: New pytest module covering input-rejection cases 9–12. Sources `init-input.sh`, invokes `aod_init_read_validated` via process substitution, asserts on caller-scope `result` plus stderr reason class. No filesystem touch.
- **`test_init_sh_adversarial.py`**: Existing integration module retained as the integration backstop. Lines 41–162 (the 12 extracted cases) are deleted; lines 1–39, 165–227 (case 13), and 229–288 (`test_no_residual_placeholders_after_init`) remain byte-unchanged.
- **`aod_template_substitute_placeholders`**: Bash helper at `.aod/scripts/bash/template-substitute.sh`. Performs literal placeholder substitution via bash parameter expansion. Untouched by the hot-fix; only its caller-test layer changes.
- **`aod_init_read_validated`**: Bash helper at `.aod/scripts/bash/init-input.sh`. Reads input, validates against allow-list, writes to caller scope via `printf -v`. Untouched by the hot-fix; only its caller-test layer changes.
- **`shopt -u patsub_replacement` shim**: Single line at `.aod/scripts/bash/template-substitute.sh:64` that disables bash 5.2+'s `patsub_replacement` option. Load-bearing per FR-010; removing it must trigger failures in unit cases 1, 3, and 6.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Per-case wall time for cases 1–12 drops from 180–258 seconds (integration form, with timeout failures) to at most 2 seconds (unit form), measured on `macos-latest` via pytest `--durations=0`.
- **SC-002**: Total init.sh-suite wall time on `macos-latest` drops from 30–40 minutes (current band) to at most 15 minutes, measured by the GitHub Actions step duration on the post-merge run.
- **SC-003**: The number of `scripts/init.sh` subprocess invocations per CI run drops from 17 (13 adversarial + 4 other init-touching tests) to 5 (1 adversarial smoke + 4 other), confirmed by a repository-wide grep for invocation identifiers in `tests/scripts/`.
- **SC-004**: The `macos-latest` matrix leg green-rate over the next 5 runs after merge is 5/5, up from 1/5 in the F-248 cycle. The `ubuntu-latest` green-rate is 5/5 (unchanged).
- **SC-005**: Total CI wall-time savings vs. baseline run `25314246672` is at least 25 minutes per run, summed across both matrix legs, confirmed by a one-shot post-merge timing sample.
- **SC-006**: Substitution-semantics regression detection is preserved verbatim — the 6 sed-metacharacter cases continue to detect the `AT&T → AT{{PROJECT_NAME}}T` corruption class that F-248 closed if it were ever reintroduced upstream of the helper. `[MANUAL-ONLY] one-shot deliberate-fault verification matrix on bash 5.x; recorded in validation log`
- **SC-007**: A repository-wide grep for `run_init_in_clone\|clone_into_tmpdir\|init_sh_helpers\|scripts/init.sh` in the new files (`test_template_substitute_unit.py`, `test_init_input_unit.py`) returns zero matches.
- **SC-008**: The hot-fix PR title is Conventional-Commits-formatted as `fix(250): extract adversarial unit tests — eliminate cold-cache CI flake`, and post-merge a release-please PR is open within ~30 seconds of the squash-merge.

---

## Assumptions

- The cold-cache 300-second timeout class on `macos-latest` is the dominant residual flake source after the hot-fix; if a different flake class surfaces in the post-merge run, it is out of scope and tracked as a follow-up.
- `test_init_sh_substitution.py` (Test-1) wall time after the hot-fix is acceptable for the ≥25-minute savings target. The architect baseline §6 calculates the 12-case extraction alone removes 36–50 minutes of subprocess time, well above the target. The Path C scope refactor that would further shrink Test-1 is explicitly deferred (NG-1).
- The bash 5.x deliberate-fault verification (FR-010 / SC-006) is a one-shot local check, not a permanent CI step. The matrix output (PASS/FAIL per case) is recorded in the validation log for audit.
- The 12 extracted cases collectively preserve regression detection at exactly the F-248 level. Case 13 plus Test-1 plus `test_no_residual_placeholders_after_init` plus the bash-version diagnostic step in the workflow continue to provide the integration backstop.
- The PR is squash-merged. The Conventional-Commits-formatted title is required because release-please reads the squash-merge subject from the PR title; `fix(250):` produces a patch-level release.

---

## Dependencies

- **Upstream**: F-248 (Substitution Surface Hardening) must be merged on `main`. F-248 introduced the `shopt -u patsub_replacement` shim (FR-010 / SC-006 reference) and authored the original 13-case adversarial table this hot-fix reorganises. F-248 was merged 2026-05-04 as PR #249.
- **Architectural**: ADR-038 (Placeholder Substitution Strategy, Accepted 2026-05-04) defines the helper contracts this hot-fix re-tests at unit level. No ADR change is triggered by the hot-fix.
- **Toolchain**: bash 3.2+ (process substitution and `printf -v`), Python 3.9+ (CI runs 3.11), pytest 8.0+. All present in the existing CI image.

---

## Non-Goals

The following items were considered and explicitly deferred:

- **NG-1 — Path C scope refactor**: modifying Test-1 (`test_init_sh_substitution.py`) to read `templates/manifest.yaml` categories rather than walking the whole project tree. This was the original Issue #250 body; it remains valuable but is a separate PRD's scope. Rationale: the hot-fix already meets the 25-minute savings target without it.
- **NG-2 — Session-scoped pytest fixtures**: shared init.sh state across tests via session fixtures. Rationale: not needed at the new ~50ms-per-case baseline; would re-introduce cross-test coupling that the unit split is precisely designed to remove.
- **NG-3 — Synthetic 5-file fixture tree**: replacing the 2,071-file baseline with a synthetic minimum tree. Rationale: case 13 and Test-1 still benefit from the realistic tree; reducing fixture size is a Path C concern.

---

## Open Questions

> **Resolution rule**: open questions resolved via PRD PM stance are recorded here as resolved. New questions that surface during plan/tasks.md authoring are recorded as `[NEEDS CLARIFICATION]` and capped at 3 per the spec quality gate.

- **OQ-1 (resolved)**: Should the deleted adversarial-cases block be preserved as a comment in `test_init_sh_adversarial.py` for git-blame archaeology, or is clean delete preferred? **Resolution**: Clean delete. Git history retains the table content; the file stays at its narrowest contract. (PM stance, PRD §Risks & Open Questions.)
- **OQ-2 (resolved)**: Is `fix(250):` the right Conventional-Commits prefix? **Resolution**: Yes. The hot-fix ships no user-visible feature and no security closure. The change is invisible to adopters except as faster CI. (PM stance, PRD §Risks & Open Questions.)

**Tasks.md-level concerns** carried forward from PRD Triad reviews:

- **TC-1** (Architect): No permanent CI canary asserts the `shopt -u patsub_replacement` shim stays in place — a future cleanup PR could remove it without immediate signal. Tasks.md should consider adding a one-line CI smoke that asserts the shim line still exists.
- **TC-2** (Architect): The baseline CI run `25314246672` should be URL+SHA pinned in tasks.md with measured minutes recorded, so the ≥25-min savings claim has a defensible reference point post-merge.
- **TC-3** (Team-Lead): Atomic-PR ordering — the three steps must merge as a single PR. A partial merge between steps leaves both old and new tests in-tree, doubling CI cost on intermediate commits.
- **TC-4** (Team-Lead): MUST_NOT scope fences for the build agent — no helper modification, no `init_sh_helpers.py` restructure, no new adversarial cases beyond the 12 extracted, no touch on case 13.
