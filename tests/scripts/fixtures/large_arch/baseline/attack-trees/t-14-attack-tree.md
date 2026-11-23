# T-14: Replay of an earlier valid update to document chunks and query...

**Component**: embed-service-2 | **Risk Level**: High | **Finding**: T-14

Replay of an earlier valid update to document chunks and query embeddings reaches embed-service-2 because updates carry no nonce or expiry, restoring a state the owner already corrected.

```mermaid
flowchart TD
    T14_root["Replay of an earlier valid update to document chunks and query..."]
    T14_or1{{"OR"}}
    T14_sub1["Reach embed-service-2 in the Agent Runtime Zone"]
    T14_sub2["Rely on the weakness described in T-14"]
    T14_leaf1["A path exists from intake-agent over gRPC over mTLS"]
    T14_leaf2["Document chunks and query embeddings are accepted without an independent check"]
    T14_leaf3["The weakness is present: Replay of an earlier valid update to document chunks and query..."]
    T14_leaf4["No effective control observed: Add a nonce and a short expiry to every update accepted by..."]

    T14_root --> T14_or1
    T14_or1 --> T14_sub1
    T14_or1 --> T14_sub2
    T14_sub1 --> T14_leaf1
    T14_sub1 --> T14_leaf2
    T14_sub2 --> T14_leaf3
    T14_sub2 --> T14_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T14_root goal
    class T14_or1 orGate
    class T14_sub1,T14_sub2 subGoal
    class T14_leaf1,T14_leaf2,T14_leaf3,T14_leaf4 leaf
```
