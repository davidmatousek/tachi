# Research Summary: Deduplication & Risk Rating (Feature 010)

## Knowledge Base Findings
- No KB entries exist for deduplication, correlation, risk rating, or coverage matrix topics
- No prior bug fixes or patterns related to finding overlap or output deduplication

## Codebase Analysis

### Orchestrator (agents/orchestrator.md)
- **Phase 3** (lines 787–917): Collects findings from all agents, validates risk levels against OWASP 3×3 matrix, assembles 6 STRIDE tables and 2 AI tables
- **Phase 4** (lines 920–1048): Generates coverage matrix, risk summary, recommended actions, structural validation
- **Risk Level Validation** (lines 804–844): OWASP 3×3 lookup with correction protocol already implemented
- **Coverage Matrix** (lines 935–971): Currently counts raw findings per component×category cell. Three cell types: count (findings found), dash (analyzed, no findings), empty (not applicable)
- **No correlation or deduplication logic exists** anywhere in the orchestrator

### Finding IR Schema (schemas/finding.yaml)
- 10 fields: id, category, component, threat, likelihood, impact, risk_level, mitigation, references, dfd_element_type
- ID pattern: `{S|T|R|I|D|E|AG|LLM}-{N}`
- Category maps 1:1 to producing agent

### Output Schema (schemas/output.yaml)
- 7 required sections: System Overview, Trust Boundaries, STRIDE Tables (6), AI Threat Tables (2), Coverage Matrix, Risk Summary, Recommended Actions
- Coverage Matrix structure: `rows=components, columns=S/T/R/I/D/E/AG/LLM, cells=finding_count`
- Risk Summary levels: Critical, High, Medium, Low, Note with count + percentage

### Output Template (templates/threats.md)
- All 7 sections defined with examples
- OWASP 3×3 matrix already documented in Section 6 (Risk Summary) header
- Coverage Matrix (Section 5) uses raw finding counts

### Interface Contract (docs/INTERFACE-CONTRACT.md)
- Section 3 mentions: "Duplicate findings from overlapping dispatches are resolved at the coverage matrix level, not at dispatch time"
- This is a forward reference to the dedup feature — coverage matrix currently does NOT implement this resolution

### Example Outputs
- `examples/ascii-web-api/` and `examples/mermaid-agentic-app/` contain example inputs
- Example outputs show the 7-section structure with raw finding counts

### Patterns to Follow
- Risk validation correction protocol pattern (Phase 3): validate, correct, annotate — same pattern should apply to correlation
- Empty-table handling pattern: always include table headers even with zero data rows
- Self-check pattern: validate after each assembly step

## Architecture Constraints
- **Prompt-only implementation**: All logic expressed as orchestrator prompt instructions, not code
- **7-section schema**: Architect concern from PRD review — new Correlated Findings should be subsection 4a to preserve section numbering
- **Backward compatibility**: New sections are additive; existing schema contracts remain valid
- **Deterministic matching**: No fuzzy/NLP-based similarity; rules must be explicit and reproducible
- **Single-pass assembly**: Correlation runs once during Phase 3/4 assembly

## Industry Research
- **STRIDE-per-Element** is the established methodology; no standard exists for cross-category finding correlation
- **OWASP Risk Rating Methodology**: 3×3 simplified matrix (Likelihood × Impact → Risk Level) is the standard; tachi already implements this correctly
- **Deduplication in security tools**: Commercial tools (Checkmarx, Snyk) deduplicate by fingerprinting (file+line+rule); tachi's approach (component+category pair matching) is appropriate for threat modeling output where findings are descriptive, not code-location-specific
- **Correlation in SIEM/SOAR tools**: Security platforms correlate alerts by shared attributes (same host, same timeframe, related CVEs); tachi's approach of correlating by same component + overlapping threat category pairs follows this pattern

## Recommendations for Spec
- Place Correlated Findings as **Section 4a** (subsection between AI Tables and Coverage Matrix) to preserve existing 7-section numbering per Architect feedback
- Define correlation group entity (CG-N) as a new concept alongside findings — not a replacement
- Coverage matrix cell model needs unification: currently 3 cell types (count, dash, empty); add awareness of deduplicated vs. raw counts
- Correlation detection should be positioned in Phase 3 (after all agent findings collected, before coverage matrix generation in Phase 4)
- Ensure the Correlated Findings section always appears (even if empty: "No cross-agent correlations detected") for schema consistency
- The Risk Calibration Matrix subsection in FR-4 is already partially present in the template (Section 6 header); this feature documents it more prominently
