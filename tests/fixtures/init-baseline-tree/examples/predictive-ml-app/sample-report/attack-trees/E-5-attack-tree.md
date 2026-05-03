---
finding: "E-5"
component: "Active-Learning Feedback Loop"
category: "elevation"
risk_level: "Critical"
classification: "confidential"
---

# Attack Tree — E-5: Loopback-Record Write Escalates to Model-Parameter Influence

```mermaid
graph TD
    G[Goal: Escalate from Prediction Submission to Model Influence]
    G --> A1[Submit Crafted Prediction Records]
    G --> A2[Loopback to Training Corpus]
    G --> A3[Re-Training Cycle]
    G --> A4[Model Drifts]

    A1 --> B1[Multiple merchant accounts]
    A2 --> C1[No held-out canary set comparison]
    A3 --> D1[Model retrains on biased corpus]
    A4 --> E1[Production behavior shifts attacker-favorable]

    style G fill:#d4183d,color:#fff
```

## Mitigations
- Held-out canary set comparison before every retraining cycle.
- Labeler-trust scoring on labeling worker.
- Reject batches with anomalous label distribution drift.
