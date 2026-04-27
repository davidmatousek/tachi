# Attack Tree: T-8 — Long-Running Learning Loop

**Risk Level**: Critical
**Component**: Long-Running Learning Loop
**Threat**: Temporal data poisoning with sleeper-agent injection via training cycle

```mermaid
graph TD
    Goal["[GOAL] Inject sleeper-agent behavior into model via poisoned training signal (temporal attack)"]
    Goal --> A["[OR] Inject adversarial entries into Audit Logger"]
    A --> A1["Audit Logger lacks append-only enforcement"]
    A --> A2["Training signal entries not cryptographically signed at source"]
    A --> A3["Compromised Application Zone service with log-write access"]
    Goal --> B["[OR] Entries survive into Learning Loop training run"]
    B --> B1["No anomaly detection on training signal distribution"]
    B --> B2["No holdout evaluation before deploying model update"]
    B --> B3["No gradient clipping or differential privacy during training"]
    Goal --> C["[AND] Poisoned model update deployed"]
    C --> C1["No staged rollout with behavioral regression checks"]
    C --> C2["Trigger pattern embedded — activates on future user prompt"]
    classDef critical fill:#d32f2f,color:#fff
    class Goal critical
```
