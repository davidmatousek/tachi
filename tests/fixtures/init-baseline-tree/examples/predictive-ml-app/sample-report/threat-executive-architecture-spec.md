---
schema_version: "1.4"
template: "executive-architecture"
date: "2026-04-28"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 43
critical_high_finding_count: 24
image_generated: false
---

## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | Predictive-ML Application (FraudDetectionML) |
| Layout | Layered MAESTRO + DFD overlay with directional arrows |
| Critical/High Findings Surfaced | 24 |

---

## 2. MAESTRO Layer Stack with F-6 ML Findings

```
┌─────────────────────────────────────────────────────────────┐
│  L1 — Foundation Model                                       │
│  ┌───────────────────────────┐  ┌────────────────────────┐ │
│  │ FraudDetectionML          │  │ Fine-Tuning Service    │ │
│  │ Prediction API            │  │ {{D-8 Cat 8 ML07,      │ │
│  │ {{T-10 Cat 10 ML01,       │  │  T-8, S-5, E-3 H}}     │ │
│  │  LLM-1 Cat 12 ML03,       │  └────────────────────────┘ │
│  │  LLM-2 Cat 13 ML04,       │                              │
│  │  I-1, D-1, E-1 H}}        │                              │
│  └───────────────────────────┘                              │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│  L2 — Data Operations                                        │
│  ┌──────────────────┐ ┌──────────────────┐ ┌─────────────┐ │
│  │ Training Pipeline│ │ Active-Learning  │ │ Feast       │ │
│  │ {{D-10 Cat 10    │ │ Loop             │ │ Feature     │ │
│  │  ML06 corpus,    │ │ {{D-9 Cat 9 ML08,│ │ Store       │ │
│  │  T-2, T-3 H}}    │ │  T-9, E-5 H}}    │ │ {{T-4, D-11 │ │
│  └──────────────────┘ └──────────────────┘ │  H}}        │ │
│                                              └─────────────┘ │
│  ┌──────────────────┐ ┌──────────────────┐                  │
│  │ MLflow Registry  │ │ Weight Checkpoint│                  │
│  │ {{LLM-3 Cat 14   │ │ Storage          │                  │
│  │  ML06 artifact,  │ │ {{LLM-4 Cat 14   │                  │
│  │  T-5, E-4 H}}    │ │  shared, T-6 H}} │                  │
│  └──────────────────┘ └──────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│  L5 — Evaluation and Observability                           │
│  ┌──────────────────┐                                        │
│  │ Interaction      │                                        │
│  │ Audit Log        │                                        │
│  │ (passive sink)   │                                        │
│  └──────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
```

External: HuggingFace Hub (Semi-Trusted) — supplies pretrained weights to Fine-Tuning Service via cross-zone HTTPS data flow without checksum/attestation.

---

## 3. Flow Edges

| Source | Destination | Annotation |
|--------|-------------|------------|
| Merchant | FraudDetectionML Prediction API | Critical S-1 boundary crossing — token spoofing |
| FraudDetectionML | MLflow Registry | Model artifact load — load-time integrity verification absent |
| FraudDetectionML | Active-Learning | Production prediction record — loopback path D-9 surface |
| HuggingFace Hub | Fine-Tuning Service | Pretrained weights without checksum — D-8 surface |
| Fine-Tuning Service | Weight Checkpoint Storage | Mutable storage — LLM-4 surface |
| Weight Checkpoint Storage | MLflow Registry | Model artifact promotion — LLM-3 promotion-gate surface |

---

## 4. Visual Design Directives

```
- Aspect Ratio: 11:8.5 portrait (PDF page 2-3 placement per F-128)
- Layered horizontal bands per MAESTRO layer (L1, L2, L5)
- Components: rounded rectangles within each layer band
- Critical findings: red badge with finding ID
- High findings: orange badge with finding ID; F-6 ML pattern findings get OWASP ML0X:2023 reference appended
- Directional arrows for data flows; thicker for high-risk crossings (Merchant→API, HuggingFace→FineTune)
- Trust boundary clusters: dashed-border rounded rectangles
- F-6 emphasis: orange highlight on Cat 8/9/10/12/13/14 badges
- Footer: "Predictive-ML Topology — F-6 ML Top 10 Coverage Bundle — 6 OWASP ML0X:2023 entries"
```
