---
prd:
  number: "141"
  topic: maestro-cross-layer-attack-chains
  created: 2026-04-12
  status: Approved
  type: feature
triad:
  pm_signoff: { agent: product-manager, date: 2026-04-12, status: APPROVED, notes: "PRD delivers the canonical MAESTRO differentiator — cross-layer attack chains transform flat findings into actionable attack stories. Correctly scoped with clear P0/P1 separation." }
  architect_signoff: { agent: architect, date: 2026-04-12, status: APPROVED_WITH_CONCERNS, notes: "6 findings (0 blocking, 3 medium, 3 low). MEDIUM: (1) Phase placement resolved to Phase 3.5 — attack-chains artifact must exist before threat-report agent; (2) Mermaid reuse clarified — Python pipeline reusable, new attack-chain.typ template needed; (3) agentic-app example best chain demonstration candidate (6 layers). LOW: (1) chain-to-Section-4a independence clarified; (2) chain-breaking controls qualified as heuristic; (3) backward-compat requires zero-output when has-attack-chains is false." }
  techlead_signoff: { agent: team-lead, date: 2026-04-12, status: APPROVED_WITH_CONCERNS, notes: "2 items addressed in PRD: (1) timeline updated 5-7d to 8-12d with 3 milestones; (2) Phase 3.5 insertion resolved. 3 non-blocking: start rule-based only for v1, prototype Mermaid chain template early, define semantic relationship as lookup table not interpretation. Parallel execution potential: 3 waves, Wave 2 has 3 parallel tracks." }
source:
  idea_id: 141
  story_id: null
---

# MAESTRO Phase 2: Cross-Layer Attack Chain Analysis

**Status**: Approved
**Created**: 2026-04-12
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1 (High)
**Evidence**: Canonical CSA MAESTRO sources (CSA blog, Snyk Labs, Practical DevSecOps) all describe cross-layer attack chain analysis as the defining MAESTRO capability. ICE: Impact 9, Confidence 6, Effort 5 = 20.

---

## Executive Summary

### The One-Liner
Surface cascading attack chains across the MAESTRO seven-layer taxonomy so security teams see how an exploit at one layer enables exploits at adjacent layers, ending in concrete business impact.

### Problem Statement
Tachi treats MAESTRO as a static post-hoc label on each finding. There is no correlation logic, no narrative walkthrough, and no visualization of how findings relate across layers. Adopters reading the threat report see individual findings with layer tags (L1 Foundation Model through L7 Agent Ecosystem) but have no way to understand cascading vertical risk. The canonical MAESTRO deliverable — vertical attack chain analysis showing how exploits propagate across the seven-layer taxonomy — is entirely absent.

The canonical CSA MAESTRO worked example walks an attack path through all seven layers of a multi-agent financial trading system: L1 adversarial examples poisoning price predictions, L2 corrupting historical market data, L3 workflow hijacking via prompt injection, L4 container escape, L5 log injection hiding trades, L6 policy manipulation disabling compliance, and L7 agent impersonation establishing false trust. Tachi today implements none of this. This is the single biggest gap between tachi's MAESTRO implementation and the canonical specification.

### Proposed Solution
Add a post-finding cross-layer correlation phase that groups related findings into vertical attack chains based on component lineage, data flow dependencies, and MAESTRO layer adjacency. Each chain is surfaced as:

1. A structured **attack-chains artifact** alongside threats.md, enumerating chain membership with finding IDs and layer progression
2. A narrative **Attack Chains section** in the threat report walking Critical and High chains through cascading layer propagation
3. **Chain diagram pages** in the PDF security report rendered as Mermaid diagrams, reusing the existing Mermaid-to-PNG pipeline from Feature 112

### Success Criteria
- Orchestrator produces an attack-chains artifact enumerating cross-layer chains with finding IDs and layer progression
- Threat report includes an Attack Chains narrative section for Critical and High chains
- PDF security report renders chain diagrams as dedicated pages
- At least one example architecture demonstrates a multi-layer chain end-to-end
- ADR-020 updated to document the cross-layer correlation architecture
- Backward compatible: architectures without detectable chains render correctly with no new sections

