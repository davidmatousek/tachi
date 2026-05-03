---
prd:
  number: "035"
  topic: quantitative-risk-scoring
  created: 2026-03-27
  status: Approved
  type: feature
triad:
  pm_signoff: { agent: product-manager, date: 2026-03-27, status: APPROVED_WITH_CONCERNS, notes: "Addressed architect and team-lead feedback; severity bands aligned, determinism reframed, context window risk added" }
  architect_signoff: { agent: architect, date: 2026-03-27, status: APPROVED_WITH_CONCERNS, notes: "Feasible with caveats: reframe determinism as reproducible-within-tolerance, target CVSS 3.1, clarify SARIF file relationship, fix no-external-API wording" }
  techlead_signoff: { agent: team-lead, date: 2026-03-27, status: APPROVED_WITH_CONCERNS, notes: "Feasible 8.5-10.5h across 3 waves; P0 scope overloaded vs precedent; recommend resolving open questions before spec; context window risk missing" }
source:
  idea_id: 35
  story_id: null
---

# Quantitative Risk Scoring - Product Requirements Document

**Status**: Draft
**Created**: 2026-03-27
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1

---

## Executive Summary

### The One-Liner
A `/risk-score` command that replaces tachi's qualitative risk ratings with quantitative scores based on CVSS, exploitability, scalability, and reachability analysis.

### Problem Statement
tachi's `/threat-model` currently produces qualitative risk ratings using a 3x3 OWASP matrix (Likelihood HIGH/MEDIUM/LOW x Impact HIGH/MEDIUM/LOW = Risk Level Critical/High/Medium/Low). While useful for initial triage, this approach is insufficient for security managers who need quantitative scores for remediation prioritization, SLA assignment, risk acceptance decisions, and executive reporting. Two threats rated "High" today are treated identically despite potentially having very different real-world risk profiles.

### Proposed Solution
A new `/risk-score` command that takes existing `/threat-model` output (`threats.md` or `threats.sarif`) and enriches each threat with four quantitative scoring dimensions -- CVSS Base, Exploitability, Scalability, and Reachability -- producing a composite score (0.0-10.0) per threat. The command also attaches risk governance fields (owner, SLA, disposition, review date) for remediation tracking.

### Success Criteria
- Security engineers can differentiate between threats that were previously rated identically
- Scored output enables precise remediation prioritization by composite score
- SARIF output includes CVSS scores compatible with GRC tooling import
- Reachability analysis leverages architecture trust boundaries for context-aware scoring

### Timeline
- **Estimated effort**: 8.5-10.5 hours across 3 implementation waves (Team-Lead estimate)
- **Next step**: `/aod.plan` after PRD approval

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](../01_Product_Vision/product-vision.md)

tachi's vision is to be "the default threat modeling toolkit for any team building agentic AI applications." Quantitative risk scoring transforms tachi from a threat identification tool into a risk management tool -- a critical capability for enterprise adoption where security managers require actionable, quantitative metrics for prioritization and reporting.

### Core Value Reinforcement
tachi already models AI-specific threats alongside STRIDE. Quantitative scoring makes these findings actionable by answering "which threats do I fix first and why?" with data-backed answers rather than qualitative judgment.

---

## Target Users & Personas

### Primary Persona: Security Engineer
- **Role**: Hands-on security practitioner running threat models
- **Experience**: Intermediate-to-advanced security knowledge, familiar with CVSS
- **Goals**: Prioritize remediation work by actual risk, not qualitative gut feel
- **Pain Points**: Current qualitative ratings treat all "High" threats equally; no way to differentiate between a High threat that's trivially exploitable vs. one requiring complex attack chains
- **Why This Matters**: Composite scores with dimensional breakdown let them justify remediation order to management and focus effort where risk is highest

