# Narrative Templates

Reference templates for narrative structure in the tachi threat report. Each section below defines the required elements, structure, and conventions for a specific report section.

---

## Executive Summary (Section 1)

Generate the Executive Summary as Section 1 of the report. This section communicates risk posture to non-technical stakeholders. Maximum ~500 words.

### 5 Required Elements

1. **Risk Posture** (1-2 sentences): Summarize the overall security health of the system. State the total finding count, risk distribution (Critical/High/Medium/Low), and an overall assessment. Acknowledge what is working well alongside concerns.

2. **Top 3-5 Threats by Business Impact**: Select the most consequential threats from the findings. Rank by business impact (not just risk level) -- a High finding on a payment system may matter more than a Critical finding on a non-production component. For each threat: state the component, the risk, and why it matters to the business in plain language.

3. **Key Recommendations**: Provide 3-5 actionable recommendations. State what to do, not how to do it (implementation details belong in the Remediation Roadmap). Recommendations should be understandable by a board member without security expertise.

4. **Compliance Relevance**: Map findings to applicable compliance frameworks where relevant:
   - SOC2 Trust Services Criteria (CC6.1 access controls, CC7.2 system monitoring, etc.)
   - ISO 27001 control mapping (A.9 access control, A.12 operations security, etc.)
   - CWE identifiers from finding `references` field
   - OWASP references from finding `references` field
   Only include mappings where the finding's `references` field contains relevant identifiers. Do not fabricate compliance mappings.

5. **Remediation Timeline by Priority Tier**:
   - **Immediate** (Critical findings): Address before next deployment
   - **Short-term** (High findings): Address within current development cycle
   - **Medium-term** (Medium findings): Schedule for next planning cycle
   - **Backlog** (Low/Note findings): Track for future consideration

---

## Architecture Overview (Section 2)

Generate the Architecture Overview as Section 2 of the report. This section derives system context from `threats.md` Sections 1 and 2.

### System Context (from Section 1: System Overview)

Extract and present in narrative form:
- **Components**: List all components from the Components table with their DFD element types and descriptions. Group by function (e.g., "user-facing services," "data stores," "external integrations").
- **Data Flows**: Describe key data movement patterns between components. Highlight flows that cross trust boundaries.
- **Technologies**: Note the technology stack identified in the Technologies table.

Present this as a narrative paragraph, not as raw tables. The audience is a non-technical reader who needs to understand what the system does and how data moves through it.

### Trust Boundary Summary (from Section 2: Trust Boundaries)

Extract and present:
- **Trust Zones**: Describe each zone and what components it contains.
- **Boundary Crossings**: Explain which data flows cross trust boundaries and what security controls are in place.
- Highlight any crossings without documented controls -- these are areas of concern.

If `threats.md` Section 2 contains the note "No trust boundaries were identified in the architecture input," state this in the Architecture Overview and note that the absence of explicit boundaries is itself a finding worth considering.

---

## Threat Analysis (Section 3)

### Per-Category Subsection Headers

Organize by threat category with these subsections:
- 3.1 Spoofing (S-*)
- 3.2 Tampering (T-*)
- 3.3 Repudiation (R-*)
- 3.4 Information Disclosure (I-*)
- 3.5 Denial of Service (D-*)
- 3.6 Elevation of Privilege (E-*)
- 3.7 Agentic Threats (AG-*)
- 3.8 LLM Threats (LLM-*)

For each category, include all findings from the corresponding STRIDE or AI table in `threats.md`.

### Per-Finding Narrative Pattern

For each finding, provide:
1. **Finding reference**: State the finding ID (e.g., "**S-1**") as a bold reference
2. **MAESTRO layer context**: On first mention of each finding, include its MAESTRO architectural layer from the `maestro_layer` field. Integrate naturally into the sentence — for example: "**S-1** targets the Agent Framework layer (L3), where..." or "Operating at the Data Operations layer (L2), **T-3** exploits...". Every finding MUST include its MAESTRO layer on first reference.
3. **Component annotation**: Name the affected component
4. **Threat description**: Explain the threat in context -- what could happen, how, and why it matters
5. **Risk context**: State the likelihood, impact, and computed risk level
6. **Mitigation summary**: Reference the recommended mitigation (the full mitigation text appears in the Remediation Roadmap)

### Progressive Technical Depth Rules

- Start each category subsection with a general overview of the threat class
- Progress from general threats to specific findings
- For Critical and High findings: provide deeper analysis including potential attack scenarios
- For Medium findings: provide standard analysis
- For categories with no findings: include the subsection heading with a note: "No {category} threats were identified in this threat model."

### Large Threat Model Handling (>30 findings)

When the total finding count exceeds 30:
- Critical and High findings always receive full individual narrative
- Medium findings are summarized by category rather than individually narrated
- Low and Note findings are mentioned in aggregate (e.g., "Three low-severity information disclosure findings were identified affecting logging components")

---

## Cross-Cutting Theme Detection (Section 4)

### 4 Detection Criteria

Scan all findings for these patterns:

**(a) Component Convergence**: Multiple findings from different threat agents (different categories) targeting the same component. Example: A component has both a Spoofing finding (S-1) and an Agentic finding (AG-2), suggesting it is a high-risk nexus.

