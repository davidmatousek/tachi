---
finding: "E-1"
component: "FraudDetectionML Prediction API"
category: "elevation"
risk_level: "Critical"
classification: "confidential"
---

# Attack Tree — E-1: Self-Authorized Arbitrary Artifact Load

```mermaid
graph TD
    G[Goal: Load Arbitrary Artifact via Prediction API]
    G --> A1[Compromise Prediction API Process]
    G --> A2[Self-Authorize Load Decision]
    G --> A3[Load Backdoored Artifact]

    A1 --> B1[Process compromise]
    A2 --> C1[No least-privilege IAM]
    A3 --> D1[Inference now under attacker control]

    style G fill:#d4183d,color:#fff
```

## Mitigations
- Apply least-privilege IAM: prediction API reads only currently-promoted production artifact ID.
- Disallow runtime-controlled model-load decisions.
