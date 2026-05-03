# Attack Tree: LLM-11 — Long-Running Learning Loop

**Risk Level**: Critical
**Component**: Long-Running Learning Loop
**Threat**: Systematic audit log poisoning for delayed temporal model behavioral shift (OWASP LLM03:2025)

```mermaid
graph TD
    Goal["[GOAL] Shift model behavior across Orchestrator, Specialist, and ClinAdvisor via audit log poisoning (OWASP LLM03:2025)"]
    Goal --> A["[OR] Systematically inject adversarial interaction records into Audit Logger"]
    A --> A1["Exploit log-write access from compromised Application Zone service"]
    A --> A2["Use timing attack: inject before batch training run"]
    Goal --> B["[AND] Adversarial records enter Learning Loop training run"]
    B --> B1["No cryptographic signing of audit log batches"]
    B --> B2["No anomaly detection on training signal distributions"]
    B --> B3["No differential privacy limiting per-example influence"]
    Goal --> C["[AND] Poisoned model updates deployed to all three agents"]
    C --> C1["No human-review gate on updates showing significant behavioral deviation"]
    C --> C2["Delayed activation: attack invisible until next update cycle"]
    classDef critical fill:#d32f2f,color:#fff
    class Goal critical
```
