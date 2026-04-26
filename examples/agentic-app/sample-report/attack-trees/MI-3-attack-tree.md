# Attack Tree: MI-3 — Retrieval-Grounding Gap Causes Fabricated Clinical Content on Low-Recall Queries

**Finding ID**: MI-3
**Risk Level**: Critical
**Component**: Clinical Advisory Sub-Agent
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    MI3_root["Cause ClinAdvisor to emit hallucinated clinical content as grounded output when KB retrieval fails"]
    MI3_and1{{"AND"}}
    MI3_sub1["Trigger low-recall KB retrieval scenario for submitted clinical query"]
    MI3_sub2["Exploit absence of retrieval-quality gate to receive speculative clinical output"]
    MI3_or1{{"OR"}}
    MI3_leaf1["Submit clinical query for condition with no matching documents in Knowledge Base"]
    MI3_leaf2["Submit out-of-distribution query that retrieves irrelevant documents with low hit score"]
    MI3_leaf3["Degrade KB relevance by stale content causing current queries to have insufficient recall"]
    MI3_and2{{"AND"}}
    MI3_leaf4["Confirm ClinAdvisor has no recall-at-k threshold evaluation before generating summary"]
    MI3_leaf5["Confirm no structured insufficient-grounding response is returned on retrieval failure"]
    MI3_leaf6["Receive plausible-sounding but hallucinated clinical summary without confidence indicator"]

    MI3_root --> MI3_and1
    MI3_and1 --> MI3_sub1
    MI3_and1 --> MI3_sub2
    MI3_sub1 --> MI3_or1
    MI3_or1 --> MI3_leaf1
    MI3_or1 --> MI3_leaf2
    MI3_or1 --> MI3_leaf3
    MI3_sub2 --> MI3_and2
    MI3_and2 --> MI3_leaf4
    MI3_and2 --> MI3_leaf5
    MI3_and2 --> MI3_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class MI3_root goal
    class MI3_and1,MI3_and2 andGate
    class MI3_or1 orGate
    class MI3_sub1,MI3_sub2 subGoal
    class MI3_leaf1,MI3_leaf2,MI3_leaf3,MI3_leaf4,MI3_leaf5,MI3_leaf6 leaf
```
