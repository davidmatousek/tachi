# I-47: Data in transit between audit-ledger and policy-engine is...

**Component**: policy-engine | **Risk Level**: High | **Finding**: I-47

Data in transit between audit-ledger and policy-engine is protected only on the outer hop, which leaves guardrail rules and approval decisions readable on the internal segment after termination.

```mermaid
flowchart TD
    I47_root["Data in transit between audit-ledger and policy-engine is protected..."]
    I47_or1{{"OR"}}
    I47_sub1["Reach policy-engine in the Operations Zone"]
    I47_sub2["Rely on the weakness described in I-47"]
    I47_leaf1["A path exists from auth-broker over gRPC over mTLS"]
    I47_leaf2["Guardrail rules and approval decisions are accepted without an independent check"]
    I47_leaf3["The weakness is present: Data in transit between audit-ledger and policy-engine is..."]
    I47_leaf4["No effective control observed: Keep TLS end to end between audit-ledger and policy-engine..."]

    I47_root --> I47_or1
    I47_or1 --> I47_sub1
    I47_or1 --> I47_sub2
    I47_sub1 --> I47_leaf1
    I47_sub1 --> I47_leaf2
    I47_sub2 --> I47_leaf3
    I47_sub2 --> I47_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I47_root goal
    class I47_or1 orGate
    class I47_sub1,I47_sub2 subGoal
    class I47_leaf1,I47_leaf2,I47_leaf3,I47_leaf4 leaf
```
