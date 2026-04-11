# Research Summary: Fix Attack Path Mermaid Rendering When mmdc Is Not Installed

**Feature**: 130
**PRD**: [docs/product/02_PRD/130-fix-attack-path-mermaid-rendering-2026-04-11.md](../../docs/product/02_PRD/130-fix-attack-path-mermaid-rendering-2026-04-11.md)
**Date**: 2026-04-11

---

## Codebase Analysis

### Current render logic (`scripts/extract-report-data.py`)
- Function `render_mermaid_to_png()` lives at **lines 710–778**.
- `shutil.which("mmdc")` preflight check is at **line 725**.
- On miss: prints a warning to stderr, sets `has_image=False` on every tree, returns silently. This is the silent-fallback path Feature 130 deletes.
- On hit: spawns `mmdc` subprocess with `-i`, `-o`, `-s 2`, `-b transparent` flags (line ~755). The rendering code itself stays.
- On mid-render failure: catches `CalledProcessError`, warns per-finding, sets `has_image=False` (lines ~763–768). This is the second silent-fallback path Feature 130 makes loud.

### Current Typst template fallback branch (`templates/tachi/security-report/attack-path.typ`)
- **Lines 74–86** contain the conditional render logic.
  - Line 74: `if has-img and img-path != ""` → renders the PNG image.
  - Line 78: `else if mermaid-text != ""` → the text-fallback branch Feature 130 **deletes**. Lines 79–85 wrap raw Mermaid source in `raw(mermaid-text, lang: "mermaid")` with gray background styling.
- After FR-130.3 the entire `else if` block (lines 78–85) is unreachable dead code.

