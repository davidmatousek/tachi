# D-28: A burst of requests exhausts the connection pool of queue-a2...

**Component**: queue-a2 | **Risk Level**: High | **Finding**: D-28

A burst of requests exhausts the connection pool of queue-a2, which queues work without a bound and blocks legitimate use of task and result messages.

```mermaid
flowchart TD
    D28_root["A burst of requests exhausts the connection pool of queue-a2, which..."]
    D28_or1{{"OR"}}
    D28_sub1["Reach queue-a2 in the Agent Runtime Zone"]
    D28_sub2["Rely on the weakness described in D-28"]
    D28_leaf1["A path exists from intake-agent over NATS over TLS"]
    D28_leaf2["Task and result messages are accepted without an independent check"]
    D28_leaf3["The weakness is present: A burst of requests exhausts the connection pool of queue-a2..."]
    D28_leaf4["No effective control observed: Set explicit concurrency and queue limits on queue-a2, shed load..."]

    D28_root --> D28_or1
    D28_or1 --> D28_sub1
    D28_or1 --> D28_sub2
    D28_sub1 --> D28_leaf1
    D28_sub1 --> D28_leaf2
    D28_sub2 --> D28_leaf3
    D28_sub2 --> D28_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D28_root goal
    class D28_or1 orGate
    class D28_sub1,D28_sub2 subGoal
    class D28_leaf1,D28_leaf2,D28_leaf3,D28_leaf4 leaf
```
