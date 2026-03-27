# Attack Tree: I-4 -- Knowledge Base Metadata Exposure

| Field | Value |
|-------|-------|
| Finding ID | I-4 |
| Component | Knowledge Base |
| Risk Level | High |
| Threat | Knowledge Base Metadata Exposure |
| Correlation | None |

```mermaid
flowchart TD
    I4_root["Extract internal metadata from Knowledge Base query responses"]
    I4_and1{{"AND"}}
    I4_leaf1["Craft queries that trigger full document retrieval"]
    I4_leaf2["Exploit missing field projection to obtain metadata"]
    I4_leaf3["Extract embedding vectors and storage schema details"]

    I4_root --> I4_and1
    I4_and1 --> I4_leaf1
    I4_and1 --> I4_leaf2
    I4_and1 --> I4_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I4_root goal
    class I4_and1 andGate
    class I4_leaf1,I4_leaf2,I4_leaf3 leaf
```
