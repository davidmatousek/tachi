---
prd_reference: docs/product/02_PRD/015-threat-report-agent-attack-trees-2026-03-23.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-23
    status: APPROVED
    notes: "All 7 PRD functional requirements mapped to 14 spec FRs. All 3 PRD user stories covered plus orchestrator integration elevated to P1 per Team Lead condition. Open questions resolved appropriately. Architect and Team Lead concerns addressed. 2 minor non-blocking observations documented in .aod/results/product-manager.md."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Threat Report Agent & Attack Trees

**Feature Branch**: `015-threat-report-agent`
**Created**: 2026-03-23
**Status**: Draft
**PRD Reference**: `docs/product/02_PRD/015-threat-report-agent-attack-trees-2026-03-23.md`

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Narrative Threat Report for Management (Priority: P1)

As a CISO or security director, when I have a completed threat model (`threats.md`) and need to present findings to my board or compliance team, I want the findings transformed into a narrative report with an executive summary so I can communicate risk posture without manually interpreting raw threat tables.

**Why this priority**: The narrative report is the primary deliverable and the foundation that all other outputs build on. Without a comprehensible report, attack trees and roadmaps lack context. CISOs are the primary decision-makers for security investment — enabling board-ready reporting is the core value proposition.

**Independent Test**: Run the report agent against the sample `examples/mermaid-agentic-app/threats.md` and verify it produces a `threat-report.md` with all seven required sections. Have a non-technical reader confirm the executive summary is understandable without STRIDE knowledge.

**Acceptance Scenarios**:

1. **Given** a completed `threats.md` with findings from STRIDE and AI agents, **When** the report agent runs, **Then** it produces `threat-report.md` containing all seven sections: Executive Summary, Architecture Overview, Threat Analysis, Cross-Cutting Themes, Attack Trees, Remediation Roadmap, and Appendix: Finding Reference.

2. **Given** the executive summary section, **When** read by a non-technical audience, **Then** it communicates the overall risk posture, top threats, and recommended actions without requiring knowledge of STRIDE methodology or security jargon. Every acronym is defined on first use.

3. **Given** findings from multiple agents targeting the same component, **When** the report agent analyzes them, **Then** it identifies and explains cross-cutting themes with references to contributing finding IDs.

4. **Given** findings with OWASP or CWE references, **When** included in the report, **Then** compliance relevance notes are added where applicable (e.g., SOC2 trust services criteria, ISO 27001 control mapping).

5. **Given** every finding ID in `threats.md` (Sections 3, 4, and 4a), **When** the report is generated, **Then** every finding ID appears in the Appendix: Finding Reference mapping — zero finding loss in transformation.

---

### User Story 2 — Mermaid Attack Trees for Critical/High Findings (Priority: P1)

As a security engineer, when I need to understand and communicate attack paths for the most severe findings, I want Mermaid-format attack trees generated for Critical and High findings so I can visualize attacker goals, preconditions, branching paths, and atomic attack actions.

**Why this priority**: Attack trees are the distinguishing capability of this feature — no existing threat modeling tool generates Mermaid attack trees automatically from findings. Critical and High findings represent the threats requiring the deepest analysis and most urgent communication to stakeholders. This is co-equal P1 with the narrative report because trees are embedded in the report structure.

**Independent Test**: Run the report agent against the sample `threats.md` and verify that every Critical and High finding has a corresponding Mermaid attack tree that renders correctly in the Mermaid Live Editor. Verify trees appear both inline in the report and as standalone files.

**Acceptance Scenarios**:

