---
prd:
  number: 250
  topic: adversarial-unit-extraction-hotfix
  created: 2026-05-04
  status: Approved
  type: infrastructure
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-04
    status: APPROVED
    notes: "PRD body authored using working-backwards framework; embedded architect baseline sections 1-6 verbatim; product-tagged R-1 (pipe-subshell trap) as top-level risk; OQ-1 (clean delete vs comment archaeology) and OQ-2 (fix vs feat prefix) captured for spec.md adjudication."
  architect_signoff:
    agent: architect
    date: 2026-05-04
    status: APPROVED_WITH_CONCERNS
    notes: "Baseline fidelity Faithful; AC testability Adequate. Three concerns addressed inline before finalization: (1) AC-5 broadened from 1 case to all 6 sed-metachar cases with explicit pass/fail matrix under fault state — cases 1/3/6 must FAIL when shim removed, 2/4/5 must PASS; (2) AC-4 forbidden-identifier grep expanded to include init_sh_helpers per baseline section 2; (3) cosmetic duplicate Architect Technical Baseline H2 header removed. Two low-severity tasks.md concerns flagged forward: R-6 no permanent shim CI canary; R-7 baseline run 25314246672 not URL+SHA pinned."
  techlead_signoff:
    agent: team-lead
    date: 2026-05-04
    status: APPROVED_WITH_CONCERNS
    notes: "Size S, 4-6 wall hours, single working session feasible. Concerns are tasks.md-level: (1) atomic-PR ordering required — substitute-unit then input-unit then delete-block must merge as one PR to avoid intermediate doubled-CI state; (2) MUST_NOT scope fences to add — no helper modification, no init_sh_helpers restructure, no new adversarial cases beyond the 12 extracted; (3) baseline run 25314246672 must be URL+SHA pinned with measured minutes in tasks.md to defend the >=25min savings claim; (4) require build agent reads architect-baseline section 1 and section 6 before authoring input-unit module."
source:
  idea_id: 250
  story_id: null
---

# Issue #250 Hot-Fix — Adversarial Unit Extraction: Product Requirements Document

**Status**: Approved (PM ✓ + Architect ⚠ + Team-Lead ⚠ — concerns addressed inline; tasks.md-level concerns flagged forward)
**Created**: 2026-05-04
**Author**: product-manager
**Reviewers**: architect, team-lead
**Phase**: BLP-02 follow-up — surgical CI stabilization wedge for the F-248 substitution-surface fix
**Priority**: P1 (CI flake on `main`; blocks confidence in BLP-02 Wave 1 closing posture)

---

## TL;DR

F-248 ("substitution surface hardening") shipped on 2026-05-03 and closed five `/security` vulnerabilities, but its closing CI run (`25314246672`) timed out on `macos-latest` at the 300-second subprocess limit on the *first* `scripts/init.sh` invocation — a cold-cache flake, not a substitution regression. The flake's mechanical root cause is the 13-case `tests/scripts/test_init_sh_adversarial.py` parametrized suite: each adversarial case clones a 2,071-file baseline tree and spawns a full `init.sh` run via `clone_into_tmpdir()` + `run_init_in_clone()`, driving total init.sh-suite wall time to 30-40 minutes on `macos-latest`. This PRD is the **surgical hot-fix wedge**: extract adversarial cases 1-12 to unit-level pytest modules that invoke the underlying helpers (`aod_template_substitute_placeholders`, `aod_init_read_validated`) directly, while keeping case 13 (trailing-newline byte-identity) as the integration smoke. The targeted outcome is at least 25 minutes of CI savings per run, sub-15-minute macos-latest init.sh-suite wall time, zero new init.sh invocations introduced, and verbatim preservation of the load-bearing sed-metachar regression detection. The broader Path C scope refactor (Test-1 reading template-manifest categories) — the *original* Issue #250 body — is explicitly deferred.

---

## Background

