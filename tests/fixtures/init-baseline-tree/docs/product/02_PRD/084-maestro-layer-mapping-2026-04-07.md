---
prd:
  number: "084"
  topic: maestro-layer-mapping
  created: 2026-04-07
  status: Approved
  type: feature
triad:
  pm_signoff: { agent: product-manager, date: 2026-04-07, status: APPROVED_WITH_CONCERNS, notes: "2 minor: (1) >90% coverage metric validated only against curated examples, real-world may vary; (2) primary persona diverges from vision target user — developer benefit note would strengthen alignment. No product veto warranted." }
  architect_signoff: { agent: architect, date: 2026-04-07, status: APPROVED_WITH_CONCERNS, notes: "5 findings (0 blocking, 2 medium, 3 low). All 5 technical claims validated. Medium items deferred to plan: backward compatibility verification method, Risk by MAESTRO Layer subsection placement. Low items: keyword ordering rationale, schema version bump, SARIF+baseline properties merge." }
  techlead_signoff: { agent: team-lead, date: 2026-04-07, status: APPROVED_WITH_CONCERNS, notes: "2 non-blocking: (1) timeline optimistic-edge — realistic 3d, pessimistic 4d due to 6 example regenerations; (2) coverage matrix scope gap — added to out-of-scope. All 8 dependencies verified delivered. Feasible, 75% confidence." }
source:
  idea_id: 84
  story_id: null
---

# MAESTRO Layer Mapping — CSA Seven-Layer Taxonomy Overlay for Threat Findings

**Status**: Approved
**Created**: 2026-04-07
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1 (High Confidence, Moderate Impact)
**Evidence**: LinkedIn thread — Marco M. (Founder, Threat Modeling Academy / Field CISO) asked about MAESTRO for agentic AI threat modeling

---

## Executive Summary

### The One-Liner
Tag every threat finding with its CSA MAESTRO architectural layer so security teams can filter, group, and prioritize threats by where they live in the AI stack.

### Problem Statement
tachi produces threat findings categorized by STRIDE and AI threat type, but lacks an architectural-layer dimension. Security teams reviewing output cannot quickly answer "which layer of our AI stack carries the most risk?" without manually mapping each finding to infrastructure layers. The CSA (Cloud Security Alliance) MAESTRO framework provides an industry-standard seven-layer taxonomy purpose-built for agentic AI architectures — exactly tachi's target domain.

External demand is evidenced by a LinkedIn inquiry from Marco M. (Founder, Threat Modeling Academy / Field CISO) specifically asking about MAESTRO support for agentic AI threat modeling.

### Proposed Solution
Add MAESTRO seven-layer classification as a taxonomy overlay during Phase 1 (Scope) of the tachi pipeline. Each component is classified by layer using keyword matching against its name, description, and DFD type. The layer tag propagates passively through the finding intermediate representation (IR) to all downstream outputs: threats.md, risk-scores.md, compensating-controls.md, SARIF, and narrative reports.

This is a **taxonomy overlay, not a pipeline change**. No changes to agent detection logic, scoring formulas, or dispatch rules.

### Success Criteria
- All findings in pipeline output include MAESTRO layer tags
- Layer-based risk summary available in threats.md
- SARIF consumers can filter by `maestro-layer` tag
- Zero regression in existing pipeline output when no MAESTRO layers are detected
- Example architectures updated with MAESTRO layer tags

### Timeline
Estimated 3 days (realistic), 2-4 day range — taxonomy overlay with passive field propagation. The 6 example architecture regenerations are the schedule bottleneck.

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)

tachi's vision is "the default threat modeling toolkit for any team building agentic AI applications." MAESTRO layer mapping directly strengthens this position by adopting an industry-standard taxonomy from CSA — the same organization that publishes the MAESTRO framework for agentic AI security. This makes tachi's output legible to security auditors, CISOs, and compliance teams who already think in MAESTRO layers.

### Roadmap Fit
Builds on the established pipeline architecture (Features 003, 005, 007, 010, 012, 035, 036, 078). Extends the finding IR schema without modifying core analysis logic — a low-risk enrichment that adds significant reporting value.

