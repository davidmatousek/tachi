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

## Reference Loading Table

Load reference files on-demand using the Read tool at the workflow phase where they are needed. Do not load all references at pipeline start.

| Reference File | Load When | Content |
|----------------|-----------|---------|
| `references/control-categories.md` | Phase 3 (Detect Controls) | 8 control category definitions, STRIDE-to-control mapping, pattern indicators, common libraries |
| `references/evidence-criteria.md` | Phase 3 (Detect Controls), Phase 4 (Map & Classify) | Evidence collection rules, confidence levels, classification rules (found/partial/missing), multi-control resolution |
| `references/residual-risk.md` | Phase 5 (Recommend & Calculate Residual Risk) | Recommendation templates, effort calibration, residual score formula, reduction factors, severity band mapping, summary statistics |
