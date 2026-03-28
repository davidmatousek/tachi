---
prd_reference: docs/product/02_PRD/036-compensating-controls-2026-03-27.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-27
    status: APPROVED_WITH_CONCERNS
    notes: "All 5 PRD user stories mapped, all 6 FRs decomposed into 20 spec FRs, P0/P1 boundary clean. 3 low-severity concerns: (1) recommendation sorting promoted P1-to-P0 — track for traceability, (2) executive summary promoted P1-to-P0 — document rationale during planning, (3) pipeline adoption metric deferred to delivery."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Compensating Controls Analysis

**Feature Branch**: `036-compensating-controls`
**Created**: 2026-03-27
**Status**: Draft
**PRD Reference**: `docs/product/02_PRD/036-compensating-controls-2026-03-27.md`
**Input**: PRD-036 — `/compensating-controls` command that scans a target codebase against scored threats to detect existing security controls, recommend missing controls, assess control effectiveness, and calculate residual risk.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Codebase Control Detection (Priority: P0)

A developer has run `/threat-model` and `/risk-score` against their agentic application and now has a list of 30+ scored threats. They want to know which threats their existing code already handles — auth middleware, input validation, rate limiters — without manually searching every file. They run `/compensating-controls --target ./my-app` and receive a report classifying each threat as "Control Found," "Partial Control," or "No Control Found" with file:line evidence linking detected controls to the actual code.

**Why this priority**: This is the foundational capability. Without control detection, no downstream analysis (recommendations, residual risk) is possible. It delivers immediate value by answering "what do I already have?"

**Independent Test**: Run `/compensating-controls` against `examples/agentic-app/` with existing `risk-scores.md` input. Verify that the output classifies each scored threat, provides file:line evidence for detected controls, and every threat receives exactly one classification (Found / Partial / Missing).

**Acceptance Scenarios**:

1. **Given** a target codebase containing auth middleware and scored threats related to spoofing, **When** `/compensating-controls` runs, **Then** spoofing threats are classified as "Control Found" with file:line evidence pointing to the middleware code.
2. **Given** a target codebase with input validation on some API endpoints but not all, **When** `/compensating-controls` runs, **Then** injection threats are classified as "Partial Control" with evidence showing which endpoints are covered and which are not.
3. **Given** a scored threat with no corresponding control in the codebase, **When** `/compensating-controls` runs, **Then** it is classified as "No Control Found" with no false evidence.
4. **Given** the analysis completes, **When** the user views the output, **Then** every scored threat has exactly one classification and the report includes a coverage matrix summarizing all findings.

---

### User Story 2 — Compensating Control Recommendations (Priority: P0)

A developer sees that 12 of their 34 threats have no controls. They need to know what to build, where to build it, and in what order. The report provides a prioritized recommendations section sorted by composite risk score (highest risk gaps first), with each recommendation specifying: what control to implement, where in the codebase to implement it, reference patterns or libraries to use, and an effort estimate (Low / Medium / High).

**Why this priority**: Recommendations are the actionable bridge between risk identification and remediation. Without them, users have a gap list but no remediation roadmap — the core problem the PRD aims to solve.

**Independent Test**: Given a set of threats classified as "No Control Found" and "Partial Control," verify the output includes a recommendations section with all required fields, sorted by composite risk score descending, with effort estimates for every recommendation.

**Acceptance Scenarios**:

