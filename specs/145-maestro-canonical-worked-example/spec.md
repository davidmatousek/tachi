---
prd_reference: docs/product/02_PRD/145-maestro-canonical-worked-example-2026-04-16.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-16
    status: APPROVED_WITH_CONCERNS
    notes: "All 8 PRD FRs covered (FR-1..FR-8 decomposed into spec FR-001..FR-018), all 6 user stories with priorities preserved, 14 SCs measurable and testable, Wave 0 deferrals correctly captured as governance gates (domain A/B/C, structure X/Y, mmdc CI availability). 3 non-blocking concerns: (1) Risk 145.6 agentic-app displacement now explicit in edge cases (fixed inline); (2) PRD FR to spec FR cross-reference table not present — coverage verified in review, can be revisited during /aod.analyze; (3) mmdc edge-case risk-reference wording tightened inline. Proceed to /aod.project-plan. Wave 0 must resolve 3 deferred operational decisions per governance gate. If Option A Healthcare chosen, DoD adds security-analyst disclaimer review per FR-017 / SC-014."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Canonical MAESTRO Worked Example

**Feature Branch**: `145-maestro-canonical-worked-example`
**Created**: 2026-04-16
**Status**: Draft
**Input**: PRD 145 — `docs/product/02_PRD/145-maestro-canonical-worked-example-2026-04-16.md`

---

## Overview

Ship a purpose-built canonical MAESTRO worked example under `examples/` — a multi-agent reference architecture covering all seven MAESTRO layers with at least one cross-layer attack chain and at least three of the six canonical agentic patterns surfaced end-to-end by the existing tachi pipeline. The deliverable is content-authoring only: a new example directory containing a hand-authored `architecture.md` (Mermaid), a hand-authored adopter-facing `README.md`, and the full set of pipeline-generated output artifacts. No code changes, no schema changes, no agent changes.

This example closes the final teaching-artifact gap in tachi's MAESTRO umbrella — Phases 1 through 5 (Features 084, 136, 141, 142, 143, 144) are all delivered, but tachi has no canonical "read this first" artifact demonstrating the full MAESTRO experience end-to-end. The canonical MAESTRO example gives new adopters, evaluators, and maintainers a single cohesive walkthrough to study before applying tachi to their own systems.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — New Adopter Canonical First-Read (Priority: P0)

A security engineer evaluating tachi for the first time opens `examples/README.md`, sees the canonical MAESTRO example called out as the recommended first read for MAESTRO users, opens the example's own `README.md`, and gets an adopter-facing tour that explains the domain, how each of the seven MAESTRO layers is represented in the architecture, what attack scenarios to look for in the generated output, and how to read the accompanying files (threats.md, threat-report.md, PDF, infographics).

**Why this priority**: This is the headline use case driving the feature. Without this story satisfied, tachi cannot point adopters at a canonical walkthrough and the MAESTRO umbrella remains structurally complete but not demonstrable. Everything else is downstream of this.

**Independent Test**: Open the repo fresh, navigate `examples/README.md` → example README → pipeline output files, and verify the adopter can follow the tour end-to-end in under 30 minutes without external references beyond the ADR links named in the README's compliance-posture section.

**Acceptance Scenarios**:
1. **Given** `examples/README.md`, **when** a reader scans the page, **then** the canonical MAESTRO example is prominently positioned as the recommended first read for MAESTRO users.
2. **Given** the example directory `README.md`, **when** read end-to-end, **then** it contains sections for introduction, domain overview, MAESTRO layer coverage table, what to look for in the output, reading-order recommendation, compliance-posture cross-references, and limitations — matching FR-003 required sections.
3. **Given** the example directory, **when** browsed, **then** it contains all standard pipeline outputs (threats.md, threats.sarif, threat-report.md, risk-scores.md, risk-scores.sarif, compensating-controls.md, compensating-controls.sarif, attack-trees/, attack-chains.md if chains surface, six infographic JPEGs with co-committed specs, security-report.pdf, security-report.pdf.baseline).

