---
prd:
  number: "036"
  topic: compensating-controls
  created: 2026-03-27
  status: Approved
  type: feature
triad:
  pm_signoff: { agent: product-manager, date: 2026-03-27, status: APPROVED, notes: "Addressed architect and team-lead feedback; P0/P1 boundary fixed, context window management elevated, SARIF supersession chain defined, AI-specific controls deferred to P1" }
  architect_signoff: { agent: architect, date: 2026-03-27, status: APPROVED_WITH_CONCERNS, notes: "Feasible with caveats: SARIF supersession chain and context window management must be addressed before spec. 12 findings total (2 High, 6 Medium, 4 Low)" }
  techlead_signoff: { agent: team-lead, date: 2026-03-27, status: APPROVED_WITH_CONCERNS, notes: "9.0-11.5h across 7 waves (60% confidence); P0/P1 boundary inconsistency flagged; context window management critical; FR-2 is critical path at 3-4h" }
source:
  idea_id: 36
  story_id: null
---

# Compensating Controls — Product Requirements Document

**Status**: Draft
**Created**: 2026-03-27
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1

---

## Executive Summary

### The One-Liner
A `/compensating-controls` command that scans a target codebase against scored threats to detect existing security controls, recommend missing controls, assess control effectiveness, and calculate residual risk.

### Problem Statement
tachi's `/threat-model` identifies threats and `/risk-score` quantifies them, but neither answers the critical follow-up questions: "What controls already exist in my code?" and "What should I implement to close the gaps?" Developers and security engineers are left with a prioritized list of risks but no actionable bridge to remediation. They must manually audit their codebase to determine which threats are already mitigated, which are partially addressed, and which have no controls at all -- a time-consuming, error-prone process that often results in duplicated effort or missed gaps.

### Proposed Solution
A new `/compensating-controls` command that takes scored threats (from `/risk-score`) and a target codebase as input, then: (1) detects existing security controls by analyzing code for known patterns (auth middleware, input validation, rate limiting, encryption, logging, CSRF tokens, CSP headers), (2) maps detected controls to the specific threats they mitigate, (3) assesses control effectiveness beyond mere existence, (4) recommends specific compensating controls for unmitigated threats prioritized by risk score, and (5) calculates residual risk by adjusting inherent scores based on control effectiveness.

### Success Criteria
- Developers can see which threats in their codebase already have compensating controls with file:line evidence
- Security engineers receive actionable, prioritized recommendations for unmitigated threats
- Security managers get a coverage matrix showing control posture at a glance
- Residual risk scores reflect the actual risk after accounting for existing controls

### Timeline
- **Estimated effort**: 9.0-11.5 hours across 7 implementation waves (Team-Lead estimate, 60% confidence)
- **Next step**: `/aod.plan` after PRD approval

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](../01_Product_Vision/product-vision.md)

tachi's vision is to be "the default threat modeling toolkit for any team building agentic AI applications." Compensating controls analysis closes the loop from threat identification through risk quantification to actionable remediation -- completing the threat-to-action pipeline. This transforms tachi from a risk assessment tool into a remediation guidance tool, which is the capability most requested after threat identification.

### Core Value Reinforcement
tachi already identifies threats (STRIDE + AI agents) and quantifies them (/risk-score). Compensating controls analysis answers "what do I already have?" and "what do I still need?" -- the natural next question after "what are the risks and how severe are they?" This positions tachi as a complete threat modeling lifecycle tool rather than a point solution.

### Dependency Chain
This feature is the third link in tachi's threat analysis pipeline:
```
/threat-model (identifies threats)
  |
  v
/risk-score (quantifies risk) -- Issue #35, Delivered
  |
  v
/compensating-controls (detects controls, recommends fixes, calculates residual risk) -- This PRD
  |
  v
Compliance Mapping (future) -- maps controls to compliance frameworks
```

---

## Target Users & Personas

