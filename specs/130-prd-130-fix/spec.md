---
prd_reference: docs/product/02_PRD/130-fix-attack-path-mermaid-rendering-2026-04-11.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-11
    status: APPROVED
    notes: "Faithful translation of PRD rev 1.1: all 3 user stories, 7 FRs, 5 SCs, and 7 out-of-scope items trace through. All 4 deliberate deviations (examples correction, Tech Stack doc add, SC-130.6 code-deletion grep, expanded edge cases) verified as reasonable, none are scope creep. No [NEEDS CLARIFICATION] markers. 6 non-blocking observations in .aod/results/product-manager.md. Ready for Plan Stage."
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: Fix Attack Path Mermaid Rendering When mmdc Is Not Installed

**Feature Branch**: `130-prd-130-fix`
**Created**: 2026-04-11
**Status**: Draft
**PRD Reference**: [docs/product/02_PRD/130-fix-attack-path-mermaid-rendering-2026-04-11.md](../../docs/product/02_PRD/130-fix-attack-path-mermaid-rendering-2026-04-11.md)
**Research**: [research.md](research.md)
**Input**: User description: "PRD: 130 - fix-attack-path-mermaid-rendering"

## Overview

When a user runs `/tachi.security-report` on a project with attack trees on a machine that does not have `@mermaid-js/mermaid-cli` (`mmdc`) installed, the pipeline silently ships a PDF where each attack path page contains 40+ lines of raw `flowchart TD` Mermaid source instead of a rendered diagram. The pipeline reports success. The user only discovers the failure by flipping through the PDF. This violates the acceptance criteria of spec 112 (attack-path-pages) and blocks the flagship "show to exec board" use case.

This feature turns that silent failure into a loud, actionable one. `/tachi.security-report` gains a preflight check that aborts immediately with a one-line install command when `mmdc` is missing and attack trees are present. The text-fallback branch in the Typst template is deleted entirely as unreachable dead code. `README.md`, `scripts/install.sh`, and the parent spec 112 documents are updated to reflect the new hard-prerequisite posture.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Prerequisites Are Enforced, Not Assumed (Priority: P1)

As a developer evaluating tachi on a fresh machine, when I run `/tachi.security-report` on a project with attack trees without having installed every prerequisite, I want the pipeline to abort immediately at preflight with an error message that names the missing tool and gives me the exact install command — so that I can install it and re-run, rather than discover a broken PDF after the pipeline claims success.

**Why this priority**: This is the core user-experience fix. Without this story, the other two stories do not deliver value — a loud mid-render failure mode (US2) and documented prerequisites (US3) matter only because preflight enforcement exists to catch the case at the front door. It is also the only story that prevents the observed regression where downstream users shipped raw Mermaid source in board-ready PDFs.

**Independent Test**: Can be fully tested by running `/tachi.security-report` on a fixture project with attack trees on a machine where `mmdc` is not on `PATH`, and asserting that the pipeline exits non-zero with a stderr message naming the missing tool and the exact `npm install -g @mermaid-js/mermaid-cli` command. Delivers value as a standalone fix even if US2 and US3 are not yet delivered.

**Acceptance Scenarios**:

1. **Given** a machine without `mmdc` on `PATH` and a target project with Critical or High attack trees in `attack-trees/`, **When** the user runs `/tachi.security-report`, **Then** the pipeline aborts at preflight with exit code non-zero and stderr contains all three of: (a) the missing prerequisite name (`@mermaid-js/mermaid-cli` or `mmdc`), (b) the reason it is needed (attack path rendering), and (c) the single-line install command `npm install -g @mermaid-js/mermaid-cli`.
2. **Given** the same machine without `mmdc`, **When** the user runs `/tachi.security-report` on a project that has no `attack-trees/` directory or where the directory contains no Critical/High attack tree files, **Then** the pipeline runs to completion normally — the mmdc check MUST NOT fire on projects that do not need rendering.
3. **Given** a machine with `mmdc` installed and a target project with Critical/High attack trees, **When** the user runs `/tachi.security-report`, **Then** the pipeline proceeds and every attack path page in the generated PDF contains a rendered diagram image. No raw Mermaid source appears anywhere in the PDF.
4. **Given** the generated PDF is viewed at page size, **When** a reader examines any attack path diagram, **Then** node labels and edge connections are legible — consistent with the legibility bar established in spec 112 SC-003.

