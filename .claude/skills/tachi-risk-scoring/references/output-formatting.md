---
source_agent: risk-scorer
extracted_from: .claude/agents/tachi/risk-scorer.md
version: 1.0.0
---

# Output Formatting Reference

Markdown output formatting specifications for risk-scores.md — column definitions, truncation rules, numeric formatting, display name mappings, and section templates.

The shipped renderer (`scripts/render-risk-scores.py`) writes the whole file, to the structure in `templates/tachi/output-schemas/risk-scores.md`, and this reference documents how it formats the tables. The risk-scorer agent writes none of it. Its rationale prose reaches the file with the slots filled in, and the renderer escapes it.

---

## Scored Threat Table Column Definitions

The scored threat table (Section 2 of risk-scores.md) contains all scored findings in a single reference table.

| Column | Source Field | Format |
|--------|-------------|--------|
| ID | `id` | Finding ID as-is (e.g., `S-1`, `AG-3`) |
| Source | `score_source` | `inherited` (a carried finding) or `fresh` (assessed this run). A copied peer takes its primary's source |
| Component | `component` | Component name, truncated to 30 characters with `...` suffix if longer |
| Threat | `threat` | Threat description, truncated to 60 characters with `...` suffix if longer |
| CVSS | `cvss_base` | Decimal with one digit (e.g., `7.2`) |
| Exploitability | `exploitability` | Decimal with one digit (e.g., `6.5`) |
| Scalability | `scalability` | Decimal with one digit (e.g., `4.0`) |
| Reachability | `reachability` | Decimal with one digit (e.g., `8.0`) |
| Composite | `composite_score` | Decimal with one digit (e.g., `6.8`) |
| Severity | `severity_band` | `Critical`, `High`, `Medium`, or `Low` |
| SLA | `remediation_sla` | Duration string (e.g., `24h`, `7d`) |
| Disposition | `risk_disposition` | `Mitigate` or `Review`. A carried Accept or Transfer is shown as it was |
| Flags | the finding's integrity flags | The flag kinds, comma-separated, in this fixed order: `corrected`, `unverifiable`, `unchecked`, `divergent`, `override`, `retagged`, `reused-id`, `input`. `—` when there are none |

**Sort order**: Rows are sorted by `composite_score` descending (highest risk first). When two findings have equal composite scores, the secondary sort is the finding-ID total order (S-2): first by prefix rank, which is `S`, `T`, `R`, `I`, `D`, `E`, `AG`, `AGP`, `LLM`, `OI`, `MI`, `TE`, and then by the numeric suffix as an integer. So `S-1` comes before `S-2`, `AG-1` before `LLM-1`, `T-9` before `T-10`, and `S-1` before `D-1`. This replaces the earlier "natural alphanumeric" order, which ranked the prefixes alphabetically (`D-1` before `S-1`), so rows with equal scores can come in a different order than in an earlier run.

### Truncation Rules

- Component names exceeding 30 characters: truncate to 27 characters and append `...` (e.g., `"LLM Agent Orchestrator Servi..."`)
- Threat descriptions exceeding 60 characters: truncate to 57 characters and append `...` (e.g., `"Attacker injects malicious prompts to bypass guardrail..."`)
- Truncation is applied only in the Scored Threat Table; the Dimensional Breakdown (Section 3) shows full untruncated text
- The renderer truncates the raw text first, and escapes what is left afterwards (ADR-050 D3), so a numeric character reference such as `&lt;` is never cut in half. A cell holds the escaped text, and the readers decode it

### Numeric Formatting

All dimension scores and composite scores are formatted with exactly one decimal place. Trailing zeros are preserved (e.g., `4.0` not `4`).

### Correlation Group Display

Correlated peer findings appear in the table with their own IDs. A NEW or UPDATED peer takes its primary's assessment and is scored with its own asset tags, so it shows its primary's scores when the tags are equal, and `divergent` in the Flags column when its own tags moved its composite. An UNCHANGED peer keeps its own scores and shows `divergent` when they differ from its primary's. No other notation is needed in the table -- a peer looks like any independently scored finding.

### Resolved Findings (Section 2a)

Findings that Section 4c of the source threat model lists as RESOLVED are listed in their own table after Section 2, under `## 2a. Resolved Findings`. It has Section 2's columns, then `Status` (always `RESOLVED`), `Owner` and `Review Date`, then `Flags` (only `resolved`). Each value is the baseline's, verbatim, and is never recomputed. The section is omitted when there are none.

---

## Dimensional Breakdown Format

Section 3 of risk-scores.md provides per-finding breakdowns. One subsection per open finding, ordered by `composite_score` descending. The layout is the one in Section 3 of `templates/tachi/output-schemas/risk-scores.md`, and both describe what the renderer writes.

### Per-Finding Subsection Template

```markdown
### {id} — {component}

**Threat**: {threat_description}

**Category**: {category} | **MAESTRO Layer**: {maestro_layer} | **Original Risk Level**: {original_risk_level} | **Composite**: {composite_score} ({severity_band})

**Correlation Group**: {correlation_group}   (only for a finding in a correlation group)

**Integrity**: {flags as kind:field:cause, comma-separated}   (only when the finding carries a flag)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | {cvss_base} | 0.35 | {cvss_base x 0.35} |
| Exploitability | {exploitability} | 0.30 | {exploitability x 0.30} |
| Scalability | {scalability} | 0.15 | {scalability x 0.15} |
| Reachability | {reachability} | 0.20 | {reachability x 0.20} |
| **Composite** | | | **{composite_score}** |

#### CVSS 3.1 Base

{the Score and Vector line, the metric table and the CVSS rationale}

#### Exploitability

{the Score line, the four sub-dimension rows and the rationale}

#### Scalability

{the Score line, the four sub-dimension rows and the rationale}

#### Reachability

{the Score and Trust Zone line and the rationale}
```

