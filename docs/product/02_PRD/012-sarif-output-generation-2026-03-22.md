---
prd:
  number: "012"
  topic: sarif-output-generation
  created: 2026-03-22
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-03-22, status: approved, notes: "PRD drafted by PM via ~aod-define skill with GitHub Issue #12 user stories, consumer guide F-006, and SARIF 2.1.0 research as primary inputs"}
  architect_signoff: {agent: architect, date: 2026-03-22, status: approved_with_concerns, notes: "Technically feasible. 8 findings (0 critical, 2 high, 4 medium, 2 low). High: Note-level SARIF severity mapping inconsistency between PRD FR-3 and output.yaml (note vs none); Finding IR category values don't match PRD rule ID suffixes (info-disclosure vs information-disclosure). All resolvable in spec phase."}
  techlead_signoff: {agent: team-lead, date: 2026-03-22, status: approved_with_concerns, notes: "Feasible in 1 sprint (85% confidence, 3.0-4.0h). Effort sizing L/M/S accurate. 3-wave execution strategy. 2 medium concerns: JSON fidelity risk needs SARIF structural self-check; two open questions (taxonomies, fingerprint keys) should be constrained before task breakdown."}
source:
  idea_id: 12
  story_id: null
---

# SARIF Output Generation - Product Requirements Document

**Status**: Approved
**Created**: 2026-03-22
**Author**: product-manager
**Reviewers**: architect, team-lead
**Phase**: Phase 1 (Foundation)
**Priority**: P1 (High)

---

## Executive Summary

### The One-Liner
Add SARIF 2.1.0 output to the orchestrator so that threat findings appear natively in GitHub Code Scanning, Azure DevOps, and other CI/CD tools that consume SARIF.

### Problem Statement
Developers using tachi generate a human-readable `threats.md` document containing threat findings from up to 11 agents (6 STRIDE + 5 AI). While this document is valuable for manual review, it cannot be consumed by automated CI/CD pipelines. GitHub Code Scanning, Azure DevOps, and other security tooling expect findings in SARIF 2.1.0 format — the OASIS standard for static analysis results interchange.

Without SARIF output, developers must manually transcribe threat findings into their security tracking systems, or build custom parsers to extract structured data from markdown. This friction reduces adoption and limits tachi's integration into automated security workflows. No existing threat modeling tool produces SARIF output — this is a greenfield opportunity to be the first.

### Proposed Solution
Extend the orchestrator's Phase 4 (Assess) to produce a `threats.sarif` file alongside the existing `threats.md`. The SARIF output maps tachi's finding IR (Intermediate Representation) to SARIF 2.1.0 objects:

1. **Each finding becomes a SARIF result** — finding ID, threat description, component location, severity level, and mitigation recommendation are mapped to SARIF `result` objects
2. **Threat categories become SARIF rules** — STRIDE categories (S, T, R, I, D, E) and AI categories (AG, LLM) are mapped to `reportingDescriptor` rule objects with detection guidance and OWASP/CWE references
3. **Risk ratings become SARIF severity levels** — using the CVSS alignment table already defined in `schemas/output.yaml`: Critical→9.0-10.0, High→7.0-8.9, Medium→4.0-6.9, Low→0.1-3.9
4. **Components become SARIF locations** — architecture component names and trust boundaries are mapped to `artifactLocation` with the input file as the physical location
5. **Correlated findings are represented** — correlation groups from F-010 (Deduplication & Risk Rating) are preserved using SARIF `relatedLocations` and `partialFingerprints`

The SARIF generation logic is implemented as **orchestrator prompt instructions**, not application code — consistent with tachi's architecture where all agents are markdown prompt files.

### Success Criteria
- Orchestrator produces both `threats.md` and `threats.sarif` in the same output directory using the same naming convention (`YYYY-MM-DD-{phase}/`)
- Generated SARIF validates against the official SARIF 2.1.0 JSON schema
- Every finding in `threats.md` has a corresponding SARIF result — no findings are lost in translation
- SARIF output is consumable by GitHub Code Scanning via `codeql/upload-sarif@v3` action
- SARIF severity levels correctly map tachi risk levels via the CVSS alignment table
- SARIF rule IDs map to STRIDE and AI threat categories with OWASP/CWE references
- Running against `examples/mermaid-agentic-app/input.md` produces a valid SARIF file with all expected findings
- Running against `examples/ascii-web-api/input.md` produces a valid SARIF file with STRIDE-only findings (no AI rules)

