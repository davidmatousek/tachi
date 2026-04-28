---
schema_version: "1.4"
template: "baseball-card"
date: "2026-04-28"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 43
image_generated: false
---

## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | Predictive-ML Application (FraudDetectionML) |
| Scan Date | 2026-04-28 |
| Analysis Agents | 8 |
| Total Findings | 43 |
| Risk Posture | Residual risk — 1 Critical and 23 High findings across 14 components; F-6 ML Top 10 Coverage Bundle closes 6 OWASP ML0X:2023 entries |

---

## 2. Risk Distribution

**Chart Title**: Residual Risk Distribution

| Severity | Count | Percentage | Color |
|----------|-------|------------|-------|
| Critical | 1 | 2% | #DC2626 |
| High | 22 | 51% | #EA580C |
| Medium | 14 | 33% | #CA8A04 |
| Low | 6 | 14% | #2563EB |
| **Total** | **43** | **100%** | — |

**Chart Format**: Donut chart with center text "43 findings". Subtitle: "F-6 ML Top 10 Coverage — 9 ML findings spanning 6 OWASP ML0X:2023 entries (ML01, ML03, ML04, ML06, ML07, ML08)".

**F-6 New Findings This Cycle**: T-10 (Adversarial Input Manipulation), LLM-1 (Model Inversion), LLM-2 (Membership Inference), LLM-3 + LLM-4 (Predictive-ML Artifact Supply Chain — ML06 artifact-side), D-8 (Transfer Learning Supply Chain), D-9 (Feedback-Loop Model Skewing), D-10 + D-11 (Predictive-ML Corpus Supply Chain — ML06 corpus-side). All 9 findings introduced in Feature 232.

---

## 3. Coverage Heat Map

| Component | Critical | High | Medium | Low | Total |
|-----------|----------|------|--------|-----|-------|
| FraudDetectionML Prediction API | 0 | 6 | 2 | 0 | 8 |
| Model Training Pipeline | 0 | 3 | 3 | 0 | 6 |
| Fine-Tuning Service | 0 | 4 | 0 | 1 | 5 |
| Active-Learning Feedback Loop | 0 | 4 | 1 | 0 | 5 |
| MLflow Model Registry | 0 | 4 | 1 | 0 | 5 |
| Feast Feature Store | 0 | 2 | 0 | 1 | 3 |
| Merchant Transaction Submitter | 1 | 0 | 0 | 1 | 2 |
| Other (8 components) | 0 | 1 | 7 | 1 | 9 |

### Cell-Level Grid

| Component | S | T | R | I | D | E | LLM |
|-----------|---|---|---|---|---|---|-----|
| FraudDetectionML Prediction API | Medium | High | High | High | High | High | High |
| Model Training Pipeline | Medium | High | High | Medium | Low | High | High |
| Fine-Tuning Service | High | High | High | --- | Low | High | --- |
| Active-Learning Feedback Loop | --- | High | Medium | Medium | Low | High | High |
| MLflow Model Registry | --- | High | High | Medium | Low | High | High |
| Feast Feature Store | --- | High | --- | Low | --- | --- | High |
| Weight Checkpoint Storage | --- | High | --- | --- | --- | --- | High |

> Note: F-6 ML pattern surface (T, LLM cells) on Prediction API and supply-chain components (Fine-Tuning, MLflow, Weight Checkpoint, Feast Feature Store) reflects the deliberate clean-slate baseline — adversarial-defense, signed-artifact, and integrity-verification controls absent.

---

## 4. Top Critical Findings

**Risk Level Column**: Residual Risk

| # | Finding ID | Component | Threat | Residual Risk |
|---|-----------|-----------|--------|---------------|
| 1 | S-1 | Merchant Transaction Submitter | Token replay/spoofing on prediction-API trust-boundary crossing | Critical (8.4) |
| 2 | S-5 | Fine-Tuning Service | HuggingFace Hub upstream maintainer spoofing | High (7.7) |
| 3 | T-10 [NEW] | FraudDetectionML Prediction API | Adversarial Input Manipulation (Pattern Cat 10, OWASP ML01:2023) | High (7.6) |
| 4 | LLM-1 [NEW] | FraudDetectionML Prediction API | Model Inversion (Pattern Cat 12, OWASP ML03:2023) | High (7.4) |
| 5 | LLM-2 [NEW] | FraudDetectionML Prediction API | Membership Inference (Pattern Cat 13, OWASP ML04:2023) | High (7.4) |

> **F-6 callout**: T-10 + LLM-1 + LLM-2 form correlation group CG-1 — three disjoint findings on the same prediction API surface per ADR-035 Decision 5 (input-evasion vs input-reconstruction vs membership-determination). LLM-3 + LLM-4 + D-10 + D-11 form CG-2 (OWASP ML06:2023 split across artifact-side and corpus-side facets per ADR-035 Decision 4).

---

## 5. Architecture Threat Overlay

| Component | Risk Weight | Finding Count | Annotation |
|-----------|-------------|---------------|------------|
| FraudDetectionML Prediction API | High (3.0) | 8 | 6 High + 2 Medium residual; F-6 inference-surface concentration — adversarial-input + model-inversion + membership-inference triad lacking adversarial-defense, DP-SGD, and query-rate throttling controls |
| MLflow Model Registry | High (2.5) | 5 | 4 High + 1 Medium residual; F-6 artifact-side ML06 facet — signed-artifact policy and load-time integrity verification absent |
| Fine-Tuning Service | High (2.5) | 5 | 4 High + 1 Low residual; F-6 transfer-learning Cat 8 + spoofing surface — revision-pinning, signed-weight-artifact policy absent |
| Active-Learning Feedback Loop | High (2.5) | 5 | 4 High + 1 Medium residual; F-6 feedback-loop Cat 9 — labeler-trust scoring and held-out canary absent |
| Model Training Pipeline | High (2.4) | 6 | 3 High + 3 Medium residual; F-6 corpus-side ML06 facet — dataset-checksum manifest absent |
| Feast Feature Store | High (2.3) | 3 | 2 High + 1 Low residual; F-6 corpus-side shared with D-10 — IAM write-audit absent |
| Weight Checkpoint Storage | Medium (2.2) | 2 | 2 High residual; mutable storage without WORM policy |
| Other (8 components) | Medium (1.8) | 9 | Includes Merchant + Analyst + Audit Log + remaining Data Layer |

---

## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: S-1 Merchant Submitter card border |
| High | #EA580C | Orange-600: F-6 ML findings, dominant card border |
| Medium | #CA8A04 | Yellow-600: hardening findings |
| Low | #2563EB | Blue-600: capacity findings |
| Note | #6B7280 | Gray-500: informational |

### Layout Structure

```
- Background: dark navy (#1E293B)
- Aspect Ratio: 16:9 landscape
- 4-Zone Layout:
  1. TOP (~10%): Title "Threat Model: Predictive-ML Application (FraudDetectionML)", subtitle "F-6 ML Top 10 Coverage — 9 ML findings, 6 OWASP ML0X:2023 entries closed"
  2. MIDDLE (~50%): Left donut chart 1C/22H/14M/6L; Center component × STRIDE+ML heat map; Right top-5 finding cards (red border for S-1 Critical, orange for High F-6 ML cards)
  3. BOTTOM (~30%): Architecture threat overlay — Prediction API + Registry + Fine-Tuning + Active-Learning prominent
  4. FOOTER (~5%): "Tachi F-6 Wave 4 — Predictive-ML Topology"
```