The F-248 delivery retrospective (`specs/248-substitution-surface-hardening/delivery.md`) recorded three baseline-staleness incidents during the build (T039, T040, T046 pre-merge) plus one new-class flake at close-out: CI run `25314246672` against commit `219dfee` succeeded on `ubuntu-latest` and timed out on `macos-latest` with two 300-second subprocess errors on the *first* `init.sh` run of the matrix leg. The substitution-semantics adversarial cases themselves passed; the failure was a runner-perf flake at the cold-cache + first-test-runs-first edge. Closure used an admin-override squash-merge (ubuntu green; macos timeout classified as a non-regression flake).

A 5 Whys analysis surfaced the mechanical root cause: macos-latest timed out because cold-cache + the runner's 3-4× spawn slowdown multiplied across the 2,071-file baseline tree exceeded 300s; the tree is walked per case because `test_init_sh_adversarial.py` parametrizes 13 inputs and each one calls `run_init_in_clone()` — a full init.sh execution; full init.sh executions are not actually needed for cases 1-12, which exercise `aod_template_substitute_placeholders` (substitution semantics) and `aod_init_read_validated` (prompt rejection) and could be tested at the helper-function level; the suite is at integration level by historical accident — the adversarial table was authored alongside the case-13 file-level integrity test and reused its `clone_into_tmpdir` fixture.

The **F-248 Lessons Learned** entry (KB Entry 1 in `docs/INSTITUTIONAL_KNOWLEDGE.md`) captured the principle: *"when a test invokes a heavy mechanism per parametrized case, ask if a unit-level test against the underlying function can prove the same invariant."* This PRD operationalizes that principle on the only suite where the mechanism is heavy enough to flake CI.

The original Issue #250 body proposed a broader Path C refactor — modifying Test-1 to read template-manifest categories instead of walking the whole tree. That work remains valuable but is **deferred**. This hot-fix is the surgical wedge: it eliminates 12 of the 17 init.sh subprocess invocations per CI run, removes the cold-cache flake at root, and lets the next PRD scope Path C with a stable CI baseline.

---

## Goals

The measurable outcomes this hot-fix must deliver:

- **G-1**: Each extracted unit case completes in ≤2 seconds wall time (down from 180-258 seconds in integration form on `macos-latest`).
- **G-2**: ≥25 minutes of total CI wall-time savings per run on the init.sh-suite, summed across the matrix.
- **G-3**: Total init.sh-suite wall time on `macos-latest` is ≤15 minutes (down from the 30-40 minute current band).
- **G-4**: Both `macos-latest` and `ubuntu-latest` matrix legs report green on the post-hot-fix CI run, with no further admin-override merges required for substitution-suite flakes.
- **G-5**: Zero new `scripts/init.sh` invocations are introduced anywhere in the test tree by this hot-fix.
- **G-6**: Substitution-semantics regression detection is preserved verbatim — the 6 sed-metacharacter cases must still detect the `AT&T → ATtachiT` corruption class that F-248 closed if it were ever reintroduced upstream of the helper.

---

## Non-Goals

The following items were considered and explicitly deferred — each remains tracked for a future PRD:

- **NG-1**: **Path C scope refactor** — modifying Test-1 (`test_init_sh_substitution.py`) to read `templates/manifest.yaml` categories rather than walking the whole project tree. This was the original Issue #250 scope. Rationale for deferral: the hot-fix already meets the 25-minute savings target without it; Path C deserves its own PRD with explicit manifest-contract review.
- **NG-2**: **Session-scoped pytest fixtures** for shared init.sh state across tests. Rationale: not needed at the new ~50ms-per-case baseline; would re-introduce cross-test coupling that the unit split is precisely designed to remove.
- **NG-3**: **Synthetic 5-file fixture tree** to replace the 2,071-file baseline. Rationale: case 13 (the one remaining integration case) and Test-1 still benefit from the realistic tree; reducing fixture size is a Path C concern, not a hot-fix concern.

