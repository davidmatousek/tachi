---
prd:
  number: "145"
  topic: maestro-canonical-worked-example
  created: 2026-04-16
  status: Approved
  type: feature
triad:
  pm_signoff: { agent: product-manager, date: 2026-04-16, status: APPROVED, notes: "PRD closes the final teaching-artifact gap in tachi's MAESTRO umbrella — a canonical walkthrough adopters can read before applying tachi to their own systems. Content-authoring only (zero code/schema/agent changes). Dependencies all DELIVERED (Phases 1-5). Domain selection, directory structure, and mmdc CI availability are Wave 0 gates per architect + team-lead reviews — all pre-resolved in PRD Operational Decisions section." }
  architect_signoff: { agent: architect, date: 2026-04-16, status: APPROVED_WITH_CONCERNS, notes: "7 findings (1 BLOCKING addressed inline, 5 MEDIUM, 1 LOW). BLOCKING B1 resolved: FR-1 now explicitly defers Option X (sample-report subdirectory) vs Option Y (flat) to Wave 0 with PRD recommendation Y, correcting the prior factual mischaracterization of a non-existent 'uniform standard structure'. M1 resolved: FR-7 prose rewritten with clean Regime A (baseline) vs Regime B (regeneration target) distinction. M2 flagged: Healthcare (Option A) carries non-trivial content-review burden; Options B/C offered; DoD adds security-analyst disclaimer review if A chosen. M3 resolved: mmdc prerequisite added to Constraints with CI availability gate. M4 resolved: FR-4 adds 4-condition pre-execution architecture review checklist. M5 resolved: FR-8 locks Path B (post-authoring checksum injection) for Feature 120 workflow. L1 resolved: ADR-023 added to References." }
  techlead_signoff: { agent: team-lead, date: 2026-04-16, status: APPROVED_WITH_CONCERNS, notes: "7 findings (0 BLOCKING, 3 MEDIUM, 4 LOW). Timeline expanded from 4-7d to 4-8d (M1) to absorb architecture iteration + domain-lock contingency. M2 resolved: README sections 1/2/5/6/7 marked for parallel drafting with Wave 3 architecture iteration; sections 3/4 gated on pipeline output freeze. M3 resolved: fallback ranking pre-resolved as (a) keyword-tune → (b) extend architecture → (c) relax FR-3 last resort. L1 resolved: Wave 0 ≤2h with EOD Day 1 hard stop. L2 resolved: README budget tightened to 1.5-2d. L3 noted: FR-7 regression integration is subtask-scoped (fold into Wave 6). L4 resolved: DoD enforces structural discipline per FR-1 Wave 0 choice. Dependencies clean — all Phase 1-5 features DELIVERED. Critical-path agent is architect; no capacity concerns." }
source:
  idea_id: 145
  story_id: null
---

# MAESTRO Canonical Worked Example: Multi-Agent Reference Architecture

**Status**: Approved
**Created**: 2026-04-16
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1 (High)
**Evidence**: Canonical CSA MAESTRO documentation uses a multi-agent financial trading system as its primary teaching artifact. Tachi's examples directory has six architectures but none is purpose-built to demonstrate MAESTRO end-to-end with all seven layers and cross-layer attack propagation. ICE: Impact 5, Confidence 8, Effort 7 = 20.

---

## Executive Summary

### The One-Liner
Ship a purpose-built MAESTRO canonical worked example — a multi-agent reference architecture covering all seven MAESTRO layers with explicit cross-layer attack propagation and surfaced agentic patterns — so new adopters have a single canonical artifact to study before applying tachi to their own systems.

### Problem Statement
Tachi now implements the full MAESTRO compliance umbrella: Phase 1 taxonomy overlay (Features 084, 136), Phase 2 cross-layer attack chains (Feature 141), Phase 3 canonical agentic patterns (Feature 142), and Phases 4/5 compliance posture ADRs (Features 143, 144). The pipeline produces layer-tagged findings, cross-layer chain narratives, and pattern-annotated findings with a dedicated Agentic Pattern Analysis section.

However, tachi's `examples/` directory contains no canonical walkthrough that shows all of this capability working together. The closest analogue is `agentic-app`, which was purpose-built as the demo for Features 141 and 142 and now surfaces cross-layer chains and agentic patterns — but it was designed component-by-component under those features' time pressure, not as a canonical teaching artifact. Its architecture clusters around three to four MAESTRO layers, its domain (generic agentic AI helper) is abstract, and its README is a pipeline test scaffold, not an adopter-facing tour.

Canonical CSA MAESTRO uses a multi-agent financial trading system as its worked example. Snyk Labs walks this example through all seven layers with concrete attack scenarios and a final cascading compromise narrative. Practitioners learning MAESTRO read this example first because it makes the abstract framework tangible. Tachi's published examples do not provide an equivalent artifact.

This creates three specific gaps:
- **Teaching gap**: New adopters have no "read this first" artifact showing the full MAESTRO capability before applying tachi to their own system
- **Validation gap**: Phase 2 cross-layer chains and Phase 3 agentic patterns have no canonical demonstration target outside the `agentic-app` regression baseline, which is not adopter-facing
- **Marketing gap**: Tachi cannot point to a published canonical MAESTRO example to counter the "STRIDE tool with MAESTRO sticker" criticism when adopters compare it to the CSA canonical walkthrough

### Proposed Solution
Add a new canonical MAESTRO reference example to `examples/` with a purpose-built multi-agent architecture that:

1. **Spans all seven MAESTRO layers** with at least two components per layer (14+ components minimum)
2. **Uses a non-financial domain** to avoid the appearance of cloning the CSA canonical example verbatim (domain recommendation in FR-2)
3. **Exercises all four structural MAESTRO deliverables** end-to-end: layer tagging (Phase 1), cross-layer attack chains (Phase 2), canonical agentic patterns (Phase 3), and the MAESTRO compliance posture documented in ADR-024 / ADR-025 (Phases 4/5)
4. **Ships with adopter-facing documentation**: a `README.md` in the example directory explaining the domain, why this architecture demonstrates MAESTRO, what each layer contains, what attack scenarios to look for in the output, and how to read the output files — written for adopters, not for regression testing
5. **Is cross-referenced from** the top-level `examples/README.md` as the canonical MAESTRO walkthrough

The example regenerates as a normal part of the pipeline (`/tachi.architecture` → `/tachi.threat-model` → `/tachi.risk-score` → `/tachi.compensating-controls` → `/tachi.infographic all` → `/tachi.security-report`) and commits a deterministic PDF baseline per ADR-021.

This is a **content-authoring feature**. Zero code changes to the pipeline, zero schema changes, zero agent changes. The deliverable is a new example directory with architecture input, generated pipeline output artifacts, and an adopter-facing README.

### Success Criteria
- New example directory committed with `architecture.md` covering all seven MAESTRO layers
- Architecture has at least two components per layer (14+ components total)
- At least one cross-layer attack chain surfaces in the pipeline output spanning three or more layers
- At least three of the six canonical MAESTRO agentic patterns (Agent Collusion, Emergent Behavior, Temporal Attack) surface in findings
- All Phase 4/5 posture ADRs (ADR-024, ADR-025) are referenced in the example README as applicable
- All pipeline outputs committed: `threats.md`, `threats.sarif`, `threat-report.md`, `risk-scores.md`, `risk-scores.sarif`, `compensating-controls.md`, `compensating-controls.sarif`, `attack-trees/`, `attack-chains.md` (if chains surface), infographic JPEGs, `security-report.pdf`, `security-report.pdf.baseline`
- Example `README.md` explains domain, layer coverage, attack scenarios to look for, and how to read the output files — written for adopters
- `examples/README.md` is updated to reference the new example as the canonical MAESTRO walkthrough
- PDF baseline regenerates byte-identical under `SOURCE_DATE_EPOCH=1700000000` (per ADR-021)
- `/aod.analyze` passes with no inconsistencies

### Timeline
Estimated **4-8 days** — focused content-authoring feature with three milestone boundaries (pessimistic bound expanded from 7 to 8 days per team-lead review M1 to absorb architecture iteration + possible domain-lock delay without breaking the schedule commitment):
- **Day 1-2**: Domain selection (≤2h Wave 0 timebox, EOD Day 1 hard stop), architecture design (14+ components across seven layers), architecture.md drafted in chosen input format (Mermaid)
- **Day 3-4**: Pipeline executed end-to-end; outputs reviewed for layer coverage, chain surfacing, and pattern findings; iterate on architecture if coverage gaps emerge (capped at 2 iterations per FR-4 pre-execution checklist)
- **Day 5-7**: README.md authored (adopter-facing tour); `examples/README.md` cross-reference added; PDF baseline committed; regression validation against 5 other example baselines (must remain byte-identical)
- **Day 8 (contingency)**: Absorbs one additional architecture iteration or domain-renegotiation cycle if Risk 145.1 triggers

