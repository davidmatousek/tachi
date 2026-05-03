---
prd_reference: docs/product/02_PRD/141-maestro-cross-layer-attack-chains-2026-04-12.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-12
    status: APPROVED_WITH_CONCERNS
    notes: "All 6 PRD FRs traced into 17 spec FRs, all 5 PRD user stories covered (decomposed into 6 spec stories with 19 acceptance scenarios). 3 LOW concerns addressed inline: (1) US6 AC sharpened with CSA canonical vocabulary tokens, (2) FR-016 ordering clarified as descending, (3) Correlation Signal cross-references Edge Case 3."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: MAESTRO Phase 2 — Cross-Layer Attack Chain Analysis

**Feature Branch**: `141-maestro-phase-2`
**Created**: 2026-04-12
**Status**: Draft
**PRD Reference**: docs/product/02_PRD/141-maestro-cross-layer-attack-chains-2026-04-12.md
**Input**: PRD 141 — Surface cascading attack chains across the MAESTRO seven-layer taxonomy so security teams see how an exploit at one layer enables exploits at adjacent layers, ending in concrete business impact.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cross-Layer Attack Chain Detection (Priority: P0)

A security engineer runs tachi's threat modeling pipeline on an agentic AI system architecture. After the pipeline completes, the output includes a dedicated attack chains artifact that identifies cross-layer attack chains — sequences of related findings that cascade across multiple MAESTRO layers. Each chain shows which findings are linked, which layers they traverse, and the causal progression from initial exploit to business impact.

**Why this priority**: This is the core capability that transforms tachi from "STRIDE tool with MAESTRO labels" to "full MAESTRO implementation." Without cross-layer chain detection, the remaining user stories have no data to surface.

**Independent Test**: Run the pipeline on an architecture with findings across 3+ MAESTRO layers. Verify the attack chains artifact contains at least one chain with ordered finding references, layer progression, and causal narrative.

**Acceptance Scenarios**:

1. **Given** a completed pipeline run with findings across 3+ MAESTRO layers sharing component lineage or data flow dependencies, **When** the pipeline finishes, **Then** an attack chains artifact is produced enumerating each detected chain with: chain ID, member finding IDs, MAESTRO layer progression (e.g., L2 -> L3 -> L7), maximum severity, and causal narrative per transition.
2. **Given** a completed pipeline run with findings in only one MAESTRO layer, **When** the pipeline finishes, **Then** no attack chains artifact is produced and no errors occur.
3. **Given** two pipeline runs on the same architecture with identical findings, **When** comparing the attack chains output, **Then** the chains are identical (deterministic correlation).
4. **Given** a chain spanning 3+ layers, **When** reviewing the chain details, **Then** each transition includes a causal explanation of how the exploit at one layer enables the exploit at the next layer.

---

### User Story 2 - Attack Chain Narrative in Threat Report (Priority: P0)

A security engineer reviewing the threat report sees a new "Attack Chains" section that narratively walks through each Critical and High-severity chain. Each chain narrative describes the initial exploit, intermediate cascade steps with layer transitions, and the final business impact — transforming a flat finding list into an actionable attack story.

**Why this priority**: The threat report is the primary consumption format for security engineers. Without chain narratives, the raw artifact data requires manual interpretation.

**Independent Test**: Generate a threat report from an architecture with detected chains. Verify the report includes an Attack Chains section with a narrative walkthrough for each Critical/High chain.

**Acceptance Scenarios**:

1. **Given** a pipeline run that produces attack chains, **When** the threat report is generated, **Then** it includes an "Attack Chains" section after the existing Attack Trees section, containing a narrative walkthrough for each chain with Critical or High maximum severity.
2. **Given** a chain with Critical maximum severity spanning L2 -> L3 -> L7, **When** reading the chain narrative, **Then** it includes: (a) initial exploit description at L2, (b) intermediate cascade with causal transition from L2 to L3 and from L3 to L7, and (c) final business impact statement.
3. **Given** a pipeline run with no detected chains, **When** the threat report is generated, **Then** no Attack Chains section appears and the report is otherwise unchanged.
4. **Given** a chain narrative, **When** reading it, **Then** it is 150-300 words — concise but complete.

---

