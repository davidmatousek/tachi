---
prd:
  number: "098"
  topic: maestro-7-layer-output-polish
  created: 2026-06-01
  status: Approved
  type: feature
triad:
  pm_signoff: { agent: product-manager, date: 2026-06-01, status: APPROVED, notes: "Author sign-off. Scope matches the user's stated goal (distinguish analyzed-but-clean / not-applicable / silently-dropped) and Issue #98. Triad-resolved v1 decisions folded into v1.1: Model A annotation as P0 (Model B clean-vs-n/a deferred to P1 follow-up), canonical L1-L7 ordering in both pipelines." }
  architect_signoff: { agent: architect, date: 2026-06-01, status: APPROVED_WITH_CONCERNS, notes: "v1.1 re-review: BLOCKING root-cause finding RESOLVED (verified against source — orchestrator.md:718 is the true root cause; layer_groups seeded from parsed_layers; _MAESTRO_LAYERS is sort-only; baseline count=6; D1/D2/D3 correct; no-SARIF/threat-report-exclusion/ADR-021/no-new-ADR re-confirmed). 1 non-blocking residual: pin the complete enumeration of example + sample-report threats.md files in tasks.md so none is left <7 rows. Details: .aod/results/architect.md" }
  techlead_signoff: { agent: team-lead, date: 2026-06-01, status: APPROVED_WITH_CONCERNS, notes: "6 findings (1 High, 3 Med, 2 Low). Revised effort to 1.0-1.5 days. Model B → P1/deferred, Model A is P0. Gate: ordering rule + annotation model frozen at definition (folded into v1.1) before any example edit. F-302 fixture drift does not apply; baseline regen is mechanical. Details: .aod/results/team-lead.md" }
source:
  idea_id: 98
  story_id: null
---

# MAESTRO Coverage Matrix — Always Render All 7 Layers

**Status**: Approved
**Created**: 2026-06-01
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P2 (Medium) — BLP-04 Wave 4 (final wave)
**Evidence**: Issue [#98](https://github.com/davidmatousek/tachi/issues/98) open since 2026-04-08; confirmed real via post-Feature-141 audit (2026-04-14) of `examples/agentic-app/sample-report/`. Scoped in `_internal/strategy/BLP-04-adoption-push.md` §5 (F-4). ICE (seed): Impact 5, Confidence 9, Effort 2.

---

## Executive Summary

### The One-Liner
Render all 7 canonical MAESTRO layers (L1–L7) in every MAESTRO coverage view — including layers with zero findings — so a reviewer can distinguish "analyzed but clean" from "not applicable to this architecture" from "silently dropped."

### Problem Statement
Tachi classifies findings across the CSA MAESTRO seven-layer taxonomy (L1 Foundation Model → L7 Agent Ecosystem), but the layer-aware *coverage views* hide layers that have zero findings. The omission originates in a single root cause and propagates downstream:

1. **Root cause** — `.claude/agents/tachi/orchestrator.md:718`: the LLM directive that authors the threats.md "Risk by MAESTRO Layer" table says *"Omit layers with zero findings."* The threats.md markdown table is the source of truth for the matrix.
2. `.claude/skills/tachi-orchestration/references/output-schemas.md:238` — the spec codifies the same rule: *"Omission: Layers with zero findings are omitted from the table."*
3. **Downstream (PDF)** — `scripts/extract-report-data.py:363-370` pre-populates its `layer_groups` from the *parsed markdown table* (`parsed_layers`), so any layer the LLM already omitted never enters the PDF data model. Line 407's `findings_by_layer = [... if layer_groups[lid]["findings"]]` then drops any remaining zero-finding layer. The PDF inherits the omission from the markdown and re-enforces it.
4. `templates/tachi/security-report/maestro-findings.typ:151–155` — an empty-layer fallback ("No findings mapped to this layer.") already exists but is **dead code** because zero-finding layers never reach it.
5. Example outputs encode the gap: `examples/agentic-app/sample-report/threats.md` shows 7 rows but **silently omits L4 (Deployment Infrastructure)**; `examples/web-app/threats.md` shows only 2 of 7 layers.

The result is an interpretability failure. A prospect evaluating a tachi report sees a 2-of-7 or 3-of-7 sparse matrix and reasonably misreads it as *"tachi only covers these few MAESTRO layers."* The reviewer cannot tell three very different situations apart:

- **Analyzed but clean** — the layer was in scope and detection agents found nothing.
- **Not applicable** — no architecture components map to this layer.
- **Silently dropped** — the layer exists but the renderer hid it.

This directly undercuts the marquee positioning the rest of BLP-04 is publicizing (five-framework OWASP coverage + seven-layer MAESTRO). The fix is small; the credibility cost of *not* fixing it grows with every report a prospect inspects.

### Proposed Solution
Fix the omission at its **root** (the orchestrator LLM directive + the output-schemas spec) so the threats.md markdown table always authors all 7 canonical layers in canonical L1–L7 order. Carry that through to the **PDF** by removing the downstream filter so the (now-present) zero-finding layers reach the existing Typst fallback. Annotate zero-finding rows so a reviewer knows *why* a layer is empty. No SARIF/schema change — markdown and PDF rendering only. Regenerate the affected example outputs and the 6 byte-deterministic PDF baselines, and add a regression test that pins the 7-row invariant so the omission cannot silently return.

### Success Criteria
- Every MAESTRO coverage view (threats.md table + PDF "MAESTRO Layer Analysis" page) renders all 7 canonical layers (L1–L7) on every run, in a single canonical order shared by both pipelines.
- Zero-finding rows are visually present and annotated so a reviewer can distinguish a clean/covered layer from a silently-dropped one — eliminating the "silently dropped" failure mode (Model A, see FR-3).
- An "Unclassified" row continues to appear only when unclassified findings exist (unchanged behavior).
- Affected example outputs regenerated; the **6** byte-deterministic PDF baselines regenerated and the backward-compatibility test passes under `SOURCE_DATE_EPOCH=1700000000` (ADR-021).
- A regression test asserts the 7-row invariant.
- No SARIF / schema change; `/aod.analyze` passes.

### Timeline
Estimated **1.0–1.5 days** (revised up from ~1 day per Team-Lead review). The rendering change is small (one LLM directive + one spec bullet + one filter line), but the regeneration tail is the real cost: 6–7 example threats.md tables must be completed to 7 canonical rows *and re-sorted to canonical order*, then 6 PDF baselines regenerated deterministically. The two design decisions with any weight (annotation granularity, row ordering) are resolved at definition (see Resolved Decisions) so no rework risk remains for build.

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)

