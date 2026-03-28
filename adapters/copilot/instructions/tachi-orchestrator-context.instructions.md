---
applyTo: "docs/architecture/**,*.mermaid,*.puml,*.drawio"
---

# Tachi Orchestrator -- Full Context Instructions

This instructions file provides the complete detailed context for the tachi orchestrator agent. It is automatically loaded when architecture files are present in the workspace. The orchestrator agent file contains the core identity, methodology overview, and dispatch rules summary. This file contains the full phase instructions, output templates, SARIF generation specification, correlation detection algorithm, and error handling details.

---

## Output Format Specification

Every invocation produces two output files in the same output directory, with two additional files when Phase 5 is enabled:

1. **`threats.md`** -- Human-readable threat model with YAML frontmatter followed by 7 required sections plus Section 4a (Correlated Findings).
2. **`threats.sarif`** -- Machine-readable SARIF 2.1.0 JSON file containing the same findings mapped to the SARIF standard for integration with GitHub Code Scanning, VS Code SARIF Viewer, Azure DevOps, and other SARIF-compatible tools.
3. **`threat-report.md`** -- (Phase 5, default-on) Narrative threat report with executive summary, attack trees, and prioritized remediation roadmap.
4. **`attack-trees/`** -- (Phase 5, default-on) Directory of standalone Mermaid attack tree files, one per Critical and High finding.

Both files use the same finding data collected in Phase 3. The `threats.md` sections must appear in the order listed below. The `threats.sarif` generation instructions appear in the "SARIF Output Generation" section after the Output Structural Validation Checklist.

### Frontmatter

The output begins with YAML frontmatter containing exactly these fields:

```yaml
---
schema_version: "1.1"
date: "YYYY-MM-DD"
input_format: "detected-or-declared-format"
classification: "confidential"
---
```

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Always `"1.1"` for this release. |
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

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|

- **ID**: Pattern `{S|T|R|I|D|E}-{N}` where N is a sequential integer starting at 1 within each category.
- **Component**: The target component name from the architecture input.
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

| ID | Component | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------------|------------|--------|------------|------------|

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

Aggregate counts of findings by risk level. Counts reflect deduplicated findings -- each correlation group counts as 1 unique threat at its group risk level. When the deduplicated total differs from the raw total, display the parenthetical raw count (e.g., `"5 (7 raw)"`).

| Risk Level | Count | Percentage |
|------------|-------|------------|
| Critical | _{dedup count}_ | _{percentage}%_ |
| High | _{dedup count}_ | _{percentage}%_ |
| Medium | _{dedup count}_ | _{percentage}%_ |
| Low | _{dedup count}_ | _{percentage}%_ |
| Note | _{dedup count}_ | _{percentage}%_ |
| **Total** | _{dedup total}_ | **100%** |

Percentages are computed as `(deduplicated count / deduplicated total) * 100`, rounded to one decimal place.

### Section 7: Recommended Actions

Prioritized list of all findings sorted by risk level descending (Critical first, Note last). Within the same risk level, findings are listed in the order they appear in the STRIDE and AI tables.

| Finding ID | Component | Threat | Risk Level | Mitigation |
|------------|-----------|--------|------------|------------|

This section provides a remediation roadmap. Critical and High findings should be addressed before deployment. Medium findings should be addressed within the current development cycle. Low and Note findings should be tracked for future consideration.

---

## Phase 1: Scope -- "What are we working on?"

This phase answers the first OWASP threat modeling question: **What are we working on?**

Phase objectives:

1. Detect the input format (or use the explicitly declared format).
2. Extract all components from the architecture input.
3. Classify each component as a DFD element type (External Entity, Process, Data Store, or Data Flow).
4. Identify trust boundaries, trust zones, and boundary crossings.
5. Produce the System Overview (Section 1) and Trust Boundaries (Section 2) of the output document.
6. Produce a visible intermediate component inventory for validation before proceeding to Phase 2.

Do not proceed to Phase 2 until this phase is complete and the intermediate component inventory has been produced.

---

### Format Detection

Determine the architecture input format before parsing. There are two modes:

**Explicit format override**: If the `format` field in the input is set to a value other than `auto`, use that format's parser directly. Skip heuristic detection entirely. If the value is not one of the allowed values (`ascii`, `free-text`, `mermaid`, `plantuml`, `c4`), return an `INVALID_FORMAT_VALUE` error (see Error Handling section).

**Heuristic detection** (`format: auto`): When `format` is `auto` (or not specified), attempt to detect the format by testing recognition patterns in the following priority order. Use the first format whose patterns match. If no format matches, return an `UNSUPPORTED_FORMAT` error (see Error Handling section).

#### Priority 1: ASCII

Recognition patterns:
- Box-drawing characters: `+--+`, `|`, `[...]`
- Arrow indicators: `-->`, `<--`, `<-->`
- Component labels enclosed in brackets or boxes

If the input contains box-drawing characters forming visual structures with arrow connectors, classify as ASCII format.

#### Priority 2: Free-text

Recognition patterns:
- No diagram syntax detected (no Mermaid keywords, no PlantUML delimiters, no C4 function calls, no box-drawing characters)
- Prose description of components and relationships
- Natural language narrative format

Free-text is the fallback for inputs that contain identifiable components and relationships described in natural language but do not match any diagramming syntax. If the input has no diagram syntax but does contain prose describing a system architecture, classify as free-text format.

#### Priority 3: Mermaid

Recognition patterns:
- Keywords: `graph`, `flowchart`, `sequenceDiagram`
- Node definitions: `A[Label]`, `B((Label))`, `C{Label}`
- Edge definitions: `-->`, `--->`, `-.->`, `-->`

If the input contains Mermaid diagram keywords (`graph`, `flowchart`, or `sequenceDiagram`) along with node and edge definitions, classify as Mermaid format.

#### Priority 4: PlantUML

Recognition patterns:
- Delimiters: `@startuml` / `@enduml`
- Component declarations: `[Component]`, `actor`, `database`
- Relationship arrows: `->`, `-->`, `.>`

If the input contains `@startuml` / `@enduml` delimiters with component declarations, classify as PlantUML format.

#### Priority 5: C4

Recognition patterns:
- Keywords: `Person`, `System`, `Container`, `Component`
- C4 function syntax: `Person(...)`, `System(...)`, `Container(...)`, `ContainerDb(...)`
- Relationship declarations: `Rel(...)`

If the input contains C4 model function calls (`Person(...)`, `System(...)`, `Container(...)`, etc.) with relationship declarations, classify as C4 format.

Record the detected (or declared) format. This value is used for the `input_format` field in the output frontmatter.

---

### Component Extraction and DFD Classification

Parse the architecture input using the detected format and extract all identifiable components. Classify each component as one of the four DFD (Data Flow Diagram) element types defined below.

#### DFD Element Types

**External Entity** -- Users, external systems, third-party services, or anything that exists outside the system boundary. External entities interact with the system but are not controlled by it.

Classification signals:
- Labeled as user, client, customer, external service, third-party provider, browser, mobile app
- Positioned outside trust boundaries or system boundaries in diagrams
- Described as sending requests to or receiving responses from the system

Examples: "User", "External API", "Third-party Auth Provider", "Mobile Client", "Browser"

**Process** -- Services, applications, servers, agents, orchestrators, or any component that actively processes, transforms, or routes data. Processes are the most broadly threatened element type (subject to all 6 STRIDE categories).

Classification signals:
- Labeled as service, server, gateway, handler, controller, agent, orchestrator, engine, worker, processor
- Described as receiving input, performing operations, and producing output
- Acts as an intermediary between other components

Examples: "API Gateway", "Auth Service", "LLM Agent Orchestrator", "MCP Tool Server", "Payment Processor"

**Data Store** -- Databases, file systems, caches, knowledge bases, message queues, or any component that persists or buffers data.

Classification signals:
- Labeled as database, DB, cache, store, queue, repository, knowledge base, file system, bucket, log
- Described as storing, persisting, buffering, or retaining data
- In Mermaid diagrams, often uses the `[( )]` cylinder notation

Examples: "User DB", "Knowledge Base", "Redis Cache", "Message Queue", "S3 Bucket"

**Data Flow** -- Connections, API calls, messages, or data transfers between components. Data flows represent the movement of data through the system and are typically represented as arrows or relationships in diagrams.

Classification signals:
- Represented as arrows, edges, or relationship lines in diagrams
- Described as API calls, requests, responses, messages, or data transfers between named components
- Has a source component and a destination component

Examples: "HTTPS Request from Client to Gateway", "SQL Query from Service to DB", "gRPC call between microservices"

#### Ambiguous Classification

When a component cannot be confidently classified into one of the four DFD element types, apply the following rule:

- Default to **Process** (broadest STRIDE coverage -- all 6 categories apply).
- Flag the classification for human review by adding a note in the component's Description field: `"[Classification uncertain -- defaulted to Process for maximum threat coverage]"`.

This ensures no component receives insufficient threat analysis due to misclassification.

#### Format-Specific Extraction

**ASCII**: Extract components from box-drawing structures (`+--+...+--+`) and bracket labels (`[Label]`). Extract data flows from arrow connectors (`-->`, `<--`, `<-->`). Each box or bracketed label is a component. Each arrow between components is a data flow.

**Free-text**: Extract components by identifying nouns and noun phrases that refer to system elements (services, databases, users, APIs, agents). Extract data flows from verbs and phrases describing interactions between components (sends, queries, forwards, connects to, calls). Parse sentence structure to identify source-destination relationships.

**Mermaid**: Extract components from node definitions (`A[Label]`, `B((Label))`, `C{Label}`, `D[(Label)]`). The label text inside the delimiters is the component name. Extract data flows from edge definitions (`-->`, `--->`, `-.->`) connecting nodes. `subgraph` blocks define trust boundaries (see Trust Boundary Identification below), not components -- the components are the nodes within them.

**PlantUML**: Extract components from declarations: `actor` for external entities, `[Component]` for processes, `database` for data stores, and other stereotype-annotated elements. Extract data flows from relationship arrows (`->`, `-->`, `.>`). Boundary blocks (`boundary`, `rectangle`) define trust boundaries, not components.

**C4**: Extract components from C4 function calls: `Person(...)` for external entities, `System(...)` / `Container(...)` / `Component(...)` for processes, `ContainerDb(...)` / `ComponentDb(...)` for data stores. The second argument in each function call is the display label. Extract data flows from `Rel(...)` declarations. `System_Boundary(...)` and `Enterprise_Boundary(...)` define trust boundaries, not components.

---

### Trust Boundary Identification

After extracting components and data flows, identify trust boundaries in the architecture input. Trust boundaries define zones where the security posture changes. Capture the following information:

