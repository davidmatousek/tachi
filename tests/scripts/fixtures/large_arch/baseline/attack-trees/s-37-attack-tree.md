# S-37: An attacker replays a captured evaluation credential against...

**Component**: eval-runner | **Risk Level**: High | **Finding**: S-37

An attacker replays a captured evaluation credential against eval-runner, which does not bind the credential to the session or channel it was issued for, so the replay is accepted as the original caller.

```mermaid
flowchart TD
    S37_root["An attacker replays a captured evaluation credential against..."]
    S37_or1{{"OR"}}
    S37_sub1["Reach eval-runner in the Operations Zone"]
    S37_sub2["Rely on the weakness described in S-37"]
    S37_leaf1["A path exists from trace-collector over gRPC over mTLS"]
    S37_leaf2["Replayed traces and judge verdicts are accepted without an independent check"]
    S37_leaf3["The weakness is present: An attacker replays a captured evaluation credential against..."]
    S37_leaf4["No effective control observed: Bind each evaluation credential to the client certificate or..."]

    S37_root --> S37_or1
    S37_or1 --> S37_sub1
    S37_or1 --> S37_sub2
    S37_sub1 --> S37_leaf1
    S37_sub1 --> S37_leaf2
    S37_sub2 --> S37_leaf3
    S37_sub2 --> S37_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S37_root goal
    class S37_or1 orGate
    class S37_sub1,S37_sub2 subGoal
    class S37_leaf1,S37_leaf2,S37_leaf3,S37_leaf4 leaf
```