**(b) Mitigation Similarity**: Similar mitigation recommendations appearing across different threat categories. Example: Multiple findings recommend "implement input validation" -- this suggests a systemic input handling gap rather than isolated issues.

**(c) Attack Chain Formation**: Findings where one finding's impact enables another finding's precondition. Example: An Information Disclosure finding (I-1) leaks credentials that enable a Spoofing finding (S-2). These form logical attack chains that are more severe than either finding alone.

**(d) Component Cluster Density**: Components with disproportionately high finding counts relative to other components. If one component has significantly more findings than the system average, it represents a concentration of risk.

### Theme Presentation

For each identified theme:
1. **Theme title**: Descriptive name (e.g., "Concentrated Risk in LLM Agent Orchestrator")
2. **Description**: Explain the pattern and why it matters
3. **Contributing findings**: Cite all finding IDs that contribute to this theme (e.g., "Contributing findings: S-1, AG-2, LLM-3")
4. **Affected components**: List components involved
5. **Synthesized recommendation**: A higher-level recommendation that addresses the systemic issue

### Minimum Thresholds

- Report at least 1 theme when the threat model has >5 findings on any single component
- Do not report themes with fewer than 2 contributing findings
- If no themes are detected (unlikely for models with >10 findings), state: "No cross-cutting themes were identified. Findings appear to be independent and component-specific."

---

## Language Rules

These rules apply to all narrative sections of the report:

- Define every acronym on first use (e.g., "STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege)")
- No jargon without explanation
- Write for a CISO presenting to a board -- authoritative but accessible
- Use active voice

---

## Remediation Roadmap (Section 6)

### Priority Ordering

List all findings in strict priority order by risk level:

| Priority Tier | Risk Level | Timeline Guidance | Action |
|--------------|-----------|-------------------|--------|
| Immediate | Critical | Address before next deployment | Block release until resolved |
| Short-term | High | Address within current development cycle | Schedule in current sprint/iteration |
| Medium-term | Medium | Schedule for next planning cycle | Add to backlog with priority |
| Backlog | Low / Note | Track for future consideration | Document and revisit periodically |

Within the same priority tier, group findings by **component**. This enables project managers to assign related items to the same team or developer.

### Roadmap Item Format

Present each item as a row in a structured table:

| Finding ID | Component | Mitigation | Effort | Dependencies |
|------------|-----------|------------|--------|--------------|
| AG-1 | LLM Agent Orchestrator | {mitigation text from threats.md -- preserved verbatim} | High | Requires tool risk classification framework |
| AG-2 | MCP Tool Server | {mitigation text} | Medium | Depends on AG-1 risk tier implementation |

**Field rules**:
- **Finding ID**: Exact ID from `threats.md` (e.g., AG-1, S-1, LLM-3)
- **Component**: Exact component name from `threats.md` -- no renaming or abbreviation
- **Mitigation**: Preserve the mitigation text from `threats.md` Section 7 (Recommended Actions) verbatim. Do not rephrase, summarize, or reinterpret. The roadmap item should be traceable back to the original finding
- **Effort**: Qualitative assessment (Low / Medium / High) -- see Effort Estimation below
- **Dependencies**: Note any prerequisites, related findings, or implementation ordering constraints. If no dependencies, state "None"

### Section Introduction

Before the table, include a brief introduction stating:
- Total number of remediation items
- Distribution by priority tier (e.g., "3 Immediate, 9 Short-term, 7 Medium-term")
- Most impacted component (the component with the most findings)
- Suggested implementation starting point

### Effort Estimation Heuristics

Assign a qualitative effort estimate (Low / Medium / High) to each roadmap item based on the mitigation's implementation complexity.

| Effort | Characteristics | Examples |
|--------|----------------|----------|
| **Low** | Configuration changes, parameter tuning, enabling existing features, policy updates | Enable rate limiting on existing API gateway; adjust token budget caps; update logging verbosity; add TLS certificate pinning configuration |
| **Medium** | New validation logic, access control additions, monitoring implementation, new middleware, schema changes | Implement input validation on tool call parameters; add role-based access control checks; deploy query pattern analysis; add document-level access controls to knowledge base |
| **High** | Architectural changes, new components, protocol redesign, new frameworks, cross-cutting infrastructure | Implement tool risk-tier classification framework; build human-in-the-loop approval workflow; deploy structured prompt template system with boundary enforcement; implement provenance tracking across RAG pipeline |

**Assessment Rules**:
1. **Assess based on mitigation text**: Use the mitigation description from `threats.md` to determine effort. Do not infer additional work beyond what the mitigation states.
2. **Compound mitigations**: If a single finding's mitigation lists multiple actions (separated by semicolons or "and"), assess effort based on the **highest-effort individual action**.
3. **Architectural indicators**: Keywords suggesting High effort: "implement framework," "redesign," "new component," "pipeline," "workflow system," "classification framework," "provenance tracking."
4. **Configuration indicators**: Keywords suggesting Low effort: "configure," "enable," "set," "adjust," "update parameter," "add to allowlist."
5. **Do not estimate time**: Never convert effort levels to hours, days, or sprints. Effort is relative complexity only.
