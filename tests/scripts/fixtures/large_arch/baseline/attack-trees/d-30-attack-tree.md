# D-30: A slow-read attack holds connections to scheduler-1 open and ties...

**Component**: scheduler-1 | **Risk Level**: High | **Finding**: D-30

A slow-read attack holds connections to scheduler-1 open and ties up the workers handling recurring planning triggers until none remain for real requests.

```mermaid
flowchart TD
    D30_root["A slow-read attack holds connections to scheduler-1 open and ties up..."]
    D30_or1{{"OR"}}
    D30_sub1["Reach scheduler-1 in the Agent Runtime Zone"]
    D30_sub2["Rely on the weakness described in D-30"]
    D30_leaf1["A path exists from queue-a2 over NATS over TLS"]
    D30_leaf2["Recurring planning triggers are accepted without an independent check"]
    D30_leaf3["The weakness is present: A slow-read attack holds connections to scheduler-1 open and ties..."]
    D30_leaf4["No effective control observed: Apply idle and total timeouts on every connection to scheduler-1..."]

    D30_root --> D30_or1
    D30_or1 --> D30_sub1
    D30_or1 --> D30_sub2
    D30_sub1 --> D30_leaf1
    D30_sub1 --> D30_leaf2
    D30_sub2 --> D30_leaf3
    D30_sub2 --> D30_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D30_root goal
    class D30_or1 orGate
    class D30_sub1,D30_sub2 subGoal
    class D30_leaf1,D30_leaf2,D30_leaf3,D30_leaf4 leaf
```
