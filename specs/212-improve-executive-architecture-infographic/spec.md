---
prd_reference: docs/product/02_PRD/212-improve-executive-architecture-infographic-2026-04-24.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-24
    status: APPROVED
    notes: "All 3 prior PM concerns resolved (MODERATE-1 fallback named; LOW-1 palette 3-way reframed as EXTEND-with-additive; LOW-2 CISO persona flagged as inferred). All 3 PRD FRs map to enforceable acceptance scenarios. P1/P1/P2 vs P0/P0/P1 is scale difference, not downgrade. F-128 preservation pinned exhaustively (FR-212-20..23 + SC-212-7). SCs measurable via pytest/diff/cmp. No scope creep — three levels only. 0 blockers, 2 minor non-blocking observations. See .aod/results/pm-review-spec-212.md."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Improve Executive-Architecture Infographic

**Feature Branch**: `212-improve-executive-architecture-infographic`
**Created**: 2026-04-24
**Status**: Draft
**Input**: User description: "PRD: 212 - improve-executive-architecture-infographic"

## Overview

Transform the `executive-architecture` infographic template from a text-label inventory into an OpenClaw-style system flow diagram (rounded-rectangle nodes, directional arrows between layers, leader-lined callouts on specific nodes, dashed sub-group clusters). Delivered in three levels: (L1) Gemini prompt rewrite; (L2) callout-selection rework to 6–8 system-wide callouts with weighted-per-layer distribution; (L3) payload data-model expansion forwarding `flow_edges[]` and `clusters[]` from the shared scope parser into the template payload.

This spec addresses the concerns raised in the Triad PRD review by:
- Restating US-212-2's "superset or reorder" acceptance criterion as a mechanically enforceable per-layer floor rule (Architect HIGH-1)
- Aligning Level 3 payload field names to the actual `parse_scope_data` producers (Architect MEDIUM-2)
- Declaring deterministic sort order on both new arrays (Architect MEDIUM-3)
- Documenting reference-dataset verification + in-repo fallback (Team-Lead MODERATE-2 + PM MODERATE-1)
- Resolving the layer-palette question as EXTEND-with-additive (PM LOW-1 + Design Q1)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - OpenClaw-Style Rendering (Priority: P1)

As a **security consultant generating a tachi PDF security report**, when I regenerate the PDF on a realistic threat-model dataset (≥3 Critical/High findings across ≥2 layers), I see the executive-architecture page render as a proper system flow diagram — every component is a rounded-rectangle node with a colored border, directional arrows connect layers top-to-bottom, and ≥5 callouts appear with leader lines pointing to specific nodes — so I can deliver a report whose highest-visibility visual credibly diagnoses the client's system.

