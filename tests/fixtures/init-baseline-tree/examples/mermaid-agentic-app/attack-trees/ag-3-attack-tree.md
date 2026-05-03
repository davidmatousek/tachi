# Attack Tree: AG-3 — Unsanitized tool call parameters forwarded to External API

| Field | Value |
|-------|-------|
| Finding ID | AG-3 |
| Component | MCP Tool Server |
| Risk Level | High |
| Threat | Unsanitized tool call parameters forwarded to External API |
| Correlation | None |

```mermaid
flowchart TD
    AG3_root["Inject malicious parameters into external API via tool calls"]
    AG3_or1{{"OR"}}
    AG3_leaf1["Craft prompt that generates tool call with SQL injection payload"]
    AG3_leaf2["Craft prompt that generates tool call with shell command payload"]
    AG3_leaf3["Craft prompt that generates tool call with path traversal payload"]

    AG3_root --> AG3_or1
    AG3_or1 --> AG3_leaf1
    AG3_or1 --> AG3_leaf2
    AG3_or1 --> AG3_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG3_root goal
    class AG3_or1 orGate
    class AG3_leaf1,AG3_leaf2,AG3_leaf3 leaf
```
