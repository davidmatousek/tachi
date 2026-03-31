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

## Loading Table

Reference files are loaded on-demand by the risk-scorer agent at specific workflow phases using the Read tool (per ADR-002).

| Reference | File | Load When |
|-----------|------|-----------|
| Scoring Dimensions | `references/scoring-dimensions.md` | Entering exploitability, scalability, or reachability assessment phases (Sections 4-6) |
| CVSS Vectors | `references/cvss-vectors.md` | Entering CVSS 3.1 base scoring phase (Section 3) |
| Severity Bands | `references/severity-bands.md` | Entering composite calculation or governance field generation phases (Sections 7-8) |
