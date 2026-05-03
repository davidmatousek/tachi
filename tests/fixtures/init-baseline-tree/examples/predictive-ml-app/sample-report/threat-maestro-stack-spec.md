---
schema_version: "1.4"
template: "maestro-stack"
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
| MAESTRO Layers Present | L1, L2, L5 (Unclassified for External Entities) |

---

## 2. MAESTRO Layer Distribution

| Layer | Critical | High | Medium | Low | Total |
|-------|---------:|-----:|-------:|----:|------:|
| L1 — Foundation Model | 0 | 11 | 2 | 1 | 14 |
| L2 — Data Operations | 0 | 11 | 7 | 5 | 23 |
| L5 — Evaluation and Observability | 0 | 0 | 3 | 0 | 3 |
| Unclassified (External Entities) | 1 | 0 | 2 | 0 | 3 |
| **Total** | **1** | **22** | **14** | **6** | **43** |

---

## 3. Layer Detail with F-6 Pattern Categories

### L1 — Foundation Model (14 findings)

- **FraudDetectionML Prediction API** (8 findings):
  - T-10 Cat 10 (ML01:2023 — adversarial input)
  - LLM-1 Cat 12 (ML03:2023 — model inversion)
  - LLM-2 Cat 13 (ML04:2023 — membership inference)
  - I-1 (full-precision confidence leakage), D-1 (rate limiting), E-1 (artifact load)
- **Fine-Tuning Service** (5 findings):
  - D-8 Cat 8 (ML07:2023 — transfer learning supply chain)
  - T-8 (poisoned weights), S-5 (HuggingFace spoofing), E-3 (parameter merge), D-3 (retry capacity)

### L2 — Data Operations (23 findings)

- **Model Training Pipeline** (6 findings): D-10 Cat 10 (ML06:2023 corpus-side), T-2, T-3, I-2, S-4, E-2
- **Active-Learning Feedback Loop** (5 findings): D-9 Cat 9 (ML08:2023), T-9, E-5, I-7, D-4
- **MLflow Model Registry** (5 findings): LLM-3 Cat 14 (ML06:2023 artifact-side), T-5, E-4, I-5, D-5
- **Feast Feature Store** (3 findings): D-11 Cat 10 shared, T-4, I-4
- **Weight Checkpoint Storage** (2 findings): LLM-4 Cat 14 shared, T-6
- **Internal Merchant Transaction History** (2 findings): T-3, I-3

### L5 — Evaluation and Observability (3 findings)

- **Interaction Audit Log** (3 findings): T-7, I-6, D-6 — passive sink without retrospective query pipeline.

---

## 4. Visual Design Directives

```
- Aspect Ratio: 16:9 landscape
- Background: light gray (#F9FAFB)
- Layers stacked vertically; color band per layer (L1 blue, L2 green, L5 yellow, Unclassified gray)
- Components within each layer: rounded rectangles with finding-count badges
- F-6 ML pattern categories: orange (#EA580C) accent on the badge; OWASP ML0X:2023 reference under finding ID
- L1 (Prediction API + Fine-Tuning) and L2 (Training + Feedback + Registry + Feature Store + Checkpoint) heavily annotated reflecting F-6 surface
- Footer: "MAESTRO Stack View — F-6 ML Top 10 Coverage Bundle"
```
