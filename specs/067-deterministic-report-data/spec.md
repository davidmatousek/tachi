---
prd_reference: docs/product/02_PRD/067-deterministic-report-data-extraction-2026-03-30.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-30
    status: APPROVED
    notes: "Spec faithfully translates PRD into 27 granular FRs without scope creep. All 4 PRD user stories covered (decomposed to 6 testable stories). All 5 architect concerns and 4 team-lead clarifications addressed. 7 success criteria are measurable and verifiable."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Deterministic Report Data Extraction

**Feature Branch**: `067-deterministic-report-data`
**Created**: 2026-03-30
**Status**: Draft
**PRD Reference**: `docs/product/02_PRD/067-deterministic-report-data-extraction-2026-03-30.md`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reproducible Report Generation (Priority: P1)

A security engineer runs `/security-report` on a directory containing threat model artifacts. They expect the same PDF output every time they run it on the same inputs. Today, running it four times produces four different severity distributions, different data flow counts, and different overall risk levels — all from identical source files. The deterministic parsing script replaces the LLM-based extraction with regex and line parsing so that identical inputs always produce byte-identical `report-data.typ` and byte-identical PDF output.

**Why this priority**: Without deterministic output, the tool cannot be trusted for compliance, audit trails, or executive communication. This is the core value of the feature.

**Independent Test**: Run the script twice on the same input directory and verify the output files are byte-identical using `diff`.

**Acceptance Scenarios**:

1. **Given** a directory with unchanged threat model artifacts (threats.md, risk-scores.md, compensating-controls.md, threat-report.md, infographic JPEGs), **When** the script runs twice, **Then** both runs produce byte-identical `report-data.typ` files
2. **Given** identical `report-data.typ` files, **When** Typst compiles them, **Then** both PDFs are byte-identical
3. **Given** a Tier 1 scenario (compensating-controls.md exists), **When** the script extracts severity counts, **Then** it counts by `residual_severity` from compensating-controls.md Section 2 findings
4. **Given** a Tier 2 scenario (risk-scores.md exists, no compensating-controls.md), **When** the script extracts severity counts, **Then** it uses risk-scores.md Section 1 severity distribution table
5. **Given** a Tier 3 scenario (only threats.md), **When** the script extracts severity counts, **Then** it uses threats.md Section 6 Risk Summary table

---

### User Story 2 - Validated Severity Counts (Priority: P1)

The parsing script extracts severity counts from markdown artifacts and validates internal consistency before writing the output. The user needs confidence that the numbers on the cover page and executive summary are mathematically correct — critical + high + medium + low must equal total findings.

**Why this priority**: Inconsistent severity counts were the most visible symptom of the LLM-parsing bug. Validation catches extraction errors before they reach the PDF.

**Independent Test**: Run the script on each example dataset and verify the validation passes with correct sums.

**Acceptance Scenarios**:

1. **Given** extracted severity counts from any tier, **When** validation runs, **Then** the script verifies critical + high + medium + low == total findings and exits with code 2 if the check fails
2. **Given** a Risk Summary table containing a "Note" severity row, **When** the script extracts counts, **Then** Note-level findings are excluded from the four-level sum but reported in a separate `note-count` variable
3. **Given** a Risk Summary Total row with format "30 (34 raw)", **When** the script parses it, **Then** it uses the raw count (34) as `total-findings` since raw count represents all individual findings in the findings table

---

### User Story 3 - Deterministic Scope Data Extraction (Priority: P1)

The script extracts scope data (components, data flows, trust boundaries, boundary crossings) from threats.md Sections 1-2. The user needs the same component count and data flow count every time, so the scope page accurately reflects the system architecture.

**Why this priority**: Scope data counts varied between runs in the LLM-parsed reports (20 vs 36 data flows from the same file). Deterministic extraction eliminates this variance.

**Independent Test**: Run the script on a threats.md with known scope data and verify extracted counts match the source.

**Acceptance Scenarios**:

1. **Given** threats.md with N data flows in Section 1, **When** the script extracts data flows, **Then** exactly N data flows appear in `report-data.typ` with `scope-data-flow-count = N`
2. **Given** threats.md with M components in Section 1, **When** the script extracts components, **Then** exactly M components appear with `scope-component-count = M`
3. **Given** threats.md where Section 1 or Section 2 tables are missing, **When** the script runs, **Then** it sets arrays to empty and counts to 0 with a logged warning