Tachi positions itself as the default threat-modeling and AI-reasoning vulnerability harness, differentiated by MAESTRO seven-layer classification. A coverage matrix that hides empty layers makes a complete scan *look* partial — it sells the differentiator short at the exact moment an evaluator is forming an opinion. Making the full seven-layer span legible in every report converts a latent capability into a visible one.

### Roadmap Fit
This is **F-4, the fourth and final wave of BLP-04 (Adoption Push)**. BLP-04 converts the OWASP 50/50 + MAESTRO coverage milestone into public, adopter-facing credibility. F-1 published the 50/50 narrative, F-2 wired community asset-tags end-to-end, F-3 built adoption-signal capture. F-4 closes the loop on output fidelity: when newly-arriving evaluators inspect a tachi run (the traffic F-1/F-2/F-3 are designed to generate), the MAESTRO matrix should show the full scan span, not a sparse subset. Independent of F-1/F-2/F-3; tail-end placement is preference, not a hard dependency.

### Predecessor Relationship
| Feature | Relationship |
|---------|-------------|
| 084 (MAESTRO Layer Mapping) | Established the L1–L7 taxonomy and the "Risk by MAESTRO Layer" subsection — the surface this PRD completes |
| 136 (MAESTRO Canonical Layer Correctness) | Froze the canonical layer names/IDs this PRD renders — prerequisite for accurate empty-row labels |
| 091 (MAESTRO Infographics + PDF section) | Built the PDF "MAESTRO Layer Analysis" page and the `maestro-findings.typ` template whose empty-layer fallback this PRD activates; also the (optional) `maestro-stack` infographic |
| 141 (Cross-Layer Attack Chains) | The 2026-04-14 post-141 audit confirmed this gap is real and not subsumed by chains; chains are cross-finding narratives, not a layer roster |
| 104 / ADR-021 (Deterministic baselines) | The 6 byte-deterministic PDF baselines must be regenerated when the matrix grows |

