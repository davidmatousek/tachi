---
prd_reference: docs/product/02_PRD/010-deduplication-risk-rating-2026-03-22.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-22
    status: APPROVED_WITH_CONCERNS
    notes: "All 5 PRD FRs trace to 11 spec FRs. All acceptance criteria preserved. No scope creep. Priorities corrected to match PRD. PRD traceability mapping added."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Deduplication & Risk Rating

**Feature Branch**: `010-deduplication-risk-rating`
**Created**: 2026-03-22
**Status**: Draft
**Input**: PRD 010 — Deduplication & Risk Rating

## User Scenarios & Testing *(mandatory)*

**PRD Traceability**: Spec US-1 maps to PRD US-1 (correlation). Spec US-2 merges PRD US-2 (risk summary counts) and PRD US-3 (coverage matrix). Spec US-3 extracts the risk calibration documentation aspect of PRD US-2.

### User Story 1 — Cross-Agent Finding Correlation (Priority: P0)

As a developer running a threat model against an agentic architecture, when the orchestrator assembles findings from multiple agents that flag the same component for related threats, I see those overlapping findings correlated into a single grouped entry showing all agent perspectives, so I can understand the full scope of each vulnerability without manually cross-referencing agent outputs.

**Why this priority**: This is the core value proposition. Without correlation, users must manually identify which findings from different agents describe the same underlying issue — the most time-consuming and error-prone part of triaging a multi-agent threat model.

**Independent Test**: Run the orchestrator against `examples/mermaid-agentic-app/input.md` (an architecture with LLM components). Verify that at least one correlation group appears in the Correlated Findings section linking findings from different agent categories on the same component.

**Acceptance Scenarios**:

1. **Given** the Tampering agent and Data-Poisoning agent both produce findings on "LLM Agent Orchestrator" for data integrity issues, **When** the orchestrator assembles the output, **Then** a correlated finding group appears in Section 4a listing both finding IDs (e.g., "T-2, LLM-1"), the shared component name, a threat summary showing each agent's perspective, and the highest risk level among the correlated findings.
2. **Given** correlated findings exist, **When** viewing the STRIDE and AI agent tables (Sections 3 and 4), **Then** the original individual findings are still present with their original IDs, unchanged.
3. **Given** two findings on different components (e.g., T-1 on "API Gateway" and LLM-1 on "LLM Agent"), **When** the orchestrator checks for correlation, **Then** they are NOT correlated because correlation requires the same target component.
4. **Given** three agents (Tampering, Data-Poisoning, and Prompt-Injection) all flag the same component, and two separate correlation rule pairs match (Tampering+Data-Poisoning, Prompt-Injection+Information-Disclosure), **When** the orchestrator processes correlations, **Then** findings that match multiple rules through the same component form one correlation group containing all matched findings.

---

### User Story 2 — Deduplicated Risk Summary and Coverage Matrix (Priority: P0)

As a security analyst reviewing a threat model, when I look at the coverage matrix and risk summary, I see counts that reflect unique threats rather than inflated raw counts, so I can accurately assess the real threat posture without manual deduplication.

**Why this priority**: Accurate counts directly affect security reporting and remediation prioritization. Inflated counts overstate the threat landscape, while accurate deduplicated counts enable correct resource allocation.

**Independent Test**: Run the orchestrator against an architecture with at least one component targeted by both STRIDE and AI agents. Compare the risk summary counts against the correlated findings: the total should be lower than the raw finding count by the number of findings absorbed into correlation groups.

**Acceptance Scenarios**:

1. **Given** a completed threat model with 3 correlation groups that merged 8 individual findings into 3 groups, **When** viewing the risk summary (Section 6), **Then** the total count reflects the deduplicated total (total findings minus merged duplicates plus correlation groups), and a parenthetical shows the raw count if different (e.g., "12 (15 raw)").
2. **Given** a completed threat model with correlation groups, **When** viewing the coverage matrix (Section 5), **Then** cells show deduplicated counts where correlation groups count as 1 finding per component-category pair, and a footnote states "Counts reflect deduplicated findings. N correlation groups merged M individual findings."
3. **Given** a cell in the coverage matrix with zero findings where the component was analyzed for that category, **When** viewing the cell, **Then** it displays "—" (em dash) to highlight the coverage gap.
4. **Given** a component that has no AI-applicable keywords (no LLM/agent references), **When** viewing the AI columns in the coverage matrix, **Then** those cells show "n/a" rather than "—" to distinguish "not applicable" from "analyzed but no findings."

