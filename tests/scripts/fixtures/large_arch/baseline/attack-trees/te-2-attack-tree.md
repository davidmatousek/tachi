# TE-2: Persuasive phrasing from intake-agent pushes operators to approve...

**Component**: intake-agent | **Risk Level**: Critical | **Finding**: TE-2

Persuasive phrasing from intake-agent pushes operators to approve proposals quickly, which reduces careful review.

```mermaid
flowchart TD
    TE2_root["Persuasive phrasing from intake-agent pushes operators to approve..."]
    TE2_or1{{"OR"}}
    TE2_sub1["Reach intake-agent in the Agent Runtime Zone"]
    TE2_sub2["Rely on the weakness described in TE-2"]
    TE2_leaf1["A path exists from edge-gateway over HTTP/2 over mTLS"]
    TE2_leaf2["Free-text shipment requests are accepted without an independent check"]
    TE2_leaf3["The weakness is present: Persuasive phrasing from intake-agent pushes operators to approve..."]
    TE2_leaf4["No effective control observed: Neutralise urgency and pressure wording in intake-agent, present..."]

    TE2_root --> TE2_or1
    TE2_or1 --> TE2_sub1
    TE2_or1 --> TE2_sub2
    TE2_sub1 --> TE2_leaf1
    TE2_sub1 --> TE2_leaf2
    TE2_sub2 --> TE2_leaf3
    TE2_sub2 --> TE2_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class TE2_root goal
    class TE2_or1 orGate
    class TE2_sub1,TE2_sub2 subGoal
    class TE2_leaf1,TE2_leaf2,TE2_leaf3,TE2_leaf4 leaf
```
