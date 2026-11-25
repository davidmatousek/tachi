# S-4: A shared or long-lived tool API key on tool-server-1 lets anyone...

**Component**: tool-server-1 | **Risk Level**: High | **Finding**: S-4

A shared or long-lived tool API key on tool-server-1 lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.

```mermaid
flowchart TD
    S4_root["A shared or long-lived tool API key on tool-server-1 lets anyone who..."]
    S4_or1{{"OR"}}
    S4_sub1["Reach tool-server-1 in the Agent Runtime Zone"]
    S4_sub2["Rely on the weakness described in S-4"]
    S4_leaf1["A path exists from worker-2 over HTTPS (TLS 1.3)"]
    S4_leaf2["Tool call arguments and results are accepted without an independent check"]
    S4_leaf3["The weakness is present: A shared or long-lived tool API key on tool-server-1 lets anyone..."]
    S4_leaf4["No effective control observed: Replace the shared tool API key with per-workload identities that..."]

    S4_root --> S4_or1
    S4_or1 --> S4_sub1
    S4_or1 --> S4_sub2
    S4_sub1 --> S4_leaf1
    S4_sub1 --> S4_leaf2
    S4_sub2 --> S4_leaf3
    S4_sub2 --> S4_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S4_root goal
    class S4_or1 orGate
    class S4_sub1,S4_sub2 subGoal
    class S4_leaf1,S4_leaf2,S4_leaf3,S4_leaf4 leaf
```