**Parallelism opportunity**: README sections 1, 2, 5, 6, 7 (domain framing + compliance references — do not reference specific pipeline findings) can be drafted by PM **in parallel with architecture iteration** (Wave 3). README sections 3 (layer coverage table) and 4 (what to look for) are output-specific and must wait for pipeline output freeze. This recovers ~1-2 days of PM work from the critical path.

The two principal schedule risks are (a) domain selection disagreement during review (team-lead / architect may push back on the PRD's recommendation) and (b) architecture iteration when the first draft does not naturally surface at least one cross-layer chain + three agentic patterns. Both are addressed as contingencies in Risks section, with a pre-execution architecture review checklist (FR-4) converting Risk 145.1 from reactive iteration to a design-time guarantee.

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](../01_Product_Vision/product-vision.md)

Tachi's vision is to be the default threat modeling toolkit for teams building agentic AI applications. The canonical MAESTRO worked example is the teaching artifact that translates tachi's implemented capability into adopter comprehension. Without a published canonical walkthrough, new adopters encounter tachi as a collection of capabilities rather than as a cohesive methodology implementation. With one, adopters see the full MAESTRO experience end-to-end before committing to adoption.

This feature directly strengthens tachi's positioning as the canonical MAESTRO toolkit — moving from "implements MAESTRO phases 1-5" (technical truth) to "ships a canonical MAESTRO walkthrough adopters can read on day one" (adopter-facing value).

### Roadmap Fit
This is the capstone teaching artifact for the MAESTRO compliance umbrella. With Phases 1-5 all delivered, the umbrella is structurally complete but is not yet demonstrated as a cohesive adopter experience. This PRD closes that gap.

It is not a new pipeline phase, not a new schema, not a new agent, not a new template. It is a content-authoring deliverable that consumes the existing pipeline.

### Predecessor Relationship
| Feature | Relationship |
|---------|-------------|
| 084 (MAESTRO Layer Mapping) | L1-L7 layer tagging appears in the example output — prerequisite capability |
| 136 (MAESTRO Canonical Layer Correctness) | Canonical L5/L6/L7 names used throughout the example — prerequisite |
| 141 (MAESTRO Cross-Layer Attack Chains) | Cross-layer chain narrative renders in the example's threat report — strong dependency |
| 142 (MAESTRO Agentic Pattern Expansion) | Agentic Pattern Analysis section renders in the example's threat report — strong dependency |
| 143 (MAESTRO AIVSS Evaluation ADR) | Referenced in example README compliance posture section — informational |
| 144 (NIST AI RMF Evaluation ADR) | Referenced in example README compliance posture section — informational |
| 024 (Example Threat Models) | Establishes the examples directory structure and adopter-facing example precedent — convention |
| 024 (Example Threat Models) pattern | The new example follows the existing structure: `architecture.md` + full pipeline output + README — convention |
| 128 (Executive Threat Architecture Infographic) | New `threat-executive-architecture.jpg` surfaces in the example — passive dependency |
| 112 (Attack Path Pages) | Attack tree pages render in the PDF for Critical/High findings — passive dependency |
| 091 (MAESTRO Infographic Templates) | `threat-maestro-stack.jpg` and `threat-maestro-heatmap.jpg` surface in the example — passive dependency |

---

## Target Users & Personas

### Primary Persona: New Tachi Adopter
- **Role**: Security engineer, threat modeler, or developer evaluating tachi for adoption
- **Experience**: Familiar with STRIDE; new to MAESTRO or evaluating its added value
- **Goals**: Understand what tachi produces, evaluate output quality, decide whether to adopt
- **Pain Points**: Tachi's existing examples are either simple baselines (web-app, microservices) or AI-first demos (agentic-app) — neither is a purpose-built MAESTRO teaching artifact; the 100+ finding outputs in `agentic-app/sample-report/` are overwhelming for a first read without curation

**Why This Matters**: The first example an adopter reads shapes their mental model of what tachi is. A dedicated canonical MAESTRO example gives adopters the right first impression — an integrated MAESTRO toolkit with cross-layer chains and agentic pattern analysis — rather than accidentally anchoring on a narrower demo.

### Secondary Persona: Security Engineer Evaluating Tachi Against Alternatives
- **Role**: Security engineer performing a tools evaluation for a multi-agent system
- **Experience**: Intermediate-to-senior; may already use threat modeling tools; familiar with CSA MAESTRO documentation
- **Goals**: Compare tachi output side-by-side with the canonical CSA MAESTRO walkthrough or manual MAESTRO deliverables
- **Pain Points**: No published tachi output mirrors the shape of the CSA canonical walkthrough; evaluators must mentally bridge between tachi's generic examples and the canonical documentation

**Why This Matters**: The evaluator comparing tachi to alternative tools needs a direct comparison target. A canonical worked example provides that target — adopter says "here is my multi-agent system; here is what tachi produces for a comparable multi-agent reference system" rather than "here is a simple web app and a simpler AI demo; extrapolate from those."

### Tertiary Persona: Tachi Maintainer / Regression Contributor
- **Role**: Tachi maintainer adding a new feature that touches MAESTRO output (any future MAESTRO enhancement)
- **Experience**: Familiar with tachi pipeline, schemas, and regression discipline
- **Goals**: Have a stable regression target that exercises the full MAESTRO surface
- **Pain Points**: Current 6 examples cover various input formats and architecture types, but only `agentic-app` exercises the full AI-threat + MAESTRO surface, and it was originally built for Feature 024 purposes and extended ad-hoc for 141 and 142 — not purpose-built as a MAESTRO regression fixture

**Why This Matters**: Future MAESTRO work (schema changes, new pattern additions, new layer semantics) needs a regression target designed for that purpose. The canonical example doubles as a maintainer fixture that surfaces regressions quickly because every MAESTRO feature is exercised by its architecture.

---

## User Stories

### US-1: New Adopter Wants a Canonical MAESTRO First-Read
**When** evaluating tachi for the first time,
**I want** a canonical MAESTRO worked example I can study as my first encounter with the tool,
**So I can** see the full seven-layer architecture in action before applying tachi to my own system.

**Acceptance Criteria**:
- **Given** the examples directory, **when** browsing `examples/README.md`, **then** the canonical MAESTRO example is prominently called out as the recommended first read for MAESTRO users
- **Given** the example's `README.md`, **when** read end-to-end, **then** it explains the domain, the seven layers, where each layer appears in the architecture, and what attack scenarios to look for in the output
- **Given** the example directory, **when** browsing its contents, **then** it contains all standard pipeline outputs (threats.md, SARIF, threat-report.md, attack-trees/, infographics, PDF)

**Priority**: P0 | **Effort**: M

### US-2: Evaluator Wants a Cross-Layer Attack Chain Demonstration
**When** evaluating tachi's MAESTRO depth vs. alternatives,
**I want** a concrete cross-layer attack chain demonstrated in the output,
**So I can** judge whether tachi's MAESTRO support is substantive or superficial before adopting.

**Acceptance Criteria**:
- **Given** the example's generated output, **when** reading `threat-report.md`, **then** the Cross-Layer Attack Chains section (Feature 141) surfaces at least one chain spanning three or more MAESTRO layers
- **Given** the example's `attack-chains.md`, **when** inspected, **then** at least one chain narrative describes a cascading compromise comparable in shape to the CSA canonical walkthrough
- **Given** the example's architecture description, **when** compared with the generated chain output, **then** the chain membership matches the architectural data flow lineage (not a keyword coincidence)

**Priority**: P0 | **Effort**: M

### US-3: Threat Model Consumer Wants Canonical Comparison Surface
**When** reviewing tachi output against canonical MAESTRO documentation (CISO, security team lead, MAESTRO practitioner),
**I want** a multi-agent reference scenario in the examples directory that mirrors the canonical CSA MAESTRO worked example structure,
**So I can** compare tachi output side-by-side with the canonical framework documentation.