---

## User Stories

**US-1 — Adopter running CI on a downstream tachi project.**
> As an adopter who forks tachi and pushes a feature branch, I want the init.sh test suite to complete inside the standard CI window without flaking on `macos-latest`, so that my PRs don't require admin-override merges or runner-retry roulette to land. The hot-fix removes the cold-cache 300-second timeout class entirely by eliminating 12 of the 17 init.sh subprocess invocations per run.

**US-2 — AOD-Kit maintainer debugging a substitution-helper regression.**
> As a maintainer triaging a substitution failure, I want a unit test that fails with a precise, helper-scoped stack trace, not a 8 MB integration-test stderr blob from a full init.sh run. After the hot-fix, a regression in `aod_template_substitute_placeholders` lights up `test_template_substitute_unit.py::case_1_ampersand` directly; a regression in `aod_init_read_validated` lights up `test_init_input_unit.py::case_9_multiline`. Root cause is named in the test ID.

---

## Success Metrics

Quantitative measurements that validate the hot-fix landed correctly. All metrics are observed on the first post-merge CI run:

| Metric | Baseline (CI run 25314246672) | Target |
|---|---|---|
| Per-case wall time (cases 1-12) | 180-258s (integration, with timeout failures) | ≤2s (unit) |
| Total init.sh-suite wall time on `macos-latest` | 30-40 min (with 300s timeouts) | ≤15 min |
| init.sh subprocess invocations per CI run | 17 (13 adversarial + 4 other init-touching tests) | 5 (1 adversarial smoke + 4 other) |
| `macos-latest` matrix green-rate over next 5 runs | 1/5 historical (4 macos timeouts in F-248 cycle) | 5/5 |
| `ubuntu-latest` matrix green-rate over next 5 runs | 5/5 historical | 5/5 (unchanged) |
| CI savings vs. baseline (single run, summed across both legs) | n/a | ≥25 minutes |

---

## Architect Technical Baseline

> The following is the architect baseline (`.aod/results/architect-baseline.md`) embedded verbatim. It documents helper-extraction shape, test architecture, regression-protection guarantee, CI-matrix risk, backwards-compatibility constraint, and the risk register. Sections below this one (Acceptance Criteria, Risks, Stakeholders) reference these decisions.

**Issue**: #250 hot-fix — extract adversarial cases 1-12 from `tests/scripts/test_init_sh_adversarial.py` into a unit-level pytest module that calls `aod_template_substitute_placeholders` and `aod_init_read_validated` directly, eliminating 12 of the 17 init.sh subprocess invocations per CI run.

### 1. Helper extraction shape

**Decision**: per-case `subprocess.run(["bash", "-c", "<source+invoke>"], ...)`, with the invocation wrapped to use **process substitution** (`< <(printf ...)`) — *not* shell pipes — for `aod_init_read_validated` cases.

**Rationale**: empirical timings on local bash 3.2.57 show a single substitution call cold-starts at ~52ms wall (0.01s user / 0.03s sys); `aod_init_read_validated` runs in ~9ms. Both are 20-200× under the ≤2s/case target with order-of-magnitude headroom for macos-latest's documented 3-4× slowdown. No need for `bash -i` interactive-shell complexity, no need for a long-running bash co-process, no need for session-scoped fixtures (out of scope per Issue #250).

**Critical constraint surfaced during baseline analysis**: `aod_init_read_validated` writes to caller scope via `printf -v "$var_name"`. When invoked via a shell pipe (`printf input | aod_init_read_validated ...`), bash runs the rightmost pipeline element in a subshell and the caller-scope assignment is lost — the function returns RC=0 but `result=""`. The unit tests **must** use process substitution `aod_init_read_validated "P: " result 100 < <(printf '%s\n' "$INPUT")` to keep the function in the parent shell and observe the assignment. Validated empirically against bash 3.2.57; identical semantics on bash 5.x. This pattern is also the only way to reach the 3-strike exit path correctly (an EOF after a single bad line on a pipe yields a misleading RC=0 because the second prompt sees EOF → empty input → accepted).

