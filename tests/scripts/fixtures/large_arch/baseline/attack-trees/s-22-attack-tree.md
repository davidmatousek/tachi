# S-22: An attacker replays a captured model API key against...

**Component**: model-gateway | **Risk Level**: High | **Finding**: S-22

An attacker replays a captured model API key against model-gateway, which does not bind the credential to the session or channel it was issued for, so the replay is accepted as the original caller.

```mermaid
flowchart TD
    S22_root["An attacker replays a captured model API key against model-gateway..."]
    S22_or1{{"OR"}}
    S22_sub1["Reach model-gateway in the Agent Runtime Zone"]
    S22_sub2["Rely on the weakness described in S-22"]
    S22_leaf1["A path exists from planner-agent over HTTPS (TLS 1.3)"]
    S22_leaf2["Prompts and completions are accepted without an independent check"]
    S22_leaf3["The weakness is present: An attacker replays a captured model API key against..."]
    S22_leaf4["No effective control observed: Bind each model API key to the client certificate or device key..."]

    S22_root --> S22_or1
    S22_or1 --> S22_sub1
    S22_or1 --> S22_sub2
    S22_sub1 --> S22_leaf1
    S22_sub1 --> S22_leaf2
    S22_sub2 --> S22_leaf3
    S22_sub2 --> S22_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S22_root goal
    class S22_or1 orGate
    class S22_sub1,S22_sub2 subGoal
    class S22_leaf1,S22_leaf2,S22_leaf3,S22_leaf4 leaf
```
