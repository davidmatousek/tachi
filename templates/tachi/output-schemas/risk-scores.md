# Risk Scores Report

<!--
  Canonical output template for tachi risk scoring reports.

  Schema version : 1.1
  Schema file    : schemas/risk-scoring.yaml
  Finding schema : schemas/finding.yaml

  Producers      : scripts/render-risk-scores.py, the shipped renderer, writes the whole file
                   from the scorer's part files and the threat model. agents/tachi/risk-scorer.md
                   supplies the judgment fields only (the CVSS vector, the sub-scores, the
                   reachability inputs and the rationale prose), and writes none of this file.
  Consumers      : Security engineers, security managers, GRC tools

  Every generated risk scoring output MUST conform to this structure.
  All sections are required, except Section 2a, which appears only when the source threat model
  lists RESOLVED findings. Sections must appear in the order listed.

  Slots: a rationale cell holds the scorer's prose with its slots filled by the renderer, so a
  number or band in a rationale always equals the one in the table beside it. Section 6's Scoring
  Inputs keeps the same prose with its slots unresolved, so that the next run can re-resolve them
  against its own values.

  Escaping: the renderer escapes the scorer's text and the text it reads from the threat model
  (`&`, `<`, `>`, `|`, a backtick and a newline become numeric or named references), and the
  readers in scripts/tachi_parsers.py decode exactly those references.
-->

---

```yaml
---
schema_version: "1.1"
date: "YYYY-MM-DD"
source_file: "{path to input threats.md or threats.sarif}"
classification: "confidential"
scoring_weights:
  cvss_base: 0.35
  exploitability: 0.30
  scalability: 0.15
  reachability: 0.20
baseline:
  source: "{baseline risk-scores.md path or null}"
  inherited_count: "{number of inherited scores or null}"
  fresh_count: "{number of freshly scored findings or null}"
---
```

**Frontmatter fields:**

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Risk scoring schema version. Always `"1.1"` for this release. 1.1 is additive to 1.0: Section 2a, the `Flags` column, Section 3's `**MAESTRO Layer**:` field, `**Correlation Group**:` line, `**Integrity**:` line and weighted table, and Section 6. |
| `date` | string | ISO 8601 date when scoring was performed, as the command passed it to the renderer. The clock never enters this file. Format: `YYYY-MM-DD`. |
| `source_file` | string | Path to the input threat model file that was scored. |
| `classification` | string | Data classification label. Default: `confidential`. |
| `scoring_weights` | object | Weights used for composite calculation. Documents the formula for reproducibility. |
| `baseline.source` | string, nullable | Path to baseline risk-scores.md used for score inheritance. Null when no baseline. |
| `baseline.inherited_count` | integer, nullable | Number of findings with inherited (not freshly computed) scores. Null when no baseline. |
| `baseline.fresh_count` | integer, nullable | Number of findings scored fresh this run. Null when no baseline. |

---

## 1. Executive Summary

{total_findings} open findings were scored on {date}: {critical_count} Critical, {high_count} High, {medium_count} Medium and {low_count} Low.

**Highest-Risk Component**: {highest_risk_component} — {highest_risk_component_finding_count} finding(s), max composite {highest_risk_component_max_composite}

**Resolved findings** (Section 2a, outside the distribution below): {resolved_count}

| Metric | Value |
|--------|-------|
| Scoring date | {date} |
| Source file | `{source_file}` |
| Schema version | {schema_version} |

**Severity Distribution:**

| Severity | Count | Percentage |
|----------|-------|------------|
| Critical | {critical_count} | {critical_pct}% |
| High | {high_count} | {high_pct}% |
| Medium | {medium_count} | {medium_pct}% |
| Low | {low_count} | {low_pct}% |
| **Total** | **{total_findings}** | **100%** |