---

## Target Users & Personas

### Primary Persona: Security Architect Evaluating Tachi
- **Role**: Security architect comparing threat-modeling tools before adoption
- **Experience**: Senior; reads tool output critically and skeptically
- **Goal**: Assess how much of the MAESTRO taxonomy tachi actually reasons over
- **Pain Point**: A sparse matrix (e.g., 2 of 7 layers) reads as a coverage *ceiling*. The reviewer cannot tell "scanned, clean" from "hidden," so they assume the worst.

**Why This Matters**: This persona forms the adoption decision off exactly the artifact this PRD fixes. The cost of the gap is paid precisely when BLP-04's distribution is sending these people to inspect a report.

### Secondary Persona: Tachi Maintainer Fielding Evaluator Questions
- **Role**: Maintainer (and, transitively, anyone advocating for tachi internally)
- **Goal**: Have the report be self-documenting so coverage questions answer themselves
- **Pain Point**: Currently must verbally clarify "we scanned that layer too, it was just clean" — a claim the artifact should make on its own.

**Why This Matters**: A self-documenting matrix removes a recurring, low-value clarification loop and makes the report defensible without a human in the loop.

---

## User Stories

### US-1: Architect Sees the Full Scan Span
**When** reviewing a tachi threat-model report for an agentic system,
**I want** the MAESTRO coverage matrix to list all 7 layers even when some have zero findings,
**So I can** understand the complete scan span and not mistake an empty layer for a coverage limit.

**Acceptance Criteria**:
- **Given** any completed pipeline run, **when** I open the threats.md "Risk by MAESTRO Layer" section, **then** all 7 canonical layers (L1–L7) appear as rows in canonical order.
- **Given** the same run, **when** I open the PDF "MAESTRO Layer Analysis" page, **then** all 7 layers appear in the same canonical order (zero-finding layers included).
- **Given** a run that produced unclassified findings, **when** I view either view, **then** an "Unclassified" row also appears (unchanged behavior); **given** no unclassified findings, **then** no "Unclassified" row appears.

**Priority**: P0 | **Effort**: S

### US-2: Self-Documenting Zero-Finding Rows
**When** I encounter a layer with zero findings in the matrix,
**I want** the row to state explicitly that the layer was analyzed and produced no findings,
**So I can** read it as "covered, clean" rather than as a gap or an omission.

**Acceptance Criteria**:
- **Given** a layer with zero findings, **when** I read its row, **then** the row shows a 0 count and an explicit annotation rather than a blank cell or absence.
- **Given** the annotation, **when** I compare the threats.md table and the PDF page, **then** the wording is identical.

**Priority**: P0 | **Effort**: S

### US-3: Regression-Proofed Completeness
**When** future features touch the renderer or example outputs,
**I want** a test that fails if a MAESTRO view drops back to fewer than 7 layers,
**So that** the completeness guarantee cannot silently regress.

**Acceptance Criteria**:
- **Given** the test suite, **when** a renderer change omits a canonical layer, **then** a test fails identifying the missing layer(s).
- **Given** regenerated examples, **when** the backward-compatibility test runs, **then** the 6 PDF baselines match byte-for-byte under `SOURCE_DATE_EPOCH=1700000000`.

**Priority**: P1 | **Effort**: S

---

## Functional Requirements

### FR-1: threats.md "Risk by MAESTRO Layer" Always Renders 7 Layers (Root Cause)
**Description**: The threats.md coverage matrix — the source of truth for the matrix — always renders all 7 canonical layers (L1–L7) in canonical order, regardless of finding count. This is the single root-cause fix; the PDF (FR-2) derives from this table.

**Changes**:
- `.claude/agents/tachi/orchestrator.md:718` — replace the *"Omit layers with zero findings"* directive with: *"always emit all 7 canonical layers (L1–L7) in canonical L1→L7 order; zero-finding layers show count 0 and the empty-row annotation (FR-3)."* Also change the ordering instruction from severity-descending to **canonical L1–L7** (see Resolved Decision D2).
- `.claude/skills/tachi-orchestration/references/output-schemas.md:238` — replace the "Omission" bullet with an "always include all 7 canonical layers" rule; update the "Ordering" bullet to canonical L1–L7; specify the empty-row annotation text (FR-3).