1. **Given** a threat classified as "No Control Found" with a composite score of 8.5 (High), **When** recommendations are generated, **Then** the recommendation includes what to implement, a suggested implementation location, reference patterns, and an effort estimate.
2. **Given** a threat classified as "Partial Control," **When** recommendations are generated, **Then** the recommendation focuses on hardening the existing control (what's missing, how to extend) rather than suggesting a replacement.
3. **Given** multiple unmitigated threats, **When** recommendations are generated, **Then** they are sorted by composite risk score descending (highest risk first).
4. **Given** any recommendation, **When** the user reads it, **Then** the effort estimate is one of Low (configuration change), Medium (new middleware/function), or High (architectural change).

---

### User Story 3 — Residual Risk Calculation (Priority: P0)

A security manager needs to report the actual risk posture after accounting for existing controls. After control detection completes, the system calculates a residual risk score for each threat using the formula `Residual = Inherent * (1 - Reduction Factor)`, where the reduction factor is determined by control status. The output includes per-threat residual scores and a summary showing total inherent risk, total residual risk, and overall risk reduction percentage.

**Why this priority**: Residual risk transforms raw threat scores into an actionable risk posture that reflects reality. Without it, the threat scores overstate risk for threats that are already mitigated.

**Independent Test**: Given threats with known control classifications, verify that residual risk scores are calculated correctly using binary reduction factors and that the summary statistics (total inherent, total residual, delta, % reduction) are arithmetically correct.

**Acceptance Scenarios**:

1. **Given** a threat with composite score 8.0 classified as "Control Found," **When** residual risk is calculated, **Then** the residual score is 4.0 (8.0 * (1 - 0.50)) with residual severity "Medium."
2. **Given** a threat with composite score 8.0 classified as "Partial Control," **When** residual risk is calculated, **Then** the residual score is 6.0 (8.0 * (1 - 0.25)) with residual severity "Medium."
3. **Given** a threat with composite score 8.0 classified as "No Control Found," **When** residual risk is calculated, **Then** the residual score equals the inherent score: 8.0 (High).
4. **Given** all threats are scored, **When** the summary is generated, **Then** it shows total inherent risk, total residual risk, the delta between them, and the overall risk reduction percentage.

---

### User Story 4 — Coverage Matrix (Priority: P0)

A security manager needs a single-glance view of their threat posture. The coverage matrix is a table showing every analyzed threat with columns: Threat ID, Component, Threat Description, Inherent Score, Inherent Severity, Control Status, Residual Score, Residual Severity. Below the table, summary statistics show the percentage of threats in each category (X% Control Found, Y% Partial Control, Z% No Control Found).

**Why this priority**: The coverage matrix is the executive-level deliverable that enables posture reporting without requiring users to read the full detailed report.

**Independent Test**: Given completed control analysis, verify the coverage matrix contains a row for every analyzed threat, summary statistics are arithmetically correct, and unmitigated threats are sorted by risk score severity.

**Acceptance Scenarios**:

1. **Given** control analysis is complete for 34 threats, **When** the coverage matrix is rendered, **Then** it contains exactly 34 rows with all required columns populated.
2. **Given** 20 threats have controls found, 8 are partial, and 6 are missing, **When** summary statistics are shown, **Then** they read "59% Control Found, 24% Partial Control, 18% No Control Found."
3. **Given** unmitigated threats with varying risk scores, **When** the matrix is viewed, **Then** threats are visually organized by residual severity (Critical/High/Medium/Low sections or equivalent grouping).

---

### User Story 5 — Dual-Format Output (Priority: P0)

The system produces two output files: `compensating-controls.md` (human-readable report with executive summary, coverage matrix, control details, recommendations, and residual risk summary) and `compensating-controls.sarif` (machine-readable SARIF 2.1.0 for GitHub Code Scanning integration). The SARIF file supersedes `risk-scores.sarif` in the alert chain, preserving finding fingerprints for alert continuity.

**Why this priority**: Dual-format output is essential for the two primary consumption paths — human review (markdown) and CI/CD integration (SARIF). Without SARIF, the feature cannot integrate into automated security workflows.

**Independent Test**: Run `/compensating-controls` and verify both files are generated, the markdown contains all required sections, and the SARIF validates against the SARIF 2.1.0 JSON schema with correct tool metadata and property fields.

**Acceptance Scenarios**:

1. **Given** control analysis completes, **When** output is generated, **Then** both `compensating-controls.md` and `compensating-controls.sarif` are written to the output directory.
2. **Given** `compensating-controls.sarif` is generated, **When** validated against the SARIF 2.1.0 JSON schema, **Then** it passes validation with no errors.
3. **Given** the upstream `risk-scores.sarif` contains finding fingerprints (`findingId/v1`), **When** `compensating-controls.sarif` is generated, **Then** the same fingerprints are preserved for every corresponding finding.
4. **Given** `compensating-controls.sarif` is uploaded to GitHub Code Scanning, **When** a user views the alerts, **Then** `security-severity` reflects the residual risk score (not the inherent score) and no duplicate alerts are created for findings already tracked by `risk-scores.sarif`.

---

### User Story 6 — Control Effectiveness Assessment (Priority: P1)

A security engineer wants to know not just whether a control exists, but whether it is adequate for the specific threat. When a control is detected, the system evaluates its effectiveness across four dimensions: coverage (does it protect all relevant paths?), configuration (are thresholds appropriate?), currency (are algorithms up to date?), and completeness (does it address the full attack vector?). Each control receives a rating of Strong, Moderate, or Weak with an explanation.

**Why this priority**: Effectiveness assessment is an enhancement to the P0 binary detection. P0 delivers value with exists/missing classification; P1 adds nuance for security engineers who need deeper analysis. When implemented, effectiveness ratings automatically upgrade the residual risk reduction factors from the 3-level binary model to the 7-level effectiveness-aware model.

**Independent Test**: Given detected controls, verify that effectiveness ratings are assigned using the four assessment dimensions with reasoned explanations, and that the 7-level reduction factor matrix is applied to residual risk calculation when this story is active.

**Acceptance Scenarios**:

1. **Given** a rate limiter is detected for a DoS threat, **When** effectiveness is assessed, **Then** the assessment evaluates threshold appropriateness (e.g., "1000 req/s is too permissive for brute-force protection") and assigns a rating with reasoning.
2. **Given** auth middleware covers 8 of 12 routes, **When** effectiveness is assessed, **Then** the coverage dimension flags the 4 uncovered routes and the rating reflects the gap (Moderate or Weak).
3. **Given** encryption using MD5 is detected, **When** effectiveness is assessed, **Then** the currency dimension flags MD5 as deprecated and the rating is Weak.
4. **Given** a control rated "Strong," **When** residual risk is calculated with P1 factors active, **Then** the reduction factor is 0.80 (not the P0 binary 0.50).

---

### Edge Cases

- **No risk score input found**: The system MUST exit with: "No risk score output found. Run `/risk-score` first."
- **Target codebase inaccessible**: The system MUST exit with: "Target codebase not accessible at `<path>`. Provide a valid project path via `--target`."
- **Partial analysis failures**: If analysis succeeds for 45/50 threats but fails for 5, the system MUST emit the 45 results with warnings for the 5 failures.
- **Empty target codebase**: If the directory contains no analyzable code files, classify all threats as "No Control Found" with a warning.
- **Architecture input missing**: Fall back to file-tree heuristics with a warning about lower accuracy.
- **File read budget exceeded**: Prioritize files within declared components; warn about skipped directories.
- **Context window overflow**: Split component batches into sub-batches by threat count; emit partial results per sub-batch.
- **Multiple controls for one threat**: Use the highest single control effectiveness (not additive).
- **Zero threats in input**: Exit with: "No scored threats found in input. Run `/threat-model` and `/risk-score` first."
- **Malformed risk score input**: Validate format before analysis; exit with descriptive parsing error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST parse scored threat findings from both `risk-scores.md` (markdown) and `risk-scores.sarif` (SARIF 2.1.0 JSON) formats interchangeably, extracting threat ID, component, threat description, composite score, severity band, dimensional scores, and governance fields.
- **FR-002**: System MUST validate that risk score input exists and is parseable before beginning analysis. If missing, exit with: "No risk score output found. Run `/risk-score` first."
- **FR-003**: System MUST scan the target codebase for security controls in 8 categories: Authentication, Input Validation, Rate Limiting, Encryption, Logging/Audit, CSRF Protection, CSP/Security Headers, and Access Control.
- **FR-004**: System MUST classify every scored threat as exactly one of: "Control Found," "Partial Control," or "No Control Found."
- **FR-005**: System MUST provide file:line evidence for every detected control, including the file path, line number, and a code snippet demonstrating the control.
- **FR-006**: System MUST map detected controls to the specific threats they mitigate using a canonical STRIDE-to-control-category mapping (Spoofing → Authentication/Access Control; Tampering → Input Validation; Repudiation → Logging/Audit; Information Disclosure → Encryption; Denial of Service → Rate Limiting; Elevation of Privilege → Access Control).
- **FR-007**: System MUST use component-based batching: group threats by target component and analyze all threats for a given component simultaneously, reading each component's files once.
- **FR-008**: When `architecture.md` is provided, use component-to-directory mapping for targeted file discovery. When absent, fall back to file-tree heuristics (`middleware/`, `auth/`, `security/`, `validators/`, `guards/`, `interceptors/`, `filters/`, `policies/`, `config/`) with a warning.
- **FR-009**: System MUST generate actionable recommendations for every threat classified as "No Control Found" or "Partial Control," including: what to implement/harden, where in the codebase, reference patterns, and effort estimate (Low / Medium / High).
- **FR-010**: Recommendations MUST be sorted by composite risk score descending (highest risk gaps first).
- **FR-011**: System MUST calculate residual risk per threat: `Residual = Inherent * (1 - Reduction Factor)` with P0 factors: Control Found = 0.50, Partial Control = 0.25, No Control Found = 0.00.
- **FR-012**: Residual risk scores MUST be clamped to [0.0, 10.0] and mapped to severity bands: Critical (>= 9.0), High (7.0-8.9), Medium (4.0-6.9), Low (< 4.0).
- **FR-013**: System MUST generate a coverage matrix with columns: Threat ID, Component, Threat, Inherent Score, Inherent Severity, Control Status, Residual Score, Residual Severity — plus summary statistics.
- **FR-014**: System MUST produce `compensating-controls.md` with: Executive Summary, Coverage Matrix, Control Details, Recommendations, Residual Risk Summary.
- **FR-015**: System MUST produce `compensating-controls.sarif` (SARIF 2.1.0) with tool `"tachi-control-analyzer"` v1.0, per-result properties (`security-severity`, `control-status`, `control-evidence`, `control-effectiveness`, `inherent-risk`, `residual-risk`, `recommendation`, `effort-estimate`), and preserved `findingId/v1` fingerprints.
- **FR-016**: System MUST accept `--target <path>` (codebase root, defaults to cwd) and `--output-dir <path>` (output location, defaults to same directory as risk score input).
- **FR-017**: System MUST handle partial failures gracefully: emit all successful results with warnings for failures.
- **FR-018**: System MUST respect a 200-file read budget. When exceeded, prioritize files within declared components and warn about skipped directories.
- **FR-019**: When multiple controls address the same threat, use the highest single effectiveness (not additive).
- **FR-020**: Control evidence MUST map to SARIF `relatedLocations` for viewer navigation.

### Key Entities

- **Scored Threat**: A threat identified by `/threat-model` and quantified by `/risk-score`. Has: ID, component, description, composite score, severity band, STRIDE/AI category. Primary input entity.
- **Detected Control**: A security mechanism found in the target codebase. Has: control category (1 of 8), file path, line number, code snippet, confidence level. Links to one or more Scored Threats.
- **Control Classification**: Assessment of a threat's mitigation status. One of: Control Found, Partial Control, No Control Found. Carries evidence and effectiveness rating (P1).
- **Recommendation**: Remediation suggestion for a gap. Has: target threat, current status, what to implement/harden, location, reference patterns, effort estimate, priority.
- **Residual Risk Score**: Adjusted risk after controls. Has: inherent score, reduction factor, residual score, residual severity band.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every scored threat receives exactly one classification with no unclassified threats.
- **SC-002**: Control detection accuracy >= 75% when validated against `examples/agentic-app/`.
- **SC-003**: Recommendation actionability >= 70% (specific enough to begin implementation without additional research).
- **SC-004**: Residual risk reasonableness >= 70% (matches intuitive post-control risk assessment).
- **SC-005**: `compensating-controls.sarif` validates against SARIF 2.1.0 schema in 100% of runs.
- **SC-006**: Finding fingerprints preserved for 100% of corresponding findings across the SARIF supersession chain.
- **SC-007**: Coverage statistics are arithmetically correct and match individual classifications.
- **SC-008**: Analysis of <= 50 threats completes in < 3 minutes; <= 200 threats in < 10 minutes.
- **SC-009**: Partial results always emitted for successful threats; zero silent data loss.

## Assumptions

- LLM-powered pattern recognition provides sufficiently accurate control detection for common security patterns.
- File:line evidence can be reliably collected for detected controls.
- Target codebase is accessible at the specified path.
- Binary reduction factors (0.50/0.25/0.00) approximate control effectiveness impact for Phase 1.
- Risk score input conforms to `schemas/risk-scoring.yaml`.
- Reduction factors are hardcoded in Phase 1; configurability deferred to Phase 2.
- AI-specific control patterns deferred to P1.

## Constraints

- No external vulnerability database dependencies.
- Static analysis only (no runtime behavior detection).
- Context window budget: ~80K tokens per pass; max 200 file reads.
- Files > 5,000 tokens truncated to security-relevant sections.
- Requires `/risk-score` output (Issue #35, delivered).
- CLI/agent command scope (not a web service).
- Monorepo: Phase 1 treats `--target` as analysis root.

## Dependencies

- `/risk-score` command (Issue #35, delivered) — provides scored threat input
- `/threat-model` command (existing) — upstream threat identification
- SARIF generation reference — schema guidance for output format
- Risk scoring schema (`schemas/risk-scoring.yaml`) — severity bands and score range
- Example architectures (`examples/agentic-app/`) — validation target

## Scope Boundaries

### In Scope (P0)
- `/compensating-controls` command with `--target` and `--output-dir` flags
- Risk score input parsing (markdown and SARIF)
- Codebase scanning for 8 control categories
- Per-threat classification with file:line evidence
- Control-to-threat mapping via STRIDE-to-control-category table
- Recommendations with effort estimates
- Residual risk with binary reduction factors
- Coverage matrix with summary statistics
- Dual output: `compensating-controls.md` + `compensating-controls.sarif`
- Component-based batching and context window management
- SARIF fingerprint preservation

### In Scope (P1)
- AI-specific control detection patterns
- Control effectiveness assessment (Strong / Moderate / Weak)
- 7-level reduction factor upgrade

### Out of Scope
- Custom control detection patterns (Phase 2)
- Per-framework calibration profiles (Phase 2)
- Configurable reduction factors (Phase 2)
- Historical coverage trending (Phase 2)
- Compliance framework mapping — separate feature
- Automated fix generation (Phase 3)
- Runtime control validation (Phase 3)
- Full monorepo analysis (Phase 2)
