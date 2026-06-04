---
prd_reference: docs/product/02_PRD/311-maestro-matrix-model-b-clean-vs-na-2026-06-03.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-03
    status: APPROVED
    notes: "PRD→spec traceability COMPLETE: 8/8 PRD FRs carried into spec FR-001..FR-014 (6 enrichments are reviewer-concern folds, no scope creep); 3/3 user stories independently-testable MVP slices; 5/5 SCs preserved/measurable; 7/7 Out-of-Scope boundaries honored (maestro-heatmap + threat-report roster structurally fenced). Both blocking Open-Qs resolved in-spec (ADR→option c recorded; per-surface n/a visual state fixed). All Architect (1H/3M/2L incl. HIGH-1 renderer condition) + Team-Lead (do-not-split; fixture=microservices) concerns folded. 0 BLOCKING / 0 CHANGES_REQUESTED / 2 LOW advisory (US P0→P1 label normalization; keep two-token doc-update a named task) carried to plan/tasks. No veto. Full: .aod/results/product-manager.md"
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: MAESTRO Matrix Model B — Clean vs. N/A

**Feature Branch**: `311-maestro-matrix-model-b-clean-vs-na`
**Created**: 2026-06-03
**Status**: Draft
**Input**: PRD 311 — MAESTRO Matrix Model B: clean vs n/a (BLP-05 Wave 1, APPROVED). Bring the two-state coverage vocabulary (analyzed-clean vs not-applicable) to the MAESTRO 7-layer view across all three rendering surfaces, closing F-098 SC-006. Single feature, do not split (Team-Lead). ADR-bearing (ADR-047).

---

## Overview *(non-mandatory context)*

A MAESTRO layer with zero findings is ambiguous today: F-098 (Model A) renders every zero-finding layer with one flat annotation — `Analyzed — no findings this scan` — whether or not any component actually maps to that layer. This conflates two distinct facts:

- **Clean** — ≥1 component maps to the layer and it was analyzed with zero findings ("We looked and found nothing").
- **n/a** — no component maps to the layer, so it was never in scope ("We did not look, as expected").

Model B splits that single state into two, reusing the **already-canonical** STRIDE coverage vocabulary (`coverage-matrix-model.md`: `---` analyzed-clean / `n/a` not-applicable) expressed in the MAESTRO layer view, and propagates it identically across the three surfaces using "author once, inherit": the orchestrator encodes the state once into the Section-6 *Highest Severity* cell it already authors, and both downstream Python extractors inherit it. No SARIF/schema/scoring/taxonomy change.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Tell clean from n/a in the report (Priority: P1)

A security engineer reviews a tachi MAESTRO layer analysis (the `threats.md` matrix, the PDF "MAESTRO Layer Analysis" page, or the shared `maestro-stack` infographic) and sees a layer with 0 findings. They can tell, **from that surface alone**, whether the layer was *analyzed-and-clean* or *not-applicable to this architecture* — without asking the report author.

**Why this priority**: This is the core user value and the reason Model B exists. It closes the exact ambiguity F-098 only half-closed (SC-006) and ends the recurring "did you actually scan L5, or does it just not apply?" clarification loop. Delivering this one story — the clean-vs-n/a distinction visible on every surface — is the feature's MVP.

**Independent Test**: Run the threat model on `examples/microservices` (L2/L4/L7 mapped; L1/L3/L5/L6 unmapped; L7 mapped with 0 findings). Confirm that on each of the three surfaces, L7 reads as **clean** and L1/L3/L5/L6 read as **n/a**, visibly distinct from each other and from finding-bearing layers (L2/L4).

**Acceptance Scenarios**:

1. **Given** an architecture where ≥1 component maps to a layer and that layer has 0 findings, **When** the report renders, **Then** that layer is shown as **clean** (analyzed, no findings) on the `threats.md` matrix, the PDF page, and the `maestro-stack` infographic.
2. **Given** an architecture where no component maps to a layer, **When** the report renders, **Then** that layer is shown as **n/a** (not applicable) on all three surfaces, visually and textually distinct from the clean state.
3. **Given** the same run, **When** the `threats.md` matrix, the PDF "MAESTRO Layer Analysis" page, and the `maestro-stack` infographic are compared, **Then** all three show the **identical** clean/n/a/findings state for every one of the 7 layers.
4. **Given** a layer that carries findings, **When** the report renders, **Then** its finding count and highest-severity rendering are unchanged from today (Model B touches only zero-finding rows).

