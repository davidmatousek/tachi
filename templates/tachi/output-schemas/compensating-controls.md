# Compensating Controls Report

<!--
  Canonical output template for tachi compensating controls reports.

  Schema version : 1.1
  Schema file    : schemas/compensating-controls.yaml
  Finding schema : schemas/finding.yaml

  Producers      : scripts/render-compensating-controls.py, the shipped renderer, writes the whole file
                   from the control analyzer's part files, the scored threats and the threat model.
                   agents/tachi/control-analyzer.md supplies the judgment fields only (each finding's
                   control status, category, confidence, evidence and recommendation, and the text cells
                   of its Section 2 row), and writes none of this file.
  Consumers      : Security engineers, security managers, developers, GRC tools

  Every generated compensating controls output MUST conform to this structure.
  All sections are required, and they must appear in the order listed. A band table, a category
  subsection or a recommendation group that would hold nothing is left out.

  Slots: the agent writes a finding's Section 2 row against this template, with one slot token in each
  computed cell ({{score:inherent}}, {{band:inherent}}, {{score:residual}} and {{band:residual}}), and
  writes each effectiveness rationale as prose with slots. The renderer fills every slot with the value
  it computed, so a number or band in a row or a rationale always equals the one in the table beside it.
  Section 7's Assessment Inputs keeps the same text with its slots unresolved, so that the next run can
  re-resolve them against its own values.

  Escaping: the renderer escapes the agent's text and the text it reads from the threat model (`&`, `<`,
  `>`, `|`, a backtick and a newline in a table cell, a `{{`, and a `#` or `~` that opens a line become
  numeric or named references), and the readers in scripts/tachi_parsers.py decode exactly those
  references.
-->

---

```yaml
---
schema_version: "1.1"
date: "YYYY-MM-DD"
source_file: "{path to input risk-scores.md or risk-scores.sarif}"
target_path: "{--target codebase path}"
classification: "security"
rescan_scope: "{full or incremental}"
carry_forward_count: "{number of carried-forward control results or null}"
---
```

**Frontmatter fields:**

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Compensating controls schema version. Always `"1.1"` for this release. 1.1 is additive to 1.0: the MAESTRO Layer and Control Category columns, `CF` in every Section 2 band table, one Section 4 block for each finding that has a recommendation, and Section 7. |
| `date` | string | ISO 8601 date when the analysis was performed, as the command passed it to the renderer. The clock never enters this file. Format: `YYYY-MM-DD`. |
| `source_file` | string | Path to the input risk score file that was analyzed, relative to the working directory. |
| `target_path` | string | Path to the target codebase scanned for controls (`--target` flag value), relative to the working directory. |
| `classification` | string | Data classification label. Always `"security"` for compensating controls reports. |
| `rescan_scope` | string | `full` (first run or all findings changed) or `incremental` (only NEW/UPDATED findings re-scanned, UNCHANGED carried forward). |
| `carry_forward_count` | integer, nullable | Number of findings with carried-forward control results from baseline: the rows whose `CF` cell reads `CF` in Section 2. Null when no baseline. |

---

## 1. Executive Summary

**{total_threats}** threats analyzed | **{coverage_found_count}** Control Found | **{coverage_partial_count}** Partial Control | **{coverage_missing_count}** No Control Found

**Coverage**: {coverage_found_pct}% Found | {coverage_partial_pct}% Partial | {coverage_missing_pct}% Missing

**Risk Reduction**: {total_inherent_risk} inherent -> {total_residual_risk} residual (**{risk_reduction_pct}%** reduction)

**Highest-Risk Unmitigated Finding**: {highest_risk_unmitigated_id} — {highest_risk_unmitigated_component} — Composite {highest_risk_unmitigated_score} ({highest_risk_unmitigated_severity})

| Metric | Value |
|--------|-------|
| Analysis date | {date} |
| Source file | `{source_file}` |
| Target codebase | `{target_path}` |
| Schema version | {schema_version} |

**Coverage Distribution:**

| Status | Count | Percentage |
|--------|-------|------------|
| Control Found | {coverage_found_count} | {coverage_found_pct}% |
| Partial Control | {coverage_partial_count} | {coverage_partial_pct}% |
| No Control Found | {coverage_missing_count} | {coverage_missing_pct}% |
| **Total** | **{total_threats}** | **100%** |

