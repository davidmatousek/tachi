---
spec_reference: specs/250-adversarial-unit-extraction-hotfix/spec.md
prd_reference: docs/product/02_PRD/250-adversarial-unit-extraction-hotfix-2026-05-04.md
adr_reference: docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-04
    status: APPROVED
    notes: "PRD G-1..G-6 each map to ≥1 plan §Components/§Data Flow/§Tech Stack item; spec FR-001..FR-022 fully covered; NG-1..NG-3 honoured. §Atomic-PR delivery flow encodes TC-3; UNCHANGED annotations fence TC-4; TC-1/TC-2 forward-flagged to tasks.md. fix(250): prefix preserved across plan. US-1 and US-2 served by chosen approach. Audit at .aod/results/pm-plan-review-250.md."
  architect_signoff:
    agent: architect
    date: 2026-05-04
    status: APPROVED
    notes: "Architect Technical Baseline §1-§6 preserved verbatim. R-1 process-substitution mandate encoded at five loci (FR-006/FR-007, plan §Components, contracts/, data-model schema, quickstart §7). Two-module split with zero init_sh_helpers import via FR-003 + quickstart grep. Six-case shim fault matrix preserved (FR-010/SC-006). Bash 3.2/5.x shim guard intact. Zero new deps/toolchain. Constitution principles I/III/VI/VII/IX/X/XI pass with VI strengthening. TC-1..TC-4 carried forward. ADR-038 §D-1/§D-5/§D-6 untouched. One informational tasks.md note: architect baseline cites init_sh_helpers:137 but live offset is :135 — applied. Audit at .aod/results/architect-plan-review-250.md."
  techlead_signoff: null
---

# Implementation Plan: Adversarial Unit Extraction Hot-Fix

