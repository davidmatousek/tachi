# D-38: Retry storms from feature-store-2 multiply the load on...

**Component**: summarizer-llm | **Risk Level**: Critical | **Finding**: D-38

Retry storms from feature-store-2 multiply the load on summarizer-llm when it slows down, turning a brief delay into a sustained outage.

```mermaid
flowchart TD
    D38_root["Retry storms from feature-store-2 multiply the load on summarizer-llm..."]
    D38_or1{{"OR"}}
    D38_sub1["Reach summarizer-llm in the Agent Runtime Zone"]
    D38_sub2["Rely on the weakness described in D-38"]
    D38_leaf1["A path exists from worker-3 over gRPC over mTLS"]
    D38_leaf2["Shipment records fed into summaries are accepted without an independent check"]
    D38_leaf3["The weakness is present: Retry storms from feature-store-2 multiply the load on..."]
    D38_leaf4["No effective control observed: Add jittered exponential backoff and a retry budget to..."]

    D38_root --> D38_or1
    D38_or1 --> D38_sub1
    D38_or1 --> D38_sub2
    D38_sub1 --> D38_leaf1
    D38_sub1 --> D38_leaf2
    D38_sub2 --> D38_leaf3
    D38_sub2 --> D38_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D38_root goal
    class D38_or1 orGate
    class D38_sub1,D38_sub2 subGoal
    class D38_leaf1,D38_leaf2,D38_leaf3,D38_leaf4 leaf
```
