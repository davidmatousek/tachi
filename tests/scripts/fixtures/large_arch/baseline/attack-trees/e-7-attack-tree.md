# E-7: An administrative interface of intake-agent is reachable from the...

**Component**: intake-agent | **Risk Level**: High | **Finding**: E-7

An administrative interface of intake-agent is reachable from the same network as ordinary callers and relies on a single shared password.

```mermaid
flowchart TD
    E7_root["An administrative interface of intake-agent is reachable from the same..."]
    E7_or1{{"OR"}}
    E7_sub1["Reach intake-agent in the Agent Runtime Zone"]
    E7_sub2["Rely on the weakness described in E-7"]
    E7_leaf1["A path exists from edge-gateway over HTTP/2 over mTLS"]
    E7_leaf2["Free-text shipment requests are accepted without an independent check"]
    E7_leaf3["The weakness is present: An administrative interface of intake-agent is reachable from the..."]
    E7_leaf4["No effective control observed: Move the administrative interface of intake-agent behind a..."]

    E7_root --> E7_or1
    E7_or1 --> E7_sub1
    E7_or1 --> E7_sub2
    E7_sub1 --> E7_leaf1
    E7_sub1 --> E7_leaf2
    E7_sub2 --> E7_leaf3
    E7_sub2 --> E7_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E7_root goal
    class E7_or1 orGate
    class E7_sub1,E7_sub2 subGoal
    class E7_leaf1,E7_leaf2,E7_leaf3,E7_leaf4 leaf
```
