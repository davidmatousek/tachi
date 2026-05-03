---
finding: "E-3"
component: "Fine-Tuning Service"
category: "elevation"
risk_level: "Critical"
classification: "confidential"
---

# Attack Tree — E-3: Pretrained Weight Merge into Production Parameters

```mermaid
graph TD
    G[Goal: Escalate from Data-Fetch to Parameter Control]
    G --> A1[Compromise External Source]
    G --> A2[No Signed-Artifact Policy]
    G --> A3[Production Parameter Override]

    A1 --> B1[HuggingFace upstream compromise]
    A2 --> C1[No Sigstore attestation required]
    A3 --> D1[Production model behaves as attacker chooses]

    style G fill:#d4183d,color:#fff
```

## Mitigations
- Enforce signed-artifact policy at fine-tune load.
- Require model-card provenance review.
- Stage every fine-tune for behavioral regression testing.
