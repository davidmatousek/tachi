---
finding: "S-5"
component: "Fine-Tuning Service"
category: "spoofing"
risk_level: "Critical"
classification: "confidential"
---

# Attack Tree — S-5: HuggingFace Hub Maintainer Spoofing

```mermaid
graph TD
    G[Goal: Spoof Trusted Upstream Maintainer]
    G --> A1[Register Same-Named Artifact]
    G --> A2[Allowlist Absent]
    G --> A3[Backdoored Weights Pulled]

    A1 --> B1[Squat namespace on HuggingFace Hub]
    A2 --> C1[Fine-tuning toolchain accepts any source]
    A3 --> D1[from_pretrained pulls poisoned artifact]

    style G fill:#d4183d,color:#fff
```

## Mitigations
- Maintain allowlist of trusted pretrained-weight sources.
- Enforce signed-weight-artifact policy at fine-tune load time.
- Pin every fine-tune load by SHA.