### Primary Persona: Developer
- **Role**: Developer building AI agent applications who runs tachi against their codebase
- **Experience**: Intermediate software engineering, basic security awareness
- **Goals**: Know which threats are already handled by their existing code and what they still need to implement
- **Pain Points**: After running `/risk-score`, they have a prioritized risk list but no visibility into which risks their existing code already addresses; manually searching for auth middleware, validation logic, and rate limiters across a codebase is tedious and error-prone
- **Why This Matters**: Pattern-based detection with file:line evidence shows exactly which controls exist and which gaps remain, letting developers focus effort on actual gaps rather than re-auditing known-good code

### Secondary Persona: Security Engineer
- **Role**: Hands-on security practitioner reviewing threat model output and guiding remediation
- **Experience**: Advanced security knowledge, familiar with CVSS and control frameworks
- **Goals**: Build a prioritized remediation roadmap with specific implementation recommendations
- **Pain Points**: Current pipeline stops at risk scores; translating scores into "what to build, where, and in what order" requires manual analysis; partial controls (e.g., rate limiter exists but with wrong thresholds) are the hardest to identify
- **Why This Matters**: Actionable recommendations with effort estimates and priority ordering enable a concrete remediation plan that can be handed to development teams

### Tertiary Persona: Security Manager
- **Role**: Manages security program, reports to CISO/leadership on security posture
- **Experience**: Broad security knowledge, focused on governance and metrics
- **Goals**: Assess overall control coverage, track residual risk, and report posture to leadership
- **Pain Points**: No way to answer "what percentage of our threats have controls?" or "what is our residual risk after accounting for existing controls?" without manual spreadsheet work
- **Why This Matters**: Coverage matrix with summary statistics (X% covered, Y% partial, Z% unmitigated) and residual risk totals enable executive-level posture reporting

### Quaternary Persona: Architect
- **Role**: System architect who designs security architecture for their application
- **Experience**: Deep system design knowledge, moderate security knowledge
- **Goals**: Validate that architectural security decisions (auth middleware, encryption layers, trust boundaries) are actually effective against identified threats
- **Pain Points**: Designed security controls during architecture but has no validation that they're correctly implemented, comprehensive in coverage, or adequate for the specific threat vectors identified
- **Why This Matters**: Control effectiveness assessment goes beyond "does it exist?" to "is it adequate?" -- exactly the validation architects need

---

## User Stories

### US-1: Codebase Control Detection
**When** I have scored threats from `/risk-score` and a target codebase to analyze,
**I want to** scan the codebase for existing security controls that address each identified threat,
**So I can** know which threats are already mitigated and focus effort on the actual gaps.

**Acceptance Criteria**:
- **Given** a target codebase with auth middleware, **when** the scan runs, **then** threats related to authentication bypass are classified as "Control Found" with file:line evidence linking to the middleware
- **Given** a target codebase with input validation on API endpoints, **when** the scan runs, **then** threats related to injection attacks are classified with evidence linking to the validation code
- **Given** a threat with no corresponding control in the codebase, **when** the scan runs, **then** it is classified as "No Control Found"
- **Given** a codebase with a rate limiter that only covers some endpoints, **when** the scan runs, **then** relevant threats are classified as "Partial Control" with evidence of what is covered and what is not
- **Given** the scan completes, **when** I view the output, **then** every threat is classified as one of: Control Found, Partial Control, or No Control Found

**Priority**: P0
**Effort**: XL

### US-2: Compensating Control Recommendations
**When** I have threats classified as "No Control Found" or "Partial Control",
**I want to** receive actionable compensating control recommendations for each gap, prioritized by risk score,
**So I can** build a remediation roadmap with specific implementation guidance.

