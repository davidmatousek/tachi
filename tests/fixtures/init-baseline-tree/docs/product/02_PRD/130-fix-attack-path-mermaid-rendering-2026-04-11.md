---
prd:
  number: 130
  topic: fix-attack-path-mermaid-rendering
  created: 2026-04-11
  status: Approved
  type: feature
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-11
    status: APPROVED
    notes: "PM-authored revision 1.1 resolves all architect and team-lead round 1 findings. Primary solution pivoted from factually incorrect pymmdc-as-primary path to mmdc-as-hard-prerequisite with preflight gate. Spec 112 SC-004 inversion, research.md:80 correction, README Prerequisites authoring, and FR-130.7 CI fresh-install test explicitly scoped. Rejected Alternatives section documents pymmdc research error so it cannot recur."
  architect_signoff:
    agent: architect
    date: 2026-04-11
    status: APPROVED
    notes: "Round 2 review: 13/13 prior findings resolved. Exec summary pivot clean, US-130.1 ACs cover all three branches, FR-130.1 uses shutil.which preflight gate, FR-130.3 deletes text fallback entirely, FR-130.5 explicitly inverts spec 112 SC-004, Rejected Alternatives section includes PyPI sources. No new concerns. Preserves runtime zero-Python-dep constraint from Feature 128."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-11
    status: APPROVED
    notes: "Round 2 review: B-1 and C-1 through C-5 all resolved. 5-day target defensible (work breakdown totals 4.35d + 0.65d buffer). Plan Stage Day 0 spike gate with S1/S2/S3 decisions is solid hygiene. FR-130.7 CI infrastructure deferral to spike day is acceptable. No new risks, no skill gaps, capacity healthy."
source:
  idea_id: 130
  story_id: null
---

# Fix Attack Path Mermaid Rendering When mmdc Is Not Installed

**Status**: Draft
**Created**: 2026-04-11
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P0
**Type**: Feature (Bug Fix / Dependency Posture)

---

## Executive Summary

### The One-Liner
Turn a silent pipeline failure into a loud, actionable one: when `mmdc` is missing, the tachi security report pipeline must fail at preflight with a one-line install command — never silently ship a PDF full of raw Mermaid source.

### Problem Statement
On a fresh tachi install — the exact moment a new user evaluates whether the tool is worth adopting — running `/tachi.security-report` on a project with attack trees produces a PDF where each attack path page contains 40+ lines of raw `flowchart TD` Mermaid source instead of a rendered diagram. The pipeline reports success, so the user is not warned; they discover the failure only when flipping through the PDF. This silently violates spec 112 AC#2 ("a rendered diagram image of the attack tree" — [specs/112-attack-path-pages/spec.md:34](specs/112-attack-path-pages/spec.md#L34)) and directly blocks the flagship "show to exec board" use case from [spec.md:25](specs/112-attack-path-pages/spec.md#L25). Observed externally in a downstream project's security report, which shipped raw Mermaid source in the attack path section after running `/tachi.security-report` without `mmdc` installed.

### Proposed Solution
Adopt **`@mermaid-js/mermaid-cli` (`mmdc`) as a documented hard prerequisite** of the `/tachi.security-report` pipeline for any project with attack trees. Three coordinated changes:

