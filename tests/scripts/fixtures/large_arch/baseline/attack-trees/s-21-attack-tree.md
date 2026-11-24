# S-21: Certificate or DNS spoofing between audit-ledger and tool-server-1...

**Component**: tool-server-1 | **Risk Level**: High | **Finding**: S-21

Certificate or DNS spoofing between audit-ledger and tool-server-1 lets an attacker terminate the connection and present a lookalike endpoint when pinning is absent.

```mermaid
flowchart TD
    S21_root["Certificate or DNS spoofing between audit-ledger and tool-server-1..."]
    S21_or1{{"OR"}}
    S21_sub1["Reach tool-server-1 in the Agent Runtime Zone"]
    S21_sub2["Rely on the weakness described in S-21"]
    S21_leaf1["A path exists from worker-2 over HTTPS (TLS 1.3)"]
    S21_leaf2["Tool call arguments and results are accepted without an independent check"]
    S21_leaf3["The weakness is present: Certificate or DNS spoofing between audit-ledger and tool-server-1..."]
    S21_leaf4["No effective control observed: Pin the expected certificate authority for the link between..."]

    S21_root --> S21_or1
    S21_or1 --> S21_sub1
    S21_or1 --> S21_sub2
    S21_sub1 --> S21_leaf1
    S21_sub1 --> S21_leaf2
    S21_sub2 --> S21_leaf3
    S21_sub2 --> S21_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S21_root goal
    class S21_or1 orGate
    class S21_sub1,S21_sub2 subGoal
    class S21_leaf1,S21_leaf2,S21_leaf3,S21_leaf4 leaf
```
