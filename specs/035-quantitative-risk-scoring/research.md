# Research Summary: Quantitative Risk Scoring

## Knowledge Base Findings
- No existing KB patterns found (KB is empty)
- No prior bug fixes or lessons learned related to risk scoring

## Codebase Analysis

### Similar Features
- **Threat-Model Command** (`.claude/commands/threat-model.md`): Primary pattern to follow for command structure — flag parsing, validation, timestamped output directories, summary reporting
- **SARIF Generation** (`adapters/claude-code/agents/references/sarif-generation.md`): Existing severity mapping table (Critical=9.0, High=8.0, Medium=5.0, Low=2.0), fingerprint generation (SHA-256 of ruleId + component), dual-location strategy
- **Finding IR Schema** (`schemas/finding.yaml`): Current finding structure with id, category, component, threat, likelihood, impact, risk_level, mitigation, references, dfd_element_type
- **Output Schema** (`schemas/output.yaml`): 7-section output format, CVSS severity mapping bands already defined (Critical 9.0-10.0, High 7.0-8.9, Medium 4.0-6.9, Low 0.1-3.9)
- **Deduplication & Risk Rating** (PRD-010): Cross-agent correlation in Section 4a, OWASP 3x3 matrix — `/risk-score` consumes deduplicated output, no re-deduplication needed
- **Threat Report Agent** (`.claude/agents/tachi/threat-report.md`): Remediation Roadmap pattern sorted by risk level, executive summary with severity distribution

### Patterns to Follow
- Command-per-workflow pattern with flag parsing and validation
- Dual-format output (markdown + SARIF) from same IR data
- Finding template with field-by-field guidance in agent definitions
- Deterministic fingerprints for GitHub Code Scanning deduplication
- Trust zone table in threats.md Section 2 as primary reachability source

### Naming Conventions
- Commands: kebab-case (`/risk-score`)
- Agent files: kebab-case with `tachi-` prefix (e.g., `tachi/risk-scorer.md`)
- Output files: plural kebab-case (`risk-scores.md`, `risk-scores.sarif`)
- IR/schema fields: snake_case (`composite_score`, `risk_owner`)
- SARIF properties: kebab-case (`security-severity`, `cvss-base`)

### Utilities to Reuse
- SARIF generation reference for property bag structure and fingerprinting
- Orchestrator Phase 3-4 assembly patterns for finding collection and validation
- Trust zone extraction from threats.md Section 2

## Architecture Constraints
- **No external APIs**: All scoring via LLM analysis (no CVE/NVD lookups)
- **Finding ID immutability**: Preserve S-N/T-N identifiers from threat model
- **Correlation preservation**: Score primaries from Section 4a; peers inherit
- **SARIF 2.1.0 compliance**: Validate schema, update security-severity dynamically per finding
- **Fingerprint stability**: Preserve `primaryLocationLineHash` + `findingId/v1` for GitHub dedup
- **Dual-format parity**: risk-scores.md and risk-scores.sarif must be synchronized
- **Output co-location**: Write alongside threats.md/threats.sarif in same directory
- **Backward compatibility**: Composite scores map to existing Critical/High/Medium/Low bands
- **CVSS 3.1 primary target** (ADR-013/PRD decision): Schema extensible for 4.0

## Industry Research

### CVSS 3.1 Automation
- Map STRIDE categories to default CVSS vectors as baseline, refine per-threat via LLM
- Store full CVSS vector string alongside numeric score for auditability
- Scope (S) is most subjective metric — provide explicit guidance for LLM mapping
- AI-specific threats (agentic, LLM) have no standard CVSS mappings — define tachi-specific defaults

### Multi-Dimensional Risk Scoring
- Weighted linear composite (PRD Pattern A) is well-established and transparent
- Consider floor/ceiling rules: if any dimension > 9.5, composite minimum = 7.0 (High)
- Test against examples/agentic-app/ output to verify score distribution avoids clustering

### SARIF Integration
- `security-severity` MUST be a numeric string (e.g., "7.8", not 7.8)
- Range: 0.1-10.0 (0.0 causes GitHub to hide the finding)
- Result-level property takes precedence over rule-level for GitHub display
- Rule-level security-severity should reflect max composite among that rule's findings

### Exploitability Frameworks
- Align with OWASP Likelihood Factors: discovery ease, exploit ease, awareness, detection
- EPSS requires CVE IDs — not applicable Phase 1 (note for Phase 2)
- AI-specific: prompt injection = trivially exploitable; model poisoning = high skill required

### Reachability Analysis
- Map trust zone levels to base reachability scores (Untrusted=9.0, Semi-Trusted=5.0, Trusted=2.0)
- Adjust with architecture.md supplementary data (auth barriers -1.5, network segmentation -1.0)
- Zone name fuzzy matching needed for non-standard naming
- Default 5.0 when architecture.md missing (per PRD)

## Recommendations for Spec
- Define tachi-specific CVSS 3.1 default vectors for all 8 threat categories (6 STRIDE + 2 AI)
- Specify scoring agent as single-pass: Parse → Score (4 dimensions) → Generate output
- Mandate CVSS vector string storage alongside numeric score for auditability
- Include floor/ceiling rule consideration for extreme single-dimension scores
- Specify trust zone-to-reachability mapping table with fuzzy matching for zone names
- Address context window risk: structured output format, potential batching for >100 findings
- Ensure risk-scores.sarif supersedes threats.sarif for GitHub upload (same fingerprints)
- Include reproducibility validation: same input within +/- 0.5 per dimension at temperature 0
