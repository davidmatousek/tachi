---
finding: "E-4"
component: "MLflow Model Registry"
category: "elevation"
risk_level: "Critical"
classification: "confidential"
---

# Attack Tree — E-4: Single-Call Promotion to Production

```mermaid
graph TD
    G[Goal: Promote Backdoor via Single API Call]
    G --> A1[Compromise Service Account]
    G --> A2[No Two-Person Sign-Off]
    G --> A3[Backdoor Reaches Production]

    A1 --> B1[Single-API-call promotion path]
    A2 --> C1[No PR review]
    A3 --> D1[Inference fleet picks up at next deploy]

    style G fill:#d4183d,color:#fff
```

## Mitigations
- Require pull-request review and two-person sign-off on promotion.
- Apply signed-artifact policy.
- Log every promotion with audit trail.