---

### User Story 2 — Evaluator Cross-Layer Attack Chain Demonstration (Priority: P0)

A security engineer performing a tools evaluation for their own multi-agent system reads the example's generated `threat-report.md` and sees the Cross-Layer Attack Chains section (Feature 141) render at least one attack chain spanning three or more MAESTRO layers with a causal narrative comparable in shape to the CSA canonical financial-trading kill-chain. Inspecting the underlying `attack-chains.md` confirms chain membership traces the architectural data-flow lineage (not a keyword coincidence).

**Why this priority**: The cross-layer chain is the single most differentiated MAESTRO deliverable vs. competing STRIDE-only tools. Without a concrete demonstration, evaluators fall back on reading agentic-app (which was not designed for this purpose) or the abstract MAESTRO framework documentation.

**Independent Test**: Open `threat-report.md`, locate the Cross-Layer Attack Chains section, verify at least one chain spans ≥3 layers, read the causal narrative, then open `attack-chains.md` and confirm the chain's member findings correspond to components connected by data flows in the architecture.

**Acceptance Scenarios**:
1. **Given** the example's generated `threat-report.md`, **when** reading the Cross-Layer Attack Chains section, **then** at least one chain spans three or more MAESTRO layers.
2. **Given** the example's `attack-chains.md`, **when** inspected, **then** at least one chain narrative describes a cascading compromise comparable in shape to the CSA canonical walkthrough.
3. **Given** the example's architecture.md data flows, **when** compared with the generated chain output, **then** chain member findings align with architectural component lineage (shared data flows or component-lineage links).

---

### User Story 3 — Canonical Comparison Surface for Multi-Agent Threat Modeling (Priority: P0)

A CISO, security team lead, or MAESTRO practitioner reviews the example's `threat-report.md` Agentic Pattern Analysis section (Feature 142) and finds at least three of the six canonical agentic patterns populated, with narratives explaining how each pattern manifests in the reference architecture. The README's MAESTRO layer coverage table maps every architecture component to one or more MAESTRO layers in a format directly comparable to the CSA canonical mapping table.

**Why this priority**: This is the story that lets evaluators compare tachi output side-by-side against the CSA canonical documentation. Without it, MAESTRO-familiar reviewers cannot use the example as a comparison anchor and must mentally bridge between tachi's generic examples and the canonical framework.

**Independent Test**: Open `threat-report.md`, locate the Agentic Pattern Analysis section, count populated patterns (≥3 required), read the narratives. Then open the example README, locate the MAESTRO layer coverage table, and confirm every component listed in `architecture.md` appears mapped to at least one layer.

**Acceptance Scenarios**:
1. **Given** the example, **when** compared with the CSA canonical walkthrough, **then** all seven MAESTRO layers have explicit representation.
2. **Given** the example's `threat-report.md`, **when** reading the Agentic Pattern Analysis section, **then** at least three of the six canonical patterns are populated with substantive narratives.
3. **Given** the example's `README.md`, **when** reading it, **then** a MAESTRO layer coverage table maps each architecture component to its MAESTRO layer(s).

---

### User Story 4 — MAESTRO Regression Fixture for Maintainers (Priority: P1)

A tachi maintainer adding a new feature that touches any MAESTRO capability (schema change, new pattern, new layer semantics) runs the backward-compatibility test suite and sees the canonical MAESTRO example regression-check the full MAESTRO surface — all seven layers populated, cross-layer chains surfaced, agentic patterns populated, infographics generated. The PDF baseline regenerates byte-identical under `SOURCE_DATE_EPOCH=1700000000` (per ADR-021).

**Why this priority**: This story is the maintainer-facing value — the canonical example doubles as a regression fixture designed for MAESTRO coverage. Priority P1 rather than P0 because it depends on mmdc CI availability being verified first (an external gate); if that gate does not hold, regression-fixture integration is deferred to a follow-up per Risk 145.3 and the adopter-facing artifact still ships.