**Acceptance Criteria**:
- **Given** the example, **when** compared with the CSA canonical walkthrough, **then** all seven MAESTRO layers have explicit representation in both
- **Given** the example's threat-report.md, **when** reading the Agentic Pattern Analysis section (Feature 142), **then** at least three of the six canonical patterns are populated
- **Given** the example's README, **when** reading it, **then** it explicitly maps architecture components to MAESTRO layers in a table comparable to the CSA mapping table

**Priority**: P0 | **Effort**: M

### US-4: Tachi Maintainer Wants a MAESTRO Regression Fixture
**When** adding a new feature that touches any MAESTRO capability,
**I want** a regression fixture that exercises all seven MAESTRO layers,
**So I can** surface regressions affecting any single layer's classification or output quickly in CI.

**Acceptance Criteria**:
- **Given** the example, **when** the pipeline is run, **then** all seven MAESTRO layers are populated in the MAESTRO Findings section of the threat-report and on the MAESTRO stack / heatmap infographics
- **Given** the example's PDF baseline, **when** regenerated under `SOURCE_DATE_EPOCH=1700000000`, **then** the regeneration is byte-identical (per ADR-021)
- **Given** the example, **when** run against the backward-compatibility test suite, **then** the example is included as a new baseline with zero-diff on subsequent runs with unchanged code

**Priority**: P1 | **Effort**: S

### US-5: Phase 2/3 Implementer Wants a Purpose-Built Validation Target
**When** developing or refactoring Phase 2 cross-layer chain logic or Phase 3 agentic pattern synthesis (or any follow-on MAESTRO phase),
**I want** an example architecture designed specifically to exercise multi-layer chains and multi-pattern findings,
**So I have** a concrete validation target instead of shoehorning existing examples into new capability.

**Acceptance Criteria**:
- **Given** the example, **when** used as a validation target for future MAESTRO work, **then** its architecture naturally exercises cross-layer chains (≥1 chain surfaces) and agentic patterns (≥3 patterns populated) without architectural contortion
- **Given** the example's architecture.md, **when** inspected, **then** component naming, trust boundaries, and data flow descriptions clearly map to expected MAESTRO output categories — the architecture "teaches" what the pipeline will surface
- **Given** future MAESTRO features, **when** implemented, **then** the canonical example is regenerated as part of the feature's Definition of Done (governance precedent)

**Priority**: P1 | **Effort**: S

### US-6: Adopter Wants Compliance Framework Cross-References
**When** reading the canonical MAESTRO example,
**I want** to see how the example maps to AIVSS (ADR-024) and NIST AI RMF (ADR-025) compliance postures,
**So I can** understand tachi's peer-framework awareness without hunting through ADRs.

