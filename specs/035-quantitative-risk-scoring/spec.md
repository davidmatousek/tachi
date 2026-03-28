---
prd_reference: docs/product/02_PRD/035-quantitative-risk-scoring-2026-03-27.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-27
    status: APPROVED_WITH_CONCERNS
    notes: "All 4 PRD user stories covered, 17 FRs traceable to PRD. Minor concerns: US-4 reachability ranges are more prescriptive than PRD (treat as norms with tolerance); SC-001 differentiation metric should clarify exclusion of correlated peer groups."
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: Quantitative Risk Scoring

**Feature Branch**: `035-quantitative-risk-scoring`
**Created**: 2026-03-27
**Status**: Draft
**PRD Reference**: `docs/product/02_PRD/035-quantitative-risk-scoring-2026-03-27.md`
**Input**: User description: "A /risk-score command that replaces qualitative risk ratings with quantitative scores based on CVSS, exploitability, scalability, and reachability analysis"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Quantitative Threat Scoring (Priority: P0)

As a security engineer who has completed a `/threat-model` run, I want to run `/risk-score` to calculate four-dimensional quantitative scores for each threat finding, so I can prioritize remediation by data-backed risk rather than qualitative gut feel.

**Why this priority**: Core value proposition. Without quantitative scoring, the feature delivers no differentiation over the existing qualitative OWASP 3x3 matrix. Every other capability (governance fields, output formats, reachability) builds on this foundation.

**Independent Test**: Can be fully tested by running `/risk-score` against `examples/agentic-app/` threat model output and verifying each finding receives four numeric scores and a composite score on a 0.0-10.0 scale.

**Acceptance Scenarios**:

1. **Given** a valid `threats.md` from `/threat-model`, **When** I run `/risk-score`, **Then** each threat finding receives scores for all four dimensions: CVSS base (0.0-10.0), exploitability (0.0-10.0), scalability (0.0-10.0), and reachability (0.0-10.0)
2. **Given** a valid `threats.sarif` from `/threat-model`, **When** I run `/risk-score`, **Then** the same four-dimensional scoring applies with equivalent results regardless of input format
3. **Given** scored threats, **When** I view the composite score, **Then** it is a weighted combination of the four dimensions on a 0.0-10.0 scale using default weights (CVSS 35%, Exploitability 30%, Scalability 15%, Reachability 20%)
4. **Given** a threat finding with CVSS base mapping, **When** I review the CVSS assessment, **Then** it includes CVSS 3.1 base metrics (attack vector, attack complexity, privileges required, user interaction, scope) and the full CVSS vector string for auditability
5. **Given** two threat findings that previously received identical qualitative ratings (e.g., both "High"), **When** I compare their composite scores, **Then** they receive different composite scores in at least 80% of such cases
6. **Given** the same threat model input run twice, **When** I compare dimension scores across runs, **Then** each dimension score is within +/- 0.5 tolerance (reproducibility at temperature 0)

---

### User Story 2 - Risk Governance Fields (Priority: P0)

As a security manager, I want risk governance fields (owner, SLA, disposition, review date) attached to each scored threat, so I can track remediation commitments and risk acceptance decisions.

**Why this priority**: Governance fields transform scored findings into actionable remediation tracking items. Without them, quantitative scores remain informational rather than operational — blocking the key security manager workflow.

**Independent Test**: Can be fully tested by verifying governance fields are populated for every scored threat and that SLA defaults align with severity bands.

**Acceptance Scenarios**:

1. **Given** a scored threat with composite score >= 9.0 (Critical), **When** governance fields are generated, **Then** SLA defaults to 24 hours and disposition defaults to "Mitigate"
2. **Given** a scored threat with composite score 7.0-8.9 (High), **When** governance fields are generated, **Then** SLA defaults to 7 days and disposition defaults to "Mitigate"
3. **Given** a scored threat with composite score 4.0-6.9 (Medium), **When** governance fields are generated, **Then** SLA defaults to 30 days and disposition defaults to "Review"
4. **Given** a scored threat with composite score < 4.0 (Low), **When** governance fields are generated, **Then** SLA defaults to 90 days and disposition defaults to "Review"
5. **Given** any scored threat, **When** the owner field is generated, **Then** it defaults to "Unassigned" for manual population
6. **Given** any scored threat, **When** the review date is generated, **Then** it is calculated as the scoring date plus the SLA duration

