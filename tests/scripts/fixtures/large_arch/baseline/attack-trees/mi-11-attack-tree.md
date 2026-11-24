# MI-11: Stale data in the knowledge base lets summarizer-llm present...

**Component**: summarizer-llm | **Risk Level**: Critical | **Finding**: MI-11

Stale data in the knowledge base lets summarizer-llm present superseded tariffs as current, causing wrong quotes.

```mermaid
flowchart TD
    MI11_root["Stale data in the knowledge base lets summarizer-llm present..."]
    MI11_or1{{"OR"}}
    MI11_sub1["Reach summarizer-llm in the Agent Runtime Zone"]
    MI11_sub2["Rely on the weakness described in MI-11"]
    MI11_leaf1["A path exists from worker-3 over gRPC over mTLS"]
    MI11_leaf2["Shipment records fed into summaries are accepted without an independent check"]
    MI11_leaf3["The weakness is present: Stale data in the knowledge base lets summarizer-llm present..."]
    MI11_leaf4["No effective control observed: Stamp every source used by summarizer-llm with an effective date..."]

    MI11_root --> MI11_or1
    MI11_or1 --> MI11_sub1
    MI11_or1 --> MI11_sub2
    MI11_sub1 --> MI11_leaf1
    MI11_sub1 --> MI11_leaf2
    MI11_sub2 --> MI11_leaf3
    MI11_sub2 --> MI11_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class MI11_root goal
    class MI11_or1 orGate
    class MI11_sub1,MI11_sub2 subGoal
    class MI11_leaf1,MI11_leaf2,MI11_leaf3,MI11_leaf4 leaf
```
