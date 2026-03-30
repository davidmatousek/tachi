---
prd_reference: docs/product/02_PRD/071-deterministic-infographic-extraction-2026-03-30.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-30
    status: APPROVED
    notes: "All 4 PRD user stories covered plus agent prompt update story. All 13 architect concerns resolved with concrete FRs. No scope creep. Largest Remainder Method replaces bare round() — research-informed improvement. 8 measurable success criteria. Ready for planning."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Deterministic Infographic Extraction

**Feature Branch**: `071-deterministic-infographic-extraction`
**Created**: 2026-03-30
**Status**: Draft
**Input**: PRD-071: Replace LLM-based data extraction in the threat-infographic agent with a deterministic Python script

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deterministic Baseball Card Specification (Priority: P1)

A security engineer runs `/infographic --template baseball-card` on a directory containing threat model artifacts. They run it again on the same unchanged input. Both runs produce byte-identical `threat-baseball-card-spec.md` files — same severity counts, same heat map values, same top findings, same percentages.

**Why this priority**: Baseball card is the most commonly used template for executive communication. Non-deterministic severity counts directly undermine trust in the tool's output.

**Independent Test**: Run the extraction script twice on `examples/agentic-app/sample-report/` with `--template baseball-card`, diff the outputs. Zero differences confirms determinism.

**Acceptance Scenarios**:

1. **Given** `examples/agentic-app/sample-report/` with unchanged artifacts, **When** the extraction script is run twice with `--template baseball-card`, **Then** both JSON outputs are byte-identical.
2. **Given** a baseball card JSON output, **When** severity counts are compared to `scripts/extract-report-data.py` output for the same tier, **Then** critical, high, medium, and low counts match exactly.
3. **Given** a baseball card JSON output with severity percentages, **When** percentages are summed, **Then** the sum equals exactly 100%.
4. **Given** findings with tied composite scores, **When** top 5 are selected, **Then** selection is deterministic: composite score descending, threat ID ascending for ties.

---

### User Story 2 - Deterministic System Architecture Specification (Priority: P1)

A security engineer runs `/infographic --template system-architecture` on threat model artifacts. Both successive runs produce byte-identical `threat-system-architecture-spec.md` files with the same component annotations, trust zone groupings, data flow severity coloring, and finding overlays.

**Why this priority**: Architecture diagrams annotated with incorrect or varying risk levels mislead engineering teams about which components need attention.

**Independent Test**: Run extraction script twice on `examples/agentic-app/sample-report/` with `--template system-architecture`, diff outputs.

**Acceptance Scenarios**:

1. **Given** unchanged artifacts, **When** the script is run twice with `--template system-architecture`, **Then** both JSON outputs are byte-identical.
2. **Given** scope data with trust zones and data flows, **When** the script extracts architecture overlay data, **Then** components are grouped by trust zone with deterministic ordering (trust level descending, component name ascending).
3. **Given** data flows between components, **When** severity coloring is assigned, **Then** the highest-severity finding targeting the flow's destination component determines the color.

---

### User Story 3 - Deterministic Risk Funnel Specification (Priority: P1)

A security engineer runs `/infographic --template risk-funnel` on a directory containing all three pipeline artifacts (threats.md, risk-scores.md, compensating-controls.md). Both successive runs produce byte-identical `threat-risk-funnel-spec.md` files with the same tier counts and reduction percentages.

**Why this priority**: The risk funnel visualizes the pipeline's progressive risk reduction. Inconsistent reduction percentages between runs invalidate the funnel's narrative.

**Independent Test**: Run extraction script twice on `examples/agentic-app/sample-report/` with `--template risk-funnel`, diff outputs.

**Acceptance Scenarios**:

1. **Given** unchanged artifacts, **When** the script is run twice with `--template risk-funnel`, **Then** both JSON outputs are byte-identical.
2. **Given** a risk funnel output, **When** reduction percentages are computed between tiers, **Then** each percentage uses the Largest Remainder Method to guarantee integer percentages sum to their expected totals.
3. **Given** Tier 1 artifacts exist (compensating-controls.md), **When** the funnel is computed, **Then** all four tiers are populated: raw findings (threats.md count), inherent risk scored (risk-scores.md count), controls applied (compensating-controls.md count), residual risk (residual severity counts).
4. **Given** only threats.md exists (Tier 3), **When** the funnel is computed, **Then** only the first tier (raw findings) is populated; remaining tiers display zero with a note indicating the enrichment command to run.

---

### User Story 4 - Cross-Output Consistency (Priority: P1)

A CISO generates both a security report and an infographic from the same threat model artifacts. The severity distribution in the infographic spec matches the `report-data.typ` severity counts exactly — no contradictions between outputs.

**Why this priority**: Infographics and security reports are often presented together. Contradicting numbers between the two outputs eliminate trust in both.

