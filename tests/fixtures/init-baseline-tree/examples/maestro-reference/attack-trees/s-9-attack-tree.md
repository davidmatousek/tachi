# Attack Tree: S-9 — Clinical MCP Tool Server Spoofing

**Component**: Clinical MCP Tool Server | **Risk Level**: High | **Finding**: S-9

An attacker spoofs the Clinical MCP Tool Server to return malicious tool results to Diagnostic Agent or Treatment Planner Agent, corrupting clinical decision inputs.

```mermaid
flowchart TD
    S9_root["Return malicious FHIR tool results to specialist agents via spoofed MCP Tool Server"]
    S9_or1{{"OR"}}
    S9_leaf1["Intercept tool call from agent and respond with rogue server lacking identity token"]
    S9_leaf2["Compromise MCP Tool Server DNS resolution to redirect tool calls to attacker-controlled endpoint"]
    S9_leaf3["Return adversarially crafted FHIR data to agent before response integrity check"]

    S9_root --> S9_or1
    S9_or1 --> S9_leaf1
    S9_or1 --> S9_leaf2
    S9_or1 --> S9_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S9_root goal
    class S9_or1 orGate
    class S9_leaf1,S9_leaf2,S9_leaf3 leaf
```
