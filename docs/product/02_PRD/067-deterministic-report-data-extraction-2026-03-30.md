---
prd:
  number: "067"
  topic: deterministic-report-data-extraction
  created: 2026-03-30
  status: Approved
  type: feature
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-30
    status: APPROVED
    notes: "PRD authored by PM. P0 bug fix replacing non-deterministic LLM parsing with deterministic Python script. Root cause well-evidenced with 4-report comparison data. All reviewer concerns are spec-level items."
  architect_signoff:
    agent: architect
    date: 2026-03-30
    status: APPROVED_WITH_CONCERNS
    notes: "Architecturally sound. 5 items for spec: (1) extract report-data.typ contract into machine-readable schema, (2) specify exact Python invocation pattern and script location, (3) resolve total-findings dedup vs raw count for all tiers, (4) handle Note severity level in validation rule, (5) enumerate markdown parsing edge cases (bold markers, code-fenced frontmatter, unicode, truncation markers) and create Tier 1 test fixture."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-30
    status: APPROVED_WITH_CONCERNS
    notes: "3-5 sessions realistic (not single-phase). Recommends 3-wave strategy: Wave 1 (core parsing + Tier 2 with real test data), Wave 2 (Tier 1 + Tier 3 paths), Wave 3 (agent rewrite + integration). Highest risk: no Tier 1 test dataset exists — needs resolution in spec. 4 clarifications needed: OpenClaw dataset existence, script location, partial-parse exit codes, risk-scores.md non-standard frontmatter format."
source:
  idea_id: 67
  story_id: null
---

# Deterministic Report Data Extraction — Product Requirements Document

**Status**: Approved
**Created**: 2026-03-30
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P0 (Critical)
**Source**: GitHub Issue #67

---

## Executive Summary

### The One-Liner
Replace the LLM-based data extraction in the report-assembler agent with a deterministic parsing script so that `/security-report` produces identical output from identical input every time.

### Problem Statement
Running `/security-report` four times on the exact same input artifacts (threats.md, risk-scores.md, compensating-controls.md, threat-report.md, infographic JPEGs) produced dramatically different PDF reports. Severity counts varied between 0 and 20 Critical findings, data flow counts changed between 20 and 36, recommendation formatting was inconsistent, and the overall risk level fluctuated between HIGH and CRITICAL — all from the same source files.

**Evidence (4 reports from identical OpenClaw data)**:

| Metric | Report 1 | Report 2 | Report 3 | Report 4 |
|--------|:--------:|:--------:|:--------:|:--------:|
| Overall Risk Level | HIGH | HIGH | CRITICAL | CRITICAL |
| Critical findings | 0 | 0 | 15 | 20 |
| High findings | 17 | 4 | 26 | 26 |
| Medium findings | 47 | 36 | 14 | 14 |
| Low findings | 0 | 24 | 3 | 3 |
| Total findings | 64 | 64 | 63 | 63 |
| Data Flows extracted | 36 | 36 | 36 | 20 |

**Root Cause (5 Whys)**: The report-assembler agent's Steps 2–3 (Data Extraction and Typst Data Generation) are executed by an LLM parsing natural language instructions. The LLM inconsistently selects between three overlapping severity source tables, produces variable-length recommendation text, and extracts different data flow counts from the same markdown — because structured parsing of well-defined tables is a deterministic task being performed by a non-deterministic system.

### Proposed Solution
Create a deterministic parsing script (Python) that replaces Steps 2–3 of the report-assembler agent. The script reads markdown artifacts using regex and line parsing, applies tier-selection logic programmatically, extracts all structured data with consistent formatting, validates internal consistency, and writes `report-data.typ`. The LLM agent is reduced to orchestration only: detect artifacts, invoke the script, invoke Typst.

### Success Criteria
- Running `/security-report` twice on identical input produces byte-identical `report-data.typ`
- Running `/security-report` twice on identical input produces byte-identical PDF output
- Severity counts are validated: critical + high + medium + low == total
- Data flow count matches source file
- Tested against both OpenClaw and agentic-app example datasets

### Timeline
Single-phase implementation. The script replaces existing natural language instructions with equivalent programmatic logic — no new data sources, no new page templates, no Typst template changes.

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](../01_Product_Vision/product-vision.md)

tachi's mission is to be the default threat modeling toolkit for agentic AI applications. A threat modeling toolkit that produces different reports from the same data on every run cannot be trusted for compliance, audit trails, or executive communication. Deterministic output is a prerequisite for professional-grade tooling — without it, users cannot rely on the numbers in the report.

### Roadmap Fit
This is a P0 bug fix for the delivered `/security-report` capability (PRD-054, PRD-060). It blocks adoption of the PDF report for any use case requiring reproducibility: CI/CD artifact generation, compliance documentation, multi-stakeholder review.

---

## Target Users & Personas

### Primary Persona: Security Engineer
- **Role**: Runs threat models and generates reports for team review
- **Pain Point**: Generated a report showing 0 Critical findings, sent it to leadership, then regenerated and got 20 Critical findings from the same data — destroying trust in the tool
- **Need**: Identical inputs must produce identical outputs, every time

