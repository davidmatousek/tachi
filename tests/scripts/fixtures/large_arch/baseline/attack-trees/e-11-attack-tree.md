# E-11: Multi-tenant separation in router-agent depends on a request...

**Component**: router-agent | **Risk Level**: High | **Finding**: E-11

Multi-tenant separation in router-agent depends on a request header that clients can set, allowing one tenant to act in another's scope.

```mermaid
flowchart TD
    E11_root["Multi-tenant separation in router-agent depends on a request header..."]
    E11_or1{{"OR"}}
    E11_sub1["Reach router-agent in the Agent Runtime Zone"]
    E11_sub2["Rely on the weakness described in E-11"]
    E11_leaf1["A path exists from planner-agent over HTTP/2 over mTLS"]
    E11_leaf2["Subtask assignments are accepted without an independent check"]
    E11_leaf3["The weakness is present: Multi-tenant separation in router-agent depends on a request..."]
    E11_leaf4["No effective control observed: Derive the tenant for router-agent from the verified credential..."]

    E11_root --> E11_or1
    E11_or1 --> E11_sub1
    E11_or1 --> E11_sub2
    E11_sub1 --> E11_leaf1
    E11_sub1 --> E11_leaf2
    E11_sub2 --> E11_leaf3
    E11_sub2 --> E11_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E11_root goal
    class E11_or1 orGate
    class E11_sub1,E11_sub2 subGoal
    class E11_leaf1,E11_leaf2,E11_leaf3,E11_leaf4 leaf
```