### User Story 3 - Visual Chain Diagrams in PDF Security Report (Priority: P0)

A CISO reviewing the PDF security assessment sees dedicated chain diagram pages showing how attacks propagate vertically through the MAESTRO layer stack. Each page contains a rendered diagram with layer labels, a condensed narrative, and impacted finding references — a board-ready visual that communicates end-to-end risk without reading individual findings.

**Why this priority**: The PDF is the primary deliverable for executive stakeholders. Visual chain diagrams make cross-layer risk comprehensible for non-technical audiences.

**Independent Test**: Generate a PDF from an architecture with detected chains. Verify chain diagram pages appear with rendered diagrams, narratives, and finding references.

**Acceptance Scenarios**:

1. **Given** a threat report with attack chains, **When** the PDF security report is generated, **Then** each Critical and High chain appears as a dedicated page with: chain title, rendered diagram showing vertical layer progression, condensed narrative, and impacted finding IDs.
2. **Given** a chain diagram, **When** viewing the rendered page, **Then** the diagram shows the MAESTRO layer stack vertically (L1 at top, L7 at bottom) with attack progression arrows between affected layers.
3. **Given** a report with no detectable chains, **When** the PDF is generated, **Then** no chain pages appear and the PDF is otherwise unchanged.
4. **Given** the chain rendering prerequisite (Mermaid CLI) is not installed, **When** the PDF pipeline detects chain diagrams to render, **Then** the pipeline fails loudly with an actionable error message (consistent with existing attack tree behavior per ADR-022).

---

### User Story 4 - Chain-Breaking Control Recommendations (Priority: P0)

A threat modeler analyzing attack chains for remediation prioritization sees which findings, if remediated, would break the chain. Chain-breaking controls are highlighted based on structural centrality within the chain, enabling targeted remediation that disrupts entire attack paths rather than treating findings independently.

**Why this priority**: Chain-breaking controls are the primary actionable output for remediation teams — the reason chains exist is to prioritize remediation.

**Independent Test**: Review chain details for a chain spanning 3+ layers. Verify at least one chain-breaking control recommendation is identified with the specific finding and rationale.

**Acceptance Scenarios**:

1. **Given** a chain with 3+ member findings, **When** viewing chain details in the attack chains artifact, **Then** at least one chain-breaking control is identified — a finding whose remediation would interrupt the chain progression.
2. **Given** a chain-breaking control recommendation, **When** reading it, **Then** it identifies the specific finding, explains why remediation breaks the chain (structural centrality), and provides a control recommendation.
3. **Given** chain-breaking controls are identified as heuristic, **When** the output presents them, **Then** a disclaimer states these are structurally derived, not verified for control effectiveness.

---

### User Story 5 - End-to-End Example Demonstration (Priority: P1)

A prospective tachi adopter evaluating the toolkit can inspect at least one example architecture that demonstrates a multi-layer attack chain end-to-end. The example includes the attack chains artifact, threat report narrative, and PDF chain diagram pages — a complete demonstration of the capability.

**Why this priority**: Example architectures are the primary evaluation mechanism for adopters. Without a working end-to-end example, the feature cannot be evaluated.

**Independent Test**: Run the pipeline on the designated example architecture. Verify the output includes a chain spanning 3+ MAESTRO layers with all output formats (artifact, narrative, diagram).

**Acceptance Scenarios**:

1. **Given** the examples directory, **When** inspecting at least one example, **Then** its output includes an attack chains artifact with a chain spanning 3+ MAESTRO layers.
2. **Given** the example chain, **When** the PDF is regenerated, **Then** it includes chain diagram pages demonstrating the full visualization capability.
3. **Given** a new user runs the pipeline on the example, **When** comparing output across runs, **Then** the chain output is reproducible (deterministic correlation per ADR-021).

---

### User Story 6 - Canonical MAESTRO Deliverable (Priority: P1)

A MAESTRO practitioner evaluating tachi as a MAESTRO-compliant tool finds that the output matches the canonical CSA MAESTRO deliverable format — cross-layer attack propagation narratives with causal language ("enables," "triggers," "manifests as") and visual layer-stack diagrams showing attack progression.

**Why this priority**: MAESTRO practitioners are a key adopter persona. Producing canonical deliverables validates tachi as a full MAESTRO implementation, not just a STRIDE tool with MAESTRO tags.