---

### User Story 2 - Rendering Failure Is Loud, Not Silent (Priority: P1)

As a developer running `/tachi.security-report` on a machine where `mmdc` is installed, when diagram rendering fails mid-run for any reason (invalid Mermaid syntax, mmdc crash, subprocess timeout), I want the pipeline output to list exactly which findings failed and why, and I want the exit code to be non-zero — so that I can immediately decide whether to fix the input, file a bug, or regenerate, rather than discover the failure only by flipping through the PDF.

**Why this priority**: Preflight (US1) catches the common "missing tool" case but cannot catch the rarer "tool present but render failed" case. Both cases previously produced the same silent, broken-looking PDF. US2 closes the second case. P1 because an installed-but-broken renderer is still a common failure mode in CI and on drift-prone developer machines.

**Independent Test**: Can be fully tested by feeding `render_mermaid_to_png()` a deliberately malformed Mermaid file and asserting the pipeline exits non-zero and prints a per-finding failure line to stderr that identifies the failing finding ID. Delivers value independently of US1 and US3.

**Acceptance Scenarios**:

1. **Given** `mmdc` is installed but the pipeline encounters an invalid Mermaid source file for one or more attack trees, **When** the pipeline completes (or aborts, depending on the design decision in FR-130.4), **Then** the command output explicitly lists each failed finding ID and a short reason on stderr, AND the exit code is non-zero.
2. **Given** a mid-render failure, **When** the user inspects any PDF that was produced, **Then** the PDF does not contain a page that silently substitutes raw Mermaid text as if it were a legitimate deliverable. Either the pipeline aborts before PDF generation, or the failing attack path page does not appear, or a clearly labeled error-state page is emitted. The specific visual outcome is decided during Plan Stage per Q130.1 in the PRD.
3. **Given** multiple attack trees where some render successfully and one fails, **When** the pipeline runs, **Then** the failure list in stderr identifies exactly the failed finding IDs (not a generic "rendering failed" message), so the user knows which input to inspect.

---

### User Story 3 - Documented Dependency Posture (Priority: P1)

As a developer installing tachi or reading the README before running any command, I want to see a single, unambiguous statement of the external tools tachi needs to produce a complete security report PDF and the exact install commands for each tool — so that I can prepare my environment before running the pipeline rather than debug missing dependencies after the fact.

**Why this priority**: Preflight enforcement (US1) is the safety net; documented prerequisites are the happy path. A user who reads the README before running never hits the safety net. P1 because the feature's explicit goal is a better first-run experience and that requires both: the documentation and the gate.

**Independent Test**: Can be fully tested by a human reader reviewing the updated README for a "Prerequisites" section that names `typst` and `@mermaid-js/mermaid-cli`, and by running `scripts/install.sh` on a machine without `mmdc` and asserting the script prints a mmdc-presence message with a one-line install command. Delivers value independently of US1 and US2.

**Acceptance Scenarios**:

1. **Given** a new user opens `README.md` for the first time, **When** they scroll to the top of the document before running any command, **Then** a "Prerequisites" section is present that explicitly names `typst` and `@mermaid-js/mermaid-cli` with install commands for macOS (brew), Linux (apt/dnf), and WSL.
2. **Given** `scripts/install.sh`, **When** a user runs it on a machine without `mmdc` on `PATH`, **Then** the script prints a clear message identifying `mmdc` as a prerequisite for attack path rendering and suggests the one-line `npm install -g @mermaid-js/mermaid-cli` command. The script does not silently succeed without mentioning mmdc.
3. **Given** `specs/112-attack-path-pages/research.md`, **When** a future engineer reads it, **Then** line 80 no longer claims pymmdc is a pure-Python alternative, AND a durable rationale block captures the mmdc-hard-prerequisite decision with a reference to this feature (130) and to the PRD's Rejected Alternatives section.
4. **Given** `specs/112-attack-path-pages/spec.md`, **When** a future engineer reads SC-004, **Then** the prior text (text-fallback is acceptable) has been replaced by a criterion asserting preflight verification and loud failure, and line 135 ("text fallback is acceptable") has been removed or rewritten.

