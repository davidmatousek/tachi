# Attack Tree: MI-1 — Ungrounded Factual Emission: Hallucinated Clinical Claims Without RAG Grounding

**Finding ID**: MI-1
**Risk Level**: Critical
**Component**: Clinical Advisory Sub-Agent
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    MI1_root["Cause ClinAdvisor to emit hallucinated clinical claims accepted as authoritative without grounding verification"]
    MI1_or1{{"OR"}}
    MI1_sub1["Trigger hallucination by providing clinical query in low-coverage KB domain"]
    MI1_sub2["Exploit absence of per-claim source anchoring to pass fabricated claims undetected"]
    MI1_and1{{"AND"}}
    MI1_leaf1["Craft clinical query for medical area with sparse or absent KB coverage"]
    MI1_leaf2["Confirm ClinAdvisor has no retrieval-strength threshold that triggers refusal on low recall"]
    MI1_leaf3["Receive hallucinated drug dose or contraindication claim in clinical summary output"]
    MI1_and2{{"AND"}}
    MI1_leaf4["Submit clinical query that causes ClinAdvisor to synthesize claims across multiple retrieved documents"]
    MI1_leaf5["Confirm no per-claim citation requirement ties each factual assertion to a specific retrieved section"]
    MI1_leaf6["Fabricated clinical assertion propagates to Orchestrator response as grounded recommendation"]

    MI1_root --> MI1_or1
    MI1_or1 --> MI1_sub1
    MI1_or1 --> MI1_sub2
    MI1_sub1 --> MI1_and1
    MI1_and1 --> MI1_leaf1
    MI1_and1 --> MI1_leaf2
    MI1_and1 --> MI1_leaf3
    MI1_sub2 --> MI1_and2
    MI1_and2 --> MI1_leaf4
    MI1_and2 --> MI1_leaf5
    MI1_and2 --> MI1_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class MI1_root goal
    class MI1_or1 orGate
    class MI1_and1,MI1_and2 andGate
    class MI1_sub1,MI1_sub2 subGoal
    class MI1_leaf1,MI1_leaf2,MI1_leaf3,MI1_leaf4,MI1_leaf5,MI1_leaf6 leaf
```