The first line is the one templated sentence of this section: the renderer fills it from the counts it computed, because no batch of the scorer sees every finding. It states the open count and then the four bands in that order, and no other line of the section does. The Severity Distribution table keeps the shape that `parse_risk_scores_severity` reads (a `Severity` and a `Count` column, a row for each band and a `Total` row), because the report and infographic extractors take their severity counts from it. The counts cover open findings only. The percentages are whole numbers that sum to 100, by largest remainder (ties go to the band name that sorts first), and are all zero when there are no open findings.

> When trust zone data is unavailable, a default reachability score of 5.0 is applied. If this condition was triggered, note it here: {reachability_warning}

---

## 2. Scored Threat Table

Findings sorted by Composite score descending (highest risk first), and by finding ID within equal scores. Boundary values map to the higher severity band (e.g., 7.0 = High, 9.0 = Critical).

| ID | Source | Component | Threat | CVSS | Exploit. | Scale. | Reach. | Composite | Severity | SLA | Disposition | Flags |
|----|--------|-----------|--------|------|----------|--------|--------|-----------|----------|-----|-------------|-------|
| {id} | {score_source} | {component} | {threat} | {cvss_base} | {exploitability} | {scalability} | {reachability} | {composite_score} | {severity_band} | {remediation_sla} | {risk_disposition} | {flags} |

### Column Definitions

| Column | Description |
|--------|-------------|
| **ID** | Original finding identifier from the threat model (e.g., `S-1`, `T-2`, `AG-1`, `LLM-3`). Preserves the source finding ID without modification. |
| **Source** | Score source: `inherited` (a carried finding: its inputs come from the baseline, and the renderer recomputed its derived fields) or `fresh` (the scorer assessed it this run, as a NEW or UPDATED finding or one with no usable baseline row). When no baseline is present, all findings show `fresh`. |
| **Component** | Target component name as identified in the threat model. |
| **Threat** | Threat description, truncated to fit table width. Full description available in the Dimensional Breakdown (Section 3). |
| **CVSS** | CVSS 3.1 base score (0.0-10.0). Derived from attack vector, attack complexity, privileges required, user interaction, scope, and CIA impact, then bounded and elevated by the asset-sensitivity pass where those apply. Full vector string shown in Section 3. |
| **Exploit.** | Exploitability score (0.0-10.0). Average of four sub-dimensions, rounded half up to one decimal: known techniques, attack complexity, tooling availability, and skill level required. |
| **Scale.** | Scalability score (0.0-10.0). Average of four sub-dimensions, rounded half up to one decimal: scriptability, target scope, resource requirements, and detection difficulty. |
| **Reach.** | Reachability score (0.0-10.0). Derived from trust zone placement: Untrusted/External = 8.0-10.0, Semi-Trusted/Application = 4.0-7.0, Trusted/Internal = 1.0-4.0. Default 5.0 when trust zone data is unavailable. |
| **Composite** | Weighted composite score (0.0-10.0). Formula: `(0.35 x CVSS) + (0.30 x Exploit.) + (0.15 x Scale.) + (0.20 x Reach.)`, rounded half up to one decimal. |
| **Severity** | Severity band mapped from composite score: Critical (9.0-10.0), High (7.0-8.9), Medium (4.0-6.9), Low (0.0-3.9). |
| **SLA** | Default remediation SLA driven by severity: Critical = 24h, High = 7d, Medium = 30d, Low = 90d. A baseline value that differs from its band's default is an override, and is carried as it was. |
| **Disposition** | Default risk disposition driven by severity: Critical/High = Mitigate, Medium/Low = Review. May be overridden in the Governance Fields table (Section 4). |
| **Flags** | The finding's integrity flags, as kind names in this fixed order: `corrected`, `unverifiable`, `unchecked`, `divergent`, `override`, `retagged`, `reused-id`, `input`. `—` when the finding has none. Section 6 lists each flag with its field and cause. |

> **Correlated findings**: For correlation groups (Section 4a of the source threat model), the primary finding is scored independently. A NEW or UPDATED peer takes the primary's vector and scores. An UNCHANGED peer keeps its own score, and is flagged `divergent` when that score differs from its primary's.

---

## 2a. Resolved Findings

