---
prd:
  number: 212
  topic: improve-executive-architecture-infographic
  created: 2026-04-24
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-04-24, status: APPROVED_WITH_CONCERNS, notes: "3 concerns (1M, 2L): L3 reference dataset data_flows presence not verified — need fallback dataset named if second-brain-mcp/2026-04-23 threats.md lacks data_flows/boundary_crossings sections; palette question should be reframed as 3-way not binary (inherit / extend visual-design-system.md / template-local fork); CISO persona pain point is inferred from consultant feedback, not direct CISO validation. All resolvable in spec."}
  architect_signoff: {agent: architect, date: 2026-04-24, status: APPROVED_WITH_CONCERNS, notes: "4 concerns (1H, 2M, 1L): HIGH — 'superset or reorder' AC is not mechanically enforceable, needs precise per-layer invariant with floor rule (every qualifying layer gets ≥1 callout when allocation permits); MEDIUM — L3 schema field names don't match existing producers (_compute_data_flows emits 'destination' not 'target', _compute_boundary_crossings has no 'members' field, emits 'crossing_point'); MEDIUM — clusters[] member ordering determinism gap, spec must declare alphabetical-case-insensitive sort matching _compute_trust_zones pattern; LOW — Level 3 introduces two new producer/consumer pairs without drift detection, track as follow-up. All resolvable in spec/plan."}
  techlead_signoff: {agent: team-lead, date: 2026-04-24, status: APPROVED_WITH_CONCERNS, notes: "4 concerns (2M, 2L): MODERATE — Phase 1 2h estimate is optimistic for Gemini visual iteration (widen to 3-5h, document 3-iteration budget); MODERATE — reference dataset lives in sibling repo (~/Projects/second-brain-mcp/docs/security/2026-04-23T23-02-25/), needs explicit Dependencies disclosure plus fallback path; LOW — 'maintainer' owner in milestone table unnamed, replace with specific agent assignments per phase; LOW — Phase 2 'at least one other tachi dataset' regression target ambiguous, either name second dataset or convert to programmatic ID-superset check. M1/M2/L1 resolvable in spec; L2 in tasks. 1-week envelope realistic with ~40% buffer if R1/R3 don't fire."}
source:
  idea_id: 212
  story_id: null
---

# Improve Executive-Architecture Infographic — Product Requirements Document

**Status**: Approved
**Created**: 2026-04-24
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1 (High)

---

## Executive Summary

### The One-Liner
Transform the executive-architecture infographic from a bulleted text inventory into an OpenClaw-style system flow diagram — nodes, directional arrows, sub-group clusters, and 6+ threat callouts distributed across layers — so the most-prominent visual in the PDF security report reads as a credible architecture diagnosis.