---

### Edge Cases

- **Attack trees directory present but empty**: `examples/mermaid-agentic-app/attack-trees/` exists but contains zero `.md` files. The preflight gate MUST NOT fire, because no rendering is needed. Detection must be "at least one attack tree file present," not "directory exists."
- **Attack trees directory contains only Low/Medium severity findings**: tachi only renders Critical and High per spec 112. If all findings are Low/Medium, no rendering happens, so the preflight gate MUST NOT fire.
- **mmdc present but out of version range**: If `mmdc --version` returns a version that breaks the subprocess call signature Feature 130 relies on, the pipeline must surface this as a mid-render failure (US2), not a silent fallback. Version pinning is out of scope for this feature; failure mode is the safety net.
- **mmdc present, valid Mermaid, but subprocess hangs**: A hung subprocess is caught by the existing timeout handling and reported via the US2 loud-failure path. No new timeout handling is introduced by this feature.
- **`SOURCE_DATE_EPOCH` is set in the developer environment**: Baseline regeneration under FR-130.6 must use `SOURCE_DATE_EPOCH=1700000000` per ADR-021, regardless of what the developer's shell already has set.
- **Node.js is present but `mmdc` is not installed via npm**: The preflight message names `npm install -g @mermaid-js/mermaid-cli`, which silently assumes the user has npm. This is acceptable — npm is a transitive prerequisite of `mmdc` and installing mmdc without npm is not a path tachi supports. The error message does not need to address Node.js absence separately.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-130.1**: `/tachi.security-report` MUST implement a preflight check for `mmdc` availability that runs at the start of the pipeline **when attack tree inputs are detected**. If the check fails, the pipeline MUST abort immediately with a non-zero exit code and an error message of the form:
  ```
  Attack path rendering requires @mermaid-js/mermaid-cli (mmdc).
  Install with: npm install -g @mermaid-js/mermaid-cli
  Then re-run /tachi.security-report.
  ```
  The check MUST complete before any rendering work begins. The check MUST NOT fire on projects without attack tree inputs — detection is gated on "at least one Critical/High attack tree file is present in `attack-trees/`," not merely "directory exists." The mechanism by which the preflight gate is implemented (inside [scripts/extract-report-data.py](../../scripts/extract-report-data.py), inside [.claude/commands/tachi.security-report.md](../../.claude/commands/tachi.security-report.md), or both as defense-in-depth) is a Plan Stage decision per PRD Open Question Q130.2 / Plan Day 0 spike S1.