**Bash 3.2 vs 5.x compatibility**: `template-substitute.sh` already issues `shopt -u patsub_replacement 2>/dev/null || true` at source time (the F-248 fix). Process substitution is bash 2.04+ — safe everywhere. `printf -v` is bash 3.1+ — safe. No new compatibility surface introduced.

### 2. Test architecture

**Two modules**, splitting on dependency:

- `tests/scripts/test_template_substitute_unit.py` — 8 cases (1-8). Source `template-substitute.sh`, set the 12 `AOD_PERSONALIZATION_*` env vars, write a 1-line src file containing `tachi`, invoke `aod_template_substitute_placeholders src dest`, then **byte-verify** by sourcing the dest's contents back through bash `printf '%s'` — mirroring the existing test's round-trip pattern at line 138 (defends against false-positive byte mismatches when shell metachars appear in input). Uses `tmp_path` (function-scoped pytest fixture) — no clone, no `clone_into_tmpdir`, no `init_sh_helpers` import.

- `tests/scripts/test_init_input_unit.py` — 4 cases (9-12). Source `init-input.sh`, invoke `aod_init_read_validated` via process substitution. For rejection cases, feed 3 copies of the bad input + assert exit 1 with the named reason class in stderr.

**Why two files, not one**: each file mirrors one helper's contract surface; failures localize cleanly; the two helpers have different fixtures (substitution needs a temp src file, input validation only needs a string). One pytest collection, two `.py` modules, no shared imports beyond `subprocess` + `pathlib`.

**No tmpdir at all for test_init_input_unit.py** — the validator operates purely on stdin and writes to a shell variable; no filesystem touch needed.

### 3. Regression-protection guarantee

**The 6 sed-metachar cases are load-bearing**: they detect the `AT&T → ATtachiT` corruption from the pre-F-248 sed era and the parallel `patsub_replacement` regression on bash 5.x.

**Argument that direct helper invocation preserves detection**: `aod_template_substitute_placeholders` *is* the function `scripts/init.sh` calls; the integration test merely wraps it in 16 unrelated initialization steps (gh auth, manifest read, file walk, etc.). The 6 substitution-semantics cases are 100% bounded by the substitution helper's behavior — none of the surrounding init.sh logic affects whether `${content//\{\{PROJECT_NAME\}\}/AT&T}` resolves to `AT&T` or `ATtachiT`. Calling the helper directly with `AOD_PERSONALIZATION_PROJECT_NAME="AT&T"` reproduces the exact bash parameter expansion under exactly the same `shopt` state set at source-time. **Higher detection sensitivity**, not lower: integration-mode failures bury the substitution-semantic root cause under 8MB of init.sh stderr; unit-mode failures pinpoint the helper directly.

**Belt-and-suspenders integration smoke**: case 13 (trailing-newline byte-identity) stays in `test_init_sh_adversarial.py` and continues to exercise the full init.sh path with one realistic project name. Combined with `test_init_sh_substitution.py` (Test-1 fixture-replay), `test_no_residual_placeholders_after_init`, and the bash-version diagnostic step in the workflow, integration coverage is preserved at exactly the F-248 level minus 12 redundant adversarial repetitions.

### 4. CI matrix risk

