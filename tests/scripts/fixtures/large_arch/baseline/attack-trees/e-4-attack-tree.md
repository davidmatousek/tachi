# E-4: edge-gateway runs with broader permissions than its function...

**Component**: edge-gateway | **Risk Level**: High | **Finding**: E-4

edge-gateway runs with broader permissions than its function needs, so a flaw in handling inbound API requests yields access to unrelated resources.

```mermaid
flowchart TD
    E4_root["edge-gateway runs with broader permissions than its function needs, so..."]
    E4_or1{{"OR"}}
    E4_sub1["Reach edge-gateway in the Edge DMZ"]
    E4_sub2["Rely on the weakness described in E-4"]
    E4_leaf1["A path exists from client-portal over HTTPS (TLS 1.3)"]
    E4_leaf2["Inbound api requests are accepted without an independent check"]
    E4_leaf3["The weakness is present: edge-gateway runs with broader permissions than its function..."]
    E4_leaf4["No effective control observed: Reduce the permissions of edge-gateway to the minimum for inbound..."]

    E4_root --> E4_or1
    E4_or1 --> E4_sub1
    E4_or1 --> E4_sub2
    E4_sub1 --> E4_leaf1
    E4_sub1 --> E4_leaf2
    E4_sub2 --> E4_leaf3
    E4_sub2 --> E4_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E4_root goal
    class E4_or1 orGate
    class E4_sub1,E4_sub2 subGoal
    class E4_leaf1,E4_leaf2,E4_leaf3,E4_leaf4 leaf
```
