---
finding: "T-8"
component: "Fine-Tuning Service"
category: "tampering"
risk_level: "Critical"
classification: "confidential"
---

# Attack Tree — T-8: Poisoned Pretrained Weights at Fine-Tune

```mermaid
graph TD
    G[Goal: Merge Poisoned Weights into Production]
    G --> A1[HuggingFace Maintainer Compromised]
    G --> A2[from_pretrained Without Pin]
    G --> A3[Backdoor Survives Evaluation]

    A1 --> B1[Push backdoored revision]
    A2 --> C1[Latest revision pulled silently]
    A3 --> D1[Standard evaluation passes baseline]

    style G fill:#d4183d,color:#fff
```

## Mitigations
- Pin every fine-tune load by SHA via revision parameter.
- Verify hash at load time; CI failure on digest drift.
- Require model-card provenance review before fine-tune.
