---
finding: "T-9"
component: "Active-Learning Feedback Loop"
category: "tampering"
risk_level: "Critical"
classification: "confidential"
---

# Attack Tree — T-9: Labeling Worker Tampering

```mermaid
graph TD
    G[Goal: Flip Labels in Loopback Path]
    G --> A1[Compromise Labeling Worker]
    G --> A2[Flip Production Labels]
    G --> A3[Skewed Corpus]

    A1 --> B1[No labeler-trust scoring]
    A2 --> C1[Flips reach training corpus]
    A3 --> D1[Model retrains on biased samples]

    style G fill:#d4183d,color:#fff
```

## Mitigations
- Apply labeler-trust scoring with reputation-based weighting.
- Multi-labeler consensus on safety-critical samples.
- Anomaly detect on label-distribution drift.
