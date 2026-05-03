# ADR-022: `mmdc` as Hard Prerequisite Gated on Attack-Tree Detection

**Status**: Accepted
**Date**: 2026-04-11
**Deciders**: Architect, Product Manager, Team-Lead
**Related Feature**: Feature 130 — Fix Attack Path Mermaid Rendering When `mmdc` Is Not Installed
**Related ADRs**: [ADR-014](ADR-014-gemini-api-optional-image-generation.md) (optional external APIs), [ADR-021](ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) (determinism)

---

## Context

Feature 112 (attack-path-pages) introduced Mermaid `flowchart TD` attack path diagrams as the visual backbone of the tachi security-report PDF booklet. The rendering path invokes `@mermaid-js/mermaid-cli` (the `mmdc` binary) via `subprocess.run` inside `scripts/extract-report-data.py::render_mermaid_to_png()`. When `mmdc` was absent from `PATH`, the original Feature 112 implementation fell back silently to raw Mermaid source rendered as a Typst `raw` code block inside `templates/tachi/security-report/attack-path.typ`.

The silent-fallback behavior was discovered in the field (Issue #130, 2026-04-11): a developer running `/tachi.security-report` on a project with Critical/High attack trees on a shell without `mmdc` shipped a PDF containing 40+ lines of raw `flowchart TD` source on every attack-path page. The pipeline reported success. The user only noticed by flipping through the PDF.

This violated:
- **Feature 112 SC-003**: attack path diagrams must be legible at page size.
- **Feature 054 precedent**: Typst is already a hard prerequisite enforced at command entry (`which typst` in `.claude/commands/tachi.security-report.md` Step 1, lines 39-54). Treating `mmdc` differently was an inconsistency, not a design choice.
- **Constitutional Observability principle (VIII)**: silent degradation masks failure signal.

No existing ADR governed CLI-prerequisite posture. [ADR-014](ADR-014-gemini-api-optional-image-generation.md) governs **optional external APIs** (image generation via Gemini with graceful degradation), which is a different class of dependency: Gemini is network-dependent, API-keyed, and truly optional because the underlying infographic spec is the primary deliverable. `mmdc` is local-only, unkeyed, and the rendered PNG **is** the deliverable for attack-path pages — there is no "spec-first" equivalent.

A decision is needed on the tachi posture for CLI tools that are **locally installable, shell-invokable, and sit on the critical path of a specific pipeline branch**.

---

## Decision

**`@mermaid-js/mermaid-cli` (the `mmdc` binary) is a hard prerequisite when `attack-trees/` contains at least one Critical or High severity finding.** When absent, the `/tachi.security-report` pipeline aborts at preflight with a non-zero exit code and the canonical error message:

```
Attack path rendering requires @mermaid-js/mermaid-cli (mmdc).
Install with: npm install -g @mermaid-js/mermaid-cli
Then re-run /tachi.security-report.
```

**Scope**:
- **Enforcement**: Defense-in-depth with two preflight gates:
  1. Shell-level `command -v mmdc` in `.claude/commands/tachi.security-report.md` Step 1 (mirroring the existing Typst check in the same file)
  2. Python-level `shutil.which("mmdc")` in `scripts/extract-report-data.py::render_mermaid_to_png()`, converted from silent `return` to `raise RuntimeError(...)`
- **Gating**: Both checks fire only when `attack-trees/*.md` contains at least one file. Projects without attack trees continue to work without `mmdc`. This preserves backward compatibility for the majority of tachi consumers who do not use attack-path diagrams.
- **Silent-fallback path deletion**: The `else if mermaid-text != ""` branch at `templates/tachi/security-report/attack-path.typ:78-86` is deleted entirely as unreachable dead code. No visual design for the "render failed" state is produced because the state ceases to exist.
- **Install.sh courtesy warning**: `scripts/install.sh` prints a clear warning if `mmdc` is absent at installation time. This is a best-effort early signal; the per-command preflight gate is the enforcement point.
- **Runtime Python stdlib-only constraint preserved**: The preflight check uses `shutil.which`, already imported. No new runtime Python dependency introduced. The Feature 128 zero-runtime-dep rule holds.

**Value**: `npm install -g @mermaid-js/mermaid-cli` is the canonical install command. It appears in exactly 7 locations across the codebase (documented in task T023 and verified by grep in Feature 130).

---

## Rationale

1. **Parity with Feature 054 Typst posture**: Typst is already a hard prerequisite at the command level. Treating the second critical-path CLI (`mmdc`) the same way is the consistent choice, not a new pattern.
2. **Fail loud is the correct default for critical-path work**: A security report PDF is an auditable deliverable. Shipping a PDF that looks legitimate but contains raw Mermaid source on every attack-path page is worse than shipping no PDF at all. Constitutional Principle VIII (Observability & Root Cause Analysis) requires that degradation be visible, not masked.
3. **Attack-tree gating preserves backward compatibility**: Projects without attack trees do not need `mmdc` and are unaffected. The gate fires only when `attack-trees/*.md` exists, so adopters using tachi for threat modeling without the Feature 112 attack-path output continue to work unchanged.
4. **Defense-in-depth is cheap and justified**: The shell-level check catches the common case (user runs the slash command). The Python-level check catches direct-invocation paths (tests, tooling, CI scripts). Both gates are ~3 lines of code each. No abstraction is introduced; each check is inline and local to its invocation point. The decision to extract a reusable helper is deferred to Future Work below.
5. **Runtime stdlib-only constraint honored**: `shutil.which` and `subprocess.run` are already imported. No new Python dependency. All rejected alternatives (pymmdc, mermaid-py, Kroki HTTP) were evaluated in the PRD and remain rejected.
6. **Empirically verified**: The existing `scripts/extract-report-data.py::render_mermaid_to_png()` already contains a `shutil.which("mmdc")` check at line 725. Feature 130 converts the silent-warn-and-fallback behavior into a `raise RuntimeError(...)` — a minimal-surface change rather than a new check.

---

## Alternatives Considered

### A. Adopt a pure-Python Mermaid renderer (pymmdc, mermaid-py)
**Rejected.** `pymmdc` on PyPI is a thin Python wrapper around the Node.js `@mermaid-js/mermaid-cli` CLI — it does not eliminate the `mmdc` dependency, only hides it. It is also GPL-3.0 licensed, which is incompatible with tachi's distribution model. `mermaid-py` is unmaintained and produces degraded output. No viable pure-Python alternative exists that preserves the current `-s 2` (2x scale) legibility. Evaluated in PRD Rejected Alternatives A and documented as a correction in `specs/112-attack-path-pages/research.md` line 80 (Feature 130 T017).

### B. Kroki HTTP rendering
**Rejected.** Kroki is a hosted diagram rendering service accessed via HTTP. Network-dependent rendering violates the "no network during pipeline" constraint and introduces availability, privacy, and rate-limiting concerns for security reports. Explicitly rejected in PRD Rejected Alternative C.

### C. Graceful degradation with a visible placeholder
**Rejected.** The text-fallback branch in `attack-path.typ:78-86` was a graceful-degradation design that shipped broken-looking PDFs and masked the rendering failure. The Feature 130 post-mortem determined that any "degraded but shipping" design has the same failure mode. Fail-loud is the only posture that guarantees the user sees the failure.

### D. Auto-install `mmdc` from `scripts/install.sh`
**Rejected.** Shifts the prerequisite to "must have `npm`" without eliminating the external dependency. Adds `npm install -g` side effects to the install script, which is out of scope for a tooling installer. Evaluated in PRD Rejected Alternative E.

### E. Single preflight check (shell-only or Python-only)
**Rejected.** Shell-only leaves direct Python invocations (tests, tooling) silently broken. Python-only fails the Feature 054 precedent and requires agent orchestration to reach the failure. Defense-in-depth with both checks costs ~5 lines of code total and closes both invocation paths. The architecturally consistent choice is to mirror the Typst check pattern at the command level AND preserve the Python-level check as a safety net.

---

## Consequences

### Positive

- **Loud-failure contract honored**: On a shell without `mmdc`, `/tachi.security-report` aborts at preflight with an actionable install command. Zero cases where the pipeline reports success but ships raw Mermaid source.
- **Tech Stack doc clarity**: `docs/architecture/00_Tech_Stack/README.md` is updated to describe `mmdc` as a hard prerequisite for projects with attack trees, cross-linking to this ADR.
- **Feature 112 SC-003 recovered**: Attack path diagrams are legible at page size because they are always rendered PNGs, not raw source dumps.
- **Runtime stdlib-only preserved**: No new Python dependency. Feature 128's zero-runtime-dep rule holds.
- **Precedent for future CLI prerequisites**: ADR-022 is the first ADR governing CLI-prerequisite posture in tachi. Future features introducing critical-path CLI dependencies should cite this ADR.

### Negative

- **Breaking change for adopters who relied on silent fallback**: Any adopter who was running `/tachi.security-report` on a shell without `mmdc` and accepting the raw-source PDF as a deliverable will now see a preflight abort. This is documented in PRD Risk 130.2 as a deliberate correctness improvement, not a regression. No downstream adopter was plausibly relying on the silent fallback because the output was unusable.
- **Increased prerequisite burden on first-run UX**: New users must install `mmdc` before running the pipeline on projects with attack trees. Mitigated by:
  - README Prerequisites section (Feature 130 T013) documenting the install commands for macOS/Linux/WSL
  - `scripts/install.sh` courtesy warning at install time (Feature 130 T014)
  - Canonical install command `npm install -g @mermaid-js/mermaid-cli` visible in every error message
- **Two preflight checks instead of one**: Small duplication (~5 lines total). Justified by defense-in-depth reasoning above; the simpler-alternative "extract a helper" is deferred to Future Work below.

### Neutral

- **CI workflow required**: A new `.github/workflows/tachi-mmdc-preflight.yml` workflow runs on `ubuntu-latest` (which does not have `mmdc` preinstalled) and asserts the loud-failure path. This adds one CI job to the repository but uses no custom Docker image.

---

## Future Work

**If a third CLI prerequisite is introduced to tachi** (i.e., a third tool beyond `typst` and `mmdc` gates a critical pipeline path), the current two-gate-per-tool inline pattern should be refactored into a reusable helper. Candidate shape:

```bash
# scripts/preflight.sh (hypothetical)
require_cli() {
  local tool="$1"
  local install_cmd="$2"
  local reason="$3"
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "$reason requires $tool." >&2
    echo "Install with: $install_cmd" >&2
    exit 1
  fi
}
```

The decision to extract is deliberately deferred until the abstraction has at least three consumers. Two inline checks is not enough to justify a helper; three is.

---

## References

- **Feature 130 PRD**: [docs/product/02_PRD/130-fix-attack-path-mermaid-rendering-2026-04-11.md](../../product/02_PRD/130-fix-attack-path-mermaid-rendering-2026-04-11.md)
- **Feature 130 spec**: [specs/130-prd-130-fix/spec.md](../../../specs/130-prd-130-fix/spec.md)
- **Feature 130 plan**: [specs/130-prd-130-fix/plan.md](../../../specs/130-prd-130-fix/plan.md)
- **Parent spec being corrected**: [specs/112-attack-path-pages/spec.md](../../../specs/112-attack-path-pages/spec.md) — SC-004 inverted; line 135 deleted; research.md line 80 corrected
- **Feature 054 precedent**: Typst hard prerequisite at `.claude/commands/tachi.security-report.md` Step 1
- **Related ADRs**: [ADR-014](ADR-014-gemini-api-optional-image-generation.md) (optional external APIs — different class), [ADR-021](ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) (baseline determinism — used by Feature 130 T020/T022)
- **Canonical install command**: `npm install -g @mermaid-js/mermaid-cli` (appears in 7 locations — verified by Feature 130 T023)
