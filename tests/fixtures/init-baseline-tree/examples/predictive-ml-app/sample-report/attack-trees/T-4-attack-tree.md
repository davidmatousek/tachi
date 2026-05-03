---
finding: "T-4"
component: "Feast Feature Store"
category: "tampering"
risk_level: "Critical"
classification: "confidential"
---

# Attack Tree — T-4: Feature Store Mutation Without Write-Audit

```mermaid
graph TD
    G[Goal: Mutate Feature Vectors]
    G --> A1[Compromise Service Account]
    G --> A2[Write Mutation]
    G --> A3[Read at Inference]

    A1 --> B1[No IAM-enforced write-audit]
    A2 --> C1[No promotion-gate review]
    A3 --> D1[Tampered feature reaches inference]

    style G fill:#d4183d,color:#fff
```

## Mitigations
- IAM with per-write audit on the feature store.
- Verify feature-vector integrity at read time.
- Monitor for anomalous feature-distribution drift.
