---
finding_id: "T-8"
risk_level: "Critical"
component: "Long-Running Learning Loop"
generated: "2026-04-19"
---

# Attack Tree: T-8 — Learning Loop Training Signal Poisoning (Temporal Attack)

```mermaid
graph TD
    GOAL["GOAL: Inject sleeper-agent trigger into\nmodel via poisoned training signal"]
    GOAL --> A["AND"]
    A --> B["Inject adversarial entries into Audit Logger"]
    A --> C["No anomaly detection on training data"]
    B --> B1["Exploit Audit Logger write access\n[Med / High]"]
    B --> B2["Compromise upstream component\nthat writes to Audit Logger\n[Med / High]"]
    C --> C1["Training signal accepted without\nprovenance attestation\n[High / High]"]
    B1 --> D["Craft adversarial interaction records\ndesigned to activate on trigger prompt"]
    B2 --> D
    C1 --> D
    D --> E["Records incorporated into\nLearning Loop training run"]
    E --> F["Sleeper-agent behavior embedded\nin model update"]
    F --> G["Future model update applied\nto Orchestrator/Specialist"]
    G --> H["Trigger prompt activates\nhidden adversarial behavior"]
```

**Chain-breaking control**: Apply training data provenance attestation with verifiable origin signatures per log entry. Implement anomaly detection on training signal distributions. Limit influence of any single data source; apply gradient clipping and differential privacy during training.
