# Attack Tree: T-12 — Medical Literature Vector Index Embedding Poisoning

**Component**: Medical Literature Vector Index | **Risk Level**: High | **Finding**: T-12

An attacker injects malicious vector embeddings into the Medical Literature Vector Index, causing Treatment Planner Agent to retrieve and incorporate adversarial literature recommendations.

```mermaid
flowchart TD
    T12_root["Corrupt Treatment Planner Agent literature retrieval via adversarial embedding injection in vector index"]
    T12_or1{{"OR"}}
    T12_leaf1["Gain write access to Medical Literature Vector Index and inject adversarial embeddings"]
    T12_leaf2["Craft embedding vectors that appear near legitimate treatment query embeddings"]
    T12_leaf3["Cause Treatment Planner Agent to retrieve and incorporate adversarial literature"]

    T12_root --> T12_or1
    T12_or1 --> T12_leaf1
    T12_or1 --> T12_leaf2
    T12_or1 --> T12_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T12_root goal
    class T12_or1 orGate
    class T12_leaf1,T12_leaf2,T12_leaf3 leaf
```