### Secondary Persona: Security Manager
- **Role**: Manages security program, reports to CISO/executive leadership
- **Experience**: Broad security knowledge, focused on governance and compliance
- **Goals**: Assign remediation SLAs, make risk acceptance decisions, produce executive reports
- **Pain Points**: Qualitative ratings don't map to SLA tiers; no governance fields for tracking remediation commitments; reporting to leadership requires quantitative metrics
- **Why This Matters**: Risk governance fields (owner, SLA, disposition, review date) enable formal risk tracking, and quantitative scores enable executive dashboards

### Tertiary Persona: Architect
- **Role**: System architect reviewing threat model output for their architecture
- **Experience**: Deep understanding of system architecture, moderate security knowledge
- **Goals**: Understand which components carry the most risk based on their actual exposure
- **Pain Points**: Current ratings don't account for trust boundary depth -- an internet-facing component and an internal-only component can receive the same risk rating
- **Why This Matters**: Reachability analysis uses architecture trust boundaries to produce context-aware scores that reflect actual exposure

---

## User Stories

### US-1: Quantitative Threat Scoring
**When** I have completed a `/threat-model` run and have `threats.md` or `threats.sarif` output,
**I want to** run `/risk-score` to calculate CVSS base + exploitability + scalability + reachability scores for each threat,
**So I can** prioritize remediation by quantitative risk rather than qualitative gut feel.

**Acceptance Criteria**:
- **Given** a valid `threats.md` from `/threat-model`, **when** I run `/risk-score`, **then** each threat receives scores for all four dimensions (CVSS base 0.0-10.0, exploitability 0.0-10.0, scalability 0.0-10.0, reachability 0.0-10.0)
- **Given** a valid `threats.sarif` from `/threat-model`, **when** I run `/risk-score`, **then** the same scoring applies with results in SARIF format
- **Given** scored threats, **when** I view the composite score, **then** it is a weighted combination of the four dimensions on a 0.0-10.0 scale
- **Given** a threat with CVSS base mapped from its category, **when** I review the CVSS assessment, **then** it references CVSS 3.1/4.0 base metrics (attack vector, attack complexity, privileges required, user interaction)

**Priority**: P0
**Effort**: L

### US-2: Risk Governance Fields
**When** I have scored threats from `/risk-score`,
**I want to** see risk governance fields (owner, SLA, disposition, review date) attached to each threat,
**So I can** track remediation commitments and risk acceptance decisions.

**Acceptance Criteria**:
- **Given** a scored threat with composite score >= 9.0 (Critical), **when** governance fields are generated, **then** SLA defaults to 24 hours and disposition defaults to "Mitigate"
- **Given** a scored threat with composite score 7.0-8.9 (High), **when** governance fields are generated, **then** SLA defaults to 7 days and disposition defaults to "Mitigate"
- **Given** a scored threat with composite score 4.0-6.9 (Medium), **when** governance fields are generated, **then** SLA defaults to 30 days and disposition defaults to "Review"
- **Given** a scored threat with composite score < 4.0 (Low), **when** governance fields are generated, **then** SLA defaults to 90 days and disposition defaults to "Review"
- **Given** any scored threat, **when** the owner field is generated, **then** it defaults to "Unassigned" for manual population

**Priority**: P0
**Effort**: M

### US-3: Dual Output Formats
**When** `/risk-score` completes,
**I want to** receive output in both human-readable (`risk-scores.md`) and machine-readable (`risk-scores.sarif`) formats,
**So I can** use scored output for reporting and integrate it with GRC tooling.

**Acceptance Criteria**:
- **Given** scored threats, **when** `risk-scores.md` is generated, **then** it contains a table sorted by composite score descending with columns: ID, Component, Threat, CVSS, Exploitability, Scalability, Reachability, Composite, Severity, SLA, Disposition
- **Given** scored threats, **when** `risk-scores.sarif` is generated, **then** it validates against SARIF 2.1.0 schema
- **Given** `risk-scores.sarif`, **when** imported into GitHub Code Scanning, **then** the `security-severity` property reflects the composite score (not the static mapping used today)
- **Given** both output files, **when** I compare them, **then** all scores and governance fields are consistent between formats

