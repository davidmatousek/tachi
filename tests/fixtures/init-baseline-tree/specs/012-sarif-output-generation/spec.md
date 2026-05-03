---
prd_reference: docs/product/02_PRD/012-sarif-output-generation-2026-03-22.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-22
    status: APPROVED
    notes: "All 6 PRD FRs covered. All 3 PRD user stories addressed plus 2 new stories filling gaps. Both open questions resolved (taxonomies P1, component+category fingerprint key). Both Architect concerns resolved (Note severity fix, canonical category mapping). Team-Lead JSON fidelity concern resolved (FR-010 self-check). 8 measurable success criteria. No scope creep."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: SARIF Output Generation

**Feature Branch**: `012-sarif-output-generation`
**Created**: 2026-03-22
**Status**: Draft
**Input**: User description: "PRD: 012 - SARIF Output Generation"
**PRD Reference**: `docs/product/02_PRD/012-sarif-output-generation-2026-03-22.md`

## User Scenarios & Testing

### User Story 1 — Export Threat Findings as SARIF 2.1.0 (Priority: P0)

A DevOps engineer runs tachi against an architecture input and wants the threat findings in SARIF 2.1.0 format so they can upload them to GitHub Code Scanning alongside other SAST tool results.

**Why this priority**: Without SARIF output, tachi findings cannot enter automated security pipelines. This is the core value proposition — converting human-readable threat findings into machine-readable, standards-compliant format.

**Independent Test**: Run the orchestrator against `examples/mermaid-agentic-app/input.md` and verify a `threats.sarif` file is produced alongside `threats.md` that validates against the SARIF 2.1.0 JSON schema.

**Acceptance Scenarios**:

1. **Given** a completed threat model run with findings across STRIDE and AI categories, **When** the orchestrator finishes Phase 4 (Assess), **Then** a `threats.sarif` file is produced in the same output directory as `threats.md` following the `YYYY-MM-DD-{phase}/` naming convention.

2. **Given** any finding in `threats.md` (e.g., S-1, T-2, AG-1, LLM-3), **When** the SARIF file is examined, **Then** a corresponding SARIF `result` exists with `ruleId` matching the threat category, `message.text` containing the threat description, `message.markdown` containing the mitigation recommendation, and `level` mapped from the risk level.

3. **Given** findings with risk levels (Critical, High, Medium, Low, Note), **When** mapped to SARIF, **Then** severity levels follow the mapping: Critical→error/9.0, High→error/8.0, Medium→warning/5.0, Low→note/2.0, Note→note/0.1.

4. **Given** the generated `threats.sarif` file, **When** validated against the official SARIF 2.1.0 JSON schema, **Then** validation passes with zero errors.

5. **Given** the SARIF `tool.driver` object, **When** examined, **Then** it identifies "Tachi" with the schema version from `output.yaml`, an information URI, and the complete set of rule definitions for all threat categories used in the run.

6. **Given** each SARIF rule (reportingDescriptor), **When** examined, **Then** it contains `shortDescription.text`, `fullDescription.text`, `help.text`, `help.markdown` (with detection guidance and OWASP/CWE references), and `properties.tags` with relevant framework identifiers.

---

### User Story 2 — Correlated Findings in SARIF (Priority: P1)

A security-aware developer reviews Code Scanning alerts and wants correlated findings (from F-010 deduplication) grouped together so they can see how threats across categories relate to the same component.

**Why this priority**: Correlation is a distinguishing feature of tachi. Without SARIF representation, correlated findings lose their relationship context in the machine-readable output, reducing the value of cross-agent analysis.

**Independent Test**: Run the orchestrator against an input that produces correlated findings and verify the SARIF output links primary findings to their correlated peers via `relatedLocations`.

**Acceptance Scenarios**:

1. **Given** a correlation group (e.g., CG-1) containing a primary finding and correlated peers, **When** mapped to SARIF, **Then** only the primary finding appears as a top-level `result` with correlated peers listed in `relatedLocations[]` with their finding IDs and component names.

2. **Given** a correlated finding result, **When** its `partialFingerprints` is examined, **Then** it contains a `correlationGroup` key with the group identifier (e.g., "CG-1").

3. **Given** the SARIF results array, **When** deduplicated findings are counted, **Then** the count matches the deduplicated count in `threats.md` — correlated peers are not duplicated as top-level results.

