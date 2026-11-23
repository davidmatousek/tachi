# E-31: Multi-tenant separation in policy-engine depends on a request...

**Component**: policy-engine | **Risk Level**: High | **Finding**: E-31

Multi-tenant separation in policy-engine depends on a request header that clients can set, allowing one tenant to act in another's scope.

```mermaid
flowchart TD
    E31_root["Multi-tenant separation in policy-engine depends on a request header..."]
    E31_or1{{"OR"}}
    E31_sub1["Reach policy-engine in the Operations Zone"]
    E31_sub2["Rely on the weakness described in E-31"]
    E31_leaf1["A path exists from auth-broker over gRPC over mTLS"]
    E31_leaf2["Guardrail rules and approval decisions are accepted without an independent check"]
    E31_leaf3["The weakness is present: Multi-tenant separation in policy-engine depends on a request..."]
    E31_leaf4["No effective control observed: Derive the tenant for policy-engine from the verified credential..."]

    E31_root --> E31_or1
    E31_or1 --> E31_sub1
    E31_or1 --> E31_sub2
    E31_sub1 --> E31_leaf1
    E31_sub1 --> E31_leaf2
    E31_sub2 --> E31_leaf3
    E31_sub2 --> E31_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E31_root goal
    class E31_or1 orGate
    class E31_sub1,E31_sub2 subGoal
    class E31_leaf1,E31_leaf2,E31_leaf3,E31_leaf4 leaf
```