---

### User Story 3 - Dual Output Formats (Priority: P0)

As a security engineer, I want scored output in both human-readable markdown and machine-readable SARIF formats, so I can use scored findings for reporting and integrate them with GRC tooling and GitHub Code Scanning.

**Why this priority**: Output generation is the delivery mechanism for all scoring work. Without dual outputs, scores remain inaccessible to downstream consumers (GRC tools, GitHub, dashboards). Tied to P0 because all three persona workflows depend on output availability.

**Independent Test**: Can be fully tested by validating `risk-scores.md` contains a sorted scored threat table and `risk-scores.sarif` validates against the SARIF 2.1.0 JSON schema.

**Acceptance Scenarios**:

1. **Given** scored threats, **When** `risk-scores.md` is generated, **Then** it contains a table sorted by composite score descending with columns: ID, Component, Threat, CVSS, Exploitability, Scalability, Reachability, Composite, Severity, SLA, Disposition
2. **Given** scored threats, **When** `risk-scores.md` is generated, **Then** it includes an executive summary with total threats by severity band and highest-risk component
3. **Given** scored threats, **When** `risk-scores.md` is generated, **Then** it includes a scoring methodology section documenting the weights and formula used
4. **Given** scored threats, **When** `risk-scores.sarif` is generated, **Then** it validates against the SARIF 2.1.0 JSON schema
5. **Given** `risk-scores.sarif`, **When** the `security-severity` property is examined, **Then** it reflects the composite score as a numeric string (e.g., "7.8") per finding, not a static category-level mapping
6. **Given** `risk-scores.sarif`, **When** finding fingerprints are examined, **Then** `partialFingerprints.findingId/v1` values are preserved from the source `threats.sarif` for alert tracking continuity
7. **Given** both output files, **When** I compare them, **Then** all scores and governance fields are consistent between formats
8. **Given** scored output, **When** I check the output location, **Then** `risk-scores.md` and `risk-scores.sarif` are written to the same directory as the input `threats.md`/`threats.sarif`

---

### User Story 4 - Reachability-Aware Scoring (Priority: P1)

As an architect reviewing threat model output, I want reachability scores adjusted based on component exposure within trust boundaries, so that threats against well-protected internal components score lower than threats against internet-facing components.

**Why this priority**: Reachability adds architecture-aware context that differentiates this tool from generic CVSS calculators. Ranked P1 because core scoring (P0) functions with default reachability (5.0) — reachability enhancement improves accuracy but is not blocking.

**Independent Test**: Can be fully tested by running `/risk-score` against a threat model with trust boundaries defined and verifying that internet-facing component threats score higher reachability than internal component threats.

**Acceptance Scenarios**:

1. **Given** a threat targeting a component in an Untrusted/External zone, **When** reachability is assessed, **Then** the reachability score reflects maximum exposure (8.0-10.0)
2. **Given** a threat targeting a component in a Semi-Trusted/Application zone, **When** reachability is assessed, **Then** the reachability score reflects moderate exposure (4.0-7.0)
3. **Given** a threat targeting a component in a Trusted/Internal zone behind authentication and network segmentation, **When** reachability is assessed, **Then** the reachability score is significantly lower (1.0-4.0) than the same threat against a public endpoint
4. **Given** an architecture with no trust boundaries defined (no trust zone table in threats.md and no architecture.md), **When** reachability is assessed, **Then** a default medium reachability (5.0) is applied with a warning message
5. **Given** trust zone data from `threats.md` Section 2, **When** reachability is calculated, **Then** the trust zone table is the primary data source for component-to-zone mapping
6. **Given** supplementary data from `architecture.md`, **When** reachability is calculated, **Then** additional context (authentication barriers, network exposure details) adjusts the baseline zone-derived score

---

### User Story 5 - Scoring Methodology Documentation (Priority: P1)

As a security manager preparing executive reports, I want a clear explanation of how scores are calculated included in the output, so I can justify prioritization decisions and explain the scoring model to stakeholders.

