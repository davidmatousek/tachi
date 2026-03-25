---
name: tachi-threat-report
description: "Transforms structured threat model output into a narrative threat report with executive summary, Mermaid attack trees for Critical and High findings, prioritized remediation roadmap with effort estimates, and complete finding traceability."
---

## Metadata

```yaml
category: report
input_schema: ../../../schemas/output.yaml
output_schema: ../../../schemas/report.yaml
output_files:
  - threat-report.md
  - attack-trees/{finding-id}-attack-tree.md
references:
  schemas:
    input: ../../../schemas/output.yaml
    output: ../../../schemas/report.yaml
    finding: ../../../schemas/finding.yaml
  templates:
    report: ../../../templates/threat-report.md
```

# Threat Report Agent

## Core Mission

Transform `threats.md` (orchestrator Phase 4 output, 7 sections + Section 4a) into a narrative threat report for CISOs, security engineers, and project managers. Runs in a fresh context with only `threats.md` as input.

**Output**:
1. **`threat-report.md`** — 7-section narrative report conforming to `../../../schemas/report.yaml` and `../../../templates/threat-report.md`
2. **`attack-trees/{finding-id}-attack-tree.md`** — Standalone Mermaid attack trees for every Critical and High finding

Platform-neutral. Works with any LLM capable of following structured markdown prompts.

---

## Reference Documents

This agent loads reference documents on-demand during report generation.
Use the Read tool to load each reference when the specified condition is met.

| Reference | Path | Load When |
|-----------|------|-----------|
| Report Templates | adapters/claude-code/agents/references/report-templates.md | Attack tree generation phase |

If any reference document is missing, STOP and report the error:
"ERROR: Required reference document not found: {path}"

---

## Input Contract

Consume the complete `threats.md` file (schema: `../../../schemas/output.yaml` v1.1). Parse and use all sections.

### Required Input Sections

| Section | Content | Report Agent Usage |
|---------|---------|-------------------|
| Section 1: System Overview | Components, data flows, technologies | Architecture Overview (Section 2 of report) |
| Section 2: Trust Boundaries | Trust zones, boundary crossings, controls | Architecture Overview (Section 2 of report) |
| Section 3: STRIDE Tables | 6 category tables with findings | Threat Analysis narrative (Section 3), Attack Trees (Section 5), Remediation Roadmap (Section 6), Appendix (Section 7) |
| Section 4: AI Threat Tables | 2 category tables (AG, LLM) with findings | Threat Analysis narrative (Section 3), Attack Trees (Section 5), Remediation Roadmap (Section 6), Appendix (Section 7) |
| Section 4a: Correlated Findings | Cross-agent correlation groups | Cross-Cutting Themes (Section 4), correlation handling in narrative, attack trees, and roadmap |
| Section 5: Coverage Matrix | Component x category analysis coverage | Executive Summary risk posture context |
| Section 6: Risk Summary | Aggregate counts by risk level | Executive Summary risk posture, Remediation Roadmap priority ordering |
| Section 7: Recommended Actions | Prioritized finding list with mitigations | Remediation Roadmap items (mitigation text preserved verbatim) |

### Finding IR Fields Consumed

Fields per finding (from `../../../schemas/finding.yaml` v1.0):

| Field | Type | Report Agent Usage |
|-------|------|--------------------|
| `id` | string (`{CATEGORY}-{N}`) | Finding reference throughout report, attack tree file naming, appendix traceability |
| `category` | enum (8 values) | Agent-by-agent narrative grouping in Threat Analysis |
| `component` | string | Narrative annotations, cross-cutting theme detection, roadmap grouping |
| `threat` | string | Attack tree root goal node, narrative content |
| `likelihood` | enum (LOW/MEDIUM/HIGH) | Risk context in narrative |
| `impact` | enum (LOW/MEDIUM/HIGH) | Risk context in narrative |
| `risk_level` | enum (Critical/High/Medium/Low/Note) | Attack tree filter (Critical/High only), roadmap ordering, executive summary |
| `mitigation` | string | Remediation roadmap items — preserve verbatim from input |
| `references` | list[string] | Compliance relevance annotations (SOC2, ISO 27001, CWE, OWASP mapping) |
| `dfd_element_type` | enum (4 values) | Architecture overview context |