**Acceptance Criteria**:
- **Given** the example's README, **when** reading the compliance posture section, **then** it summarizes tachi's AIVSS and NIST AI RMF posture per ADR-024 / ADR-025 in 2-3 sentences each with links to the authoritative ADRs
- **Given** the example, **when** the PDF is read, **then** the scope / methodology section surfaces the existing CVSS 3.1 + exploitability + scalability + reachability scoring model (tachi's canonical scoring per ADR-024)
- **Given** the READMEs, **when** read in sequence (`examples/README.md` → example README), **then** the new example is correctly positioned as "canonical MAESTRO walkthrough" separately from the 6 existing examples that serve other purposes (baseline STRIDE, input-format fixtures, prior AI demo)

**Priority**: P1 | **Effort**: S

---

## Functional Requirements

### FR-1: New Example Directory Structure
**Description**: Create a new example directory under `examples/` following the established pattern (architecture.md + generated pipeline outputs + README.md).

**Directory name**: `examples/maestro-reference/` (default recommendation; architect may rename during `/aod.plan` if a clearer name emerges from the domain choice). The name should (a) signal canonical MAESTRO scope, (b) not conflict with any existing example name, and (c) avoid being tied to a specific domain so the example's identity is "MAESTRO reference" rather than "healthcare demo" or similar.

**Directory contents**:
- `architecture.md` — architecture input in Mermaid format (matches agentic-app / mermaid-agentic-app format convention)
- `README.md` — adopter-facing tour (distinct purpose from architecture.md)
- `threats.md` — generated pipeline output
- `threats.sarif` — generated pipeline output
- `threat-report.md` — generated pipeline output
- `risk-scores.md` — generated pipeline output
- `risk-scores.sarif` — generated pipeline output
- `compensating-controls.md` — generated pipeline output
- `compensating-controls.sarif` — generated pipeline output
- `attack-trees/` — directory of per-finding Mermaid attack trees for Critical/High findings
- `attack-chains.md` — cross-layer chain aggregate artifact (Feature 141), conditional on chain surfacing
- Infographic JPEGs: `threat-baseball-card.jpg`, `threat-system-architecture.jpg`, `threat-executive-architecture.jpg`, `threat-risk-funnel.jpg`, `threat-maestro-stack.jpg`, `threat-maestro-heatmap.jpg` (infographic specs co-committed per existing convention)
- `security-report.pdf` — generated PDF report
- `security-report.pdf.baseline` — deterministic PDF baseline per ADR-021 / Feature 128 convention

**Business Rules**:
- The `README.md` is committed alongside generated artifacts (adopter-facing, not regression scaffolding)
- **Directory structure decision is deferred to `/aod.plan` Wave 0** (per Open Questions): the 5 existing non-multi-agent examples (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice) ship a *minimal* artifact set — `architecture.md` (or `input.md` for mermaid-agentic-app) + `threats.md` + `security-report.pdf.baseline`. The only precedent for the full artifact set envisioned here (threats + risk-scores + controls + attack-trees + attack-chains + 6 infographics + full PDF + baseline) is `agentic-app/sample-report/`. There is **no uniform existing convention** for the richer artifact set. Architect must make an explicit call in Wave 0:
  - **Option X** — Mirror agentic-app's `sample-report/` subdirectory: top-level `architecture.md` + `README.md` + `threats.md` + `security-report.pdf.baseline`, full richer artifact set under `maestro-reference/sample-report/`. Preserves the existing informal convention; regression fixture path is `examples/maestro-reference/sample-report/security-report.pdf.baseline`
  - **Option Y** — Commit flat at top-level with all ~20 artifacts under `examples/maestro-reference/` root; update `examples/README.md` to document this as the new canonical structure going forward. `agentic-app` retains its `sample-report/` variant for historical compatibility
- PRD **recommendation**: Option Y (flat at top-level) for adopter-navigation clarity and to establish the canonical structure, but the architect call is binding
- Whichever structure is chosen, the DoD line item (tracked in tasks.md) enforces that the pipeline output lands in the chosen location — no accidental mixed structures

### FR-2: Domain Selection
**Description**: Select the domain the canonical MAESTRO example will model. The domain must satisfy four criteria:
1. **Non-financial** — the CSA canonical example is multi-agent financial trading. Cloning the domain would appear derivative even if the architecture differs
2. **Naturally multi-agent** — the domain must plausibly support 2+ cooperating agents with distinct responsibilities (supervisor + specialist, agent mesh, etc.)
3. **Naturally spans seven MAESTRO layers** — the domain must have foundation models (L1), data pipelines (L2), agent frameworks (L3), deployment substrate (L4), evaluation / observability (L5), security / compliance (L6), and agent ecosystem / user interface (L7) as natural architectural concerns
4. **Non-obviously agentic** — the domain should make a substantive case for agentic threat modeling beyond "chat with multiple LLMs"

**Candidate domains** (three options; architect leads the final choice during `/aod.plan` with PM and team-lead concurrence):

**Option A — Healthcare Clinical Decision Support (Recommended):**
- Multi-agent clinical decision support system: diagnostic agent (differential diagnosis), treatment planner agent (evidence-based treatment options), risk stratification agent (patient cohort comparison), all coordinating through a supervisor orchestrator; L2 data sources include EHR integration, clinical literature embedding index, guideline corpus; L5 observability includes clinical audit log, outcomes tracking, physician override registry; L6 security/compliance includes HIPAA audit trail, role-based access control, consent management; L7 includes physician portal and patient-facing summary generator.
- **Pros**: Rich natural surface for all seven layers; non-financial; multi-agent is genuinely load-bearing; adopters in healthcare-adjacent domains (legal, compliance, HR) can extrapolate easily
- **Cons**: Regulatory detail (HIPAA, FDA considerations) must be accurate enough to be credible but general enough to avoid claiming the example is a real clinical system

**Option B — Autonomous Research Assistant:**
- Multi-agent research system: literature scanner, claim extractor, citation validator, synthesis agent, coordinated by a research director orchestrator; L2 includes academic corpus, web crawl index, prior research vector store; L5 includes citation provenance log, confidence tracking; L6 includes source authorization, license compliance; L7 includes researcher interface and publication formatting agent
- **Pros**: Genuinely agentic (research is naturally multi-step); non-financial; L2 data poisoning is a canonical threat (academic corpus tampering); cross-layer chains are natural
- **Cons**: Domain may feel niche; L6 compliance is less sharp than in healthcare

**Option C — Supply-Chain Optimization:**
- Multi-agent supply-chain optimization: demand forecasting agent, inventory balancing agent, logistics routing agent, risk assessment agent, coordinated by a supply-chain orchestrator; L2 includes ERP integration, supplier data vectors; L5 includes decision audit log; L6 includes vendor compliance tracking; L7 includes supply manager portal
- **Pros**: Clear business domain; genuinely multi-agent; cross-layer chains surface via supplier-risk propagation
- **Cons**: Overlaps thematically with microservices example (B2B operations); less dramatic attack scenarios than healthcare or research

**PRD recommendation**: **Option A (Healthcare Clinical Decision Support)** — richest layer coverage with genuine regulatory surface, adopter-facing relatability across industries, and dramatic cross-layer attack scenarios (L1 foundation model corruption → L2 training data poisoning → L3 workflow hijacking → L5 audit log tampering → L6 policy bypass → L7 false clinical recommendations). Architect makes the final call during `/aod.plan` with PM and team-lead concurrence.

**Business Rules**:
- Whichever domain is chosen, the example must not claim to be a real clinical / research / supply-chain system — disclaimer in README states it is a reference scenario for security teaching purposes only
- The domain choice is locked in `/aod.plan` Wave 0 before architecture drafting begins (changing domains mid-architecture is the highest-cost revision)
- The domain must be documented in the feature spec's research phase output (`specs/145-*/research.md`) with the full trade-off analysis from PM + architect + team-lead review preserved for future reference

### FR-3: Seven-Layer Architecture Coverage
**Description**: The architecture must have explicit representation of all seven MAESTRO layers with at least two components per layer.

**Per-layer minimum coverage** (component type examples, not exhaustive):
- **L1 Foundation Models**: At least two foundation model references (primary LLM, specialized embedding model, or primary LLM + specialized fine-tuned variant)
- **L2 Data Operations**: At least two data pipelines or stores (RAG vector index, fine-tuning pipeline, training data store, document corpus)
- **L3 Agent Frameworks**: At least two agent frameworks or orchestration components (supervisor orchestrator, tool router, agent runtime, delegation protocol)
- **L4 Deployment and Infrastructure**: At least two deployment / infra components (model serving endpoint, container runtime, API gateway, secret store)
- **L5 Evaluation and Observability**: At least two evaluation / observability components (audit log, outcome tracking, anomaly detector, behavior drift monitor) — explicit L5 components are required to exercise Feature 136's corrected L5 name
- **L6 Security and Compliance**: At least two security / compliance components (RBAC, policy engine, consent manager, compliance audit)
- **L7 Agent Ecosystem**: At least two L7 components including at least one inter-agent communication substrate (agent-to-agent channel) and one user-facing component (portal, chat interface) — exercises Feature 136's corrected L7 Agent Ecosystem name

**Business Rules**:
- Total component count ≥14 (2 × 7 layers)
- At least one component must be tagged as agentic (AG dispatch) for Phase 2 (cross-layer chain) and Phase 3 (agentic pattern) content to surface
- At least two agents must cooperate via inter-agent communication (exercises Agent Collusion and Communication Vulnerability patterns)
- At least one component must involve persistent state or long-running learning (exercises Temporal Attack pattern)
- Trust boundaries must cross MAESTRO layer boundaries (e.g., User Zone → Application Zone spanning L4/L7 → L3/L6) to make cross-layer chains plausible

### FR-4: Pipeline Execution and Output Commit
**Description**: Run the full tachi pipeline end-to-end against the new architecture and commit all outputs as the canonical reference.

**Pipeline sequence** (matches `/aod.run` or manual invocation):
1. `/tachi.architecture` — generates / validates the architecture.md (or skip if already authored)
2. `/tachi.threat-model` — generates threats.md, threats.sarif, threat-report.md, attack-trees/, attack-chains.md (if chains surface)
3. `/tachi.risk-score` — generates risk-scores.md, risk-scores.sarif
4. `/tachi.compensating-controls` — generates compensating-controls.md, compensating-controls.sarif
5. `/tachi.infographic all` — generates all 6 infographic JPEGs with specs
6. `/tachi.security-report` — generates security-report.pdf (and baseline under SOURCE_DATE_EPOCH)

**Output quality gates**:
- `threats.md` surfaces findings tagged with ≥6 MAESTRO layers populated (not all seven — some layers may legitimately have zero findings if no Critical/High risk surfaces there, but at least 6/7 is required)
- `threat-report.md` renders:
  - MAESTRO Findings section (Feature 084 / 091) with populated per-layer subsections
  - Cross-Layer Attack Chains section (Feature 141) with ≥1 chain spanning ≥3 layers
  - Agentic Pattern Analysis section (Feature 142) with ≥3 of 6 patterns populated
- `security-report.pdf` renders with all expected pages: cover, disclaimer, TOC, executive summary, executive architecture page (Feature 128), attack path pages (Feature 112) for Critical/High findings, MAESTRO findings page (Feature 091), body sections, infographic pages
- `security-report.pdf.baseline` is byte-identical on re-run under `SOURCE_DATE_EPOCH=1700000000`

**Pre-execution architecture review checklist** (per architect review M4 — converts Risk 145.1 from reactive iteration to design-time guarantee; all four conditions MUST be green before first pipeline invocation):
1. **Multi-agent gate predicate TRUE** — verified by static review of architecture.md: ≥2 components classified as `agentic` or `llm` dispatch category **AND** (inter-agent data flow between two agentic components exists **OR** architecture description contains multi-agent coordination keywords — multi-agent, swarm, supervisor, delegation, agent mesh)
2. **Rule R-01 precondition satisfied** — inter-agent data flow between two agentic components is explicitly present in the Mermaid diagram
3. **Rule R-02 precondition satisfied** — at least one persistent-state component exists (fine-tuning pipeline, agent memory store, learning loop, or long-running training cycle)
4. **Rule R-03 precondition satisfied** — multi-agent topology **AND** at least one agentic component description contains emergent-behavior keywords (cascading, unpredictable, aggregate, coordination, feedback loop)

Source: `.claude/skills/tachi-shared/references/maestro-agentic-patterns-shared.md` Section 4 (authoritative rule table). Verifying conditions 1-4 is a static review of `architecture.md` — no pipeline execution needed. Guarantees ≥3 agentic patterns surface before the pipeline runs, removing the open-ended iteration loop.

**Business Rules**:
- Pipeline runs must be deterministic (ADR-021) — re-running the same architecture on the same codebase commit produces byte-identical output (minus the PDF's standard non-deterministic metadata not covered by SOURCE_DATE_EPOCH — same caveats as existing baselines)
- If the pre-execution checklist fails, the architecture is tuned (components renamed, trust boundaries adjusted, descriptions enriched) until all 4 conditions are green BEFORE first pipeline invocation — this converts Risk 145.1 from reactive iteration to static pre-flight validation
- If any pipeline stage fails or produces unexpected output after checklist is green, architecture is iterated; iteration is capped at 2 rounds (per team-lead review M3 fallback ranking); see Risk 145.1 for escalation path
- Fallback ranking (team-lead review M3, pre-resolved): (a) **keyword-tune** component names / descriptions to match detection keywords → (b) **extend architecture** with 2-3 additional multi-agent components → (c) **relax FR-3 coverage expectation** to 6/7 layers as last resort (not first option)

### FR-5: Adopter-Facing README.md
**Description**: A `README.md` in the example directory explaining the example in adopter-facing terms (distinct from architecture.md which is pipeline input).

**Required sections**:

1. **Introduction** (~100-150 words): What this example is, why it exists as the canonical MAESTRO walkthrough, what the adopter should expect to take away from reading it
2. **Domain overview** (~150-200 words): What the reference scenario models (healthcare / research / supply-chain per FR-2), its components at a glance, disclaimer that it is a security reference scenario not a real system
3. **MAESTRO layer coverage table**: Two-column table mapping architecture components to MAESTRO layers (L1-L7), enumerating at least the 14+ components
4. **What to look for in the output**: Pointers to specific sections and findings in the output files that demonstrate canonical MAESTRO deliverables:
   - Layer-tagged findings in threats.md Section 7 (Feature 084)
   - Cross-layer attack chain narrative in threat-report.md Section 6 (Feature 141) with the specific chain title
   - Agentic Pattern Analysis subsections in threat-report.md (Feature 142) with the specific patterns populated
   - MAESTRO infographic images (threat-maestro-stack.jpg, threat-maestro-heatmap.jpg)
5. **Reading order recommendation**: "If you have 5 minutes, read X. If you have 15 minutes, read X + Y. If you have an hour, read the full PDF." — curation for adopters with varying time budgets
6. **Compliance posture cross-references**: Short (~100-150 words) summarizing tachi's AIVSS (ADR-024) and NIST AI RMF (ADR-025) posture with links to the authoritative ADRs
7. **Limitations and scope**: What this example does not demonstrate (e.g., custom risk weights, organization-specific controls, real-world constraint data)

**Business Rules**:
- README is adopter-facing — written for someone who has never used tachi, not for tachi maintainers
- README is committed alongside generated artifacts as the primary entry point for the example
- README is not regenerated by the pipeline — it is hand-authored and maintained as part of the example

### FR-6: Examples Directory Cross-Reference
**Description**: Update `examples/README.md` to position the new example as the canonical MAESTRO walkthrough.

**Changes to `examples/README.md`**:
- New row in the "Standardized Examples" table (or equivalent table) for the canonical MAESTRO example with "Canonical MAESTRO walkthrough" in the Key Demonstration column
- New subsection or callout (prominent, near the top of the README) directing first-time adopters to the canonical MAESTRO example as the recommended first read
- Existing 6 examples retain their listings — the new example is added, not a replacement

**Business Rules**:
- `examples/README.md` is the adopter's first hop after the top-level repo README — the canonical MAESTRO cross-reference here is the primary funnel
- The existing `agentic-app` example retains its position in the table — it continues to serve as the Feature 141/142 regression baseline and the primary AI+dual-dispatch demo. The canonical MAESTRO example does not replace it; they serve different purposes
- If the new example demonstrates layer / chain / pattern capability more completely than agentic-app, agentic-app's Key Demonstration text may be tightened to distinguish the two (e.g., "STRIDE + AI findings with dual-dispatch" vs. canonical MAESTRO's "seven-layer coverage with cross-layer chains")

### FR-7: Regression Suite Integration
**Description**: Integrate the new example as a regression baseline in the backward-compatibility test suite.

**Changes**:
- Add `examples/maestro-reference/security-report.pdf.baseline` (or `examples/maestro-reference/sample-report/security-report.pdf.baseline` if FR-1 Option X is chosen) to the regression fixture list in `tests/scripts/test_backward_compatibility.py`
- The regression test verifies byte-identical PDF regeneration under `SOURCE_DATE_EPOCH=1700000000` (per ADR-021)
- The canonical MAESTRO example joins the 5 existing non-multi-agent baselines (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice) as a new **6th baseline** enforced by `test_backward_compatibility.py`

**Conventions clarified** (per architect review M1 — two regimes must not be conflated):
- **Regime A — Baseline** (byte-identity-enforced): 5 existing examples. The canonical MAESTRO example joins as the 6th.
- **Regime B — Regeneration target** (excluded from backward-compat suite entirely): `agentic-app` only, per Feature 128 convention and Features 141/142 precedent. `agentic-app` has **no `.baseline` file** and is not "excluded as a baseline" — it is excluded from the suite's fixture list deliberately
- The canonical MAESTRO example adopts Regime A (baseline); `agentic-app` retains Regime B (regeneration target); the two conventions coexist unchanged by this feature

**Business Rules**:
- The canonical MAESTRO example is a regression baseline, not a regeneration target — future features must preserve its byte-identical output unless they explicitly declare it a regeneration target (same governance as the other 5 baselines)
- `agentic-app` convention (Regime B) is NOT modified as part of this feature — continuity with Features 141/142 precedent

### FR-8: Architecture Version Tracking
**Description**: Use the `/tachi.architecture` version tracking mechanism (Feature 120) to mark the example's architecture.md as v1.0 on initial commit.

**Changes**:
- `architecture.md` includes YAML frontmatter per Feature 120 convention: `version: "1.0"`, `date: 2026-04-YY`, `description: ...`, `checksum: sha256:...`
- No archive directory is committed on initial commit (archive exists only if the architecture is later updated)

**Workflow path** (per architect review M5 — specify command invocation sequence for hand-authored Mermaid):
- **Chosen path: Path B (post-authoring checksum injection)** — Hand-author the complete architecture.md body (Mermaid flowchart + Component Summary + Expected Dispatch Behavior sections) during Wave 1, iterate during Wave 3 pipeline tuning WITHOUT committing frontmatter. Once the architecture is frozen (all 4 pre-execution checklist conditions green + pipeline output meets FR-4 gates), invoke `/tachi.architecture` in "create" mode to compute SHA-256 checksum via `shasum -a 256` on the body and inject frontmatter. Commit frontmatter + body together as the v1.0 initial commit.
- Path A (frontmatter-first scaffolding then body replacement) is rejected — `/tachi.architecture` re-invocation may overwrite or question hand-authored content during iteration.

**Business Rules**:
- **Frontmatter is injected as the final step before commit**, NOT during iteration; iteration drafts do NOT commit frontmatter
- If the architecture is iterated during the feature's execution (architecture tuning loop per FR-4), intermediate versions are NOT committed — only the final accepted architecture is committed as v1.0
- Since this is a NEW architecture (no prior version exists), no `.archive/v0/` entry is created on initial commit — Feature 120's legacy-file-to-v0 archival applies only to existing files without frontmatter being updated via `/tachi.architecture`, which does not apply here
- Future updates to the canonical MAESTRO example's architecture follow the standard `/tachi.architecture` update flow with v1.0 archived to `examples/maestro-reference/.archive/v1/architecture.md`

---

## Non-Functional Requirements

### Backward Compatibility
- **The 5 existing non-multi-agent baselines remain byte-identical** under `SOURCE_DATE_EPOCH=1700000000` — the new example is additive, not a rewrite of existing artifacts
- **The agentic-app example is not modified** — it retains its current shape, generated output, and regeneration convention
- **The `examples/README.md` changes are additive** — new row in the table, new first-read callout, no existing rows deleted

### Determinism
- Pipeline regeneration of the canonical MAESTRO example is byte-identical on repeat runs under `SOURCE_DATE_EPOCH=1700000000` (ADR-021)
- Architecture authorship is deterministic in the sense that, given the same architecture input, pipeline outputs are deterministic — but architecture authorship itself is a creative content-writing activity (not a deterministic computation), and iteration is expected during the authoring loop

### Content Quality
- README is adopter-readable — clear prose, no unexplained acronyms, explicit tachi-specific terms (STRIDE, MAESTRO, dispatch) defined inline or cross-referenced
- Architecture.md is pipeline-readable — passes `/tachi.architecture` validation with no warnings; component names include expected dispatch keywords (per Feature 084/136/142 canonical pattern recognition rules)
- Attack chain narrative and agentic pattern subsections surfacing in the generated threat-report are substantive (not filler) — reflects real cross-layer attack propagation plausible in the chosen domain

### Maintainability
- The canonical MAESTRO example joins the regression fixture list — future MAESTRO schema or pipeline changes regenerate it alongside the other baselines
- The example is owned at the feature level — maintenance burden is shared across all future MAESTRO work per existing convention (Features 084, 091, 104, 136, 141, 142 precedent for the other examples)
- README cross-references (ADR-024, ADR-025, Features 141/142/084/136) are stable — they link to canonical sources that do not rot quickly

### Performance
- Pipeline run against the new example completes in time comparable to the agentic-app example (existing production fixture)
- PDF generation time remains within the existing budget
- Infographic generation adds normal per-image Gemini API calls for JPEG generation — one-time cost, not ongoing

---

## Success Metrics

### Primary Metrics

**Canonical MAESTRO Walkthrough Coverage**:
- **Definition**: Percentage of MAESTRO deliverables (seven layers, cross-layer chains, agentic patterns, compliance posture, infographics) visible in the example's committed output
- **Target**: 100% — all five deliverables surface in the committed artifacts

**Adopter First-Read Completion Rate** (proxy metric):
- **Definition**: Percentage of external visitors who land on `examples/README.md` and follow through to `examples/maestro-reference/README.md` (proxied via GitHub traffic analytics if available, otherwise not measured)
- **Target**: Not measured quantitatively; qualitative adopter feedback on the first-read experience is the proxy signal

**Regression Fixture Health**:
- **Definition**: PDF baseline byte-identity on repeat regeneration under `SOURCE_DATE_EPOCH=1700000000`
- **Target**: 100% byte-identical (hard requirement — if broken, the regression suite is broken)

### Adoption Indicators
- External adopters cite the canonical MAESTRO example in security reviews, blog posts, or comparison writeups
- Tachi issue tracker shows comparison questions framed against the canonical example ("how does my architecture compare to maestro-reference?")
- Future MAESTRO features cite the canonical example as a validation target in their PRD reference sections

---

## Scope & Boundaries

### In Scope (P0 — This PRD)
- New example directory `examples/maestro-reference/` (or architect-approved alternative name) with architecture.md + adopter-facing README.md (FR-1, FR-5)
- Domain selection during `/aod.plan` Wave 0 (FR-2) with architect leading the call from three candidate options (healthcare / research / supply-chain)
- Seven-layer architecture design with ≥2 components per layer and ≥14 total components (FR-3)
- Full pipeline execution committing all standard outputs (FR-4)
- Cross-reference from `examples/README.md` (FR-6)
- Regression fixture integration (FR-7)
- Architecture version tracking v1.0 (FR-8)
- PDF baseline committed and byte-identical under SOURCE_DATE_EPOCH=1700000000 (FR-4, FR-7)

### Should Have (P1)
- **Top-level repo README cross-reference**: A one-line mention in the top-level `README.md` pointing adopters at the canonical MAESTRO example under the "Quickstart" or "Examples" section, if such a section exists
- **Diagram thumbnails in the example README**: Embedded preview images of the infographic JPEGs in the README rather than only file links, improving the adopter's first-read experience
- **Comparative table with CSA canonical**: A table in the example README showing how components / layers / attack scenarios in the tachi example correspond to the CSA canonical financial trading walkthrough (to provide explicit comparison anchor for MAESTRO-familiar adopters)

### Out of Scope
- **No new pipeline phases or agents** — this is purely content authoring consuming the existing pipeline
- **No schema changes** — the canonical MAESTRO example uses the existing schema (finding v1.4, attack-chain v1.0, infographic v1.x) unchanged
- **No template changes** — existing Typst templates, infographic templates, and output schemas are unchanged
- **No new ADRs** — the compliance posture ADRs (ADR-024, ADR-025) and MAESTRO ADRs (ADR-020, ADR-026) already exist; this feature references them but does not author new ADRs
- **No regeneration of other examples** — the 5 non-multi-agent baselines remain byte-identical; agentic-app is unchanged unless incidentally
- **No scripting of the example regeneration** — the example is regenerated manually via the existing pipeline invocation (no new CI job, no new `make` target specific to this example)
- **Replacement of agentic-app** — agentic-app continues to serve as the Features 141/142 demonstration baseline; the canonical MAESTRO example is an addition, not a replacement
- **Custom per-adopter reference architectures** — adopters still bring their own architectures; this example is a reference, not a template library
- **Architecture template that adopters copy** — adopters can copy and modify, but this feature does not ship a dedicated "copy this" template beyond the existing Usage Instructions in `examples/README.md`

### Assumptions
- Phases 1 / 2 / 3 of the MAESTRO umbrella (Features 084 / 136 / 141 / 142) are merged and stable — the canonical example demonstrates their combined capability
- The chosen domain is plausible enough to produce substantive threat model output without being so specific that adopters distrust its reference value
- The existing pipeline produces deterministic output for the new architecture per ADR-021 (no new determinism work)
- Architect + team-lead + PM concur on the domain during `/aod.plan` Wave 0 (if concurrence fails, fallback Option A-then-B-then-C ranking is used per PRD recommendation)

### Constraints

**Technical Constraints**:
- Architecture must be expressible in Mermaid format (matches agentic-app / mermaid-agentic-app; the other format options — ASCII and free-text — are retained for fixture coverage but less suitable for a complex 14+ component architecture)
- PDF baseline must be byte-identical per ADR-021 — if a domain choice introduces non-deterministic output (e.g., timestamps in generated narrative), that domain is rejected
- `/tachi.architecture` validation must pass on the authored architecture.md (no validation warnings committed)
- **`@mermaid-js/mermaid-cli` (mmdc) prerequisite** (per Feature 130 / ADR-022 hard-prerequisite posture): The canonical MAESTRO example WILL produce Critical/High findings (14+ components with multi-agent topology guarantees this per FR-3), which invokes mmdc for attack tree rendering. Implications:
  - Local developer environment must have mmdc installed (`npm install -g @mermaid-js/mermaid-cli`) to regenerate the example
  - **CI environment running `tests/scripts/test_backward_compatibility.py` MUST have mmdc available** — current `.github/workflows/tachi-mmdc-preflight.yml` tests mmdc *absence* specifically (asserts pipeline fails loudly); the backward-compat test CI job is a separate workflow and must be verified to have mmdc present, or provisioned to have it added, before FR-7 integration lands
  - If CI provisioning blocks FR-7 integration, FR-7 is deferred to a follow-up task per Risk 145.3 contingency (canonical example still ships as an adopter-facing artifact; regression fixture integration follows in a subsequent PR once CI is updated)

**Content Constraints**:
- Domain must not claim or imply that the reference scenario is a real production system
- Regulatory / compliance framing (HIPAA in Option A, data licensing in Option B) must be plausible but not prescriptive — adopters should not infer regulatory advice from the example

**External Dependencies**:
- No new runtime dependencies (zero-dependency runtime constraint preserved)
- No new external API calls beyond the existing Gemini infographic pipeline

---

## Risks & Dependencies

### Technical Risks

**Risk 145.1**: Architecture draft does not naturally surface at least one cross-layer chain + three agentic patterns
- **Likelihood**: Medium (output surfacing depends on pattern-detection heuristics matching architecture component names / descriptions)
- **Impact**: Medium (if initial draft produces insufficient MAESTRO content, Phase 2/3 demonstrations are weak)
- **Mitigation**: Architecture is iterated (components renamed, trust boundaries adjusted, descriptions enriched) until output matches FR-3 and FR-4 expectations — this is the normal authoring loop. PRD timeline includes 1-2 days for iteration. Feature 142 delivery precedent (agentic-app architecture extension) confirms this is tractable in the budget.
- **Contingency**: If output gaps persist after 2 days of iteration, architect + team-lead meet to decide whether to adjust domain choice or relax FR-3 coverage expectation (explicitly documented in spec).

**Risk 145.2**: Domain selection disagreement during `/aod.plan` Wave 0
- **Likelihood**: Medium (three distinct candidate domains; reviewers may have strong preferences)
- **Impact**: Low-Medium (disagreement delays architecture work but does not block the feature)
- **Mitigation**: PRD provides explicit recommendation (Option A Healthcare) with stated reasoning; ranked fallback order (A > B > C) resolves disagreement if preference is not overwhelming; decision is locked in Wave 0 with PM / architect / team-lead concurrence
- **Contingency**: If Wave 0 ends without consensus after ≤2h, team-lead escalates to user for tiebreak (not a blocker — tiebreak returns same-day)

**Risk 145.3**: PDF baseline regeneration is non-byte-identical due to subtle architecture difference
- **Likelihood**: Low (existing pipeline is deterministic per ADR-021; 5 existing baselines validate this)
- **Impact**: High (breaks regression suite if integration fails)
- **Mitigation**: Follow existing baseline creation procedure exactly (same SOURCE_DATE_EPOCH, same pipeline invocation order); validate baseline regeneration twice before committing
- **Contingency**: If byte-identity cannot be achieved, defer baseline integration to a follow-up task (FR-7 becomes P1 instead of P0); canonical example still ships without regression fixture status temporarily

**Risk 145.4**: Example README prose reads as marketing rather than teaching
- **Likelihood**: Medium (canonical walkthroughs have a natural tendency toward promotional framing)
- **Impact**: Medium (adopters lose trust in tachi's technical depth if the README overclaims)
- **Mitigation**: README follows the existing `examples/README.md` tone — neutral, factual, matter-of-fact about what the example demonstrates and what it does not; PM reviews the README draft for tone before final commit
- **Contingency**: If README tone is flagged during review, rewrite is a low-cost iteration (≤0.5 day)

**Risk 145.5**: Domain choice introduces real-world sensitivity (e.g., Healthcare PHI implications)
- **Likelihood**: Low (reference scenario is clearly marked as fictional; no real patient data)
- **Impact**: Medium-High (if adopters or third parties perceive the example as making healthcare claims)
- **Mitigation**: Disclaimer prominently in README — "This is a security reference scenario for threat modeling teaching; it is not a real clinical system and does not model real patient data, real clinical workflows, or regulatory requirements beyond what is needed for the threat model walkthrough"; avoid PHI-looking names in data flows (use "Patient Record" not specific patient names; avoid medical specialty names that imply clinical accuracy)
- **Contingency**: If any reviewer flags content as too realistic or too specific, iterate to more abstract naming before commit

**Risk 145.6**: Canonical example inadvertently displaces agentic-app in adopters' mental model
- **Likelihood**: Low (explicit positioning in `examples/README.md` distinguishes the two)
- **Impact**: Low (agentic-app retains its role as the Feature 141/142 regression baseline regardless)
- **Mitigation**: `examples/README.md` explicitly names the two examples' distinct purposes — canonical MAESTRO walkthrough vs. dual-dispatch demonstration baseline
- **Contingency**: If adopter confusion surfaces post-ship, tighten the positioning prose in a documentation follow-up (low-cost)

### Dependencies

**Internal Dependencies**:
- **Feature 084** (MAESTRO Layer Mapping): L1-L7 layer tagging — DELIVERED
- **Feature 136** (MAESTRO Canonical Layer Correctness): Canonical layer names (L5/L6/L7) — DELIVERED
- **Feature 141** (Cross-Layer Attack Chains): Phase 2 cross-layer chain rendering — DELIVERED
- **Feature 142** (Agentic Pattern Expansion): Phase 3 agentic pattern categorization — DELIVERED
- **Feature 143** (AIVSS Evaluation ADR): Compliance posture reference — DELIVERED
- **Feature 144** (NIST AI RMF Evaluation ADR): Compliance posture reference — DELIVERED
- **Feature 091** (MAESTRO Infographics): maestro-stack and maestro-heatmap infographics — DELIVERED
- **Feature 128** (Executive Threat Architecture Infographic): threat-executive-architecture.jpg surfaces — DELIVERED
- **Feature 112** (Attack Path Pages): PDF attack tree pages for Critical/High findings — DELIVERED
- **Feature 104** (Downstream Baseline Propagation): Baseline columns in output (even though this example has no prior baseline) — DELIVERED
- **Feature 120** (Architecture Lifecycle Command): Architecture version frontmatter v1.0 — DELIVERED
- **Feature 121** (Tachi Commands Namespace): `/tachi.architecture`, `/tachi.threat-model`, etc. — DELIVERED
- **Feature 129** (Attack Tree Delta Sub-Agent): Per-finding attack trees — DELIVERED

**External Dependencies**:
- Gemini API for infographic JPEG generation (existing dependency; no new calls beyond infographic pipeline)
- `@mermaid-js/mermaid-cli` (mmdc) for attack tree and chain PNG rendering (Feature 130 hard prerequisite when attack trees present)
- Typst compiler for PDF generation (existing prerequisite)

**Dependency Graph**:
```
[Canonical MAESTRO Example (145)]
  +-- Depends on: All Phase 1-5 MAESTRO features (DELIVERED)
  +-- Depends on: Full pipeline (architecture → threat-model → risk-score → controls → infographic → report)
  +-- Dependency-free at the code level (no new code, no new schemas)
  +-- Downstream: Future MAESTRO feature regressions regenerate this example
```

---

## Definition of Done

- [ ] New example directory committed at `examples/maestro-reference/` (or architect-approved alternative name) with:
  - [ ] `architecture.md` — Mermaid format, all seven MAESTRO layers represented, ≥14 components, Feature 120 v1.0 frontmatter
  - [ ] `README.md` — adopter-facing tour per FR-5 required sections
  - [ ] `threats.md` + `threats.sarif` — generated, ≥6 of 7 MAESTRO layers populated
  - [ ] `threat-report.md` — generated, includes MAESTRO Findings section, Cross-Layer Attack Chains section (≥1 chain spanning ≥3 layers), Agentic Pattern Analysis section (≥3 of 6 patterns populated)
  - [ ] `risk-scores.md` + `risk-scores.sarif`
  - [ ] `compensating-controls.md` + `compensating-controls.sarif`
  - [ ] `attack-trees/` directory with Mermaid attack trees for all Critical and High findings
  - [ ] `attack-chains.md` (if ≥1 chain surfaces)
  - [ ] All 6 infographic JPEGs with co-committed specs (baseball-card, system-architecture, executive-architecture, risk-funnel, maestro-stack, maestro-heatmap)
  - [ ] `security-report.pdf`
  - [ ] `security-report.pdf.baseline` (byte-identical under SOURCE_DATE_EPOCH=1700000000)
- [ ] `examples/README.md` updated with cross-reference to the canonical MAESTRO example as recommended first read
- [ ] Regression test suite updated: `tests/scripts/test_backward_compatibility.py` includes the new baseline
- [ ] PDF baseline byte-identical on repeat regeneration under `SOURCE_DATE_EPOCH=1700000000`
- [ ] 5 existing non-multi-agent baselines (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice) remain byte-identical (backward-compatibility invariant preserved)
- [ ] agentic-app example unchanged (not modified as part of this feature)
- [ ] Domain selection documented in `specs/145-*/research.md` with PM + architect + team-lead concurrence record
- [ ] README reviewed by PM for adopter-readability and neutral tone
- [ ] Compliance posture section in README references ADR-024 and ADR-025 with accurate summary
- [ ] `/aod.analyze` passes with no cross-artifact inconsistencies
- [ ] All pipeline outputs regenerate cleanly without manual post-processing
- [ ] **Structural discipline**: Pipeline output lands in the chosen location per FR-1 Wave 0 decision (Option X subdirectory OR Option Y flat); no accidental mixed structure (e.g., no stray `sample-report/` subdirectory if Option Y is chosen)
- [ ] **Pre-execution architecture checklist** (FR-4): 4 conditions verified green before first pipeline invocation, recorded in `specs/145-*/research.md`
- [ ] **Feature 120 workflow**: Architecture.md frontmatter + SHA-256 checksum injected as final step via `/tachi.architecture` create mode (Path B per FR-8); no intermediate frontmatter commits during iteration
- [ ] **Domain-specific disclaimer review**: If Healthcare domain (Option A) is chosen, security-analyst reviews README disclaimer prose for content-risk framing (per architect review M2)
- [ ] **mmdc CI availability** (FR-7 gate): CI environment running `test_backward_compatibility.py` has `@mermaid-js/mermaid-cli` installed; OR FR-7 deferred to follow-up task per Risk 145.3 contingency

---

## Open Questions

### Product Questions
- [ ] Should the canonical MAESTRO example replace `agentic-app` in the "Standardized Examples" table of `examples/README.md` as the primary AI demonstration, with agentic-app demoted to format-specific fixtures? — product-manager — 2026-04-23 — Open (PRD leans toward **no** — they serve distinct purposes; agentic-app remains the dual-dispatch + regression demonstration while canonical MAESTRO is the adopter walkthrough)
- [ ] Should the P1 "top-level repo README cross-reference" be promoted to P0 if the canonical MAESTRO example is intended to be the headline marketing artifact? — product-manager — 2026-04-23 — Open
- [ ] Should the example README include a pre-baked "adopter comparison table" against the CSA canonical financial trading walkthrough (P1 Should Have), or is that overscope for the first ship? — product-manager — 2026-04-23 — Open

### Technical Questions (deferred to `/aod.plan`)
- [ ] **Directory structure — Option X (`sample-report/` subdirectory per agentic-app) vs Option Y (flat at top-level)** (architect review B1)? PRD recommendation: Option Y. Architect makes the final call in Wave 0; decision must be reconciled with FR-1 prose and FR-7 regression fixture path before spec is frozen. — architect — `/aod.plan` Wave 0 — Open
- [ ] Which of the three FR-2 domain options (A Healthcare / B Research Assistant / C Supply-Chain) should be selected? PRD recommendation is Option A; architect review M2 flagged that Options B and C carry materially lower content-review overhead for equivalent MAESTRO demonstration strength. If Option A is retained, README disclaimer (FR-5 section 2) must pass a security-analyst review for content-risk framing (add to DoD). Architect makes the final call in Wave 0 with PM + team-lead concurrence. — architect — `/aod.plan` Wave 0 — Open
- [ ] What is the final directory name? PRD default is `examples/maestro-reference/`. Architect may rename if a better name emerges from the domain choice (e.g., `examples/canonical-maestro/` or domain-anchored like `examples/clinical-ai-reference/`). — architect — `/aod.plan` Wave 0 — Open
- [ ] Should CI for `test_backward_compatibility.py` have mmdc provisioned, or should FR-7 integration be deferred to a follow-up task until CI is updated? (architect review M3) — architect + team-lead — `/aod.plan` Wave 0 — Open (Recommendation: verify mmdc CI availability before FR-7 commit; defer to follow-up if not available.)
- [ ] Should the PDF baseline use `SOURCE_DATE_EPOCH=1700000000` (matching all other baselines) or a different deterministic timestamp? Recommendation: use the same value for consistency. — architect — `/aod.plan` — Open (low-risk; recommendation acceptable)
- [ ] Should the canonical MAESTRO example be regenerated on every future MAESTRO feature (like the 5 baselines) or treated as a periodically-refreshed artifact (like some archived docs)? Recommendation: treat as baseline (regenerate on every MAESTRO-affecting feature) — this establishes governance precedent for maintenance. — team-lead — `/aod.plan` — Open

### Pre-resolved Operational Decisions (embedded in PRD; carry forward to spec)
- **Architecture iteration fallback ranking** (team-lead review M3): (a) keyword-tune component names / descriptions → (b) extend architecture with 2-3 additional multi-agent components → (c) relax FR-3 coverage expectation to 6/7 layers (last resort). Encoded in FR-4 Business Rules.
- **Pre-execution architecture review checklist** (architect review M4): 4-condition static review of architecture.md before first pipeline invocation (multi-agent gate predicate + R-01 + R-02 + R-03 preconditions). Encoded in FR-4 pre-execution checklist.
- **Wave 0 timebox** (team-lead review L1): ≤2h with EOD Day 1 hard stop; escalate to user if no consensus. Encoded in Timeline.
- **README parallelism** (team-lead review M2 / L2): README sections 1, 2, 5, 6, 7 drafted in parallel with architecture iteration (Wave 3); sections 3 and 4 gated on pipeline output freeze. Encoded in Timeline.
- **Feature 120 workflow path** (architect review M5): Path B — hand-author body first, invoke `/tachi.architecture` in "create" mode AFTER architecture is frozen to inject checksum + frontmatter. Encoded in FR-8.
- **Structural DoD discipline** (team-lead review L4): DoD enforces "no accidental mixed structure" per chosen Option X or Y (FR-1 Wave 0 decision). Encoded in DoD checklist.

---

## References

### Product Documentation
- Product Vision: [product-vision.md](../01_Product_Vision/product-vision.md)
- GitHub Issue: [#145](https://github.com/davidmatousek/tachi/issues/145)
- Parent Issue: [#136](https://github.com/davidmatousek/tachi/issues/136) (MAESTRO framework compliance)

### Related PRDs
- [PRD 024: Example Threat Models](024-example-threat-models-2026-03-23.md) — established examples directory convention
- [PRD 084: MAESTRO Layer Mapping](084-maestro-layer-mapping-2026-04-07.md) — L1-L7 taxonomy overlay
- [PRD 091: MAESTRO Infographic Templates](091-maestro-infographic-templates-and-pdf-report-section-2026-04-08.md) — MAESTRO visualization
- [PRD 136: MAESTRO Canonical Layer Correctness](136-maestro-canonical-layer-correctness-fix-2026-04-10.md) — canonical layer names
- [PRD 141: MAESTRO Cross-Layer Attack Chains](141-maestro-cross-layer-attack-chains-2026-04-12.md) — Phase 2 cross-layer chain capability
- [PRD 142: MAESTRO Agentic Pattern Expansion](142-maestro-agentic-pattern-expansion-2026-04-16.md) — Phase 3 agentic pattern capability
- [PRD 143: MAESTRO AIVSS Evaluation ADR](143-maestro-aivss-evaluation-adr-2026-04-14.md) — Phase 4 compliance posture
- [PRD 144: NIST AI RMF Evaluation ADR](144-nist-ai-rmf-evaluation-adr-2026-04-15.md) — Phase 5 compliance posture
- [PRD 120: Architecture Lifecycle Command](120-architecture-lifecycle-command-2026-04-09.md) — architecture version tracking
- [PRD 128: Executive Threat Architecture Infographic](128-executive-threat-architecture-2026-04-09.md) — executive architecture infographic
- [PRD 112: Attack Path Pages](112-attack-path-pages-in-pdf-2026-04-09.md) — PDF attack tree pages

### Technical Documentation
- [ADR-020: MAESTRO Layer Classification](../../architecture/02_ADRs/ADR-020-maestro-layer-classification.md) — MAESTRO classification architecture (Phases 1-3 documented)
- [ADR-021: SOURCE_DATE_EPOCH for Deterministic PDF](../../architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) — determinism constraint for PDF baseline
- [ADR-022: mmdc Hard Prerequisite](../../architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md) — mermaid-cli is a hard prerequisite for examples with Critical/High findings
- [ADR-023: Threat Agent Skill References Pattern](../../architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md) — lean agent detection tier that produces the example's STRIDE+AI findings
- [ADR-024: OWASP AIVSS Evaluation](../../architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md) — Phase 4 AIVSS posture
- [ADR-025: NIST AI RMF Evaluation](../../architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md) — Phase 5 NIST AI RMF posture
- [ADR-026: Pattern Classification Mechanism](../../architecture/02_ADRs/ADR-026-pattern-classification-mechanism.md) — Phase 3 hybrid synthesis decision

### External Resources
- [CSA Blog: Agentic AI Threat Modeling Framework — MAESTRO (2025-02-06)](https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro)
- [Snyk Labs: MAESTRO — Layered Threat Modeling for Agentic AI Ecosystems](https://labs.snyk.io/resources/maestro-threat-modeling/)
- [Practical DevSecOps: MAESTRO — An Agentic AI Threat Modeling Framework](https://www.practical-devsecops.com/maestro-agentic-ai-threat-modeling-framework/)

---

## Approval Sign-offs

**Product Manager**: APPROVED
**Date**: 2026-04-16
**Notes**: Closes the final teaching-artifact gap in tachi's MAESTRO umbrella. Content-authoring only. All Phase 1-5 dependencies DELIVERED. Wave 0 gates (domain, directory structure, mmdc CI) pre-resolved in PRD Operational Decisions section.

**Architect**: APPROVED_WITH_CONCERNS
**Date**: 2026-04-16
**Notes**: 7 findings (1 BLOCKING addressed inline, 5 MEDIUM, 1 LOW). Full details: `.aod/results/architect-145.md`. BLOCKING B1 (FR-1 structure ambiguity) resolved by making Option X/Y an explicit Wave 0 decision. M1-M5 and L1 all addressed inline. Sign-off conditioned on Wave 0 reconciliation of domain (A/B/C), structure (X/Y), and mmdc CI availability.

**Team-Lead**: APPROVED_WITH_CONCERNS
**Date**: 2026-04-16
**Notes**: 7 findings (0 BLOCKING, 3 MEDIUM, 4 LOW). Full details: `.aod/results/team-lead-145.md`. Timeline expanded to 4-8d. Fallback ranking and Wave 0 timebox pre-resolved in PRD. README parallelism structure (Waves 3/4 overlap) adopted. Proposed wave structure included in results file. Dependencies clean; no capacity concerns.

---

**Next Steps**:
- `/aod.plan 145` — Generate spec, project plan, and tasks with triple sign-off
- Wave 0 gates (per architect + team-lead reviews) must be reconciled at spec authoring:
  1. Domain selection (A Healthcare / B Research / C Supply-Chain) — PRD recommends A, architect flagged B/C have lower content-review overhead
  2. Directory structure (X subdirectory / Y flat) — PRD recommends Y
  3. mmdc CI availability verified OR FR-7 deferred to follow-up
