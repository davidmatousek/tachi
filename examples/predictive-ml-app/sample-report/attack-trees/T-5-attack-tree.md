---
finding: "T-5"
component: "MLflow Model Registry"
category: "tampering"
risk_level: "Critical"
classification: "confidential"
---

# Attack Tree — T-5: MLflow Registry Backdoored Promotion

```mermaid
graph TD
    G[Goal: Promote Backdoored Artifact]
    G --> A1[Compromise ML-Engineering Credentials]
    G --> A2[Push Backdoored Artifact]
    G --> A3[Single-Call Promotion]

    A1 --> B1[Stolen API key]
    A2 --> C1[No signed-artifact policy]
    A3 --> D1[No PR review or two-person sign-off]

    style G fill:#d4183d,color:#fff
```

## Mitigations
- Enforce signed-artifact policy with Sigstore-style attestation.
- Require PR review and two-person sign-off on promotion.