The renderer fills this whole section from the rows of Section 2, so every count equals the sum of the rows it counts. The percentages are whole numbers that sum to 100, by largest remainder (ties go to the label that sorts first). The `**Risk Reduction**` line keeps its ASCII arrow, because the readers' pattern needs it. The highest-risk unmitigated finding is the Partial Control or No Control Found finding with the highest inherent score, ties going to the first in finding ID order (defined in Section 2): a Control Found finding is never named, whatever its score.

> {analysis_warnings}

The renderer fills the warnings line from its own checks. A finding whose Section 2 cells disagree with its structured judgment is named there, and Section 7 lists the same flags.

---

## 2. Coverage Matrix

Threats grouped by residual severity (Critical first, then High, Medium, Low). Within each group, threats are sorted by residual score descending, and by finding ID within equal scores. Finding ID order is the threat model's: prefix rank `S`, `T`, `R`, `I`, `D`, `E`, `AG`, `AGP`, `LLM`, `OI`, `MI`, `TE`, then the numeric suffix as an integer. A band with no finding has no heading and no table.

Every band table uses the one schema below, in this column order. The four computed cells show slot tokens here, and the renderer writes the number or band in their place.

### Critical Residual Severity

| Threat ID | CF | Component | MAESTRO Layer | Threat | Inherent Score | Inherent Severity | Control Status | Control Category | Residual Score | Residual Severity |
|-----------|----|-----------|---------------|--------|----------------|-------------------|----------------|------------------|----------------|-------------------|
| {id} | {cf} | {component} | {maestro_layer} | {threat} | {{score:inherent}} | {{band:inherent}} | {control_status} | {control_category} | {{score:residual}} | {{band:residual}} |

### High Residual Severity

| Threat ID | CF | Component | MAESTRO Layer | Threat | Inherent Score | Inherent Severity | Control Status | Control Category | Residual Score | Residual Severity |
|-----------|----|-----------|---------------|--------|----------------|-------------------|----------------|------------------|----------------|-------------------|
| {id} | {cf} | {component} | {maestro_layer} | {threat} | {{score:inherent}} | {{band:inherent}} | {control_status} | {control_category} | {{score:residual}} | {{band:residual}} |

### Medium Residual Severity

| Threat ID | CF | Component | MAESTRO Layer | Threat | Inherent Score | Inherent Severity | Control Status | Control Category | Residual Score | Residual Severity |
|-----------|----|-----------|---------------|--------|----------------|-------------------|----------------|------------------|----------------|-------------------|
| {id} | {cf} | {component} | {maestro_layer} | {threat} | {{score:inherent}} | {{band:inherent}} | {control_status} | {control_category} | {{score:residual}} | {{band:residual}} |

### Low Residual Severity

| Threat ID | CF | Component | MAESTRO Layer | Threat | Inherent Score | Inherent Severity | Control Status | Control Category | Residual Score | Residual Severity |
|-----------|----|-----------|---------------|--------|----------------|-------------------|----------------|------------------|----------------|-------------------|
| {id} | {cf} | {component} | {maestro_layer} | {threat} | {{score:inherent}} | {{band:inherent}} | {control_status} | {control_category} | {{score:residual}} | {{band:residual}} |

### Summary Statistics

| Residual Severity | Count | Percentage |
|-------------------|-------|------------|
| Critical | {residual_critical_count} | {residual_critical_pct}% |
| High | {residual_high_count} | {residual_high_pct}% |
| Medium | {residual_medium_count} | {residual_medium_pct}% |
| Low | {residual_low_count} | {residual_low_pct}% |
| **Total** | **{total_threats}** | **100%** |

### Column Definitions

