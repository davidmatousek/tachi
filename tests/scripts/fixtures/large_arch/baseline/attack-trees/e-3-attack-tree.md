# E-3: An administrative interface of edge-gateway is reachable from the...

**Component**: edge-gateway | **Risk Level**: Critical | **Finding**: E-3

An administrative interface of edge-gateway is reachable from the same network as ordinary callers and relies on a single shared password.

```mermaid
flowchart TD
    E3_root["An administrative interface of edge-gateway is reachable from the same..."]
    E3_or1{{"OR"}}
    E3_sub1["Reach edge-gateway in the Edge DMZ"]
    E3_sub2["Rely on the weakness described in E-3"]
    E3_leaf1["A path exists from client-portal over HTTPS (TLS 1.3)"]
    E3_leaf2["Inbound api requests are accepted without an independent check"]
    E3_leaf3["The weakness is present: An administrative interface of edge-gateway is reachable from the..."]
    E3_leaf4["No effective control observed: Move the administrative interface of edge-gateway behind a..."]

    E3_root --> E3_or1
    E3_or1 --> E3_sub1
    E3_or1 --> E3_sub2
    E3_sub1 --> E3_leaf1
    E3_sub1 --> E3_leaf2
    E3_sub2 --> E3_leaf3
    E3_sub2 --> E3_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E3_root goal
    class E3_or1 orGate
    class E3_sub1,E3_sub2 subGoal
    class E3_leaf1,E3_leaf2,E3_leaf3,E3_leaf4 leaf
```
