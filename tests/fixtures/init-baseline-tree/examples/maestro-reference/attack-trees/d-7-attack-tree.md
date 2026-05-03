# Attack Tree: D-7 — Clinical MCP Tool Server JSON-RPC Flood

**Component**: Clinical MCP Tool Server | **Risk Level**: High | **Finding**: D-7

An attacker who compromises an agent floods the Clinical MCP Tool Server with excessive JSON-RPC tool calls or FHIR operations, exhausting server resources and denying tool access to legitimate agents.

```mermaid
flowchart TD
    D7_root["Exhaust MCP Tool Server resources via JSON-RPC tool call flood denying access to legitimate agents"]
    D7_or1{{"OR"}}
    D7_leaf1["Compromise agent to generate high-volume JSON-RPC tool calls without per-agent rate limits"]
    D7_leaf2["Issue excessive FHIR operation requests exhausting tool server processing capacity"]
    D7_leaf3["Sustain flood using multiple compromised agents to overcome per-agent quotas via coordination"]

    D7_root --> D7_or1
    D7_or1 --> D7_leaf1
    D7_or1 --> D7_leaf2
    D7_or1 --> D7_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D7_root goal
    class D7_or1 orGate
    class D7_leaf1,D7_leaf2,D7_leaf3 leaf
```
