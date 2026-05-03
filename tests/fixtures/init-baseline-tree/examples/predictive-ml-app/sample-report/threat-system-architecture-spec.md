---
schema_version: "1.4"
template: "system-architecture"
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
| Diagram Type | DFD overlay with F-6 ML threat annotations |
| Total Findings | 43 |
| F-6 ML Findings | 9 (T-10, LLM-1, LLM-2, LLM-3, LLM-4, D-8, D-9, D-10, D-11) |

---

## 2. Component Inventory

| Component | DFD Type | MAESTRO Layer | Trust Zone | F-6 Pattern Categories |
|-----------|----------|---------------|------------|------------------------|
| Merchant Transaction Submitter | External Entity | Unclassified | User Zone (Untrusted) | — |
| Fraud Analyst | External Entity | Unclassified | User Zone (Untrusted) | — |
| FraudDetectionML Prediction API | Process | L1 — Foundation Model | Application Zone | Cat 10 (Tampering), Cat 12 (Model Inversion), Cat 13 (Membership Inference) |
| Model Training Pipeline | Process | L2 — Data Operations | Application Zone | Cat 10 (Data-Poisoning corpus-side) |
| Fine-Tuning Service | Process | L1 — Foundation Model | Application Zone | Cat 8 (Transfer Learning) |
| Active-Learning Feedback Loop | Process | L2 — Data Operations | Application Zone | Cat 9 (Feedback Skewing) |
| Feast Feature Store | Data Store | L2 — Data Operations | Data Layer | Cat 10 shared (Corpus Supply Chain) |
| MLflow Model Registry | Data Store | L2 — Data Operations | Data Layer | Cat 14 (Artifact Supply Chain) |
| Weight Checkpoint Storage | Data Store | L2 — Data Operations | Data Layer | Cat 14 shared (Artifact Supply Chain) |
| HuggingFace Hub | External Entity | Unclassified | External Services | — |

---

## 3. Trust Boundary Diagram

```
[User Zone — Untrusted]
  Merchant ─[HTTPS]─▶ {{S-1, T-10 + LLM-1 + LLM-2}}
                                      │
                                      ▼
[Application Zone — Trusted]
  ┌─────────────────────────────────────────────────────────────┐
  │  FraudDetectionML Prediction API (L1)                       │
  │  └ Cat 10/12/13 cluster — adversarial-input + extraction   │
  │                                                              │
  │  Model Training Pipeline (L2)                                │
  │  └ Cat 10 corpus-side {{D-10}}                              │
  │                                                              │
  │  Fine-Tuning Service (L1)                                    │
  │  └ Cat 8 + Spoofing {{D-8, T-8, S-5}}                       │
  │                                                              │
  │  Active-Learning Feedback Loop (L2)                          │
  │  └ Cat 9 {{D-9, T-9, E-5}}                                  │
  └─────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
[Data Layer — Trusted]
  Feast Feature Store {{T-4, D-11}}
  MLflow Model Registry {{T-5, LLM-3, E-4}}
  Weight Checkpoint Storage {{T-6, LLM-4}}
                                      │
                                      ▼
[External Services — Semi-Trusted]
  HuggingFace Hub {{S-6 (DNS/BGP hijack)}}
```

---

## 4. Critical Threat Annotations

| ID | Component | Annotation Style |
|----|-----------|------------------|
| S-1 | Merchant Transaction Submitter | Red badge on User Zone boundary — "Critical: Token Spoofing" |
| T-10 | FraudDetectionML Prediction API | Orange badge on Process — "F-6 Cat 10: Adversarial Input Manipulation (ML01:2023)" |
| LLM-1 | FraudDetectionML Prediction API | Orange badge on Process — "F-6 Cat 12: Model Inversion (ML03:2023)" |
| LLM-2 | FraudDetectionML Prediction API | Orange badge on Process — "F-6 Cat 13: Membership Inference (ML04:2023)" |
| LLM-3 | MLflow Model Registry | Orange badge on Data Store — "F-6 Cat 14: Artifact Supply Chain (ML06:2023)" |
| LLM-4 | Weight Checkpoint Storage | Orange badge on Data Store — "F-6 Cat 14 shared" |
| D-8 | Fine-Tuning Service | Orange badge on Process — "F-6 Cat 8: Transfer Learning (ML07:2023)" |
| D-9 | Active-Learning Feedback Loop | Orange badge on Process — "F-6 Cat 9: Feedback Skewing (ML08:2023)" |
| D-10 | Model Training Pipeline | Orange badge on Process — "F-6 Cat 10: Corpus Supply Chain (ML06:2023)" |

---

## 5. Visual Design Directives

```
- Aspect Ratio: 16:9 landscape
- Background: light gray (#F9FAFB) with thin grid lines
- Trust zones rendered as rounded-rectangle clusters with dashed borders
- Components rendered as rectangles (Process), cylinders (Data Store), stick-figures (External Entity)
- F-6 ML threat badges: orange (#EA580C) circles with finding ID overlaid on the affected component
- Critical findings (S-1): red (#DC2626) badge with arrow indicating boundary crossing
- Data flow arrows: thin (regular flows), thick (high-risk flows like Merchant→API and HuggingFace→FineTune)
- Footer: "Tachi F-6 Wave 4 — Predictive-ML Topology — 9 ML findings, 6 OWASP ML0X:2023 entries closed"
```
