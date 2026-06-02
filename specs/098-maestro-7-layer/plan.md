---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-01
    status: APPROVED
    notes: "Faithful, scope-disciplined realization of the PM-approved spec. 12/12 FRs served by Decisions A–E; US-1/US-2/US-3 all served; zero requirements dropped. Spec-review CONCERN-2 RESOLVED — Decision E pins 9 carries-a-MAESTRO-table files (re-verified file-for-file), EXCLUDES 2 table-less sample-reports, path-excludes test-output without hardcoding count. Annotation 'Analyzed — no findings this scan' PM-confirmed (coverage metadata, STRIDE-`---`-consistent, house em-dash OK). Deferrals (infographic, Model B) off the #98 close-gate; populator justified, not gold-plating. 2 non-blocking obs carried to tasks.md (OBS-1 expected agentic-app diff churn; OBS-2 assert phrase not trailing period). Details: .aod/results/product-manager.md"
  architect_signoff:
    agent: architect
    date: 2026-06-01
    status: APPROVED_WITH_CONCERNS
    notes: "Architecturally sound; all 12 source citations verified accurate. FR-003 minimal filter removal (no canonical seeding) preserves single-source-of-truth; Decision B examples-only populator correctly avoids a 2nd production authority; Decision A, determinism, no-new-ADR, backward-compat all verified correct. 3 concerns folded into plan Carry-Forward for tasks.md: CONCERN-1 (HIGH, tasks pin not plan defect) — 3 in-scope files use `###` while extractor substring-matches `####`, so populator + invariant test MUST be heading-level-agnostic and the 3 h3 headings normalized to `####`, else agentic-app PDF renders 0 layers + invariant false-greens; CONCERN-2 (LOW) drop snapshot count; CONCERN-3 (LOW) pin U+2014 + populator-not-production-path one-liner. Details: .aod/results/architect.md"
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: MAESTRO Coverage Matrix — Always Render All 7 Layers

