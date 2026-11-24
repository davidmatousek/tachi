# MI-10: summarizer-llm fabricates reference numbers and clause citations...

**Component**: summarizer-llm | **Risk Level**: High | **Finding**: MI-10

summarizer-llm fabricates reference numbers and clause citations that look real, which operators then paste into official documents.

```mermaid
flowchart TD
    MI10_root["summarizer-llm fabricates reference numbers and clause citations that..."]
    MI10_or1{{"OR"}}
    MI10_sub1["Reach summarizer-llm in the Agent Runtime Zone"]
    MI10_sub2["Rely on the weakness described in MI-10"]
    MI10_leaf1["A path exists from worker-3 over gRPC over mTLS"]
    MI10_leaf2["Shipment records fed into summaries are accepted without an independent check"]
    MI10_leaf3["The weakness is present: summarizer-llm fabricates reference numbers and clause citations..."]
    MI10_leaf4["No effective control observed: Verify identifiers and citations produced by summarizer-llm..."]

    MI10_root --> MI10_or1
    MI10_or1 --> MI10_sub1
    MI10_or1 --> MI10_sub2
    MI10_sub1 --> MI10_leaf1
    MI10_sub1 --> MI10_leaf2
    MI10_sub2 --> MI10_leaf3
    MI10_sub2 --> MI10_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class MI10_root goal
    class MI10_or1 orGate
    class MI10_sub1,MI10_sub2 subGoal
    class MI10_leaf1,MI10_leaf2,MI10_leaf3,MI10_leaf4 leaf
```