- **Zone names**: The named regions or groupings in the architecture.
- **Zone components**: Which components belong to each zone.
- **Boundary crossings**: Data flows that cross from one trust zone to another.

#### Format-Specific Trust Boundary Notation

**Mermaid**: Trust boundaries are defined by `subgraph` blocks. Each `subgraph` name is a trust zone. Components (nodes) within the `subgraph ... end` block belong to that zone. Data flows (edges) connecting nodes in different subgraphs are boundary crossings.

**ASCII**: Trust boundaries are indicated by dashed lines (`- - -` or `---`) or labeled zones. Look for labels such as "Trust Boundary", "DMZ", "Internal Network", or similar zone descriptors near dashed-line separators. Components above and below the dashed line belong to different trust zones.

**PlantUML**: Trust boundaries are defined by the `boundary` keyword or `rectangle` blocks with `<<boundary>>` stereotype. Components declared within a boundary block belong to that trust zone. Data flows connecting components in different boundary blocks are boundary crossings.

**C4**: Trust boundaries are defined by `System_Boundary(...)` or `Enterprise_Boundary(...)` function calls. Components declared within a boundary block belong to that trust zone. Data flows (`Rel(...)`) connecting components across boundaries are boundary crossings.

**Free-text**: Trust boundaries are indicated by section headers (e.g., "Internal Network", "DMZ"), explicit markers (e.g., "Trust boundary:", "A trust boundary exists between..."), or descriptive phrases that delineate zones (e.g., "the external zone and the internal network"). Parse the prose to identify which components belong to which zones.

#### No Trust Boundaries

If the architecture input contains no explicit trust boundaries, include the Trust Boundaries section (Section 2) in the output with the Trust Zones and Boundary Crossings table headers but no data rows. Add a note: "No trust boundaries were identified in the architecture input." Do not omit the section.

---

### System Overview Assembly

Using the extracted components, data flows, trust boundaries, and any technology information, assemble Section 1 (System Overview) and Section 2 (Trust Boundaries) of the output document.

#### Section 1: System Overview

Produce three tables:

**Components table** -- one row per identified component:

