# Attack Tree: AG-4 -- Capability Escalation via Tool Chaining

| Field | Value |
|-------|-------|
| Finding ID | AG-4 |
| Component | MCP Tool Server |
| Risk Level | High |
| Threat | Capability Escalation via Tool Chaining |
| Correlation | CG-4 (See also: D-3) |

```mermaid
flowchart TD
    AG4_root["Achieve data exfiltration via tool call chaining"]
    AG4_and1{{"AND"}}
    AG4_sub1["Execute data retrieval tool"]
    AG4_sub2["Execute data export tool"]
    AG4_sub3["Execute network send tool"]
    AG4_leaf1["Query database via authorized read tool"]
    AG4_leaf2["Write results to file via authorized export tool"]
    AG4_leaf3["Transmit file externally via authorized network tool"]

    AG4_root --> AG4_and1
    AG4_and1 --> AG4_sub1
    AG4_and1 --> AG4_sub2
    AG4_and1 --> AG4_sub3
    AG4_sub1 --> AG4_leaf1
    AG4_sub2 --> AG4_leaf2
    AG4_sub3 --> AG4_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG4_root goal
    class AG4_and1 andGate
    class AG4_sub1,AG4_sub2,AG4_sub3 subGoal
    class AG4_leaf1,AG4_leaf2,AG4_leaf3 leaf
```