Findings that the source threat model lists in Section 4c as RESOLVED. Each row keeps the values it last had in the baseline, verbatim: the renderer recomputes nothing for it, and the SLA clock doesn't run for it. The Executive Summary counts these rows apart from the distribution, and neither SARIF file carries them. This section appears only when there is at least one such finding.

| ID | Source | Component | Threat | CVSS | Exploit. | Scale. | Reach. | Composite | Severity | SLA | Disposition | Status | Owner | Review Date | Flags |
|----|--------|-----------|--------|------|----------|--------|--------|-----------|----------|-----|-------------|--------|-------|-------------|-------|
| {id} | inherited | {component} | {threat} | {cvss_base} | {exploitability} | {scalability} | {reachability} | {composite_score} | {severity_band} | {remediation_sla} | {risk_disposition} | RESOLVED | {risk_owner} | {review_date} | resolved |

The first twelve columns are Section 2's. `Status` is always `RESOLVED`, and the only flag a resolved row carries is `resolved`. A value the baseline doesn't hold, which is every score and the review date of a finding that only Section 4c lists, reads `—`: the renderer never computes one for a resolved row. Readers of Section 2 stop at its table, so these rows never count as open.

---

## 3. Dimensional Breakdown

Per-finding detail showing the full scoring rationale for each dimension. One subsection per open finding, ordered by composite score descending (matching Section 2 sort order).

### {id} — {component}

**Threat**: {threat_full_description}

**Category**: {category} | **MAESTRO Layer**: {maestro_layer} | **Original Risk Level**: {original_risk_level} | **Composite**: {composite_score} ({severity_band})

`{maestro_layer}` is the finding's MAESTRO layer as the threat model records it (for example `L7 — Agent Ecosystem`), or `Unclassified`. It is the same string as the `maestro-layer` property of the finding's result in risk-scores.sarif.

**Correlation Group**: {correlation_group}

The `**Correlation Group**:` line appears only for a finding that Section 4a of the source threat model lists in a correlation group. It names the group and says whether the finding is the group's primary, a NEW or UPDATED peer that takes its primary's assessment, or an UNCHANGED peer that keeps its own score.

**Integrity**: {flags_as_kind_field_cause}

The `**Integrity**:` line appears only for a finding that carries at least one flag. It lists each flag as `kind:field:cause`, comma-separated, as Section 6's Score Flags table does.

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | {cvss_base} | 0.35 | {cvss_base_weighted} |
| Exploitability | {exploitability} | 0.30 | {exploitability_weighted} |
| Scalability | {scalability} | 0.15 | {scalability_weighted} |
| Reachability | {reachability} | 0.20 | {reachability_weighted} |
| **Composite** | | | **{composite_score}** |

Every finding has this table, after its optional lines. A Weighted value is the stored one-decimal score times its weight, computed in exact decimal arithmetic and rounded half up to two decimals, so it always shows two decimals (`8.3 x 0.35 = 2.905` shows `2.91`, and `2.5 x 0.20 = 0.50` shows `0.50`). The Composite cell repeats the composite score. The renderer rounds that once, from the exact sum of the four products, and does not add up the four rounded cells, so the cells can add to as much as a hundredth more.

#### CVSS 3.1 Base

**Score**: {cvss_base} | **Vector**: `{cvss_vector}`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | {av_value} | {av_rationale} |
| Attack Complexity (AC) | {ac_value} | {ac_rationale} |
| Privileges Required (PR) | {pr_value} | {pr_rationale} |
| User Interaction (UI) | {ui_value} | {ui_rationale} |
| Scope (S) | {s_value} | {s_rationale} |
| Confidentiality (C) | {c_value} | {c_rationale} |
| Integrity (I) | {i_value} | {i_rationale} |
| Availability (A) | {a_value} | {a_rationale} |

{cvss_rationale}

A metric's rationale is the scorer's optional per-metric prose, and reads `—` when it wrote none. The metric values come from the vector.

#### Exploitability