**Business Rules**:
- All 7 canonical layers always present; canonical order is L1, L2, L3, L4, L5, L6, L7, then a conditional "Unclassified" row last.
- The "Unclassified" row remains conditional on the presence of unclassified findings (unchanged).
- Canonical layer names/IDs come from the single shared reference (`.claude/skills/tachi-shared/references/maestro-layers-shared.md`).

### FR-2: PDF "MAESTRO Layer Analysis" Page Always Renders 7 Layers (Carry-Through — depends on FR-1)
**Description**: The PDF security report's MAESTRO page renders all 7 canonical layers. **This depends on FR-1**: `extract-report-data.py` builds its `layer_groups` by pre-populating from the *parsed markdown table* (`parsed_layers`, `extract-report-data.py:363-370`) — **not** from a hard-coded canonical list — so the PDF can only show layers that FR-1 has already placed in the markdown.

**Changes**:
- `scripts/extract-report-data.py:407` — drop (or invert) the `if layer_groups[lid]["findings"]` filter so zero-finding layers — now present in `parsed_layers` thanks to FR-1 — survive into `findings_by_layer` and reach the template. (Note: `_MAESTRO_LAYERS` at line 399 is used only for sort ordering, not seeding; the v1.0 claim that the dict was "seeded with all 7 via `_MAESTRO_LAYERS`" was incorrect — corrected per Architect review.)
- `templates/tachi/security-report/maestro-findings.typ:151–155` — no code change required; the `else` branch ("No findings mapped to this layer.") becomes live once the filter is removed. Confirm the rendered wording matches the FR-3 annotation; adjust the literal string if needed for cross-format consistency.

**Business Rules**:
- Canonical order preserved (`extract-report-data.py` already sorts L1–L7 then Unclassified at lines 397-406 — this already matches the FR-1 canonical ordering, so no PDF ordering change is needed; FR-1 brings the markdown into line with the PDF, not vice versa).
- The per-layer heading already renders a `(N findings)` count — verify it reads correctly for `0 findings`.

### FR-3: Zero-Finding Row Annotation — Model A (v1)
**Description**: Zero-finding rows carry an explicit annotation so a reviewer reads them as "covered, clean" rather than as a gap. **Resolved at definition (D1): Model A is the v1 implementation.**

- **Model A (v1, accepted)**: every zero-finding layer shows a `0` count plus an annotation such as *"no detection-agent contributions for this layer in current scan."* This eliminates the "silently dropped" failure mode and makes every layer's status explicit.
- **Model B (P1 follow-up, deferred)**: distinguish `0 (clean)` (components map to the layer, no findings) from `n/a (no components mapped)`. This delivers the *full* three-state distinction but requires routing component→layer mapping into the matrix renderer. That data is computed today only in a *different* pipeline (`component_layer_map` in `extract-infographic-data.py`, for the heatmap), so wiring it into the orchestrator LLM directive + threats.md table is cross-pipeline work disproportionate to a ~1-day polish (Architect + Team-Lead concurrence). Tracked as a follow-up; **not** a close-gate for Issue #98.

**Business Rules**:
- Annotation wording is identical across threats.md and the PDF page (cross-format consistency).
- The annotation is coverage metadata, never a severity — phrased so it cannot be misread as a finding.

### FR-4: Example Output Regeneration
**Description**: Regenerate affected example outputs so shipped examples demonstrate the 7-layer matrix in canonical order.

**Scope**: At minimum `examples/agentic-app/` (richest MAESTRO coverage; currently omits L4) regenerated and its diff shown in the PR. The sparse-matrix examples (`web-app`, `mermaid-agentic-app`, `microservices`, `free-text-microservice`, `ascii-web-api`, `maestro-reference`) regenerated for consistency. Each table is (a) completed to all 7 canonical rows with Model A annotations for zero-finding layers and (b) re-sorted to canonical L1–L7 order (non-empty rows change order too, per D2).

**Business Rules**:
- Regeneration under `SOURCE_DATE_EPOCH=1700000000` per ADR-021.
- `sample-report/` artifacts (with delta annotations) regenerated consistently with their parent example.
- **Plan-stage decision**: whether the markdown table completion is hand-edited or driven by a small deterministic populator (cf. the F-260b `populate-affected-assets.py` precedent). Either is acceptable; the populator is preferable if it reduces per-example manual edits and guards determinism.

