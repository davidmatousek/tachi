# S-30: An attacker replays a captured scheduler credential against...

**Component**: scheduler-1 | **Risk Level**: Critical | **Finding**: S-30

An attacker replays a captured scheduler credential against scheduler-1, which does not bind the credential to the session or channel it was issued for, so the replay is accepted as the original caller.

```mermaid
flowchart TD
    S30_root["An attacker replays a captured scheduler credential against..."]
    S30_or1{{"OR"}}
    S30_sub1["Reach scheduler-1 in the Agent Runtime Zone"]
    S30_sub2["Rely on the weakness described in S-30"]
    S30_leaf1["A path exists from queue-a2 over NATS over TLS"]
    S30_leaf2["Recurring planning triggers are accepted without an independent check"]
    S30_leaf3["The weakness is present: An attacker replays a captured scheduler credential against..."]
    S30_leaf4["No effective control observed: Bind each scheduler credential to the client certificate or device..."]

    S30_root --> S30_or1
    S30_or1 --> S30_sub1
    S30_or1 --> S30_sub2
    S30_sub1 --> S30_leaf1
    S30_sub1 --> S30_leaf2
    S30_sub2 --> S30_leaf3
    S30_sub2 --> S30_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S30_root goal
    class S30_or1 orGate
    class S30_sub1,S30_sub2 subGoal
    class S30_leaf1,S30_leaf2,S30_leaf3,S30_leaf4 leaf
```
