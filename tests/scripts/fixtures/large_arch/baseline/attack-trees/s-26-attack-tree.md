# S-26: Low-entropy identifiers accepted by summarizer-llm double as...

**Component**: summarizer-llm | **Risk Level**: High | **Finding**: S-26

Low-entropy identifiers accepted by summarizer-llm double as credentials, so an attacker who enumerates them submits requests under a victim's identity.

```mermaid
flowchart TD
    S26_root["Low-entropy identifiers accepted by summarizer-llm double as..."]
    S26_or1{{"OR"}}
    S26_sub1["Reach summarizer-llm in the Agent Runtime Zone"]
    S26_sub2["Rely on the weakness described in S-26"]
    S26_leaf1["A path exists from worker-3 over gRPC over mTLS"]
    S26_leaf2["Shipment records fed into summaries are accepted without an independent check"]
    S26_leaf3["The weakness is present: Low-entropy identifiers accepted by summarizer-llm double as..."]
    S26_leaf4["No effective control observed: Separate identifiers from secrets, generate secrets from a..."]

    S26_root --> S26_or1
    S26_or1 --> S26_sub1
    S26_or1 --> S26_sub2
    S26_sub1 --> S26_leaf1
    S26_sub1 --> S26_leaf2
    S26_sub2 --> S26_leaf3
    S26_sub2 --> S26_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S26_root goal
    class S26_or1 orGate
    class S26_sub1,S26_sub2 subGoal
    class S26_leaf1,S26_leaf2,S26_leaf3,S26_leaf4 leaf
```