**Score**: {exploitability} (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | {exploit_known_techniques} | {exploit_known_techniques_rationale} |
| Attack Complexity | {exploit_attack_complexity} | {exploit_attack_complexity_rationale} |
| Tooling Availability | {exploit_tooling_availability} | {exploit_tooling_availability_rationale} |
| Skill Level | {exploit_skill_level} | {exploit_skill_level_rationale} |

{exploitability_rationale}

#### Scalability

**Score**: {scalability} (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | {scale_scriptability} | {scale_scriptability_rationale} |
| Target Scope | {scale_target_scope} | {scale_target_scope_rationale} |
| Resource Requirements | {scale_resource_requirements} | {scale_resource_requirements_rationale} |
| Detection Difficulty | {scale_detection_difficulty} | {scale_detection_difficulty_rationale} |

{scalability_rationale}

#### Reachability

**Score**: {reachability} | **Trust Zone**: {trust_zone} ({trust_level})

{reachability_rationale}

---

*Repeat the above block for each scored finding, ordered by composite score descending.*

---

## 4. Governance Fields

Remediation tracking metadata for each scored finding. Default values are severity-driven and intended for manual override by security managers during risk review.

| ID | Severity | Owner | SLA | Disposition | Review Date |
|----|----------|-------|-----|-------------|-------------|
| {id} | {severity_band} | {risk_owner} | {remediation_sla} | {risk_disposition} | {review_date} |

### Field Definitions

| Field | Description | Default |
|-------|-------------|---------|
| **ID** | Finding identifier matching Section 2. | Preserved from source threat model. |
| **Severity** | Severity band from composite score. | Critical (9.0-10.0), High (7.0-8.9), Medium (4.0-6.9), Low (0.0-3.9). |
| **Owner** | Responsible party for remediation or risk acceptance. | `Unassigned` for a fresh finding — populate during risk review. A human-assigned owner is carried forward from the baseline and never overwritten. |
| **SLA** | Remediation deadline relative to scoring date. | Critical = 24 hours, High = 7 days, Medium = 30 days, Low = 90 days. |
| **Disposition** | Risk treatment decision. | Critical/High = `Mitigate`, Medium/Low = `Review`. Valid values: Mitigate, Review, Accept, Transfer. |
| **Review Date** | Date by which the disposition must be reviewed. | Scoring date + SLA duration (e.g., scoring on 2026-03-27 with 7d SLA = 2026-04-03). A carried finding keeps its review date while its band holds. |

### Override Guidance

- **Owner**: Assign during remediation planning. Each finding should have a named owner before the SLA expires.
- **Disposition**: Change from default when a risk acceptance or transfer decision is made. Document the justification in your risk register.
  - `Accept` — Risk is acknowledged and accepted at the current level. Requires documented justification and management approval.
  - `Transfer` — Risk is transferred to a third party (e.g., insurance, vendor SLA). Document the transfer mechanism.
- **SLA**: Override when organizational policy defines different remediation windows. The default SLAs follow industry-standard baselines (24h/7d/30d/90d).
- **Review Date**: Automatically recalculates when SLA is overridden.

The next run carries an `Accept` or `Transfer` disposition, and an SLA or disposition that differs from the stored band's default, as it finds it, and flags it `override` in Section 2 and Section 6. A model slip that looks like an override therefore stays visible.

---

## 5. Scoring Methodology

This section documents the quantitative scoring model used to produce the risk scores in this report. All scores are derived from the threat findings identified during threat modeling and are intended to replace qualitative risk ratings with data-backed, reproducible numeric assessments.

### 5.1 Scoring Dimensions

Each threat finding is assessed across four independent dimensions, each producing a score on a 0.0 to 10.0 scale.

| Dimension | Weight | What It Measures |
|-----------|--------|------------------|
| **CVSS Base** | 35% | Intrinsic severity of the vulnerability using CVSS 3.1 base metrics: attack vector, attack complexity, privileges required, user interaction, scope, and confidentiality/integrity/availability impact. Each finding includes the full CVSS vector string for auditability. |
| **Exploitability** | 30% | Practical likelihood of exploitation based on known attack techniques, tooling availability, required skill level, and attack complexity. Higher scores indicate threats with well-documented exploit paths and readily available tooling. |
| **Scalability** | 15% | Potential for automated, large-scale exploitation based on scriptability, breadth of target scope, resource requirements for the attacker, and difficulty of detection. Higher scores indicate threats that can be weaponized across many targets with minimal effort. |
| **Reachability** | 20% | Exposure of the targeted component within the system's trust boundary architecture. Derived from trust zone data in the threat model and supplemented by architecture documentation when available. Higher scores indicate components directly exposed to untrusted networks. |

### 5.2 Default Weights and Rationale

The default weight allocation reflects the following priorities:

- **CVSS Base (35%)** receives the highest weight because intrinsic vulnerability severity is the strongest predictor of potential damage. CVSS 3.1 is an industry-standard metric with well-understood interpretation.
- **Exploitability (30%)** is weighted second because a severe vulnerability that is difficult to exploit in practice poses less immediate risk than one with known, tooled attack paths.
- **Reachability (20%)** accounts for architectural context. A critical vulnerability behind multiple trust boundaries and authentication layers presents less operational risk than the same vulnerability on an internet-facing endpoint.
- **Scalability (15%)** receives the lowest weight because while automation potential increases aggregate risk, it is less deterministic than the other dimensions and often correlates with exploitability.

These weights are fixed for this scoring run and are recorded in the report frontmatter for reproducibility.

### 5.3 Composite Score Formula

The composite risk score for each finding is calculated as a weighted sum of the four dimension scores:

```
Composite = (0.35 x CVSS Base) + (0.30 x Exploitability) + (0.15 x Scalability) + (0.20 x Reachability)
```

The sum runs over the stored one-decimal values and is rounded half up to one decimal (a composite of 4.55 is 4.6). The composite score is bounded to the 0.0-10.0 range. Because each dimension is independently scored on a 0.0-10.0 scale and the weights sum to 1.0, the composite inherently falls within this range.

### 5.4 Severity Band Mapping

Composite scores are mapped to severity bands that drive default governance actions:

| Severity | Composite Score Range | Default SLA | Default Disposition |
|----------|-----------------------|-------------|---------------------|
| **Critical** | 9.0 -- 10.0 | 24 hours | Mitigate |
| **High** | 7.0 -- 8.9 | 7 days | Mitigate |
| **Medium** | 4.0 -- 6.9 | 30 days | Review |
| **Low** | 0.0 -- 3.9 | 90 days | Review |

Boundary values map to the higher band (e.g., a composite score of exactly 7.0 maps to High, not Medium). These bands are aligned with the severity classifications defined in `schemas/output.yaml` to maintain backward compatibility with existing tachi threat model output.

### 5.5 Data Sources

Scoring draws on the following inputs:

- **Threat findings**: Parsed from `threats.md` (markdown table format) or `threats.sarif` (SARIF 2.1.0 JSON). All original threat metadata (ID, component, category, description, likelihood, impact) is preserved through the scoring pipeline.
- **Trust zone data**: Extracted from `threats.md` Section 2 (trust zone table) as the primary source for reachability scoring. Components in Untrusted/External zones score 8.0-10.0 reachability; Semi-Trusted/Application zones score 4.0-7.0; Trusted/Internal zones score 1.0-4.0.
- **Architecture documentation**: When `architecture.md` is available, it provides supplementary context such as authentication barriers and network exposure details that refine the baseline reachability score derived from trust zones.
- **Category default vectors**: CVSS 3.1 baseline vectors are defined per STRIDE threat category in `schemas/risk-scoring.yaml`. This includes tachi-specific defaults for AI threat categories (agentic and LLM) that lack standard CVSS mappings. Per-threat analysis may refine these baselines based on the specific threat description.
- **The baseline**: When a baseline `risk-scores.md` is available, a carried finding's inputs (its vector, sub-scores, reachability inputs and human governance fields) come from it, and Section 6 records which baseline was used.

When trust zone data is unavailable (no Section 2 in `threats.md` and no `architecture.md`), a default reachability score of 5.0 is applied with a warning in the output.

### 5.6 Reproducibility

The scorer's assessments (the CVSS vector, the eight sub-scores and the reachability inputs) are produced by an LLM at temperature 0. For the same threat model input, each of them is expected to be reproducible within a **+/- 0.5 tolerance** across runs. This tolerance reflects the inherent variability in LLM-based analysis and is considered acceptable for risk prioritization purposes.

Everything the renderer computes from those assessments is deterministic: the averages, the CVSS base score, the composite, the severity band, the SLA and the review date. The renderer uses exact decimal arithmetic and takes the date as an input, so the same parts and the same date give the same file, byte for byte. The composite formula, weights, and severity band mappings carry no tolerance.

---

## 6. Score Integrity

What the renderer checked, corrected or could not check, and the inputs it scored from. A first run with no baseline has nothing to correct, so its Score Flags table is empty.

### Integrity Summary

| Kind | Cause | Count |
|------|-------|-------|
| {kind} | {cause} | {count} |

**Normalized (rounding only)**: {normalized_count}

**Baseline source**: {baseline_source_or_none}

**Tag source**: {tag_source_block_or_architecture_or_none}

The table counts the flags of Section 6's Score Flags by kind and cause. A difference that comes only from rounding, and leaves the band, SLA, disposition and review date as they were, is normalized and counted here, never flagged per finding. The tag source is the one the asset-sensitivity pass used for the whole run: the `## Affected Assets` block of `threats.md`, the architecture file's own tags, or none. It is marked unverified when the block was used and no architecture file existed to check it against.

### Score Flags

| ID | Flag | Field | Stored | Rendered | Cause |
|----|------|-------|--------|----------|-------|
| {id} | {kind} | {field} | {stored_value} | {rendered_value} | {cause} |

One row for each flag, in finding-ID order (prefix rank `S`, `T`, `R`, `I`, `D`, `E`, `AG`, `AGP`, `LLM`, `OI`, `MI`, `TE`, then the numeric suffix as an integer). `Stored` is the value the baseline held, `Rendered` is the value this file shows, and `Cause` says why they differ. The kinds are `corrected` (a stored value the renderer recomputed to a different one), `unverifiable` (no vector to check the score against), `unchecked` (a check that depends on an ambiguity, so the value is kept), `divergent` (an UNCHANGED peer whose score differs from its primary's, or a NEW or UPDATED peer whose own asset tags moved its score), `override` (a human choice carried as it was), `retagged` (a change that the asset tags alone explain), `reused-id` (a NEW finding whose ID the baseline used) and `input` (a kept input with a problem, a narrative field that took its fixed sentence, or a prose field cut at its length limit).

### Input Issues

Rows and files that the renderer couldn't read or fully use, one entry each, naming the file, the section and the problem: a baseline file that is unreadable (its owners, SLAs and dispositions weren't carried), a baseline row that has no usable form, a vector that the markdown and the SARIF disagree on, and a source row it couldn't parse. `None.` when there are none.

### Scoring Inputs

| ID | Field | Value |
|----|-------|-------|
| {id} | {field} | {value} |

One row for each value that the next run needs to carry this finding forward, so that it reads them from one place. The rows go in finding-ID order, and within a finding in the order of the scorer's part (`cvss_vector`, the exploitability and scalability sub-scores, `reachability.*`, `rationale.*`, then `metric_rationale.*` and `subscore_rationale.*` where the scorer wrote them), with these last: `score_bounds` (the low and high bound, joined by `,`), `tags` (the asset tags the run used, sorted and joined by `,`, and empty for none) and `scored_on` (`YYYY-MM-DD`). A field name is a dotted address, such as `exploitability.known_techniques` or `rationale.cvss`. A field with no value writes no row. Narrative values keep their slot tokens, and every value is escaped on write.

<!-- tachi-provenance: renderer=render-risk-scores.py; version={X.Y.Z}; input-digest=sha256:{hex} -->
