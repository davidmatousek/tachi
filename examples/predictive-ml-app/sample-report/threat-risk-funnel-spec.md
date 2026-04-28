---
schema_version: "1.4"
template: "risk-funnel"
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
| Risk Reduction | 0% (architecture-only review) |
| Total Findings | 43 |

---

## 2. Funnel Stages

```
[Total Findings: 43]
   │
   ├── Critical: 1 (S-1 Merchant Token Spoofing)
   │      ↓ Inherent: 8.4 / Residual: 8.4
   │
   ├── High: 22 (F-6 ML cluster + supply-chain integrity)
   │      ↓ Inherent: 7.0–7.7 / Residual: 7.0–7.7 (no controls applied)
   │      F-6 ML in this band: 9 of 9 findings
   │
   ├── Medium: 14 (Hardening — mTLS, encryption, scoped access)
   │      ↓ Inherent: 5.0–6.6 / Residual: 5.0–6.6
   │
   └── Low: 6 (Capacity, repudiation hygiene)
          ↓ Inherent: 4.0–4.9 / Residual: 4.0–4.9
```

---

## 3. F-6 ML Top 10 Coverage Highlight

| OWASP ML Entry | Finding | Pattern Category | Component |
|----------------|---------|------------------|-----------|
| ML01:2023 | T-10 | Cat 10 — Adversarial Input Manipulation | FraudDetectionML Prediction API |
| ML03:2023 | LLM-1 | Cat 12 — Model Inversion | FraudDetectionML Prediction API |
| ML04:2023 | LLM-2 | Cat 13 — Membership Inference | FraudDetectionML Prediction API |
| ML06:2023 (artifact) | LLM-3 | Cat 14 — Artifact Supply Chain | MLflow Model Registry |
| ML06:2023 (artifact) | LLM-4 | Cat 14 shared | Weight Checkpoint Storage |
| ML06:2023 (corpus) | D-10 | Cat 10 — Corpus Supply Chain | Model Training Pipeline |
| ML06:2023 (corpus) | D-11 | Cat 10 shared | Feast Feature Store |
| ML07:2023 | D-8 | Cat 8 — Transfer Learning | Fine-Tuning Service |
| ML08:2023 | D-9 | Cat 9 — Feedback Skewing | Active-Learning Feedback Loop |

---

## 4. Visual Design Directives

```
- Funnel Chart layout (top wide, bottom narrow)
- Severity bands stacked vertically: Critical (red), High (orange), Medium (yellow), Low (blue)
- Width proportional to count: Critical thin (1), High wide (22), Medium medium (14), Low narrow (6)
- F-6 ML callout panel right of funnel — 9 findings + OWASP ML mapping
- Risk reduction indicator: 0% → projected ≥85% with F-6 mitigation portfolio
- Footer: "Tachi F-6 Wave 4 — 6 OWASP ML0X:2023 entries closed"
```
