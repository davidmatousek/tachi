# Attack Tree: LLM-2 — Indirect Prompt Injection via Adversarial Knowledge Base Documents

**Finding ID**: LLM-2
**Risk Level**: Critical
**Component**: LLM Agent Orchestrator
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    LLM2_root["Hijack Orchestrator reasoning by injecting adversarial instructions via poisoned KB documents"]
    LLM2_or1{{"OR"}}
    LLM2_sub1["Inject adversarial documents into Knowledge Base directly"]
    LLM2_sub2["Exploit existing document with instruction-like content"]
    LLM2_and1{{"AND"}}
    LLM2_leaf1["Obtain write access to Knowledge Base document store"]
    LLM2_leaf2["Craft document embedding adversarial instructions with high retrieval ranking"]
    LLM2_leaf3["Confirm no retrieval-time sanitization strips instruction patterns from documents"]
    LLM2_and2{{"AND"}}
    LLM2_leaf4["Identify existing KB document containing instruction-like text patterns"]
    LLM2_leaf5["Craft user query that triggers retrieval of exploitable document into Orchestrator context"]

    LLM2_root --> LLM2_or1
    LLM2_or1 --> LLM2_sub1
    LLM2_or1 --> LLM2_sub2
    LLM2_sub1 --> LLM2_and1
    LLM2_and1 --> LLM2_leaf1
    LLM2_and1 --> LLM2_leaf2
    LLM2_and1 --> LLM2_leaf3
    LLM2_sub2 --> LLM2_and2
    LLM2_and2 --> LLM2_leaf4
    LLM2_and2 --> LLM2_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM2_root goal
    class LLM2_or1 orGate
    class LLM2_and1,LLM2_and2 andGate
    class LLM2_sub1,LLM2_sub2 subGoal
    class LLM2_leaf1,LLM2_leaf2,LLM2_leaf3,LLM2_leaf4,LLM2_leaf5 leaf
```