### Timeline
Phase 1 delivery — estimated 1 sprint

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: `docs/product/01_Product_Vision/product-vision.md`

SARIF output directly supports the vision of being "the default threat modeling toolkit for any team building agentic AI applications." CI/CD integration via SARIF removes the adoption barrier of manual finding transcription and positions tachi as a pipeline-native security tool — not just a documentation generator.

### Roadmap Fit
**Phase**: Phase 1 (Foundation)
**Dependencies**: F-005/F-010 (Orchestrator, Deduplication & Risk Rating) — delivered

---

## Target Users & Personas

### Primary Persona: DevOps Engineer
- **Role**: CI/CD pipeline owner, security tooling integrator
- **Experience**: Familiar with GitHub Actions, SARIF, code scanning tools
- **Goals**: Integrate threat modeling into automated security pipelines
- **Pain Points**: No threat modeling tools produce SARIF; must build custom integrations or manually triage findings

**Why This Matters**: SARIF output lets DevOps engineers add tachi to their existing security scanning pipeline with a single GitHub Action step, just like any other SAST tool.

### Secondary Persona: CI Engineer
- **Role**: Build system maintainer, quality gate enforcer
- **Experience**: Configures automated checks, merge gates, and reporting
- **Goals**: Enforce security quality gates that include threat model coverage
- **Pain Points**: Threat modeling results exist only as documents, not as machine-readable data

### Tertiary Persona: Security-Aware Developer
- **Role**: Application developer reviewing Code Scanning alerts
- **Experience**: Reads GitHub Code Scanning results in PR reviews
- **Goals**: See threat findings in the same UI as other security alerts
- **Pain Points**: Threat model findings live in a separate document, not in the code scanning dashboard

---

## User Stories

### US-1: Export Threats as SARIF 2.1.0
**When**: I have generated a threat model with tachi and need findings in my CI/CD security dashboard,
**I want to**: have threats exported as SARIF 2.1.0,
**So I can**: see threat findings natively in GitHub Code Scanning, Azure DevOps, and other SARIF-consuming tools.

**Acceptance Criteria**:
- **Given** a completed threat model run, **when** the orchestrator finishes Phase 4 (Assess), **then** a `threats.sarif` file is produced alongside `threats.md`
- **Given** any STRIDE finding (e.g., S-1), **when** mapped to SARIF, **then** it becomes a `result` with `ruleId` matching the threat category, `message.text` containing the threat description, and `level` mapped from the risk level
- **Given** any AI finding (e.g., AG-1, LLM-2), **when** mapped to SARIF, **then** OWASP references appear in the rule's `help.markdown` and `properties.tags`
- **Given** risk levels from the OWASP 3x3 matrix, **when** mapped to SARIF severity, **then** Critical→`error`(9.0-10.0), High→`error`(7.0-8.9), Medium→`warning`(4.0-6.9), Low→`note`(0.1-3.9)

**Priority**: P0
**Effort**: L

### US-2: Generate SARIF Alongside threats.md
**When**: I run the orchestrator against an architecture input,
**I want to**: SARIF output generated alongside `threats.md`,
**So I can**: get both human-readable and machine-readable outputs in a single run.

**Acceptance Criteria**:
- **Given** an orchestrator run, **when** Phase 4 (Assess) completes, **then** both `threats.md` and `threats.sarif` are produced in the same output directory
- **Given** the output directory, **when** named, **then** it follows the existing convention: `YYYY-MM-DD-{phase}/`
- **Given** the generated `threats.sarif`, **when** validated against the SARIF 2.1.0 JSON schema, **then** validation passes with zero errors

**Priority**: P0
**Effort**: M

