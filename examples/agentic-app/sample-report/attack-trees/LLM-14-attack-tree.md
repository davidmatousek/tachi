# Attack Tree: LLM-14 — Clinical Advisory Sub-Agent

**Risk Level**: Critical
**Component**: Clinical Advisory Sub-Agent
**Threat**: Training data poisoning via adversarial Clinical Decision Log Entries (OWASP LLM03:2025)

```mermaid
graph TD
    Goal["[GOAL] Shift ClinAdvisor clinical reasoning toward attacker-preferred outputs via training data poisoning (OWASP LLM03:2025)"]
    Goal --> A["[OR] Inject adversarial Clinical Decision Log Entries into Audit Logger"]
    A --> A1["Compromise service with Audit Logger write access"]
    A --> A2["Cause ClinAdvisor to log attacker-controlled clinical interactions (via LLM-13)"]
    Goal --> B["[AND] Adversarial entries enter ClinAdvisor training via Learning Loop"]
    B --> B1["No Clinical Decision Log Entry provenance attestation"]
    B --> B2["No anomaly detection on clinical training signal patterns"]
    Goal --> C["[AND] Poisoned ClinAdvisor update deployed without clinical validation"]
    C --> C1["No clinical-domain holdout evaluation suite before deployment"]
    C --> C2["ClinAdvisor consistently recommends specific drugs or omits contraindications"]
    classDef critical fill:#d32f2f,color:#fff
    class Goal critical
```
