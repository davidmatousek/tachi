# S-38: An attacker replays a captured policy token against policy-engine...

**Component**: policy-engine | **Risk Level**: High | **Finding**: S-38

An attacker replays a captured policy token against policy-engine, which does not bind the credential to the session or channel it was issued for, so the replay is accepted as the original caller.

```mermaid
flowchart TD
    S38_root["An attacker replays a captured policy token against policy-engine..."]
    S38_or1{{"OR"}}
    S38_sub1["Reach policy-engine in the Operations Zone"]
    S38_sub2["Rely on the weakness described in S-38"]
    S38_leaf1["A path exists from auth-broker over gRPC over mTLS"]
    S38_leaf2["Guardrail rules and approval decisions are accepted without an independent check"]
    S38_leaf3["The weakness is present: An attacker replays a captured policy token against policy-engine..."]
    S38_leaf4["No effective control observed: Bind each policy token to the client certificate or device key..."]

    S38_root --> S38_or1
    S38_or1 --> S38_sub1
    S38_or1 --> S38_sub2
    S38_sub1 --> S38_leaf1
    S38_sub1 --> S38_leaf2
    S38_sub2 --> S38_leaf3
    S38_sub2 --> S38_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S38_root goal
    class S38_or1 orGate
    class S38_sub1,S38_sub2 subGoal
    class S38_leaf1,S38_leaf2,S38_leaf3,S38_leaf4 leaf
```
