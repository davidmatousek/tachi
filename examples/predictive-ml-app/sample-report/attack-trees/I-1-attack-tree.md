---
finding: "I-1"
component: "FraudDetectionML Prediction API"
category: "info-disclosure"
risk_level: "Critical"
classification: "confidential"
---

# Attack Tree — I-1: Confidence-Value Leakage

```mermaid
graph TD
    G[Goal: Leak Training-Data Signal via Confidence]
    G --> A1[Submit Probe Queries]
    G --> A2[Receive Full-Precision Confidence]
    G --> A3[Substrate for LLM-1 + LLM-2]

    A1 --> B1[No per-tenant rate limit]
    A2 --> C1[No confidence-output truncation]
    A2 --> C2[No label-only mode]
    A3 --> D1[Inversion + membership inference enabled]

    style G fill:#d4183d,color:#fff
```

## Mitigations
- Apply confidence-output truncation (round to 1–2 decimal places).
- Provide label-only response mode for sensitive endpoints.
- Enforce per-tenant query-rate throttling.
