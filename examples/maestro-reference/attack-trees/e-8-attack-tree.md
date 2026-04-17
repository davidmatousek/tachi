# Attack Tree: E-8 — Clinical LLM Prompt Injection Privilege Escalation

**Component**: Clinical LLM | **Risk Level**: High | **Finding**: E-8

An attacker exploits prompt injection in the Clinical LLM to gain elevated reasoning authority, causing the model to output instructions that the Supervisor Orchestrator interprets as authorized system commands with elevated privilege.

```mermaid
flowchart TD
    E8_root["Cause Supervisor Orchestrator to execute elevated-privilege commands via Clinical LLM prompt injection"]
    E8_or1{{"OR"}}
    E8_leaf1["Craft clinical query containing prompt injection payload encoding system command instructions"]
    E8_leaf2["Bypass prompt injection detection at API Gateway to deliver adversarial instruction to Clinical LLM"]
    E8_leaf3["Cause LLM completion containing system command pattern to be interpreted as trusted orchestrator instruction"]

    E8_root --> E8_or1
    E8_or1 --> E8_leaf1
    E8_or1 --> E8_leaf2
    E8_or1 --> E8_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E8_root goal
    class E8_or1 orGate
    class E8_leaf1,E8_leaf2,E8_leaf3 leaf
```
