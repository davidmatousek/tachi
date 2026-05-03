# Attack Tree: T-6 — Treatment Planner Agent Input Tampering

**Component**: Treatment Planner Agent | **Risk Level**: High | **Finding**: T-6

An attacker tampers with the Treatment Planner Agent's literature retrieval queries or tool calls, injecting adversarially crafted inputs that corrupt treatment plan generation.

```mermaid
flowchart TD
    T6_root["Corrupt treatment plan generation via Treatment Planner Agent input tampering"]
    T6_or1{{"OR"}}
    T6_leaf1["Intercept literature retrieval query and inject adversarial search parameters"]
    T6_leaf2["Compromise agent process to modify tool call payload before MCP Tool Server execution"]
    T6_leaf3["Bypass schema-enforced tool call validation to execute unauthorized FHIR operations"]

    T6_root --> T6_or1
    T6_or1 --> T6_leaf1
    T6_or1 --> T6_leaf2
    T6_or1 --> T6_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T6_root goal
    class T6_or1 orGate
    class T6_leaf1,T6_leaf2,T6_leaf3 leaf
```
