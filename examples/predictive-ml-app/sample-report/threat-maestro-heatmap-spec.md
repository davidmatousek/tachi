---
schema_version: "1.4"
template: "maestro-heatmap"
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
| Heatmap Axes | MAESTRO Layer × STRIDE+ML Category |

---

## 2. MAESTRO × STRIDE+ML Heatmap

| Layer / Category | S | T | R | I | D | E | LLM (Model-Theft) | LLM (Data-Poisoning) |
|------------------|----|----|----|----|----|----|--------------------|-----------------------|
| L1 — Foundation Model | Medium | High | High | High | High | High | High (LLM-1, LLM-2) | High (D-8 — Cat 8) |
| L2 — Data Operations | Medium | High | High | Medium | Low | High | High (LLM-3, LLM-4) | High (D-9, D-10, D-11) |
| L5 — Evaluation and Observability | --- | Medium | --- | Medium | Medium | --- | --- | --- |
| Unclassified | Critical (S-1) | --- | Low | --- | --- | --- | --- | --- |

### F-6 Pattern Category Concentration

- **L1 — F-6 inference-surface trio**: T-10 Cat 10, LLM-1 Cat 12, LLM-2 Cat 13 — all on FraudDetectionML Prediction API.
- **L1 — F-6 transfer-learning Cat 8**: D-8 on Fine-Tuning Service.
- **L2 — F-6 corpus-side Cat 10**: D-10 + D-11 on Training Pipeline + Feast Feature Store.
- **L2 — F-6 feedback Cat 9**: D-9 on Active-Learning Feedback Loop.
- **L2 — F-6 artifact-side Cat 14**: LLM-3 + LLM-4 on MLflow Registry + Weight Checkpoint Storage.

---

## 3. Visual Design Directives

```
- Aspect Ratio: 16:9 landscape
- Heatmap grid with row labels (MAESTRO layers) and column labels (STRIDE+ML categories)
- Color intensity proportional to severity: Critical=#DC2626, High=#EA580C, Medium=#CA8A04, Low=#2563EB
- Empty cells: light gray (#F3F4F6)
- F-6 callouts: small badges in cells with finding IDs (T-10, LLM-1/2, LLM-3/4, D-8, D-9, D-10/11)
- Legend: severity color scale + F-6 ML callout indicator
- Footer: "MAESTRO Heatmap — F-6 ML Top 10 Coverage Bundle: 9 ML findings, 6 OWASP ML0X:2023 entries"
```