**Independent Test**: Run `scripts/extract-report-data.py` and the new infographic extraction script on the same directory, compare severity counts from both outputs.

**Acceptance Scenarios**:

1. **Given** the same directory with threat model artifacts, **When** `extract-report-data.py` and the infographic extraction script both extract severity counts for the same tier, **Then** critical, high, medium, low, and note counts are identical.
2. **Given** Tier 1 artifacts, **When** both scripts parse compensating-controls.md, **Then** residual severity distributions match exactly.

---

### User Story 5 - Agent Prompt Update (Priority: P2)

The threat-infographic agent is updated to invoke the deterministic extraction script instead of performing LLM-based parsing for Steps 1-2. The agent retains responsibility for assembling the spec markdown file and generating Gemini images.

**Why this priority**: The script produces the data; the agent consumes it. Without the agent update, the deterministic script sits unused.

**Independent Test**: Run `/infographic` end-to-end on example datasets and verify the generated spec files contain data matching the script's JSON output.

**Acceptance Scenarios**:

1. **Given** the updated infographic agent, **When** `/infographic` is invoked, **Then** the agent calls the extraction script and uses its JSON output for spec generation.
2. **Given** the extraction script exits with code 1 (missing artifact), **When** the agent handles the error, **Then** the agent displays a clear error message and does not attempt spec generation.
3. **Given** the extraction script exits with code 2 (validation failure), **When** the agent handles the error, **Then** the agent displays the validation failure details and does not attempt spec generation.

---

### Edge Cases

- **Empty findings table**: Script outputs zero counts for all severities and an empty findings array; percentages are all 0%.
- **Single severity level**: If all findings are "High" with no other severities, the donut chart shows High=100%, all others=0%.
- **Component with zero findings**: Component appears in heat map with all-zero row if it is listed in scope data.
- **Duplicate threat IDs across agent tables**: Deduplication uses the union of all threat IDs; each ID counted once regardless of how many agent tables contain it.
- **Missing Section 4a (correlation groups)**: Skip deduplication — count all individual findings from agent tables. Log a note: "No correlation groups found; using raw finding counts."
- **Malformed markdown table row**: Log warning with row content, skip the row, continue processing remaining rows.
- **Unicode characters in findings**: Preserve em dashes, smart quotes, and other Unicode in output JSON using UTF-8 encoding.
- **Note severity findings**: Include in total finding count metadata but exclude from donut chart percentage calculations and heat map severity columns.
- **Trust zones absent from scope data**: Omit the trust zone grouping from architecture overlay; use a flat component list instead. Log a note: "No trust zones found; using flat component layout."
- **risk-scores.md absent when computing funnel inherent scores**: Set the inherent tier to `null` in the JSON output. Do not recalculate inherent scores from threats.md severity.

## Requirements *(mandatory)*

### Functional Requirements

#### Script Infrastructure

- **FR-001**: System MUST provide a Python script (`scripts/extract-infographic-data.py`) that reads tachi pipeline markdown artifacts and outputs structured JSON for infographic specification generation.
- **FR-002**: Script MUST accept CLI arguments: `--target-dir` (required, directory containing artifacts), `--template` (required, one of `baseball-card`, `system-architecture`, `risk-funnel`), `--output` (required, path for JSON output file).
- **FR-003**: Script MUST reuse parser functions from `scripts/extract-report-data.py` via a shared module pattern — common parsers factored into an importable location. No duplicated table parsing logic.
- **FR-004**: Script MUST use only Python 3.9+ standard library (re, pathlib, argparse, sys, os, json, math). No external dependencies.
- **FR-005**: Script MUST exit with code 0 (success), 1 (missing required artifact — threats.md), or 2 (validation failure).
- **FR-006**: Script MUST output valid JSON to the `--output` path, encoded as UTF-8.

#### Tier Detection & Severity Extraction

- **FR-007**: Script MUST implement the same 3-tier detection logic as `extract-report-data.py`: Tier 1 (compensating-controls.md exists) > Tier 2 (risk-scores.md exists) > Tier 3 (threats.md only).
- **FR-008**: For Tier 1, severity source MUST be residual severity from compensating-controls.md Section 2 Coverage Matrix, extracting residual severity per finding from the "Residual" or "Residual Score" column.
- **FR-009**: For Tier 2, severity source MUST be scored severity from risk-scores.md Section 1 Severity Distribution, using composite score bands: 9.0-10.0=Critical, 7.0-8.9=High, 4.0-6.9=Medium, 0.0-3.9=Low.
- **FR-010**: For Tier 3, severity source MUST be Section 6 Risk Summary from threats.md.
- **FR-011**: Severity counts MUST match `extract-report-data.py` output for the same input and tier — this is the cross-output consistency guarantee.

