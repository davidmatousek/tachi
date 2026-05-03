# Attack Tree: LLM-3 — Knowledge base poisoning with adversarial documents

| Field | Value |
|-------|-------|
| Finding ID | LLM-3 |
| Component | Knowledge Base |
| Risk Level | High |
| Threat | Knowledge base poisoning with adversarial documents |
| Correlation | None |

```mermaid
flowchart TD
    LLM3_root["Poison knowledge base with adversarial documents"]
    LLM3_or1{{"OR"}}
    LLM3_sub1["Insert new malicious documents"]
    LLM3_sub2["Modify existing documents to embed adversarial content"]
    LLM3_and1{{"AND"}}
    LLM3_leaf1["Obtain document upload credentials or exploit weak write controls"]
    LLM3_leaf2["Craft document with factually incorrect content that passes validation"]
    LLM3_leaf3["Optimize document embeddings to rank highly for target queries"]
    LLM3_leaf4["Gain write access to existing document store"]
    LLM3_leaf5["Modify document content while preserving metadata and embedding similarity"]

    LLM3_root --> LLM3_or1
    LLM3_or1 --> LLM3_sub1
    LLM3_or1 --> LLM3_sub2
    LLM3_sub1 --> LLM3_and1
    LLM3_and1 --> LLM3_leaf1
    LLM3_and1 --> LLM3_leaf2
    LLM3_and1 --> LLM3_leaf3
    LLM3_sub2 --> LLM3_leaf4
    LLM3_sub2 --> LLM3_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333

    class LLM3_root goal
    class LLM3_or1 orGate
    class LLM3_and1 andGate
    class LLM3_sub1,LLM3_sub2 subGoal
    class LLM3_leaf1,LLM3_leaf2,LLM3_leaf3,LLM3_leaf4,LLM3_leaf5 leaf
```