**Independent Test**: Run `pytest tests/scripts/test_backward_compatibility.py` with `SOURCE_DATE_EPOCH=1700000000` and verify the new baseline passes byte-identity. Run the full pipeline against the example architecture on a subsequent day and verify output is byte-identical.

**Acceptance Scenarios**:
1. **Given** the example, **when** the pipeline is run, **then** all seven MAESTRO layers are populated in the MAESTRO Findings section and on the MAESTRO stack / heatmap infographics.
2. **Given** the example's PDF baseline, **when** regenerated under `SOURCE_DATE_EPOCH=1700000000`, **then** the regeneration is byte-identical.
3. **Given** the example, **when** the backward-compatibility test suite runs, **then** the example is included as a baseline with zero diff on subsequent runs with unchanged code.

---

### User Story 5 — Purpose-Built Validation Target for Future MAESTRO Work (Priority: P1)

A developer implementing or refactoring Phase 2 cross-layer chain logic, Phase 3 agentic pattern synthesis, or any follow-on MAESTRO phase needs a regression target that naturally exercises multi-layer chains and multi-pattern findings without architectural contortion. The canonical MAESTRO example satisfies this by virtue of its seven-layer coverage, inter-agent data flows, persistent-state components, and emergent-behavior descriptions — all pre-verified by the Pre-Execution Architecture Review Checklist (FR-005) before first pipeline run.

**Why this priority**: This story secures maintainer buy-in for the example's regression-target convention. P1 rather than P0 because the value accrues to future features, not the first ship.

**Independent Test**: Take the example's architecture.md and verify by static review that the Pre-Execution Architecture Review Checklist's four conditions are all green (multi-agent gate predicate, R-01, R-02, R-03 preconditions). Then use the example as an integration-test input for a hypothetical future MAESTRO feature and confirm the intended capability surfaces without architecture modifications.

**Acceptance Scenarios**:
1. **Given** the example, **when** used as a validation target for future MAESTRO work, **then** its architecture exercises cross-layer chains (≥1 surfaces) and agentic patterns (≥3 populated) without requiring architectural contortion.
2. **Given** the example's architecture.md, **when** inspected, **then** component names, trust boundaries, and data-flow descriptions clearly map to expected MAESTRO output categories.
3. **Given** future MAESTRO features, **when** implemented, **then** the canonical example is regenerated as part of the feature's Definition of Done (governance precedent).

---

### User Story 6 — Adopter Compliance Framework Cross-References (Priority: P1)

An adopter reading the canonical MAESTRO example's README encounters a short compliance-posture section (approximately 100-150 words) summarizing tachi's AIVSS (ADR-024) and NIST AI RMF (ADR-025) posture with links to the authoritative ADRs, so they understand tachi's peer-framework awareness without hunting through the `docs/architecture/02_ADRs/` directory. The `examples/README.md` positions the canonical MAESTRO example as distinct from the existing six examples (baseline STRIDE, input-format fixtures, dual-dispatch demo).

**Why this priority**: This story ensures the example is correctly positioned in the broader tachi documentation surface and avoids displacing agentic-app in adopters' mental model. P1 because misalignment would be caught and corrected in a later docs-only follow-up if it slipped to first ship.

**Independent Test**: Read `examples/README.md`, then the example's README compliance-posture section, then the referenced ADR-024 and ADR-025. Verify the summary in the example README is consistent with the ADR decision-noun phrasing.