**Priority**: P0
**Effort**: M

### US-4: Reachability-Aware Scoring
**When** I run `/risk-score` with an `architecture.md` that contains trust boundaries,
**I want to** reachability scores adjusted based on component exposure,
**So that** threats against components behind multiple trust boundaries are scored lower than internet-facing components.

**Acceptance Criteria**:
- **Given** a threat targeting a component inside a trust boundary, **when** reachability is assessed, **then** the reachability score is reduced proportionally to boundary depth
- **Given** a threat targeting an internet-facing component with no trust boundary, **when** reachability is assessed, **then** the reachability score reflects maximum exposure
- **Given** a threat targeting a component behind authentication + VPN, **when** reachability is assessed, **then** the reachability score is significantly lower than the same threat against a public endpoint
- **Given** an architecture with no trust boundaries defined, **when** reachability is assessed, **then** a default medium reachability (5.0) is applied with a warning

**Priority**: P1
**Effort**: L

---

## Functional Requirements

### Core Capabilities

#### FR-1: Threat Parsing
**Description**: Parse threat findings from `/threat-model` output files.

**Inputs**: `threats.md` (markdown table format) or `threats.sarif` (SARIF 2.1.0 JSON)
**Processing**: Extract threat ID, component, threat description, category (STRIDE/AI), existing likelihood/impact ratings
**Outputs**: Structured threat list ready for scoring

**Business Rules**:
- Must support both input formats interchangeably
- Must preserve all original threat metadata through the scoring pipeline
- Must validate input exists and is parseable before scoring begins
- If input is missing, exit with clear error: "No threat model output found. Run `/threat-model` first."

#### FR-2: CVSS Base Scoring
**Description**: Map each threat to a CVSS 3.1/4.0 base score based on threat category and description.

**Scoring Approach**:
- Map STRIDE category + threat description to CVSS base vector
- Attack Vector (AV): Derived from component exposure (Network/Adjacent/Local/Physical)
- Attack Complexity (AC): Derived from threat description complexity indicators
- Privileges Required (PR): Derived from authentication requirements
- User Interaction (UI): Derived from whether attack requires user action
- Scope (S): Derived from whether attack crosses trust boundaries

**Output**: CVSS base score 0.0-10.0 per threat

#### FR-3: Exploitability Assessment
**Description**: Assess how exploitable each threat is in practice.

**Scoring Dimensions**:
- Known exploit/technique existence (public PoCs, CVE references, MITRE ATT&CK mappings)
- Attack complexity (single-step vs. multi-step attack chain)
- Tooling availability (automated tools exist vs. manual-only exploitation)
- Skill level required (script kiddie vs. advanced persistent threat)

**Output**: Exploitability score 0.0-10.0 per threat

#### FR-4: Scalability Assessment
**Description**: Evaluate whether the attack can be automated against many targets.

**Scoring Dimensions**:
- Scriptability (can the attack be automated?)
- Target scope (single target vs. mass target)
- Resource requirements (minimal vs. significant infrastructure needed)
- Detection difficulty (easily detected vs. stealthy at scale)

**Output**: Scalability score 0.0-10.0 per threat

#### FR-5: Reachability Analysis
**Description**: Analyze trust boundaries and exposure from `architecture.md` to determine component reachability.

**Scoring Dimensions**:
- Trust boundary depth (0 = internet-facing, higher = more protected)
- Authentication barriers (none, single-factor, multi-factor)
- Network exposure (public internet, VPN-only, internal-only)
- Access control complexity (open, role-based, attribute-based)

