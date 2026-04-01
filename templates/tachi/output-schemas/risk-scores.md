# Risk Scores Report

<!--
  Canonical output template for tachi risk scoring reports.

  Schema version : 1.0
  Schema file    : schemas/risk-scoring.yaml
  Finding schema : schemas/finding.yaml

  Producers      : agents/tachi/risk-scorer.md
  Consumers      : Security engineers, security managers, GRC tools

  Every generated risk scoring output MUST conform to this structure.
  All sections are required. Sections must appear in the order listed.
-->

---

```yaml
---
schema_version: "1.0"
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
| `schema_version` | string | Risk scoring schema version. Always `"1.0"` for this release. |
| `date` | string | ISO 8601 date when scoring was performed. Format: `YYYY-MM-DD`. |
| `source_file` | string | Path to the input threat model file that was scored. |
| `classification` | string | Data classification label. Default: `confidential`. |
| `scoring_weights` | object | Weights used for composite calculation. Documents the formula for reproducibility. |
| `baseline.source` | string, nullable | Path to baseline risk-scores.md used for score inheritance. Null when no baseline. |
| `baseline.inherited_count` | integer, nullable | Number of findings with inherited (not freshly computed) scores. Null when no baseline. |
| `baseline.fresh_count` | integer, nullable | Number of findings scored fresh this run. Null when no baseline. |

---

## 1. Executive Summary

**{total_findings}** threats scored | **{critical_count}** Critical | **{high_count}** High | **{medium_count}** Medium | **{low_count}** Low

**Highest-Risk Component**: {highest_risk_component} — {highest_risk_component_finding_count} finding(s), max composite {highest_risk_component_max_composite}

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

> When trust zone data is unavailable, a default reachability score of 5.0 is applied. If this condition was triggered, note it here: {reachability_warning}

---

## 2. Scored Threat Table

Findings sorted by Composite score descending (highest risk first). Boundary values map to the higher severity band (e.g., 7.0 = High, 9.0 = Critical).

| ID | Source | Component | Threat | CVSS | Exploit. | Scale. | Reach. | Composite | Severity | SLA | Disposition |
|----|--------|-----------|--------|------|----------|--------|--------|-----------|----------|-----|-------------|
| {id} | {score_source} | {component} | {threat} | {cvss_base} | {exploitability} | {scalability} | {reachability} | {composite_score} | {severity_band} | {remediation_sla} | {risk_disposition} |

### Column Definitions

| Column | Description |
|--------|-------------|
| **ID** | Original finding identifier from the threat model (e.g., `S-1`, `T-2`, `AG-1`, `LLM-3`). Preserves the source finding ID without modification. |
| **Source** | Score source: `inherited` (scores copied from baseline for UNCHANGED/RESOLVED findings) or `fresh` (scores computed this run for NEW/UPDATED findings). When no baseline is present, all findings show `fresh`. |
| **Component** | Target component name as identified in the threat model. |
| **Threat** | Threat description, truncated to fit table width. Full description available in the Dimensional Breakdown (Section 3). |
| **CVSS** | CVSS 3.1 base score (0.0-10.0). Derived from attack vector, attack complexity, privileges required, user interaction, scope, and CIA impact. Full vector string shown in Section 3. |
| **Exploit.** | Exploitability score (0.0-10.0). Average of four sub-dimensions: known techniques, attack complexity, tooling availability, and skill level required. |
| **Scale.** | Scalability score (0.0-10.0). Average of four sub-dimensions: scriptability, target scope, resource requirements, and detection difficulty. |
| **Reach.** | Reachability score (0.0-10.0). Derived from trust zone placement: Untrusted/External = 8.0-10.0, Semi-Trusted/Application = 4.0-7.0, Trusted/Internal = 1.0-4.0. Default 5.0 when trust zone data is unavailable. |
| **Composite** | Weighted composite score (0.0-10.0). Formula: `(0.35 x CVSS) + (0.30 x Exploit.) + (0.15 x Scale.) + (0.20 x Reach.)`. |
| **Severity** | Severity band mapped from composite score: Critical (9.0-10.0), High (7.0-8.9), Medium (4.0-6.9), Low (0.0-3.9). |
| **SLA** | Default remediation SLA driven by severity: Critical = 24h, High = 7d, Medium = 30d, Low = 90d. |
| **Disposition** | Default risk disposition driven by severity: Critical/High = Mitigate, Medium/Low = Review. May be overridden in the Governance Fields table (Section 4). |

> **Correlated findings**: For correlation groups (Section 4a of the source threat model), the primary finding is scored independently. Correlated peer findings inherit the primary's scores to maintain group consistency.

---

## 3. Dimensional Breakdown

Per-finding detail showing the full scoring rationale for each dimension. One subsection per finding, ordered by composite score descending (matching Section 2 sort order).

### {id} — {component}

**Threat**: {threat_full_description}

**Category**: {category} | **Original Risk Level**: {original_risk_level} | **Composite**: {composite_score} ({severity_band})

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

#### Exploitability

**Score**: {exploitability} (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | {exploit_known_techniques} | {exploit_known_techniques_rationale} |
| Attack Complexity | {exploit_attack_complexity} | {exploit_attack_complexity_rationale} |
| Tooling Availability | {exploit_tooling_availability} | {exploit_tooling_availability_rationale} |
| Skill Level | {exploit_skill_level} | {exploit_skill_level_rationale} |

#### Scalability

**Score**: {scalability} (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | {scale_scriptability} | {scale_scriptability_rationale} |
| Target Scope | {scale_target_scope} | {scale_target_scope_rationale} |
| Resource Requirements | {scale_resource_requirements} | {scale_resource_requirements_rationale} |
| Detection Difficulty | {scale_detection_difficulty} | {scale_detection_difficulty_rationale} |

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
| **Owner** | Responsible party for remediation or risk acceptance. | `Unassigned` — populate during risk review. |
| **SLA** | Remediation deadline relative to scoring date. | Critical = 24 hours, High = 7 days, Medium = 30 days, Low = 90 days. |
| **Disposition** | Risk treatment decision. | Critical/High = `Mitigate`, Medium/Low = `Review`. Valid values: Mitigate, Review, Accept, Transfer. |
| **Review Date** | Date by which the disposition must be reviewed. | Scoring date + SLA duration (e.g., scoring on 2026-03-27 with 7d SLA = 2026-04-03). |

### Override Guidance

- **Owner**: Assign during remediation planning. Each finding should have a named owner before the SLA expires.
- **Disposition**: Change from default when a risk acceptance or transfer decision is made. Document the justification in your risk register.
  - `Accept` — Risk is acknowledged and accepted at the current level. Requires documented justification and management approval.
  - `Transfer` — Risk is transferred to a third party (e.g., insurance, vendor SLA). Document the transfer mechanism.
- **SLA**: Override when organizational policy defines different remediation windows. The default SLAs follow industry-standard baselines (24h/7d/30d/90d).
- **Review Date**: Automatically recalculates when SLA is overridden.

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

The composite score is bounded to the 0.0-10.0 range. Because each dimension is independently scored on a 0.0-10.0 scale and the weights sum to 1.0, the composite inherently falls within this range.

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

When trust zone data is unavailable (no Section 2 in `threats.md` and no `architecture.md`), a default reachability score of 5.0 is applied with a warning in the output.

### 5.6 Reproducibility

Scoring is performed at LLM temperature 0 to maximize consistency. For the same threat model input, each dimension score is expected to be reproducible within a **+/- 0.5 tolerance** across runs. This tolerance reflects the inherent variability in LLM-based analysis and is considered acceptable for risk prioritization purposes.

Factors that may cause minor score variation between runs include model version updates and non-deterministic sampling behavior at temperature 0. The composite formula, weights, and severity band mappings are deterministic -- only the per-dimension LLM assessments carry the stated tolerance.
