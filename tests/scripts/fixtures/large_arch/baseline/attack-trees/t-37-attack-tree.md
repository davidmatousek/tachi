# T-37: Serialised objects arriving from trace-collector are deserialised...

**Component**: eval-runner | **Risk Level**: Critical | **Finding**: T-37

Serialised objects arriving from trace-collector are deserialised by eval-runner with permissive type handling, allowing crafted payloads to instantiate unintended behaviour.

```mermaid
flowchart TD
    T37_root["Serialised objects arriving from trace-collector are deserialised by..."]
    T37_or1{{"OR"}}
    T37_sub1["Reach eval-runner in the Operations Zone"]
    T37_sub2["Rely on the weakness described in T-37"]
    T37_leaf1["A path exists from trace-collector over gRPC over mTLS"]
    T37_leaf2["Replayed traces and judge verdicts are accepted without an independent check"]
    T37_leaf3["The weakness is present: Serialised objects arriving from trace-collector are deserialised..."]
    T37_leaf4["No effective control observed: Replace permissive deserialisation in eval-runner with a closed..."]

    T37_root --> T37_or1
    T37_or1 --> T37_sub1
    T37_or1 --> T37_sub2
    T37_sub1 --> T37_leaf1
    T37_sub1 --> T37_leaf2
    T37_sub2 --> T37_leaf3
    T37_sub2 --> T37_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T37_root goal
    class T37_or1 orGate
    class T37_sub1,T37_sub2 subGoal
    class T37_leaf1,T37_leaf2,T37_leaf3,T37_leaf4 leaf
```
