# Attack Tree: T-5 — Diagnostic Agent Tool Call Tampering

**Component**: Diagnostic Agent | **Risk Level**: High | **Finding**: T-5

An attacker tampers with the Diagnostic Agent's tool call requests to Clinical MCP Tool Server, injecting malicious FHIR operations or corrupting guideline retrieval queries.

```mermaid
flowchart TD
    T5_root["Corrupt Diagnostic Agent tool operations via tool call request tampering"]
    T5_or1{{"OR"}}
    T5_leaf1["Intercept Diagnostic Agent outbound tool call and modify FHIR operation parameters"]
    T5_leaf2["Compromise agent process to inject adversarial inputs into guideline retrieval query"]
    T5_leaf3["Bypass tool call schema validation at MCP Tool Server to execute unauthorized FHIR write"]

    T5_root --> T5_or1
    T5_or1 --> T5_leaf1
    T5_or1 --> T5_leaf2
    T5_or1 --> T5_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T5_root goal
    class T5_or1 orGate
    class T5_leaf1,T5_leaf2,T5_leaf3 leaf
```