---

### User Story 4 - Agent Prompt Update (Priority: P1)

The report-assembler agent instructions are updated so the agent orchestrates (detect artifacts, invoke script, compile PDF) instead of performing data extraction and Typst generation itself. Steps 2-3 of the current agent are replaced with a single step: invoke the Python script and verify its exit code.

**Why this priority**: The agent update is required for the script to be used. Without it, the LLM continues parsing non-deterministically.

**Independent Test**: Run `/security-report` end-to-end and verify it invokes the Python script rather than performing inline LLM parsing.

**Acceptance Scenarios**:

1. **Given** the updated agent prompt, **When** `/security-report` is invoked, **Then** the agent calls the Python script with `--target-dir`, `--output`, and `--template-dir` arguments
2. **Given** the script exits with code 0, **When** the agent receives the result, **Then** it proceeds to Typst compilation (Step 4)
3. **Given** the script exits with code 1 (missing required artifact), **When** the agent receives the error, **Then** it displays the error message and aborts
4. **Given** the script exits with code 2 (validation failure), **When** the agent receives the error, **Then** it displays which validation check failed and the offending values

---

### User Story 5 - Consistent Recommendation Formatting (Priority: P2)

The script extracts finding recommendations verbatim from the source markdown without paraphrasing or variable-length rewriting. Every time the script runs, the same recommendation text appears in the findings table.

**Why this priority**: Recommendation formatting was one of the inconsistencies in LLM-parsed reports. Verbatim extraction eliminates variability.

**Independent Test**: Run the script twice and verify all recommendation text in `report-data.typ` is character-identical between runs.

**Acceptance Scenarios**:

1. **Given** a Tier 1 finding with a recommendation in compensating-controls.md, **When** the script extracts it, **Then** the recommendation text is preserved verbatim from the source (minus Typst string escaping)
2. **Given** findings across all severity levels, **When** the script formats them, **Then** all recommendations use consistent formatting with proper Typst string escaping (double quotes escaped as `\"`, backslashes as `\\`)

---

### User Story 6 - Testing Against Both Example Datasets (Priority: P2)

The script is tested against both the OpenClaw and agentic-app example datasets to verify correctness across different artifact configurations. Testing includes Tier 1, Tier 2, and Tier 3 scenarios.

**Why this priority**: Testing against real data from the existing example directories validates the script handles actual tachi pipeline output, not just synthetic test cases.

**Independent Test**: Run the script on each example dataset directory and verify the output matches expected values.

**Acceptance Scenarios**:

1. **Given** the agentic-app example dataset (threats.md + risk-scores.md + threat-report.md), **When** the script runs, **Then** it produces valid Tier 2 output with correct severity counts
2. **Given** a Tier 1 test fixture (compensating-controls.md added to an example directory), **When** the script runs, **Then** it produces valid Tier 1 output with residual severity counts and coverage matrix
3. **Given** a Tier 3 scenario (only threats.md present), **When** the script runs, **Then** it produces valid Tier 3 output with findings from Section 7

---

### Edge Cases