### US-3: Link SARIF Results to Architecture Components
**When**: I view SARIF findings in GitHub Code Scanning or another SARIF viewer,
**I want to**: results linked to architecture components,
**So I can**: navigate findings by component and trust boundary in the code scanning UI.

**Acceptance Criteria**:
- **Given** a SARIF result, **when** examining its `locations` array, **then** the `artifactLocation.uri` references the input architecture file and `region` or `logicalLocations` identifies the component name
- **Given** a SARIF result, **when** examining its `message`, **then** it includes the mitigation recommendation as markdown
- **Given** the SARIF `tool.driver` object, **when** examined, **then** it identifies "Tachi" with the schema version (e.g., "1.1") and lists the agent roster used for the run

**Priority**: P1
**Effort**: S

---

## Functional Requirements

### FR-1: Finding IR → SARIF Result Mapping

**Description**: Map each finding from the finding IR (`schemas/finding.yaml`) to a SARIF `result` object.

**Mapping Table**:

| Finding IR Field | SARIF Object Path | Notes |
|-----------------|-------------------|-------|
| `id` | `result.ruleId` + `result.partialFingerprints.findingId` | Rule ID is category-based (e.g., `tachi/stride/spoofing`); finding ID preserved as fingerprint |
| `category` | `result.ruleId` | Maps to rule: S→`tachi/stride/spoofing`, T→`tachi/stride/tampering`, etc. |
| `component` | `result.locations[].logicalLocations[].name` | Component name as logical location |
| `threat` | `result.message.text` | Threat description |
| `likelihood` | Used in `properties.security-severity` computation | Combined with impact via OWASP 3x3 |
| `impact` | Used in `properties.security-severity` computation | Combined with likelihood via OWASP 3x3 |
| `risk_level` | `result.level` + rule `properties.security-severity` | Critical/High→error, Medium→warning, Low→note |
| `mitigation` | `result.message.markdown` | Mitigation as markdown supplement |
| `references` | Rule `help.markdown`, `properties.tags` | OWASP, CWE, CVE references |
| `dfd_element_type` | `result.locations[].logicalLocations[].kind` | External Entity, Process, Data Store, Data Flow |

### FR-2: Threat Categories → SARIF Rules

**Description**: Map threat categories to SARIF `reportingDescriptor` (rule) objects in `tool.driver.rules[]`.

**Rule Definitions**:

| Category | Rule ID | Short Description | Tags |
|----------|---------|-------------------|------|
| Spoofing | `tachi/stride/spoofing` | Identity spoofing threats | `security`, `stride`, `spoofing` |
| Tampering | `tachi/stride/tampering` | Data tampering threats | `security`, `stride`, `tampering` |
| Repudiation | `tachi/stride/repudiation` | Repudiation threats | `security`, `stride`, `repudiation` |
| Info Disclosure | `tachi/stride/information-disclosure` | Information disclosure threats | `security`, `stride`, `information-disclosure` |
| Denial of Service | `tachi/stride/denial-of-service` | Denial of service threats | `security`, `stride`, `denial-of-service` |
| Elevation of Privilege | `tachi/stride/elevation-of-privilege` | Privilege escalation threats | `security`, `stride`, `elevation-of-privilege` |
| Agentic Threats | `tachi/ai/agentic-threats` | AI agent autonomy and misuse threats | `security`, `ai`, `agentic` |
| LLM Threats | `tachi/ai/llm-threats` | LLM-specific threats (prompt injection, data poisoning) | `security`, `ai`, `llm` |

Each rule includes `help.markdown` with detection guidance and framework references (OWASP, CWE, MITRE ATT&CK).

### FR-3: SARIF Severity Mapping

**Description**: Map tachi risk levels to SARIF severity using the CVSS alignment table from `schemas/output.yaml`.

| Tachi Risk Level | SARIF `level` | `security-severity` Float | GitHub Display |
|-----------------|---------------|--------------------------|----------------|
| Critical | error | 9.0 | Critical |
| High | error | 8.0 | High |
| Medium | warning | 5.0 | Medium |
| Low | note | 2.0 | Low |
| Note | note | 0.0 | No severity |

### FR-4: SARIF Tool Metadata

