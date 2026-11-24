# D-34: Expensive queries over guardrail rules and approval decisions can...

**Component**: policy-engine | **Risk Level**: Critical | **Finding**: D-34

Expensive queries over guardrail rules and approval decisions can be triggered by any authorised caller of policy-engine, so one user can degrade the service for all.

```mermaid
flowchart TD
    D34_root["Expensive queries over guardrail rules and approval decisions can be..."]
    D34_or1{{"OR"}}
    D34_sub1["Reach policy-engine in the Operations Zone"]
    D34_sub2["Rely on the weakness described in D-34"]
    D34_leaf1["A path exists from auth-broker over gRPC over mTLS"]
    D34_leaf2["Guardrail rules and approval decisions are accepted without an independent check"]
    D34_leaf3["The weakness is present: Expensive queries over guardrail rules and approval decisions can..."]
    D34_leaf4["No effective control observed: Enforce cost limits and pagination on queries to policy-engine..."]

    D34_root --> D34_or1
    D34_or1 --> D34_sub1
    D34_or1 --> D34_sub2
    D34_sub1 --> D34_leaf1
    D34_sub1 --> D34_leaf2
    D34_sub2 --> D34_leaf3
    D34_sub2 --> D34_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D34_root goal
    class D34_or1 orGate
    class D34_sub1,D34_sub2 subGoal
    class D34_leaf1,D34_leaf2,D34_leaf3,D34_leaf4 leaf
```
