# E-1: Object identifiers in requests to edge-gateway are trusted without...

Carried from the baseline run.

**Component**: edge-gateway | **Risk Level**: High | **Finding**: E-1

Object identifiers in requests to edge-gateway are trusted without an ownership check, so a caller can read or change inbound API requests that belong to others.

```mermaid
flowchart TD
    E1_root["Object identifiers in requests to edge-gateway are trusted without an..."]
    E1_or1{{"OR"}}
    E1_sub1["Reach edge-gateway in the Edge DMZ"]
    E1_sub2["Rely on the weakness described in E-1"]
    E1_leaf1["A path exists from client-portal over HTTPS (TLS 1.3)"]
    E1_leaf2["Inbound api requests are accepted without an independent check"]
    E1_leaf3["The weakness is present: Object identifiers in requests to edge-gateway are trusted without..."]
    E1_leaf4["No effective control observed: Check ownership or entitlement for every object reference at..."]

    E1_root --> E1_or1
    E1_or1 --> E1_sub1
    E1_or1 --> E1_sub2
    E1_sub1 --> E1_leaf1
    E1_sub1 --> E1_leaf2
    E1_sub2 --> E1_leaf3
    E1_sub2 --> E1_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E1_root goal
    class E1_or1 orGate
    class E1_sub1,E1_sub2 subGoal
    class E1_leaf1,E1_leaf2,E1_leaf3,E1_leaf4 leaf
```