### Problem Statement
The current `threat-executive-architecture.jpg` renders components as floating text labels inside three horizontal pastel bands (External / Application / Supabase). For the 9-High-finding `second-brain-mcp/docs/security/2026-04-23T23-02-25/` system it renders only 2 callouts, leaving the bottom 30% of the page showing "No high-severity residual findings in this layer" — wasted space that undercuts the perceived value of the entire security-report booklet. Executives glancing at the page cannot tell how data flows, how components relate, or where threats cluster. This is the most-prominent visual in the PDF (pages 2–3, established by PRD #128), and it sets reader expectations for the rest of the document.

### Proposed Solution
Rewrite the executive-architecture template so Gemini renders the page as a proper system flow diagram matching the `openclaw-agent-threat-model-infographic.jpg` reference aesthetic. Three implementation levels bundled in this PRD:
- **Level 1** — Gemini prompt rewrite (nodes, arrows, leader-lined callouts, layer colors, empty-layer badges)
- **Level 2** — Callout selection rework (6–8 callouts across the system, not per-layer dedup)
- **Level 3** — Data-model expansion (forward `flow_edges[]` and `clusters[]` from `parse_scope_data` into the executive-architecture payload)

Levels 1+2 ship first as an immediate quality win (~70% of target aesthetic); Level 3 lands after as the endgame that eliminates Gemini inference for flow and clustering.

### Success Criteria
- Regenerated `threat-executive-architecture.jpg` for `second-brain-mcp/docs/security/2026-04-23T23-02-25/` passes a side-by-side comparison with `openclaw-agent-threat-model-infographic.jpg` on four structural criteria: components are rounded-rectangle nodes, directional arrows connect layers, callouts are on specific nodes with leader lines, ≥5 callouts visible
- No empty-layer "No high-severity residual findings" placeholder consuming 30%+ of page height
- After Level 3: payload JSON includes populated `flow_edges[]` and `clusters[]` fields derived from `parse_scope_data`
- Backward compatibility: systems with zero Critical/High findings continue to skip the template as today (PRD #128 skip behavior preserved)

### Timeline
Target delivery: **1 week total across three levels** — Level 1 + Level 2 within 3 days (immediate quality win), Level 3 within 4 more days (architectural endgame).

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [docs/product/01_Product_Vision/product-vision.md](../01_Product_Vision/product-vision.md)

Tachi's mission is making threat modeling accessible to teams without deep security expertise. The executive-architecture page is the first visual artifact a non-technical executive encounters in the PDF report. If that page fails to communicate *where the system breaks*, tachi fails its vision at the point of highest reader attention. This PRD directly serves the mission by ensuring the highest-visibility visual earns its placement.

### Roadmap Fit
This is a direct quality follow-up to **PRD #128** (Executive Threat Architecture Infographic, delivered 2026-04-09). #128 established the template and its page-2–3 position; #212 makes the rendered image live up to that placement. It is the fourth iteration in the infographic quality arc: F-128 established position → F-136/F-145 corrected MAESTRO layer accuracy → **F-212 upgrades the executive-architecture visual from inventory to diagnosis.**

### Lineage
- **Predecessor**: PRD #128 (executive-threat-architecture template — delivered)
- **Trigger**: Issue #209 fix (producer/consumer contract drift) — once the pipeline ran end-to-end again, executive-architecture quality emerged as the next user-facing gap on the `second-brain-mcp` reporter output
- **Reference aesthetic**: `openclaw-agent-threat-model-infographic.jpg` (external system flow diagram the reporter compared tachi's output against)

---

## Target Users & Personas

### Primary Persona: Security Consultant / Template Adopter
- **Role**: Generates security-report PDFs from tachi threat model output, delivers to client executives
- **Experience**: Uses tachi as a reporting toolchain, understands threat modeling, does not author the templates themselves
- **Goal**: Produce a PDF whose first visual page credibly diagnoses the client's system architecture and threat exposure
- **Pain Point**: The current executive-architecture page reads as a bulleted inventory — it forces the consultant to apologize or manually annotate the page before delivery

### Secondary Persona: CISO / Security Executive (report consumer)
- **Role**: Receives security assessment PDFs, makes remediation budget decisions
- **Experience**: Business-oriented, limited reading time, low tolerance for dense technical content
- **Goal**: Quickly identify which architectural layer carries the most risk and how components relate
- **Pain Point**: A text-label inventory with 2 callouts on a page-sized band offers no architectural insight; the page looks unfinished

### Tertiary Persona: Tachi Maintainer / Contributor
- **Role**: Owns `.claude/skills/tachi-infographics/` and `scripts/extract-infographic-data.py`
- **Experience**: Contributes to tachi core
- **Goal**: Preserve deterministic output and pipeline contract while improving template quality
- **Pain Point**: Changes that improve visual quality risk breaking contract with downstream consumers (`report-data.typ`, PDF assembly)

---

## User Stories

### US-212-1: OpenClaw-Style Rendering
**When** I regenerate a PDF security report on a realistic threat-model dataset,
**I want to** see the executive-architecture page render as a proper system flow diagram — nodes with colored borders, directional arrows between layers, dashed sub-group clusters, and ≥5 threat callouts with leader lines,
**So I can** deliver a report whose highest-visibility visual matches the production aesthetic of reference tools like OpenClaw's agent threat-model infographic.

**Acceptance Criteria**:
- **Given** a threat model with ≥3 Critical/High findings across ≥2 layers, **when** the infographic is generated, **then** every component is a rounded-rectangle node with layer-coded fill and colored border (not floating text)
- **Given** the same input, **when** the image is rendered, **then** directional arrows connect the primary data-flow path from topmost (untrusted) layer to bottommost (trusted) layer
- **Given** the same input, **when** the image is rendered, **then** ≥5 callouts appear with leader lines pointing to specific nodes (not floating inside the band)
- **Given** a layer with zero Critical/High findings, **when** the image is rendered, **then** the layer renders a compact factual badge (e.g., "0 High/Critical findings") sized to ≤15% of page height rather than a full-band placeholder

**Priority**: P0
**Effort**: M (Level 1 scope — ~2h prompt rewrite)

### US-212-2: Denser, System-Wide Callout Distribution
**When** the threat model contains 8+ qualifying Critical/High findings,
**I want to** see 6–8 callouts distributed roughly evenly across layers rather than a single callout per layer,
**So I can** read the page as a comprehensive diagnosis where each visible callout represents a distinct risk rather than one synthetic "representative" risk per band.

**Acceptance Criteria**:
- **Given** a threat model with 8 qualifying Critical/High findings, **when** callouts are selected, **then** 6–8 callouts are emitted with the distribution weighted by findings-per-layer
- **Given** a threat model with 2 qualifying findings total, **when** callouts are selected, **then** 2 callouts are emitted (no synthetic inflation, no empty slots)
- **Given** the same threat model input run twice, **when** callouts are selected, **then** the output is identical (determinism preserved via stable tie-break)
- **Given** callouts emitted by the new selection logic, **when** compared to the F-128 per-layer-dedup output on an identical threat model, **then** the new output is a superset or reorder — no qualifying finding previously shown is dropped

**Priority**: P0
**Effort**: S (Level 2 scope — ~4h extractor change)

### US-212-3: Structural Data in the Payload (Endgame)
**When** I inspect the JSON payload emitted by `scripts/extract-infographic-data.py` for the executive-architecture template,
**I want to** see explicit `flow_edges[]` and `clusters[]` fields populated from `parse_scope_data`,
**So I can** trust that Gemini is drawing arrows and groups from structured data rather than inferring them from component names.

**Acceptance Criteria**:
- **Given** a threat model with defined `data_flows` and `boundary_crossings` sections in `threats.md`, **when** the extractor runs, **then** the executive-architecture payload includes a non-empty `flow_edges[]` array with `source` and `target` fields matching `parse_scope_data` output
- **Given** the same input, **then** the payload includes a non-empty `clusters[]` array with grouping membership derived from `boundary_crossings` (or a documented fallback when absent)
- **Given** a threat model with no `data_flows` / `boundary_crossings` sections, **when** the extractor runs, **then** `flow_edges[]` and `clusters[]` are present but empty — no extractor failure
- **Given** the updated payload schema, **when** the Gemini prompt is run, **then** the prompt references `flow_edges` and `clusters` by name and no longer asks Gemini to infer flow from component names

**Priority**: P1
**Effort**: L (Level 3 scope — ~1–2 days data-model expansion)

---

## User Experience Requirements

### Journey Context
The executive-architecture page sits at **pages 2–3** of the PDF security report (position established by PRD #128). It is the first visual content the reader encounters after the Executive Summary. Four journey touchpoints matter:
1. The reader opens the PDF — the executive-architecture page is the first thing that looks "like a diagram"
2. The reader has ~30 seconds of attention on this page before scrolling
3. The reader forms a mental model of *what this system is and where it breaks*
4. The reader either reads deeper (win) or skims to the end (loss) — this page is the tipping point

### Visual Directives (for Gemini Prompt)
From Issue #212 Level 1 scope, the prompt MUST instruct Gemini to:
- Render every component as a rounded-rectangle **node** with colored fill + border (not bare text)
- Draw **directional arrows** between layers showing primary data flow (top = untrusted, bottom = trusted)
- Place **callouts on specific nodes** with leader lines (not floating in the band)
- Use **layer-specific accent colors** for node borders
- Fill empty layers with a **compact factual badge** (e.g., "0 High/Critical findings in this layer") instead of wasting a full band

### Reference Aesthetic
The target is `openclaw-agent-threat-model-infographic.jpg` — nodes, arrows top-to-bottom, dashed sub-group clusters, ~6 callouts distributed across every layer, layer-specific color palette (blue UI, orange gateway, green LLM, gray tools, purple scheduler, yellow control plane, coral advisories).

### Out-of-Scope UX Changes
- The page stays **portrait** orientation (matches PRD #128)
- The page stays at **pages 2–3** (no repositioning)
- The template alias (`exec` / `executive-architecture`) stays as-is
- The page heading and caption stay as-is
- The `has-executive-architecture` gate stays as-is

---

## Functional Requirements

### FR-212-1: Gemini Prompt Rewrite (Level 1)
**Description**: Update `.claude/skills/tachi-infographics/references/gemini-prompt-construction.md` and `.claude/skills/tachi-infographics/references/executive-architecture.md` to encode the visual directives listed above.

**Inputs**: Current prompt construction templates; the visual-directive list from Issue #212.
**Processing**: Rewrite the prompt template, preserving the portrait orientation, skip-behavior, and output-artifact contracts.
**Outputs**: Updated skill reference files. Regenerated `threat-executive-architecture.jpg` on the `second-brain-mcp` reference dataset.

**Business Rules**:
- Prompt rewrite MUST NOT alter the output file name, file format, or skip behavior established by PRD #128
- Prompt rewrite MUST NOT alter the `has-executive-architecture` gate or the PDF positioning contract
- Prompt MUST be deterministic in structure — same input produces a visually comparable image on re-run (same nodes, same arrows, same callout assignments)

**Edge Cases**:
- System has a single-layer architecture → render the one layer with its nodes and callouts; skip the arrow directives; render a short "Single-zone architecture" caption instead of cross-layer arrows
- System has ambiguous component names that Gemini cannot infer flow from → prompt MUST fall back to alphabetical node ordering within the layer and omit inter-layer arrows (handled gracefully in Level 1; eliminated in Level 3)

### FR-212-2: Callout Selection Rework (Level 2)
**Description**: Change `scripts/extract-infographic-data.py` `_select_critical_high_callouts()` from "top-scored finding per layer" to "top 6–8 findings across the whole system, distributed roughly evenly by layer".

**Inputs**: Sorted list of Critical/High findings with layer attribution and optional composite score.
**Processing**: Select 6–8 findings, weighted toward layers with more qualifying findings, with stable tie-break.
**Outputs**: Callout list passed into the executive-architecture payload.

**Business Rules**:
- Selection cap: 8 callouts maximum (visual-density ceiling to match OpenClaw reference)
- Selection floor: all qualifying findings when total count ≤ 8 (no callouts dropped on small datasets)
- Tie-break: severity descending (Critical before High) → composite score descending (when available) → finding ID ascending (deterministic)
- Distribution: weighted by count-per-layer but not strict equal-per-layer — a layer with 6 qualifying findings should get more callouts than a layer with 1, up to an individual layer cap of 4 callouts to avoid visual imbalance
- Backward compatibility: a threat model run under the new logic MUST NOT drop any finding that the old per-layer-dedup logic would have displayed (the new logic produces a superset or reorder, not a disjoint selection)

**Edge Cases**:
- Total qualifying findings < 6: emit all of them (no synthetic inflation)
- Total qualifying findings = 0: skip the template (PRD #128 skip behavior preserved)
- One layer has all qualifying findings: cap that layer at 4 callouts; surface the rest as "+ N more in this layer" compact annotation

### FR-212-3: Payload Data-Model Expansion (Level 3)
**Description**: Forward `data_flows` (as `flow_edges[]`) and `boundary_crossings` (as `clusters[]`) from `parse_scope_data` into the executive-architecture payload emitted by `scripts/extract-infographic-data.py`.

**Inputs**: `parse_scope_data` output already consumed elsewhere in the extractor (see `scripts/extract-infographic-data.py` line 49 import).
**Processing**: Add `flow_edges[]` and `clusters[]` fields to the `_build_executive_architecture_payload` return dict.
**Outputs**: Extended payload schema with two new arrays; updated Gemini prompt that references them explicitly.

**Business Rules**:
- Schema extension is additive — existing payload fields remain unchanged
- When `data_flows` / `boundary_crossings` sections are absent from `threats.md`, the new fields MUST emit as empty arrays (not `null`, not missing) so the Gemini prompt can branch on length
- Payload schema change MUST be documented in `.claude/skills/tachi-infographics/references/executive-architecture.md`
- The Gemini prompt MUST be updated in the same Level 3 change so the new data is actually consumed (no orphaned fields)

**Edge Cases**:
- `data_flows` defined but no matching components in the DFD → log a warning, emit the edges anyway with best-effort component matching, let the prompt degrade to the Level 1 fallback if matching fails
- Very large threat models (50+ edges) → truncate to the top N edges by some ordering (TBD in spec) — visual density must match page size

### Data Requirements
**Schema change (Level 3)** — `_build_executive_architecture_payload` return dict gains:

```
flow_edges: list[dict]
  - source: string (component name)
  - target: string (component name)
  - optional: label (string), protocol (string), direction ("bidirectional" | "unidirectional")

clusters: list[dict]
  - name: string (cluster/boundary name)
  - members: list[string] (component names)
  - optional: style ("dashed" | "solid"), accent_color (string)
```

**Validation**:
- `source` and `target` in `flow_edges[]` MUST match component names that appear elsewhere in the payload (no dangling edges)
- `members` in `clusters[]` MUST be a subset of payload component names
- Empty arrays are valid; missing fields are not valid

---

## Non-Functional Requirements

### Performance Requirements
- Extractor runtime MUST NOT regress by more than 10% on a reference threat model — the callout selection and payload expansion are O(n) over findings and components
- Gemini call latency is out of scope (external service)
- PDF assembly latency MUST NOT change (no Typst changes in this PRD)

### Reliability Requirements
- Pipeline determinism: re-running the extractor on identical input MUST produce byte-identical payloads
- PDF byte-identity: when a threat model has zero Critical/High findings, the PDF output MUST remain byte-identical to the pre-F-212 baseline (skip behavior invariant)
- No regressions on threat models already processed by F-128 — the image may differ visually (that's the point), but no pipeline step fails

### Security Requirements
- No new data exfiltration paths (the new payload fields are already present in `threats.md` input)
- Gemini prompt changes MUST NOT inject user-controlled content unescaped (prompt injection surface unchanged from F-128)

### Compatibility Requirements
- F-128 output-artifact contract preserved (`threat-executive-architecture.jpg`, `threat-executive-architecture-spec.md`)
- F-128 PDF positioning contract preserved (`has-executive-architecture` gate, pages 2–3)
- F-128 skip-behavior contract preserved (no image generated when 0 Critical/High findings)
- Level 3 payload schema change is additive only — downstream consumers relying on existing fields see no change

---

## Success Metrics

### Primary Metrics (Pass/Fail on First Release)

**M1: Structural Parity with OpenClaw Reference**
- **Definition**: Side-by-side visual comparison of regenerated `threat-executive-architecture.jpg` (on `second-brain-mcp/docs/security/2026-04-23T23-02-25/`) against `openclaw-agent-threat-model-infographic.jpg` on four structural criteria
- **Criteria**: (1) components are nodes, not floating text — PASS/FAIL; (2) arrows connect layers — PASS/FAIL; (3) callouts have leader lines to specific nodes — PASS/FAIL; (4) ≥5 callouts visible — PASS/FAIL
- **Baseline**: Current image fails criteria 1, 2, 3; partially passes 4 (2/5 callouts)
- **Target**: All four criteria PASS
- **Measurement**: Human reviewer side-by-side comparison at release time

**M2: Empty-Layer Waste Elimination**
- **Definition**: Percentage of page height consumed by empty-layer placeholder text
- **Baseline**: ~30% of page height on the reference dataset
- **Target**: ≤15% of page height (compact badge treatment)
- **Measurement**: Pixel-height measurement on regenerated reference image

**M3: Callout Density**
- **Definition**: Number of threat callouts visible on the page for the reference dataset (9 qualifying findings)
- **Baseline**: 2 callouts
- **Target**: 6–8 callouts
- **Measurement**: Count in regenerated spec JSON and rendered image

### Secondary Metrics (Process Quality)

**M4: Payload Schema Compliance (Level 3)**
- **Definition**: Presence and non-emptiness of `flow_edges[]` and `clusters[]` in the payload for threat models that define them in `threats.md`
- **Target**: 100% of threat models with `data_flows` / `boundary_crossings` emit non-empty arrays
- **Measurement**: Extractor unit test or smoke-test run

**M5: Determinism Preservation**
- **Definition**: Byte-identity of payload JSON across two consecutive runs on the same input
- **Target**: 100% byte-identical
- **Measurement**: `diff` on payload JSON between runs

---

## Scope & Boundaries

### In Scope

**Must Have (P0) — Level 1 + Level 2**:
- Gemini prompt rewrite for OpenClaw-style nodes, arrows, callout leader lines, layer colors, empty-layer badges (FR-212-1)
- Callout selection rework to 6–8 findings with weighted distribution and updated tie-break (FR-212-2)
- Regenerated reference image passing all four M1 structural criteria
- Preservation of F-128 contracts (output artifacts, PDF positioning, skip behavior)

**Should Have (P1) — Level 3**:
- Payload data-model expansion with `flow_edges[]` and `clusters[]` fields (FR-212-3)
- Gemini prompt update consuming the new payload fields
- Documentation of new payload schema in `.claude/skills/tachi-infographics/references/executive-architecture.md`

### Out of Scope

**Won't Have (Explicitly Excluded)**:
- Changes to any infographic template other than `executive-architecture` (baseball-card, system-architecture, risk-funnel, maestro-stack, maestro-heatmap are untouched)
- Changes to PDF positioning or the `has-executive-architecture` gate
- Changes to Typst helpers or `report-data.typ` structure
- Changes to the extractor's `parse_scope_data` function itself (we consume it; we do not modify it)
- Changes to `threats.md` format or authoring conventions
- A visual-regression test harness (tracked separately; Level 1 + 2 validated by human side-by-side review)
- Changes to the Gemini model version or API parameters
- Support for alternative rendering backends (Mermaid, Graphviz, etc.)

### Assumptions
- The reference aesthetic (`openclaw-agent-threat-model-infographic.jpg`) is a stable visual target the Gemini model can approximate via prompt engineering
- `parse_scope_data` in the extractor already produces structured `data_flows` and `boundary_crossings` output (verified via `scripts/extract-infographic-data.py` line 49 import) — Level 3 only forwards existing data, does not re-parse
- Threat models produced by the tachi pipeline already populate the `data_flows` and `boundary_crossings` sections of `threats.md` when architecture is described — Level 3 benefit is gated on that content being present
- The 9-High-finding `second-brain-mcp/docs/security/2026-04-23T23-02-25/` dataset is representative enough to validate the quality improvement (additional datasets may be tested but are not gating)

**Validation Needed**:
- [ ] Confirm Gemini can reliably render leader-lined callouts on nodes at the page-2–3 aspect ratio (Level 1 spike — test in one prompt iteration before finalizing)
- [ ] Confirm `parse_scope_data` output shape matches what Level 3 expects (read the existing function before writing the Level 3 schema change)

### Constraints

**Technical Constraints**:
- All changes MUST preserve the deterministic-extraction contract (same input → same payload)
- Gemini is the image-generation provider; no swap-out is in scope
- Portrait orientation is the only supported layout for this template (set by F-128)
- The image is rendered as a JPEG (set by F-128)

**Business Constraints**:
- Timeline: 1 week total across all three levels (Level 1 + 2 in the first 3 days; Level 3 in the following 4 days)
- Ideally ships before the next security-report booklet release for external distribution
- No third-party library additions without explicit approval

---

## Timeline & Milestones

### Phase Breakdown

**Phase 1: Level 1 Prompt Rewrite** (Day 1, ~2h)
- Rewrite `.claude/skills/tachi-infographics/references/gemini-prompt-construction.md` visual-directive block
- Rewrite `.claude/skills/tachi-infographics/references/executive-architecture.md` to document the new directives
- Regenerate the reference image; validate structural criteria M1.1–M1.4 by inspection
- **Deliverable**: Updated skill references + regenerated reference image passing all four M1 criteria

**Phase 2: Level 2 Callout Selection Rework** (Day 2–3, ~4h)
- Modify `_select_critical_high_callouts()` in `scripts/extract-infographic-data.py`
- Update tie-break and distribution logic; add compact "+ N more" annotation for over-populated layers
- Regenerate the reference image; validate M3 callout density
- Regression-test on at least one other tachi dataset to confirm no callout previously shown is dropped
- **Deliverable**: Updated extractor + regenerated reference image with 6–8 callouts

**Phase 3: Level 3 Data-Model Expansion** (Day 4–7, ~1–2 days)
- Extend `_build_executive_architecture_payload` with `flow_edges[]` and `clusters[]` from `parse_scope_data`
- Update Gemini prompt to consume the new fields explicitly
- Document the schema change in the skill reference
- Regenerate the reference image; confirm M4 (payload fields populated) and M5 (determinism preserved)
- **Deliverable**: Extended payload schema + updated prompt + documentation + final reference image

### Key Milestones

| Milestone | Target Date | Owner | Status |
|-----------|-------------|-------|--------|
| PRD Approval | 2026-04-24 | product-manager | In Review |
| Spec Complete | 2026-04-25 | architect | Pending |
| Level 1 Complete | 2026-04-25 | maintainer | Pending |
| Level 2 Complete | 2026-04-27 | maintainer | Pending |
| Level 3 Complete | 2026-05-01 | maintainer | Pending |
| Delivery | 2026-05-01 | product-manager | Pending |

---

## Risks & Dependencies

### Technical Risks

**R1: Gemini Prompt Engineering Fragility**
- **Likelihood**: Medium
- **Impact**: Medium (Level 1 may need multiple prompt iterations to reach the target aesthetic)
- **Mitigation**: Level 3 data-model expansion specifically eliminates Gemini inference for flow/clustering. Treat Level 1 as a 70% quality win; Level 3 as the endgame.
- **Contingency**: If Level 1 cannot reach 3/4 of the M1 criteria after 2 prompt iterations, prioritize Level 3 first and accept slower time-to-first-quality-win.

**R2: Backward-Compatibility Break**
- **Likelihood**: Low
- **Impact**: High (any change that alters the F-128 contract breaks downstream PDF assembly)
- **Mitigation**: Explicit out-of-scope list in this PRD enumerates the F-128 contracts that MUST NOT change; regression test at each phase gate confirms PDF byte-identity on a no-finding input.
- **Contingency**: Revert prompt changes if PDF positioning or skip behavior regresses; Level 2/3 can proceed independently of Level 1 if needed.

**R3: `parse_scope_data` Output Shape Mismatch**
- **Likelihood**: Low
- **Impact**: Medium (Level 3 schema depends on what the function currently returns)
- **Mitigation**: Read the function before writing the Level 3 spec; validation task `[ ] Confirm parse_scope_data output shape` in the scope section.
- **Contingency**: Adapt the schema extension to match the real output shape during spec; if the existing function needs expansion, de-scope Level 3 and track as a separate PRD.

### Business Risks

**R4: Partial Delivery Perception**
- **Likelihood**: Low
- **Impact**: Low (Levels 1 + 2 ship first and deliver ~70% of user-visible value; Level 3 ships as endgame)
- **Mitigation**: Bundling rationale is documented — all three levels target the same user-visible output and benefit from a single end-to-end test cycle. Sequencing Level 1 → 2 → 3 is the right order regardless.

### Dependencies

**Internal Dependencies**:
- **Tachi extractor pipeline (`scripts/extract-infographic-data.py`)**: Already end-to-end functional after Issue #209 fix. No unblocking needed.
- **Tachi infographics skill (`.claude/skills/tachi-infographics/`)**: Stable; no upstream blockers.
- **Gemini API availability**: Required for image regeneration during validation. Existing production credentials.

**External Dependencies**: None.

---

## Open Questions

### Product Questions
- [ ] Callout cap per layer — is 4 the right ceiling, or should it be proportional to total page area? *Owner: product-manager — Due: before spec*
- [ ] "+ N more" compact annotation wording — is a number adequate, or do we want category attribution? *Owner: product-manager — Due: before spec*

### Technical Questions
- [ ] Exact `parse_scope_data` output shape — needs reading before Level 3 spec finalization *Owner: architect — Due: before spec for Level 3*
- [ ] `flow_edges[]` truncation ordering for very large threat models — by source layer, by score, by edge count? *Owner: architect — Due: before spec for Level 3*
- [ ] Visual-regression test harness — out of scope here, but should it be a follow-up PRD? *Owner: team-lead — Due: after delivery*

### Design Questions
- [ ] Layer color palette — inherit from `visual-design-system.md` or introduce executive-architecture-specific palette matching OpenClaw? *Owner: product-manager + architect — Due: during Level 1*

---

## References

### Product Documentation
- Product Vision: [docs/product/01_Product_Vision/product-vision.md](../01_Product_Vision/product-vision.md)
- Predecessor PRD: [docs/product/02_PRD/128-executive-threat-architecture-2026-04-09.md](128-executive-threat-architecture-2026-04-09.md)
- Source Issue: [GitHub Issue #212](https://github.com/davidmatousek/tachi/issues/212)

### Technical Documentation
- Constitution: [.aod/memory/constitution.md](../../../.aod/memory/constitution.md)
- Infographic skill: [.claude/skills/tachi-infographics/references/executive-architecture.md](../../../.claude/skills/tachi-infographics/references/executive-architecture.md)
- Extractor script: [scripts/extract-infographic-data.py](../../../scripts/extract-infographic-data.py)

### Reference Assets
- Target aesthetic: `openclaw-agent-threat-model-infographic.jpg` (external reference)
- Current output: `second-brain-mcp/docs/security/2026-04-23T23-02-25/threat-executive-architecture.jpg`

### Related PRDs
- PRD #018 (threat-infographic-agent — foundational)
- PRD #128 (executive-threat-architecture — predecessor)
- PRD #136 (maestro-canonical-layer-correctness-fix — related quality arc)
- PRD #145 (maestro-canonical-worked-example — related quality arc)

---

## Approval & Sign-Off

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | APPROVED_WITH_CONCERNS | 2026-04-24 | 3 concerns (1M, 2L) — see `.aod/results/pm-review-prd-212.md` |
| Architect | architect | APPROVED_WITH_CONCERNS | 2026-04-24 | 4 concerns (1H, 2M, 1L) — see `.aod/results/architect-review-prd-212.md` |
| Engineering Lead | team-lead | APPROVED_WITH_CONCERNS | 2026-04-24 | 4 concerns (2M, 2L) — see `.aod/results/teamlead-review-prd-212.md` |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-24 | product-manager | Initial PRD from Issue #212 |
