# D-33: A dependency of eval-runner becomes unavailable and the failure...

**Component**: eval-runner | **Risk Level**: High | **Finding**: D-33

A dependency of eval-runner becomes unavailable and the failure cascades because eval-runner waits on it synchronously for every request.

```mermaid
flowchart TD
    D33_root["A dependency of eval-runner becomes unavailable and the failure..."]
    D33_or1{{"OR"}}
    D33_sub1["Reach eval-runner in the Operations Zone"]
    D33_sub2["Rely on the weakness described in D-33"]
    D33_leaf1["A path exists from trace-collector over gRPC over mTLS"]
    D33_leaf2["Replayed traces and judge verdicts are accepted without an independent check"]
    D33_leaf3["The weakness is present: A dependency of eval-runner becomes unavailable and the failure..."]
    D33_leaf4["No effective control observed: Isolate calls from eval-runner to the dependency with timeouts and..."]

    D33_root --> D33_or1
    D33_or1 --> D33_sub1
    D33_or1 --> D33_sub2
    D33_sub1 --> D33_leaf1
    D33_sub1 --> D33_leaf2
    D33_sub2 --> D33_leaf3
    D33_sub2 --> D33_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D33_root goal
    class D33_or1 orGate
    class D33_sub1,D33_sub2 subGoal
    class D33_leaf1,D33_leaf2,D33_leaf3,D33_leaf4 leaf
```