**Description**: Populate `tool.driver` with tachi identification.

```json
{
  "name": "Tachi",
  "semanticVersion": "{schema_version from output.yaml}",
  "informationUri": "https://github.com/{repo}",
  "rules": [ /* FR-2 rule definitions */ ]
}
```

### FR-5: Correlated Finding Representation

**Description**: Correlated findings from F-010 (Deduplication & Risk Rating) are represented in SARIF using `relatedLocations` to link the primary finding to its correlated peers.

- Primary finding: Full SARIF `result` with all mapped fields
- Correlated peers: Listed in `relatedLocations[]` with their finding IDs
- Correlation group: Preserved in `partialFingerprints.correlationGroup` (e.g., `CG-1`)
- Deduplicated count: Only the primary finding appears as a top-level result; correlated peers are referenced, not duplicated

### FR-6: SARIF Schema Compliance

**Description**: The generated SARIF must conform to SARIF 2.1.0 specification.

**Required top-level structure**:
```json
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [{
    "tool": { "driver": { /* FR-4 */ } },
    "results": [ /* FR-1 mapped findings */ ]
  }]
}
```

**GitHub Code Scanning constraints**:
- Max file size (gzip): 10 MB
- Max results per run: 25,000
- Max rules per run: 25,000

---

## Non-Functional Requirements

### Completeness
- Every finding in `threats.md` MUST have a corresponding SARIF result — zero findings lost in translation
- If the orchestrator produces N findings, the SARIF file MUST contain exactly N results (or N-correlated for deduplicated findings where correlated peers are in `relatedLocations`)

### Consistency
- SARIF severity levels MUST match the risk levels shown in `threats.md` — no divergence between human-readable and machine-readable output
- SARIF rule IDs MUST be stable across runs for the same threat category — enables GitHub Code Scanning to track findings over time

### Schema Validity
- Generated SARIF MUST validate against the official SARIF 2.1.0 JSON schema with zero validation errors
- SARIF MUST be parseable by `codeql/upload-sarif@v3` GitHub Action

### Performance
- SARIF generation adds no additional orchestrator phases — mapping occurs within Phase 4 (Assess) alongside existing threats.md generation
- Output file size is bounded by the number of findings — typical threat models produce <100 findings, well within GitHub's 25,000 limit

---

## Success Metrics

### Primary Metrics

**SARIF Schema Validity**: 100% of generated SARIF files validate against SARIF 2.1.0 JSON schema
- **Baseline**: N/A (no SARIF output exists)
- **Target**: 100% validation pass rate
- **Timeline**: At delivery

**Finding Completeness**: 100% of threats.md findings represented in SARIF
- **Baseline**: N/A
- **Target**: Zero finding loss between markdown and SARIF output
- **Timeline**: At delivery

**GitHub Code Scanning Upload**: Generated SARIF is accepted by `codeql/upload-sarif@v3`
- **Baseline**: N/A
- **Target**: Successful upload with findings displayed in Code Scanning alerts
- **Timeline**: At delivery

---

## Scope & Boundaries

### In Scope (MVP)

**Must Have (P0)**:
- Finding IR → SARIF result mapping for all 8 threat categories
- SARIF rule definitions for STRIDE and AI categories
- SARIF severity mapping via CVSS alignment table
- Tool metadata with tachi identification
- Co-generation with threats.md in same output directory
- SARIF 2.1.0 schema validation

**Should Have (P1)**:
- Component-to-location mapping with logical locations
- Correlated finding representation via `relatedLocations`
- `partialFingerprints` for stable finding tracking across runs

### Out of Scope

**Won't Have**:
- SARIF viewer or dashboard (use GitHub Code Scanning or existing SARIF viewers)
- GitHub Action for automated upload (users configure their own CI/CD)
- SARIF for non-threat outputs (e.g., coverage matrix as SARIF)
- Custom SARIF extensions beyond standard 2.1.0 properties
- Multi-run SARIF support (baseline comparison, fixed finding tracking)
- Code-level location mapping (tachi analyzes architecture, not source code)