---

### User Story 3 — Architecture Component Navigation in SARIF Viewers (Priority: P1)

A CI engineer views SARIF findings in GitHub Code Scanning or another SARIF viewer and wants results linked to architecture components so they can navigate findings by component and trust boundary.

**Why this priority**: Component-level navigation provides structural context that plain finding lists lack. This enhances the developer experience in code scanning UIs, but the core SARIF output (US-1) delivers value without it.

**Independent Test**: Generate SARIF from an input with multiple architecture components and verify each result includes both physical and logical location information.

**Acceptance Scenarios**:

1. **Given** a SARIF result for a finding targeting component "API Gateway" in trust zone "DMZ", **When** its `locations` array is examined, **Then** `physicalLocation.artifactLocation.uri` references the input architecture file and `region.startLine` is set to 1, and `logicalLocations[]` contains the component name in `name`, the trust zone path in `fullyQualifiedName` (e.g., "DMZ/API Gateway"), and the DFD element type in `kind`.

2. **Given** any SARIF result, **When** its physical location is examined, **Then** it always contains `artifactLocation.uri` and `region.startLine` — this is mandatory for GitHub Code Scanning display.

---

### User Story 4 — Stable Finding Tracking Across Runs (Priority: P1)

A DevOps engineer runs tachi multiple times against evolving architecture and wants GitHub Code Scanning to track findings as persistent alerts (not creating new duplicates each run) so the security dashboard reflects actual finding state.

**Why this priority**: Without stable fingerprints, every run creates new alerts and marks old ones as "fixed" — generating noise that undermines trust in the security dashboard.

**Independent Test**: Run the orchestrator twice against the same input and verify that `partialFingerprints` values are identical for the same category+component combinations.

**Acceptance Scenarios**:

1. **Given** two SARIF files generated from the same architecture input, **When** their `partialFingerprints` are compared for findings with the same rule ID and component, **Then** the `primaryLocationLineHash` values are identical.

2. **Given** a SARIF result, **When** its `partialFingerprints` is examined, **Then** it contains `primaryLocationLineHash` (deterministic hash of `ruleId` + `component_name` for GitHub dedup) and `findingId/v1` (the finding IR `id` for cross-reference to `threats.md`).

---

### Edge Cases

- **Zero findings**: If the threat model produces no findings, the SARIF file contains an empty `results` array and no rules in `tool.driver.rules[]`.
- **STRIDE-only input**: If the architecture has no AI components, only STRIDE rules appear in the SARIF output — AI rules are omitted from `tool.driver.rules[]`.
- **AI-only findings**: If an input triggers only AI category findings, STRIDE rules for unused categories are omitted.
- **Maximum findings**: For inputs producing more than 100 findings (unusual), the SARIF file remains valid and within GitHub's 25,000 result limit.
- **Missing references**: If a finding has no OWASP/CWE references in the IR, the corresponding rule's `help.markdown` omits the references section but remains structurally valid.
- **Single-component architecture**: If only one component exists, all results share the same logical location — the SARIF file remains valid.

## Requirements

### Functional Requirements

- **FR-001**: The orchestrator MUST produce a `threats.sarif` file alongside `threats.md` in the same output directory during Phase 4 (Assess), using the existing `YYYY-MM-DD-{phase}/` naming convention.

- **FR-002**: Every finding in `threats.md` MUST have a corresponding SARIF `result` — zero findings lost in translation. If the orchestrator produces N findings (after deduplication), the SARIF file MUST contain exactly N top-level results.

- **FR-003**: Each finding from the finding IR (`schemas/finding.yaml`) MUST be mapped to a SARIF `result` using the following field correspondence:

  | Finding IR Field | SARIF Object Path | Notes |
  |-----------------|-------------------|-------|
  | `id` | `result.partialFingerprints["findingId/v1"]` | Preserved for cross-reference to threats.md |
  | `category` | `result.ruleId` | Via canonical category→rule mapping (FR-004) |
  | `component` | `result.locations[].logicalLocations[].name` | Component name |
  | `component` + trust zone | `result.locations[].logicalLocations[].fullyQualifiedName` | "{trust_zone}/{component_name}" |
  | `threat` | `result.message.text` | Threat description |
  | `mitigation` | `result.message.markdown` | Mitigation as markdown supplement |
  | `risk_level` | `result.level` + rule `properties.security-severity` | Via severity mapping (FR-005) |
  | `dfd_element_type` | `result.locations[].logicalLocations[].kind` | Custom kinds: `external-entity`, `process`, `data-store`, `data-flow` |
  | `references` | Rule `help.markdown` + `properties.tags` | OWASP, CWE, MITRE framework identifiers |
  | Input file | `result.locations[].physicalLocation.artifactLocation.uri` | Architecture input file path |
  | (fixed) | `result.locations[].physicalLocation.region.startLine` | Set to 1 (architecture-level, no line mapping) |