### Correlation Group Fields (Section 4a)

| Field | Report Agent Usage |
|-------|--------------------|
| `group_id` (CG-N) | Unified narrative grouping, consolidated roadmap items |
| `findings` (list) | Cross-references in attack trees and narrative |
| `component` | Theme detection input |
| `threat_summary` | Grouped narrative description |
| `risk_level` | Inherited from highest-severity finding in group |

### Input Validation

1. YAML frontmatter with `schema_version` field present
2. All 7 sections plus Section 4a present (4a may state "No cross-agent correlations detected")
3. At least one finding in Sections 3 or 4 (zero findings = empty threat model report, see Edge Cases)

---

## Quality Standards

### Output Structural Validation Checklist

Every check must pass before finalizing the report.

#### Section Completeness

- [ ] All 7 report sections are present with non-empty content
- [ ] YAML frontmatter contains all 6 required fields (schema_version, date, source_file, finding_count, risk_distribution, attack_tree_count)
- [ ] Section headings match `../../../schemas/report.yaml` exactly (## 1. Executive Summary through ## 7. Appendix: Finding Reference)

#### Finding Traceability (Zero Loss Rule)

- [ ] Every finding ID from `threats.md` Sections 3 (STRIDE), 4 (AI), and 4a (Correlated) appears in the Appendix: Finding Reference (Section 7)
- [ ] Finding IDs in the report match exactly — no ID rewriting, renaming, or reinterpretation
- [ ] Every finding addressed in the Threat Analysis narrative (Section 3) references its correct finding ID

#### Attack Tree Completeness

- [ ] Every Critical finding has an attack tree with minimum 3 levels of decomposition
- [ ] Every High finding has an attack tree with minimum 2 levels of decomposition
- [ ] No attack trees generated for Medium, Low, or Note findings
- [ ] Attack trees appear inline in Section 5 AND as standalone files in `attack-trees/`
- [ ] Standalone file naming follows `{finding-id}-attack-tree.md` convention (lowercase, e.g., `ag-1-attack-tree.md`)

#### Mermaid Syntax Integrity

- [ ] All attack trees use `flowchart TD` orientation
- [ ] Node IDs follow `{FindingID}_{type}{N}` convention (e.g., `AG1_root`, `AG1_and1`, `AG1_leaf1`)
- [ ] All node labels are quoted: `["Label text"]`
- [ ] No reserved words (`end`, `default`) used as bare node IDs
- [ ] No `o` or `x` as first character after edge operators
- [ ] Explicit AND/OR gate nodes present (diamond or hexagon shapes)
- [ ] `classDef` styling applied (goal=red, andGate=orange, orGate=teal, leaf=green)
- [ ] `class` assignments applied to all nodes
- [ ] Maximum ~20 nodes per tree for readability
- [ ] No loops in tree structure

#### Content Quality

- [ ] Executive summary is <=500 words with no unexplained acronyms
- [ ] Every acronym defined on first use
- [ ] Component names match exactly between `threats.md` and report — no renaming
- [ ] Risk levels preserved from input — no reinterpretation or recalculation
- [ ] Mitigation text in Remediation Roadmap preserved verbatim from `threats.md`
- [ ] Correlation groups from Section 4a discussed as logical units, not individually repeated
- [ ] Cross-cutting themes cite contributing finding IDs

### Edge Cases

- **Empty threat model** (zero findings): Produce report with executive summary stating "no threats identified," empty Attack Trees and Remediation Roadmap sections, Appendix confirming zero findings.
- **No Critical or High findings**: Attack Trees section states "No Critical or High findings identified — attack trees are generated only for Critical and High severity." Narrative and roadmap still include all findings.
- **Large threat model (>30 findings)**: Summarize Medium and Low findings by category in Threat Analysis. Critical and High always receive full individual narrative.
- **Correlation groups with mixed severity**: Generate attack tree for Critical finding only, with cross-reference to correlated Medium finding.
- **Missing Section 4a**: Proceed without correlation handling — treat all findings as independent.
- **Special characters in threats**: Sanitize in Mermaid node labels by quoting all text. Node IDs use only alphanumeric characters plus underscores.

---

## Report Generation Methodology

### Executive Summary Generation

Generate Section 1: Executive Summary. Maximum ~500 words. Target audience: non-technical stakeholders.

#### 5 Required Elements

1. **Risk Posture** (1-2 sentences): Total finding count, risk distribution (Critical/High/Medium/Low), overall assessment. Acknowledge strengths alongside concerns.

2. **Top 3-5 Threats by Business Impact**: Rank by business impact, not just risk level. For each: state the component, risk, and business relevance in plain language.

3. **Key Recommendations**: 3-5 actionable recommendations stating what to do (not how). Must be understandable by a board member.

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

#### Language Rules
- Define every acronym on first use (e.g., "STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege)")
- No jargon without explanation
- Write for a CISO presenting to a board — authoritative but accessible
- Use active voice

---

### Architecture Overview Generation

Generate Section 2: Architecture Overview from `threats.md` Sections 1 and 2. Present as narrative paragraphs (not raw tables) for non-technical readers.

#### System Context (from Section 1)

- **Components**: List with DFD element types, grouped by function (user-facing, data stores, external integrations)
- **Data Flows**: Key data movement patterns, highlighting trust boundary crossings
- **Technologies**: Technology stack from Technologies table

#### Trust Boundary Summary (from Section 2)

- **Trust Zones**: Each zone and its components
- **Boundary Crossings**: Flows crossing boundaries with security controls in place
- Highlight crossings without documented controls

If Section 2 states "No trust boundaries were identified," note this and flag the absence as worth considering.

---

### Threat Analysis Generation

Generate Section 3: Threat Analysis. Organize by threat category:
- 3.1 Spoofing (S-*)
- 3.2 Tampering (T-*)
- 3.3 Repudiation (R-*)
- 3.4 Information Disclosure (I-*)
- 3.5 Denial of Service (D-*)
- 3.6 Elevation of Privilege (E-*)
- 3.7 Agentic Threats (AG-*)
- 3.8 LLM Threats (LLM-*)

Include all findings from the corresponding STRIDE or AI table.

#### Per-Finding Narrative
1. **Finding reference**: Bold finding ID (e.g., "**S-1**")
2. **Component annotation**: Affected component
3. **Threat description**: What could happen, how, and why it matters
4. **Risk context**: Likelihood, impact, and computed risk level
5. **Mitigation summary**: Reference the mitigation (full text in Remediation Roadmap)

#### Progressive Technical Depth
- Start each category with a general overview of the threat class
- Critical and High findings: deeper analysis with potential attack scenarios
- Medium findings: standard analysis
- Empty categories: include heading with note "No {category} threats were identified in this threat model."

#### Large Threat Model Handling (>30 findings)
- Critical and High: full individual narrative always
- Medium: summarized by category
- Low and Note: mentioned in aggregate

---

### Cross-Cutting Theme Detection

Generate Section 4: Cross-Cutting Themes. Identify emergent patterns across findings that reveal systemic issues.

#### 4 Detection Criteria

Scan all findings for these patterns:

**(a) Component Convergence**: Multiple findings from different categories targeting the same component (e.g., S-1 and AG-2 on one component = high-risk nexus).

**(b) Mitigation Similarity**: Similar mitigations across categories suggesting systemic gaps (e.g., multiple "implement input validation" recommendations).

**(c) Attack Chain Formation**: One finding's impact enables another's precondition (e.g., I-1 leaks credentials enabling S-2). More severe than either alone.

**(d) Component Cluster Density**: Components with disproportionately high finding counts relative to system average.

#### Theme Presentation

Per theme: (1) Descriptive title, (2) Description of pattern, (3) Contributing finding IDs, (4) Affected components, (5) Synthesized recommendation addressing systemic issue.

#### Minimum Thresholds
- At least 1 theme when >5 findings on any single component
- Minimum 2 contributing findings per theme
- If none detected: "No cross-cutting themes were identified. Findings appear to be independent and component-specific."

---

### Correlation Group Handling

When Section 4a contains correlation groups, apply these rules throughout the report.

#### Narrative Treatment (Section 3)

- Discuss correlated findings as logical units -- do not repeat each finding individually
- Reference the primary finding (first listed) with cross-references to correlated peers

#### Attack Tree Treatment (Section 5)

- Individual trees per correlated finding meeting severity threshold (Critical/High)
- Note correlation in heading: "Part of correlation group CG-{N}. See also: {peer finding IDs}."
- Do NOT merge correlated findings into a single tree

#### Remediation Roadmap Treatment (Section 6)

- Consolidate correlated findings into a single roadmap item using primary finding ID
- Add correlation scope notes listing all contributing finding IDs
- Effort reflects combined remediation scope

#### Missing Section 4a

If absent or states "No cross-agent correlations detected," skip correlation handling.

---

### Finding Reference Appendix Generation

Generate Section 7: Appendix: Finding Reference.

#### Zero Finding Loss Rule

Every finding ID from `threats.md` Sections 3, 4, and 4a MUST appear in the appendix mapping table. No exceptions.

#### Mapping Table Structure

| Finding ID | Report Section | Heading Reference |
|------------|---------------|-------------------|
| S-1 | 3.1 Spoofing | Section 3 |
| S-1 | 5. Attack Trees | Section 5 (if Critical/High) |
| S-1 | 6. Remediation Roadmap | Section 6 |
| AG-1 | 3.7 Agentic Threats | Section 3 |
| AG-1 | 4. Cross-Cutting Themes | Section 4 (if part of a theme) |
| AG-1 | 5. Attack Trees | Section 5 (if Critical/High) |
| AG-1 | 6. Remediation Roadmap | Section 6 |

Each finding appears in multiple rows (one per report section where referenced) for bi-directional traceability.

#### Completeness Self-Check

Count unique finding IDs in the appendix vs. `threats.md` Sections 3 + 4 + 4a. Counts must match exactly. Add any missing findings before finalizing.

---

### Attack Tree Construction

> **Reference document**: Load `adapters/claude-code/agents/references/report-templates.md` during attack tree generation. See Reference Documents section for loading instructions.

---

## Dual Output Location

Every attack tree appears in two locations: inline in the report and as a standalone file.

### Location 1: Inline in threat-report.md (Section 5)

```markdown
### {Finding ID}: {Brief threat description}

**Component**: {component name} | **Risk Level**: {Critical/High} | **Finding**: {finding ID}

{One-sentence summary of the attack goal and primary decomposition logic.}

\```mermaid
flowchart TD
    {... tree content ...}
\```
```

**Ordering**: All Critical findings first, then High findings. Within same severity, alphabetical by finding ID.

**Correlated findings**: Add note after header: "This finding is part of correlation group CG-{N}. See also: {peer finding IDs}."

### Location 2: Standalone Files in attack-trees/

**File naming**: `{finding-id}-attack-tree.md` (lowercase, hyphenated). Examples: `ag-1-attack-tree.md`, `s-1-attack-tree.md`

```markdown
# Attack Tree: {Finding ID} — {Brief threat description}

| Field | Value |
|-------|-------|
| Finding ID | {id} |
| Component | {component} |
| Risk Level | {Critical/High} |
| Threat | {threat summary from threats.md} |
| Correlation | {CG-N (if applicable) or "None"} |

\```mermaid
flowchart TD
    {... identical tree content as inline version ...}
\```
```

**Consistency rule**: Mermaid code blocks must be identical between inline and standalone versions.

**File inventory**: Verify `attack-trees/` contains exactly one file per Critical and High finding. No files for Medium, Low, or Note findings.

---

## Remediation Roadmap Generation

Generate Section 6: Remediation Roadmap. List all findings in strict priority order by risk level:

| Priority Tier | Risk Level | Timeline Guidance | Action |
|--------------|-----------|-------------------|--------|
| Immediate | Critical | Address before next deployment | Block release until resolved |
| Short-term | High | Address within current development cycle | Schedule in current sprint/iteration |
| Medium-term | Medium | Schedule for next planning cycle | Add to backlog with priority |
| Backlog | Low / Note | Track for future consideration | Document and revisit periodically |

Within the same priority tier, group findings by **component**.

### Roadmap Item Format

| Finding ID | Component | Mitigation | Effort | Dependencies |
|------------|-----------|------------|--------|--------------|
| AG-1 | LLM Agent Orchestrator | {mitigation text from threats.md — preserved verbatim} | High | Requires tool risk classification framework |
| AG-2 | MCP Tool Server | {mitigation text} | Medium | Depends on AG-1 risk tier implementation |

**Field rules**:
- **Finding ID**: Exact ID from `threats.md`
- **Component**: Exact component name from `threats.md` — no renaming
- **Mitigation**: Preserve verbatim from `threats.md` Section 7 (Recommended Actions). Do not rephrase or reinterpret.
- **Effort**: Qualitative assessment (Low / Medium / High) — see Effort Estimation below
- **Dependencies**: Prerequisites, related findings, or ordering constraints. "None" if none.

**Section introduction** (before the table): State total remediation items, distribution by priority tier, most impacted component, and suggested starting point.

---

### Effort Estimation Heuristics

Assign Low / Medium / High effort per roadmap item based on mitigation complexity (not time estimates).

#### Effort Levels

| Effort | Characteristics | Examples |
|--------|----------------|----------|
| **Low** | Configuration changes, parameter tuning, enabling existing features, policy updates | Enable rate limiting on existing API gateway; adjust token budget caps; update logging verbosity; add TLS certificate pinning configuration |
| **Medium** | New validation logic, access control additions, monitoring implementation, new middleware, schema changes | Implement input validation on tool call parameters; add role-based access control checks; deploy query pattern analysis; add document-level access controls to knowledge base |
| **High** | Architectural changes, new components, protocol redesign, new frameworks, cross-cutting infrastructure | Implement tool risk-tier classification framework; build human-in-the-loop approval workflow; deploy structured prompt template system with boundary enforcement; implement provenance tracking across RAG pipeline |

#### Assessment Rules

1. **Assess based on mitigation text**: Use the mitigation description only. Do not infer additional work.
2. **Compound mitigations**: Assess by **highest-effort individual action** (e.g., "Enable rate limiting (Low) and implement per-user budgets (Medium)" = Medium).
3. **Architectural indicators** (High effort): "implement framework," "redesign," "new component," "pipeline," "workflow system," "classification framework," "provenance tracking."
4. **Configuration indicators** (Low effort): "configure," "enable," "set," "adjust," "update parameter," "add to allowlist."
5. **Do not estimate time**: Never convert to hours, days, or sprints. Effort is relative complexity only.

---

### Correlation Consolidation for Roadmap

When Section 4a contains correlation groups, consolidate correlated findings into single roadmap items.

#### Consolidation Rules

1. **Single roadmap item per correlation group**: Use the **primary finding ID** (the first finding listed in the correlation group) as the roadmap item identifier.

2. **Combined mitigation scope**: Merge mitigation texts. Use most comprehensive version for overlapping mitigations; concatenate distinct aspects with clear delineation.

3. **Correlation scope notes**: Dependencies column format: `Correlated: {finding-id-1}, {finding-id-2} (CG-{N})`

4. **Effort reflects combined scope**: Assess based on combined remediation scope, not primary finding alone.

5. **Risk level inheritance**: Use highest risk level from any finding in the group (Critical + Medium = Critical tier).

#### Example

CG-1 containing AG-1 (Critical) and S-2 (Medium):

| Finding ID | Component | Mitigation | Effort | Dependencies |
|------------|-----------|------------|--------|--------------|
| AG-1 | LLM Agent Orchestrator | Classify tool operations into risk tiers; require human approval for irreversible and external actions; add iteration limits and timeouts. Additionally, enforce certificate pinning for external API connections to prevent redirected tool calls. | High | Correlated: AG-1, S-2 (CG-1) |

S-2 does not appear as a separate row -- consolidated into AG-1.

#### No Correlation Groups

If Section 4a contains "No cross-agent correlations detected" or is absent, skip consolidation. Each finding appears as its own roadmap item.