### Assumptions
- SARIF 2.1.0 is the target version (not 2.0 or draft 2.2)
- GitHub Code Scanning is the primary integration target, but output is standard-compliant for any SARIF consumer
- Architecture component names are sufficient as logical locations (no source code line mapping)
- The orchestrator already produces a complete finding IR before Phase 4 assembly

### Constraints
- **No application code**: SARIF generation is orchestrator prompt instructions, not a code generator
- **Schema version stability**: SARIF rule IDs must remain stable across tachi versions for finding tracking
- **Dependency**: Requires F-005/F-010 (Deduplication & Risk Rating) — delivered

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: SARIF location mapping for architecture-level findings
- **Likelihood**: Medium
- **Impact**: Low
- **Mitigation**: Use `logicalLocations` with component names rather than `physicalLocation` line numbers. Architecture threat modeling operates at component level, not source code level — `logicalLocations` is the appropriate SARIF construct.
- **Contingency**: Fall back to input file URI without line-level granularity

**Risk 2**: JSON output fidelity from LLM-generated content
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**: Define strict JSON structure in orchestrator prompt with example output. Validate against schema in test runs. The orchestrator already produces structured markdown tables — JSON is a different serialization of the same data.
- **Contingency**: Add schema validation checklist to orchestrator prompt

### Dependencies

**Internal Dependencies**:
- **F-003 (Orchestrator)**: Delivered — provides Phase 4 assembly where SARIF generation is added
- **F-005/F-010 (Deduplication & Risk Rating)**: Delivered — provides correlated findings and CVSS alignment table
- **`schemas/output.yaml` v1.1**: Already includes SARIF severity mapping table and lists SARIF as a consumer
- **`schemas/finding.yaml`**: Defines the finding IR that SARIF maps from

**Dependency Graph**:
```
F-006 (SARIF Output)
  ├── Depends on: F-003 (Orchestrator) ✅ Delivered
  ├── Depends on: F-005/F-010 (Dedup & Risk) ✅ Delivered
  └── Blocks: F-009 (Platform Adapters — SARIF upload automation)
```

---

## Open Questions

- [x] Which SARIF version to target? — 2.1.0 (OASIS standard, GitHub Code Scanning requirement) — Answered
- [x] How to handle architecture-level locations (no source code)? — Use `logicalLocations` with component names — Answered
- [x] How to represent correlated findings? — `relatedLocations` + `partialFingerprints.correlationGroup` — Answered
- [ ] Should the SARIF file include a `taxonomies` array for OWASP/CWE/MITRE frameworks? — architect — Decide in spec phase
- [ ] Should `partialFingerprints` use component+category or component+threat as the dedup key? — architect — Decide in spec phase

---

## References

### Product Documentation
- Product Vision: `docs/product/01_Product_Vision/product-vision.md`
- Consumer Guide: `docs/guides/CONSUMER_GUIDE_TACHI.md` § F-006
- Research: `docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md` § 6 (SARIF 2.1.0), § 10 (CVSS)

### Technical Documentation
- Output Schema: `schemas/output.yaml` (v1.1 — includes SARIF severity mapping)
- Finding Schema: `schemas/finding.yaml` (finding IR)
- Orchestrator: `agents/orchestrator.md` (Phase 4 assembly)
- Output Template: `templates/threats.md` (current markdown output)

### External Resources
- SARIF 2.1.0 Specification: OASIS Standard
- GitHub Code Scanning SARIF Support: GitHub Docs
- SARIF JSON Schema: SchemaStore / oasis-tcs

---

## Approval & Sign-Off

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | ✅ Approved | 2026-03-22 | PRD drafted with GitHub Issue #12 stories, consumer guide F-006, and SARIF 2.1.0 research |
| Architect | architect | 🟡 Approved with Concerns | 2026-03-22 | 2 high findings resolvable in spec: severity mapping alignment, category-to-ruleId naming |
| Engineering Lead | team-lead | 🟡 Approved with Concerns | 2026-03-22 | 1 sprint feasible (85% confidence, 3.0-4.0h). JSON fidelity risk needs mitigation in spec |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-22 | product-manager | Initial PRD |