1. **Given** a Critical or High finding from `threats.md`, **When** the report agent processes it, **Then** it generates a Mermaid `flowchart TD` attack tree with a root goal node (attacker's ultimate objective), intermediate sub-goal nodes with explicit AND/OR gate logic, and leaf nodes representing concrete atomic attack actions.

2. **Given** a Critical finding, **When** the attack tree is generated, **Then** the tree has a minimum of three levels of decomposition (root → intermediate → leaf). **Given** a High finding, **Then** the tree has a minimum of two levels of decomposition.

3. **Given** generated attack trees, **When** the report agent completes, **Then** trees are embedded inline in the Attack Trees section of `threat-report.md` AND saved as standalone Markdown files in `attack-trees/{finding-id}-attack-tree.md` (e.g., `attack-trees/AG-1-attack-tree.md`).

4. **Given** a Medium or Low finding, **When** processed, **Then** no attack tree is generated — attack trees are reserved for Critical and High severity only.

5. **Given** any generated Mermaid attack tree, **When** rendered in GitHub Markdown preview or Mermaid Live Editor, **Then** the tree renders correctly without syntax errors. Node IDs use alphanumeric prefixed format (`{FindingID}_{type}{N}`), labels are quoted, and no reserved words (`end`, `default`) are used as bare identifiers.

6. **Given** correlated findings from Section 4a of `threats.md`, **When** attack trees are generated, **Then** each correlated finding gets its own individual tree with cross-references to related findings noted in the tree or its heading — not a single unified tree for the correlation group.

---

### User Story 3 — Prioritized Remediation Roadmap (Priority: P2)

As a project manager, when I need to plan security remediation work, I want a prioritized remediation roadmap with effort estimates so I can convert findings into development tasks and plan sprint work without further interpretation.

**Why this priority**: The roadmap is highly valuable but depends on the narrative report and attack tree analysis to provide context. It can be generated from `threats.md` Section 7 (Recommended Actions) with effort estimates added — a more mechanical transformation than the narrative or trees.

**Independent Test**: Run the report agent against the sample `threats.md` and verify the Remediation Roadmap section lists all findings ordered by risk level with effort estimates. Have a project manager confirm each item is directly convertible to a backlog item.

**Acceptance Scenarios**:

1. **Given** all findings from `threats.md`, **When** the remediation roadmap is generated, **Then** mitigations are listed in priority order: Critical (Immediate) first, then High (Short-term), Medium (Medium-term), Low (Backlog). Within the same risk level, items are grouped by component.

2. **Given** each roadmap item, **When** listed, **Then** it includes: finding ID (cross-reference to `threats.md`), component name, mitigation description (preserving original text from `threats.md`), effort estimate (Low / Medium / High), and dependency notes where applicable.

3. **Given** correlated findings from Section 4a, **When** the roadmap is generated, **Then** correlated findings are consolidated into a single roadmap item with the primary finding ID and notes indicating the correlation scope and contributing finding IDs.

4. **Given** the complete roadmap, **When** reviewed by a project manager, **Then** each item is directly convertible to a development task or backlog item without requiring additional interpretation or security expertise.

---

### User Story 4 — Orchestrator Integration as Phase 5 (Priority: P1)

As a tachi user running the threat modeling pipeline, when the orchestrator completes Phase 4 (Assess), I want Phase 5 (Report) to automatically generate the threat report and attack trees so I receive a complete threat model deliverable without manual intervention.

**Why this priority**: Without orchestrator integration, the report agent cannot be invoked as part of the standard pipeline — users would need to manually trigger report generation. This is the integration glue that makes the feature functional. Elevated to P1 per Team Lead condition during PRD review.

**Independent Test**: Run the full orchestrator pipeline against the sample input and verify that Phase 5 automatically produces `threat-report.md` and `attack-trees/` in the output directory alongside `threats.md` and `threats.sarif`.

**Acceptance Scenarios**:

1. **Given** the orchestrator completes Phase 4 (Assess) and `threats.md` is generated, **When** Phase 5 (Report) is enabled (default), **Then** the report agent is invoked with `threats.md` as input and produces `threat-report.md` and `attack-trees/` in the same output directory.

2. **Given** the orchestrator configuration, **When** Phase 5 is set to skip (opt-out), **Then** the pipeline completes after Phase 4 without invoking the report agent. Existing Phase 1–4 behavior is unchanged.

3. **Given** Phase 5 execution, **When** the report agent is invoked, **Then** it runs in a fresh context with only `threats.md` as input — not the accumulated pipeline context from Phases 1–4. This prevents context window pressure.

4. **Given** a completed Phase 5, **When** the output directory is examined, **Then** the structure includes:
   ```
   YYYY-MM-DD-{phase}/
   ├── threats.md           (Phase 4 — existing)
   ├── threats.sarif         (Phase 4 — existing, F-012)
   ├── threat-report.md      (Phase 5 — new)
   └── attack-trees/         (Phase 5 — new)
       ├── {finding-id}-attack-tree.md
       └── ...
   ```

---

### Edge Cases

- **Empty threat model**: If `threats.md` contains zero findings (all components analyzed clean), the report agent produces a report with an executive summary stating "no threats identified," empty Attack Trees and Remediation Roadmap sections, and a note in the Appendix confirming zero findings.
- **No Critical or High findings**: If all findings are Medium or Low, the Attack Trees section states "No Critical or High findings identified — attack trees are generated only for Critical and High severity." The Remediation Roadmap and narrative sections still include all findings.
- **Large threat model (>30 findings)**: For threat models exceeding 30 findings, the Threat Analysis section summarizes Medium and Low findings by category rather than providing individual narrative for each. Critical and High findings always receive full individual narrative treatment.
- **Correlation groups with mixed severity**: If a correlation group contains both a Critical finding and a Medium finding, the attack tree is generated for the Critical finding only, with a cross-reference noting the correlated Medium finding.
- **Missing optional sections in threats.md**: If `threats.md` is missing Section 4a (no correlations detected by F-010), the report agent proceeds without correlation handling — findings are treated as independent.
- **Mermaid rendering edge cases**: Findings with special characters in threat descriptions (parentheses, colons, quotes) are sanitized in Mermaid node labels by quoting all text. Node IDs use only alphanumeric characters plus underscores.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a report agent defined as a markdown prompt file (`agents/threat-report.md`) that consumes the structured `threats.md` and produces a narrative threat report, Mermaid attack trees, and a remediation roadmap.

- **FR-002**: The report agent MUST produce a `threat-report.md` with seven required sections: (1) Executive Summary, (2) Architecture Overview, (3) Threat Analysis, (4) Cross-Cutting Themes, (5) Attack Trees, (6) Remediation Roadmap, (7) Appendix: Finding Reference.

- **FR-003**: The Executive Summary MUST communicate the overall risk posture, top threats (by business impact), key recommendations, and compliance relevance in language understandable by a non-technical audience. No acronyms without first-use definitions. Maximum ~500 words.

- **FR-004**: The Threat Analysis section MUST provide agent-by-agent narrative with full reasoning, component annotations, and references to finding IDs. Each finding from `threats.md` MUST be addressed in the narrative.

- **FR-005**: The report agent MUST identify cross-cutting themes using four detection criteria: (a) multiple findings from different agents targeting the same component, (b) similar mitigation recommendations across threat categories, (c) findings that form attack chains (one finding's impact enables another's precondition), (d) component clusters with disproportionately high finding counts. Each theme MUST cite contributing finding IDs.

- **FR-006**: The report agent MUST generate a Mermaid `flowchart TD` attack tree for every Critical and High finding. Trees MUST follow Schneier's methodology with root goal, intermediate sub-goals with explicit AND/OR gate nodes, and leaf nodes representing atomic attack actions. Minimum three levels for Critical findings, two levels for High findings.

- **FR-007**: Attack trees MUST use consistent Mermaid conventions: node IDs prefixed with finding ID (`{FindingID}_{type}{N}`), all labels quoted, explicit AND/OR gate nodes using diamond or hexagon shapes, and color-coded styling via `classDef` (red for goals, orange for AND gates, teal for OR branches, green for leaf actions).

- **FR-008**: Attack trees MUST be output in two locations: embedded inline in the Attack Trees section of `threat-report.md`, and as standalone Markdown files in `attack-trees/{finding-id}-attack-tree.md`.

- **FR-009**: The Remediation Roadmap MUST list all findings ordered by risk level (Critical first) with grouping by component within each level. Each item MUST include: finding ID, component, mitigation (preserving original text), effort estimate (Low/Medium/High), and dependency notes.

- **FR-010**: The report agent MUST respect correlation groups from `threats.md` Section 4a: correlated findings are discussed as groups in the narrative, attack trees reference the primary finding with cross-references to peers, and remediation roadmap items consolidate correlated findings.

- **FR-011**: The Appendix: Finding Reference MUST provide a complete mapping from report sections back to original finding IDs in `threats.md`. Every finding ID from the input MUST appear in the appendix — zero finding loss.

- **FR-012**: The orchestrator MUST integrate the report agent as Phase 5 (Report) that runs after Phase 4 (Assess) completes. Phase 5 is default-on with an opt-out configuration to skip report generation. Phase 5 MUST invoke the report agent in a fresh context with only `threats.md` as input.

- **FR-013**: The report agent prompt MUST include a Mermaid validation checklist covering: reserved word avoidance (`end`, `default`), quoted labels for special characters, alphanumeric-prefixed node IDs, maximum ~20 nodes per tree for readability, and proper `classDef`/`class` styling.

- **FR-014**: A report output schema (`schemas/report.yaml`) MUST be defined specifying the required sections, finding reference completeness rules, and attack tree file naming conventions for structural validation.

### Key Entities

- **Threat Report** (`threat-report.md`): The narrative output document containing seven sections derived from `threats.md`. Authored by the report agent, consumed by CISOs, security engineers, and project managers.

- **Attack Tree** (`attack-trees/{finding-id}-attack-tree.md`): A standalone Mermaid `flowchart TD` visualization for a single Critical or High finding. Contains the root goal, decomposition logic, and atomic attack leaf nodes. Cross-referenced by finding ID.

- **Remediation Item**: A single entry in the Remediation Roadmap representing one actionable mitigation. Attributes: finding ID, component, mitigation text, priority tier, effort estimate, dependencies.

- **Cross-Cutting Theme**: An emergent pattern identified across multiple findings from different agents. Attributes: theme description, contributing finding IDs, affected components, synthesized recommendation.

- **Correlation Group**: A set of related findings from Section 4a of `threats.md` (produced by F-010). The report agent treats these as logical units in narrative, trees, and roadmap.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The report agent produces a complete `threat-report.md` from the sample `examples/mermaid-agentic-app/threats.md` containing all seven required sections with non-empty content in each.

- **SC-002**: The executive summary is comprehensible by a non-technical reader — validated against the Definition of Done by having a reader with no security training confirm they understand the risk posture and top recommendations.

- **SC-003**: 100% of Critical and High findings in the sample `threats.md` have corresponding Mermaid attack trees in both inline (`threat-report.md`) and standalone (`attack-trees/`) format.

- **SC-004**: 100% of Mermaid attack trees render correctly in GitHub Markdown preview and Mermaid Live Editor without syntax errors.

- **SC-005**: 100% of finding IDs from `threats.md` appear in the Appendix: Finding Reference — zero finding loss in transformation.

- **SC-006**: The remediation roadmap includes all findings with effort estimates, ordered by risk level, and each item is directly convertible to a development task without further interpretation.

- **SC-007**: Cross-cutting themes are identified when findings from different agents target the same component or share similar mitigations — at least one theme identified in the sample threat model (which has 19 findings across 5 components).

- **SC-008**: The full orchestrator pipeline (Phases 1–5) completes successfully against the sample input, with Phase 5 producing `threat-report.md` and `attack-trees/` alongside existing `threats.md` and `threats.sarif`.

- **SC-009**: Phase 5 (Report) can be skipped via orchestrator configuration without affecting Phase 1–4 behavior — backward compatibility preserved.

## Assumptions

- `threats.md` is complete and valid, produced by the orchestrator with all Phases 1–4 complete.
- The finding IR schema (`schemas/finding.yaml`) and output schema (`schemas/output.yaml`) remain stable at their current versions.
- Mermaid `flowchart TD` syntax is sufficient for attack tree representation without requiring extensions or plugins.
- Effort estimates in the remediation roadmap are qualitative (Low/Medium/High based on mitigation complexity), not quantitative time estimates.
- The report agent runs within the same LLM context infrastructure as other tachi agents.
- Phase 5 receives only `threats.md` as input (fresh context), not the accumulated orchestrator pipeline context from Phases 1–4.
- Correlated findings in Section 4a follow the structure defined by F-010 (ADR-012): group ID, contributing finding IDs, primary finding designation.
- The sample `examples/mermaid-agentic-app/threats.md` is representative of real-world threat model output for testing purposes.

## Scope Boundaries

### In Scope
- Report agent prompt file (`agents/threat-report.md`)
- Report output schema (`schemas/report.yaml`)
- Narrative report with all seven sections
- Mermaid attack trees for Critical/High findings (inline + standalone)
- Prioritized remediation roadmap with effort estimates
- Cross-cutting theme identification
- Correlated finding group handling
- Orchestrator integration as Phase 5 (default-on, opt-out)
- Compliance relevance annotations (SOC2, ISO 27001 where applicable)
- Finding-to-report traceability via appendix

### Out of Scope
- Interactive attack tree visualization (use existing Mermaid renderers)
- PDF or HTML export (Markdown is the output format)
- Quantitative risk scoring or financial impact estimation
- Attack tree generation for Medium/Low findings
- Custom report templates or branding
- Automated remediation ticket creation in issue trackers
- Report comparison across multiple threat model runs
- Attack-defense trees (defensive nodes are a potential future enhancement)
- Dashboard or web-based report viewing