### Predecessor Relationship
| Feature | Relationship |
|---------|-------------|
| 003 (Orchestrator) | Phase 1 component inventory is where MAESTRO classification is added |
| 005/007 (STRIDE/AI Agents) | Agents produce findings that receive MAESTRO layer tags — no agent changes |
| 010 (Deduplication) | Correlation detection unchanged — MAESTRO tag is passive metadata |
| 012 (SARIF) | SARIF output schema extended with `maestro-layer` tag/property |
| 035 (Risk Scoring) | Layer tag propagated through scored findings — no scoring formula changes |
| 036 (Compensating Controls) | Layer tag propagated through control analysis — no control logic changes |
| 078 (Context Optimization) | Shared reference files pattern reused for MAESTRO layer definitions |

---

## Target Users & Personas

### Primary Persona: Threat Analyst
- **Role**: Security engineer reviewing tachi threat model output
- **Experience**: Intermediate-to-senior security professional, familiar with STRIDE
- **Goals**: Quickly identify which architectural layers carry the most risk
- **Pain Points**: Currently must mentally map each finding to infrastructure layers

**Why This Matters**: Layer-tagged findings enable filtering and grouping by architectural layer, reducing time to identify risk concentrations from hours to seconds.

### Secondary Persona: Security Auditor
- **Role**: Compliance/audit professional consuming SARIF output in GitHub Code Scanning or similar tooling
- **Experience**: Familiar with security scanning tools and compliance frameworks
- **Goals**: Filter security alerts by architectural layer for targeted remediation
- **Pain Points**: Generic SARIF tags lack architectural context for prioritization

### Tertiary Persona: CISO
- **Role**: Chief Information Security Officer reviewing executive risk summaries
- **Experience**: Strategic security leader, familiar with industry frameworks
- **Goals**: Communicate risk posture using industry-standard vocabulary (MAESTRO layers)
- **Pain Points**: tachi output groups by threat type, not by architectural layer — CISOs want both dimensions

---

## MAESTRO Seven-Layer Taxonomy

The CSA MAESTRO framework defines seven layers for agentic AI architectures:

| Layer | Name | Description | Example Components |
|-------|------|-------------|-------------------|
| L1 | Foundation Model | Base LLM, fine-tuned models, model weights | LLM, base model, fine-tuned model |
| L2 | Data Operations | Data pipelines feeding AI systems | Vector DB, RAG pipeline, training data, embeddings |
| L3 | Agent Framework | Orchestration and tool dispatch | Orchestrator, planner, executor, tool dispatch |
| L4 | Deployment Infrastructure | Runtime and networking | Container runtime, API gateway, load balancer |
| L5 | Security | Security services and controls | Auth service, WAF, secrets manager, audit logging |
| L6 | Agent Ecosystem | Multi-agent coordination | Multi-agent coordination, agent-to-agent protocols |
| L7 | User Interface | User-facing surfaces | Chat UI, API endpoints, admin console |

---

## User Stories

### US-1: Threat Analyst Wants Layer-Tagged Findings
**When** reviewing tachi threat model output after a pipeline run,
**I want** each finding tagged with its MAESTRO layer,
**So I can** filter and group threats by architectural layer to identify which layer carries the most risk.

**Acceptance Criteria**:
- Given a completed pipeline run, when viewing threats.md, then each finding in STRIDE and AI threat tables includes a MAESTRO Layer column
- Given a finding from a classified component, when the layer is assigned, then the layer is derived from component classification in Phase 1
- Given a finding from an unclassifiable component, when no layer keyword matches, then the finding defaults to "Unclassified"

**Priority**: P0 | **Effort**: M

### US-2: Security Auditor Wants SARIF Layer Tags
**When** consuming tachi SARIF output in GitHub Code Scanning or similar security tooling,
**I want** MAESTRO layer tags on each SARIF result,
**So I can** filter alerts by architectural layer in my security tooling.

**Acceptance Criteria**:
- Given a SARIF output file, when inspecting a result, then `properties.tags` array includes `maestro-layer:{layer-name}`
- Given a SARIF output file, when inspecting a result, then `properties` includes `maestro-layer` key with the layer name value
- Given existing SARIF consumers, when processing tachi SARIF output, then the new fields do not break existing consumers (additive only)

**Priority**: P0 | **Effort**: S

### US-3: CISO Wants Layer-Based Risk Summary
**When** reviewing the threat report for executive communication,
**I want** risk summaries grouped by MAESTRO layer,
**So I can** prioritize remediation by architectural layer and communicate risk posture using industry-standard vocabulary.

**Acceptance Criteria**:
- Given a completed pipeline run, when viewing threats.md risk summary, then a "Risk by MAESTRO Layer" subsection is present
- Given findings across multiple layers, when the summary is rendered, then each layer shows finding count and highest severity
- Given layers with zero findings, when the summary is rendered, then those layers are omitted

