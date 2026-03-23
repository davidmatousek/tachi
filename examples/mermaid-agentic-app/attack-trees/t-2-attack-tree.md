# Attack Tree: T-2 — Unauthorized document modification corrupting RAG retrieval

| Field | Value |
|-------|-------|
| Finding ID | T-2 |
| Component | Knowledge Base |
| Risk Level | High |
| Threat | Unauthorized document modification corrupting RAG retrieval |
| Correlation | None |

```mermaid
flowchart TD
    T2_root["Corrupt RAG results via unauthorized document modification"]
    T2_or1{{"OR"}}
    T2_leaf1["Exploit weak access controls to modify documents directly"]
    T2_leaf2["Compromise document review workflow to approve malicious changes"]
    T2_leaf3["Modify documents during replication or backup process"]

    T2_root --> T2_or1
    T2_or1 --> T2_leaf1
    T2_or1 --> T2_leaf2
    T2_or1 --> T2_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T2_root goal
    class T2_or1 orGate
    class T2_leaf1,T2_leaf2,T2_leaf3 leaf
```
