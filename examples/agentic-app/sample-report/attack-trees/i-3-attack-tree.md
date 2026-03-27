# Attack Tree: I-3 -- API Key Exposure via Unsanitized Error Forwarding

| Field | Value |
|-------|-------|
| Finding ID | I-3 |
| Component | MCP Tool Server |
| Risk Level | High |
| Threat | API Key Exposure via Unsanitized Error Forwarding |
| Correlation | None |

```mermaid
flowchart TD
    I3_root["Extract API keys from forwarded External API error responses"]
    I3_and1{{"AND"}}
    I3_leaf1["Trigger External API errors via malformed tool requests"]
    I3_leaf2["Raw error containing credentials forwarded to Orchestrator"]
    I3_leaf3["Extract sensitive data from error response in user output"]

    I3_root --> I3_and1
    I3_and1 --> I3_leaf1
    I3_and1 --> I3_leaf2
    I3_and1 --> I3_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I3_root goal
    class I3_and1 andGate
    class I3_leaf1,I3_leaf2,I3_leaf3 leaf
```