### FR-5: Regression Test for 7-Row Invariant
**Description**: Add a test asserting that MAESTRO coverage views always contain all 7 canonical layers.

**Scope**:
- Assert that, given a parsed markdown table containing all 7 canonical rows (post-FR-1), `extract-report-data.py` `findings_by_layer` retains all 7 (including zero-finding) — i.e., the filter no longer drops them.
- Assert the empty-layer annotation renders for a zero-finding layer.
- Existing backward-compatibility test (`tests/scripts/test_backward_compatibility.py`) continues to validate the **6** PDF baselines byte-for-byte after regeneration.

### FR-6 (P1, Optional): maestro-stack Infographic Completeness
**Description**: Optionally extend the `maestro-stack` infographic so its layered stack also shows zero-finding layers explicitly (Issue #98 item 4, marked optional).

**Business Rules**:
- Out of the P0 core; include only if it fits the envelope. The `maestro-heatmap` infographic already renders empty cells, so the heatmap is unaffected.
- If deferred, record as a follow-up; not a close-gate for Issue #98.

---

## Non-Functional Requirements

### Backward Compatibility
- **No SARIF / schema change.** Layer counts are already structured in SARIF; this PRD changes markdown + PDF rendering only. *(Confirmed in Architect review.)*
- The **6** byte-deterministic PDF baselines **will** change (matrix grows by 1–5 rows per example, and non-empty rows re-sort to canonical order). They are regenerated under `SOURCE_DATE_EPOCH=1700000000` and re-committed; the backward-compatibility test then re-passes. This is expected churn, not a compatibility break.
- Existing non-MAESTRO sections of every output are unchanged.

### Determinism
- All regeneration respects ADR-021 determinism. Row ordering is deterministic: canonical L1–L7, then conditional Unclassified (D2).

### Consistency
- Cross-format consistency: the threats.md table, the PDF page, and (if in scope) the infographic show the same 7 layers, the same canonical ordering, and the same annotation wording. FR-1's switch to canonical ordering eliminates the current markdown-vs-PDF ordering divergence.

### Maintainability
- Canonical layer list is sourced from the single shared reference (`.claude/skills/tachi-shared/references/maestro-layers-shared.md`) / `scripts/tachi_parsers.py:MAESTRO_LAYERS`; no duplicate hard-coded layer lists introduced.

---

## Success Metrics

- **Completeness**: 100% of pipeline runs render exactly 7 canonical MAESTRO layers (+ conditional Unclassified) in every coverage view. *(Verified by FR-5 test + regenerated examples.)*
- **Legibility**: 0 instances of a silently-omitted canonical layer across all shipped examples. *(Verified by inspection of regenerated examples.)*
- **No regression**: 6/6 PDF baselines byte-identical post-regeneration; `/aod.analyze` clean.

---

## Scope & Boundaries

### In Scope (P0)
- threats.md "Risk by MAESTRO Layer" always renders L1–L7 in canonical order (FR-1, root cause).
- PDF "MAESTRO Layer Analysis" page always renders L1–L7 (FR-2, carry-through).
- Zero-finding row annotation — Model A (FR-3).
- output-schemas.md spec updated to match (rule + ordering + annotation).
- Affected example outputs + 6 PDF baselines regenerated (FR-4).
- 7-row invariant regression test (FR-5).
- CHANGELOG `feat(098)` entry.

### Should Have (P1)
- Model B two-state annotation (clean vs n/a) as a tracked follow-up (FR-3).
- `maestro-stack` infographic completeness (FR-6).

### Out of Scope
- **threat-report.md per-layer roster.** *(Architect-confirmed exclusion.)* The threat report has **no** per-layer roster section today — only per-finding `maestro_layer` references and the Feature-141 "Cross-Layer Attack Chains" narrative (finding-driven, not a layer roster). Adding a "paragraph per layer including empties" would be net-new structure, not a polish of an existing view. The blueprint's mention of threat-report per-layer paragraphs reflected an inaccurate model of the current structure.
- **SARIF / schema changes** — layer counts already structured; no change.
- **maestro-heatmap infographic** — already renders empty cells; no change needed.
- **New MAESTRO layers or taxonomy changes** — canonical 7 are frozen (Feature 136).
- **Re-scoring / risk-model changes** — zero-finding rows do not affect CVSS or composite scores.

### Assumptions
- Canonical 7-layer taxonomy is stable (Feature 136 merged).
- `extract-report-data.py` pre-populates `layer_groups` from the parsed markdown table (`parsed_layers`), so FR-2 is strictly downstream of FR-1 (confirmed at lines 363-407).
- The `maestro-findings.typ` empty-layer fallback is present and correct (confirmed at lines 151–155; currently dead code).

### Constraints
- Determinism (ADR-021) governs all regeneration.
- Annotation wording must be cross-format identical.

---

## Risks & Dependencies

### Technical Risks

**Risk 98.1 — Regeneration tail underestimated.**
- **Likelihood**: Medium | **Impact**: Medium (the LLM-authored example tables are hand/script edits, not a pure re-run)
- **Mitigation**: Team-Lead revised the estimate to 1.0–1.5 days to absorb this; FR-4 lets the plan choose a deterministic populator to cut per-example manual edits. Freeze ordering + annotation (done at definition, D1/D2) before editing examples to avoid redo.

**Risk 98.2 — Cross-pipeline ordering divergence (RESOLVED at definition).**
- **Status**: Resolved by D2 — single canonical L1–L7 ordering in both pipelines. The PDF already sorts canonically; FR-1 brings the markdown into line. No residual divergence.

**Risk 98.3 — Baseline regeneration churn / accidental content drift.**
- **Likelihood**: Low | **Impact**: Medium (a botched regeneration could change more than the matrix)
- **Mitigation**: Regenerate under `SOURCE_DATE_EPOCH=1700000000`; review the example diffs in the PR to confirm only matrix rows/order changed; the backward-compatibility test gates the merge. (Team-Lead confirmed the F-302 `init-baseline-tree` fixture-drift incident is a separate surface and does not apply here.)

**Risk 98.4 — Annotation misread as a finding.**
- **Likelihood**: Low | **Impact**: Low
- **Mitigation**: PM sign-off on annotation wording; phrase as coverage metadata ("0 — no detection-agent contributions this scan"), never as a severity.

### Dependencies
- **Internal**: Features 084, 091, 136 — all DELIVERED. ADR-021 determinism — in force.
- **External**: `typst` for PDF regeneration (existing toolchain); `mmdc` only if FR-6 infographic is pursued.

---

## Definition of Done

- [ ] threats.md "Risk by MAESTRO Layer" renderer always emits all 7 canonical layers in canonical L1–L7 order (orchestrator.md:718 directive + output-schemas.md:238 spec updated).
- [ ] PDF "MAESTRO Layer Analysis" page always emits all 7 layers (`extract-report-data.py:407` filter removed/inverted; `maestro-findings.typ` fallback live); FR-2 verified downstream of FR-1.
- [ ] Zero-finding rows carry the Model A annotation, identical across threats.md and PDF.
- [ ] "Unclassified" row behavior unchanged (present only when unclassified findings exist).
- [ ] Affected example outputs regenerated; the `examples/agentic-app/` diff is shown in the PR description.
- [ ] 6 PDF baselines regenerated under `SOURCE_DATE_EPOCH=1700000000`; `tests/scripts/test_backward_compatibility.py` passes.
- [ ] 7-row invariant regression test added and passing.
- [ ] No SARIF / schema change (verified).
- [ ] CHANGELOG entry: `feat(098): MAESTRO coverage matrix always shows all 7 layers (Issue #98)`.
- [ ] `/aod.analyze` passes with no inconsistencies.
- [ ] Issue #98 closed.

---

## Resolved Decisions (Triad consensus at definition)

- **D1 — Annotation model: Model A for v1.** Single "no detection-agent contributions this scan" annotation on zero-finding rows. Model B (clean vs n/a) deferred to a P1 follow-up — its component→layer data lives in a different pipeline and is disproportionate to this feature. *(Architect + Team-Lead concurrence.)*
- **D2 — Ordering: canonical L1–L7 in both pipelines.** The markdown table switches from severity-descending to canonical L1–L7 ordering to match the PDF (which already sorts canonically), eliminating today's divergence. Non-empty row order changes as a result — an accepted, deliberate consistency fix. *(Architect + Team-Lead concurrence.)*
- **D3 — Root cause: the orchestrator LLM directive (FR-1), not the PDF filter.** The PDF derives from the parsed markdown; FR-2 is a downstream carry-through dependent on FR-1. *(Architect BLOCKING correction to v1.0, addressed in v1.1.)*

## Open Questions

- [ ] **maestro-stack infographic (FR-6)**: include in this feature or defer as a follow-up? — product-manager — Open (default: defer if it doesn't fit the envelope).
- [ ] **Table completion mechanism (FR-4)**: hand-edit example tables vs. a small deterministic populator — resolve at `/aod.plan`. — architect — Open.
- [ ] **Complete file enumeration (FR-4, Architect re-review residual)**: `tasks.md` must pin the *full* set of example **and** `sample-report/` `threats.md` files carrying the MAESTRO table — broader than FR-4's named list — so no `sample-report` is left at <7 rows. — architect — Open (resolve at `/aod.plan` / `/aod.tasks`).

### Resolved at Definition
- [x] **Annotation granularity** → Model A v1 (D1).
- [x] **Row ordering** → canonical L1–L7 in both pipelines (D2).
- [x] **Root-cause mechanism** → LLM directive is the root; PDF is downstream (D3).
- [x] **threat-report.md per-layer paragraphs?** → out of scope (no such roster exists today).
- [x] **Canonical layer names** → use `maestro-layers-shared.md` (Foundation Model, Data Operations, Agent Framework, Deployment Infrastructure, Evaluation and Observability, Security and Compliance, Agent Ecosystem).

---

## References

### Product Documentation
- Product Vision: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)
- GitHub Issue: [#98](https://github.com/davidmatousek/tachi/issues/98)
- Strategy: `_internal/strategy/BLP-04-adoption-push.md` §5 (F-4) *(internal, gitignored)*

### Related PRDs
- [PRD 084: MAESTRO Layer Mapping](084-maestro-layer-mapping-2026-04-07.md)
- [PRD 091: MAESTRO Infographic Templates & PDF Section](091-maestro-infographic-templates-and-pdf-report-section-2026-04-08.md)
- [PRD 136: MAESTRO Canonical Layer Correctness](136-maestro-canonical-layer-correctness-fix-2026-04-10.md)
- [PRD 141: MAESTRO Cross-Layer Attack Chains](141-maestro-cross-layer-attack-chains-2026-04-12.md)

### Technical Documentation
- ADR-020: MAESTRO Layer Classification — current architecture (no new ADR; Architect concurred)
- ADR-021: SOURCE_DATE_EPOCH for Deterministic PDF — determinism constraint for baseline regeneration
- Shared reference: `.claude/skills/tachi-shared/references/maestro-layers-shared.md` — canonical L1–L7 names
- Spec: `.claude/skills/tachi-orchestration/references/output-schemas.md` — "Risk by MAESTRO Layer" spec (to update)
- Renderer: `.claude/agents/tachi/orchestrator.md:718` (root-cause directive); `scripts/extract-report-data.py:363-407` (PDF data); `templates/tachi/security-report/maestro-findings.typ:151-155` (fallback)

---

## Approval & Sign-Off

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | Approved | 2026-06-01 | Author sign-off; D1/D2 folded in; annotation = Model A |
| Architect | architect | Approved with Concerns | 2026-06-01 | v1.1 re-review: blocking root-cause RESOLVED; 1 non-blocking residual (pin full file enumeration in tasks.md) |
| Team Lead | team-lead | Approved with Concerns | 2026-06-01 | 1.0–1.5 days; Model B P1/deferred; ordering+annotation frozen at definition |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-01 | product-manager | Initial PRD (BLP-04 F-4) |
| 1.1 | 2026-06-01 | product-manager | Addressed Triad review: corrected root cause to the orchestrator LLM directive (FR-1) with the PDF as downstream carry-through (FR-2, D3); resolved Model A as v1 / Model B deferred (D1); resolved canonical L1–L7 ordering in both pipelines (D2); corrected baseline count 5→6; revised effort to 1.0–1.5 days |