**Primary Data Source**: Trust zone table in `threats.md` Section 2 (zone names, trust levels, component assignments -- already produced by `/threat-model`). Boundary depth is inferred from zone metadata, not structurally encoded.
**Supplementary Input**: `architecture.md` Mermaid diagram for richer context (authentication barriers, network exposure details not captured in the trust zone summary)
**Output**: Reachability score 0.0-10.0 per threat (higher = more reachable = higher risk)

#### FR-6: Composite Score Calculation
**Description**: Combine four dimensions into a single composite risk score.

**Weighted Formula**:
```
Composite = (w1 * CVSS) + (w2 * Exploitability) + (w3 * Scalability) + (w4 * Reachability)
```

**Default Weights** (configurable):
| Dimension | Weight | Rationale |
|-----------|--------|-----------|
| CVSS Base | 0.35 | Severity of the vulnerability class is the primary driver |
| Exploitability | 0.30 | Practical exploitability determines real-world risk |
| Scalability | 0.15 | Mass-target capability amplifies risk |
| Reachability | 0.20 | Exposure context adjusts risk to architecture reality |

**Output**: Composite score 0.0-10.0 per threat, mapped to severity bands (aligned with existing `schemas/output.yaml` CVSS ranges):
| Composite Score | Severity | SLA Default |
|----------------|----------|-------------|
| 9.0 - 10.0 | Critical | 24 hours |
| 7.0 - 8.9 | High | 7 days |
| 4.0 - 6.9 | Medium | 30 days |
| 0.0 - 3.9 | Low | 90 days |

#### FR-7: Risk Governance Fields
**Description**: Attach governance metadata to each scored threat.

**Fields Per Threat**:
| Field | Default | Purpose |
|-------|---------|---------|
| Risk Owner | "Unassigned" | Responsible party for remediation |
| Remediation SLA | Severity-driven | Timeline for resolution |
| Risk Disposition | Mitigate (Critical/High), Review (Medium/Low) | Action decision |
| Review Date | SLA deadline | When accepted risks must be re-evaluated |

#### FR-8: Output Generation
**Description**: Produce scored output in dual formats.

**risk-scores.md**: Human-readable markdown with:
- Executive summary (total threats by severity band, highest-risk component)
- Scored threat table sorted by composite score descending
- Dimensional breakdown per threat
- Governance fields per threat
- Scoring methodology explanation
- Weight configuration used

**risk-scores.sarif**: Machine-readable SARIF 2.1.0 with:
- `properties.security-severity` set to composite score (string format, e.g., "7.8")
- `properties.cvss-base` with CVSS 3.1 base score
- `properties.exploitability` with exploitability score
- `properties.scalability` with scalability score
- `properties.reachability` with reachability score
- `properties.risk-owner`, `properties.remediation-sla`, `properties.risk-disposition`
- `partialFingerprints.findingId/v1` preserved from source `threats.sarif` for alert continuity
- Results sorted by composite score descending

**SARIF file relationship**: `risk-scores.sarif` supersedes `threats.sarif` for GitHub Code Scanning upload. It contains the same findings with enriched scoring properties. Users should upload `risk-scores.sarif` (not both files) to avoid duplicate alerts. Finding fingerprints (`findingId/v1`) are preserved for alert tracking continuity.

**Output location**: Output files are written to the same directory as the `/threat-model` output, alongside `threats.md` and `threats.sarif`.

### Interface Contract

**Command**: `/risk-score`

**Input** (required):
- `threats.md` OR `threats.sarif` -- from `/threat-model` output

**Input** (optional):
- `architecture.md` -- for reachability analysis of trust boundaries

**Output** (produces):
- `risk-scores.md` -- scored threat table with dimensional breakdown
- `risk-scores.sarif` -- SARIF 2.1.0 with scoring properties

**Dependencies**:
- Requires `/threat-model` output to exist
- Architecture input is optional but recommended for reachability accuracy

---

## Non-Functional Requirements

