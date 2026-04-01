---
name: tachi-control-analysis
description: Domain knowledge for compensating controls analysis — control category definitions with detection patterns, evidence criteria with effectiveness classification, and residual risk calculation with recommendation generation. Loaded on-demand by the control-analyzer agent during codebase scanning and risk assessment phases.
---

# Tachi Control Analysis Skill

This skill contains the domain knowledge extracted from the tachi control-analyzer agent. It provides the reference data needed to detect compensating controls in a target codebase, classify their effectiveness, calculate residual risk, and generate remediation recommendations.

## Domain Overview

The control analysis domain covers three areas:

1. **Control Categories and Detection Patterns** -- Definitions for the 8 compensating control categories (authentication, input-validation, rate-limiting, encryption, logging-audit, csrf-protection, csp-security-headers, access-control), their STRIDE-to-control mapping, pattern indicators for Phase A scanning, and common library/framework references.

2. **Evidence Criteria and Effectiveness Classification** -- Phase B semantic analysis criteria (context checks, enforcement checks, strength assessments), evidence collection rules (snippet selection, deduplication, file path format), confidence level definitions (High/Medium/Low), and Phase 4 classification rules (found/partial/missing with multi-control resolution and cross-component handling).

3. **Residual Risk Calculation and Recommendations** -- Recommendation generation rules for missing and partial controls (templates, effort calibration), residual score computation formula with the P0 binary reduction model (reduction factors by control status), severity band mapping for residual scores, and summary statistics calculations.

## Baseline-Aware Control Analysis Rules

### Carry-Forward Conditions

Control status is carried forward from baseline when ALL of the following are true:

1. Finding `delta_status` is `UNCHANGED`
2. Baseline `compensating-controls.md` exists and is parseable
3. Finding ID matches a baseline controlled finding (exact `findingId/v1` match)

### Carry-Forward Fields

For UNCHANGED findings, copy these fields verbatim from baseline:

| Field | Treatment |
|-------|-----------|
| `control_status` | Copy (found/partial/missing) |
| `control_evidence` | Copy all evidence entries |
| `control_category` | Copy |
| `control_effectiveness` | Copy |
| `reduction_factor` | Copy |
| `residual_score` | Copy |
| `residual_severity_band` | Copy |
| `recommendation` | Copy (if any) |
| `effort_estimate` | Copy (if any) |

Set `control_carry_forward: true` and `rescan_scope: "incremental"`.

### Incremental Re-Scan Scope

When baseline controls are available:

| Scenario | Re-Scan Scope | Rationale |
|----------|---------------|-----------|
| All findings UNCHANGED | `incremental` (nothing to scan) | Full inheritance |
| Mix of UNCHANGED + NEW/UPDATED | `incremental` (scan only changed) | Partial inheritance |
| All findings NEW (first run or no baseline controls) | `full` | No inheritance possible |

### Evidence Preservation

Carried-forward evidence entries retain their original file paths, line numbers, and snippets from the baseline run. These represent the control state as of the baseline — they are **not** re-validated against the current codebase for UNCHANGED findings.

### First Run Behavior

When no baseline `compensating-controls.md` exists, all findings are scanned with `rescan_scope: "full"` and `control_carry_forward: false`. No behavioral change from pre-baseline pipeline.

## Reference Loading Table

Load reference files on-demand using the Read tool at the workflow phase where they are needed. Do not load all references at pipeline start.

| Reference File | Load When | Content |
|----------------|-----------|---------|
| `references/control-categories.md` | Phase 3 (Detect Controls) | 8 control category definitions, STRIDE-to-control mapping, pattern indicators, common libraries |
| `references/evidence-criteria.md` | Phase 3 (Detect Controls), Phase 4 (Map & Classify) | Evidence collection rules, confidence levels, classification rules (found/partial/missing), multi-control resolution |
| `references/residual-risk.md` | Phase 5 (Recommend & Calculate Residual Risk) | Recommendation templates, effort calibration, residual score formula, reduction factors, severity band mapping, summary statistics |