**Why this priority**: This is the user-visible quality win. The executive-architecture page sits at pages 2–3 of the PDF (locked by PRD #128); it is the first visual content the reader encounters. Shipping this without the other two levels still delivers ~70% of the value — the image looks like a diagnosis, not an inventory. Levels 2 and 3 amplify but do not gate this story.

**Independent Test**: Regenerate `threat-executive-architecture.jpg` on the reference dataset (`~/Projects/second-brain-mcp/docs/security/2026-04-23T23-02-25/`) with only the Level 1 prompt changes in place. Validate by human side-by-side comparison against `openclaw-agent-threat-model-infographic.jpg` on the four M1 structural criteria (nodes vs. text, arrows, leader-lined callouts, ≥5 callouts). If all four PASS, the story is delivered.

**Acceptance Scenarios**:

1. **Given** a threat model with ≥3 Critical/High findings distributed across ≥2 architectural layers, **When** the extractor and image-generation pipeline run end-to-end, **Then** every component in the rendered image appears as a rounded-rectangle node with a layer-coded fill and a colored border (no floating text-only labels).
2. **Given** the same threat model, **When** the image is rendered, **Then** directional arrows (solid line + explicit arrowhead) connect the primary data-flow path from the topmost (least-trusted) layer to the bottommost (most-trusted) layer.
3. **Given** the same threat model, **When** the image is rendered, **Then** at least 5 callouts appear with visible leader lines terminating on specific nodes (callouts are not floating inside a layer band with no visual anchor).
4. **Given** a layer that qualifies for the infographic (≥1 component defined) but contains zero Critical/High findings, **When** the image is rendered, **Then** that layer renders a compact factual badge (e.g., "0 High/Critical findings in this layer") occupying no more than 15% of the page height — not a full-band placeholder.
5. **Given** a threat model with zero Critical/High findings across the entire system, **When** the extractor runs, **Then** the template is skipped entirely (PRD #128 skip behavior preserved) and the PDF output is byte-identical to the pre-F-212 baseline.

---

### User Story 2 - Denser, System-Wide Callout Distribution (Priority: P1)

As a **security consultant delivering a PDF whose client has a lot of risk**, when the threat model contains 8+ qualifying Critical/High findings, I want the page to show 6–8 callouts distributed across layers with weighting, so the reader perceives the page as a comprehensive diagnosis rather than a one-per-layer sampler.

**Why this priority**: Without Level 2, a 9-High threat model renders only 2–3 callouts (one per layer) and wastes 60%+ of the page on empty-layer placeholders. Level 2 is the highest-leverage data-side change — one function, deterministic, no schema change. Ships behind Level 1 because visual form (L1) is more foundational than density (L2), but both are P1.

**Independent Test**: Run the extractor on the reference dataset with only the Level 2 callout-selection change in place. Verify `threat-executive-architecture-spec.md` `callouts[]` contains 6–8 entries with the weighted distribution described in the rules below, and that the set of finding IDs in the new output is a superset of the finding IDs the old per-layer-dedup logic would have emitted for the same input.

**Acceptance Scenarios**:

1. **Given** a threat model with 8 qualifying Critical/High findings distributed across 3 layers (e.g., 6 in one layer, 1 in another, 1 in a third), **When** callouts are selected, **Then** 6–8 callouts are emitted, each layer with ≥1 qualifying finding gets at least 1 callout, and no single layer exceeds 4 callouts.
2. **Given** a threat model with exactly 2 qualifying Critical/High findings, **When** callouts are selected, **Then** exactly 2 callouts are emitted (no synthetic inflation, no empty slots).
3. **Given** a threat model with zero qualifying Critical/High findings, **When** the extractor runs, **Then** the template skips image generation (PRD #128 skip behavior preserved) and no callouts are selected.
4. **Given** the same threat model input processed twice in separate runs, **When** callouts are selected, **Then** the `callouts[]` array is byte-identical across both runs (stable tie-break).
5. **Given** a threat model processed by the new Level 2 logic, **When** its output is compared to the output that the old per-layer-dedup logic would have produced on the same input, **Then** for every qualifying layer that contained ≥1 Critical/High finding under the old logic, that same layer appears in the new `callouts[]` with ≥1 entry (per-layer floor rule — enforceable as a pytest invariant on a fixture matrix).
6. **Given** a threat model where a single layer contains 6 qualifying findings and all other layers contain zero, **When** callouts are selected, **Then** that layer gets exactly 4 callouts (single-layer cap) and a compact "+ 2 more in this layer" annotation captures the remainder.

---

### User Story 3 - Structural Data in the Payload (Priority: P2)

As a **tachi maintainer inspecting the payload JSON**, I want to see `flow_edges[]` and `clusters[]` populated directly from the shared scope parser's `data_flows` and `trust_boundaries` sections, so I can trust that Gemini is drawing arrows and group boundaries from structured data rather than inferring them from component names — and so any future infographic change can reuse that structure without re-parsing.

**Why this priority**: Level 3 is the endgame. Levels 1 and 2 can ship without it and still deliver the user-visible quality win; L3 hardens the pipeline and unblocks future iteration. P2 because the Level 1 prompt already covers the rendered-image quality bar; L3 benefit is architectural (less Gemini inference, more determinism) and future-looking.

**Independent Test**: Add `flow_edges[]` and `clusters[]` to `_build_executive_architecture_payload()`. Run the extractor on the reference dataset and a fixture with empty `data_flows`/`trust_boundaries`. Verify: (a) on the populated dataset, both arrays are non-empty and field values match `parse_scope_data` output byte-for-byte; (b) on the empty fixture, both arrays are present and empty (not `null`, not missing); (c) both arrays are deterministically sorted across two consecutive runs.

**Acceptance Scenarios**:

1. **Given** a threat model whose `threats.md` contains a `### Data Flows` section populated by `parse_scope_data`, **When** the extractor runs, **Then** the executive-architecture payload includes a non-empty `flow_edges[]` array where each entry has `source` and `destination` string fields matching the component names produced by `parse_scope_data.data_flows[]` (the field name is `destination`, not `target` — aligned to producer).
2. **Given** the same threat model, **When** the extractor runs, **Then** the payload includes a non-empty `clusters[]` array where each entry has `name` (from `trust_boundaries[].zone`) and `members` (list of component names from `trust_boundaries[].components`), derived from `parse_scope_data.trust_boundaries[]`.
3. **Given** a threat model whose `threats.md` has no `### Data Flows` or `### Trust Boundaries` sections, **When** the extractor runs, **Then** both `flow_edges[]` and `clusters[]` are present in the payload as empty arrays (not `null`, not missing keys) — the Gemini prompt can then branch on array length.
4. **Given** a threat model processed twice on identical input, **When** `flow_edges[]` is serialized, **Then** entries are sorted by `(source.lower(), destination.lower())` ascending and the output is byte-identical between runs.
5. **Given** a threat model processed twice on identical input, **When** `clusters[]` is serialized, **Then** entries are sorted by `(trust_level_order, name.lower())` using the same `_TRUST_LEVEL_ORDER` mapping as `_compute_trust_zones`, `members` within each cluster are sorted case-insensitively, and the output is byte-identical between runs.
6. **Given** the updated Gemini prompt shipped in the same Level 3 change, **When** the prompt is rendered, **Then** it references `flow_edges` and `clusters` by name and no longer instructs Gemini to infer flow or clustering from component names alone.
7. **Given** a pathological threat model with more than 50 flow edges, **When** the extractor runs, **Then** `flow_edges[]` is truncated to the first 50 entries after the deterministic sort and a warning is logged (ordering policy: sort-then-truncate; richer prioritization deferred to follow-up PRD).

---

### Edge Cases

- **Single-layer architecture**: Only one layer has components. Level 1 prompt falls back to rendering the single layer with its nodes + callouts, omitting inter-layer arrows, and adds a "Single-zone architecture" caption in place of the top-to-bottom flow.
- **Ambiguous component names (pre-L3)**: When L1+L2 ship before L3, Gemini may mis-infer flow direction. Mitigation: L1 prompt instructs alphabetical node ordering within a layer when flow cannot be inferred. Eliminated by L3 (explicit `flow_edges[]`).
- **`data_flows` defined but references unknown components**: `parse_scope_data` output contains a flow edge whose `source` or `destination` does not match any component in the DFD. Extractor emits the edge anyway (best-effort — the Gemini prompt degrades gracefully by dropping the edge if no matching node renders) and logs a warning.
- **Very large threat model (50+ flow edges or 20+ trust boundaries)**: Truncate `flow_edges[]` to 50 entries after deterministic sort; emit warning. `clusters[]` is not truncated (trust boundaries per architecture rarely exceed 10). Richer truncation policy deferred.
- **One layer dominates with ≥5 qualifying findings and all other layers have 0**: Level 2 caps that layer at 4 callouts and emits a compact "+ N more in this layer" annotation; the page does not become a single-layer wall.
- **Reference dataset (sibling repo) unavailable**: The in-repo fixture at `tests/scripts/fixtures/exec_arch/agentic_app/threats.md` serves as the CI-validated source of truth. Sibling-repo validation (second-brain-mcp) is a local developer affordance, not a CI gate.
- **L3 lands before the Gemini prompt update**: Prompt still references layer-based inference; payload has `flow_edges[]`/`clusters[]` but Gemini ignores them. This is a no-op regression — L3 requires prompt update in the same landing (listed in Acceptance Scenario 6 above). Tasks.md enforces co-landing.

## Requirements *(mandatory)*

### Functional Requirements

#### Level 1 — Gemini Prompt Rewrite

- **FR-212-1**: The Gemini prompt for `executive-architecture` MUST instruct the model to render every component as a rounded-rectangle node with a layer-coded fill color and a colored border (not a bare text label).
- **FR-212-2**: The Gemini prompt MUST instruct the model to render directional arrows between layers, top-to-bottom, with explicit arrowheads (solid stroke + arrowhead glyph — bare lines not acceptable). The prompt MUST begin with the phrase "schematic diagram with shapes and arrows" (or equivalent directive) to defeat the text-only failure mode in current Gemini image-gen practice.
- **FR-212-3**: The Gemini prompt MUST instruct the model to render callouts as boxes anchored by thin leader lines to specific nodes — not as floating text inside a layer band.
- **FR-212-4**: The Gemini prompt MUST define per-layer border-accent colors drawn from the severity / layer palette published in `visual-design-system.md` (see Palette Strategy below). Severity colors (Critical `#DC2626`, High `#EA580C`) are inherited unchanged; layer-fill pastels are extended deterministically.
- **FR-212-5**: The Gemini prompt MUST instruct the model to render a qualifying layer that contains zero Critical/High findings as a compact factual badge ("0 High/Critical findings in this layer") sized to ≤15% of page height — not a full-band placeholder.
- **FR-212-6**: The updated prompt text MUST be locked VERBATIM in `.claude/skills/tachi-infographics/references/gemini-prompt-construction.md` and/or `.claude/skills/tachi-infographics/references/executive-architecture.md` (no runtime composition of aesthetic language).
- **FR-212-7**: The prompt rewrite MUST NOT alter the output file name, file format, portrait orientation, or skip behavior established by PRD #128. These are F-128 contracts.

#### Level 2 — Callout Selection Rework

- **FR-212-8**: The `_select_critical_high_callouts()` function MUST return 6–8 callouts drawn from the system-wide set of Critical/High findings, not one callout per layer.
- **FR-212-9**: Selection algorithm: Largest Remainder Method applied to qualifying-findings-per-layer, with the following floor and ceiling rules:
  - Total-cap: 8 callouts maximum.
  - Total-floor: when the system-wide qualifying count is < 6, emit all qualifying findings (no synthetic inflation).
  - Per-layer floor: for every layer with ≥1 qualifying finding, the layer MUST be represented by ≥1 callout when the total-cap permits — that is, whenever (number of qualifying layers) ≤ 8, every qualifying layer is represented. This is the mechanically-enforceable restatement of the PRD's "superset or reorder" criterion. (Architect HIGH-1 resolution.)
  - Per-layer ceiling: 4 callouts maximum per layer.
  - Overflow annotation: when a layer's qualifying count exceeds its allocated slot count, a `layer_overflow` field is emitted on the layer record with the text `"+ N more in this layer"` where N is the count of unshown qualifying findings.
- **FR-212-10**: Tie-break within a layer's allocation: severity descending (Critical before High) → composite score descending (where available) → finding ID ascending (lexicographic). Order of layers in the output: existing layer ordering from `_build_executive_architecture_payload` (no new layer-sort semantics introduced by Level 2).
- **FR-212-11**: The output of the new `_select_critical_high_callouts()` MUST satisfy the per-layer floor rule enforceable by pytest fixture matrix (absent / 1-qualifying-layer / 2-qualifying-layer / 3-qualifying-layer / all-layers-qualifying). Fixture matrix MUST be added to `tests/scripts/test_extract_infographic_data.py`.
- **FR-212-12**: The output of `_select_critical_high_callouts()` MUST be byte-identical across two consecutive runs on the same input (deterministic — ADR-017 invariant).

#### Level 3 — Payload Data-Model Expansion

- **FR-212-13**: `_build_executive_architecture_payload()` MUST return two new top-level keys: `flow_edges` (list of flow-edge records) and `clusters` (list of cluster records). Both keys MUST be present on every payload — empty arrays when source sections are absent from `threats.md`, never `null`, never missing. Additive-schema pattern per ADR-028.
- **FR-212-14**: `flow_edges[]` records MUST have the following fields (matching `parse_scope_data.data_flows[]` producer output — Architect MEDIUM-2 resolution):
  - `source` (string — component name, required)
  - `destination` (string — component name, required — field name is `destination`, NOT `target`, to match producer)
  - `data` (string — optional, may be empty; from producer)
  - `protocol` (string — optional, may be empty; from producer)
- **FR-212-15**: `clusters[]` records MUST be sourced from `parse_scope_data.trust_boundaries[]` (NOT from `boundary_crossings[]` — the PRD's original reference to `boundary_crossings` was imprecise; clusters represent zone membership, boundary crossings represent edges between zones). Fields:
  - `name` (string — from `trust_boundaries[].zone`)
  - `members` (list of strings — from `trust_boundaries[].components`)
  - `trust_level` (string — from `trust_boundaries[].trust-level`; one of `trusted` / `semi-trusted` / `untrusted`)
- **FR-212-16**: Sort order on `flow_edges[]`: ascending by `(source.lower(), destination.lower())`. Sort order on `clusters[]`: ascending by `(_TRUST_LEVEL_ORDER[trust_level] default 99, name.lower())` matching the `_compute_trust_zones` pattern at `scripts/extract-infographic-data.py:784`. `members` within a cluster: ascending case-insensitive. (Architect MEDIUM-3 resolution.)
- **FR-212-17**: When `flow_edges[]` produced by `parse_scope_data` exceeds 50 entries, the extractor MUST truncate to the first 50 after the deterministic sort and emit a warning log line. `clusters[]` is not truncated.
- **FR-212-18**: The Gemini prompt MUST be updated in the same Level 3 change to reference `flow_edges` and `clusters` by name (no orphaned payload fields). Co-landing enforced by tasks.md.
- **FR-212-19**: A new test file `tests/scripts/test_executive_architecture_payload.py` MUST validate the payload schema across an absent / empty / single / multi fixture matrix, mirroring the F-189 precedent. This addresses Architect LOW-4 (drift detection follow-up) partially — the test file is the drift guard.

#### Cross-Level Contracts (F-128 Preservation)

- **FR-212-20**: All F-128 output-artifact contracts MUST be preserved: output filenames (`threat-executive-architecture.jpg`, `threat-executive-architecture-spec.md`), PDF position (pages 2–3), skip behavior (zero Critical/High → no image, `has-executive-architecture=false`), Typst bindings (`has-executive-architecture`, `executive-architecture-image-path`), portrait orientation.
- **FR-212-21**: Changes MUST NOT touch any of the other 5 templates (`baseball-card`, `system-architecture`, `risk-funnel`, `maestro-stack`, `maestro-heatmap`).
- **FR-212-22**: PDF output on a zero-finding input MUST remain byte-identical to the pre-F-212 baseline when compared under `SOURCE_DATE_EPOCH=1700000000` (ADR-021 invariant).
- **FR-212-23**: Re-running the extractor on identical input MUST produce byte-identical payloads (ADR-017 invariant). This covers the new `flow_edges[]` and `clusters[]` fields and the reworked `callouts[]` field.

### Palette Strategy *(resolves PM L1 + Design Q1)*

**Decision: EXTEND-with-additive (not inherit-only, not fork).**

- **Severity colors** (inherited unchanged from `visual-design-system.md`): Critical `#DC2626`, High `#EA580C`, Medium `#CA8A04`, Low `#2563EB`, Informational `#6B7280`. Used for callout borders.
- **Layer-fill pastels** (extend with additive — cycled deterministically by layer index): `["#F0F4FF", "#FFF4F0", "#F0FFF4", "#FFF0F8", "#F8F0FF"]`. These fills are local to the `executive-architecture` template; they do not replace or modify any color in `visual-design-system.md`. Documented inline in `executive-architecture.md` skill reference.
- **Rationale**: Inherit-only cannot communicate layer identity visually; fork risks diverging from canonical tachi colors across templates. Extend-with-additive preserves canonical severity semantics while giving the executive-architecture page its own layer palette.

### Key Entities

- **Infographic Payload (executive-architecture)**: The JSON dictionary returned by `_build_executive_architecture_payload()` and written to `threat-executive-architecture-spec.md`. Entity is extended (not replaced) in Level 3.
  - Pre-F-212 keys: `metadata`, `layers`, `callouts`, `severity_distribution`.
  - F-212 additions: `flow_edges` (always present), `clusters` (always present).
  - Contract: consumers (Gemini prompt builder, PDF assembler) rely on key presence; empty arrays are valid.
- **Flow Edge**: A directed data-flow relationship between two components. Fields: `source`, `destination`, `data` (optional), `protocol` (optional). Sourced from `parse_scope_data.data_flows[]`. Field name `destination` matches producer (not `target`).
- **Cluster**: A trust-zone grouping of components. Fields: `name`, `members` (list of component names), `trust_level`. Sourced from `parse_scope_data.trust_boundaries[]`. Renders as a dashed boundary in the Gemini prompt directive.
- **Callout**: A threat annotation displayed on the infographic. Existing entity — fields unchanged by Level 2 (`layer_name`, `finding_id`, `severity`, `raw_description`, `composite_score`, `affected_component`). Level 2 changes *how many* callouts are selected and *how they are distributed*, not their field shape. Layer records gain an optional `layer_overflow` string field when applicable.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-212-1 — Structural Parity with OpenClaw Reference**: The regenerated `threat-executive-architecture.jpg` on the primary reference dataset (`~/Projects/second-brain-mcp/docs/security/2026-04-23T23-02-25/`) passes all four structural criteria by human side-by-side review: (1) components are rounded-rectangle nodes, not floating text; (2) directional arrows with explicit arrowheads connect layers; (3) callouts have leader lines to specific nodes; (4) ≥5 callouts visible. Baseline: currently 0/4. Target: 4/4.
- **SC-212-2 — Empty-Layer Waste Elimination**: Pixel-height measurement of empty-layer placeholder content on the regenerated reference image is ≤15% of page height. Baseline: ~30%. Target: ≤15%.
- **SC-212-3 — Callout Density on Reference Dataset**: Count of callouts in the regenerated `threat-executive-architecture-spec.md` `callouts[]` array for the 9-qualifying-finding reference dataset is 6, 7, or 8. Baseline: 2. Target: 6–8.
- **SC-212-4 — Per-Layer Floor Rule Invariant (Level 2)**: On a pytest fixture matrix (absent / 1-qualifying-layer / 2-qualifying-layer / 3-qualifying-layer / all-layers-qualifying), every qualifying layer appears in `callouts[]` with ≥1 entry whenever the total-cap (8) permits. Measurement: `pytest tests/scripts/test_extract_infographic_data.py -k per_layer_floor` passes on all matrix entries.
- **SC-212-5 — Payload Schema Compliance (Level 3)**: For every threat model in the fixture matrix that defines `data_flows` and `trust_boundaries` sections, the payload emits non-empty `flow_edges[]` and `clusters[]` arrays. For threat models without those sections, both keys are present as empty arrays. Measurement: `pytest tests/scripts/test_executive_architecture_payload.py` passes across absent / empty / single / multi fixtures.
- **SC-212-6 — Determinism Preservation**: Two consecutive runs of the extractor on identical input produce byte-identical payload JSON (including new `flow_edges[]` and `clusters[]` keys). Measurement: `diff` on payload JSON between runs returns zero differences. Covers ADR-017 invariant.
- **SC-212-7 — PDF Byte-Identity on Zero-Finding Input**: PDF rendered from a threat model with zero Critical/High findings is byte-identical to the pre-F-212 baseline PDF under `SOURCE_DATE_EPOCH=1700000000`. Measurement: `cmp` on both PDFs returns zero differences. Covers ADR-021 invariant and F-128 skip-behavior contract.
- **SC-212-8 — Extractor Runtime Regression Bound**: Extractor wall-clock time on the reference dataset increases by no more than 10% versus the pre-F-212 baseline. Measurement: mean of 5 timed runs compared against baseline mean.

## Assumptions

- The reference aesthetic (`openclaw-agent-threat-model-infographic.jpg`) is a stable visual target the Gemini 2.5 Flash Image / Gemini 3 Pro Image model family can approximate reliably via prompt engineering. If Level 1 cannot reach 3/4 of the SC-212-1 criteria after 2 prompt iterations, Risk R1 contingency triggers — re-prioritize L3 ahead of L1.
- The CISO secondary-persona pain point ("text-label inventory offers no architectural insight") is inferred from security-consultant feedback on delivered reports, not direct CISO interviews. Validating against a CISO is a post-delivery follow-up — not in scope here. (Addresses PM LOW-2.)
- The `openclaw-agent-threat-model-infographic.jpg` reference asset is a static visual target; tachi does not bundle or redistribute it. The comparison is performed by a human reviewer with local access to the reference file.
- `parse_scope_data` in `scripts/tachi_parsers.py` is a stable producer; its output shape is the source of truth for Level 3 field names. Verified 2026-04-24 in codebase research.

## Dependencies

### Internal

- **`scripts/extract-infographic-data.py`** — end-to-end functional since Issue #209 fix (merged in 4.21.1). No unblocking work needed.
- **`scripts/tachi_parsers.py` — `parse_scope_data()`** — stable; outputs `data_flows[]` with `source`/`destination` fields and `trust_boundaries[]` with `zone`/`trust-level`/`components` fields. Verified 2026-04-24.
- **`.claude/skills/tachi-infographics/`** — stable; receives edits to `executive-architecture.md` and `gemini-prompt-construction.md` only. Other template refs untouched.
- **Gemini API** — required for image regeneration during Phase 1 validation. Existing production credentials used via the `tachi-infographic` agent.

### External

- **Reference dataset — primary**: `~/Projects/second-brain-mcp/docs/security/2026-04-23T23-02-25/` (sibling local repo). Contains 9-qualifying-High findings + populated `data_flows` and `boundary_crossings`/`trust_boundaries` sections (verified 2026-04-24). **Not required for CI** — used for human side-by-side review only. (Addresses Team-Lead MODERATE-2.)
- **Reference dataset — fallback / CI**: `tests/scripts/fixtures/exec_arch/agentic_app/threats.md` (in-repo). All CI validation uses this fixture. If sibling repo unavailable, SC-212-1 validation is deferred to local reviewer with access.

## Out of Scope

- Changes to any infographic template other than `executive-architecture` (baseball-card, system-architecture, risk-funnel, maestro-stack, maestro-heatmap untouched).
- Changes to PDF positioning or the `has-executive-architecture` gate.
- Changes to Typst helpers or `report-data.typ` structure.
- Changes to the `parse_scope_data` function itself (consume existing output; do not modify).
- Changes to `threats.md` authoring conventions or format.
- A visual-regression test harness (tracked as follow-up PRD — Level 1+2 validated by human side-by-side review; Level 3 validated by pytest).
- Changes to the Gemini model version or API parameters.
- Support for alternative rendering backends (Mermaid, Graphviz, etc.).
- Changes to any of the 5 other infographic templates.
- Direct CISO-user validation of the rendered image (inferred persona; follow-up).

## Open Questions

- **Follow-up PRD — Visual-regression test harness**: Should we automate image comparison for SC-212-1? *Owner: team-lead — Due: after delivery.*
- **Follow-up PRD — Producer/consumer drift detection**: Level 3 introduces 2 new producer/consumer pairs (extractor → Gemini; extractor → Typst-via-payload). Should a schema-contract test module be generalized beyond the per-feature test file? *Owner: architect — Due: after delivery.* (Partial mitigation already in scope via `test_executive_architecture_payload.py`.)
- **Level-2 overflow annotation format**: PRD asked whether "+ N more" should include category attribution. Resolved to plain `"+ N more in this layer"` (no categorization — simpler to test, matches page-density budget). Re-open only if reviewer feedback requests.
- **`flow_edges[]` truncation policy refinement**: For systems with >50 data flows, current policy is sort-then-truncate-at-50. Richer prioritization (e.g., prefer cross-layer edges, prefer edges involving Critical/High-affected components) deferred to follow-up PRD. Open only if the reference dataset or near-term follow-ups exceed 50 edges.
