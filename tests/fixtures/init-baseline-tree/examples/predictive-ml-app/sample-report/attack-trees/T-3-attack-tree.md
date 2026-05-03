---
finding: "T-3"
component: "Internal Merchant Transaction History"
category: "tampering"
risk_level: "Critical"
classification: "confidential"
---

# Attack Tree — T-3: Internal Training Corpus Mutation

```mermaid
graph TD
    G[Goal: Mutate Training Samples]
    G --> A1[Compromise Service Account]
    G --> A2[Write Mutation]
    G --> A3[Inject Biased Labels]

    A1 --> B1[No IAM-enforced write-audit]
    A2 --> C1[No immutability lock on training snapshots]
    A3 --> D1[Subsequent retraining ingests poison]

    style G fill:#d4183d,color:#fff
```

## Mitigations
- Enforce IAM with least-privilege on write access.
- Per-write audit logging (actor, before/after, timestamp).
- Immutable WORM storage for committed training snapshots.
