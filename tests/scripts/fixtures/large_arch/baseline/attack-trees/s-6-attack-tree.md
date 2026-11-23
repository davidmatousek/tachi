# S-6: Session fixation against intake-agent lets an attacker pre-seed an...

**Component**: intake-agent | **Risk Level**: High | **Finding**: S-6

Session fixation against intake-agent lets an attacker pre-seed an identifier and reuse the session after the victim authenticates.

```mermaid
flowchart TD
    S6_root["Session fixation against intake-agent lets an attacker pre-seed an..."]
    S6_or1{{"OR"}}
    S6_sub1["Reach intake-agent in the Agent Runtime Zone"]
    S6_sub2["Rely on the weakness described in S-6"]
    S6_leaf1["A path exists from edge-gateway over HTTP/2 over mTLS"]
    S6_leaf2["Free-text shipment requests are accepted without an independent check"]
    S6_leaf3["The weakness is present: Session fixation against intake-agent lets an attacker pre-seed an..."]
    S6_leaf4["No effective control observed: Issue a fresh session identifier on every authentication and..."]

    S6_root --> S6_or1
    S6_or1 --> S6_sub1
    S6_or1 --> S6_sub2
    S6_sub1 --> S6_leaf1
    S6_sub1 --> S6_leaf2
    S6_sub2 --> S6_leaf3
    S6_sub2 --> S6_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S6_root goal
    class S6_or1 orGate
    class S6_sub1,S6_sub2 subGoal
    class S6_leaf1,S6_leaf2,S6_leaf3,S6_leaf4 leaf
```