### Performance
- Scoring 50 threats: < 60 seconds
- Scoring 200 threats: < 5 minutes
- No external vulnerability database lookups (CVE/NVD) required -- all scoring via LLM analysis of threat descriptions (LLM API calls are inherent to tachi's agent architecture)

### Reliability
- Graceful handling of malformed threat input (skip individual threats, report errors, continue)
- Reproducible scoring: same input produces scores within +/- 0.5 tolerance per dimension across runs (temperature 0; exact determinism not guaranteed across LLM model versions)
- If `architecture.md` is missing, apply default reachability (5.0) with warning

### Compatibility
- SARIF output validates against SARIF 2.1.0 JSON schema
- SARIF compatible with GitHub Code Scanning upload
- Composite score maps to existing severity bands for backward compatibility with qualitative ratings

### Extensibility
- Scoring weights configurable (future: per-project weight profiles)
- Additional scoring dimensions can be added without changing composite formula structure
- Governance field defaults configurable (future: per-organization SLA policies)

---

## Success Metrics

### Primary Metrics
- **Score Differentiation**: Threats previously rated identically (e.g., two "High" threats) receive different composite scores in >= 80% of cases
- **Prioritization Accuracy**: User validates that top-5 composite-scored threats match their intuitive risk ranking in >= 70% of cases
- **SLA Coverage**: 100% of scored threats have governance fields populated

### Secondary Metrics
- **Adoption**: `/risk-score` is run after >= 50% of `/threat-model` invocations (measured by example usage patterns)
- **Format Compliance**: `risk-scores.sarif` validates against SARIF 2.1.0 schema in 100% of runs

---

## Scope & Boundaries

### In Scope (Phase 1)

**Must Have (P0)**:
- `/risk-score` command parsing `threats.md` and `threats.sarif`
- CVSS base scoring per threat
- Exploitability assessment per threat
- Scalability assessment per threat
- Reachability analysis using `architecture.md` trust boundaries
- Composite score calculation with configurable weights
- Risk governance fields (owner, SLA, disposition, review date)
- `risk-scores.md` output with dimensional breakdown
- `risk-scores.sarif` output validating against SARIF 2.1.0

**Should Have (P1)**:
- Scoring methodology explanation section in `risk-scores.md`
- Executive summary with severity band distribution
- Example output against `examples/agentic-app/`

### Out of Scope (Future Phases)

**Won't Have**:
- Custom weight profiles per project (Phase 2)
- Historical score trending across multiple runs (Phase 2)
- Integration with external vulnerability databases (CVE/NVD lookup) (Phase 2)
- Compensating controls analysis that adjusts scores based on existing mitigations (separate feature -- Issue B)
- Interactive score override/adjustment UI (Phase 3)
- Financial impact estimation (cost-of-breach modeling) (Phase 3)

### Assumptions
- LLM analysis provides sufficiently consistent CVSS mapping for threat categories
- Trust boundary annotations in `architecture.md` Mermaid diagrams are parseable
- Default scoring weights serve the majority of use cases

### Constraints
- **No external vulnerability database dependencies**: All scoring performed via LLM analysis; no CVE/NVD lookups required (LLM API is inherent to tachi)
- **tachi scope**: This is a CLI/agent command, not a web service
- **Dependency**: Requires `/threat-model` to have been run first

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: CVSS mapping consistency
- **Likelihood**: Medium
- **Impact**: High
- **Mitigation**: Establish mapping tables for common STRIDE/AI threat categories; use LLM with structured output format and reference examples
- **Contingency**: Fall back to category-level default scores if per-threat mapping proves inconsistent

**Risk 2**: Trust boundary parsing from Mermaid diagrams
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**: Define supported Mermaid trust boundary syntax; fail gracefully with default reachability if parsing fails
- **Contingency**: Accept `architecture.md` as optional input; reachability defaults to 5.0 without it

**Risk 3**: Score calibration
- **Likelihood**: High
- **Impact**: Medium
- **Mitigation**: Validate against `examples/agentic-app/` output; compare composite scores against security expert intuition; include calibration as an explicit task in task breakdown
- **Contingency**: Iterate on weights and scoring rubrics based on user feedback

**Risk 4**: Context window pressure
- **Likelihood**: Medium
- **Impact**: High
- **Mitigation**: A 50-threat model with 4 scoring dimensions could approach 40,000-50,000 tokens. Process threats in the scoring agent with structured output format to minimize token overhead. Consider batching for large threat models (>100 findings).
- **Contingency**: Split scoring into per-dimension sub-invocations if single-pass exceeds context limits

### Dependencies

**Internal Dependencies**:
- `/threat-model` command (existing, delivered) -- provides input
- SARIF generation reference (`adapters/claude-code/agents/references/sarif-generation.md`) -- schema guidance
- Example architectures (`examples/`) -- validation targets

**Dependency Graph**:
```
/threat-model (existing)
  |
  v
/risk-score (this feature)
  |
  v
Compensating Controls (future, Issue B)
```

---

## Open Questions

- [x] Should composite weights be declared in `architecture.md` frontmatter or a separate config file? - architect - 2026-03-27 - **Resolved**: Weights defined in `schemas/risk-scoring.yaml` (consistent with existing schema patterns). Phase 1 defaults hardcoded in command; separate config is Phase 2.
- [x] Should `/risk-score` be chainable from `/threat-model` (auto-run option) or always standalone? - product-manager - 2026-03-27 - **Resolved**: Standalone command for Phase 1. Optional `--risk-score` flag on `/threat-model` for chaining deferred to Phase 2.
- [x] What CVSS version to target: 3.1 (widely adopted) or 4.0 (newer, richer)? - architect - 2026-03-27 - **Resolved**: CVSS 3.1 primary (NVD, GitHub Advisory Database, GRC tooling compatibility). Schema structured to accept 4.0 vectors when adoption matures.

---

## References

### Product Documentation
- Product Vision: [product-vision.md](../01_Product_Vision/product-vision.md)
- GitHub Issue: [#35 - Quantitative Risk Scoring](https://github.com/davidmatousek/tachi/issues/35)

### Technical Documentation
- Constitution: [constitution.md](../../.aod/memory/constitution.md)
- SARIF Reference: `adapters/claude-code/agents/references/sarif-generation.md`
- ADR-013: SARIF Output Format Adoption

### Related PRDs
- PRD-010: [Deduplication & Risk Rating](010-deduplication-risk-rating-2026-03-22.md) -- established the qualitative 3x3 matrix this feature enhances
- PRD-012: [SARIF Output Generation](012-sarif-output-generation-2026-03-22.md) -- SARIF format this feature extends
- PRD-015: [Threat Report Agent & Attack Trees](015-threat-report-agent-attack-trees-2026-03-23.md) -- narrative report that may consume scored output in future

---

## Approval & Sign-Off

| Role | Agent | Status | Date | Comments |
|------|-------|--------|------|----------|
| Product Manager | product-manager | APPROVED_WITH_CONCERNS | 2026-03-27 | Addressed reviewer feedback; severity bands aligned, determinism reframed |
| Architect | architect | APPROVED_WITH_CONCERNS | 2026-03-27 | Target CVSS 3.1; clarify SARIF relationship; reframe determinism |
| Team Lead | team-lead | APPROVED_WITH_CONCERNS | 2026-03-27 | 8.5-10.5h estimate; P0 scope heavy vs precedent; add context window risk |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-27 | product-manager | Initial PRD from GitHub Issue #35 |
| 1.1 | 2026-03-27 | product-manager | Addressed Architect + Team-Lead review concerns: aligned severity bands with schemas/output.yaml, reframed determinism as reproducible-within-tolerance, clarified SARIF file relationship, added context window risk, resolved 3 open questions, added timeline estimate |