**Acceptance Criteria**:
- **Given** a threat classified as "No Control Found", **when** recommendations are generated, **then** the recommendation includes: what to implement, where in the codebase to implement it, and reference patterns or libraries to use
- **Given** a threat classified as "Partial Control", **when** recommendations are generated, **then** the recommendation focuses on hardening the existing control (what's missing, how to extend it)
- **Given** multiple unmitigated threats, **when** recommendations are generated, **then** they are sorted by composite risk score descending (highest risk first)
- **Given** any recommendation, **when** I view effort estimates, **then** each has a Low/Medium/High effort rating

**Priority**: P0
**Effort**: L

### US-3: Control Coverage Matrix
**When** the compensating controls analysis is complete,
**I want to** see a coverage matrix showing control status across all threats,
**So I can** assess overall security posture at a glance.

**Acceptance Criteria**:
- **Given** all threats have been classified, **when** I view the coverage matrix, **then** it shows a table with columns: Threat ID, Component, Threat, Risk Score, Control Status (Found/Partial/Missing)
- **Given** the coverage matrix, **when** I view summary statistics, **then** it shows: X% covered (Control Found), Y% partial (Partial Control), Z% unmitigated (No Control Found)
- **Given** unmitigated threats, **when** I view the matrix, **then** they are visually distinguished by risk score severity (Critical/High/Medium/Low)

**Priority**: P0
**Effort**: M

### US-4: Residual Risk Calculation
**When** controls have been detected and effectiveness assessed,
**I want to** see residual risk calculated for each threat,
**So I can** understand the actual risk after accounting for existing controls.

**Acceptance Criteria**:
- **Given** a threat with "Control Found" and full effectiveness, **when** residual risk is calculated, **then** the residual score is significantly reduced from the inherent score (reduction factor based on effectiveness assessment)
- **Given** a threat with "Partial Control", **when** residual risk is calculated, **then** the residual score is partially reduced (proportional to assessed effectiveness)
- **Given** a threat with "No Control Found", **when** residual risk is calculated, **then** residual risk equals inherent risk (no reduction)
- **Given** all threats scored, **when** I view the summary, **then** it shows total inherent risk vs. total residual risk across all threats with the delta

**Priority**: P0
**Effort**: L

### US-5: Control Effectiveness Assessment
**When** a security control is detected in the codebase,
**I want to** know whether the control is adequate for the specific threat (not just that it exists),
**So I can** identify controls that need hardening vs. controls that are sufficient.

**Acceptance Criteria**:
- **Given** a rate limiter is detected, **when** effectiveness is assessed, **then** the assessment considers whether the limit thresholds are appropriate for the threat (e.g., DoS protection needs different limits than brute-force protection)
- **Given** auth middleware is detected, **when** effectiveness is assessed, **then** the assessment considers route coverage (does it protect all relevant endpoints?)
- **Given** input validation is detected, **when** effectiveness is assessed, **then** the assessment considers whether it covers the specific injection vector identified in the threat
- **Given** encryption is detected, **when** effectiveness is assessed, **then** the assessment considers algorithm and key length currency
- **Given** effectiveness assessment is complete, **when** I view the result, **then** each control is rated: Strong (fully effective), Moderate (partially effective), or Weak (exists but inadequate)

**Priority**: P1
**Effort**: L

---

## Functional Requirements

### Core Capabilities

#### FR-1: Risk Score Parsing
**Description**: Parse scored threat findings from `/risk-score` output files.

**Inputs**: `risk-scores.md` (markdown format) or `risk-scores.sarif` (SARIF 2.1.0 JSON)
**Processing**: Extract threat ID, component, threat description, composite score, severity band, dimensional scores (CVSS, exploitability, scalability, reachability), and governance fields
**Outputs**: Structured scored threat list ready for control analysis

**Business Rules**:
- Must support both input formats interchangeably
- Must preserve all original threat and scoring metadata through the control analysis pipeline
- Must validate input exists and is parseable before analysis begins
- If input is missing, exit with clear error: "No risk score output found. Run `/risk-score` first."

#### FR-2: Codebase Control Detection
**Description**: Scan the target codebase for known security control patterns and map them to threats.

**Detection Categories**:
| Control Category | Patterns to Detect | Maps to Threat Types |
|-----------------|-------------------|---------------------|
| Authentication | Auth middleware, JWT verification, OAuth handlers, session management | Spoofing, unauthorized access |
| Input Validation | Schema validation, sanitization functions, parameterized queries, type checking | Injection (SQL, XSS, command), tampering |
| Rate Limiting | Rate limiter middleware, throttling configuration, circuit breakers | Denial of service, brute force |
| Encryption | TLS/SSL configuration, encryption functions, key management, hashing | Information disclosure, data exposure |
| Logging/Audit | Structured logging, audit trail, event tracking | Repudiation, insufficient monitoring |
| CSRF Protection | CSRF tokens, SameSite cookies, origin validation | Cross-site request forgery |
| CSP/Security Headers | Content-Security-Policy, X-Frame-Options, HSTS | XSS, clickjacking |
| Access Control | RBAC/ABAC implementations, permission checks, role guards | Privilege escalation, unauthorized access |
**Note**: AI-specific control patterns (prompt sanitization, output filtering, tool call validation, agent boundary enforcement) are deferred to P1 -- these patterns are less standardized than the 8 categories above, and deferring reduces P0 scope by ~15% with minimal value loss.

**Codebase Discovery Strategy**:
- When `architecture.md` is provided: Use component-to-directory mapping from the architecture diagram to target file discovery to relevant directories per component. This is the recommended mode for accurate analysis.
- When `architecture.md` is absent: Fall back to project-wide file tree listing (`--target` path is the analysis root), then use file naming heuristics (e.g., `middleware/`, `auth/`, `validators/`, `security/`) to prioritize reads. Accuracy will be lower; emit a warning.
- File selection budget: Maximum 200 file reads per analysis run. If the codebase exceeds this, prioritize files within declared components and emit a warning listing skipped directories.
- Monorepo support: Phase 1 treats the `--target` path as the analysis root. Users analyzing a monorepo should point `--target` at the relevant subdirectory. Full cross-directory monorepo analysis is Phase 2.

**Processing**:
- Static analysis: Search for import patterns, middleware registration, decorator usage, configuration files
- Semantic analysis: Agent reasons about whether detected code actually mitigates the mapped threat (not just pattern existence)
- Evidence collection: Record file path, line number, code snippet, and confidence level for each detected control
- **Component-based batching**: Group threats by target component and analyze all threats for a given component simultaneously. This amortizes file discovery costs -- reading a component's files once and assessing all relevant threats against those files rather than re-reading per threat.

**Output**: Per-threat classification (Control Found / Partial Control / No Control Found) with evidence

#### FR-3: Control Effectiveness Assessment
**Description**: Evaluate whether detected controls are adequate for the specific threats they address, not just whether they exist.

**Assessment Dimensions**:
| Dimension | What It Checks | Example |
|-----------|---------------|---------|
| Coverage | Does the control protect all relevant paths/endpoints? | Auth middleware covers 8/12 routes |
| Configuration | Are thresholds, limits, and settings appropriate? | Rate limiter set to 1000 req/s (too permissive for brute-force) |
| Currency | Are algorithms, protocols, and libraries up to date? | Using SHA-256 (current) vs. MD5 (deprecated) |
| Completeness | Does the control address the full attack vector? | Validates SQL injection but not NoSQL injection |

**Output Per Control**:
- Effectiveness rating: Strong / Moderate / Weak
- Reasoning: Explanation of assessment
- Gaps identified: What's missing or inadequate

#### FR-4: Compensating Control Recommendations
**Description**: Generate actionable implementation recommendations for unmitigated and partially mitigated threats.

**Recommendation Structure Per Threat**:
| Field | Content |
|-------|---------|
| Threat ID | Reference to the scored threat |
| Current Status | No Control Found / Partial Control |
| Recommendation | Specific control to implement or harden |
| Implementation Location | Where in the codebase (file/module suggestion) |
| Reference Patterns | Libraries, frameworks, or code patterns to use |
| Effort Estimate | Low / Medium / High |
| Priority | Inherited from composite risk score |

**Business Rules**:
- Recommendations sorted by composite risk score descending (highest risk gaps first)
- "Partial Control" recommendations focus on hardening existing controls, not replacing them
- "No Control Found" recommendations include both what to implement and where
- Effort estimates based on control complexity: Low (configuration change), Medium (new middleware/function), High (architectural change)

#### FR-5: Residual Risk Calculation
**Description**: Calculate residual risk by adjusting inherent risk scores based on control effectiveness.

**Residual Risk Formula**:
```
Residual Risk = Inherent Risk * (1 - Effectiveness Reduction Factor)
```

**P0 Reduction Factors** (binary, based on control status only):
| Control Status | Reduction Factor | Rationale |
|---------------|-----------------|-----------|
| Control Found | 0.50 (50% risk reduction) | Control exists and addresses the threat |
| Partial Control | 0.25 (25% risk reduction) | Control exists but coverage is incomplete |
| No Control Found | 0.00 (no risk reduction) | No control detected |

**P1 Reduction Factors** (effectiveness-aware, requires US-5 effectiveness assessment):
| Control Status | Effectiveness Rating | Reduction Factor |
|---------------|---------------------|-----------------|
| Control Found | Strong | 0.80 (80% risk reduction) |
| Control Found | Moderate | 0.50 (50% risk reduction) |
| Control Found | Weak | 0.20 (20% risk reduction) |
| Partial Control | Strong | 0.50 (50% risk reduction) |
| Partial Control | Moderate | 0.30 (30% risk reduction) |
| Partial Control | Weak | 0.10 (10% risk reduction) |
| No Control Found | N/A | 0.00 (no risk reduction) |

**Phase strategy**: P0 uses binary factors (no dependency on effectiveness assessment). When P1 effectiveness assessment (US-5) is implemented, reduction factors upgrade to the 7-level matrix automatically.

**Residual Severity Band Mapping**: Residual scores map to the same severity bands defined in `schemas/risk-scoring.yaml` (Critical >= 9.0, High 7.0-8.9, Medium 4.0-6.9, Low < 4.0). Both inherent and residual severity bands are displayed in the coverage matrix.

**Output**:
- Per-threat: inherent score, reduction factor, residual score, residual severity band
- Summary: total inherent risk, total residual risk, overall risk reduction percentage

#### FR-6: Output Generation
**Description**: Produce control analysis output in dual formats.

**compensating-controls.md**: Human-readable markdown with:
- Executive summary (total threats analyzed, control coverage statistics, overall risk reduction)
- Coverage matrix: Threat ID x Control Status x Risk Score x Residual Risk
- Control details: Per-control evidence with file:line references and effectiveness rating
- Recommendations: Prioritized list for unmitigated/partial threats with effort estimates
- Residual risk summary: Inherent vs. residual totals with delta

**compensating-controls.sarif**: Machine-readable SARIF 2.1.0 with:
- `tool.driver.name`: `"tachi-control-analyzer"` with schema version `"1.0"`
- `properties.security-severity` set to residual risk score (string format, e.g., "4.2") -- reflects post-control risk posture
- `properties.control-status` set to "found" / "partial" / "missing"
- `properties.control-evidence` array with structured elements: `[{"file": "path", "line": N, "snippet": "code"}]`
- `properties.control-effectiveness` set to "strong" / "moderate" / "weak" / "none"
- `properties.inherent-risk` with original composite score from `/risk-score`
- `properties.residual-risk` with calculated residual score
- `properties.recommendation` with remediation guidance
- `properties.effort-estimate` with Low/Medium/High rating
- `partialFingerprints.findingId/v1` preserved from source `risk-scores.sarif` for alert continuity
- Results sorted by residual risk descending

**SARIF supersession chain**: `compensating-controls.sarif` supersedes `risk-scores.sarif`, which supersedes `threats.sarif`. Users should upload `compensating-controls.sarif` (not all three files) to GitHub Code Scanning to avoid duplicate alerts. Finding fingerprints (`findingId/v1`) are preserved through the entire chain for alert tracking continuity. The `security-severity` property reflects residual risk (post-control), providing the most actionable severity for triage.

**Output location**: Output files are written to the same directory as the `/risk-score` output, alongside `risk-scores.md` and `risk-scores.sarif`.

### Interface Contract

**Command**: `/compensating-controls`

**Input** (required):
- `risk-scores.md` OR `risk-scores.sarif` -- from `/risk-score` output (auto-detected from input directory or cwd)
- `--target <path>` -- root directory of the target codebase to analyze (defaults to cwd if omitted)

**Input** (optional):
- `architecture.md` -- for component-to-code mapping context (recommended for accuracy)
- `--output-dir <path>` -- output directory override (defaults to same directory as input, consistent with `/threat-model` and `/risk-score`)

**Output** (produces):
- `compensating-controls.md` -- coverage matrix + control details + recommendations + residual risk
- `compensating-controls.sarif` -- SARIF 2.1.0 with control mappings and residual risk

**Dependencies**:
- Requires `/risk-score` output to exist (Issue #35)
- Requires target codebase access for control detection
- Architecture input is optional but recommended for component-to-code mapping accuracy

---

## Non-Functional Requirements

### Performance
- Control analysis for a codebase with 50 threats: < 3 minutes
- Control analysis for a codebase with 200 threats: < 10 minutes
- Component-based batching: Threats targeting the same component are analyzed together to amortize file reads
- No external vulnerability database lookups required -- all analysis via LLM-powered code analysis (LLM API calls are inherent to tachi's agent architecture)

### Context Window Management (Architectural Requirement)
This feature reads arbitrary user codebases, making context window pressure categorically different from `/risk-score` (which processes structured tachi output only). Context management is a first-class architectural constraint, not a performance optimization:
- **Token budget**: Maximum ~80,000 tokens per analysis pass for codebase content
- **Batching strategy**: The command layer (not the agent) groups threats by component and dispatches per-component analysis batches. The command merges results from all batches into the final output.
- **File selection**: Maximum 200 file reads per analysis run. Files selected via architecture.md component mapping (preferred) or file-tree heuristics (fallback).
- **Large file handling**: Files exceeding 5,000 tokens are truncated to relevant sections (imports, middleware registration, security-relevant functions) with a warning.
- **Graceful degradation**: If a batch exceeds context limits, split into sub-batches by threat count. Partial results are always emitted; never fail silently.

### Reliability
- Graceful handling of unreadable source files (skip with warning, continue analysis)
- Graceful handling of malformed risk score input (validate and report errors before analysis begins)
- If target codebase is not accessible, exit with clear error: "Target codebase not accessible. Provide a valid project path."
- Partial results are valuable: if analysis completes for 45/50 threats, output the 45 results with warnings for the 5 failures

### Compatibility
- SARIF output validates against SARIF 2.1.0 JSON schema
- SARIF compatible with GitHub Code Scanning upload
- Finding fingerprints preserved from upstream `risk-scores.sarif` for alert tracking continuity
- Control status classifications consistent with industry terminology (NIST, ISO 27001)

### Extensibility
- Control detection patterns extensible (future: user-defined control patterns via configuration)
- Effectiveness assessment criteria extensible (future: per-framework calibration profiles)
- Reduction factors configurable (future: per-organization risk appetite settings)

---

## Success Metrics

### Primary Metrics
- **Control Detection Accuracy**: Detected controls match manual audit findings in >= 75% of cases (validated against example codebase)
- **Recommendation Actionability**: User validates that recommendations are specific enough to implement without additional research in >= 70% of cases
- **Residual Risk Reasonableness**: User validates that residual risk scores reflect their intuitive assessment of actual risk after controls in >= 70% of cases

### Secondary Metrics
- **Coverage Statistics Accuracy**: Coverage percentages (found/partial/missing) match manual assessment within +/- 10% tolerance
- **Format Compliance**: `compensating-controls.sarif` validates against SARIF 2.1.0 schema in 100% of runs
- **Pipeline Adoption**: `/compensating-controls` is run after >= 30% of `/risk-score` invocations (measured by example usage patterns)

---

## Scope & Boundaries

### In Scope (Phase 1)

**Must Have (P0)**:
- `/compensating-controls` command parsing `risk-scores.md` and `risk-scores.sarif`
- Codebase scanning for 8 common security control categories (auth, validation, rate limiting, encryption, logging, CSRF, CSP/security headers, access control)
- Per-threat classification: Control Found / Partial Control / No Control Found
- File:line evidence for detected controls
- Control-to-threat mapping
- Actionable recommendations for unmitigated/partial threats with effort estimates
- Residual risk calculation per threat using binary reduction factors (Found=0.50, Partial=0.25, Missing=0.00)
- Coverage matrix with summary statistics
- `compensating-controls.md` output with full details
- `compensating-controls.sarif` output validating against SARIF 2.1.0
- Component-based batching and context window management

**Should Have (P1)**:
- AI-specific control detection patterns (prompt sanitization, output filtering, tool call validation, agent boundary enforcement)
- Control effectiveness assessment (Strong/Moderate/Weak) with 7-level reduction factor upgrade
- Recommendations sorted by composite risk score
- Executive summary with overall risk reduction percentage
- Example output generated against `examples/agentic-app/`

### Out of Scope (Future Phases)

**Won't Have**:
- Custom control detection patterns via configuration (Phase 2)
- Per-framework calibration profiles for effectiveness assessment (Phase 2)
- Historical control coverage trending across multiple runs (Phase 2)
- Compliance framework mapping (NIST 800-53, ISO 27001, SOC 2) -- separate feature (Issue C)
- Automated fix generation / pull request creation (Phase 3)
- Runtime control validation (dynamic analysis) (Phase 3)

### Assumptions
- Static code analysis via LLM-powered pattern recognition provides sufficiently accurate control detection for common security patterns
- File:line evidence can be reliably collected for detected controls
- Reduction factors provide a reasonable approximation of control effectiveness impact on risk
- Target codebase is accessible to tachi's agent for analysis

### Constraints
- **No external vulnerability database dependencies**: All analysis performed via LLM code analysis; no CVE/NVD lookups required (LLM API is inherent to tachi)
- **tachi scope**: This is a CLI/agent command, not a web service
- **Dependency**: Requires `/risk-score` to have been run first (Issue #35)
- **Static analysis only**: Phase 1 detects controls through code pattern analysis, not runtime behavior

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: Control detection accuracy (false positives/negatives)
- **Likelihood**: High
- **Impact**: High
- **Mitigation**: Start with well-defined detection patterns for the most common control categories (auth, validation, rate limiting); use LLM semantic analysis to reduce false positives (e.g., distinguish between a rate limiter and a counter); validate against `examples/agentic-app/`
- **Contingency**: Accept lower accuracy for uncommon patterns in Phase 1; iterate based on user feedback; allow users to override classifications in Phase 2

**Risk 2**: Control-to-threat mapping accuracy
- **Likelihood**: Medium
- **Impact**: High
- **Mitigation**: Use threat category (STRIDE/AI type) to narrow mapping scope; leverage architecture.md for component-to-code relationships; include confidence levels in mappings
- **Contingency**: Present low-confidence mappings with explicit uncertainty indicators for user review

**Risk 3**: Context window pressure from codebase analysis
- **Likelihood**: High
- **Impact**: High
- **Mitigation**: Elevated to first-class architectural requirement (see Non-Functional Requirements > Context Window Management). Component-based batching, ~80K token budget per pass, max 200 file reads, large file truncation. Command layer handles batching/merging; agent processes one batch at a time.
- **Contingency**: Split batches into sub-batches by threat count if limits exceeded; partial results always emitted

**Risk 4**: Effectiveness assessment subjectivity
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**: Define clear rubrics for each effectiveness dimension (coverage, configuration, currency, completeness); use structured LLM prompts with specific assessment criteria
- **Contingency**: Default to binary (exists/missing) classification if effectiveness assessment proves unreliable; defer nuanced assessment to Phase 2

### Dependencies

**Internal Dependencies**:
- `/risk-score` command (Issue #35, delivered) -- provides input
- `/threat-model` command (existing, delivered) -- upstream threat identification
- SARIF generation reference -- schema guidance for output format
- Example architectures (`examples/`) -- validation targets

**Dependency Graph**:
```
/threat-model (existing)
  |
  v
/risk-score (delivered, Issue #35)
  |
  v
/compensating-controls (this feature, Issue #36)
  |
  v
Compliance Mapping (future, Issue C)
  |
  v
Risk Register (future, Issue E)
```

---

## Open Questions

- [x] Should the command accept a project path argument or detect the target codebase from the current working directory? - architect - 2026-03-27 - **Resolved**: Accept optional `--target <path>` flag (defaults to cwd). Risk score input auto-detected from input directory or cwd. Separate `--target` flag allows the codebase and risk-score output to be in different directories.
- [x] How should the command handle monorepo structures where components span multiple directories? - architect - 2026-03-27 - **Resolved**: Phase 1 treats `--target` path as the analysis root. Monorepo users point the flag at the relevant subdirectory. Full cross-directory monorepo analysis is Phase 2.
- [ ] Should reduction factors be configurable in Phase 1 or hardcoded with Phase 2 configurability? - product-manager - TBD - Deferrable to spec (implied by Extensibility section: hardcode in Phase 1, consistent with `/risk-score` precedent)
- [ ] What is the minimum set of AI-specific control patterns to detect in Phase 1? - product-manager - TBD - Deferrable to spec (AI-specific patterns moved to P1; pattern catalog defined during spec creation)

---

## References

### Product Documentation
- Product Vision: [product-vision.md](../01_Product_Vision/product-vision.md)
- GitHub Issue: [#36 - Compensating Controls](https://github.com/davidmatousek/tachi/issues/36)

### Technical Documentation
- Constitution: [constitution.md](../../.aod/memory/constitution.md)
- SARIF Reference: `adapters/claude-code/agents/references/sarif-generation.md`
- ADR-013: SARIF Output Format Adoption

### Related PRDs
- PRD-035: [Quantitative Risk Scoring](035-quantitative-risk-scoring-2026-03-27.md) -- direct upstream dependency; provides scored threat input
- PRD-010: [Deduplication & Risk Rating](010-deduplication-risk-rating-2026-03-22.md) -- established qualitative rating this pipeline enhances
- PRD-012: [SARIF Output Generation](012-sarif-output-generation-2026-03-22.md) -- SARIF format this feature extends

---

## Approval & Sign-Off

| Role | Agent | Status | Date | Comments |
|------|-------|--------|------|----------|
| Product Manager | product-manager | APPROVED | 2026-03-27 | Addressed reviewer feedback; P0/P1 boundary fixed, context window management elevated |
| Architect | architect | APPROVED_WITH_CONCERNS | 2026-03-27 | SARIF supersession chain + context window management are critical for spec |
| Team Lead | team-lead | APPROVED_WITH_CONCERNS | 2026-03-27 | 9.0-11.5h estimate; FR-2 is critical path; resolve remaining questions during spec |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-27 | product-manager | Initial PRD from GitHub Issue #36 |
| 1.1 | 2026-03-27 | product-manager | Addressed Architect + Team-Lead review: fixed P0/P1 boundary (binary reduction factors for P0), elevated context window management to architectural requirement, added SARIF supersession chain and tool metadata, moved AI-specific controls to P1, added codebase discovery strategy and component-based batching, resolved 2 open questions, added --target and --output-dir flags, added timeline estimate |