**Why this priority**: Transparency builds trust in the scoring system and enables security managers to defend prioritization decisions. Important for adoption but not required for core functionality.

**Independent Test**: Can be fully tested by verifying `risk-scores.md` includes a methodology section that explains the four dimensions, their weights, and the composite formula.

**Acceptance Scenarios**:

1. **Given** scored output, **When** I read the methodology section in `risk-scores.md`, **Then** it explains each scoring dimension (CVSS, exploitability, scalability, reachability) and what each measures
2. **Given** scored output, **When** I read the methodology section, **Then** it documents the weights used and the composite formula
3. **Given** scored output, **When** I read the methodology section, **Then** it explains the severity band mapping (composite score ranges to Critical/High/Medium/Low)

---

### Edge Cases

- **Malformed threat input**: What happens when individual threat entries in `threats.md` are malformed or missing required fields? The system must skip malformed entries, report them as errors, and continue scoring valid entries.
- **Empty threat model**: What happens when `threats.md` or `threats.sarif` contains zero threat findings? The system must exit with a clear message: "No threat findings to score."
- **Missing input files**: What happens when neither `threats.md` nor `threats.sarif` exists? The system must exit with: "No threat model output found. Run `/threat-model` first."
- **Correlated findings**: What happens when Section 4a contains correlation groups? Primary findings receive full scoring; correlated peers inherit the primary's scores to maintain group consistency.
- **Score boundary precision**: What happens when a composite score falls exactly on a severity band boundary (e.g., exactly 7.0)? The boundary value maps to the higher band (7.0 = High, 4.0 = Medium, 9.0 = Critical).
- **Large threat models (>100 findings)**: What happens with large threat models? The system must handle up to 200 threats within the 5-minute performance target, using batching strategies if needed to manage context window constraints.
- **AI-specific threat categories**: What happens for agentic and LLM threat categories that have no standard CVSS mappings? The system must apply tachi-specific default CVSS vectors for these categories, documented in the methodology section.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST parse threat findings from both `threats.md` (markdown table format) and `threats.sarif` (SARIF 2.1.0 JSON), extracting threat ID, component, category, description, likelihood, impact, and existing risk level
- **FR-002**: System MUST map each threat finding to a CVSS 3.1 base score (0.0-10.0) using attack vector, attack complexity, privileges required, user interaction, and scope metrics derived from the threat category and description
- **FR-003**: System MUST store the full CVSS 3.1 vector string (e.g., `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`) alongside the numeric base score for auditability
- **FR-004**: System MUST assess exploitability (0.0-10.0) for each threat based on known exploit/technique existence, attack complexity, tooling availability, and skill level required
- **FR-005**: System MUST assess scalability (0.0-10.0) for each threat based on scriptability, target scope, resource requirements, and detection difficulty
- **FR-006**: System MUST assess reachability (0.0-10.0) for each threat using trust zone data from `threats.md` Section 2 as primary source, supplemented by `architecture.md` when available
- **FR-007**: System MUST calculate a composite risk score (0.0-10.0) per threat using the weighted formula: `Composite = (0.35 x CVSS) + (0.30 x Exploitability) + (0.15 x Scalability) + (0.20 x Reachability)`
- **FR-008**: System MUST map composite scores to severity bands: Critical (9.0-10.0), High (7.0-8.9), Medium (4.0-6.9), Low (0.0-3.9) — aligned with existing `schemas/output.yaml` CVSS ranges
- **FR-009**: System MUST attach governance fields to each scored threat: Risk Owner (default "Unassigned"), Remediation SLA (severity-driven), Risk Disposition (Mitigate for Critical/High, Review for Medium/Low), and Review Date (scoring date + SLA duration)
- **FR-010**: System MUST generate `risk-scores.md` containing an executive summary, scored threat table sorted by composite score descending, dimensional breakdown per threat, governance fields, and scoring methodology explanation
- **FR-011**: System MUST generate `risk-scores.sarif` validating against SARIF 2.1.0 schema, with `security-severity` set to the composite score per finding, and scoring properties in the result property bag
- **FR-012**: System MUST preserve all original threat metadata (ID, component, category, description, mitigation, references) through the scoring pipeline without modification
- **FR-013**: System MUST preserve SARIF fingerprints (`partialFingerprints.findingId/v1` and `primaryLocationLineHash`) from the source `threats.sarif` for GitHub Code Scanning alert continuity
- **FR-014**: System MUST apply default medium reachability (5.0) with a warning when trust zone data is unavailable (no Section 2 in threats.md and no architecture.md)
- **FR-015**: System MUST gracefully handle malformed threat entries by skipping individual findings, reporting errors, and continuing to score remaining valid findings
- **FR-016**: System MUST validate that input files exist and are parseable before scoring begins, exiting with a clear error message if validation fails
- **FR-017**: System MUST write output files to the same directory as the input `threats.md`/`threats.sarif`

