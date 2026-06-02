---
prd_reference: docs/product/02_PRD/098-maestro-7-layer-output-polish-2026-06-01.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-01
    status: APPROVED_WITH_CONCERNS
    notes: "Faithful, complete, scope-disciplined realization of PRD v1.1. All 6 PRD FRs → 12 spec FRs (decomposition, not creep); D1/D2/D3 carried verbatim and verified against source; Architect complete-enumeration residual elevated to FR-007; test-output excluded by robust path pattern; US-1/US-2/US-3 map 1:1 with close-gate set preserved; SC-001..006 measurable. 2 non-blocking concerns: C1 (priority-scale relabel) FOLDED IN; C2 (carry to tasks.md) — pin enumeration by carries-a-MAESTRO-table = 9 files; EXCLUDE 2 table-less sample-reports (predictive-ml-app, consumer-agent-app); test-output is 8 snapshots, path-excluded, do not hardcode count. Details: .aod/results/product-manager.md"
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: MAESTRO Coverage Matrix — Always Render All 7 Layers

**Feature Branch**: `098-maestro-7-layer`
**Created**: 2026-06-01
**Status**: Draft
**Input**: PRD 098 — `docs/product/02_PRD/098-maestro-7-layer-output-polish-2026-06-01.md` (Issue #98, BLP-04 Wave 4)

## User Scenarios & Testing *(mandatory)*

> **Priority scale**: User-story priorities use the spec-template scale, where **P1 = MVP / close-gate** and **P2 = should-have, not-MVP**. These correspond to the PRD's product-backlog labels (PRD P0 → spec P1, PRD P1 → spec P2). The close-gate set is unchanged: US-1 + US-2 close Issue #98; US-3 is the durability mechanism.

### User Story 1 - Architect Sees the Full Scan Span (Priority: P1)

A security architect evaluating tachi opens a completed threat-model report for an agentic system and reads the MAESTRO coverage views (the threats.md "Risk by MAESTRO Layer" table and the PDF "MAESTRO Layer Analysis" page). Today, layers with zero findings are silently omitted, so the matrix appears 2-of-7 or 6-of-7 and reads as a *coverage ceiling* — the reviewer cannot tell whether a layer was scanned-and-clean, not-applicable, or silently dropped, and assumes the worst. After this feature, every MAESTRO coverage view lists all 7 canonical layers (L1–L7) in a single canonical order, so the reviewer sees the complete scan span.

**Why this priority**: This is the core interpretability fix and the reason Issue #98 exists. The cost of the gap is paid precisely when BLP-04 distribution sends evaluators to inspect a report. P1 because it directly closes the issue and delivers a viable, demonstrable result on its own.

**Independent Test**: Run the pipeline against any example architecture and open both the threats.md table and the PDF page; confirm all 7 canonical layers appear as rows in canonical L1→L7 order, regardless of finding count. Fully demonstrable without US-2's annotation wording or US-3's regression test.

**Acceptance Scenarios**:

1. **Given** any completed pipeline run, **When** I open the threats.md "Risk by MAESTRO Layer" section, **Then** all 7 canonical layers (L1–L7) appear as rows in canonical L1→L7 order.
2. **Given** the same run, **When** I open the PDF "MAESTRO Layer Analysis" page, **Then** all 7 layers appear in the same canonical L1→L7 order, including zero-finding layers.
3. **Given** a run that produced unclassified findings, **When** I view either view, **Then** an "Unclassified" row also appears after L7 (unchanged behavior); **Given** no unclassified findings, **Then** no "Unclassified" row appears.
4. **Given** the threats.md table and the PDF page for the same run, **When** I compare them, **Then** they show the identical set of 7 layers in the identical order.

---

### User Story 2 - Self-Documenting Zero-Finding Rows (Priority: P1)

A reviewer encounters a layer with zero findings in the matrix. Rather than a blank cell or an absence that reads as a gap, the row explicitly states the layer was analyzed and produced no findings, so the reviewer reads it as "covered, clean."

**Why this priority**: Rendering all 7 rows (US-1) without an annotation would leave a zero-count row ambiguous — a reviewer could still misread it. The annotation is what eliminates the "silently dropped" failure mode and makes each layer's status explicit. P1 because US-1 and US-2 together are the close-gate for Issue #98 (Model A).

**Independent Test**: Inspect a regenerated example that has a zero-finding layer (e.g., agentic-app's L4); confirm the row shows a `0` count plus the explicit annotation, and that the threats.md and PDF wording are character-identical.

**Acceptance Scenarios**:

1. **Given** a layer with zero findings, **When** I read its row, **Then** the row shows a `0` count and an explicit annotation (Model A) rather than a blank cell or absence.
2. **Given** the annotation, **When** I compare the threats.md table and the PDF page, **Then** the wording is identical (cross-format consistency).
3. **Given** the annotation text, **When** a reviewer reads it, **Then** it is unambiguously coverage metadata and cannot be misread as a finding or a severity.
4. **Given** the same report already uses the STRIDE coverage matrix's `---`/`n/a` vocabulary elsewhere, **When** I read the MAESTRO annotation, **Then** it does not contradict that established analyzed-clean / not-applicable semantics.

---

### User Story 3 - Regression-Proofed Completeness (Priority: P2)

A maintainer makes a future change that touches the renderer or the example outputs. An automated test fails if any MAESTRO coverage view drops back below 7 canonical layers, so the completeness guarantee cannot silently regress.

**Why this priority**: Protects the US-1/US-2 guarantee over time. P2 because the user-facing value lands with US-1+US-2; the test is the durability mechanism. Still in-scope for this feature (DoD requires it), but the report is already correct before the test exists.

**Independent Test**: Introduce a renderer change that omits a canonical layer and confirm the new test fails identifying the missing layer(s); revert and confirm it passes. Separately, confirm the existing backward-compatibility test matches the 6 regenerated PDF baselines byte-for-byte under `SOURCE_DATE_EPOCH=1700000000`.

**Acceptance Scenarios**:

1. **Given** the test suite, **When** a renderer change omits a canonical layer from the PDF data model, **Then** a test fails identifying the missing layer(s).
2. **Given** a parsed markdown table containing all 7 canonical rows, **When** the PDF data extraction runs, **Then** all 7 layers (including zero-finding) are retained — i.e., the downstream filter no longer drops them.
3. **Given** the regenerated examples, **When** the backward-compatibility test runs, **Then** the 6 gated PDF baselines match byte-for-byte under `SOURCE_DATE_EPOCH=1700000000`.
4. **Given** the regression test scans example outputs, **When** it runs, **Then** it evaluates shipped examples and their `sample-report/` variants but excludes frozen `test-output/` snapshots.

---

### Edge Cases

- **All 7 layers have findings** (e.g., `maestro-reference`): no empty rows render, but the table/page must still appear in canonical L1→L7 order — the row *order* may change even when no rows are *added* (D2).
- **Unclassified findings present**: the conditional "Unclassified" row appears after L7 in both views; its presence/absence is governed solely by whether unclassified findings exist (unchanged from today).
- **A layer with zero findings AND an unclassified row**: both the zero-finding annotated rows and the Unclassified row coexist; the 7 canonical layers are not collapsed into Unclassified.
- **A sample-report MAESTRO table not in the PRD's named list** (e.g., `mobile-banking-app/sample-report`): it is in scope and must be completed to 7 rows.
- **Frozen `test-output/` snapshots**: timestamped historical artifacts that also contain MAESTRO tables are intentionally left unchanged; the regression test must not assert the invariant against them.
- **Per-layer count heading reads `(0 findings)`**: the PDF per-layer heading must render the zero count grammatically (already supported) and the empty-layer fallback text must become live.

## Requirements *(mandatory)*

### Functional Requirements

> Acceptance criteria for these requirements are expressed in the User Story scenarios above (Given/When/Then). This feature changes markdown + PDF rendering only — no SARIF / schema change.

- **FR-001 (Root cause — threats.md authoring)**: The threats.md "Risk by MAESTRO Layer" table MUST always render all 7 canonical layers (L1–L7), regardless of finding count. The authoring directive MUST be changed from "omit layers with zero findings" to "always emit all 7 canonical layers," and the row ordering MUST change from severity-descending to **canonical L1→L7**. This is the single source of truth from which the PDF derives.
- **FR-002 (Spec parity)**: The output-schema specification governing the "Risk by MAESTRO Layer" table MUST be updated to match FR-001 — the omission rule replaced by an "always include all 7 canonical layers" rule, the ordering rule set to canonical L1→L7, and the zero-finding annotation text specified.
- **FR-003 (PDF carry-through)**: The PDF "MAESTRO Layer Analysis" page MUST always render all 7 canonical layers. The downstream filter that drops zero-finding layers MUST be removed/inverted so the (now-present) zero-finding layers reach the existing empty-layer template branch. This requirement is strictly **downstream of FR-001**: the PDF data model is seeded from the parsed markdown table, so it can only show layers FR-001 has already authored.
- **FR-004 (Zero-finding annotation — Model A)**: Every zero-finding layer row MUST show a `0` count plus an explicit annotation indicating the layer was analyzed and produced no findings (Model A — a single annotation, not the clean-vs-n/a distinction). The annotation wording MUST be identical across the threats.md table and the PDF page, MUST be phrased as coverage metadata (never a severity or finding), and MUST NOT contradict the existing STRIDE-matrix `---`/`n/a` vocabulary used elsewhere in the report.
- **FR-005 (Conditional Unclassified — unchanged)**: An "Unclassified" row MUST continue to appear only when unclassified findings exist, positioned after L7 in both views. The 7 canonical layers MUST NOT be folded into or replaced by the Unclassified row.
- **FR-006 (Canonical-order parity across pipelines)**: Both views MUST present the layers in one shared canonical order (L1→L7, then conditional Unclassified). The canonical layer identifiers and names MUST be sourced from the single shared reference; no new hard-coded layer list may be introduced.
- **FR-007 (Example regeneration — complete enumeration)**: Every shipped output that carries a MAESTRO coverage table MUST be regenerated to all 7 canonical rows in canonical order with Model A annotations on zero-finding rows. The complete in-scope set MUST be pinned at task time and MUST include the sample-report variants beyond the PRD's originally-named list (e.g., `mobile-banking-app/sample-report`). Frozen `test-output/` snapshots are out of scope. The `examples/agentic-app/` diff MUST be shown in the PR description.
- **FR-008 (Deterministic regeneration)**: All regeneration MUST occur under `SOURCE_DATE_EPOCH=1700000000` (ADR-021). The 6 gated PDF baselines MUST be regenerated and the backward-compatibility test MUST pass byte-for-byte afterward.
- **FR-009 (Regression test — 7-row invariant)**: A test MUST assert that, given a parsed markdown table with all 7 canonical rows, the PDF data extraction retains all 7 (including zero-finding) layers; and that the empty-layer annotation renders for a zero-finding layer. The test MUST evaluate shipped examples and `sample-report/` variants while excluding `test-output/` snapshots.
- **FR-010 (No SARIF / schema change)**: This feature MUST NOT alter SARIF output or any schema. Layer counts are already structured; the change is markdown + PDF rendering only. `/aod.analyze` MUST pass with no inconsistencies.
- **FR-011 (P1 follow-up — Model B, deferred)**: The clean-vs-n/a two-state distinction (Model B) MUST be recorded as a tracked P1 follow-up, NOT delivered in this feature. It requires routing component→layer mapping (computed today only in a different pipeline) into the matrix renderer — cross-pipeline work disproportionate to this polish. It is not a close-gate for Issue #98.
- **FR-012 (P1 optional — maestro-stack infographic)**: Extending the `maestro-stack` infographic to show zero-finding layers explicitly MAY be included if it fits the envelope; otherwise it MUST be recorded as a follow-up. It is not a close-gate for Issue #98. (The `maestro-heatmap` infographic already renders empty cells and is unaffected.)

### Key Entities

- **MAESTRO Layer**: One of the 7 canonical CSA MAESTRO layers (L1 Foundation Model, L2 Data Operations, L3 Agent Framework, L4 Deployment Infrastructure, L5 Evaluation and Observability, L6 Security and Compliance, L7 Agent Ecosystem). Frozen by Feature 136; sourced from the single shared reference. Has an ID, a name, a finding count (≥ 0), and a highest-severity (or none).
- **Coverage Matrix Row**: A rendered row representing one layer's status in a coverage view — finding count, highest severity, and (when count = 0) the Model A annotation. Exists in both the threats.md table and the PDF page; the two must agree.
- **Zero-Finding Annotation (Model A)**: Coverage metadata attached to a count-0 row stating the layer was analyzed with no findings. Cross-format identical; never a severity.
- **Unclassified Row**: A conditional row for findings that mapped to no canonical layer. Present only when such findings exist; positioned after L7.
- **PDF Baseline**: A byte-deterministic reference PDF (one of 6 gated examples) regenerated under a fixed epoch and compared byte-for-byte by the backward-compatibility test.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of pipeline runs render exactly 7 canonical MAESTRO layers (plus a conditional Unclassified row) in every coverage view — verified by the FR-009 regression test and inspection of regenerated examples.
- **SC-002**: 0 instances of a silently-omitted canonical layer across all shipped examples and their `sample-report/` variants — verified by inspection of regenerated outputs.
- **SC-003**: The threats.md table and PDF page for any given run show the identical 7 layers, in the identical canonical order, with identical zero-finding annotation wording — verified by cross-format comparison.
- **SC-004**: 6/6 gated PDF baselines are byte-identical after regeneration under `SOURCE_DATE_EPOCH=1700000000`; the backward-compatibility test passes.
- **SC-005**: No SARIF / schema change is introduced (verified by diff); `/aod.analyze` passes with no inconsistencies.
- **SC-006**: A reviewer can, from the report alone and with no human clarification, distinguish "analyzed but clean" from "silently dropped" for every layer — eliminating the recurring "we scanned that too, it was just clean" clarification loop (the full clean-vs-n/a distinction is deferred to Model B/P1).

## Assumptions

- The canonical 7-layer MAESTRO taxonomy is stable (Feature 136 merged); no taxonomy/enum changes are in scope.
- The PDF data extractor seeds its layer model from the parsed markdown table, making FR-003 strictly downstream of FR-001 (confirmed in research at `extract-report-data.py:363-407`).
- The PDF template's empty-layer fallback is present and correct, currently unreachable dead code (confirmed at `maestro-findings.typ:151-155`); activating it requires no template logic change beyond reconciling its literal wording with the FR-004 annotation.
- Frozen `test-output/` snapshots are historical artifacts, not user-facing shipped examples, and are out of scope; the regression test excludes them.
- The mechanism for completing the example markdown tables (hand-edit vs. a small deterministic populator modeled on `populate-affected-assets.py`) is a plan-stage decision; either is acceptable, with the populator preferred if it reduces per-example manual edits and guards determinism.

## Dependencies

- **Internal (all DELIVERED)**: Feature 084 (MAESTRO layer mapping + the table this completes), 091 (PDF MAESTRO page + `maestro-findings.typ` template), 136 (frozen canonical layer names/IDs), 141 (confirmed this gap is real and not subsumed by cross-layer chains).
- **Architecture in force**: ADR-020 (MAESTRO classification — no new ADR), ADR-021 (determinism — `SOURCE_DATE_EPOCH=1700000000`).
- **Shared reference**: `.claude/skills/tachi-shared/references/maestro-layers-shared.md` / `scripts/tachi_parsers.py:MAESTRO_LAYERS` (canonical layer source).
- **External tooling**: `typst` for PDF regeneration (existing toolchain); `mmdc` only if the optional FR-012 infographic is pursued.

## Scope & Boundaries

### In Scope (P0)
- threats.md "Risk by MAESTRO Layer" always renders L1–L7 in canonical order (FR-001, root cause).
- output-schema spec updated to match — rule + ordering + annotation (FR-002).
- PDF "MAESTRO Layer Analysis" page always renders L1–L7 (FR-003, carry-through).
- Zero-finding row annotation, Model A, cross-format identical (FR-004).
- Conditional Unclassified row behavior preserved (FR-005); canonical-order parity (FR-006).
- All shipped MAESTRO tables regenerated to 7 rows, complete enumeration pinned (FR-007), including sample-report variants beyond the PRD's named list.
- Deterministic regeneration; 6 PDF baselines regenerated; backward-compat test passes (FR-008).
- 7-row invariant regression test (FR-009).
- No SARIF / schema change; `/aod.analyze` clean (FR-010).
- CHANGELOG `feat(098)` entry.

### Should Have / Optional (P1)
- Model B two-state annotation (clean vs n/a) as a tracked follow-up (FR-011).
- `maestro-stack` infographic completeness (FR-012), only if it fits the envelope.

### Out of Scope
- **threat-report.md per-layer roster** — no such roster exists today (only per-finding references and Feature-141 cross-layer attack-chain narratives); adding one would be net-new structure, not a polish. (Architect-confirmed exclusion.)
- **SARIF / schema changes** — layer counts already structured.
- **`maestro-heatmap` infographic** — already renders empty cells.
- **New MAESTRO layers or taxonomy changes** — the canonical 7 are frozen (Feature 136).
- **Re-scoring / risk-model changes** — zero-finding rows do not affect CVSS or composite scores.
- **Frozen `test-output/` snapshots** — historical artifacts, intentionally unchanged.
- **MAESTRO *classification* evaluation order** — unchanged; this feature changes *render* order only (the two are distinct orderings).