**Branch**: `098-maestro-7-layer` | **Date**: 2026-06-01 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/098-maestro-7-layer/spec.md` · PRD `docs/product/02_PRD/098-maestro-7-layer-output-polish-2026-06-01.md` (Issue #98, BLP-04 Wave 4)

## Summary

Fix the MAESTRO coverage matrix at its root (the orchestrator LLM directive + the output-schemas spec) so the threats.md "Risk by MAESTRO Layer" table always authors all 7 canonical layers (L1–L7) in canonical order, with zero-finding rows annotated (Model A). Carry that through to the PDF by removing one downstream filter so the (now-present) zero-finding layers reach the already-existing-but-dead Typst empty-layer branch. Regenerate the 9 shipped example tables (via a small deterministic populator) and the 6 byte-deterministic PDF baselines, and add a regression test pinning the 7-row invariant. No SARIF/schema change — markdown + PDF rendering only.

## Technical Context

**Language/Version**: Python 3.11 (`scripts/`, `tests/`); Typst (PDF template); Markdown (LLM-authored threats.md + agent/skill spec docs)
**Primary Dependencies**: stdlib-only for the new populator (matches `populate-affected-assets.py` precedent); `typst` for PDF compile (existing toolchain); `pytest` for tests. No new runtime dependencies.
**Storage**: Files only — committed example outputs under `examples/`, PDF `.baseline` fixtures, markdown spec/agent docs.
**Testing**: `pytest` — `tests/scripts/test_extract_report_data.py` (filter-removal unit test), a new/extended 7-row invariant test, `tests/scripts/test_backward_compatibility.py` (6-baseline byte gate).
**Target Platform**: Developer/CI environment running the tachi harness inside Claude Code.
**Project Type**: single (instrumentation harness — no frontend/backend split).
**Performance Goals**: N/A (deterministic batch regeneration; no runtime hot path).
**Constraints**: ADR-021 determinism — all regeneration under `SOURCE_DATE_EPOCH=1700000000`; cross-format annotation wording byte-identical; no new hard-coded layer list (import `MAESTRO_LAYERS` from `scripts/tachi_parsers.py`).
**Scale/Scope**: 4 production-surface edits (1 LLM directive, 1 spec doc, 1 Python filter line, 1 Typst literal) + 1 new populator script + 1 new/extended test + regeneration of 9 markdown tables and 6 PDF baselines.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| III. Backward Compatibility (NON-NEGOTIABLE) | ✅ PASS | No SARIF/schema change (FR-010). Existing non-MAESTRO output unchanged. The 6 PDF baselines change by design (matrix grows + re-sorts) and are regenerated deterministically; the backward-compat test re-passes byte-for-byte. Expected churn, not a compatibility break. |
| VI. Testing Excellence | ✅ PASS | New regression test pins the 7-row invariant (FR-009); existing 6-baseline byte gate preserved. Test-first: write the invariant test against the target state before/with the renderer edits. |
| VII. Definition of Done | ✅ PASS | DoD checklist carried from PRD; `/aod.analyze` gate; CHANGELOG `feat(098)` entry. |
| VIII. Observability & RCA | ✅ PASS | Root cause established via 5 Whys at definition (D3: the orchestrator LLM directive, not the PDF filter). |
| IX. Git Workflow (NON-NEGOTIABLE) | ✅ PASS | Feature branch `098-maestro-7-layer`; draft PR #310; conventional commits; squash title `feat(098):`. |
| X. Product-Spec Alignment (NON-NEGOTIABLE) | ✅ PASS | PM sign-off on spec complete; this plan submitted for PM + Architect dual sign-off. |

**No violations. Complexity Tracking not required.** The one net-new artifact (the populator) is justified below (Decision B) and is a small, stdlib-only, single-purpose tool that follows an existing project precedent — it reduces, not adds, complexity relative to hand-editing 9 tables under a byte-determinism constraint.

## Resolved Plan-Stage Decisions

The PRD and spec deferred five items to plan/tasks. All five are resolved here.

### Decision A — Canonical Model A annotation string (resolves FR-004 wording)
**Decision**: The zero-finding annotation string is **`Analyzed — no findings this scan`**, placed in the table's existing **Highest Severity** column (no 4th column added). The PDF empty-layer branch renders the same string.
- **Markdown** zero-finding row: `| L4 — Deployment Infrastructure | 0 | Analyzed — no findings this scan |`
- **PDF** (`maestro-findings.typ:154`): replace the dead literal `[No findings mapped to this layer.]` with `[Analyzed — no findings this scan.]` (period in prose context; the heading already renders `(0 findings)`). The *annotation phrase* is byte-identical across both formats (FR-004); the trailing period is the only format-local difference and is pinned in tasks.md.
- **Rationale**: (a) affirms the layer *was analyzed* — directly kills the "silently dropped" reading (US-2); (b) parallels the STRIDE coverage-matrix `---` semantics ("analyzed, zero findings") in `coverage-matrix-model.md` without claiming the clean-vs-n/a distinction that Model A defers; (c) short enough for a table cell; (d) cannot be misread as a severity or finding. Final wording is PM-confirmed via this plan's sign-off.

### Decision B — Example completion mechanism: deterministic populator (resolves FR-007 mechanism)
**Decision**: Build a small **stdlib-only deterministic populator**, `scripts/populate-maestro-coverage.py`, modeled on `scripts/populate-affected-assets.py`. Role: an **examples-regeneration helper** (NOT a production-path component — production authoring remains the LLM directive, FR-001). It parses a threats.md "Risk by MAESTRO Layer" table, preserves each present layer's `(count, severity)`, emits **all 7 canonical layers in L1→L7 order** (importing `MAESTRO_LAYERS` from `tachi_parsers.py`), annotates zero-finding layers with the Decision-A string, and preserves a trailing conditional Unclassified row. Idempotent regex upsert; `--check` mode for CI/regression (exit-code drift signal).
- **Rationale**: 9 files must each be completed to 7 rows **and re-sorted** to canonical order under a byte-determinism constraint (6 of them gate PDF baselines). Hand-reordering 9 markdown tables byte-exactly is the single largest error source (Risk 98.1/98.3). A small deterministic transform eliminates that class of error, is re-runnable, and doubles as the FR-009 invariant gate via `--check`. This is the project's proven idiom (F-260b). The populator must emit the **same format** the FR-001 directive specifies, with `output-schemas.md` (FR-002) as the shared contract both honor.
- **Heading-level-agnostic discovery (Architect CONCERN-1, HIGH)**: the populator MUST locate the table by a heading-level-agnostic match (`^#{3,4}\s+Risk by MAESTRO Layer`), because 3 in-scope files use `### ` (h3) and 6 use `#### ` (h4) — see Decision E. It MUST also **normalize the 3 h3 headings to the canonical `#### `** during regeneration (the extractor substring-matches `#### Risk by MAESTRO Layer`, so an h3 heading currently parses to empty → 0 PDF layers).
- **Not a production-path component (Architect)**: unlike `populate-affected-assets.py` (which IS wired into the orchestrator/commands as a production value-authority), `populate-maestro-coverage.py` MUST NOT be wired into any command or orchestrator phase — it is a one-off examples-regeneration + `--check` tool only. Wiring it in would create the second production source-of-truth this design avoids. The precedent is borrowed for byte-stable transform *mechanics only* (stdlib, idempotent regex upsert, `--check`), not for its production role or its ~468-line size.
- **Fallback**: if the populator proves disproportionate during build, hand-edit is acceptable (per PRD FR-4) — but the invariant test (Decision below) gates either way, and the h3→h4 normalization + heading-agnostic test discovery still apply.

