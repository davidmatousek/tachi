# E-12: Role claims carried in the worker credential presented to worker-2...

**Component**: worker-2 | **Risk Level**: High | **Finding**: E-12

Role claims carried in the worker credential presented to worker-2 are honoured without confirmation against the authoritative directory.

```mermaid
flowchart TD
    E12_root["Role claims carried in the worker credential presented to worker-2 are..."]
    E12_or1{{"OR"}}
    E12_sub1["Reach worker-2 in the Agent Runtime Zone"]
    E12_sub2["Rely on the weakness described in E-12"]
    E12_leaf1["A path exists from router-agent over HTTP/2 over mTLS"]
    E12_leaf2["Work orders and route candidates are accepted without an independent check"]
    E12_leaf3["The weakness is present: Role claims carried in the worker credential presented to worker-2..."]
    E12_leaf4["No effective control observed: Resolve roles for worker-2 from the authoritative directory on..."]

    E12_root --> E12_or1
    E12_or1 --> E12_sub1
    E12_or1 --> E12_sub2
    E12_sub1 --> E12_leaf1
    E12_sub1 --> E12_leaf2
    E12_sub2 --> E12_leaf3
    E12_sub2 --> E12_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E12_root goal
    class E12_or1 orGate
    class E12_sub1,E12_sub2 subGoal
    class E12_leaf1,E12_leaf2,E12_leaf3,E12_leaf4 leaf
```
