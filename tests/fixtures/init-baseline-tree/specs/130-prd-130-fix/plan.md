---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-11
    status: APPROVED
    notes: "Plan faithfully translates PRD rev 1.1 and PM-approved spec into implementation design. All 4 spike decisions (S1/S2/S3/Q130.1) sit inside PRD-authorized option sets. ADR-022 and Tech Stack additions inherited from spec stage. All 7 FR-130.x trace to Deliverables Checklist. 6-location canonical error message list complete. Risk register expansion from 4 to 7 justified by plan-shape-specific risks. Timeline tight — off-budget items (ADR-022, pytest tests, quickstart) roughly match 0.65d buffer, flagged for team-lead at tasks stage. 6 non-blocking observations in .aod/results/product-manager-plan.md."
  architect_signoff:
    agent: architect
    date: 2026-04-11
    status: APPROVED
    notes: "Plan is technically sound and closes all 4 Plan Stage Day 0 spike decisions (S1/S2/S3/Q130.1) with defensible reasoning. Zero blocking concerns; 9 non-blocking refinements (R1-R9) for tasks.md. ADR-014 verified as not covering CLI tools — ADR-022 as separate ADR (not amendment) is correct. Happy-path byte-identity verified by code trace. mermaid-agentic-app is the critical backward-compat target; agentic-app/sample-report correctly stays excluded from baseline set. Defense-in-depth (shell + Python) justified by different invocation paths. R6 High priority: mid-render failure error message format underspecified in plan — tasks.md must require finding ID + file path + failure class + stderr excerpt. Full findings in .aod/results/architect-plan.md."
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: Fix Attack Path Mermaid Rendering When mmdc Is Not Installed