**Priority**: P1 | **Effort**: S

### US-4: Orchestrator Classifies Components by Layer
**When** the tachi orchestrator runs Phase 1 (Scope),
**I want** each component classified by its MAESTRO layer using keyword matching,
**So that** the layer tag is available for all downstream phases without requiring agent changes.

**Acceptance Criteria**:
- Given an architecture description with identifiable components, when Phase 1 completes, then the component inventory includes MAESTRO layer assignment
- Given the dispatch table, when displayed to user, then it includes a MAESTRO Layer column
- Given a component name, description, and DFD type, when keyword matching runs, then classification uses all three fields
- Given a component with no keyword matches, when classification completes, then it is assigned "Unclassified" (not treated as an error)

**Priority**: P0 | **Effort**: M

---

## Functional Requirements

### FR-1: MAESTRO Layer Keyword Mapping
**Description**: A shared reference file defining keyword-to-layer mappings for component classification.

**Inputs**: Component name, description, DFD type
**Processing**: Keyword matching against the MAESTRO layer keyword table
**Outputs**: Layer assignment (L1-L7 or "Unclassified")

**Business Rules**:
- Keywords are case-insensitive
- First matching layer wins (layers ordered L1-L7)
- Components matching no keywords default to "Unclassified"
- Keyword table is maintained in a shared reference file (not hardcoded in agent definitions)

### FR-2: Finding IR Schema Extension
**Description**: Add optional `maestro_layer` field to the finding intermediate representation.

**Data Model**:
```
Field: maestro_layer
Type: string (optional)
Values: "L1 — Foundation Model" | "L2 — Data Operations" | ... | "L7 — User Interface" | "Unclassified"
Default: "Unclassified"
```

**Business Rules**:
- Field is optional — absent field treated as "Unclassified"
- No changes to existing IR fields
- Downstream agents propagate the field without modification

### FR-3: Output Schema Extensions
**Description**: Add MAESTRO Layer column to threat tables and layer summary to risk section in threats.md.

**Outputs Modified**:
- threats.md: STRIDE table gains MAESTRO Layer column
- threats.md: AI threat table gains MAESTRO Layer column
- threats.md: Risk summary gains "Risk by MAESTRO Layer" subsection
- risk-scores.md: Layer tag propagated (no scoring formula changes)
- compensating-controls.md: Layer tag propagated (no control logic changes)

### FR-4: SARIF Output Extension
**Description**: Add MAESTRO layer metadata to each SARIF result.

**SARIF Changes**:
- `result.properties.tags[]` gains `"maestro-layer:{layer-name}"` entry
- `result.properties.maestro-layer` gains layer name string value
- Changes are additive — no existing SARIF fields modified or removed

---

## Non-Functional Requirements

### Backward Compatibility (NON-NEGOTIABLE)
- Existing pipeline output must remain unchanged when no MAESTRO layers are detected
- SARIF consumers must not break from additive field additions
- All new fields are optional with sensible defaults

### Performance
- Keyword matching adds negligible overhead to Phase 1 (string matching against <100 keywords)
- No additional API calls, network requests, or model invocations required

### Maintainability
- MAESTRO layer definitions stored in shared reference file following Feature 078 pattern
- Keyword table is human-editable without code changes
- New layers can be added by extending the reference file

---

## Success Metrics

### Primary Metrics
- **Layer Classification Coverage**: >90% of components in example architectures receive a non-"Unclassified" layer assignment
- **Output Completeness**: 100% of findings in threats.md, risk-scores.md, compensating-controls.md, and SARIF include `maestro_layer` field
- **Zero Regression**: Existing pipeline output byte-identical (excluding new MAESTRO columns) on example architectures

### Adoption Indicators
- MAESTRO layer grouping used in executive summaries and threat reports
- SARIF `maestro-layer` filter adopted by security teams using GitHub Code Scanning

---

## Scope & Boundaries

### In Scope (P0 — This PRD)
- MAESTRO layer keyword mapping reference file
- Phase 1 component classification by MAESTRO layer
- Dispatch table MAESTRO Layer column
- Finding IR `maestro_layer` field
- threats.md MAESTRO Layer columns in STRIDE and AI tables
- threats.md "Risk by MAESTRO Layer" summary subsection
- risk-scores.md layer tag propagation
- compensating-controls.md layer tag propagation
- SARIF `maestro-layer` tag and property per result
- Example architecture output updates

