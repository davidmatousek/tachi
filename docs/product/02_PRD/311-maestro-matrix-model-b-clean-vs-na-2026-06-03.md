---
prd:
  number: 311
  topic: maestro-matrix-model-b-clean-vs-na
  created: 2026-06-03
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-06-03, status: APPROVED, notes: "Authored via ~aod-define. BLP-05 Wave 1; carved out of F-315 as the ADR-bearing MAESTRO output-fidelity finisher. User value (clean-vs-n/a no longer ambiguous) and scope boundaries (no SARIF/scoring/taxonomy change; crosswalk waves excluded) clear. Folded both reviewers' concerns inline at v1.1."}
  architect_signoff: {agent: architect, date: 2026-06-03, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 1 HIGH / 3 MEDIUM / 2 LOW. Option (c) Section-6-carried-state confirmed against live code (orchestrator owns L1–L7 mapping at authoring time; both extractors share the Section-6 cell). HIGH-1: FR-003/004 understate renderer work — maestro-findings.typ and the maestro-stack prompt hardcode the clean string, so each surface needs a NEW n/a visual state (inherit is necessary-not-sufficient); resolve the visual-state Open-Q before build. MEDIUM: name the Section-6 token sole authority + fence the Section-1 component_layer_map derivation. Confirmed: no SARIF/schema change realistic; ADR-047 correct. Full: .aod/results/architect.md"}
  techlead_signoff: {agent: team-lead, date: 2026-06-03, status: APPROVED_WITH_CONCERNS, notes: "Single Plan→Build→Deliver cycle realistic; do NOT split (three surfaces share one source cell; splitting breaks cross-surface testability). Deps F-315 (v4.40.0) + F-098 (v4.39.0) verified done. MED (Architect-owned): infographic must INHERIT the Section-6 cell, not re-derive from Section-1 mapping, else author-once-inherit fails. LOW: fixture is S not M — examples/microservices/threats.md already yields ≥4 n/a + ≥1 clean layer (Open-Q3 answered, no synthetic fixture). LOW: confirm v4.40.0 git tag present locally before deliver. Full: .aod/results/team-lead.md"}
source:           # Automatically populated from GitHub Issue
  idea_id: 311    # Always equals prd.number (GitHub Issue number)
  story_id: null  # Deprecated — user stories now stored in GitHub Issue body
---

# MAESTRO Matrix Model B: Clean vs. N/A — Product Requirements Document

**Status**: Approved (with concerns — see sign-offs)
**Created**: 2026-06-03
**Author**: product-manager
**Reviewers**: architect, team-lead
**Phase**: BLP-05 — Framework-Mapping Authority & MAESTRO Output Fidelity (Wave 1)
**Priority**: P1

---

## 📋 Executive Summary

### The One-Liner
When a MAESTRO layer shows zero findings, the report should say whether we *looked and found nothing* (clean) or whether *the layer doesn't apply here* (n/a) — never leave the reader guessing.

### Problem Statement
Feature 098 (Model A, shipped v4.39.0) made the MAESTRO coverage view always render all 7 canonical layers, annotating every zero-finding layer uniformly as *"Analyzed — no findings this scan."* That single annotation **conflates two distinct facts**:

- **Clean** — the layer is in scope for the analyzed architecture (≥1 component maps to it) and was analyzed with zero findings. *"We looked and found nothing."*
- **n/a** — no component in the architecture maps to the layer, so it was never in scope. *"We did not look, and that's expected."*

A security engineer reading the report — or a downstream AI-security tool consuming tachi's machine-readable output — cannot today tell coverage (clean) from out-of-scope (n/a). The result is a recurring "we scanned that too, it was just clean" clarification loop, and a weaker machine-readable contract. F-098's own SC-006 explicitly deferred this full distinction to "Model B / P1."

### Proposed Solution
Adopt the **two-state vocabulary already defined for the STRIDE coverage matrix** (`---` for analyzed-clean, `n/a` for not-applicable — see `coverage-matrix-model.md`) and bring it to the MAESTRO 7-layer view across **all three rendering surfaces**:

1. The `threats.md` **MAESTRO layer matrix**
2. The PDF **"MAESTRO Layer Analysis"** page
3. The **`maestro-stack` infographic** (made to render all 7 layers by F-315, v4.40.0)

Applicability is derived from the **component→layer mapping** the orchestrator already computes during MAESTRO classification. Per the Architect-recommended approach (pre-analyzed at F-315's define stage), the orchestrator **encodes the clean-vs-n/a state once** into the layer row's existing *Highest Severity* cell, and both downstream extractors **inherit** it — making cross-surface consistency *structural* rather than three independent re-derivations.

### Success Criteria
- All three surfaces show the **identical per-layer state** for every layer on any given run.
- A **≥1-n/a-layer fixture** exists and is gated in CI, proving both states render and stay consistent.
- **No SARIF/schema change**; `/aod.analyze` passes; the canonical 7-layer taxonomy is untouched.
- From any single surface alone, a reader or tool can distinguish clean from n/a — closing F-098's SC-006 gap.

### Timeline
Single ADR-bearing feature on its own `feat(311)` branch. Target: one Plan→Build→Deliver cycle. No external date dependency (Wave-0 prerequisite F-315 already delivered 2026-06-03).

---

## 🎯 Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](../01_Product_Vision/product-vision.md)

tachi's strategic position is the **upstream, machine-readable contract** that AI-security point tools consume. That contract is only as strong as the *fidelity* of its output. Model B makes a zero-finding MAESTRO layer **unambiguous** — a reader (or a downstream tool) can finally trust "0 findings" as either "covered, clean" or "out of scope," never a guess. This is precision work on the exact differentiator the OSS positioning rests on.

### Initiative Fit — BLP-05 Wave 1
**Reference**: BLP-05 (`_internal/strategy/BLP-05-framework-mapping-and-output-fidelity.md`)

- **Wave 1** (this PRD, #311): MAESTRO Model B clean-vs-n/a — the carved-out output-fidelity *finisher* of the MAESTRO arc.
- **Lineage**: F-098 (Model A, all-7 always render + zero-finding annotation, v4.39.0) → F-315 (maestro-stack all-7 infographic + CI gate, v4.40.0) → **#311 (Model B, this feature)**. Completes the MAESTRO output story end-to-end.
- **Sequencing gate**: Model B's annotation rides on the `maestro-stack` infographic rendering all 7 layers — first made true by **F-315, delivered 2026-06-03 (v4.40.0)**. ✅ Satisfied; Wave 1 is unblocked.
- Waves 2–3 (crosswalk depth, #182–#186) are independent of this feature.

### Roadmap Fit
**Phase**: BLP-05 Wave 1 (P1, ADR-bearing, heavy/cross-pipeline).
**Dependencies**: F-315 (✅ delivered), F-098 (✅ delivered). No downstream feature blocks on #311; it is the terminal node of the MAESTRO output arc.

---

## 🧑‍💼 Target Users & Personas

### Primary Persona: Security Engineer / Threat-Model Consumer
- **Role**: AppSec / AI-security engineer reviewing a tachi report (`threats.md`, the PDF security booklet, or the shared infographic).
- **Goal**: Understand true coverage at a glance — which MAESTRO layers were analyzed-and-clean vs not-applicable.
- **Pain Point**: Today a 0-finding layer is ambiguous; they must ask the report author "did you actually scan L5, or does it just not apply?" — the recurring clarification loop F-098 set out to reduce but only half-closed.
- **Why this matters**: Distinguishing clean from n/a converts "0 findings" from a question into an answer.

### Secondary Persona: Downstream AI-Security Tool / Integrator
- **Role**: An automated consumer parsing tachi's machine-readable output as the upstream source-of-truth contract.
- **Goal**: Represent MAESTRO coverage accurately in its own UI/risk model.
- **Pain Point**: A uniform zero-finding annotation forces the integrator to guess applicability or drop the layer.
- **Why this matters**: A machine-discernible two-state token makes the contract more *consumable* and more *defensible*.

### Tertiary Persona: tachi Maintainer
- **Role**: Engineer extending or regenerating MAESTRO output.
- **Goal**: Keep the three surfaces from silently drifting apart.
- **Why this matters**: The Architect-recommended "author once, inherit" design makes cross-surface consistency *structural*, so a future change to one surface cannot desync the others.

---

## 📖 User Stories

#### US-311.1: Tell clean from n/a in the report
**When** I review a MAESTRO layer analysis and see a layer with 0 findings,
**I want to** know whether that layer was *analyzed-and-clean* or *not-applicable to this architecture*,
**So I can** tell real coverage from out-of-scope without asking the report author.

**Acceptance Criteria**:
- **Given** an architecture where ≥1 component maps to layer L3, **when** L3 has 0 findings, **then** the report renders L3 as **clean** (analyzed, no findings).
- **Given** an architecture where no component maps to layer L7, **when** the report renders, **then** L7 is shown as **n/a** (not applicable).
- **Given** the same run, **when** I compare the `threats.md` matrix, the PDF "MAESTRO Layer Analysis" page, and the `maestro-stack` infographic, **then** all three show the **identical** state for every one of the 7 layers.

**Priority**: P0 (core) · **Effort**: M

#### US-311.2: Machine-discernible coverage for downstream tools
**When** my tool consumes tachi's MAESTRO output as the upstream contract,
**I want** the clean-vs-n/a distinction to be machine-discernible on the surface I parse,
**So I can** represent coverage accurately without guessing applicability.

**Acceptance Criteria**:
- **Given** the `threats.md` MAESTRO matrix, **when** a layer is clean vs n/a, **then** the two states are represented by **distinct, documented tokens** (reusing the `---` / `n/a` vocabulary from `coverage-matrix-model.md`).
- **Given** no SARIF/schema change is in scope, **when** an existing consumer parses tachi SARIF, **then** nothing breaks (the distinction is a render-layer concern, not a schema change).

**Priority**: P0 (core) · **Effort**: S

#### US-311.3: Structural cross-surface consistency
**When** a future change touches one MAESTRO rendering surface,
**I want** cross-surface consistency to be structural (authored once, inherited),
**So I can** trust the three surfaces cannot silently drift apart.

**Acceptance Criteria**:
- **Given** the orchestrator authors the per-layer state once (Section-6-carried-state), **when** the PDF and infographic extractors run, **then** they **inherit** that state rather than independently recomputing applicability.
- **Given** a ≥1-n/a-layer fixture, **when** CI runs, **then** a regression test asserts all three surfaces agree on every layer's state.

**Priority**: P1 · **Effort**: M

---

## ⚙️ Functional Requirements

#### FR-001: Two-state MAESTRO vocabulary (threats.md)
The `threats.md` MAESTRO layer view MUST distinguish a zero-finding **clean** layer (≥1 mapped component, 0 findings) from a zero-finding **n/a** layer (no mapped component). Reuse the count / `---` (clean) / `n/a` semantics already defined in `coverage-matrix-model.md`; do **not** reinvent the vocabulary. Non-zero layers keep their finding count unchanged.

#### FR-002: Applicability source = component→layer mapping (Section-6-carried-state)
Layer applicability MUST be derived from the component→layer mapping the orchestrator already computes during MAESTRO classification (Phase 1 inventory + layer assignment). Per the Architect-recommended ADR option, the orchestrator MUST encode the clean-vs-n/a state directly into the layer row's existing **Highest Severity** cell, so the state is authored exactly once at the source.

#### FR-003: PDF surface parity
The PDF "MAESTRO Layer Analysis" page MUST inherit the per-layer clean-vs-n/a state from the `threats.md` table (via `extract-report-data.py` reading the carried cell), showing states identical to the markdown. Inheriting the data is necessary but **not sufficient**: the Typst template (`maestro-findings.typ`, which today hardcodes the single clean string) MUST add a distinct **n/a visual state** so the third state actually renders. [Architect HIGH-1]

#### FR-004: Infographic surface parity
The `maestro-stack` infographic MUST inherit the per-layer state **from the Section-6 carried cell** — it MUST NOT independently re-derive applicability from the Section-1 `component_layer_map` it computes today, or "author once, inherit" (FR-005) breaks at this surface. (This is the single sharpest divergence point both reviewers flagged.) The maestro-stack Gemini prompt (which currently hardcodes the clean string) MUST add a distinct **n/a visual state**. (`maestro-heatmap` already renders empty cells and is unaffected.)

#### FR-005: Cross-surface consistency (structural)
For any single run, all three surfaces MUST show the identical per-layer state for all 7 layers. This consistency MUST be structural — a consequence of "author once, inherit" (FR-002) — not three independent applicability computations. The **Section-6 carried cell is the single source of authority**; every downstream renderer reads it, and no renderer re-derives applicability independently.

#### FR-006: ≥1-n/a fixture + CI gate
A test fixture architecture with **≥1 n/a layer AND ≥1 clean layer** MUST exist, with expected outputs across all three surfaces, gated in CI. This is the regression anchor that proves both states render and remain consistent (the reason Model B was carved out of F-315). **The existing `examples/microservices/` architecture already yields ≥4 n/a layers + ≥1 clean layer** (Team-Lead-confirmed), so no synthetic fixture is needed — reuse it as the gate. Effort: **S**.

#### FR-007: Public ADR
A public ADR (**ADR-047** — confirmed next available; ADR-046 is latest on disk, ADR-043 reserved for BLP-03) MUST record the Model B decision, narrowly scoped to the technical decision, no commercial framing. The live decision is **Section-6 carried cell as sole authority + inherit** (Architect-recommended) vs. **shared-module re-derivation per consumer**. Note: `scripts/tachi_parsers.py` already exists as a shared module, so the earlier "option (a) build a shared module" framing is stale — the real question is *single-authored-cell* vs *re-derive-per-consumer*. Option (b) — duplicating the infographic parser into the report pipeline — is already rejected for divergence risk.

#### FR-008 (constraint): No schema, scoring, or taxonomy change
The feature MUST NOT introduce SARIF/schema changes, MUST NOT alter risk scoring (zero-finding rows do not affect CVSS or composite scores), and MUST NOT change the canonical 7-layer taxonomy (frozen by Feature 136).

---

## 🚀 Non-Functional Requirements

### Determinism & Backward Compatibility
- Outputs MUST remain byte-deterministic under `SOURCE_DATE_EPOCH` (preserving the F-098/F-315 determinism gates).
- PDF baselines for any gated example whose architecture contains an n/a layer **will legitimately change**; they MUST be regenerated and re-frozen deliberately, with the diff verified to contain **only** the intended clean-vs-n/a annotation change.
- Examples where all 7 layers are in scope (no n/a) MUST render with no spurious diff — every layer simply remains "clean," matching today's "analyzed, no findings" meaning.

### Performance
Negligible: applicability is derived from data the orchestrator already computes; no new analysis pass is introduced.

### Consumability
The two-state tokens MUST be documented (extend the `coverage-matrix-model.md` reference or its MAESTRO equivalent) so downstream consumers can rely on them.

---

## 📊 Success Metrics

- **SC-001 (Cross-surface agreement)**: For every run, the `threats.md` matrix, PDF page, and `maestro-stack` infographic show identical clean-vs-n/a state for all 7 layers — verified by a cross-surface consistency test. **Target: 100% agreement.**
- **SC-002 (Both states proven)**: A ≥1-n/a-layer fixture renders ≥1 layer as `n/a` and ≥1 as clean across all three surfaces — verified by a dedicated CI-gated regression test. **Target: fixture passing.**
- **SC-003 (No schema drift)**: No SARIF/schema change (diff-verified); `/aod.analyze` passes with no inconsistencies. **Target: 0 schema changes, 0 analyze findings.**
- **SC-004 (Determinism preserved)**: All gated PDF baselines are byte-deterministic after intentional regeneration under `SOURCE_DATE_EPOCH`; the backward-compatibility test passes. **Target: 100% deterministic.**
- **SC-005 (Ambiguity closed)**: From any single surface alone, a reader can distinguish "analyzed-clean" from "not-applicable" for every zero-finding layer — closing F-098 SC-006. **Target: 0 ambiguous zero-finding layers.**

---

## 🔍 Scope & Boundaries

### In Scope (P0/P1)
- ✅ Two-state clean-vs-n/a rendering on the `threats.md` MAESTRO layer matrix (FR-001/FR-002).
- ✅ PDF "MAESTRO Layer Analysis" page parity (FR-003).
- ✅ `maestro-stack` infographic parity (FR-004).
- ✅ Structural cross-surface consistency (FR-005).
- ✅ ≥1-n/a-layer fixture + CI gate (FR-006).
- ✅ Public ADR for the Model B decision (FR-007).

### Out of Scope
- ❌ **SARIF / schema changes** — layer counts are already structured; the distinction is a render-layer concern.
- ❌ **Re-scoring / risk-model changes** — zero-finding rows never affected CVSS or composite scores.
- ❌ **New MAESTRO layers or taxonomy changes** — the canonical 7 are frozen (Feature 136).
- ❌ **`maestro-heatmap` infographic** — already renders empty cells; unaffected.
- ❌ **Section 5 STRIDE coverage matrix** — already implements the three-state model; this feature brings the *MAESTRO* view to parity, not the reverse.
- ❌ **`threat-report.md` per-layer roster** — no such roster exists today; adding one is net-new structure, not polish (Architect-confirmed exclusion at F-098).
- ❌ **Crosswalk depth (BLP-05 Waves 2–3, #182–#186)** — independent data-layer work.

### Assumptions
- The orchestrator's MAESTRO classification already has enough component→layer information to decide applicability per layer (to be confirmed at plan stage by inspecting the classification path).
- The `maestro-stack` infographic renders all 7 layers post-F-315 (✅ delivered v4.40.0).
- At least one existing example architecture, or a small synthetic fixture, can exhibit a genuine n/a layer for FR-006.

### Constraints
- **Technical**: Three rendering surfaces (one LLM-authored markdown, two Python extractors) must agree — the dominant design constraint, addressed by Section-6-carried-state.
- **Process**: ADR-bearing; the decision is #311's to formalize at plan stage.

---

## 🛣️ Timeline & Milestones

| Milestone | Owner | Status |
|-----------|-------|--------|
| PRD Approval (this doc) | product-manager | 🟡 In Review |
| Spec + ADR | architect | 📋 Pending (`/aod.plan`) |
| Tasks + assignments | team-lead | 📋 Pending (`/aod.plan`) |
| Build (3 surfaces + fixture) | (assigned at plan) | 📋 Pending |
| Deliver + release | devops | 📋 Pending |

Single feature; no multi-week phasing. Heaviest task is the cross-surface fixture + the three-surface wiring.

---

## ⚠️ Risks & Dependencies

### Technical Risks

**Risk 1 — Cross-surface consistency (the hard one)**
- **Likelihood**: Medium · **Impact**: High
- Three renderers (LLM-authored `threats.md`, PDF extractor, infographic extractor) must agree on every layer's state.
- **Mitigation**: Architect-recommended **Section-6-carried-state** — orchestrator authors the state once into the Highest Severity cell; both extractors inherit it, making consistency structural. **Sharpest divergence point (both reviewers): the `maestro-stack` infographic must inherit the carried cell, NOT re-derive applicability from its own Section-1 `component_layer_map`** — the ADR must lock this. The ≥1-n/a fixture (`examples/microservices/`) is a hard CI gate. (This is precisely why #311 was carved out of #315 — to give it room.)

**Risk 2 — PDF baseline churn**
- **Likelihood**: High (expected) · **Impact**: Low
- Baselines for n/a-bearing examples will change.
- **Mitigation**: Regenerate + re-freeze deliberately under `SOURCE_DATE_EPOCH`; verify the diff contains only the intended annotation change.

**Risk 3 — ADR option not yet formalized**
- **Likelihood**: Low · **Impact**: Medium
- Option (c) is recommended but not yet ratified.
- **Mitigation**: Formalize the ADR at `/aod.plan` (option c Section-6-carried-state vs option a shared parser module; option b — duplicate the infographic parser into the report pipeline — already rejected for divergence risk).

### Dependencies
- **F-315** (maestro-stack all-7 infographic) — ✅ delivered 2026-06-03 (v4.40.0). Satisfied.
- **F-098** (Model A, all-7 render + zero-finding annotation) — ✅ delivered (v4.39.0). This feature builds directly on it.
- **Prior art**: `coverage-matrix-model.md` three-state vocabulary — reuse, do not re-derive.
- **Deliver-time check**: confirm the `v4.40.0` git tag is present locally before #311's deliver (release commits land on `main`; the tag may not be fetched locally yet — Team-Lead note).

```
F-098 (Model A) ──▶ F-315 (infographic all-7) ──▶ #311 (Model B, this PRD)
   ✅ v4.39.0            ✅ v4.40.0                    ◀── terminal node of MAESTRO arc
```

---

## ❓ Open Questions

- [ ] **ADR option** — Confirm Section-6 carried cell as sole authority + inherit (recommended) vs shared-module re-derivation. — *Architect* — at `/aod.plan` — Researching (recommended option staged)
- [ ] **n/a visual state on each surface (resolve BEFORE build)** — Each of the 3 renderers needs a *concrete* third visual state, not just inherited data: the `threats.md` glyph (`---` / `n/a` per `coverage-matrix-model.md`), the Typst `maestro-findings.typ` page (today hardcodes one clean string), and the `maestro-stack` Gemini prompt (same). — *Architect + PM* — gate before build at `/aod.plan` — Open [raised by Architect HIGH-1]
- [x] **Fixture sourcing** — ANSWERED: `examples/microservices/` already yields ≥4 n/a + ≥1 clean layer; reuse it, no synthetic fixture needed. — *Team-Lead* — Resolved

---

## 📚 References

- **Issue**: [#311](https://github.com/davidmatousek/tachi/issues/311) — MAESTRO matrix Model B (this PRD's source; body is primary input)
- **Deferred requirement**: `specs/098-maestro-7-layer/spec.md` FR-011 (Model B deferral) + SC-006
- **Prior art (vocabulary)**: `.claude/skills/tachi-orchestration/references/coverage-matrix-model.md` (three-state model)
- **Render surfaces**: `scripts/extract-report-data.py` (PDF), `scripts/extract-infographic-data.py` (`component_layer_map`), `scripts/populate-maestro-coverage.py` / orchestrator (threats.md)
- **Initiative**: BLP-05 Wave 1 (`_internal/strategy/BLP-05-framework-mapping-and-output-fidelity.md` §5)
- **Carve-out record**: `docs/product/02_PRD/315-maestro-output-completeness-round-2-2026-06-02.md` §Carve-Out

---

## ✅ Approval & Sign-Off

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | ✅ Approved | 2026-06-03 | Authored via ~aod-define; user value + scope boundaries clear |
| Architect | architect | 🟡 Approved with Comments | 2026-06-03 | Option (c) confirmed against live code; FR-003/004 each need a new n/a visual state (HIGH-1); ADR-047 correct. See `.aod/results/architect.md` |
| Engineering Lead | team-lead | 🟡 Approved with Comments | 2026-06-03 | Do NOT split (shared source cell); deps verified; fixture = `examples/microservices` (S, not M). See `.aod/results/team-lead.md` |

Legend: ✅ Approved | 🟡 Approved with Comments | ❌ Rejected | 📋 Pending

---

## 📝 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-03 | product-manager | Initial PRD (BLP-05 Wave 1, #311) |
| 1.1 | 2026-06-03 | product-manager | Folded Architect + Team-Lead review: per-surface n/a visual state (FR-003/004), infographic must inherit the cell not re-derive (FR-004/005), fixture = `examples/microservices` (FR-006), ADR framing fix (FR-007), open-Q updates |