| Component | Type | Description |
|-----------|------|-------------|
| _{component name}_ | _{External Entity \| Process \| Data Store \| Data Flow}_ | _{brief description of the component's role}_ |

- **Component**: The name as it appears in the architecture input.
- **Type**: The DFD element type assigned during classification.
- **Description**: A brief description of the component's role in the system. Derive this from the architecture input context (labels, annotations, surrounding text). If no description can be inferred, state the component type and its connections.

**Data Flows table** -- one row per identified data flow:

| Source | Destination | Data | Protocol |
|--------|-------------|------|----------|
| _{source component}_ | _{destination component}_ | _{what data moves}_ | _{transport protocol}_ |

- **Source**: The component where the data flow originates.
- **Destination**: The component where the data flow terminates.
- **Data**: A description of what data moves along this flow. Infer from labels, annotations, or context. If not specified in the input, describe the likely data based on the components involved.
- **Protocol**: The transport protocol used. Populate from explicit labels in the input (e.g., "HTTPS", "gRPC", "SQL"). If not specified, enter "Not specified".

**Technologies table** -- list technologies, frameworks, and protocols identified:

| Category | Technology | Version (if known) |
|----------|------------|--------------------|
| _{category}_ | _{technology name}_ | _{version or "Not specified"}_ |

- Populate from explicit technology mentions in the architecture input (language names, framework names, database engines, protocol specifications, cloud services).
- The Technologies table may have sparse data. Populate what can be inferred from the input. If no technologies are explicitly mentioned, include the table header with no data rows and add a note: "No technologies were explicitly identified in the architecture input."

#### Section 2: Trust Boundaries

Produce two tables using the trust boundary data captured during identification:

**Trust Zones table**:

| Zone | Trust Level | Components |
|------|-------------|------------|
| _{zone name}_ | _{trust level description}_ | _{comma-separated component names}_ |

**Boundary Crossings table**:

| Crossing | From Zone | To Zone | Components | Controls |
|----------|-----------|---------|------------|----------|
| _{crossing name}_ | _{source zone}_ | _{destination zone}_ | _{components involved}_ | _{security controls at boundary}_ |

- For trust level, infer from the zone name and position (e.g., "Public Internet" is "Untrusted", "Internal Network" is "Trusted").
- For controls, populate from explicit mentions in the input. If no controls are specified, enter "Not specified".
- If no trust boundaries were identified, include both table headers with no data rows and the note described in Trust Boundary Identification above.

---

### Component Inventory (Intermediate Output)

Before proceeding to Phase 2, produce a visible intermediate artifact listing the complete component inventory. This enables validation that parsing and classification are correct before dispatch begins.

Label this section clearly:

```
### Component Inventory (Intermediate)
```

The intermediate output must include:

1. **Detected format**: State the input format that was detected or declared.
2. **Component list**: A table with columns: Name, DFD Type, Description -- one row per component.
3. **Data flow count**: The total number of data flows identified.
4. **Trust boundary summary**: The number of trust zones identified, or "None identified" if no trust boundaries were found.

#### Self-Check

After producing the intermediate component inventory, verify the following minimum requirements:

- At least **1 component** has been identified.
- At least **1 data flow** has been identified.

If either requirement is not met, stop processing and return the `NO_COMPONENTS` error (see Error Handling section). Do not proceed to Phase 2.

If both requirements are met, proceed to Phase 2: Determine Threats.

---

## Phase 2: Determine Threats -- "What can go wrong?"

This phase answers the second OWASP threat modeling question: **What can go wrong?**

Phase 2 REQUIRES the component inventory produced by Phase 1 as input. Every component identified in Phase 1 is dispatched to the applicable threat agents based on two deterministic rule sets:

1. **STRIDE-per-Element normalization** -- determines which of the 6 STRIDE categories apply to each component, based on its DFD element type.
2. **AI keyword dispatch** -- determines whether AI-specific threat agents (LLM and/or AG) are additionally dispatched, based on keyword matching against component names and descriptions.

Phase objectives:

1. Apply the STRIDE-per-Element normalization table to map each component's DFD type to its applicable STRIDE categories.
2. Apply AI keyword dispatch rules to identify components requiring AI-specific threat analysis.
3. Produce a visible dispatch table as an intermediate artifact for validation.
4. Invoke threat agents with full architecture context.

Do not invoke any agents until the dispatch table intermediate artifact has been produced and validated.

---

### STRIDE-per-Element Normalization

Each component from the Phase 1 inventory is mapped to its applicable STRIDE threat categories based on its DFD element type. Agents are dispatched only for applicable categories, ensuring focused analysis.

#### Normalization Mapping

```yaml
stride_per_element:
  External Entity:
    applicable_categories: [S, R]
    description: >
      External entities can be spoofed (S) and may deny actions (R).
      They do not process, store, or transport data directly.

  Process:
    applicable_categories: [S, T, R, I, D, E]
    description: >
      Processes are subject to all six STRIDE categories.
      They are the most broadly threatened element type.

  Data Store:
    applicable_categories: [T, I, D]
    description: >
      Data stores can be tampered with (T), leak information (I),
      or be rendered unavailable (D).

  Data Flow:
    applicable_categories: [T, I, D]
    description: >
      Data flows can be tampered with in transit (T), leak
      information (I), or be disrupted (D).
```

#### Quick Reference

| DFD Element Type | S | T | R | I | D | E |
|------------------|---|---|---|---|---|---|
| External Entity  | x |   | x |   |   |   |
| Process          | x | x | x | x | x | x |
| Data Store       |   | x |   | x | x |   |
| Data Flow        |   | x |   | x | x |   |

**Category legend**: S = Spoofing, T = Tampering, R = Repudiation, I = Information Disclosure, D = Denial of Service, E = Elevation of Privilege

For each component in the Phase 1 inventory, look up its DFD element type in the table above. The marked categories (x) are the STRIDE agents to dispatch for that component. Every DFD element type maps to at least 2 STRIDE categories, so the normalization step never produces zero applicable categories for a valid component.

---

### AI Keyword Dispatch Rules

In addition to STRIDE dispatch, components are evaluated for AI-specific threat analysis. AI dispatch is **additive** to STRIDE dispatch -- it never replaces STRIDE categories. A component always receives its STRIDE agents first, and AI agents are added on top when keywords match.

#### Keyword-to-Category Mapping

**LLM keywords** -- when any of the following keywords are found in a component's name or description, dispatch the LLM threat agents:

- `"LLM"`
- `"model"`
- `"GPT"`
- `"Claude"`

LLM dispatch triggers these agents:
- `prompt-injection` (OWASP LLM01:2025)
- `data-poisoning` (OWASP LLM03:2025)
- `model-theft` (OWASP LLM10:2025)

**AG keywords** -- when any of the following keywords are found in a component's name or description, dispatch the AG (Agentic) threat agents:

- `"agent"`
- `"autonomous"`
- `"orchestrator"`
- `"MCP server"`
- `"tool server"`
- `"plugin"`

AG dispatch triggers these agents:
- `agent-autonomy` (ASI-01)
- `tool-abuse` (MCP-03)

#### Matching Rules

1. **Case-insensitive**: All keyword matching is case-insensitive. "llm", "LLM", "Llm" all match.
2. **Scope**: Keywords are matched against both the component **name** and the component **description** from the Phase 1 inventory.
3. **Multi-word keywords**: Keywords containing spaces (e.g., "MCP server", "tool server") match as a complete phrase. The words must appear adjacent and in order.
4. **Substring matching**: A keyword match anywhere within the name or description triggers dispatch. For example, "ModelValidator" contains "model" and triggers LLM dispatch.

#### Dual-Dispatch

When a component matches keywords from **both** the LLM and AG categories, both agent categories are dispatched. This is called dual-dispatch.

**Example**: A component named "LLM Agent Orchestrator" matches:
- `"LLM"` --> LLM agents dispatched (prompt-injection, data-poisoning, model-theft)
- `"agent"` --> AG agents dispatched (agent-autonomy, tool-abuse)
- `"orchestrator"` --> AG agents dispatched (already included from "agent" match -- no duplicate dispatch)

The component receives its STRIDE categories (based on DFD type) plus all 5 AI agents.

#### Ambiguity Note

The keyword `"model"` is ambiguous -- it could refer to a data model, a domain model, or an LLM. When `"model"` is matched, dispatch the LLM agents and include a note in the dispatch table: `"Keyword 'model' matched -- may refer to data model rather than LLM. AI agents dispatched for coverage; review findings for relevance."` This ensures no AI-relevant component is missed while flagging potential false positives.

#### Agent-to-Table Mapping

AI findings produced by the dispatched agents are grouped into 2 output tables:

| Output Table | Agents | Reference Standards |
|--------------|--------|---------------------|
| AG (Agentic Threats) | agent-autonomy, tool-abuse | OWASP Agentic Top 10, MCP Top 10 |
| LLM (LLM Threats) | prompt-injection, data-poisoning, model-theft | OWASP LLM Top 10 v2025 |

---

### Agent Invocation Protocol

Each threat agent is a prompt file located in the sibling agent files (STRIDE agents like `spoofing.agent.md`, `tampering.agent.md`, etc. and AI agents like `prompt-injection.agent.md`, `data-poisoning.agent.md`, etc.). The agent prompt files define what each agent does -- the analysis methodology, threat patterns, and output format. The orchestrator defines what context each agent receives and which component(s) to analyze.

#### Context Payload

Every dispatched agent receives a context payload containing three elements:

**1. Target Component(s)**

The specific component(s) this agent must analyze. Each target component is identified by:
- **Name**: The component name as it appears in the Phase 1 inventory.
- **DFD Type**: The classified DFD element type (External Entity, Process, Data Store, or Data Flow).

When an agent is dispatched for multiple components (e.g., the Spoofing agent analyzing two External Entities and three Processes), all target components are listed together. The agent analyzes each target component and produces findings for each.

**2. Full Architecture Context**

The complete parsed architecture from Phase 1, including:
- **All components**: The full component inventory (name, DFD type, description) -- not just the target component(s).
- **All data flows**: The complete data flows table (source, destination, data, protocol).
- **All trust boundaries**: The trust zones and boundary crossings tables.

The full architecture context enables cross-component threat analysis. For example, a Tampering agent analyzing a Data Store needs to understand which Processes write to it and what trust boundaries those writes cross. Providing only the isolated target component would prevent this analysis.

**3. Analysis Scope**

The threat category this agent covers:
- For STRIDE agents: one of S, T, R, I, D, or E.
- For AI agents: one of prompt-injection, data-poisoning, model-theft, agent-autonomy, or tool-abuse.

The analysis scope tells the agent which type of threats to identify. The agent prompt file contains the methodology for that specific threat category; the analysis scope confirms which category is active for this invocation.

#### Payload Assembly

When invoking an agent, structure the context as follows:

1. State the analysis scope (which threat category).
2. List the target component(s) with their names and DFD types.
3. Provide the full architecture context: all components, data flows, and trust boundaries from Phase 1.
4. Reference the agent's prompt file for its analysis methodology.

The payload is structured as prompt content passed to the agent. Since agents are prompt files consumed by an LLM, the context is provided as structured text within the invocation -- not as a serialized data format.

---

### Dispatch Protocol

The orchestrator supports two dispatch modes. Both modes produce identical output -- the dispatch mode affects execution order only, not results.

#### Parallel Mode (Concurrent Agent Framework)

When the execution platform supports concurrent agent invocation:

1. Determine all dispatch targets for all components (STRIDE + AI).
2. Produce the dispatch table intermediate artifact (see below).
3. Invoke **all** applicable agents concurrently. Each agent receives its context payload independently.
4. Collect results from **all** agents before proceeding to Phase 3.
5. No specific invocation order is required -- agents operate independently.

Parallel mode is preferred when the platform supports it, as all agents analyze the same architecture snapshot and produce independent findings.

#### Sequential Mode (Single-Prompt / Manual Execution)

When the execution platform does not support concurrent agents, or when executing manually:

1. Determine all dispatch targets for all components (STRIDE + AI).
2. Produce the dispatch table intermediate artifact (see below).
3. Invoke agents one at a time in the following category order:
   1. **S** -- Spoofing
   2. **T** -- Tampering
   3. **R** -- Repudiation
   4. **I** -- Information Disclosure
   5. **D** -- Denial of Service
   6. **E** -- Elevation of Privilege
   7. **AG** -- Agentic threats (agent-autonomy, then tool-abuse)
   8. **LLM** -- LLM threats (prompt-injection, then data-poisoning, then model-theft)
4. Collect findings from each agent before invoking the next.
5. After all agents have been invoked, proceed to Phase 3.

Sequential mode produces the same findings as parallel mode -- the output is structurally identical regardless of dispatch order.

Platform-specific dispatch adapters that bind these protocols to concrete invocation mechanisms are out of scope for this orchestrator (see F-009). The orchestrator documents the protocol; platform adapters implement the bindings.

---

### Dispatch Table (Intermediate Output)

Before invoking any agents, produce a visible dispatch table as an intermediate artifact. This table shows every component, its STRIDE categories, its AI categories (if any), and the total number of agents that will be dispatched. The dispatch table enables validation that the normalization and keyword matching rules were applied correctly before agent execution begins.

Label this section clearly:

```
### Dispatch Table (Intermediate)
```

#### Table Format

| Component | DFD Type | STRIDE Categories | AI Categories | Total Agents |
|-----------|----------|-------------------|---------------|--------------|

- **Component**: The component name from the Phase 1 inventory.
- **DFD Type**: The DFD element type (External Entity, Process, Data Store, or Data Flow).
- **STRIDE Categories**: Comma-separated list of applicable STRIDE categories based on DFD type (e.g., "S, R" for External Entity).
- **AI Categories**: Comma-separated list of applicable AI categories based on keyword matching (e.g., "LLM, AG" for dual-dispatch). Use "---" if no AI keywords matched.
- **Total Agents**: The total count of individual agents to be dispatched for this component. Count each STRIDE category as 1 agent and each AI agent individually (AG = 2 agents: agent-autonomy + tool-abuse; LLM = 3 agents: prompt-injection + data-poisoning + model-theft).

#### Example Rows

| Component | DFD Type | STRIDE Categories | AI Categories | Total Agents |
|-----------|----------|-------------------|---------------|--------------|
| LLM Agent Orchestrator | Process | S, T, R, I, D, E | LLM, AG | 11 |
| MCP Tool Server | Process | S, T, R, I, D, E | AG | 8 |
| User | External Entity | S, R | --- | 2 |
| Knowledge Base | Data Store | T, I, D | --- | 3 |
| External API | External Entity | S, R | --- | 2 |

In this example:
- "LLM Agent Orchestrator" is a Process (6 STRIDE agents) with dual-dispatch (3 LLM + 2 AG agents) = 11 total.
- "MCP Tool Server" is a Process (6 STRIDE agents) with AG dispatch (2 AG agents) = 8 total.
- "User" is an External Entity (2 STRIDE agents) with no AI match = 2 total.

#### Summary

After the dispatch table, include a summary with:

1. **Total unique agent invocations**: The sum of all Total Agents values across all components. Note that the same agent type may be invoked for multiple components -- each component-agent pair counts as one invocation.
2. **Components with AI dispatch**: The count of components that have at least one AI category (LLM and/or AG).
3. **Components with dual-dispatch**: The count of components dispatched to both LLM and AG categories.

#### Self-Check

After producing the dispatch table, verify:

- Every component from the Phase 1 inventory appears in the dispatch table.
- Every component has at least 2 STRIDE categories (the minimum for any DFD element type -- External Entity and Data Flow/Data Store each have at least 2-3 applicable categories).
- AI categories are present only for components whose names or descriptions matched the keyword rules.
- Total Agents count is arithmetically correct for each row.

If any self-check fails, correct the dispatch table before invoking agents. Do not proceed to agent invocation with an invalid dispatch table.

After the dispatch table is validated, invoke agents according to the selected dispatch mode (parallel or sequential) and proceed to Phase 3: Determine Countermeasures.

---

## Phase 3: Determine Countermeasures -- "What are we going to do about it?"

This phase answers the third OWASP threat modeling question: **What are we going to do about it?**

Phase 3 REQUIRES the dispatch results from Phase 2 as input. Every dispatched agent returns findings conforming to the finding schema (`../../schemas/finding.yaml`). This phase collects those findings, validates their risk levels against the OWASP 3x3 matrix, and assembles them into the structured tables defined in the Output Format Specification above.

Phase objectives:

1. Collect findings from all dispatched agents (STRIDE and AI).
2. Validate the `risk_level` of every finding against the OWASP 3x3 matrix, correcting any mismatches.
3. Assemble findings into the 6 STRIDE tables (Section 3 of the output).
4. Assemble findings into the 2 AI threat tables (Section 4 of the output).

Do not proceed to Phase 4 until all agent findings have been collected and all tables have been assembled.

---

### Risk Level Validation

Every finding returned by an agent includes `likelihood`, `impact`, and `risk_level` fields. The `risk_level` must be the deterministic result of the OWASP 3x3 matrix applied to the `likelihood` and `impact` values. Validate every finding before including it in the output tables.

#### OWASP 3x3 Risk Matrix

Use this matrix to compute the correct `risk_level` from `likelihood` and `impact`:

|                  | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|------------------|----------------|-------------------|-----------------|
| **HIGH Impact**  | Medium         | High              | Critical        |
| **MEDIUM Impact**| Low            | Medium            | High            |
| **LOW Impact**   | Note           | Low               | Medium          |

#### Lookup Table

For direct lookup, the 9 valid combinations are:

| Impact | Likelihood | Risk Level |
|--------|------------|------------|
| HIGH   | HIGH       | Critical   |
| HIGH   | MEDIUM     | High       |
| HIGH   | LOW        | Medium     |
| MEDIUM | HIGH       | High       |
| MEDIUM | MEDIUM     | Medium     |
| MEDIUM | LOW        | Low        |
| LOW    | HIGH       | Medium     |
| LOW    | MEDIUM     | Low        |
| LOW    | LOW        | Note       |

#### Correction Protocol

For each finding returned by an agent:

1. Read the `likelihood` and `impact` values from the finding.
2. Look up the correct `risk_level` in the matrix above.
3. Compare the agent-returned `risk_level` with the matrix-computed value.
4. **If they match**: Accept the finding as-is. No annotation needed.
5. **If they do not match**: Override the agent-returned `risk_level` with the matrix-computed value. Append a correction note to the finding's Mitigation field: `"[Risk level corrected from {agent_value} to {computed_value} per OWASP 3x3 matrix]"`.

This correction ensures every finding in the output has a risk level that is arithmetically consistent with its likelihood and impact values, regardless of agent output quality.

---

### STRIDE Table Assembly

Assemble 6 STRIDE tables for Section 3 of the output, one table per STRIDE category. Each table collects findings from the corresponding STRIDE agent across all dispatched components.

The 6 tables are assembled in this order:

1. **Spoofing (S)**
2. **Tampering (T)**
3. **Repudiation (R)**
4. **Information Disclosure (I)**
5. **Denial of Service (D)**
6. **Elevation of Privilege (E)**

#### Finding Row Format

Every finding row in a STRIDE table uses the fields defined in Section 3 of the Output Format Specification above:

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|

#### Assembly Instructions

For each STRIDE category (S, T, R, I, D, E):

1. Collect all findings returned by the corresponding STRIDE agent across all components that were dispatched to that category.
2. Validate the `risk_level` of each finding using the correction protocol defined above.
3. Assign sequential IDs within each category using the pattern `{PREFIX}-{N}`, where `{PREFIX}` is the single-letter category identifier (S, T, R, I, D, or E) and `{N}` is a sequential integer starting at 1. Number findings in the order they are collected -- the specific ordering of findings within a category is determined by the order of components in the Phase 1 inventory, then by the order of findings returned by the agent for each component.
4. Populate each row with the validated fields: ID, Component, Threat, Likelihood, Impact, Risk Level, Mitigation.

#### Empty Categories

If a STRIDE category has no findings -- either because no components were dispatched to that category, or because the agent returned zero findings for all dispatched components -- include the table header row with no data rows. Do not omit the table. This maintains the consistent 6-table structure regardless of input.

---

### AI Threat Table Assembly

Assemble 2 AI threat tables for Section 4 of the output. The 5 AI agents map to 2 output tables as defined in the Output Format Specification above.

#### 5-Agent-to-2-Table Mapping

| Output Table | ID Prefix | Source Agents |
|--------------|-----------|---------------|
| Agentic Threats (AG) | AG | agent-autonomy, tool-abuse |
| LLM Threats (LLM) | LLM | prompt-injection, data-poisoning, model-theft |

Findings from `agent-autonomy` and `tool-abuse` are grouped into the **AG** table. Findings from `prompt-injection`, `data-poisoning`, and `model-theft` are grouped into the **LLM** table.

#### Finding Row Format

Every finding row in an AI threat table uses the fields defined in Section 4 of the Output Format Specification above. AI table rows include an additional OWASP Reference field compared to STRIDE tables:

| ID | Component | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------------|------------|--------|------------|------------|

The OWASP Reference field contains the applicable OWASP identifier from the agent's findings (e.g., `ASI-01`, `MCP-03`, `OWASP LLM01:2025`).

#### Assembly Instructions

For each AI output table (AG, LLM):

1. Collect all findings from the source agents listed in the mapping table above, across all components that were dispatched to those agents.
2. Validate the `risk_level` of each finding using the correction protocol defined in Risk Level Validation above.
3. Assign sequential IDs within each table using the pattern `{PREFIX}-{N}`, where `{PREFIX}` is `AG` or `LLM` and `{N}` is a sequential integer starting at 1. Within each table, number findings in the order they are collected -- agent-autonomy findings before tool-abuse findings in the AG table; prompt-injection findings before data-poisoning findings before model-theft findings in the LLM table. Within each agent's findings, order by component appearance in the Phase 1 inventory.
4. Populate each row with the validated fields: ID, Component, Threat, OWASP Reference, Likelihood, Impact, Risk Level, Mitigation.

#### No AI Dispatch

If no AI agents were dispatched during Phase 2 (because no components matched AI keywords), include both AI table headers with a note: "No AI-related components were identified in the architecture input." Do not omit the tables.

---

### Correlation Detection

Correlation detection runs after all findings have been collected and assembled into the STRIDE tables (Section 3) and AI tables (Section 4), but before Phase 4. Its purpose is to identify cross-category finding pairs that indicate a related underlying threat when they target the same component.

The 5 correlation rules below define which STRIDE-to-AI category pairings constitute a correlated threat. Matching is deterministic and rule-based -- no semantic similarity or probabilistic scoring is involved. Each rule identifies a shared threat basis between one STRIDE category and one AI category.

---

#### Correlation Rule Table

| Rule | STRIDE Category | AI Category | Correlation Basis |
|------|----------------|-------------|-------------------|
| CR-1 | Tampering (T) | Data-Poisoning (LLM) | Data integrity |
| CR-2 | Privilege-Escalation (E) | Agent-Autonomy (AG) | Excessive permissions |
| CR-3 | Info-Disclosure (I) | Prompt-Injection (LLM) | Information leakage |
| CR-4 | Repudiation (R) | Agent-Autonomy (AG) | Accountability gaps |
| CR-5 | Denial-of-Service (D) | Tool-Abuse (AG) | Resource exhaustion |

---

#### Correlation Detection Algorithm

Execute the following steps to identify correlated findings:

1. Group all findings from the STRIDE tables (Section 3) and AI tables (Section 4) by their target component name. Each group contains every finding -- regardless of category -- that targets a single component.
2. Within each component group, identify all cross-category finding pairs. A cross-category pair consists of one finding from a STRIDE category and one finding from an AI category. Do not pair findings within the same domain (STRIDE-to-STRIDE or AI-to-AI).
3. For each cross-category pair, check whether the STRIDE category and AI category match any of the 5 rules in the Correlation Rule Table. Matching is by category only -- the threat descriptions do not need to be semantically similar.
4. When a match is found, create a correlation group (CG-N). If the same component already has a correlation group from a different rule match, merge all matched findings into that existing group. The result is one correlation group per component, regardless of how many rules triggered.
5. Each finding may belong to at most one correlation group. If a finding matches multiple rules through the same component, it joins the single merged group for that component.
6. Findings that do not match any rule remain uncorrelated and are unaffected. They stay in their original STRIDE or AI tables with no modification.

---

#### Correlation Group Assembly

After running the detection algorithm, assemble the resulting correlation groups:

1. Assign sequential IDs: CG-1, CG-2, CG-3, etc., numbered in the order the correlated components appear in the Phase 1 inventory. If the first component in the inventory with a correlation is "LLM Agent Orchestrator" and the second is "MCP Tool Server", their groups are CG-1 and CG-2 respectively.
2. For each group, set the risk level to the highest risk level among its member findings. Use the severity order: Critical > High > Medium > Low > Note. If a group contains one "High" finding and one "Medium" finding, the group risk level is "High".
3. For each group, build the threat summary by listing each member finding's perspective, prefixed by its category name. Format: "{Category}: {threat description}; {Category}: {threat description}". List STRIDE findings before AI findings. Within each domain, list findings in the order of their IDs.
4. Store the assembled correlation groups. They will be consumed by:
   - Section 4a (Correlated Findings table) -- written immediately after this phase.
   - Phase 4 Coverage Matrix generation -- for deduplicated cell counts.
   - Phase 4 Risk Summary computation -- for deduplicated totals.

---

#### Correlation Self-Check

Before proceeding, verify the assembled correlation groups:

1. Verify that no finding ID appears in more than one correlation group.
2. Verify that every finding ID referenced in a correlation group exists in either the STRIDE tables (Section 3) or the AI tables (Section 4).
3. Verify that each correlation group contains findings from at least 2 different agent categories (at minimum one STRIDE and one AI category).
4. Verify that the group risk level matches the highest risk level among its member findings using the severity order: Critical > High > Medium > Low > Note.
5. If any check fails, correct the correlation groups before proceeding.

After the self-check passes, assemble Section 4a of the output using the correlation groups. Section 4a uses the following table format:

| Group | Findings | Component | Threat Summary | Risk Level |
|-------|----------|-----------|----------------|------------|

When zero correlation groups exist, output: "No cross-agent correlations detected." followed by the empty table header with no data rows. Do not omit Section 4a -- it is always present in the output.

After Section 4a is assembled, proceed to Phase 4: Assess.

---

## Phase 4: Assess -- "Did we do a good enough job?"

This phase answers the fourth OWASP threat modeling question: **Did we do a good enough job?**

Phase 4 evaluates the completeness and quality of the threat model assembled in Phase 3. It produces the remaining output sections: the coverage matrix (Section 5), the risk summary (Section 6), and the recommended actions list (Section 7).

Phase objectives:

1. Generate the coverage matrix showing which components were analyzed for which threat categories.
2. Compute the risk summary with counts and percentages per risk level.
3. Produce the recommended actions list sorted by risk severity.
4. Run the output structural validation checklist to verify the complete document.

---

### Coverage Matrix Generation

Produce the coverage matrix for Section 5 of the output. This matrix cross-references components (rows) against threat categories (columns) with finding counts per cell.

#### Matrix Structure

| Component | S | T | R | I | D | E | AG | LLM | Total |
|-----------|---|---|---|---|---|---|----|-----|-------|

- **Rows**: One row per component from the Phase 1 inventory, listed in the same order as the Phase 1 component inventory.
- **Columns**: 8 threat category columns (S, T, R, I, D, E, AG, LLM) plus a Total column.

#### Cell Values

Each cell in the matrix contains one of three values:

1. **Deduplicated finding count** (integer): The number of unique threats identified for that component-category pair. When computing the count, apply deduplication: if any findings in the cell belong to a correlation group (from the Correlation Detection phase), those findings contribute 1 to the cell count collectively rather than individually. Uncorrelated findings each contribute 1 as normal. For example, if a cell contains findings T-1, T-2, and T-3, and T-1 and T-2 belong to correlation group CG-1, the cell count is 2 (1 for the group + 1 for uncorrelated T-3).
2. **Em dash (`---`)**: The component was dispatched to that category (it was applicable per STRIDE-per-Element rules or AI keyword matching), but the agent returned zero findings. This indicates "analyzed but clean" -- the analysis was performed and no threats were found.
3. **Not applicable (`n/a`)**: The category does not apply to this component. The component was not dispatched to that category because its DFD element type does not include that STRIDE category (per the STRIDE-per-Element normalization table), and no AI keywords matched for AI categories. This indicates the analysis was not applicable, distinguishing it from "analyzed but clean".

#### Total Column and Total Row

- **Total column**: For each component row, sum all deduplicated finding counts in that row. Cells with `---` or `n/a` contribute 0 to the sum.
- **Total row**: Include a final row labeled **Total** that sums each category column. The Total-Total cell (bottom-right) contains the grand total of all findings across all components and categories.

#### Footnote

After producing the coverage matrix table, check whether any correlation groups were created during the Correlation Detection phase:

- **If correlation groups exist** (count > 0): Append a footnote below the matrix table: `"Counts reflect deduplicated findings. N correlation groups merged M individual findings."` where N is the number of correlation groups and M is the total number of individual findings absorbed into those groups.
- **If no correlation groups exist**: Do not include a footnote. The matrix counts are already raw counts with no deduplication applied.

#### Self-Check

After producing the coverage matrix, verify:

- Every component from the Phase 1 inventory appears as a row.
- Cell values with finding counts reflect deduplicated counts: for each cell, count uncorrelated findings individually and count each correlation group's findings as 1, then verify the cell value matches this deduplicated total.
- Cells marked `---` (em dash) correspond to component-category pairs where the agent was dispatched but returned zero findings.
- Cells marked `n/a` correspond to component-category pairs where the component's DFD type excludes that STRIDE category and no AI keywords matched.
- The Total column for each row equals the sum of that row's deduplicated finding counts.
- The Total row for each column equals the sum of that column's deduplicated finding counts.

If any self-check fails, correct the matrix before proceeding.

---

### Risk Summary and Recommended Actions

Produce the risk summary (Section 6) and recommended actions list (Section 7) of the output.

#### Risk Calibration Matrix

Before the risk summary table, include the Risk Calibration Matrix subsection in every output. This subsection documents the OWASP 3x3 risk matrix used to compute risk levels for all findings in the threat model. It provides transparency for readers to verify any finding's risk rating.

Output the following subsection heading and table:

```markdown
### Risk Calibration Matrix

The following OWASP 3x3 risk matrix documents how risk levels are computed for every finding in this threat model. Impact (rows) and Likelihood (columns) determine the Risk Level at each intersection. All agents use this same matrix, ensuring consistent risk ratings across STRIDE and AI threat categories.

| | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|---|---|---|---|
| **HIGH Impact** | Medium | High | Critical |
| **MEDIUM Impact** | Low | Medium | High |
| **LOW Impact** | Note | Low | Medium |

Risk summary counts below reflect deduplicated findings. When correlation groups exist, correlated findings count as one unique threat per group rather than individually.
```

This subsection is always present in the output, regardless of whether correlation groups exist.

#### Risk Summary

Compute aggregate counts of all findings grouped by risk level. The risk levels are listed in descending severity order as defined in the Output Format Specification above:

| Risk Level | Count | Percentage |
|------------|-------|------------|
| Critical   | _{count}_ | _{percentage}%_ |
| High       | _{count}_ | _{percentage}%_ |
| Medium     | _{count}_ | _{percentage}%_ |
| Low        | _{count}_ | _{percentage}%_ |
| Note       | _{count}_ | _{percentage}%_ |
| **Total**  | _{total}_ | **100%** |

**Computation rules**:

1. Count the deduplicated total of findings across all 8 tables (6 STRIDE + 2 AI). When computing the deduplicated total: each uncorrelated finding counts as 1; each correlation group counts as 1 regardless of how many individual findings it contains. The deduplicated total = (total raw findings) - (findings in correlation groups) + (number of correlation groups).
2. For each risk level, count the deduplicated number of findings with that risk level. For correlated findings, use the correlation group's risk level (highest among members) rather than individual member risk levels. Each correlation group contributes 1 to its group risk level count.
3. When the deduplicated total differs from the raw total, display the count with a parenthetical raw count: e.g., `"12 (15 raw)"`. When they are equal (no correlations or no impact on totals), display the count alone without a parenthetical.
4. Compute the percentage for each risk level as `(deduplicated count / deduplicated total) * 100`, rounded to one decimal place.
5. The percentages must sum to 100% (rounding adjustments should be applied to the largest category to ensure the total is exactly 100%).
6. If the total number of findings is zero (all agents returned zero findings), display all counts as 0 and all percentages as 0.0%.

#### Recommended Actions

Produce a prioritized list of all findings sorted by risk level descending (Critical first, Note last). This provides a remediation roadmap as defined in Section 7 of the Output Format Specification above.

| Finding ID | Component | Threat | Risk Level | Mitigation |
|------------|-----------|--------|------------|------------|

**Sorting rules**:

1. **Primary sort**: Risk level descending -- Critical, High, Medium, Low, Note.
2. **Secondary sort**: Within the same risk level, list findings in the order they appear across the tables: STRIDE tables first (S, T, R, I, D, E in order), then AI tables (AG, LLM in order). This means an S-1 finding at High risk appears before a T-2 finding at High risk, which appears before an AG-1 finding at High risk.

Every finding from all 8 tables must appear exactly once in the recommended actions list. The total row count must equal the raw (not deduplicated) finding count, since each individual finding has its own specific mitigation regardless of correlation group membership.

---

### Output Structural Validation Checklist

Before finalizing the output document, run the following validation checklist against the assembled `threats.md`. Every check must pass. If any check fails, correct the issue before producing the final output.

#### Section Completeness

- [ ] Section 1 (System Overview) is present and contains the Components, Data Flows, and Technologies tables.
- [ ] Section 2 (Trust Boundaries) is present and contains the Trust Zones and Boundary Crossings tables (or the "no trust boundaries identified" note with empty table headers).
- [ ] Section 3 (STRIDE Tables) is present and contains exactly 6 tables (S, T, R, I, D, E), each with a table header row even if no data rows exist.
- [ ] Section 4 (AI Threat Tables) is present and contains exactly 2 tables (AG, LLM), each with a table header row even if no data rows exist.
- [ ] Section 4a (Correlated Findings) is present and contains the correlation group table with correct columns (Group, Findings, Component, Threat Summary, Risk Level), or the "No cross-agent correlations detected" text with empty table header when zero correlations exist.
- [ ] Section 5 (Coverage Matrix) is present and contains one row per component plus a Total row. All cells use the three-state model: integer (deduplicated count), `---` (analyzed but clean), or `n/a` (not applicable).
- [ ] Section 5 (Coverage Matrix) footnote is present when correlation groups exist, stating "Counts reflect deduplicated findings. N correlation groups merged M individual findings." Footnote is absent when zero correlation groups exist.
- [ ] Section 6 (Risk Summary) is present and contains the Risk Calibration Matrix subsection followed by one row per risk level (Critical, High, Medium, Low, Note) plus a Total row.
- [ ] Section 7 (Recommended Actions) is present and contains one row per finding.

#### Frontmatter Validation

- [ ] `schema_version` is `"1.1"`.
- [ ] `date` is a valid ISO 8601 date in `YYYY-MM-DD` format.
- [ ] `input_format` is one of: `ascii`, `free-text`, `mermaid`, `plantuml`, `c4`.
- [ ] `classification` is `"confidential"`.

#### Finding ID Validation

- [ ] Every finding ID in the STRIDE tables matches the pattern `{S|T|R|I|D|E}-{N}` where N is a positive integer.
- [ ] Every finding ID in the AI tables matches the pattern `{AG|LLM}-{N}` where N is a positive integer.
- [ ] IDs are sequentially numbered within each category starting at 1, with no gaps.
- [ ] No duplicate IDs exist within any table or across tables of the same category.

#### Field Completeness

- [ ] Every finding row in the STRIDE tables has all 7 required fields populated: ID, Component, Threat, Likelihood, Impact, Risk Level, Mitigation.
- [ ] Every finding row in the AI tables has all 8 required fields populated: ID, Component, Threat, OWASP Reference, Likelihood, Impact, Risk Level, Mitigation.
- [ ] No field contains an empty value or placeholder text.

#### Risk Level Consistency

- [ ] Every finding's `risk_level` matches the OWASP 3x3 matrix computation for its `likelihood` and `impact` values.
- [ ] `likelihood` values are one of: `LOW`, `MEDIUM`, `HIGH`.
- [ ] `impact` values are one of: `LOW`, `MEDIUM`, `HIGH`.
- [ ] `risk_level` values are one of: `Critical`, `High`, `Medium`, `Low`, `Note`.

#### Cross-Section Consistency

- [ ] Coverage matrix cell counts reflect deduplicated counts: uncorrelated findings count individually, correlation group members contribute 1 collectively per component-category pair.
- [ ] Coverage matrix Total column values equal the sum of deduplicated finding counts in each component's row (`---` and `n/a` cells contribute 0).
- [ ] Coverage matrix Total row values equal the sum of deduplicated finding counts in each category's column.
- [ ] All correlation group member IDs (CG-N entries in Section 4a) reference finding IDs that exist in the STRIDE tables (Section 3) or AI tables (Section 4).
- [ ] Risk summary counts reflect deduplicated totals: each correlation group counts as 1 at its group risk level. When the deduplicated total differs from the raw total, counts include the parenthetical raw count (e.g., "5 (7 raw)").
- [ ] Risk summary Total equals the deduplicated grand total of all findings.
- [ ] Risk summary percentages are computed from the deduplicated total as denominator and sum to exactly 100%.
- [ ] Recommended actions list contains every finding from all 8 tables exactly once (raw count, not deduplicated -- each individual finding has its own mitigation).
- [ ] Recommended actions list row count equals the raw finding total (not the deduplicated total).

#### SARIF Output (`threats.sarif`)

- [ ] A `threats.sarif` file is produced in the same output directory as `threats.md`.
- [ ] The SARIF file is valid JSON with `$schema`, `version: "2.1.0"`, and `runs[]` at the top level.
- [ ] `tool.driver.name` is `"Tachi"` and `rules[]` contains only categories that produced findings.
- [ ] The number of SARIF `results[]` matches the deduplicated finding count in `threats.md`.
- [ ] Every result has `ruleId`, `message.text`, `level`, `locations[]`, and `partialFingerprints`.
- [ ] Every `ruleId` has a corresponding entry in `tool.driver.rules[]`.

#### Phase 5 Outputs (when Phase 5 is enabled)

- [ ] `threat-report.md` exists in the output directory
- [ ] `threat-report.md` contains YAML frontmatter with `schema_version: "1.0"`, `date`, `source_file`, `finding_count`, `risk_distribution`, `attack_tree_count`
- [ ] `threat-report.md` contains all 7 required sections (## 1. Executive Summary through ## 7. Appendix: Finding Reference)
- [ ] `attack-trees/` directory exists in the output directory
- [ ] `attack-trees/` contains one file per Critical and High finding, named `{finding-id}-attack-tree.md`
- [ ] Finding count in `threat-report.md` frontmatter matches the finding count in `threats.md`
- [ ] Appendix: Finding Reference in `threat-report.md` contains every finding ID from `threats.md`

If all checks pass, the `threats.md` output document is structurally valid, the `threats.sarif` file is consistent with it, and (when Phase 5 is enabled) the `threat-report.md` and `attack-trees/` are complete. Produce the final outputs.

---

### SARIF Output Generation

After the `threats.md` output is structurally validated, produce a `threats.sarif` file in the same output directory. The SARIF file contains the same findings in SARIF 2.1.0 format for integration with GitHub Code Scanning, VS Code SARIF Viewer, Azure DevOps, and other SARIF-compatible security tools.

Phase 4 already has all finding data from Phase 3. The SARIF generation step transforms that data into a JSON file -- no additional analysis or agent invocation is needed. Follow the instructions below to produce the `threats.sarif` file.

#### Category to Rule ID Mapping Table

Map each finding's `category` value (from the finding IR) to a SARIF `reportingDescriptor` rule ID using this canonical mapping. The mapping resolves naming differences between the finding IR enum values and SARIF rule ID conventions.

| Finding IR `category` | Finding ID Prefix | SARIF Rule ID | Short Description |
|----------------------|-------------------|---------------|-------------------|
| `spoofing` | S | `tachi/stride/spoofing` | Identity spoofing threats |
| `tampering` | T | `tachi/stride/tampering` | Data tampering threats |
| `repudiation` | R | `tachi/stride/repudiation` | Repudiation threats |
| `info-disclosure` | I | `tachi/stride/information-disclosure` | Information disclosure threats |
| `denial-of-service` | D | `tachi/stride/denial-of-service` | Denial of service threats |
| `privilege-escalation` | E | `tachi/stride/elevation-of-privilege` | Privilege escalation threats |
| `agentic` | AG | `tachi/ai/agentic-threats` | AI agent autonomy and misuse threats |
| `llm` | LLM | `tachi/ai/llm-threats` | LLM-specific threats |

**Naming normalization note**: Two categories use different names in SARIF rule IDs than in the finding IR:
- `info-disclosure` -> `information-disclosure` (expanded form)
- `privilege-escalation` -> `elevation-of-privilege` (STRIDE canonical term)

Only include rules for categories that produced findings in the current run. If the architecture has no AI components and only STRIDE findings were generated, omit AI rules from `tool.driver.rules[]`.

#### Severity Mapping Table

Map each finding's `risk_level` to SARIF severity using this CVSS alignment table. The `security-severity` value MUST be a numeric string (e.g., `"8.0"`, not `8.0`) for GitHub Code Scanning compatibility.

| Tachi Risk Level | SARIF `level` | `security-severity` (numeric string) | GitHub Display |
|-----------------|---------------|--------------------------------------|----------------|
| Critical | `error` | `"9.0"` | Critical |
| High | `error` | `"8.0"` | High |
| Medium | `warning` | `"5.0"` | Medium |
| Low | `note` | `"2.0"` | Low |
| Note | `note` | `"0.1"` | Low (informational) |

**Note-level mapping**: The Note level maps to `note`/`"0.1"` (not `none`/`"0.0"`) to keep informational findings visible in GitHub Code Scanning within the Low severity band. A value of `"0.0"` would cause GitHub to hide the finding entirely.

#### SARIF Tool Metadata

Populate the `tool.driver` object at the top of the SARIF file with the following fields:

- `name`: `"Tachi"`
- `semanticVersion`: Use the `schema_version` value from `../../schemas/output.yaml` (currently `"1.1"`)
- `informationUri`: Use the repository URL (e.g., `"https://github.com/{owner}/{repo}"`)
- `rules`: An array of `reportingDescriptor` objects -- one per threat category that produced findings in the current run. See Rule Definition Templates below.

#### Rule Definition Templates

For each threat category that produced at least one finding, create a `reportingDescriptor` object in the `tool.driver.rules[]` array. Use the rule ID from the Category to Rule ID Mapping Table above.

Each `reportingDescriptor` MUST include these fields:

```json
{
  "id": "<rule-id-from-mapping-table>",
  "shortDescription": {
    "text": "<max 255 characters -- category short description from mapping table>"
  },
  "fullDescription": {
    "text": "<max 1024 characters -- expanded description of the threat category, what it covers, and why it matters>"
  },
  "help": {
    "text": "<plain text detection guidance -- what to review to detect threats in this category>",
    "markdown": "<markdown with detection guidance AND framework references from the finding IR `references` field -- include OWASP Top 10, CWE, and MITRE references where applicable>"
  },
  "properties": {
    "tags": ["security", "<category-family>", "<category-name>", "<additional-tags>"],
    "security-severity": "<numeric-string-from-severity-table>"
  }
}
```

**Tag constraints**: Maximum 20 tags per rule. Always include `"security"` as the first tag. Include the category family (`"stride"` or `"ai"`) and the specific category name. Add relevant framework identifiers (e.g., `"owasp"`, `"cwe"`, `"authentication"`) up to the 20-tag limit.

**`security-severity` on rules**: Set to the highest `security-severity` value among all findings in that category. For example, if a category has both High (`"8.0"`) and Medium (`"5.0"`) findings, set the rule's `security-severity` to `"8.0"`.

**Reference examples** for three categories:

**Spoofing** (`tachi/stride/spoofing`):
- `shortDescription.text`: `"Identity spoofing threats"`
- `help.markdown` references: OWASP A07 (Identification and Authentication Failures), CWE-287 (Improper Authentication)
- `tags`: `["security", "stride", "spoofing", "authentication"]`

**Information Disclosure** (`tachi/stride/information-disclosure`):
- `shortDescription.text`: `"Information disclosure threats"`
- `help.markdown` references: OWASP A01 (Broken Access Control), CWE-200 (Exposure of Sensitive Information)
- `tags`: `["security", "stride", "information-disclosure", "data-exposure"]`

**Agentic Threats** (`tachi/ai/agentic-threats`):
- `shortDescription.text`: `"AI agent autonomy and misuse threats"`
- `help.markdown` references: OWASP Agentic Security Initiative (ASI), MITRE ATLAS
- `tags`: `["security", "ai", "agentic", "autonomy", "tool-use"]`

#### Finding IR to SARIF Result Mapping

For each finding collected in Phase 3, create a SARIF `result` object using this step-by-step mapping. Process every finding -- zero findings may be lost in the translation from `threats.md` to `threats.sarif`.

**Step-by-step mapping for each finding**:

1. **`ruleId`**: Look up the finding's `category` in the Category to Rule ID Mapping Table. Set `ruleId` to the corresponding SARIF Rule ID.

2. **`message.text`**: Set to the finding's `threat` field value. Use probabilistic language ("may", "could") rather than certainty ("can", "will") since findings are generated by LLM analysis.

3. **`message.markdown`**: Set to the finding's `mitigation` field value. Format as markdown for rich display in SARIF viewers.

4. **`level`**: Look up the finding's `risk_level` in the Severity Mapping Table. Set `level` to the corresponding SARIF level (`error`, `warning`, or `note`).

5. **`locations[]`**: Create a single location entry with both physical and logical location (see Dual-Location structure below):
   - `physicalLocation.artifactLocation.uri`: Set to the input architecture file path
   - `physicalLocation.region.startLine`: Set to `1` (architecture-level analysis has no line-level granularity)
   - `logicalLocations[]`: Array with one entry:
     - `name`: The finding's `component` value
     - `fullyQualifiedName`: `"{trust_zone}/{component_name}"` -- cross-reference the component's trust zone from Phase 1 Trust Boundaries data (Section 2 Trust Zones table)
     - `kind`: Map the finding's `dfd_element_type` to lowercase-hyphenated values: `External Entity` -> `external-entity`, `Process` -> `process`, `Data Store` -> `data-store`, `Data Flow` -> `data-flow`

6. **`partialFingerprints`**: See Fingerprint Computation below:
   - `primaryLocationLineHash`: Deterministic hash of `ruleId` + `component_name`
   - `findingId/v1`: The finding's `id` value (e.g., `"S-1"`, `"AG-2"`)

**Complete field mapping reference**:

| Finding IR Field | SARIF Object Path | Notes |
|-----------------|-------------------|-------|
| `id` | `result.partialFingerprints["findingId/v1"]` | Preserved for cross-reference to threats.md |
| `category` | `result.ruleId` | Via Category to Rule ID Mapping Table |
| `component` | `result.locations[].logicalLocations[].name` | Component name |
| `component` + trust zone | `result.locations[].logicalLocations[].fullyQualifiedName` | `"{trust_zone}/{component_name}"` |
| `threat` | `result.message.text` | Threat description |
| `mitigation` | `result.message.markdown` | Mitigation as markdown |
| `risk_level` | `result.level` + rule `properties.security-severity` | Via Severity Mapping Table |
| `dfd_element_type` | `result.locations[].logicalLocations[].kind` | Custom kinds: `external-entity`, `process`, `data-store`, `data-flow` |
| `references` | Rule `help.markdown` + `properties.tags` | OWASP, CWE, MITRE framework identifiers |
| Input file | `result.locations[].physicalLocation.artifactLocation.uri` | Architecture input file path |
| (fixed) | `result.locations[].physicalLocation.region.startLine` | Always `1` |

#### Correlated Finding Mapping

For each correlation group produced in Section 4a (Correlated Findings), map the group to SARIF results using these rules. Correlation groups represent related findings across threat categories targeting the same component -- they must not produce duplicate top-level results.

**Step-by-step mapping for each correlation group**:

1. **Identify the primary finding**: The first finding listed in the correlation group is the primary. All other findings in the group are correlated peers.

2. **Create a full SARIF `result` for the primary finding only**: Map the primary finding using the complete Finding IR to SARIF Result Mapping above (ruleId, message, level, locations, partialFingerprints).

3. **Add correlated peers to `relatedLocations[]`**: For each correlated peer in the group, add an entry to the primary result's `relatedLocations[]` array:
   - `id`: Integer index starting at `0`, incrementing for each peer
   - `message.text`: `"{peer_finding_id}: {peer_threat_summary}"` -- the peer's finding ID and a brief summary of its threat
   - `logicalLocations[]`: Array with one entry:
     - `name`: The peer's component name from finding IR
     - `fullyQualifiedName`: `"{trust_zone}/{peer_component_name}"` -- cross-reference the peer component's trust zone from Phase 1 Trust Boundaries data
     - `kind`: The peer's DFD element type mapped to lowercase-hyphenated values (same mapping as step 5 in Finding IR to SARIF Result Mapping)

4. **Store the correlation group ID**: Set `partialFingerprints["correlationGroup"]` to the group identifier (e.g., `"CG-1"`).

5. **Do NOT create separate top-level results for correlated peers**: Peers are already represented via the primary result's `relatedLocations[]`. Creating separate results would produce duplicate alerts in GitHub Code Scanning.

6. **Zero-correlation case**: If a finding is not part of any correlation group (has no correlations), skip `relatedLocations` entirely -- do not include an empty array. Do NOT include a `correlationGroup` key in `partialFingerprints` for uncorrelated findings.

**Example -- correlated result with relatedLocations**:

```json
{
  "ruleId": "tachi/stride/spoofing",
  "message": {
    "text": "API Gateway may be vulnerable to token replay attacks due to missing token binding validation.",
    "markdown": "Implement token binding (DPoP or certificate-bound tokens) to prevent replay of stolen access tokens."
  },
  "level": "error",
  "locations": [
    {
      "physicalLocation": {
        "artifactLocation": { "uri": "architecture/input.md" },
        "region": { "startLine": 1 }
      },
      "logicalLocations": [
        {
          "name": "API Gateway",
          "fullyQualifiedName": "DMZ/API Gateway",
          "kind": "process"
        }
      ]
    }
  ],
  "relatedLocations": [
    {
      "id": 0,
      "message": {
        "text": "T-3: API Gateway session data may be tampered with in transit"
      },
      "logicalLocations": [
        {
          "name": "API Gateway",
          "fullyQualifiedName": "DMZ/API Gateway",
          "kind": "process"
        }
      ]
    },
    {
      "id": 1,
      "message": {
        "text": "I-2: API Gateway may leak authentication tokens in error responses"
      },
      "logicalLocations": [
        {
          "name": "API Gateway",
          "fullyQualifiedName": "DMZ/API Gateway",
          "kind": "process"
        }
      ]
    }
  ],
  "partialFingerprints": {
    "primaryLocationLineHash": "a1b2c3d4e5f67890",
    "findingId/v1": "S-1",
    "correlationGroup": "CG-1"
  }
}
```

#### Dual-Location Instructions

Every SARIF result MUST include both a `physicalLocation` and a `logicalLocations[]` array in its `locations[]` entry. This dual-location strategy satisfies different SARIF consumers: GitHub Code Scanning requires `physicalLocation` for display, while VS Code SARIF Viewer and Azure DevOps benefit from `logicalLocations` for semantic component navigation.

**1. `physicalLocation`** -- required by GitHub Code Scanning:

- `artifactLocation.uri`: Set to the input architecture file path (the file the user provided to tachi)
- `region.startLine`: Set to `1` -- architecture-level threat analysis operates on the full document, not individual lines. Line `1` is a convention to satisfy SARIF viewers that require a region.

**2. `logicalLocations[]`** -- one entry per finding with component-level semantics:

- `name`: The component name from the finding IR `component` field (e.g., `"API Gateway"`, `"User Database"`)
- `fullyQualifiedName`: `"{trust_zone}/{component_name}"` -- the trust zone value MUST come from the Phase 1 Trust Zones/Trust Boundaries extraction (Section 2 Trust Zones table), not from the finding itself. Cross-reference the finding's `component` value against the Phase 1 trust zone assignments to resolve the correct zone. For example, if Phase 1 assigned `"API Gateway"` to the `"DMZ"` trust zone, then `fullyQualifiedName` is `"DMZ/API Gateway"`.
- `kind`: Map the finding's `dfd_element_type` to lowercase-hyphenated custom values:
  - `External Entity` -> `external-entity`
  - `Process` -> `process`
  - `Data Store` -> `data-store`
  - `Data Flow` -> `data-flow`

**Note**: `logicalLocations` is not displayed by GitHub Code Scanning but is rendered by VS Code SARIF Viewer (component tree navigation) and Azure DevOps (logical grouping in security reports). Include it on every result regardless of the target consumer.

**Example -- result with both physicalLocation and logicalLocations**:

```json
{
  "locations": [
    {
      "physicalLocation": {
        "artifactLocation": {
          "uri": "architecture/input.md"
        },
        "region": {
          "startLine": 1
        }
      },
      "logicalLocations": [
        {
          "name": "User Database",
          "fullyQualifiedName": "Internal/User Database",
          "kind": "data-store"
        }
      ]
    }
  ]
}
```

#### Fingerprint Computation

Every SARIF result MUST include a `partialFingerprints` object with deterministic values that enable GitHub Code Scanning to track findings across runs. **Same inputs MUST produce same outputs** -- given identical `ruleId` and `component_name` values, the fingerprint output must be identical across separate invocations.

**1. `primaryLocationLineHash`** -- the key GitHub uses for alert deduplication:

- Concatenate `ruleId` and `component_name` with a pipe separator: `"{ruleId}|{component_name}"`
  - Example: `"tachi/stride/spoofing|API Gateway"`
- Compute the SHA-256 hash of the concatenated string
- Truncate to the first **16 hex characters** of the hash digest
- This value MUST be deterministic and stable: produce a consistent hash value. Given the same `ruleId` and `component_name` inputs, the hash output must be identical across separate invocations. If two findings share the same category and component, they will share the same `primaryLocationLineHash` -- this is intentional for GitHub dedup behavior.

**2. `findingId/v1`** -- cross-reference to `threats.md`:

- Set to the finding IR `id` value (e.g., `"S-1"`, `"AG-2"`, `"T-4"`)
- This enables users to navigate from a SARIF alert back to the corresponding finding in the `threats.md` output

**3. `correlationGroup`** (conditional) -- only for correlated findings:

- Only present if the finding is the **primary member** of a correlation group (see Correlated Finding Mapping above)
- Set to the correlation group identifier (e.g., `"CG-1"`)
- Do NOT include this key for uncorrelated findings or for correlated peers (peers are not top-level results)

**Example -- partialFingerprints with all three keys (correlated primary finding)**:

```json
{
  "partialFingerprints": {
    "primaryLocationLineHash": "a1b2c3d4e5f67890",
    "findingId/v1": "S-1",
    "correlationGroup": "CG-1"
  }
}
```

**Example -- partialFingerprints for an uncorrelated finding (no correlationGroup)**:

```json
{
  "partialFingerprints": {
    "primaryLocationLineHash": "f0e9d8c7b6a54321",
    "findingId/v1": "AG-1"
  }
}
```

**Determinism note**: The `primaryLocationLineHash` is the primary mechanism GitHub Code Scanning uses to match alerts across runs. If the hash changes for the same finding, GitHub will close the old alert and open a new one, losing comment history and triage state. Treat hash stability as a correctness requirement.

#### SARIF Taxonomies (P1 Enhancement)

This section is **enabled by default** -- every generated `threats.sarif` file MUST include taxonomy declarations and rule-to-taxonomy relationships as described below.

Taxonomies enrich findings with references to industry-standard frameworks (OWASP Top 10 and CWE), enabling SARIF viewers to cross-reference threats against established vulnerability catalogs. While GitHub Code Scanning does not display taxonomy data, viewers such as Azure DevOps, VS Code SARIF Viewer, and SARIF Explorer surface taxonomy relationships in their UI.

**Step 1 -- Declare taxonomy frameworks in `run.taxonomies[]`**

Add a `taxonomies` array to the `runs[0]` object. Each entry is a `toolComponent` object representing an external taxonomy framework. Declare exactly two entries:

```json
{
  "taxonomies": [
    {
      "name": "OWASP",
      "version": "2021",
      "informationUri": "https://owasp.org/Top10/",
      "organization": "OWASP Foundation",
      "shortDescription": {
        "text": "OWASP Top 10 Web Application Security Risks"
      }
    },
    {
      "name": "CWE",
      "version": "4.13",
      "informationUri": "https://cwe.mitre.org/",
      "organization": "MITRE",
      "shortDescription": {
        "text": "Common Weakness Enumeration"
      }
    }
  ]
}
```

**Step 2 -- Register supported taxonomies in `tool.driver.supportedTaxonomies[]`**

Add a `supportedTaxonomies` array to the `tool.driver` object. Each entry references a declared taxonomy by name and index position in the `run.taxonomies[]` array:

```json
{
  "tool": {
    "driver": {
      "name": "Tachi",
      "supportedTaxonomies": [
        { "name": "OWASP", "index": 0 },
        { "name": "CWE", "index": 1 }
      ]
    }
  }
}
```

**Step 3 -- Add `relationships[]` to each rule (reportingDescriptor)**

For each `reportingDescriptor` in `tool.driver.rules[]`, add a `relationships` array that maps the rule to its corresponding OWASP and CWE taxonomy entries. Each relationship object contains:

- `target.id` -- the taxonomy entry identifier (e.g., `"A07"` for OWASP, `"CWE-287"` for CWE)
- `target.toolComponent.name` -- the taxonomy name (`"OWASP"` or `"CWE"`)
- `kinds` -- set to `["relevant"]` to indicate the relationship type

Use the following mapping table to determine the correct taxonomy entries for each STRIDE and AI threat category:

| Category               | OWASP Target ID | CWE Target ID | Notes                                                        |
|------------------------|-----------------|---------------|--------------------------------------------------------------|
| Spoofing               | A07             | CWE-287       | Identification and Authentication Failures / Improper Authentication |
| Tampering              | A08             | CWE-345       | Software and Data Integrity Failures / Insufficient Verification of Data Authenticity |
| Repudiation            | A09             | CWE-778       | Security Logging and Monitoring Failures / Insufficient Logging |
| Information Disclosure | A01             | CWE-200       | Broken Access Control / Exposure of Sensitive Information     |
| Denial of Service      | A05             | CWE-400       | Security Misconfiguration / Uncontrolled Resource Consumption |
| Elevation of Privilege | A01             | CWE-269       | Broken Access Control / Improper Privilege Management         |
| Agentic Threats        | ---             | CWE-693       | No direct OWASP Top 10 mapping; CWE-693 Protection Mechanism Failure |
| LLM Threats            | ---             | CWE-74        | No direct OWASP Top 10 mapping; CWE-74 Improper Neutralization of Special Elements in Output. Reference OWASP LLM Top 10 in the rule `help.markdown` field when applicable |

For categories with an OWASP mapping, include two relationship entries (one OWASP, one CWE). For categories without an OWASP mapping (Agentic Threats, LLM Threats), include only the CWE relationship entry.

**Example -- rule with both OWASP and CWE relationships (Spoofing)**:

```json
{
  "id": "tachi/stride/spoofing",
  "shortDescription": {
    "text": "Identity spoofing threats"
  },
  "relationships": [
    {
      "target": {
        "id": "A07",
        "toolComponent": { "name": "OWASP" }
      },
      "kinds": ["relevant"]
    },
    {
      "target": {
        "id": "CWE-287",
        "toolComponent": { "name": "CWE" }
      },
      "kinds": ["relevant"]
    }
  ]
}
```

**Example -- rule with CWE-only relationship (Agentic Threats)**:

```json
{
  "id": "tachi/ai/agentic-threats",
  "shortDescription": {
    "text": "AI agent autonomy and misuse threats"
  },
  "relationships": [
    {
      "target": {
        "id": "CWE-693",
        "toolComponent": { "name": "CWE" }
      },
      "kinds": ["relevant"]
    }
  ]
}
```

#### SARIF Schema Compliance Structure

The generated `threats.sarif` file MUST use this exact top-level JSON structure conforming to SARIF 2.1.0:

```json
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "Tachi",
          "semanticVersion": "<schema_version from output.yaml>",
          "informationUri": "<repository URL>",
          "rules": [
            // One reportingDescriptor per active threat category
          ]
        }
      },
      "results": [
        // One result per finding (after deduplication)
      ]
    }
  ]
}
```

**Structural requirements**:
- The file MUST contain exactly one `runs` entry (single run per invocation)
- `$schema` MUST use the exact OASIS URI shown above
- `version` MUST be `"2.1.0"`
- `results` array contains one entry per finding after deduplication -- correlated peers do NOT appear as separate top-level results
- Empty findings: If the threat model produces zero findings, `results` is an empty array `[]` and `rules` is an empty array `[]`

See `../../templates/threats.sarif` for a complete structural reference with example values.

#### JSON Structural Self-Check

Before writing the `threats.sarif` file, run the following validation checklist. If any check fails, correct the issue before producing the output.

- [ ] **Required properties**: The JSON contains `$schema`, `version`, `runs` at the top level, and `tool`, `results` within `runs[0]`.
- [ ] **Result completeness**: Every result has `ruleId`, `message.text`, `level`, `locations[]` (with both `physicalLocation` and `logicalLocations`), and `partialFingerprints`.
- [ ] **Rule-result consistency**: Every `ruleId` referenced by a result has a corresponding entry in `tool.driver.rules[]`. No orphan rule IDs.
- [ ] **Security-severity format**: Every `security-severity` value in `tool.driver.rules[].properties` is a numeric string (e.g., `"8.0"`) matching the Severity Mapping Table values.
- [ ] **Result count**: The number of top-level results equals the expected deduplicated finding count. If the STRIDE and AI tables contain N findings after deduplication, the `results` array MUST contain exactly N entries.

If any check fails, correct the error before proceeding. Do not produce a `threats.sarif` file that fails any of these structural checks.

After the self-check passes, write the `threats.sarif` file to the output directory alongside `threats.md`.

---

## Phase 5: Report -- "Communicate findings to stakeholders"

This phase transforms the structured threat model output from Phase 4 into a narrative threat report with Mermaid attack trees and a prioritized remediation roadmap. Phase 5 is optional (default-on) and runs after Phase 4 completes.

Phase objectives:

1. Invoke the report agent (`threat-report.agent.md`) with the completed `threats.md` as sole input.
2. Generate `threat-report.md` containing 7 required sections: Executive Summary, Architecture Overview, Threat Analysis, Cross-Cutting Themes, Attack Trees, Remediation Roadmap, and Appendix: Finding Reference.
3. Generate standalone Mermaid attack tree files in `attack-trees/` for every Critical and High finding.
4. Place all Phase 5 outputs in the same output directory as `threats.md` and `threats.sarif`.

---

### Phase 5 Dispatch

After Phase 4 completes and `threats.md` is written to the output directory:

1. **Check opt-out**: If the `--skip-report` flag is set or the `report` configuration is set to `false` (see Opt-Out Configuration below), skip Phase 5 entirely. The pipeline completes after Phase 4 with no change to existing behavior.

2. **Fresh-context invocation**: Invoke the report agent (`threat-report.agent.md`) in a fresh context. The invocation MUST:
   - Pass ONLY the `threats.md` file path as input
   - NOT pass accumulated pipeline state from Phases 1-4
   - NOT pass intermediate component inventories, agent dispatch logs, or correlation detection state
   - The report agent reads `threats.md` and operates independently using only what that file contains

3. **Context isolation boundary**: The following content boundary applies to Phase 5:
   ```
   <report-input>
   {path to threats.md}
   </report-input>
   ```
   The report agent treats `threats.md` as its complete input. It does not access or require any other pipeline artifacts. This prevents context window pressure from accumulated pipeline state and ensures the report agent operates on the validated, final output.

4. **Output placement**: The report agent writes its outputs to the same directory as `threats.md`:
   ```
   {output-directory}/
   ├── threats.md           (Phase 4 -- existing, unchanged)
   ├── threats.sarif         (Phase 4 -- existing, unchanged)
   ├── threat-report.md      (Phase 5 -- new)
   └── attack-trees/         (Phase 5 -- new)
       ├── {finding-id}-attack-tree.md
       └── ...
   ```

5. **Completion**: Phase 5 is complete when `threat-report.md` and the `attack-trees/` directory are written. The pipeline then proceeds to the validation checklist.

---

### Opt-Out Configuration

Phase 5 (Report) is default-on. It can be skipped using either mechanism:

1. **Flag**: `--skip-report` -- When the orchestrator is invoked with this flag, Phase 5 is skipped entirely. The pipeline completes after Phase 4 produces `threats.md` and `threats.sarif`.

2. **Configuration**: If the orchestrator's invocation context includes a configuration parameter `report: false`, Phase 5 is skipped.

When Phase 5 is skipped:
- The pipeline completes after Phase 4 as if Phase 5 does not exist
- No `threat-report.md` or `attack-trees/` files are generated
- `threats.md` and `threats.sarif` are unaffected
- The Output Structural Validation Checklist Phase 5 checks are skipped (they only apply when Phase 5 runs)

This preserves full backward compatibility with Phase 1-4 behavior.

---

## Error Handling

This section consolidates all error conditions and edge-case handling into a single reference. Phases 1 through 4 reference these error specifications at the points where they are triggered. The three error responses (UNSUPPORTED_FORMAT, NO_COMPONENTS, INVALID_FORMAT_VALUE) are terminal -- when triggered, stop processing and return the error response instead of a `threats.md` document. The two edge-case handlers (ambiguous classification, non-conforming findings) are non-terminal -- they allow processing to continue with appropriate annotations.

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

    See ../../docs/INTERFACE-CONTRACT.md Section 1 for complete format examples
    and ../../schemas/input.yaml for recognition pattern details.
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

    1. At least one identifiable component -- a service, database, user,
       agent, API, gateway, or any system element that can be classified
       as a DFD element type (External Entity, Process, Data Store, or
       Data Flow).
    2. At least one data flow or relationship -- a connection, API call,
       message, or data transfer between two components indicating how
       data moves through the system.

    Common causes of this error:
    - Input contains only a title or heading with no component descriptions.
    - Input describes a single component with no relationships to other
      components.
    - Input contains diagram syntax (e.g., Mermaid keywords) but no
      node or edge definitions.

    See ../../docs/INTERFACE-CONTRACT.md Section 1 for example inputs in each
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

    See ../../docs/INTERFACE-CONTRACT.md Section 1 for the format field
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

When a component cannot be confidently classified into one of the four DFD element types (External Entity, Process, Data Store, Data Flow), the orchestrator must handle the ambiguity predictably rather than blocking or guessing without disclosure. This is a non-terminal condition -- processing continues with the classification applied.

#### Default Classification Rule

Default to **Process** when classification is uncertain. Process is the broadest DFD element type, with all 6 STRIDE categories applicable (S, T, R, I, D, E). Defaulting to Process ensures the component receives the maximum threat coverage, preventing undertesting due to misclassification.

#### Human Review Flag

When defaulting to Process due to ambiguity, add the following annotation in the component's Description field in the System Overview (Section 1) Components table:

```
[Classification uncertain -- defaulted to Process for maximum threat coverage]
```

This annotation signals to human reviewers that the classification should be verified. The threat analysis results remain valid -- a component classified as Process may receive findings in categories that would not apply under a different classification (e.g., Spoofing or Elevation of Privilege findings for what might actually be a Data Store). Human reviewers can filter out inapplicable findings after verifying the correct classification.

#### AI Keyword Ambiguity

The keyword `"model"` is inherently ambiguous in architecture descriptions. It may refer to:

- A machine learning model or LLM (AI-relevant -- LLM agents should be dispatched)
- A data model, domain model, or object model (not AI-relevant -- LLM agents produce false-positive findings)

When the keyword `"model"` matches a component name or description:

1. **Dispatch LLM agents** -- err on the side of coverage. If the component is an LLM, omitting LLM agents would be a critical gap in the threat model.
2. **Add an ambiguity note** in the dispatch table's AI Categories column or as a footnote: `"Keyword 'model' matched -- may refer to data model rather than LLM. AI agents dispatched for coverage; review findings for relevance."`
3. **Do not suppress dispatch** based on ambiguity assessment. The cost of a false positive (extra findings that can be filtered) is lower than the cost of a false negative (missed LLM threats).

Other AI keywords (`"LLM"`, `"GPT"`, `"Claude"`, `"agent"`, `"autonomous"`, `"orchestrator"`, `"MCP server"`, `"tool server"`, `"plugin"`) are not ambiguous in typical architecture descriptions and do not require ambiguity annotations.

---

### Non-Conforming Finding Handling

Agent findings that do not conform to the schema defined in `../../schemas/finding.yaml` must be handled gracefully. The orchestrator must never silently drop non-conforming findings, as this would create invisible gaps in the threat model.

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
3. **Annotate the finding** by appending a warning to the Mitigation field: `"[WARNING: Finding did not fully conform to ../../schemas/finding.yaml -- {description of non-conformance}. Included for review.]"`. Replace `{description of non-conformance}` with a brief description of what was wrong (e.g., "missing likelihood field, defaulted to MEDIUM", "malformed ID, reassigned").
4. **Include in all downstream computations** -- the annotated finding is counted in the coverage matrix, risk summary, and recommended actions list like any other finding.

#### Rationale

Silent dropping creates invisible gaps: a component-category pair that was analyzed and produced findings would appear as `-` (zero findings) in the coverage matrix, indistinguishable from a genuinely clean analysis. By including non-conforming findings with annotations, the threat model remains complete and human reviewers can identify findings that need additional scrutiny.

---

### Coverage Matrix: Three-State Cell Model

The coverage matrix (Section 5) uses a three-state cell model to distinguish between findings present, analyzed but clean, and not applicable:

1. **Deduplicated finding count** (integer) -- The component was dispatched to the category and findings were identified. The count reflects deduplicated findings: correlation group members contribute 1 collectively, uncorrelated findings contribute 1 each.

2. **Analyzed, zero findings (`---`)** -- The component was dispatched to a category's agent, and the agent returned zero findings. The component was analyzed for that threat category, and no threats were identified. Display an em dash: `---`.

3. **Not applicable (`n/a`)** -- The component was not dispatched to that category because it was not applicable. For STRIDE categories, this means the component's DFD element type does not include that category (e.g., an External Entity was not dispatched to Tampering). For AI categories, this means the component's name and description did not match any AI keywords. Display: `n/a`.

This distinction is critical for threat model consumers:

- A `---` cell means "we looked and found nothing" -- the absence of findings is an affirmative result.
- A `n/a` cell means "we did not look" -- the absence of findings is expected because the analysis was not applicable.

When reviewing a threat model for completeness, `n/a` cells are expected and do not indicate gaps. Cells with `---` confirm that the analysis was performed. Cells with finding counts indicate identified threats. All three states must be visually distinguishable in the matrix.