### Timeline
Estimated 8-12 days — multi-component feature touching orchestration, narrative generation, and PDF assembly. Three milestone boundaries: (a) correlation engine validated against 1 example (day 4), (b) full artifact chain validated end-to-end (day 8), (c) all 6 examples regenerated + regression (day 12). The correlation engine design decision and example architecture regeneration are the schedule bottlenecks.

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)

Tachi's vision is "the default threat modeling toolkit for any team building agentic AI applications." Cross-layer attack chain analysis is the defining capability that separates MAESTRO-aware tooling from generic STRIDE tools with layer tags. By implementing the canonical MAESTRO deliverable, tachi moves from "STRIDE tool with MAESTRO metadata" to "full MAESTRO implementation," directly strengthening its position as the default toolkit for agentic AI threat modeling.

### Roadmap Fit
This is Phase 2 of the MAESTRO compliance initiative (parent [#136](https://github.com/davidmatousek/tachi/issues/136)). It builds on the established MAESTRO taxonomy overlay (Feature 084), the canonical layer name corrections (Feature 136), and the attack path visualization pipeline (Feature 112). It extends the pipeline from passive layer tagging to active cross-layer analysis — the first pipeline-level change driven by MAESTRO.

### Predecessor Relationship
| Feature | Relationship |
|---------|-------------|
| 084 (MAESTRO Layer Mapping) | Provides the L1-L7 layer classification that chains traverse — prerequisite taxonomy |
| 136 (MAESTRO Canonical Layer Correctness) | Corrected L5/L6/L7 names — chains reference canonical names — prerequisite |
| 112 (Attack Path Pages) | Mermaid-to-PNG rendering pipeline reused for chain diagrams — infrastructure dependency |
| 130 (Fix Attack Path Mermaid Rendering) | mmdc hard prerequisite — chain diagrams require mmdc when present |
| 015 (Threat Report & Attack Trees) | Attack trees are per-finding; chains are cross-finding — complementary, not overlapping |
| 104 (Downstream Baseline Propagation) | Baseline status fields propagate through chains — passive compatibility |
| 091 (MAESTRO Infographics) | MAESTRO heatmap and stack templates may surface chain data in future — not in scope |
| 003 (Orchestrator) | New correlation phase added to orchestrator pipeline — extension point |

---

## Target Users & Personas

### Primary Persona: Security Engineer
- **Role**: Security engineer running tachi on agentic AI systems
- **Experience**: Intermediate-to-senior, familiar with STRIDE and MAESTRO frameworks
- **Goals**: Reason about cascading vertical risk propagation across architectural layers
- **Pain Points**: Currently must manually correlate individual findings across STRIDE categories and MAESTRO layers to identify attack chains

**Why This Matters**: Cross-layer chains transform a flat list of 50-70 individual findings into 3-5 actionable attack stories, each showing how an initial exploit cascades through the stack to business impact. Security engineers can prioritize remediation based on chain-breaking controls rather than treating each finding independently.

### Secondary Persona: CISO / Security Leadership
- **Role**: Chief Information Security Officer reviewing PDF security assessment
- **Experience**: Strategic security leader, limited time for finding-level detail
- **Goals**: Brief executives on end-to-end business impact of agentic AI risks
- **Pain Points**: Individual findings don't tell a story; board members need visual, self-contained chain narratives showing how attacks propagate vertically

**Why This Matters**: A single chain diagram showing L2 data poisoning to L3 workflow hijack to L7 unauthorized action is a board-ready slide. No translation needed from technical findings to business impact.

### Tertiary Persona: MAESTRO Practitioner
- **Role**: Threat modeler adopting MAESTRO methodology
- **Experience**: Familiar with CSA MAESTRO framework, evaluating tools
- **Goals**: Produce the canonical MAESTRO deliverable (cross-layer attack propagation narratives)
- **Pain Points**: Tachi currently produces STRIDE findings with MAESTRO tags, not the canonical MAESTRO output

**Why This Matters**: Cross-layer attack chain analysis is the litmus test for whether a tool is a "MAESTRO implementation" or "STRIDE with MAESTRO labels." This feature makes tachi pass that test.

---

## User Stories

### US-1: Security Engineer Wants Cross-Layer Chains in Threat Report
**When** reviewing tachi threat model output after a pipeline run on an agentic system,
**I want** the threat report to show cross-layer attack chains for Critical and High findings,
**So I can** reason about cascading vertical risk propagation without manually correlating findings across STRIDE categories.

**Acceptance Criteria**:
- **Given** a completed pipeline run with findings across multiple MAESTRO layers, **when** viewing threat-report.md, **then** a new "Attack Chains" section enumerates each detected cross-layer chain with finding IDs and layer progression (e.g., L2 Data Operations -> L3 Agent Framework -> L7 Agent Ecosystem)
- **Given** a chain spanning 3+ layers with a Critical finding, **when** viewing the chain narrative, **then** it includes: initial exploit description, intermediate cascade steps with layer transitions, and final business impact
- **Given** an architecture with findings in only one MAESTRO layer, **when** the pipeline runs, **then** no Attack Chains section is generated (no false chains)

**Priority**: P0 | **Effort**: L

### US-2: CISO Wants Visual Chain Diagrams in PDF
**When** reviewing the PDF security assessment for board communication,
**I want** a visual attack chain diagram showing how an exploit at one layer enables exploits at adjacent layers,
**So I can** brief executives on end-to-end business impact using a single image instead of reading individual findings.

**Acceptance Criteria**:
- **Given** a threat report with attack chains, **when** the PDF is generated, **then** each Critical and High chain appears as a dedicated page with a rendered Mermaid diagram showing layer-to-layer propagation
- **Given** a chain diagram page, **when** I view it, **then** it includes: chain title, rendered diagram with layer labels (L1-L7), narrative explanation, and impacted finding IDs
- **Given** a report with no detectable chains, **when** the PDF is generated, **then** no chain pages are included and no errors occur

**Priority**: P0 | **Effort**: L

### US-3: Threat Modeler Wants Causal Relationships Between Findings
**When** analyzing threat model output for remediation prioritization,
**I want** the orchestrator to surface which findings share a causal relationship across layers,
**So I can** prioritize remediation based on chain-breaking controls rather than treating each finding as independent.

**Acceptance Criteria**:
- **Given** a completed pipeline run, **when** viewing the attack-chains artifact, **then** each chain lists its member findings with their MAESTRO layers and the causal relationship between adjacent findings
- **Given** a chain where remediating one finding would break the chain, **when** viewing remediation recommendations, **then** chain-breaking controls are highlighted
- **Given** findings with no cross-layer relationship, **when** viewing the artifact, **then** they do not appear in any chain (no false grouping)

**Priority**: P0 | **Effort**: L

### US-4: MAESTRO Practitioner Wants Canonical Deliverables
**When** evaluating tachi as a MAESTRO-compliant threat modeling tool,
**I want** tachi to produce the canonical MAESTRO deliverable (cross-layer attack propagation narratives),
**So that** tachi is recognized as a full MAESTRO implementation rather than a STRIDE tool with MAESTRO metadata.

**Acceptance Criteria**:
- **Given** the agentic-app example (or a purpose-built example), **when** the full pipeline runs, **then** the output includes at least one cross-layer chain spanning 3+ layers with narrative walkthrough
- **Given** the chain narrative, **when** compared to the canonical CSA MAESTRO worked example format, **then** it follows the same structure: initial exploit, intermediate cascades, business impact
- **Given** the chain diagram, **when** rendered, **then** it visually shows the seven-layer stack with attack progression arrows between affected layers

**Priority**: P1 | **Effort**: M

### US-5: Adopter Wants Example Demonstrating End-to-End Chain
**When** evaluating tachi before adopting it for my organization,
**I want** at least one example architecture to demonstrate a multi-layer chain end-to-end,
**So I can** see what the capability looks like before committing to adoption.

**Acceptance Criteria**:
- **Given** the examples directory, **when** inspecting at least one example, **then** its output includes an attack-chains artifact with a chain spanning 3+ MAESTRO layers
- **Given** the example chain, **when** the PDF is regenerated, **then** it includes chain diagram pages demonstrating the full visualization capability
- **Given** the example, **when** a new user runs the pipeline, **then** the chain output is reproducible (deterministic correlation)

**Priority**: P1 | **Effort**: M

---

## Functional Requirements

### FR-1: Cross-Layer Correlation Engine
**Description**: A new post-finding correlation phase in the orchestrator pipeline that identifies cross-layer attack chains by analyzing relationships between findings across MAESTRO layers.

**Inputs**:
- Deduplicated findings with MAESTRO layer assignments (from Phase 1 classification + Phase 2 detection + Phase 3 deduplication)
- Architecture description (component relationships, data flows, trust boundaries)

**Processing**:
1. Group findings by target component and MAESTRO layer
2. Identify cross-layer relationships using correlation signals:
   - **Component lineage**: Findings targeting components connected by data flows
   - **Data flow dependencies**: Findings on components that share data flow paths
   - **Layer adjacency**: Findings in adjacent MAESTRO layers (L(n) to L(n+1)) affecting related components
   - **Semantic relationship**: Findings where one finding's exploit enables another's (e.g., data poisoning at L2 enables workflow hijack at L3)
3. Assemble chains: ordered sequences of findings forming a coherent attack progression from initial exploit to business impact
4. Filter: retain only chains spanning 2+ layers with at least one Critical or High finding
5. Rank: order chains by maximum severity, then by chain length (longer = more impactful)

**Outputs**:
- Attack chain data structure: list of chains, each containing ordered finding references with layer progression and causal narrative
- Boolean flag `has-attack-chains` for conditional downstream inclusion

**Business Rules**:
- A finding can appear in multiple chains (many-to-many relationship)
- Cross-layer chains and existing Section 4a correlation groups (CR-1 through CR-5) are independent grouping mechanisms — a finding may appear in both without conflict
- Chains must span at least 2 distinct MAESTRO layers
- Only chains containing at least one Critical or High finding are surfaced
- Maximum chain length: 7 (one per layer — full-stack chain)
- Chains are deterministic: same input produces same chains every run

**Design Decision** (resolved per Architect + Team-Lead review):
- **Option A — Rule-based** (selected for v1): Explicit correlation patterns keyed on STRIDE category + MAESTRO layer + component type + data flow connectivity. Deterministic, auditable, and ADR-021 compliant by construction. Semantic relationship detection is implemented as a lookup table mapping (STRIDE category, MAESTRO layer) pairs to valid successor pairs — not interpretive judgment.
- **Option B — Hybrid** (future follow-up): Add LLM-assisted narrative synthesis for richer causal explanations. The structural correlation remains rule-based; only the narrative prose generation uses LLM (matching the existing threat-report agent pattern).
- **Option C — LLM-assisted**: Rejected — non-deterministic, conflicts with ADR-021.

### FR-2: Attack Chains Artifact
**Description**: A new output artifact (`attack-chains.md`) produced alongside threats.md that enumerates all detected cross-layer attack chains.

**Schema** (proposed):
```markdown
# Attack Chains

## Chain Summary
| Chain ID | Layers | Max Severity | Findings | Initial Exploit | Business Impact |

## Chain Details

### CHAIN-001: [Chain Title]
**Layers**: L2 -> L3 -> L7
**Max Severity**: Critical
**Findings**: [F-ID-1, F-ID-2, F-ID-3]

**Attack Progression**:
1. **L2 (Data Operations)**: [Finding description] — [How this enables next step]
2. **L3 (Agent Framework)**: [Finding description] — [How this enables next step]
3. **L7 (Agent Ecosystem)**: [Finding description] — [Business impact]

**Chain-Breaking Controls** (heuristic — identifies structurally central findings, not verified control effectiveness):
- Remediating [F-ID-2] at L3 breaks the chain (narrowest point in the chain)
- [Specific control recommendation]
```

**Business Rules**:
- Artifact is conditional: only produced when `has-attack-chains` is true
- Schema versioning follows existing `schemas/` convention
- Finding references use existing finding ID format from threats.md
- Backward compatible: pipeline runs without chains produce no artifact

### FR-3: Threat Report Attack Chains Section
**Description**: A new section in `threat-report.md` that narratively walks through each Critical and High attack chain.

**Placement**: New section after existing Attack Trees section (Section 5) — Section 6 "Cross-Layer Attack Chains"

**Content per chain**:
- Chain title and layer progression
- Narrative walkthrough: initial exploit, intermediate cascades, business impact
- Impacted finding IDs with cross-references to findings detail
- Chain-breaking control recommendations

**Business Rules**:
- Section is conditional: only included when attack chains exist
- Narrative is generated by the threat-report agent (extends existing narrative generation)
- Each chain narrative is 150-300 words (concise but complete)
- Chains ordered by severity (Critical first), then by chain length

### FR-4: PDF Attack Chain Pages
**Description**: New pages in the PDF security report rendering cross-layer attack chains as Mermaid diagrams.

**Reuse**: The Python-level Mermaid rendering pipeline from Feature 112 (`render_mermaid_to_png()` with ThreadPoolExecutor, mmdc preflight, error aggregation) is reused for image generation. A **new Typst template** (`attack-chain.typ`) is required because chain diagrams have a fundamentally different layout than attack trees — vertical MAESTRO layer stacks with progression arrows, not branching tree decompositions.

**Layout** (portrait, A4/Letter):
- **Header**: Chain ID badge + Chain title + Layer progression (e.g., "L2 -> L3 -> L7")
- **Diagram Section**: Rendered Mermaid flowchart showing vertical layer stack (L1 at top, L7 at bottom) with attack progression arrows pointing downward between affected layers
- **Narrative Section**: Condensed chain walkthrough
- **Impacted Findings**: List of finding IDs in the chain
- **Footer**: Standard page numbering

**Placement**: After Attack Path pages (Feature 112), before Findings Detail. Conditional on `has-attack-chains`.

**Business Rules**:
- Reuses `mmdc` hard prerequisite from Feature 130 (ADR-022)
- Each chain gets one page (no multi-page chains)
- Diagram uses MAESTRO layer colors (distinct from attack tree red/orange/green scheme)
- Gated by `has-attack-chains` boolean — no pages when no chains detected

### FR-5: Finding Schema Extension
**Description**: Extend the finding schema to support chain membership references.

**Option A — Finding-level references**:
```yaml
# schemas/finding.yaml addition
chain_ids:
  type: array
  items: string
  description: "IDs of attack chains this finding belongs to"
  default: []
```

**Option B — Separate chain schema** (recommended):
```yaml
# schemas/attack-chain.yaml (new)
schema_version: "1.0"
chain_id: string
title: string
layers: array of string  # ["L2", "L3", "L7"]
max_severity: string
findings: array of { finding_id, maestro_layer, role_in_chain }
narrative: string
chain_breaking_controls: array of string
```

**Business Rules**:
- Schema choice to be resolved in spec/plan
- If Option A: finding.yaml schema_version bumps from 1.3 to 1.4
- If Option B: new schema file, finding.yaml unchanged
- Both options are backward compatible (new fields are optional/additive)

### FR-6: ADR-020 Update
**Description**: Update ADR-020 to document the transition from "taxonomy overlay, not a pipeline change" to active cross-layer correlation.

**Content**:
- New "Phase 2" section documenting the correlation architecture
- Updated "Decision" to reflect that MAESTRO now includes active analysis, not just passive tagging
- Cross-reference to the new attack-chain schema

---

## Non-Functional Requirements

### Backward Compatibility (NON-NEGOTIABLE)
- Existing pipeline output must remain unchanged when no cross-layer chains are detected
- All new sections and pages are conditionally gated (same pattern as `has-maestro-data`, `has-attack-trees`)
- Existing attack trees (Feature 112) are unaffected — chains complement, not replace
- All 6 example outputs regenerated and validated

### Determinism
- Correlation engine must produce identical chains for identical input (per ADR-021)
- If hybrid approach chosen (FR-1 Option B), structural correlation must be deterministic; only narrative synthesis may use LLM
- Chain ordering is deterministic (severity, then chain length, then alphabetical chain ID)

### Performance
- Correlation phase adds <10s to pipeline runtime for architectures with <100 findings
- No additional external API calls for rule-based correlation
- Mermaid rendering reuses existing Feature 112 pipeline — no new rendering infrastructure

### Maintainability
- Correlation patterns stored in a shared reference file (following Feature 078 pattern)
- Chain schema is human-readable markdown (following threats.md convention)
- New pipeline phase is modular — can be disabled without affecting other phases

---

## Success Metrics

### Primary Metrics

**Chain Detection Coverage**:
- **Definition**: Percentage of architectures with findings in 3+ MAESTRO layers that produce at least one cross-layer chain
- **Target**: >80% of qualifying architectures produce at least one chain

**Chain Quality**:
- **Definition**: Percentage of detected chains that represent genuine causal relationships (not false groupings)
- **Target**: >90% precision (validated against example architectures)

**Output Completeness**:
- **Definition**: All detected chains appear in attack-chains.md, threat-report.md narrative, and PDF chain pages
- **Target**: 100% propagation through all output formats

### Adoption Indicators
- MAESTRO practitioners recognize tachi output as canonical MAESTRO deliverables
- Chain diagrams used in board-level security briefings
- Remediation prioritization shifts from individual findings to chain-breaking controls

---

## Scope & Boundaries

### In Scope (P0 — This PRD)
- Cross-layer correlation engine (post-finding phase in orchestrator)
- Attack chains artifact (`attack-chains.md`)
- Threat report "Attack Chains" narrative section
- PDF attack chain diagram pages (reusing Feature 112 Mermaid pipeline)
- Chain schema (new or extended finding schema)
- ADR-020 update documenting correlation architecture
- At least one example architecture demonstrating a multi-layer chain
- All 6 example outputs regenerated

### Should Have (P1)
- Chain-breaking control highlighting in compensating-controls.md
- SARIF chain references (chain_id in result properties)

### Out of Scope
- Medium/Low severity chains (only Critical/High chains are surfaced)
- Custom correlation rules (users cannot define their own chain patterns in this phase)
- Interactive chain visualization (PDF is static)
- MAESTRO infographic templates for chains (future enhancement)
- Chain-aware risk scoring (chain membership does not affect CVSS scores in this phase)
- Automated chain validation against CSA worked examples
- Multi-architecture chain analysis (chains are per-architecture, not cross-architecture)

### Assumptions
- Feature 136 (canonical layer names) is merged and stable — chains reference corrected L5/L6/L7 names
- Feature 112 Mermaid-to-PNG pipeline works for chain diagrams (flowcharts, not just tree diagrams)
- Architectures with findings in 3+ MAESTRO layers are common enough to demonstrate the feature (validated against existing examples)
- Rule-based correlation captures the majority of genuine cross-layer chains; edge cases are acceptable as "not detected" rather than false positives

### Constraints

**Technical Constraints**:
- Deterministic correlation is required (ADR-021) — full LLM-based correlation is not acceptable for the structural phase
- Chain diagrams require `mmdc` (Feature 130 hard prerequisite) — chain pages are conditional on mmdc availability
- Mermaid flowchart syntax may need adaptation for vertical layer-stack rendering

**External Dependencies**:
- CSA MAESTRO framework specification for canonical worked example format
- `mmdc` (Mermaid CLI) for chain diagram rendering — same dependency as Feature 112/130

---

## Risks & Dependencies

### Technical Risks

**Risk 141.1**: Correlation quality — false positive chains
- **Likelihood**: Medium
- **Impact**: High (false chains undermine credibility of the entire feature)
- **Mitigation**: Conservative correlation rules (require component lineage OR data flow dependency, not just layer adjacency); validate against all 6 examples before release
- **Contingency**: Add confidence score per chain; only surface high-confidence chains in v1

**Risk 141.2**: Chain explosion — too many chains generated
- **Likelihood**: Medium (complex architectures with many findings across layers)
- **Impact**: Medium (PDF becomes unwieldy with 20+ chain pages)
- **Mitigation**: Cap surfaced chains at top 5 by severity x chain length; include full list in attack-chains.md artifact
- **Contingency**: Add configurable chain limit

**Risk 141.3**: Design decision delays — rule-based vs hybrid correlation
- **Likelihood**: Low (issue already identifies hybrid as recommended)
- **Impact**: Medium (wrong choice requires rework in spec/plan)
- **Mitigation**: Resolve in spec phase with architect review; prototype both approaches against agentic-app example
- **Contingency**: Start with rule-based only; add LLM narrative synthesis as follow-up

**Risk 141.4**: Mermaid diagram complexity for chain visualization
- **Likelihood**: Low (chains have 7 or fewer nodes, one per layer)
- **Impact**: Low (diagram scaling, not a fundamental blocker)
- **Mitigation**: Design chain diagram Mermaid template with fixed vertical layout; test with maximum 7-layer chain

### Dependencies

**Internal Dependencies**:
- **Feature 084** (MAESTRO Layer Mapping): Provides L1-L7 classification — DELIVERED
- **Feature 136** (MAESTRO Canonical Layer Correctness): Provides correct layer names — DELIVERED
- **Feature 112** (Attack Path Pages): Mermaid-to-PNG rendering pipeline — DELIVERED
- **Feature 130** (mmdc Hard Prerequisite): Chain diagrams require mmdc — DELIVERED
- **Feature 015** (Threat Report): Narrative generation patterns reused — DELIVERED
- **Feature 003** (Orchestrator): Pipeline phase extension point — DELIVERED

**External Dependencies**:
- CSA MAESTRO framework specification (canonical worked example format)
- `mmdc` (Mermaid CLI) for chain diagram rendering

**Dependency Graph**:
```
[Cross-Layer Attack Chain Analysis (141)]
  +-- Depends on: Feature 084 (MAESTRO Layer Mapping) — DELIVERED
  +-- Depends on: Feature 136 (Canonical Layer Names) — DELIVERED
  +-- Depends on: Feature 112 (Attack Path Pages / Mermaid Pipeline) — DELIVERED
  +-- Depends on: Feature 130 (mmdc Hard Prerequisite) — DELIVERED
  +-- External: mmdc (Mermaid CLI) for diagram rendering
  +-- External: CSA MAESTRO spec for canonical format reference
```

---

## Definition of Done

- [ ] Orchestrator produces an attack-chains artifact alongside threats.md that enumerates cross-layer chains with finding IDs
- [ ] Cross-layer correlation is deterministic: same input produces same chains every run
- [ ] Threat report includes an Attack Chains section walking Critical and High chains through layer cascades
- [ ] PDF security report renders chain diagrams as dedicated pages (reusing Feature 112 Mermaid pipeline)
- [ ] At least one example architecture demonstrates a multi-layer chain spanning 3+ layers end-to-end
- [ ] ADR-020 updated (or new ADR created) documenting the cross-layer correlation architecture
- [ ] Chain schema documented (new schema file or extended finding.yaml)
- [ ] Backward compatible: architectures without detectable chains produce identical output to pre-feature
- [ ] All 6 example pipeline outputs regenerated
- [ ] Backward-compatibility test: 5 baseline PDFs byte-identical under `SOURCE_DATE_EPOCH=1700000000` (per ADR-021) for architectures without chains
- [ ] Chain pages gated by `has-attack-chains` boolean (conditional inclusion)
- [ ] `/aod.analyze` passes with no inconsistencies

---

## Open Questions

### Product Questions
- [ ] Should the attack-chains artifact include Medium-severity chains for completeness, even if they're not surfaced in the report/PDF? — product-manager — 2026-04-19 — Open
- [ ] Should chain-breaking control recommendations be integrated into compensating-controls.md in this phase, or deferred? — product-manager — 2026-04-19 — Open

### Technical Questions (resolved per Architect + Team-Lead review)
- [x] Rule-based vs hybrid correlation: Which approach for v1? — architect — 2026-04-12 — **Answered: Rule-based only for v1** (ADR-021 compliant by construction; LLM narrative as fast-follow)
- [x] Separate attack-chain schema (new file) vs extended finding.yaml (chain_ids field)? — architect — 2026-04-12 — **Answered: Separate schema** (`schemas/attack-chain.yaml`) — chains are cross-finding aggregates, not finding-level properties; avoids bumping finding.yaml to v1.4
- [x] Should chain correlation run as a new Phase 3.5 (post-dedup, pre-scoring) or as part of Phase 6 (reporting)? — architect — 2026-04-12 — **Answered: Phase 3.5** (post-dedup, pre-report) — attack-chains artifact must exist before the threat-report agent runs in Phase 5
- [x] Mermaid diagram layout for chains: vertical layer stack vs horizontal flow? — architect — 2026-04-12 — **Answered: Vertical layer stack** (top-to-bottom, L1 at top, L7 at bottom) — matches how security engineers reason about attack propagation "down the stack"
- [x] Should the existing agentic-app example be extended to demonstrate chains, or should a new purpose-built example be created? — architect — 2026-04-12 — **Answered: Extend agentic-app** (richest MAESTRO coverage at 6 layers; adding 1-2 components for stronger cross-layer data flows is less work than a 7th example)

---

## References

### Product Documentation
- Product Vision: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)
- GitHub Issue: [#141](https://github.com/davidmatousek/tachi/issues/141)
- Parent Issue: [#136](https://github.com/davidmatousek/tachi/issues/136) (MAESTRO framework compliance)

### Related PRDs
- [PRD 084: MAESTRO Layer Mapping](084-maestro-layer-mapping-2026-04-07.md) — taxonomy overlay this feature extends
- [PRD 136: MAESTRO Canonical Layer Correctness](136-maestro-canonical-layer-correctness-fix-2026-04-10.md) — corrected layer names
- [PRD 112: Attack Path Pages](112-attack-path-pages-in-pdf-2026-04-09.md) — Mermaid-to-PNG pipeline reused
- [PRD 130: Fix Attack Path Mermaid Rendering](130-fix-attack-path-mermaid-rendering-2026-04-11.md) — mmdc hard prerequisite
- [PRD 015: Threat Report & Attack Trees](015-threat-report-agent-attack-trees-2026-03-23.md) — narrative generation patterns
- [PRD 091: MAESTRO Infographic Templates](091-maestro-infographic-templates-and-pdf-report-section-2026-04-08.md) — MAESTRO visualization precedent

### Technical Documentation
- [ADR-020: MAESTRO Layer Classification](docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md) — current architecture (to be updated)
- [ADR-021: SOURCE_DATE_EPOCH for Deterministic PDF](docs/architecture/02_ADRs/ADR-021-source-date-epoch-deterministic-pdf.md) — determinism constraint
- [ADR-022: mmdc Hard Prerequisite](docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md) — chain diagram dependency

### External Resources
- CSA Blog: Agentic AI Threat Modeling Framework, MAESTRO (2025-02-06)
- Snyk Labs: MAESTRO, Layered Threat Modeling for Agentic AI Ecosystems — canonical multi-agent financial trading worked example
- Practical DevSecOps: MAESTRO, An Agentic AI Threat Modeling Framework

---

## Approval & Sign-Off

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | Approved | 2026-04-12 | Canonical MAESTRO differentiator; correctly scoped P0/P1 |
| Architect | architect | Approved with Concerns | 2026-04-12 | 3M/3L findings; Phase 3.5 resolved, Typst template clarified, agentic-app for demo |
| Team Lead | team-lead | Approved with Concerns | 2026-04-12 | Timeline updated to 8-12d; rule-based v1; 3-wave parallel execution |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-12 | product-manager | Initial PRD |