**Branch**: `250-adversarial-unit-extraction-hotfix` | **Date**: 2026-05-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/250-adversarial-unit-extraction-hotfix/spec.md`
**PRD**: `docs/product/02_PRD/250-adversarial-unit-extraction-hotfix-2026-05-04.md`
**ADR Reference**: `docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md` (Accepted 2026-05-04)

## Summary

Surgical CI-stability hot-fix that extracts adversarial cases 1–12 from `tests/scripts/test_init_sh_adversarial.py` into two unit-level pytest modules invoking `aod_template_substitute_placeholders` and `aod_init_read_validated` directly via `subprocess.run` with process-substitution. Case 13 (trailing-newline byte-identity) and `test_no_residual_placeholders_after_init` stay in place as the integration backstop. The hot-fix eliminates 12 of the 17 init.sh subprocess invocations per CI run, targeting ≥25 minutes of CI savings and ≤15 minutes total wall time on `macos-latest`. No bash helpers are modified; `init_sh_helpers.py` is untouched. The PR ships atomically as `fix(250):` to trigger a release-please patch bump.

## Technical Context

**Language/Version**: Python 3.9+ (CI pins 3.11) — `pyproject.toml:requires-python`
**Primary Dependencies**: pytest ≥8.0, pytest-timeout (already in CI image)
**Shell Runtime**: bash 3.2.57 (macOS gate) and bash 5.x (Linux); both supported. Process substitution `< <(...)` is bash 2.04+; `printf -v` is bash 3.1+; `shopt -u patsub_replacement` is guarded with `2>/dev/null || true` for bash 3.2 compatibility.
**Storage**: N/A — no filesystem state beyond function-scoped pytest `tmp_path` for substitution cases. Input-rejection cases touch no filesystem.
**Testing**: pytest with parametrize, `--durations=0` for wall-time observation, `--timeout=15` per-module cap, `subprocess.run` for bash-helper invocation
**Target Platform**: GitHub Actions `macos-latest` and `ubuntu-latest` matrix legs (CI workflow `tachi-pytest.yml`)
**Project Type**: methodology template — test-tree-only hot-fix; no application code changes
**Performance Goals**: ≤2s wall time per case (down from 180–258s); ≤15 min total init.sh-suite wall time on `macos-latest` (down from 30–40 min); ≥25 min total CI savings per run
**Constraints**: zero new init.sh invocations; zero modifications to `.aod/scripts/bash/`; zero modifications to `tests/scripts/init_sh_helpers.py`; case 13 + `test_no_residual_placeholders_after_init` byte-unchanged
**Scale/Scope**: 12 case extractions across 2 new modules (8 + 4); 1 deletion block (lines 41–162) in 1 existing module

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution version: 1.0.0 | Active tier: `standard`

### Principle-by-principle review

| Principle | Status | Justification |
|-----------|--------|---------------|
| I. General-Purpose Architecture | ✅ Pass | Hot-fix is on test tree only. No domain-specific logic introduced. |
| II. API-First Design | ✅ N/A | No API surface affected. |
| III. Backward Compatibility (NON-NEGOTIABLE) | ✅ Pass | Pre-hot-fix integration coverage preserved exactly: case 13 + Test-1 + `test_no_residual_placeholders_after_init` + bash-version diagnostic step are byte-unchanged. Local `.aod/` workflows and adopter forks see only faster CI. |
| IV. Concurrency & Data Integrity | ✅ N/A | No state transitions, no locking, no shared filesystem. Each test uses function-scoped `tmp_path` (or no filesystem for input-rejection cases). |
| V. Privacy & Data Isolation | ✅ N/A | No user data, no auth, no cross-tenant surface. |
| VI. Testing Excellence (NON-NEGOTIABLE) | ✅ Pass with strengthening | The hot-fix moves 12 cases from integration to unit, raising helper-scoped test coverage from 1 (case 13) to 13 cases per CI run. Coverage thresholds (80% unit) are maintained — the helpers under test are 100% coverage either way. Per-case wall time drops from 180–258s to ≤2s, clearing the API-response-time analogue (<500ms tier) by 2 orders of magnitude. |
| VII. Definition of Done (NON-NEGOTIABLE) | ✅ Pass | Plan defines: (1) deployment = squash-merge to `main` triggering release-please patch bump; (2) tested = post-merge CI green on both matrix legs + deliberate-fault verification matrix on bash 5.x; (3) user-validated = adopter (US-1) and maintainer (US-2) flows confirmed by 5/5 green-rate observation over post-merge runs. |
| VIII. Observability & Root Cause Analysis | ✅ Pass | The hot-fix itself was discovered via 5 Whys analysis (PRD §Background). The new unit failures emit helper-scoped stderr (vs 8MB integration blob), strengthening observability. Lessons captured in F-248 KB Entry 1 are operationalised here. |
| IX. Git Workflow & Feature Branching (NON-NEGOTIABLE) | ✅ Pass | Branch `250-adversarial-unit-extraction-hotfix` exists and tracks origin. Draft PR #253 already opened. Atomic single-PR delivery per FR-017 / TC-3. PR title `fix(250): extract adversarial unit tests — eliminate cold-cache CI flake` matches Conventional Commits. |
| X. Product-Spec Alignment & Architecture Review (NON-NEGOTIABLE) | ✅ Pass | PRD has triple Triad sign-off (PM ✓ + Architect ⚠ + Team-Lead ⚠). spec.md has PM ✓. plan.md will receive PM + Architect dual sign-off (this gate). tasks.md will receive triple sign-off. |
| XI. SDLC Triad Collaboration | ✅ Pass | Architect baseline embedded verbatim in PRD §Architect Technical Baseline. Tech-Lead concerns (TC-3, TC-4) carried forward to tasks.md. |

**Gate result**: ✅ All principles pass. No violations to track in §Complexity Tracking.

## Project Structure

### Documentation (this feature)

```
specs/250-adversarial-unit-extraction-hotfix/
├── plan.md                          # This file
├── spec.md                          # Feature specification (PM ✓)
├── research.md                      # Phase 0: research grounding
├── data-model.md                    # Phase 1: case data structure
├── quickstart.md                    # Phase 1: how to run + verify
├── contracts/
│   ├── aod_template_substitute_placeholders.md  # Helper contract under test
│   └── aod_init_read_validated.md               # Helper contract under test
├── checklists/
│   └── requirements.md              # Spec quality checklist (passed)
└── tasks.md                         # /aod.tasks output (triple sign-off)
```

### Source Code (repository root)

```
tachi/
├── tests/
│   └── scripts/
│       ├── test_template_substitute_unit.py     # NEW — 8 cases (substitution semantics)
│       ├── test_init_input_unit.py              # NEW — 4 cases (input rejection) + canary
│       ├── test_init_sh_adversarial.py          # MODIFIED — delete lines 41–162; preserve 1–39, 165–227, 229–288
│       ├── test_init_sh_constitution.py         # UNCHANGED
│       ├── test_init_sh_self_delete.py          # UNCHANGED
│       ├── test_init_sh_substitution.py         # UNCHANGED (Test-1 long pole, Path C deferred)
│       ├── init_sh_helpers.py                   # UNCHANGED (FR-021, TC-4 fence)
│       └── conftest.py                          # UNCHANGED
├── .aod/
│   └── scripts/
│       └── bash/
│           ├── template-substitute.sh           # UNCHANGED (FR-019, TC-4 fence) — line 64 shim load-bearing
│           └── init-input.sh                    # UNCHANGED (FR-019, TC-4 fence)
└── pyproject.toml                               # UNCHANGED (testpaths, markers already correct)
```

**Structure Decision**: Tachi is a methodology template, not an application — the hot-fix lives entirely in `tests/scripts/`. No `src/`, `backend/`, `frontend/`, or `api/` layout applies. The single project structure (Option 1) is the closest match, scoped to the test tree only.

## Components

### Component 1: `test_template_substitute_unit.py` (new)

**Responsibility**: Cover adversarial substitution-semantics cases 1–8 by invoking `aod_template_substitute_placeholders` directly.

**Inputs**:
- 12 `AOD_PERSONALIZATION_*` env vars per case (one per template variable; case-specific values for `AOD_PERSONALIZATION_PROJECT_NAME`)
- 1-line src file at `tmp_path/src` containing exactly `{{PROJECT_NAME}}\n`

**Operation**: per case, `subprocess.run(["bash", "-c", "shopt -u patsub_replacement 2>/dev/null||true; source .aod/scripts/bash/template-substitute.sh; aod_template_substitute_placeholders <src> <dest>"], env=..., timeout=15, capture_output=True, text=True)`. Then byte-verify dest contents against expected literal.

**Coverage**: cases 1 (ampersand `AT&T`), 2 (pipe `foo|bar`), 3 (backref `\1\2`), 4 (single-quoted), 5 (double-quoted), 6 (multibyte `Ⅷ-Ⅸ`), 7 (newline-in-value), 8 (empty-value).

**No imports from `init_sh_helpers.py`**. Function-scoped `tmp_path` only.

### Component 2: `test_init_input_unit.py` (new)

**Responsibility**: Cover adversarial input-rejection cases 9–12 by invoking `aod_init_read_validated` directly via process substitution.

**Inputs**: per case, a string fed via `< <(printf '%s\n' "$INPUT")`. For 3-strike rejection cases, 3 copies of the bad input.

**Operation**: per case, `subprocess.run(["bash", "-c", "set -euo pipefail; source .aod/scripts/bash/init-input.sh; result=''; aod_init_read_validated 'P: ' result 100 < <(printf '%s\\n' \"$INPUT\"); declare -p result"], env={"LC_ALL":"C","PATH":...,"INPUT":"..."}, timeout=15, capture_output=True, text=True)`. Then assert on `result` value (positive cases) or exit code 1 + named reason class on stderr (rejection cases).

**Module-load canary** (FR-007): the **first** test collected is `test_canary_positive_path` — a known-good input round-trips and produces non-empty `result`. If process substitution is broken (regression introduces a pipe), the canary fails fast.

**Coverage**: case 0 (canary, positive), case 9 (empty), case 10 (multiline), case 11 (disallowed-character class A), case 12 (disallowed-character class B).

**No filesystem touch**. **No imports from `init_sh_helpers.py`**.

### Component 3: `test_init_sh_adversarial.py` (modified)

**Responsibility unchanged**: integration backstop for case 13 (trailing-newline byte-identity) and `test_no_residual_placeholders_after_init`.

**Surgical change**: delete lines 41–162 (the `ADVERSARIAL_CASES` table, the `_ids` helper, the `adversarial_run` fixture, the `test_adversarial_input` parametrized test). Lines 1–39 (imports, including `from init_sh_helpers import ...`), 165–227 (case 13), and 229–288 (`test_no_residual_placeholders_after_init`) remain byte-unchanged.

**Verification**: `git diff` against parent commit shows exactly one contiguous deletion block; no additions; no whitespace changes outside that block.

## Data Flow

### Per-case test invocation flow (test_template_substitute_unit.py)

```mermaid
sequenceDiagram
    participant Pytest
    participant Subprocess
    participant Bash as bash 3.2/5.x
    participant Helper as aod_template_substitute_placeholders
    participant TmpFS as tmp_path

    Pytest->>Pytest: parametrize → case dict (env, src_content, expected)
    Pytest->>TmpFS: write src file ({{PROJECT_NAME}}\n)
    Pytest->>Subprocess: run(bash -c "source helper; aod_template_substitute_placeholders src dest", env=..., timeout=15)
    Subprocess->>Bash: spawn shell with LC_ALL=C, PATH, AOD_PERSONALIZATION_*
    Bash->>Bash: shopt -u patsub_replacement (no-op on 3.2)
    Bash->>Helper: source template-substitute.sh
    Helper->>TmpFS: read src
    Helper->>Helper: bash parameter expansion ${content//{{PROJECT_NAME}}/AT&T}
    Helper->>TmpFS: write dest
    Bash->>Subprocess: exit 0
    Subprocess->>Pytest: stdout, stderr, returncode
    Pytest->>TmpFS: read dest
    Pytest->>Pytest: assert dest == expected (byte-identical)
```

### Per-case test invocation flow (test_init_input_unit.py)

```mermaid
sequenceDiagram
    participant Pytest
    participant Subprocess
    participant Bash as bash 3.2/5.x
    participant Helper as aod_init_read_validated
    participant Stdin as process-substitution stdin

    Pytest->>Pytest: parametrize → case dict (input, expected_result, expected_rc, expected_reason)
    Pytest->>Subprocess: run(bash -c "source helper; aod_init_read_validated 'P: ' result 100 < <(printf '%s\n' \"$INPUT\"); declare -p result", env={LC_ALL=C, INPUT=...}, timeout=15)
    Subprocess->>Bash: spawn shell
    Bash->>Helper: source init-input.sh
    Helper->>Stdin: read line via process substitution
    Note over Helper,Stdin: Process substitution keeps Helper in parent shell;<br/>printf -v "$var_name" assignment IS observable.<br/>Pipe would lose the assignment (R-1 trap).
    Helper->>Helper: validate via regex; reject or printf -v result
    alt input accepted
        Helper->>Bash: declare -p result → "declare -- result=<value>"
        Bash->>Subprocess: exit 0
    else 3 strikes rejected
        Helper->>Bash: stderr "ERR: <reason class>"
        Bash->>Subprocess: exit 1
    end
    Subprocess->>Pytest: stdout, stderr, returncode
    Pytest->>Pytest: assert returncode == expected_rc
    Pytest->>Pytest: assert <result value> in stdout (positive) or <reason class> in stderr (negative)
```

### Atomic-PR delivery flow

```mermaid
flowchart LR
    A[branch: 250-adversarial-unit-extraction-hotfix] --> B[Step 1: add test_template_substitute_unit.py]
    B --> C[Step 2: add test_init_input_unit.py]
    C --> D[Step 3: delete lines 41-162 from test_init_sh_adversarial.py]
    D --> E[push to draft PR #253]
    E --> F[mark PR ready]
    F --> G[squash-merge with title fix(250): ...]
    G --> H[release-please opens patch-bump PR within ~30s]
    H --> I[v4.28.X released]
```

**Critical invariant** (TC-3): all three steps merge as **one** PR. Intermediate states (Step 1+2 without Step 3, or Step 3 without Steps 1+2) leave the test tree in an incoherent doubled-CI or zero-coverage state.

## Tech Stack

| Layer | Choice | Version | Rationale |
|-------|--------|---------|-----------|
| Test runner | pytest | ≥8.0 | Already the project standard (`pyproject.toml`); supports parametrize + `--timeout` + `--durations=0`. |
| Test invocation | `subprocess.run` (stdlib) | Python 3.9+ stdlib | Zero new dependency. Mirrors existing pattern in `init_sh_helpers.run_init_in_clone`. |
| Per-test timeout | `pytest-timeout` (already CI-installed) + per-call `timeout=15` | Already in CI | Two-layer cap: outer pytest-timeout for total module bound, inner `subprocess.run(timeout=15)` for fast-fail on subprocess hang. |
| Locale | `LC_ALL=C` per call | n/a | Matches `init_sh_helpers.run_init_in_clone:135` baseline; prevents locale drift on multibyte case 6. |
| Shell | bash 3.2.57 (macOS) + bash 5.x (Linux) | Existing CI image | Process substitution and `printf -v` available on both; `shopt -u patsub_replacement` already guarded with `2>/dev/null \|\| true`. |
| Helper invocation pattern | `< <(printf ...)` (process substitution) | bash 2.04+ | Only sanctioned pattern that preserves `printf -v` caller-scope assignment for `aod_init_read_validated` (R-1 mitigation). |
| Release tooling | release-please | already configured | `fix(250):` PR-title prefix triggers patch-bump release. |
| CI matrix | GitHub Actions: `[macos-latest, ubuntu-latest]` | unchanged | Both legs must be green; matrix unchanged from F-248 baseline. |

**No new dependencies**. **No new toolchain**. **No new CI step**. The hot-fix is purely a test-tree reorganisation that obeys the existing dependency surface.

## Phase 0: Outline & Research

Phase 0 was completed during `/aod.spec` and is captured in [research.md](./research.md). All NEEDS CLARIFICATION markers were resolved during PRD authoring (PRD has triple Triad sign-off). Key decisions:

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Helper invocation pattern | per-case `subprocess.run(["bash", "-c", "<source+invoke>"])` | Empirical timings: 52ms cold-start for substitute, 9ms for input-validate. 20–200× under ≤2s target. |
| Pipe vs process substitution for `aod_init_read_validated` | **Process substitution** `< <(printf ...)` (R-1 mandatory mitigation) | Pipe runs rightmost element in subshell → `printf -v` caller-scope write silently lost → false-pass. Process substitution keeps function in parent shell. |
| Module split | **Two modules** (substitute + input) | Each mirrors one helper's contract; failures localise; different fixtures (substitute needs `tmp_path`, input does not). |
| Locale pinning | `LC_ALL=C` per call | Mirrors F-248 baseline at `init_sh_helpers.run_init_in_clone:135`; prevents multibyte UTF-8 case 6 drift. |
| Per-test timeout | pytest `--timeout=15` outer + `subprocess.run(timeout=15)` inner | Two-layer fast-fail. 15s vs 180–258s integration baseline = 12× headroom even on macos-latest 4× slowdown. |
| Tasks.md authority on remaining concerns | TC-1 (shim canary), TC-2 (baseline URL+SHA pin), TC-3 (atomic-PR ordering), TC-4 (MUST_NOT fences) | All four flagged forward in spec; tasks.md will resolve. |

**Output**: [research.md](./research.md) is complete with no outstanding NEEDS CLARIFICATION.

## Phase 1: Design & Contracts

### Data model

The "data" in this feature is the parametrize-table entry per test case. See [data-model.md](./data-model.md) for the full schema (CaseDict shape: id, input, env_overrides, expected_result, expected_rc, expected_reason_class, marker).

### API contracts

The bash helpers `aod_template_substitute_placeholders` and `aod_init_read_validated` are the contracts under test. Their full specifications live in [contracts/](./contracts/) and reference the canonical source: `docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md`.

### Quickstart

[quickstart.md](./quickstart.md) describes how to run the new tests locally, how to run the deliberate-fault verification matrix on bash 5.x, and how to confirm CI green-rate on the post-merge run.

### Agent context update

This is a methodology/test hot-fix; no new technology choice is being introduced. The agent context file (`CLAUDE.md`) does not require update — bash + pytest + subprocess are already the active stack. Skipping `update-agent-context.sh` per the no-new-tech criterion.

## Re-Evaluation: Constitution Check Post-Design

After Phase 1 design completion, re-evaluating gates:

| Principle | Re-check Status | Notes |
|-----------|-----------------|-------|
| VI. Testing Excellence | ✅ Reinforced | Two-layer test split (unit + integration smoke) strengthens helper-scoped coverage. Per-case wall time of ≤2s clears the 80% unit threshold by exercise-frequency. |
| VII. Definition of Done | ✅ Maintained | Quickstart.md documents the manual deliberate-fault verification matrix (FR-010 / SC-006) so the DoD step "Tested" is fully procedural. |
| IX. Git Workflow | ✅ Maintained | Atomic single-PR delivery encoded in §Data Flow → "Atomic-PR delivery flow"; intermediate states forbidden. |
| X. Product-Spec Alignment | ✅ Maintained | All PRD AC-1..AC-8 → spec FR-001..FR-022 → plan §Components, §Data Flow, §Tech Stack are bidirectionally traceable. |

**Re-check result**: ✅ All principles pass post-design. No violations introduced.

## Complexity Tracking

*Empty — no Constitution Check violations require justification.*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | (n/a) | (n/a) |

## Risks & Mitigations

Carried forward from PRD §Architect Technical Baseline §6 risk register, scoped to plan-level mitigations:

| ID | Risk | Severity | Plan-level mitigation |
|----|------|----------|----------------------|
| R-1 | Pipe-subshell trap | HIGH | FR-006 mandates process substitution; FR-007 mandates positive-path canary as the first collected test in `test_init_input_unit.py`. Quickstart.md documents the diagnosis: if canary fails, suspect pipe regression. |
| R-2 | macos-latest cold-cache flake at ~50ms baseline | LOW | `--timeout=15` outer cap + `subprocess.run(timeout=15)` inner cap give 200× headroom. If a single case ever hits >5s on CI, escalate to session-scoped fixture (deferred Path C). |
| R-3 | Test-1 long pole | MEDIUM | Out of scope (NG-1). Architect baseline §6 calculation shows 12-case extraction alone removes 36–50 minutes; ≥25-minute target met with margin. One-shot post-merge timing sample confirms. |
| R-4 | Locale drift on multibyte case 6 | LOW | FR-008 pins `LC_ALL=C` per call. |
| R-5 | Future helper-invocation drift | LOW | Case 13 + Test-1 + `test_no_residual_placeholders_after_init` retained as integration backstop per FR-004. |

**Tasks.md-level concerns** (from spec, awaiting resolution in `/aod.tasks`):

- TC-1 — permanent CI canary for `shopt -u patsub_replacement` shim
- TC-2 — baseline run `25314246672` URL+SHA pin with measured minutes
- TC-3 — atomic-PR ordering enforcement (encoded as merge-order in §Data Flow → "Atomic-PR delivery flow")
- TC-4 — MUST_NOT scope fences for build agent (encoded as plan §Project Structure → "UNCHANGED" annotations + spec FR-019..FR-022)