1. **Preflight gate**: `/tachi.security-report` checks for `mmdc` availability at the start of the run **when attack tree inputs are present**. If missing, the pipeline aborts loudly with a one-line install command — it does not proceed, does not render a broken PDF, and does not emit the text-fallback code.
2. **Text fallback removed**: The `else if mermaid-text != ""` branch at [templates/tachi/security-report/attack-path.typ:78-86](templates/tachi/security-report/attack-path.typ#L78-L86) is **deleted entirely**. It is an unreachable code path after the preflight gate lands.
3. **Install-time documentation**: `README.md` gains a "Prerequisites" section that names `mmdc` alongside `typst`. `scripts/install.sh` gains a `mmdc` presence check that prints installation guidance. `specs/112-attack-path-pages/spec.md` SC-004 is inverted (text fallback is no longer a supported shipping mode), and `research.md:80` is corrected (pymmdc is not pure-Python — see Rejected Alternatives).

This preserves tachi's runtime zero-Python-dependency constraint established by Feature 128 (no Python pip dependency added), turns silent failure into loud failure, and aligns the mmdc prerequisite with how the pipeline already treats Typst (another documented hard prerequisite).

### Success Criteria
- On a machine without `mmdc`, running `/tachi.security-report` on a project with attack trees **aborts at preflight with an actionable install command** — it never produces a broken PDF.
- On a machine with `mmdc` installed, 100% of attack path pages show rendered diagram images — no text fallback, no silent failures.
- Text fallback is removed from the Typst template (FR-130.3) and from spec 112's success criteria (FR-130.5).
- Zero regressions on the 6 example outputs in `examples/` — all continue to generate successfully on developer machines where mmdc is present.
- A CI job enforces the preflight behavior on every PR by running the pipeline in a minimal container without `mmdc` in `PATH` and asserting the loud-failure path.

### Timeline
Target spec-to-delivery: **~5 days** (see Plan Stage Day 0 spike gate in Timeline section below). Exact dates set during Plan stage.

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [docs/product/01_Product_Vision/product-vision.md](docs/product/01_Product_Vision/product-vision.md)

tachi's mission is to be "the default threat modeling toolkit for any team building agentic AI applications." A first-run experience where the flagship artifact (the PDF report) ships with raw source code instead of rendered diagrams directly undermines adoption. Fixing this bug is a mission-critical polish item — it does not add capabilities, it ensures existing capabilities actually work out of the box.

### Target User Fit
Developers evaluating tachi on a fresh machine deserve a clear contract: here are the prerequisites, the pipeline will tell you if any are missing, and when they are installed everything works. The current silent-failure mode violates that contract. Adopting `mmdc` as a documented prerequisite restores it.

### Roadmap Fit
This is a **spec 112 follow-up** — it closes an accepted gap in a previously shipped feature rather than introducing new scope. It fits the "polish and correctness" bucket between feature waves.

---

## Target Users & Personas

### Primary Persona: Template Adopter on Fresh Install
- **Role**: Developer/security engineer evaluating tachi for the first time
- **Environment**: Python ≥3.11, Typst installed, Node.js and `@mermaid-js/mermaid-cli` status **unknown**
- **Goal**: Generate a board-presentation-ready security PDF within minutes of install
- **Pain today**: When `mmdc` is missing, generated PDF contains raw Mermaid source instead of diagrams; failure is silent (no error, no warning in stdout)

### Secondary Persona: CISO / Executive Audience
- **Role**: Recipient of the generated PDF (indirectly)
- **Context**: Opens a PDF shared by the primary user in a board meeting
- **Pain today**: Sees incomprehensible `flowchart TD` source code on what should be the "money slides" of the report — erodes trust in the tool and the team using it

---

## User Stories

### US-130.1: Prerequisites Are Enforced, Not Assumed
**When** I run `/tachi.security-report` on a project with attack trees on a machine where I have not yet installed the documented prerequisites,
**I want to** see the pipeline abort immediately at preflight with an actionable error message naming the missing prerequisite and the exact install command,
**So I can** install what's missing and re-run — rather than discover a broken PDF after the pipeline claims success.

**Acceptance Criteria**:
- **Given** a machine without `mmdc` on `PATH` and a target project with Critical/High attack trees, **when** the user runs `/tachi.security-report`, **then** the pipeline aborts at preflight with exit code ≠ 0 and stderr contains: (a) the missing prerequisite name, (b) the reason it is needed ("attack path rendering"), and (c) the single-line install command `npm install -g @mermaid-js/mermaid-cli`.
- **Given** the same machine, **when** the user runs `/tachi.security-report` on a project **without** any attack tree inputs, **then** the pipeline runs normally — the mmdc check MUST be gated on "attack trees detected," not always-on.
- **Given** a machine with `mmdc` installed and a target project with attack trees, **when** the user runs `/tachi.security-report`, **then** the pipeline proceeds and every attack path page in the generated PDF contains a rendered diagram image — no raw Mermaid source anywhere in the output.
- **Given** the PDF is viewed at page size, **when** a reader examines an attack path diagram, **then** node labels and edge connections are legible (consistent with the existing spec 112 SC-003 legibility bar).

**Priority**: P0

---

### US-130.2: Rendering Failure Is Loud, Not Silent
**When** diagram rendering fails for any reason during the run itself (corrupted input, unsupported Mermaid syntax, mmdc crash mid-render),
**I want to** see a clear warning in the pipeline output identifying which finding(s) failed to render and why, and **I want the pipeline to exit non-zero**,
**So I can** immediately decide whether to fix the input, file a bug, or regenerate — rather than discover the failure by flipping through the PDF.

**Acceptance Criteria**:
- **Given** `mmdc` is installed but fails mid-render for one or more attack trees (syntax error, timeout, crash), **when** the pipeline completes, **then** the command output explicitly lists each failed finding ID and a short reason, AND the exit code is non-zero.
- **Given** a mid-render failure, **when** the user examines the generated PDF (if one was produced at all), **then** the pipeline MUST NOT ship a page containing raw Mermaid text as a legitimate-looking deliverable.
- **Given** multiple attack trees, **when** one fails mid-render, **then** the pipeline MAY either (a) abort the run entirely, or (b) complete with non-zero exit and a clear per-finding failure list — architect review chooses which during spec stage.

**Priority**: P0

---

### US-130.3: Documented Dependency Posture
**When** I install tachi and read the README or run the install script,
**I want to** see a single, unambiguous statement of what external tools tachi needs to produce a complete report,
**So I can** prepare my environment before running the pipeline rather than debug missing dependencies after the fact.

**Acceptance Criteria**:
- **Given** the README, **when** a new user reads it before running any command, **then** a "Prerequisites" section explicitly names `typst` and `@mermaid-js/mermaid-cli` (with install commands for macOS/Linux/WSL) as the external tools required for full PDF generation.
- **Given** `scripts/install.sh`, **when** a user runs it, **then** the script checks for `mmdc` availability and either (a) confirms it is present, or (b) prints a clear one-line install command and a follow-up reminder — consistent with how the script currently treats Typst.
- **Given** spec 112 research.md, **when** a future engineer reads it, **then** line 80 no longer asserts "pymmdc is a pure-Python alternative" (a factual error), and the rationale for the mmdc hard-prerequisite decision is captured as a durable note.

**Priority**: P0

---

## Functional Requirements

### FR-130.1: Preflight Prerequisite Gate
`/tachi.security-report` MUST check for `mmdc` availability via `shutil.which("mmdc")` (or equivalent shell-agnostic mechanism) **at the start of the pipeline run when attack tree inputs are detected**. If the check fails, the pipeline MUST abort immediately with a non-zero exit code and an error message of the form:
```
Attack path rendering requires @mermaid-js/mermaid-cli (mmdc).
Install with: npm install -g @mermaid-js/mermaid-cli
Then re-run /tachi.security-report.
```
The preflight check MUST occur before any rendering work begins and MUST NOT run on projects without attack tree inputs (so reports that don't need rendering are unaffected).

### FR-130.2: Remove Silent Text-Fallback Path in Extraction
The `render_mermaid_to_png()` function at [scripts/extract-report-data.py:710-778](scripts/extract-report-data.py#L710-L778) MUST be updated so that when `mmdc` is unavailable, the function either (a) never runs because the preflight gate in FR-130.1 has already aborted the pipeline, or (b) raises a clear exception rather than silently marking entries as `has_image=False`. The current "warning + silent fallback" path MUST be eliminated.

### FR-130.3: Remove Text-Fallback Branch in Typst Template
The `else if mermaid-text != ""` branch at [templates/tachi/security-report/attack-path.typ:78-86](templates/tachi/security-report/attack-path.typ#L78-L86) MUST be **deleted entirely**. After the preflight gate lands, this branch is unreachable dead code. Removing it eliminates an entire class of "how does this visual state appear" ambiguity. No visual spec for the removed branch is needed because it will not exist.

### FR-130.4: Loud Mid-Render Failure Mode
When `mmdc` is installed and running but fails on a specific attack tree (syntax error, timeout, crash), the pipeline MUST print an explicit stderr warning listing the failed finding ID and a short cause, AND MUST exit with a non-zero code. The pipeline MUST NOT produce a PDF containing a page that silently falls back to raw Mermaid text as if it were a legitimate deliverable. The architect review during spec stage decides whether mid-render failure aborts the whole pipeline (simpler) or completes with non-zero exit and a per-finding failure list (more informative).

### FR-130.5: Documentation and Spec Corpus Sync
The following files MUST be updated in the same feature delivery:

- **`README.md`** — **Authoring task**: create a new "Prerequisites" section (currently does not exist) that names `typst` and `@mermaid-js/mermaid-cli` with install commands for macOS/Linux/WSL. Do not assume the section exists.
- **`scripts/install.sh`** — add an `mmdc` presence check, consistent with how the script currently handles Typst (if any; verify during plan stage). On miss, print the same one-line install command as FR-130.1.
- **`specs/112-attack-path-pages/spec.md`** — line 135 ("text fallback is acceptable") MUST be deleted or rewritten to explicitly mark text fallback as a removed shipping mode. Line 125 (SC-004 — "When the rendering tool is unavailable, 100% of attack path pages still appear with text fallback") MUST be **inverted**: it is being reversed, not edited. Replace with a new criterion asserting that rendering tool availability is verified at preflight and the pipeline aborts loudly if unavailable.
- **`specs/112-attack-path-pages/research.md`** — line 80 ("Pure Python alternative: pymmdc package (no Node.js dependency)") MUST be corrected. Append a note that pymmdc on PyPI wraps the Node.js `mmdc` CLI and is not a pure-Python renderer (see Rejected Alternatives below for sources). Lines 91-93 MUST carry a durable rationale for the mmdc hard-prerequisite decision.

### FR-130.6: Zero-Regression on Example Outputs
All 6 example outputs in `examples/` MUST continue to generate without errors after this change when `mmdc` is present (the developer-machine baseline). Attack-tree-bearing examples (`examples/web-app/` and `examples/mermaid-agentic-app/`) MUST produce rendered diagrams and regenerated byte-deterministic baselines (per ADR-021, `SOURCE_DATE_EPOCH=1700000000`).

### FR-130.7: CI Fresh-Install Acceptance Test
A CI job MUST run in a minimal container where `mmdc` is **not** installed and assert that `/tachi.security-report` on a fixture project with attack trees aborts at preflight with the expected error message. This job MUST run on every PR touching `scripts/extract-report-data.py`, `templates/tachi/security-report/attack-path.typ`, `scripts/install.sh`, or `.claude/commands/tachi.security-report.md`. Without CI enforcement, this regression will recur. The test fixture SHOULD reuse one of the existing examples (recommend `examples/mermaid-agentic-app/` — it has attack trees) rather than introduce a new test project or reference external projects.

---

## Non-Functional Requirements

### Performance
- The preflight `mmdc` availability check MUST add no more than 100ms to pipeline startup. (It is a single `shutil.which()` call — this budget is trivially achievable.)
- Render time for projects with `mmdc` present MUST be unchanged from the current implementation. The existing `ThreadPoolExecutor(max_workers=4)` pattern at [scripts/extract-report-data.py:772](scripts/extract-report-data.py#L772) MUST be preserved.

### Determinism
- **Resolved**: the current `mmdc` Node.js CLI path is empirically deterministic under `SOURCE_DATE_EPOCH=1700000000` per the Feature 128 baseline harness (ADR-021). This PRD does not change the renderer, so the determinism story is unchanged. No new determinism validation is required.
- **Validation gate for CI**: the baseline comparison test for `examples/web-app/` and `examples/mermaid-agentic-app/` MUST continue to pass after the refactor. This is the pre-existing ADR-021 test — no new test needed.

### Dependency Posture — Single Accepted Decision
**Decision**: Adopt `@mermaid-js/mermaid-cli` (Node.js CLI) as a documented **hard prerequisite** of `/tachi.security-report` when attack tree inputs are present.

**Rationale**:
- Preserves the runtime zero-Python-dependency constraint established by Feature 128 — no Python pip package is added; `mmdc` lives outside the Python dep tree entirely.
- Aligns with how `/tachi.security-report` already treats Typst (hard prerequisite, documented in install docs, checked at preflight).
- Turns a silent failure into a loud one — the single most important user-experience improvement in this PRD.
- Other options (accept pip dep / vendor / alternative library) were evaluated and rejected — see Rejected Alternatives.

### Security
- Preflight check is a single shell lookup — no new attack surface.
- Removing the silent text fallback (FR-130.3) eliminates a class of "unexpected output state," a security-adjacent quality win.
- Documenting the `mmdc` prerequisite in `scripts/install.sh` and `README.md` gives downstream security analysts a known dep to track.
- **License compatibility note**: any future proposal to adopt a Python-package Mermaid renderer MUST include explicit license analysis. The rejected pymmdc package (see below) is GPL-3.0, which is incompatible with tachi's permissive-license distribution posture. This is a blocking concern for any future dependency-posture reconsideration, not a concern for the current PRD.
- The Node.js `@mermaid-js/mermaid-cli` tool is widely used, well-maintained by the Mermaid.js project, and carries a standard MIT-compatible supply chain posture.

---

## Rejected Alternatives

### A. Adopt `pymmdc` (PyPI) as a pure-Python renderer — REJECTED
**Claim (from `specs/112-attack-path-pages/research.md:80`)**: pymmdc is a pure-Python Mermaid renderer that removes the Node.js dependency.

**Finding (verified against PyPI 2026-04-11)**: False. [pymmdc v0.1.0](https://pypi.org/project/pymmdc/) is a thin Python wrapper that shells out to the Node.js `@mermaid-js/mermaid-cli` CLI. Its own documentation explicitly requires Node.js v14+ and `mmdc` installed via npm. Adopting it would **add** a Python dependency while still requiring Node.js — strictly worse than today. Additional disqualifiers: GPL-3.0 license (incompatible with tachi's distribution model), Python ≥3.12 requirement (tachi baseline is Python ≥3.11), single 0.1.0 release, single-individual maintainer.

**Source**: architect review 2026-04-11, [`.aod/results/architect.md` §1](/.aod/results/architect.md), team-lead review 2026-04-11, [`.aod/results/team-lead.md` B-1](/.aod/results/team-lead.md).

### B. Adopt alternative pure-Python Mermaid libraries — REJECTED
**Considered**: `mmdc` (Raziei) on PyPI, `mermaid-py`, `python_mermaid`, `md-mermaid`, `mermaid-mcp`.

**Findings**: None meet tachi's constraints today.
- `mmdc` (Raziei) transitively depends on **PhantomJS**, deprecated since 2017 and archived 2019 — unpatched security posture disqualifies it for a security-modeling tool.
- `mermaid-py` defaults to the `mermaid.ink` HTTP service — violates the "no network during pipeline" NFR.
- The remaining libraries are Mermaid **source builders** (DSLs emitting Mermaid text), not renderers — out of scope for this problem.

**Source**: architect review 2026-04-11, [`.aod/results/architect.md` §1](/.aod/results/architect.md).

### C. Adopt Kroki HTTP service — REJECTED
Kroki requires network access at pipeline runtime or a local Docker container. Both violate the fresh-install and offline-reliability promises of the tachi pipeline.

### D. Vendor a Mermaid renderer under `scripts/_vendor/` — REJECTED (for this PRD)
No viable pure-Python renderer exists to vendor (see A and B above). If one emerges in the future, vendoring would require its own PRD and ADR covering license compatibility, total LOC added, transitive dep analysis, and maintenance strategy. Out of scope here.

### E. Bundle `@mermaid-js/mermaid-cli` with tachi's install script — NOT CHOSEN
`scripts/install.sh` could auto-install `mmdc` via npm as part of tachi setup. Rejected as the primary path because (a) it assumes npm is already present, which only shifts the prerequisite, and (b) it conflates tachi's install story with the Node.js ecosystem in a way that surprises Python-first users. **However**, the install script SHOULD print a one-line npm install command when `mmdc` is missing — making it easy for users who do have npm to one-click the fix.

---

## Success Metrics

### Primary (Fresh Install Experience)
**SC-130.1**: **Loud-failure rate** — On a machine with no `mmdc`, running `/tachi.security-report` on a project with attack trees aborts at preflight with the expected error message on 100% of runs. Zero cases where the pipeline reports success but ships raw Mermaid source.
- **Baseline**: 0% loud failure (100% silent failure today on fresh installs)
- **Target**: 100% loud failure
- **Measurement**: FR-130.7 CI job on every PR; manual validation on a clean VM during acceptance testing.

**SC-130.2**: **Rendered-output rate** — On a machine with `mmdc` installed, running `/tachi.security-report` on `examples/web-app/` and `examples/mermaid-agentic-app/` produces PDFs where 100% of attack path pages show rendered diagram images.
- **Baseline**: 100% today (developer machines have mmdc installed)
- **Target**: 100% (no regression)
- **Measurement**: `make examples` (or equivalent regeneration) succeeds and baseline diff is clean per ADR-021.

### Secondary (Regression Safety)
**SC-130.3**: **Example output stability** — All 6 example outputs continue to generate successfully on developer machines.
- **Baseline**: 6/6 generate today
- **Target**: 6/6 continue to generate
- **Measurement**: Full example regeneration as part of acceptance testing.

**SC-130.4**: **Baseline byte-determinism** — The 2 attack-tree-bearing examples maintain byte-identical baseline PDFs after regeneration under `SOURCE_DATE_EPOCH=1700000000`, per ADR-021.
- **Baseline**: Byte-deterministic today
- **Target**: Byte-deterministic after refactor
- **Measurement**: Baseline comparison test in the ADR-021 harness.

### Tertiary (Install Script UX)
**SC-130.5**: **Install script clarity** — `scripts/install.sh` prints a clear message about the `mmdc` prerequisite when run on a machine without it.
- **Baseline**: No mention of mmdc in install output today
- **Target**: Clear prerequisite message with one-line install command
- **Measurement**: Manual validation during acceptance testing.

---

## Scope & Boundaries

### In Scope (P0)
- Add preflight `mmdc` availability check to `/tachi.security-report` gated on attack tree inputs (FR-130.1).
- Refactor `scripts/extract-report-data.py:710-778` so silent fallback is removed (FR-130.2).
- Delete the text-fallback branch at `templates/tachi/security-report/attack-path.typ:78-86` (FR-130.3).
- Add loud mid-render failure mode (FR-130.4).
- Author a new README "Prerequisites" section and update `scripts/install.sh` to check for `mmdc` (FR-130.5).
- Invert spec 112 SC-004 and delete/rewrite spec 112 line 135; correct research.md line 80 (FR-130.5).
- Regenerate baselines for the 2 attack-tree-bearing example outputs (FR-130.6).
- Add CI fresh-install acceptance test in a minimal container (FR-130.7).

### Out of Scope
- ❌ **Adopting a runtime Python dependency.** The decision to break the runtime zero-Python-dep constraint established by Feature 128 — if ever made — requires a dedicated PRD and ADR. It MUST NOT be a side effect of a bug fix.
- ❌ **Attack tree content generation changes.** This PRD only changes the rendering and prerequisite story, not how attack trees are authored or extracted from threat-report.md.
- ❌ **Expanding rendering beyond `attack-path.typ`.** Other Typst templates that may embed diagrams (none exist today) are untouched.
- ❌ **Broader dependency strategy overhaul.** Adopting `mmdc` as a hard prerequisite is a targeted decision for one rendering path, not a general move to Node.js-based tooling.
- ❌ **Kroki HTTP integration or network-based rendering.** Explicitly rejected (see Rejected Alternatives C).
- ❌ **Visual spec for a "rendering failed" error page in Typst.** FR-130.3 removes the failing branch entirely; no error-state page needs to be designed.

### Assumptions
1. `mmdc` (`@mermaid-js/mermaid-cli`) remains well-maintained by the Mermaid.js project. (Verified: it is the reference CLI for Mermaid.)
2. The current `shutil.which("mmdc")` call at [scripts/extract-report-data.py:725](scripts/extract-report-data.py#L725) is a reliable availability signal on macOS, Linux, and WSL. (Verified: already used in production without issue.)
3. The existing 2 attack-tree-bearing examples (`examples/web-app/`, `examples/mermaid-agentic-app/`) continue to use the same Mermaid grammar after the refactor — no input changes needed. (Verified: rendering logic is not being changed, only the fallback path.)
4. CI infrastructure can run a job in a minimal container without `mmdc` on `PATH`. (To be validated during plan stage.)

---

## Risks & Dependencies

### Risk 130.1: Install Script May Require More Cross-Platform Polish Than Estimated
- **Likelihood**: Medium.
- **Impact**: Low-Medium — cross-platform install guidance (macOS brew, Linux apt, WSL, Windows) is more nuanced than a single-line install command suggests.
- **Mitigation**: Keep the install-script message minimal and link to the README Prerequisites section for detail; do not try to auto-install mmdc from the script. Plan stage should check how the existing Typst install guidance is phrased and match its style.

### Risk 130.2: Existing Downstream Adopters Relying on Text Fallback
- **Likelihood**: Low — text fallback produces unusable output, so no one is relying on it deliberately. Any user whose pipeline currently ships text fallback is by definition seeing a broken PDF.
- **Impact**: Low — loud-failure actually *improves* their experience by giving them an actionable install command.
- **Mitigation**: Note the change clearly in the CHANGELOG and release notes for the version shipping this fix. No migration guide needed.

### Risk 130.3: Adding a System-Level Prerequisite Surprises Python-First Users
- **Likelihood**: Low — clearly documented.
- **Impact**: Low — one-line install command is trivial to run.
- **Mitigation**: Explicit README Prerequisites section (FR-130.5), install script check (FR-130.5), single-line install command in error message (FR-130.1).

### Risk 130.4: Scope Creep into "General Rendering Strategy"
- **Likelihood**: Low-Medium — team may be tempted to also rework infographic image generation (Gemini API), ASCII diagram rendering, etc.
- **Impact**: Medium — inflates a 5-day fix into a multi-week refactor.
- **Mitigation**: Explicit "Out of Scope" call-out above. Team-lead review during plan and tasks stages must enforce the boundary.

### Critical-Path Note
There is a single serial gate: **the preflight gate design decision** (does mmdc check live inside `extract-report-data.py` before render, inside the `/tachi.security-report` command template before Python invocation, or both?). This choice constrains FR-130.1 through FR-130.5 in sequence and cannot be parallelized. Plan stage must schedule this decision as the first task.

### Dependencies
- **Internal**: None — this is a self-contained change within `scripts/extract-report-data.py`, `templates/tachi/security-report/attack-path.typ`, `scripts/install.sh`, `README.md`, and spec/research.md files.
- **External**: `@mermaid-js/mermaid-cli` — already present in developer environments and already used by the current render path. No new external dep.

---

## Timeline

### Plan Stage Day 0: Spike & Decision Gate
Before any spec or task authoring begins, Plan stage MUST answer:

- **S1**: Where does the preflight gate live? Options: (a) inside `extract-report-data.py` as an early check, (b) inside `.claude/commands/tachi.security-report.md` as a shell preflight before Python invocation, (c) both. Architect chooses; this decision blocks FR-130.1 through FR-130.5.
- **S2**: Does `scripts/install.sh` currently check Typst? If yes, match that style for mmdc. If no, this becomes a larger change that touches the install-script structure.
- **S3**: Can CI run a minimal container without `mmdc` on `PATH`? Validate the test infrastructure path before committing to FR-130.7.

Spike should not exceed 0.5 days. If any answer is unclear, team-lead escalates to defer spec authoring until the spike closes.

### Realistic Work Breakdown (~5 days)

| Task | Effort |
|------|--------|
| Plan Day 0: spike & decision gate (S1–S3) | 0.5d |
| FR-130.1 preflight gate implementation | 0.5d |
| FR-130.2 `extract-report-data.py` refactor (remove silent fallback) | 0.25d |
| FR-130.3 Typst template branch deletion | 0.1d |
| FR-130.4 loud mid-render failure path | 0.25d |
| FR-130.5 docs sync: README Prerequisites section (authoring), install.sh check, spec 112 + research.md edits | 0.75d |
| FR-130.6 baseline regeneration for 2 examples | 0.5d |
| FR-130.7 CI fresh-install test (new container lane) | 0.5d |
| Triad reviews (PM + Architect + Team-Lead) at spec, plan, tasks stages | 0.5d |
| Code review + integration | 0.5d |
| **Total** | **~4.35d** |

5-day target gives 0.65d of buffer for unforeseen Triad re-reviews or CI infrastructure debugging.

---

## Open Questions

- **Q130.1**: Should mid-render failure (FR-130.4) abort the whole pipeline or complete with non-zero exit and a per-finding failure list? **Owner**: architect. **Due**: Plan stage Day 1. **Status**: To be decided during spec authoring.
- **Q130.2**: Where exactly does the preflight gate live — extraction script, command template, or both (S1 in Plan Day 0 spike)? **Owner**: architect. **Due**: Plan stage Day 0. **Status**: Spike gate.
- **Q130.3**: Does CI have a minimal-container lane available, or does FR-130.7 require new CI infrastructure? **Owner**: team-lead. **Due**: Plan stage Day 0. **Status**: Spike gate.

(Previous drafts of this PRD referenced pymmdc feasibility questions — those have been answered during architect review. See Rejected Alternatives A.)

---

## References

### Product Documentation
- Product Vision: [docs/product/01_Product_Vision/product-vision.md](docs/product/01_Product_Vision/product-vision.md)
- PRD Index: [docs/product/02_PRD/INDEX.md](docs/product/02_PRD/INDEX.md)

### Technical Documentation
- Parent spec: [specs/112-attack-path-pages/spec.md](specs/112-attack-path-pages/spec.md)
- Parent research: [specs/112-attack-path-pages/research.md](specs/112-attack-path-pages/research.md)
- Parent PRD: [docs/product/02_PRD/112-attack-path-pages-in-pdf-2026-04-09.md](docs/product/02_PRD/112-attack-path-pages-in-pdf-2026-04-09.md)
- Current render code: [scripts/extract-report-data.py:710-778](scripts/extract-report-data.py#L710-L778)
- Current text fallback to remove: [templates/tachi/security-report/attack-path.typ:78-86](templates/tachi/security-report/attack-path.typ#L78-L86)
- ADR-021 (reproducible PDFs): referenced in CLAUDE.md Feature 128 notes
- Architect review findings: [.aod/results/architect.md](.aod/results/architect.md)
- Team-Lead review findings: [.aod/results/team-lead.md](.aod/results/team-lead.md)

### Source
- GitHub Issue: [#130 — Fix attack path Mermaid rendering when mmdc is not installed](https://github.com/davidmatousek/tachi/issues/130)
- External observation: a downstream project's security report was observed shipping raw Mermaid source after running `/tachi.security-report` without `mmdc` installed. The observation is cited as user-impact evidence only — no external report artifacts are imported into tachi, and the FR-130.7 CI test uses the existing `examples/mermaid-agentic-app/` fixture, not an external one.

### External Sources (Rejected Alternatives)
- [pymmdc on PyPI](https://pypi.org/project/pymmdc/) — not pure-Python; wraps mmdc CLI
- [mmdc (Raziei) on PyPI](https://pypi.org/project/mmdc/) — transitively depends on deprecated PhantomJS
- [mermaid-py on PyPI](https://pypi.org/project/mermaid-py/) — defaults to network HTTP service

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-11 | product-manager | Initial PRD (pymmdc-as-primary approach — superseded) |
| 1.1 | 2026-04-11 | product-manager | Post-review rewrite: pivot to mmdc-as-hard-prerequisite per architect and team-lead findings. pymmdc rejected as factually not pure-Python. All FRs, NFRs, risks, scope, open questions, and timeline updated. Added Rejected Alternatives section. |
