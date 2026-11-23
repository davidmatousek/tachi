# TE-16: Persuasive phrasing from intake-agent pushes operators to approve...

**Component**: intake-agent | **Risk Level**: High | **Finding**: TE-16

Persuasive phrasing from intake-agent pushes operators to approve proposals quickly, which reduces careful review.

```mermaid
flowchart TD
    TE16_root["Persuasive phrasing from intake-agent pushes operators to approve..."]
    TE16_or1{{"OR"}}
    TE16_sub1["Reach intake-agent in the Agent Runtime Zone"]
    TE16_sub2["Rely on the weakness described in TE-16"]
    TE16_leaf1["A path exists from edge-gateway over HTTP/2 over mTLS"]
    TE16_leaf2["Free-text shipment requests are accepted without an independent check"]
    TE16_leaf3["The weakness is present: Persuasive phrasing from intake-agent pushes operators to approve..."]
    TE16_leaf4["No effective control observed: Neutralise urgency and pressure wording in intake-agent, present..."]

    TE16_root --> TE16_or1
    TE16_or1 --> TE16_sub1
    TE16_or1 --> TE16_sub2
    TE16_sub1 --> TE16_leaf1
    TE16_sub1 --> TE16_leaf2
    TE16_sub2 --> TE16_leaf3
    TE16_sub2 --> TE16_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class TE16_root goal
    class TE16_or1 orGate
    class TE16_sub1,TE16_sub2 subGoal
    class TE16_leaf1,TE16_leaf2,TE16_leaf3,TE16_leaf4 leaf
```
