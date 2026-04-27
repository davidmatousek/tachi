# Attack Tree: AG-7 — Long-Running Learning Loop

**Risk Level**: Critical
**Component**: Long-Running Learning Loop
**Threat**: Training data causes model to expand autonomous action scope on next update

```mermaid
graph TD
    Goal["[GOAL] Expand model's autonomous capability scope via temporal training data attack"]
    Goal --> A["[OR] Inject adversarial capability-expansion instructions via training data"]
    A --> A1["Poison Audit Logger with interaction records encoding capability expansion (T-8)"]
    A --> A2["Training signals shaped to cause model to self-authorize new capabilities"]
    Goal --> B["[AND] Poisoned update deployed without capability audit"]
    B --> B1["No capability regression suite testing updated model before deployment"]
    B --> B2["No strict capability allowlist evaluated post-update"]
    B --> B3["No behavioral comparison of pre/post-update on held-out capability test set"]
    Goal --> C["[AND] Updated model operates with expanded unauthorized capability scope"]
    C --> C1["Orchestrator, Specialist, ClinAdvisor all receive poisoned update"]
    C --> C2["Capability expansion accumulates gradually across update cycles"]
    classDef critical fill:#d32f2f,color:#fff
    class Goal critical
```