---

### User Story 3 — Risk Calibration Documentation (Priority: P1)

As a developer or security analyst reviewing the threat model, when I want to understand how a risk level was computed, I see the OWASP 3×3 risk matrix documented in the output, so I can verify any finding's risk rating and trust the consistency of risk assessments across all agents.

**Why this priority**: Risk transparency builds trust in the output. Without visible calibration, users may question whether "High" from one agent means the same as "High" from another. The matrix is already implemented for computation; this documents it for reader consumption.

**Independent Test**: Run the orchestrator against any architecture. Verify that the Risk Summary section includes a Risk Calibration Matrix subsection showing the OWASP 3×3 matrix, and that the summary counts note they are computed from deduplicated findings.

**Acceptance Scenarios**:

1. **Given** a completed threat model, **When** viewing the Risk Summary section (Section 6), **Then** a Risk Calibration Matrix subsection is present showing the 3×3 table (Likelihood rows × Impact columns → Risk Level cells) with all 9 combinations documented.
2. **Given** a completed threat model with deduplicated findings, **When** viewing the risk summary counts, **Then** each risk level row shows the count from deduplicated findings and the percentage based on the deduplicated total.

---

### Edge Cases

- **Zero correlations**: When no findings match any correlation rule (e.g., a simple non-AI architecture), the Correlated Findings section shows "No cross-agent correlations detected" with an empty table. The section is never omitted.
- **All findings correlated**: When every finding belongs to a correlation group, the coverage matrix and risk summary reflect all deduplicated counts. No special handling needed — the algorithm handles this naturally.
- **Single-agent architecture**: When only STRIDE agents are dispatched (no AI components), AI columns in the coverage matrix show "n/a" and no cross-STRIDE/AI correlations are possible. Same-category correlations (e.g., two Tampering findings on the same component) are NOT correlated — dedup only applies across different agent categories.
- **Finding belongs to one group only**: A finding may appear in at most one correlation group. If a finding matches multiple rules (e.g., T-2 matches both CR-1 with LLM-1 and CR-4 with AG-1), all matching findings for that component merge into a single group.
- **Risk level of correlation group**: The group's risk level equals the highest risk level among its member findings (conservative merge). If T-2 is "High" and LLM-1 is "Medium", the group risk is "High".

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST detect correlated findings across different agent categories when two or more findings target the same component and their agent categories match a defined correlation rule pair.
- **FR-002**: System MUST implement exactly 5 correlation rules mapping STRIDE-to-AI agent category pairs: (1) Tampering + Data-Poisoning for data integrity, (2) Privilege-Escalation + Agent-Autonomy for excessive permissions, (3) Information-Disclosure + Prompt-Injection for information leakage, (4) Repudiation + Agent-Autonomy for accountability gaps, (5) Denial-of-Service + Tool-Abuse for resource exhaustion.
- **FR-003**: System MUST produce a Correlated Findings section (Section 4a) in the output containing a table with columns: Group ID (CG-N), Findings (comma-separated original IDs), Component, Threat Summary (each agent's perspective prefixed by category name), and Risk Level (highest among group members).
- **FR-004**: System MUST preserve all original individual findings in their respective STRIDE tables (Section 3) and AI tables (Section 4) unchanged — correlation groups are additive, not replacements.
- **FR-005**: System MUST compute coverage matrix cell values using deduplicated finding counts, where findings that belong to a correlation group count as 1 per component-category pair rather than individually.
- **FR-006**: System MUST mark zero-coverage cells in the coverage matrix with "—" (analyzed but no findings) and non-applicable cells with "n/a" (category not dispatched for that component).
- **FR-007**: System MUST include a Risk Calibration Matrix subsection in the Risk Summary section showing the OWASP 3×3 likelihood × impact matrix with all 9 risk level mappings.
- **FR-008**: System MUST compute risk summary counts using deduplicated findings, with a parenthetical showing raw count when it differs from the deduplicated count.
- **FR-009**: System MUST include the Correlated Findings section in every output even when zero correlations are detected, displaying "No cross-agent correlations detected" with the table header row.
- **FR-010**: System MUST limit each finding to at most one correlation group. When multiple correlation rules match findings on the same component, all matched findings merge into a single group.
- **FR-011**: System MUST include a coverage matrix footnote stating "Counts reflect deduplicated findings. N correlation groups merged M individual findings." when correlations exist.

### Key Entities

- **Finding**: An individual threat identified by a single agent for a specific component. Conforms to the Finding IR schema (`schemas/finding.yaml`). Identified by a prefixed ID (e.g., T-2, LLM-1).
- **Correlation Group**: A set of related findings from different agent categories that target the same component and match a defined correlation rule. Identified by `CG-N` (sequential). Contains 2+ findings. Has a risk level equal to the highest among its members.
- **Correlation Rule**: A defined pairing of two agent categories that, when both produce findings on the same component, indicates a related underlying threat. Five rules are defined (CR-1 through CR-5).
- **Coverage Matrix Cell**: A component×category intersection that shows deduplicated finding count, "—" for analyzed-but-clean, or "n/a" for not-applicable.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running the orchestrator against `examples/mermaid-agentic-app/input.md` produces at least one correlation group in the Correlated Findings section (expected: Tampering + Data-Poisoning overlap on LLM components).
- **SC-002**: Running the orchestrator against a traditional (non-AI) architecture produces zero AI-category findings, zero correlation groups, and no false correlations.
- **SC-003**: The risk summary total count for a threat model with correlations is strictly less than the raw finding count across all 8 tables, demonstrating deduplication is applied.
- **SC-004**: Every correlation group in the output links back to original finding IDs that are present and unchanged in their respective STRIDE/AI tables, confirming audit trail preservation.
- **SC-005**: Every risk level in the output matches the OWASP 3×3 matrix computation for that finding's likelihood and impact values, as verified by the existing risk validation protocol.
- **SC-006**: The coverage matrix accurately differentiates between three cell states: findings present (count), analyzed-but-clean ("—"), and not-applicable ("n/a").
- **SC-007**: The output structural validation checklist passes, confirming all required sections (including the new Correlated Findings section) are present and correctly structured.

### Assumptions

- All 11 agents (6 STRIDE + 5 AI) are validated and producing component-specific findings conforming to the Finding IR schema (confirmed: F-005 and F-007 delivered).
- The OWASP 3×3 risk validation logic in the orchestrator is correct (confirmed: implemented in orchestrator Phase 3, lines 804–844).
- The 5 correlation rules (CR-1 through CR-5) cover the primary overlap scenarios between STRIDE and AI agent categories. Additional rules may be added in future iterations.
- The `examples/mermaid-agentic-app/input.md` architecture contains at least one component that triggers both STRIDE and AI agent dispatch, producing overlapping findings suitable for correlation testing.

### Scope Boundaries

**In scope**: Correlation detection algorithm (5 rules), Correlated Findings output section, deduplicated coverage matrix, risk calibration documentation in output, deduplicated risk summary counts.

**Out of scope**: Fuzzy semantic similarity matching, SARIF/CVSS output mapping (F-006), interactive correlation rule configuration, cross-component correlation, NIST SP 800-30 5-level matrix.

### Constraints

- **Prompt-only implementation**: All logic is expressed as orchestrator prompt instructions extending `agents/orchestrator.md`, not application code.
- **Deterministic matching**: No probabilistic or LLM-based similarity — rules are explicit and reproducible.
- **Single-pass assembly**: Correlation detection runs once during the assembly phase, not iteratively.
- **Backward compatibility**: Output format changes are additive. Existing example outputs and schema contracts remain valid.