### Secondary Persona: CISO / Security Manager
- **Role**: Reviews and distributes security assessment reports
- **Pain Point**: Cannot use tachi reports for compliance or audit evidence because the same data produces different severity distributions
- **Need**: A report that accurately reflects the underlying threat model data and can be regenerated reproducibly

---

## User Stories

### US-067-1: Reproducible Report Generation
**When** I run `/security-report` on a directory containing threat model artifacts,
**I want to** get the same PDF output every time I run it on the same inputs,
**So I can** trust the report numbers and use it for compliance and executive communication.

**Acceptance Criteria**:
- **Given** a directory with unchanged threat model artifacts, **when** I run `/security-report` twice, **then** both runs produce identical `report-data.typ` files
- **Given** identical `report-data.typ` files, **when** Typst compiles them, **then** both PDFs are byte-identical
- **Given** a Tier 1 scenario (compensating-controls.md exists), **when** the script extracts severity counts, **then** it uses the residual severity from compensating-controls.md Section 2

### US-067-2: Validated Severity Counts
**When** the parsing script extracts severity counts from markdown artifacts,
**I want to** be confident the counts are internally consistent,
**So I can** trust the numbers on the cover page and executive summary.

**Acceptance Criteria**:
- **Given** extracted severity counts, **when** validation runs, **then** critical + high + medium + low == total
- **Given** a Tier 2 scenario (risk-scores.md exists, no compensating-controls.md), **when** the script extracts counts, **then** it uses risk-scores.md Section 1 severity distribution
- **Given** a Tier 3 scenario (only threats.md), **when** the script extracts counts, **then** it uses threats.md Section 6 Risk Summary

### US-067-3: Deterministic Data Flow Extraction
**When** the parsing script extracts scope data from threats.md,
**I want to** get the same component count and data flow count every time,
**So I can** trust the scope page accurately reflects the system architecture.

**Acceptance Criteria**:
- **Given** threats.md with N data flows in Section 1, **when** the script extracts data flows, **then** exactly N data flows appear in `report-data.typ`
- **Given** threats.md with M components in Section 1, **when** the script extracts components, **then** exactly M components appear in `report-data.typ`

### US-067-4: Consistent Recommendation Formatting
**When** the parsing script extracts findings with recommendations,
**I want to** get identically formatted recommendation text every time,
**So I can** the findings table has uniform presentation across all rows.

**Acceptance Criteria**:
- **Given** a Tier 1 finding with a recommendation in compensating-controls.md, **when** the script extracts it, **then** the recommendation text is preserved verbatim from the source
- **Given** findings across all severity levels, **when** the script formats them, **then** all recommendations use consistent formatting (no variable-length paraphrasing)

---

## Functional Requirements

### FR-1: Deterministic Parsing Script

**Description**: A Python script that reads tachi pipeline markdown artifacts and writes a `report-data.typ` file with all Typst variable bindings.

**Inputs**:
- `--target-dir`: Directory containing markdown artifacts and images
- `--output`: Path for the generated `report-data.typ` file
- `--title`: Optional title override (replaces auto-detected project name)
- `--template-dir`: Path to `templates/tachi/security-report/` (for image path calculation)

**Processing**:
1. Detect artifacts and determine tier (same logic as agent Step 1)
2. Parse each artifact using regex/line parsing (replaces agent Step 2)
3. Apply tier-selection logic programmatically for severity source
4. Extract all structured data: frontmatter, severity counts, findings, scope, coverage, remediation
5. Validate internal consistency (severity sum, data flow count, finding ID uniqueness)
6. Generate `report-data.typ` with deterministic string formatting (replaces agent Step 3)

**Outputs**: Single `report-data.typ` file with identical content on every run given identical inputs.

**Validation Rules**:
- `critical_count + high_count + medium_count + low_count == total_findings`
- `len(scope_data_flows) == scope_data_flow_count`
- `len(scope_components) == scope_component_count`
- All finding IDs are unique
- All Typst string values are properly escaped (quotes, backslashes)

### FR-2: Tier-Based Severity Source Selection

**Description**: Unambiguous, programmatic severity source selection.

| Tier | Condition | Severity Source | Cover Page Counts |
|------|-----------|----------------|-------------------|
| Tier 1 | `compensating-controls.md` exists | Residual severity counts from Section 2 findings | Count by `residual_severity` field |
| Tier 2 | `risk-scores.md` exists, no compensating-controls | Scored severity from Section 1 distribution table | Use Section 1 counts directly |
| Tier 3 | Only `threats.md` | Section 6 Risk Summary table | Use Section 6 counts directly |

### FR-3: Agent Prompt Update

**Description**: The report-assembler agent instructions are updated to orchestrate (detect, invoke script, compile) instead of parsing.

**Changes**:
- Steps 2–3 replaced with a single step: invoke the parsing script
- Step 1 (artifact detection) and Step 4 (Typst compilation) remain unchanged
- Error handling updated to capture script exit codes and stderr

