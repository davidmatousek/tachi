# Attack Tree: T-8 — Clinical LLM Prompt Input Tampering

**Component**: Clinical LLM | **Risk Level**: High | **Finding**: T-8

An attacker tampers with Clinical LLM prompt inputs forwarded by the API Gateway, injecting adversarial tokens that corrupt the clinical reasoning completion.

```mermaid
flowchart TD
    T8_root["Corrupt Clinical LLM reasoning completions via adversarial prompt input tampering at API Gateway"]
    T8_or1{{"OR"}}
    T8_leaf1["Compromise API Gateway to intercept and modify prompt before forwarding to Clinical LLM"]
    T8_leaf2["Exploit absent prompt input validation to inject adversarial tokens into assembled context"]
    T8_leaf3["Modify prompt content to cause Clinical LLM to produce clinically dangerous reasoning output"]

    T8_root --> T8_or1
    T8_or1 --> T8_leaf1
    T8_or1 --> T8_leaf2
    T8_or1 --> T8_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T8_root goal
    class T8_or1 orGate
    class T8_leaf1,T8_leaf2,T8_leaf3 leaf
```