**Independent Test**: Compare the chain narrative and diagram output against the canonical CSA MAESTRO worked example format. Verify structural alignment.

**Acceptance Scenarios**:

1. **Given** a chain narrative, **When** compared to the canonical CSA MAESTRO worked example format, **Then** it follows the same structure: initial exploit, intermediate cascades with causal transitions using canonical vocabulary ("enables," "triggers," "shifts," "manifests as"), and business impact statement.
2. **Given** a chain diagram, **When** rendered, **Then** it visually shows the seven-layer stack with attack progression arrows between affected layers — matching the canonical MAESTRO layer-stack representation.

---

### Edge Cases

- What happens when all findings are in a single MAESTRO layer? No chains are detected; no chain-related output is produced.
- What happens when a finding has `maestro_layer: "Unclassified"`? Unclassified findings are excluded from chain correlation — they cannot participate in cross-layer chains.
- What happens when the architecture has findings across multiple layers but no component lineage or data flow relationship? No chains are detected — layer adjacency alone is insufficient without a structural relationship signal.
- What happens when a chain contains only Medium/Low findings? The chain is detected but not surfaced in the report or PDF — only chains with at least one Critical or High finding are surfaced.
- What happens when more than 5 chains are detected? The top 5 chains (by severity, then chain length) are surfaced in the report and PDF; the complete list remains in the attack chains artifact.
- What happens when a finding belongs to multiple chains? This is valid — findings can participate in multiple chains (many-to-many relationship).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Pipeline MUST include a cross-layer correlation phase that identifies attack chains by analyzing relationships between findings across different MAESTRO layers, using component lineage, data flow dependencies, and layer adjacency as correlation signals.
- **FR-002**: Correlation MUST be deterministic — the same set of findings and architecture description MUST produce identical chains on every run.
- **FR-003**: Pipeline MUST produce an attack chains artifact enumerating all detected chains, each containing: chain ID, ordered finding references with MAESTRO layer assignments, maximum severity, causal narrative per layer transition, and chain-breaking control recommendations.
- **FR-004**: Attack chains artifact MUST only be produced when chains are detected (`has-attack-chains` conditional gate). When no chains are detected, no artifact is produced and no downstream sections appear.
- **FR-005**: Chains MUST span at least 2 distinct MAESTRO layers. Single-layer groupings are not chains.
- **FR-006**: Only chains containing at least one Critical or High finding MUST be surfaced in the threat report narrative and PDF diagram pages. Lower-severity chains are recorded in the artifact only.
- **FR-007**: Maximum chain length MUST be 7 (one finding per layer — full-stack chain). A finding can appear in multiple chains (many-to-many).
- **FR-008**: Threat report MUST include an "Attack Chains" narrative section for Critical and High chains, placed after the existing Attack Trees section. Each chain narrative MUST be 150-300 words covering initial exploit, intermediate cascades, and business impact.
- **FR-009**: PDF security report MUST render chain diagrams as dedicated pages with vertical MAESTRO layer stack layout (L1 at top, L7 at bottom), attack progression arrows, chain title, condensed narrative, and impacted finding IDs. Each chain gets one page.
- **FR-010**: Chain diagrams MUST reuse the existing Mermaid-to-PNG rendering infrastructure and follow the existing fail-loud prerequisite pattern (ADR-022 enforcement).
- **FR-011**: Chain-breaking controls MUST be identified for each chain based on structural centrality (heuristic — not verified control effectiveness). A disclaimer MUST accompany all chain-breaking recommendations.
- **FR-012**: A chain schema MUST be documented as a new schema file, separate from the existing finding schema. Chains are cross-finding aggregates, not finding-level properties.
- **FR-013**: At least one example architecture MUST demonstrate a multi-layer chain spanning 3+ MAESTRO layers with all output formats (artifact, narrative, diagram).
- **FR-014**: All 6 existing example pipeline outputs MUST be regenerated. Architectures without detectable chains MUST produce byte-identical output under deterministic conditions (ADR-021).
- **FR-015**: Cross-layer chains and existing intra-component correlation groups (Section 4a) MUST remain independent grouping mechanisms — a finding may appear in both without conflict.
- **FR-016**: Surfaced chains MUST be capped at the top 5 by severity descending (Critical first), then by chain length descending (longer chains first), then by alphabetical chain ID ascending. The complete list remains in the artifact.
- **FR-017**: ADR-020 MUST be updated to document the transition from passive taxonomy overlay to active cross-layer correlation analysis.

