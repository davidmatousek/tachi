---
source_agent: orchestrator
extracted_from: .claude/agents/tachi/orchestrator.md
version: 1.0.0
---

# Output Schema Tables, Validation Checklist, and Error Templates

## Output Format Specification

Every invocation produces two output files in the same output directory, with two additional files when Phase 5 is enabled:

1. **`threats.md`** — Human-readable threat model with YAML frontmatter followed by 7 required sections plus Section 4a (Correlated Findings).
2. **`threats.sarif`** — Machine-readable SARIF 2.1.0 JSON file containing the same findings mapped to the SARIF standard for integration with GitHub Code Scanning, VS Code SARIF Viewer, Azure DevOps, and other SARIF-compatible tools.
3. **`threat-report.md`** — (Phase 5, default-on) Narrative threat report with executive summary, attack trees, and prioritized remediation roadmap.
4. **`attack-trees/`** — (Phase 5, default-on) Directory of standalone Mermaid attack tree files, one per Critical and High finding.

Both files use the same finding data collected in Phase 3. The `threats.md` sections must appear in the order listed below. The `threats.sarif` generation instructions appear in the SARIF specification reference file.

### Frontmatter

The output begins with YAML frontmatter containing exactly these fields:

```yaml
---
schema_version: "1.3"
date: "YYYY-MM-DD"
input_format: "detected-or-declared-format"
classification: "confidential"
---
```

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Always `"1.2"` for this release. |
| `date` | string | ISO 8601 date when the threat model was generated. Format: `YYYY-MM-DD`. |
| `input_format` | string | The architecture input format that was analyzed. One of: `ascii`, `free-text`, `mermaid`, `plantuml`, `c4`. Set to the detected format when `format: auto`, or the explicitly declared format value. |
| `classification` | string | Always `"confidential"`. |

### Section 1: System Overview

Parsed summary of the architecture input. This section establishes the scope of the threat model by enumerating everything that was analyzed. It contains three tables.

**Components table** -- list every component identified in the architecture input:

| Component | Type | Description |
|-----------|------|-------------|
| _{component name}_ | _{External Entity \| Process \| Data Store \| Data Flow}_ | _{brief description of the component's role}_ |

**Data Flows table** -- describe data flows between components:

| Source | Destination | Data | Protocol |
|--------|-------------|------|----------|
| _{source component}_ | _{destination component}_ | _{what data moves}_ | _{transport protocol}_ |

**Technologies table** -- list technologies, frameworks, and protocols identified:

| Category | Technology | Version (if known) |
|----------|------------|--------------------|
| _{category}_ | _{technology name}_ | _{version or "unknown"}_ |

### Section 2: Trust Boundaries

Identified trust zones and boundary crossings derived from the architecture input.

**Trust Zones table**:

| Zone | Trust Level | Components |
|------|-------------|------------|
| _{zone name}_ | _{trust level description}_ | _{comma-separated component names}_ |

**Boundary Crossings table**:

| Crossing | From Zone | To Zone | Components | Controls |
|----------|-----------|---------|------------|----------|
| _{crossing name}_ | _{source zone}_ | _{destination zone}_ | _{components involved}_ | _{security controls at boundary}_ |

If the architecture input contains no explicit trust boundaries, include the section headers with a note stating that no trust boundaries were identified in the input. Do not omit the section.

### Section 3: STRIDE Tables

Six tables, one per STRIDE category. Each table contains threat findings for applicable components. Every finding row uses the fields defined below.

**ID prefix convention**:

| Prefix | Category |
|--------|----------|
| S | Spoofing |
| T | Tampering |
| R | Repudiation |
| I | Information Disclosure |
| D | Denial of Service |
| E | Elevation of Privilege |

**Finding row fields** (same for all 6 STRIDE tables):

| ID | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|---------------|--------|------------|--------|------------|------------|

When baseline-aware, an additional Status column is included after ID:

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|

- **ID**: Pattern `{S|T|R|I|D|E}-{N}` where N is a sequential integer starting at 1 within each category.
- **Component**: The target component name from the architecture input.
- **MAESTRO Layer**: The CSA MAESTRO architectural layer classification inherited from the component's Phase 1 classification (e.g., "L3 — Agent Framework"). Defaults to "Unclassified" if the component matched no layer keywords.
- **Threat**: Description of the identified threat.
- **Likelihood**: One of `LOW`, `MEDIUM`, `HIGH`.
- **Impact**: One of `LOW`, `MEDIUM`, `HIGH`.
- **Risk Level**: Computed from the OWASP 3x3 matrix (see below). One of `Critical`, `High`, `Medium`, `Low`, `Note`.
- **Mitigation**: Recommended countermeasure.

**OWASP 3x3 Risk Matrix** -- use this to compute Risk Level from Likelihood and Impact:

|                  | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|------------------|----------------|-------------------|-----------------|
| **HIGH Impact**  | Medium         | High              | Critical        |
| **MEDIUM Impact**| Low            | Medium            | High            |
| **LOW Impact**   | Note           | Low               | Medium          |

The six STRIDE tables are:
1. **Spoofing (S)** -- threats where an attacker assumes another identity
2. **Tampering (T)** -- threats where an attacker modifies data or code
3. **Repudiation (R)** -- threats where an attacker denies actions
4. **Information Disclosure (I)** -- threats where sensitive data is exposed
5. **Denial of Service (D)** -- threats where availability is degraded
6. **Elevation of Privilege (E)** -- threats where an attacker gains higher access

If a STRIDE category has no findings (because no components were dispatched to it, or the agent returned zero findings), include the table header row with no data rows.

### Section 4: AI Threat Tables

Two tables containing findings from AI-specific threat agents. Each finding row includes an OWASP Reference field in addition to the standard finding fields.

**ID prefix convention**:

| Prefix | Category |
|--------|----------|
| AG | Agentic Threats |
| LLM | LLM Threats |

**Finding row fields** (same for both AI tables):

| ID | Component | MAESTRO Layer | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|---------------|--------|------------------|------------|--------|------------|------------|

When baseline-aware, an additional Status column is included after ID:

| ID | Status | Component | MAESTRO Layer | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------------|------------|--------|------------|------------|

- **MAESTRO Layer**: The CSA MAESTRO architectural layer classification inherited from the component's Phase 1 classification. Same field as in STRIDE tables.
- **OWASP Reference**: The applicable OWASP identifier (e.g., `ASI-01`, `MCP-03`, `OWASP LLM01:2025`).

**5-agent-to-2-table mapping**:

| Output Table | Agents | Reference Standards |
|--------------|--------|---------------------|
| Agentic Threats (AG) | agent-autonomy, tool-abuse | OWASP Agentic Top 10, MCP Top 10 |
| LLM Threats (LLM) | prompt-injection, data-poisoning, model-theft | OWASP LLM Top 10 v2025 |

Findings from `agent-autonomy` and `tool-abuse` agents are grouped under the **AG** table. Findings from `prompt-injection`, `data-poisoning`, and `model-theft` agents are grouped under the **LLM** table.

If no AI agents were dispatched (because no components matched AI keywords), include both table headers with a note stating no AI-related components were identified. Do not omit the tables.

### Section 5: Coverage Matrix

Cross-reference matrix showing which components were analyzed for which threat categories. Components are rows, threat categories are columns.

| Component | S | T | R | I | D | E | AG | LLM | Total |
|-----------|---|---|---|---|---|---|----|-----|-------|

- Each cell contains the deduplicated count of findings identified for that component-category pair. When findings belong to a correlation group, the group contributes 1 to the count collectively.
- An em dash (`---`) indicates the component was analyzed for that category but no threats were found (analyzed but clean).
- `n/a` indicates the component was not dispatched to that category (not applicable per STRIDE-per-Element rules or AI keyword matching).
- The Total column contains the sum of all findings for that component.
- Include a **Total** row at the bottom summing each column.

### Section 6: Risk Summary

Aggregate counts of findings by risk level. Counts reflect deduplicated findings --- each correlation group counts as 1 unique threat at its group risk level. When the deduplicated total differs from the raw total, display the parenthetical raw count (e.g., `"5 (7 raw)"`).

| Risk Level | Count | Percentage |
|------------|-------|------------|
| Critical | _{dedup count}_ | _{percentage}%_ |
| High | _{dedup count}_ | _{percentage}%_ |
| Medium | _{dedup count}_ | _{percentage}%_ |
| Low | _{dedup count}_ | _{percentage}%_ |
| Note | _{dedup count}_ | _{percentage}%_ |
| **Total** | _{dedup total}_ | **100%** |

Percentages are computed as `(deduplicated count / deduplicated total) * 100`, rounded to one decimal place.

#### Risk by MAESTRO Layer

A subsection within the Risk Summary showing finding counts and highest severity grouped by CSA MAESTRO architectural layer. This subsection appears after the Risk Calibration Matrix and before Section 7.

| MAESTRO Layer | Finding Count | Highest Severity |
|---------------|---------------|------------------|
| _{layer name}_ | _{deduplicated count}_ | _{Critical\|High\|Medium\|Low\|Note}_ |

- **Ordering**: Rows are ordered by highest severity descending (Critical first), then by finding count descending within the same severity.
- **Omission**: Layers with zero findings are omitted from the table.
- **Deduplication**: Finding counts use deduplicated values — correlation groups count as 1.
- **"Unclassified" row**: If any findings have "Unclassified" as their MAESTRO layer, include an "Unclassified" row in the table. Do not omit it.

### Section 7: Recommended Actions

Prioritized list of all findings sorted by risk level descending (Critical first, Note last). Within the same risk level, findings are listed in the order they appear in the STRIDE and AI tables.

| Finding ID | Component | Threat | Risk Level | Mitigation |
|------------|-----------|--------|------------|------------|

This section provides a remediation roadmap. Critical and High findings should be addressed before deployment. Medium findings should be addressed within the current development cycle. Low and Note findings should be tracked for future consideration.

---

## Output Structural Validation Checklist

Before finalizing the output document, run the following validation checklist against the assembled `threats.md`. Every check must pass. If any check fails, correct the issue before producing the final output.

### Section Completeness

- [ ] Section 1 (System Overview) is present and contains the Components, Data Flows, and Technologies tables.
- [ ] Section 2 (Trust Boundaries) is present and contains the Trust Zones and Boundary Crossings tables (or the "no trust boundaries identified" note with empty table headers).
- [ ] Section 3 (STRIDE Tables) is present and contains exactly 6 tables (S, T, R, I, D, E), each with a table header row even if no data rows exist.
- [ ] Section 4 (AI Threat Tables) is present and contains exactly 2 tables (AG, LLM), each with a table header row even if no data rows exist.
- [ ] Section 4a (Correlated Findings) is present and contains the correlation group table with correct columns (Group, Findings, Component, Threat Summary, Risk Level), or the "No cross-agent correlations detected" text with empty table header when zero correlations exist.
- [ ] Section 4b (Resolved Findings) is present when a baseline was used. Contains resolved findings with columns: ID, Component, Threat, Last Risk Level, Resolution Reason. Omitted entirely when no baseline (first run).
- [ ] Section 5 (Coverage Matrix) is present and contains one row per component plus a Total row. All cells use the three-state model: integer (deduplicated count), `---` (analyzed but clean), or `n/a` (not applicable).
- [ ] Section 5 (Coverage Matrix) footnote is present when correlation groups exist, stating "Counts reflect deduplicated findings. N correlation groups merged M individual findings." Footnote is absent when zero correlation groups exist.
- [ ] Section 5a (Coverage Gate Results) is present and contains the Coverage Requirements Matrix showing each component's determined type and required vs. evaluated categories. Gap Resolution Details table present when gaps were detected.
- [ ] Section 6 (Risk Summary) is present and contains the Risk Calibration Matrix subsection, the "Risk by MAESTRO Layer" subsection, followed by one row per risk level (Critical, High, Medium, Low, Note) plus a Total row.
- [ ] Section 7 (Recommended Actions) is present and contains one row per finding.
- [ ] Section 8 (Delta Summary) is present when a baseline was used. Contains baseline reference, status count table, and finding-level change lines grouped by delta status. Omitted when no baseline.

### Frontmatter Validation

- [ ] `schema_version` is `"1.2"`.
- [ ] `date` is a valid ISO 8601 date in `YYYY-MM-DD` format.
- [ ] `input_format` is one of: `ascii`, `free-text`, `mermaid`, `plantuml`, `c4`.
- [ ] `classification` is `"confidential"`.
- [ ] `run_id` is present in format `YYYY-MM-DDTHH-MM-SS`.
- [ ] `baseline.source`, `baseline.date`, `baseline.finding_count`, `baseline.run_id` are present (null when no baseline, populated when baseline used).
- [ ] `coverage_gate.status` is one of: `"pass"`, `"warn"`.
- [ ] `coverage_gate.gaps` is a list (empty when no gaps; each entry has `component`, `missing_category`, `resolution`).

### Finding ID Validation

- [ ] Every finding ID in the STRIDE tables matches the pattern `{S|T|R|I|D|E}-{N}` where N is a positive integer.
- [ ] Every finding ID in the AI tables matches the pattern `{AG|LLM}-{N}` where N is a positive integer.
- [ ] IDs are sequentially numbered within each category starting at 1, with no gaps.
- [ ] No duplicate IDs exist within any table or across tables of the same category.

### Field Completeness

- [ ] Every finding row in the STRIDE tables has all 9 required fields populated: ID, Status, Component, MAESTRO Layer, Threat, Likelihood, Impact, Risk Level, Mitigation. Status is one of: `NEW`, `UNCHANGED`, `UPDATED`. MAESTRO Layer is one of L1-L7 or "Unclassified".
- [ ] Every finding row in the AI tables has all 10 required fields populated: ID, Status, Component, MAESTRO Layer, Threat, OWASP Reference, Likelihood, Impact, Risk Level, Mitigation. Status is one of: `NEW`, `UNCHANGED`, `UPDATED`. MAESTRO Layer is one of L1-L7 or "Unclassified".
- [ ] No field contains an empty value or placeholder text.
- [ ] Every finding has exactly one delta status annotation. When no baseline is present, all findings have Status `NEW`.

### Risk Level Consistency

- [ ] Every finding's `risk_level` matches the OWASP 3x3 matrix computation for its `likelihood` and `impact` values.
- [ ] `likelihood` values are one of: `LOW`, `MEDIUM`, `HIGH`.
- [ ] `impact` values are one of: `LOW`, `MEDIUM`, `HIGH`.
- [ ] `risk_level` values are one of: `Critical`, `High`, `Medium`, `Low`, `Note`.

### Cross-Section Consistency

- [ ] Coverage matrix cell counts reflect deduplicated counts: uncorrelated findings count individually, correlation group members contribute 1 collectively per component-category pair.
- [ ] Coverage matrix Total column values equal the sum of deduplicated finding counts in each component's row (`---` and `n/a` cells contribute 0).
- [ ] Coverage matrix Total row values equal the sum of deduplicated finding counts in each category's column.
- [ ] All correlation group member IDs (CG-N entries in Section 4a) reference finding IDs that exist in the STRIDE tables (Section 3) or AI tables (Section 4).
- [ ] Risk summary counts reflect deduplicated totals: each correlation group counts as 1 at its group risk level. When the deduplicated total differs from the raw total, counts include the parenthetical raw count (e.g., "5 (7 raw)").
- [ ] Risk summary Total equals the deduplicated grand total of all findings.
- [ ] Risk summary percentages are computed from the deduplicated total as denominator and sum to exactly 100%.
- [ ] Recommended actions list contains every finding from all 8 tables exactly once (raw count, not deduplicated --- each individual finding has its own mitigation).
- [ ] Recommended actions list row count equals the raw finding total (not the deduplicated total).

### SARIF Output (`threats.sarif`)

- [ ] A `threats.sarif` file is produced in the same output directory as `threats.md`.
- [ ] The SARIF file is valid JSON with `$schema`, `version: "2.1.0"`, and `runs[]` at the top level.
- [ ] `tool.driver.name` is `"Tachi"` and `rules[]` contains only categories that produced findings.
- [ ] The number of SARIF `results[]` matches the deduplicated finding count in `threats.md`.
- [ ] Every result has `ruleId`, `message.text`, `level`, `locations[]`, and `partialFingerprints`.
- [ ] Every `ruleId` has a corresponding entry in `tool.driver.rules[]`.

### Phase 5 Outputs (when Phase 5 is enabled)

- [ ] `threat-report.md` exists in the output directory
- [ ] `threat-report.md` contains YAML frontmatter with `schema_version: "1.0"`, `date`, `source_file`, `finding_count`, `risk_distribution`, `attack_tree_count`
- [ ] `threat-report.md` contains all required sections (## 1. Executive Summary through ## 7. Appendix: Finding Reference, plus ## 6. Cross-Layer Attack Chains when chains exist)
- [ ] `attack-trees/` directory exists in the output directory
- [ ] `attack-trees/` contains one file per Critical and High finding, named `{finding-id}-attack-tree.md`
- [ ] Finding count in `threat-report.md` frontmatter matches the finding count in `threats.md`
- [ ] Appendix: Finding Reference in `threat-report.md` contains every finding ID from `threats.md`

### Phase 3.5 Outputs (conditional on chain detection)

- [ ] `attack-chains.md` exists in the output directory when cross-layer chains are detected
- [ ] `attack-chains.md` is absent when no cross-layer chains are detected (no empty artifact)
- [ ] `attack-chains.md` contains YAML frontmatter with `schema_version: "1.0"`, `date`, `chain_count`, `surfaced_count`
- [ ] `attack-chains.md` Section 1 (Chain Summary) contains a table with columns: Chain ID, Title, Layers, Max Severity, Finding Count, Chain-Breaking Target
- [ ] `attack-chains.md` Section 2 (Chain Details) contains one subsection per chain with: title, layer progression, member findings table (Finding ID, MAESTRO Layer, Role, Component, Category, Severity), attack progression narrative with causal vocabulary, and chain-breaking controls
- [ ] Chain IDs match pattern `CHAIN-NNN` with sequential numbering in ranked order
- [ ] Each chain spans at least 2 distinct MAESTRO layers
- [ ] Each surfaced chain has at least one Critical or High severity member finding
- [ ] Chain narratives use canonical causal vocabulary ("enables," "triggers," "shifts," "manifests as")
- [ ] Each chain has at least one chain-breaking control with heuristic disclaimer
- [ ] `has-attack-chains` boolean is set for downstream consumption by threat-report agent and PDF pipeline

---

## Error Handling

This section consolidates all error conditions and edge-case handling into a single reference. Phases 1 through 4 reference these error specifications at the points where they are triggered. The three error responses (UNSUPPORTED_FORMAT, NO_COMPONENTS, INVALID_FORMAT_VALUE) are terminal --- when triggered, stop processing and return the error response instead of a `threats.md` document. The two edge-case handlers (ambiguous classification, non-conforming findings) are non-terminal --- they allow processing to continue with appropriate annotations.

---

### UNSUPPORTED_FORMAT Error

**Trigger**: The `format` field is set to `auto` (or not specified), and heuristic detection fails to match any of the 5 supported format recognition patterns. This error is raised during Phase 1 format detection after all 5 priority-ordered pattern checks have been exhausted without a match.

**When to raise**: After testing ASCII (Priority 1), Free-text (Priority 2), Mermaid (Priority 3), PlantUML (Priority 4), and C4 (Priority 5) recognition patterns against the architecture input, and none match.

**Response**: Return the following error response instead of a `threats.md` document. Do not proceed to component extraction or any subsequent phase.

```yaml
error:
  code: UNSUPPORTED_FORMAT
  message: "Input format not recognized."
  supported_formats:
    - ascii
    - free-text
    - mermaid
    - plantuml
    - c4
  guidance: >
    The architecture input did not match any supported format's recognition
    patterns during auto-detection. To resolve this:

    1. Set the 'format' field explicitly to one of the supported formats
       listed above, bypassing auto-detection.
    2. Or restructure the input to match one of the supported format
       recognition patterns:
       - ASCII: Use box-drawing characters (+--+, |, [...]) with arrow
         connectors (-->, <--, <-->).
       - Free-text: Describe components and relationships in natural
         language prose.
       - Mermaid: Use 'graph', 'flowchart', or 'sequenceDiagram' keywords
         with node and edge definitions.
       - PlantUML: Use @startuml/@enduml delimiters with component
         declarations.
       - C4: Use Person(...), System(...), Container(...), or Component(...)
         function calls with Rel(...) declarations.

    See ../../../docs/INTERFACE-CONTRACT.md Section 1 for complete format examples
    and ../../../schemas/input.yaml for recognition pattern details.
```

This error is distinct from INVALID_FORMAT_VALUE. UNSUPPORTED_FORMAT applies when `format: auto` detection fails. INVALID_FORMAT_VALUE applies when the `format` field contains a value outside the allowed enum (see below).

---

### NO_COMPONENTS Error

**Trigger**: The architecture input is in a recognized format (format detection succeeded), but parsing finds fewer than 1 identifiable component or 0 data flows between components. This error is raised during the Phase 1 component inventory self-check after extraction and classification are complete.

**When to raise**: After format detection succeeds and component extraction completes, the self-check verifies minimum requirements. If the component inventory contains fewer than 1 component or 0 data flows, raise this error.

**Response**: Return the following error response instead of a `threats.md` document. Do not proceed to Phase 2.

```yaml
error:
  code: NO_COMPONENTS
  message: "No architecture components or data flows detected in input."
  minimum_requirements:
    components: 1
    data_flows: 1
  guidance: >
    The input was recognized as a valid format, but it does not contain
    enough architectural structure for threat analysis. A valid architecture
    input must include:

    1. At least one identifiable component — a service, database, user,
       agent, API, gateway, or any system element that can be classified
       as a DFD element type (External Entity, Process, Data Store, or
       Data Flow).
    2. At least one data flow or relationship — a connection, API call,
       message, or data transfer between two components indicating how
       data moves through the system.

    Common causes of this error:
    - Input contains only a title or heading with no component descriptions.
    - Input describes a single component with no relationships to other
      components.
    - Input contains diagram syntax (e.g., Mermaid keywords) but no
      node or edge definitions.

    See ../../../docs/INTERFACE-CONTRACT.md Section 1 for example inputs in each
    supported format that meet the minimum requirements.
```

---

### INVALID_FORMAT_VALUE Error

**Trigger**: The `format` field in the input is set to a value that is not one of the allowed enum values: `auto`, `ascii`, `free-text`, `mermaid`, `plantuml`, `c4`. This error is raised at the start of Phase 1 format detection, before any parsing or heuristic detection begins.

**When to raise**: Before any format detection or parsing occurs, check the `format` field. If it is present and its value is not one of the 6 allowed values listed above, raise this error immediately.

**Response**: Return the following error response instead of a `threats.md` document. Do not proceed to any parsing or detection.

```yaml
error:
  code: INVALID_FORMAT_VALUE
  message: "The 'format' field contains an invalid value."
  provided: "<the-invalid-value-from-input>"
  allowed_values:
    - auto
    - ascii
    - free-text
    - mermaid
    - plantuml
    - c4
  guidance: >
    The 'format' field must be one of the allowed values listed above,
    or omitted entirely (which defaults to 'auto'). To resolve this:

    1. Set 'format' to one of the 6 allowed values.
    2. Use 'auto' (or omit the field) to enable heuristic format
       detection based on recognition patterns.
    3. Use an explicit format value ('ascii', 'free-text', 'mermaid',
       'plantuml', 'c4') to bypass auto-detection and parse the input
       directly with the specified format's parser.

    See ../../../docs/INTERFACE-CONTRACT.md Section 1 for the format field
    specification and supported values.
```

Replace `<the-invalid-value-from-input>` with the actual value provided in the input's `format` field so the user can see exactly what was rejected.

This error is distinct from UNSUPPORTED_FORMAT. INVALID_FORMAT_VALUE applies when the `format` field itself contains an invalid enum value. UNSUPPORTED_FORMAT applies when `format: auto` detection fails to match the input content against any recognition pattern.

---

### Error Evaluation Order

When evaluating the `format` field and architecture input, check for errors in this order:

1. **INVALID_FORMAT_VALUE**: Check the `format` field value first. If it contains an invalid value, return this error immediately. No parsing occurs.
2. **UNSUPPORTED_FORMAT**: If `format: auto`, run heuristic detection. If no patterns match, return this error. No component extraction occurs.
3. **NO_COMPONENTS**: If format detection succeeds, extract components and data flows. If the minimum requirements are not met, return this error.

This order ensures that format-level errors are caught before any parsing work begins, and content-level errors are caught before any dispatch work begins.

---

### Ambiguous DFD Classification Handling

When a component cannot be confidently classified into one of the four DFD element types (External Entity, Process, Data Store, Data Flow), the orchestrator handles the ambiguity predictably rather than blocking or guessing without disclosure. This is a non-terminal condition --- processing continues with the classification applied.

#### Default Classification Rule

Default to **Process** when classification is uncertain. Process is the broadest DFD element type, with all 6 STRIDE categories applicable (S, T, R, I, D, E). Defaulting to Process ensures the component receives the maximum threat coverage, preventing undertesting due to misclassification.

#### Human Review Flag

When defaulting to Process due to ambiguity, add the following annotation in the component's Description field in the System Overview (Section 1) Components table:

```
[Classification uncertain -- defaulted to Process for maximum threat coverage]
```

This annotation signals to human reviewers that the classification should be verified. The threat analysis results remain valid --- a component classified as Process may receive findings in categories that would not apply under a different classification (e.g., Spoofing or Elevation of Privilege findings for what might actually be a Data Store). Human reviewers can filter out inapplicable findings after verifying the correct classification.

#### AI Keyword Ambiguity

The keyword `"model"` is inherently ambiguous in architecture descriptions. It may refer to:

- A machine learning model or LLM (AI-relevant --- LLM agents should be dispatched)
- A data model, domain model, or object model (not AI-relevant --- LLM agents produce false-positive findings)

When the keyword `"model"` matches a component name or description:

1. **Dispatch LLM agents** --- err on the side of coverage. If the component is an LLM, omitting LLM agents would be a critical gap in the threat model.
2. **Add an ambiguity note** in the dispatch table's AI Categories column or as a footnote: `"Keyword 'model' matched -- may refer to data model rather than LLM. AI agents dispatched for coverage; review findings for relevance."`
3. **Do not suppress dispatch** based on ambiguity assessment. The cost of a false positive (extra findings that can be filtered) is lower than the cost of a false negative (missed LLM threats).

Other AI keywords (`"LLM"`, `"GPT"`, `"Claude"`, `"agent"`, `"autonomous"`, `"orchestrator"`, `"MCP server"`, `"tool server"`, `"plugin"`) are not ambiguous in typical architecture descriptions and do not require ambiguity annotations.

---

### Non-Conforming Finding Handling

Agent findings that do not conform to the schema defined in `../../../schemas/finding.yaml` are handled gracefully. The orchestrator does not silently drop non-conforming findings, as this would create invisible gaps in the threat model.

#### Detection

A finding is non-conforming when any of the following conditions are true:

- A required field is missing (`id`, `category`, `component`, `threat`, `likelihood`, `impact`, `risk_level`, `mitigation`).
- A field value is outside the allowed enum (`likelihood` not in [LOW, MEDIUM, HIGH], `impact` not in [LOW, MEDIUM, HIGH], `risk_level` not in [Critical, High, Medium, Low, Note]).
- The `id` does not match the expected pattern (`{S|T|R|I|D|E|AG|LLM}-{N}`).
- The `category` does not match the dispatched agent type.
- The `risk_level` does not match the OWASP 3x3 matrix computation for the given `likelihood` and `impact` (note: this specific case is handled by the Risk Level Validation correction protocol in Phase 3, not by the non-conforming finding handler).

#### Handling Protocol

When a non-conforming finding is detected:

1. **Do not drop the finding.** Include it in the output tables with whatever valid fields it contains.
2. **Attempt field recovery** where possible:
   - If `id` is missing or malformed, assign the next sequential ID in the appropriate category based on the dispatching agent.
   - If `likelihood` or `impact` contain non-enum values, map to the closest valid value (e.g., "high" maps to "HIGH", "moderate" maps to "MEDIUM") or default to "MEDIUM" if no reasonable mapping exists. Recompute `risk_level` from the corrected values.
   - If `component` is missing, use the target component name from the dispatch record.
   - If `mitigation` is missing, enter: `"[No mitigation provided by agent -- review required]"`.
3. **Annotate the finding** by appending a warning to the Mitigation field: `"[WARNING: Finding did not fully conform to ../../../schemas/finding.yaml -- {description of non-conformance}. Included for review.]"`. Replace `{description of non-conformance}` with a brief description of what was wrong (e.g., "missing likelihood field, defaulted to MEDIUM", "malformed ID, reassigned").
4. **Include in all downstream computations** -- the annotated finding is counted in the coverage matrix, risk summary, and recommended actions list like any other finding.

#### Rationale

Silent dropping creates invisible gaps: a component-category pair that was analyzed and produced findings would appear as `---` (zero findings) in the coverage matrix, indistinguishable from a genuinely clean analysis. By including non-conforming findings with annotations, the threat model remains complete and human reviewers can identify findings that need additional scrutiny.

---

### Coverage Matrix: Three-State Cell Model

The coverage matrix (Section 5) uses a three-state cell model to distinguish between findings present, analyzed but clean, and not applicable:

1. **Deduplicated finding count** (integer) --- The component was dispatched to the category and findings were identified. The count reflects deduplicated findings: correlation group members contribute 1 collectively, uncorrelated findings contribute 1 each.

2. **Analyzed, zero findings (`---`)** --- The component was dispatched to a category's agent, and the agent returned zero findings. The component was analyzed for that threat category, and no threats were identified. Display an em dash: `---`.

3. **Not applicable (`n/a`)** --- The component was not dispatched to that category because it was not applicable. For STRIDE categories, this means the component's DFD element type does not include that category (e.g., an External Entity was not dispatched to Tampering). For AI categories, this means the component's name and description did not match any AI keywords. Display: `n/a`.

This distinction is critical for threat model consumers:

- A `---` cell means "we looked and found nothing" --- the absence of findings is an affirmative result.
- A `n/a` cell means "we did not look" --- the absence of findings is expected because the analysis was not applicable.

When reviewing a threat model for completeness, `n/a` cells are expected and do not indicate gaps. Cells with `---` confirm that the analysis was performed. Cells with finding counts indicate identified threats. All three states must be visually distinguishable in the matrix.
