# T-40: Serialised objects arriving from audit-ledger are deserialised by...

**Component**: policy-engine | **Risk Level**: High | **Finding**: T-40

Serialised objects arriving from audit-ledger are deserialised by policy-engine with permissive type handling, allowing crafted payloads to instantiate unintended behaviour.

```mermaid
flowchart TD
    T40_root["Serialised objects arriving from audit-ledger are deserialised by..."]
    T40_or1{{"OR"}}
    T40_sub1["Reach policy-engine in the Operations Zone"]
    T40_sub2["Rely on the weakness described in T-40"]
    T40_leaf1["A path exists from auth-broker over gRPC over mTLS"]
    T40_leaf2["Guardrail rules and approval decisions are accepted without an independent check"]
    T40_leaf3["The weakness is present: Serialised objects arriving from audit-ledger are deserialised by..."]
    T40_leaf4["No effective control observed: Replace permissive deserialisation in policy-engine with a closed..."]

    T40_root --> T40_or1
    T40_or1 --> T40_sub1
    T40_or1 --> T40_sub2
    T40_sub1 --> T40_leaf1
    T40_sub1 --> T40_leaf2
    T40_sub2 --> T40_leaf3
    T40_sub2 --> T40_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T40_root goal
    class T40_or1 orGate
    class T40_sub1,T40_sub2 subGoal
    class T40_leaf1,T40_leaf2,T40_leaf3,T40_leaf4 leaf
```