- **FR-004**: Threat categories MUST be mapped to SARIF `reportingDescriptor` (rule) objects using this canonical mapping between finding IR category enum values and SARIF rule IDs:

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

  Each rule MUST include `shortDescription.text` (max 255 chars), `fullDescription.text` (max 1024 chars), `help.text`, and `help.markdown` (with detection guidance and framework references). Each rule MUST include `properties.tags` with relevant identifiers (e.g., `["security", "stride", "spoofing"]`). Maximum 20 tags per rule.

  Only rules for categories that produced findings in the current run are included in `tool.driver.rules[]`.

- **FR-005**: Risk levels MUST be mapped to SARIF severity using the CVSS alignment table:

  | Tachi Risk Level | SARIF `level` | `security-severity` (numeric string) | GitHub Display |
  |-----------------|---------------|--------------------------------------|----------------|
  | Critical | `error` | `"9.0"` | Critical |
  | High | `error` | `"8.0"` | High |
  | Medium | `warning` | `"5.0"` | Medium |
  | Low | `note` | `"2.0"` | Low |
  | Note | `note` | `"0.1"` | Low (informational) |

  Note: The Note level maps to `note`/`"0.1"` (not `none`/`"0.0"`) to keep informational findings visible in GitHub Code Scanning within the Low severity band. This resolves the Architect's concern about the PRD FR-3 / output.yaml inconsistency.

- **FR-006**: The SARIF `tool.driver` object MUST contain:
  - `name`: `"Tachi"`
  - `semanticVersion`: The `schema_version` value from `schemas/output.yaml` (e.g., `"1.1"`)
  - `informationUri`: The repository URL (e.g., `"https://github.com/{owner}/{repo}"`)
  - `rules`: Array of `reportingDescriptor` objects per FR-004

- **FR-007**: Correlated findings from F-010 (Deduplication & Risk Rating) MUST be represented as follows:
  - The primary finding in each correlation group appears as a full top-level SARIF `result`
  - Correlated peers are listed in the primary result's `relatedLocations[]` array with their finding IDs and component names
  - The correlation group identifier is stored in `partialFingerprints["correlationGroup"]` (e.g., `"CG-1"`)
  - Correlated peers do NOT appear as separate top-level results

- **FR-008**: Each SARIF result MUST include `partialFingerprints` with:
  - `primaryLocationLineHash`: A deterministic hash of `ruleId` + `component_name` (SHA-256, truncated to 16 hex characters). This provides stable identity for GitHub Code Scanning alert tracking across runs.
  - `findingId/v1`: The finding IR `id` value (e.g., `"S-1"`, `"AG-2"`) for cross-reference between SARIF results and `threats.md` findings.

- **FR-009**: The generated SARIF MUST conform to the SARIF 2.1.0 specification with the following top-level structure:

  ```json
  {
    "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
    "version": "2.1.0",
    "runs": [{
      "tool": { "driver": { /* FR-006 */ } },
      "results": [ /* FR-003 mapped findings */ ]
    }]
  }
  ```

- **FR-010**: The orchestrator prompt MUST include a JSON structural self-check before writing the SARIF output. The self-check validates:
  - All required SARIF properties are present (`$schema`, `version`, `runs`, `tool`, `results`)
  - Every result has `ruleId`, `message.text`, `level`, `locations[]` with both physical and logical locations, and `partialFingerprints`
  - Every referenced `ruleId` has a corresponding entry in `tool.driver.rules[]`
  - The `security-severity` value is a numeric string matching the severity mapping table
  - Result count matches expected finding count

