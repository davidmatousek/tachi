---
finding: "T-6"
component: "Weight Checkpoint Storage"
category: "tampering"
risk_level: "Critical"
classification: "confidential"
---

# Attack Tree — T-6: In-Place Weight Overwrite

```mermaid
graph TD
    G[Goal: Overwrite Weights In-Place]
    G --> A1[Compromise Bucket Write Access]
    G --> A2[Replace Weight File]
    G --> A3[Serving Loads Tampered Weights]

    A1 --> B1[No write-once-read-many policy]
    A2 --> C1[No per-write audit logging]
    A3 --> D1[No load-time integrity verification]

    style G fill:#d4183d,color:#fff
```

## Mitigations
- S3 Object Lock or WORM policy on production weight artifacts.
- Audit-log every write/read with actor identity.
- Verify SHA-256 digest at model-load time.
