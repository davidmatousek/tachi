# E-27: Multi-tenant separation in scheduler-1 depends on a request header...

**Component**: scheduler-1 | **Risk Level**: High | **Finding**: E-27

Multi-tenant separation in scheduler-1 depends on a request header that clients can set, allowing one tenant to act in another's scope.

```mermaid
flowchart TD
    E27_root["Multi-tenant separation in scheduler-1 depends on a request header..."]
    E27_or1{{"OR"}}
    E27_sub1["Reach scheduler-1 in the Agent Runtime Zone"]
    E27_sub2["Rely on the weakness described in E-27"]
    E27_leaf1["A path exists from queue-a2 over NATS over TLS"]
    E27_leaf2["Recurring planning triggers are accepted without an independent check"]
    E27_leaf3["The weakness is present: Multi-tenant separation in scheduler-1 depends on a request header..."]
    E27_leaf4["No effective control observed: Derive the tenant for scheduler-1 from the verified credential..."]

    E27_root --> E27_or1
    E27_or1 --> E27_sub1
    E27_or1 --> E27_sub2
    E27_sub1 --> E27_leaf1
    E27_sub1 --> E27_leaf2
    E27_sub2 --> E27_leaf3
    E27_sub2 --> E27_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E27_root goal
    class E27_or1 orGate
    class E27_sub1,E27_sub2 subGoal
    class E27_leaf1,E27_leaf2,E27_leaf3,E27_leaf4 leaf
```