### Out of Scope
- Agent detection logic changes (all 11 agents unchanged)
- Scoring formula changes (CVSS, exploitability, scalability, reachability weights unchanged)
- Dispatch rule changes (STRIDE-per-Element and AI keyword dispatch unchanged)
- Correlation detection rule changes (5 deterministic rules unchanged)
- Compensating controls analysis logic changes (8 control categories unchanged)
- Residual risk calculation changes (reduction factors unchanged)
- MAESTRO-based scoring adjustments (layer does not affect risk scores)
- Custom layer definitions (users cannot add layers in this phase)
- Coverage Matrix MAESTRO Layer column (future enhancement)
- Narrative threat report MAESTRO grouping (future enhancement)
- PDF security report MAESTRO integration (future enhancement)

### Assumptions
- CSA MAESTRO seven-layer taxonomy is stable and will not change significantly in the near term
- Keyword matching provides sufficient classification accuracy for the initial release
- "Unclassified" is an acceptable default for components that don't match any layer keywords

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: Keyword matching produces low-quality classifications
- **Likelihood**: Low (MAESTRO layers map well to standard component naming)
- **Impact**: Medium (poor classification reduces value of layer grouping)
- **Mitigation**: Validate against all example architectures before release; tune keyword table iteratively

**Risk 2**: SARIF consumers reject unknown properties
- **Likelihood**: Very Low (SARIF spec allows arbitrary properties)
- **Impact**: Medium (breaks integration for affected consumers)
- **Mitigation**: Fields are additive; test with GitHub Code Scanning specifically

### Dependencies

**Internal Dependencies**:
- Feature 078 shared reference pattern (delivered) — reuse for MAESTRO layer definitions
- Orchestrator Phase 1 component inventory (delivered) — extension point for classification
- Finding IR schema (delivered) — extension point for new field

**External Dependencies**:
- CSA MAESTRO framework specification — layer definitions and descriptions

---

## Definition of Done

- [ ] MAESTRO layer classification added to Phase 1 component inventory
- [ ] Dispatch table includes MAESTRO Layer column
- [ ] Finding IR schema extended with optional `maestro_layer` field
- [ ] threats.md STRIDE and AI tables include MAESTRO Layer column
- [ ] threats.md risk summary includes "Risk by MAESTRO Layer" subsection
- [ ] risk-scores.md propagates layer tag (no scoring formula changes)
- [ ] compensating-controls.md propagates layer tag (no control logic changes)
- [ ] SARIF output includes `maestro-layer` tag and property per result
- [ ] Existing pipeline output unchanged when no MAESTRO layers detected (backward compatible)
- [ ] Example architectures updated with MAESTRO layer tags in output
- [ ] No changes to agent detection logic, scoring formulas, or dispatch rules validated

---

## Open Questions

### Product Questions
- [ ] Should the narrative threat report (threat-report.md) include MAESTRO layer grouping in this phase, or defer to a follow-up? — product-manager — 2026-04-07 — Open
- [ ] Should the PDF security report include a MAESTRO layer breakdown page? — product-manager — 2026-04-07 — Open
- [ ] Should the infographic templates support MAESTRO layer visualization? — product-manager — 2026-04-07 — Open

### Technical Questions (from Architect review)
- [ ] "Risk by MAESTRO Layer" subsection placement within output schema ordering (after existing Risk Level table in Section 6, or new Section 6a?) — architect — 2026-04-07 — Deferred to plan
- [ ] Backward compatibility verification method: diff-based regression test vs. feature flag? — architect — 2026-04-07 — Deferred to plan
- [ ] Schema version bump (1.1 → 1.2) to signal MAESTRO field presence? — architect — 2026-04-07 — Deferred to plan
- [ ] SARIF properties merge behavior when baseline mode + MAESTRO are both active — architect — 2026-04-07 — Deferred to plan
- [ ] Keyword table ordering rationale documentation (first-match-wins is load-bearing) — architect — 2026-04-07 — Deferred to plan

---

## References

### Product Documentation
- Product Vision: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)
- GitHub Issue: [#84](https://github.com/davidmatousek/tachi/issues/84)

### Technical Documentation
- Constitution: [constitution.md](.aod/memory/constitution.md)
- Architecture: [README.md](docs/architecture/README.md)
- Shared References Pattern: Feature 078 (Agent Context Optimization)

### External Resources
- CSA MAESTRO Framework: Cloud Security Alliance seven-layer taxonomy for agentic AI architectures