#### Deduplication (Tier 3)

- **FR-012**: For the threats.md path, the script MUST deduplicate findings using threat IDs. Each threat ID is counted exactly once regardless of how many agent tables contain it.
- **FR-013**: When Section 4a (correlation groups) exists, the script MUST build the deduplication set as the union of: (a) all threat IDs from individual agent tables in Section 3, and (b) all threat IDs listed in Section 4a correlation groups. A threat ID appearing in both an agent table and a correlation group is counted once.
- **FR-014**: When Section 4a is absent (schema v1.0 compatibility), the script MUST skip deduplication and count all findings from individual agent tables. The script MUST log: "Note: No correlation groups found; using raw finding counts."
- **FR-015**: Severity counts for Tier 3 MUST use the deduplicated finding set. The metric labeled "total findings" in infographic metadata uses the deduplicated count. The metric labeled "raw findings" (used in risk funnel Tier 0) uses the pre-deduplication count from Section 6 Risk Summary.

#### Percentage Calculations

- **FR-016**: All percentage distributions that must sum to a target (donut chart severities, funnel reduction percentages) MUST use the Largest Remainder Method (Hamilton/Hare-Niemeyer) with deterministic tie-breaking: fractional part descending, then label/ID ascending.
- **FR-017**: Individual percentage values not part of a distribution (e.g., a single "reduction from previous tier" display) MUST use Python `round()` to one decimal place.
- **FR-018**: When total finding count is zero, all percentage values MUST be 0. No division-by-zero errors.

#### Heat Map Cross-Tabulation

- **FR-019**: The script MUST compute a component x severity cross-tabulation matrix. Rows are components; columns are Critical, High, Medium, Low (Note excluded from heat map columns).
- **FR-020**: Every component listed in scope data (from `parse_scope_data()`) MUST appear as a row in the heat map, even if the component has zero findings (all-zero row).
- **FR-021**: Heat map rows MUST be ordered by total finding count descending, then component name ascending for ties.
- **FR-022**: When more than 8 components exist, the script MUST display the top 7 by total count and aggregate all remaining components into an "Other" row.

#### Top N Finding Selection

- **FR-023**: The script MUST select the top 5 findings using deterministic ranking: primary sort by composite score descending (Tier 1: residual score, Tier 2: composite score, Tier 3: severity ordinal — Critical=4, High=3, Medium=2, Low=1), secondary sort by threat ID ascending (lexicographic) for ties.
- **FR-024**: Each finding in the top 5 MUST include: threat ID, component, one-sentence threat description, risk level (severity label or score).

#### Template-Specific: Baseball Card

- **FR-025**: Baseball card output MUST include: metadata (project name, scan date, agent count, total findings, note count, risk posture summary), severity distribution with percentages and color codes, component x severity heat map, top 5 findings, and component risk weight summary (high/medium/low classification using weighted score: C=4, H=3, M=2, L=1).

#### Template-Specific: System Architecture