**Acceptance Scenarios**:
1. **Given** the example's README, **when** reading the compliance-posture section, **then** it summarizes tachi's AIVSS and NIST AI RMF posture per ADR-024 / ADR-025 with links.
2. **Given** the example, **when** the PDF is read, **then** the scope / methodology section surfaces the existing CVSS 3.1 + exploitability + scalability + reachability scoring model (tachi's canonical scoring).
3. **Given** the READMEs, **when** read in sequence (`examples/README.md` → example README), **then** the canonical MAESTRO example is positioned distinctly from the six existing examples.

---

### Edge Cases

- **Architecture iteration exceeds cap**: If the pre-execution architecture checklist surfaces a gap during static review, the architecture is tuned (fallback ranking: keyword-tune → extend with 2-3 additional multi-agent components → relax FR-004 coverage to 6/7 layers as last resort). If 2 iteration rounds fail after first pipeline invocation, architect and team-lead meet to decide whether to adjust the chosen domain or relax FR-004 coverage.
- **Domain change mid-implementation**: The domain is locked during `/aod.plan` Wave 0 with a ≤2h timebox and EOD Day 1 hard stop. If consensus is not reached in Wave 0, team-lead escalates to the user for a same-day tiebreak. Changing the domain after architecture drafting begins is explicitly out of scope (restart cost too high).
- **mmdc CI not available**: The backward-compatibility CI workflow must have `@mermaid-js/mermaid-cli` provisioned before the regression fixture integration lands. If not available, FR-011 is deferred to a follow-up PR per the FR-011 contingency clause — the canonical example still ships as adopter-facing artifact.
- **Canonical example inadvertently displaces agentic-app in adopter mental model**: FR-010 and FR-014 guard this structurally (existing listings preserved; agentic-app unchanged), and US-6 AC-3 verifies distinct positioning. If post-ship adopter confusion surfaces (e.g., comparison questions conflating the two), tighten the positioning prose in a docs-only follow-up.
- **Byte-identity baseline regeneration fails**: If the PDF regeneration under `SOURCE_DATE_EPOCH=1700000000` is non-byte-identical, baseline integration is deferred to a follow-up while the adopter-facing artifact ships. Root cause must be diagnosed before the baseline is finally committed.
- **README prose reads as marketing**: If PM review flags the README as overclaiming or promotional in tone, a rewrite for neutral factual tone is a low-cost iteration (≤0.5 day). PM reviews the README draft before final commit.
- **Domain content-risk signals**: If Healthcare (Option A) is chosen, any reviewer flagging README content as too realistic or too specific triggers a rewrite to more abstract naming before commit. Security-analyst reviews the disclaimer prose per DoD gate.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The project MUST ship a new example directory under `examples/` whose identity is "canonical MAESTRO walkthrough" rather than a specific domain label, with the directory name chosen to signal MAESTRO canonical scope and avoid conflict with existing example names. Recommended default: `examples/maestro-reference/`.
- **FR-002**: The example directory MUST contain an `architecture.md` in Mermaid format as the canonical pipeline input.
- **FR-003**: The example directory MUST contain a hand-authored `README.md` serving as the adopter-facing tour, distinct in purpose from `architecture.md`, with sections covering (a) introduction, (b) domain overview with disclaimer that the scenario is not a real system, (c) MAESTRO layer coverage table mapping components to layers, (d) what to look for in the output files, (e) reading-order recommendation tailored to varying time budgets, (f) compliance posture cross-references with links to ADR-024 and ADR-025, and (g) limitations and scope.
- **FR-004**: The architecture MUST represent all seven MAESTRO layers (L1 Foundation Models, L2 Data Operations, L3 Agent Frameworks, L4 Deployment and Infrastructure, L5 Evaluation and Observability, L6 Security and Compliance, L7 Agent Ecosystem) with at least two components per layer and at least fourteen total components.
- **FR-005**: The architecture MUST satisfy all four conditions of the Pre-Execution Architecture Review Checklist by static review before first pipeline invocation: (a) multi-agent gate predicate TRUE, (b) R-01 precondition (inter-agent data flow between two agentic components), (c) R-02 precondition (at least one persistent-state component — fine-tuning pipeline, agent memory store, or long-running learning loop), (d) R-03 precondition (multi-agent topology with emergent-behavior keywords in at least one agentic component description).
- **FR-006**: The pipeline MUST be run end-to-end against the authored architecture using the standard command sequence (`/tachi.architecture` → `/tachi.threat-model` → `/tachi.risk-score` → `/tachi.compensating-controls` → `/tachi.infographic all` → `/tachi.security-report`), and all generated outputs MUST be committed to the example directory.
- **FR-007**: The generated `threats.md` MUST surface findings across at least six of the seven MAESTRO layers (all seven preferred; six accepted as fallback per FR-004 relax option).
- **FR-008**: The generated `threat-report.md` MUST render (a) a populated MAESTRO Findings section with per-layer subsections, (b) a Cross-Layer Attack Chains section containing at least one chain spanning three or more MAESTRO layers, and (c) an Agentic Pattern Analysis section with at least three of the six canonical patterns populated.
- **FR-009**: The generated `security-report.pdf.baseline` MUST be byte-identical across repeat regenerations under `SOURCE_DATE_EPOCH=1700000000` (per ADR-021 determinism convention).
- **FR-010**: The top-level `examples/README.md` MUST be updated to position the new example as the canonical MAESTRO walkthrough, with (a) a new row or equivalent table entry describing "Canonical MAESTRO walkthrough" in the Key Demonstration column, and (b) a prominent first-read callout near the top of the README. The existing six examples MUST retain their listings — the new example is added, not a replacement.
- **FR-011**: The backward-compatibility regression test suite `tests/scripts/test_backward_compatibility.py` MUST include the new example as a sixth baseline alongside the existing five non-multi-agent baselines (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice). This requirement is conditional on the CI environment running the suite having `@mermaid-js/mermaid-cli` provisioned; if not available, regression-fixture integration is deferred to a follow-up per Risk 145.3.
- **FR-012**: The example's `architecture.md` MUST carry Feature 120 version-tracking YAML frontmatter (version "1.0", date, description, SHA-256 checksum) injected as the final step before commit via `/tachi.architecture` in "create" mode operating on the frozen hand-authored body — intermediate frontmatter commits during iteration are prohibited.
- **FR-013**: The five existing non-multi-agent baselines (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice) MUST remain byte-identical after this feature — the new example is additive, not a rewrite of existing artifacts.
- **FR-014**: The `agentic-app` example MUST NOT be modified as part of this feature — it retains its current shape, generated output, and regeneration convention (Feature 128 / 141 / 142 precedent).
- **FR-015**: The chosen domain MUST be non-financial (to avoid appearing derivative of the CSA canonical multi-agent financial trading walkthrough), MUST plausibly support two or more cooperating agents with distinct responsibilities, MUST naturally span all seven MAESTRO layers, and MUST make a substantive case for agentic threat modeling beyond "chat with multiple LLMs".
- **FR-016**: The example's README MUST include a prominent disclaimer stating the scenario is a security reference for threat-modeling teaching purposes only and is not a real production system, regardless of which candidate domain is chosen.
- **FR-017**: If the Healthcare domain option is chosen, the security-analyst MUST review the README disclaimer prose for content-risk framing before the README is committed.
- **FR-018**: `/aod.analyze` MUST pass with no cross-artifact inconsistencies after all artifacts are committed.

### Deferred to /aod.plan Wave 0

Three operational decisions are explicitly deferred to the project-plan wave; the spec captures them as Wave 0 gates, not as open ambiguities blocking spec sign-off:

- **[NEEDS CLARIFICATION: Domain selection — Option A Healthcare / B Autonomous Research / C Supply-Chain Optimization]** — architect leads the final call with PM and team-lead concurrence. PRD recommends Option A. Fallback ranking A → B → C. Locked in Wave 0; if no consensus after ≤2h timebox, team-lead escalates to user for same-day tiebreak.
- **[NEEDS CLARIFICATION: Directory structure — Option X subdirectory `sample-report/` / Option Y flat at top-level]** — architect makes the final call in Wave 0. PRD recommends Option Y. Aligns with 5-of-6 existing flat precedent.
- **[NEEDS CLARIFICATION: mmdc CI availability for FR-011]** — architect and team-lead jointly verify in Wave 0 whether the backward-compat CI workflow has `@mermaid-js/mermaid-cli` provisioned. If available, FR-011 lands in this feature. If not, FR-011 is deferred to a follow-up PR per Risk 145.3 contingency.

### Key Entities

- **Example Directory**: A new directory under `examples/` containing the architecture input, pipeline-generated outputs, and adopter-facing README. Identity is canonical MAESTRO scope, not a specific domain.
- **Architecture.md**: Hand-authored Mermaid `flowchart TD` document representing fourteen or more components across all seven MAESTRO layers, with trust-boundary subgraphs, component summary table below the diagram, and Feature 120 version-tracking YAML frontmatter (injected last). Serves as the canonical pipeline input.
- **Adopter-Facing README.md**: Hand-authored markdown document serving as the adopter's tour of the example. Seven required sections per FR-003. Not regenerated by the pipeline; maintained as part of the example content.
- **Pipeline Output Artifacts**: The standard set of files produced by running the full tachi pipeline against the architecture — `threats.md`, `threats.sarif`, `threat-report.md`, `risk-scores.md`, `risk-scores.sarif`, `compensating-controls.md`, `compensating-controls.sarif`, `attack-trees/` directory, `attack-chains.md` (if chains surface), six infographic JPEGs with co-committed specs, `security-report.pdf`, `security-report.pdf.baseline`.
- **Cross-Layer Attack Chain** (domain entity in the output): A narrative describing a cascading compromise across three or more MAESTRO layers, assembled by orchestrator Phase 3.5 from the deduplicated finding intermediate representation. Surfacing depends on architecture satisfying the chain-assembly preconditions (2+ layers, Critical/High severity, structural component lineage or data-flow dependency).
- **Agentic Pattern Annotation** (domain entity in the output): A per-finding classification tagging findings with one of the six canonical patterns (Agent Collusion, Emergent Behavior, Temporal Attack, Trust Exploitation, Communication Vulnerability, Resource Competition) via the deterministic rule table R-01 through R-06.
- **PDF Baseline**: A deterministic `security-report.pdf.baseline` file regenerated byte-identical under `SOURCE_DATE_EPOCH=1700000000` per ADR-021, used as the anchor for regression byte-identity checks.

---

## Assumptions

- Phases 1 through 5 of the MAESTRO umbrella (Features 084, 136, 141, 142, 143, 144) are merged to main and stable. The canonical example demonstrates their combined capability without modifying any of them.
- The existing pipeline is deterministic under `SOURCE_DATE_EPOCH=1700000000` per ADR-021. No new determinism work is needed.
- The chosen domain is plausible enough to produce substantive threat-model output without being so domain-specific that adopters distrust its reference value.
- Architect, team-lead, and PM can reach concurrence on the domain during `/aod.plan` Wave 0 using the ≤2h timebox and fallback ranking (A → B → C); if not, team-lead escalates to the user for a same-day tiebreak.
- The local developer environment running the pipeline has `@mermaid-js/mermaid-cli` installed (hard prerequisite per ADR-022 when attack trees are present).
- The Gemini API used for infographic JPEG generation is available during the authoring session — one-time cost, no ongoing dependency.
- No new runtime dependencies are added (zero-dependency runtime constraint preserved).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The new example directory is committed containing `architecture.md` covering all seven MAESTRO layers with at least fourteen components (≥2 per layer).
- **SC-002**: The generated `threat-report.md` surfaces at least one cross-layer attack chain spanning three or more MAESTRO layers.
- **SC-003**: The generated `threat-report.md` Agentic Pattern Analysis section contains at least three of the six canonical agentic patterns populated with substantive narrative.
- **SC-004**: The generated `threats.md` surfaces findings tagged with at least six of the seven MAESTRO layers populated (all seven preferred).
- **SC-005**: The example README contains all seven FR-003 required sections with neutral factual tone (verified by PM review before commit).
- **SC-006**: `examples/README.md` positions the new example as the canonical MAESTRO walkthrough with a prominent first-read callout; no existing examples are removed.
- **SC-007**: The `security-report.pdf.baseline` regenerates byte-identical on repeat runs under `SOURCE_DATE_EPOCH=1700000000`.
- **SC-008**: The five existing non-multi-agent baselines (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice) regenerate byte-identical — this feature introduces no backward-compatibility break.
- **SC-009**: The `agentic-app` example is unchanged — no files under `examples/agentic-app/` are modified as part of this feature.
- **SC-010**: `/aod.analyze` passes on the committed spec, plan, and tasks artifacts with no cross-artifact inconsistencies.
- **SC-011**: The Pre-Execution Architecture Review Checklist (FR-005) is verified green for all four conditions before first pipeline invocation, with the verification recorded in research.md and carried into the plan's Wave tracking.
- **SC-012**: The Feature 120 version-tracking frontmatter is present on the committed `architecture.md` with version "1.0" and a valid SHA-256 checksum computed over the post-frontmatter body.
- **SC-013** (conditional on FR-011): If mmdc is provisioned in the backward-compat CI workflow, `tests/scripts/test_backward_compatibility.py` includes the new example in `BASELINE_EXAMPLES` and passes byte-identity. If not, FR-011 and SC-013 are deferred to a follow-up PR per Risk 145.3 contingency with the deferral documented in the plan.
- **SC-014** (conditional on Option A Healthcare domain): The security-analyst reviews the README disclaimer prose before commit and signs off that content-risk framing is adequate.

### Non-Functional Quality Bars

- **Adopter readability**: The example README uses clear prose, defines or cross-references tachi-specific terms (STRIDE, MAESTRO, dispatch) inline, and is readable end-to-end by someone who has never used tachi.
- **Pipeline readability**: The `architecture.md` passes `/tachi.architecture` validation with no warnings; component names contain the expected dispatch keywords (per Feature 084 / 136 / 142 canonical pattern recognition rules) so the MAESTRO classifier's first-match-wins ordering produces the intended layer assignments.
- **Narrative substance**: The attack chain narrative and agentic pattern subsections are substantive (not filler) — describing plausible cross-layer attack propagation grounded in the chosen domain rather than generic templated prose.

---

## Scope & Boundaries

### In Scope
All FR-001 through FR-018 requirements, P0 and P1 user stories US-1 through US-6, and all SC-001 through SC-014 measurable outcomes.

### Out of Scope
- **No new pipeline phases, agents, schemas, templates, or ADRs** — this is purely content authoring consuming the existing pipeline. MAESTRO ADRs (ADR-020, ADR-026) and compliance posture ADRs (ADR-024, ADR-025) already exist.
- **No regeneration of the 5 existing baselines or agentic-app** — they remain byte-identical.
- **No scripting of the example regeneration** — the example is regenerated manually via the existing pipeline invocation (no new CI job or `make` target specific to this example).
- **No replacement of agentic-app** — agentic-app continues to serve as the Features 141/142 demonstration baseline; the canonical MAESTRO example is an addition, not a replacement.
- **No per-adopter reference architectures or adopter template library** — this example is a reference, not a template library.
- **No pre-baked CSA-comparison table in the README** (P1 "Should Have" stretch; explicitly out of scope for first ship unless time permits).

### Deferred to Follow-Up PR (Conditional)
- **FR-011 regression-fixture integration** if mmdc CI is not available (Risk 145.3).
- **P1 "Should Have" top-level repo README cross-reference** (one-line mention in top-level README pointing to canonical MAESTRO) — may ship with first commit or in a follow-up.
- **P1 "Should Have" diagram thumbnails in the example README** — may ship with first commit or in a follow-up.
- **P1 "Should Have" CSA canonical comparative table in the example README** — deferred to follow-up unless it fits within the 4-8 day timeline without compressing Waves.

---

## References

### Source PRD
- [PRD 145: MAESTRO Canonical Worked Example](../../docs/product/02_PRD/145-maestro-canonical-worked-example-2026-04-16.md) — full requirements, risks, and approval sign-offs

### Predecessor Features (All DELIVERED)
- PRD 024 (Example Threat Models) — established examples directory convention
- PRD 084 (MAESTRO Layer Mapping) — L1-L7 taxonomy overlay; prerequisite capability
- PRD 091 (MAESTRO Infographic Templates) — MAESTRO stack and heatmap infographics
- PRD 104 (Downstream Baseline Propagation) — baseline columns in output
- PRD 112 (Attack Path Pages) — PDF attack tree pages for Critical/High findings
- PRD 120 (Architecture Lifecycle Command) — architecture version frontmatter
- PRD 121 (Tachi Commands Namespace) — `/tachi.architecture`, `/tachi.threat-model`, etc.
- PRD 128 (Executive Threat Architecture Infographic) — `threat-executive-architecture.jpg`
- PRD 129 (Attack Tree Delta Sub-Agent) — per-finding attack trees
- PRD 136 (MAESTRO Canonical Layer Correctness) — canonical L5/L6/L7 names
- PRD 141 (MAESTRO Cross-Layer Attack Chains) — Phase 2 cross-layer chains
- PRD 142 (MAESTRO Agentic Pattern Expansion) — Phase 3 agentic patterns
- PRD 143 (MAESTRO AIVSS Evaluation ADR) — Phase 4 compliance posture
- PRD 144 (NIST AI RMF Evaluation ADR) — Phase 5 compliance posture

### Technical Architecture
- [ADR-020: MAESTRO Layer Classification](../../docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md)
- [ADR-021: SOURCE_DATE_EPOCH for Deterministic PDF](../../docs/architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md)
- [ADR-022: mmdc Hard Prerequisite](../../docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md)
- [ADR-023: Threat Agent Skill References Pattern](../../docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md)
- [ADR-024: OWASP AIVSS Evaluation](../../docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md)
- [ADR-025: NIST AI RMF Evaluation](../../docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md)
- [ADR-026: Pattern Classification Mechanism](../../docs/architecture/02_ADRs/ADR-026-pattern-classification-mechanism.md)

### Shared References (pipeline detection rules)
- [.claude/skills/tachi-shared/references/maestro-layers-shared.md](../../.claude/skills/tachi-shared/references/maestro-layers-shared.md)
- [.claude/skills/tachi-shared/references/maestro-agentic-patterns-shared.md](../../.claude/skills/tachi-shared/references/maestro-agentic-patterns-shared.md)
- [.claude/skills/tachi-shared/references/attack-chain-patterns-shared.md](../../.claude/skills/tachi-shared/references/attack-chain-patterns-shared.md)

### External Canonical References
- [CSA Blog: Agentic AI Threat Modeling Framework — MAESTRO](https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro)
- [Snyk Labs: MAESTRO — Layered Threat Modeling for Agentic AI Ecosystems](https://labs.snyk.io/resources/maestro-threat-modeling/) — Tier-1 worked example with financial trading narrative
- [Practical DevSecOps: MAESTRO — An Agentic AI Threat Modeling Framework](https://www.practical-devsecops.com/maestro-agentic-ai-threat-modeling-framework/)

### Research Artifact
- [research.md](research.md) — research findings: examples directory conventions, MAESTRO detection patterns, CSA canonical walkthrough structure, candidate domain analysis (Option A/B/C trade-offs), Feature 120 workflow, mmdc CI prerequisite
