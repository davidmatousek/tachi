# Attack Tree: AG-3 -- Unscoped Tool Access on MCP Server

| Field | Value |
|-------|-------|
| Finding ID | AG-3 |
| Component | MCP Tool Server |
| Risk Level | Critical |
| Threat | Unscoped Tool Access on MCP Server |
| Correlation | None |

```mermaid
flowchart TD
    AG3_root["Access all MCP tools regardless of agent authorization"]
    AG3_or1{{"OR"}}
    AG3_sub1["Exploit unscoped tool registry"]
    AG3_sub2["Dynamic tool discovery enumeration"]
    AG3_and1{{"AND"}}
    AG3_leaf1["Connect to MCP Tool Server as any agent"]
    AG3_leaf2["Enumerate all available tools via discovery endpoint"]
    AG3_leaf3["Invoke privileged tool not in agent capability set"]
    AG3_leaf4["Query tool registry for complete tool listing"]
    AG3_leaf5["Identify high-value tools outside intended scope"]

    AG3_root --> AG3_or1
    AG3_or1 --> AG3_sub1
    AG3_or1 --> AG3_sub2
    AG3_sub1 --> AG3_and1
    AG3_and1 --> AG3_leaf1
    AG3_and1 --> AG3_leaf2
    AG3_and1 --> AG3_leaf3
    AG3_sub2 --> AG3_leaf4
    AG3_sub2 --> AG3_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG3_root goal
    class AG3_or1 orGate
    class AG3_and1 andGate
    class AG3_sub1,AG3_sub2 subGoal
    class AG3_leaf1,AG3_leaf2,AG3_leaf3,AG3_leaf4,AG3_leaf5 leaf
```