### Field Rules

| Field | Rule |
|-------|------|
| `{id}` | Finding ID, untruncated |
| `{component}` | Full component name, untruncated |
| `{threat_description}` | Full threat description text, untruncated (no 60-character limit) |
| `{category}` | The category ID, as `tachi_scoring.category_for_prefix` returns it for the finding's ID prefix, such as `info-disclosure` or `agentic` |
| `{maestro_layer}` | The finding's MAESTRO layer as the threat model records it (such as `L7 — Agent Ecosystem`), or `Unclassified`. It is the string that the finding's SARIF result carries as `maestro-layer` |
| `{original_risk_level}` | The risk level that the threat model gave the finding |
| `{composite_score}` | Decimal with one digit |
| `{severity_band}` | `Critical`, `High`, `Medium`, or `Low` |
| Dimension scores | Decimal with one digit |
| Weight | `0.35`, `0.30`, `0.15` and `0.20`, as in the frontmatter's `scoring_weights` |
| Weighted values | Always two decimals (e.g., `2.52`, `1.95`, `0.50`). The stored one-decimal score multiplied by its weight in exact decimal arithmetic, then rounded half up to two decimals, never with a float: `8.3 x 0.35` is `2.905` and shows `2.91` |
| Composite row | The composite score, which the renderer rounds once, half up to one decimal, from the exact sum of the four products. It is not the sum of the four shown Weighted values, so those can add to as much as a hundredth more |
| `{cvss_vector}` | Full CVSS 3.1 vector string, or `—` when the finding has none |
| Rationale | The agent's prose for that dimension, under its `####` heading, with its slots filled by the renderer, so every number in it equals the table's. A fallback sentence stands in for a field that broke the narrative rules, and Section 6 flags it |

### Correlation Group Display in Breakdown

A finding in a correlation group has a `**Correlation Group**:` line after the Category line, and every member has its own subsection. A primary's line names its group and its peers (up to ten, then a count). A NEW or UPDATED peer takes its primary's assessment, so its rationale is its primary's text with the slots filled against the peer's own values, and its table is scored with the peer's own asset tags. With equal tags the table equals its primary's. Its line reads `Scores inherited from primary finding {primary_id} ({group})` while its table equals its primary's, and `Assessment inherited from primary finding {primary_id} ({group}); scored with its own asset tags` when its own tags moved its CVSS score. A peer whose own tags moved its composite also carries the `divergent` flag in its Integrity line. An UNCHANGED peer's line says that it keeps its own score, its table shows its own scores, and its Integrity line carries `divergent` when they differ from its primary's.

---

## Category Display Name Mapping

The renderer writes the category ID itself on a finding's Category line. This table gives the display name of each category, for prose that names one.

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
| Owner | `risk_owner` | A baseline's owner, carried as it was. Default for a finding without one: `Unassigned` |
| SLA | `remediation_sla` | Duration string (e.g., `24h`, `7d`, `30d`, `90d`) |
| Disposition | `risk_disposition` | `Mitigate` or `Review` |
| Review Date | `review_date` | ISO 8601 date (e.g., `2026-04-03`) |

**Sort order**: Same as the Scored Threat Table -- `composite_score` descending, secondary sort by `id`.

**Rules**:
- Every scored finding must appear (no omissions)
- Owner column reads `Unassigned` for a fresh finding, and shows the baseline's owner for a carried one
- Review Date calculated per governance rules: scoring date + SLA duration, with the carried-forward rules in `severity-bands.md`
- NEW and UPDATED correlation group peers take the governance of their own band, as any NEW or UPDATED finding does (fresh when NEW, the UPDATED rule otherwise), and an UPDATED peer keeps its own owner

---

## Scoring Methodology Section

Section 5 of risk-scores.md documents how scores were calculated. This section is static for a given schema version.

**Required content**:

1. **Scoring Dimensions**: Table listing four dimensions with weights and descriptions
2. **Default Weights and Rationale**: Why each dimension receives its weight
3. **Composite Score Formula**: Weighted sum formula with actual weights
4. **Severity Band Mapping**: Score ranges to bands with SLAs and dispositions
5. **Data Sources**: Inputs consumed (findings, trust zones, architecture, category defaults)
6. **Reproducibility**: Temperature 0 and ±0.5 tolerance for the agent's assessments, and exact, deterministic arithmetic for everything the renderer computes

**Rules**:
- Content is static -- does not vary between scoring runs
- Weights in formula must match `scoring_weights` in frontmatter
- Severity band boundaries must match `schemas/risk-scoring.yaml` → `severity_bands`

---

## Score Integrity (Section 6)

Section 6, `## 6. Score Integrity`, records what the renderer checked, corrected or could not check, and the inputs it scored from. Its four subsections, in order, are `### Integrity Summary` (counts by kind and cause, the normalized count, and the baseline and tag sources), `### Score Flags` (`ID | Flag | Field | Stored | Rendered | Cause`, in finding-ID order), `### Input Issues` and `### Scoring Inputs` (`ID | Field | Value`, one row for each input value, with the agent's narrative text kept with its slot tokens). The template documents each table.