### FR-4: Brand Asset Detection

**Description**: The script detects brand logos using the same path checks as the current agent Step 2i.

No changes to brand asset logic — the existing detection rules are already deterministic (file existence checks). The script replicates this logic.

---

## Non-Functional Requirements

### Determinism
- **Requirement**: Given identical input files (same content, any filesystem metadata), the script produces byte-identical `report-data.typ` output
- **Verification**: Run script twice, `diff` the outputs — zero differences

### Performance
- **Parsing time**: < 5 seconds for the largest expected artifact set (64+ findings, 36 data flows, 20+ components)
- **No external dependencies beyond Python standard library**: The script must run with Python 3.9+ using only `re`, `yaml` (or regex-based frontmatter parsing), `pathlib`, `argparse`, `sys`

### Compatibility
- **Python 3.9+**: Must run on macOS, Linux, and Windows
- **Typst output format**: Generated `report-data.typ` must be syntactically valid Typst and structurally identical to what the LLM previously generated (same variable names, same types)
- **Backward compatibility**: No changes to Typst templates — the script produces the same data contract

### Error Handling
- **Missing required artifact**: Exit with code 1 and clear error message
- **Malformed markdown table**: Log warning, extract what's parseable, continue
- **Validation failure**: Exit with code 2, display which validation check failed and the offending values

---

## Scope & Boundaries

### In Scope (P0)

- **Deterministic parsing script** (Python) that reads markdown artifacts and writes `report-data.typ`
- **All data extraction from Steps 2a–2j** of the current agent: frontmatter, severity counts, findings (all 3 tiers), scope data, coverage matrix, controls, remediation actions, brand assets, report config
- **Tier-based severity source selection** with unambiguous programmatic logic
- **Internal consistency validation**: severity sum check, data flow count check, finding ID uniqueness
- **Agent prompt update**: report-assembler.md updated to invoke script instead of LLM-parsing
- **Command update**: security-report.md updated if needed for script invocation
- **Testing against OpenClaw example dataset** (the 4-report scenario from the issue)
- **Testing against agentic-app example dataset** for regression

### Out of Scope

- **Typst template changes**: Templates already render correctly with well-formed data
- **Upstream pipeline agent changes**: Threat agents, risk scorer, and control analyzer are unaffected
- **Infographic generation changes**: Separate pipeline, not part of report assembly
- **New report pages or sections**: This is a data extraction fix, not a feature addition
- **CI/CD integration**: Future work — deterministic output enables it, but the pipeline itself is out of scope

### Assumptions
- Python 3.9+ is available on all target platforms (macOS, Linux, Windows)
- The markdown artifact format is stable (schema v1.0 and v1.1 as documented)
- The Typst variable contract in `report-data.typ` does not need to change

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: Markdown table parsing edge cases
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**: Use the existing example datasets (OpenClaw, agentic-app) as parsing test fixtures. These cover all table formats generated by tachi pipeline agents.

**Risk 2**: Typst string escaping in finding text
- **Likelihood**: Medium
- **Impact**: Low
- **Mitigation**: The LLM already had to handle this — the script can apply the same escaping rules deterministically. Test with findings containing quotes, backslashes, and special characters.

**Risk 3**: YAML frontmatter parsing without PyYAML
- **Likelihood**: Low
- **Impact**: Low
- **Mitigation**: The frontmatter is simple key-value pairs (`date`, `classification`, `schema_version`). Regex extraction is sufficient without a YAML library dependency.

### Dependencies

**Internal Dependencies**:
- **Typst template system** (PRD-054, PRD-060): Delivered and stable. The script targets the existing `report-data.typ` variable contract.
- **Example datasets**: OpenClaw and agentic-app examples must be current and contain all artifact types for testing.

**No external dependencies**: Script uses Python standard library only.

---

## Open Questions

- [x] Which severity source for each tier? — Answered in FR-2 (residual for Tier 1, scored for Tier 2, original for Tier 3)
- [x] Should the script use PyYAML? — No, regex-based frontmatter parsing avoids external dependency
- [ ] Should the script output to stdout or write directly to file? — Recommend direct file write with `--output` flag for simplicity — architect to confirm during spec

---

## References

### Product Documentation
- Product Vision: [product-vision.md](../01_Product_Vision/product-vision.md)
- PRD-054 (Security Assessment PDF): [054-security-assessment-pdf-booklet-2026-03-28.md](054-security-assessment-pdf-booklet-2026-03-28.md)
- PRD-060 (Professional Branding): [060-professional-pdf-security-report-branding-2026-03-29.md](060-professional-pdf-security-report-branding-2026-03-29.md)

### Technical Documentation
- Report Assembler Agent: `.claude/agents/tachi/report-assembler.md`
- Security Report Command: `.claude/commands/security-report.md`
- Typst Templates: `templates/tachi/security-report/`
- Constitution: `.aod/memory/constitution.md`

### Issue & Evidence
- GitHub Issue #67: Full 5 Whys root cause analysis with 4-report evidence table