- **FR-130.2**: The `render_mermaid_to_png()` function at [scripts/extract-report-data.py:710-778](../../scripts/extract-report-data.py#L710-L778) MUST be updated so that when `mmdc` is unavailable the function either (a) is never reached because the preflight gate in FR-130.1 has already aborted the pipeline, or (b) raises a clear exception rather than silently marking every entry as `has_image=False`. The current `if not shutil.which("mmdc"):` silent-warn path at line 725 MUST be eliminated. No code path remains where missing mmdc produces `has_image=False` without also raising or aborting.

- **FR-130.3**: The `else if mermaid-text != ""` branch at [templates/tachi/security-report/attack-path.typ:78-86](../../templates/tachi/security-report/attack-path.typ#L78-L86) MUST be **deleted entirely**. Lines 78–85 that render raw Mermaid source as fallback content are unreachable dead code after FR-130.1 lands. No visual design for the removed state is needed because the state ceases to exist. The remaining `if has-img and img-path != ""` branch is the only supported render path.

- **FR-130.4**: When `mmdc` is installed and running but fails on a specific attack tree (syntax error, timeout, crash), the pipeline MUST print an explicit stderr warning listing the failed finding ID and a short cause, AND MUST exit with a non-zero code. The pipeline MUST NOT ship a PDF page containing raw Mermaid text as if it were a legitimate deliverable. The Plan Stage architect review decides whether mid-render failure aborts the whole pipeline (simpler) or completes with non-zero exit and a per-finding failure list (more informative) — this is PRD Open Question Q130.1.

- **FR-130.5**: The following docs-sync changes MUST ship in the same feature delivery:
  - **[README.md](../../README.md)**: Author a new "## Prerequisites" section positioned between "## What is tachi?" (~line 29) and "## Quick Start" (~line 30). The section MUST name `typst` and `@mermaid-js/mermaid-cli` and provide install commands for macOS (brew), Linux (apt/dnf), and WSL. README does not currently contain a Prerequisites section; this is authoring, not editing.
  - **[scripts/install.sh](../../scripts/install.sh)**: Add an `mmdc` presence check. The script does not currently check Typst — Plan Stage decides whether to (a) add both Typst and mmdc checks for consistency, or (b) add only the mmdc check with an inline note to align with how the command-level Typst check works (PRD Plan Day 0 spike S2).
  - **[specs/112-attack-path-pages/spec.md](../../specs/112-attack-path-pages/spec.md)**: Line 125 (SC-004 — "When the rendering tool is unavailable, 100% of attack path pages still appear with text fallback") MUST be **inverted**. The new SC-004 MUST assert that rendering tool availability is verified at preflight and the pipeline aborts loudly if unavailable. Line 135 ("text fallback is acceptable") MUST be removed or rewritten to mark text fallback as a removed shipping mode.
  - **[specs/112-attack-path-pages/research.md](../../specs/112-attack-path-pages/research.md)**: Line 80 ("Pure Python alternative: pymmdc package (no Node.js dependency)") MUST be corrected. Append a note that pymmdc on PyPI is a thin Python wrapper around the Node.js `@mermaid-js/mermaid-cli` CLI and is not a pure-Python renderer. Lines 91–93 MUST carry a durable rationale block for the mmdc hard-prerequisite decision with references to Feature 130 and the PRD Rejected Alternatives section.
  - **[docs/architecture/00_Tech_Stack/README.md](../../docs/architecture/00_Tech_Stack/README.md)** line 279: The sentence describing mmdc as optional with text fallback MUST be updated to describe it as a hard prerequisite for projects with attack trees. This target was missed in the PRD but is required for doc-corpus consistency — the spec adds it.

- **FR-130.6**: All 6 example outputs under [examples/](../../examples/) MUST continue to generate without errors after this change on developer machines where `mmdc` is present. The two attack-tree-bearing examples are:
  - [examples/agentic-app/sample-report/](../../examples/agentic-app/sample-report/) — 47 attack tree files
  - [examples/mermaid-agentic-app/](../../examples/mermaid-agentic-app/) — 24 attack tree files

  **PRD Correction**: The PRD named `examples/web-app/` as attack-tree-bearing. This is factually incorrect — `examples/web-app/` has only `threats.md` and no `attack-trees/` directory. The spec corrects this. The two examples above are the correct regeneration targets.

  Baseline regeneration for these two examples MUST use `SOURCE_DATE_EPOCH=1700000000` per ADR-021. Whether `examples/agentic-app/sample-report/` rejoins the byte-deterministic baseline set (it was excluded in Feature 128) is a Plan Stage decision — the spec requires only that regeneration succeed and produce rendered diagrams, not that it achieve byte-determinism.

- **FR-130.7**: A CI job MUST run in a minimal container where `mmdc` is **not** installed on `PATH` and assert that running `/tachi.security-report` on a fixture project with attack trees aborts at preflight with the expected error message. This job MUST run on every pull request that touches any of: [scripts/extract-report-data.py](../../scripts/extract-report-data.py), [templates/tachi/security-report/attack-path.typ](../../templates/tachi/security-report/attack-path.typ), [scripts/install.sh](../../scripts/install.sh), [.claude/commands/tachi.security-report.md](../../.claude/commands/tachi.security-report.md), and [README.md](../../README.md). The test fixture MUST be [examples/mermaid-agentic-app/](../../examples/mermaid-agentic-app/) — an existing example with attack trees. No new test project is introduced. Whether the CI infrastructure can run a minimal container without mmdc on PATH is a Plan Stage decision per PRD Plan Day 0 spike S3.

### Key Entities

- **Attack tree**: A Mermaid `flowchart TD` diagram describing an attack path for a Critical or High severity finding. Stored as `.md` files under `attack-trees/` in a target project. Rendered to PNG at 2x resolution by `mmdc` for inclusion in the security report PDF. The unit of rendering work governed by this spec.
- **Preflight gate**: A pre-pipeline availability check for a required external CLI tool. Runs before any rendering work begins. Exits non-zero with an actionable install message if the tool is missing. Feature 130 introduces the first such gate for `mmdc`; the existing `which typst` check in Step 1 of `.claude/commands/tachi.security-report.md` is the precedent pattern.
- **Render failure (mid-render)**: Any failure of `mmdc` to produce a PNG from a valid-looking attack tree input after the preflight gate has passed. Includes invalid Mermaid syntax, mmdc subprocess crash, and subprocess timeout. Distinguished from preflight failures because `mmdc` is known to be available when the failure occurs.
- **Text fallback**: The deleted code path. Before Feature 130: when `mmdc` was absent or render failed, the Typst template rendered raw Mermaid source as a code block in the PDF. After Feature 130: this path does not exist.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-130.1 (Loud-failure rate)**: On a machine with no `mmdc` on `PATH`, running `/tachi.security-report` on a project with attack trees aborts at preflight with the expected error message on 100% of runs. Zero cases where the pipeline reports success but ships raw Mermaid source. **Baseline**: 0% loud failure (100% silent failure today). **Target**: 100% loud failure. **Measurement**: FR-130.7 CI job on every PR + manual validation on a clean VM during acceptance testing.

- **SC-130.2 (Rendered-output rate)**: On a machine with `mmdc` installed, running `/tachi.security-report` on [examples/agentic-app/sample-report/](../../examples/agentic-app/sample-report/) and [examples/mermaid-agentic-app/](../../examples/mermaid-agentic-app/) produces PDFs where 100% of attack path pages show rendered diagram images. **Baseline**: 100% today (developer machines have mmdc installed). **Target**: 100% (no regression). **Measurement**: Manual PDF inspection + existing `test_backward_compatibility.py` run under `SOURCE_DATE_EPOCH=1700000000`.

- **SC-130.3 (Example output stability)**: All 6 example outputs under `examples/` continue to generate successfully on developer machines. **Baseline**: 6/6 generate today. **Target**: 6/6 continue to generate. **Measurement**: Full example regeneration as part of acceptance testing.

- **SC-130.4 (Baseline byte-determinism)**: The attack-tree-bearing examples that participate in the byte-deterministic baseline set maintain byte-identical baseline PDFs after regeneration under `SOURCE_DATE_EPOCH=1700000000` per ADR-021. (Note: `examples/agentic-app/sample-report/` was explicitly excluded from the baseline set in Feature 128; whether it rejoins is a Plan Stage decision.) **Baseline**: current byte-deterministic set holds. **Target**: unchanged or expanded, not reduced. **Measurement**: `test_backward_compatibility.py` passes on main after merge.

- **SC-130.5 (Install script clarity)**: `scripts/install.sh` prints a clear message about the `mmdc` prerequisite when run on a machine without it. **Baseline**: no mention of mmdc in install output today. **Target**: clear prerequisite message with one-line install command. **Measurement**: Manual validation during acceptance testing on a clean VM.

- **SC-130.6 (Deleted code actually deleted)**: After merge, neither `else if mermaid-text != ""` appears anywhere in [templates/tachi/security-report/attack-path.typ](../../templates/tachi/security-report/attack-path.typ), nor does a silent `has_image=False` fallback on missing `mmdc` appear in [scripts/extract-report-data.py:710-778](../../scripts/extract-report-data.py#L710-L778). **Baseline**: both paths exist today. **Target**: zero occurrences. **Measurement**: grep review in PR.

## Assumptions

1. **`mmdc` remains well-maintained**: The Mermaid.js project continues to maintain `@mermaid-js/mermaid-cli`. (Verified: it is the reference CLI for Mermaid.js, actively released.)
2. **`shutil.which("mmdc")` is reliable across platforms**: The call at [scripts/extract-report-data.py:725](../../scripts/extract-report-data.py#L725) is a reliable availability signal on macOS, Linux, and WSL. (Verified: already used in production without reported false positives or negatives.)
3. **The two attack-tree-bearing examples continue to use the same Mermaid grammar**: `examples/agentic-app/sample-report/` and `examples/mermaid-agentic-app/` continue to use the current Mermaid dialect. No input-side changes are required.
4. **Plan Stage Day 0 spike resolves S1, S2, S3**: The PRD's Plan Stage Day 0 spike will answer:
   - **S1**: Where does the preflight gate live — in `extract-report-data.py`, in `.claude/commands/tachi.security-report.md`, or both?
   - **S2**: Does `scripts/install.sh` currently check Typst (no, per research) — and should Feature 130 add both checks, or only mmdc?
   - **S3**: Can CI run a minimal container without `mmdc` on `PATH`?

   The spec does not pin these decisions. They are Plan Stage work.
5. **Feature 130 produces a new ADR**: No existing ADR governs CLI-prerequisite posture transitions (ADR-014 covers optional external APIs, not CLI tools). Plan Stage MUST produce **ADR-022** (next available number) documenting the decision to treat `mmdc` as a hard prerequisite gated on attack-tree detection. This is a Plan Stage deliverable, not a spec deliverable, but the spec asserts it will exist.
6. **No runtime Python dependency is added**: The runtime `scripts/*.py` stdlib-only constraint established by Feature 128 remains intact. All rejected alternatives (pymmdc, mermaid-py, mmdc-Raziei, Kroki) are off the table per the PRD Rejected Alternatives section.

## Dependencies

### Internal
- **Feature 054** (tachi.security-report PDF booklet) — established the "fail loud on missing prerequisite" precedent for Typst that Feature 130 replicates for `mmdc`.
- **Feature 112** (attack-path-pages) — the feature being corrected. SC-004 is inverted, research.md line 80 is corrected, and the text-fallback branch introduced in this feature is deleted.
- **Feature 128** (executive architecture infographic) — established ADR-021 and `SOURCE_DATE_EPOCH=1700000000` for baseline reproducibility. FR-130.6 baseline regeneration depends on this convention.

### External
- **`@mermaid-js/mermaid-cli`** — already present in developer environments and already used by the current render path. No new external dep; the feature just makes the existing dep explicit and enforced.

## Out of Scope

- Adopting a runtime Python dependency (pymmdc, mermaid-py, any PyPI Mermaid package). All alternatives were evaluated in the PRD and rejected. A decision to break the runtime zero-Python-dep constraint would require its own PRD and ADR.
- Attack tree content generation changes. This spec only changes rendering and prerequisite enforcement, not how attack trees are authored or extracted from `threat-report.md`.
- Expanding rendering beyond `attack-path.typ`. Other Typst templates that might embed diagrams (none do today) are untouched.
- Broader dependency strategy overhaul. Adopting `mmdc` as a hard prerequisite is a targeted decision for one rendering path, not a general move toward Node.js-based tooling.
- Kroki HTTP integration or any network-based rendering. Explicitly rejected (PRD Rejected Alternatives C).
- Visual design for a "rendering failed" error page in Typst. FR-130.3 removes the failing branch entirely; no error-state page is needed.
- Version pinning or capability checks on `mmdc` (e.g., minimum version). If the installed `mmdc` fails to satisfy the pipeline's needs, the US2 loud-failure path surfaces it — no new version-checking logic is introduced.
