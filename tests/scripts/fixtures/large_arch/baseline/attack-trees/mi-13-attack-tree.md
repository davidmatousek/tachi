# MI-13: Confident wording from summarizer-llm hides low retrieval quality...

**Component**: summarizer-llm | **Risk Level**: Critical | **Finding**: MI-13

Confident wording from summarizer-llm hides low retrieval quality, so operators cannot tell a grounded answer from a guess.

```mermaid
flowchart TD
    MI13_root["Confident wording from summarizer-llm hides low retrieval quality, so..."]
    MI13_or1{{"OR"}}
    MI13_sub1["Reach summarizer-llm in the Agent Runtime Zone"]
    MI13_sub2["Rely on the weakness described in MI-13"]
    MI13_leaf1["A path exists from worker-3 over gRPC over mTLS"]
    MI13_leaf2["Shipment records fed into summaries are accepted without an independent check"]
    MI13_leaf3["The weakness is present: Confident wording from summarizer-llm hides low retrieval quality..."]
    MI13_leaf4["No effective control observed: Expose retrieval strength alongside the answers of summarizer-llm..."]

    MI13_root --> MI13_or1
    MI13_or1 --> MI13_sub1
    MI13_or1 --> MI13_sub2
    MI13_sub1 --> MI13_leaf1
    MI13_sub1 --> MI13_leaf2
    MI13_sub2 --> MI13_leaf3
    MI13_sub2 --> MI13_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class MI13_root goal
    class MI13_or1 orGate
    class MI13_sub1,MI13_sub2 subGoal
    class MI13_leaf1,MI13_leaf2,MI13_leaf3,MI13_leaf4 leaf
```
