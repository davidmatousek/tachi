# Attack Tree: I-1 — Sensitive document retrieval by unauthorized users

| Field | Value |
|-------|-------|
| Finding ID | I-1 |
| Component | Knowledge Base |
| Risk Level | High |
| Threat | Sensitive document retrieval by unauthorized users |
| Correlation | None |

```mermaid
flowchart TD
    I1_root["Retrieve sensitive documents via unauthorized RAG queries"]
    I1_or1{{"OR"}}
    I1_leaf1["Craft semantic query targeting known sensitive document topics"]
    I1_leaf2["Iteratively probe knowledge base to map document contents"]
    I1_leaf3["Request broad context retrieval to surface protected documents"]

    I1_root --> I1_or1
    I1_or1 --> I1_leaf1
    I1_or1 --> I1_leaf2
    I1_or1 --> I1_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I1_root goal
    class I1_or1 orGate
    class I1_leaf1,I1_leaf2,I1_leaf3 leaf
```
