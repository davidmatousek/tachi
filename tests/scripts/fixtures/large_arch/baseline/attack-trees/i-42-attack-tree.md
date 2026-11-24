# I-42: Logs and traces emitted by audit-ledger include raw approval and...

**Component**: audit-ledger | **Risk Level**: High | **Finding**: I-42

Logs and traces emitted by audit-ledger include raw approval and tool call records, so anyone with access to the logging pipeline can read content meant for one tenant.

```mermaid
flowchart TD
    I42_root["Logs and traces emitted by audit-ledger include raw approval and tool..."]
    I42_or1{{"OR"}}
    I42_sub1["Reach audit-ledger in the Operations Zone"]
    I42_sub2["Rely on the weakness described in I-42"]
    I42_leaf1["A path exists from tool-server-1 over gRPC over mTLS"]
    I42_leaf2["Approval and tool call records are accepted without an independent check"]
    I42_leaf3["The weakness is present: Logs and traces emitted by audit-ledger include raw approval and..."]
    I42_leaf4["No effective control observed: Redact or tokenise sensitive fields before audit-ledger emits logs..."]

    I42_root --> I42_or1
    I42_or1 --> I42_sub1
    I42_or1 --> I42_sub2
    I42_sub1 --> I42_leaf1
    I42_sub1 --> I42_leaf2
    I42_sub2 --> I42_leaf3
    I42_sub2 --> I42_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I42_root goal
    class I42_or1 orGate
    class I42_sub1,I42_sub2 subGoal
    class I42_leaf1,I42_leaf2,I42_leaf3,I42_leaf4 leaf
```
