---
name: tachi-risk-scoring
description: "Domain knowledge for quantitative risk scoring — four-dimensional scoring model (CVSS 3.1, exploitability, scalability, reachability), CVSS base vector mappings, composite score formulas, severity band thresholds, and governance field derivation rules. Consumed by the risk-scorer agent during scoring pipeline execution."
---

# tachi-risk-scoring

Quantitative risk scoring domain knowledge extracted from the tachi risk-scorer agent. This skill provides the reference tables, formulas, and assessment criteria that the risk-scorer uses to transform qualitative threat findings into data-backed risk scores.

## Domain Overview

The risk scoring model assesses each threat finding on four dimensions:

1. **CVSS 3.1 Base Score** (weight: 0.35) -- Inherent vulnerability severity using standard CVSS 3.1 vector analysis, with AI-specific refinements for agentic and LLM threat categories
2. **Exploitability** (weight: 0.30) -- Practical attack feasibility across four sub-dimensions: known techniques, attack complexity, tooling availability, and skill level
3. **Scalability** (weight: 0.15) -- Blast radius and operational economics across four sub-dimensions: scriptability, target scope, resource requirements, and detection difficulty
4. **Reachability** (weight: 0.20) -- Architecture-aware attack surface exposure derived from trust zone position, zone name analysis, and architecture barrier adjustments

Dimensional scores combine into a weighted composite score (0.0-10.0), which maps to a severity band (Critical/High/Medium/Low) that drives governance fields (SLA, disposition, review date).

## Baseline-Aware Scoring Rules

### Score Inheritance

When a finding has `delta_status: UNCHANGED`, all scoring fields are inherited verbatim from the baseline run:

| Field | Treatment | Rationale |
|-------|-----------|-----------|
| `cvss_base` | Copy verbatim | Zero drift guarantee |
| `cvss_vector` | Copy verbatim | Audit consistency |
| `exploitability` | Copy verbatim | Assessment unchanged |
| `scalability` | Copy verbatim | Assessment unchanged |
| `reachability` | Copy verbatim | Architecture unchanged |
| `composite_score` | Copy verbatim | Derived from unchanged inputs |
| `severity_band` | Copy verbatim | Derived from unchanged composite |

**When to inherit**: Only when `delta_status` is `UNCHANGED`. The finding's component, threat, likelihood, and impact must all match the baseline exactly.

**When NOT to inherit**: `UPDATED` findings are re-scored fresh using the full 4-dimensional model. `NEW` findings are scored fresh. `RESOLVED` findings retain last-known scores but are not actively scored.

### Score Source Field

Every scored finding includes `score_source` (per `schemas/risk-scoring.yaml` v1.1):

- `"inherited"` — Scores copied from baseline (UNCHANGED, RESOLVED)
- `"fresh"` — Scores computed this run (NEW, UPDATED)

### Bounded Scoring for NEW Findings

When scoring `NEW` findings from Phase 2 isolated discovery, the CVSS base score is constrained within ±1.0 of the category default. This prevents score drift from LLM non-determinism while still allowing meaningful differentiation between findings in the same category.

**Formula**: `clamped_score = clamp(assessed_score, category_default - 1.0, category_default + 1.0)`, where `clamp(v, min, max)` returns `min` if `v < min`, `max` if `v > max`, and `v` otherwise. The outer bounds are always [0.0, 10.0].

**Applicability**:

| Delta Status | Bounding Applied? | Rationale |
|-------------|-------------------|-----------|
| `NEW` | Yes | No established context — bound to category default to prevent outlier scores |
| `UPDATED` | No | Re-scored fresh with full context — established finding with history |
| `UNCHANGED` | No | Scores inherited verbatim — no scoring occurs |
| `RESOLVED` | No | Scores retained from baseline — no scoring occurs |

**Edge cases at CVSS extremes**:
- Category default 9.5 → bounded range 8.5–10.0 (CVSS ceiling caps upper bound)
- Category default 1.0 → bounded range 0.0–2.0 (CVSS floor caps lower bound)
- Category default 0.5 → bounded range 0.0–1.5 (floor applies)

**When no baseline is present**: Bounding does not apply. All findings are scored without constraints using the standard 4-dimensional model.

### First Run Behavior

When no baseline is present, all findings receive `score_source: "fresh"` and are scored using the standard 4-dimensional model. No behavioral change from pre-baseline pipeline.

### Governance Field Persistence

When scoring findings with `delta_status` from a baseline-aware run, governance fields follow carry-forward rules to preserve human-assigned values across pipeline runs.

**Core principle**: `risk_owner` is a human-assigned field and is **never** auto-overwritten by the scoring pipeline. SLA and disposition are only recalculated when the severity band changes.

**Carry-forward by delta status**:

| Delta Status | risk_owner | remediation_sla | risk_disposition | review_date |
|-------------|-----------|-----------------|-----------------|-------------|
| `UNCHANGED` | Preserve from baseline | Preserve from baseline | Preserve from baseline | Preserve from baseline |
| `UPDATED` (same band) | Preserve from baseline | Preserve from baseline | Preserve from baseline | Preserve from baseline |
| `UPDATED` (band changed) | Preserve from baseline | Recalculate per new band | Recalculate per new band | Today + new SLA |
| `NEW` | `"Unassigned"` | Per severity mapping | Per severity mapping | Today + SLA |
| `RESOLVED` | Preserve from baseline | Preserve from baseline | Preserve from baseline | Preserve from baseline |

**SLA recalculation trigger**: Compare the baseline severity band to the current severity band. If different, recalculate `remediation_sla` and `review_date` using the new band's mappings. The `risk_disposition` threshold is: Critical/High → `"Mitigate"`, Medium/Low → `"Review"`.

**Baseline governance detection**: Parse the baseline `risk-scores.md` governance fields by matching on finding ID. If baseline `risk-scores.md` is unavailable, assign fresh governance fields for all findings (graceful degradation).

## Loading Table

Reference files are loaded on-demand by the risk-scorer agent at specific workflow phases using the Read tool (per ADR-002).

| Reference | File | Load When |
|-----------|------|-----------|
| Scoring Dimensions | `references/scoring-dimensions.md` | Entering exploitability or scalability assessment phases (Sections 4-5) |
| CVSS Vectors | `references/cvss-vectors.md` | Entering CVSS 3.1 base scoring phase (Section 3) |
| Severity Bands | `references/severity-bands.md` | Entering composite calculation or governance field generation phases (Sections 7-8) |
| Trust Zones | `references/trust-zones.md` | Entering trust zone extraction phase (Section 2) |
| Reachability Analysis | `references/reachability-analysis.md` | Entering reachability assessment phase (Section 6) |
| Output Formatting | `references/output-formatting.md` | Entering markdown output generation phase (Section 9) |
