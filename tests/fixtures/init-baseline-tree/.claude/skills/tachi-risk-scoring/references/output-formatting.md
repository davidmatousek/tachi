---
source_agent: risk-scorer
extracted_from: .claude/agents/tachi/risk-scorer.md
version: 1.0.0
---

# Output Formatting Reference

Markdown output formatting specifications for risk-scores.md — column definitions, truncation rules, numeric formatting, display name mappings, and section templates.

---

## Scored Threat Table Column Definitions

The scored threat table (Section 2 of risk-scores.md) contains all scored findings in a single reference table.

| Column | Source Field | Format |
|--------|-------------|--------|
| ID | `id` | Finding ID as-is (e.g., `S-1`, `AG-3`) |
| Component | `component` | Component name, truncated to 30 characters with `...` suffix if longer |
| Threat | `threat` | Threat description, truncated to 60 characters with `...` suffix if longer |
| CVSS | `cvss_base` | Decimal with one digit (e.g., `7.2`) |
| Exploitability | `exploitability` | Decimal with one digit (e.g., `6.5`) |
| Scalability | `scalability` | Decimal with one digit (e.g., `4.0`) |
| Reachability | `reachability` | Decimal with one digit (e.g., `8.0`) |
| Composite | `composite_score` | Decimal with one digit (e.g., `6.8`) |
| Severity | `severity_band` | `Critical`, `High`, `Medium`, or `Low` |
| SLA | `remediation_sla` | Duration string (e.g., `24h`, `7d`) |
| Disposition | `risk_disposition` | `Mitigate` or `Review` |

**Sort order**: Rows are sorted by `composite_score` descending (highest risk first). When two findings have equal composite scores, secondary sort by `id` in natural alphanumeric order (e.g., `S-1` before `S-2`, `AG-1` before `LLM-1`).

### Truncation Rules

- Component names exceeding 30 characters: truncate to 27 characters and append `...` (e.g., `"LLM Agent Orchestrator Servi..."`)
- Threat descriptions exceeding 60 characters: truncate to 57 characters and append `...` (e.g., `"Attacker injects malicious prompts to bypass guardrail..."`)
- Truncation is applied only in the Scored Threat Table; the Dimensional Breakdown (Section 3) shows full untruncated text

### Numeric Formatting

All dimension scores and composite scores are formatted with exactly one decimal place. Trailing zeros are preserved (e.g., `4.0` not `4`).

### Correlation Group Display

Correlated peer findings appear in the table with their own IDs but carry the primary's scores. No special notation is needed in the table -- peers are indistinguishable from independently scored findings.

---

## Dimensional Breakdown Format

Section 3 of risk-scores.md provides per-finding breakdowns. One subsection per finding, ordered by `composite_score` descending.

### Per-Finding Subsection Template

```markdown
### {id}: {threat_description}

**Component**: {component}
**Category**: {category}
**Composite Score**: {composite_score} ({severity_band})

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | {cvss_base} | 0.35 | {cvss_base * 0.35} |
| Exploitability | {exploitability} | 0.30 | {exploitability * 0.30} |
| Scalability | {scalability} | 0.15 | {scalability * 0.15} |
| Reachability | {reachability} | 0.20 | {reachability * 0.20} |
| **Composite** | | | **{composite_score}** |

**CVSS Vector**: `{cvss_vector}`

**Scoring Rationale**:
- **CVSS**: {1-2 sentence justification for the CVSS base score}
- **Exploitability**: {1-2 sentence justification}
- **Scalability**: {1-2 sentence justification}
- **Reachability**: {1-2 sentence justification referencing the trust zone if available}
```

### Field Rules

| Field | Rule |
|-------|------|
| `{id}` | Finding ID, untruncated |
| `{threat_description}` | Full threat description text, untruncated (no 60-character limit) |
| `{component}` | Full component name, untruncated |
| `{category}` | Human-readable category name (see Category Display Mapping below) |
| `{composite_score}` | Decimal with one digit |
| `{severity_band}` | `Critical`, `High`, `Medium`, or `Low` |
| Dimension scores | Decimal with one digit |
| Weighted values | Decimal with two digits (e.g., `2.52`, `1.95`). Calculated as score multiplied by weight |
| `{cvss_vector}` | Full CVSS 3.1 vector string |
| Scoring Rationale | Brief justification drawn from the assessment. Each line explains key factors for that dimension |

### Correlation Group Display in Breakdown

Correlated peer findings each get their own subsection but include an additional line after the Category line: `**Correlation Group**: Scores inherited from primary finding {primary_id}`. The dimensional table and rationale reflect the primary's assessment.

---

## Category Display Name Mapping

| IR Category | Display Name |
|-------------|-------------|
| `spoofing` | Spoofing |
| `tampering` | Tampering |
| `repudiation` | Repudiation |
| `info-disclosure` | Information Disclosure |
| `denial-of-service` | Denial of Service |
| `privilege-escalation` | Privilege Escalation |
| `agentic` | Agentic Threats |
| `llm` | LLM Threats |

---

## Governance Fields Table Format

Section 4 of risk-scores.md provides a consolidated governance tracking table.

| Column | Source Field | Format |
|--------|-------------|--------|
| ID | `id` | Finding ID as-is |
| Component | `component` | Full component name, untruncated |
| Severity | `severity_band` | `Critical`, `High`, `Medium`, or `Low` |
| Owner | `risk_owner` | Default: `Unassigned` |
| SLA | `remediation_sla` | Duration string (e.g., `24h`, `7d`, `30d`, `90d`) |
| Disposition | `risk_disposition` | `Mitigate` or `Review` |
| Review Date | `review_date` | ISO 8601 date (e.g., `2026-04-03`) |

**Sort order**: Same as the Scored Threat Table -- `composite_score` descending, secondary sort by `id`.

**Rules**:
- Every scored finding must appear (no omissions)
- Owner column always reads `Unassigned` in scorer-generated output
- Review Date calculated per governance rules: scoring date + SLA duration
- Correlation group peers inherit governance fields from the primary

---

## Scoring Methodology Section

Section 5 of risk-scores.md documents how scores were calculated. This section is static for a given schema version.

**Required content**:

1. **Scoring Dimensions**: Table listing four dimensions with weights and descriptions
2. **Default Weights and Rationale**: Why each dimension receives its weight
3. **Composite Score Formula**: Weighted sum formula with actual weights
4. **Severity Band Mapping**: Score ranges to bands with SLAs and dispositions
5. **Data Sources**: Inputs consumed (findings, trust zones, architecture, category defaults)
6. **Reproducibility**: Temperature 0 and ±0.5 tolerance per dimension

**Rules**:
- Content is static -- does not vary between scoring runs
- Weights in formula must match `scoring_weights` in frontmatter
- Severity band boundaries must match `schemas/risk-scoring.yaml` → `severity_bands`