**Runtime determinism**: unit tests run in ≤200ms wall on dev hardware; even with 4× macos-latest slowdown, total suite cost is sub-second per case. No timeout knobs need bumping. Recommend pytest `--timeout=15` for the new modules (vs the integration suite's 360s) — fast-fail surface for any subprocess hang regressions.

**Env-var pinning**: the substitution unit tests do **not** need `AOD_RATIFICATION_DATE_OVERRIDE` / `AOD_CURRENT_DATE_OVERRIDE` because they bypass init.sh date capture entirely — values are set explicitly per test. No tz-skew false-fail surface. Recommend setting `LC_ALL=C` in the per-case `subprocess.run(env=...)` to match the F-248 baseline locale and avoid UTF-8 multibyte behavior drift on case 6 (Ⅷ-Ⅸ U+2160 range).

**`shopt -u patsub_replacement` shim**: every per-case `bash -c "source helpers; ..."` call re-sources `template-substitute.sh`, which means the shim runs on every invocation. Both bash 3.2 (where the shopt is unknown) and bash 5.x (where the default is *on* and we explicitly disable it) are exercised on every case. This is **stronger** coverage than the current integration suite, which sources the helper once per init.sh run.

### 5. Backwards-compatibility constraint

`test_init_sh_adversarial.py` retains:
- `test_case_13_file_level_byte_identity` (lines 165-227) — unchanged
- `test_no_residual_placeholders_after_init` (lines 229-288) — unchanged
- The shared `from init_sh_helpers import build_canonical_stdin, clone_into_tmpdir, run_init_in_clone` block — unchanged (case 13 still uses these)

Deleted: lines 41-162 (the `ADVERSARIAL_CASES` table, the `_ids` helper, the `adversarial_run` fixture, the `test_adversarial_input` parametrized test). This is a contiguous block — clean delete, no surrounding fixture machinery cross-references.

`tests/scripts/init_sh_helpers.py` is **untouched**. Both new unit modules are standalone and do not import from it.

### 6. Risk register

| ID | Risk | Severity | Likelihood | Mitigation |
|----|------|----------|------------|------------|
| R-1 | Pipe-subshell trap: `aod_init_read_validated` silently fails to assign in caller scope when invoked via shell pipe → unit tests "pass" while validating nothing | **HIGH** | High if not flagged in tasks.md | Mandate process-substitution pattern (`< <(printf ...)`) in the test file's module docstring; first task for the test author is a positive-path canary that asserts `result` is non-empty after a known-good input. |
| R-2 | macos-latest still flakes on cold-cache subprocess spawn even at ~50ms baseline (F-248 history) | MEDIUM | Low (baseline is 50× under target) | Keep pytest `--timeout=15` outer cap; if a single case ever hits >5s on CI, escalate to session-scoped fixture (deferred Issue #250 backlog). |
| R-3 | Test-1 (`test_init_sh_substitution.py` fixture-replay) still needs init.sh — total CI savings <25min if Test-1 is the long pole | MEDIUM | Medium | Out of this PRD's scope (deferred Path C). The 12-case extraction alone removes ~36-50 minutes of subprocess time (12 × 180-258s); even with Test-1 unchanged, target ≥25 min savings is achieved. Verify with a one-shot post-merge CI timing sample. |
| R-4 | Case 6 (Ⅷ-Ⅸ multibyte UTF-8) drift between LC_ALL=C in the new test vs LC_ALL=en_US.UTF-8 in dev shells could mask a regression on the runner | LOW | Low | Pin `LC_ALL=C` in per-case `subprocess.run(env=...)`; document the rationale inline (mirrors `init_sh_helpers.run_init_in_clone` line 137). The substitution helper uses bash parameter expansion which is byte-literal, not locale-aware — but standardizing avoids future surprise. |
| R-5 | Unit tests pass but a future init.sh refactor changes how the helper is invoked (e.g., added pre-validation step), so the unit-tested helper diverges from production behavior | LOW | Low | Case 13 + Test-1 still exercise init.sh end-to-end on every CI run; any drift between unit-tested helper and integrated behavior surfaces in those two integration tests. The two-layer protection (unit + smoke) is the deferred backstop. |

**Pre-mortem lens summary**: F-248's three baseline-staleness incidents all stemmed from integration-test fragility (cold-cache timeouts, locale drift, fixture tree size). The hot-fix moves regression detection to the most stable test layer possible — pure helper invocation with deterministic stdin. The dominant residual risk is R-1 (pipe-subshell), which is structurally unavoidable in pytest-driven shell-function testing and must be encoded in the test pattern explicitly.

---

## Acceptance Criteria

Each criterion below maps to one or more goals (G-1..G-6) and is independently testable on the post-merge CI run.

- **AC-1** (G-1): Every test in `tests/scripts/test_template_substitute_unit.py` and `tests/scripts/test_init_input_unit.py` completes in ≤2 seconds wall time on `macos-latest` per the pytest `--durations=0` summary. The pytest `--timeout=15` per-module cap fast-fails any drift.
- **AC-2** (G-2, G-3): Total wall time of the init.sh suite on `macos-latest` is ≤15 minutes, measured by the GitHub Actions step duration on the post-merge run. Compared to CI run `25314246672`, the delta is ≥25 minutes. A single one-shot timing sample on the merge commit is sufficient evidence.
- **AC-3** (G-4): The post-merge CI run is green on both `macos-latest` and `ubuntu-latest`. No admin-override merge is required to land this hot-fix.
- **AC-4** (G-5): A repository-wide grep for `run_init_in_clone\|clone_into_tmpdir\|init_sh_helpers\|scripts/init.sh` in `tests/scripts/` shows that the new files (`test_template_substitute_unit.py`, `test_init_input_unit.py`) contain **zero** references to those identifiers. The `init_sh_helpers` term enforces architect baseline §2's "no shared imports" mandate. The integration-smoke remnant in `test_init_sh_adversarial.py` (case 13 + `test_no_residual_placeholders_after_init`) retains exactly the same invocation count it had before the hot-fix.
- **AC-5** (G-6): Substitution-semantics regression detection is verified by a deliberate-fault check spanning **all six** sed-metachar cases (1: ampersand `AT&T`, 2: pipe `foo|bar`, 3: backref `\1\2`, 4: single-quoted, 5: double-quoted, 6: multibyte UTF-8 `Ⅷ-Ⅸ`). Removing the `shopt -u patsub_replacement 2>/dev/null || true` shim from `.aod/scripts/bash/template-substitute.sh` on bash 5.x **must** cause **at least cases 1, 3, and 6 of `test_template_substitute_unit.py`** to fail with non-zero exit and stderr messages naming corrupted byte sequences (the three cases bash's `patsub_replacement` is documented to mishandle). Cases 2, 4, 5 are required to *pass* under the fault state — confirming they are independent of the shim and exercise pure parameter expansion. This six-case verification matrix is run once locally on bash 5.x as part of validation; it is not a permanent CI step. The matrix output (PASS/FAIL per case) is recorded in the validation log for audit.
- **AC-6** (architect baseline §5): The `tests/scripts/test_init_sh_adversarial.py` file retains `test_case_13_file_level_byte_identity` (lines 165-227) and `test_no_residual_placeholders_after_init` (lines 229-288) byte-unchanged; the `init_sh_helpers` import block is unchanged; only lines 41-162 (the `ADVERSARIAL_CASES` table and parametrized adversarial test) are deleted. `tests/scripts/init_sh_helpers.py` is unmodified.
- **AC-7** (architect baseline §6, R-1): The first test in `test_init_input_unit.py` is a positive-path canary asserting that a known-good input round-trips through `aod_init_read_validated` and produces a non-empty `result` — guarding against the pipe-subshell silent-pass trap.
- **AC-8** (release trigger): The hot-fix PR title is Conventional-Commits-formatted as `fix(250): extract adversarial unit tests — eliminate cold-cache CI flake`. Belt-and-suspenders release verification per `.claude/rules/git-workflow.md`: post-merge `gh pr list --state open --search "release-please"` returns an open release-please PR within ~30s; if not, push an empty `fix(250):` release-marker commit.

---

## Risks & Open Questions

The architect baseline §6 enumerates the full risk register (R-1 through R-5). Product-tagging the load-bearing risks:

- **R-1 (HIGH, promoted to top-level product risk)** — *Pipe-subshell trap*. The `aod_init_read_validated` helper writes via `printf -v` to caller scope, which is silently lost when the function is invoked through a shell pipe. Unit tests using the wrong invocation pattern would return RC=0 with empty result and pass while validating nothing — a false-negative that defeats the entire hot-fix. **Mitigation (mandatory in tasks.md)**: process substitution (`< <(printf ...)`) is the only sanctioned invocation pattern; AC-7 codifies the canary test that fails fast if the pattern is broken.

- **R-3 (MEDIUM, scope boundary)** — *Test-1 long pole*. If `test_init_sh_substitution.py` is the dominant remaining CI cost, the ≥25-minute savings target may be tight. Architect baseline §6 calculates the 12-case extraction alone removes 36-50 minutes of subprocess time, clearing the target with margin — but a one-shot post-merge CI timing measurement is required to confirm.

**Tasks.md-level concerns** (carried forward from Triad reviews; addressed in the Plan stage, not in this PRD):

- **TC-1** (Architect): No permanent CI canary asserts the `shopt -u patsub_replacement` shim stays in place — a future cleanup PR could remove it without immediate signal. Tasks.md should consider adding a one-line CI smoke that asserts the shim line still exists.
- **TC-2** (Architect): The baseline CI run `25314246672` should be URL+SHA pinned in tasks.md with measured minutes recorded, so the `≥25min savings` claim has a defensible reference point post-merge.
- **TC-3** (Team-Lead): Atomic-PR ordering — the three steps (substitute-unit module → input-unit module → delete-block from adversarial.py) must merge as a single PR. A partial merge between steps 2 and 3 leaves both old and new tests in-tree, doubling CI cost on intermediate commits.
- **TC-4** (Team-Lead): MUST_NOT scope fences for the build agent — no helper modification, no `init_sh_helpers.py` restructure, no new adversarial cases beyond the 12 extracted, no touch on case 13.

**Open Questions (product side)**:

- **OQ-1**: Should the deleted adversarial-cases block be preserved as a comment in `test_init_sh_adversarial.py` for git-blame archaeology, or is clean delete preferred (architect baseline §5 default)? **PM stance**: clean delete; git history retains the table content. Architect to adjudicate in spec.md if a different stance is needed.

- **OQ-2**: Is `fix(250):` the right Conventional-Commits prefix? The change ships no user-visible feature and no security closure — `fix:` matches the "CI-stability fix" semantic. **PM stance**: `fix(250):` is correct; the change is invisible to adopters except as faster CI. Confirmed in tasks.md.

---

## Stakeholders & Sign-Offs

- **Product Manager**: product-manager — APPROVED 2026-05-04 (PRD body authored, architect baseline embedded verbatim, three architect concerns addressed inline before finalization)
- **Architect**: architect — APPROVED_WITH_CONCERNS 2026-05-04 (baseline at `.aod/results/architect-baseline.md`; final review at `.aod/results/architect-final-review.md`; technical concerns AC-4/AC-5/header-dup addressed inline; R-6/R-7 flagged as TC-1/TC-2 for tasks.md)
- **Team Lead**: team-lead — APPROVED_WITH_CONCERNS 2026-05-04 (review at `.aod/results/team-lead-review.md`; size S, 4-6 wall hours; tasks.md-level concerns captured as TC-3/TC-4)
- **Implementation owner**: TBD (assigned in `agent-assignments.md` during `/aod.tasks`)
- **Reviewer**: code-reviewer — post-build review per `/aod.build` Step 5

**Sign-off matrix per `.claude/rules/governance.md`**: spec.md (PM), plan.md (PM + Architect), tasks.md (PM + Architect + Team-Lead). This PRD seeds the spec stage.