### Key Entities

- **Scored Finding**: A threat finding enriched with four dimensional scores (CVSS base, exploitability, scalability, reachability), a composite score, a severity band, and governance fields. Extends the existing finding IR without modifying original fields.
- **Scoring Dimensions**: Four independent assessment axes (CVSS base, exploitability, scalability, reachability) each producing a 0.0-10.0 score. Combined via weighted formula into a composite score.
- **Governance Record**: Per-threat remediation tracking metadata comprising risk owner, remediation SLA, risk disposition, and review date. Defaults are severity-driven; intended for manual override by security managers.
- **Severity Band**: Classification of composite scores into four tiers (Critical, High, Medium, Low) with associated default SLA and disposition values. Aligned with existing tachi severity bands.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Score Differentiation — Threats previously rated identically (e.g., two "High" threats) receive different composite scores in >= 80% of such cases when validated against `examples/agentic-app/` output
- **SC-002**: Prioritization Accuracy — Top-5 composite-scored threats match intuitive risk ranking (validated by security-knowledgeable reviewer) in >= 70% of cases
- **SC-003**: SLA Coverage — 100% of scored threats have all governance fields populated (owner, SLA, disposition, review date)
- **SC-004**: Format Compliance — `risk-scores.sarif` validates against SARIF 2.1.0 JSON schema in 100% of runs
- **SC-005**: Dual-Format Parity — All scores and governance fields are consistent between `risk-scores.md` and `risk-scores.sarif` in 100% of runs
- **SC-006**: Performance — Scoring completes within 60 seconds for 50 threats and within 5 minutes for 200 threats
- **SC-007**: Reproducibility — Same input produces dimension scores within +/- 0.5 tolerance across runs at temperature 0
- **SC-008**: Backward Compatibility — Composite severity bands map to existing Critical/High/Medium/Low classifications used by `schemas/output.yaml`
- **SC-009**: Alert Continuity — SARIF fingerprints are preserved, enabling `risk-scores.sarif` to supersede `threats.sarif` for GitHub Code Scanning without creating duplicate alerts

## Assumptions

- LLM analysis provides sufficiently consistent CVSS mapping for threat categories to achieve the +/- 0.5 reproducibility target at temperature 0
- Trust zone annotations in existing `threats.md` Section 2 provide sufficient data for meaningful reachability differentiation
- Default scoring weights (35/30/15/20) serve the majority of use cases without per-project customization (Phase 1)
- The existing `/threat-model` deduplication (Section 4a) is complete — `/risk-score` does not need to re-deduplicate
- AI-specific threat categories (agentic, LLM) can be meaningfully mapped to CVSS 3.1 vectors using tachi-specific defaults
- Output file co-location (same directory as threat model output) is the expected workflow; no separate output directory configuration is needed for Phase 1

## Out of Scope

- Custom weight profiles per project (Phase 2)
- Historical score trending across multiple runs (Phase 2)
- Integration with external vulnerability databases such as CVE/NVD (Phase 2)
- Compensating controls analysis adjusting scores based on existing mitigations (separate feature)
- Optional `--risk-score` flag on `/threat-model` for command chaining (Phase 2)
- Interactive score override/adjustment UI (Phase 3)
- Financial impact estimation / cost-of-breach modeling (Phase 3)

## Dependencies

- `/threat-model` command output (`threats.md` and/or `threats.sarif`) must exist as input
- SARIF 2.1.0 schema compliance for output validation
- `schemas/output.yaml` severity band definitions for backward compatibility alignment
- `examples/agentic-app/` threat model output for validation and calibration testing