- **Bold markers in table cells**: Some markdown table cells contain `**text**` (e.g., the Total row in Risk Summary: `**30 (34 raw)**`). The script must strip bold markers before parsing numeric values.
- **Code-fenced frontmatter**: If the YAML frontmatter contains code fence markers or unusual characters, the script must handle them without crashing.
- **Unicode characters in findings**: Threat descriptions may contain Unicode characters (em dashes, smart quotes, etc.). The script must pass these through with proper Typst string escaping.
- **Truncation markers**: The `...` truncation in threat descriptions (risk-scores.md) must be preserved as-is in the output.
- **Empty tables**: If a markdown table has headers but zero data rows, the script must produce an empty Typst array `()`.
- **Missing optional sections**: If threat-report.md lacks a Remediation Timeline section, the script must set `remediation-actions = none` without error.
- **Schema v1.0 compatibility**: threats.md with `schema_version: "1.0"` lacks Section 4a (Correlated Findings). The script must skip it without error.
- **risk-scores.md nested frontmatter**: The frontmatter contains nested YAML (`scoring_weights` with sub-keys). The regex-based parser must handle or skip nested structures without a YAML library.
- **Note severity level**: Risk Summary may include a "Note" row. The script must parse it but exclude it from the four-level severity sum validation (critical + high + medium + low == total - note_count).
- **Partial parsing on malformed tables**: If a table row has fewer columns than expected, the script logs a warning and skips that row rather than aborting.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a Python script that reads tachi pipeline markdown artifacts from a target directory and writes a `report-data.typ` file with all Typst variable bindings
- **FR-002**: The script MUST accept the following CLI arguments: `--target-dir` (required, directory containing artifacts), `--output` (required, path for generated `report-data.typ`), `--title` (optional, title override), `--template-dir` (required, path to `templates/tachi/security-report/`)
- **FR-003**: The script MUST detect artifacts and determine the data source tier using the same 3-tier logic as the current agent: Tier 1 (compensating-controls.md) > Tier 2 (risk-scores.md) > Tier 3 (threats.md only)
- **FR-004**: The script MUST parse YAML frontmatter from threats.md to extract `date`, `classification`, and `schema_version` using regex-based parsing (no external YAML library dependency)
- **FR-005**: The script MUST parse the project name from the first `# Threat Model: {name}` heading in threats.md, with the `--title` flag overriding the auto-detected name
- **FR-006**: The script MUST parse severity counts from the tier-appropriate source: Tier 1 counts by `residual_severity` from compensating-controls.md Section 2 findings, Tier 2 from risk-scores.md Section 1 distribution, Tier 3 from threats.md Section 6 Risk Summary
- **FR-007**: The script MUST parse the Total row in Risk Summary, handling the "N (M raw)" format by extracting the raw count as `total-findings`
- **FR-008**: The script MUST strip markdown bold markers (`**`) from table cell values before parsing
- **FR-009**: The script MUST extract findings with tier-specific columns: Tier 1 (id, component, threat, residual_score, residual_severity, control_status, recommendation), Tier 2 (id, component, threat, composite_score, severity, cvss, exploitability), Tier 3 (id, component, threat, likelihood, impact, risk_level, mitigation)
- **FR-010**: The script MUST set Tier 3 `likelihood` and `impact` to `"—"` (em dash) since these granular values are not available in the Section 7 table
- **FR-011**: The script MUST extract scope data from threats.md: components (Section 1), data flows (Section 1), trust zones (Section 2), boundary crossings (Section 2), with counts for each category
- **FR-012**: The script MUST extract component distribution by counting findings per component from the findings table, sorted by count descending
- **FR-013**: The script MUST extract the executive narrative from threat-report.md Section 1 (Risk Posture + Top 5 Threats + Key Recommendations), truncating to 2000 characters if needed
- **FR-014**: The script MUST extract remediation actions with priority: compensating-controls.md Section 3 recommendations (if available) > threat-report.md Remediation Timeline (if available) > `none`
- **FR-015**: The script MUST extract STRIDE coverage matrix from compensating-controls.md (per-category found/partial/missing counts) and detailed controls with component, category, status, evidence, effectiveness
- **FR-016**: The script MUST detect brand assets by checking file existence: `brand/final/tachi-logo-primary.png`, `brand/final/tachi-logo-primary-dark.png`, `brand/final/tachi-logo-horizontal.png`
- **FR-017**: The script MUST compute image paths relative to `templates/tachi/security-report/` using the `../../{target_dir}/` pattern
- **FR-018**: The script MUST escape Typst string values: double quotes to `\"`, backslashes to `\\`, newlines to `\n`
- **FR-019**: The script MUST validate internal consistency: (a) critical + high + medium + low == total - note_count, (b) len(scope_data_flows) == scope_data_flow_count, (c) len(scope_components) == scope_component_count, (d) all finding IDs are unique
- **FR-020**: The script MUST exit with code 0 on success, code 1 when a required artifact is missing (threats.md), and code 2 when a validation check fails (with stderr describing which check failed and the offending values)
- **FR-021**: The script MUST handle schema v1.0 compatibility by skipping Section 4a references without error
- **FR-022**: The script MUST handle malformed table rows by logging a warning to stderr and skipping the row rather than aborting
- **FR-023**: The script MUST set page inclusion flags (has-threat-report, has-risk-scores, has-compensating-controls, has-funnel-image, has-baseball-image, has-architecture-image) based on artifact existence and non-zero file size
- **FR-024**: The script MUST generate output using the exact same Typst variable names, types, and structure as defined in the current report-assembler agent Steps 3a-3q
- **FR-025**: The report-assembler agent prompt MUST be updated to invoke the script instead of performing inline LLM parsing, with Steps 2-3 replaced by a single script invocation step
- **FR-026**: The script MUST be located at `scripts/extract-report-data.py` and run with Python 3.9+ using only standard library modules (`re`, `pathlib`, `argparse`, `sys`, `os`)
- **FR-027**: The script MUST handle the Note severity level by parsing it from the Risk Summary table and exposing it as `note-count` but excluding it from the four-level validation sum

