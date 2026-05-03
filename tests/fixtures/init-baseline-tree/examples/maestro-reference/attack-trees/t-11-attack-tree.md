# Attack Tree: T-11 — RAG Corpus Adversarial Embedding Poisoning

**Component**: Clinical Guideline RAG Corpus | **Risk Level**: Critical | **Finding**: T-11

An attacker poisons the Clinical Guideline RAG Corpus by injecting adversarially crafted guideline embeddings, causing the RAG retrieval to surface malicious clinical guidance to the Diagnostic Agent.

```mermaid
flowchart TD
    T11_root["Cause Diagnostic Agent to retrieve adversarial clinical guidance via RAG corpus poisoning"]
    T11_or1{{"OR"}}
    T11_sub1["Inject adversarial document directly into corpus indexing pipeline"]
    T11_sub2["Manipulate vector embeddings to bias semantic retrieval results"]
    T11_and1{{"AND"}}
    T11_and2{{"AND"}}
    T11_leaf1["Obtain write access to corpus document ingestion endpoint"]
    T11_leaf2["Craft guideline document that appears legitimate but encodes adversarial clinical content"]
    T11_leaf3["Inject document before provenance verification step in indexing pipeline"]
    T11_leaf4["Access vector store index with write permissions"]
    T11_leaf5["Craft adversarial embedding that appears near trusted guideline queries"]
    T11_leaf6["Replace or insert embedding to bias retrieval toward attacker-preferred outputs"]

    T11_root --> T11_or1
    T11_or1 --> T11_sub1
    T11_or1 --> T11_sub2
    T11_sub1 --> T11_and1
    T11_and1 --> T11_leaf1
    T11_and1 --> T11_leaf2
    T11_and1 --> T11_leaf3
    T11_sub2 --> T11_and2
    T11_and2 --> T11_leaf4
    T11_and2 --> T11_leaf5
    T11_and2 --> T11_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T11_root goal
    class T11_and1,T11_and2 andGate
    class T11_or1 orGate
    class T11_sub1,T11_sub2 subGoal
    class T11_leaf1,T11_leaf2,T11_leaf3,T11_leaf4,T11_leaf5,T11_leaf6 leaf
```