### Key Entities

- **Attack Chain**: An ordered sequence of 2-7 findings spanning multiple MAESTRO layers, connected by component lineage, data flow dependencies, or layer adjacency, forming a coherent attack progression from initial exploit to business impact. Key attributes: chain ID, ordered member findings, layer progression, maximum severity, causal narrative, chain-breaking controls.
- **Chain Member Finding**: A reference to an existing finding (from threats.md) that participates in a chain. Key attributes: finding ID, MAESTRO layer, role in chain (initial exploit, intermediate cascade, terminal impact), causal relationship to next finding.
- **Chain-Breaking Control**: A heuristic recommendation identifying a chain member whose remediation would interrupt the attack progression. Key attributes: target finding ID, structural rationale, control recommendation, heuristic disclaimer.
- **Correlation Signal**: The evidence connecting two findings across layers into a chain. Three types: component lineage (findings target components connected by data flows), data flow dependency (findings on components sharing data flow paths), and layer adjacency (findings in adjacent MAESTRO layers affecting related components). Note: layer adjacency alone is insufficient — at least one structural relationship signal (component lineage or data flow dependency) is required to form a chain (see Edge Case 3).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Chain detection coverage — at least 80% of architectures with findings in 3+ MAESTRO layers produce at least one cross-layer chain.
- **SC-002**: Chain quality (precision) — at least 90% of detected chains represent genuine causal relationships, validated against example architectures with known expected chains.
- **SC-003**: Output completeness — 100% of detected chains appear in all three output formats (attack chains artifact, threat report narrative, PDF chain diagram pages) when they meet the Critical/High severity threshold.
- **SC-004**: Determinism — pipeline runs on identical inputs produce byte-identical chain output under deterministic conditions (SOURCE_DATE_EPOCH per ADR-021).
- **SC-005**: Backward compatibility — 5 existing example PDFs remain byte-identical under SOURCE_DATE_EPOCH=1700000000 when no chains are detected. The 6th example (chain demonstration) is intentionally regenerated.
- **SC-006**: Correlation phase adds less than 10 seconds to pipeline runtime for architectures with fewer than 100 findings.
- **SC-007**: At least one example architecture demonstrates a chain spanning 3+ MAESTRO layers end-to-end with all output formats.

### Assumptions

- MAESTRO layer classification (Feature 084) and canonical layer names (Feature 136) are merged and stable — chains reference corrected L5-L7 names.
- The existing Mermaid-to-PNG rendering pipeline (Feature 112) supports flowchart syntax for vertical layer-stack diagrams, not just tree decompositions.
- Architectures with findings in 3+ MAESTRO layers are common enough to demonstrate the feature — validated against existing examples (mermaid-agentic-app has L1/L2/L3/L7; agentic-app has 6-layer coverage).
- Rule-based correlation captures the majority of genuine cross-layer chains; edge cases are acceptable as "not detected" rather than false positives (conservative precision over recall).
- The existing Section 4a correlation detection mechanism and the new cross-layer chain correlation are independent — neither subsumes nor conflicts with the other.

### Scope Boundaries

**In Scope (P0)**:
- Cross-layer correlation engine (post-finding phase)
- Attack chains artifact
- Threat report "Attack Chains" narrative section
- PDF attack chain diagram pages
- Chain schema (new schema file)
- ADR-020 update
- At least one example architecture demonstrating a multi-layer chain
- All 6 example outputs regenerated

**Should Have (P1)**:
- Chain-breaking control highlighting in compensating-controls.md
- SARIF chain references (chain_id in result properties)

**Out of Scope**:
- Medium/Low severity chains in report/PDF (artifact only)
- Custom user-defined correlation rules
- Interactive chain visualization
- MAESTRO infographic templates for chains
- Chain-aware risk scoring (chain membership does not affect CVSS scores)
- Multi-architecture chain analysis (chains are per-architecture)