### Key Entities

- **Parsing Script**: The Python script at `scripts/extract-report-data.py` that deterministically extracts structured data from markdown artifacts and writes `report-data.typ`
- **report-data.typ**: The intermediate Typst data file containing all extracted variables as `#let` bindings — the data contract between the parsing script and the Typst template system
- **Data Source Tier**: The 3-level hierarchy determining which artifact provides findings data and severity counts (Tier 1: compensating-controls.md, Tier 2: risk-scores.md, Tier 3: threats.md)
- **Markdown Artifacts**: The input files produced by tachi pipeline agents: threats.md (required), risk-scores.md (optional), compensating-controls.md (optional), threat-report.md (optional), infographic JPEGs (optional)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running the script twice on identical input produces byte-identical `report-data.typ` output (determinism verified by `diff`)
- **SC-002**: Running `/security-report` twice on identical input produces byte-identical PDF output
- **SC-003**: Severity count validation passes on both OpenClaw and agentic-app example datasets (critical + high + medium + low == total - note_count)
- **SC-004**: Data flow count in `report-data.typ` exactly matches the data flow count in the source threats.md for both example datasets
- **SC-005**: The script runs in under 5 seconds on the largest expected artifact set (64+ findings, 36 data flows, 20+ components)
- **SC-006**: The script uses only Python 3.9+ standard library modules (zero external dependencies)
- **SC-007**: All three tiers are exercised by at least one test: Tier 1 (compensating-controls.md present), Tier 2 (risk-scores.md present, no compensating-controls), Tier 3 (threats.md only)

## Assumptions

- Python 3.9+ is available on all target platforms (macOS, Linux, Windows)
- The markdown artifact format is stable (schema v1.0 and v1.1 as documented in `schemas/output.yaml`, `schemas/risk-scoring.yaml`, `schemas/compensating-controls.yaml`)
- The Typst variable contract in `report-data.typ` does not need to change — the script produces the same variable names and types as the current LLM-generated output
- No compensating-controls.md example exists in the repo today; a Tier 1 test fixture must be created as part of testing
- The agentic-app example dataset (`examples/agentic-app/sample-report/`) is current and contains threats.md + risk-scores.md + threat-report.md
- This is a data extraction refactor — no Typst template changes, no new report pages, no upstream pipeline agent changes

## Scope Boundaries

### In Scope
- Deterministic Python parsing script (`scripts/extract-report-data.py`) covering all data extraction from current agent Steps 2a-2j
- Tier-based severity source selection with programmatic logic
- Internal consistency validation (severity sums, scope counts, finding ID uniqueness)
- Agent prompt update (`report-assembler.md`) to invoke script instead of LLM parsing
- Testing against OpenClaw and agentic-app example datasets
- Creation of a Tier 1 test fixture (compensating-controls.md for an example dataset)
- Exit code conventions (0 = success, 1 = missing required artifact, 2 = validation failure)

### Out of Scope
- Typst template changes (templates render correctly with well-formed data)
- Upstream pipeline agent changes (threat agents, risk scorer, control analyzer)
- Infographic generation (separate pipeline)
- New report pages or sections (this is a data extraction fix)
- CI/CD integration (deterministic output enables it, but the pipeline itself is out of scope)
- Security-report command changes (command invokes agent, which invokes script — no command-level changes needed)
