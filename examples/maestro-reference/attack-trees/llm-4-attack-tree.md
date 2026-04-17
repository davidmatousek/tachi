# Attack Tree: LLM-4 — Risk Stratification Model Adversarial Input Manipulation

**Component**: Risk Stratification Model | **Risk Level**: High | **Finding**: LLM-4

An attacker crafts adversarial patient record inputs passed to the Risk Stratification Model to generate manipulated risk scores, causing incorrect clinical triage and resource allocation decisions.

```mermaid
flowchart TD
    LLM4_root["Cause incorrect clinical triage via adversarial patient record inputs to Risk Stratification Model"]
    LLM4_or1{{"OR"}}
    LLM4_leaf1["Craft adversarial patient record with modified feature values triggering model risk score manipulation"]
    LLM4_leaf2["Inject modified patient EHR data upstream to cause adversarial features to reach model at inference time"]
    LLM4_leaf3["Exploit absent ensemble validation to deliver manipulated risk score into clinical decision workflow"]

    LLM4_root --> LLM4_or1
    LLM4_or1 --> LLM4_leaf1
    LLM4_or1 --> LLM4_leaf2
    LLM4_or1 --> LLM4_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM4_root goal
    class LLM4_or1 orGate
    class LLM4_leaf1,LLM4_leaf2,LLM4_leaf3 leaf
```