**Branch**: `130-prd-130-fix` | **Date**: 2026-04-11 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/130-prd-130-fix/spec.md`
**PRD**: [docs/product/02_PRD/130-fix-attack-path-mermaid-rendering-2026-04-11.md](../../docs/product/02_PRD/130-fix-attack-path-mermaid-rendering-2026-04-11.md)
**Research**: [research.md](research.md)

## Summary

Turn the tachi security-report pipeline's silent-fallback behavior when `@mermaid-js/mermaid-cli` (`mmdc`) is missing into an immediate, actionable loud failure. The plan delivers seven changes:

1. **Two preflight gates** (defense-in-depth): a shell-level `which mmdc` check in `.claude/commands/tachi.security-report.md` that fires when attack-trees/ contains Critical/High findings, and a Python-level `shutil.which("mmdc")` check at the top of `render_mermaid_to_png()` that raises `RuntimeError` instead of returning silently. Both emit the same one-line install command and both are gated on attack-tree presence.
2. **Deleted dead code** in `scripts/extract-report-data.py:725-730` (silent `has_image=False` path) and `templates/tachi/security-report/attack-path.typ:78-86` (text fallback branch).
3. **Loud mid-render failure**: `render_mermaid_to_png()` aborts the whole pipeline with a non-zero exit code and per-finding error list when any individual attack tree fails to render after the preflight gate has passed (Q130.1 decision: **abort**, not "complete with errors" — simpler and matches the fail-loud contract).
4. **README Prerequisites section** authored as a new top-level section between "What is tachi?" and "Quick Start."
5. **`scripts/install.sh` mmdc check** only — `install.sh` does not currently check Typst (research S2 finding), and adding a Typst check would be scope creep.
6. **Spec 112 sync**: SC-004 inverted, line 135 deleted, research.md line 80 corrected, research.md lines 91-93 rationale block added.
7. **ADR-022 authored** documenting the decision to treat `mmdc` as a hard prerequisite gated on attack-tree detection (first ADR governing CLI-prerequisite posture in tachi).
8. **CI fresh-install test**: new `.github/workflows/tachi-mmdc-preflight.yml` running on `ubuntu-latest` (no custom Docker image needed — `ubuntu-latest` does not have `mmdc` preinstalled). Test runs `/tachi.security-report` on `examples/mermaid-agentic-app/` fixture and asserts non-zero exit with expected stderr.

**Approach**: Bug fix on a known corpus. No data model changes, no new API contracts, no new external dependencies. All changes are modifications or deletions in existing files plus three new files (one ADR, one CI workflow, one quickstart doc).

## Technical Context

**Language/Version**: Python 3.11+ (runtime), Bash (command dispatch), Typst 0.12+ (PDF templating)
**Primary Dependencies** (runtime):
- Python standard library only — `shutil`, `subprocess`, `concurrent.futures`, `tempfile`, `pathlib`, `os`, `sys` (already imported; no new imports needed for the preflight change)
- **External CLI (hard prerequisite when attack-trees/ present)**: `@mermaid-js/mermaid-cli` v11+ (via npm, `mmdc` binary on PATH)
- **External CLI (hard prerequisite always)**: Typst 0.12+
**Primary Dependencies** (dev-time only, per Feature 128):
- pytest >=8.0, pytest-cov >=4.1 (from `requirements-dev.txt`)
**Storage**: N/A — file-based pipeline, no database
**Testing**:
- `pytest` unit tests for the modified `render_mermaid_to_png()` function (mocked `shutil.which`)
- Existing backward-compatibility test in `tests/scripts/test_backward_compatibility.py` validates baseline PDFs under `SOURCE_DATE_EPOCH=1700000000`
- **New CI workflow** `.github/workflows/tachi-mmdc-preflight.yml` runs the pipeline on `examples/mermaid-agentic-app/` in a `PATH` environment that excludes `mmdc` and asserts non-zero exit with expected stderr
**Target Platform**: macOS + Linux + WSL developer machines (for running `/tachi.security-report`); Ubuntu GitHub Actions runners for CI
**Project Type**: Single project — tachi is a command/template/script toolkit, not a web/mobile app
**Performance Goals**:
- Preflight check (`shutil.which` + file-glob on `attack-trees/`) adds <100ms to pipeline startup
- Render time for the happy path (mmdc present) is unchanged — existing `ThreadPoolExecutor(max_workers=4)` at [scripts/extract-report-data.py:772](../../scripts/extract-report-data.py#L772) preserved verbatim
**Constraints**:
- **Runtime zero-Python-dep** (from Feature 128 / Tech Stack doc): `scripts/*.py` must remain stdlib-only. Enforced by FR-130.1 using `shutil.which` (already imported)
- **Reproducible baselines** (from ADR-021): `SOURCE_DATE_EPOCH=1700000000` required for FR-130.6 baseline regeneration
- **No network during pipeline**: preflight check is shell-local only; no HTTP calls to Mermaid.ink or similar rejected alternatives
**Scale/Scope**:
- 7 source file modifications, 3 new files (ADR-022, CI workflow, quickstart.md), 2 baseline regenerations
- 2 attack-tree-bearing examples affected: `examples/agentic-app/sample-report/` (47 trees), `examples/mermaid-agentic-app/` (24 trees)
- Estimated code diff: ~50 LOC added (preflight checks, exception raising, CI workflow), ~15 LOC deleted (silent fallback paths in Python + Typst)

## Plan Stage Day 0 Spike — Resolved

The PRD explicitly called out three spike questions that must be answered before tasks can be authored. This plan closes all three.

### S1: Where does the preflight gate live?

**Decision**: **Both** — shell-level check in `.claude/commands/tachi.security-report.md` AND Python-level check in `scripts/extract-report-data.py::render_mermaid_to_png()`. Defense-in-depth.

**Rationale**:
- The shell-level check at the command entry point matches the Feature 054 precedent for Typst (`.claude/commands/tachi.security-report.md` Step 1, lines 39-54). Consistency with Typst is both architecturally correct and trains user expectations.
- The Python-level check is already partially implemented at [scripts/extract-report-data.py:725](../../scripts/extract-report-data.py#L725). Converting the silent `if not shutil.which("mmdc"):` path from a warn-and-continue into a `raise RuntimeError(...)` is a minimal diff that provides defense-in-depth for: (a) direct invocations of `extract-report-data.py` from tests or tooling outside the command flow, (b) scenarios where the shell-level check is bypassed (e.g., someone editing the command file or running Python directly).
- Both checks emit the **same error message** (FR-130.1 format) so users see consistent output regardless of entry point.
- **Gating**: Both checks fire only when `attack-trees/` contains at least one `.md` file with Critical or High severity. Shell-level uses `ls examples/.../attack-trees/*.md 2>/dev/null | wc -l`; Python-level uses the existing `if not attack_trees:` early-return at line 721-722 (already present) combined with the new `raise` at line 725.

**Rejected alternatives**:
- **Python-only**: Fails the Feature 054 precedent (command-level check expected by users). Python is only reached after agent orchestration — lots of wasted work before the failure.
- **Shell-only**: Leaves direct Python invocations silently broken. Tests and developer tooling would still hit the silent path.
- **Extract a reusable helper**: Premature. One other tool (`typst`) is checked with a two-line shell block in the same command file. Introducing an abstraction for two consumers is over-engineering.

### S2: Does `scripts/install.sh` currently check Typst?

**Finding**: **No**. The current `scripts/install.sh` validates source directory, manifest, and git availability. It does not check for Typst or any external CLI. The existing Typst check lives exclusively in `.claude/commands/tachi.security-report.md` Step 1.

**Decision**: **Add an mmdc check only**. Do not add a Typst check.

**Rationale**:
- Adding a Typst check to `install.sh` expands scope beyond Feature 130's mandate and creates redundancy with the command-level check.
- `install.sh` runs once at installation time; the command checks Typst at every invocation. The command-level check is the enforcement point; `install.sh` is a courtesy early warning.
- The mmdc check in `install.sh` gives a one-time install hint — it does NOT replace the per-command preflight gate (FR-130.1). If a user runs `install.sh` without mmdc and ignores the warning, the per-command preflight still catches the failure later.
- Structure: mirror the existing command-level Typst check style. Single `if ! command -v mmdc >/dev/null 2>&1; then` block with a 2-line echo pointing to the `npm install -g @mermaid-js/mermaid-cli` command and the README Prerequisites section.

**Rejected alternative**: Auto-install mmdc from `install.sh`. Explicitly rejected in the PRD (Rejected Alternative E). Shifts the prerequisite to "must have npm" without solving the problem.

### S3: Can CI run a job without `mmdc` on PATH?

**Finding**: **Yes**, trivially, using a `ubuntu-latest` GitHub Actions runner.

**Decision**: New workflow `.github/workflows/tachi-mmdc-preflight.yml` that runs on `ubuntu-latest` and does NOT install mmdc. No custom Docker image needed.

**Rationale**:
- `ubuntu-latest` ships **without** mmdc preinstalled. A workflow that omits the `npm install -g @mermaid-js/mermaid-cli` step automatically satisfies the "mmdc not on PATH" precondition.
- The workflow installs Typst (so the happy-path Typst check passes) and Python 3.11 (for running the extraction script), then runs `/tachi.security-report` on `examples/mermaid-agentic-app/`. The test asserts:
  - Exit code is non-zero
  - stderr contains `mmdc`, `@mermaid-js/mermaid-cli`, and `npm install -g @mermaid-js/mermaid-cli`
- The workflow triggers on `pull_request` for paths listed in FR-130.7 (plus the test workflow itself).
- Total new CI infra: **one workflow file, zero Dockerfiles, zero new base images**. This is the minimum viable shape.

**Rejected alternatives**:
- **Custom Docker image** (e.g., `mcr.microsoft.com/devcontainers/python:3.11`): adds build time and maintenance burden without functional benefit.
- **Piggyback on an existing workflow**: tachi has only `release-please.yml` in `.github/workflows/` today. Separating concerns is cleaner than retrofitting the release workflow with a test job.

### Q130.1: Mid-render failure mode — abort or complete with errors?

**Decision**: **Abort the whole pipeline** with a non-zero exit code and a complete per-finding failure list on stderr before any PDF is written.

**Rationale**:
- Simpler: one control flow, no partial PDF output to clean up.
- Matches the fail-loud contract: the feature's explicit goal is to eliminate "pipeline reports success but PDF is broken." A partial PDF with some pages missing IS a broken PDF.
- Matches the Typst failure mode: Typst already aborts the whole pipeline on any compilation error; this plan makes mmdc's failure mode consistent.
- Implementation: in `render_mermaid_to_png()`, if the `as_completed` loop yields any `success=False`, collect all failures into a list, print them to stderr, and raise `RuntimeError("Attack path rendering failed for N findings: [...]")`. The caller (the main extraction flow) propagates the exception and the pipeline exits non-zero.

**Rejected alternative**: Complete with per-finding failure list. More informative in theory, but creates a PDF that looks legitimate but is missing some pages — exactly the silent-failure shape we are trying to eliminate.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. General-Purpose Architecture — PASS
Feature 130 is a correctness fix to a tooling pipeline. It adds no domain-specific logic. It makes the pipeline work as advertised for all projects with attack trees.

### II. API-First Design — N/A
No API surface. Internal CLI/command refactoring only.

### III. Backward Compatibility (NON-NEGOTIABLE) — PASS (with one caveat)
- **Pipeline behavior**: Projects without attack trees continue to work unchanged. Projects with attack trees on machines with mmdc installed continue to work unchanged (the happy path is unchanged).
- **Caveat / explicit breaking change**: Projects with attack trees on machines **without** mmdc previously produced a silent broken PDF; they now produce a loud preflight failure. This IS a behavior change but is documented in PRD Risk 130.2 and in this plan's Summary — it is a deliberate correctness improvement, not a regression. No downstream adopter was deliberately relying on the silent fallback (it produces unusable output).
- **File format compatibility**: `.typ` template is backward compatible (deletion of unreachable branch), `.py` extraction script is backward compatible on the happy path, ADR-022 is additive.

### IV. Concurrency & Data Integrity — N/A
No state transitions, no concurrency model beyond the existing `ThreadPoolExecutor(max_workers=4)` in `render_mermaid_to_png()`, which is preserved verbatim.

### V. Privacy & Data Isolation — N/A
No data handling changes.

### VI. Testing Excellence — PASS
- **Unit tests**: new pytest cases for `render_mermaid_to_png()` covering: (a) preflight raises when mmdc missing, (b) happy path unchanged, (c) mid-render failure raises with per-finding list
- **Integration tests**: new CI workflow `tachi-mmdc-preflight.yml` runs the actual pipeline end-to-end on a real example fixture with mmdc absent
- **Regression tests**: existing `test_backward_compatibility.py` validates baseline PDFs for both attack-tree-bearing examples after regeneration
- **Contract testing**: N/A (no API contracts)
- Coverage: the modified function `render_mermaid_to_png()` will reach 100% line coverage in the new tests (mocked `shutil.which` for the preflight branch, small fixture for the happy path, deliberately-malformed fixture for the mid-render failure branch)

### VII. Definition of Done (NON-NEGOTIABLE) — PASS (plan stage assertion)
All three DoD steps will be validated at delivery:
1. **Pushed to production**: Merge to main triggers the automatic `release-please` release workflow (see recent commit 1095dbb for v4.9.2 precedent)
2. **Tested**: unit + integration + CI fresh-install test all pass
3. **User validated**: `make examples` regenerates the two attack-tree examples locally with visible rendered diagrams (manual PDF inspection)

### VIII. Observability & Root Cause Analysis — PASS
- **5 Whys already applied**: PRD Risk analysis traces the root cause back through: silent fallback → "text fallback acceptable" SC in spec 112 → pymmdc research error at research.md:80 → spec 112 research never interrogated the hard-prerequisite alternative
- **Structured error messages**: FR-130.1 specifies the exact stderr format
- **Loud failure is the feature**: the whole point is to eliminate silent degradation

### IX. Git Workflow & Feature Branching (NON-NEGOTIABLE) — PASS
- Feature branch: `130-prd-130-fix` (created by `/aod.spec` setup script — conforms to `NNN-*` pattern even though it is shorter than the descriptive PRD topic)
- PR review required before merge
- Conventional commits: `fix(130):` scope

### X. Product-Spec Alignment & Architecture Review (NON-NEGOTIABLE) — IN PROGRESS
- PRD approved (rev 1.1, full Triad sign-off)
- Spec approved (PM sign-off 2026-04-11, 6 non-blocking observations)
- Plan (this document) pending PM + Architect dual sign-off in Step 3 of `/aod.project-plan`
- Tasks pending triple sign-off in `/aod.tasks`

### XI. SDLC Triad Collaboration — PASS
PM + Architect + Team-Lead all signed off on the PRD. The spike decisions (S1/S2/S3) in this plan respect each role's authority: Architect decides S1 (where preflight lives), Architect decides S2 (install.sh scope), Team-Lead decides S3 (CI infrastructure feasibility). Q130.1 (abort vs complete-with-errors) is an Architect call, resolved above.

### Testing Requirements — PASS
- Unit tests required for `render_mermaid_to_png()` changes ✓
- Integration tests required for CI fresh-install path ✓
- No E2E tests needed beyond baseline PDF comparison (existing mechanism)
- Test-first approach: write failing unit tests for preflight behavior before modifying `render_mermaid_to_png()`

### Security Standards — PASS
- **Dependency scanning**: no new runtime dependencies, so no new attack surface
- **Input validation**: preflight check is a single shell lookup — no user input
- **Secret management**: N/A
- **OWASP Top 10**: N/A (no web-facing surface)
- License compatibility: `@mermaid-js/mermaid-cli` is MIT-compatible. Explicitly **not** adopting GPL-3.0 pymmdc (documented in spec + PRD Rejected Alternatives)

### System Architecture Constraints — PASS
- Backend requirements: N/A (tachi is not a web service in this feature's scope)
- Frontend requirements: N/A
- MCP interface: N/A
- Performance targets: preflight check adds <100ms to startup (trivially met by a single `shutil.which` call)

**Overall Constitution Check**: **PASS**. Proceeds to Phase 0 research (already complete) and Phase 1 design.

## Project Structure

### Documentation (this feature)

```
specs/130-prd-130-fix/
├── plan.md              # This file (/aod.project-plan output)
├── research.md          # Phase 0 research (already written in /aod.spec)
├── quickstart.md        # Phase 1 output: how to validate the fix locally
├── spec.md              # Feature specification (PM approved)
├── checklists/
│   └── requirements.md  # Spec quality checklist (already written)
└── tasks.md             # Task breakdown (/aod.tasks output — pending)

# N/A for this feature (bug fix — no new data model, no new contracts):
# ├── data-model.md
# └── contracts/
```

**Rationale for skipped artifacts**:
- `data-model.md`: Feature 130 is a bug fix. No new entities, no new persistent state, no schema changes. The existing attack-tree dict structure (`id`, `mermaid_code`, `has_image`, `image_path`) is preserved. A `data-model.md` would contain only "no changes" and adds no value.
- `contracts/`: No API contracts. The only interfaces are the internal `render_mermaid_to_png()` function signature (unchanged) and the CLI error message format (specified in FR-130.1 and already captured in spec.md US-1 AC-1). A `contracts/` directory would be empty.

### Source Code (repository root)

```
tachi/
├── scripts/
│   ├── extract-report-data.py           # MODIFY: lines 710-778 (preflight + abort-on-failure)
│   └── install.sh                        # MODIFY: add mmdc presence check
├── templates/tachi/security-report/
│   └── attack-path.typ                   # MODIFY: delete lines 78-86 (text fallback branch)
├── .claude/commands/
│   └── tachi.security-report.md          # MODIFY: Step 1 — add mmdc shell-level preflight
├── .github/workflows/
│   └── tachi-mmdc-preflight.yml          # NEW: CI fresh-install test
├── docs/architecture/
│   ├── 00_Tech_Stack/README.md           # MODIFY: line 279 (mmdc is hard prereq, not optional)
│   └── 02_ADRs/
│       └── ADR-022-mmdc-hard-prerequisite.md  # NEW: first ADR governing CLI prerequisite
├── specs/112-attack-path-pages/
│   ├── spec.md                           # MODIFY: invert SC-004 (line 125), delete line 135
│   └── research.md                       # MODIFY: correct line 80, add rationale at 91-93
├── README.md                             # MODIFY: add new "## Prerequisites" section
├── examples/
│   ├── agentic-app/sample-report/        # REGENERATE: attack path PDFs (47 trees)
│   └── mermaid-agentic-app/              # REGENERATE: attack path PDFs (24 trees)
└── tests/scripts/
    └── test_mmdc_preflight.py            # NEW: pytest unit tests for preflight behavior
```

**Structure Decision**: tachi is a single-project toolkit; the project structure is "existing file modifications + 3 new files." No Option 1/2/3 tree overhaul applies here. The new files are listed above with their purposes.

**Pre-existing structure preserved**:
- `scripts/*.py` stays stdlib-only
- `templates/tachi/security-report/` keeps its current Typst layout
- `.claude/commands/` keeps its current command catalog (FR-130 only modifies `tachi.security-report.md`)
- `docs/architecture/02_ADRs/` gains ADR-022 following the existing ADR numbering and format

## Phase 0: Outline & Research

**Status**: **Complete.** See [research.md](research.md) written during `/aod.spec`.

Key findings consumed by this plan:

1. **Current render logic**: `render_mermaid_to_png()` at [scripts/extract-report-data.py:710-778](../../scripts/extract-report-data.py#L710-L778), silent fallback at line 725.
2. **Typst template fallback**: lines 78-86 of `templates/tachi/security-report/attack-path.typ`.
3. **Preflight gate precedent**: `which typst` in [.claude/commands/tachi.security-report.md](../../.claude/commands/tachi.security-report.md) Step 1, lines 39-54.
4. **install.sh baseline**: No current Typst check; no current mmdc check. Adding mmdc only (S2 decision).
5. **README baseline**: No current Prerequisites section. Insertion point at top, between "What is tachi?" and "Quick Start."
6. **Parent spec 112 SC-004 text** (to invert): verbatim captured in research.md for exact find/replace.
7. **Parent research.md line 80 text** (to correct): verbatim captured for exact find/replace.
8. **Attack-tree-bearing examples** (PRD error corrected): `examples/agentic-app/sample-report/` + `examples/mermaid-agentic-app/`.
9. **ADR-021 determinism rules**: `SOURCE_DATE_EPOCH=1700000000` for baseline regeneration.
10. **Feature 054 precedent**: Typst hard prerequisite via command-level `which` check. First "fail loud on missing CLI" in tachi.
11. **Feature 128 dev-only pytest baseline**: new test file lands in `tests/scripts/` under the existing pytest infrastructure.

**No NEEDS CLARIFICATION markers remain.** All unknowns resolved during the spec-stage research phase and the Plan Stage Day 0 spike section above.

## Phase 1: Design & Contracts

**Prerequisites**: research.md complete ✓

### Data Model

**N/A — no data model changes.**

Feature 130 preserves the existing attack-tree dict structure used by `render_mermaid_to_png()`:
- `id`: finding identifier (string, unchanged)
- `mermaid_code`: Mermaid source text (string, unchanged)
- `has_image`: whether a PNG was successfully rendered (bool, unchanged — but the semantics of `False` change from "missing or failed" to "failed after preflight passed," since "missing" now raises instead of returning `False`)
- `image_path`: relative path to rendered PNG (string, unchanged)

No schema version bump needed — the same field set serves the same purpose.

### API Contracts

**N/A — no API surface changes.**

Internal function signatures preserved:
- `render_mermaid_to_png(attack_trees: list, target_dir: Path, template_dir: Path) -> None` — unchanged signature; new behavior is "raises RuntimeError instead of returning silently when mmdc missing."
- Exit codes from `/tachi.security-report`: the existing non-zero exit path is reused. No new exit code numbering.

The only "contract" that changes is the **user-facing stderr message format**, which is specified in FR-130.1 and captured as:

```
Attack path rendering requires @mermaid-js/mermaid-cli (mmdc).
Install with: npm install -g @mermaid-js/mermaid-cli
Then re-run /tachi.security-report.
```

This is the single source of truth for the error message. It appears in:
- `scripts/extract-report-data.py::render_mermaid_to_png()` (raised as `RuntimeError`)
- `.claude/commands/tachi.security-report.md` Step 1 (shell-level `echo`)
- `scripts/install.sh` (warning message on install)
- `README.md` Prerequisites section (how-to-install guidance)
- `tests/scripts/test_mmdc_preflight.py` (assertion string)
- `.github/workflows/tachi-mmdc-preflight.yml` (`grep` assertion)

**Consistency check during `/aod.tasks`**: tasks.md MUST list a verification task that greps for the canonical message string across all six locations to confirm they match.

### Quickstart

`quickstart.md` will document:

1. **Local reproduction of the bug** (before the fix):
   ```bash
   # Temporarily hide mmdc from PATH
   PATH=$(echo $PATH | tr ':' '\n' | grep -v mmdc | tr '\n' ':')
   /tachi.security-report examples/mermaid-agentic-app/
   # → produces PDF with raw Mermaid source (broken)
   ```

2. **Validation after the fix**:
   ```bash
   PATH=$(echo $PATH | tr ':' '\n' | grep -v mmdc | tr '\n' ':')
   /tachi.security-report examples/mermaid-agentic-app/
   # → exits non-zero with the canonical error message
   ```

3. **Happy path validation**:
   ```bash
   # With mmdc installed:
   /tachi.security-report examples/mermaid-agentic-app/
   # → generates PDF with all attack path pages rendered as diagrams
   SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py
   # → passes (baseline byte-identity preserved)
   ```

4. **Regeneration of examples**:
   ```bash
   SOURCE_DATE_EPOCH=1700000000 make examples
   # → regenerates all 6 example outputs; the 2 attack-tree-bearing ones get rendered diagrams
   ```

Written during tasks stage; listed here only as the quickstart.md outline.

### Agent Context Update

Run `.aod/scripts/bash/update-agent-context.sh claude` during tasks stage to refresh the Claude-specific agent context file with the new entries under CLAUDE.md's "Recent Changes" section:

```
- Feature 130: Loud-Failure Preflight Gate for mmdc
  - @mermaid-js/mermaid-cli (mmdc) is now a documented hard prerequisite when attack-trees/ is present; /tachi.security-report aborts at preflight with a one-line install command
  - Deleted silent text fallback in scripts/extract-report-data.py:725-730 and templates/tachi/security-report/attack-path.typ:78-86
  - New ADR-022 documents the CLI-prerequisite posture decision — first ADR governing this class of decisions in tachi
  - New CI workflow tachi-mmdc-preflight.yml asserts the loud-failure path on every PR touching the affected files
  - Spec 112 SC-004 inverted, research.md line 80 corrected
```

### Post-Design Constitution Re-Check

**All gates still PASS.** The design does not introduce:
- New runtime Python dependencies (still stdlib-only)
- New external services (mmdc was already in use)
- Breaking API changes (no API surface)
- Schema changes (no data model)
- Architecture changes (same tooling pipeline shape)

The only new addition to the architecture is **ADR-022**, which documents the decision and sets precedent for future CLI-prerequisite transitions. This is constitutional compliance, not a violation.

## Components

(Included for system-design auto-extraction by `/aod.project-plan` Step 6.)

### Preflight Gate (shell-level)
- **Location**: `.claude/commands/tachi.security-report.md` Step 1
- **Role**: First-line enforcement of mmdc availability at command entry, gated on attack-tree detection
- **Pattern**: mirrors the existing Typst `which typst` check in the same file
- **Failure mode**: non-zero exit with canonical error message

### Preflight Gate (Python-level)
- **Location**: `scripts/extract-report-data.py::render_mermaid_to_png()` line 725
- **Role**: Defense-in-depth for direct Python invocations (tests, tooling)
- **Pattern**: existing `shutil.which("mmdc")` check, converted from silent `return` to `raise RuntimeError(...)`
- **Failure mode**: exception propagates up and exits the pipeline non-zero

### Mid-Render Failure Aggregator (new behavior)
- **Location**: `scripts/extract-report-data.py::render_mermaid_to_png()` after the `as_completed` loop (currently lines 774-777)
- **Role**: Collects per-finding rendering failures into a list, then raises `RuntimeError("Attack path rendering failed for N findings: [...]")` if the list is non-empty
- **Failure mode**: same as preflight — exception propagates, pipeline exits non-zero, stderr shows per-finding detail

### CI Workflow
- **Location**: `.github/workflows/tachi-mmdc-preflight.yml` (new file)
- **Trigger**: `pull_request` on the 5 file paths listed in FR-130.7
- **Role**: CI-level enforcement that the loud-failure path works on a machine without mmdc
- **Platform**: `ubuntu-latest` (no custom Docker image)

### Docs Sync Cluster
- `README.md` Prerequisites section (new)
- `scripts/install.sh` mmdc check (new code block)
- `docs/architecture/00_Tech_Stack/README.md` line 279 (update mmdc from optional to hard prereq)
- `specs/112-attack-path-pages/spec.md` SC-004 inversion, line 135 deletion
- `specs/112-attack-path-pages/research.md` line 80 correction, lines 91-93 rationale block
- `docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md` (new — first ADR governing CLI prerequisite transitions)

## Data Flow

```
user runs /tachi.security-report on project with attack-trees/
            │
            ▼
.claude/commands/tachi.security-report.md Step 1
            │
            ├── which typst? ──No──> abort with Typst install guidance (existing behavior)
            │
            Yes
            │
            ├── attack-trees/*.md present? ──No──> skip mmdc check, proceed
            │
            Yes
            │
            ├── which mmdc? ──No──> abort with canonical error message (NEW, FR-130.1)
            │
            Yes
            │
            ▼
report-assembler agent invokes scripts/extract-report-data.py
            │
            ▼
render_mermaid_to_png(attack_trees, target_dir, template_dir)
            │
            ├── attack_trees empty? ──Yes──> return (existing behavior)
            │
            No
            │
            ├── shutil.which("mmdc")? ──No──> raise RuntimeError with canonical message (NEW, FR-130.2; defense-in-depth)
            │
            Yes
            │
            ▼
        ThreadPoolExecutor(max_workers=4) rendering loop
            │
            ▼
        Collect per-finding success/failure results
            │
            ├── any failures? ──Yes──> raise RuntimeError(per-finding list) (NEW, FR-130.4; aborts pipeline)
            │
            No
            │
            ▼
        All entries have has_image=True, image_path=<path>
            │
            ▼
        Typst template renders with has_img branch only (else-if branch deleted, FR-130.3)
            │
            ▼
        PDF ships with 100% rendered diagrams
```

## Tech Stack

| Layer | Choice | Rationale | New in this feature? |
|---|---|---|---|
| Runtime language | Python 3.11+ | Matches existing `scripts/*.py` constraint | No |
| Runtime Python deps | stdlib only (`shutil`, `subprocess`, `concurrent.futures`, `tempfile`, `pathlib`) | Tech Stack doc line 199-201 hard rule | No |
| External CLI (hard prereq, always) | Typst 0.12+ | PDF compilation | No |
| External CLI (hard prereq, gated) | `@mermaid-js/mermaid-cli` v11+ (npm install) | Attack path rendering | **Yes** (was optional, now hard) |
| Dev-time test framework | pytest 8.0+ (from `requirements-dev.txt`) | Feature 128 precedent | No |
| CI runner | GitHub Actions `ubuntu-latest` | Standard, no mmdc preinstalled | No (workflow file is new, infrastructure is existing) |
| PDF template engine | Typst with `attack-path.typ` component | Existing Feature 112 pipeline | No |
| Determinism harness | `SOURCE_DATE_EPOCH=1700000000` + `tests/scripts/test_backward_compatibility.py` | ADR-021 | No (reused) |
| Architecture Decision Records | `docs/architecture/02_ADRs/` | Existing pattern (21 ADRs today, 22 after this feature) | **Yes** (ADR-022 is new) |

**No new technology introduced.** Every choice above either already exists in the tachi codebase or is a GitHub Actions primitive.

## Risk & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Python-level raise propagates incorrectly and masks the canonical error | Low | Medium | Unit test asserts exact stderr string; CI workflow asserts end-to-end stderr |
| Shell-level check fires on projects without attack trees | Low | Medium | Gate is `ls attack-trees/*.md 2>/dev/null | wc -l` — deterministic; unit-testable via shell harness |
| Baseline regeneration under `SOURCE_DATE_EPOCH` diverges from existing baselines | Low | Low | `test_backward_compatibility.py` catches it in PR CI |
| Scope creep: team adds Typst check to `install.sh` despite S2 decision | Medium | Low | Plan explicitly forbids it; tasks.md will enforce in task descriptions |
| ADR-022 written but not referenced from Tech Stack doc | Low | Low | FR-130.5 adds Tech Stack doc update; tasks.md will list ADR-022 link as a required addition to that file |
| CI workflow accidentally installs mmdc via a transitive dep (e.g., if setup-typst includes it) | Very Low | High | Explicit `PATH` print step in CI workflow + grep assertion for "mmdc: command not found" in diagnostics |
| Mid-render abort leaves partial files in attack-trees/ directory | Low | Low | `tempfile.TemporaryDirectory()` at [extract-report-data.py:770](../../scripts/extract-report-data.py#L770) is the working area; partial files are ephemeral; target directory is only written on success |

All risks inherit from the PRD risk register; no new risks introduced by this plan.

## Deliverables Checklist (for tasks.md to consume)

- [ ] **Code changes**:
  - [ ] `scripts/extract-report-data.py` lines 710-778 refactored (preflight raise + mid-render aggregator raise)
  - [ ] `scripts/install.sh` mmdc check added
  - [ ] `templates/tachi/security-report/attack-path.typ` lines 78-86 deleted
  - [ ] `.claude/commands/tachi.security-report.md` Step 1 mmdc preflight added
- [ ] **New files**:
  - [ ] `.github/workflows/tachi-mmdc-preflight.yml`
  - [ ] `docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md`
  - [ ] `tests/scripts/test_mmdc_preflight.py`
  - [ ] `specs/130-prd-130-fix/quickstart.md`
- [ ] **Docs sync**:
  - [ ] `README.md` Prerequisites section authored
  - [ ] `docs/architecture/00_Tech_Stack/README.md` line 279 updated (optional→hard prereq)
  - [ ] `specs/112-attack-path-pages/spec.md` SC-004 inverted, line 135 deleted
  - [ ] `specs/112-attack-path-pages/research.md` line 80 corrected, lines 91-93 rationale added
  - [ ] CLAUDE.md "Recent Changes" section appended via `update-agent-context.sh`
- [ ] **Baseline regeneration**:
  - [ ] `examples/agentic-app/sample-report/security-report.pdf` regenerated
  - [ ] `examples/mermaid-agentic-app/security-report.pdf` regenerated (and baseline if included in byte-deterministic set — Plan Stage leaves this optional)
- [ ] **Verification**:
  - [ ] grep-verified: zero occurrences of `else if mermaid-text` in `attack-path.typ`
  - [ ] grep-verified: zero occurrences of silent `has_image = False` fallback in `extract-report-data.py:710-778`
  - [ ] Canonical error message string consistent across all six locations
  - [ ] `pytest tests/scripts/test_mmdc_preflight.py` passes
  - [ ] `pytest tests/scripts/test_backward_compatibility.py` passes under `SOURCE_DATE_EPOCH=1700000000`
  - [ ] New CI workflow runs green on a test PR
  - [ ] Manual PDF inspection of regenerated examples — all attack path pages show rendered diagrams

## Complexity Tracking

*No constitution violations to justify. No complexity escape hatches used.*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *(none)* | *(n/a)* | *(n/a)* |

The plan stays within every constitutional gate. Defense-in-depth (two preflight gates instead of one) is **not** a complexity violation because:
1. Each gate is ~2-3 lines of code
2. The two locations serve different invocation paths (user runs command vs. tests/tooling invoke Python directly)
3. The Feature 054 precedent requires the command-level check for Typst parity
4. No abstraction is introduced; each check is inline and local

## References

- **PRD**: [docs/product/02_PRD/130-fix-attack-path-mermaid-rendering-2026-04-11.md](../../docs/product/02_PRD/130-fix-attack-path-mermaid-rendering-2026-04-11.md)
- **Spec**: [spec.md](spec.md) — PM approved 2026-04-11
- **Research**: [research.md](research.md)
- **Parent feature**: [specs/112-attack-path-pages/](../112-attack-path-pages/) — the feature being corrected
- **Precedent feature**: Feature 054 — established Typst hard-prerequisite pattern
- **ADR-021**: `SOURCE_DATE_EPOCH` for deterministic PDF comparison — governs FR-130.6 baseline regeneration
- **To be written (ADR-022)**: CLI-prerequisite hard-gate with attack-tree detection — documents this plan's S1 decision
- **Tech Stack constraint**: [docs/architecture/00_Tech_Stack/README.md:199-201](../../docs/architecture/00_Tech_Stack/README.md#L199-L201) — stdlib-only Python runtime rule
- **Constitution**: [.aod/memory/constitution.md](../../.aod/memory/constitution.md) — all gates pass
