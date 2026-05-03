# Attack Tree: AG-4 — Diagnostic Agent MCP Tool Server Abuse

**Component**: Diagnostic Agent | **Risk Level**: High | **Finding**: AG-4

A compromised Diagnostic Agent abuses the Clinical MCP Tool Server as a tool abuse vector, issuing malicious FHIR operations (bulk reads, unauthorized writes) exceeding the agent's authorized scope.

```mermaid
flowchart TD
    AG4_root["Perform unauthorized FHIR operations via Diagnostic Agent MCP Tool Server abuse"]
    AG4_or1{{"OR"}}
    AG4_leaf1["Compromise Diagnostic Agent to issue bulk FHIR read operations beyond per-session token scope"]
    AG4_leaf2["Exploit absent operation-level authorization to perform unauthorized FHIR write via MCP tool call"]
    AG4_leaf3["Issue malicious FHIR operations using legitimate agent session token with over-provisioned permissions"]

    AG4_root --> AG4_or1
    AG4_or1 --> AG4_leaf1
    AG4_or1 --> AG4_leaf2
    AG4_or1 --> AG4_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG4_root goal
    class AG4_or1 orGate
    class AG4_leaf1,AG4_leaf2,AG4_leaf3 leaf
```