- **FR-011**: Every SARIF result MUST include a dual-location strategy:
  - `physicalLocation`: `artifactLocation.uri` pointing to the input architecture file, `region.startLine` set to 1 (architecture-level analysis has no line-level granularity)
  - `logicalLocations[]`: Component `name`, trust zone `fullyQualifiedName`, and DFD element type `kind`

  This is mandatory (not contingent). GitHub Code Scanning requires `physicalLocation` for display; `logicalLocations` provide semantic navigation for other SARIF viewers.

### Should Have (P1)

- **FR-012**: The SARIF file SHOULD include a `taxonomies` array for OWASP and CWE frameworks with `tool.driver.supportedTaxonomies[]` references and `rule.relationships[]` mapping rules to taxonomy entries. This benefits SARIF viewers beyond GitHub (Azure DevOps, VS Code SARIF Viewer) but is not displayed by GitHub Code Scanning.

### Key Entities

- **SARIF Result**: A single threat finding mapped from the finding IR. Contains rule reference, message, severity level, locations, and fingerprints.
- **SARIF Rule (reportingDescriptor)**: A threat category definition with detection guidance, framework references, and severity metadata. One rule per active threat category per run.
- **SARIF Run**: A single execution of tachi against one architecture input. Contains the tool definition and all results.
- **Correlation Group**: A set of related findings across threat categories targeting the same component. Represented via `relatedLocations` and `partialFingerprints.correlationGroup`.
- **Partial Fingerprint**: A deterministic identifier enabling stable finding tracking across runs. Composed of rule ID and component name.

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% of generated SARIF files validate against the official SARIF 2.1.0 JSON schema with zero validation errors.

- **SC-002**: 100% of findings in `threats.md` have corresponding SARIF results — zero finding loss between markdown and SARIF output.

- **SC-003**: SARIF severity levels match `threats.md` risk levels with zero divergence — Critical→error/9.0, High→error/8.0, Medium→warning/5.0, Low→note/2.0, Note→note/0.1.

- **SC-004**: Generated SARIF is accepted by GitHub Code Scanning via `codeql/upload-sarif@v3` action with findings displayed as security alerts.

- **SC-005**: SARIF rule IDs are stable across runs for the same threat category — `tachi/stride/spoofing` always maps to the same rule regardless of run.

- **SC-006**: Running against `examples/mermaid-agentic-app/input.md` produces a valid SARIF file with findings across both STRIDE and AI categories.

- **SC-007**: Running against `examples/ascii-web-api/input.md` produces a valid SARIF file with STRIDE-only findings (no AI rules in `tool.driver.rules[]`).

- **SC-008**: `partialFingerprints.primaryLocationLineHash` values are identical across two runs against the same architecture input for the same category+component findings.

## Assumptions

- SARIF 2.1.0 is the target version (not 2.0 or draft 2.2).
- GitHub Code Scanning is the primary integration target, but the output is standard-compliant for any SARIF consumer.
- Architecture component names are sufficient as logical locations — no source code line mapping is attempted.
- The orchestrator already produces a complete finding IR before Phase 4 assembly.
- Typical threat models produce fewer than 100 findings, well within GitHub's 25,000 result limit.
- The `security-severity` property must be a numeric string (e.g., `"8.0"`) for GitHub Code Scanning compatibility.
- Threat description language in SARIF messages should use probabilistic framing ("may", "could") rather than certainty ("can", "will") since findings are generated by LLM analysis.

## Scope Boundaries

### In Scope
- Finding IR → SARIF result mapping for all 8 threat categories (P0)
- SARIF rule definitions with detection guidance and framework references (P0)
- Severity mapping via CVSS alignment table with Note-level fix (P0)
- Tool metadata with tachi identification (P0)
- Co-generation with threats.md in same output directory (P0)
- SARIF 2.1.0 schema compliance (P0)
- JSON structural self-check in orchestrator prompt (P0)
- Dual-location strategy (physical + logical) (P0)
- Correlated finding representation via relatedLocations (P1)
- Stable finding tracking via partialFingerprints (P1)
- SARIF taxonomies for OWASP/CWE frameworks (P1)

### Out of Scope
- SARIF viewer or dashboard (use GitHub Code Scanning or existing SARIF viewers)
- GitHub Action for automated upload (users configure their own CI/CD)
- SARIF for non-threat outputs (e.g., coverage matrix as SARIF)
- Custom SARIF extensions beyond standard 2.1.0 properties
- Multi-run SARIF support (baseline comparison, fixed finding tracking)
- Code-level location mapping (tachi analyzes architecture, not source code)