### Decision C — FR-006/FR-012 maestro-stack infographic: DEFER
**Decision**: Defer the optional `maestro-stack` infographic completeness to a tracked P1 follow-up issue; not implemented in this feature. The `maestro-heatmap` already renders empty cells (unaffected). Keeps the 1.0–1.5 day envelope; not a close-gate for Issue #98.

### Decision D — Model B (clean vs n/a): DEFER
**Decision**: Model B (the two-state clean-vs-n/a distinction) is recorded as a tracked P1 follow-up. It requires routing `component_layer_map` (computed today only in `extract-infographic-data.py`) into the matrix renderer — cross-pipeline work disproportionate to this polish. The eventual Model B should adopt the `coverage-matrix-model.md` three-state vocabulary (`---` / `n/a`). Not a close-gate for Issue #98.

### Decision E — test-output exclusion + complete enumeration (resolves Architect residual + PM CONCERN-2)
**Decision**: The in-scope set is defined by the **carries-a-MAESTRO-table** criterion, not directory presence. Nine files are in scope; two table-less sample-reports are excluded; `test-output/` snapshots are excluded by **path pattern** (not enumeration — their count is immaterial and MUST NOT be hardcoded anywhere).

**In-scope (9 files — pinned for tasks.md)**:
| File | Now | Action |
|------|-----|--------|
| `examples/agentic-app/threats.md` | 6/7 (missing L4) | complete + reorder; **PR diff target** |
| `examples/agentic-app/sample-report/threats.md` | 6/7 | complete + reorder |
| `examples/web-app/threats.md` | 4/7 | complete + reorder; **baseline-gated** |
| `examples/microservices/threats.md` | 2/7 | complete + reorder; **baseline-gated** |
| `examples/ascii-web-api/threats.md` | 4/7 | complete + reorder; **baseline-gated** |
| `examples/mermaid-agentic-app/threats.md` | 4/7 | complete + reorder; **baseline-gated** |
| `examples/free-text-microservice/threats.md` | 2/7 | complete + reorder; **baseline-gated** |
| `examples/mobile-banking-app/sample-report/threats.md` | 2/7 | complete + reorder (**Architect-named residual; not in PRD's list**) |
| `examples/maestro-reference/threats.md` | 7/7 | **re-order only** (canonical L1→L7); **baseline-gated** |

**Excluded — table-less sample-reports (MUST NOT force-fit a table)**: `examples/predictive-ml-app/sample-report/threats.md`, `examples/consumer-agent-app/sample-report/threats.md`.
**Excluded — frozen snapshots (path pattern `test-output/`)**: all `examples/agentic-app/test-output/*/threats.md`.

## Project Structure

### Documentation (this feature)
```
specs/098-maestro-7-layer/
├── plan.md              # This file
├── spec.md              # PM-approved feature spec
├── research.md          # Research findings (enumeration, line verification, lessons)
├── quickstart.md        # Regeneration + test runbook (Phase 1 output)
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # /aod.tasks output (next sub-step)
```
*data-model.md and contracts/ are **N/A** for this feature — see Phase 1.*

### Source Code (files touched)
```
.claude/agents/tachi/orchestrator.md                       # FR-001: line ~718 directive (omit→always-7 + canonical order)
.claude/skills/tachi-orchestration/references/
    └── output-schemas.md                                  # FR-002: lines ~237-238 (Ordering + Omission + annotation)
scripts/
    ├── extract-report-data.py                             # FR-003: line 407 filter removal
    ├── populate-maestro-coverage.py   (NEW)               # FR-007: deterministic example populator (+ --check)
    └── tachi_parsers.py                                   # READ-ONLY: import MAESTRO_LAYERS (no change)
templates/tachi/security-report/maestro-findings.typ       # FR-004: line 154 literal → canonical annotation
tests/scripts/
    ├── test_extract_report_data.py                        # FR-009: filter-removal unit assertions
    ├── test_maestro_coverage_invariant.py  (NEW)          # FR-009: 7-row invariant across in-scope examples
    └── test_backward_compatibility.py                     # UNCHANGED test; 6 baselines regenerated
examples/**/threats.md                                     # FR-007: 9 in-scope tables regenerated (see Decision E)
examples/*/security-report.pdf.baseline                    # FR-008: 6 gated baselines regenerated (SOURCE_DATE_EPOCH)
CHANGELOG.md                                               # feat(098) entry
```

**Structure Decision**: Single-project instrumentation harness. No new module boundaries; the change is concentrated in the existing render pipeline (LLM directive → markdown table → `extract-report-data.py` → Typst) plus one new sibling populator under `scripts/` following the `populate-affected-assets.py` precedent. No new system components are introduced (system-design auto-scaffold correctly skips).

## Technical Approach (the render pipeline change)

The MAESTRO coverage flows in one direction: **orchestrator LLM directive → threats.md markdown table → `parse_maestro_data` (`parsed_layers`) → `layer_groups` (seeded from `parsed_layers`) → `findings_by_layer` (filtered) → Typst `maestro-findings.typ`**. The fix touches three points on this line plus the regenerated artifacts:

1. **Root (FR-001/FR-002)** — change the *authoring* rule so the markdown always carries 7 canonical rows in L1→L7 order. `orchestrator.md:718`: replace *"Omit layers with zero findings. Order rows by highest severity descending…"* with *"Always emit all 7 canonical layers (L1–L7) in canonical L1→L7 order; zero-finding layers show count 0 and the annotation 'Analyzed — no findings this scan'. The Unclassified row remains conditional, after L7."* `output-schemas.md:237-238`: replace the Omission bullet with an "always include all 7 canonical layers" rule, set Ordering to canonical L1→L7, and specify the annotation string in the cell schema.

2. **Carry-through (FR-003)** — `extract-report-data.py:407`: change
   `findings_by_layer = [layer_groups[lid] for lid in sorted_layer_ids if layer_groups[lid]["findings"]]`
   to
   `findings_by_layer = [layer_groups[lid] for lid in sorted_layer_ids]`
   so every parsed layer (now all 7, thanks to FR-001) survives to the template. **No canonical seeding is added to the extractor** — `layer_groups` stays seeded from `parsed_layers` so the PDF can never show *more* layers than the markdown authored (preserves single-source-of-truth + cross-format parity; SC-003). The existing canonical `layer_sort_key` (lines 398-404) already orders L1→L7 then Unclassified — unchanged.

3. **Template (FR-004)** — `maestro-findings.typ:154`: the `else` branch is already correct structurally (fires when `count == 0`); change only its literal text to the canonical annotation. The `(0 findings)` heading (line 149) already renders the zero count grammatically — verify, no change.

4. **Regeneration (FR-007/FR-008)** — run `populate-maestro-coverage.py` over the 9 in-scope files, then regenerate the 6 gated PDF baselines under `SOURCE_DATE_EPOCH=1700000000`. Review the `agentic-app` diff (and spot-check others) to confirm only matrix rows/order changed (Risk 98.3).

5. **Regression (FR-009)** — (a) unit test on `extract-report-data.py`: a synthetic `parsed_layers` of all 7 canonical layers (some zero-finding) yields a `maestro_findings_by_layer` of length 7; a zero-finding group has empty `findings` (so the Typst else-branch fires). (b) Invariant test: for every `examples/**/threats.md` **excluding `test-output/`**, *if* the file contains a "Risk by MAESTRO Layer" table *then* all 7 canonical L-IDs are present — this both pins the invariant and naturally skips the 2 table-less sample-reports. **Table discovery MUST be heading-level-agnostic** (`^#{3,4}\s+Risk by MAESTRO Layer` or a bare substring on `Risk by MAESTRO Layer`) — anchoring on `#### ` would skip the 3 h3 files (incl. agentic-app) and false-green the test (Architect CONCERN-1). Optionally implemented as `populate-maestro-coverage.py --check`.

## Phase 0: Outline & Research

**Status: COMPLETE.** No `NEEDS CLARIFICATION` markers remain. `research.md` (already written) verified all four cited code locations against source, enumerated the 14-file reality (9 in-scope by the carries-a-table criterion + 2 table-less excluded + frozen snapshots path-excluded), confirmed the 6-baseline gate and `SOURCE_DATE_EPOCH=1700000000`, identified `populate-affected-assets.py` as the populator precedent and `coverage-matrix-model.md` as the three-state vocabulary precedent, and surfaced the F-302 init-baseline-tree transitive-drift caution. The PM independently re-verified every load-bearing claim during spec sign-off.

**Consolidated decisions** (Decision/Rationale/Alternatives):
- **Decision**: annotation = `Analyzed — no findings this scan` in the Highest Severity column. **Rationale**: affirms analysis, aligns with STRIDE `---` semantics, table-cell-sized. **Alternatives rejected**: PRD's longer "no detection-agent contributions…" (verbose for a cell); Typst's "No findings mapped to this layer" (ambiguous about whether analysis occurred); a new 4th "Notes" column (more invasive — changes every row).
- **Decision**: deterministic populator. **Rationale**: 9 files × (complete + reorder) under byte-determinism. **Alternatives rejected**: hand-edit (byte-determinism error risk across 9 tables, esp. reordering); re-running the LLM (non-deterministic, violates ADR-021); seeding canonical layers in the PDF extractor (creates a 2nd source of truth → markdown/PDF divergence risk).
- **Decision**: defer FR-6 infographic + Model B. **Rationale**: envelope + cross-pipeline cost; neither is a close-gate.

## Phase 1: Design & Contracts

**Prerequisites:** research.md complete ✅

- **`data-model.md`: N/A.** No new data entities or schema. The relevant "model" is the frozen canonical MAESTRO layer set, already the single source of truth in `.claude/skills/tachi-shared/references/maestro-layers-shared.md` and `scripts/tachi_parsers.py:MAESTRO_LAYERS` — reused by import, not redefined. The spec's Key Entities section documents the conceptual entities (Layer, Coverage Row, Annotation, Unclassified Row, PDF Baseline).
- **`contracts/`: N/A.** No API/endpoint surface. FR-010 forbids SARIF/schema change. The only "contract" is the markdown table format spec in `output-schemas.md` (Section "Risk by MAESTRO Layer"), updated in place by FR-002 — both the LLM directive and the populator honor it.
- **`quickstart.md`: GENERATE** — a short runbook: how to run the populator over the 9 files, regenerate the 6 PDF baselines under `SOURCE_DATE_EPOCH=1700000000`, run the three relevant test modules, and the F-302 init-baseline-tree drift remedy (`tests/fixtures/regenerate-baseline.sh`) if the merge surfaces unrelated doc-drift.
- **Agent context update**: not required — no new technology or cross-cutting convention is introduced (a single stdlib script + existing pipeline edits). Skipped intentionally.

**Post-design Constitution re-check**: ✅ still PASS — no new violations introduced by the design (no new dependency, no schema change, no new system component).

## Risks & Sequencing

| Risk | L/I | Mitigation |
|------|-----|------------|
| **98.1** Regeneration tail underestimated | M/M | Deterministic populator (Decision B) cuts 9× manual edits to one reviewed script; freeze annotation string + canonical order **before** editing (done here). |
| **98.3** Baseline regen accidental content drift | L/M | Regenerate under `SOURCE_DATE_EPOCH=1700000000`; review `agentic-app` diff + spot-check others to confirm only matrix rows/order changed; backward-compat test gates merge. |
| **98.4** Annotation misread as a finding | L/L | Decision-A wording is coverage metadata ("Analyzed — no findings"), PM-confirmed via this plan; never a severity. |
| **F-302 transitive init-tree drift** | L/M | If the merge surfaces `init-baseline-tree` failure on unrelated doc-drift, run `tests/fixtures/regenerate-baseline.sh` after verifying substitution semantics (INSTITUTIONAL_KNOWLEDGE Entry 9). One-line note carried to tasks.md. |
| **Cross-format wording divergence** | L/M | Single canonical string pinned in tasks.md; applied to orchestrator directive, output-schemas spec, populator, and Typst literal in one task group. |

**Sequencing (hard ordering)**: (1) Freeze annotation string + canonical order [done] → (2) FR-001/FR-002 directive+spec → (3) FR-003 filter + FR-004 Typst literal → (4) build populator (FR-007) → (5) FR-009 tests (write invariant against target state) → (6) regenerate 9 tables → (7) regenerate 6 PDF baselines → (8) run full test suite + `/aod.analyze` → (9) CHANGELOG + PR diff. Steps 2–5 are code; 6–7 are the regeneration tail; the populator (4) must exist before the table regeneration (6).

## Carry-Forward to tasks.md (from PM + Architect plan sign-off)

Both reviewers granted sign-off (PM APPROVED; Architect APPROVED_WITH_CONCERNS). The following must be pinned in tasks.md. Full detail: `.aod/results/architect.md`, `.aod/results/product-manager.md`.

- **[HIGH — Architect CONCERN-1] Heading-level heterogeneity.** 3 in-scope files use `### Risk by MAESTRO Layer` (h3): `agentic-app/threats.md` (the PR-diff target), `agentic-app/sample-report`, `mobile-banking-app/sample-report`. The other 6 (all baseline-gated) use `#### ` (h4). The extractor substring-matches `#### Risk by MAESTRO Layer`, so the 3 h3 tables parse to empty today → their PDFs render **0** MAESTRO layers. **tasks.md MUST**: (1) normalize the 3 h3 headings to `#### ` during regeneration (recommended — aligns with `output-schemas.md:229`); (2) make the populator's table discovery heading-level-agnostic; (3) make the invariant test discovery heading-level-agnostic (`^#{3,4}\s+Risk by MAESTRO Layer`). Without this, the agentic-app PDF MAESTRO page stays empty (US-1 AC-2 / SC-003 fail for the headline deliverable) and the invariant test false-greens.
- **[LOW — Architect CONCERN-3] Em-dash codepoint.** Pin the annotation em dash as **U+2014** in both the markdown cell and the Typst literal, matching `output-schemas.md` / `maestro-layers-shared.md` convention.
- **[LOW — Architect CONCERN-2] No hardcoded snapshot count.** Do not cite any `test-output/` count (the earlier "8"/"5" figures are immaterial) — exclude by path pattern only.
- **[Architect] Populator boundary one-liner.** State in tasks.md that `populate-maestro-coverage.py` MUST NOT be wired into any command/orchestrator phase (examples-regeneration + `--check` only) — unlike the production-path `populate-affected-assets.py` precedent.
- **[OBS-1 — PM] Expected agentic-app diff churn.** The named PR-diff target will show the added L4 row **+** the Unclassified row relocating to the bottom (from mid-table) **+** all non-empty rows re-sorting to canonical order (D2). Reviewer should expect row-relocation noise and confirm only rows/order changed (Risk 98.3 spot-check) — not mistake diff size for content drift.
- **[OBS-2 — PM] Cross-format parity test asserts the phrase.** The FR-004/SC-003 cross-format check must assert on the phrase `Analyzed — no findings this scan`, NOT require the trailing period to match (markdown cell has none; Typst prose has one — a sanctioned format-local difference).

## Out of Scope (carried from spec)
threat-report.md per-layer roster (no such view exists); SARIF/schema changes; `maestro-heatmap` infographic; new MAESTRO layers/taxonomy; re-scoring; frozen `test-output/` snapshots; MAESTRO *classification* evaluation order (this changes *render* order only).