- **FR-026**: System architecture output MUST include all baseball card data plus: trust zone groupings (components grouped by trust zone, ordered by trust level descending then component name ascending), data flow list with severity coloring (highest severity finding targeting the flow's destination determines color), and boundary crossing annotations.
- **FR-027**: When trust zones are absent from scope data, the script MUST use a flat component list (no zone grouping) and log: "Note: No trust zones found; using flat component layout."

#### Template-Specific: Risk Funnel

- **FR-028**: Risk funnel output MUST include four tiers: Tier 0 (raw findings from threats.md — total count from Section 6 Risk Summary), Tier 1 (inherent risk scored — count from risk-scores.md if available), Tier 2 (controls applied — count from compensating-controls.md if available), Tier 3 (residual risk — residual severity counts if Tier 1 artifacts exist).
- **FR-029**: Reduction percentages between tiers MUST be computed as: `reduction_pct = ((previous_tier_count - current_tier_count) / previous_tier_count) * 100`, rounded using the Largest Remainder Method when presented as a set of tier-to-tier reductions.
- **FR-030**: When an intermediate artifact is absent (e.g., risk-scores.md missing but compensating-controls.md present), the script MUST populate available tiers and set missing tiers to `null` in the JSON output. The infographic agent handles display of partial funnels.
- **FR-031**: When only threats.md exists (Tier 3 scenario), the funnel MUST populate Tier 0 only. Tiers 1-3 are `null`. The JSON includes a `missing_enrichments` array listing the commands to run (e.g., `["/risk-score", "/compensating-controls"]`).
- **FR-032**: When risk-scores.md is absent, the script MUST NOT attempt to recalculate inherent scores from threats.md severity. The inherent tier is set to `null`.

#### Note Severity Handling

- **FR-033**: Note-severity findings MUST be included in the total finding count reported in metadata.
- **FR-034**: Note-severity findings MUST be excluded from: donut chart percentage calculations, heat map severity columns, top N finding selection, and component risk weight calculations.
- **FR-035**: The JSON output MUST include a separate `note_count` field for Note-severity findings.

#### Rounding Strategy for 100% Sum

- **FR-036**: The Largest Remainder Method implementation MUST: (1) compute floor of each percentage, (2) calculate remainder = 100 - sum of floors, (3) sort by fractional part descending with tie-breaking on label ascending, (4) distribute +1 to the top N items where N = remainder.
- **FR-037**: When all severity counts are zero, all percentages MUST be 0 and the sum is 0 (not 100%).

#### Structured Output Format

- **FR-038**: Script output MUST be JSON with the following top-level structure: `metadata` (project name, scan date, tier, template, total findings, note count, risk posture), `severity_distribution` (array of {label, count, percentage, color}), `heat_map` (array of component rows), `top_findings` (array of up to 5 findings), `template_data` (template-specific data: risk weights for baseball-card, architecture overlay for system-architecture, funnel tiers for risk-funnel).
- **FR-039**: Script MUST output data only — no spec markdown generation. The infographic agent consumes the JSON and assembles the spec markdown file.

#### Validation

- **FR-040**: Script MUST validate that severity sum (critical + high + medium + low) equals total findings minus note count. Validation failure triggers exit code 2.
- **FR-041**: Script MUST validate that all finding IDs in the top 5 exist in the parsed finding set. Validation failure triggers exit code 2.
- **FR-042**: Script MUST validate that heat map row counts are internally consistent (sum of severity columns per row equals the row total).

#### Agent Prompt Update

- **FR-043**: The threat-infographic agent MUST be updated to invoke `scripts/extract-infographic-data.py` for data extraction instead of performing LLM-based parsing in Steps 1-2.
- **FR-044**: The agent MUST pass the script's JSON output into its spec assembly logic, using the structured data to populate Sections 1-5 of the spec markdown.
- **FR-045**: The agent MUST handle script exit codes: code 0 proceeds with spec generation, code 1 displays the missing artifact error and halts, code 2 displays the validation failure and halts.
- **FR-046**: The agent MUST retain full responsibility for Section 6 (Visual Design Directives) and Gemini image generation — these are not part of the extraction script.

#### Error Handling

- **FR-047**: Missing required artifact (threats.md): Exit code 1 with message: "Error: threats.md not found in {target_dir}".
- **FR-048**: Malformed markdown table row: Log warning to stderr ("Warning: Skipping malformed row in {section}: {row_content}"), skip the row, continue processing.
- **FR-049**: Validation failure: Exit code 2 with message identifying the specific check that failed (e.g., "Validation error: Severity sum mismatch — expected {n}, got {m}").

### Key Entities

- **Extraction Script**: `scripts/extract-infographic-data.py` — deterministic data extractor for infographic specifications.
- **Shared Parser Module**: Common parser functions shared between `extract-report-data.py` and `extract-infographic-data.py`. Architecture for sharing (common module import vs. symlink vs. inline extraction) is an implementation concern for plan.md.
- **JSON Output**: Structured data contract between the extraction script and the infographic agent.
- **Infographic Agent**: `.claude/agents/tachi/threat-infographic.md` — updated to consume JSON instead of LLM-parsing markdown.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running the extraction script twice on identical input produces byte-identical JSON output for all three templates (baseball-card, system-architecture, risk-funnel).
- **SC-002**: Running `/infographic` twice on identical input produces byte-identical spec files for all three templates.
- **SC-003**: Severity counts in infographic JSON match `extract-report-data.py` severity counts for the same input and tier — zero discrepancy across all severity levels.
- **SC-004**: All severity percentage distributions sum to exactly 100% (or exactly 0% when total is zero).
- **SC-005**: Script executes in under 5 seconds on the largest example dataset (agentic-app with 34+ findings).
- **SC-006**: Zero external dependencies — Python 3.9+ standard library only.
- **SC-007**: All three tiers tested: Tier 1 (compensating-controls.md), Tier 2 (risk-scores.md), Tier 3 (threats.md only).
- **SC-008**: Tested against both `examples/agentic-app/sample-report/` (full artifact set) and at least one Tier 3-only example dataset.

### Assumptions

- Python 3.9+ is available on all target platforms (macOS, Linux, Windows).
- Markdown artifact formats are stable and consistent with Feature 067 assumptions.
- Parsers from `scripts/extract-report-data.py` can be shared without major refactoring — the sharing mechanism is an implementation decision for plan.md.
- Example datasets in `examples/` contain representative data for all three tiers.
- The infographic agent's Sections 1-5 spec structure does not change — only the data source (JSON vs LLM extraction) changes.
