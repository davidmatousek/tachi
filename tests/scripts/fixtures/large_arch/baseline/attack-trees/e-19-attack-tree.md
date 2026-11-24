# E-19: Multi-tenant separation in tool-server-1 depends on a request...

**Component**: tool-server-1 | **Risk Level**: Critical | **Finding**: E-19

Multi-tenant separation in tool-server-1 depends on a request header that clients can set, allowing one tenant to act in another's scope.

```mermaid
flowchart TD
    E19_root["Multi-tenant separation in tool-server-1 depends on a request header..."]
    E19_or1{{"OR"}}
    E19_sub1["Reach tool-server-1 in the Agent Runtime Zone"]
    E19_sub2["Rely on the weakness described in E-19"]
    E19_leaf1["A path exists from worker-2 over HTTPS (TLS 1.3)"]
    E19_leaf2["Tool call arguments and results are accepted without an independent check"]
    E19_leaf3["The weakness is present: Multi-tenant separation in tool-server-1 depends on a request..."]
    E19_leaf4["No effective control observed: Derive the tenant for tool-server-1 from the verified credential..."]

    E19_root --> E19_or1
    E19_or1 --> E19_sub1
    E19_or1 --> E19_sub2
    E19_sub1 --> E19_leaf1
    E19_sub1 --> E19_leaf2
    E19_sub2 --> E19_leaf3
    E19_sub2 --> E19_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E19_root goal
    class E19_or1 orGate
    class E19_sub1,E19_sub2 subGoal
    class E19_leaf1,E19_leaf2,E19_leaf3,E19_leaf4 leaf
```