---

### User Story 2 - Machine-discernible coverage for downstream tools (Priority: P1)

A downstream AI-security tool consumes tachi's MAESTRO output as the upstream source-of-truth contract. The clean-vs-n/a distinction is machine-discernible on the surface it parses, so it can represent coverage accurately without guessing applicability — and without any SARIF/schema change breaking its existing parsing.

**Why this priority**: tachi's strategic position is the machine-readable contract AI-security tools consume; the contract is only as strong as its output fidelity. A uniform zero-finding annotation forces an integrator to guess or drop the layer. This story is P1 and small (S) — it falls out of US-1's authored tokens plus a code-computed coverage-state field.

**Independent Test**: Parse the `examples/microservices` `threats.md` Section-6 table and the generated `maestro-stack.json`; confirm clean and n/a layers carry **distinct, documented** values (cell token and `coverage_state` enum), and that the SARIF output for the same run is byte-unchanged versus a Model-A baseline.

**Acceptance Scenarios**:

1. **Given** the `threats.md` MAESTRO matrix, **When** a layer is clean vs n/a, **Then** the two states are represented by **distinct, documented tokens** in the Highest-Severity cell (aligned to the `coverage-matrix-model.md` analyzed-clean / not-applicable semantics).
2. **Given** the generated `maestro-stack.json` infographic data, **When** a layer is clean vs n/a, **Then** each layer carries an explicit, code-computed `coverage_state` value (`findings` | `clean` | `not_applicable`) — not an agent-counted guess.
3. **Given** an existing consumer parsing tachi SARIF, **When** Model B ships, **Then** nothing breaks: the SARIF schema and the emitted results are byte-unchanged (the distinction is a render-layer concern, not a schema change).

---

### User Story 3 - Structural cross-surface consistency (Priority: P2)

A tachi maintainer changes one MAESTRO rendering surface. Cross-surface consistency is **structural** — authored once and inherited — so the three surfaces cannot silently drift apart, and a CI gate proves it on every change.

**Why this priority**: This is the durability mechanism that makes US-1/US-2 trustworthy over time and the reason Model B was carved out of F-315 (to give the fixture room). It protects rather than creates user-visible value, so P2 — but it is the structural guarantee the whole feature rests on.

**Independent Test**: With `examples/microservices` as the gated fixture, run the cross-surface consistency test; confirm it asserts all three surfaces agree on every layer's state and that it fails (naming the layer) if any surface is forced to disagree.

**Acceptance Scenarios**:

1. **Given** the orchestrator authors the per-layer state once into the Section-6 Highest-Severity cell, **When** the PDF and infographic extractors run, **Then** they **inherit** that state (classify the carried token) rather than independently recomputing applicability from the Section-1 component mapping.
2. **Given** the `examples/microservices` fixture (≥4 n/a + ≥1 clean layer), **When** CI runs, **Then** a regression test asserts all three surfaces agree on every layer's state, and fails with the offending layer ID if they do not.
3. **Given** a future refactor that tried to drive the `maestro-stack` state from the Section-1 `component_layer_map` instead of the Section-6 cell, **When** the consistency test runs, **Then** the divergence is caught (the Section-6 carried token is the sole authority for the three in-scope surfaces).

---

### Edge Cases