| Column | Description |
|--------|-------------|
| **Threat ID** | The finding's ID. An ID that isn't the finding's own rejects the finding's item in the part. |
| **CF** | `CF` when the finding's control result was carried forward from the baseline (an UNCHANGED finding), and `—` when it was assessed in this run. The renderer fills this cell, and `carry_forward_count` counts the `CF` rows. |
| **Component** | The component name from the threat model. The renderer checks the agent's cell against it. |
| **MAESTRO Layer** | The finding's MAESTRO layer as the scored input records it, or `Unclassified`. The renderer checks the cell by layer code (`L1` to `L7`) against the layer that the SARIF writes as `maestro-layer`. |
| **Threat** | The threat description, cut to 80 characters. This is the agent's text. |
| **Inherent Score** | The finding's composite score from this run's `risk-scores.md`, to one decimal. It is never re-scored. |
| **Inherent Severity** | The band of the inherent score: Critical (9.0-10.0), High (7.0-8.9), Medium (4.0-6.9) or Low (0.0-3.9). |
| **Control Status** | `Control Found`, `Partial Control` or `No Control Found`. The renderer checks it against the structured `control_status`. |
| **Control Category** | The display name of the control category: Authentication, Access Control, Input Validation, Encryption, Rate Limiting, Logging/Audit, CSRF Protection or CSP/Security Headers. The category's own name, such as `input-validation`, is read as the same value. |
| **Residual Score** | Inherent score * (1 - reduction factor), rounded half up to one decimal. |
| **Residual Severity** | The band of the residual score. It names the band table that the row sits under. |

**The agent's row.** In its part, the agent writes each finding's row as `matrix_row`: one line of these 11 cells, written as a table line (`| ` before the first cell, ` | ` between cells and ` |` after the last, with no `|` inside a cell). Its own cells are the Threat ID, Component, MAESTRO Layer, Threat, Control Status and Control Category, and it puts one slot token in each computed cell: `{{score:inherent}}`, `{{band:inherent}}`, `{{score:residual}}` and `{{band:residual}}`. The renderer fills those four cells by column position, overwrites any other content that the agent put there, and counts each overwrite in the stage record. It fills `CF` itself and never counts it. A Threat ID that isn't the finding's own, or a cell count other than 11, rejects the finding's item, and the command re-dispatches its batch. A Component, MAESTRO Layer, Control Status or Control Category cell that disagrees with the structured judgment or the input is flagged in Section 7, and the SARIF and every total follow the structured value.

---

## 3. Control Details

Per-control evidence showing detected security controls with their location, code evidence, and threat coverage. One block for each distinct control, which is a control category, a file and a line, grouped by control category. A control that several findings share is listed once, and its Threats Mitigated table names each of them.

### {control_category}

#### {control_id} — {control_summary}

**Category**: {control_category} | **Status**: {control_status} | **Effectiveness**: {control_effectiveness}

**Detected in**: `{evidence_file}:{evidence_line}`

```{evidence_language}
{evidence_snippet}
```

> Code snippet limited to 5 lines centered on the control implementation. The fence is one backtick longer than the longest backtick run in the snippet, and never shorter than three.