### Preflight gate location options (`.claude/commands/tachi.security-report.md`)
- **Step 1 (lines 39–54)** already contains a `which typst` shell check that aborts with install guidance when Typst is missing. This is the **precedent pattern to mirror**.
- The command flow is: Step 1 Typst check → Step 2 agent invocation → Step 3 artifact detection (attack-trees/ scan at line 71) → `extract-report-data.py` invocation owned by the report-assembler agent.
- **Recommended preflight gate location**: immediately after the Typst check in Step 1, but **gated on attack-trees detection** (the command must not fail on projects that don't need rendering). This means the preflight has two layers: (a) a simple existence check that runs first if the target has `attack-trees/`, and (b) the pre-existing Python-level `shutil.which("mmdc")` in `extract-report-data.py` as defense-in-depth.
- **Alternative**: Move the Python-level check to raise a clear exception instead of returning silently — it already exists at line 725.

### Install script (`scripts/install.sh`)
- **Does NOT currently check Typst**. The Typst check lives in the command file, not install.sh.
- This is a **scope expansion signal**: FR-130.5 "consistent with how the script currently handles Typst" must be reinterpreted as "consistent with the no-check-today baseline" — either (a) add both Typst and mmdc checks to install.sh, or (b) only add the mmdc one-line install hint. This is a Plan Stage Day 0 spike decision (S2 in PRD).

### README (`README.md`)
- **Does NOT currently have a "Prerequisites" section**.
- Natural insertion point: after "## What is tachi?" (around line 29) and **before** "## Quick Start" (lines 30–90).
- FR-130.5 README work is **authoring**, not editing. This matches the PRD language ("Authoring task: create a new 'Prerequisites' section").
- Line 217 mentions "Requires `typst` CLI for PDF compilation" and "optionally `mmdc` (Mermaid CLI) for attack path diagram rendering" inside a developer-guide context. The new Prerequisites section must supersede the "optionally mmdc" framing.

### Parent spec 112 — SC-004 to invert
- **File**: `specs/112-attack-path-pages/spec.md`, **line 125**.
- **Exact current text**:
  > SC-004: When the rendering tool is unavailable, 100% of attack path pages still appear with text fallback — no pages dropped due to rendering failure
- Feature 130 FR-130.5 **replaces this** with a criterion asserting preflight verification and loud failure. The inversion must be explicit (not a silent edit) so the git history is traceable.

### Parent research 112 — line 80 correction
- **File**: `specs/112-attack-path-pages/research.md`, **line 80**.
- **Exact current text**:
  > - Pure Python alternative: `pymmdc` package (no Node.js dependency)
- **Correction**: the pymmdc v0.1.0 package on PyPI is a **thin Python wrapper around the Node.js mmdc CLI** — it requires Node.js + mmdc installed via npm and adds Python ≥3.12 + GPL-3.0 license on top. The line as written is factually wrong. FR-130.5 appends a correction note and captures the durable rationale for the mmdc hard-prerequisite decision at lines 91–93.

### Attack-tree-bearing examples (PRD discrepancy found)
- The PRD asserts `examples/web-app/` has attack trees. **This is incorrect.** `examples/web-app/` has only `threats.md` — no `attack-trees/` directory.
- **Actual attack-tree-bearing examples**:
  - `examples/agentic-app/sample-report/attack-trees/` — 47 files (mix of `.md` + `.png`)
  - `examples/mermaid-agentic-app/attack-trees/` — 24 files (mix of `.md` + `.png`)
- **Impact on FR-130.6 and SC-130.2**: The spec must use `examples/agentic-app/sample-report/` and `examples/mermaid-agentic-app/` as the two attack-tree examples for baseline regeneration, not `examples/web-app/`. This is a **PRD correction** that the spec formalizes.
- FR-130.7 PRD recommendation (use `examples/mermaid-agentic-app/` as the CI fixture) is still correct — that example does have attack trees.

### Preflight pattern precedent
- `shutil.which` appears **exactly once** in the codebase, at `scripts/extract-report-data.py:725`. No other Python-level preflight pattern exists.
- Typst `which` check in the command file (`.claude/commands/tachi.security-report.md` Step 1) is the only shell-level prerequisite pattern.
- **Conclusion**: Feature 130 is both consumer and establisher of the preflight gate pattern. Plan stage should consider whether to extract a reusable helper or keep it inline.

---

## Architecture Constraints

### Runtime Python constraint (hard, from Tech Stack)
- [docs/architecture/00_Tech_Stack/README.md:199–201](../../docs/architecture/00_Tech_Stack/README.md#L199-L201): "All `scripts/*.py` files must use only Python standard library modules." **Zero pip dependencies.**
- Implication: `pymmdc`, `mermaid-py`, `md-mermaid`, and all other PyPI Mermaid packages are **off the table** regardless of their merit. The only acceptable paths are external CLI (current `mmdc`) or bundled assets.
- Feature 128 established pytest as a **dev-time** dep via `pyproject.toml` / `requirements-dev.txt`. Runtime `scripts/*.py` remain stdlib-only. Feature 130 adds no runtime deps.

### Hard-prerequisite precedent (Typst)
- `/tachi.security-report` already treats Typst as a hard prerequisite: checks `which typst` at command entry, aborts loudly with install guidance. This is Feature 054's precedent.
- Feature 130 mirrors this pattern for `mmdc`, with one additional constraint: the check is **gated on attack-tree detection** (not always-on), because projects without attack trees must continue to work regardless of mmdc status.

### Optional-vs-hard prerequisite posture
- [docs/architecture/00_Tech_Stack/README.md:279](../../docs/architecture/00_Tech_Stack/README.md#L279) currently describes mmdc as optional: "When absent, the `/tachi.security-report` command still generates attack path pages but renders the raw Mermaid diagram text instead of a PNG image."
- Feature 130 **flips this**. The Tech Stack doc is an implicit docs-sync target alongside README and spec 112.
- No existing ADR governs CLI-prerequisite posture transitions. **ADR-014** covers optional external **APIs** (Gemini) with graceful degradation — CLI tools are not in its scope. Feature 130 is the first delivery to cross this line and **should produce a new ADR** (likely ADR-022) documenting the decision.

### Determinism / reproducibility (ADR-021)
- [docs/architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md](../../docs/architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md): `SOURCE_DATE_EPOCH=1700000000` is the fixed epoch for baseline generation and the backward-compatibility test.
- Test file: `tests/scripts/test_backward_compatibility.py` (constant at line 36, subprocess env at line 77).
- Scope: test baselines **only**. Production pipelines retain real timestamps.
- Implication for FR-130.6: regenerating baselines for the two attack-tree-bearing examples MUST use `SOURCE_DATE_EPOCH=1700000000` or the `test_backward_compatibility.py` test will fail. Agentic-app was explicitly excluded from byte-determinism in Feature 128's baseline set; the spec must decide whether to keep that exclusion or include it now that attack path rendering is a hard requirement.

### Pipeline overview
- [docs/architecture/01_system_design/README.md](../../docs/architecture/01_system_design/README.md) (Feature 054 pipeline section) shows the data flow: Command validation (which typst) → artifact detection (attack-trees/ scan) → `scripts/extract-report-data.py` → Typst compile.
- mmdc is invoked from inside `extract-report-data.py`, not from the command directly. A shell-level preflight in the command file **cannot** directly assert mmdc behavior inside extraction — it can only assert mmdc is on PATH. Defense-in-depth with the Python-level check is therefore not redundant.

---

## Knowledge Base Findings

### Feature 054 (tachi.security-report / PDF booklet) — established "fail loud on missing prerequisite" pattern
- [.claude/commands/tachi.security-report.md](../../.claude/commands/tachi.security-report.md) Step 1 lines 39–54: Typst `which` check with platform-specific install guidance and non-zero exit.
- Precedent outcome: no user has ever hit a silent failure on missing Typst since Feature 054. This is the pattern to replicate.

### Feature 112 (Attack Path Pages in PDF Reports) — parent feature that introduced the bug
- Original spec codified text fallback as acceptable in **SC-004** and in **line 135** ("text fallback is acceptable").
- Research.md line 80 contains the factual error about pymmdc being "pure Python alternative (no Node.js dependency)."
- Plan/tasks/retro for spec 112 **do not** capture a written rationale for why text fallback was preferred over hard prerequisite. The architect's review for Feature 130 identified this as the root cause of the regression — the decision was never interrogated.
- Feature 130 FR-130.5 corrects these errors and appends a durable rationale at research.md lines 91–93.

### Feature 128 (Executive Threat Architecture Infographic) — reproducible-build precedent
- Introduced `SOURCE_DATE_EPOCH=1700000000` and the `pdf.baseline` file convention in ADR-021.
- Explicitly **excluded** `examples/agentic-app/sample-report/` from byte-deterministic baselines because its attack path rendering was fragile. Feature 130 fixes the fragility but must consciously decide whether to include `agentic-app` in the baseline set now.
- Feature 128 also established pytest as dev-time dep infrastructure. Feature 130's FR-130.7 CI fresh-install test can build on this.

### PAT-005 (Threat Infographic — graceful degradation) — pattern explicitly NOT followed here
- PAT-005 says: optional external enhancements degrade gracefully if the local artifact retains value.
- Feature 130 deliberately rejects PAT-005 for `mmdc` because raw Mermaid text in a rendered PDF has **no independent value** — it is a broken artifact, not a degraded one. The spec should cite this contrast explicitly so future reviewers do not misapply PAT-005 to rendering paths.

### No prior silent-fallback deletion in tachi's history
- Feature 130 is the **first delivered feature** that deliberately removes a `warn-and-continue` code path in favor of `fail-loud`. The spec should note this as precedent-setting so Plan stage captures the rationale in a new ADR.

### GitHub Issue #130
- Status: Open. Labeled `P0`, `bug`, `stage:plan`.
- PRD approved 2026-04-11 (rev 1.1 after round-2 Triad review). ICE score documented at 27/27.
- Root cause: Spec 112 codified "text fallback is acceptable" without interrogating the rationale; research.md:80 made a pymmdc factual error that propagated; no preflight gate existed to catch the silent failure on fresh installs.

---

## Industry Research

### Dependency posture for diagram-as-code pipelines
- **Mermaid**: `@mermaid-js/mermaid-cli` is the reference CLI maintained by the Mermaid.js project. MIT license, widely used, supply chain in good standing. This is what tachi already uses.
- **pymmdc (PyPI)**: v0.1.0 wraps the Node.js mmdc CLI. Not pure Python. GPL-3.0. Python ≥3.12. Single 0.1.0 release, single-individual maintainer. Disqualified on correctness, license, and Python version.
- **mmdc (Raziei, PyPI)**: transitively depends on PhantomJS, deprecated since 2017, archived 2019. Disqualified on security posture.
- **mermaid-py**: defaults to `mermaid.ink` HTTP service. Violates tachi's offline-pipeline NFR.
- **Kroki**: HTTP service or local Docker. Violates fresh-install + offline promises.

### Fail-loud vs silent-degrade precedent in the ecosystem
- GitHub Actions, pre-commit, and most CI tools fail fast on missing binaries. This is the dominant convention and users expect it.
- The `shutil.which` preflight pattern is standard Python practice for any tool that shells out to CLIs; the Python docs explicitly recommend it for portable availability checks.

---

## Recommendations for Spec

**Include**:
- Three user stories mapped 1:1 to PRD US-130.1, US-130.2, US-130.3 with all ACs transcribed.
- Seven functional requirements mapped 1:1 to PRD FR-130.1 through FR-130.7 with file/line citations from this research to make them unambiguous.
- Explicit correction: `examples/web-app/` does NOT have attack trees — FR-130.6 must target `examples/agentic-app/sample-report/` and `examples/mermaid-agentic-app/`. Document the PRD error.
- Plan stage Day 0 spike S1/S2/S3 gate (per PRD timeline section) — referenced in Assumptions, not as an FR.
- Success criteria SC-130.1 through SC-130.5 mapped 1:1 from PRD.
- Explicit scope boundary: no ADR for CLI prerequisite posture today in tachi; Feature 130 should produce **ADR-022** as a deliverable of the Plan stage, not the Spec stage.
- Edge cases: attack-trees/ directory exists but is empty; attack-trees/ directory exists but no Critical/High findings; mmdc is present but out of version range; mmdc errors on syntactically valid Mermaid.

**Avoid**:
- Restating the rejected alternatives section in full — reference the PRD.
- Specifying the *mechanism* of the preflight gate (Python vs shell vs both) — that is a Plan-stage decision per PRD S1.
- Specifying CI infrastructure details — per PRD S3 that is a Plan-stage spike.

**Clarifications required before PM sign-off**:
- None anticipated. PRD is revision 1.1 with full Triad sign-off; all three key open questions (Q130.1, Q130.2, Q130.3) are explicitly Plan-stage decisions, not spec-stage clarifications.
- One PRD factual error (`examples/web-app/` has attack trees) is corrected inline in the spec with an audit trail in this research doc — no user clarification needed.
