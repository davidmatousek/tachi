# T-41: Backups and exports of guardrail rules and approval decisions on...

**Component**: policy-engine | **Risk Level**: High | **Finding**: T-41

Backups and exports of guardrail rules and approval decisions on policy-engine are writable by operators without a second approver, so a malicious change survives restores.

```mermaid
flowchart TD
    T41_root["Backups and exports of guardrail rules and approval decisions on..."]
    T41_or1{{"OR"}}
    T41_sub1["Reach policy-engine in the Operations Zone"]
    T41_sub2["Rely on the weakness described in T-41"]
    T41_leaf1["A path exists from auth-broker over gRPC over mTLS"]
    T41_leaf2["Guardrail rules and approval decisions are accepted without an independent check"]
    T41_leaf3["The weakness is present: Backups and exports of guardrail rules and approval decisions on..."]
    T41_leaf4["No effective control observed: Protect exports and backups of guardrail rules and approval..."]

    T41_root --> T41_or1
    T41_or1 --> T41_sub1
    T41_or1 --> T41_sub2
    T41_sub1 --> T41_leaf1
    T41_sub1 --> T41_leaf2
    T41_sub2 --> T41_leaf3
    T41_sub2 --> T41_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T41_root goal
    class T41_or1 orGate
    class T41_sub1,T41_sub2 subGoal
    class T41_leaf1,T41_leaf2,T41_leaf3,T41_leaf4 leaf
```