- **Layer mapped but zero findings (clean)** — e.g. `microservices` L7 (Client Application mapped, 0 findings): MUST render clean, never n/a. This is the discriminating case the feature exists to get right.
- **All 7 layers in scope (no n/a)** — every zero-finding layer stays clean with its existing rendering; the example MUST produce **no spurious diff** (clean string and PDF/infographic bytes unchanged for that example).
- **All 7 layers zero-finding, mixed applicability** — clean and n/a both appear; finding-bearing rendering is absent; most-exposed-layer selection MUST NOT pick a clean or n/a layer.
- **Table-less / partial-input threat model** (no Section-6 table) — the infographic backfill path synthesizes absent layers; backfilled layers default to the **clean** rendering (today's behavior preserved), and an n/a token that *is* present in Section 6 MUST survive the backfill merge unoverwritten.
- **Heading-level variance** (`### ` vs `#### Risk by MAESTRO Layer`) — fixture/example regeneration MUST run the populator's heading normalization so an n/a-bearing example does not silently parse to zero layers (empty PDF page).
- **Unclassified components** — components in Section 1's "Unclassified" row do not map to any L1–L7 layer and therefore do not, by themselves, make a layer in-scope.

---

## Requirements *(mandatory)*

> **Acceptance Criteria Rule**: each AC begins with **Given** and follows Given/When/Then. `[MANUAL-ONLY] <reason>` marks ACs that cannot be automated.

### Functional Requirements — Source / Authoring

- **FR-001** (two-state vocabulary): The `threats.md` MAESTRO Section-6 view MUST distinguish a zero-finding **clean** layer (≥1 mapped component, 0 findings) from a zero-finding **n/a** layer (0 mapped components), reusing the `coverage-matrix-model.md` analyzed-clean / not-applicable **semantics**; it MUST NOT reinvent the vocabulary. Non-zero layers keep their finding count and severity rendering unchanged.
  - **Given** a clean layer, **When** Section 6 is authored, **Then** its Highest-Severity cell carries the documented **clean** token `Analyzed — no findings this scan` (unchanged from Model A; em-dash U+2014, no trailing period).
  - **Given** an n/a layer, **When** Section 6 is authored, **Then** its Highest-Severity cell carries the documented **n/a** token (a new distinct annotation expressing not-applicable — see Key Design Decisions).

- **FR-002** (applicability source = Section-6 carried state): Layer applicability MUST be derived from the component→layer mapping the orchestrator already computes during MAESTRO classification (Phase 1 inventory + layer assignment), and encoded **once** into the layer row's existing Highest-Severity cell at authoring time. No new analysis pass is introduced.
  - **Given** the orchestrator holds the Section-1 component→layer set, **When** it authors Section 6, **Then** a layer is marked n/a iff no Section-1 component carries that layer code, and clean iff ≥1 does and finding count is 0.

- **FR-003** (regeneration tooling parity): `scripts/populate-maestro-coverage.py` MUST author the same two-token logic when it regenerates example `threats.md` tables, remaining **examples-regeneration-only** (it MUST NOT be wired into any command/orchestrator phase). Its heading normalization to `#### Risk by MAESTRO Layer` MUST be preserved.
  - **Given** an example with ≥1 unmapped layer, **When** the populator regenerates its Section-6 table, **Then** unmapped zero-finding layers receive the n/a token, mapped zero-finding layers the clean token, and the heading is normalized to `####`.

### Functional Requirements — Inheritance

- **FR-004** (single applicability authority): The Section-6 carried token MUST be the **sole** applicability authority for the three in-scope surfaces. Both extractors MUST classify that carried token rather than independently re-deriving applicability. `extract-infographic-data.py:parse_component_layer_mapping()` (Section-1-derived) MUST remain **heatmap-only** and MUST NOT be re-routed to drive the `maestro-stack` clean-vs-n/a state.
  - **Given** the carried token in Section 6, **When** either extractor processes a zero-finding layer, **Then** it determines clean-vs-n/a from that token (via the shared classifier, FR-005), never from `component_layer_map`.

- **FR-005** (shared token classifier → `coverage_state` enum): A pure, shared helper in `scripts/tachi_parsers.py` MUST classify `(finding_count, highest_severity_token)` into a `coverage_state` enum of exactly `findings` | `clean` | `not_applicable`. Both extractors MUST call it and emit `coverage_state` per layer into their render data (`report-data.typ` for PDF, `maestro-stack.json` for the infographic). The helper MUST NOT read Section 1 (it classifies the already-authored token; it does not decide applicability).
  - **Given** the shared classifier, **When** both extractors run on the same `threats.md`, **Then** they emit identical `coverage_state` for every layer (one classifier, one result).
  - **Given** the infographic data, **When** generated, **Then** each layer's `coverage_state` is code-computed and deterministic (not agent-derived).

- **FR-006** (n/a token survives backfill): The orchestrator MUST author the n/a token in the Section-6 row itself (never relying on backfill). The infographic backfill (`extract-infographic-data.py`, absent-layer synthesis) MUST default a backfilled (table-less) layer to **clean** rendering, and MUST preserve an n/a token that *is* present in Section 6 — the merge MUST NOT overwrite a present n/a token to empty/clean.
  - **Given** an n/a layer present in the Section-6 table, **When** the infographic backfill merge runs, **Then** the layer's `coverage_state` is `not_applicable` in the output (not overwritten by the backfill default).

### Functional Requirements — Rendering (three surfaces)

- **FR-007** (`threats.md` matrix renders both states): The `threats.md` Section-6 table MUST display clean and n/a as the two distinct documented tokens (FR-001), all 7 layers always present (F-098), canonical L1→L7 order preserved.

- **FR-008** (PDF surface parity + renderer n/a state): The PDF "MAESTRO Layer Analysis" page MUST inherit the per-layer `coverage_state` (via `extract-report-data.py` → `report-data.typ`) AND `templates/tachi/security-report/maestro-findings.typ` MUST branch the zero-finding row on that state, rendering a **distinct n/a visual state** (today it hardcodes only the clean literal at line 154). Inheriting the data is necessary but not sufficient — the Typst template MUST render the third state. [Architect HIGH-1]
  - **Given** a clean layer, **When** the PDF renders, **Then** the row reads `Analyzed — no findings this scan.` (unchanged styling).
  - **Given** an n/a layer, **When** the PDF renders, **Then** the row reads the distinct n/a prose with a visually distinguishable muted treatment (see Key Design Decisions), never the clean string.

- **FR-009** (infographic surface parity + inherit-not-rederive + renderer n/a state): The `maestro-stack` infographic MUST inherit the per-layer state **from the Section-6 carried token** (via `coverage_state`, FR-004/FR-005), and `templates/tachi/infographics/infographic-maestro-stack.md` (prose + Gemini prompt + Accessibility section) MUST add a documented **third band state** so clean is visually and textually distinct from n/a. The Accessibility text-label rule MUST be extended to name the n/a label (today it names only the empty-dash). `maestro-heatmap` is unaffected (out of scope). [Architect HIGH-1]
  - **Given** a clean layer, **When** the infographic renders, **Then** its band is muted with the existing dash treatment.
  - **Given** an n/a layer, **When** the infographic renders, **Then** its band uses the distinct n/a treatment with the documented n/a text label.

### Functional Requirements — Consistency, Fixture, Invariants, ADR

- **FR-010** (structural cross-surface consistency): For any single run, all three surfaces MUST show the identical per-layer state for all 7 layers, as a **structural consequence** of the single carried authority (FR-004) — not three independent applicability computations.

- **FR-011** (≥1-n/a fixture + CI gate): `examples/microservices` (which already yields ≥4 n/a + ≥1 clean layer) MUST be the gated fixture; **no synthetic fixture is authored**. Its expected outputs across all three surfaces MUST be frozen, and a cross-surface consistency assertion MUST be added to the dedicated `.github/workflows/tachi-maestro-coverage.yml` job, in **F-250 lock-step** (the workflow `paths:` list AND the pytest invocation updated in the same commit).
  - **Given** the `microservices` fixture, **When** the consistency test runs in CI, **Then** it asserts every layer's state agrees across the three surfaces and fails (naming the layer) on any forced disagreement.
  - **Given** a new test/author surface is added, **When** committed, **Then** both the workflow `paths:` and the pytest invocation are updated together (no false-green).

- **FR-012** (most-exposed invariant): The n/a token AND the clean token MUST both resolve to severity ordinal **0** in the most-exposed-layer tie-break (`extract-report-data.py:417`, `extract-infographic-data.py:1700`), and `compute_most_exposed_layer` MUST never select a clean or n/a (zero-finding) layer. This MUST be an explicit, tested invariant, not an accident of dict-miss.
  - **Given** an architecture whose only non-zero layers are L2/L4, **When** the most-exposed layer is computed, **Then** it is one of L2/L4 and never a clean/n/a layer; **Given** the n/a token, **When** looked up in `_SEVERITY_ORDINAL`, **Then** it returns 0.

- **FR-013** (ADR-047): A public ADR (**ADR-047**) MUST record the Model B decision, narrowly scoped to the technical decision (no commercial framing): **Section-6 carried token as sole authority + per-consumer inherit via the shared token-classifier** (chosen) vs **add an applicability/token helper to the shared parser that re-derives from Section 1** (option a). Option (b) — duplicating the infographic parser into the report pipeline — is recorded as rejected for divergence risk. The ADR MUST note `tachi_parsers.py` already exists (correcting the stale "build a shared module" framing).

- **FR-014** (constraint — no schema/scoring/taxonomy change): The feature MUST NOT introduce SARIF schema changes or alter the emitted SARIF results, MUST NOT alter risk scoring (zero-finding rows never affected CVSS/composite scores), and MUST NOT change the canonical 7-layer taxonomy (frozen by Feature 136).
  - **Given** a Model-A baseline run, **When** Model B runs on the same input, **Then** the SARIF file is byte-unchanged and no risk score changes.

### Key Entities

- **Coverage state** — the per-layer enum `findings` | `clean` | `not_applicable`, code-computed by the shared classifier from `(finding_count, Highest-Severity token)`. The machine-discernible representation of the distinction; emitted into `report-data.typ` and `maestro-stack.json`.
- **Carried token** — the string in the Section-6 *Highest Severity* cell that is the single authored source of the distinction: a severity label (findings), the clean annotation, or the n/a annotation.
- **Rendering surfaces** — (1) `threats.md` Section-6 matrix (LLM-authored markdown), (2) PDF "MAESTRO Layer Analysis" page (`extract-report-data.py` → `maestro-findings.typ`), (3) `maestro-stack` infographic (`extract-infographic-data.py` → Gemini prompt). All three inherit the same `coverage_state`.
- **Fixture** — `examples/microservices`: the regression anchor (≥4 n/a + ≥1 clean) whose three-surface outputs are frozen and CI-gated.

---

## Key Design Decisions *(resolves PRD Open Questions)*

### Open-Q1 — ADR-047 option (RESOLVED → option c)

**Decision**: The Section-6 carried token is the **sole applicability authority**; both extractors **inherit** it through a *pure* shared token-classifier (`classify_maestro_coverage_state` in `tachi_parsers.py`) that maps the already-authored token to a `coverage_state` enum. The classifier does **not** read Section 1 — it does not decide applicability, it classifies the orchestrator's decision. This avoids a second source of truth (the divergence risk both reviewers flagged) while still centralizing the token→enum mapping in the existing shared module. Rejected: (a) re-derive applicability per consumer from Section 1 (two derivation paths → desync); (b) duplicate the infographic parser into the report pipeline (divergence). Ratified in ADR-047 at `/aod.project-plan`.

### Open-Q2 — concrete n/a visual state per surface (RESOLVED)

| Surface | Findings (>0) | Clean (≥1 mapped, 0 findings) | n/a (0 mapped) |
|---------|---------------|-------------------------------|----------------|
| `threats.md` Section-6 cell | severity label (unchanged) | `Analyzed — no findings this scan` (**unchanged**, no trailing period) | **NEW** distinct annotation: `Not applicable — no components map to this layer` (em-dash U+2014, no trailing period) |
| PDF `maestro-findings.typ` | findings table (unchanged) | `Analyzed — no findings this scan.` muted italic (unchanged) | distinct n/a prose `Not applicable — no components map to this layer.` with a visually separable muted treatment (e.g. lighter tint / "(out of scope)" qualifier) |
| `maestro-stack` infographic | colored band (unchanged) | muted band, grayed text, dash (—) (unchanged) | distinct muted band treatment + documented **"N/A"** text label; Accessibility section extended to name it |

The exact clean token, exact n/a wording per surface, and the precise n/a infographic styling are recorded here as the spec decision; the punctuation convention follows the F-098 precedent (markdown no-period, Typst adds a period — "the only sanctioned cross-format difference"). The two zero-finding tokens MUST be documented in the MAESTRO coverage reference (extend `coverage-matrix-model.md` or its MAESTRO equivalent) per NFR Consumability. Machine-discernibility (US-2) is delivered by these two distinct documented tokens **plus** the code-computed `coverage_state` enum.

> *Note*: the bare-glyph form (`---` clean / `n/a` not-applicable) is the **STRIDE matrix** surface form; the MAESTRO layer view expresses the same semantics in the prose Highest-Severity column (F-098's deliberate choice for the layer view). The spec maps the two so the MAESTRO view never contradicts the STRIDE matrix.

### Open-Q3 — fixture sourcing (RESOLVED, carried from PRD)

`examples/microservices` already yields ≥4 n/a + ≥1 clean layer (Team-Lead-confirmed); no synthetic fixture is authored.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (cross-surface agreement): For every run, the `threats.md` matrix, the PDF page, and the `maestro-stack` infographic show the identical clean/n/a/findings state for all 7 layers — verified by the cross-surface consistency test. **Target: 100% agreement.**
- **SC-002** (both states proven): The `examples/microservices` fixture renders ≥1 layer as n/a AND ≥1 as clean across all three surfaces — verified by a dedicated CI-gated regression test. **Target: fixture passing in CI.**
- **SC-003** (no schema drift): No SARIF schema change and no change to emitted SARIF results (diff-verified); `/aod.analyze` passes with no inconsistencies. **Target: 0 SARIF changes, 0 analyze findings.**
- **SC-004** (determinism preserved): All byte-gated PDF baselines are byte-deterministic after intentional regeneration under `SOURCE_DATE_EPOCH=1700000000`; the backward-compatibility byte-identity test passes; non-gated PDFs refreshed with a `[MANUAL-ONLY]` diff confirming annotation-only churn. **Target: 6/6 gated baselines deterministic.**
- **SC-005** (ambiguity closed): From any single surface alone, a reader can distinguish analyzed-clean from not-applicable for every zero-finding layer — closing F-098 SC-006. **Target: 0 ambiguous zero-finding layers.**

---

## Scope & Boundaries

### In Scope
- Two-state clean-vs-n/a rendering on the `threats.md` MAESTRO Section-6 matrix (FR-001/002/003/007).
- Inheritance via the shared `coverage_state` classifier; single-authority + heatmap fence + backfill survival + ordinal invariant (FR-004/005/006/012).
- PDF and infographic renderer parity with **explicit n/a visual states** (FR-008/009).
- Structural cross-surface consistency + `examples/microservices` fixture + CI gate in F-250 lock-step (FR-010/011).
- Public ADR-047 (FR-013) and the documented two-token vocabulary.
- Deterministic regeneration of the churning example baselines (≥6 examples) as a discrete, diff-reviewed step (SC-004).

### Out of Scope
- ❌ SARIF / schema changes — render-layer concern only.
- ❌ Re-scoring / risk-model changes — zero-finding rows never affected CVSS/composite scores.
- ❌ New MAESTRO layers or taxonomy changes — the canonical 7 are frozen (Feature 136).
- ❌ `maestro-heatmap` infographic — already renders empty cells; uses the Section-1 derivation, not the Section-6 cell.
- ❌ Section 5 STRIDE coverage matrix — already three-state; this feature brings the MAESTRO view to parity, not the reverse.
- ❌ `threat-report.md` per-layer roster — no such roster exists; adding one is net-new structure (Architect-confirmed exclusion at F-098).
- ❌ Crosswalk depth (BLP-05 Waves 2–3, #182–#186) — independent data-layer work.

### Assumptions
- The orchestrator's MAESTRO classification holds enough component→layer information at authoring time to decide applicability per layer (Architect-validated against `orchestrator.md:176–186`).
- The `maestro-stack` infographic renders all 7 layers post-F-315 (delivered v4.40.0).
- `examples/microservices` exhibits a genuine n/a layer set and a genuine clean layer (Team-Lead-confirmed).

### Dependencies
- **F-315** (maestro-stack all-7 infographic) — delivered 2026-06-03 (v4.40.0). Satisfied.
- **F-098** (Model A, all-7 render + zero-finding annotation) — delivered (v4.39.0). Built directly upon.
- **Prior art**: `coverage-matrix-model.md` two-state vocabulary — reuse, do not re-derive.
- **Deliver-time check**: confirm the `v4.40.0` git tag is present locally before deliver (release commits land on `main`; the tag may lag — Team-Lead note).

### Constraints
- **Technical**: three rendering surfaces (one LLM-authored markdown, two Python extractors) must agree — the dominant design constraint, addressed by the single Section-6 carried authority.
- **Determinism**: outputs MUST remain byte-deterministic under `SOURCE_DATE_EPOCH`; n/a-bearing example PDF baselines will legitimately change and MUST be regenerated and re-frozen deliberately, with the diff verified to contain only the intended annotation change; all-in-scope examples MUST show no spurious diff.
- **Process**: ADR-bearing; the decision is #311's to formalize at plan stage. Single feature — do not split (Team-Lead).

---

## Open Questions *(residual — none blocking)*

- [x] **ADR option** — RESOLVED: option (c) carried-token sole authority + inherit (Key Design Decisions / ratified in ADR-047 at `/aod.project-plan`).
- [x] **n/a visual state per surface** — RESOLVED: per-surface tokens/treatments table above. Exact infographic styling tint to be finalized in the Typst/prompt edits at build; the *state and label* are fixed here.
- [x] **Fixture sourcing** — RESOLVED: `examples/microservices` (no synthetic fixture).
- [ ] **Deliver-time** — confirm `v4.40.0` tag present locally before `/aod.deliver` (mechanical; carried to deliver stage).