**Effectiveness Assessment** (written only when the agent assessed the control; each rationale is the agent's prose with its slots filled):

| Dimension | Rating | Rationale |
|-----------|--------|-----------|
| Coverage | {eff_coverage_rating} | {eff_coverage_rationale} |
| Configuration | {eff_configuration_rating} | {eff_configuration_rationale} |
| Currency | {eff_currency_rating} | {eff_currency_rationale} |
| Completeness | {eff_completeness_rating} | {eff_completeness_rationale} |

**Threats Mitigated by This Control**:

| Threat ID | Component | Threat | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|--------|----------------|------------------|----------------|
| {threat_id} | {threat_component} | {threat_description} | {inherent_score} | {reduction_factor} | {residual_score} |

---

*Repeat the above block for each detected control, grouped by control category in this order: Authentication, Access Control, Input Validation, Encryption, Rate Limiting, Logging/Audit, CSRF Protection, CSP/Security Headers.*

---

## 4. Recommendations

Actionable recommendations for findings classified as "No Control Found" or "Partial Control". Each of those findings has exactly one block, and a block never covers more than one finding. A Control Found finding has no block. The blocks are numbered from 1 through the whole section, sorted by inherent score descending (highest risk gaps first) and by finding ID within equal scores, and they sit under one group for each inherent severity band: Critical and High together, then Medium, then Low. A group with no block has no heading.

### Critical / High Risk Gaps

#### {rec_number}. {rec_threat_id} — {rec_component} (Composite: {rec_inherent_score}, {rec_inherent_severity})

**Current Status**: {rec_control_status}

**What to Implement**: {rec_what}

**Where to Implement**: {rec_where}

**Reference Patterns**: {rec_reference_patterns}

**Effort Estimate**: {rec_effort_estimate} — {rec_effort_rationale}

---

### Medium Risk Gaps

#### {rec_number}. {rec_threat_id} — {rec_component} (Composite: {rec_inherent_score}, {rec_inherent_severity})

**Current Status**: {rec_control_status}

**What to Implement**: {rec_what}

**Where to Implement**: {rec_where}

**Reference Patterns**: {rec_reference_patterns}

**Effort Estimate**: {rec_effort_estimate} — {rec_effort_rationale}

---

### Low Risk Gaps

#### {rec_number}. {rec_threat_id} — {rec_component} (Composite: {rec_inherent_score}, {rec_inherent_severity})

**Current Status**: {rec_control_status}

**What to Implement**: {rec_what}

**Where to Implement**: {rec_where}

**Reference Patterns**: {rec_reference_patterns}

**Effort Estimate**: {rec_effort_estimate} — {rec_effort_rationale}

---

*Repeat the recommendation block for each Partial Control or No Control Found finding, in the group of its inherent severity band. "Partial Control" recommendations focus on hardening (what's missing, how to extend) rather than replacement.*

**Who writes what.** The renderer writes each block's group, number, heading and `**Current Status**:` line, and joins the block to its row in Section 2 by the finding's ID. The agent writes the four lines after them, as the finding's `recommendation_body`: `**What to Implement**:`, `**Where to Implement**:`, `**Reference Patterns**:` and `**Effort Estimate**:`, each once and in this order. The Effort Estimate starts with `Low`, `Medium` or `High`, and the body holds no heading and no table line. A body that breaks these rules rejects the finding's item, and the command re-dispatches its batch. The renderer escapes the body as prose, so a backtick in it is written as a reference, and the body never forms a code span, a heading or a table. The SARIF `recommendation` is the What to Implement text and `effort-estimate` is the Effort word, so the two files agree by construction.

### Recommendation Field Definitions

| Field | Description |
|-------|-------------|
| **What to Implement** | Specific control to add or harden. For "No Control Found": full implementation guidance. For "Partial Control": targeted hardening of the existing control. |
| **Where to Implement** | Suggested file path or module in the target codebase. Based on architecture mapping or codebase heuristics. |
| **Reference Patterns** | Industry-standard patterns, libraries, or framework features to use as implementation reference. |
| **Effort Estimate** | **Low**: Configuration change or flag toggle. **Medium**: New middleware, function, or module. **High**: Architectural change affecting multiple components. |

---

## 5. Residual Risk Summary

Comparison of inherent risk (before controls) to residual risk (after controls), showing the risk reduction achieved by existing controls. The renderer computes every figure here from the rows of Section 2, in exact decimal arithmetic, so each total equals the sum of its rows. The overall reduction is the delta over the inherent total, rounded half up to one decimal (0.0 for a zero inherent total).

### Aggregate Risk Reduction

| Metric | Value |
|--------|-------|
| Total Inherent Risk Score | {total_inherent_risk} |
| Total Residual Risk Score | {total_residual_risk} |
| Delta | {risk_delta} |
| Overall Reduction | {risk_reduction_pct}% |

### Per-Severity-Band Shift

Breakdown of how threats shifted between severity bands after residual risk calculation. "Shifted" means a threat moved from a higher inherent severity band to a lower residual severity band due to detected controls.

| Shift | Count | Examples |
|-------|-------|---------|
| Critical -> High | {shift_critical_to_high_count} | {shift_critical_to_high_examples} |
| Critical -> Medium | {shift_critical_to_medium_count} | {shift_critical_to_medium_examples} |
| Critical -> Low | {shift_critical_to_low_count} | {shift_critical_to_low_examples} |
| High -> Medium | {shift_high_to_medium_count} | {shift_high_to_medium_examples} |
| High -> Low | {shift_high_to_low_count} | {shift_high_to_low_examples} |
| Medium -> Low | {shift_medium_to_low_count} | {shift_medium_to_low_examples} |
| No Shift | {shift_none_count} | {shift_none_examples} |
| **Total** | **{total_threats}** | |

Each Examples cell names the finding IDs of its shift, or `—` when there are none. A finding whose band holds is counted under No Shift.

### Severity Distribution Comparison

| Severity | Inherent Count | Residual Count | Change |
|----------|----------------|----------------|--------|
| Critical | {inherent_critical_count} | {residual_critical_count} | {critical_change} |
| High | {inherent_high_count} | {residual_high_count} | {high_change} |
| Medium | {inherent_medium_count} | {residual_medium_count} | {medium_change} |
| Low | {inherent_low_count} | {residual_low_count} | {low_change} |
| **Total** | **{total_threats}** | **{total_threats}** | |

Change is the residual count less the inherent count, signed.

### Reduction Factor Reference

| Control Status | Reduction Factor | Formula | Description |
|----------------|------------------|---------|-------------|
| Control Found | 0.50 | Inherent * 0.50 | Control detected with evidence. Residual is 50% of inherent. |
| Partial Control | 0.25 | Inherent * 0.75 | Control exists but incomplete coverage. Residual is 75% of inherent. |
| No Control Found | 0.00 | Inherent * 1.00 | No matching control detected. Residual equals inherent. |

> P1 enhancement: When control effectiveness assessment (User Story 6) is active, reduction factors upgrade from the 3-level binary model above to a 7-level effectiveness-aware model. See spec FR-011 and User Story 6 for the extended factor table.

---

## 6. Methodology

This section documents the compensating controls analysis methodology used to produce this report.

### 6.1 Control Detection

The analysis scans the target codebase for security controls across 8 categories:

| Category | What It Detects | STRIDE Mapping |
|----------|-----------------|----------------|
| **Authentication** | Login mechanisms, token validation, session management, identity verification | Spoofing |
| **Access Control** | Role checks, permission guards, authorization middleware, RBAC/ABAC patterns | Spoofing, Elevation of Privilege |
| **Input Validation** | Schema validation, sanitization, parameterized queries, type checking | Tampering |
| **Encryption** | TLS configuration, data-at-rest encryption, hashing algorithms, key management | Information Disclosure |
| **Rate Limiting** | Request throttling, circuit breakers, backpressure, quota enforcement | Denial of Service |
| **Logging/Audit** | Structured logging, audit trails, immutable logs, event tracking | Repudiation |
| **CSRF Protection** | Anti-CSRF tokens, SameSite cookies, origin validation | Tampering |
| **CSP/Security Headers** | Content-Security-Policy, HSTS, X-Frame-Options, security header middleware | Information Disclosure |

### 6.2 Classification Logic

Each scored threat receives exactly one classification based on detected controls:

| Classification | Criteria | Reduction Factor |
|----------------|----------|------------------|
| **Control Found** | A matching control is detected with file:line evidence that addresses the threat's attack vector | 0.50 |
| **Partial Control** | A control exists but does not cover all paths, vectors, or components targeted by the threat | 0.25 |
| **No Control Found** | No matching control detected in the target codebase for this threat | 0.00 |

When multiple controls address the same threat, the highest single control effectiveness is used (not additive).

### 6.3 Residual Risk Calculation

Residual risk per threat is calculated as:

```
Residual Score = Inherent Score * (1 - Reduction Factor)
```

Residual scores are clamped to [0.0, 10.0] and mapped to severity bands using the same thresholds as risk scoring:

| Severity | Residual Score Range |
|----------|---------------------|
| **Critical** | >= 9.0 |
| **High** | 7.0 -- 8.9 |
| **Medium** | 4.0 -- 6.9 |
| **Low** | < 4.0 |

### 6.4 Data Sources

Analysis draws on the following inputs:

- **Scored threats**: Parsed from `risk-scores.md` (canonical) or `risk-scores.sarif` (fallback). All original threat metadata (ID, component, category, description, composite score, severity band) is preserved.
- **Target codebase**: Scanned via `--target` path. When `architecture.md` is available, component-to-directory mapping enables targeted file discovery. When absent, heuristic directories (`middleware/`, `auth/`, `security/`, `validators/`, `guards/`, `interceptors/`, `filters/`, `policies/`, `config/`) are prioritized.
- **STRIDE-to-control mapping**: Canonical mapping from threat categories to control categories drives which controls are searched for each threat.

### 6.5 Limitations

- Static analysis only — runtime control behavior is not evaluated
- 200-file read budget — large codebases may have directories skipped with warnings
- Files > 5,000 tokens are truncated to security-relevant sections
- Binary reduction factors (P0) approximate control impact; effectiveness-aware factors available in P1
- AI-specific control patterns (agentic, LLM) limited to general categories in P0; specialized patterns in P1

---

## 7. Analysis Integrity

What the renderer checked, flagged or could not use, and the controls inputs it persists for the next run. A run with nothing to flag has an empty Integrity Flags table and no input issues.

### Integrity Flags

| ID | Flag | Field | Stored | Rendered | Cause |
|----|------|-------|--------|----------|-------|
| {id} | {kind} | {field} | {stored_value} | {rendered_value} | {cause} |

One row for each flag, in finding ID order (prefix rank `S`, `T`, `R`, `I`, `D`, `E`, `AG`, `AGP`, `LLM`, `OI`, `MI`, `TE`, then the numeric suffix as an integer). A flag is a `kind:field:cause` string, and the finding's SARIF `integrity-flags` property carries the same strings, sorted. `Stored` is the value that the agent's part or the input held and `Rendered` is the value this file shows, where a flag compares two values, and both read `—` otherwise. The renderer raises a flag when a Section 2 cell that it only checks (the Component, MAESTRO Layer, Control Status or Control Category) disagrees with the structured judgment or the input, when a narrative field breaks the slot rules and takes its fixed sentence, when a prose field is cut at its length limit, and when the scored input flags a finding whose ID the baseline used. The SARIF and every total follow the structured value, never the cell that disagrees.

### Input Issues

Rows and files that the renderer couldn't read or fully use, one entry each, naming the file, the section and the problem: a row of the scored input that has no usable form, and a finding ID that the scored input lists twice. `None.` when there are none.

### Assessment Inputs

| ID | Field | Value |
|----|-------|-------|
| {id} | {field} | {value} |

One row for each value of a finding's controls result that the next run needs in order to carry the finding forward, so that it reads them from one place. This one table holds the whole result: the finding's judgment, each of its evidence entries and its Section 2 row. No second table holds the evidence or the row, because the reader reads this one. The planner of the next run decodes an UNCHANGED finding's values into that finding's batch input, and the agent copies them from there, so nothing is ever copied from this file's Sections 2, 3 or 4. The rows go in finding ID order, and within a finding in the order of the agent's part:

- `control_status`, `control_category`, `confidence` and `carried_forward` (`true` or `false`);
- the finding's evidence, one entry at a time and numbered from 0: `evidence.<n>.file`, `evidence.<n>.line`, `evidence.<n>.language`, `evidence.<n>.snippet` and `evidence.<n>.summary`, then, where the agent assessed the control, `evidence.<n>.assessment.<dimension>.rating` and `evidence.<n>.assessment.<dimension>.rationale` for the dimensions `coverage`, `configuration`, `currency` and `completeness`, in that order;
- `matrix_row`;
- `recommendation_body`.

A field name is a dotted address, with a list entry as a numeric segment, such as `evidence.0.summary`. A field with no value writes no row: a No Control Found finding has no `confidence` row and no `evidence` rows, and a Control Found finding has no `recommendation_body` row. `matrix_row` is the finding's whole Section 2 row as one value: its 11 cells in the order of Section 2's header, written as a table line, with every `|` in it, the cell separators included, written as `&#124;` so that the row stays one cell. Its four computed cells hold their slot tokens (`{{score:inherent}}`, `{{band:inherent}}`, `{{score:residual}}` and `{{band:residual}}`), never the numbers that Section 2 shows, and its `CF` cell holds the value that Section 2 shows. So a carried row is copied, read and checked with no overwrite, whatever the first run put in those cells. An assessment rationale keeps its slot tokens too, a snippet keeps its line breaks as `&#10;`, and every value is escaped on write.

<!-- tachi-provenance: renderer=render-compensating-controls.py; version={X.Y.Z}; input-digest=sha256:{hex} -->
