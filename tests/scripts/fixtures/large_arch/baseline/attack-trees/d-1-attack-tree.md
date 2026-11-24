# D-1: A dependency of edge-gateway becomes unavailable and the failure...

**Component**: edge-gateway | **Risk Level**: High | **Finding**: D-1

A dependency of edge-gateway becomes unavailable and the failure cascades because edge-gateway waits on it synchronously for every request.

```mermaid
flowchart TD
    D1_root["A dependency of edge-gateway becomes unavailable and the failure..."]
    D1_or1{{"OR"}}
    D1_sub1["Reach edge-gateway in the Edge DMZ"]
    D1_sub2["Rely on the weakness described in D-1"]
    D1_leaf1["A path exists from client-portal over HTTPS (TLS 1.3)"]
    D1_leaf2["Inbound api requests are accepted without an independent check"]
    D1_leaf3["The weakness is present: A dependency of edge-gateway becomes unavailable and the failure..."]
    D1_leaf4["No effective control observed: Isolate calls from edge-gateway to the dependency with timeouts..."]

    D1_root --> D1_or1
    D1_or1 --> D1_sub1
    D1_or1 --> D1_sub2
    D1_sub1 --> D1_leaf1
    D1_sub1 --> D1_leaf2
    D1_sub2 --> D1_leaf3
    D1_sub2 --> D1_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D1_root goal
    class D1_or1 orGate
    class D1_sub1,D1_sub2 subGoal
    class D1_leaf1,D1_leaf2,D1_leaf3,D1_leaf4 leaf
```
